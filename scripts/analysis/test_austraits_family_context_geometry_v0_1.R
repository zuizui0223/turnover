#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
effects<-getarg("--effects");out<-getarg("--out")
x<-read.csv(effects,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=259)stop("unexpected final core")
x$z_log_n_s3<-as.numeric(scale(log(x$n_species_S3)))
x$z_prune_fraction<-as.numeric(scale(x$n_species_prune/x$n_species_S3))
x$z_log_n_prune<-as.numeric(scale(log(x$n_species_prune)))
fitone<-function(form){
 f<-lmer(form,data=x,REML=TRUE,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
 vc<-as.data.frame(VarCorr(f));vf<-vc$vcov[vc$grp=="family"][1];ve<-sigma(f)^2
 list(family_variance=vf,residual_variance=ve,conditional_family_repeatability=vf/(vf+ve),
      singular=isSingular(f,tol=1e-4),fixed_effects=as.list(fixef(f)))
}
raw_s3<-fitone(S3_rho~0+trait_name+(1|family))
adj_s3<-fitone(S3_rho~0+trait_name+z_log_n_s3+z_prune_fraction+(1|family))
raw_pr<-fitone(prune_only_rho~0+trait_name+(1|family))
adj_pr<-fitone(prune_only_rho~0+trait_name+z_log_n_prune+(1|family))
res<-list(version="v0.1",status="AUSTRAITS_FAMILY_CONTEXT_GEOMETRY_SENSITIVITY_ESTIMATED",
 post_outcome_exploratory=TRUE,
 covariates=list(S3=c("z_log_n_s3","z_prune_fraction"),prune=c("z_log_n_prune")),
 source_native=list(S3_unadjusted=raw_s3,S3_adjusted=adj_s3,prune_unadjusted=raw_pr,prune_adjusted=adj_pr),
 interpretation="If family repeatability remains similar after species coverage and native-tip fraction adjustment, these measured sampling/tree-coverage variables are not a simple explanation of the AusTraits family context.")
write_json(res,out,pretty=TRUE,auto_unbox=TRUE,null="null");cat(toJSON(res,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
