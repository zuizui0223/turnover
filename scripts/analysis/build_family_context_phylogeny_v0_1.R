#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(ape);library(V.PhyloMaker2)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
tips_path<-getarg("--family-tips"); reps_path<-getarg("--reps-out"); dist_path<-getarg("--dist-out"); result_path<-getarg("--result")
ft<-read.csv(tips_path,stringsAsFactors=FALSE,check.names=FALSE)
families<-sort(unique(ft$family))
rows<-list()
for(i in seq_along(families)){
 fam<-families[[i]]
 tips<-intersect(unique(ft$tip[ft$family==fam]),GBOTB.extended.TPL$tip.label)
 if(length(tips)>=2){node<-getMRCA(GBOTB.extended.TPL,tips);kind<-"MRCA"}
 else if(length(tips)==1){node<-match(tips,GBOTB.extended.TPL$tip.label);kind<-"TIP"}
 else {node<-NA_integer_;kind<-"NONE"}
 rows[[i]]<-data.frame(family=fam,n_native_tips=length(tips),representative_node=node,representative_kind=kind,stringsAsFactors=FALSE)
}
reps<-do.call(rbind,rows);write.csv(reps,reps_path,row.names=FALSE,na="")
valid<-reps[!is.na(reps$representative_node),,drop=FALSE]
# Convert node/tip representatives to pairwise patristic distances using ape node.depth.edgelength.
depth<-node.depth.edgelength(GBOTB.extended.TPL)
ancestor_chain<-function(node){
 out<-integer();cur<-node
 repeat{
   out<-c(out,cur)
   e<-which(GBOTB.extended.TPL$edge[,2]==cur)
   if(!length(e))break
   cur<-GBOTB.extended.TPL$edge[e[1],1]
 }
 out
}
node_distance<-function(a,b){
 aa<-ancestor_chain(a);bb<-ancestor_chain(b);common<-intersect(aa,bb)
 if(!length(common))stop("no common ancestor")
 mrca<-common[which.max(depth[common])]
 depth[a]+depth[b]-2*depth[mrca]
}
pairs<-list();k<-0L
for(i in seq_len(nrow(valid)-1))for(j in (i+1):nrow(valid)){
 k<-k+1L
 pairs[[k]]<-data.frame(family1=valid$family[i],family2=valid$family[j],
   patristic_distance=node_distance(valid$representative_node[i],valid$representative_node[j]))
}
pd<-do.call(rbind,pairs);write.csv(pd,dist_path,row.names=FALSE)
gate<-nrow(valid)>=30
out<-list(version="v0.1",status=if(gate)"FAMILY_CONTEXT_PHYLOGENY_COVERAGE_PASS" else "HOLD_FAMILY_CONTEXT_PHYLOGENY_COVERAGE",
 post_outcome_exploratory=TRUE,n_families_with_native_tips=length(families),n_valid_family_representatives=nrow(valid),
 n_MRCA=sum(valid$representative_kind=="MRCA"),n_single_tip=sum(valid$representative_kind=="TIP"),
 n_family_pairs=nrow(pd),minimum_required_families=30,gate_pass=gate)
write_json(out,result_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
