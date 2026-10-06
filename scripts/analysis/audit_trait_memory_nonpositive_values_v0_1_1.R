#!/usr/bin/env Rscript
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this audit script. Author verification is required before use.
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
  library(V.PhyloMaker2)
})

args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){
  i <- match(flag,args)
  if(is.na(i) || i==length(args)) stop(paste("missing",flag))
  args[[i+1]]
}
core_path <- getarg("--core")
reference_path <- getarg("--reference")
out_dir <- getarg("--out-dir")
dir.create(out_dir,recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","trait_memory_nonpositive_value_audit_design_v0_1.json"),simplifyVector=FALSE)
stopifnot(identical(design$status,"FROZEN_BEFORE_NONPOSITIVE_RAW_VALUE_AUDIT"))
stopifnot(identical(design$scope$stage,"A_RAW_DATA_VALIDITY_ONLY"))
stopifnot(isTRUE(design$scope$no_rho_recalculation))

core <- read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
ref <- read.csv(reference_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(core)!=201 || nrow(ref)!=201) stop("frozen 201-system inputs changed")
keys <- paste(core$family,core$trait_name,sep="\x1f")
ref_keys <- paste(ref$family,ref$trait_name,sep="\x1f")
if(anyDuplicated(keys) || anyDuplicated(ref_keys) || !setequal(keys,ref_keys))
  stop("core/reference family-trait graph mismatch")
if(!all(core$semantic_class=="continuous_scalar")) stop("audit population is not continuous_scalar")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN database version changed")

esc <- function(x) gsub("'","''",x,fixed=TRUE)
mk_values <- function(d){
  paste(paste0("('",esc(d$family),"','",esc(d$trait_name),"')"),collapse=",\n")
}
all_values <- mk_values(core)

# Stage 1: all-201 identity query. No source/citation string aggregation here.
species_sql <- sprintf("
WITH systems(family,trait_name) AS (VALUES %s),
base AS (
  SELECT
    a.scrubbed_species_binomial AS species,
    a.scrubbed_genus AS genus,
    a.scrubbed_family AS family,
    a.trait_name,
    CASE WHEN a.trait_value::text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
         THEN a.trait_value::numeric ELSE NULL END AS value_num,
    coalesce(nullif(trim(a.unit::text),''),'__MISSING__') AS unit_key
  FROM agg_traits a JOIN systems s
    ON a.scrubbed_family=s.family AND a.trait_name=s.trait_name
  WHERE a.scrubbed_species_binomial IS NOT NULL
    AND trim(a.scrubbed_species_binomial)<>''
    AND a.scrubbed_genus IS NOT NULL
    AND trim(a.scrubbed_genus)<>''
    AND a.trait_value IS NOT NULL
    AND trim(a.trait_value::text)<>''
    AND a.unit IS NOT NULL
    AND trim(a.unit::text)<>''
    AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
),
nb AS (SELECT * FROM base WHERE value_num IS NOT NULL)
SELECT family,trait_name,species,min(genus) AS genus,
       percentile_cont(0.5) WITHIN GROUP(ORDER BY value_num) AS species_median,
       count(*)::integer AS n_numeric_records,
       count(*) FILTER (WHERE value_num<0)::integer AS n_negative_records,
       count(*) FILTER (WHERE value_num=0)::integer AS n_zero_records,
       count(*) FILTER (WHERE value_num>0)::integer AS n_positive_records,
       min(value_num) AS min_value,max(value_num) AS max_value,
       count(DISTINCT unit_key)::integer AS n_units,
       string_agg(DISTINCT unit_key,' | ' ORDER BY unit_key) AS distinct_units
FROM nb
GROUP BY family,trait_name,species
ORDER BY family,trait_name,species;
",all_values)
sp <- .BIEN_sql(species_sql)
if(!is.data.frame(sp) || nrow(sp)<201*20) stop("species audit query unexpectedly small")
sp$species_median <- as.numeric(sp$species_median)
sp$min_value <- as.numeric(sp$min_value)
sp$max_value <- as.numeric(sp$max_value)
for(z in c("n_numeric_records","n_negative_records","n_zero_records","n_positive_records","n_units"))
  sp[[z]] <- as.integer(sp[[z]])
if(any(!is.finite(sp$species_median))) stop("nonfinite species median in audit")

classify <- function(m,nneg,nzero,n){
  if(m<0) return("NEGATIVE_MEDIAN")
  if(m==0 && nzero==n) return("ZERO_MEDIAN_ALL_ZERO")
  if(m==0) return("ZERO_MEDIAN_MIXED")
  if(nneg+nzero>0) return("POSITIVE_MEDIAN_WITH_NONPOSITIVE_RAW")
  "CLEAN_POSITIVE"
}
sp$classification <- mapply(classify,sp$species_median,sp$n_negative_records,sp$n_zero_records,sp$n_numeric_records)
sp$unit_mixed_flag <- sp$n_units>1
sp$median_nonpositive <- sp$species_median<=0
sp$raw_nonpositive <- (sp$n_negative_records+sp$n_zero_records)>0
positive_only <- unlist(design$semantic_domain$positive_only_traits,use.names=FALSE)
sp$predeclared_positive_only_trait <- sp$trait_name %in% positive_only

median_bad_systems <- unique(sp[sp$median_nonpositive,c("family","trait_name"),drop=FALSE])
raw_bad_systems <- unique(sp[sp$raw_nonpositive,c("family","trait_name"),drop=FALSE])
if(nrow(median_bad_systems)==0) stop("no nonpositive medians despite upstream blocker")

sp$key <- paste(sp$family,sp$trait_name,sep="\x1f")
median_keys <- paste(median_bad_systems$family,median_bad_systems$trait_name,sep="\x1f")
sp$phylo_status <- NA_character_
sp$in_S3 <- NA
sp$in_prune_only <- NA

# Frozen membership annotation only for systems with median <=0.
for(k in median_keys){
  z <- sp[sp$key==k,,drop=FALSE]
  capture.output(
    phy <- phylo.maker(
      z[,c("species","genus","family"),drop=FALSE],
      tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
      output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"
    ),
    file=tempfile()
  )
  if(is.null(phy$species.list)) stop(paste("phylo.maker failed for",k))
  pl <- phy$species.list
  smap <- setNames(as.character(pl$status),as.character(pl$species))
  idx <- which(sp$key==k)
  st <- unname(smap[sp$species[idx]])
  if(any(is.na(st))) stop(paste("species membership mapping failed for",k))
  sp$phylo_status[idx] <- st
  sp$in_S3[idx] <- st %in% c("prune","bind")
  sp$in_prune_only[idx] <- st=="prune"
}

# Identity gate against v0.3.
ref2 <- ref[,c("family","trait_name","S3_n_nonpositive","prune_n_nonpositive"),drop=FALSE]
counts <- lapply(split(sp,paste(sp$family,sp$trait_name,sep="\x1f")),function(z){
  data.frame(
    family=z$family[[1]],trait_name=z$trait_name[[1]],
    S3_nonpositive=sum(z$median_nonpositive & !is.na(z$in_S3) & z$in_S3),
    prune_nonpositive=sum(z$median_nonpositive & !is.na(z$in_prune_only) & z$in_prune_only)
  )
})
audit_counts <- do.call(rbind,counts)
chk <- merge(ref2,audit_counts,by=c("family","trait_name"),all=FALSE)
if(nrow(chk)!=201) stop("identity merge lost systems")
chk$S3_match <- as.integer(chk$S3_n_nonpositive)==as.integer(chk$S3_nonpositive)
chk$prune_match <- as.integer(chk$prune_n_nonpositive)==as.integer(chk$prune_nonpositive)
identity_pass <- all(chk$S3_match & chk$prune_match)
write.csv(chk,file.path(out_dir,"identity_gate.csv"),row.names=FALSE,na="")
if(!identity_pass) stop("HOLD_NONPOSITIVE_AUDIT_CROSSWALK_OR_DATA_DRIFT")
if(sum(chk$S3_n_nonpositive>0)!=25 || sum(chk$prune_n_nonpositive>0)!=18)
  stop("reference affected-system counts changed")

# Stage 2: provenance only for systems that contain any raw <=0 record.
raw_values <- mk_values(raw_bad_systems)
prov_base <- sprintf("
WITH affected(family,trait_name) AS (VALUES %s),
base AS (
  SELECT
    a.scrubbed_species_binomial AS species,
    a.scrubbed_family AS family,a.trait_name,
    CASE WHEN a.trait_value::text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
         THEN a.trait_value::numeric ELSE NULL END AS value_num,
    coalesce(nullif(trim(a.unit::text),''),'__MISSING__') AS unit_key,
    coalesce(nullif(trim(a.source::text),''),'__MISSING__') AS source_key,
    coalesce(nullif(trim(a.source_citation::text),''),'__MISSING__') AS citation_key
  FROM agg_traits a JOIN affected s
    ON a.scrubbed_family=s.family AND a.trait_name=s.trait_name
  WHERE a.scrubbed_species_binomial IS NOT NULL AND trim(a.scrubbed_species_binomial)<>''
    AND a.scrubbed_genus IS NOT NULL AND trim(a.scrubbed_genus)<>''
    AND a.trait_value IS NOT NULL AND trim(a.trait_value::text)<>''
    AND a.unit IS NOT NULL AND trim(a.unit::text)<>''
    AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
),
nb AS (SELECT * FROM base WHERE value_num IS NOT NULL)
",raw_values)

species_prov_sql <- paste0(prov_base,"
SELECT family,trait_name,species,
       count(DISTINCT source_key)::integer AS n_sources,
       string_agg(DISTINCT source_key,' | ' ORDER BY source_key) AS distinct_sources,
       count(DISTINCT citation_key)::integer AS n_citations,
       string_agg(DISTINCT citation_key,' | ' ORDER BY citation_key) AS distinct_citations
FROM nb
GROUP BY family,trait_name,species
ORDER BY family,trait_name,species;
")
sprov <- .BIEN_sql(species_prov_sql)
if(!is.data.frame(sprov)) stop("species provenance query failed")

source_sql <- paste0(prov_base,"
SELECT family,trait_name,unit_key,source_key,citation_key,
       count(*)::integer AS n_records,
       count(*) FILTER (WHERE value_num<0)::integer AS n_negative_records,
       count(*) FILTER (WHERE value_num=0)::integer AS n_zero_records,
       count(*) FILTER (WHERE value_num>0)::integer AS n_positive_records
FROM nb
GROUP BY family,trait_name,unit_key,source_key,citation_key
ORDER BY family,trait_name,n_zero_records DESC,n_negative_records DESC,n_records DESC;
")
prov <- .BIEN_sql(source_sql)
if(!is.data.frame(prov)) stop("source/unit summary query failed")
write.csv(prov,file.path(out_dir,"source_unit_summary.csv"),row.names=FALSE,na="")

values_sql <- paste0(prov_base,"
SELECT family,trait_name,value_num,unit_key,source_key,citation_key,count(*)::integer AS n_records
FROM nb
WHERE value_num<=0
GROUP BY family,trait_name,value_num,unit_key,source_key,citation_key
ORDER BY family,trait_name,value_num,unit_key,source_key,citation_key;
")
nv <- .BIEN_sql(values_sql)
if(!is.data.frame(nv)) stop("nonpositive value-frequency query failed")
write.csv(nv,file.path(out_dir,"nonpositive_raw_value_frequency.csv"),row.names=FALSE,na="")

contam <- sp[sp$raw_nonpositive,,drop=FALSE]
contam <- merge(contam,sprov,by=c("family","trait_name","species"),all.x=TRUE,sort=FALSE)
if(nrow(contam)!=sum(sp$raw_nonpositive)) stop("species provenance merge changed contaminated species count")
contam$key <- NULL
write.csv(contam,file.path(out_dir,"species_nonpositive_audit.csv"),row.names=FALSE,na="")

# System summaries over all 201 systems.
sys_rows <- lapply(split(sp,paste(sp$family,sp$trait_name,sep="\x1f")),function(z){
  data.frame(
    family=z$family[[1]],trait_name=z$trait_name[[1]],
    n_species=nrow(z),
    n_species_median_nonpositive=sum(z$median_nonpositive),
    n_species_raw_nonpositive=sum(z$raw_nonpositive),
    n_raw_records=sum(z$n_numeric_records),
    n_raw_negative=sum(z$n_negative_records),
    n_raw_zero=sum(z$n_zero_records),
    n_raw_positive=sum(z$n_positive_records),
    n_unit_mixed_species=sum(z$unit_mixed_flag),
    n_S3_median_nonpositive=sum(z$median_nonpositive & !is.na(z$in_S3) & z$in_S3),
    n_prune_median_nonpositive=sum(z$median_nonpositive & !is.na(z$in_prune_only) & z$in_prune_only)
  )
})
sys <- do.call(rbind,sys_rows)
sys$median_nonpositive_fraction <- sys$n_species_median_nonpositive/sys$n_species
sys$raw_nonpositive_fraction <- (sys$n_raw_negative+sys$n_raw_zero)/sys$n_raw_records
write.csv(sys,file.path(out_dir,"system_summary.csv"),row.names=FALSE,na="")

tr_rows <- lapply(split(sp,sp$trait_name),function(z){
  data.frame(
    trait_name=z$trait_name[[1]],n_systems=length(unique(z$family)),n_species=nrow(z),
    n_species_median_nonpositive=sum(z$median_nonpositive),
    n_species_raw_nonpositive=sum(z$raw_nonpositive),
    n_raw_records=sum(z$n_numeric_records),
    n_raw_negative=sum(z$n_negative_records),n_raw_zero=sum(z$n_zero_records),n_raw_positive=sum(z$n_positive_records),
    n_unit_mixed_species=sum(z$unit_mixed_flag),
    n_S3_median_nonpositive=sum(z$median_nonpositive & !is.na(z$in_S3) & z$in_S3),
    n_prune_median_nonpositive=sum(z$median_nonpositive & !is.na(z$in_prune_only) & z$in_prune_only)
  )
})
trs <- do.call(rbind,tr_rows)
trs$median_nonpositive_fraction <- trs$n_species_median_nonpositive/trs$n_species
trs$raw_nonpositive_fraction <- (trs$n_raw_negative+trs$n_raw_zero)/trs$n_raw_records
trs <- trs[order(-trs$n_species_median_nonpositive,trs$trait_name),]
write.csv(trs,file.path(out_dir,"trait_summary.csv"),row.names=FALSE,na="")

class_counts <- as.data.frame(table(contam$classification),stringsAsFactors=FALSE)
names(class_counts) <- c("classification","n_species")
write.csv(class_counts,file.path(out_dir,"classification_counts.csv"),row.names=FALSE,na="")

nonpos <- contam[contam$median_nonpositive,,drop=FALSE]
invalid_outside <- nonpos[!nonpos$predeclared_positive_only_trait,,drop=FALSE]

out <- list(
  version="v0.1.1",
  status="TRAIT_MEMORY_NONPOSITIVE_RAW_VALUE_AUDIT_COMPLETE",
  stage="A_RAW_DATA_VALIDITY_ONLY",
  execution="staged_query_optimization_no_scientific_change",
  observed_database_version=observed_version,
  n_systems=201,
  n_species_audited=nrow(sp),
  n_systems_with_median_nonpositive=sum(sys$n_species_median_nonpositive>0),
  n_systems_with_any_nonpositive_raw=sum(sys$n_species_raw_nonpositive>0),
  n_species_with_median_nonpositive=nrow(nonpos),
  n_species_with_any_nonpositive_raw=nrow(contam),
  n_nonpositive_median_outside_predeclared_positive_only_traits=nrow(invalid_outside),
  identity_gate=list(pass=identity_pass,S3_affected_systems=25,prune_affected_systems=18),
  classification_counts=as.list(setNames(as.integer(class_counts$n_species),class_counts$classification)),
  output_files=c("species_nonpositive_audit.csv","system_summary.csv","trait_summary.csv","source_unit_summary.csv","nonpositive_raw_value_frequency.csv","classification_counts.csv","identity_gate.csv"),
  hard_guard="No rho or downstream manuscript statistic was recomputed in Stage A."
)
write_json(out,file.path(out_dir,"result.json"),pretty=TRUE,auto_unbox=TRUE,null="null",digits=17)
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null",digits=17),"\n")
