#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
})

args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args); if(is.na(i)||i==length(args)) stop(paste("missing",flag)); args[[i+1]]}
core_path<-getarg("--core-table")
out_path<-getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

core<-read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(!all(c("family","trait_name") %in% names(core))) stop("BIEN core missing family/trait")
if(nrow(core)!=201) stop(paste("expected 201 BIEN systems, got",nrow(core)))

rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version()
observed<-if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed,"4.2.8")) stop("BIEN patch changed")

esc<-function(x) gsub("'","''",x,fixed=TRUE)
vals<-paste0("('",esc(core$family),"','",esc(core$trait_name),"')")
pairs<-paste(vals,collapse=",\n")

sql<-sprintf("
WITH core(family,trait_name) AS (VALUES %s)
SELECT DISTINCT a.source_citation
FROM agg_traits a
JOIN core c ON a.scrubbed_family=c.family AND a.trait_name=c.trait_name
WHERE a.scrubbed_species_binomial IS NOT NULL
  AND trim(a.scrubbed_species_binomial)<>''
  AND a.scrubbed_genus IS NOT NULL
  AND trim(a.scrubbed_genus)<>''
  AND a.trait_value IS NOT NULL
  AND trim(a.trait_value::text)<>''
  AND a.unit IS NOT NULL
  AND trim(a.unit::text)<>''
  AND a.trait_value::text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
  AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
  AND a.source_citation IS NOT NULL
  AND trim(a.source_citation)<>''
ORDER BY a.source_citation;
",pairs)

x<-.BIEN_sql(sql)
if(!is.data.frame(x) || !"source_citation" %in% names(x)) stop("BIEN citation query failed")
write.csv(x[,c("source_citation"),drop=FALSE],out_path,row.names=FALSE,na="")
cat(sprintf('{"status":"BIEN_CORE_SOURCE_CITATIONS_EXTRACTED","database_version":"%s","n_citations":%d}\n',observed,nrow(x)))
