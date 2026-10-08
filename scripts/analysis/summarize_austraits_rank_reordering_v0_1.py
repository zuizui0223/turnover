#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--rank-portability",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
df=pd.read_csv(a.effects)
rp=json.loads(a.rank_portability.read_text())
for c in ["S3_rho","prune_only_rho"]:
    if df[c].isna().any():raise SystemExit(f"nonfinite {c}")

def family_ranks(col):
    parts=[]
    for fam,g in df.groupby("family",sort=True):
        if len(g)<2:continue
        h=g[["family","trait_name",col]].copy()
        r=rankdata(h[col].to_numpy(float),method="average")
        h["rank01"]=(r-1)/(len(h)-1);parts.append(h)
    return pd.concat(parts,ignore_index=True)

def reversal(col,minco):
    vals=[];w=[];pairs=[];trs=sorted(df.trait_name.unique())
    for i,A in enumerate(trs):
        da=df[df.trait_name==A][["family",col]].rename(columns={col:"a"})
        for B in trs[i+1:]:
            db=df[df.trait_name==B][["family",col]].rename(columns={col:"b"})
            m=da.merge(db,on="family")
            if len(m)<minco:continue
            d=m.a-m.b;pos=int((d>0).sum());neg=int((d<0).sum());n=pos+neg
            if n<2:continue
            p=2*pos*neg/(n*(n-1));ww=n*(n-1)/2
            vals.append(p);w.append(ww);pairs.append({"trait_a":A,"trait_b":B,"n_families":n,"reversal_probability":p})
    return {"n_trait_pairs":len(vals),"weighted_probability":float(np.average(vals,weights=w)) if vals else None,
            "mean_unweighted":float(np.mean(vals)) if vals else None,"median":float(np.median(vals)) if vals else None,
            "pairs":pairs}

def family_pair_corr(col,minshared):
    fs=sorted(df.family.unique());vals=[]
    for i,A in enumerate(fs):
        da=df[df.family==A][["trait_name",col]]
        for B in fs[i+1:]:
            db=df[df.family==B][["trait_name",col]]
            m=da.merge(db,on="trait_name",suffixes=("_a","_b"))
            if len(m)>=minshared:
                v=spearmanr(m[col+"_a"],m[col+"_b"]).statistic
                if np.isfinite(v):vals.append(float(v))
    return {"n_family_pairs":len(vals),"mean_spearman":float(np.mean(vals)) if vals else None,
            "median_spearman":float(np.median(vals)) if vals else None}

s3mean=family_ranks("S3_rho").groupby("trait_name").rank01.mean()
prmean=family_ranks("prune_only_rho").groupby("trait_name").rank01.mean()
common=s3mean.index.intersection(prmean.index)
global_corr=float(spearmanr(s3mean.loc[common],prmean.loc[common]).statistic)
rev_s3=reversal("S3_rho",10);rev_pr=reversal("prune_only_rho",10)
p3=rev_s3["weighted_probability"];pp=rev_pr["weighted_probability"]
strong=bool(p3 is not None and pp is not None and p3>=0.40 and pp>=0.40)
substantial=bool(p3 is not None and pp is not None and p3>=1/3 and pp>=1/3)
portable=bool(rp["S3"]["axis_pass"] and rp["prune_only"]["axis_pass"])
if portable and strong:decision="GLOBAL_SPECTRUM_PLUS_STRONG_REORDERING_REPLICATED"
elif portable and substantial:decision="GLOBAL_SPECTRUM_PLUS_SUBSTANTIAL_REORDERING_REPLICATED"
elif portable:decision="GLOBAL_SPECTRUM_REPLICATED_REORDERING_LIMITED_OR_AXIS_SENSITIVE"
else:decision="GLOBAL_SPECTRUM_PORTABILITY_NOT_REPLICATED"
out={
 "version":"v0.1","status":"AUSTRAITS_TRAIT_RANK_REORDERING_SUMMARIZED","austraits_memory_effects_opened":True,
 "n_systems":len(df),"n_families":df.family.nunique(),"n_traits":df.trait_name.nunique(),
 "global_trait_mean_rank_S3_vs_prune_spearman":global_corr,
 "direct_reordering":{
   "S3_min2":reversal("S3_rho",2),"prune_min2":reversal("prune_only_rho",2),
   "S3_min10":rev_s3,"prune_min10":rev_pr
 },
 "family_pair_rank_similarity":{
   "S3_min3":family_pair_corr("S3_rho",3),"prune_min3":family_pair_corr("prune_only_rho",3),
   "S3_min4":family_pair_corr("S3_rho",4),"prune_min4":family_pair_corr("prune_only_rho",4)
 },
 "rank_portability":{"S3":rp["S3"],"prune_only":rp["prune_only"]},
 "decision":decision,
 "strong_reordering":strong,"substantial_reordering":substantial,"global_spectrum_portability":portable
}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in out.items() if k!="direct_reordering"},indent=2,sort_keys=True))
