#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(RPostgreSQL);library(DBI);library(jsonlite);library(V.PhyloMaker2)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path<-getarg("--effects"); out_path<-getarg("--out")
x<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=201 || length(unique(x$family))!=45) stop("unexpected fixed core")
families<-sort(unique(x$family))
rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"));source(file.path(rbien_dir,"R","BIEN_sql.R"));source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version()
observed<-if(is.data.frame(ver)&&nrow(ver))as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed,"4.2.8"))stop("BIEN patch changed")
esc<-function(z)gsub("'","''",z,fixed=TRUE)
fam_sql<-paste(sprintf("'%s'",esc(families)),collapse=",")
sql<-sprintf("
SELECT DISTINCT scrubbed_family AS family,scrubbed_species_binomial AS species
FROM agg_traits
WHERE scrubbed_family IN (%s)
  AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
  AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
  AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
ORDER BY scrubbed_family,scrubbed_species_binomial;",fam_sql)
sp<-.BIEN_sql(sql)
norm_first<-function(z)gsub("(^[[:alpha:]])","\\U\\1",z,perl=TRUE)
norm_species<-function(z)norm_first(gsub(" ","_",z,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
sp<-sp[sp$tip %in% GBOTB.extended.TPL$tip.label,c("family","tip"),drop=FALSE]
sp<-unique(sp)
write.csv(sp,out_path,row.names=FALSE,na="")
cat(toJSON(list(status="FAMILY_NATIVE_TIP_MEMBERSHIP_EXTRACTED",n_families=length(unique(sp$family)),n_tips=nrow(sp),observed_database_version=observed),pretty=TRUE,auto_unbox=TRUE),"\n")
