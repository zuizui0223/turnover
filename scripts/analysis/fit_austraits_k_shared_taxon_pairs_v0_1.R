#!/usr/bin/env Rscript
# Exploratory matched-species two-trait K sensitivity on exactly identical trees.
# Uses phytools-equivalent validated O(n_edges) BM covariance K kernel for
# large datasets; source files and species labels remain runner-local.
suppressPackageStartupMessages({
  library(ape);library(V.PhyloMaker2);library(Rcpp);library(jsonlite)
})
args<-commandArgs(trailingOnly=TRUE)
opt<-function(n) {j<-match(n,args);if(is.na(j)||j==length(args))stop(paste("Missing",n));args[[j+1]]}
manifest_file<-opt("--manifest")
out_file<-opt("--out")
items<-fromJSON(manifest_file,simplifyVector=FALSE)
if(length(items)<1L)stop("empty matched-tip pair manifest")
dir.create("build/rcpp-pair-cache",recursive=TRUE,showWarnings=FALSE)
Rcpp::sourceCpp("scripts/analysis/austraits_ou_k_kernel_v0_1.cpp",
    cacheDir="build/rcpp-pair-cache",rebuild=FALSE,showOutput=FALSE,verbose=FALSE)
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
tree_K_pair<-function(tr,mapA,mapB,refA,refB,axis) {
  if(is.null(tr))
    return(list(status="HOLD_TREE_MISSING",n_tips=0L))
  n<-length(tr$tip.label)
  if(n<20L)
    return(list(status="HOLD_FEWER_THAN_20_MATCHED_TIPS",n_tips=n))
  tr<-ape::reorder.phylo(tr,"cladewise")
  n<-length(tr$tip.label)
  e<-tr$edge
  el<-tr$edge.length
  if(is.null(el)||length(el)!=nrow(e)||any(!is.finite(el))||any(el<0))
    return(list(status="HOLD_INVALID_NATIVE_TREE_GEOMETRY",n_tips=n))
  root<-setdiff(unique(e[,1]),e[,2])
  if(length(root)!=1L)stop("native tree root not unique")
  internalPost<-rev(unique(e[,1]))
  x<-unname(mapA[tr$tip.label])
  y<-unname(mapB[tr$tip.label])
  if(length(x)!=n||length(y)!=n||any(!is.finite(x))||any(!is.finite(y)))
    stop("native pair had missing named taxon state")
  if(length(unique(x))<2L||length(unique(y))<2L)
    return(list(status="HOLD_ZERO_TRAIT_VARIANCE",n_tips=n))
  trace<-sum(ape::node.depth.edgelength(tr)[seq_len(n)])
  a<-fast_k_real_tree_cpp(e,el,n,internalPost,root,trace,x)
  b<-fast_k_real_tree_cpp(e,el,n,internalPost,root,trace,y)
  if(any(!is.finite(c(a,b)))||any(c(a,b)<=0))stop("nonfinite source-native K")
  if(!is.finite(refA)||!is.finite(refB)||refA<=0||refB<=0)
    stop("original independently sourced K identity invalid")
  # One-time parity check with original reference phylosig for a small
  # matched-tip tree; no alternative estimator/tuning is introduced.
  if(!exists(".validated_same_tip_fastK",envir=.GlobalEnv,inherits=FALSE)&&n<=220L){
    if(!requireNamespace("phytools",quietly=TRUE))stop("phytools absent for cross-validation")
    xx<-x;names(xx)<-tr$tip.label
    yy<-y;names(yy)<-tr$tip.label
    k0<-as.numeric(phytools::phylosig(tr,xx,method="K",test=FALSE))
    k1<-as.numeric(phytools::phylosig(tr,yy,method="K",test=FALSE))
    if(max(abs(c(k0-a,k1-b)))>2e-5)
      stop(sprintf("exact K cross-implementation parity violated on %s",axis))
    assign(".validated_same_tip_fastK",TRUE,envir=.GlobalEnv)
  }
  d<-log(a)-log(b)
  orig<-log(refA)-log(refB)
  list(status="PASS",n_tips=n,K_A=a,K_B=b,delta_shared_logK=d,
       delta_original_logK=orig,delta_support_shift=d-orig)
}
run_one<-function(item){
  fam<-as.character(item$family)
  a<-as.character(item$trait_A);b<-as.character(item$trait_B)
  sp<-read.csv(item$state_file,stringsAsFactors=FALSE,check.names=FALSE)
  if(nrow(sp)!=as.integer(item$n_shared_species)||nrow(sp)<20L||
      any(sp$family!=fam)||anyDuplicated(sp$species)||
      any(!is.finite(sp$state_A))||any(!is.finite(sp$state_B))||
      any(sp$state_A<=0)||any(sp$state_B<=0))
      stop("wrong shared-taxon support or nonpositive source state")
  sp$tip<-norm_species(sp$species)
  if(anyDuplicated(sp$tip))stop("ambiguous normalized original taxon identity")
  mapA<-setNames(log(sp$state_A),sp$tip)
  mapB<-setNames(log(sp$state_B),sp$tip)
  capture.output(
    ph<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
        tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
        output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
    file=tempfile()
  )
  statuses<-as.character(ph$species.list$status)
  if(length(statuses)!=nrow(sp))stop("original phylogenetic crosswalk length changed")
  s3<-tree_K_pair(ph$scenario.3,mapA,mapB,
        as.numeric(item$original_S3_K_A),
        as.numeric(item$original_S3_K_B),"S3")
  prone<-norm_species(as.character(ph$species.list$species[statuses=="prune"]))
  prtree<-if(length(prone)>=20L)keep.tip(GBOTB.extended.TPL,prone) else NULL
  prune<-tree_K_pair(prtree,mapA,mapB,
        as.numeric(item$original_prune_K_A),
        as.numeric(item$original_prune_K_B),"prune_only")
  list(pair_id=item$pair_id,family=fam,
       trait_A=a,trait_B=b,system_A=item$system_A,system_B=item$system_B,
       n_shared_species=nrow(sp),
       axes=list(S3=s3,prune_only=prune))
}
results<-lapply(items,run_one)
ans<-list(version="v0.1",status="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED",
     post_original_K_outcome_exploratory=TRUE,
     n_family_trait_pairs=length(results),pairs=results,
     no_species_names_or_raw_values_persisted=TRUE,
     biological_boundary="Same-tip K comparison within AusTraits; no selection/OU parameter inference, no TRY independent replication")
dir.create(dirname(out_file),recursive=TRUE,showWarnings=FALSE)
write_json(ans,out_file,pretty=FALSE,auto_unbox=TRUE,null="null",digits=15)
cat(toJSON(list(status=ans$status,n_pairs=length(results),
              S3_pass=sum(vapply(results,function(x)x$axes$S3$status=="PASS",TRUE)),
              prune_pass=sum(vapply(results,function(x)x$axes$prune_only$status=="PASS",TRUE))),auto_unbox=TRUE),"\n")
