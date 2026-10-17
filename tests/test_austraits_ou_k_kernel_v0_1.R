#!/usr/bin/env Rscript
suppressPackageStartupMessages({
 library(Rcpp)
 library(ape)
 library(phytools)
})
Rcpp::sourceCpp("scripts/analysis/austraits_ou_k_kernel_v0_1.cpp",
                showOutput=FALSE,verbose=FALSE)
set.seed(20261008)
tr<-ape::reorder.phylo(ape::rtree(12),"cladewise")
n<-length(tr$tip.label)
root<-setdiff(unique(tr$edge[,1]),tr$edge[,2])
stopifnot(length(root)==1L)
post<-rev(unique(tr$edge[,1]))
traceC<-sum(ape::node.depth.edgelength(tr)[seq_len(n)])
x<-rnorm(n);names(x)<-tr$tip.label
known<-as.numeric(phytools::phylosig(tr,x,method="K",test=FALSE))
fast<-fast_k_real_tree_cpp(tr$edge,tr$edge.length,n,post,
        as.integer(root),traceC,unname(x))
stopifnot(is.finite(fast),abs(fast-known)<1e-8)
stopifnot(abs(fast_k_real_tree_cpp(tr$edge,tr$edge.length,n,post,
          as.integer(root),traceC,10*unname(x))-known)<1e-8)
set.seed(20261008)
s1<-simulate_shared_ou_logK_cpp(tr$edge,tr$edge.length,n,post,
                               as.integer(root),traceC,.1,1500L)
set.seed(20261008)
s2<-simulate_shared_ou_logK_cpp(tr$edge,tr$edge.length,n,post,
                               as.integer(root),traceC,4,1500L)
stopifnot(length(s1)==1500,length(s2)==1500,
          all(is.finite(s1)),all(is.finite(s2)))
cat("PASS: fast real-tree K agrees with phytools to 1e-8; scaling invariant; shared-OU simulation finite\n")
cat(sprintf("Synthetic mean K (alpha .1, 4): %.4f, %.4f\n",mean(exp(s1)),mean(exp(s2))))
