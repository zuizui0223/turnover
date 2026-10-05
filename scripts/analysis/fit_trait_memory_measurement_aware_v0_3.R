#!/usr/bin/env Rscript
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
suppressPackageStartupMessages({
  library(jsonlite)
  library(metafor)
  library(lme4)
})

args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){
  i <- match(flag,args)
  if(is.na(i)||i==length(args)) stop(paste("missing",flag))
  args[[i+1]]
}
effects_path <- getarg("--effects")
aggregate_json <- getarg("--aggregate-json")
out_path <- getarg("--out")
boot_path <- getarg("--bootstrap-table")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(boot_path),recursive=TRUE,showWarnings=FALSE)

design <- fromJSON("data/trait_memory_robustness_design_v0_3.json",simplifyVector=FALSE)
agg <- fromJSON(aggregate_json,simplifyVector=FALSE)
if(!identical(agg$status,"TRAIT_MEMORY_ROBUST_EFFECTS_AGGREGATED"))
  stop("robust effect aggregate did not pass")
x <- read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=201 || length(unique(x$family))!=45 || length(unique(x$trait_name))!=12)
  stop("frozen core dimensions mismatch")
if(anyDuplicated(x$system_id)) stop("system ids not unique")

naive_fit <- function(y,ff=x$family,tt=x$trait_name){
  d <- data.frame(rho=as.numeric(y),family=factor(ff),trait_name=factor(tt))
  f <- lmer(rho~1+(1|family)+(1|trait_name),data=d,REML=TRUE,
            control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
  vc <- as.data.frame(VarCorr(f))
  vf <- vc$vcov[vc$grp=="family"][1]
  vt <- vc$vcov[vc$grp=="trait_name"][1]
  vr <- sigma(f)^2
  tot <- vf+vt+vr
  list(var_family=vf,var_trait=vt,var_residual=vr,
       R_family=vf/tot,R_trait=vt/tot,R_residual=vr/tot,
       singular=isSingular(f,tol=1e-4))
}

meta_fit <- function(y,se,ff=x$family,tt=x$trait_name,ss=x$system_id){
  d <- data.frame(
    yi=as.numeric(y),vi=as.numeric(se)^2,
    family=factor(ff),trait_name=factor(tt),system_id=factor(ss)
  )
  if(any(!is.finite(d$yi)) || any(!is.finite(d$vi)) || any(d$vi<=0))
    stop("invalid yi/vi for meta model")
  f <- rma.mv(
    yi=yi,V=vi,
    random=list(~1|family,~1|trait_name,~1|system_id),
    data=d,method="REML"
  )
  s <- as.numeric(f$sigma2)
  if(length(s)!=3 || any(!is.finite(s)) || any(s<0))
    stop("unexpected meta-analysis variance components")
  names(s) <- c("family","trait","system")
  h <- sum(s)
  mean_vi <- mean(d$vi)
  median_vi <- median(d$vi)
  list(
    fit=f,
    summary=list(
      intercept=as.numeric(coef(f)[1]),
      intercept_se=as.numeric(f$se[1]),
      sigma2_family=s[["family"]],
      sigma2_trait=s[["trait"]],
      sigma2_system=s[["system"]],
      heterogeneity_total=h,
      family_share_heterogeneity=if(h>0)s[["family"]]/h else NA_real_,
      trait_share_heterogeneity=if(h>0)s[["trait"]]/h else NA_real_,
      system_share_heterogeneity=if(h>0)s[["system"]]/h else NA_real_,
      mean_sampling_variance=mean_vi,
      median_sampling_variance=median_vi,
      sampling_share_mean_total=mean_vi/(h+mean_vi),
      sampling_share_median_total=median_vi/(h+median_vi)
    )
  )
}

s3_raw <- meta_fit(x$S3_raw_rho,x$S3_raw_se)
pr_raw <- meta_fit(x$prune_raw_rho,x$prune_raw_se)
naive_s3 <- naive_fit(x$S3_raw_rho)
naive_pr <- naive_fit(x$prune_raw_rho)

log_complete <- all(x$S3_log_status=="LOG_POSITIVE") &&
                all(x$prune_log_status=="LOG_POSITIVE") &&
                all(is.finite(x$S3_log_rho)) && all(is.finite(x$S3_log_se)) &&
                all(is.finite(x$prune_log_rho)) && all(is.finite(x$prune_log_se))
log_s3 <- NULL; log_pr <- NULL; naive_log_s3 <- NULL; naive_log_pr <- NULL
if(log_complete){
  log_s3 <- meta_fit(x$S3_log_rho,x$S3_log_se)$summary
  log_pr <- meta_fit(x$prune_log_rho,x$prune_log_se)$summary
  naive_log_s3 <- naive_fit(x$S3_log_rho)
  naive_log_pr <- naive_fit(x$prune_log_rho)
}

# Two-way family x trait cluster bootstrap for primary S3 measurement-aware model.
B <- as.integer(design$measurement_error$uncertainty$replicates)
seed0 <- as.integer(design$measurement_error$uncertainty$seed)
set.seed(seed0)
families <- sort(unique(x$family))
traits <- sort(unique(x$trait_name))
key <- paste(x$family,x$trait_name,sep="\r")
idx_map <- setNames(seq_len(nrow(x)),key)

boot <- data.frame(
  replicate=seq_len(B),success=FALSE,
  sigma2_family=NA_real_,sigma2_trait=NA_real_,sigma2_system=NA_real_,
  family_share_heterogeneity=NA_real_,
  trait_share_heterogeneity=NA_real_,
  system_share_heterogeneity=NA_real_,
  sampling_share_mean_total=NA_real_,
  naive_R_family=NA_real_,naive_R_trait=NA_real_,naive_R_residual=NA_real_,
  stringsAsFactors=FALSE
)

for(b in seq_len(B)){
  fd <- sample(families,length(families),replace=TRUE)
  td <- sample(traits,length(traits),replace=TRUE)
  yy <- c(); ss <- c(); ff <- c(); tt <- c(); sid <- c()
  kk <- 0L
  for(i in seq_along(fd)){
    for(j in seq_along(td)){
      z <- idx_map[[paste(fd[[i]],td[[j]],sep="\r")]]
      if(is.null(z) || is.na(z)) next
      kk <- kk+1L
      yy[[kk]] <- x$S3_raw_rho[[z]]
      ss[[kk]] <- x$S3_raw_se[[z]]
      ff[[kk]] <- paste0("F",i)
      tt[[kk]] <- paste0("T",j)
      sid[[kk]] <- paste0("B",b,"_",kk)
    }
  }
  if(kk<50 || length(unique(ff))<2 || length(unique(tt))<2) next
  fitb <- tryCatch(meta_fit(yy,ss,ff,tt,sid),error=function(e)NULL)
  if(is.null(fitb)) next
  q <- fitb$summary
  boot$success[[b]] <- TRUE
  boot$sigma2_family[[b]] <- q$sigma2_family
  boot$sigma2_trait[[b]] <- q$sigma2_trait
  boot$sigma2_system[[b]] <- q$sigma2_system
  boot$family_share_heterogeneity[[b]] <- q$family_share_heterogeneity
  boot$trait_share_heterogeneity[[b]] <- q$trait_share_heterogeneity
  boot$system_share_heterogeneity[[b]] <- q$system_share_heterogeneity
  boot$sampling_share_mean_total[[b]] <- q$sampling_share_mean_total
  nb <- tryCatch(naive_fit(yy,ff,tt),error=function(e)NULL)
  if(!is.null(nb)){
    boot$naive_R_family[[b]] <- nb$R_family
    boot$naive_R_trait[[b]] <- nb$R_trait
    boot$naive_R_residual[[b]] <- nb$R_residual
  }
}
write.csv(boot,boot_path,row.names=FALSE,na="")
ok <- boot$success
success_fraction <- mean(ok)
if(success_fraction < as.numeric(design$measurement_error$uncertainty$min_success_fraction))
  stop("cluster bootstrap success fraction below frozen minimum")
ci <- function(v) as.numeric(quantile(v[ok],c(.025,.975),na.rm=TRUE,names=FALSE,type=7))

primary_ci <- list(
  sigma2_family=ci(boot$sigma2_family),
  sigma2_trait=ci(boot$sigma2_trait),
  sigma2_system=ci(boot$sigma2_system),
  family_share_heterogeneity=ci(boot$family_share_heterogeneity),
  trait_share_heterogeneity=ci(boot$trait_share_heterogeneity),
  system_share_heterogeneity=ci(boot$system_share_heterogeneity),
  sampling_share_mean_total=ci(boot$sampling_share_mean_total),
  naive_R_family=ci(boot$naive_R_family),
  naive_R_trait=ci(boot$naive_R_trait),
  naive_R_residual=ci(boot$naive_R_residual)
)

out <- list(
  version="v0.3",
  status="TRAIT_MEMORY_MEASUREMENT_AWARE_ESTIMATED",
  n_systems=nrow(x),n_families=length(families),n_traits=length(traits),
  original_naive_reference=list(
    R_family=0.1504,R_trait=0.0433,R_residual=0.8063
  ),
  recomputed_naive=list(S3=naive_s3,prune_only=naive_pr),
  measurement_aware=list(
    S3=s3_raw$summary,
    prune_only=pr_raw$summary,
    primary_S3_cluster_bootstrap=list(
      replicates=B,success_fraction=success_fraction,ci95=primary_ci,seed=seed0
    )
  ),
  log_scale=list(
    complete_all_201=log_complete,
    measurement_aware_S3=log_s3,
    measurement_aware_prune_only=log_pr,
    naive_S3=naive_log_s3,
    naive_prune_only=naive_log_pr
  ),
  interpretation_guard="Sampling variance is separated from between-system heterogeneity. Do not equate the original lmer residual share with biological system specificity."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17)
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17),"\n")
