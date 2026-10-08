#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(ape);library(V.PhyloMaker2)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
cid<-getarg("--cell-id");family<-getarg("--family");ta<-getarg("--trait-a");tb<-getarg("--trait-b")
state_path<-getarg("--state-table");out_path<-getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
sp<-read.csv(state_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20)stop("shared species below 20")
if(any(!is.finite(sp$state_a))||any(!is.finite(sp$state_b))||any(sp$state_a<=0)||any(sp$state_b<=0))stop("invalid positive states")
capture.output(
 p<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
                tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
 file=tempfile()
)
if(is.null(p$species.list)||is.null(p$scenario.3))stop("phylo.maker failed")
st<-as.character(p$species.list$status)
np<-sum(st=="prune",na.rm=TRUE);nb<-sum(st=="bind",na.rm=TRUE);nf<-sum(st=="fail to bind",na.rm=TRUE)
if(np<20||np+nb<20){
 out<-list(version="v0.1",status="HOLD_PAIRED_PHYLOGENY_SUPPORT",cell_id=cid,family=family,trait_a=ta,trait_b=tb,
           n_shared_species=nrow(sp),n_prune=np,n_bind=nb,n_fail_to_bind=nf)
 write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null");quit(save="no",status=0)
}
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
a_map<-setNames(log(sp$state_a),sp$tip);b_map<-setNames(log(sp$state_b),sp$tip)
tree_s3<-p$scenario.3
prune_names<-norm_species(as.character(p$species.list$species[st=="prune"]))
tree_prune<-keep.tip(GBOTB.extended.TPL,prune_names)

rho_one<-function(tree,map){
 tips<-tree$tip.label;y<-unname(map[tips])
 if(any(!is.finite(y)))stop("state map failure")
 sep<-as.numeric(as.dist(cophenetic.phylo(tree)));diss<-as.numeric(dist(y))
 if(length(sep)!=length(diss)||length(unique(diss))<2)stop("invalid paired geometry")
 r<-suppressWarnings(cor(sep,diss,method="spearman",use="complete.obs"))
 if(!is.finite(r))stop("nonfinite paired rho")
 as.numeric(r)
}
out<-list(
 version="v0.1",status="PAIRED_SPECIES_RHO_ESTIMATED",
 cell_id=cid,family=family,trait_a=ta,trait_b=tb,
 n_shared_species=nrow(sp),n_S3=length(tree_s3$tip.label),n_prune=length(tree_prune$tip.label),
 n_bind=nb,n_fail_to_bind=nf,
 S3_rho_a=rho_one(tree_s3,a_map),S3_rho_b=rho_one(tree_s3,b_map),
 prune_rho_a=rho_one(tree_prune,a_map),prune_rho_b=rho_one(tree_prune,b_map),
 species_names_persisted=FALSE,states_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
