#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(V.PhyloMaker2);library(jsonlite)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
inp<-getarg("--species-table");sid<-getarg("--id");fam<-getarg("--family");tr<-getarg("--trait");typ<-getarg("--class");out<-getarg("--out")
sp<-read.csv(inp,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<1)stop("empty species list")
capture.output(p<-phylo.maker(sp[,c("species","genus","family")],tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),file=tempfile())
if(is.null(p$species.list))stop("phylo.maker species.list missing")
st<-as.character(p$species.list$status)
np<-sum(st=="prune");nb<-sum(st=="bind");nf<-sum(st=="fail to bind");primary<-np+nb
reasons<-character();if(primary<20)reasons<-c(reasons,"PRIMARY_RESOLVABLE_LT20");if(np<20)reasons<-c(reasons,"PRUNE_ONLY_LT20")
x<-list(version="v0.4.3",system_id=sid,family=fam,trait_name=tr,config_type=typ,n_input_species=nrow(sp),n_prune=np,n_bind=nb,n_fail_to_bind=nf,primary_resolvable_species=primary,crosswalk_pass=length(reasons)==0,hold_reason=paste(reasons,collapse=";"),outcome_blind=TRUE,austraits_memory_effects_opened=FALSE)
write_json(x,out,pretty=TRUE,auto_unbox=TRUE,null="null");cat(toJSON(x,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
