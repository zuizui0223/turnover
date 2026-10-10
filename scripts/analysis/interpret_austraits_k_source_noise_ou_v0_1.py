#!/usr/bin/env python3
"""Frozen conservative source-noise OU contrast; rank gain primary, ICC secondary."""
from __future__ import annotations
import argparse,json
from pathlib import Path

MODELS=("trait_global","system_local")
SCENARIOS=("c0p25","c1","c4")
AXES=("S3","prune_only")
METRIC_STATUS="AUSTRAITS_K_SOURCE_NOISE_OU_METRIC_NULL_ESTIMATED"
FAMILY_STATUS="AUSTRAITS_SOURCE_NOISE_OU_FAMILY_REPEATABILITY_CALIBRATED"
DESIGN_STATUS="POST_OBSERVED_K_AND_SHARED_OU_PRE_SOURCE_DISPERSION_OUTCOMES_FROZEN"
FINAL_STATUS="AUSTRAITS_K_SOURCE_NOISE_OU_NULL_INTERPRETED"

def compare(metric, families, design):
    if design.get("status")!=DESIGN_STATUS or metric.get("status")!=METRIC_STATUS:
        raise ValueError("unfrozen or incomplete source-noise interpretation")
    if metric.get("observed_graph")!={"systems":249,"families":42,"traits":12}:
        raise ValueError("source-conditioned K graph changed")
    if metric.get("replicates")!=256:
        raise ValueError("not all fixed OU source draws completed")
    if set(metric["models"])!=set(MODELS):
        raise ValueError("not all source models covered")
    if set(families)!={(m,s,a) for m in MODELS for s in SCENARIOS for a in AXES}:
        raise ValueError("missing/duplicate family model/scenario/axis")
    all_rank_exceed=True
    any_rank_accommodated=False
    result={
      "status":FINAL_STATUS,"version":"v0.1",
      "fixed_graph":metric["observed_graph"],
      "source_noise_models":{},
      "hard_nonclaims":metric["hard_nonclaims"],
      "classification_on_predeclared_rank_gain_only":True,
      "comparisons":12
    }
    for model in MODELS:
        out={}
        for scen in SCENARIOS:
            axes={}
            for axis in AXES:
                v=metric["models"][model][scen]["axes"][axis]
                f=families[(model,scen,axis)]
                if (f.get("status")!=FAMILY_STATUS or f.get("scenario")!=scen or
                    f.get("model")!=model or f.get("axis")!=axis or
                    f.get("n_null_replicates")!=256 or f.get("valid_null_replicates",0)<243):
                    raise ValueError("wrong source-noise family replicate or identity")
                rank_ob=v["observed"]["rank_gain"]
                rank_null=v["null"]["rank_gain"]
                exceed=rank_ob>rank_null["q975"]
                all_rank_exceed &= exceed
                any_rank_accommodated |= not exceed
                fam_ob=f["observed_family_repeatability"]
                fam_null=f["null_family_repeatability"]
                axes[axis]={
                    "observed_rank_gain":rank_ob,
                    "null_rank_mean":rank_null["mean"],
                    "null_rank_q975":rank_null["q975"],
                    "rank_p_null_ge":rank_null["p_null_ge_observed"],
                    "rank_exceeds_q975":exceed,
                    "observed_family_ICC":fam_ob,
                    "null_family_mean":fam_null["mean"],
                    "null_family_q975":fam_null["q975"],
                    "family_p_null_ge":fam_null["p_null_ge_observed"],
                    "family_exceeds_q975":fam_ob>fam_null["q975"],
                    "observed_reversal":v["observed"]["reversal_probability"],
                    "null_reversal_mean":v["null"]["reversal_probability"]["mean"]
                }
            out[scen]=axes
        result["source_noise_models"][model]=out
    result["decision"]=("RANK_PORTABILITY_BEYOND_TESTED_INDEPENDENT_OU_SOURCE_ENVELOPES"
                       if all_rank_exceed else
                       "RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES")
    result["at_least_one_predeclared_model_accommodates_rank"]=any_rank_accommodated
    return result

def main():
    ap=argparse.ArgumentParser()
    for k in ("metrics","family-dir","design","out"):
        ap.add_argument("--"+k,required=True,type=Path)
    a=ap.parse_args()
    fam={}
    for p in a.__dict__["family_dir"].glob("*.json"):
        z=json.loads(p.read_text())
        key=z.get("model"),z.get("scenario"),z.get("axis")
        if key in fam:raise ValueError("duplicate family model")
        fam[key]=z
    result=compare(json.loads(a.metrics.read_text()),fam,json.loads(a.design.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"decision":result["decision"],
                      "any_accommodation":result["at_least_one_predeclared_model_accommodates_rank"]}))

if __name__=="__main__":
    main()
