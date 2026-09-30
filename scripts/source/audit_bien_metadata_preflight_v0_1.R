#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2 || args[[1]] != "--out") stop("usage: audit_bien_metadata_preflight_v0_1.R --out PATH")
out_path <- args[[2]]
dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root, "data", "bien_metadata_preflight_design_v0_1.json"), simplifyVector = FALSE)

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR", unset = "build/RBIEN")
source(file.path(rbien_dir, "R", "internals.R"))
source(file.path(rbien_dir, "R", "BIEN_sql.R"))
source(file.path(rbien_dir, "R", "BIEN.R"))

transport_error <- NULL
version_df <- schema_df <- trait_df <- count_df <- NULL

tryCatch({
  version_df <- BIEN_metadata_database_version()
  schema_df <- .BIEN_sql("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='agg_traits' ORDER BY ordinal_position ;")
  trait_df <- BIEN_trait_list()
  count_df <- .BIEN_sql("SELECT COUNT(*) AS n FROM agg_traits ;")
}, error = function(e) {
  transport_error <<- paste0(class(e)[1], ": ", conditionMessage(e))
})

version_rows <- if (is.data.frame(version_df)) unname(split(version_df, seq_len(nrow(version_df)))) else list()
schema_rows <- if (is.data.frame(schema_df)) unname(split(schema_df, seq_len(nrow(schema_df)))) else list()
traits <- if (is.data.frame(trait_df) && "trait_name" %in% names(trait_df)) sort(unique(as.character(trait_df$trait_name))) else character()
n_rows <- if (is.data.frame(count_df) && nrow(count_df) >= 1) as.numeric(count_df[[1]][1]) else NULL

fields <- if (is.data.frame(schema_df) && "column_name" %in% names(schema_df)) as.character(schema_df$column_name) else character()
required <- unlist(design$required_agg_traits_fields)
missing <- setdiff(required, fields)
observed_version <- if (is.data.frame(version_df) && nrow(version_df) >= 1 && "db_version" %in% names(version_df)) as.character(version_df$db_version[[1]]) else NULL

pass_core <- is.null(transport_error) &&
  identical(observed_version, design$gate$require_database_version) &&
  length(missing) == 0 &&
  !is.null(n_rows) && is.finite(n_rows) && n_rows > 0 &&
  length(traits) > 0

result <- list(
  version = "v0.1",
  status = if (pass_core) "BIEN_METADATA_PREFLIGHT_PASS" else "HOLD_BIEN_METADATA_PREFLIGHT",
  design = "data/bien_metadata_preflight_design_v0_1.json",
  outcome_blind = TRUE,
  generalized_trait_values_opened = FALSE,
  biological_turnover_outcomes_opened = FALSE,
  row_level_trait_records_returned = FALSE,
  row_level_coordinates_returned = FALSE,
  transport_error = transport_error,
  database_version_rows = version_rows,
  observed_database_version = observed_version,
  agg_traits_row_count = n_rows,
  agg_traits_schema = schema_rows,
  missing_required_fields = as.list(missing),
  trait_names = as.list(traits),
  n_trait_names = length(traits),
  reference_trait_count = design$gate$expected_trait_vocabulary_size_reference,
  trait_count_matches_reference = identical(length(traits), as.integer(design$gate$expected_trait_vocabulary_size_reference)),
  gate_pass = pass_core,
  next_gate = if (pass_core) design$next_gate_if_pass else design$next_gate_if_hold
)

write_json(result, out_path, pretty = TRUE, auto_unbox = TRUE, null = "null")
cat(toJSON(result, pretty = TRUE, auto_unbox = TRUE, null = "null"), "\n")
