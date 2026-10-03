#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(RPostgreSQL);library(DBI);library(jsonlite);library(V.PhyloMaker2)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path<-getarg("--effects"); out_path<-getarg("--out")
x<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=201 || length(unique(x$family))!=45 || length(unique(x$trait_name))!=12) stop("unexpected fixed core")
rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"));source(file.path(rbien_dir,"R","BIEN_sql.R"));source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version()
observed<-if(is.data.frame(ver)&&nrow(ver))as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed,"4.2.8"))stop("BIEN patch changed")
esc<-function(z)gsub("'","''",z,fixed=TRUE)

# All 201 final-core traits are continuous scalar. Recover exactly the species-state
# eligibility used by the real-effect extractor for each admitted family x trait edge,
# then union species within family.
vals<-paste0("('",esc(x$family),"','",esc(x$trait_name),"')")
pairs<-paste(unique(vals),collapse=",\n")
sql<-sprintf("
WITH systems(family,trait_name) AS (VALUES %s),
base AS (
 SELECT a.scrubbed_family AS family,a.scrubbed_species_binomial AS species,a.trait_name,
        CASE WHEN a.trait_value::text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
             THEN a.trait_value::numeric ELSE NULL END AS value_num
 FROM agg_traits a JOIN systems s ON a.scrubbed_family=s.family AND a.trait_name=s.trait_name
 WHERE a.scrubbed_species_binomial IS NOT NULL AND trim(a.scrubbed_species_binomial)<>''
   AND a.trait_value IS NOT NULL AND trim(a.trait_value::text)<>''
   AND a.unit IS NOT NULL AND trim(a.unit::text)<>''
   AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
),
states AS (
 SELECT family,trait_name,species,percentile_cont(0.5) WITHIN GROUP(ORDER BY value_num) AS state
 FROM base WHERE value_num IS NOT NULL
 GROUP BY family,trait_name,species
)
SELECT DISTINCT family,species FROM states ORDER BY family,species;
",pairs)
sp<-.BIEN_sql(sql)
norm_first<-function(z)gsub("(^[[:alpha:]])","\\U\\1",z,perl=TRUE)
norm_species<-function(z)norm_first(gsub(" ","_",z,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
sp<-sp[sp$tip %in% GBOTB.extended.TPL$tip.label,c("family","tip"),drop=FALSE]
sp<-unique(sp)
write.csv(sp,out_path,row.names=FALSE,na="")
cat(toJSON(list(status="FINAL_CORE_FAMILY_NATIVE_TIP_MEMBERSHIP_EXTRACTED",n_families=length(unique(sp$family)),n_tips=nrow(sp),observed_database_version=observed),pretty=TRUE,auto_unbox=TRUE),"\n")
