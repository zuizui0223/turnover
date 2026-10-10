#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
argv<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){
 i<-match(f,argv)
 if(is.na(i)||i==length(argv))stop(paste("missing",f))
 argv[[i+1]]
}
obs<-read.csv(getarg("--observed-K"),stringsAsFactors=FALSE,check.names=FALSE)
null<-read.csv(getarg("--null-table"),stringsAsFactors=FALSE,check.names=FALSE)
out_path<-getarg("--out")
if(nrow(obs)!=254||length(unique(obs$family))!=42||length(unique(obs$trait_name))!=13)
  stop("observed K graph changed")
if(nrow(null)!=64*254||length(unique(null$replicate))!=64)
  stop("null graph or replicate count changed")
calc<-function(d,col){
  z<-data.frame(y=as.numeric(d[[col]]),family=factor(d$family),
    trait=factor(d$trait_name))
  f<-tryCatch(
    suppressWarnings(lmer(y~0+trait+(1|family),data=z,REML=TRUE,
      control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=100000)))),
    error=function(e)NULL)
  if(is.null(f))return(NA_real_)
  vc<-as.data.frame(VarCorr(f))
  vf<-vc$vcov[vc$grp=="family"][1]
  ve<-sigma(f)^2
  if(!is.finite(vf)||!is.finite(ve)||vf+ve<=0)return(NA_real_)
  as.numeric(vf/(vf+ve))
}
all_axes<-list()
for(axis in c("S3_logK","prune_logK")){
 observed<-calc(obs,axis)
 sim<-vapply(split(null,null$replicate),calc,0.,col=axis)
 ok<-is.finite(sim)
 if(mean(ok)<.95)stop(paste("too many failed null lmer fits",axis))
 vals<-sim[ok]
 all_axes[[axis]]<-list(
   observed_family_repeatability=observed,
   valid_null_replicates=sum(ok),
   null_family_repeatability=list(
     mean=mean(vals),q025=as.numeric(quantile(vals,.025)),
     q975=as.numeric(quantile(vals,.975)),
     p_null_ge_observed=(1+sum(vals>=observed))/(1+length(vals)),
     p_null_le_observed=(1+sum(vals<=observed))/(1+length(vals))),
   successful_fit_fraction=mean(ok))
}
out<-list(version="v0.1",
 status="AUSTRAITS_REAL_TREE_EQUAL_BM_K_FAMILY_REPEATABILITY_CALIBRATED",
 n_systems=254,n_families=42,n_traits=13,
 n_null_replicates=64,
 post_outcome_null_calibration=TRUE,
 null_equal_rate_process=TRUE,
 axes=all_axes)
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
