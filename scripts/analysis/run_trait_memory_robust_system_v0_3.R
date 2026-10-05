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
out_path <- getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","trait_memory_robustness_design_v0_3.json"),simplifyVector=FALSE)
if(!identical(design$status,"FROZEN_BEFORE_TRAIT_MEMORY_ROBUSTNESS_OUTCOMES"))
  stop("robustness design not frozen")
B <- as.integer(design$measurement_error$replicates)
seed0 <- as.integer(design$measurement_error$master_seed)
if(B != 199L) stop("bootstrap replicate count drifted")

core <- read.csv(file.path(root,"results","trait_memory_crossed_core_v0_6","core_systems.csv"),
                 stringsAsFactors=FALSE,check.names=FALSE)
row <- core[core$family==family & core$trait_name==trait_name,,drop=FALSE]
if(nrow(row)!=1) stop("system is not a unique final crossed-core member")
if(as.character(row$semantic_class[[1]])!="continuous_scalar")
  stop("v0.3 robustness route is continuous-scalar only")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed before robustness extraction")

esc <- function(x) gsub("'","''",x,fixed=TRUE)
famq <- esc(family); trq <- esc(trait_name)
sql <- sprintf("
  WITH base AS (
    SELECT scrubbed_species_binomial AS species,
           scrubbed_genus AS genus,
           scrubbed_family AS family,
           CASE WHEN trait_value::text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
                THEN trait_value::numeric ELSE NULL END AS value_num
    FROM agg_traits
    WHERE scrubbed_family='%s' AND trait_name='%s'
      AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
      AND scrubbed_genus IS NOT NULL AND trim(scrubbed_genus)<>''
      AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
      AND unit IS NOT NULL AND trim(unit::text)<>''
      AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
  )
  SELECT species,genus,family,
         percentile_cont(0.5) WITHIN GROUP(ORDER BY value_num) AS state_num
  FROM base WHERE value_num IS NOT NULL
  GROUP BY species,genus,family
  ORDER BY species;
",famq,trq)

sp <- .BIEN_sql(sql)
if(!is.data.frame(sp) || nrow(sp)<20) stop("species-state extraction fell below 20")
sp$state_num <- as.numeric(sp$state_num)
if(any(!is.finite(sp$state_num))) stop("nonfinite species medians")

capture.output(
  phy <- phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
                     tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                     output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
  file=tempfile()
)
if(is.null(phy$scenario.3) || is.null(phy$species.list)) stop("phylo.maker failed")
st <- as.character(phy$species.list$status)
keep_primary <- st %in% c("prune","bind")
keep_prune <- st=="prune"
if(sum(keep_primary)<20 || sum(keep_prune)<20) stop("frozen crosswalk thresholds no longer met")

norm_first <- function(x) gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species <- function(x) norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip <- norm_species(as.character(sp$species))
state_map <- setNames(sp$state_num,sp$tip)

tree_s3 <- phy$scenario.3
prune_names <- norm_species(as.character(phy$species.list$species[keep_prune]))
tree_prune <- keep.tip(GBOTB.extended.TPL,prune_names)

safe_spearman <- function(sep,diss){
  z <- suppressWarnings(cor(sep,diss,method="spearman",use="complete.obs"))
  if(!is.finite(z)) return(NA_real_)
  as.numeric(z)
}

weighted_midranks <- function(group_id,weights,n_groups){
  gw <- tabulate(group_id,nbins=n_groups,weights=weights)
  before <- c(0,head(cumsum(gw),-1))
  mid <- before + (gw+1)/2
  mid[group_id]
}

weighted_spearman_counts <- function(counts,pair_i,pair_j,gx,gy,nx,ny){
  w_self <- counts*(counts-1)/2
  w_pair <- counts[pair_i]*counts[pair_j]
  w <- c(w_self,w_pair)
  N <- sum(w)
  if(!is.finite(N) || N<=1) return(NA_real_)
  rx <- weighted_midranks(gx,w,nx)
  ry <- weighted_midranks(gy,w,ny)
  mu <- (N+1)/2
  dx <- rx-mu; dy <- ry-mu
  vx <- sum(w*dx*dx)
  vy <- sum(w*dy*dy)
  if(vx<=0 || vy<=0) return(NA_real_)
  z <- sum(w*dx*dy)/sqrt(vx*vy)
  if(!is.finite(z)) return(NA_real_)
  as.numeric(z)
}

axis_summary <- function(tree,axis_seed){
  tips <- tree$tip.label
  state_raw <- unname(state_map[tips])
  if(any(!is.finite(state_raw))) stop("missing continuous state after tree mapping")
  D <- cophenetic.phylo(tree)
  sep0 <- as.numeric(as.dist(D))
  raw_obs <- safe_spearman(sep0,as.numeric(dist(state_raw)))
  if(!is.finite(raw_obs)) stop("nonfinite raw rho")

  log_ok <- all(state_raw > 0)
  state_log <- if(log_ok) log(state_raw) else rep(NA_real_,length(state_raw))
  log_obs <- if(log_ok) safe_spearman(sep0,as.numeric(dist(state_log))) else NA_real_

  # Exact species-bootstrap Spearman without expanding duplicate bootstrap tips.
  # A bootstrap sample with species counts c_i contains c_i*c_j copies of each
  # original i-j pair and choose(c_i,2) self-copy pairs with distance/dissimilarity 0.
  # Weighted average ranks on these fixed value categories are exactly the ranks
  # obtained from the fully expanded bootstrap sample.
  n <- length(state_raw)
  ij <- which(lower.tri(D),arr.ind=TRUE)
  pair_i <- ij[,1]; pair_j <- ij[,2]
  sep_cat <- c(rep(0,n),D[ij])
  raw_diss_cat <- c(rep(0,n),abs(state_raw[pair_i]-state_raw[pair_j]))
  gx <- match(sep_cat,sort(unique(sep_cat)))
  gy_raw <- match(raw_diss_cat,sort(unique(raw_diss_cat)))
  nx <- max(gx); ny_raw <- max(gy_raw)
  if(log_ok){
    log_diss_cat <- c(rep(0,n),abs(state_log[pair_i]-state_log[pair_j]))
    gy_log <- match(log_diss_cat,sort(unique(log_diss_cat)))
    ny_log <- max(gy_log)
  } else {
    gy_log <- NULL; ny_log <- NULL
  }

  raw_boot <- rep(NA_real_,B)
  log_boot <- rep(NA_real_,B)
  set.seed(axis_seed)
  for(b in seq_len(B)){
    counts <- tabulate(sample.int(n,n,replace=TRUE),nbins=n)
    raw_boot[b] <- weighted_spearman_counts(counts,pair_i,pair_j,gx,gy_raw,nx,ny_raw)
    if(log_ok) log_boot[b] <- weighted_spearman_counts(counts,pair_i,pair_j,gx,gy_log,nx,ny_log)
  }
  raw_good <- is.finite(raw_boot)
  log_good <- is.finite(log_boot)
  min_valid <- as.numeric(design$measurement_error$valid_fraction_min)
  raw_vf <- mean(raw_good)
  log_vf <- if(log_ok) mean(log_good) else 0
  raw_se <- if(raw_vf>=min_valid) sd(raw_boot[raw_good]) else NA_real_
  log_se <- if(log_ok && log_vf>=min_valid) sd(log_boot[log_good]) else NA_real_

  list(
    n_species=n,
    raw_rho=raw_obs,
    raw_bootstrap_se=raw_se,
    raw_bootstrap_valid_fraction=raw_vf,
    log_status=if(log_ok) "LOG_POSITIVE" else "LOG_HOLD_NONPOSITIVE_STATE",
    n_nonpositive=sum(state_raw<=0),
    log_rho=if(log_ok) log_obs else NULL,
    log_bootstrap_se=if(log_ok && is.finite(log_se)) log_se else NULL,
    log_bootstrap_valid_fraction=if(log_ok) log_vf else NULL,
    bootstrap_implementation="exact_weighted_midrank_equivalent_to_expanded_species_bootstrap"
  )
}

num_id <- suppressWarnings(as.integer(gsub("[^0-9]","",system_id)))
if(!is.finite(num_id)) stop("system id lacks numeric component")
s3 <- axis_summary(tree_s3,seed0 + num_id*10L + 1L)
pr <- axis_summary(tree_prune,seed0 + num_id*10L + 2L)

status <- "TRAIT_MEMORY_ROBUST_SYSTEM_ESTIMATED"
if(!is.finite(s3$raw_bootstrap_se) || !is.finite(pr$raw_bootstrap_se))
  status <- "HOLD_TRAIT_MEMORY_ROBUST_BOOTSTRAP_VALIDITY"

out <- list(
  version="v0.3",
  status=status,
  system_id=system_id,
  family=family,
  trait_name=trait_name,
  semantic_class="continuous_scalar",
  observed_database_version=observed_version,
  bootstrap=list(
    unit="species_cluster",
    replicates=B,
    master_seed=seed0,
    pairwise_resampling_used=FALSE
  ),
  S3=s3,
  prune_only=pr,
  raw_trait_measurements_persisted=FALSE,
  species_states_persisted=FALSE,
  species_names_persisted=FALSE
)
txt <- toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17)
writeLines(txt,out_path)
cat(txt,"\n")
