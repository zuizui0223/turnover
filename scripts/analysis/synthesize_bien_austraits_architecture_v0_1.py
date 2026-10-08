#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,warnings,math
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr
warnings.filterwarnings("ignore")

ap=argparse.ArgumentParser()
ap.add_argument("--bien-effects",type=Path,required=True)
ap.add_argument("--austraits-effects",type=Path,required=True)
ap.add_argument("--austraits-analysis-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--family-scores-out",type=Path,required=True)
ap.add_argument("--permutations",type=int,default=9999)
ap.add_argument("--seed",type=int,default=20261007)
a=ap.parse_args()
b=pd.read_csv(a.bien_effects);u=pd.read_csv(a.austraits_effects)
ul=u[u.log_domain_pass==True].copy()
if len(b)!=201 or len(u)!=259 or len(ul)!=254: raise SystemExit("unexpected source dimensions")

def absolute_portability(df,col,B,seed):
    fams=sorted(df.family.unique());trs=sorted(df.trait_name.unique())
    fm={f:i for i,f in enumerate(fams)};tm={t:i for i,t in enumerate(trs)}
    fi=np.array([fm[x] for x in df.family]);ti=np.array([tm[x] for x in df.trait_name]);y=df[col].to_numpy(float)
    nf=len(fams);nt=len(trs);n=len(y)
    fg=[np.flatnonzero(fi==k) for k in range(nf)]
    fc=np.bincount(fi,minlength=nf);tc=np.bincount(ti,minlength=nt)
    total=y.sum();fs=np.bincount(fi,weights=y,minlength=nf);ts=np.bincount(ti,weights=y,minlength=nt)
    base=(total-fs[fi])/(n-fc[fi]);pred=(ts[ti]-y)/(tc[ti]-1)
    s0=float(np.sum((y-base)**2));gain=1-float(np.sum((y-pred)**2))/s0
    rng=np.random.default_rng(seed);null=np.empty(B)
    for j in range(B):
        yp=y.copy()
        for idx in fg:yp[idx]=rng.permutation(yp[idx])
        tsum=np.bincount(ti,weights=yp,minlength=nt);pp=(tsum[ti]-yp)/(tc[ti]-1)
        null[j]=1-float(np.sum((yp-pp)**2))/s0
    p=float((1+np.sum(null>=gain))/(B+1))
    return {"gain":gain,"p_one_sided":p,"null_q025":float(np.quantile(null,.025)),
            "null_median":float(np.median(null)),"null_q975":float(np.quantile(null,.975))}

def reversal(df,col,minco=10):
    traits=sorted(df.trait_name.unique())
    obs=maxobs=den=0;n_pairs=0
    for i,A in enumerate(traits):
        da=df[df.trait_name==A][["family",col]].rename(columns={col:"a"})
        for B in traits[i+1:]:
            db=df[df.trait_name==B][["family",col]].rename(columns={col:"b"})
            m=da.merge(db,on="family")
            if len(m)<minco:continue
            d=m.a-m.b;pos=int((d>0).sum());neg=int((d<0).sum());n=pos+neg
            if n<2:continue
            obs+=pos*neg
            maxobs+=(n//2)*(n-n//2)
            den+=n*(n-1)/2
            n_pairs+=1
    return {"n_trait_pairs":n_pairs,"weighted_reversal_probability":obs/den,
            "fraction_of_pair_specific_maximum":obs/maxobs}

def fit_blup(df,col):
    d=df[["family","trait_name",col]].dropna().rename(columns={col:"rho"}).copy()
    m=smf.mixedlm("rho ~ 0 + C(trait_name)",d,groups=d.family)
    last=None
    for method in ["lbfgs","powell","cg","bfgs","nm"]:
        try:
            f=m.fit(reml=True,method=method,maxiter=2000,disp=False)
            vf=float(f.cov_re.iloc[0,0]);ve=float(f.scale)
            if vf>1e-10:
                re={fam:float(np.asarray(v).ravel()[0]) for fam,v in f.random_effects.items()}
                return re,{"family_variance":vf,"residual_variance":ve,"conditional_repeatability":vf/(vf+ve),"optimizer":method}
        except Exception as e:last=e
    raise RuntimeError(last)

def cross_source_family_context(bb,uu,bc,uc,seed):
    rb,mb=fit_blup(bb,bc);ru,mu=fit_blup(uu,uc)
    fams=sorted(set(rb)&set(ru));x=np.array([rb[f] for f in fams]);y=np.array([ru[f] for f in fams])
    obs=float(spearmanr(x,y).statistic)
    rng=np.random.default_rng(seed);null=np.empty(a.permutations)
    for i in range(a.permutations):null[i]=spearmanr(x,rng.permutation(y)).statistic
    p=float((1+np.sum(null>=obs))/(a.permutations+1))
    rows=[{"family":f,"bien_blup":rb[f],"austraits_blup":ru[f]} for f in fams]
    return {"n_shared_families":len(fams),"spearman":obs,"p_one_sided":p,
            "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
            "BIEN_model":mb,"AusTraits_model":mu},rows

rank_bien={
 "S3_log":{"gain":0.0681399209446556,"p_one_sided":0.0003},
 "prune_log":{"gain":0.02790313402089284,"p_one_sided":0.0071}
}
ar=json.load(open(a.austraits_analysis_dir/"rank_portability.json"))
af=json.load(open(a.austraits_analysis_dir/"family_repeatability.json"))

abs_bien={
 "S3_log":absolute_portability(b,"S3_log_rho",a.permutations,a.seed),
 "prune_log":absolute_portability(b,"prune_log_rho",a.permutations,a.seed+1)
}
abs_aus={
 "S3_log":absolute_portability(ul,"S3_log_rho",a.permutations,a.seed+2),
 "prune_log":absolute_portability(ul,"prune_log_rho",a.permutations,a.seed+3)
}
rev={
 "BIEN_log_S3":reversal(b,"S3_log_rho"),
 "BIEN_log_prune":reversal(b,"prune_log_rho"),
 "AusTraits_log_S3":reversal(ul,"S3_log_rho"),
 "AusTraits_log_prune":reversal(ul,"prune_log_rho"),
 "AusTraits_source_native_S3":reversal(u,"S3_rho"),
 "AusTraits_source_native_prune":reversal(u,"prune_only_rho")
}

ctx_s3,score_s3=cross_source_family_context(b,ul,"S3_log_rho","S3_log_rho",a.seed+4)
ctx_pr,score_pr=cross_source_family_context(b,ul,"prune_log_rho","prune_log_rho",a.seed+5)
score_rows=[]
for r in score_s3:score_rows.append({"axis":"log_S3",**r})
for r in score_pr:score_rows.append({"axis":"log_prune",**r})
pd.DataFrame(score_rows).to_csv(a.family_scores_out,index=False)

anchors={
 "leaf_area":("leaf area","leaf_area"),
 "LMA_SLA":("leaf area per leaf dry mass","leaf_mass_per_area"),
 "height":("whole plant height","plant_height"),
 "seed_mass":("seed mass","seed_dry_mass")
}
anchor_rows=[]
for k,(bt,ut) in anchors.items():
    anchor_rows.append((k,float(b.loc[b.trait_name==bt,"S3_log_rho"].mean()),float(ul.loc[ul.trait_name==ut,"S3_log_rho"].mean())))
x=np.array([z[1] for z in anchor_rows]);y=np.array([z[2] for z in anchor_rows])
anchor_pair_agree=0;anchor_pair_total=0
for i in range(len(anchor_rows)):
    for j in range(i+1,len(anchor_rows)):
        anchor_pair_total+=1
        if np.sign(x[i]-x[j])==np.sign(y[i]-y[j]):anchor_pair_agree+=1

strict_validated=bool(ar["S3"]["axis_pass"] and ar["prune_only"]["axis_pass"] and
                      rev["AusTraits_source_native_S3"]["weighted_reversal_probability"]>=1/3 and
                      rev["AusTraits_source_native_prune"]["weighted_reversal_probability"]>=1/3)

out={
 "version":"v0.1",
 "status":"BIEN_AUSTRAITS_POST_OUTCOME_ARCHITECTURE_SYNTHESIS",
 "strict_prefrozen_architecture_validation":{
   "validated":strict_validated,
   "decision":"NOT_VALIDATED" if not strict_validated else "VALIDATED",
   "reason":"AusTraits pre-frozen rank-portability component did not achieve positive gain on both tree axes." if not strict_validated else "All pre-frozen components passed."
 },
 "source_dimensions":{
   "BIEN":{"systems":201,"families":45,"traits":12},
   "AusTraits":{"systems":259,"families":42,"traits":14},
   "AusTraits_matched_log":{"systems":254,"families":42,"traits":13}
 },
 "family_context":{
   "BIEN_primary_raw":{"estimate":0.1825,"ci95":[0.0285,0.3369],"interpretation":"UNCERTAIN_RELATIVE_TO_0.10"},
   "AusTraits_source_native":{"estimate":af["primary_S3"]["conditional_family_repeatability"],
     "ci95":af["bootstrap"]["ci95_conditional_family_repeatability"],"interpretation":af["interpretation"],
     "prune_estimate":af["prune_only_sensitivity"]["conditional_family_repeatability"]},
   "cross_source_log_S3_BLUP":ctx_s3,
   "cross_source_log_prune_BLUP":ctx_pr
 },
 "harmonized_absolute_trait_portability":{
   "BIEN_matched_log":abs_bien,
   "AusTraits_matched_log":abs_aus,
   "interpretation":"Named trait identity improves held-out-family absolute-rho prediction on both tree axes in both compilations, but gains are small."
 },
 "within_family_rank_portability":{
   "BIEN_log":rank_bien,
   "AusTraits_source_native":{"S3":ar["S3"],"prune_only":ar["prune_only"]},
   "interpretation":"Relative trait ranking was weakly portable in BIEN log analyses but failed the prospective positive-gain criterion in AusTraits; a universal portable hierarchy is therefore not validated."
 },
 "pair_order_reordering":rev,
 "anchor_trait_descriptive":{
   "n_anchor_concepts":4,
   "log_S3_mean_rho_spearman":float(spearmanr(x,y).statistic),
   "pairwise_order_agreement":anchor_pair_agree/anchor_pair_total,
   "anchor_means":[{"anchor":k,"BIEN_mean_rho":bv,"AusTraits_mean_rho":uv} for k,bv,uv in anchor_rows],
   "interpretation":"Only four semantic anchors; descriptive, not an inferential replication test."
 },
 "revised_cross_dataset_architecture":{
   "supported":[
     "lineage-wide family context recurs within both compilations",
     "trait identity carries modest absolute cross-lineage predictive information in both compilations",
     "trait-pair ordering is extensively reconfigured among families in both compilations"
   ],
   "not_supported":[
     "a robust portable conservative-to-labile trait hierarchy across lineages"
   ],
   "central_interpretation":"Traits carry weak global priors in average phylogenetic memory, while lineage context strongly reconstructs their relative ordering."
 },
 "chronology":"Post-outcome synthesis. It does not reclassify the prospectively frozen AusTraits decisions."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
