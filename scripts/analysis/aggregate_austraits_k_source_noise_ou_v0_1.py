#!/usr/bin/env python3
"""Matched 12-trait OU+source envelope: original observed K versus calibrated null.

No calibration uses K outcomes. Both observations and all simulated statistics
use the same original systems, minus seed_height's predeclared source gate.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from aggregate_austraits_k_brownian_null_v0_1 import rank_gain,absolute_gain,reversal
from aggregate_austraits_k_shared_ou_v0_1 import verify_archived_K_identity

B=256
AXES={"S3":"S3_logK","prune_only":"prune_logK"}
SCENARIOS=("c0p25","c1","c4")
MODELS=("trait_global","system_local")
STATUS="AUSTRAITS_K_SOURCE_NOISE_OU_METRIC_NULL_ESTIMATED"

def main():
    ap=argparse.ArgumentParser()
    for nm in ("input-dir","observed-K","source-calibration","time-reference","design","out","tables-dir"):
        ap.add_argument("--"+nm,required=True,type=Path)
    a=ap.parse_args()
    design=json.loads(a.design.read_text())
    if design.get("status")!="POST_OBSERVED_K_AND_SHARED_OU_PRE_SOURCE_DISPERSION_OUTCOMES_FROZEN":
        raise ValueError("source-noise decision not frozen")
    src=json.loads(a.__dict__["source_calibration"].read_text())
    if src.get("status")!="AUSTRAITS_K_CROSS_SOURCE_DISPERSION_ESTIMATED" or src.get("eligible_traits")!=12:
        raise ValueError("incorrect independent source calibration")
    reference=json.loads(a.__dict__["time_reference"].read_text())
    if reference.get("status")!="AUSTRAITS_REAL_TREE_OU_TIME_REFERENCE_FROZEN":
        raise ValueError("bad prior source-native OU time reference")
    observed=pd.read_csv(a.__dict__["observed_K"])
    if (len(observed),observed.family.nunique(),observed.trait_name.nunique())!=(254,42,13):
        raise ValueError("original K reference modified")
    observed=observed.loc[observed.trait_name!="seed_height"].copy()
    observed=observed.sort_values(["family","trait_name"]).reset_index(drop=True)
    if (len(observed),observed.family.nunique(),observed.trait_name.nunique())!=(249,42,12):
        raise ValueError("wrong pre-frozen 12-trait system graph")
    if (observed.groupby("family").size()<2).any():
        raise ValueError("source-conditioned family has fewer than 2 traits")
    if observed[["family","trait_name"]].duplicated().any():
        raise ValueError("duplicate original matched family trait graph")
    if set(src["traits"])!=set(pd.read_csv(a.__dict__["observed_K"]).trait_name):
        raise ValueError("source trait list diverges")
    exact={r.system_id:r for r in observed.itertuples(index=False)}
    src_sys={r["system_id"]:r for r in src["systems"]}
    if len(src_sys)!=254:raise ValueError("source ratio system identity duplicate")
    sims={}
    for file in sorted(a.__dict__["input_dir"].glob("*.json")):
        z=json.loads(file.read_text())
        sid=z.get("system_id")
        if z.get("status")!="AUSTRAITS_K_SOURCE_NOISE_OU_SYSTEM_ESTIMATED":
            raise ValueError("invalid K source-noise archive")
        if sid not in exact or sid in sims:
            raise ValueError("duplicate/unexpected source-noise simulation "+str(sid))
        r=exact[sid]
        if (z["family"],z["trait_name"])!=(r.family,r.trait_name):
            raise ValueError("changed K family/trait identity")
        trait_meta=src["traits"][r.trait_name]
        system_meta=src_sys[sid]
        global_eta=trait_meta["source_log_variance_ratio_median"]
        local_eta=(system_meta["relative_source_dispersion"]
                   if system_meta["calibratable"] else global_eta)
        for key,refvalue in [("eta_global",global_eta),("eta_local",local_eta)]:
            if refvalue is None or not np.isfinite(refvalue) or refvalue<0:
                raise ValueError("invalid calibrated source ratio")
            if abs(float(z[key])-float(refvalue))>1e-9*max(1,refvalue):
                raise ValueError("source-model eta no longer matches K-blind calibration")
        if z["eta_local_fallback"]!= (not system_meta["calibratable"]):
            raise ValueError("wrong K-blind local fallback")
        if abs(z["T_ref"]-reference["T_ref"])>1e-10*reference["T_ref"]:
            raise ValueError("time normalization mutated")
        for axis,col in AXES.items():
            meta=z["axes"][axis]
            verify_archived_K_identity(sid,axis,meta,r,col)
            if meta["observed_fast_K_error"]>.0002:
                raise ValueError("native tip-tree K identity failed")
            for scen in SCENARIOS:
                s=meta["scenarios"][scen]
                if abs(float(s["alpha"])-float(reference["absolute_alpha_grid"][scen]))>1e-10*s["alpha"]:
                    raise ValueError("OU attraction not pre-frozen")
                for model in MODELS:
                    vals=s["models"][model]["logK"]
                    if len(vals)!=B or not np.isfinite(np.asarray(vals,dtype=float)).all():
                        raise ValueError("incomplete/nonfinite simulation K")
        sims[sid]=z
    if set(sims)!=set(exact):
        raise ValueError(f"missing K source-noise systems: {len(set(exact)-set(sims))}")
    out={
        "status":STATUS,"version":"v0.1",
        "observed_graph":{"systems":249,"families":42,"traits":12},
        "excluded_by_K_blind_source_gate":["seed_height"],
        "replicates":B,"source_calibration_input_status":src["status"],
        "models":{},"hard_nonclaims":[
           "Source-associated species dispersion is not pure measurement error.",
           "Latent homogeneous OU with independent tip noise omits correlated environmental and source effects.",
           "This post-K/OU sensitivity cannot be described as prospective discovery or adaptive mechanism."]
    }
    a.__dict__["tables_dir"].mkdir(parents=True,exist_ok=True)
    observed.to_csv(a.__dict__["tables_dir"]/"observed_subset.csv",index=False)
    for model in MODELS:
        result={}
        for scen in SCENARIOS:
            rows=[]
            for rep in range(B):
                for r in observed.itertuples(index=False):
                    z=sims[r.system_id]
                    rows.append({
                        "replicate":rep,"scenario":scen,"noise_model":model,
                        "system_id":r.system_id,"family":r.family,"trait_name":r.trait_name,
                        "S3_logK":float(z["axes"]["S3"]["scenarios"][scen]["models"][model]["logK"][rep]),
                        "prune_logK":float(z["axes"]["prune_only"]["scenarios"][scen]["models"][model]["logK"][rep])
                    })
            table=pd.DataFrame(rows).sort_values(["replicate","family","trait_name"])
            table.to_csv(a.__dict__["tables_dir"]/f"null_effects_{model}_{scen}.csv",index=False)
            scen_out={"axes":{}}
            for axis,col in AXES.items():
                ob={"rank_gain":rank_gain(observed,col),"absolute_gain":absolute_gain(observed,col)}
                ob["reversal_probability"],ob["n_trait_pairs"]=reversal(observed,col)
                arr=[]
                for rep,g in table.groupby("replicate",sort=True):
                    rr={"rank_gain":rank_gain(g,col),"absolute_gain":absolute_gain(g,col)}
                    rr["reversal_probability"],rr["n_trait_pairs"]=reversal(g,col)
                    arr.append(rr)
                null={}
                for metric in ("rank_gain","absolute_gain","reversal_probability"):
                    vals=np.asarray([v[metric] for v in arr],float)
                    null[metric]={
                       "mean":float(vals.mean()),
                       "q025":float(np.quantile(vals,.025)),
                       "q975":float(np.quantile(vals,.975)),
                       "p_null_ge_observed":float((1+(vals>=ob[metric]).sum())/(B+1)),
                       "p_null_le_observed":float((1+(vals<=ob[metric]).sum())/(B+1))
                    }
                scen_out["axes"][axis]={"observed":ob,"null":null}
            result[scen]=scen_out
        out["models"][model]=result
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"graph":out["observed_graph"],
                     "model_scenarios":len(MODELS)*len(SCENARIOS)}))

if __name__=="__main__":main()
