#!/usr/bin/env Rscript
# Source-calibrated observational-dispersion sensitivity on exact AusTraits K trees.
# Frozen after original K/OU results, before seeing source-dispersion magnitude.
suppressPackageStartupMessages({library(jsonlite);library(ape);library(V.PhyloMaker2)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){
  i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f))
  args[[i+1]]
}
sid<-getarg("--system-id");family<-getarg("--family");trait<-getarg("--trait")
statesfile<-getarg("--state-table")
expected_prune<-as.integer(getarg("--expected-prune"))
expected_bind<-as.integer(getarg("--expected-bind"))
outpath<-getarg("--out")
if(trait=="seed_height")stop("seed_height was excluded by source gate")
sourcefile<-Sys.getenv("AUSTRAITS_SOURCE_DISPERSION_FILE","")
timefile<-Sys.getenv("AUSTRAITS_OU_TREF_FILE","")
kfile<-Sys.getenv("AUSTRAITS_OU_K_REFERENCE_FILE","")
if(!all(file.exists(c(sourcefile,timefile,kfile))))stop("missing pinned source/time/K identity inputs")

source<-fromJSON(sourcefile)
if(source$status!="AUSTRAITS_K_CROSS_SOURCE_DISPERSION_ESTIMATED"||
   !isTRUE(source$no_K_response_used) || source$eligible_traits!=12)
  stop("source calibration has unexpected provenance/coverage")
design<-fromJSON("data/austraits_k_source_dispersion_ou_null_design_v0_1.json")
if(design$status!="POST_OBSERVED_K_AND_SHARED_OU_PRE_SOURCE_DISPERSION_OUTCOMES_FROZEN")
   stop("unfrozen source-error forward process")
global<-source$traits[[trait]]$source_log_variance_ratio_median
if(!isTRUE(source$traits[[trait]]$calibratable_for_followon_process_null)||
   length(global)!=1||!is.finite(global)||global<0)
   stop("uncalibrated named trait source ratio")
sr<-source$systems[source$systems$system_id==sid,]
if(nrow(sr)!=1||sr$family!=family||sr$trait_name!=trait)
   stop("family/trait source identity mismatch")
local<-if(isTRUE(sr$calibratable) && is.finite(sr$relative_source_dispersion))
    as.numeric(sr$relative_source_dispersion) else as.numeric(global)
if(!is.finite(local)||local<0)stop("invalid local dispersion")
fallback<-!isTRUE(sr$calibratable)
reference<-fromJSON(timefile)
if(reference$status!="AUSTRAITS_REAL_TREE_OU_TIME_REFERENCE_FROZEN"||
   reference$n_systems!=254||reference$n_axis_tree_samples!=508)
  stop("wrong OU time reference")
Tref<-as.numeric(reference$T_ref)
Ktable<-read.csv(kfile,stringsAsFactors=FALSE,check.names=FALSE)
Krow<-Ktable[Ktable$system_id==sid,,drop=FALSE]
if(nrow(Krow)!=1||Krow$family!=family||Krow$trait_name!=trait)
   stop("wrong original archived K identity")
sp<-read.csv(statesfile,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20||any(!is.finite(sp$state_num))||any(sp$state_num<=0))
   stop("invalid exact source-native positive states")
sp$log_state<-log(sp$state_num)
capture.output(ph<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
   tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
   output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),file=tempfile())
statuses<-as.character(ph$species.list$status)
np<-sum(statuses=="prune",na.rm=TRUE);nb<-sum(statuses=="bind",na.rm=TRUE)
nf<-sum(statuses=="fail to bind",na.rm=TRUE)
if(np!=expected_prune||nb!=expected_bind||
   nf!=nrow(sp)-expected_prune-expected_bind)
   stop("source/native V.PhyloMaker2 crosswalk changed")
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
statemap<-setNames(sp$log_state,sp$tip)
prune_names<-norm_species(as.character(ph$species.list$species[statuses=="prune"]))
trees<-list(S3=ph$scenario.3,prune_only=keep.tip(GBOTB.extended.TPL,prune_names))
dir.create("build/rcpp-source-cache",recursive=TRUE,showWarnings=FALSE)
Rcpp::sourceCpp("scripts/analysis/austraits_ou_source_noise_k_kernel_v0_1.cpp",
  cacheDir="build/rcpp-source-cache",rebuild=FALSE,showOutput=FALSE,verbose=FALSE)
sidnum<-as.integer(gsub("[^0-9]","",sid))
if(is.na(sidnum))stop("bad system ID")
axes<-list()
for(axis in names(trees)){
  tr<-ape::reorder.phylo(trees[[axis]],"cladewise")
  n<-length(tr$tip.label)
  edge<-tr$edge; ell<-tr$edge.length
  if(n<20||is.null(ell)||any(!is.finite(ell))||any(ell<0))
    stop("invalid native tree")
  root<-setdiff(unique(edge[,1]),edge[,2])
  if(length(root)!=1)stop("invalid native root")
  depths<-ape::node.depth.edgelength(tr)
  traceC<-sum(depths[seq_len(n)])
  post<-rev(unique(edge[,1]))
  observed<-unname(statemap[tr$tip.label])
  if(any(!is.finite(observed)))stop("missing observed tip states")
  frozen_K<-if(axis=="S3")as.numeric(Krow$S3_K) else as.numeric(Krow$prune_K)
  checkK<-fast_k_real_tree_cpp(edge,ell,n,post,root,traceC,observed)
  if(abs(checkK-frozen_K)>0.0002)
     stop(sprintf("K identity differs, %s: %.9f versus %.9f",axis,checkK,frozen_K))
  sc<-list()
  for(i in 1:3){
    c<-c(0.25,1,4)[[i]]
    label<-c("c0p25","c1","c4")[[i]]
    alpha<-c/Tref
    if(abs(alpha-reference$absolute_alpha_grid[[label]])>1e-10*alpha)
       stop("changed global OU alpha")
    set.seed(20261008L+sidnum*101L+(if(axis=="S3")0L else 1000000L)+(i-1L)*2000000L)
    raw<-simulate_shared_ou_source_noise_logK_cpp(edge,ell,n,post,root,traceC,
                 alpha,as.numeric(global),as.numeric(local),256L)
    if(length(raw$trait_global)!=256||length(raw$system_local)!=256 ||
       any(!is.finite(raw$trait_global))||any(!is.finite(raw$system_local)))
       stop("invalid source-noise K replicates")
    sc[[label]]<-list(alpha=alpha,models=list(
       trait_global=list(logK=as.list(as.numeric(raw$trait_global))),
       system_local=list(logK=as.list(as.numeric(raw$system_local)))))
  }
  axes[[axis]]<-list(n_tips=n,observed_logK=log(frozen_K),
                    observed_fast_K_error=abs(checkK-frozen_K),
                    scenarios=sc)
}
ans<-list(version="v0.1",status="AUSTRAITS_K_SOURCE_NOISE_OU_SYSTEM_ESTIMATED",
   system_id=sid,family=family,trait_name=trait,
   T_ref=Tref,eta_global=as.numeric(global),eta_local=as.numeric(local),
   eta_local_fallback=fallback,n_models=2,n_scenarios=3,
   replicates_per_model=256,axes=axes,
   species_states_persisted=FALSE,original_tips_persisted=FALSE)
dir.create(dirname(outpath),recursive=TRUE,showWarnings=FALSE)
write_json(ans,outpath,pretty=TRUE,auto_unbox=TRUE,null="null",digits=15)
cat(toJSON(list(status=ans$status,system_id=sid,
    eta_global=global,eta_local=local,n_tips_S3=axes$S3$n_tips),auto_unbox=TRUE),"\n")
