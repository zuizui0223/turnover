#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL); library(DBI); library(jsonlite); library(V.PhyloMaker2)
})
args<-commandArgs(trailingOnly=TRUE)
if(length(args)!=6 || args[[1]]!="--semantic-table" || args[[3]]!="--out" || args[[5]]!="--table-out")
  stop("usage: audit_trait_memory_crosswalk_v0_4.R --semantic-table CSV --out JSON --table-out CSV")
semantic_path<-args[[2]]; out_path<-args[[4]]; table_path<-args[[6]]
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE); dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)
root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_phylogeny_crosswalk_design_v0_4.json"),simplifyVector=FALSE)
sem<-read.csv(semantic_path,stringsAsFactors=FALSE,check.names=FALSE)
flag<-tolower(trimws(as.character(sem$semantic_pass))) %in% c("true","t","1")
cand<-unique(sem[flag,c("family","trait_name","semantic_class"),drop=FALSE])
if(!nrow(cand)) stop("no semantic candidates")

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
 SELECT family,trait_name,semantic_class,species,genus,count(*) FILTER(WHERE n=max_n) AS n_modal
 FROM cat_ranked GROUP BY family,trait_name,semantic_class,species,genus
),
cat AS (
 SELECT family,trait_name,semantic_class,species,genus FROM cat_species WHERE n_modal=1
)
SELECT * FROM cont UNION ALL SELECT * FROM cat ORDER BY family,trait_name,species;
",candidate_values)
sp<-.BIEN_sql(sql)
if(!is.data.frame(sp)) stop("species crosswalk query failed")

norm_first<-function(x) gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x) norm_first(gsub(" ","_",x,fixed=TRUE))
tree_species<-GBOTB.extended.TPL$tip.label
node_genus<-unique(as.character(nodes.info.1.TPL$genus[nodes.info.1.TPL$level=="G"]))
node_family<-unique(as.character(nodes.info.1.TPL$family[nodes.info.1.TPL$level=="F"]))

rows<-vector("list",nrow(cand))
for(i in seq_len(nrow(cand))){
  fam<-cand$family[[i]]; tr<-cand$trait_name[[i]]; cls<-cand$semantic_class[[i]]
  x<-unique(sp[sp$family==fam & sp$trait_name==tr,c("species","genus","family"),drop=FALSE])
  ns<-norm_species(as.character(x$species))
  ng<-norm_first(as.character(x$genus))
  nf<-norm_first(as.character(x$family))
  prune<-ns %in% tree_species
  bind<-!prune & (ng %in% node_genus | nf %in% node_family)
  fail<-!prune & !bind
  np<-sum(prune); nb<-sum(bind); nfai<-sum(fail); nres<-np+nb
  pass<-nres>=20 && np>=20
  rows[[i]]<-data.frame(family=fam,trait_name=tr,semantic_class=cls,n_input_species=nrow(x),
    n_prune=np,n_bind=nb,n_fail_to_bind=nfai,primary_resolvable_species=nres,
    crosswalk_pass=pass,hold_reason=if(np<20)"PRUNE_ONLY_LT20" else if(nres<20)"PRIMARY_RESOLVABLE_LT20" else "",
    stringsAsFactors=FALSE)
}
audit<-do.call(rbind,rows)
write.csv(audit,table_path,row.names=FALSE,na="")
pass<-audit[audit$crosswalk_pass,,drop=FALSE]
families<-sort(unique(as.character(pass$family))); traits<-sort(unique(as.character(pass$trait_name)))
gate<-length(families)>=12 && length(traits)>=4
out<-list(version="v0.4",status=if(gate)"TRAIT_MEMORY_PHYLOGENY_CROSSWALK_PASS" else "HOLD_TRAIT_MEMORY_PHYLOGENY_CROSSWALK",
 outcome_blind=TRUE,real_trait_values_opened=FALSE,real_memory_effects_opened=FALSE,
 observed_database_version=observed_version,n_candidate_systems=nrow(audit),n_crosswalk_pass=nrow(pass),
 n_independent_families=length(families),n_distinct_traits=length(traits),
 qualifying_families=as.list(families),qualifying_traits=as.list(traits),gate_pass=gate,
 next_gate=if(gate)"Run frozen temporal S3 and prune-only informativeness." else "Stop follow-up before memory effects.")
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
