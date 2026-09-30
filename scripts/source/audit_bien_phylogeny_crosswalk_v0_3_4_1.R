#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
  library(V.PhyloMaker2)
})

args<-commandArgs(trailingOnly=TRUE)
if(length(args)!=6 || args[[1]]!="--semantic-table" || args[[3]]!="--out" || args[[5]]!="--table-out"){
  stop("usage: audit_bien_phylogeny_crosswalk_v0_3_4_1.R --semantic-table CSV --out JSON --table-out CSV")
}
semantic_path<-args[[2]]; out_path<-args[[4]]; table_path<-args[[6]]
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

root<-normalizePath(".")
design<-fromJSON(file.path(root,"data","bien_phylogeny_crosswalk_design_v0_3_4.json"),simplifyVector=FALSE)
amend<-fromJSON(file.path(root,"data","bien_phylogeny_crosswalk_status_fallback_v0_3_4_1.json"),simplifyVector=FALSE)
src<-fromJSON(file.path(root,"results","bien_phylogeny_source_v0_3_1","result_pass_v0_3_1_1.json"),simplifyVector=FALSE)
if(!identical(src$status,"BIEN_PHYLOGENY_SOURCE_PASS")) stop("phylogeny source did not pass")
if(!identical(amend$status,"BIEN_PHYLOGENY_CROSSWALK_STATUS_ONLY_FALLBACK_FROZEN_PRE_RESULT")) stop("fallback amendment missing")

sem<-read.csv(semantic_path,stringsAsFactors=FALSE,check.names=FALSE)
flag<-tolower(trimws(as.character(sem$semantic_pass))) %in% c("true","t","1")
cand<-unique(sem[flag,c("family","trait_name","semantic_class"),drop=FALSE])
if(!nrow(cand)) stop("no semantic candidates")

escape_sql<-function(x) gsub("'","''",x,fixed=TRUE)
vals<-paste0("('",escape_sql(cand$family),"','",escape_sql(cand$trait_name),"','",cand$semantic_class,"')")
candidate_values<-paste(vals,collapse=",\n")

rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R")); source(file.path(rbien_dir,"R","BIEN_sql.R")); source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version()
observed_version<-if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed before crosswalk")

sql<-sprintf("
WITH candidates(family,trait_name,semantic_class) AS (VALUES %s),
base AS (
 SELECT a.scrubbed_family AS family,a.scrubbed_species_binomial AS species,a.scrubbed_genus AS genus,
        a.trait_name,c.semantic_class,a.trait_value::text AS value_text
 FROM agg_traits a JOIN candidates c ON a.scrubbed_family=c.family AND a.trait_name=c.trait_name
 WHERE a.scrubbed_species_binomial IS NOT NULL AND trim(a.scrubbed_species_binomial)<>''
   AND a.scrubbed_genus IS NOT NULL AND trim(a.scrubbed_genus)<>''
   AND a.trait_value IS NOT NULL AND trim(a.trait_value::text)<>''
   AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
),
cont AS (
 SELECT DISTINCT family,trait_name,semantic_class,species,genus
 FROM base
 WHERE semantic_class='continuous_scalar'
   AND value_text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
),
cat_counts AS (
 SELECT family,trait_name,semantic_class,species,genus,value_text,count(*) AS n
 FROM base WHERE semantic_class='nominal_categorical'
 GROUP BY family,trait_name,semantic_class,species,genus,value_text
),
cat_ranked AS (
 SELECT *,max(n) OVER(PARTITION BY family,trait_name,species) AS max_n FROM cat_counts
),
cat_species AS (
 SELECT family,trait_name,semantic_class,species,genus,
        count(*) FILTER(WHERE n=max_n) AS n_modal
 FROM cat_ranked GROUP BY family,trait_name,semantic_class,species,genus
),
cat AS (
 SELECT family,trait_name,semantic_class,species,genus FROM cat_species WHERE n_modal=1
)
SELECT * FROM cont UNION ALL SELECT * FROM cat
ORDER BY family,trait_name,species
;",candidate_values)

spdat<-.BIEN_sql(sql)
if(!is.data.frame(spdat)) stop("species aggregate query failed")

norm_first<-function(x) gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x) norm_first(gsub(" ","_",x,fixed=TRUE))
tree_species<-as.character(GBOTB.extended.TPL$tip.label)
tree_genera<-unique(as.character(nodes.info.1.TPL$genus[nodes.info.1.TPL$level=="G"]))
tree_families<-unique(as.character(nodes.info.1.TPL$family[nodes.info.1.TPL$level=="F"]))

rows<-vector("list",nrow(cand))
for(i in seq_len(nrow(cand))){
  fam<-cand$family[[i]]; tr<-cand$trait_name[[i]]; cls<-cand$semantic_class[[i]]
  x<-unique(spdat[spdat$family==fam & spdat$trait_name==tr,c("species","genus","family"),drop=FALSE])
  sp<-norm_species(as.character(x$species))
  ge<-norm_first(as.character(x$genus))
  fa<-norm_first(as.character(x$family))
  is_prune<-sp %in% tree_species
  can_bind<-(!is_prune) & ((ge %in% tree_genera) | (fa %in% tree_families))
  is_fail<-(!is_prune) & (!can_bind)
  n_prune<-sum(is_prune); n_bind<-sum(can_bind); n_fail<-sum(is_fail)
  n_input<-nrow(x); primary<-n_prune+n_bind
  pass<-primary>=20 && n_prune>=20
  rows[[i]]<-data.frame(
    family=fam,trait_name=tr,semantic_class=cls,n_input_species=n_input,
    n_prune=n_prune,n_bind=n_bind,n_fail_to_bind=n_fail,
    primary_resolvable_species=primary,crosswalk_pass=pass,
    hold_reason=if(n_prune<20)"PRUNE_ONLY_LT20" else if(primary<20)"PRIMARY_RESOLVABLE_LT20" else "",
    stringsAsFactors=FALSE
  )
}
audit<-do.call(rbind,rows)
write.csv(audit,table_path,row.names=FALSE,na="")
pass_rows<-audit[audit$crosswalk_pass,,drop=FALSE]
families<-sort(unique(as.character(pass_rows$family)))
gate<-length(families)>=12

out<-list(
  version="v0.3.4.1",
  status=if(gate)"BIEN_PHYLOGENY_CROSSWALK_PASS" else "HOLD_BIEN_PHYLOGENY_CROSSWALK",
  design="data/bien_phylogeny_crosswalk_design_v0_3_4.json",
  fallback="data/bien_phylogeny_crosswalk_status_fallback_v0_3_4_1.json",
  outcome_blind=TRUE,raw_trait_values_opened=FALSE,biological_turnover_outcomes_opened=FALSE,
  observed_database_version=observed_version,n_candidate_systems=nrow(audit),
  n_crosswalk_pass=nrow(pass_rows),n_independent_families=length(families),
  qualifying_families=as.list(families),gate_pass=gate,
  next_gate=if(gate)"Run frozen observed-geometry informativeness simulations before real turnover outcomes." else "BIEN trait route is crosswalk HOLD; no alternate backbone/scenario/taxonomic matching."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
