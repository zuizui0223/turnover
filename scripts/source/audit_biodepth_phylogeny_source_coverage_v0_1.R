#!/usr/bin/env Rscript
# BIODEPTH source-only species/planting and GBOTB TPL S3 tree qualification.
# Never reads GIFT trait values, biomass responses or observed FD/PD effects.
suppressPackageStartupMessages({
  library(ape)
  library(jsonlite)
  library(V.PhyloMaker2)
})
args <- commandArgs(trailingOnly=TRUE)
key <- function(k) {i<-match(k,args);if(is.na(i)||i==length(args))stop(paste("missing",k));args[[i+1]]}
input <- key("--planting")
output <- key("--out")
x <- read.csv(input, stringsAsFactors=FALSE, check.names=FALSE)
required <- c("site","plot","species")
if(!all(required %in% colnames(x)))stop("SOURCE_HOLD: missing source planting fields")
if(nrow(x)!=1934L || length(unique(x$species))!=103L ||
    length(unique(x$plot))!=480L || length(unique(x$site))!=8L)
  stop("SOURCE_HOLD: original BIODEPTH 103 taxa/480 plots/8 fields mismatch")
if(anyDuplicated(x[,required]))stop("SOURCE_HOLD: duplicated planted taxon within site/plot")
if(any(!grepl("^[a-z-]+ [a-z-]+$",x$species)))stop("SOURCE_HOLD: original normalized names not binomial")

# The earlier BIEN/AusTraits phylogeny source chain already fixed this commit,
# but verify the actual GBOTB object and unique exact tips anew.
if(length(GBOTB.extended.TPL$tip.label)!=74529L ||
   anyDuplicated(GBOTB.extended.TPL$tip.label) ||
   any(!is.finite(GBOTB.extended.TPL$edge.length)) ||
   any(GBOTB.extended.TPL$edge.length<0) ||
   !is.rooted(GBOTB.extended.TPL))
  stop("SOURCE_HOLD: pinned GBOTB.extended.TPL source geometry unexpected")
tips <- tips.info.TPL
if(!all(c("species","genus","family") %in% names(tips)))
  stop("SOURCE_HOLD: pinned tips.info.TPL taxonomy schema unexpected")
tg <- tolower(trimws(as.character(tips$genus)))
tf <- trimws(as.character(tips$family))
if(any(!nzchar(tg)) || any(!nzchar(tf)))stop("SOURCE_HOLD: missing backbone genus/family")
families <- split(tf,tg)
unique_genus <- lapply(families, function(v)unique(v[nzchar(v)]))
safe_genus <- names(unique_genus)[lengths(unique_genus)==1L]
genus_to_family <- setNames(vapply(unique_genus[safe_genus], function(x)x[[1]], ""),safe_genus)
spp <- sort(unique(x$species))
parts <- strsplit(spp," ",fixed=TRUE)
genus <- vapply(parts, function(z)z[1],"")
ep <- vapply(parts, function(z)z[2],"")
safe <- !is.na(genus_to_family[genus]) & nzchar(unname(genus_to_family[genus]))
rejected <- spp[!safe]
name_canon <- paste0(toupper(substring(genus[safe],1,1)),substring(genus[safe],2)," ",ep[safe])
genus_canon <- paste0(toupper(substring(genus[safe],1,1)),substring(genus[safe],2))
taxo <- data.frame(species=name_canon,genus=genus_canon,
                   family=unname(genus_to_family[genus[safe]]),stringsAsFactors=FALSE)
if(anyDuplicated(taxo$species))stop("SOURCE_HOLD: duplicated canonical species")
if(nrow(taxo)==0L)stop("SOURCE_HOLD: zero exact genus-family matches")
# Count exact native tips against the 74,529-tip anchored tree.
to_tip <- function(sp)gsub(" ","_",sp,fixed=TRUE)
native <- sum(to_tip(taxo$species) %in% GBOTB.extended.TPL$tip.label)
# The pre-outcome source pass is frozen before opening any PD values or biomass.
sinked <- capture.output({
 phy <- phylo.maker(taxo,tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                    output.sp.list=TRUE,output.tree=FALSE,scenarios="S3")
})
if(is.null(phy$species.list) || is.null(phy$scenario.3))
  stop("SOURCE_HOLD: V.PhyloMaker2 S3 returned no complete source crosswalk")
raw_status <- as.character(phy$species.list$status)
raw_species <- tolower(gsub("_"," ",as.character(phy$species.list$species),fixed=TRUE))
if(length(raw_status)!=nrow(taxo) || any(is.na(raw_status)) ||
   anyDuplicated(raw_species) || !setequal(raw_species,tolower(taxo$species)))
  stop("SOURCE_HOLD: V.PhyloMaker2 source species/status identity incomplete")
status <- raw_status[match(tolower(taxo$species),raw_species)]
if(any(is.na(status)))stop("SOURCE_HOLD: impossible matched phylo statuses")
if(!all(status %in% c("prune","bind","fail to bind")))
  stop("SOURCE_HOLD: unexpected V.PhyloMaker2 species status")
tree <- phy$scenario.3
resol <- status %in% c("prune","bind")
if(!inherits(tree,"phylo") || anyDuplicated(tree$tip.label) ||
   any(!is.finite(tree$edge.length)) || any(tree$edge.length<0))
  stop("SOURCE_HOLD: generated S3 tree is not finite")
if(sum(resol)!=length(tree$tip.label))
  stop("SOURCE_HOLD: returned S3 tip count does not match source resolved taxa")
if(sum(status=="prune")!=native)
  stop("SOURCE_HOLD: direct native tip count not equal to package status")
if(sum(resol)>0) {
  resolved <- tolower(gsub("_"," ",tree$tip.label,fixed=TRUE))
  if(!setequal(resolved,tolower(taxo$species[resol])))
    stop("SOURCE_HOLD: S3 exact plant species tip set changed")
}
kept <- setNames(status,spp[safe])
is_ok <- spp %in% names(kept)[kept %in% c("prune","bind")]
resolved_names <- spp[is_ok]
covered_plot <- vapply(split(x$species,x$plot),
                       function(z)sum(z %in% resolved_names)>=3,logical(1))
plot_source <- unique(x[,c("plot","site"),drop=FALSE])
site_counts <- tapply(as.integer(covered_plot[plot_source$plot]),plot_source$site,sum)
site_counts <- sort(as.integer(site_counts))
n_site8 <- sum(site_counts>=8)
n_plot3 <- sum(covered_plot)
n_family <- length(unique(taxo$family[resol]))
qualification <- sum(safe)>=70 && sum(resol)>=60 && n_family>=6 &&
                 native>=25 && n_plot3>=200 && n_site8>=6
out <- list(version="v0.1",status=if(qualification)"BIODEPTH_GBOTB_S3_SOURCE_COVERAGE_PASS" else "HOLD_BIODEPTH_GBOTB_S3_SOURCE_COVERAGE",
  type="SOURCE_ONLY",tree_source="jinyizju/V.PhyloMaker2@7af3fb5152f691af2e4ec9d5e2e467d1b50505e9",
  backbone="GBOTB.extended.TPL",scenario="S3",tree_backbone_tips=74529,
  source_original_taxa=length(spp),source_original_plots=length(unique(x$plot)),
  source_original_planted_incidence=nrow(x),source_original_sites=length(unique(x$site)),
  n_exact_genus_family=as.integer(sum(safe)),
  n_unresolved_genus_family=length(rejected),
  n_native_tips=as.integer(native),
  n_S3_prune=sum(status=="prune"),n_S3_bind=sum(status=="bind"),
  n_S3_fail=sum(status=="fail to bind"),
  n_S3_eligible=as.integer(sum(resol)),
  n_resolved_families=as.integer(n_family),
  n_source_plots_with_at_least_3_S3_species=as.integer(n_plot3),
  n_sites_with_at_least_8_S3_plots=as.integer(n_site8),
  site_plot_counts_with_3_species=as.list(tapply(as.integer(covered_plot[plot_source$plot]),plot_source$site,sum)),
  thresholds=list(min_exact_genus_family=70,min_S3_eligible=60,min_resolved_families=6,min_native_tips=25,
                  min_plots_atleast3_S3=200,min_sites_atleast8_plots=6),
  status_taxa_match_S3_count=TRUE,
  n_biomass_records_opened=0, n_trait_values_opened=0, n_PD_or_FD_effects_estimated=0,
  preserved_prior_biomass_findings=TRUE,
  next_gate=if(qualification) "SOURCE_ONLY joint GIFT-height × phylogeny original-plot coverage; freeze new PD→FD model before response access"
  else "HOLD: do not use this source tree for PD→FD biomass analysis without a new separately motivated protocol",
  hard_nonclaims=c("Taxonomic accepted-name link does not prove trait or phylogeny independence",
       "S3-bound tips are not direct backbone-native species", "No PD, FD, biomass, K or evolutionary-process result was estimated",
       "Earlier BIODEPTH strong source gate, BIEN global cross-axis gate and NEON auth HOLD remain unchanged"))
dir.create(dirname(output),showWarnings=FALSE,recursive=TRUE)
write_json(out,output,pretty=TRUE,auto_unbox=TRUE,null="null")
cat("BIODEPTH_PHYLOGENY_SOURCE_ONLY ",toJSON(out,auto_unbox=TRUE,null="null"),"\n",sep="")
