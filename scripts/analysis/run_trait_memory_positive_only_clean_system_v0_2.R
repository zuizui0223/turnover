#!/usr/bin/env Rscript
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this audit script. Author verification is required before use.
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
design <- fromJSON(file.path(root,"data","trait_memory_positive_only_cleaning_impact_design_v0_2.json"),simplifyVector=FALSE)
if(!identical(design$status,"FROZEN_BEFORE_POSITIVE_ONLY_CLEANING_IMPACT_OUTCOMES"))
  stop("Stage B design not frozen")
if(!isTRUE(design$execution_optimization$before_cleaned_effect_outcomes))
  stop("Stage B optimization not frozen before outcomes")

clean_traits <- unlist(design$cleaning_rule$predeclared_positive_only_traits_from_stage_A,use.names=FALSE)
if(!(trait_name %in% clean_traits)) stop("Stage B system runner received a non-cleaned trait")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN database version changed")

esc <- function(x) gsub("'","''",x,fixed=TRUE)
famq <- esc(family); trq <- esc(trait_name)
sql <- sprintf("
WITH base AS (
  SELECT
    scrubbed_species_binomial AS species,
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
),
nb AS (
  SELECT * FROM base WHERE value_num IS NOT NULL
)
SELECT species,min(genus) AS genus,min(family) AS family,
       percentile_cont(0.5) WITHIN GROUP(ORDER BY value_num) AS state_raw,
       percentile_cont(0.5) WITHIN GROUP(ORDER BY value_num) FILTER (WHERE value_num>0) AS state_clean,
       count(*)::integer AS n_records,
       count(*) FILTER (WHERE value_num<=0)::integer AS n_nonpositive_records,
       count(*) FILTER (WHERE value_num>0)::integer AS n_positive_records
FROM nb
GROUP BY species
ORDER BY species;
",famq,trq)

sp <- .BIEN_sql(sql)
if(!is.data.frame(sp) || nrow(sp)<20) stop("Stage B extraction unexpectedly small")
sp$state_raw <- as.numeric(sp$state_raw)
sp$state_clean <- as.numeric(sp$state_clean)
sp$n_records <- as.integer(sp$n_records)
sp$n_nonpositive_records <- as.integer(sp$n_nonpositive_records)
sp$n_positive_records <- as.integer(sp$n_positive_records)
if(any(!is.finite(sp$state_raw))) stop("nonfinite original state")

capture.output(
  phy <- phylo.maker(
    sp[,c("species","genus","family"),drop=FALSE],
    tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
    output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"
  ),
  file=tempfile()
)
if(is.null(phy$scenario.3) || is.null(phy$species.list)) stop("phylo.maker failed")
st <- as.character(phy$species.list$status)
keep_primary <- st %in% c("prune","bind")
keep_prune <- st=="prune"
if(sum(keep_primary)<20 || sum(keep_prune)<20) stop("original frozen crosswalk support changed")

norm_first <- function(x) gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species <- function(x) norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip <- norm_species(as.character(sp$species))
raw_map <- setNames(sp$state_raw,sp$tip)
clean_map <- setNames(sp$state_clean,sp$tip)
raw_nonpos_record_map <- setNames(sp$n_nonpositive_records,sp$tip)

tree_s3 <- phy$scenario.3
prune_names <- norm_species(as.character(phy$species.list$species[keep_prune]))
tree_prune <- keep.tip(GBOTB.extended.TPL,prune_names)

safe_spearman <- function(sep,diss){
  z <- suppressWarnings(cor(sep,diss,method="spearman",use="complete.obs"))
  if(!is.finite(z)) return(NA_real_)
  as.numeric(z)
}

weighted_midranks <- function(group_id,weights,n_groups){
  rs <- rowsum(matrix(weights,ncol=1),group=group_id,reorder=TRUE)
  gw <- numeric(n_groups)
  gw[as.integer(rownames(rs))] <- as.numeric(rs[,1])
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
  vx <- sum(w*dx*dx); vy <- sum(w*dy*dy)
  if(vx<=0 || vy<=0) return(NA_real_)
  z <- sum(w*dx*dy)/sqrt(vx*vy)
  if(!is.finite(z)) return(NA_real_)
  as.numeric(z)
}

B <- as.integer(design$effect_outputs$species_bootstrap_replicates)
seed0 <- 20261008L

axis_summary <- function(tree,axis_seed){
  tips <- tree$tip.label
  state_raw <- unname(raw_map[tips])
  state_clean_all <- unname(clean_map[tips])
  n_nonpos_raw_records <- unname(raw_nonpos_record_map[tips])
  if(any(!is.finite(state_raw))) stop("missing original state on frozen tree")
  D0 <- cophenetic.phylo(tree)
  original_rho <- safe_spearman(as.numeric(as.dist(D0)),as.numeric(dist(state_raw)))
  if(!is.finite(original_rho)) stop("nonfinite original rho")

  valid <- is.finite(state_clean_all)
  clean_tips <- tips[valid]
  n_clean <- length(clean_tips)
  min_n <- as.integer(design$tree_contract$minimum_species_after_cleaning_each_axis)
  if(n_clean < min_n){
    return(list(
      status="HOLD_CLEANED_SYSTEM_SUPPORT",
      original_n_species=length(tips),
      cleaned_n_species=n_clean,
      n_species_removed_for_no_positive_state=sum(!valid),
      original_nonpositive_species=sum(state_raw<=0),
      original_species_with_any_nonpositive_raw=sum(n_nonpos_raw_records>0),
      original_raw_rho=original_rho
    ))
  }

  tree_clean <- if(all(valid)) tree else keep.tip(tree,clean_tips)
  state_clean <- unname(clean_map[tree_clean$tip.label])
  if(any(!is.finite(state_clean)) || any(state_clean<=0))
    stop("cleaned state is not strictly positive")

  D <- cophenetic.phylo(tree_clean)
  sep <- as.numeric(as.dist(D))
  raw_rho <- safe_spearman(sep,as.numeric(dist(state_clean)))
  log_state <- log(state_clean)
  log_rho <- safe_spearman(sep,as.numeric(dist(log_state)))
  if(!is.finite(raw_rho) || !is.finite(log_rho)) stop("nonfinite cleaned rho")

  n <- length(state_clean)
  ij <- which(lower.tri(D),arr.ind=TRUE)
  pair_i <- ij[,1]; pair_j <- ij[,2]
  sep_cat <- c(rep(0,n),D[ij])
  raw_diss <- c(rep(0,n),abs(state_clean[pair_i]-state_clean[pair_j]))
  log_diss <- c(rep(0,n),abs(log_state[pair_i]-log_state[pair_j]))
  gx <- match(sep_cat,sort(unique(sep_cat)))
  gy_raw <- match(raw_diss,sort(unique(raw_diss)))
  gy_log <- match(log_diss,sort(unique(log_diss)))
  nx <- max(gx); ny_raw <- max(gy_raw); ny_log <- max(gy_log)

  raw_boot <- rep(NA_real_,B)
  log_boot <- rep(NA_real_,B)
  set.seed(axis_seed)
  for(b in seq_len(B)){
    counts <- tabulate(sample.int(n,n,replace=TRUE),nbins=n)
    raw_boot[b] <- weighted_spearman_counts(counts,pair_i,pair_j,gx,gy_raw,nx,ny_raw)
    log_boot[b] <- weighted_spearman_counts(counts,pair_i,pair_j,gx,gy_log,nx,ny_log)
  }
  raw_good <- is.finite(raw_boot); log_good <- is.finite(log_boot)
  min_valid <- 0.95
  raw_vf <- mean(raw_good); log_vf <- mean(log_good)
  if(raw_vf<min_valid || log_vf<min_valid)
    stop("cleaned bootstrap validity below frozen threshold")

  list(
    status="CLEANED_EFFECT_ESTIMATED",
    original_n_species=length(tips),
    cleaned_n_species=n,
    n_species_removed_for_no_positive_state=sum(!valid),
    original_nonpositive_species=sum(state_raw<=0),
    original_species_with_any_nonpositive_raw=sum(n_nonpos_raw_records>0),
    original_raw_rho=original_rho,
    cleaned_raw_rho=raw_rho,
    cleaned_raw_se=sd(raw_boot[raw_good]),
    cleaned_raw_boot_valid_fraction=raw_vf,
    cleaned_log_rho=log_rho,
    cleaned_log_se=sd(log_boot[log_good]),
    cleaned_log_boot_valid_fraction=log_vf
  )
}

num_id <- suppressWarnings(as.integer(gsub("[^0-9]","",system_id)))
if(!is.finite(num_id)) stop("system id lacks numeric component")
s3 <- axis_summary(tree_s3,seed0 + num_id*10L + 1L)
pr <- axis_summary(tree_prune,seed0 + num_id*10L + 2L)

status <- if(identical(s3$status,"CLEANED_EFFECT_ESTIMATED") && identical(pr$status,"CLEANED_EFFECT_ESTIMATED"))
  "TRAIT_MEMORY_CLEANED_SYSTEM_ESTIMATED" else "HOLD_CLEANED_SYSTEM_SUPPORT"

out <- list(
  version="v0.2",
  status=status,
  system_id=system_id,
  family=family,
  trait_name=trait_name,
  observed_database_version=observed_version,
  cleaning_rule="raw_value_gt_0_for_stage_A_predeclared_positive_only_trait",
  S3=s3,
  prune_only=pr,
  raw_trait_measurements_persisted=FALSE,
  species_states_persisted=FALSE,
  species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17)
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17),"\n")
