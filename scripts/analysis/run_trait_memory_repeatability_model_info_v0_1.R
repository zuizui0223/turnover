#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
})

args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
core_path<-getarg("--core-table")
out_path<-getarg("--out")
table_path<-getarg("--table-out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_repeatability_design_v0_1.json"),simplifyVector=FALSE)
prior<-fromJSON(file.path(root,"data","trait_memory_model_informativeness_v0_6_1.json"),simplifyVector=FALSE)
core<-read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(core)!=201 || length(unique(core$family))!=45 || length(unique(core$trait_name))!=12)
  stop("frozen core dimensions mismatch")

fam<-factor(core$family); tr<-factor(core$trait_name)
fam_idx<-as.integer(fam); tr_idx<-as.integer(tr)
nf<-nlevels(fam); nt<-nlevels(tr); n<-nrow(core)

fit_once<-function(y){
  dat<-data.frame(y=y,family=fam,trait_name=tr)
  tryCatch(
    lmer(y ~ 1 + (1|family) + (1|trait_name),data=dat,REML=TRUE,
         control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000))),
    error=function(e) NULL
  )
}
shares_from_fit<-function(fit){
  if(is.null(fit)||isSingular(fit,tol=1e-4)) return(NULL)
  vc<-as.data.frame(VarCorr(fit))
  vf<-vc$vcov[vc$grp=="family"][1]
  vt<-vc$vcov[vc$grp=="trait_name"][1]
  vr<-sigma(fit)^2
  if(length(vf)==0||length(vt)==0||!all(is.finite(c(vf,vt,vr)))) return(NULL)
  total<-vf+vt+vr
  if(!is.finite(total)||total<=0) return(NULL)
  c(R_family=vf/total,R_trait=vt/total,R_residual=vr/total)
}

B<-as.integer(d$model_informativeness$replicates_per_benchmark)
if(B!=1000) stop("unexpected replicate count")
seed0<-as.integer(d$model_informativeness$master_seed)
mu<-as.numeric(prior$benchmarks$intercept)
vr<-as.numeric(prior$benchmarks$residual_variance)
cases<-c("trait_dominant","lineage_dominant","mixed")
rows<-list(); summaries<-list()

for(ci in seq_along(cases)){
  nm<-cases[[ci]]
  p<-prior$benchmarks[[nm]]
  vf_true<-as.numeric(p$family_variance)
  vt_true<-as.numeric(p$trait_variance)
  truth<-unlist(d$model_informativeness$benchmarks[[nm]])
  set.seed(seed0+ci-1L)
  mat<-matrix(NA_real_,nrow=B,ncol=3,dimnames=list(NULL,c("R_family","R_trait","R_residual")))
  singular<-rep(FALSE,B); failed<-rep(FALSE,B)
  for(i in seq_len(B)){
    uf<-rnorm(nf,0,sqrt(vf_true))
    ut<-rnorm(nt,0,sqrt(vt_true))
    eps<-rnorm(n,0,sqrt(vr))
    y<-mu + uf[fam_idx] + ut[tr_idx] + eps
    fit<-fit_once(y)
    if(is.null(fit)){failed[i]<-TRUE;next}
    if(isSingular(fit,tol=1e-4)){singular[i]<-TRUE;next}
    sh<-shares_from_fit(fit)
    if(is.null(sh))next
    mat[i,]<-sh
  }
  valid<-apply(mat,1,function(z)all(is.finite(z)))
  vfraction<-mean(valid)
  mae_f<-if(any(valid))median(abs(mat[valid,"R_family"]-truth[["true_R_family"]])) else Inf
  mae_t<-if(any(valid))median(abs(mat[valid,"R_trait"]-truth[["true_R_trait"]])) else Inf
  mae_r<-if(any(valid))median(abs(mat[valid,"R_residual"]-truth[["true_R_residual"]])) else Inf
  pass<-vfraction>=as.numeric(d$model_informativeness$admission$valid_nonsingular_fraction_min) &&
        mae_f<=as.numeric(d$model_informativeness$admission$median_absolute_error_R_family_max) &&
        mae_t<=as.numeric(d$model_informativeness$admission$median_absolute_error_R_trait_max)
  summaries[[nm]]<-list(
    true_R_family=truth[["true_R_family"]],
    true_R_trait=truth[["true_R_trait"]],
    true_R_residual=truth[["true_R_residual"]],
    valid_fraction=vfraction,
    median_absolute_error_R_family=mae_f,
    median_absolute_error_R_trait=mae_t,
    median_absolute_error_R_residual=mae_r,
    median_estimated_R_family=if(any(valid))median(mat[valid,"R_family"])else NULL,
    median_estimated_R_trait=if(any(valid))median(mat[valid,"R_trait"])else NULL,
    median_estimated_R_residual=if(any(valid))median(mat[valid,"R_residual"])else NULL,
    singular_fraction=mean(singular),
    failed_fraction=mean(failed),
    pass=pass
  )
  rows[[ci]]<-data.frame(
    benchmark=nm,replicate=seq_len(B),valid=valid,singular=singular,failed=failed,
    estimated_R_family=mat[,"R_family"],estimated_R_trait=mat[,"R_trait"],estimated_R_residual=mat[,"R_residual"],
    true_R_family=truth[["true_R_family"]],true_R_trait=truth[["true_R_trait"]],true_R_residual=truth[["true_R_residual"]],
    stringsAsFactors=FALSE
  )
}
tab<-do.call(rbind,rows)
write.csv(tab,table_path,row.names=FALSE,na="")
gate<-all(vapply(cases,function(nm)isTRUE(summaries[[nm]]$pass),logical(1)))
out<-list(
  version="v0.1",
  status=if(gate)"TRAIT_MEMORY_REPEATABILITY_MODEL_INFORMATIVENESS_PASS" else "HOLD_TRAIT_MEMORY_REPEATABILITY_MODEL_INFORMATIVENESS",
  outcome_blind=TRUE,
  real_memory_effects_opened=FALSE,
  n_core_systems=n,
  n_core_families=nf,
  n_core_traits=nt,
  replicates_per_benchmark=B,
  master_seed=seed0,
  benchmarks=summaries,
  gate_pass=gate,
  next_gate=if(gate)"Real memory rho may be opened only to estimate R_family, R_trait, and R_residual; no dominance comparison." else "Stop repeatability follow-up before real memory rho."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
