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
core_path <- getarg("--core-table")
out_path <- getarg("--out")
table_path <- getarg("--table-out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
d <- fromJSON(file.path(root,"data","backbone_stable_context_model_info_v0_1.json"),simplifyVector=FALSE)
core <- read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(core)!=201) stop("unexpected core size")
if(length(unique(core$family))!=45 || length(unique(core$trait_name))!=12) stop("core dimensions mismatch")
core$system_id <- paste(core$family,core$trait_name,sep="||")

stack <- rbind(
  data.frame(family=core$family,trait_name=core$trait_name,system_id=core$system_id,backbone="S3",stringsAsFactors=FALSE),
  data.frame(family=core$family,trait_name=core$trait_name,system_id=core$system_id,backbone="prune_only",stringsAsFactors=FALSE)
)
stack$family <- factor(stack$family)
stack$trait_name <- factor(stack$trait_name)
stack$system_id <- factor(stack$system_id)
stack$backbone <- factor(stack$backbone,levels=c("S3","prune_only"))

fit_once <- function(y){
  dat <- stack
  dat$rho <- y
  tryCatch(
    lmer(rho ~ backbone + (1|family) + (1|trait_name) + (1|system_id),
         data=dat,REML=TRUE,
         control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000))),
    error=function(e) NULL
  )
}
summarize_fit <- function(fit){
  if(is.null(fit) || isSingular(fit,tol=1e-4)) return(NULL)
  vc <- as.data.frame(VarCorr(fit))
  getv <- function(g){
    z <- vc$vcov[vc$grp==g]
    if(length(z)!=1 || !is.finite(z)) return(NA_real_)
    as.numeric(z)
  }
  vf<-getv("family"); vt<-getv("trait_name"); vs<-getv("system_id"); vr<-sigma(fit)^2
  if(any(!is.finite(c(vf,vt,vs,vr)))) return(NULL)
  cs <- if((vs+vr)>0) vs/(vs+vr) else NA_real_
  list(vf=vf,vt=vt,vs=vs,vr=vr,conditional=cs)
}

B <- as.integer(d$replicates_per_benchmark)
seed0 <- as.integer(d$master_seed)
mu <- as.numeric(d$common_parameters$intercept)
beta <- as.numeric(d$common_parameters$prune_mean_shift)
vf_true <- as.numeric(d$common_parameters$family_variance)
vt_true <- as.numeric(d$common_parameters$trait_variance)
fam_idx <- as.integer(stack$family)
trait_idx <- as.integer(stack$trait_name)
sys_idx <- as.integer(stack$system_id)
back_ind <- as.integer(stack$backbone=="prune_only")
nf<-nlevels(stack$family); nt<-nlevels(stack$trait_name); ns<-nlevels(stack$system_id); n<-nrow(stack)

cases <- names(d$benchmarks)
all_rows <- list()
summaries <- list()

for(ci in seq_along(cases)){
  nm <- cases[[ci]]
  bm <- d$benchmarks[[nm]]
  vs_true <- as.numeric(bm$system_variance)
  vr_true <- as.numeric(bm$residual_variance)
  target <- as.numeric(bm$target_conditional_system_stability)
  set.seed(seed0 + ci - 1L)
  est <- rep(NA_real_,B)
  singular <- rep(FALSE,B)
  failed <- rep(FALSE,B)
  for(i in seq_len(B)){
    uf <- rnorm(nf,0,sqrt(vf_true))
    ut <- rnorm(nt,0,sqrt(vt_true))
    us <- rnorm(ns,0,sqrt(vs_true))
    eps <- rnorm(n,0,sqrt(vr_true))
    y <- mu + beta*back_ind + uf[fam_idx] + ut[trait_idx] + us[sys_idx] + eps
    fit <- fit_once(y)
    if(is.null(fit)){ failed[i] <- TRUE; next }
    if(isSingular(fit,tol=1e-4)){ singular[i] <- TRUE; next }
    sm <- summarize_fit(fit)
    if(is.null(sm) || !is.finite(sm$conditional)) next
    est[i] <- sm$conditional
  }
  valid <- is.finite(est)
  vfraction <- mean(valid)
  medae <- if(any(valid)) median(abs(est[valid]-target)) else Inf
  pass <- vfraction >= as.numeric(d$admission$valid_nonsingular_fraction_min) &&
          medae <= as.numeric(d$admission$median_absolute_error_conditional_stability_max)
  summaries[[nm]] <- list(
    target_conditional_system_stability=target,
    valid_fraction=vfraction,
    median_estimate=if(any(valid)) median(est[valid]) else NULL,
    median_absolute_error=medae,
    singular_fraction=mean(singular),
    failed_fraction=mean(failed),
    pass=pass
  )
  all_rows[[ci]] <- data.frame(
    benchmark=nm,replicate=seq_len(B),valid=valid,singular=singular,failed=failed,
    estimate_conditional_system_stability=est,target=target,stringsAsFactors=FALSE
  )
}

tab <- do.call(rbind,all_rows)
write.csv(tab,table_path,row.names=FALSE,na="")
required <- unlist(d$admission$required_benchmarks)
gate <- all(vapply(required,function(z)isTRUE(summaries[[z]]$pass),logical(1)))
out <- list(
  version="v0.1",
  status=if(gate)"BACKBONE_STABLE_CONTEXT_MODEL_INFO_PASS" else "HOLD_BACKBONE_STABLE_CONTEXT_MODEL_INFO",
  post_outcome_supporting_design=TRUE,
  real_stability_decomposition_opened=FALSE,
  n_systems=201,
  n_families=45,
  n_traits=12,
  observations=402,
  replicates_per_benchmark=B,
  benchmarks=summaries,
  gate_pass=gate,
  next_gate=if(gate)"Fit the frozen repeated-measures decomposition to the already-opened 201 paired S3/prune effects." else "Do not use the repeated-measures decomposition to strengthen the synthesis."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
