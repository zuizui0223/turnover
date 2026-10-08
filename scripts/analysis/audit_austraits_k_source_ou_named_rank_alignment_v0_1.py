#!/usr/bin/env python3
"""Post-OU-outcome *exploratory* posterior-predictive named-trait rank check.

This does not change, replace, tune or upgrade the frozen pre-source-noise
primary statistic (LOFO rank gain). The primary test assesses how repeatable
a trait ranking is; this audit asks if it is the *empirical named ranking*.
The 256 independent source-OU draws provide a conditional internal
reference distribution, not independent evidence of actual process history.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SCENARIOS=("c0p25","c1","c4")
MODELS=("trait_global","system_local")
AXES={"S3":"S3_logK","prune_only":"prune_logK"}
STATUS="AUSTRAITS_SOURCE_OU_NAMED_TRAIT_ALIGNMENT_EXPLORATORY_V0_1"

def profile_rank(z:np.ndarray,families:list[np.ndarray],tr_index:np.ndarray,nt:int)->np.ndarray:
    z=np.asarray(z,float)
    if z.ndim==1:z=z[None,:]
    if not np.isfinite(z).all():raise ValueError("nonfinite logK")
    ranks=np.empty_like(z)
    for ix in families:
        if len(ix)<2:raise ValueError("family with fewer than two traits")
        vals=z[:,ix]
        if np.any(np.diff(np.sort(vals,axis=1),axis=1)==0):
            raise ValueError("exact trait rank ties require a predeclared tie policy")
        order=np.argsort(vals,axis=1)
        ranks[:,ix]=np.argsort(order,axis=1)/(len(ix)-1)
    return np.column_stack([ranks[:,tr_index==t].mean(axis=1) for t in range(nt)])

def main():
    p=argparse.ArgumentParser()
    for f in ("input-dir","observed-K","out"):
        p.add_argument("--"+f,required=True,type=Path)
    a=p.parse_args()
    k=pd.read_csv(a.__dict__["observed_K"])
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(254,42,13):
        raise ValueError("source-native observed K core changed")
    k=k[k.trait_name!="seed_height"].sort_values(["family","trait_name"]).reset_index(drop=True)
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(249,42,12):
        raise ValueError("K-blind 12-trait subgraph changed")
    traits=sorted(k.trait_name.unique())
    ix={t:i for i,t in enumerate(traits)}
    tidx=k.trait_name.map(ix).to_numpy(int)
    families=[g.index.to_numpy() for _,g in k.groupby("family",sort=True)]
    raw={}
    for path in sorted(a.__dict__["input_dir"].glob("*.json")):
        z=json.loads(path.read_text())
        sid=z.get("system_id")
        if z.get("status")!="AUSTRAITS_K_SOURCE_NOISE_OU_SYSTEM_ESTIMATED" or sid in raw:
            raise ValueError("invalid/duplicate archived OU source system")
        raw[sid]=z
    if set(raw)!=set(k.system_id):
        raise ValueError("OU source archive does not match 249 systems")
    for r in k.itertuples(index=False):
        if (raw[r.system_id]["family"],raw[r.system_id]["trait_name"])!=(r.family,r.trait_name):
            raise ValueError("source-OU system identity mismatch")
    out={"version":"v0.1","status":STATUS,
         "fixed_graph":{"systems":249,"families":42,"traits":12},
         "after_empirical_K_and_source_OU_outcomes":True,
         "models":{},
         "scientific_nonclaim":"A posterior-predictive descriptive diagnostic. Failure to reproduce the named-trait rank profile does not prove process heterogeneity or adaptation."}
    ids=list(k.system_id)
    for model in MODELS:
        out["models"][model]={}
        for scen in SCENARIOS:
            out["models"][model][scen]={}
            for axis,col in AXES.items():
                empirical=profile_rank(k[col].to_numpy(float),families,tidx,len(traits))[0]
                null=np.asarray([raw[sid]["axes"][axis]["scenarios"][scen]["models"][model]["logK"] for sid in ids],float).T
                if null.shape!=(256,249):raise ValueError("wrong source-null draw dimensions")
                profiles=profile_rank(null,families,tidx,len(traits))
                expected=profiles.mean(axis=0)
                observed_rho=float(spearmanr(empirical,expected).statistic)
                # Self-held-out reference: each simulated realization is
                # compared to its expectation from the other 255 draws.
                ref=(256*expected[None,:]-profiles)/255
                ref_rho=np.array([spearmanr(profiles[i],ref[i]).statistic for i in range(256)],float)
                if not np.isfinite(ref_rho).all():raise ValueError("undefined profile correlation")
                out["models"][model][scen][axis]={
                    "observed_vs_null_expected_named_trait_rho":observed_rho,
                    "null_replicate_self_rho_mean":float(ref_rho.mean()),
                    "null_replicate_self_rho_q025":float(np.quantile(ref_rho,.025)),
                    "null_replicate_self_rho_q975":float(np.quantile(ref_rho,.975)),
                    "descriptive_p_null_self_rho_le_observed":float((1+np.sum(ref_rho<=observed_rho))/257),
                    "observed_mean_normalized_within_family_rank":dict(zip(traits,map(float,empirical))),
                    "null_expected_mean_normalized_within_family_rank":dict(zip(traits,map(float,expected))),
                }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"example_S3_global_c1":
        out["models"]["trait_global"]["c1"]["S3"]["observed_vs_null_expected_named_trait_rho"]}))

if __name__=="__main__":
    main()
