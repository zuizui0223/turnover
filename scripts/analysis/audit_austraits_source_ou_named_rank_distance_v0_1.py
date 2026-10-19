#!/usr/bin/env python3
"""Post-outcome global adequacy diagnostic for the *named-trait K rank profile*.

This is NOT the pre-frozen primary source-OU test. It compares the observed
12-dimensional profile of within-family normalized ranks against the
conditional, frozen OU+source-noise simulator, preserving exact families,
traits, missingness and tip support. No model parameter is fitted to K.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr

STATUS="AUSTRAITS_SOURCE_OU_NAMED_RANK_DISTANCE_EXPLORATORY_V0_1"
MODELS=("trait_global","system_local")
SCENARIOS=("c0p25","c1","c4")
AXES={"S3":"S3_logK","prune_only":"prune_logK"}

def profile(x, family_indices, trait_indices):
    x=np.asarray(x,dtype=float)
    if x.ndim==1:x=x[None,:]
    if not np.isfinite(x).all():raise ValueError("nonfinite K states")
    rank=np.empty(x.shape,float)
    for ix in family_indices:
        if len(ix)<2:raise ValueError("family with fewer than two traits")
        for b in range(x.shape[0]):
            rank[b,ix]=(rankdata(x[b,ix],method="average")-1)/(len(ix)-1)
    return np.stack([rank[:,ix].mean(axis=1) for ix in trait_indices],axis=1)

def analyze(observed:pd.DataFrame, systems:dict):
    if (len(observed),observed.family.nunique(),observed.trait_name.nunique())!=(254,42,13):
        raise ValueError("changed original archived K graph")
    if observed[["system_id","family","trait_name"]].duplicated().any():
        raise ValueError("duplicate K source system")
    sub=observed.loc[observed.trait_name!="seed_height"].copy()
    sub=sub.sort_values(["family","trait_name"]).reset_index(drop=True)
    if (len(sub),sub.family.nunique(),sub.trait_name.nunique())!=(249,42,12):
        raise ValueError("wrong pre-frozen source-eligible graph")
    if set(systems)!=set(sub.system_id):raise ValueError("archived simulator does not match all 249 systems")
    for r in sub.itertuples(index=False):
        v=systems[r.system_id]
        if (v.get("family"),v.get("trait_name"))!=(r.family,r.trait_name):
            raise ValueError("misidentified simulator system")
        if v.get("status")!="AUSTRAITS_K_SOURCE_NOISE_OU_SYSTEM_ESTIMATED":
            raise ValueError("wrong source-OU simulator provenance")
    traits=sorted(sub.trait_name.unique())
    family_ix=[g.index.to_numpy(dtype=int) for _,g in sub.groupby("family",sort=True)]
    trait_ix=[sub.index[sub.trait_name==t].to_numpy(dtype=int) for t in traits]
    result={"version":"v0.1","status":STATUS,
            "fixed_graph":{"systems":249,"families":42,"traits":12},
            "replicates":256,"post_source_ou_outcome_exploratory":True,
            "not_a_primary_or_preregistered_result":True,"models":{},
            "estimand":"Sum across 12 named traits of squared deviations of family-normalized mean K ranks from model-expected ranks",
            "nonclaims":["Does not identify selection or trait-specific OU parameters",
                         "Does not supersede pre-frozen rank-gain classifier",
                         "Uses source-dispersion point estimates without their measurement uncertainty",
                         "The 12 comparisons share data and must not be treated as independent discoveries"]}
    ids=list(sub.system_id)
    for model in MODELS:
        result["models"][model]={}
        for scen in SCENARIOS:
            result["models"][model][scen]={}
            for axis,col in AXES.items():
                obs_profile=profile(sub[col].to_numpy(float),family_ix,trait_ix)[0]
                draws=np.asarray([systems[sid]["axes"][axis]["scenarios"][scen]
                     ["models"][model]["logK"] for sid in ids],float).T
                if draws.shape!=(256,249):
                    raise ValueError("wrong fixed-source OU simulation dimensions")
                sim_profiles=profile(draws,family_ix,trait_ix)
                center=sim_profiles.mean(axis=0)
                distance_obs=float(np.square(obs_profile-center).sum())
                # Compute a leave-one-replicate-out null reference to avoid
                # optimistic self-comparison of simulated data with its mean.
                self_center=(sim_profiles.sum(axis=0)[None,:]-sim_profiles)/255
                distance_null=np.square(sim_profiles-self_center).sum(axis=1)
                if not np.isfinite(distance_null).all():
                    raise ValueError("nonfinite profile simulation distance")
                mismatch=(obs_profile-center)
                by_trait={t:{"observed_rank":float(obs_profile[i]),
                             "null_expected_rank":float(center[i]),
                             "observed_minus_null":float(mismatch[i])}
                          for i,t in enumerate(traits)}
                result["models"][model][scen][axis]={
                     "observed_named_rank_squared_distance":distance_obs,
                     "null_distance_mean":float(distance_null.mean()),
                     "null_distance_q025":float(np.quantile(distance_null,.025)),
                     "null_distance_q975":float(np.quantile(distance_null,.975)),
                     "null_distance_exceedances":int(np.sum(distance_null>=distance_obs)),
                     "descriptive_p_null_ge_observed":float((1+np.sum(distance_null>=distance_obs))/257),
                     "observed_vs_null_named_rank_spearman":float(spearmanr(obs_profile,center).statistic),
                     "named_traits":by_trait
                }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",required=True,type=Path)
    p.add_argument("--observed-K",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    systems={}
    for file in sorted(a.input_dir.glob("*.json")):
        v=json.loads(file.read_text());key=v.get("system_id")
        if key in systems:raise ValueError("duplicate source-OU simulation")
        systems[key]=v
    result=analyze(pd.read_csv(a.__dict__["observed_K"]),systems)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"n_conditions":12,
         "p_values":[result["models"][m][s][axis]["descriptive_p_null_ge_observed"]
                     for m in MODELS for s in SCENARIOS for axis in AXES]},indent=2))

if __name__=="__main__":main()
