#!/usr/bin/env Rscript
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
suppressPackageStartupMessages({
  library(jsonlite)
  library(lme4)
  library(Matrix)
  library(MASS)
})
args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path <- getarg("--effects")
aggregate_json <- getarg("--aggregate-json")
out_path <- getarg("--out")
null_path <- getarg("--null-table")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(null_path),recursive=TRUE,showWarnings=FALSE)

design <- fromJSON("data/trait_memory_robustness_design_v0_3.json",simplifyVector=FALSE)
agg <- fromJSON(aggregate_json,simplifyVector=FALSE)
if(!identical(agg$status,"TRAIT_MEMORY_ROBUST_EFFECTS_AGGREGATED")) stop("robust aggregate did not pass")
x <- read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=201 || length(unique(x$family))!=45 || length(unique(x$trait_name))!=12)
  stop("frozen graph changed")

fit_shares <- function(y,trait_group=x$trait_name){
  d <- data.frame(rho=as.numeric(y),family=factor(x$family),trait_group=factor(trait_group))
  f <- lmer(rho~1+(1|family)+(1|trait_group),data=d,REML=TRUE,
            control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
  vc <- as.data.frame(VarCorr(f))
  vf <- vc$vcov[vc$grp=="family"][1]
  vt <- vc$vcov[vc$grp=="trait_group"][1]
  vr <- sigma(f)^2
  tot <- vf+vt+vr
  list(
    R_family=vf/tot,R_trait_group=vt/tot,R_residual=vr/tot,
    var_family=vf,var_trait_group=vt,var_residual=vr,
    singular=isSingular(f,tol=1e-4)
  )
}

blocks <- lapply(design$correlated_trait_family_null$predeclared_trait_blocks,unlist)
all_traits <- sort(unique(x$trait_name))
blocked <- unique(unlist(blocks))
singletons <- setdiff(all_traits,blocked)
min_overlap <- as.integer(design$correlated_trait_family_null$parameter_estimation$minimum_pair_overlap)
B <- as.integer(design$correlated_trait_family_null$simulation$replicates)
seed0 <- as.integer(design$correlated_trait_family_null$simulation$master_seed)

axis_null <- function(y,axis_name,axis_seed){
  fams <- sort(unique(x$family))
  trts <- sort(unique(x$trait_name))
  wide <- matrix(NA_real_,nrow=length(fams),ncol=length(trts),dimnames=list(fams,trts))
  for(i in seq_len(nrow(x))) wide[x$family[[i]],x$trait_name[[i]]] <- as.numeric(y[[i]])
  mu <- colMeans(wide,na.rm=TRUE)
  sdev <- apply(wide,2,sd,na.rm=TRUE)
  if(any(!is.finite(mu)) || any(!is.finite(sdev)) || any(sdev<=0)) stop("invalid trait moments")

  block_info <- list()
  cov_blocks <- list()
  for(bi in seq_along(blocks)){
    tr <- blocks[[bi]]
    if(!all(tr %in% trts)) stop("predeclared block trait missing")
    R <- diag(length(tr)); dimnames(R) <- list(tr,tr)
    overlap <- matrix(0L,length(tr),length(tr),dimnames=list(tr,tr))
    diag(overlap) <- colSums(!is.na(wide[,tr,drop=FALSE]))
    if(length(tr)>1){
      for(i in seq_len(length(tr)-1)){
        for(j in (i+1):length(tr)){
          ok <- is.finite(wide[,tr[[i]]]) & is.finite(wide[,tr[[j]]])
          overlap[i,j] <- overlap[j,i] <- sum(ok)
          if(sum(ok)<min_overlap) stop(paste("block pair overlap below frozen minimum",tr[[i]],tr[[j]],sum(ok)))
          rr <- cor(wide[ok,tr[[i]]],wide[ok,tr[[j]]],method="pearson")
          if(!is.finite(rr)) stop("nonfinite block correlation")
          R[i,j] <- R[j,i] <- rr
        }
      }
    }
    eig_before <- eigen(R,symmetric=TRUE,only.values=TRUE)$values
    projected <- any(eig_before <= 1e-10)
    Rpd <- if(projected) as.matrix(nearPD(R,corr=TRUE,keepDiag=TRUE)$mat) else R
    D <- diag(sdev[tr],nrow=length(tr))
    Sigma <- D %*% Rpd %*% D
    cov_blocks[[bi]] <- list(traits=tr,Sigma=Sigma)
    block_info[[bi]] <- list(
      traits=tr,
      raw_correlation=unname(split(as.data.frame(R),seq_len(nrow(R)))),
      overlap=unname(split(as.data.frame(overlap),seq_len(nrow(overlap)))),
      min_eigen_before_projection=min(eig_before),
      projected_to_nearPD=projected,
      regularized_correlation=unname(split(as.data.frame(Rpd),seq_len(nrow(Rpd))))
    )
  }

  obs <- fit_shares(y)
  set.seed(axis_seed)
  null <- data.frame(
    replicate=seq_len(B),success=FALSE,R_family=NA_real_,R_trait=NA_real_,R_residual=NA_real_,
    singular=FALSE,stringsAsFactors=FALSE
  )
  for(r in seq_len(B)){
    simwide <- matrix(NA_real_,nrow=length(fams),ncol=length(trts),dimnames=list(fams,trts))
    for(fi in seq_along(fams)){
      for(bi in seq_along(cov_blocks)){
        tr <- cov_blocks[[bi]]$traits
        z <- mvrnorm(1,mu=mu[tr],Sigma=cov_blocks[[bi]]$Sigma,tol=1e-10)
        simwide[fi,tr] <- z
      }
      for(tr in singletons) simwide[fi,tr] <- rnorm(1,mu[[tr]],sdev[[tr]])
    }
    ys <- vapply(seq_len(nrow(x)),function(i) simwide[x$family[[i]],x$trait_name[[i]]],numeric(1))
    fs <- tryCatch(fit_shares(ys),error=function(e)NULL)
    if(is.null(fs)) next
    null$success[[r]] <- TRUE
    null$R_family[[r]] <- fs$R_family
    null$R_trait[[r]] <- fs$R_trait_group
    null$R_residual[[r]] <- fs$R_residual
    null$singular[[r]] <- fs$singular
  }
  ok <- null$success
  if(mean(ok)<0.90) stop("correlated-trait null fit success below 0.90")
  p <- (1+sum(null$R_family[ok]>=obs$R_family))/(1+sum(ok))
  list(
    summary=list(
      axis=axis_name,
      observed=obs,
      null_replicates=B,
      success_fraction=mean(ok),
      R_family_null_median=median(null$R_family[ok]),
      R_family_null_q025_q975=as.numeric(quantile(null$R_family[ok],c(.025,.975),names=FALSE)),
      p_family_ge_observed=p,
      block_parameters=block_info,
      singleton_traits=singletons
    ),
    table=transform(null,axis=axis_name)
  )
}

s3 <- axis_null(x$S3_raw_rho,"S3",seed0+1L)
pr <- axis_null(x$prune_raw_rho,"prune_only",seed0+2L)
write.csv(rbind(s3$table,pr$table),null_path,row.names=FALSE,na="")

# Secondary trait-domain sensitivity.
domains <- design$trait_domain_sensitivity$domains
domain_map <- c()
for(nm in names(domains)){
  z <- unlist(domains[[nm]])
  domain_map[z] <- nm
}
if(!all(x$trait_name %in% names(domain_map))) stop("trait-domain map incomplete")
td <- unname(domain_map[x$trait_name])
domain_s3 <- fit_shares(x$S3_raw_rho,td)
domain_pr <- fit_shares(x$prune_raw_rho,td)

out <- list(
  version="v0.3",
  status="TRAIT_MEMORY_CORRELATED_TRAIT_NULL_ESTIMATED",
  null_type="outcome_covariance_preserving_block_null",
  true_family_main_effect_zero_by_construction=TRUE,
  S3=s3$summary,
  prune_only=pr$summary,
  trait_domain_sensitivity=list(
    n_domains=length(unique(td)),
    S3=domain_s3,
    prune_only=domain_pr,
    descriptive_only=TRUE
  ),
  interpretation_guard="This is a statistical dependence null for the repeatability estimator, not a mechanistic multivariate trait-evolution model."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17)
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17),"\n")
