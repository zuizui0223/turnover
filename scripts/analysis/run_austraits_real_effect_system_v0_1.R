#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(jsonlite)
  library(ape)
  library(V.PhyloMaker2)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
sid<-getarg("--system-id");family<-getarg("--family");trait_name<-getarg("--trait")
config_type<-getarg("--config-type");state_path<-getarg("--state-table")
expected_prune<-as.integer(getarg("--expected-prune"));expected_bind<-as.integer(getarg("--expected-bind"))
log_enabled<-tolower(getarg("--log-enabled")) %in% c("true","t","1")
out_path<-getarg("--out");dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

sp<-read.csv(state_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20 || !all(c("species","genus","family","state_num","state_cat") %in% names(sp))) stop("invalid state table")
if(any(sp$family!=family)) stop("family mismatch in state table")
if(config_type=="numeric"){
  state_num<-as.numeric(sp$state_num)
  if(any(!is.finite(state_num))) stop("nonfinite numeric species state")
  if(length(unique(state_num))<2) stop("numeric state lacks variation")
  state_cat<-NULL
} else if(config_type=="categorical"){
  state_cat<-as.character(sp$state_cat)
  if(any(is.na(state_cat) | state_cat=="")) stop("missing categorical species state")
  if(length(unique(state_cat))<2) stop("categorical state lacks variation")
  state_num<-NULL
  if(log_enabled) stop("categorical system cannot enable log")
} else stop("unsupported config type")

capture.output(
  phy<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
                  tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                  output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
  file=tempfile()
)
if(is.null(phy$species.list)||is.null(phy$scenario.3)) stop("phylo.maker failed")
st<-as.character(phy$species.list$status)
n_prune<-sum(st=="prune",na.rm=TRUE);n_bind<-sum(st=="bind",na.rm=TRUE);n_fail<-sum(st=="fail to bind",na.rm=TRUE)
if(n_prune!=expected_prune || n_bind!=expected_bind) stop("exact crosswalk count mismatch")
if(n_prune<20 || n_prune+n_bind<20) stop("frozen phylogeny thresholds no longer met")

norm_first<-function(x) gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x) norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
if(anyDuplicated(sp$tip)) stop("duplicate normalized species tip")
if(config_type=="numeric") map_num<-setNames(state_num,sp$tip) else map_cat<-setNames(state_cat,sp$tip)
tree_s3<-phy$scenario.3
prune_names<-norm_species(as.character(phy$species.list$species[st=="prune"]))
if(any(!prune_names %in% GBOTB.extended.TPL$tip.label)) stop("prune tip absent from backbone")
tree_prune<-keep.tip(GBOTB.extended.TPL,prune_names)

effect_one<-function(tree,scale_name){
  tips<-tree$tip.label
  sep<-as.numeric(as.dist(cophenetic.phylo(tree)))
  if(config_type=="numeric"){
    y<-unname(map_num[tips])
    if(any(!is.finite(y))) stop("numeric state mapping failure")
    if(scale_name=="log"){
      if(any(y<=0)) stop("nonpositive log state")
      y<-log(y)
    }
    diss<-as.numeric(dist(y))
  } else {
    y<-unname(map_cat[tips])
    if(any(is.na(y))) stop("categorical state mapping failure")
    n<-length(y); idx<-which(lower.tri(matrix(FALSE,n,n)),arr.ind=TRUE)
    diss<-as.integer(y[idx[,1]]!=y[idx[,2]])
  }
  if(length(sep)!=length(diss) || length(unique(diss))<2) stop("invalid dissimilarity geometry")
  rho<-suppressWarnings(cor(sep,diss,method="spearman",use="complete.obs"))
  if(!is.finite(rho)) stop("nonfinite memory rho")
  as.numeric(rho)
}
s3_raw<-effect_one(tree_s3,"raw");pr_raw<-effect_one(tree_prune,"raw")
s3_log<-NA_real_;pr_log<-NA_real_
if(log_enabled){s3_log<-effect_one(tree_s3,"log");pr_log<-effect_one(tree_prune,"log")}

out<-list(
  version="v0.1",status="AUSTRAITS_REAL_EFFECT_SYSTEM_ESTIMATED",
  system_id=sid,family=family,trait_name=trait_name,config_type=config_type,
  n_species_S3=length(tree_s3$tip.label),n_species_prune=length(tree_prune$tip.label),
  n_prune=n_prune,n_bind=n_bind,n_fail_to_bind=n_fail,
  S3_rho=s3_raw,prune_only_rho=pr_raw,
  S3_raw_rho=s3_raw,prune_raw_rho=pr_raw,
  log_domain_pass=log_enabled,
  S3_log_rho=if(log_enabled)s3_log else NULL,
  prune_log_rho=if(log_enabled)pr_log else NULL,
  null_mean_exact=0,
  raw_trait_measurements_persisted=FALSE,
  species_states_persisted=FALSE,
  species_names_persisted=FALSE
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
