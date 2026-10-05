#!/usr/bin/env Rscript
# Diagnostic only: reproduce the frozen first two-way cluster-bootstrap replicate and print fit errors.
suppressPackageStartupMessages({
  library(jsonlite)
  library(metafor)
  library(lme4)
})
args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path <- getarg("--effects")
x <- read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
design <- fromJSON("data/trait_memory_robustness_design_v0_3.json",simplifyVector=FALSE)
seed0 <- as.integer(design$measurement_error$uncertainty$seed)

naive_fit <- function(y,ff,tt){
  dat <- data.frame(rho=as.numeric(y),family=factor(ff),trait_name=factor(tt))
  lmer(rho~1+(1|family)+(1|trait_name),data=dat,REML=TRUE,
       control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
}
meta_fit <- function(y,se,ff,tt,ss){
  d <- data.frame(yi=as.numeric(y),vi=as.numeric(se)^2,
                  family=factor(ff),trait_name=factor(tt),system_id=factor(ss))
  rma.mv(yi=yi,V=vi,
         random=list(~1|family,~1|trait_name,~1|system_id),
         data=d,method="REML")
}

families <- sort(unique(x$family)); traits <- sort(unique(x$trait_name))
key <- paste(x$family,x$trait_name,sep="\r")
idx_map <- setNames(seq_len(nrow(x)),key)

set.seed(seed0)
fd <- sample(families,length(families),replace=TRUE)
td <- sample(traits,length(traits),replace=TRUE)
yy <- c(); ss <- c(); ff <- c(); tt <- c(); sid <- c()
kk <- 0L
for(i in seq_along(fd)){
  for(j in seq_along(td)){
    z <- idx_map[paste(fd[[i]],td[[j]],sep="\r")]
    if(length(z)==0 || is.na(z[[1]])) next
    z <- unname(z[[1]])
    kk <- kk+1L
    yy[[kk]] <- x$S3_raw_rho[[z]]
    ss[[kk]] <- x$S3_raw_se[[z]]
    ff[[kk]] <- paste0("F",i)
    tt[[kk]] <- paste0("T",j)
    sid[[kk]] <- paste0("B1_",kk)
  }
}
cat("rows=",kk,
    " family_levels=",length(unique(ff)),
    " trait_levels=",length(unique(tt)),
    " se_min=",min(as.numeric(ss)),
    " se_max=",max(as.numeric(ss)),"\n",sep="")

try_one <- function(label,expr){
  ans <- tryCatch(
    { fit <- eval(expr); list(ok=TRUE,message="OK",fit=fit) },
    error=function(e) list(ok=FALSE,message=conditionMessage(e),fit=NULL),
    warning=function(w) {cat(label," warning: ",conditionMessage(w),"\n",sep=""); invokeRestart("muffleWarning")}
  )
  cat(label," ok=",ans$ok," message=",ans$message,"\n",sep="")
  if(ans$ok){
    if(inherits(ans$fit,"merMod")) print(VarCorr(ans$fit))
    if(inherits(ans$fit,"rma.mv")) print(ans$fit$sigma2)
  }
  invisible(ans)
}
try_one("naive",quote(naive_fit(yy,ff,tt)))
try_one("meta",quote(meta_fit(yy,ss,ff,tt,sid)))
