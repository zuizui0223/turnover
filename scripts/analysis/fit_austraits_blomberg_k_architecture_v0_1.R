#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
x<-read.csv(getarg("--effects"),stringsAsFactors=FALSE,check.names=FALSE);out<-getarg("--out")
if(nrow(x)!=254||length(unique(x$family))!=42||length(unique(x$trait_name))!=13)stop("unexpected K graph")
axis<-function(col){
 d<-data.frame(y=as.numeric(x[[col]]),family=factor(x$family),trait=factor(x$trait_name))
 f1<-lmer(y~0+trait+(1|family),data=d,REML=TRUE,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
 vc1<-as.data.frame(VarCorr(f1));vf1<-vc1$vcov[vc1$grp=="family"][1];ve1<-sigma(f1)^2
 f2<-lmer(y~1+(1|family)+(1|trait),data=d,REML=TRUE,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
 vc<-as.data.frame(VarCorr(f2));vf<-vc$vcov[vc$grp=="family"][1];vt<-vc$vcov[vc$grp=="trait"][1];ve<-sigma(f2)^2
 L<-vf/(vf+ve);A<-vt/(vt+ve)
 list(
  conditional_family_repeatability=vf1/(vf1+ve1),
  family_variance_fixed_trait=vf1,residual_variance_fixed_trait=ve1,
  crossed=list(family_variance=vf,trait_variance=vt,residual_variance=ve,
               shares=list(family=vf/(vf+vt+ve),trait=vt/(vf+vt+ve),residual=ve/(vf+vt+ve)),
               memory_level_stability_L=L,allocation_stability_A=A,
               gaussian_pair_order_reversal=acos(max(-1,min(1,A)))/pi)
 )
}
res<-list(version="v0.1",status="AUSTRAITS_BLOMBERG_K_MIXED_MODELS_ESTIMATED",
          prune_primary=axis("prune_logK"),S3_sensitivity=axis("S3_logK"))
dir.create(dirname(out),recursive=TRUE,showWarnings=FALSE);write_json(res,out,pretty=TRUE,auto_unbox=TRUE)
cat(toJSON(res,pretty=TRUE,auto_unbox=TRUE),"\n")
