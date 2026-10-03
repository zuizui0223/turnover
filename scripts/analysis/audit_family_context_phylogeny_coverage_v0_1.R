#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(ape)
  library(V.PhyloMaker2)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path<-getarg("--effects")
out_path<-getarg("--out")
table_path<-getarg("--table-out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)

x<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(x)!=201 || length(unique(x$family))!=45) stop("unexpected fixed core")
if(!all(c("family","trait_name","n_species_prune") %in% names(x))) stop("effect table missing core metadata")

# Family representatives are defined from backbone-native final-core tips.
# The exact species names are not persisted by prior real-effect artifacts, so recover
# only the admitted family species pool from the same frozen BIEN query in the full
# execution workflow. This preflight consumes a family-tip membership table.
tips_path<-getarg("--family-tips")
ft<-read.csv(tips_path,stringsAsFactors=FALSE,check.names=FALSE)
if(!all(c("family","tip") %in% names(ft))) stop("family-tip table malformed")
ft<-unique(ft)
families<-sort(unique(x$family))
rows<-list()
for(i in seq_along(families)){
  fam<-families[[i]]
  tips<-intersect(unique(ft$tip[ft$family==fam]),GBOTB.extended.TPL$tip.label)
  n<-length(tips)
  if(n>=2){
    node<-getMRCA(GBOTB.extended.TPL,tips)
    if(is.null(node) || is.na(node)) stop(paste("MRCA failed",fam))
    kind<-"MRCA"
  } else if(n==1){
    node<-match(tips,GBOTB.extended.TPL$tip.label)
    kind<-"TIP"
  } else {
    node<-NA_integer_; kind<-"NONE"
  }
  rows[[i]]<-data.frame(family=fam,n_native_tips=n,representative_node=node,representative_kind=kind,stringsAsFactors=FALSE)
}
tab<-do.call(rbind,rows)
write.csv(tab,table_path,row.names=FALSE,na="")
valid<-tab[!is.na(tab$representative_node),,drop=FALSE]
gate<-nrow(valid)>=30
out<-list(
  version="v0.1",
  status=if(gate)"FAMILY_CONTEXT_PHYLOGENY_COVERAGE_PASS" else "HOLD_FAMILY_CONTEXT_PHYLOGENY_COVERAGE",
  post_outcome_exploratory=TRUE,
  n_core_families=45,
  n_valid_family_representatives=nrow(valid),
  n_MRCA=sum(valid$representative_kind=="MRCA"),
  n_single_tip=sum(valid$representative_kind=="TIP"),
  minimum_required_families=30,
  gate_pass=gate,
  next_gate=if(gate)"Compute frozen family-context score and family-pair phylogenetic association." else "Stop exploratory family-phylogeny analysis."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
