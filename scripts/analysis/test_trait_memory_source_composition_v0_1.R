#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(RPostgreSQL);library(DBI);library(jsonlite);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
getarg<-function(flag){i<-match(flag,args);if(is.na(i)||i==length(args))stop(paste("missing",flag));args[[i+1]]}
effects_path<-getarg("--effects"); core_path<-getarg("--core"); out_path<-getarg("--out"); table_path<-getarg("--table-out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE);dir.create(dirname(table_path),recursive=TRUE,showWarnings=FALSE)
root<-normalizePath(".")
d<-fromJSON(file.path(root,"data","trait_memory_source_composition_sensitivity_v0_1.json"),simplifyVector=FALSE)
effects<-read.csv(effects_path,stringsAsFactors=FALSE,check.names=FALSE)
core<-read.csv(core_path,stringsAsFactors=FALSE,check.names=FALSE)
if(nrow(effects)!=201||nrow(core)!=201)stop("expected frozen 201-system core")
keys<-paste(core$family,core$trait_name,sep="\x1f")
if(!setequal(keys,paste(effects$family,effects$trait_name,sep="\x1f")))stop("effect/core keys differ")

rbien_dir<-Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"));source(file.path(rbien_dir,"R","BIEN_sql.R"));source(file.path(rbien_dir,"R","BIEN.R"))
ver<-BIEN_metadata_database_version();obs<-if(is.data.frame(ver)&&nrow(ver))as.character(ver$db_version[[1]])else NA_character_
if(!identical(obs,"4.2.8"))stop("BIEN patch changed")
esc<-function(x)gsub("'","''",x,fixed=TRUE)
vals<-paste0("('",esc(core$family),"','",esc(core$trait_name),"')")
vsql<-paste(vals,collapse=",\n")
sql<-sprintf("
WITH systems(family,trait_name) AS (VALUES %s),
base AS (
 SELECT a.scrubbed_family AS family,a.trait_name,
        coalesce(nullif(trim(a.source::text),''),'__MISSING__') AS source_key,
        coalesce(nullif(trim(a.source_citation::text),''),'__MISSING__') AS citation_key
 FROM agg_traits a JOIN systems s
 ON a.scrubbed_family=s.family AND a.trait_name=s.trait_name
 WHERE a.scrubbed_species_binomial IS NOT NULL AND trim(a.scrubbed_species_binomial)<>''
   AND a.trait_value IS NOT NULL AND trim(a.trait_value::text)<>''
   AND (a.is_cultivated_observation=0 OR a.is_cultivated_observation IS NULL)
), sc AS (
 SELECT family,trait_name,source_key,count(*)::double precision AS n
 FROM base GROUP BY family,trait_name,source_key
), ss AS (
 SELECT family,trait_name,sum(n) AS n_records,count(*) AS n_sources,
        sum(n*n)/(sum(n)*sum(n)) AS source_hhi,max(n)/sum(n) AS dominant_source_share
 FROM sc GROUP BY family,trait_name
), cc AS (
 SELECT family,trait_name,citation_key,count(*)::double precision AS n
 FROM base GROUP BY family,trait_name,citation_key
), cs AS (
 SELECT family,trait_name,count(*) AS n_citations,
        sum(n*n)/(sum(n)*sum(n)) AS citation_hhi,max(n)/sum(n) AS dominant_citation_share
 FROM cc GROUP BY family,trait_name
)
SELECT ss.*,cs.n_citations,cs.citation_hhi,cs.dominant_citation_share
FROM ss JOIN cs USING(family,trait_name)
ORDER BY family,trait_name;
",vsql)
p<-.BIEN_sql(sql)
if(!is.data.frame(p)||nrow(p)!=201)stop("provenance aggregation failed")
x<-merge(effects,p,by=c("family","trait_name"),all=FALSE)
if(nrow(x)!=201)stop("merge lost systems")
write.csv(x,table_path,row.names=FALSE,na="")

# Trait-centered, leave-family-out context score.
ctx<-data.frame(family=sort(unique(x$family)),context=NA_real_)
for(i in seq_len(nrow(ctx))){
 f<-ctx$family[[i]]
 z<-x[x$family==f,,drop=FALSE]
 dev<-numeric(nrow(z))
 for(j in seq_len(nrow(z))){
   tr<-z$trait_name[[j]]
   train<-x$S3_rho[x$trait_name==tr & x$family!=f]
   dev[[j]]<-z$S3_rho[[j]]-mean(train)
 }
 ctx$context[[i]]<-median(dev)
}
famprov<-aggregate(cbind(source_hhi,dominant_source_share,n_sources,citation_hhi,dominant_citation_share,n_citations)~family,data=x,FUN=median)
ctx<-merge(ctx,famprov,by="family")

fnv<-function(s){
 h<-2166136261
 for(b in as.integer(charToRaw(enc2utf8(s)))){
  lo<-h%%256; h<-h-lo+bitwXor(as.integer(lo),as.integer(b))
  l16<-h%%65536; hi<-floor(h/65536); p<-l16*403
  h<-(p%%65536)+((floor(p/65536)+l16*256+hi*403)%%65536)*65536
 }
 as.integer((h%%2147483646)+1)
}
perm_test<-function(a,b,key,B=9999){
 obs<-suppressWarnings(cor(a,b,method="spearman"))
 set.seed(fnv(key)); vals<-numeric(B)
 for(k in seq_len(B))vals[k]<-suppressWarnings(cor(a,sample(b),method="spearman"))
 p<-(1+sum(abs(vals)>=abs(obs)))/(B+1)
 list(rho=as.numeric(obs),p_two_sided=p,permutations=B)
}
A_source_hhi<-perm_test(ctx$context,ctx$source_hhi,"source_hhi")
A_dom<-perm_test(ctx$context,ctx$dominant_source_share,"dominant_source_share")
A_cit_hhi<-perm_test(ctx$context,ctx$citation_hhi,"citation_hhi")
A_cit_dom<-perm_test(ctx$context,ctx$dominant_citation_share,"dominant_citation_share")

std<-function(v){s<-sd(v);if(!is.finite(s)||s==0)rep(0,length(v))else(as.numeric(v)-mean(as.numeric(v)))/s}
x$z_log_n_trait_records<-std(log(x$n_records))
x$z_source_HHI<-std(x$source_hhi)
x$z_dominant_source_share<-std(x$dominant_source_share)
x$z_citation_HHI<-std(x$citation_hhi)
x$z_dominant_citation_share<-std(x$dominant_citation_share)
varsum<-function(fit){
 vc<-as.data.frame(VarCorr(fit));vf<-vc$vcov[vc$grp=="family"][1];vt<-vc$vcov[vc$grp=="trait_name"][1];vr<-sigma(fit)^2;tot<-vf+vt+vr
 list(family_variance=vf,trait_variance=vt,residual_variance=vr,R_family=vf/tot,R_trait=vt/tot,R_residual=vr/tot,singular=isSingular(fit,tol=1e-4))
}
fit_source<-lmer(S3_rho~z_log_n_trait_records+z_source_HHI+z_dominant_source_share+(1|family)+(1|trait_name),data=x,REML=TRUE,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
fit_cit<-lmer(S3_rho~z_log_n_trait_records+z_citation_HHI+z_dominant_citation_share+(1|family)+(1|trait_name),data=x,REML=TRUE,control=lmerControl(optimizer="bobyqa",optCtrl=list(maxfun=200000)))
vs<-varsum(fit_source);vc<-varsum(fit_cit)
out<-list(version="v0.1",status="TRAIT_MEMORY_SOURCE_COMPOSITION_SENSITIVITY_ESTIMATED",post_outcome_sensitivity=TRUE,
 n_systems=201,n_families=45,n_traits=12,observed_database_version=obs,
 family_context_associations=list(source_HHI=A_source_hhi,dominant_source_share=A_dom,citation_HHI=A_cit_hhi,dominant_citation_share=A_cit_dom),
 source_adjusted=c(vs,list(fixed_effects=as.list(setNames(as.numeric(fixef(fit_source)),names(fixef(fit_source)))))),
 citation_adjusted=c(vc,list(fixed_effects=as.list(setNames(as.numeric(fixef(fit_cit)),names(fixef(fit_cit)))))),
 unadjusted=list(R_family=0.1504,R_trait=0.0433,R_residual=0.8063),
 absolute_change_R_family=list(source=vs$R_family-0.1504,citation=vc$R_family-0.1504),
 interpretation_role="Post-outcome sensitivity only; no causal inference and no change to prospective conclusions.")
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
