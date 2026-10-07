#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
effects<-getarg("--effects");out<-getarg("--out")
x<-read.csv(effects,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=259||length(unique(x$family))!=42||length(unique(x$trait_name))!=14)stop("unexpected final core")

fit_axis<-function(dat,col){
 d<-data.frame(rho=as.numeric(dat[[col]]),family=factor(dat$family),trait_name=factor(dat$trait_name))
 if(any(!is.finite(d$rho)))stop(paste("nonfinite",col))
 f<-lmer(rho~1+(1|family)+(1|trait_name),data=d,REML=TRUE,
         control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
 vc<-as.data.frame(VarCorr(f))
 vf<-vc$vcov[vc$grp=="family"][1]
 vt<-vc$vcov[vc$grp=="trait_name"][1]
 ve<-sigma(f)^2
 total<-vf+vt+ve
 r<-vt/(vt+ve)
 list(
  n_systems=nrow(d),n_families=length(unique(d$family)),n_traits=length(unique(d$trait_name)),
  variance=list(family=vf,trait=vt,residual=ve),
  shares=list(family=vf/total,trait=vt/total,residual=ve/total),
  conditional_family_repeatability_given_trait=vf/(vf+ve),
  trait_contrast_correlation_across_families=r,
  gaussian_pair_order_reversal_probability=acos(max(-1,min(1,r)))/pi,
  singular=isSingular(f,tol=1e-4)
 )
}
logx<-x[x$log_domain_pass %in% c(TRUE,"True","TRUE","true",1,"1"),,drop=FALSE]
if(nrow(logx)!=254||length(unique(logx$family))!=42||length(unique(logx$trait_name))!=13)stop("unexpected matched log core")
res<-list(
 version="v0.1",status="AUSTRAITS_CROSSED_VARIANCE_EXPLORATORY_ESTIMATED",
 post_outcome_exploratory=TRUE,
 interpretation_guard="Residual includes family-by-trait heterogeneity plus finite-species estimation error; do not call it a pure biological interaction variance.",
 source_native=list(S3=fit_axis(x,"S3_rho"),prune_only=fit_axis(x,"prune_only_rho")),
 matched_log=list(S3=fit_axis(logx,"S3_log_rho"),prune_only=fit_axis(logx,"prune_log_rho"))
)
write_json(res,out,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(res,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
