#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
})

args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args); if(is.na(i)||i==length(args)) stop(paste("missing",flag)); args[[i+1]]}
effects_path<-getarg("--effects")
out_path<-getarg("--out")
boot_path<-getarg("--bootstrap-table")
loo_path<-getarg("--loo-table")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(boot_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(loo_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","lineage_memory_repeatability_design_v0_1.json"),simplifyVector=FALSE)
x<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
req<-c("family","trait_name","S3_rho","prune_only_rho")
if(!all(req %in% names(x))) stop("effects table missing required columns")
if(nrow(x)!=201 || length(unique(x$family))!=45 || length(unique(x$trait_name))!=12) stop("frozen core dimensions changed")
if(any(!is.finite(x$S3_rho)) || any(!is.finite(x$prune_only_rho))) stop("nonfinite memory rho")

fit_model<-function(response,fam=x$family,tr=x$trait_name){
  dat<-data.frame(rho=as.numeric(response),family=factor(fam),trait_name=factor(tr))
  lmer(rho ~ 0 + trait_name + (1|family),data=dat,REML=TRUE,
       control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
}
summary_fit<-function(fit){
  vc<-as.data.frame(VarCorr(fit))
  vf<-vc$vcov[vc$grp=="family"][1]
  ve<-sigma(fit)^2
  if(length(vf)==0 || !is.finite(vf) || !is.finite(ve) || vf<0 || ve<0 || vf+ve<=0) stop("invalid variance extraction")
  list(
    family_variance=vf,
    residual_variance=ve,
    conditional_family_repeatability=vf/(vf+ve),
    singular=isSingular(fit,tol=1e-4)
  )
}

fit<-fit_model(x$S3_rho)
primary<-summary_fit(fit)
beta<-fixef(fit)
traits<-levels(factor(x$trait_name))
families<-levels(factor(x$family))
trait_idx<-match(x$trait_name,sub("^trait_name","",names(beta)))
if(any(is.na(trait_idx))){
  # lme4 names are normally trait_name<level>; fall back to model matrix.
  X<-model.matrix(~0+trait_name,data=data.frame(trait_name=factor(x$trait_name,levels=traits)))
  mu<-as.numeric(X %*% beta)
} else {
  mu<-as.numeric(beta[trait_idx])
}
fam_idx<-match(x$family,families)
B<-as.integer(d$real_analysis_if_gate_passes$bootstrap$replicates)
seed0<-as.integer(d$real_analysis_if_gate_passes$bootstrap$master_seed)
if(B!=2000) stop("unexpected bootstrap replicate count")
set.seed(seed0)
sd_f<-sqrt(primary$family_variance); sd_e<-sqrt(primary$residual_variance)
boot<-data.frame(replicate=seq_len(B),valid=FALSE,failed=FALSE,singular=FALSE,
                 family_variance=NA_real_,residual_variance=NA_real_,
                 conditional_family_repeatability=NA_real_,stringsAsFactors=FALSE)
for(i in seq_len(B)){
  uf<-if(sd_f>0)rnorm(length(families),0,sd_f) else rep(0,length(families))
  eps<-rnorm(nrow(x),0,sd_e)
  y<-mu+uf[fam_idx]+eps
  fb<-tryCatch(fit_model(y),error=function(e)NULL)
  if(is.null(fb)){boot$failed[i]<-TRUE;next}
  sm<-tryCatch(summary_fit(fb),error=function(e)NULL)
  if(is.null(sm)){boot$failed[i]<-TRUE;next}
  boot$valid[i]<-TRUE
  boot$singular[i]<-sm$singular
  boot$family_variance[i]<-sm$family_variance
  boot$residual_variance[i]<-sm$residual_variance
  boot$conditional_family_repeatability[i]<-sm$conditional_family_repeatability
}
write.csv(boot,boot_path,row.names=FALSE,na="")
valid<-boot$valid & is.finite(boot$conditional_family_repeatability)
vfraction<-mean(valid)
minvf<-as.numeric(d$real_analysis_if_gate_passes$bootstrap$minimum_valid_fraction)
if(vfraction<minvf){
  status<-"HOLD_LINEAGE_MEMORY_BOOTSTRAP_VALIDITY"
  ci<-c(NA_real_,NA_real_)
  interpretation<-"UNRESOLVED"
  gate<-FALSE
} else {
  icc<-boot$conditional_family_repeatability[valid]
  ci<-as.numeric(quantile(icc,c(0.025,0.975),type=7,names=FALSE))
  ref<-as.numeric(d$practical_reference$meaningful_repeatability)
  if(ci[1]>ref) interpretation<-"REPEATABLE_LINEAGE_REGIME"
  else if(ci[2]<ref) interpretation<-"WEAK_LINEAGE_REPEATABILITY"
  else interpretation<-"UNCERTAIN_RELATIVE_TO_10_PERCENT_REFERENCE"
  status<-"LINEAGE_MEMORY_REPEATABILITY_ESTIMATED"
  gate<-TRUE
}

# Mandatory prune-only descriptive sensitivity on identical systems.
fitp<-fit_model(x$prune_only_rho)
prune<-summary_fit(fitp)

# Pre-frozen leave-one-out descriptive robustness.
loo_rows<-list(); k<-0L
for(tr in sort(unique(x$trait_name))){
  keep<-x$trait_name!=tr
  if(length(unique(x$trait_name[keep]))<2 || length(unique(x$family[keep]))<2) next
  f<-tryCatch(fit_model(x$S3_rho[keep],x$family[keep],x$trait_name[keep]),error=function(e)NULL)
  k<-k+1L
  if(is.null(f)) loo_rows[[k]]<-data.frame(kind="trait",omitted=tr,n_systems=sum(keep),estimate=NA,singular=NA)
  else {sm<-summary_fit(f);loo_rows[[k]]<-data.frame(kind="trait",omitted=tr,n_systems=sum(keep),estimate=sm$conditional_family_repeatability,singular=sm$singular)}
}
for(fam in sort(unique(x$family))){
  keep<-x$family!=fam
  if(length(unique(x$trait_name[keep]))<2 || length(unique(x$family[keep]))<2) next
  f<-tryCatch(fit_model(x$S3_rho[keep],x$family[keep],x$trait_name[keep]),error=function(e)NULL)
  k<-k+1L
  if(is.null(f)) loo_rows[[k]]<-data.frame(kind="family",omitted=fam,n_systems=sum(keep),estimate=NA,singular=NA)
  else {sm<-summary_fit(f);loo_rows[[k]]<-data.frame(kind="family",omitted=fam,n_systems=sum(keep),estimate=sm$conditional_family_repeatability,singular=sm$singular)}
}
loo<-do.call(rbind,loo_rows)
write.csv(loo,loo_path,row.names=FALSE,na="")

out<-list(
  version="v0.2",
  status=status,
  real_memory_effects_opened=TRUE,
  n_systems=nrow(x),n_families=length(unique(x$family)),n_traits=length(unique(x$trait_name)),
  primary_S3=primary,
  bootstrap=list(replicates=B,valid_replicates=sum(valid),valid_fraction=vfraction,
                 ci95_conditional_family_repeatability=as.list(ci),master_seed=seed0),
  practical_reference=d$practical_reference$meaningful_repeatability,
  interpretation=interpretation,
  prune_only_sensitivity=prune,
  leave_one_out=list(
    n_trait_omissions=sum(loo$kind=="trait"),
    n_family_omissions=sum(loo$kind=="family"),
    min_estimate=min(loo$estimate,na.rm=TRUE),
    max_estimate=max(loo$estimate,na.rm=TRUE)
  ),
  model_gate_pass=gate,
  raw_trait_measurements_persisted=FALSE,
  species_states_persisted=FALSE,
  species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
