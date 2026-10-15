#!/usr/bin/env python3
"""Post-outcome functional-module adequacy against the FROZEN original-tip OU
plus K-blind calibrated observation/source variance simulator.

This is a distinct, original-separate-tip 249-system analysis. DO NOT use its
null envelopes as a reference for 760 matched-species/trees pairs, which have
different geometry. Organ module was named after observing real K outcomes;
Monte Carlo p values are DESCRIPTIVE model-adequacy diagnostics only.
"""
from __future__ import annotations
import argparse,json
from itertools import product
from pathlib import Path
import numpy as np,pandas as pd

STATUS="AUSTRAITS_K_ORGAN_MODULE_SOURCE_OU_POST_OUTCOME_ADEQUACY_V0_1"
VALID_STATUS="AUSTRAITS_K_SOURCE_NOISE_OU_SYSTEM_ESTIMATED"
AXES={"S3":"S3_logK","prune_only":"prune_logK"}
SCENARIOS=("c0p25","c1","c4")
MODELS=("trait_global","system_local")
N=256

def metric_summary(original_signs,sim_signs,family_ids):
    """Two null adequacy targets; preserve whole-family dependence per draw."""
    original=np.asarray(original_signs,dtype=float)
    sim=np.asarray(sim_signs,dtype=float)
    ids=np.asarray(family_ids)
    if original.ndim!=1 or sim.shape!=(len(original),N):
        raise ValueError("wrong number of named-organ null draws or pair identities")
    if not np.isin(original,[0,1]).all() or not np.isin(sim,[0,1]).all():
        raise ValueError("invalid binary module rank comparison")
    uniq=np.unique(ids)
    if len(uniq)<1:raise ValueError("empty family support")
    p_o=float(original.mean());p_sim=sim.mean(axis=0)
    o_f=np.asarray([original[ids==f].mean() for f in uniq])
    p_f=np.asarray([sim[ids==f].mean(axis=0) for f in uniq])
    observed_f=float(o_f.mean());sim_f=p_f.mean(axis=0)
    def audit_one(x,reference):
        return {"observed":float(x),
                "null_mean":float(reference.mean()),
                "null_q025":float(np.quantile(reference,.025)),
                "null_q975":float(np.quantile(reference,.975)),
                "null_replicates_ge_observed":int((reference>=x).sum()),
                "descriptive_Monte_Carlo_p_one_sided":float((1+(reference>=x).sum())/(N+1)),
                "observed_exceeds_q975":bool(x>np.quantile(reference,.975))}
    return {"n_inter_organ_family_pairs":int(len(original)),
            "n_families":int(len(uniq)),
            "pair_weighted":audit_one(p_o,p_sim),
            "equal_family":audit_one(observed_f,sim_f)}

def analyze(k,raw,design):
    if design.get("status")!="POST_760_K_OUTCOMES_FUNCTIONAL_MODULE_EXPLORATORY_AUDIT_FROZEN_BEFORE_NEW_RESULTS":
        raise ValueError("functional module post-outcome provenance missing")
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(254,42,13):
        raise ValueError("the original observed K graph changed")
    k=k[k.trait_name!="seed_height"].copy().sort_values(["family","trait_name"]).reset_index(drop=True)
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(249,42,12):
        raise ValueError("not source-calibratable 249-system graph")
    reps=set(design["fixed_organ_classes"]["reproductive"])
    veg=set(design["fixed_organ_classes"]["vegetative"])
    if len(reps)!=6 or len(veg)!=6 or reps&veg or set(k.trait_name)!=reps|veg:
        raise ValueError("functional morphology class identities changed")
    if set(raw)!=set(k.system_id):
        raise ValueError("not every original source-OU system present")
    by_fam={}
    for r in k.itertuples(index=False):
        z=raw[str(r.system_id)]
        if (z.get("status")!=VALID_STATUS or z["family"]!=r.family
            or z["trait_name"]!=r.trait_name or z["replicates_per_model"]!=N):
            raise ValueError("source-OU system identity or simulation length invalid")
        by_fam.setdefault(r.family,[]).append(r)
    combos=[]
    for f,systems in sorted(by_fam.items()):
        rs=[r for r in systems if r.trait_name in reps]
        vs=[r for r in systems if r.trait_name in veg]
        for a,b in product(rs,vs):
            combos.append((f,a,b))
    if (len(combos),len(set(f for f,a,b in combos)))!=(410,34):
        raise ValueError("original-tip reproductive/vegetative graph must be 410 pairs / 34 families")
    out={"version":"v0.1","status":STATUS,
         "fixed_graph":{"systems":249,"families":42,"traits":12},
         "observed_original_tip_inter_organ_pairs":410,
         "families_with_inter_organ_pairs":34,
         "simulation_draws":N,"model_results":{},
         "after_observed_K_OU_source_and_matched_tip_K":True,
         "NOT_applicable_to_760_matched_taxon_null_distribution":True,
         "independent_TRY_v7_validation":False,
         "no_original_process_null_decision_changed":True,
         "scientific_nonclaim":"Organ grouping selected after K outcomes; each process-null cell is an exploratory posterior predictive adequacy check on the ORIGINAL disparate tip supports. No adaptive/selection process identified."}
    for model in MODELS:
        out["model_results"][model]={}
        for scenario in SCENARIOS:
            out["model_results"][model][scenario]={}
            for axis,column in AXES.items():
                signs=[];sim=[];families=[]
                for f,A,B in combos:
                    rawA=raw[A.system_id]["axes"][axis]
                    rawB=raw[B.system_id]["axes"][axis]
                    # The same source-native K graph was independently
                    # recomputed in the archived original processes.
                    if abs(float(rawA["observed_logK"])-float(getattr(A,column)))>1e-3 or abs(float(rawB["observed_logK"])-float(getattr(B,column)))>1e-3:
                        raise ValueError("original K response differs materially from source-OU archive")
                    a=np.asarray(rawA["scenarios"][scenario]["models"][model]["logK"],float)
                    b=np.asarray(rawB["scenarios"][scenario]["models"][model]["logK"],float)
                    if a.shape!=(N,) or b.shape!=(N,) or not np.isfinite(a).all() or not np.isfinite(b).all():
                        raise ValueError("not 256 finite source-OU simulations per system")
                    signs.append(float(getattr(A,column)>getattr(B,column)))
                    sim.append(a>b)
                    families.append(f)
                result=metric_summary(signs,sim,families)
                if (result["n_inter_organ_family_pairs"],result["n_families"])!=(410,34):
                    raise ValueError("source-calibrated OU module graph mismatch")
                out["model_results"][model][scenario][axis]=result
    return out

def main():
    p=argparse.ArgumentParser()
    for flag in ("source-ou-dir","observed-K","design","out"):
        p.add_argument("--"+flag,required=True,type=Path)
    a=p.parse_args()
    src={}
    for path in sorted(a.__dict__["source_ou_dir"].glob("*.json")):
        v=json.loads(path.read_text())
        sid=str(v["system_id"])
        if sid in src:raise ValueError("duplicate original source-OU system")
        src[sid]=v
    result=analyze(pd.read_csv(a.__dict__["observed_K"]),src,
                   json.loads(a.design.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,"n_conditions":12,
         "all_pair_weighted_exceed_q975":all(
          result["model_results"][m][s][a]["pair_weighted"]["observed_exceeds_q975"]
          for m in MODELS for s in SCENARIOS for a in AXES),
         "all_family_equal_exceed_q975":all(
          result["model_results"][m][s][a]["equal_family"]["observed_exceeds_q975"]
          for m in MODELS for s in SCENARIOS for a in AXES)},indent=2))
if __name__=="__main__":main()
