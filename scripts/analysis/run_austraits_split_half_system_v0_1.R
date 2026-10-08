#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(ape);library(V.PhyloMaker2)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
sid<-getarg("--system-id");family<-getarg("--family");trait_name<-getarg("--trait")
state_path<-getarg("--state-table");expected_prune<-as.integer(getarg("--expected-prune"));expected_bind<-as.integer(getarg("--expected-bind"))
frozen_s3<-as.numeric(getarg("--frozen-s3"));frozen_prune<-as.numeric(getarg("--frozen-prune"));out_path<-getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
sp<-read.csv(state_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<40||any(!is.finite(sp$state_num))||any(sp$state_num<=0))stop("invalid split-half state table")
sp$log_state<-log(sp$state_num)

capture.output(
 p<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
                tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
 file=tempfile()
)
if(is.null(p$species.list)||is.null(p$scenario.3))stop("phylo.maker failed")
st<-as.character(p$species.list$status)
np<-sum(st=="prune",na.rm=TRUE);nb<-sum(st=="bind",na.rm=TRUE);nf<-sum(st=="fail to bind",na.rm=TRUE)
ef<-nrow(sp)-expected_prune-expected_bind
if(np!=expected_prune||nb!=expected_bind||nf!=ef)stop("crosswalk identity mismatch")
if(np<40)stop("prune support below frozen split-half threshold")

norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
state_map<-setNames(sp$log_state,sp$tip)
tree_s3<-p$scenario.3
prune_names<-norm_species(as.character(p$species.list$species[st=="prune"]))
tree_prune<-keep.tip(GBOTB.extended.TPL,prune_names)

rho_subset<-function(D,y,idx){
 sep<-as.numeric(as.dist(D[idx,idx,drop=FALSE]))
 diss<-as.numeric(dist(y[idx]))
 if(length(sep)!=length(diss)||length(unique(diss))<2)stop("invalid split dissimilarity")
 z<-suppressWarnings(cor(sep,diss,method="spearman",use="complete.obs"))
 if(!is.finite(z))stop("nonfinite split rho")
 as.numeric(z)
}
axis_eval<-function(tree,axis,seed_offset,frozen){
 tips<-tree$tip.label
 y<-unname(state_map[tips])
 if(any(!is.finite(y)))stop("state mapping failure")
 D<-cophenetic.phylo(tree)
 full<-rho_subset(D,y,seq_along(y))
 if(abs(full-frozen)>0.00011)stop(sprintf("full rho identity mismatch %s: %.8f vs frozen %.8f",axis,full,frozen))
 sidnum<-as.integer(gsub("[^0-9]","",sid))
 splits<-list()
 for(rep in 1:3){
  set.seed(20261007 + sidnum*100 + seed_offset + rep)
  ord<-sample.int(length(y))
  nA<-floor(length(y)/2)
  ia<-ord[seq_len(nA)];ib<-ord[(nA+1):length(y)]
  if(length(ia)<20||length(ib)<20)stop("split half below 20 tips")
  splits[[rep]]<-list(replicate=rep,n_A=length(ia),n_B=length(ib),
                      rho_A=rho_subset(D,y,ia),rho_B=rho_subset(D,y,ib))
 }
 list(n_tips=length(y),full_rho=full,splits=splits)
}
out<-list(
 version="v0.1",status="AUSTRAITS_SPLIT_HALF_SYSTEM_ESTIMATED",
 system_id=sid,family=family,trait_name=trait_name,
 S3=axis_eval(tree_s3,"S3",0,frozen_s3),
 prune_only=axis_eval(tree_prune,"prune",1000000,frozen_prune),
 split_replicates=3,master_seed=20261007,
 raw_trait_states_persisted=FALSE,species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
