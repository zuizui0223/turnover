#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
core_path<-getarg("--core-table"); out_path<-getarg("--out"); table_path<-getarg("--table-out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE);dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)
root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_component_detectability_v0_6_2.json"),simplifyVector=FALSE)
primary<-fromJSON(file.path(root,"results","trait_memory_model_informativeness_v0_6_1","result.json"),simplifyVector=FALSE)
if(primary$status!="HOLD_TRAIT_MEMORY_MODEL_INFORMATIVENESS" || isTRUE(primary$gate_pass)) stop("primary ratio gate not terminal HOLD")
core<-read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(core)!=201 || length(unique(core$family))!=45 || length(unique(core$trait_name))!=12) stop("core mismatch")
fam<-factor(core$family); tr<-factor(core$trait_name)
fi<-as.integer(fam); ti<-as.integer(tr); nf<-nlevels(fam); nt<-nlevels(tr); n<-nrow(core)
mu<-as.numeric(d$benchmarks$intercept); vr<-as.numeric(d$benchmarks$residual_variance); B<-as.integer(d$replicates_per_benchmark)
fit_one<-function(y){
  dat<-data.frame(y=y,family=fam,trait_name=tr)
  fit<-tryCatch(lmer(y~1+(1|family)+(1|trait_name),data=dat,REML=TRUE,
    control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000))),error=function(e)NULL)
  if(is.null(fit)) return(c(family=NA_real_,trait=NA_real_,singular=NA_real_))
  vc<-as.data.frame(VarCorr(fit))
  vf<-vc$vcov[vc$grp=="family"][1]; vt<-vc$vcov[vc$grp=="trait_name"][1]
  if(length(vf)==0||length(vt)==0||!is.finite(vf)||!is.finite(vt)) return(c(family=NA_real_,trait=NA_real_,singular=as.numeric(isSingular(fit,tol=1e-4))))
  c(family=max(0,vf),trait=max(0,vt),singular=as.numeric(isSingular(fit,tol=1e-4)))
}
cases<-c("null","trait_component","family_component","both_components")
all<-list()
for(ci in seq_along(cases)){
  nm<-cases[[ci]]; b<-d$benchmarks[[nm]]
  vf<-as.numeric(b$family_variance); vt<-as.numeric(b$trait_variance)
  set.seed(as.integer(d$master_seed)+ci-1L)
  mat<-matrix(NA_real_,nrow=B,ncol=3,dimnames=list(NULL,c("family","trait","singular")))
  for(i in seq_len(B)){
    uf<-if(vf>0)rnorm(nf,0,sqrt(vf)) else rep(0,nf)
    ut<-if(vt>0)rnorm(nt,0,sqrt(vt)) else rep(0,nt)
    y<-mu+uf[fi]+ut[ti]+rnorm(n,0,sqrt(vr))
    mat[i,]<-fit_one(y)
  }
  all[[ci]]<-data.frame(benchmark=nm,replicate=seq_len(B),
    family_variance=mat[,"family"],trait_variance=mat[,"trait"],
    singular=as.logical(mat[,"singular"]),stringsAsFactors=FALSE)
}
tab<-do.call(rbind,all)
null<-tab[tab$benchmark=="null",]
if(mean(is.finite(null$family_variance))<0.90 || mean(is.finite(null$trait_variance))<0.90) stop("null valid fraction below 0.90")
qfun<-function(x)as.numeric(quantile(x[is.finite(x)],0.95,type=7,names=FALSE))
thr_f<-qfun(null$family_variance); thr_t<-qfun(null$trait_variance)
summ<-list()
for(nm in cases){
  z<-tab[tab$benchmark==nm,]
  valid<-is.finite(z$family_variance)&is.finite(z$trait_variance)
  summ[[nm]]<-list(
    valid_fraction=mean(valid),
    singular_fraction=mean(z$singular %in% TRUE,na.rm=TRUE),
    family_detection_rate=sum(valid & z$family_variance>thr_f)/B,
    trait_detection_rate=sum(valid & z$trait_variance>thr_t)/B,
    median_family_variance=if(any(valid))median(z$family_variance[valid]) else NULL,
    median_trait_variance=if(any(valid))median(z$trait_variance[valid]) else NULL
  )
}
trait_power<-summ$trait_component$trait_detection_rate
family_power<-summ$family_component$family_detection_rate
valid_min<-min(summ$trait_component$valid_fraction,summ$family_component$valid_fraction)
gate<-trait_power>=as.numeric(d$calibration_and_admission$trait_power_min) &&
      family_power>=as.numeric(d$calibration_and_admission$family_power_min) &&
      valid_min>=as.numeric(d$calibration_and_admission$valid_fit_fraction_min)
write.csv(tab,table_path,row.names=FALSE,na="")
out<-list(version="v0.6.2",status=if(gate)"TRAIT_MEMORY_COMPONENT_DETECTABILITY_PASS" else "HOLD_TRAIT_MEMORY_COMPONENT_DETECTABILITY",
 outcome_blind=TRUE,real_memory_effects_opened=FALSE,n_core_systems=n,n_core_families=nf,n_core_traits=nt,
 null_thresholds=list(family_variance_95=thr_f,trait_variance_95=thr_t),
 benchmarks=summ,trait_component_power=trait_power,family_component_power=family_power,
 minimum_power=0.80,minimum_valid_fraction=0.90,gate_pass=gate,
 next_gate=if(gate)"Real rho may be opened only for independent component-presence inference; the trait-vs-lineage dominance ratio remains closed." else "Stop before real rho; component presence is not sufficiently detectable.")
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
