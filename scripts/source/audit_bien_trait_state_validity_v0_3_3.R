#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
})

args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 6 || args[[1]]!="--support-table" || args[[3]]!="--out" || args[[5]]!="--table-out") {
  stop("usage: audit_bien_trait_state_validity_v0_3_3.R --support-table CSV --out JSON --table-out CSV")
}
support_path <- args[[2]]
out_path <- args[[4]]
table_path <- args[[6]]
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","bien_trait_state_validity_design_v0_3_2.json"),simplifyVector=FALSE)
recon <- fromJSON(file.path(root,"data","bien_trait_semantic_reconciliation_v0_3_3.json"),simplifyVector=FALSE)
sem <- fromJSON(file.path(root,"data","bien_trait_semantic_contract_v0_3.json"),simplifyVector=FALSE)
phy <- fromJSON(file.path(root,"data","bien_phylogeny_contract_v0_3_1.json"),simplifyVector=FALSE)

if (!identical(recon$status,"BIEN_TRAIT_SEMANTIC_CONTRACT_RECONCILED_PRE_SUPPORT_RESULT")) stop("missing semantic reconciliation")
if (!identical(recon$can_rescue_failure,FALSE)) stop("reconciliation is not stricter-only")
if (!identical(recon$raw_trait_values_opened,FALSE)) stop("raw values unexpectedly opened")

support <- read.csv(support_path, stringsAsFactors=FALSE, check.names=FALSE)
req <- c("family","trait_name","joint_support_pass")
if (!all(req %in% names(support))) stop("support table missing required columns")
pass <- support[support$joint_support_pass %in% c(TRUE,"TRUE","t","1",1),c("family","trait_name"),drop=FALSE]
pass <- unique(pass)
if (!nrow(pass)) {
  result <- list(
    version="v0.3.3",
    status="HOLD_BIEN_TRAIT_STATE_VALIDITY_NO_STRUCTURAL_CANDIDATES",
    outcome_blind=TRUE,
    raw_trait_values_opened=FALSE,
    biological_turnover_outcomes_opened=FALSE,
    n_structural_candidates=0L,
    n_semantic_pass=0L,
    n_independent_families=0L,
    gate_pass=FALSE
  )
  write_json(result,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
  write.csv(data.frame(),table_path,row.names=FALSE)
  quit(status=0)
}

continuous <- unlist(sem$representation_rules$continuous_scalar$traits)
categorical <- unlist(sem$representation_rules$nominal_categorical$traits)
hold_traits <- unique(c(
  vapply(sem$representation_rules$primary_hold$traits,function(x)x$trait_name,character(1)),
  unlist(recon$effective_primary_hold_traits)
))
pass$semantic_class <- ifelse(pass$trait_name %in% continuous,"continuous_scalar",
                       ifelse(pass$trait_name %in% categorical,"nominal_categorical",
                       ifelse(pass$trait_name %in% hold_traits,"primary_hold","unclassified")))

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR", unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if (!identical(observed_version,"4.2.8")) stop("BIEN patch changed before state-validity audit")

# Candidate keys are loaded into SQL as a VALUES relation. Raw values are used only inside aggregate
# expressions and are never returned at row or species-state level.
escape_sql <- function(x) gsub("'","''",x,fixed=TRUE)
vals <- paste0("('",escape_sql(pass$family),"','",escape_sql(pass$trait_name),"','",pass$semantic_class,"')")
candidate_values <- paste(vals,collapse=",\n")

R <- 6371008.8
std <- 30*pi/180
cell <- 25000

sql <- sprintf("
WITH candidates(family,trait_name,semantic_class) AS (
  VALUES %s
),
base AS (
  SELECT
    a.scrubbed_family AS family,
    a.scrubbed_species_binomial AS species,
    a.trait_name,
    c.semantic_class,
    a.trait_value::text AS value_text,
    a.unit::text AS unit,
    a.is_geovalid,
    a.latitude::double precision AS latitude,
    a.longitude::double precision AS longitude
  FROM agg_traits a
  INNER JOIN candidates c
    ON a.scrubbed_family=c.family AND a.trait_name=c.trait_name
  WHERE a.scrubbed_species_binomial IS NOT NULL
    AND trim(a.scrubbed_species_binomial)<>''
    AND a.trait_value IS NOT NULL
    AND trim(a.trait_value::text)<>''
    AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
),
continuous_rows AS (
  SELECT *,
    CASE
      WHEN value_text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
      THEN value_text::numeric
      ELSE NULL
    END AS value_num
  FROM base
  WHERE semantic_class='continuous_scalar'
),
continuous_system AS (
  SELECT family,trait_name,
    count(*) AS n_total,
    count(value_num) AS n_numeric_valid,
    count(*) - count(value_num) AS n_invalid,
    count(*) FILTER (WHERE unit IS NULL OR trim(unit)='') AS n_missing_unit,
    count(DISTINCT unit) FILTER (WHERE unit IS NOT NULL AND trim(unit)<>'') AS distinct_units,
    string_agg(DISTINCT unit,' | ' ORDER BY unit) FILTER (WHERE unit IS NOT NULL AND trim(unit)<>'') AS unit_labels
  FROM continuous_rows
  GROUP BY family,trait_name
),
continuous_species_state AS (
  SELECT family,trait_name,species,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY value_num) AS species_median
  FROM continuous_rows
  WHERE value_num IS NOT NULL
  GROUP BY family,trait_name,species
),
continuous_temporal AS (
  SELECT family,trait_name,
    count(*) AS temporal_resolvable_species,
    count(DISTINCT species_median) AS temporal_distinct_states
  FROM continuous_species_state
  GROUP BY family,trait_name
),
continuous_geo AS (
  SELECT family,trait_name,species,value_num,
    floor((%f*radians(longitude)*cos(%f))/%f)::bigint AS cell_x,
    floor((%f*sin(radians(latitude))/cos(%f))/%f)::bigint AS cell_y
  FROM continuous_rows
  WHERE value_num IS NOT NULL
    AND is_geovalid=1
    AND latitude BETWEEN -90 AND 90
    AND longitude BETWEEN -180 AND 180
),
continuous_sp_species AS (
  SELECT family,trait_name,species,
    count(*) AS georef_records,
    count(DISTINCT (cell_x::text||':'||cell_y::text)) AS occupied_cells,
    count(DISTINCT value_num) AS distinct_states
  FROM continuous_geo
  GROUP BY family,trait_name,species
),
continuous_spatial AS (
  SELECT family,trait_name,
    count(*) FILTER (WHERE georef_records>=20 AND occupied_cells>=5 AND distinct_states>=2) AS spatial_qualifying_species
  FROM continuous_sp_species
  GROUP BY family,trait_name
),
categorical_system AS (
  SELECT family,trait_name,
    count(*) AS n_total,
    count(DISTINCT unit) FILTER (WHERE unit IS NOT NULL AND trim(unit)<>'') AS distinct_nonempty_units,
    string_agg(DISTINCT unit,' | ' ORDER BY unit) FILTER (WHERE unit IS NOT NULL AND trim(unit)<>'') AS unit_labels
  FROM base
  WHERE semantic_class='nominal_categorical'
  GROUP BY family,trait_name
),
cat_counts AS (
  SELECT family,trait_name,species,value_text,count(*) AS n
  FROM base
  WHERE semantic_class='nominal_categorical'
  GROUP BY family,trait_name,species,value_text
),
cat_ranked AS (
  SELECT *,
    max(n) OVER (PARTITION BY family,trait_name,species) AS max_n
  FROM cat_counts
),
cat_modes AS (
  SELECT family,trait_name,species,
    count(*) FILTER (WHERE n=max_n) AS n_modal,
    min(value_text) FILTER (WHERE n=max_n) AS mode_internal
  FROM cat_ranked
  GROUP BY family,trait_name,species
),
categorical_temporal AS (
  SELECT family,trait_name,
    count(*) FILTER (WHERE n_modal=1) AS temporal_resolvable_species,
    count(DISTINCT mode_internal) FILTER (WHERE n_modal=1) AS temporal_distinct_states,
    count(*) FILTER (WHERE n_modal>1) AS tied_mode_species
  FROM cat_modes
  GROUP BY family,trait_name
),
categorical_geo_base AS (
  SELECT family,trait_name,species,value_text,
    floor((%f*radians(longitude)*cos(%f))/%f)::bigint AS cell_x,
    floor((%f*sin(radians(latitude))/cos(%f))/%f)::bigint AS cell_y
  FROM base
  WHERE semantic_class='nominal_categorical'
    AND is_geovalid=1
    AND latitude BETWEEN -90 AND 90
    AND longitude BETWEEN -180 AND 180
),
categorical_sp_species AS (
  SELECT family,trait_name,species,
    count(*) AS georef_records,
    count(DISTINCT (cell_x::text||':'||cell_y::text)) AS occupied_cells,
    count(DISTINCT value_text) AS distinct_states
  FROM categorical_geo_base
  GROUP BY family,trait_name,species
),
categorical_spatial AS (
  SELECT family,trait_name,
    count(*) FILTER (WHERE georef_records>=20 AND occupied_cells>=5 AND distinct_states>=2) AS spatial_qualifying_species
  FROM categorical_sp_species
  GROUP BY family,trait_name
)
SELECT
  c.family,
  c.trait_name,
  c.semantic_class,
  coalesce(cs.n_total,0) AS n_total,
  coalesce(cs.n_numeric_valid,0) AS n_numeric_valid,
  coalesce(cs.n_invalid,0) AS n_invalid,
  CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(cs.n_missing_unit,0) ELSE 0 END AS n_missing_unit,
  CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(cs.distinct_units,0)
       WHEN c.semantic_class='nominal_categorical' THEN coalesce(ks.distinct_nonempty_units,0)
       ELSE 0 END AS distinct_units,
  CASE WHEN c.semantic_class='continuous_scalar' THEN cs.unit_labels
       WHEN c.semantic_class='nominal_categorical' THEN ks.unit_labels
       ELSE NULL END AS unit_labels,
  CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(ct.temporal_resolvable_species,0)
       WHEN c.semantic_class='nominal_categorical' THEN coalesce(kt.temporal_resolvable_species,0)
       ELSE 0 END AS temporal_resolvable_species,
  CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(ct.temporal_distinct_states,0)
       WHEN c.semantic_class='nominal_categorical' THEN coalesce(kt.temporal_distinct_states,0)
       ELSE 0 END AS temporal_distinct_states,
  CASE WHEN c.semantic_class='nominal_categorical' THEN coalesce(kt.tied_mode_species,0) ELSE 0 END AS tied_mode_species,
  CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(cp.spatial_qualifying_species,0)
       WHEN c.semantic_class='nominal_categorical' THEN coalesce(kp.spatial_qualifying_species,0)
       ELSE 0 END AS spatial_qualifying_species
FROM candidates c
LEFT JOIN continuous_system cs USING (family,trait_name)
LEFT JOIN continuous_temporal ct USING (family,trait_name)
LEFT JOIN continuous_spatial cp USING (family,trait_name)
LEFT JOIN categorical_system ks USING (family,trait_name)
LEFT JOIN categorical_temporal kt USING (family,trait_name)
LEFT JOIN categorical_spatial kp USING (family,trait_name)
ORDER BY c.family,c.trait_name
;",
candidate_values,R,std,cell,R,std,cell,R,std,cell,R,std,cell)

audit <- .BIEN_sql(sql)
if (!is.data.frame(audit)) stop("BIEN state-validity query returned no dataframe")
forbidden <- c("trait_value","value_text","value_num","species","mode_internal","latitude","longitude","cell_x","cell_y")
if (any(forbidden %in% names(audit))) stop("raw/state firewall violated by output columns")

audit$semantic_pass <- FALSE
audit$hold_reason <- ""
for (i in seq_len(nrow(audit))) {
  cls <- audit$semantic_class[[i]]
  reasons <- character()
  if (cls=="primary_hold" || cls=="unclassified") {
    reasons <- c(reasons,"PRIMARY_HOLD_OR_UNCLASSIFIED")
  } else if (cls=="continuous_scalar") {
    if (audit$n_invalid[[i]] != 0) reasons <- c(reasons,"NONNUMERIC_OR_NONFINITE_VALUE")
    if (audit$n_missing_unit[[i]] != 0) reasons <- c(reasons,"CONTINUOUS_MISSING_UNIT")
    if (audit$distinct_units[[i]] != 1) reasons <- c(reasons,"CONTINUOUS_UNIT_COUNT_NOT_ONE")
    if (audit$temporal_resolvable_species[[i]] < 20) reasons <- c(reasons,"TEMPORAL_SPECIES_LT20")
    if (audit$temporal_distinct_states[[i]] < 2) reasons <- c(reasons,"NO_TEMPORAL_STATE_VARIATION")
    if (audit$spatial_qualifying_species[[i]] < 8) reasons <- c(reasons,"SPATIAL_SPECIES_LT8_AFTER_VARIATION")
  } else if (cls=="nominal_categorical") {
    if (audit$distinct_units[[i]] != 0) reasons <- c(reasons,"CATEGORICAL_NONEMPTY_UNIT")
    if (audit$temporal_resolvable_species[[i]] < 20) reasons <- c(reasons,"TEMPORAL_UNIQUE_MODE_SPECIES_LT20")
    if (audit$temporal_distinct_states[[i]] < 2) reasons <- c(reasons,"NO_TEMPORAL_STATE_VARIATION")
    if (audit$spatial_qualifying_species[[i]] < 8) reasons <- c(reasons,"SPATIAL_SPECIES_LT8_AFTER_VARIATION")
  }
  audit$semantic_pass[[i]] <- length(reasons)==0
  audit$hold_reason[[i]] <- paste(reasons,collapse=";")
}

write.csv(audit,table_path,row.names=FALSE,na="")
pass_rows <- audit[audit$semantic_pass,,drop=FALSE]
families <- sort(unique(as.character(pass_rows$family)))
gate <- length(families) >= 12

# Do not persist category labels, species-state values, or raw measurements.
summary_systems <- lapply(seq_len(nrow(audit)), function(i) {
  list(
    family=as.character(audit$family[[i]]),
    trait_name=as.character(audit$trait_name[[i]]),
    semantic_class=as.character(audit$semantic_class[[i]]),
    n_total=as.integer(audit$n_total[[i]]),
    n_numeric_valid=as.integer(audit$n_numeric_valid[[i]]),
    n_invalid=as.integer(audit$n_invalid[[i]]),
    n_missing_unit=as.integer(audit$n_missing_unit[[i]]),
    distinct_units=as.integer(audit$distinct_units[[i]]),
    unit_labels=if(is.na(audit$unit_labels[[i]])) NULL else as.character(audit$unit_labels[[i]]),
    temporal_resolvable_species=as.integer(audit$temporal_resolvable_species[[i]]),
    temporal_distinct_states=as.integer(audit$temporal_distinct_states[[i]]),
    tied_mode_species=as.integer(audit$tied_mode_species[[i]]),
    spatial_qualifying_species=as.integer(audit$spatial_qualifying_species[[i]]),
    semantic_pass=as.logical(audit$semantic_pass[[i]]),
    hold_reason=as.character(audit$hold_reason[[i]])
  )
})

result <- list(
  version="v0.3.3",
  status=if(gate) "BIEN_TRAIT_STATE_VALIDITY_PASS" else "HOLD_BIEN_TRAIT_STATE_VALIDITY",
  design="data/bien_trait_state_validity_design_v0_3_2.json",
  reconciliation="data/bien_trait_semantic_reconciliation_v0_3_3.json",
  outcome_blind=TRUE,
  raw_trait_values_opened=FALSE,
  biological_turnover_outcomes_opened=FALSE,
  observed_database_version=observed_version,
  n_structural_candidates=nrow(pass),
  n_semantic_pass=nrow(pass_rows),
  n_independent_families=length(families),
  qualifying_families=as.list(families),
  systems=summary_systems,
  gate_pass=gate,
  next_gate=if(gate) "Run frozen phylogeny crosswalk and observed-geometry informativeness gates before any real turnover response." else "BIEN primary trait route is semantic HOLD; do not relax rules and evaluate the already-frozen second trait source AusTraits."
)
write_json(result,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(result,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
