#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(f){i<-match(f,args);if(is.na(i)||i==length(args))stop(paste("missing",f));args[[i+1]]}
effects_path<-getarg("--effects");geometry_path<-getarg("--geometry");out_path<-getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)
e<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
g<-read.csv(geometry_path,stringsAsFactors=FALSE,check.names=FALSE)
x<-merge(e,g,by=c("system_id","family","trait_name"),all=FALSE)
if(nrow(x)!=259||length(unique(x$family))!=42||length(unique(x$trait_name))!=14)stop("merge changed final core")

safe_z<-function(v){
 v<-as.numeric(v)
 if(any(!is.finite(v)))stop("nonfinite geometry metric")
 s<-sd(v)
 if(!is.finite(s)||s<=0)return(rep(0,length(v)))
 (v-mean(v))/s
}
prep_axis<-function(prefix){
 data.frame(
   z_log_n=safe_z(log(x[[paste0(prefix,"_n_tips")]])),
   z_polytomy=safe_z(x[[paste0(prefix,"_polytomy_burden")]]),
   z_pair_cv=safe_z(x[[paste0(prefix,"_pairwise_distance_cv")]]),
   z_max_tie=safe_z(x[[paste0(prefix,"_max_distance_tie_share")]]),
   z_pendant_cv=safe_z(x[[paste0(prefix,"_pendant_branch_cv")]])
 )
}
summ<-function(fit){
 vc<-as.data.frame(VarCorr(fit))
 vf<-vc$vcov[vc$grp=="family"][1];ve<-sigma(fit)^2
 list(family_variance=vf,residual_variance=ve,
      conditional_family_repeatability=vf/(vf+ve),
      singular=isSingular(fit,tol=1e-4),
      fixed_effects=as.list(round(fixef(fit),6)))
}
fit_axis<-function(response,prefix){
 dat<-data.frame(rho=as.numeric(x[[response]]),family=factor(x$family),trait_name=factor(x$trait_name),prep_axis(prefix))
 unadj<-lmer(rho~0+trait_name+(1|family),data=dat,REML=TRUE,
             control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
 adj<-lmer(rho~0+trait_name+z_log_n+z_polytomy+z_pair_cv+z_max_tie+z_pendant_cv+(1|family),
           data=dat,REML=TRUE,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
 vars<-c("z_log_n","z_polytomy","z_pair_cv","z_max_tie","z_pendant_cv")
 one<-list()
 for(v in vars){
   form<-as.formula(paste0("rho~0+trait_name+",v,"+(1|family)"))
   f<-lmer(form,data=dat,REML=TRUE,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
   one[[v]]<-summ(f)
 }
 u<-summ(unadj);a<-summ(adj)
 list(unadjusted=u,adjusted=a,one_at_a_time=one,
      family_variance_ratio_adjusted_to_unadjusted=a$family_variance/u$family_variance,
      repeatability_difference=a$conditional_family_repeatability-u$conditional_family_repeatability)
}
out<-list(
 version="v0.1",status="AUSTRAITS_TREE_GEOMETRY_FAMILY_CONTEXT_SENSITIVITY_ESTIMATED",
 post_outcome_exploratory=TRUE,
 design="data/austraits_family_context_tree_geometry_v0_1.json",
 n_systems=nrow(x),n_families=length(unique(x$family)),n_traits=length(unique(x$trait_name)),
 S3=fit_axis("S3_rho","S3"),
 prune_only=fit_axis("prune_only_rho","prune"),
 interpretation="If adjusted family repeatability remains close to unadjusted on both axes, measured tree topology and patristic-distance geometry are not a simple explanation of family context."
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
