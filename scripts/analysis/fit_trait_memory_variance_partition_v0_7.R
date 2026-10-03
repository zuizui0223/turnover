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
table_path <- getarg("--bootstrap-table")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","trait_memory_real_effect_execution_v0_7.json"),simplifyVector=FALSE)
core <- fromJSON(file.path(root,"results","trait_memory_crossed_core_v0_6","result.json"),simplifyVector=FALSE)
if(!identical(core$status,"TRAIT_MEMORY_CROSSED_CORE_PASS") || !isTRUE(core$gate_pass))
  stop("crossed-core prerequisite did not pass")

x <- read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
req <- c("family","trait_name","semantic_class","S3_rho","prune_only_rho")
if(!all(req %in% names(x))) stop("effect table missing required columns")
if(nrow(x)!=as.integer(core$n_core_systems)) stop("effect row count differs from frozen core")
if(any(!is.finite(x$S3_rho)) || any(!is.finite(x$prune_only_rho))) stop("nonfinite rho")
if(length(unique(x$family))!=as.integer(core$n_core_families)) stop("family count mismatch")
if(length(unique(x$trait_name))!=as.integer(core$n_core_traits)) stop("trait count mismatch")

variance_summary <- function(fit){
  vc <- as.data.frame(VarCorr(fit))
  vf <- vc$vcov[vc$grp=="family"][1]
  vt <- vc$vcov[vc$grp=="trait_name"][1]
  vr <- sigma(fit)^2
  if(length(vf)==0 || length(vt)==0 || !is.finite(vr)) stop("variance extraction failed")
  total <- vf+vt+vr
  logratio <- if(vt==0 && vf>0) -Inf else if(vf==0 && vt>0) Inf else if(vf==0 && vt==0) NA_real_ else log(vt/vf)
  list(family_variance=vf,trait_variance=vt,residual_variance=vr,total_variance=total,
       share_family=if(total>0)vf/total else NA_real_,
       share_trait=if(total>0)vt/total else NA_real_,
       share_residual=if(total>0)vr/total else NA_real_,
       log_variance_ratio=logratio)
}

fit_model <- function(response){
  dat <- data.frame(
    rho=as.numeric(response),
    family=factor(x$family),
    trait_name=factor(x$trait_name)
  )
  lmer(rho ~ 1 + (1|family) + (1|trait_name),data=dat,REML=TRUE,
       control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
}

fit <- fit_model(x$S3_rho)
primary <- variance_summary(fit)

# Parametric bootstrap under the fitted crossed Gaussian random-effects model.
B <- as.integer(design$bootstrap$replicates)
if(B!=2000) stop("unexpected bootstrap replicate count")
set.seed(as.integer(design$bootstrap$master_seed))
n <- nrow(x)
families <- levels(factor(x$family))
traits <- levels(factor(x$trait_name))
fam_idx <- match(x$family,families)
trait_idx <- match(x$trait_name,traits)
mu <- as.numeric(fixef(fit)[["(Intercept)"]])
sd_f <- sqrt(primary$family_variance)
sd_t <- sqrt(primary$trait_variance)
sd_e <- sqrt(primary$residual_variance)

boot <- data.frame(
  replicate=seq_len(B),
  valid=FALSE,
  singular=FALSE,
  family_variance=NA_real_,
  trait_variance=NA_real_,
  residual_variance=NA_real_,
  log_variance_ratio=NA_real_,
  stringsAsFactors=FALSE
)

for(b in seq_len(B)){
  uf <- if(sd_f>0) rnorm(length(families),0,sd_f) else rep(0,length(families))
  ut <- if(sd_t>0) rnorm(length(traits),0,sd_t) else rep(0,length(traits))
  eps <- if(sd_e>0) rnorm(n,0,sd_e) else rep(0,n)
  y <- mu + uf[fam_idx] + ut[trait_idx] + eps
  fb <- tryCatch(fit_model(y),error=function(e) NULL)
  if(is.null(fb)) next
  sing <- isSingular(fb,tol=1e-4)
  boot$singular[b] <- sing
  if(sing) next
  vs <- tryCatch(variance_summary(fb),error=function(e) NULL)
  if(is.null(vs)) next
  lr <- vs$log_variance_ratio
  if(is.na(lr)) next
  boot$valid[b] <- TRUE
  boot$family_variance[b] <- vs$family_variance
  boot$trait_variance[b] <- vs$trait_variance
  boot$residual_variance[b] <- vs$residual_variance
  boot$log_variance_ratio[b] <- lr
}

write.csv(boot,table_path,row.names=FALSE,na="")
valid <- boot$valid
valid_fraction <- mean(valid)
if(valid_fraction < 0.90){
  status <- "HOLD_TRAIT_MEMORY_MODEL_UNCERTAINTY"
  architecture <- "UNRESOLVED"
  ci <- c(NA_real_,NA_real_)
  gate <- FALSE
} else {
  lr <- boot$log_variance_ratio[valid]
  ci <- as.numeric(quantile(lr,probs=c(0.025,0.975),type=7,names=FALSE,na.rm=TRUE))
  if(primary$family_variance==0 && primary$trait_variance==0){
    architecture <- "UNSTRUCTURED"
  } else if(ci[1]>0){
    architecture <- "TRAIT_DOMINANT"
  } else if(ci[2]<0){
    architecture <- "LINEAGE_DOMINANT"
  } else {
    architecture <- "MIXED"
  }
  status <- "TRAIT_MEMORY_VARIANCE_ARCHITECTURE_ESTIMATED"
  gate <- TRUE
}

# Mandatory prune-only sensitivity on the identical core.
fit_prune <- fit_model(x$prune_only_rho)
prune <- variance_summary(fit_prune)

# Secondary semantic-class model only if pre-frozen identifiability rule is met.
tab_cls <- table(x$semantic_class)
trait_cls <- tapply(x$trait_name,x$semantic_class,function(z)length(unique(z)))
secondary_allowed <- length(tab_cls)>=2 &&
  all(tab_cls>=10) &&
  all(trait_cls[names(tab_cls)]>=2)
secondary <- list(run=FALSE)
if(secondary_allowed){
  dat <- data.frame(
    rho=as.numeric(x$S3_rho),
    semantic_class=factor(x$semantic_class),
    family=factor(x$family),
    trait_name=factor(x$trait_name)
  )
  fs <- lmer(rho ~ semantic_class + (1|family) + (1|trait_name),data=dat,REML=TRUE,
             control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
  secondary <- list(
    run=TRUE,
    fixed_effects=as.list(setNames(as.numeric(fixef(fs)),names(fixef(fs)))),
    singular=isSingular(fs,tol=1e-4)
  )
}

out <- list(
  version="v0.7",
  status=status,
  real_memory_effects_opened=TRUE,
  n_systems=nrow(x),
  n_families=length(unique(x$family)),
  n_traits=length(unique(x$trait_name)),
  primary_S3=primary,
  bootstrap=list(
    replicates=B,
    valid_replicates=sum(valid),
    valid_fraction=valid_fraction,
    ci95_log_variance_ratio=as.list(ci),
    master_seed=as.integer(design$bootstrap$master_seed)
  ),
  architecture=architecture,
  prune_only_sensitivity=prune,
  semantic_class_secondary=secondary,
  model_gate_pass=gate,
  raw_trait_measurements_persisted=FALSE,
  species_states_persisted=FALSE,
  species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
