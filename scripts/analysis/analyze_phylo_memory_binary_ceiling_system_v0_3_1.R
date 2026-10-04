#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
  library(ape)
  library(V.PhyloMaker2)
})

args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){
  i <- match(flag,args)
  if(is.na(i) || i==length(args)) stop(paste("missing",flag))
  args[[i+1]]
}
family <- getarg("--family")
trait_name <- getarg("--trait")
system_id <- getarg("--id")
crosswalk_path <- getarg("--crosswalk")
systems_table_path <- getarg("--systems-table")
out_path <- getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

sys <- read.csv(systems_table_path,stringsAsFactors=FALSE,check.names=FALSE)
src <- sys[sys$system_id==system_id & sys$family==family & sys$trait_name==trait_name,,drop=FALSE]
if(nrow(src)!=1) stop("system is not unique in frozen v0.2 systems table")
if(as.character(src$semantic_class[[1]])!="nominal_categorical") stop("v0.3.1 is categorical only")

cw <- read.csv(crosswalk_path,stringsAsFactors=FALSE,check.names=FALSE)
flag <- tolower(trimws(as.character(cw$crosswalk_pass))) %in% c("true","t","1")
row <- cw[flag & cw$family==family & cw$trait_name==trait_name,,drop=FALSE]
if(nrow(row)!=1) stop("system is not a unique crosswalk-PASS candidate")
if(as.character(row$semantic_class[[1]])!="nominal_categorical") stop("crosswalk class mismatch")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed before edge-split ceiling audit")

esc <- function(x) gsub("'","''",x,fixed=TRUE)
famq <- esc(family); trq <- esc(trait_name)
sql <- sprintf("
  WITH counts AS (
    SELECT scrubbed_species_binomial AS species,
           scrubbed_genus AS genus,
           scrubbed_family AS family,
           trait_value::text AS value_text,
           count(*) AS n
    FROM agg_traits
    WHERE scrubbed_family='%s' AND trait_name='%s'
      AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
      AND scrubbed_genus IS NOT NULL AND trim(scrubbed_genus)<>''
      AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
      AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
    GROUP BY scrubbed_species_binomial,scrubbed_genus,scrubbed_family,trait_value::text
  ), ranked AS (
    SELECT *,max(n) OVER(PARTITION BY species) AS max_n FROM counts
  ), modes AS (
    SELECT species,genus,family,count(*) FILTER(WHERE n=max_n) AS n_modal
    FROM ranked GROUP BY species,genus,family
  )
  SELECT species,genus,family FROM modes WHERE n_modal=1 ORDER BY species;
",famq,trq)
sp <- .BIEN_sql(sql)
if(!is.data.frame(sp) || nrow(sp)<20) stop("categorical species query failed or fell below 20")
sp <- unique(sp[,c("species","genus","family"),drop=FALSE])

capture.output(
  phy <- phylo.maker(sp,tree=GBOTB.extended.TPL,nodes=nodes.info.1.TPL,
                     output.sp.list=TRUE,output.tree=FALSE,scenarios="S3"),
  file=tempfile()
)
if(is.null(phy$species.list) || is.null(phy$scenario.3)) stop("phylo.maker did not return S3 tree/species list")
st <- as.character(phy$species.list$status)
n_prune <- sum(st=="prune",na.rm=TRUE)
n_bind <- sum(st=="bind",na.rm=TRUE)
n_fail <- sum(st=="fail to bind",na.rm=TRUE)
if(nrow(sp)!=as.integer(src$n_input_species[[1]]) ||
   n_prune!=as.integer(src$n_prune[[1]])) stop("rebuilt geometry disagrees with frozen v0.2 systems table")
if(n_prune!=as.integer(row$n_prune[[1]]) ||
   n_bind!=as.integer(row$n_bind[[1]]) ||
   n_fail!=as.integer(row$n_fail_to_bind[[1]])) stop("rebuilt geometry disagrees with frozen crosswalk")

tr <- reorder.phylo(phy$scenario.3,"cladewise")
if(is.null(tr$edge.length) || any(!is.finite(tr$edge.length)) || any(tr$edge.length<0)) stop("invalid S3 edge lengths")
D <- cophenetic.phylo(tr)
dvec <- as.numeric(as.dist(D))
rx <- rank(dvec,ties.method="average")
M <- length(rx)
meanrx <- mean(rx)
sxx <- sum((rx-meanrx)^2)
if(!is.finite(sxx) || sxx<=0) stop("zero pair-distance rank variance")
n <- length(tr$tip.label)

# Compute the rank-weight cut sum for every tree edge in O(n^2), not O(n^3).
# For each unordered tip pair (i,j) with rank weight w, add +w to both tips
# and -2w to their LCA. A postorder subtree sum then equals the total pair
# weight crossing the parent-child edge. This is exactly the cross_sum used
# by the binary point-biserial/Spearman formula.
nall <- n + tr$Nnode
root <- setdiff(tr$edge[,1],tr$edge[,2])
if(length(root)!=1) stop("tree root not unique")
L <- mrca(tr,full=FALSE)
if(!is.matrix(L) || nrow(L)!=n || ncol(L)!=n) stop("tip MRCA matrix dimension mismatch")

delta <- numeric(nall)
lca_loss <- numeric(nall)
offset <- 0L
if(length(rx) != n*(n-1)/2) stop("pair-rank length mismatch")
for(j in seq_len(n-1L)){
  m <- n-j
  idx <- seq.int(offset+1L,offset+m)
  ii <- seq.int(j+1L,n)
  w <- rx[idx]
  delta[j] <- delta[j] + sum(w)
  delta[ii] <- delta[ii] + w
  lc <- as.integer(L[ii,j])
  if(any(!is.finite(lc)) || any(lc<1L) || any(lc>nall)) stop("invalid LCA node index")
  acc <- rowsum(matrix(w,ncol=1),group=lc,reorder=FALSE)
  ai <- as.integer(rownames(acc))
  lca_loss[ai] <- lca_loss[ai] + acc[,1]
  offset <- offset+m
}
if(offset!=length(rx)) stop("pair-rank traversal incomplete")
delta <- delta - 2*lca_loss
rm(L,lca_loss); gc(FALSE)

post <- reorder.phylo(tr,"postorder")
E <- nrow(post$edge)
subtree_weight <- delta
tip_count <- c(rep(1,n),rep(0,tr$Nnode))
cross_sum <- numeric(E)
edge_size <- integer(E)
for(e in seq_len(E)){
  parent <- post$edge[e,1]
  child <- post$edge[e,2]
  cross_sum[e] <- subtree_weight[child]
  edge_size[e] <- tip_count[child]
  subtree_weight[parent] <- subtree_weight[parent] + subtree_weight[child]
  tip_count[parent] <- tip_count[parent] + tip_count[child]
}
scale_check <- max(1,sum(abs(delta)))
if(abs(subtree_weight[root]) > 1e-9*scale_check) stop("postorder cut-sum accumulation failed")
if(tip_count[root] != n) stop("postorder tip-count accumulation failed")
if(any(edge_size<=0L) || any(edge_size>=n)) stop("invalid edge split size")

K <- edge_size*(n-edge_size)
den <- sqrt(sxx * K * (M-K) / M)
rho <- (cross_sum - K*meanrx)/den
if(!any(is.finite(rho))) stop("no finite edge-split rho")
imax <- which.max(ifelse(is.finite(rho),rho,-Inf))
best <- data.frame(
  edge_index=imax,
  child=post$edge[imax,2],
  clade_size=edge_size[imax],
  minority_fraction=min(edge_size[imax],n-edge_size[imax])/n,
  K=K[imax],
  rho=rho[imax]
)

sr <- sort(rx,decreasing=TRUE)
cs <- cumsum(sr)
Ks <- seq_len(M-1)
nums <- cs[Ks] - Ks*meanrx
dens <- sqrt(sxx * Ks * (M-Ks) / M)
ur <- nums/dens
unconstrained_max <- max(ur[is.finite(ur)])

benchmark <- 0.15
parse_bool <- function(x) tolower(trimws(as.character(x))) %in% c("true","t","1")
no_bracket <- parse_bool(src$s3_no_bracket[[1]])
ou_max <- suppressWarnings(as.numeric(src$s3_max_grid_median[[1]]))
if(no_bracket && !is.finite(ou_max)) stop("frozen v0.2 OU maximum is not finite for no-bracket system")
edge_gap <- if(is.finite(ou_max)) as.numeric(best$rho-ou_max) else NA_real_

out <- list(
  version="v0.3.1",
  status="PHYLO_MEMORY_EDGE_SPLIT_CEILING_ESTIMATED",
  system_id=system_id,family=family,trait_name=trait_name,semantic_class="nominal_categorical",
  outcome_type="known_truth_geometry_only",
  real_trait_values_used=FALSE,real_memory_effects_used=FALSE,
  n_input_species=n,n_prune=n_prune,n_bind=n_bind,n_fail_to_bind=n_fail,
  n_pairs=M,n_edges=nrow(tr$edge),
  benchmark=benchmark,
  original_s3_no_bracket=no_bracket,
  original_ou_max_grid_median=ou_max,
  max_edge_split_rho=as.numeric(best$rho),
  max_edge_split_edge_index=as.integer(best$edge_index),
  max_edge_split_clade_size=as.integer(best$clade_size),
  max_edge_split_minority_fraction=as.numeric(best$minority_fraction),
  max_edge_split_mismatch_pairs=as.numeric(best$K),
  edge_split_reaches_benchmark=as.logical(best$rho>=benchmark),
  edge_minus_ou_gap=edge_gap,
  unconstrained_pair_label_upper_bound=as.numeric(unconstrained_max),
  interpretation_guard="Edge splits are realizable one-transition binary states, not a global upper bound over arbitrary multi-transition binary patterns."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
