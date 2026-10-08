#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(ape);library(V.PhyloMaker2);library(phytools)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
sid<-getarg("--system-id");fam<-getarg("--family");trait<-getarg("--trait");p<-getarg("--state-table")
ep<-as.integer(getarg("--expected-prune")); eb<-as.integer(getarg("--expected-bind")); out<-getarg("--out")
sp<-read.csv(p,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20||any(!is.finite(sp$state_num))||any(sp$state_num<=0))stop("invalid K state table")
sp$log_state<-log(sp$state_num)
capture.output(
  ph<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
                  tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                  output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
  file=tempfile()
)
st<-as.character(ph$species.list$status)
np<-sum(st=="prune",na.rm=TRUE);nb<-sum(st=="bind",na.rm=TRUE);nf<-sum(st=="fail to bind",na.rm=TRUE)
ef<-nrow(sp)-ep-eb
if(np!=ep||nb!=eb||nf!=ef)stop("crosswalk status-count mismatch")
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(sp$species); m<-setNames(sp$log_state,sp$tip)
s3<-ph$scenario.3
prnames<-norm_species(as.character(ph$species.list$species[st=="prune"]))
pr<-keep.tip(GBOTB.extended.TPL,prnames)
getK<-function(tr){
  x<-unname(m[tr$tip.label]); names(x)<-tr$tip.label
  if(any(!is.finite(x))||length(unique(x))<2)stop("invalid K values")
  k<-as.numeric(phylosig(tr,x,method="K",test=FALSE))
  if(!is.finite(k)||k<=0)stop("nonpositive K")
  k
}
K3<-getK(s3); Kp<-getK(pr)
ans<-list(version="v0.1",status="AUSTRAITS_BLOMBERG_K_SYSTEM_ESTIMATED",
          system_id=sid,family=fam,trait_name=trait,
          n_species_S3=length(s3$tip.label),n_species_prune=length(pr$tip.label),
          S3_K=K3,prune_K=Kp,S3_logK=log(K3),prune_logK=log(Kp))
dir.create(dirname(out),recursive=TRUE,showWarnings=FALSE)
write_json(ans,out,pretty=TRUE,auto_unbox=TRUE);cat(toJSON(ans,pretty=TRUE,auto_unbox=TRUE),"\n")
