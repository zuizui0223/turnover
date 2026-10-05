#!/usr/bin/env Rscript
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
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
system_id <- getarg("--id")
crosswalk_path <- getarg("--crosswalk")
systems_table_path <- getarg("--systems-table")
out_path <- getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

design <- fromJSON("data/phylo_memory_mk2_generator_design_v0_4_1.json",simplifyVector=FALSE)
if(!identical(design$status,"FROZEN_BEFORE_MK2_GENERATOR_RESULT_OPENING")) stop("Mk2 design not frozen")
target <- as.numeric(design$generator$calibration_target_rho)
tol <- as.numeric(design$generator$calibration_tolerance_rho)
minvf <- as.numeric(design$generator$valid_replicate_fraction_min)
grid <- as.numeric(unlist(design$generator$grid))
pilot_reps <- as.integer(design$generator$pilot_replicates_per_candidate)
eval_reps <- as.integer(design$generator$evaluation_replicates)
maxstep <- 20L

sys <- read.csv(systems_table_path,stringsAsFactors=FALSE,check.names=FALSE)
src <- sys[sys$system_id==system_id & sys$family==family & sys$trait_name==trait_name,,drop=FALSE]
if(nrow(src)!=1) stop("system is not unique in frozen v0.2 systems table")
if(as.character(src$semantic_class[[1]])!="nominal_categorical") stop("Mk2 test is categorical only")

cw <- read.csv(crosswalk_path,stringsAsFactors=FALSE,check.names=FALSE)
flag <- tolower(trimws(as.character(cw$crosswalk_pass))) %in% c("true","t","1")
row <- cw[flag & cw$family==family & cw$trait_name==trait_name,,drop=FALSE]
if(nrow(row)!=1) stop("system is not a unique crosswalk-PASS candidate")
if(as.character(row$semantic_class[[1]])!="nominal_categorical") stop("crosswalk class mismatch")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed before Mk2 generator test")

esc <- function(x) gsub("'","''",x,fixed=TRUE)
famq <- esc(family); trq <- esc(trait_name)
sql <- sprintf("
  WITH counts AS (
    SELECT scrubbed_species_binomial AS species,
           scrubbed_genus AS genus,
           scrubbed_family AS family,
           trait_value::text AS value_text,
           count(*) AS n
    FROM agg_traits
    WHERE scrubbed_family='%s' AND trait_name='%s'
      AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
      AND scrubbed_genus IS NOT NULL AND trim(scrubbed_genus)<>''
      AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
      AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
    GROUP BY scrubbed_species_binomial,scrubbed_genus,scrubbed_family,trait_value::text
  ), ranked AS (
    SELECT *,max(n) OVER(PARTITION BY species) AS max_n FROM counts
  ), modes AS (
    SELECT species,genus,family,count(*) FILTER(WHERE n=max_n) AS n_modal
    FROM ranked GROUP BY species,genus,family
  )
  SELECT species,genus,family FROM modes WHERE n_modal=1 ORDER BY species;
",famq,trq)
sp <- .BIEN_sql(sql)
if(!is.data.frame(sp) || nrow(sp)<20) stop("categorical species query failed or fell below 20")
sp <- unique(sp[,c("species","genus","family"),drop=FALSE])

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
if(nrow(sp)!=as.integer(src$n_input_species[[1]]) || n_prune!=as.integer(src$n_prune[[1]]))
  stop("rebuilt geometry disagrees with frozen v0.2 systems table")
if(n_prune!=as.integer(row$n_prune[[1]]) ||
   n_bind!=as.integer(row$n_bind[[1]]) ||
   n_fail!=as.integer(row$n_fail_to_bind[[1]]))
  stop("rebuilt geometry disagrees with frozen crosswalk")

tr <- reorder.phylo(phy$scenario.3,"cladewise")
if(is.null(tr$edge.length) || any(!is.finite(tr$edge.length)) || any(tr$edge.length<0)) stop("invalid S3 edge lengths")
D <- cophenetic.phylo(tr)
dvec <- as.numeric(as.dist(D))
pos <- dvec[is.finite(dvec) & dvec>0]
if(!length(pos)) stop("no positive patristic distance")
med_dist <- median(pos)
rx <- rank(dvec,ties.method="average")
meanrx <- mean(rx)
sxx <- sum((rx-meanrx)^2)
if(!is.finite(sxx) || sxx<=0) stop("zero pair-distance rank variance")
n <- length(tr$tip.label)
M <- length(rx)
Rmat <- matrix(0,n,n)
Rmat[lower.tri(Rmat)] <- rx
Rmat <- Rmat + t(Rmat)
rm(D,dvec,rx); gc(FALSE)

fnv1a32_unsigned <- function(key){
  h <- 2166136261
  bytes <- as.integer(charToRaw(enc2utf8(key)))
  for(b in bytes){
    low8 <- h %% 256
    h <- h - low8 + bitwXor(as.integer(low8),as.integer(b))
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
   fnv1a32_unsigned("foobar") != 3214735720) stop("FNV self-test failed")
fnv_seed <- function(key) as.integer((fnv1a32_unsigned(key) %% 2147483646)+1)

make_randoms <- function(reps,key){
  E <- nrow(tr$edge)
  set.seed(fnv_seed(key))
  list(root=runif(reps)<0.5, U=matrix(runif(E*reps),nrow=E,ncol=reps))
}

simulate_mk2 <- function(eta,rnd){
  if(!is.finite(eta) || eta<=0) stop("invalid eta")
  q <- eta/med_dist
  E <- nrow(tr$edge)
  nall <- n + tr$Nnode
  vals <- matrix(FALSE,nrow=nall,ncol=length(rnd$root))
  root <- setdiff(tr$edge[,1],tr$edge[,2])
  if(length(root)!=1) stop("tree root not unique")
  vals[root,] <- rnd$root
  for(k in seq_len(E)){
    parent <- tr$edge[k,1]; child <- tr$edge[k,2]
    pflip <- (1-exp(-2*q*tr$edge.length[k]))/2
    if(!is.finite(pflip) || pflip<0 || pflip>0.5+1e-12) stop("invalid Mk2 transition probability")
    vals[child,] <- xor(vals[parent,], rnd$U[k,] < pflip)
  }
  vals[seq_len(n),,drop=FALSE]
}

binary_effects <- function(G){
  n1 <- colSums(G)
  K <- n1*(n-n1)
  valid <- K>0 & K<M
  out <- rep(NA_real_,ncol(G))
  if(any(valid)){
    Gv <- G[,valid,drop=FALSE]*1.0
    cross_sum <- colSums(Gv * (Rmat %*% (1-Gv)))
    Kv <- K[valid]
    den <- sqrt(sxx * Kv * (M-Kv)/M)
    out[valid] <- (cross_sum - Kv*meanrx)/den
  }
  out
}

pilot_stats <- function(eta,rnd){
  eff <- binary_effects(simulate_mk2(eta,rnd))
  good <- is.finite(eff)
  list(median=if(any(good)) median(eff[good]) else NA_real_,
       valid_fraction=mean(good))
}

calibrate <- function(){
  rnd <- make_randoms(pilot_reps,paste(20261004,family,trait_name,"mk2","pilot",sep="|"))
  meds <- rep(NA_real_,length(grid)); vfs <- rep(0,length(grid))
  for(i in seq_along(grid)){
    z <- pilot_stats(grid[i],rnd)
    meds[i] <- z$median; vfs[i] <- z$valid_fraction
  }
  good <- is.finite(meds) & vfs>=minvf
  diag <- lapply(seq_along(grid),function(i)list(eta=grid[i],median_effect=meds[i],valid_fraction=vfs[i]))
  exact <- which(good & abs(meds-target)<=tol)
  if(length(exact)){
    i <- exact[1]
    return(list(ok=TRUE,eta=grid[i],pilot_median=meds[i],pilot_valid_fraction=vfs[i],grid=diag,bisection_steps=0L))
  }
  bracket <- NA_integer_
  for(i in seq_len(length(grid)-1L)){
    if(good[i] && good[i+1L] && (meds[i]-target)*(meds[i+1L]-target)<=0){
      bracket <- i; break
    }
  }
  if(is.na(bracket)) return(list(ok=FALSE,reason="CALIBRATION_NO_BRACKET",grid=diag))
  lo <- grid[bracket]; hi <- grid[bracket+1L]
  mlo <- meds[bracket]; mhi <- meds[bracket+1L]
  for(step in seq_len(maxstep)){
    mid <- exp((log(lo)+log(hi))/2)
    z <- pilot_stats(mid,rnd)
    if(!is.finite(z$median) || z$valid_fraction<minvf)
      return(list(ok=FALSE,reason="CALIBRATION_INVALID_MIDPOINT",grid=diag,bisection_steps=step))
    if(abs(z$median-target)<=tol)
      return(list(ok=TRUE,eta=mid,pilot_median=z$median,pilot_valid_fraction=z$valid_fraction,grid=diag,bisection_steps=step))
    if((mlo-target)*(z$median-target)<=0){
      hi <- mid; mhi <- z$median
    } else {
      lo <- mid; mlo <- z$median
    }
  }
  list(ok=FALSE,reason="CALIBRATION_TOLERANCE_NOT_REACHED",grid=diag,bisection_steps=maxstep)
}

cal <- calibrate()
if(isTRUE(cal$ok)){
  rnd <- make_randoms(eval_reps,paste(20261004,family,trait_name,"mk2","evaluation",sep="|"))
  eff <- binary_effects(simulate_mk2(cal$eta,rnd))
  good <- is.finite(eff)
  vf <- mean(good)
  mae <- if(any(good)) median(abs(eff[good]-target)) else Inf
  directional <- sum(good & eff>0)/length(eff)
  pass <- vf>=as.numeric(design$evaluation_thresholds$valid_replicate_fraction_min) &&
          directional>=as.numeric(design$evaluation_thresholds$directional_recovery_min) &&
          mae<=as.numeric(design$evaluation_thresholds$median_absolute_recovery_error_max)
  eval <- list(valid_fraction=vf,median_absolute_recovery_error=mae,
               directional_recovery=directional,pass=pass,
               hold_reason=if(pass)"" else "RECOVERY_THRESHOLD_FAIL")
} else {
  eval <- list(valid_fraction=NA_real_,median_absolute_recovery_error=NA_real_,
               directional_recovery=NA_real_,pass=FALSE,hold_reason=cal$reason)
}

parse_bool <- function(x) tolower(trimws(as.character(x))) %in% c("true","t","1")
out <- list(
  version="v0.4.1",
  status="PHYLO_MEMORY_MK2_GENERATOR_SYSTEM_ESTIMATED",
  system_id=system_id,family=family,trait_name=trait_name,semantic_class="nominal_categorical",
  outcome_type="known_truth_generator_substitution_only",
  real_trait_values_used=FALSE,real_memory_effects_used=FALSE,
  n_input_species=n,n_prune=n_prune,n_bind=n_bind,n_fail_to_bind=n_fail,
  median_positive_patristic_distance=med_dist,
  original_ou_no_bracket=parse_bool(src$s3_no_bracket[[1]]),
  original_ou_s3_pass=parse_bool(src$s3_pass[[1]]),
  mk2_calibrated=isTRUE(cal$ok),
  mk2_no_bracket=!isTRUE(cal$ok),
  mk2_hold_reason=if(isTRUE(cal$ok)) eval$hold_reason else cal$reason,
  mk2_eta=if(isTRUE(cal$ok)) cal$eta else NA_real_,
  mk2_pilot_median=if(isTRUE(cal$ok)) cal$pilot_median else NA_real_,
  mk2_pilot_valid_fraction=if(isTRUE(cal$ok)) cal$pilot_valid_fraction else NA_real_,
  mk2_bisection_steps=if(isTRUE(cal$ok)) cal$bisection_steps else if(!is.null(cal$bisection_steps)) cal$bisection_steps else 0L,
  mk2_grid=cal$grid,
  mk2_valid_fraction=eval$valid_fraction,
  mk2_median_absolute_recovery_error=eval$median_absolute_recovery_error,
  mk2_directional_recovery=eval$directional_recovery,
  mk2_s3_pass=isTRUE(eval$pass),
  interpretation_guard="Mk2 is a representation-appropriate generator substitution test with the estimator and target held fixed; it is not asserted to be the true evolutionary model for each observed trait."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
