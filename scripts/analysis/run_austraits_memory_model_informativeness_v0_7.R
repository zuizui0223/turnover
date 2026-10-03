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
d<-fromJSON(file.path(root,"data","austraits_memory_context_replication_v0_1.json"),simplifyVector=FALSE)
core<-read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(core)<1 || !all(c("family","trait_name") %in% names(core))) stop("invalid final core")
families<-sort(unique(core$family)); traits<-sort(unique(core$trait_name))
if(length(families)<12 || length(traits)<4) stop("final core below frozen global minimum")

fam_idx<-match(core$family,families)
trait_idx<-match(core$trait_name,traits)
n<-nrow(core)
trait_means<-setNames(seq(-0.10,0.10,length.out=length(traits)),traits)
mu_edge<-unname(trait_means[core$trait_name])

fit_once<-function(y){
  dat<-data.frame(y=as.numeric(y),family=factor(core$family),trait_name=factor(core$trait_name,levels=traits))
  tryCatch(
    lmer(y ~ 0 + trait_name + (1|family),data=dat,REML=TRUE,
         control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000))),
    error=function(e) NULL
  )
}
icc_from_fit<-function(fit){
  if(is.null(fit)) return(NA_real_)
  vc<-as.data.frame(VarCorr(fit))
  vf<-vc$vcov[vc$grp=="family"][1]
  ve<-sigma(fit)^2
  if(length(vf)==0 || !is.finite(vf) || !is.finite(ve) || vf<0 || ve<0 || vf+ve<=0) return(NA_real_)
  vf/(vf+ve)
}

g<-d$model_informativeness
B<-as.integer(g$replicates_per_benchmark)
seed0<-as.integer(g$master_seed)
if(B!=1000) stop("unexpected benchmark replicate count")
cases<-c("meaningful","null")
rows<-list(); summaries<-list()

for(ci in seq_along(cases)){
  nm<-cases[[ci]]
  b<-if(nm=="meaningful") g$meaningful_benchmark else g$null_benchmark
  vf<-as.numeric(b$family_variance)
  ve<-as.numeric(b$residual_variance)
  target<-as.numeric(b$conditional_family_repeatability)
  set.seed(seed0+ci-1L)
  est<-rep(NA_real_,B); failed<-rep(FALSE,B); singular<-rep(FALSE,B)
  for(i in seq_len(B)){
    uf<-if(vf>0) rnorm(length(families),0,sqrt(vf)) else rep(0,length(families))
    eps<-rnorm(n,0,sqrt(ve))
    y<-mu_edge + uf[fam_idx] + eps
    fit<-fit_once(y)
    if(is.null(fit)){failed[i]<-TRUE; next}
    singular[i]<-isSingular(fit,tol=1e-4)
    est[i]<-icc_from_fit(fit)
  }
  valid<-is.finite(est)
  fit_fraction<-mean(valid)
  med<-if(any(valid)) median(est[valid]) else NA_real_
  mae<-if(any(valid)) median(abs(est[valid]-target)) else Inf
  frac_gt_010<-sum(valid & est>0.10)/B
  a<-g$admission
  if(nm=="meaningful"){
    pass<-fit_fraction>=as.numeric(a$successful_fit_fraction_min) &&
      mae<=as.numeric(a$meaningful_median_absolute_icc_error_max) &&
      abs(med-target)<=as.numeric(a$meaningful_abs_median_bias_max) &&
      frac_gt_010>=as.numeric(a$meaningful_fraction_estimate_gt_0_10_min)
  } else {
    pass<-fit_fraction>=as.numeric(a$successful_fit_fraction_min) &&
      frac_gt_010<=as.numeric(a$null_fraction_estimate_gt_0_10_max) &&
      med<=as.numeric(a$null_median_estimate_max)
  }
  summaries[[nm]]<-list(
    target_repeatability=target,
    successful_fit_fraction=fit_fraction,
    singular_fraction=mean(singular),
    median_estimate=med,
    median_absolute_error=mae,
    fraction_estimate_gt_0_10=frac_gt_010,
    pass=pass
  )
  rows[[ci]]<-data.frame(
    benchmark=nm,replicate=seq_len(B),valid=valid,failed=failed,singular=singular,
    estimated_repeatability=est,target_repeatability=target,stringsAsFactors=FALSE
  )
}

tab<-do.call(rbind,rows)
write.csv(tab,table_path,row.names=FALSE,na="")
gate<-isTRUE(summaries$meaningful$pass) && isTRUE(summaries$null$pass)
out<-list(
  version="v0.7",
  status=if(gate)"AUSTRAITS_MEMORY_MODEL_INFORMATIVENESS_PASS" else "HOLD_AUSTRAITS_MEMORY_MODEL_INFORMATIVENESS",
  outcome_blind=TRUE,
  austraits_memory_effects_opened=FALSE,
  n_core_systems=nrow(core),
  n_families=length(families),
  n_traits=length(traits),
  replicates_per_benchmark=B,
  master_seed=seed0,
  benchmarks=summaries,
  gate_pass=gate,
  next_gate=if(gate)"Run frozen provenance-overlap audit before real AusTraits rho." else "Stop AusTraits replication before real memory effects."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
