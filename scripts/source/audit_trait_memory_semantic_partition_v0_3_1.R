#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL); library(DBI); library(jsonlite)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args); if(is.na(i)||i==length(args)) stop(paste("missing",flag)); args[[i+1]]}
trait_name<-getarg("--trait")
semantic_class<-getarg("--class")
support_path<-getarg("--support-table")
out_path<-getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

support<-read.csv(support_path,stringsAsFactors=FALSE,check.names=FALSE)
flag<-tolower(trimws(as.character(support$structural_pass))) %in% c("true","t","1")
cand<-sort(unique(as.character(support$family[flag & support$trait_name==trait_name])))
if(!length(cand)) stop("no structural families for trait")

rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R")); source(file.path(rbien_dir,"R","BIEN_sql.R")); source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version()
observed_version<-if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed")

esc<-function(x) gsub("'","''",x,fixed=TRUE)
fam_sql<-paste(sprintf("'%s'",esc(cand)),collapse=",")
trq<-esc(trait_name)

if(semantic_class=="continuous_scalar"){
 sql<-sprintf("
 WITH base AS (
   SELECT scrubbed_family AS family,scrubbed_species_binomial AS species,
          trait_value::text AS value_text,unit::text AS unit,
          CASE WHEN trait_value::text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
               THEN trait_value::numeric ELSE NULL END AS value_num
   FROM agg_traits
   WHERE trait_name='%s' AND scrubbed_family IN (%s)
     AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
     AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
     AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
 ), sys AS (
   SELECT family,count(*) AS n_total,count(value_num) AS n_numeric,
          count(*)-count(value_num) AS n_invalid,
          count(*) FILTER(WHERE unit IS NULL OR trim(unit)='') AS n_bad_unit_rows,
          count(DISTINCT unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS distinct_units,
          string_agg(DISTINCT unit,' | ' ORDER BY unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS unit_labels
   FROM base GROUP BY family
 ), states AS (
   SELECT family,species,percentile_cont(0.5) WITHIN GROUP(ORDER BY value_num) AS state
   FROM base WHERE value_num IS NOT NULL GROUP BY family,species
 ), temporal AS (
   SELECT family,count(*) AS resolvable_species,count(DISTINCT state) AS distinct_states
   FROM states GROUP BY family
 )
 SELECT s.family,s.n_total,s.n_invalid,s.n_bad_unit_rows,s.distinct_units,s.unit_labels,
        coalesce(t.resolvable_species,0) AS resolvable_species,coalesce(t.distinct_states,0) AS distinct_states,
        0::bigint AS tied_mode_species
 FROM sys s LEFT JOIN temporal t USING(family) ORDER BY s.family;
 ",trq,fam_sql)
} else if(semantic_class=="nominal_categorical"){
 sql<-sprintf("
 WITH base AS (
   SELECT scrubbed_family AS family,scrubbed_species_binomial AS species,
          trait_value::text AS value_text,unit::text AS unit
   FROM agg_traits
   WHERE trait_name='%s' AND scrubbed_family IN (%s)
     AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
     AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
     AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
 ), sys AS (
   SELECT family,count(*) AS n_total,0::bigint AS n_invalid,
          count(*) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS n_bad_unit_rows,
          count(DISTINCT unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS distinct_units,
          string_agg(DISTINCT unit,' | ' ORDER BY unit) FILTER(WHERE unit IS NOT NULL AND trim(unit)<>'') AS unit_labels
   FROM base GROUP BY family
 ), counts AS (
   SELECT family,species,value_text,count(*) AS n FROM base GROUP BY family,species,value_text
 ), ranked AS (
   SELECT *,max(n) OVER(PARTITION BY family,species) AS max_n FROM counts
 ), modes AS (
   SELECT family,species,count(*) FILTER(WHERE n=max_n) AS n_modal,
          min(value_text) FILTER(WHERE n=max_n) AS mode_internal
   FROM ranked GROUP BY family,species
 ), temporal AS (
   SELECT family,
          count(*) FILTER(WHERE n_modal=1) AS resolvable_species,
          count(DISTINCT mode_internal) FILTER(WHERE n_modal=1) AS distinct_states,
          count(*) FILTER(WHERE n_modal>1) AS tied_mode_species
   FROM modes GROUP BY family
 )
 SELECT s.family,s.n_total,s.n_invalid,s.n_bad_unit_rows,s.distinct_units,s.unit_labels,
        coalesce(t.resolvable_species,0) AS resolvable_species,coalesce(t.distinct_states,0) AS distinct_states,
        coalesce(t.tied_mode_species,0) AS tied_mode_species
 FROM sys s LEFT JOIN temporal t USING(family) ORDER BY s.family;
 ",trq,fam_sql)
} else stop("unsupported semantic class")

x<-.BIEN_sql(sql)
if(!is.data.frame(x)) stop("trait-partition semantic query failed")
x$trait_name<-trait_name
x$semantic_class<-semantic_class
x$semantic_pass<-FALSE
x$hold_reason<-""
for(i in seq_len(nrow(x))){
 reasons<-character()
 if(semantic_class=="continuous_scalar"){
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
cols<-c("family","trait_name","semantic_class","n_total","n_invalid","n_bad_unit_rows","distinct_units","unit_labels","resolvable_species","distinct_states","tied_mode_species","semantic_pass","hold_reason")
x<-x[,cols,drop=FALSE]
write.csv(x,out_path,row.names=FALSE,na="")
cat(toJSON(list(version="v0.3.1",trait_name=trait_name,semantic_class=semantic_class,n_candidates=length(cand),n_rows=nrow(x),n_pass=sum(x$semantic_pass),real_memory_effects_opened=FALSE),auto_unbox=TRUE,pretty=TRUE),"\n")
