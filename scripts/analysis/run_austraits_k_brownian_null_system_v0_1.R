#!/usr/bin/env Rscript
# Exact-tree equal-rate Brownian process-null for each frozen AusTraits trait system.
# O(n_edges) K evaluation using bottom-up independent-contrasts GLS, explicitly
# verified against phytools::phylosig on the observed, positive-only log states.
suppressPackageStartupMessages({
  library(jsonlite)
  library(ape)
  library(V.PhyloMaker2)
  library(phytools)
})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f) {
  i<-match(f,args)
  if(is.na(i)||i==length(args))stop(paste("missing",f))
  args[[i+1]]
}
sid<-getarg("--system-id")
family<-getarg("--family")
trait<-getarg("--trait")
states_file<-getarg("--state-table")
expected_prune<-as.integer(getarg("--expected-prune"))
expected_bind<-as.integer(getarg("--expected-bind"))
out_file<-getarg("--out")
B<-64L
seed0<-20261008L

sp<-read.csv(states_file,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(sp)<20||any(!is.finite(sp$state_num))||any(sp$state_num<=0))
  stop("invalid state table or positive-only rule")

sp$log_state<-log(sp$state_num)
capture.output(
  ph<-phylo.maker(sp[,c("species","genus","family"),drop=FALSE],
       tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
       output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
  file=tempfile()
)
status<-as.character(ph$species.list$status)
np<-sum(status=="prune",na.rm=TRUE)
nb<-sum(status=="bind",na.rm=TRUE)
nf<-sum(status=="fail to bind",na.rm=TRUE)
if(np!=expected_prune||nb!=expected_bind||
   nf!=nrow(sp)-expected_prune-expected_bind)
  stop("exact phylogeny crosswalk mismatch")

norm_first<-function(x)gsub("(^[[:alpha:]])","\\U\\1",x,perl=TRUE)
norm_species<-function(x)norm_first(gsub(" ","_",x,fixed=TRUE))
sp$tip<-norm_species(as.character(sp$species))
state_map<-setNames(sp$log_state,sp$tip)
prune_names<-norm_species(as.character(ph$species.list$species[status=="prune"]))
trees<-list(S3=ph$scenario.3,prune_only=keep.tip(GBOTB.extended.TPL,prune_names))

# Compute phytools' K without forming C or C^{-1} for every simulated state.
# Precision-weighted ancestor combinations recover the GLS root mean and
# the independent-contrasts quadratic residual Q=(x-a)' C^{-1} (x-a).
k_context<-function(tree) {
  tree<-ape::reorder.phylo(tree,"cladewise")
  n<-length(tree$tip.label)
  e<-tree$edge
  ell<-tree$edge.length
  if(is.null(ell)||any(!is.finite(ell))||any(ell<0))
    stop("missing/negative branch lengths")
  all_nodes<-n+tree$Nnode
  parent_ids<-unique(e[,1])
  root<-setdiff(parent_ids,e[,2])
  if(length(root)!=1)stop("tree lacks unique root")
  depths<-ape::node.depth.edgelength(tree)
  internals<-n+seq_len(tree$Nnode)
  descending<-internals[order(depths[internals],decreasing=TRUE)]
  child_rows<-split(seq_len(nrow(e)),as.character(e[,1]))
  list(tree=tree,n=n,all_nodes=all_nodes,edge=e,ell=ell,
       descending=descending,child_rows=child_rows,root=root,
       trace_covariance=sum(depths[seq_len(n)]))
}
fast_K<-function(context,tip_values) {
  n<-context$n
  if(length(tip_values)!=n)stop("tip K state mismatch")
  val<-numeric(context$all_nodes)
  vv<-numeric(context$all_nodes)
  val[seq_len(n)]<-as.numeric(tip_values)
  Q<-0
  for(node in context$descending) {
    rows<-context$child_rows[[as.character(node)]]
    children<-context$edge[rows,2]
    vch<-vv[children]+context$ell[rows]
    if(any(!is.finite(vch))||any(vch<=0))
      stop("nonpositive child variance in fast K")
    w<-1/vch
    m<-sum(w*val[children])/sum(w)
    Q<-Q+sum(w*(val[children]-m)^2)
    val[node]<-m
    vv[node]<-1/sum(w)
  }
  a<-val[context$root]
  norm<-(context$trace_covariance-n*vv[context$root])/(n-1)
  if(!is.finite(Q)||Q<=0||norm<=0)stop("invalid fast K")
  out<-sum((tip_values-a)^2)/Q/norm
  if(!is.finite(out)||out<=0)stop("invalid fast K statistic")
  as.numeric(out)
}
simulate_tip_state<-function(ctx) {
  s<-numeric(ctx$all_nodes)
  epsilon<-rnorm(length(ctx$ell))*sqrt(ctx$ell)
  # Cladewise ordering is preorder: every parent is assigned before its child.
  for(i in seq_along(epsilon)) {
    from<-ctx$edge[i,1]
    to<-ctx$edge[i,2]
    s[to]<-s[from]+epsilon[i]
  }
  s[seq_len(ctx$n)]
}
results<-list()
idint<-as.integer(gsub("[^0-9]","",sid))
if(is.na(idint))stop("numeric system ID missing")
for(ax in names(trees)) {
  ctx<-k_context(trees[[ax]])
  obs<-unname(state_map[ctx$tree$tip.label])
  if(any(!is.finite(obs)))stop("species state mapping mismatch")
  names(obs)<-ctx$tree$tip.label
  known<-as.numeric(phytools::phylosig(ctx$tree,obs,method="K",test=FALSE))
  fast<-fast_K(ctx,obs)
  relerr<-abs(known-fast)/max(1,abs(known))
  if(relerr>1e-5)
    stop(sprintf("fast K not equal to phytools K (%s): %.12f vs %.12f",ax,known,fast))
  set.seed(seed0+idint*101L+if(ax=="S3")0L else 1000000L)
  simlogK<-numeric(B)
  for(i in seq_len(B))simlogK[i]<-log(fast_K(ctx,simulate_tip_state(ctx)))
  results[[ax]]<-list(
    n_tips=ctx$n,
    observed_K=known,
    observed_logK=log(known),
    rel_error_manual_vs_phytools=relerr,
    null_logK=as.list(simlogK),
    mean_null_logK=mean(simlogK),
    sd_null_logK=sd(simlogK))
}
ans<-list(
  version="v0.1",
  status="AUSTRAITS_REAL_TREE_BROWNIAN_NULL_SYSTEM_ESTIMATED",
  system_id=sid,
  family=family,
  trait_name=trait,
  n_input_species=nrow(sp),
  n_prune=np,
  n_bind=nb,
  n_fail_to_bind=nf,
  null_process="identical independent Brownian evolution sigma2=1",
  null_replicates=B,
  master_seed=seed0,
  S3=results$S3,
  prune_only=results$prune_only,
  raw_species_states_persisted=FALSE,
  species_names_persisted=FALSE)
dir.create(dirname(out_file),recursive=TRUE,showWarnings=FALSE)
write_json(ans,out_file,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(jsonlite::toJSON(list(
 status=ans$status,system_id=sid,n_tips_S3=ans$S3$n_tips,
 relative_K_error=ans$S3$rel_error_manual_vs_phytools,
 n_replicates=B),auto_unbox=TRUE),"\n")
