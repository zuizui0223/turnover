#!/usr/bin/env Rscript
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
})
args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path <- getarg("--effects")
aggregate_json <- getarg("--aggregate-json")
out_path <- getarg("--out")
pred_path <- getarg("--predictions")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(pred_path),recursive=TRUE,showWarnings=FALSE)

design <- fromJSON("data/trait_memory_robustness_design_v0_3.json",simplifyVector=FALSE)
agg <- fromJSON(aggregate_json,simplifyVector=FALSE)
if(!identical(agg$status,"TRAIT_MEMORY_ROBUST_EFFECTS_AGGREGATED")) stop("robust aggregate did not pass")
x <- read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=201 || length(unique(x$family))!=45 || length(unique(x$trait_name))!=12)
  stop("frozen graph changed")

axis_blup <- function(y,label){
  dat <- data.frame(
    rho=as.numeric(y),
    family=as.character(x$family),
    trait_name=as.character(x$trait_name),
    stringsAsFactors=FALSE
  )
  if(any(!is.finite(dat$rho))) stop(paste(label,"has nonfinite rho"))
  fams <- sort(unique(dat$family))
  pred <- rep(NA_real_,nrow(dat))
  base <- rep(NA_real_,nrow(dat))
  trait_var <- rep(NA_real_,length(fams))
  resid_var <- rep(NA_real_,length(fams))
  fit_singular <- rep(FALSE,length(fams))
  success <- rep(FALSE,length(fams))

  for(k in seq_along(fams)){
    fm <- fams[[k]]
    tr <- dat[dat$family!=fm,,drop=FALSE]
    te_idx <- which(dat$family==fm)
    if(nrow(tr)<50) next
    tr$family <- factor(tr$family)
    tr$trait_name <- factor(tr$trait_name)
    fit <- tryCatch(
      lmer(rho~1+(1|trait_name)+(1|family),data=tr,REML=TRUE,
           control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000))),
      error=function(e) NULL
    )
    if(is.null(fit)) next
    re <- ranef(fit,condVar=FALSE)$trait_name
    mu <- as.numeric(fixef(fit)[["(Intercept)"]])
    base[te_idx] <- mean(tr$rho)
    tnames <- dat$trait_name[te_idx]
    bl <- rep(0,length(te_idx))
    hit <- tnames %in% rownames(re)
    bl[hit] <- re[tnames[hit],"(Intercept)"]
    pred[te_idx] <- mu + bl
    vc <- as.data.frame(VarCorr(fit))
    trait_var[[k]] <- vc$vcov[vc$grp=="trait_name"][1]
    resid_var[[k]] <- sigma(fit)^2
    fit_singular[[k]] <- isSingular(fit,tol=1e-4)
    success[[k]] <- TRUE
  }

  if(!all(success) || any(!is.finite(pred)) || any(!is.finite(base)))
    stop(paste(label,"BLUP LOFO fit failed for at least one family"))

  # Original unshrunk trait-mean predictor on exactly the same LOFO folds.
  unshrunk <- rep(NA_real_,nrow(dat))
  for(fm in fams){
    tr <- dat[dat$family!=fm,,drop=FALSE]
    te_idx <- which(dat$family==fm)
    tm <- tapply(tr$rho,tr$trait_name,mean)
    unshrunk[te_idx] <- unname(tm[dat$trait_name[te_idx]])
  }
  if(any(!is.finite(unshrunk))) stop(paste(label,"unshrunk LOFO predictor failed"))

  sse_base <- sum((dat$rho-base)^2)
  sse_unshrunk <- sum((dat$rho-unshrunk)^2)
  sse_blup <- sum((dat$rho-pred)^2)
  list(
    summary=list(
      axis=label,
      gain_unshrunk=1-sse_unshrunk/sse_base,
      gain_blup=1-sse_blup/sse_base,
      sse_global=sse_base,
      sse_unshrunk=sse_unshrunk,
      sse_blup=sse_blup,
      paired_sse_improvement_blup_vs_unshrunk=sse_unshrunk-sse_blup,
      median_training_trait_variance=median(trait_var),
      q25_q75_training_trait_variance=as.numeric(quantile(trait_var,c(.25,.75),names=FALSE)),
      median_training_residual_variance=median(resid_var),
      singular_fraction=mean(fit_singular)
    ),
    pred=pred,base=base,unshrunk=unshrunk
  )
}

s3 <- axis_blup(x$S3_raw_rho,"S3_raw")
pr <- axis_blup(x$prune_raw_rho,"prune_raw")

log_complete <- all(x$S3_log_status=="LOG_POSITIVE") && all(x$prune_log_status=="LOG_POSITIVE") &&
                all(is.finite(x$S3_log_rho)) && all(is.finite(x$prune_log_rho))
s3log <- NULL; prlog <- NULL
if(log_complete){
  s3log <- axis_blup(x$S3_log_rho,"S3_log")
  prlog <- axis_blup(x$prune_log_rho,"prune_log")
}

pred_rows <- data.frame(
  family=x$family,trait_name=x$trait_name,
  observed_S3_raw=x$S3_raw_rho,
  baseline_S3_raw=s3$base,
  unshrunk_S3_raw=s3$unshrunk,
  blup_S3_raw=s3$pred,
  observed_prune_raw=x$prune_raw_rho,
  baseline_prune_raw=pr$base,
  unshrunk_prune_raw=pr$unshrunk,
  blup_prune_raw=pr$pred,
  stringsAsFactors=FALSE
)
if(log_complete){
  pred_rows$observed_S3_log <- x$S3_log_rho
  pred_rows$baseline_S3_log <- s3log$base
  pred_rows$unshrunk_S3_log <- s3log$unshrunk
  pred_rows$blup_S3_log <- s3log$pred
  pred_rows$observed_prune_log <- x$prune_log_rho
  pred_rows$baseline_prune_log <- prlog$base
  pred_rows$unshrunk_prune_log <- prlog$unshrunk
  pred_rows$blup_prune_log <- prlog$pred
}
write.csv(pred_rows,pred_path,row.names=FALSE)

out <- list(
  version="v0.3",
  status="TRAIT_MEMORY_BLUP_PORTABILITY_SENSITIVITY_ESTIMATED",
  secondary_sensitivity_only=TRUE,
  S3_raw=s3$summary,
  prune_raw=pr$summary,
  log_complete_all_201=log_complete,
  S3_log=if(log_complete)s3log$summary else NULL,
  prune_log=if(log_complete)prlog$summary else NULL,
  interpretation_guard="BLUP sensitivity does not replace or reclassify the frozen v0.2 portability HOLD. It distinguishes noisy unshrunk trait means from genuinely small transferable trait effects."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17)
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17),"\n")
