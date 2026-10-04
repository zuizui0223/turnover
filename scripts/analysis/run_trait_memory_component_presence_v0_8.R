#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args); if(is.na(i)||i==length(args)) stop(paste("missing",flag)); args[[i+1]]}
core_path<-getarg("--core-table"); out_path<-getarg("--out"); table_path<-getarg("--table-out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE); dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_component_presence_design_v0_8.json"),simplifyVector=FALSE)
prior<-fromJSON(file.path(root,"results","trait_memory_model_informativeness_v0_6_1","result.json"),simplifyVector=FALSE)
if(!identical(prior$status,"HOLD_TRAIT_MEMORY_MODEL_INFORMATIVENESS") || isTRUE(prior$gate_pass))
  stop("prior variance-ratio question is not terminal HOLD")

core<-read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(core)!=201 || length(unique(core$family))!=45 || length(unique(core$trait_name))!=12)
  stop("frozen graph identity mismatch")
fam<-factor(core$family); tr<-factor(core$trait_name)
fi<-as.integer(fam); ti<-as.integer(tr); nf<-nlevels(fam); nt<-nlevels(tr); n<-nrow(core)

fit_once<-function(y){
  dat<-data.frame(y=y,family=fam,trait_name=tr)
  tryCatch(
    lmer(y ~ 1 + (1|family) + (1|trait_name),data=dat,REML=TRUE,
         control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000))),
    error=function(e) NULL
  )
}
extract_var<-function(fit){
  if(is.null(fit)) return(c(family=NA_real_,trait=NA_real_,residual=NA_real_))
  vc<-as.data.frame(VarCorr(fit))
  vf<-vc$vcov[vc$grp=="family"][1]; vt<-vc$vcov[vc$grp=="trait_name"][1]
  c(family=vf,trait=vt,residual=sigma(fit)^2)
}

cases<-names(d$known_truth_cases)
B<-as.integer(d$replicates_per_case)
seed0<-as.integer(d$master_seed)
mu<-as.numeric(d$benchmark_scale$intercept)
threshold<-as.numeric(d$component_detection$detection_threshold_variance)
allrows<-list(); summaries<-list()

for(ci in seq_along(cases)){
  nm<-cases[[ci]]
  cs<-d$known_truth_cases[[nm]]
  vf<-as.numeric(cs$family_variance); vt<-as.numeric(cs$trait_variance); vr<-as.numeric(cs$residual_variance)
  set.seed(seed0+ci-1L)
  tab<-data.frame(case=nm,replicate=seq_len(B),valid=FALSE,singular=FALSE,
                  family_variance=NA_real_,trait_variance=NA_real_,residual_variance=NA_real_,
                  family_detected=FALSE,trait_detected=FALSE)
  for(b in seq_len(B)){
    uf<-if(vf>0)rnorm(nf,0,sqrt(vf)) else rep(0,nf)
    ut<-if(vt>0)rnorm(nt,0,sqrt(vt)) else rep(0,nt)
    eps<-rnorm(n,0,sqrt(vr))
    y<-mu+uf[fi]+ut[ti]+eps
    fit<-fit_once(y)
    if(is.null(fit)) next
    # Singular fits are invalid for the admission metrics because one or more
    # random-effect dimensions are on the numerical boundary.
    sing<-isSingular(fit,tol=1e-4)
    tab$singular[b]<-sing
    if(sing) next
    vv<-extract_var(fit)
    if(any(!is.finite(vv))) next
    tab$valid[b]<-TRUE
    tab$family_variance[b]<-vv[["family"]]
    tab$trait_variance[b]<-vv[["trait"]]
    tab$residual_variance[b]<-vv[["residual"]]
    tab$family_detected[b]<-vv[["family"]]>=threshold
    tab$trait_detected[b]<-vv[["trait"]]>=threshold
  }
  valid<-tab$valid
  denom<-sum(valid)
  rate<-function(v) if(denom>0) sum(v & valid)/denom else NA_real_
  summaries[[nm]]<-list(
    valid_fraction=mean(valid),
    singular_fraction=mean(tab$singular),
    family_detection_rate=rate(tab$family_detected),
    trait_detection_rate=rate(tab$trait_detected),
    median_family_variance=if(denom)median(tab$family_variance[valid]) else NULL,
    median_trait_variance=if(denom)median(tab$trait_variance[valid]) else NULL
  )
  allrows[[ci]]<-tab
}
tab<-do.call(rbind,allrows)
write.csv(tab,table_path,row.names=FALSE,na="")

A<-d$admission
valid_ok<-all(vapply(summaries,function(z)z$valid_fraction>=as.numeric(A$valid_fit_fraction_min),logical(1)))
trait_only_ok<-summaries$trait_only$trait_detection_rate>=as.numeric(A$trait_only_trait_sensitivity_min) &&
               summaries$trait_only$family_detection_rate<=as.numeric(A$trait_only_family_false_positive_max)
family_only_ok<-summaries$family_only$family_detection_rate>=as.numeric(A$family_only_family_sensitivity_min) &&
                summaries$family_only$trait_detection_rate<=as.numeric(A$family_only_trait_false_positive_max)
both_ok<-summaries$both$family_detection_rate>=as.numeric(A$both_each_sensitivity_min) &&
         summaries$both$trait_detection_rate>=as.numeric(A$both_each_sensitivity_min)
neither_ok<-summaries$neither$family_detection_rate<=as.numeric(A$neither_each_false_positive_max) &&
            summaries$neither$trait_detection_rate<=as.numeric(A$neither_each_false_positive_max)
gate<-valid_ok && trait_only_ok && family_only_ok && both_ok && neither_ok

out<-list(
  version="v0.8",
  status=if(gate)"TRAIT_MEMORY_COMPONENT_PRESENCE_INFORMATIVENESS_PASS" else "HOLD_TRAIT_MEMORY_COMPONENT_PRESENCE_INFORMATIVENESS",
  outcome_blind=TRUE,real_memory_effects_opened=FALSE,
  n_core_systems=n,n_core_families=nf,n_core_traits=nt,
  detection_threshold_variance=threshold,replicates_per_case=B,master_seed=seed0,
  cases=summaries,
  checks=list(valid_fit_fraction=valid_ok,trait_only=trait_only_ok,family_only=family_only_ok,both=both_ok,neither=neither_ok),
  gate_pass=gate,
  next_gate=if(gate)d$decision_if_pass else d$decision_if_hold
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
