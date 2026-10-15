#!/usr/bin/env Rscript
# Same-source-only (shared AusTraits dataset ID) source composition robustness.
# Post-discovery original AusTraits within-study reanalysis, NOT new evidence of
# independent evolutionary process or TRY v7 primary-source replication.
suppressPackageStartupMessages({
  library(ape);library(V.PhyloMaker2);library(Rcpp);library(jsonlite)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){
  i<-match(flag,args)
  if(is.na(i)||i==length(args))stop(paste("missing argument",flag))
  args[[i+1]]
}
manifest_path<-getarg("--manifest")
output_path<-getarg("--out")
entries<-fromJSON(manifest_path,simplifyVector=FALSE)
if(length(entries)<1)stop("empty source-selected source-native K input manifest")
dir.create("build/rcpp-common-source-cache",recursive=TRUE,showWarnings=FALSE)
Rcpp::sourceCpp("scripts/analysis/austraits_ou_k_kernel_v0_1.cpp",
    cacheDir="build/rcpp-common-source-cache",
    rebuild=FALSE,showOutput=FALSE,verbose=FALSE)

norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
REPRESENTED<-c("fruit_height","fruit_length","fruit_width",
                "seed_dry_mass","seed_length","seed_width")

test_k<-function(tree,vals,axis) {
  n<-length(tree$tip.label)
  if(n<20L)return(list(status="HOLD_FEWER_THAN_20_NATIVE_TREE_TIPS",n_tips=n))
  tr<-ape::reorder.phylo(tree,"cladewise")
  n<-length(tr$tip.label)
  if(is.null(tr$edge.length)||length(tr$edge.length)!=nrow(tr$edge)||
     any(!is.finite(tr$edge.length))||any(tr$edge.length<0))
    return(list(status="HOLD_INVALID_NATIVE_TREE",n_tips=n))
  root<-setdiff(unique(tr$edge[,1]),tr$edge[,2])
  if(length(root)!=1L)stop("source-native plant tree root ambiguous")
  post<-rev(unique(tr$edge[,1]))
  states<-lapply(vals,function(x){
    v<-unname(x[tr$tip.label])
    if(length(v)!=n||any(!is.finite(v)))
      stop("missing original source-native taxon on shared tree")
    v
  })
  if(any(vapply(states,function(x)length(unique(x))<2L,logical(1))))
    return(list(status="HOLD_ZERO_SOURCE_TRAIT_VARIANCE",n_tips=n))
  trace<-sum(ape::node.depth.edgelength(tr)[seq_len(n)])
  ks<-vapply(states,function(x)
    fast_k_real_tree_cpp(tr$edge,tr$edge.length,n,post,root,trace,x),numeric(1))
  if(any(!is.finite(ks))||any(ks<=0))
    return(list(status="HOLD_NONFINITE_SOURCE_K",n_tips=n))
  if(!exists(".did_validate_common_source_kernel",envir=.GlobalEnv,inherits=FALSE)&&n<=230){
    if(!requireNamespace("phytools",quietly=TRUE))
      stop("source K kernel original implementation cross-check unavailable")
    direct<-vapply(states,function(x){
       names(x)<-tr$tip.label
       as.numeric(phytools::phylosig(tr,x,method="K",test=FALSE))
    },numeric(1))
    if(max(abs(direct-ks))>2e-5)
      stop("common-source linear-time original Blomberg K parity violated")
    assign(".did_validate_common_source_kernel",TRUE,envir=.GlobalEnv)
  }
  full_delta<-log(ks[["full_A"]])-log(ks[["full_B"]])
  source_delta<-log(ks[["source_A"]])-log(ks[["source_B"]])
  list(status="PASS",n_tips=n,
       K_full_A=unname(ks[["full_A"]]),
       K_full_B=unname(ks[["full_B"]]),
       K_source_A=unname(ks[["source_A"]]),
       K_source_B=unname(ks[["source_B"]]),
       delta_full=full_delta,
       delta_source=source_delta,
       delta_source_measurements=source_delta-full_delta,
       original_full_and_common_source_are_on_identical_tips=TRUE)
}
compute_pair<-function(entry){
  fam<-as.character(entry$family)
  trA<-as.character(entry$trait_A)
  trB<-as.character(entry$trait_B)
  base<-list(pair_id=entry$pair_id,
             family=fam,trait_A=trA,trait_B=trB,
             system_A=entry$system_A,system_B=entry$system_B,
             n_source_positive_dataset_common=as.integer(entry$n_source_positive_dataset_common),
             n_same_source_positive_species=as.integer(entry$n_pair_native_positive_source_median),
             n_lost_after_source_median=as.integer(entry$n_lost_after_source_median))
  if((trA%in%REPRESENTED)==(trB%in%REPRESENTED))
    stop("only original cross-organ biological K pairs allowed")
  if(entry$status!="READY"){
    if(entry$status!="HOLD_SOURCE_NATIVE_MEDIANS_BELOW_20_AFTER_SAME_DATASET_RESTRICTION")
      stop("unknown original K-blind source eligibility status")
    return(c(base,list(axes=list(
      S3=list(status="HOLD_SOURCE_NATIVE_MEDIANS_BELOW_20_AFTER_SAME_DATASET_RESTRICTION",n_tips=entry$n_pair_native_positive_source_median),
      prune_only=list(status="HOLD_SOURCE_NATIVE_MEDIANS_BELOW_20_AFTER_SAME_DATASET_RESTRICTION",n_tips=entry$n_pair_native_positive_source_median)))))
  }
  sp<-read.csv(entry$state_table,stringsAsFactors=FALSE,check.names=FALSE)
  expected_n<-as.integer(entry$n_pair_native_positive_source_median)
  if(nrow(sp)!=expected_n||expected_n<20L||
     any(sp$family!=fam)||anyDuplicated(sp$species)||
     any(!is.finite(as.matrix(sp[,c("all_A","all_B","source_A","source_B")]))))
    stop("common-dataset native-source K species support/values changed")
  if(any(as.matrix(sp[,c("all_A","all_B","source_A","source_B")])<=0))
    stop("nonpositive original common-source median K state")
  sp$tip<-norm_species(sp$species)
  if(anyDuplicated(sp$tip))stop("nonunique source-native normalized binomial")
  vals=list(
    full_A=setNames(log(sp$all_A),sp$tip),
    full_B=setNames(log(sp$all_B),sp$tip),
    source_A=setNames(log(sp$source_A),sp$tip),
    source_B=setNames(log(sp$source_B),sp$tip))
  capture.output(
    ph<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
       tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
       output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
    file=tempfile()
  )
  status<-as.character(ph$species.list$status)
  if(length(status)!=nrow(sp))stop("source native phylogeny builder status mismatch")
  s3<-test_k(ph$scenario.3,vals,"S3")
  prnames<-norm_species(as.character(ph$species.list$species[status=="prune"]))
  ptree<-if(length(prnames)>=20L)keep.tip(GBOTB.extended.TPL,prnames) else NULL
  prune<-if(is.null(ptree))
     list(status="HOLD_FEWER_THAN_20_NATIVE_TREE_TIPS",n_tips=length(prnames))
     else test_k(ptree,vals,"prune_only")
  c(base,list(axes=list(S3=s3,prune_only=prune)))
}
out<-list(version="v0.1",status="AUSTRAITS_K_SAME_DATASET_PAIR_BATCH_COMPLETE",
          pairs=lapply(entries,compute_pair),
          post_organ_and_760_K_outcome_source_robustness=TRUE,
          NOT_independent_primary_measurement_validation=TRUE,
          same_AusTraits_dataset_id_not_same_specimen=TRUE,
          n_original_K_blind_source_selected_pairs=length(entries),
          no_species_observation_IDs_or_raw_trait_measurements_persisted=TRUE)
dir.create(dirname(output_path),recursive=TRUE,showWarnings=FALSE)
write_json(out,output_path,auto_unbox=TRUE,pretty=FALSE,null="null",digits=15)
cat(toJSON(list(status=out$status,
   n_original_pairs=length(out$pairs),
   S3_PASS=sum(vapply(out$pairs,function(p)p$axes$S3$status=="PASS",logical(1))),
   prune_PASS=sum(vapply(out$pairs,function(p)p$axes$prune_only$status=="PASS",logical(1)))),
   auto_unbox=TRUE),"\n")
