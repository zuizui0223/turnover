#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
})

args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){
  i <- match(flag,args)
  if(is.na(i) || i==length(args)) stop(paste("missing",flag))
  args[[i+1]]
}
effects_path <- getarg("--effects")
out_path <- getarg("--out")
boot_path <- getarg("--bootstrap-table")
loo_path <- getarg("--loo-table")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(boot_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(loo_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","backbone_stable_context_design_v0_1.json"),simplifyVector=FALSE)
exec <- fromJSON(file.path(root,"data","backbone_stable_context_execution_v0_1_1.json"),simplifyVector=FALSE)
model_info <- fromJSON(file.path(root,"results","backbone_stable_context_model_info_v0_1","result.json"),simplifyVector=FALSE)
if(!identical(model_info$status,"BACKBONE_STABLE_CONTEXT_MODEL_INFO_PASS") || !isTRUE(model_info$gate_pass))
  stop("model informativeness prerequisite did not pass")

x <- read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
req <- c("family","trait_name","S3_rho","prune_only_rho")
if(!all(req %in% names(x))) stop("effects missing required columns")
if(nrow(x)!=201 || length(unique(x$family))!=45 || length(unique(x$trait_name))!=12)
  stop("effects do not match frozen core")
if(any(!is.finite(x$S3_rho)) || any(!is.finite(x$prune_only_rho))) stop("nonfinite rho")

x$system_id <- paste(x$family,x$trait_name,sep="||")
stack <- rbind(
  data.frame(family=x$family,trait_name=x$trait_name,system_id=x$system_id,backbone="S3",rho=x$S3_rho,stringsAsFactors=FALSE),
  data.frame(family=x$family,trait_name=x$trait_name,system_id=x$system_id,backbone="prune_only",rho=x$prune_only_rho,stringsAsFactors=FALSE)
)
stack$family <- factor(stack$family)
stack$trait_name <- factor(stack$trait_name)
stack$system_id <- factor(stack$system_id)
stack$backbone <- factor(stack$backbone,levels=c("S3","prune_only"))

fit_raw <- function(dat){
  lmer(rho ~ backbone + (1|family) + (1|trait_name) + (1|system_id),
       data=dat,REML=TRUE,
       control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
}
fit_z <- function(dat){
  z <- dat
  z$rho <- ave(z$rho,z$backbone,FUN=function(v)(v-mean(v))/sd(v))
  lmer(rho ~ 1 + (1|family) + (1|trait_name) + (1|system_id),
       data=z,REML=TRUE,
       control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
}
summarize_fit <- function(fit){
  vc <- as.data.frame(VarCorr(fit))
  getv <- function(g){
    z <- vc$vcov[vc$grp==g]
    if(length(z)!=1 || !is.finite(z)) return(NA_real_)
    as.numeric(z)
  }
  vf<-getv("family"); vt<-getv("trait_name"); vs<-getv("system_id"); vr<-sigma(fit)^2
  if(any(!is.finite(c(vf,vt,vs,vr)))) stop("variance extraction failed")
  total<-vf+vt+vs+vr
  cond<-if((vs+vr)>0) vs/(vs+vr) else NA_real_
  stable<-(vf+vt+vs)/total
  list(
    variance_family=vf,variance_trait=vt,variance_system=vs,variance_residual=vr,total_variance=total,
    share_family=vf/total,share_trait=vt/total,share_system_total=vs/total,share_residual=vr/total,
    conditional_system_stability=cond,backbone_stable_total_share=stable,backbone_specific_share=vr/total
  )
}

fit <- fit_raw(stack)
singular <- isSingular(fit,tol=as.numeric(exec$real_model_gate$singular_tolerance))
if(singular){
  out<-list(version="v0.1.1",status="HOLD_BACKBONE_STABLE_CONTEXT_SINGULAR_REAL_MODEL",
            post_outcome_supporting_analysis=TRUE,n_systems=201,n_families=45,n_traits=12,
            gate_pass=FALSE)
  write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
  cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
  quit(status=0)
}
primary <- summarize_fit(fit)
fx <- fixef(fit)
prune_shift <- as.numeric(fx[grep("^backbone",names(fx))[1]])
intercept <- as.numeric(fx[["(Intercept)"]])

fitz <- fit_z(stack)
z_singular <- isSingular(fitz,tol=as.numeric(exec$real_model_gate$singular_tolerance))
zsum <- if(z_singular) NULL else summarize_fit(fitz)

# Parametric bootstrap under the fitted raw-rho repeated-measures model.
B <- as.integer(exec$bootstrap$replicates)
set.seed(as.integer(exec$bootstrap$master_seed))
families <- levels(stack$family); traits <- levels(stack$trait_name); systems <- levels(stack$system_id)
fam_idx<-as.integer(stack$family); trait_idx<-as.integer(stack$trait_name); sys_idx<-as.integer(stack$system_id)
back_ind<-as.integer(stack$backbone=="prune_only")
nf<-length(families); nt<-length(traits); ns<-length(systems); n<-nrow(stack)
sd_f<-sqrt(primary$variance_family); sd_t<-sqrt(primary$variance_trait)
sd_s<-sqrt(primary$variance_system); sd_e<-sqrt(primary$variance_residual)

boot <- data.frame(
  replicate=seq_len(B),valid=FALSE,singular=FALSE,
  conditional_system_stability=NA_real_,share_system_total=NA_real_,
  backbone_stable_total_share=NA_real_,backbone_specific_share=NA_real_,
  prune_mean_shift=NA_real_,stringsAsFactors=FALSE
)
for(b in seq_len(B)){
  uf<-if(sd_f>0)rnorm(nf,0,sd_f) else rep(0,nf)
  ut<-if(sd_t>0)rnorm(nt,0,sd_t) else rep(0,nt)
  us<-if(sd_s>0)rnorm(ns,0,sd_s) else rep(0,ns)
  eps<-if(sd_e>0)rnorm(n,0,sd_e) else rep(0,n)
  y<-intercept + prune_shift*back_ind + uf[fam_idx]+ut[trait_idx]+us[sys_idx]+eps
  dat<-stack; dat$rho<-y
  fb<-tryCatch(fit_raw(dat),error=function(e)NULL)
  if(is.null(fb)) next
  sb<-isSingular(fb,tol=as.numeric(exec$real_model_gate$singular_tolerance))
  boot$singular[b]<-sb
  if(sb) next
  sm<-tryCatch(summarize_fit(fb),error=function(e)NULL)
  if(is.null(sm)) next
  fxb<-fixef(fb)
  pidx<-grep("^backbone",names(fxb))[1]
  if(length(pidx)!=1 || !is.finite(fxb[pidx])) next
  boot$valid[b]<-TRUE
  boot$conditional_system_stability[b]<-sm$conditional_system_stability
  boot$share_system_total[b]<-sm$share_system_total
  boot$backbone_stable_total_share[b]<-sm$backbone_stable_total_share
  boot$backbone_specific_share[b]<-sm$backbone_specific_share
  boot$prune_mean_shift[b]<-as.numeric(fxb[pidx])
}
write.csv(boot,boot_path,row.names=FALSE,na="")
valid<-boot$valid
vfraction<-mean(valid)
qci<-function(v){
  z<-v[valid & is.finite(v)]
  if(!length(z)) c(NA_real_,NA_real_) else as.numeric(quantile(z,c(.025,.975),names=FALSE,type=7))
}
cis<-list(
  conditional_system_stability=as.list(qci(boot$conditional_system_stability)),
  share_system_total=as.list(qci(boot$share_system_total)),
  backbone_stable_total_share=as.list(qci(boot$backbone_stable_total_share)),
  backbone_specific_share=as.list(qci(boot$backbone_specific_share)),
  prune_mean_shift=as.list(qci(boot$prune_mean_shift))
)
gate<-vfraction>=as.numeric(exec$real_model_gate$bootstrap_valid_fraction_min)

# Leave-one-trait and leave-one-family descriptive robustness.
loo_rows<-list(); k<-0L
for(tr in sort(unique(x$trait_name))){
  keep<-x$trait_name!=tr
  subx<-x[keep,,drop=FALSE]
  dat<-rbind(
    data.frame(family=subx$family,trait_name=subx$trait_name,system_id=paste(subx$family,subx$trait_name,sep="||"),backbone="S3",rho=subx$S3_rho),
    data.frame(family=subx$family,trait_name=subx$trait_name,system_id=paste(subx$family,subx$trait_name,sep="||"),backbone="prune_only",rho=subx$prune_only_rho)
  )
  dat$family<-factor(dat$family);dat$trait_name<-factor(dat$trait_name);dat$system_id<-factor(dat$system_id);dat$backbone<-factor(dat$backbone,levels=c("S3","prune_only"))
  fl<-tryCatch(fit_raw(dat),error=function(e)NULL)
  k<-k+1L
  if(is.null(fl)||isSingular(fl,tol=1e-4)){
    loo_rows[[k]]<-data.frame(kind="trait",omitted=tr,n_systems=nrow(subx),valid=FALSE,conditional_system_stability=NA,share_system_total=NA)
  } else {
    sm<-summarize_fit(fl)
    loo_rows[[k]]<-data.frame(kind="trait",omitted=tr,n_systems=nrow(subx),valid=TRUE,conditional_system_stability=sm$conditional_system_stability,share_system_total=sm$share_system_total)
  }
}
for(fam in sort(unique(x$family))){
  keep<-x$family!=fam
  subx<-x[keep,,drop=FALSE]
  dat<-rbind(
    data.frame(family=subx$family,trait_name=subx$trait_name,system_id=paste(subx$family,subx$trait_name,sep="||"),backbone="S3",rho=subx$S3_rho),
    data.frame(family=subx$family,trait_name=subx$trait_name,system_id=paste(subx$family,subx$trait_name,sep="||"),backbone="prune_only",rho=subx$prune_only_rho)
  )
  dat$family<-factor(dat$family);dat$trait_name<-factor(dat$trait_name);dat$system_id<-factor(dat$system_id);dat$backbone<-factor(dat$backbone,levels=c("S3","prune_only"))
  fl<-tryCatch(fit_raw(dat),error=function(e)NULL)
  k<-k+1L
  if(is.null(fl)||isSingular(fl,tol=1e-4)){
    loo_rows[[k]]<-data.frame(kind="family",omitted=fam,n_systems=nrow(subx),valid=FALSE,conditional_system_stability=NA,share_system_total=NA)
  } else {
    sm<-summarize_fit(fl)
    loo_rows[[k]]<-data.frame(kind="family",omitted=fam,n_systems=nrow(subx),valid=TRUE,conditional_system_stability=sm$conditional_system_stability,share_system_total=sm$share_system_total)
  }
}
loo<-do.call(rbind,loo_rows)
write.csv(loo,loo_path,row.names=FALSE,na="")
loo_good<-loo$valid & is.finite(loo$conditional_system_stability)
loo_summary<-list(
  n_trait_omissions=sum(loo$kind=="trait"),
  n_family_omissions=sum(loo$kind=="family"),
  valid_fraction=mean(loo$valid),
  conditional_system_stability_range=if(any(loo_good))as.list(range(loo$conditional_system_stability[loo_good])) else list(NULL,NULL),
  share_system_total_range=if(any(loo$valid & is.finite(loo$share_system_total)))as.list(range(loo$share_system_total[loo$valid & is.finite(loo$share_system_total)])) else list(NULL,NULL)
)

status<-if(gate)"BACKBONE_STABLE_CONTEXT_ESTIMATED" else "HOLD_BACKBONE_STABLE_CONTEXT_BOOTSTRAP"
out<-list(
  version="v0.1.1",status=status,post_outcome_supporting_analysis=TRUE,
  n_systems=201,n_families=45,n_traits=12,n_observations=402,
  raw_rho_model=list(
    fixed_intercept=intercept,prune_mean_shift=prune_shift,
    variance=primary,singular=FALSE
  ),
  bootstrap=list(
    replicates=B,valid_replicates=sum(valid),valid_fraction=vfraction,
    ci95=cis,master_seed=as.integer(exec$bootstrap$master_seed)
  ),
  z_standardized_sensitivity=if(is.null(zsum))list(singular=TRUE) else list(
    singular=FALSE,conditional_system_stability=zsum$conditional_system_stability,
    share_system_total=zsum$share_system_total,backbone_stable_total_share=zsum$backbone_stable_total_share,
    backbone_specific_share=zsum$backbone_specific_share
  ),
  leave_one_out=loo_summary,
  gate_pass=gate,
  no_dominance_test_performed=TRUE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
