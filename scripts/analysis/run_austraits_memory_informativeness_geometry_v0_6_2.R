#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(ape)
  library(V.PhyloMaker2)
})

args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){
  i <- match(flag,args)
  if(is.na(i) || i==length(args)) stop(paste("missing",flag))
  args[[i+1]]
}
family <- getarg("--family")
trait_name <- getarg("--trait")
config_type <- getarg("--config-type")
semantic_class <- if(config_type=="numeric") "continuous_scalar" else if(config_type=="categorical") "nominal_categorical" else stop("unsupported config type")
geometry_id <- getarg("--geometry-id")
geometry_hash <- getarg("--geometry-hash")
species_path <- getarg("--species-table")
expected_prune <- as.integer(getarg("--expected-prune"))
expected_bind <- as.integer(getarg("--expected-bind"))
out_path <- getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","bien_informativeness_design_v0_4.json"),simplifyVector=FALSE)
exec <- fromJSON(file.path(root,"data","bien_informativeness_execution_v0_4_2.json"),simplifyVector=FALSE)
repdesign <- fromJSON(file.path(root,"data","austraits_memory_informativeness_v0_6.json"),simplifyVector=FALSE)
dedup <- fromJSON(file.path(root,"data","austraits_memory_geometry_dedup_v0_6_1.json"),simplifyVector=FALSE)
if(!identical(repdesign$status,"FROZEN_BEFORE_AUSTRAITS_INFORMATIVENESS_RESULT")) stop("replication informativeness contract missing")
if(!identical(dedup$status,"AUSTRAITS_GEOMETRY_DEDUP_CANONICALIZATION_FROZEN_PRE_RESULT")) stop("geometry dedup contract missing")

sp <- read.csv(species_path,stringsAsFactors=FALSE,check.names=FALSE)
if(!all(c("species","genus","family") %in% names(sp))) stop("species table missing required columns")
sp <- unique(sp[,c("species","genus","family"),drop=FALSE])
if(nrow(sp)<20) stop("species table fell below 20")

capture.output(
  phy <- phylo.maker(sp,tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                     output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
  file=tempfile()
)
if(is.null(phy$species.list) || is.null(phy$scenario.3)) stop("phylo.maker did not return S3 tree/species list")
st <- as.character(phy$species.list$status)
n_prune <- sum(st=="prune",na.rm=TRUE)
n_bind <- sum(st=="bind",na.rm=TRUE)
n_fail <- sum(st=="fail to bind",na.rm=TRUE)
expected_fail <- nrow(sp) - expected_prune - expected_bind
if(expected_fail < 0) stop("invalid frozen crosswalk status counts")
status_match <- n_prune==expected_prune && n_bind==expected_bind && n_fail==expected_fail
if(!status_match) stop(sprintf("phylo.maker status counts disagree with frozen exact crosswalk: observed prune/bind/fail=%d/%d/%d expected=%d/%d/%d",n_prune,n_bind,n_fail,expected_prune,expected_bind,expected_fail))

norm_first <- function(x) gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species <- function(x) norm_first(gsub(" ","_",x,fixed=TRUE))
prune_names <- norm_species(as.character(phy$species.list$species[st=="prune"]))
if(length(prune_names)<20) stop("prune-only tips below 20")
if(any(!prune_names %in% GBOTB.extended.TPL$tip.label)) stop("prune species absent from frozen backbone")
tree_s3 <- phy$scenario.3
tree_prune <- keep.tip(GBOTB.extended.TPL,prune_names)

fnv1a32_unsigned <- function(key){
  h <- 2166136261
  bytes <- as.integer(charToRaw(enc2utf8(key)))
  for(b in bytes){
    # XOR affects only the low byte because b is uint8.
    low8 <- h %% 256
    h <- h - low8 + bitwXor(as.integer(low8),as.integer(b))
    # Exact multiply by FNV prime 0x01000193 modulo 2^32 using 16-bit limbs.
    lo <- h %% 65536
    hi <- floor(h/65536)
    prodlo <- lo*403
    newlo <- prodlo %% 65536
    carry <- floor(prodlo/65536)
    newhi <- (carry + lo*256 + hi*403) %% 65536
    h <- newlo + newhi*65536
  }
  h
}
if(fnv1a32_unsigned("") != 2166136261 ||
   fnv1a32_unsigned("a") != 3826002220 ||
   fnv1a32_unsigned("foobar") != 3214735720)
  stop("FNV-1a 32-bit self-test failed")
fnv_seed <- function(key) as.integer((fnv1a32_unsigned(key) %% 2147483646)+1)

prepare_geometry <- function(tree,cls){
  tree <- reorder.phylo(tree,"cladewise")
  if(is.null(tree$edge.length) || any(!is.finite(tree$edge.length)) || any(tree$edge.length<0)) stop("invalid tree edge lengths")
  D <- cophenetic.phylo(tree)
  dvec <- as.numeric(as.dist(D))
  rm(D); gc(FALSE)
  pos <- dvec[dvec>0 & is.finite(dvec)]
  if(length(pos)==0) stop("no positive patristic distances")
  med <- median(pos)
  rx <- rank(dvec,ties.method="average")
  meanrx <- mean(rx)
  sxx <- sum((rx-meanrx)^2)
  if(!is.finite(sxx) || sxx<=0) stop("zero separation rank variance")
  n <- length(tree$tip.label)
  M <- length(rx)
  if(cls=="nominal_categorical"){
    Rmat <- matrix(0,n,n)
    Rmat[lower.tri(Rmat)] <- rx
    Rmat <- Rmat + t(Rmat)
    rm(rx,dvec); gc(FALSE)
    list(tree=tree,med=med,n=n,M=M,meanrx=meanrx,sxx=sxx,Rmat=Rmat,rx=NULL)
  } else {
    rm(dvec); gc(FALSE)
    list(tree=tree,med=med,n=n,M=M,meanrx=meanrx,sxx=sxx,Rmat=NULL,rx=rx)
  }
}

make_Z <- function(geom,reps,key){
  e <- nrow(geom$tree$edge)
  set.seed(fnv_seed(key))
  matrix(rnorm((e+1)*reps),nrow=e+1,ncol=reps)
}

simulate_ou <- function(geom,lambda,Z){
  tr <- geom$tree
  E <- nrow(tr$edge)
  if(nrow(Z)!=(E+1)) stop("innovation matrix dimension mismatch")
  reps <- ncol(Z)
  nt <- length(tr$tip.label); nall <- nt+tr$Nnode
  vals <- matrix(NA_real_,nrow=nall,ncol=reps)
  root <- setdiff(tr$edge[,1],tr$edge[,2])
  if(length(root)!=1) stop("tree root not unique")
  vals[root,] <- Z[1,]
  scale <- lambda * geom$med
  if(!is.finite(scale) || scale<=0) stop("invalid OU scale")
  for(k in seq_len(E)){
    parent <- tr$edge[k,1]; child <- tr$edge[k,2]
    a <- exp(-tr$edge.length[k]/scale)
    sd <- sqrt(max(0,1-a*a))
    vals[child,] <- a*vals[parent,] + sd*Z[k+1,]
  }
  vals[seq_len(nt),,drop=FALSE]
}

continuous_effects <- function(states,geom){
  reps <- ncol(states)
  out <- rep(NA_real_,reps)
  rx <- geom$rx; mx <- geom$meanrx; sxx <- geom$sxx
  for(r in seq_len(reps)){
    yd <- as.numeric(dist(states[,r]))
    if(length(yd)==0 || !all(is.finite(yd)) || max(yd)==min(yd)) next
    ry <- rank(yd,ties.method="average")
    my <- mean(ry)
    syy <- sum((ry-my)^2)
    if(syy<=0) next
    out[r] <- sum((rx-mx)*(ry-my))/sqrt(sxx*syy)
  }
  out
}

binary_effects <- function(states,geom){
  G <- states>0
  n1 <- colSums(G)
  K <- n1*(geom$n-n1)
  valid <- K>0 & K<geom$M
  out <- rep(NA_real_,ncol(states))
  if(any(valid)){
    Gv <- G[,valid,drop=FALSE]*1.0
    cross_sum <- colSums(Gv * (geom$Rmat %*% (1-Gv)))
    Kv <- K[valid]
    den <- sqrt(geom$sxx * Kv * (geom$M-Kv)/geom$M)
    out[valid] <- (cross_sum - Kv*geom$meanrx)/den
  }
  out
}

effects_for <- function(geom,cls,lambda,Z){
  states <- simulate_ou(geom,lambda,Z)
  if(cls=="continuous_scalar") continuous_effects(states,geom) else binary_effects(states,geom)
}

pilot_stats <- function(effects){
  good <- is.finite(effects)
  vf <- mean(good)
  med <- if(any(good)) median(effects[good]) else NA_real_
  list(median=med,valid_fraction=vf)
}

calibrate <- function(geom,cls,axis_key){
  target <- as.numeric(design$canonical_effect$benchmark_delta_rho)
  tol <- as.numeric(design$continuous_scalar_generator$calibration$tolerance_delta_rho)
  minvf <- as.numeric(exec$lambda_search$pilot_valid_fraction_min)
  reps <- as.integer(exec$lambda_search$pilot_replicates_per_value)
  grid <- as.numeric(unlist(exec$lambda_search$lambda_values))
  Z <- make_Z(geom,reps,paste(20260930,family,trait_name,axis_key,"pilot",sep="|"))
  meds <- rep(NA_real_,length(grid)); vfs <- rep(0,length(grid))
  for(i in seq_along(grid)){
    stt <- pilot_stats(effects_for(geom,cls,grid[i],Z))
    meds[i] <- stt$median; vfs[i] <- stt$valid_fraction
  }
  good <- is.finite(meds) & vfs>=minvf
  exact <- which(good & abs(meds-target)<=tol)
  grid_diag <- lapply(seq_along(grid),function(i)list(lambda=grid[i],median_effect=meds[i],valid_fraction=vfs[i]))
  if(length(exact)>0){
    i <- exact[1]
    return(list(ok=TRUE,lambda=grid[i],pilot_median=meds[i],pilot_valid_fraction=vfs[i],grid=grid_diag,bisection_steps=0))
  }
  bracket <- NA_integer_
  if(length(grid)>=2){
    for(i in seq_len(length(grid)-1)){
      if(good[i] && good[i+1] && (meds[i]-target)*(meds[i+1]-target)<=0){ bracket<-i; break }
    }
  }
  if(is.na(bracket)) return(list(ok=FALSE,reason="CALIBRATION_NO_BRACKET",grid=grid_diag))
  lo <- grid[bracket]; hi <- grid[bracket+1]; mlo <- meds[bracket]; mhi <- meds[bracket+1]
  maxstep <- as.integer(design$continuous_scalar_generator$calibration$max_bisection_steps)
  for(step in seq_len(maxstep)){
    mid <- exp((log(lo)+log(hi))/2)
    stt <- pilot_stats(effects_for(geom,cls,mid,Z))
    if(!is.finite(stt$median) || stt$valid_fraction<minvf)
      return(list(ok=FALSE,reason="CALIBRATION_INVALID_MIDPOINT",grid=grid_diag,bisection_steps=step))
    if(abs(stt$median-target)<=tol)
      return(list(ok=TRUE,lambda=mid,pilot_median=stt$median,pilot_valid_fraction=stt$valid_fraction,grid=grid_diag,bisection_steps=step))
    if((mlo-target)*(stt$median-target)<=0){
      hi<-mid; mhi<-stt$median
    } else {
      lo<-mid; mlo<-stt$median
    }
  }
  list(ok=FALSE,reason="CALIBRATION_TOLERANCE_NOT_REACHED",grid=grid_diag,bisection_steps=maxstep)
}

evaluate_geometry <- function(tree,cls,axis_key){
  geom <- prepare_geometry(tree,cls)
  cal <- calibrate(geom,cls,axis_key)
  if(!isTRUE(cal$ok)){
    return(list(axis=axis_key,n_tips=geom$n,calibration=cal,pass=FALSE,hold_reason=cal$reason))
  }
  reps <- as.integer(design$continuous_scalar_generator$evaluation_replicates)
  Z <- make_Z(geom,reps,paste(20260930,family,trait_name,axis_key,"evaluation",sep="|"))
  eff <- effects_for(geom,cls,cal$lambda,Z)
  good <- is.finite(eff)
  vf <- mean(good)
  target <- as.numeric(design$canonical_effect$benchmark_delta_rho)
  mae <- if(any(good)) median(abs(eff[good]-target)) else Inf
  directional <- sum(good & eff>0)/length(eff)
  th <- design$canonical_effect$admission_thresholds
  pass <- vf>=as.numeric(th$valid_replicate_fraction_min) &&
          directional>=as.numeric(th$directional_recovery_min) &&
          mae<=as.numeric(th$median_absolute_recovery_error_max)
  list(axis=axis_key,n_tips=geom$n,lambda=cal$lambda,pilot_median=cal$pilot_median,
       pilot_valid_fraction=cal$pilot_valid_fraction,bisection_steps=cal$bisection_steps,
       median_absolute_recovery_error=mae,directional_recovery=directional,
       valid_replicate_fraction=vf,pass=pass,
       hold_reason=if(pass)"" else "RECOVERY_THRESHOLD_FAIL")
}

prune <- evaluate_geometry(tree_prune,semantic_class,"temporal_prune_only")
if(isTRUE(prune$pass)){
  s3 <- evaluate_geometry(tree_s3,semantic_class,"temporal_s3")
} else {
  s3 <- list(axis="temporal_s3",n_tips=length(tree_s3$tip.label),pass=FALSE,
             hold_reason="SKIPPED_AFTER_PRUNE_FAIL")
}
system_pass <- isTRUE(prune$pass) && isTRUE(s3$pass)

out <- list(
  version="v0.6.2",
  status=if(system_pass)"AUSTRAITS_MEMORY_TEMPORAL_INFORMATIVENESS_GEOMETRY_PASS" else "HOLD_AUSTRAITS_MEMORY_TEMPORAL_INFORMATIVENESS_GEOMETRY",
  geometry_id=geometry_id,geometry_hash=geometry_hash,
  canonical_family=family,canonical_trait_name=trait_name,config_type=config_type,
  semantic_class=semantic_class,
  outcome_blind=TRUE,austraits_memory_effects_opened=FALSE,
  crosswalk_status_counts_match=status_match,
  n_input_species=nrow(sp),n_prune=n_prune,n_bind=n_bind,n_fail_to_bind=n_fail,
  temporal_prune_only=prune,temporal_s3=s3,geometry_temporal_pass=system_pass
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
