#!/usr/bin/env python3
"""Exploratory post-K check: does a larger K-blind source variance ratio
consistently point toward smaller observed Blomberg K?

Uses the exact same frozen 249-system subset as the pre-frozen OU+source
forward simulation. This is a *diagnostic*, not a substitute for its
simulation, a newly preregistered hypothesis, or an instrument-error estimate.
Permutation acts on trait labels globally, never on correlated family pairs.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

STATUS="AUSTRAITS_K_SOURCE_ETA_DIRECTION_EXPLORATORY_DIAGNOSTIC"
AXES=("S3_logK","prune_logK")

def compare(k:pd.DataFrame,source:dict,nperm:int=20000,seed:int=20261008)->dict:
    if source.get("status")!="AUSTRAITS_K_CROSS_SOURCE_DISPERSION_ESTIMATED" or source.get("eligible_traits")!=12:
        raise ValueError("incomplete K-blind source envelope")
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(254,42,13):
        raise ValueError("original observed K graph changed")
    if k[["family","trait_name"]].duplicated().any():
        raise ValueError("duplicate K systems")
    k=k[k.trait_name!="seed_height"].copy()
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(249,42,12):
        raise ValueError("fixed 12-trait source coverage graph changed")
    eta={t:float(source["traits"][t]["source_log_variance_ratio_median"])
         for t in sorted(k.trait_name.unique())}
    if any(not np.isfinite(z) or z<0 for z in eta.values()):
        raise ValueError("nonfinite/negative source dispersion ratios")
    traits=sorted(eta)
    if len(set(eta.values()))!=12:
        raise ValueError("source contrast ties require explicit prior rule")
    idx={t:i for i,t in enumerate(traits)}
    vals=np.array([eta[t] for t in traits],float)
    labels=k.trait_name.map(idx).to_numpy(int)
    f=k.family.to_numpy()
    pi=[];pj=[];rows=[]
    for fam,g in k.groupby("family",sort=True):
        inds=g.index.to_list()
        for i in range(len(inds)):
            for j in range(i):
                pi.append(idx[k.loc[inds[i],"trait_name"]])
                pj.append(idx[k.loc[inds[j],"trait_name"]])
                rows.append((inds[i],inds[j]))
    if len(rows)==0:raise ValueError("not enough within-family trait pairs")
    pi=np.asarray(pi,int);pj=np.asarray(pj,int)
    rng=np.random.default_rng(seed)
    perm=np.array([rng.permutation(len(traits)) for _ in range(nperm)])
    result={}
    for col in AXES:
        if not np.isfinite(k[col].to_numpy(float)).all():
            raise ValueError("nonfinite observed logK")
        y=k[col].astype(float)
        direction=np.array([np.sign(y.loc[i]-y.loc[j]) for i,j in rows])
        retain=direction!=0
        a,b,sgn=pi[retain],pj[retain],direction[retain]
        observed=float(np.mean((vals[a]-vals[b])*sgn<0))
        null=[]
        # Shared label shuffling preserves correlated pair observations.
        for batch in np.array_split(perm,max(1,min(nperm,100))):
            mapped=vals[batch]
            null.extend(np.mean((mapped[:,a]-mapped[:,b])*sgn[None,:]<0,axis=1))
        null=np.asarray(null,float)
        result[col]={
          "source_ratio_higher_predicts_K_lower_pair_agreement":observed,
          "n_within_family_comparisons":int(len(sgn)),
          "permutation_null_mean":float(np.mean(null)),
          "permutation_null_q025":float(np.quantile(null,.025)),
          "permutation_null_q975":float(np.quantile(null,.975)),
          "exploratory_p_global_trait_label_permutation":float((1+np.sum(null>=observed))/(len(null)+1))
        }
    return {
      "status":STATUS,"version":"v0.1",
      "graph":{"systems":249,"families":42,"traits":12},
      "permutations":nperm,"permutation_seed":seed,
      "description":"Exploratory trait-label permutation of family-blocked source-ratio versus observed K pair direction, not a process-null test.",
      "axes":result,
      "cannot_infer":["Instrument measurement-error causality","Heterogeneous evolution","Success/failure of full independent OU+source simulations"]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--observed-K",required=True,type=Path)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=compare(pd.read_csv(args.__dict__["observed_K"]),json.loads(args.source.read_text()))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({axis:r["source_ratio_higher_predicts_K_lower_pair_agreement"]
        for axis,r in result["axes"].items()},sort_keys=True))

if __name__=="__main__":
    main()
