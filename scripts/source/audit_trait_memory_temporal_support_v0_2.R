#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
})
args<-commandArgs(trailingOnly=TRUE)
if(length(args)!=4 || args[[1]]!="--out" || args[[3]]!="--table-out") stop("usage: audit_trait_memory_temporal_support_v0_2.R --out JSON --table-out CSV")
out_path<-args[[2]]; table_path<-args[[4]]
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_temporal_support_design_v0_2.json"),simplifyVector=FALSE)
sem<-fromJSON(file.path(root,"data","bien_trait_semantic_contract_v0_3.json"),simplifyVector=FALSE)

continuous<-unlist(sem$representation_rules$continuous_scalar$traits)
categorical<-unlist(sem$representation_rules$nominal_categorical$traits)
traits<-c(continuous,categorical)
classes<-c(setNames(rep("continuous_scalar",length(continuous)),continuous),
           setNames(rep("nominal_categorical",length(categorical)),categorical))
if(length(unique(traits))!=52) stop("unexpected preclassified trait universe size")

rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R")); source(file.path(rbien_dir,"R","BIEN_sql.R")); source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version()
observed_version<-if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed")

esc<-function(x) gsub("'","''",x,fixed=TRUE)
trait_sql<-paste(sprintf("'%s'",esc(traits)),collapse=",")
sql<-sprintf("
SELECT scrubbed_family AS family, trait_name,
       count(DISTINCT scrubbed_species_binomial) AS temporal_species
FROM agg_traits
WHERE scrubbed_family IS NOT NULL AND trim(scrubbed_family)<>''
  AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
  AND trait_name IN (%s)
  AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
  AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
GROUP BY scrubbed_family,trait_name
ORDER BY scrubbed_family,trait_name;
",trait_sql)
x<-.BIEN_sql(sql)
if(!is.data.frame(x)) stop("BIEN temporal support query failed")
x$semantic_class<-unname(classes[as.character(x$trait_name)])
if(any(is.na(x$semantic_class))) stop("unclassified trait returned")
x$structural_pass<-x$temporal_species>=20

write.csv(x,table_path,row.names=FALSE,na="")
pass<-x[x$structural_pass,,drop=FALSE]
families<-sort(unique(as.character(pass$family)))
pass_traits<-sort(unique(as.character(pass$trait_name)))
gate<-length(families)>=12 && length(pass_traits)>=4

out<-list(
  version="v0.2",
  status=if(gate)"TRAIT_MEMORY_TEMPORAL_SUPPORT_PASS" else "HOLD_TRAIT_MEMORY_TEMPORAL_SUPPORT",
  outcome_blind=TRUE,
  real_trait_values_opened=FALSE,
  real_memory_effects_opened=FALSE,
  observed_database_version=observed_version,
  n_family_trait_systems=nrow(x),
  n_structural_pass_systems=nrow(pass),
  n_independent_families=length(families),
  n_distinct_traits=length(pass_traits),
  qualifying_families=as.list(families),
  qualifying_traits=as.list(pass_traits),
  minimum_families=12,
  minimum_traits=4,
  gate_pass=gate,
  next_gate=if(gate)d$next_gate_if_pass else d$next_gate_if_hold
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
