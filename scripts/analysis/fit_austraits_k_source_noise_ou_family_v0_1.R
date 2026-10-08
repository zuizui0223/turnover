#!/usr/bin/env Rscript
# Fixed 12-trait conditional family ICC for original and K-blind source-calibrated OU draws.
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
arg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
scenario<-arg("--scenario")
model<-arg("--model")
axis<-arg("--axis")
if(!model %in% c("trait_global","system_local"))stop("bad source model")
obsfile<-arg("--observed-K")
nullfile<-arg("--null-table")
outfile<-arg("--out")
if(!scenario %in% c("c0p25","c1","c4"))stop("bad OU scenario")
if(!axis %in% c("S3","prune_only"))stop("bad OU axis")
col<-if(axis=="S3")"S3_logK" else "prune_logK"

observed<-read.csv(obsfile,stringsAsFactors=FALSE,check.names=FALSE)
null<-read.csv(nullfile,stringsAsFactors=FALSE,check.names=FALSE)
if((nrow(observed)!=249)||(length(unique(observed$family))!=42)||
   (length(unique(observed$trait_name))!=12)||any(observed$trait_name=="seed_height"))stop("frozen 12-trait graph changed")
if(nrow(null)!=256*249||length(unique(null$replicate))!=256||
   !all(null$scenario==scenario)||!all(null$noise_model==model))stop("source-noise null table incomplete")
pairs<-observed[order(observed$family,observed$trait_name),c("family","trait_name")]
get_ICC<-function(d) {
 z<-data.frame(y=as.numeric(d[[col]]),family=factor(d$family),
               trait=factor(d$trait_name))
 f<-tryCatch(suppressWarnings(lmer(y~0+trait+(1|family),data=z,REML=TRUE,
   control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=100000)))),
   error=function(e)NULL)
 if(is.null(f))return(NA_real_)
 v<-as.data.frame(VarCorr(f))
 vf<-v$vcov[v$grp=="family"][1]
 ve<-sigma(f)^2
 if(!is.finite(vf)||!is.finite(ve)||vf+ve<=0)return(NA_real_)
 as.numeric(vf/(vf+ve))
}
emp<-get_ICC(observed)
if(!is.finite(emp))stop("observed family model failed")
draws<-numeric(256)
for(i in 0:255) {
  dd<-null[null$replicate==i,]
  dd<-dd[order(dd$family,dd$trait_name),]
  key_observed<-paste(pairs$family,pairs$trait_name,sep="|")
  key_null<-paste(dd$family,dd$trait_name,sep="|")
  if(!identical(key_observed,key_null))
     stop(sprintf("null graph mismatch replicate %d",i))
  draws[i+1]<-get_ICC(dd)
}
n_valid<-sum(is.finite(draws))
if(n_valid<.95*256)stop("too many failed OU family fits")
r<-draws[is.finite(draws)]
out<-list(version="v0.1",
  status="AUSTRAITS_SOURCE_NOISE_OU_FAMILY_REPEATABILITY_CALIBRATED",
  post_BM_outcome_pre_OU_outcome=TRUE,
  scenario=scenario,model=model,axis=axis,
  n_systems=249,n_families=42,n_traits=12,
  n_null_replicates=256,valid_null_replicates=n_valid,
  observed_family_repeatability=emp,
  null_family_repeatability=list(
     mean=mean(r),
     q025=as.numeric(quantile(r,.025)),
     q975=as.numeric(quantile(r,.975)),
     p_null_ge_observed=(1+sum(r>=emp))/(1+n_valid),
     p_null_le_observed=(1+sum(r<=emp))/(1+n_valid)))
dir.create(dirname(outfile),recursive=TRUE,showWarnings=FALSE)
write_json(out,outfile,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,auto_unbox=TRUE),"\n")
