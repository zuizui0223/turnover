#!/usr/bin/env Rscript
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
semantic_class <- getarg("--class")
system_id <- getarg("--id")
out_path <- getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","trait_memory_real_effect_execution_v0_7.json"),simplifyVector=FALSE)
core <- read.csv(file.path(root,"results","trait_memory_crossed_core_v0_6","core_systems.csv"),stringsAsFactors=FALSE,check.names=FALSE)
row <- core[core$family==family & core$trait_name==trait_name,,drop=FALSE]
if(nrow(row)!=1) stop("system is not a unique final crossed-core member")
if(as.character(row$semantic_class[[1]])!=semantic_class) stop("semantic class mismatch")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed before real effect extraction")

esc <- function(x) gsub("'","''",x,fixed=TRUE)
famq <- esc(family); trq <- esc(trait_name)

if(semantic_class=="continuous_scalar"){
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
} else if(semantic_class=="nominal_categorical"){
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
        AND (unit IS NULL OR trim(unit::text)='')
        AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
      GROUP BY scrubbed_species_binomial,scrubbed_genus,scrubbed_family,trait_value::text
    ), ranked AS (
      SELECT *,max(n) OVER(PARTITION BY species) AS max_n FROM counts
    ), modes AS (
      SELECT species,genus,family,
             count(*) FILTER(WHERE n=max_n) AS n_modal,
             min(value_text) FILTER(WHERE n=max_n) AS state_cat
      FROM ranked GROUP BY species,genus,family
    )
    SELECT species,genus,family,state_cat FROM modes WHERE n_modal=1 ORDER BY species;
  ",famq,trq)
} else stop("unsupported semantic class")

sp <- .BIEN_sql(sql)
if(!is.data.frame(sp) || nrow(sp)<20) stop("species-state extraction fell below 20")

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
state_map_num <- if(semantic_class=="continuous_scalar") setNames(as.numeric(sp$state_num),sp$tip) else NULL
state_map_cat <- if(semantic_class=="nominal_categorical") setNames(as.character(sp$state_cat),sp$tip) else NULL

tree_s3 <- phy$scenario.3
prune_names <- norm_species(as.character(phy$species.list$species[keep_prune]))
tree_prune <- keep.tip(GBOTB.extended.TPL,prune_names)

spearman_exact <- function(tree,cls){
  tips <- tree$tip.label
  if(cls=="continuous_scalar"){
    state <- unname(state_map_num[tips])
    if(any(!is.finite(state))) stop("missing continuous state after tree mapping")
  } else {
    state <- unname(state_map_cat[tips])
    if(any(is.na(state))) stop("missing categorical state after tree mapping")
  }
  D <- cophenetic.phylo(tree)
  sep <- as.numeric(as.dist(D))
  rm(D); gc(FALSE)
  if(cls=="continuous_scalar"){
    diss <- as.numeric(dist(state))
    if(length(diss)!=length(sep)) stop("pair length mismatch")
    rho <- suppressWarnings(cor(sep,diss,method="spearman",use="complete.obs"))
  } else {
    n <- length(state)
    idx <- which(lower.tri(matrix(FALSE,n,n)),arr.ind=TRUE)
    diss <- as.integer(state[idx[,1]] != state[idx[,2]])
    if(length(diss)!=length(sep)) stop("pair length mismatch")
    rho <- suppressWarnings(cor(sep,diss,method="spearman",use="complete.obs"))
  }
  if(!is.finite(rho)) stop("nonfinite real memory rho")
  as.numeric(rho)
}

rho_s3 <- spearman_exact(tree_s3,semantic_class)
rho_prune <- spearman_exact(tree_prune,semantic_class)

out <- list(
  version="v0.7",
  status="TRAIT_MEMORY_REAL_EFFECT_SYSTEM_ESTIMATED",
  system_id=system_id,
  family=family,
  trait_name=trait_name,
  semantic_class=semantic_class,
  observed_database_version=observed_version,
  n_species_S3=length(tree_s3$tip.label),
  n_species_prune=length(tree_prune$tip.label),
  S3_rho=rho_s3,
  prune_only_rho=rho_prune,
  null_mean_exact=0,
  raw_trait_measurements_persisted=FALSE,
  species_states_persisted=FALSE,
  species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
