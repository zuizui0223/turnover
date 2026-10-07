#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(ape);library(V.PhyloMaker2)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
sid<-getarg("--system-id");family<-getarg("--family");trait_name<-getarg("--trait")
sp_path<-getarg("--species-table");expected_prune<-as.integer(getarg("--expected-prune"))
expected_bind<-as.integer(getarg("--expected-bind"));out_path<-getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
sp<-read.csv(sp_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20)stop("species list below 20")

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
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
prune_names<-norm_species(as.character(p$species.list$species[st=="prune"]))
tree_s3<-p$scenario.3
tree_prune<-keep.tip(GBOTB.extended.TPL,prune_names)

safe_cv<-function(v){
 v<-as.numeric(v);v<-v[is.finite(v)]
 if(length(v)<2||mean(v)==0)return(NA_real_)
 sd(v)/mean(v)
}
metrics<-function(tr){
 tr<-reorder.phylo(tr,"cladewise")
 n<-length(tr$tip.label);M<-n*(n-1)/2
 D<-cophenetic.phylo(tr);d<-as.numeric(as.dist(D));rm(D)
 if(length(d)!=M||any(!is.finite(d)))stop("invalid patristic distances")
 tab<-table(d)
 deg<-table(tr$edge[,1])
 internal<-as.integer(names(deg))
 internal_deg<-as.integer(deg)
 pend<-tr$edge.length[tr$edge[,2] <= n]
 list(
   n_tips=n,
   n_pairs=M,
   n_internal_nodes=tr$Nnode,
   polytomy_burden=if(n>1)1-tr$Nnode/(n-1) else NA_real_,
   multifurcating_internal_fraction=if(length(internal_deg))mean(internal_deg>2) else NA_real_,
   pairwise_distance_cv=safe_cv(d),
   pairwise_unique_fraction=length(tab)/length(d),
   max_distance_tie_share=max(as.numeric(tab))/length(d),
   pendant_branch_cv=safe_cv(pend),
   zero_edge_fraction=mean(tr$edge.length==0)
 )
}
out<-list(
 version="v0.1",status="AUSTRAITS_TREE_GEOMETRY_SYSTEM_ESTIMATED",
 system_id=sid,family=family,trait_name=trait_name,
 n_input_species=nrow(sp),n_prune=np,n_bind=nb,n_fail_to_bind=nf,
 S3=metrics(tree_s3),prune_only=metrics(tree_prune),
 outcome_opened_elsewhere=TRUE,
 raw_trait_states_persisted=FALSE,species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
