#!/usr/bin/env Rscript
# Homogeneous stationary OU K calibration on frozen 254 AusTraits system trees.
# Phase 'reference' obtains source-native time depth without K outcomes.
# Phase 'simulate' uses one globally common alpha=c/T_ref for all systems.
suppressPackageStartupMessages({
  library(jsonlite);library(ape);library(V.PhyloMaker2)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){
 i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f))
 args[[i+1]]
}
sid<-getarg("--system-id")
family<-getarg("--family")
trait<-getarg("--trait")
states_file<-getarg("--state-table")
np_expected<-as.integer(getarg("--expected-prune"))
nb_expected<-as.integer(getarg("--expected-bind"))
out_file<-getarg("--out")
phase<-Sys.getenv("AUSTRAITS_OU_PHASE","")
if(!phase %in% c("reference","simulate"))stop("AUSTRAITS_OU_PHASE must be reference or simulate")

sp<-read.csv(states_file,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20 || any(!is.finite(sp$state_num)) || any(sp$state_num<=0))
  stop("invalid source-native positive-numeric species states")
sp$log_state<-log(sp$state_num)
capture.output(
 p<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
               tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
               output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
 file=tempfile()
)
st<-as.character(p$species.list$status)
np<-sum(st=="prune",na.rm=TRUE)
nb<-sum(st=="bind",na.rm=TRUE)
nf<-sum(st=="fail to bind",na.rm=TRUE)
if(np!=np_expected || nb!=nb_expected || nf!=nrow(sp)-np_expected-nb_expected)
  stop("frozen source-native species-to-tree crosswalk changed")
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
state_map<-setNames(sp$log_state,sp$tip)
prune_names<-norm_species(as.character(p$species.list$species[st=="prune"]))
trees<-list(S3=p$scenario.3,prune_only=keep.tip(GBOTB.extended.TPL,prune_names))
ctxs<-list()
for(axis in names(trees)){
 tr<-ape::reorder.phylo(trees[[axis]],"cladewise")
 n<-length(tr$tip.label)
 lengths<-tr$edge.length
 if(n<20 || is.null(lengths)||any(!is.finite(lengths))||any(lengths<0))
   stop("invalid frozen tree edges")
 edge<-tr$edge
 root<-setdiff(unique(edge[,1]),edge[,2])
 if(length(root)!=1)stop("source-native tree root is not unique")
 depth<-ape::node.depth.edgelength(tr)
 tipmax<-max(depth[seq_len(n)])
 if(!is.finite(tipmax)||tipmax<=0)stop("invalid tree time depth")
 ctxs[[axis]]<-list(tr=tr,n=n,edge=edge,ell=lengths,
                   root=as.integer(root),post=rev(unique(edge[,1])),
                   depth=tipmax,traceC=sum(depth[seq_len(n)]))
}

ans<-list(version="v0.1",
          system_id=sid,family=family,trait_name=trait,
          n_input_species=nrow(sp),n_prune=np,n_bind=nb,n_fail_to_bind=nf,
          n_scenarios=3,ou_null_replicates_per_scenario=256,
          source_tip_states_persisted=FALSE,species_names_persisted=FALSE)

if(phase=="reference"){
 ans$status<-"AUSTRAITS_REAL_TREE_OU_DEPTH_REFERENCE_ESTIMATED"
 ans$axes<-lapply(ctxs,function(z)list(n_tips=z$n,maximum_root_to_tip_depth=z$depth))
}else{
 Tpath<-Sys.getenv("AUSTRAITS_OU_TREF_FILE","")
 Kpath<-Sys.getenv("AUSTRAITS_OU_K_REFERENCE_FILE","")
 if(!file.exists(Tpath)||!file.exists(Kpath))stop("missing frozen OU reference or K archive")
 design<-fromJSON(Tpath)
 if(design$status!="AUSTRAITS_REAL_TREE_OU_TIME_REFERENCE_FROZEN"||
    design$n_systems!=254 || design$n_axis_tree_samples!=508)
    stop("incorrect/partial OU time-scale reference")
 Tref<-as.numeric(design$T_ref)
 if(!is.finite(Tref)||Tref<=0)stop("invalid T_ref")
 kdata<-read.csv(Kpath,stringsAsFactors=FALSE,check.names=FALSE)
 row<-kdata[kdata$system_id==sid,,drop=FALSE]
 if(nrow(row)!=1||row$family!=family||row$trait_name!=trait)
    stop("wrong frozen source-native observed-K identity")

 cacheDir<-"build/rcpp-cache"
 dir.create(cacheDir,recursive=TRUE,showWarnings=FALSE)
 Rcpp::sourceCpp("scripts/analysis/austraits_ou_k_kernel_v0_1.cpp",
        cacheDir=cacheDir,rebuild=FALSE,showOutput=FALSE,verbose=FALSE)
 labels<-c("c0p25","c1","c4")
 cs<-c(0.25,1,4)
 sidnum<-as.integer(gsub("[^0-9]","",sid))
 if(is.na(sidnum))stop("system id must contain integer")
 results<-list()
 for(axis in names(ctxs)){
   z<-ctxs[[axis]]
   obs<-unname(state_map[z$tr$tip.label])
   if(any(!is.finite(obs)))stop("trait values missing for reconstructed tree")
   known<-if(axis=="S3")as.numeric(row$S3_K)else as.numeric(row$prune_K)
   kfast<-fast_k_real_tree_cpp(z$edge,z$ell,z$n,z$post,z$root,z$traceC,obs)
   if(abs(kfast-known)>0.0002)
     stop(sprintf("reconstructed fast K mismatch for %s: %.8f vs %.8f",axis,kfast,known))
   sc<-list()
   for(i in seq_along(cs)){
     alpha<-cs[[i]]/Tref
     set.seed(20261008L+sidnum*101L+
             if(axis=="S3")0L else 1000000L+
             (i-1L)*2000000L)
     draw<-simulate_shared_ou_logK_cpp(z$edge,z$ell,z$n,z$post,z$root,
                         z$traceC,alpha,256L)
     if(length(draw)!=256||any(!is.finite(draw)))stop("nonfinite OU K simulation")
     sc[[labels[[i]]]]<-list(
       dimensionless_alpha=cs[[i]],alpha=alpha,
       logK=as.list(as.numeric(draw)))
   }
   results[[axis]]<-list(
     n_tips=z$n,maximum_root_to_tip_depth=z$depth,
     observed_logK=log(known),
     relative_fast_K_error=abs(kfast-known)/max(1,known),
     scenarios=sc)
 }
 ans$status<-"AUSTRAITS_REAL_TREE_SHARED_OU_NULL_SYSTEM_ESTIMATED"
 ans$T_ref=Tref
 ans$stationary_root=TRUE
 ans$root_theta=0
 ans$shared_diffusion_sigma2=1
 ans$axes<-results
}
dir.create(dirname(out_file),recursive=TRUE,showWarnings=FALSE)
write_json(ans,out_file,pretty=TRUE,auto_unbox=TRUE,null="null",digits=15)
cat(toJSON(list(status=ans$status,system_id=sid,
                phase=phase,n_tips_S3=ctxs$S3$n,
                max_tip_depth_S3=ctxs$S3$depth),auto_unbox=TRUE),"\n")
