#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
})

args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=4 || args[[1]]!="--out" || args[[3]]!="--table-out"){
  stop("usage: audit_bien_trait_support_v0_2_3.R --out JSON --table-out CSV")
}
out_path<-args[[2]]; table_path<-args[[4]]
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
design<-fromJSON(file.path(root,"data","bien_trait_support_design_v0_2.json"),simplifyVector=FALSE)
amend<-fromJSON(file.path(root,"data","bien_trait_support_queryplan_fallback_v0_2_3.json"),simplifyVector=FALSE)
pre<-fromJSON(file.path(root,"results","bien_metadata_preflight_v0_1","result_pass_v0_1_2.json"),simplifyVector=FALSE)
if(!identical(pre$status,"BIEN_METADATA_PREFLIGHT_PASS")) stop("metadata prerequisite failed")
if(!identical(amend$status,"BIEN_SUPPORT_QUERY_PLAN_FALLBACK_FROZEN_PRE_RESULT")) stop("fallback contract missing")
if(!identical(amend$support_thresholds_changed,FALSE)) stop("fallback changed thresholds")

rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))

ver<-BIEN_metadata_database_version()
observed_version<-if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed before fallback support")

min_temp<-as.integer(design$temporal_support$minimum_species_per_family_trait)
min_geo<-as.integer(design$spatial_support$minimum_georeferenced_records_per_species)
min_cells<-as.integer(design$spatial_support$minimum_cells_per_species)
min_spatial<-as.integer(design$spatial_support$minimum_spatial_species_per_family_trait)
cell<-as.numeric(design$spatial_support$cell_size_m)
R<-as.numeric(design$spatial_support$projection$earth_radius_m)
std<-30*pi/180

base_filter <- "
  scrubbed_family IS NOT NULL AND trim(scrubbed_family)<>''
  AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
  AND trait_name IS NOT NULL AND trim(trait_name)<>''
  AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
  AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
"
base_filter_a <- "
  a.scrubbed_family IS NOT NULL AND trim(a.scrubbed_family)<>''
  AND a.scrubbed_species_binomial IS NOT NULL AND trim(a.scrubbed_species_binomial)<>''
  AND a.trait_name IS NOT NULL AND trim(a.trait_name)<>''
  AND a.trait_value IS NOT NULL AND trim(a.trait_value::text)<>''
  AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
"

q1<-paste0("
SELECT scrubbed_family AS family, trait_name,
       count(DISTINCT scrubbed_species_binomial) AS temporal_species
FROM agg_traits
WHERE ",base_filter,"
GROUP BY scrubbed_family,trait_name
ORDER BY scrubbed_family,trait_name;
")
temporal<-.BIEN_sql(q1)
if(!is.data.frame(temporal)) stop("temporal aggregate query failed")
candidates<-temporal[temporal$temporal_species>=min_temp,c("family","trait_name"),drop=FALSE]

escape_sql<-function(x) gsub("'","''",x,fixed=TRUE)
if(nrow(candidates)>0){
  vals<-paste0("('",escape_sql(candidates$family),"','",escape_sql(candidates$trait_name),"')")
  candidate_values<-paste(vals,collapse=",\n")
  q2<-sprintf("
WITH candidates(family,trait_name) AS (VALUES %s),
geo AS (
 SELECT a.scrubbed_family AS family,a.trait_name,a.scrubbed_species_binomial AS species,
        floor((%f*radians(a.longitude::double precision)*cos(%f))/%f)::bigint AS cell_x,
        floor((%f*sin(radians(a.latitude::double precision))/cos(%f))/%f)::bigint AS cell_y
 FROM agg_traits a
 JOIN candidates c ON a.scrubbed_family=c.family AND a.trait_name=c.trait_name
 WHERE %s
   AND a.is_geovalid=1
   AND a.latitude BETWEEN -90 AND 90
   AND a.longitude BETWEEN -180 AND 180
),
sp AS (
 SELECT family,trait_name,species,
        count(*) AS georef_records,
        count(DISTINCT (cell_x::text||':'||cell_y::text)) AS occupied_cells
 FROM geo
 GROUP BY family,trait_name,species
)
SELECT family,trait_name,
       count(*) AS georeferenced_species,
       count(*) FILTER(WHERE georef_records>=%d AND occupied_cells>=%d) AS spatial_qualifying_species
FROM sp
GROUP BY family,trait_name
ORDER BY family,trait_name;
",candidate_values,R,std,cell,R,std,cell,base_filter_a,min_geo,min_cells)
  spatial<-.BIEN_sql(q2)
  if(!is.data.frame(spatial)) stop("spatial aggregate query failed")
}else{
  spatial<-data.frame(family=character(),trait_name=character(),georeferenced_species=integer(),spatial_qualifying_species=integer())
}

support<-merge(temporal,spatial,by=c("family","trait_name"),all.x=TRUE,sort=TRUE)
support$georeferenced_species[is.na(support$georeferenced_species)]<-0
support$spatial_qualifying_species[is.na(support$spatial_qualifying_species)]<-0
support$joint_support_pass <- support$temporal_species>=min_temp & support$spatial_qualifying_species>=min_spatial

forbidden<-c("trait_value","species","latitude","longitude","cell_x","cell_y")
if(any(forbidden %in% names(support))) stop("fallback output firewall violated")
write.csv(support,table_path,row.names=FALSE,na="")

pass_rows<-support[support$joint_support_pass,,drop=FALSE]
families<-sort(unique(as.character(pass_rows$family)))
gate<-length(families)>=as.integer(design$joint_gate$minimum_independent_families)

systems<-if(nrow(pass_rows)) lapply(seq_len(nrow(pass_rows)),function(i){
  list(
    family=as.character(pass_rows$family[[i]]),
    trait_name=as.character(pass_rows$trait_name[[i]]),
    temporal_species=as.integer(pass_rows$temporal_species[[i]]),
    georeferenced_species=as.integer(pass_rows$georeferenced_species[[i]]),
    spatial_qualifying_species=as.integer(pass_rows$spatial_qualifying_species[[i]])
  )
}) else list()

out<-list(
  version="v0.2.3",
  status=if(gate)"BIEN_TRAIT_SUPPORT_PASS" else "HOLD_BIEN_TRAIT_SUPPORT",
  design="data/bien_trait_support_design_v0_2.json",
  query_plan_amendment="data/bien_trait_support_queryplan_fallback_v0_2_3.json",
  outcome_blind=TRUE,
  generalized_trait_values_opened=FALSE,
  biological_turnover_outcomes_opened=FALSE,
  raw_rows_returned=FALSE,
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
  n_temporal_candidate_systems=nrow(candidates),
  n_joint_support_family_trait_systems=nrow(pass_rows),
  n_independent_qualifying_families=length(families),
  qualifying_families=as.list(families),
  qualifying_systems=systems,
  non_gating_unit_diagnostics_deferred=TRUE,
  gate_pass=gate,
  next_gate=if(gate)design$next_gate_if_pass else design$next_gate_if_hold
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
