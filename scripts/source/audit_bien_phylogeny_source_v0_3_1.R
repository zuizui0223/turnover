#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(ape)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2 || args[[1]] != "--out") stop("usage: audit_bien_phylogeny_source_v0_3_1.R --out PATH")
out_path <- args[[2]]
dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)

root <- normalizePath(".")
contract <- fromJSON(file.path(root, "data", "bien_phylogeny_contract_v0_3_1.json"), simplifyVector = FALSE)
src <- Sys.getenv("VPHYLO_SOURCE_DIR", unset = "build/V.PhyloMaker2")

load(file.path(src, "data", "GBOTB.extended.TPL.rda"))
load(file.path(src, "data", "tips.info.TPL.rda"))
load(file.path(src, "data", "nodes.info.1.TPL.rda"))

tree <- GBOTB.extended.TPL
n_tip <- length(tree$tip.label)
n_edge <- nrow(tree$edge)
edge_lengths_present <- !is.null(tree$edge.length) && length(tree$edge.length) == n_edge
edge_lengths_finite <- edge_lengths_present && all(is.finite(tree$edge.length))
edge_lengths_nonnegative <- edge_lengths_finite && all(tree$edge.length >= 0)
rooted <- is.rooted(tree)

bt <- tryCatch(branching.times(tree), error=function(e) numeric())
dated_signal <- length(bt) > 0 && all(is.finite(bt)) && max(bt) > 0

tip_meta_n <- nrow(tips.info.TPL)
tip_meta_complete <- all(c("group","species","genus","family") %in% names(tips.info.TPL)) &&
  all(nzchar(trimws(as.character(tips.info.TPL$species)))) &&
  all(nzchar(trimws(as.character(tips.info.TPL$genus)))) &&
  all(nzchar(trimws(as.character(tips.info.TPL$family))))

tree_tips <- as.character(tree$tip.label)
meta_tips <- as.character(tips.info.TPL$species)
tree_tips_unique <- !anyDuplicated(tree_tips)
meta_tips_unique <- !anyDuplicated(meta_tips)
tip_set_match <- tree_tips_unique && meta_tips_unique &&
  length(setdiff(tree_tips, meta_tips)) == 0 &&
  length(setdiff(meta_tips, tree_tips)) == 0

nodes_nonempty <- is.data.frame(nodes.info.1.TPL) && nrow(nodes.info.1.TPL) > 0

expected <- as.integer(contract$phylogeny_source$documented_backbone_tip_count)
gate <- inherits(tree, "phylo") &&
  n_tip == expected &&
  tip_meta_n == expected &&
  tip_meta_complete &&
  tip_set_match &&
  edge_lengths_nonnegative &&
  rooted &&
  dated_signal &&
  nodes_nonempty

result <- list(
  version="v0.3.1.1",
  status=if (gate) "BIEN_PHYLOGENY_SOURCE_PASS" else "HOLD_BIEN_PHYLOGENY_SOURCE",
  outcome_blind=TRUE,
  generalized_trait_values_opened=FALSE,
  biological_turnover_outcomes_opened=FALSE,
  repository=contract$phylogeny_source$repository,
  commit=contract$phylogeny_source$commit,
  backbone=contract$phylogeny_source$backbone,
  expected_tip_count=expected,
  observed_tip_count=n_tip,
  tips_metadata_rows=tip_meta_n,
  tips_metadata_complete=tip_meta_complete,
  raw_tip_set_match=tip_set_match,
  tree_tip_labels_unique=tree_tips_unique,
  tips_metadata_species_unique=meta_tips_unique,
  edge_count=n_edge,
  edge_lengths_present=edge_lengths_present,
  edge_lengths_finite=edge_lengths_finite,
  edge_lengths_nonnegative=edge_lengths_nonnegative,
  rooted=rooted,
  dated_branching_time_signal=dated_signal,
  max_branching_time=if (length(bt)) max(bt) else NULL,
  nodes_info_rows=if (is.data.frame(nodes.info.1.TPL)) nrow(nodes.info.1.TPL) else NULL,
  gate_pass=gate,
  next_gate=if (gate) "Use only this pinned TPL backbone under the frozen BIEN crosswalk rules; run crosswalk after structural trait support." else "Stop BIEN temporal-arm crosswalk and resolve the pinned phylogeny-source mismatch before any trait values are opened."
)

write_json(result, out_path, pretty=TRUE, auto_unbox=TRUE, null="null")
cat(toJSON(result, pretty=TRUE, auto_unbox=TRUE, null="null"), "\n")
