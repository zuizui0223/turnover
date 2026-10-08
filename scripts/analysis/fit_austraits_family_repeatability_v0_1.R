#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
effects_path<-getarg("--effects");out_path<-getarg("--out");boot_path<-getarg("--bootstrap-table");loo_path<-getarg("--loo-table")
for(p in c(out_path,boot_path,loo_path))dir.create(dirname(p),recursive=TRUE,showWarnings=FALSE)
d<-fromJSON("data/austraits_real_effect_execution_v0_1.json",simplifyVector=FALSE)
x<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
req<-c("family","trait_name","S3_rho","prune_only_rho")
if(!all(req%in%names(x)))stop("effects missing required columns")
if(nrow(x)<1||length(unique(x$family))<12||length(unique(x$trait_name))<4)stop("final core below frozen minimum")
if(any(!is.finite(x$S3_rho))||any(!is.finite(x$prune_only_rho)))stop("nonfinite rho")
fit_model<-function(y,fam=x$family,tr=x$trait_name){
  dat<-data.frame(y=as.numeric(y),family=factor(fam),trait_name=factor(tr))
  lmer(y~0+trait_name+(1|family),data=dat,REML=TRUE,
       control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
}
sumfit<-function(f){
  vc<-as.data.frame(VarCorr(f));vf<-vc$vcov[vc$grp=="family"][1];ve<-sigma(f)^2
  if(length(vf)==0||!is.finite(vf)||!is.finite(ve)||vf<0||ve<0||vf+ve<=0)stop("invalid variance")
  list(family_variance=vf,residual_variance=ve,conditional_family_repeatability=vf/(vf+ve),singular=isSingular(f,tol=1e-4))
}
fit<-fit_model(x$S3_rho);primary<-sumfit(fit)
dat0<-data.frame(family=factor(x$family),trait_name=factor(x$trait_name))
X<-model.matrix(~0+trait_name,data=dat0);mu<-as.numeric(X%*%fixef(fit))
families<-levels(dat0$family);fi<-match(x$family,families)
B<-as.integer(d$primary_replication$bootstrap_replicates);seed0<-as.integer(d$primary_replication$bootstrap_seed)
if(B!=2000)stop("unexpected bootstrap count")
set.seed(seed0);sf<-sqrt(primary$family_variance);se<-sqrt(primary$residual_variance)
boot<-data.frame(replicate=seq_len(B),valid=FALSE,failed=FALSE,singular=FALSE,icc=NA_real_)
for(i in seq_len(B)){
  uf<-if(sf>0)rnorm(length(families),0,sf)else rep(0,length(families));eps<-rnorm(nrow(x),0,se)
  fb<-tryCatch(fit_model(mu+uf[fi]+eps),error=function(e)NULL)
  if(is.null(fb)){boot$failed[i]<-TRUE;next}
  sm<-tryCatch(sumfit(fb),error=function(e)NULL)
  if(is.null(sm)){boot$failed[i]<-TRUE;next}
  boot$valid[i]<-TRUE;boot$singular[i]<-sm$singular;boot$icc[i]<-sm$conditional_family_repeatability
}
write.csv(boot,boot_path,row.names=FALSE,na="")
ok<-boot$valid&is.finite(boot$icc);vfraction<-mean(ok)
if(vfraction<0.90)stop("bootstrap valid fraction below 0.90")
ci<-as.numeric(quantile(boot$icc[ok],c(.025,.975),names=FALSE,type=7))
ref<-as.numeric(d$primary_replication$practical_reference)
interp<-if(ci[1]>ref)"REPEATABLE_LINEAGE_CONTEXT" else if(ci[2]<ref)"WEAK_LINEAGE_REPEATABILITY" else "UNCERTAIN_RELATIVE_TO_10_PERCENT_REFERENCE"
prune<-sumfit(fit_model(x$prune_only_rho))
loo<-list();k<-0
for(tr in sort(unique(x$trait_name))){
  keep<-x$trait_name!=tr
  if(length(unique(x$trait_name[keep]))<4||length(unique(x$family[keep]))<12)next
  f<-tryCatch(fit_model(x$S3_rho[keep],x$family[keep],x$trait_name[keep]),error=function(e)NULL);k<-k+1
  loo[[k]]<-data.frame(kind="trait",omitted=tr,n_systems=sum(keep),estimate=if(is.null(f))NA else sumfit(f)$conditional_family_repeatability)
}
for(fa in sort(unique(x$family))){
  keep<-x$family!=fa
  if(length(unique(x$trait_name[keep]))<4||length(unique(x$family[keep]))<12)next
  f<-tryCatch(fit_model(x$S3_rho[keep],x$family[keep],x$trait_name[keep]),error=function(e)NULL);k<-k+1
  loo[[k]]<-data.frame(kind="family",omitted=fa,n_systems=sum(keep),estimate=if(is.null(f))NA else sumfit(f)$conditional_family_repeatability)
}
lootab<-do.call(rbind,loo);write.csv(lootab,loo_path,row.names=FALSE,na="")
out<-list(
 version="v0.1",status="AUSTRAITS_FAMILY_REPEATABILITY_ESTIMATED",austraits_memory_effects_opened=TRUE,
 n_systems=nrow(x),n_families=length(unique(x$family)),n_traits=length(unique(x$trait_name)),
 primary_S3=primary,
 bootstrap=list(replicates=B,valid_fraction=vfraction,ci95_conditional_family_repeatability=as.list(ci),seed=seed0),
 practical_reference=ref,interpretation=interp,
 prune_only_sensitivity=prune,
 leave_one_out=list(n_trait_omissions=sum(lootab$kind=="trait"),n_family_omissions=sum(lootab$kind=="family"),
                    min_estimate=min(lootab$estimate,na.rm=TRUE),max_estimate=max(lootab$estimate,na.rm=TRUE))
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null");cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
