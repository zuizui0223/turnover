#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL); library(DBI); library(jsonlite)
})
args<-commandArgs(trailingOnly=TRUE)
if(length(args)!=6 || args[[1]]!="--support-table" || args[[3]]!="--out" || args[[5]]!="--table-out")
  stop("usage: audit_trait_memory_semantic_v0_3.R --support-table CSV --out JSON --table-out CSV")
support_path<-args[[2]]; out_path<-args[[4]]; table_path<-args[[6]]
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)
root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_semantic_design_v0_3.json"),simplifyVector=FALSE)
sem<-fromJSON(file.path(root,"data","bien_trait_semantic_contract_v0_3.json"),simplifyVector=FALSE)

support<-read.csv(support_path,stringsAsFactors=FALSE,check.names=FALSE)
flag<-tolower(trimws(as.character(support$structural_pass))) %in% c("true","t","1")
cand<-unique(support[flag,c("family","trait_name","semantic_class"),drop=FALSE])
if(!nrow(cand)) stop("no structural candidates")

rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R")); source(file.path(rbien_dir,"R","BIEN_sql.R")); source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version()
observed_version<-if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed")

esc<-function(x) gsub("'","''",x,fixed=TRUE)
vals<-paste0("('",esc(cand$family),"','",esc(cand$trait_name),"','",cand$semantic_class,"')")
candidate_values<-paste(vals,collapse=",\n")
sql<-sprintf("
WITH candidates(family,trait_name,semantic_class) AS (VALUES %s),
base AS (
 SELECT a.scrubbed_family AS family,a.scrubbed_species_binomial AS species,
        a.trait_name,c.semantic_class,a.trait_value::text AS value_text,a.unit::text AS unit
 FROM agg_traits a JOIN candidates c ON a.scrubbed_family=c.family AND a.trait_name=c.trait_name
 WHERE a.scrubbed_species_binomial IS NOT NULL AND trim(a.scrubbed_species_binomial)<>''
   AND a.trait_value IS NOT NULL AND trim(a.trait_value::text)<>''
   AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
),
cont_rows AS (
 SELECT *,
   CASE WHEN value_text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
        THEN value_text::numeric ELSE NULL END AS value_num
 FROM base WHERE semantic_class='continuous_scalar'
),
cont_sys AS (
 SELECT family,trait_name,count(*) AS n_total,count(value_num) AS n_numeric,
        count(*)-count(value_num) AS n_invalid,
        count(*) FILTER(WHERE unit IS NULL OR trim(unit)='') AS n_missing_unit,
        count(DISTINCT unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS distinct_units,
        string_agg(DISTINCT unit,' | ' ORDER BY unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS unit_labels
 FROM cont_rows GROUP BY family,trait_name
),
cont_state AS (
 SELECT family,trait_name,species,percentile_cont(0.5) WITHIN GROUP(ORDER BY value_num) AS state
 FROM cont_rows WHERE value_num IS NOT NULL GROUP BY family,trait_name,species
),
cont_temporal AS (
 SELECT family,trait_name,count(*) AS resolvable_species,count(DISTINCT state) AS distinct_states
 FROM cont_state GROUP BY family,trait_name
),
cat_sys AS (
 SELECT family,trait_name,count(*) AS n_total,
        count(*) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS n_nonblank_unit_rows,
        count(DISTINCT unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS distinct_units,
        string_agg(DISTINCT unit,' | ' ORDER BY unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS unit_labels
 FROM base WHERE semantic_class='nominal_categorical'
 GROUP BY family,trait_name
),
cat_counts AS (
 SELECT family,trait_name,species,value_text,count(*) AS n
 FROM base WHERE semantic_class='nominal_categorical'
 GROUP BY family,trait_name,species,value_text
),
cat_ranked AS (
 SELECT *,max(n) OVER(PARTITION BY family,trait_name,species) AS max_n FROM cat_counts
),
cat_modes AS (
 SELECT family,trait_name,species,
        count(*) FILTER(WHERE n=max_n) AS n_modal,
        min(value_text) FILTER(WHERE n=max_n) AS mode_internal
 FROM cat_ranked GROUP BY family,trait_name,species
),
cat_temporal AS (
 SELECT family,trait_name,
        count(*) FILTER(WHERE n_modal=1) AS resolvable_species,
        count(DISTINCT mode_internal) FILTER(WHERE n_modal=1) AS distinct_states,
        count(*) FILTER(WHERE n_modal>1) AS tied_mode_species
 FROM cat_modes GROUP BY family,trait_name
)
SELECT c.family,c.trait_name,c.semantic_class,
       CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(cs.n_total,0) ELSE coalesce(ks.n_total,0) END AS n_total,
       CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(cs.n_invalid,0) ELSE 0 END AS n_invalid,
       CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(cs.n_missing_unit,0) ELSE coalesce(ks.n_nonblank_unit_rows,0) END AS n_bad_unit_rows,
       CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(cs.distinct_units,0) ELSE coalesce(ks.distinct_units,0) END AS distinct_units,
       CASE WHEN c.semantic_class='continuous_scalar' THEN cs.unit_labels ELSE ks.unit_labels END AS unit_labels,
       CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(ct.resolvable_species,0) ELSE coalesce(kt.resolvable_species,0) END AS resolvable_species,
       CASE WHEN c.semantic_class='continuous_scalar' THEN coalesce(ct.distinct_states,0) ELSE coalesce(kt.distinct_states,0) END AS distinct_states,
       CASE WHEN c.semantic_class='nominal_categorical' THEN coalesce(kt.tied_mode_species,0) ELSE 0 END AS tied_mode_species
FROM candidates c
LEFT JOIN cont_sys cs USING(family,trait_name)
LEFT JOIN cont_temporal ct USING(family,trait_name)
LEFT JOIN cat_sys ks USING(family,trait_name)
LEFT JOIN cat_temporal kt USING(family,trait_name)
ORDER BY c.family,c.trait_name;
",candidate_values)
x<-.BIEN_sql(sql)
if(!is.data.frame(x)) stop("semantic aggregate query failed")

x$semantic_pass<-FALSE; x$hold_reason<-""
for(i in seq_len(nrow(x))){
  cls<-x$semantic_class[[i]]; reasons<-character()
  if(cls=="continuous_scalar"){
    if(x$n_invalid[[i]]!=0) reasons<-c(reasons,"NONNUMERIC_VALUE")
    if(x$n_bad_unit_rows[[i]]!=0) reasons<-c(reasons,"MISSING_UNIT")
    if(x$distinct_units[[i]]!=1) reasons<-c(reasons,"UNIT_COUNT_NOT_ONE")
  } else {
    if(x$n_bad_unit_rows[[i]]!=0) reasons<-c(reasons,"CATEGORICAL_NONBLANK_UNIT")
  }
  if(x$resolvable_species[[i]]<20) reasons<-c(reasons,"RESOLVABLE_SPECIES_LT20")
  if(x$distinct_states[[i]]<2) reasons<-c(reasons,"DISTINCT_STATES_LT2")
  x$semantic_pass[[i]]<-length(reasons)==0
  x$hold_reason[[i]]<-paste(reasons,collapse=";")
}
write.csv(x,table_path,row.names=FALSE,na="")
pass<-x[x$semantic_pass,,drop=FALSE]
families<-sort(unique(as.character(pass$family)))
traits<-sort(unique(as.character(pass$trait_name)))
gate<-length(families)>=12 && length(traits)>=4
out<-list(
 version="v0.3",status=if(gate)"TRAIT_MEMORY_SEMANTIC_PASS" else "HOLD_TRAIT_MEMORY_SEMANTIC",
 outcome_blind=TRUE,real_trait_values_opened=FALSE,real_memory_effects_opened=FALSE,
 observed_database_version=observed_version,n_structural_candidates=nrow(cand),
 n_semantic_pass=nrow(pass),n_independent_families=length(families),n_distinct_traits=length(traits),
 qualifying_families=as.list(families),qualifying_traits=as.list(traits),
 gate_pass=gate,next_gate=if(gate)"Run frozen temporal phylogeny crosswalk." else "Stop temporal follow-up before memory effects."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
