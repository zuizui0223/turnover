#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
})

args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args); if(is.na(i)||i==length(args)) stop(paste("missing",flag)); args[[i+1]]}
core_path<-getarg("--core-table")
out_path<-getarg("--out")
table_path<-getarg("--table-out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_model_informativeness_v0_6_1.json"),simplifyVector=FALSE)
core_result<-fromJSON(file.path(root,"results","trait_memory_crossed_core_v0_6","result.json"),simplifyVector=FALSE)
if(!identical(core_result$status,"TRAIT_MEMORY_CROSSED_CORE_PASS") || !isTRUE(core_result$gate_pass))
  stop("final crossed core did not pass")

core<-read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(!all(c("family","trait_name") %in% names(core))) stop("core table missing family/trait")
fam<-factor(core$family)
tr<-factor(core$trait_name)
if(length(levels(fam))!=as.integer(core_result$n_core_families)) stop("family count mismatch")
if(length(levels(tr))!=as.integer(core_result$n_core_traits)) stop("trait count mismatch")

fit_once<-function(y){
  dat<-data.frame(y=y,family=fam,trait_name=tr)
  tryCatch(
    lmer(y ~ 1 + (1|family) + (1|trait_name),data=dat,REML=TRUE,
         control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000))),
    error=function(e) NULL
  )
}
ratio_from_fit<-function(fit){
  if(is.null(fit) || isSingular(fit,tol=1e-4)) return(NA_real_)
  vc<-as.data.frame(VarCorr(fit))
  vf<-vc$vcov[vc$grp=="family"][1]
  vt<-vc$vcov[vc$grp=="trait_name"][1]
  if(length(vf)==0 || length(vt)==0 || is.na(vf) || is.na(vt)) return(NA_real_)
  if(vf==0 && vt==0) return(NA_real_)
  if(vf==0 && vt>0) return(Inf)
  if(vt==0 && vf>0) return(-Inf)
  log(vt/vf)
}

B<-as.integer(d$replicates_per_benchmark)
if(B!=1000) stop("unexpected benchmark replicate count")
seed0<-as.integer(d$master_seed)
mu<-as.numeric(d$benchmarks$intercept)
vr<-as.numeric(d$benchmarks$residual_variance)
fam_idx<-as.integer(fam); tr_idx<-as.integer(tr)
nf<-nlevels(fam); nt<-nlevels(tr); n<-nrow(core)

cases<-c("trait_dominant","lineage_dominant","mixed")
all_rows<-list()
summaries<-list()

for(ci in seq_along(cases)){
  nm<-cases[[ci]]
  b<-d$benchmarks[[nm]]
  vf_true<-as.numeric(b$family_variance)
  vt_true<-as.numeric(b$trait_variance)
  target<-as.numeric(b$target_log_variance_ratio)
  set.seed(seed0 + ci - 1L)
  ratios<-rep(NA_real_,B)
  singular<-rep(FALSE,B)
  failed<-rep(FALSE,B)
  for(i in seq_len(B)){
    uf<-rnorm(nf,0,sqrt(vf_true))
    ut<-rnorm(nt,0,sqrt(vt_true))
    eps<-rnorm(n,0,sqrt(vr))
    y<-mu + uf[fam_idx] + ut[tr_idx] + eps
    fit<-fit_once(y)
    if(is.null(fit)){ failed[i]<-TRUE; next }
    if(isSingular(fit,tol=1e-4)){ singular[i]<-TRUE; next }
    ratios[i]<-ratio_from_fit(fit)
  }
  valid<-!is.na(ratios)
  vfraction<-mean(valid)
  medae<-if(any(valid)) median(abs(ratios[valid]-target)) else Inf
  directional<-if(nm=="trait_dominant"){
    sum(valid & ratios>0)/B
  } else if(nm=="lineage_dominant"){
    sum(valid & ratios<0)/B
  } else NA_real_
  pass<-if(nm=="mixed") NA else (
    vfraction>=as.numeric(d$admission$valid_nonsingular_refit_fraction_min) &&
    directional>=as.numeric(d$admission$directional_recovery_min) &&
    medae<=as.numeric(d$admission$median_absolute_log_ratio_error_max)
  )
  summaries[[nm]]<-list(
    target_log_variance_ratio=target,
    valid_fraction=vfraction,
    directional_recovery=if(is.na(directional)) NULL else directional,
    median_absolute_log_ratio_error=medae,
    median_estimated_log_ratio=if(any(valid)) median(ratios[valid]) else NULL,
    singular_fraction=mean(singular),
    failed_fraction=mean(failed),
    pass=if(is.na(pass)) NULL else pass
  )
  all_rows[[ci]]<-data.frame(
    benchmark=nm,replicate=seq_len(B),valid=valid,singular=singular,failed=failed,
    estimated_log_variance_ratio=ratios,target_log_variance_ratio=target,
    stringsAsFactors=FALSE
  )
}
tab<-do.call(rbind,all_rows)
write.csv(tab,table_path,row.names=FALSE,na="")
gate<-isTRUE(summaries$trait_dominant$pass) && isTRUE(summaries$lineage_dominant$pass)
out<-list(
  version="v0.6.1",
  status=if(gate)"TRAIT_MEMORY_MODEL_INFORMATIVENESS_PASS" else "HOLD_TRAIT_MEMORY_MODEL_INFORMATIVENESS",
  outcome_blind=TRUE,
  real_memory_effects_opened=FALSE,
  n_core_systems=nrow(core),
  n_core_families=nf,
  n_core_traits=nt,
  replicates_per_benchmark=B,
  master_seed=seed0,
  benchmarks=summaries,
  gate_pass=gate,
  next_gate=if(gate)"Real memory rho may be opened under frozen v0.7 estimator." else "Stop before opening real memory rho; crossed variance architecture is not sufficiently recoverable."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
