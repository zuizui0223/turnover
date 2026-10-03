#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path<-getarg("--effects")
out_path<-getarg("--out")
boot_path<-getarg("--bootstrap-table")
loo_path<-getarg("--loo-table")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(boot_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(loo_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_repeatability_design_v0_1.json"),simplifyVector=FALSE)
mi<-fromJSON(file.path(root,"results","trait_memory_repeatability_model_info_v0_1","result.json"),simplifyVector=FALSE)
if(!identical(mi$status,"TRAIT_MEMORY_REPEATABILITY_MODEL_INFORMATIVENESS_PASS") || !isTRUE(mi$gate_pass))
  stop("repeatability model-informativeness prerequisite failed")

x<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
req<-c("family","trait_name","S3_rho","prune_only_rho")
if(!all(req %in% names(x)))stop("effect table missing columns")
if(nrow(x)!=201 || length(unique(x$family))!=45 || length(unique(x$trait_name))!=12)
  stop("frozen core dimensions mismatch")
if(any(!is.finite(x$S3_rho))||any(!is.finite(x$prune_only_rho)))stop("nonfinite rho")

fit_data<-function(y,ff=x$family,tt=x$trait_name){
  dat<-data.frame(rho=as.numeric(y),family=factor(ff),trait_name=factor(tt))
  lmer(rho~1+(1|family)+(1|trait_name),data=dat,REML=TRUE,
       control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
}
shares<-function(fit){
  vc<-as.data.frame(VarCorr(fit))
  vf<-vc$vcov[vc$grp=="family"][1]
  vt<-vc$vcov[vc$grp=="trait_name"][1]
  vr<-sigma(fit)^2
  if(length(vf)==0||length(vt)==0||!all(is.finite(c(vf,vt,vr))))stop("variance extraction failed")
  total<-vf+vt+vr
  if(total<=0)stop("nonpositive total variance")
  list(
    var_family=vf,var_trait=vt,var_residual=vr,
    R_family=vf/total,R_trait=vt/total,R_residual=vr/total,
    singular=isSingular(fit,tol=1e-4)
  )
}

fit<-fit_data(x$S3_rho)
primary<-shares(fit)

B<-as.integer(d$real_analysis_if_admitted$uncertainty |> sub(" parametric bootstrap replicates under seed 20261003","",x=_))
# JSON string parsing above is brittle; enforce the frozen numeric count directly.
B<-2000L
seed0<-20261003L
set.seed(seed0)
families<-levels(factor(x$family)); traits<-levels(factor(x$trait_name))
fam_idx<-match(x$family,families); trait_idx<-match(x$trait_name,traits)
mu<-as.numeric(fixef(fit)[["(Intercept)"]])
sd_f<-sqrt(primary$var_family); sd_t<-sqrt(primary$var_trait); sd_e<-sqrt(primary$var_residual)
n<-nrow(x)

boot<-data.frame(
  replicate=seq_len(B),success=FALSE,singular=FALSE,
  R_family=NA_real_,R_trait=NA_real_,R_residual=NA_real_,
  stringsAsFactors=FALSE
)
for(b in seq_len(B)){
  uf<-if(sd_f>0)rnorm(length(families),0,sd_f)else rep(0,length(families))
  ut<-if(sd_t>0)rnorm(length(traits),0,sd_t)else rep(0,length(traits))
  eps<-if(sd_e>0)rnorm(n,0,sd_e)else rep(0,n)
  y<-mu+uf[fam_idx]+ut[trait_idx]+eps
  fb<-tryCatch(fit_data(y),error=function(e)NULL)
  if(is.null(fb))next
  sh<-tryCatch(shares(fb),error=function(e)NULL)
  if(is.null(sh))next
  boot$success[b]<-TRUE
  boot$singular[b]<-sh$singular
  boot$R_family[b]<-sh$R_family
  boot$R_trait[b]<-sh$R_trait
  boot$R_residual[b]<-sh$R_residual
}
write.csv(boot,boot_path,row.names=FALSE,na="")
success<-boot$success
success_fraction<-mean(success)
ci<-function(z)as.numeric(quantile(z[success],c(.025,.975),type=7,na.rm=TRUE,names=FALSE))
if(success_fraction<0.90){
  status<-"HOLD_TRAIT_MEMORY_REPEATABILITY_BOOTSTRAP"
  cis<-list(R_family=c(NA,NA),R_trait=c(NA,NA),R_residual=c(NA,NA))
  gate<-FALSE
}else{
  status<-"TRAIT_MEMORY_REPEATABILITY_ESTIMATED"
  cis<-list(R_family=ci(boot$R_family),R_trait=ci(boot$R_trait),R_residual=ci(boot$R_residual))
  gate<-TRUE
}

fitp<-fit_data(x$prune_only_rho)
prune<-shares(fitp)

# Pre-frozen leave-one-out descriptive robustness.
loo_rows<-list(); k<-0L
for(tr in sort(unique(x$trait_name))){
  keep<-x$trait_name!=tr
  if(length(unique(x$trait_name[keep]))<2||length(unique(x$family[keep]))<2)next
  fl<-tryCatch(fit_data(x$S3_rho[keep],x$family[keep],x$trait_name[keep]),error=function(e)NULL)
  k<-k+1L
  if(is.null(fl)){
    loo_rows[[k]]<-data.frame(kind="trait",omitted=tr,n_systems=sum(keep),success=FALSE,singular=NA,R_family=NA,R_trait=NA,R_residual=NA)
  }else{
    sh<-shares(fl)
    loo_rows[[k]]<-data.frame(kind="trait",omitted=tr,n_systems=sum(keep),success=TRUE,singular=sh$singular,R_family=sh$R_family,R_trait=sh$R_trait,R_residual=sh$R_residual)
  }
}
for(fm in sort(unique(x$family))){
  keep<-x$family!=fm
  if(length(unique(x$trait_name[keep]))<2||length(unique(x$family[keep]))<2)next
  fl<-tryCatch(fit_data(x$S3_rho[keep],x$family[keep],x$trait_name[keep]),error=function(e)NULL)
  k<-k+1L
  if(is.null(fl)){
    loo_rows[[k]]<-data.frame(kind="family",omitted=fm,n_systems=sum(keep),success=FALSE,singular=NA,R_family=NA,R_trait=NA,R_residual=NA)
  }else{
    sh<-shares(fl)
    loo_rows[[k]]<-data.frame(kind="family",omitted=fm,n_systems=sum(keep),success=TRUE,singular=sh$singular,R_family=sh$R_family,R_trait=sh$R_trait,R_residual=sh$R_residual)
  }
}
loo<-do.call(rbind,loo_rows)
write.csv(loo,loo_path,row.names=FALSE,na="")
finite_range<-function(v){
  z<-v[is.finite(v)]
  if(!length(z))list(min=NULL,max=NULL)else list(min=min(z),max=max(z))
}

out<-list(
  version="v0.2",
  status=status,
  real_memory_effects_opened=TRUE,
  n_systems=nrow(x),n_families=length(families),n_traits=length(traits),
  primary_S3=primary,
  bootstrap=list(
    replicates=B,success_fraction=success_fraction,successful=sum(success),
    singular_fraction_among_success=if(any(success))mean(boot$singular[success])else NULL,
    ci95=cis,master_seed=seed0
  ),
  prune_only_sensitivity=prune,
  leave_one_out=list(
    n_leave_one_trait=sum(loo$kind=="trait"),
    n_leave_one_family=sum(loo$kind=="family"),
    R_family_range=finite_range(loo$R_family),
    R_trait_range=finite_range(loo$R_trait)
  ),
  dominance_comparison_performed=FALSE,
  dominance_label=NULL,
  analysis_gate_pass=gate,
  raw_trait_measurements_persisted=FALSE,
  species_states_persisted=FALSE,
  species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
