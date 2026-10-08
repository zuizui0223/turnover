#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(ape);library(V.PhyloMaker2);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
bien_path<-getarg("--bien");aus_path<-getarg("--austraits");out<-getarg("--out")
b<-read.csv(bien_path,stringsAsFactors=FALSE,check.names=FALSE)
a<-read.csv(aus_path,stringsAsFactors=FALSE,check.names=FALSE)
a<-a[a$log_domain_pass %in% c(TRUE,"TRUE","True","true",1,"1"),,drop=FALSE]
if(nrow(b)!=201||nrow(a)!=254)stop("unexpected source dimensions")

family_blup<-function(x,col){
 d<-data.frame(rho=as.numeric(x[[col]]),family=factor(x$family),trait_name=factor(x$trait_name))
 fit<-lmer(rho~0+trait_name+(1|family),data=d,REML=TRUE,
           control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
 rf<-ranef(fit)$family
 data.frame(family=rownames(rf),context=as.numeric(rf[,1]),stringsAsFactors=FALSE)
}
family_geom<-function(families){
 tips<-tips.info.TPL
 depth<-node.depth.edgelength(GBOTB.extended.TPL)
 tipdepth<-depth[seq_along(GBOTB.extended.TPL$tip.label)]
 tree_height<-max(tipdepth)
 rows<-list()
 for(i in seq_along(families)){
  fam<-families[[i]]
  ft<-unique(as.character(tips$species[tips$family==fam]))
  ft<-intersect(ft,GBOTB.extended.TPL$tip.label)
  if(length(ft)>=2){node<-getMRCA(GBOTB.extended.TPL,ft);age<-tree_height-depth[node]}
  else if(length(ft)==1){node<-match(ft,GBOTB.extended.TPL$tip.label);age<-0}
  else {node<-NA_integer_;age<-NA_real_}
  rows[[i]]<-data.frame(family=fam,n_backbone_tips=length(ft),crown_age=age,stringsAsFactors=FALSE)
 }
 do.call(rbind,rows)
}
analyse<-function(x,col){
 s<-family_blup(x,col);g<-family_geom(sort(unique(x$family)));m<-merge(s,g,by="family")
 valid_age<-is.finite(m$crown_age)
 valid_rich<-m$n_backbone_tips>0
 ag<-suppressWarnings(cor.test(m$context[valid_age],m$crown_age[valid_age],method="spearman",exact=FALSE))
 rr<-suppressWarnings(cor.test(m$context[valid_rich],log10(m$n_backbone_tips[valid_rich]),method="spearman",exact=FALSE))
 list(n_families=nrow(m),n_age=sum(valid_age),n_richness=sum(valid_rich),
      crown_age=list(rho=unname(ag$estimate),p=ag$p.value),
      richness=list(rho=unname(rr$estimate),p=rr$p.value))
}
res<-list(
 version="v0.1",status="FAMILY_CONTEXT_AGE_RICHNESS_EXPLORATORY_ESTIMATED",post_outcome_exploratory=TRUE,
 BIEN=list(S3=analyse(b,"S3_log_rho"),prune=analyse(b,"prune_log_rho")),
 AusTraits=list(S3=analyse(a,"S3_log_rho"),prune=analyse(a,"prune_log_rho"))
)
write_json(res,out,pretty=TRUE,auto_unbox=TRUE,null="null");cat(toJSON(res,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
