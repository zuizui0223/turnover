#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4 || args[[1]] != "--out" || args[[3]] != "--table-out") {
  stop("usage: audit_bien_trait_support_v0_2.R --out PATH --table-out PATH")
}
out_path <- args[[2]]
table_path <- args[[4]]
dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(table_path), recursive = TRUE, showWarnings = FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root, "data", "bien_trait_support_design_v0_2.json"), simplifyVector = FALSE)
pre <- fromJSON(file.path(root, "results", "bien_metadata_preflight_v0_1", "result_pass_v0_1_2.json"), simplifyVector = FALSE)
if (!identical(pre$status, "BIEN_METADATA_PREFLIGHT_PASS")) stop("BIEN metadata prerequisite did not pass")
if (!identical(pre$generalized_trait_values_opened, FALSE)) stop("trait values unexpectedly opened")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR", unset = "build/RBIEN")
source(file.path(rbien_dir, "R", "internals.R"))
source(file.path(rbien_dir, "R", "BIEN_sql.R"))
source(file.path(rbien_dir, "R", "BIEN.R"))

version_df <- BIEN_metadata_database_version()
observed_version <- if (is.data.frame(version_df) && nrow(version_df) >= 1) as.character(version_df$db_version[[1]]) else NA_character_
if (!identical(observed_version, design$source$exact_patch_pin)) {
  result <- list(
    version="v0.2.2",
    status="HOLD_BIEN_PATCH_CHANGED_BEFORE_SUPPORT",
    outcome_blind=TRUE,
    generalized_trait_values_opened=FALSE,
    biological_turnover_outcomes_opened=FALSE,
    observed_database_version=observed_version,
    required_exact_patch=design$source$exact_patch_pin,
    gate_pass=FALSE,
    next_gate="Stop and rerun BIEN source qualification before any support or trait-value opening."
  )
  write_json(result,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
  cat(toJSON(result,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
  quit(status=0)
}

R <- as.numeric(design$spatial_support$projection$earth_radius_m)
std <- 30*pi/180
cell <- as.numeric(design$spatial_support$cell_size_m)
min_geo <- as.integer(design$spatial_support$minimum_georeferenced_records_per_species)
min_cells <- as.integer(design$spatial_support$minimum_cells_per_species)
min_temp <- as.integer(design$temporal_support$minimum_species_per_family_trait)
min_spatial <- as.integer(design$spatial_support$minimum_spatial_species_per_family_trait)

sql <- sprintf("
WITH base AS (
  SELECT
    scrubbed_family AS family,
    scrubbed_species_binomial AS species,
    trait_name,
    unit,
    is_geovalid,
    latitude::double precision AS latitude,
    longitude::double precision AS longitude
  FROM agg_traits
  WHERE scrubbed_family IS NOT NULL
    AND trim(scrubbed_family) <> ''
    AND scrubbed_species_binomial IS NOT NULL
    AND trim(scrubbed_species_binomial) <> ''
    AND trait_name IS NOT NULL
    AND trim(trait_name) <> ''
    AND trait_value IS NOT NULL
    AND trim(trait_value::text) <> ''
    AND (is_cultivated_observation = 0 OR is_cultivated_observation IS NULL)
),
temporal_species AS (
  SELECT family, trait_name, species, count(*) AS n_records
  FROM base
  GROUP BY family, trait_name, species
),
temporal_ft AS (
  SELECT family, trait_name, count(*) AS temporal_species
  FROM temporal_species
  GROUP BY family, trait_name
),
candidate_ft AS (
  SELECT family, trait_name
  FROM temporal_ft
  WHERE temporal_species >= %d
),
geo_rows AS (
  SELECT
    b.family,
    b.trait_name,
    b.species,
    floor((%f * radians(b.longitude) * cos(%f)) / %f)::bigint AS cell_x,
    floor((%f * sin(radians(b.latitude)) / cos(%f)) / %f)::bigint AS cell_y
  FROM base b
  INNER JOIN candidate_ft c
    ON b.family=c.family AND b.trait_name=c.trait_name
  WHERE b.is_geovalid = 1
    AND b.latitude BETWEEN -90 AND 90
    AND b.longitude BETWEEN -180 AND 180
),
spatial_species AS (
  SELECT
    family,
    trait_name,
    species,
    count(*) AS georef_records,
    count(DISTINCT (cell_x::text || ':' || cell_y::text)) AS occupied_cells
  FROM geo_rows
  GROUP BY family, trait_name, species
),
spatial_ft AS (
  SELECT
    family,
    trait_name,
    count(*) AS georeferenced_species,
    count(*) FILTER (
      WHERE georef_records >= %d AND occupied_cells >= %d
    ) AS spatial_qualifying_species
  FROM spatial_species
  GROUP BY family, trait_name
),
units AS (
  SELECT
    family,
    trait_name,
    count(DISTINCT unit) FILTER (WHERE unit IS NOT NULL AND trim(unit) <> '') AS distinct_units,
    string_agg(DISTINCT unit, ' | ' ORDER BY unit) FILTER (WHERE unit IS NOT NULL AND trim(unit) <> '') AS unit_labels
  FROM base
  GROUP BY family, trait_name
)
SELECT
  t.family,
  t.trait_name,
  t.temporal_species,
  coalesce(s.georeferenced_species,0) AS georeferenced_species,
  coalesce(s.spatial_qualifying_species,0) AS spatial_qualifying_species,
  coalesce(u.distinct_units,0) AS distinct_units,
  u.unit_labels,
  CASE WHEN t.temporal_species >= %d
        AND coalesce(s.spatial_qualifying_species,0) >= %d
       THEN TRUE ELSE FALSE END AS joint_support_pass
FROM temporal_ft t
LEFT JOIN spatial_ft s USING (family,trait_name)
LEFT JOIN units u USING (family,trait_name)
ORDER BY t.family,t.trait_name
;",
min_temp,R,std,cell,R,std,cell,min_geo,min_cells,min_temp,min_spatial)

if (!grepl("trait_value IS NOT NULL", sql, fixed=TRUE)) stop("validity firewall: trait_value presence predicate missing")

support <- .BIEN_sql(sql)
if (!is.data.frame(support)) stop("BIEN support query returned no dataframe")
if ("trait_value" %in% names(support)) stop("outcome firewall: trait_value returned")
write.csv(support,table_path,row.names=FALSE,na="")

pass_rows <- support[which(support$joint_support_pass %in% c(TRUE,"TRUE","t","1",1)),,drop=FALSE]
families <- sort(unique(as.character(pass_rows$family)))
gate <- length(families) >= as.integer(design$joint_gate$minimum_independent_families)

qualifying <- if (nrow(pass_rows)) {
  lapply(seq_len(nrow(pass_rows)), function(i) {
    list(
      family=as.character(pass_rows$family[[i]]),
      trait_name=as.character(pass_rows$trait_name[[i]]),
      temporal_species=as.integer(pass_rows$temporal_species[[i]]),
      georeferenced_species=as.integer(pass_rows$georeferenced_species[[i]]),
      spatial_qualifying_species=as.integer(pass_rows$spatial_qualifying_species[[i]]),
      distinct_units=as.integer(pass_rows$distinct_units[[i]]),
      unit_labels=if (is.na(pass_rows$unit_labels[[i]])) NULL else as.character(pass_rows$unit_labels[[i]])
    )
  })
} else list()

result <- list(
  version="v0.2",
  status=if (gate) "BIEN_TRAIT_SUPPORT_PASS" else "HOLD_BIEN_TRAIT_SUPPORT",
  design="data/bien_trait_support_design_v0_2.json",
  outcome_blind=TRUE,
  generalized_trait_values_opened=FALSE,
  biological_turnover_outcomes_opened=FALSE,
  trait_value_presence_only=TRUE,
  trait_value_returned=FALSE,
  row_level_species_returned=FALSE,
  row_level_coordinates_returned=FALSE,
  observed_database_version=observed_version,
  thresholds=list(
    temporal_min_species=min_temp,
    spatial_min_species=min_spatial,
    spatial_min_georeferenced_records=min_geo,
    spatial_min_cells=min_cells,
    cell_size_m=as.integer(cell),
    minimum_independent_families=as.integer(design$joint_gate$minimum_independent_families)
  ),
  n_family_trait_systems=nrow(support),
  n_joint_support_family_trait_systems=nrow(pass_rows),
  n_independent_qualifying_families=length(families),
  qualifying_families=as.list(families),
  qualifying_systems=qualifying,
  support_table=table_path,
  gate_pass=gate,
  next_gate=if (gate) design$next_gate_if_pass else design$next_gate_if_hold
)
write_json(result,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(result,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
