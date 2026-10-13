#!/usr/bin/env Rscript
# Post-outcome source-composition sensitivity: same-tree/tips paired Blomberg K.
# Scientific primary estimands and original K source graph are NOT updated.
suppressPackageStartupMessages({
  library(ape);library(V.PhyloMaker2);library(phytools);library(jsonlite)
})
argv<-commandArgs(trailingOnly=TRUE)
arg<-function(x){i<-match(x,argv);if(is.na(i)||i==length(argv))stop(paste("missing",x));argv[[i+1]]}
sid<-arg("--system-id"); fam<-arg("--family")
f<-arg("--states"); dest<-arg("--out")
original_K_S3<-as.numeric(arg("--original-K-S3"))
original_K_prune<-as.numeric(arg("--original-K-prune"))
sp<-read.csv(f,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20||length(unique(sp$species))!=nrow(sp)||
   any(sp$family!=fam)||any(!is.finite(sp$original_state))||
   any(!is.finite(sp$nonkew_state))||
   any(sp$original_state<=0)||any(sp$nonkew_state<=0))
  stop("source-native matched-tip state input invalid")
if(any(!is.finite(c(original_K_S3,original_K_prune)))||
   any(c(original_K_S3,original_K_prune)<=0))
  stop("archived original K reference values invalid")
sp$log_full<-log(sp$original_state)
sp$log_nonkew<-log(sp$nonkew_state)
capture.output(
  ph<-phylo.maker(sp[,c("species","genus","family")],
    tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
    output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
  file=tempfile()
)
status<-as.character(ph$species.list$status)
if(length(status)!=nrow(sp))stop("phylogenetic status support mismatch")
norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(sp$species)
if(anyDuplicated(sp$tip))stop("duplicate normalized species tips")
m_full<-setNames(sp$log_full,sp$tip)
m_nonkew<-setNames(sp$log_nonkew,sp$tip)
fit_pair<-function(tr,archived_full_K,axis){
  if(is.null(tr)||length(tr$tip.label)<20)
     return(list(status="HOLD_FEWER_THAN_20_MATCHED_TIPS",n_tips=if(is.null(tr))0L else length(tr$tip.label)))
  x<-as.numeric(m_full[tr$tip.label])
  y<-as.numeric(m_nonkew[tr$tip.label])
  if(any(!is.finite(x))||any(!is.finite(y)))
     stop(sprintf("missing matched original taxa on %s tree",axis))
  if(length(unique(x))<2||length(unique(y))<2)
     return(list(status="HOLD_NO_NONZERO_STATE_VARIANCE",n_tips=length(x)))
  names(x)<-tr$tip.label; names(y)<-tr$tip.label
  kk<-tryCatch(c(
     as.numeric(phylosig(tr,x,method="K",test=FALSE)),
     as.numeric(phylosig(tr,y,method="K",test=FALSE))
  ),error=function(e)c(NA_real_,NA_real_))
  if(any(!is.finite(kk))||any(kk<=0))
     return(list(status="HOLD_NONFINITE_PHYLOGENETIC_K",n_tips=length(x)))
  source_delta<-log(kk[2])-log(kk[1])
  geometry_delta<-log(kk[1])-log(archived_full_K)
  list(status="PASS",n_tips=length(x),
       K_full_sources_matched_tips=kk[1],
       K_nonkew_matched_tips=kk[2],
       K_archived_original_tipset=archived_full_K,
       delta_source_logK=source_delta,
       delta_support_geometry_logK=geometry_delta,
       delta_total_logK=source_delta+geometry_delta)
}
s3<-fit_pair(ph$scenario.3,original_K_S3,"S3")
pr_names<-norm_species(as.character(ph$species.list$species[status=="prune"]))
pr_tree<-if(length(pr_names)>=20)keep.tip(GBOTB.extended.TPL,pr_names) else NULL
pr<-fit_pair(pr_tree,original_K_prune,"prune_only")
result<-list(version="v0.1",
   status="AUSTRAITS_SEED_MASS_MATCHED_TIP_K_PAIR_CALCULATED",
   post_original_K_and_source_support=TRUE,
   system_id=sid,family=fam,trait_name="seed_dry_mass",
   n_retained_source_species=nrow(sp),
   n_source_native_original_tree_prune=length(pr_names),
   axes=list(S3=s3,prune_only=pr),
   note="All-versus-nonKew values on exact same reduced tree; old full-K uses separately rounded archived K; descriptive post-discovery check only.")
dir.create(dirname(dest),recursive=TRUE,showWarnings=FALSE)
write_json(result,dest,pretty=TRUE,auto_unbox=TRUE,null="null",digits=15)
cat(toJSON(list(status=result$status,system_id=sid,
    S3_status=s3$status,prune_status=pr$status,
    n_source=nrow(sp)),auto_unbox=TRUE),"\n")
