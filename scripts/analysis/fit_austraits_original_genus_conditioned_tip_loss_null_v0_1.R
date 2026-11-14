#!/usr/bin/env Rscript
# Genus-CONDITIONED source-relative fixed-tree n-matched random tip removal.
# Technically uses the original phylogeny maker and original Rcpp K kernel.
# All species, genus and actual trait values exist only in runner TEMP files.
# This is a POST-HOC conditional null, NOT a prospective confirmatory result.
suppressPackageStartupMessages({
  library(ape);library(V.PhyloMaker2);library(Rcpp);library(jsonlite)
})
args<-commandArgs(trailingOnly=TRUE)
arg<-function(flag) {
  p<-match(flag,args)
  if(is.na(p)||p==length(args))stop(paste("Missing",flag))
  args[[p+1]]
}
input<-arg("--manifest")
output<-arg("--out")
draws<-as.integer(arg("--draws"))
seed<-as.integer(arg("--seed"))
if(draws!=128L||seed!=20261114L)stop("Original frozen null replica settings changed")
items<-fromJSON(input,simplifyVector=FALSE)
if(length(items)<1L)stop("Source-qualified original 142 K null batch absent")
dir.create("build/original-random-pruning-Rcpp-cache",recursive=TRUE,showWarnings=FALSE)
Rcpp::sourceCpp("scripts/analysis/austraits_ou_k_kernel_v0_1.cpp",
  cacheDir="build/original-random-pruning-Rcpp-cache",rebuild=FALSE,
  showOutput=FALSE,verbose=FALSE)
repro<-c("fruit_height","fruit_length","fruit_width",
         "seed_dry_mass","seed_length","seed_width")
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
axes<-c("S3","prune_only")
testk<-function(tr,states,repA) {
  if(is.null(tr))stop("Missing fixed original broad phylogeny")
  tr<-ape::reorder.phylo(tr,"cladewise")
  n<-length(tr$tip.label)
  if(n<20L)stop("Native original K tree undersupported")
  e<-tr$edge;len<-tr$edge.length
  if(is.null(len)||length(len)!=nrow(e)||any(!is.finite(len))||
     any(len<0))stop("Invalid original native tree")
  root<-setdiff(unique(e[,1]),e[,2])
  if(length(root)!=1L)stop("Ambiguous native root")
  internalPost<-rev(unique(e[,1]))
  trace<-sum(ape::node.depth.edgelength(tr)[seq_len(n)])
  val<-lapply(states,function(v) {
    x<-unname(v[tr$tip.label])
    if(length(x)!=n||any(!is.finite(x)))stop("Missing original log trait on sampled tree")
    x
  })
  if(any(vapply(val,function(x)length(unique(x))<2L,logical(1))))
    return(list(status="HOLD_RANDOM_ZERO_TRAIT_VARIANCE",
                n_tips=n,PD=sum(len)))
  k<-vapply(val,function(x)
    fast_k_real_tree_cpp(e,len,n,internalPost,root,trace,x),numeric(1))
  if(any(k<=0)||any(!is.finite(k)))stop("Nonpositive original source K")
  delta<-if(repA)log(k[[1]])-log(k[[2]]) else log(k[[2]])-log(k[[1]])
  list(status="PASS",delta=unname(delta),K_A=unname(k[[1]]),K_B=unname(k[[2]]),
       n_tips=n,PD=sum(len))
}
run_context<-function(entry) {
  sp<-read.csv(as.character(entry$ephemeral_original_state_csv),
    stringsAsFactors=FALSE,check.names=FALSE)
  neednames<-c("family","genus","species","state_A","state_B","strict_survivor")
  if(!all(neednames%in%names(sp)))stop("Ephemeral source states missing columns")
  if(nrow(sp)!=as.integer(entry$original_broad_nonflora_species)||
    any(sp$family!=entry$family)||anyDuplicated(sp$species)||
    any(!is.finite(sp$state_A))||any(!is.finite(sp$state_B))||
    any(sp$state_A<=0)||any(sp$state_B<=0)||
    any(!sp$strict_survivor%in%c(0,1))||
    sum(sp$strict_survivor)!=as.integer(entry$original_strict_source_species))
    stop("Original broad/strict species state support changed")
  sp$tip<-norm_species(sp$species)
  if(anyDuplicated(sp$tip))stop("Ambiguous source name normalization")
  genus_for_tip<-setNames(as.character(sp$genus),sp$tip)
  if(any(!nzchar(genus_for_tip)))stop("Original genus for source native K missing")
  states<-list(A=setNames(log(sp$state_A),sp$tip),
               B=setNames(log(sp$state_B),sp$tip))
  reps<-as.character(entry$trait_A)%in%repro
  if(reps==(as.character(entry$trait_B)%in%repro))
    stop("Not original reproductive-versus-vegetative trait K pair")
  capture.output(
    ph<-phylo.maker(sp[,c("species","genus","family")],
       tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
       output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
    file=tempfile()
  )
  statuses<-as.character(ph$species.list$status)
  if(length(statuses)!=nrow(sp))stop("Original native tree taxon-status count changed")
  native<-norm_species(as.character(ph$species.list$species[statuses=="prune"]))
  prtree<-if(length(native)>=20L)ape::keep.tip(GBOTB.extended.TPL,native) else NULL
  original_trees<-list(S3=ph$scenario.3,prune_only=prtree)
  strict<-sp$tip[sp$strict_survivor==1]
  observed=list()
  for(ax in axes) {
    ref<-entry$original_K_axes[[ax]]
    if(ref$status!="PASS"){
      if(ax!="prune_only")stop("Original S3 hold encountered")
      observed[[ax]]<-list(status="HOLD_ORIGINAL_NATIVE_PRUNE")
      next
    }
    tree<-original_trees[[ax]]
    if(is.null(tree))stop("Original broad native PASS without a tree")
    if(!setequal(tree$tip.label,intersect(sp$tip,tree$tip.label)))
      stop("Original broad native tree contained non-source species")
    base<-testk(tree,states,reps)
    if(base$status!="PASS"||base$n_tips!=as.integer(ref$broad_native_tips)||
       abs(base$delta-as.numeric(ref$broad_delta))>2e-8)
      stop(sprintf("Original source-v7 native K baseline failed %s %s %s: fresh %.12g original %.12g",
            entry$family,entry$trait_A,ax,base$delta,as.numeric(ref$broad_delta)))
    survives<-intersect(tree$tip.label,strict)
    k<-length(survives)
    if(k!=as.integer(ref$strict_original_native_tips)||k<20L)
      stop("Actual original strict native K survivor cohort changed")
    pruned<-if(k==base$n_tips)tree else ape::keep.tip(tree,survives)
    actual<-testk(pruned,states,reps)
    if(actual$status!="PASS")
      stop("Original real strict-source survivor subset has undefined K")
    observed[[ax]]<-list(
       status="PASS",
       tree=tree,states=states,repA=reps,
       native_tips=tree$tip.label,
        genus_by_native_tip=genus_for_tip[tree$tip.label],
        strict_survivor_genus_counts=table(genus_for_tip[survives]),
       n_baseline_tips=base$n_tips,
       n_actual_strict_tips=k,
       baseline_logK_contrast=base$delta,
       actual_strict_survivors_logK_on_fixed_broad_tree=actual$delta,
       actual_strict_survivor_flip_on_fixed_broad_tree=
         as.integer((base$delta>0)!=(actual$delta>0)),
       actual_strict_survivor_signed_shift=actual$delta-base$delta,
       baseline_total_native_PD=base$PD,
       actual_survivor_PD_fraction_of_broad_tree=actual$PD/base$PD,
       historical_stage2_rebuilt_logK_contrast=as.numeric(ref$strict_original_rebuilt_delta),
       historical_rebuilt_tree_minus_actual_fixed_tree=
         as.numeric(ref$strict_original_rebuilt_delta)-actual$delta
    )
  }
  list(input=entry,axes=observed)
}
contexts<-lapply(items,run_context)
# Every family stays entirely inside one workload batch, so a common
# seeded random rank for each original source species can correlate draws
# across original trait pairs from the same family (not pseudoreplicates).
fams<-unique(vapply(items,function(x)as.character(x$family),character(1)))
unique_tips<-list()
for(fam in fams){
  trees<-unlist(lapply(contexts,function(ctx){
    if(as.character(ctx$input$family)!=fam)return(NULL)
    unlist(lapply(ctx$axes,function(a){
      if(a$status!="PASS")return(NULL)
      a$native_tips
    }))
  }))
  unique_tips[[fam]]<-sort(unique(as.character(trees)))
}
null_flip<-lapply(contexts,function(ctx)lapply(ctx$axes,function(x)
  if(x$status=="PASS")integer(draws) else NULL))
null_shift<-lapply(contexts,function(ctx)lapply(ctx$axes,function(x)
  if(x$status=="PASS")numeric(draws) else NULL))
null_pd<-lapply(contexts,function(ctx)lapply(ctx$axes,function(x)
  if(x$status=="PASS")numeric(draws) else NULL))
# A random equal-n pruning may occasionally erase all variation of one
# original trait, so Blomberg K becomes mathematically UNDEFINED. The
# original 142/101 source-qualified comparisons have valid K by definition.
# Reject the WHOLE candidate priority for that family/replicate and sample
# again, preserving correlations across the family's trait pairs and trees.
# Record all rejections so the conditional-valid-K null is transparent.
max_attempts<-256L
family_candidate_rejections<-setNames(integer(length(fams)),fams)
family_candidate_attempts<-setNames(integer(length(fams)),fams)
for(r in seq_len(draws)){
  for(fam in fams){
    chars<-utf8ToInt(fam)
    accepted<-FALSE
    for(attempt in seq_len(max_attempts)){
      family_candidate_attempts[[fam]]<-family_candidate_attempts[[fam]]+1L
      family_seed<-seed+r*10000L+sum(chars*seq_along(chars))*7L+
                   attempt*99991L
      set.seed(family_seed)
      u<-unique_tips[[fam]]
      random_rank<-setNames(runif(length(u)),u)
      trial<-vector("list",length(contexts))
      invalid<-FALSE
      for(i in seq_along(contexts)){
        ctx<-contexts[[i]]
        if(as.character(ctx$input$family)!=fam)next
        trial[[i]]<-list()
        for(ax in axes){
          a<-ctx$axes[[ax]]
          if(a$status!="PASS")next
          native<-a$native_tips
          if(a$n_actual_strict_tips==a$n_baseline_tips){
            k<-a$baseline_logK_contrast
            pd<-1
          }else{
            # Preserve the ACTUAL strict-source number of native tips in
            # EACH original genus of the same family-by-trait-pair.
            # Only within-genus species identities are randomized.
            target<-a$strict_survivor_genus_counts
            kept<-lapply(names(target),function(gn) {
              available<-native[a$genus_by_native_tip[native]==gn]
              quota<-as.integer(target[[gn]])
              if(length(available)<quota||quota<1L)
                stop("Genus-conditioned source survivor tip quota invalid")
              if(length(available)==quota)return(available)
              order_genus<-available[order(random_rank[available],available)]
              order_genus[seq_len(quota)]
            })
            keep<-unlist(kept,use.names=FALSE)
            if(length(keep)!=a$n_actual_strict_tips||anyDuplicated(keep))
              stop("Actual strict original per-genus tip counts not preserved")
            sub<-ape::keep.tip(a$tree,keep)
            z<-testk(sub,a$states,a$repA)
            if(z$status=="HOLD_RANDOM_ZERO_TRAIT_VARIANCE"){
              invalid<-TRUE
              break
            }
            if(z$status!="PASS")stop("Unexpected invalid original K null draw status")
            k<-z$delta
            pd<-z$PD/a$baseline_total_native_PD
          }
          trial[[i]][[ax]]<-list(
            flip=as.integer((k>0)!=(a$baseline_logK_contrast>0)),
            shift=k-a$baseline_logK_contrast,pd=pd)
        }
        if(invalid)break
      }
      if(invalid){
        family_candidate_rejections[[fam]]<-family_candidate_rejections[[fam]]+1L
        next
      }
      for(i in seq_along(contexts)){
        if(as.character(contexts[[i]]$input$family)!=fam)next
        for(ax in axes){
          a<-contexts[[i]]$axes[[ax]]
          if(a$status!="PASS")next
          z<-trial[[i]][[ax]]
          if(is.null(z)||any(!is.finite(unlist(z))))
            stop("Accepted K-valid family-priority draw incomplete")
          null_flip[[i]][[ax]][[r]]<-z$flip
          null_shift[[i]][[ax]][[r]]<-z$shift
          null_pd[[i]][[ax]][[r]]<-z$pd
        }
      }
      accepted<-TRUE
      break
    }
    if(!accepted)stop(sprintf(
      "No K-valid equal-n null sample after %d family-level draws for family %s replicate %d",
      max_attempts,fam,r))
  }
}
summ<-function(x)if(length(x))list(
  mean=mean(x),median=median(x),
  q025=unname(quantile(x,0.025,type=1)),
  q975=unname(quantile(x,0.975,type=1))) else NULL
out_pairs<-vector("list",length(contexts))
for(i in seq_along(contexts)){
  ctx<-contexts[[i]]
  ref<-ctx$input
  outer=list(null_pair_id=ref$null_pair_id,family=ref$family,
       trait_A=ref$trait_A,trait_B=ref$trait_B,
       original_broad_source_species=as.integer(ref$original_broad_nonflora_species),
       original_strict_surviving_source_species=as.integer(ref$original_strict_source_species),
       axes=list())
  for(ax in axes){
    a<-ctx$axes[[ax]]
    if(a$status!="PASS"){
      outer$axes[[ax]]<-list(status="HOLD_ORIGINAL_NATIVE_PRUNE")
      next
    }
    nflip<-null_flip[[i]][[ax]]
    shifts<-null_shift[[i]][[ax]]
    pd<-null_pd[[i]][[ax]]
    actual<-abs(a$actual_strict_survivor_signed_shift)
    if(any(!is.finite(shifts))||any(!is.finite(pd))||
       any(nflip%in%c(0L,1L)==FALSE))stop("Invalid original null draw")
    outer$axes[[ax]]<-list(
       status="PASS",
       n_baseline_tips=a$n_baseline_tips,
       n_actual_strict_tips=a$n_actual_strict_tips,
       baseline_logK_contrast=a$baseline_logK_contrast,
       actual_strict_survivors_logK_on_fixed_broad_tree=
            a$actual_strict_survivors_logK_on_fixed_broad_tree,
       actual_strict_survivor_flip_on_fixed_broad_tree=
            a$actual_strict_survivor_flip_on_fixed_broad_tree,
       actual_strict_survivor_signed_shift=a$actual_strict_survivor_signed_shift,
       historical_stage2_rebuilt_logK_contrast=
            a$historical_stage2_rebuilt_logK_contrast,
       historical_rebuilt_tree_minus_actual_fixed_tree=
            a$historical_rebuilt_tree_minus_actual_fixed_tree,
       actual_survivor_PD_fraction_of_broad_tree=
            a$actual_survivor_PD_fraction_of_broad_tree,
       random_tree_PD_fraction_of_broad_tree=summ(pd),
       empirical_null_tail_prob_abs_delta_shift=
            (1+sum(abs(shifts)>=actual))/(draws+1),
       null_K_sign_flip_probability=mean(nflip),
       random_signed_delta_change=summ(shifts),
       random_absolute_delta_change=summ(abs(shifts)),
       null_flip_bits=paste0(nflip,collapse=""))
  }
  out_pairs[[i]]<-outer
}
out<-list(version="v0.1",status="PASS_ORIGINAL_142_TIP_LOSS_FROZEN_BROAD_TREE_NULL_BATCH",
   original_K_source_release="AusTraits v7.0.0",
   source_native_units_and_original_tree_pinned=TRUE,
   source_eligible_original_pair_ids_fixed_K_blind=TRUE,
   no_original_species_names_or_measurement_values_persisted=TRUE,
   original_organs_and_null_design_post_discovery=TRUE,
   null_replicates=draws,null_seed=seed,
   same_family_random_rank_shared_across_original_trait_pairs=TRUE,
   family_batches_are_disjoint=TRUE,
   null_inference_conditioned_on_phylogenetic_K_estimable_in_every_family_pair=TRUE,
   n_total_candidate_family_priorities_evaluated=sum(family_candidate_attempts),
   n_rejected_family_priorities_due_to_undefined_K=sum(family_candidate_rejections),
   rejected_K_undefined_draws_by_family=as.list(family_candidate_rejections),
   n_candidates_evaluated_by_family=as.list(family_candidate_attempts),
   no_per_pair_independent_resampling_after_K_variance_hold=TRUE,
   null_preserves_original_strict_survivor_count_within_each_genus=TRUE,
   original_family_tips_and_broad_tree_fixed_and_only_within_genus_identity_random=TRUE,
   genus_strata_extracted_from_same_original_public_v7_source_without_new_measurements=TRUE,
   fixed_broad_tree_all_trait_values_and_taxon_numbers_source_checked=TRUE,
   no_evolutionary_rate_or_K_selection_hypothesis_confirmed=TRUE,
   pairs=out_pairs)
dir.create(dirname(output),recursive=TRUE,showWarnings=FALSE)
jsonlite::write_json(out,output,auto_unbox=TRUE,pretty=TRUE,null="null",digits=15)
cat(toJSON(list(status=out$status,n_original_pairs=length(out_pairs),
 S3_PASS=sum(vapply(out_pairs,function(x)x$axes$S3$status=="PASS",logical(1))),
 prune_PASS=sum(vapply(out_pairs,function(x)x$axes$prune_only$status=="PASS",logical(1))),
 S3_observed_survivor_flips=sum(vapply(out_pairs,function(x)
    x$axes$S3$actual_strict_survivor_flip_on_fixed_broad_tree,numeric(1)))),
 auto_unbox=TRUE),"\n")
