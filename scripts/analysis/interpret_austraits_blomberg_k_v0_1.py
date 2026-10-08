#!/usr/bin/env python3
"""Post-outcome interpretation of the fixed AusTraits Blomberg-K sensitivity.

Do not use this script to alter primary prospective rho decisions.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def check_inputs(architecture:dict,portability:dict,rho_k:dict,contract:dict):
    assert contract["status"]=="POST_RHO_PRE_K_OUTCOME_INTERPRETATION_CONTRACT"
    assert architecture["status"]=="AUSTRAITS_BLOMBERG_K_MIXED_MODELS_ESTIMATED"
    assert portability["status"]=="AUSTRAITS_BLOMBERG_K_PORTABILITY_ESTIMATED"
    assert rho_k["n_matched_systems"]==254
    assert set(architecture)>= {"prune_primary","S3_sensitivity"}
    assert set(portability)>= {"prune_primary","S3_sensitivity"}
    assert "S3" in rho_k and "prune" in rho_k

def classify(architecture:dict,portability:dict,rho_k:dict,contract:dict):
    check_inputs(architecture,portability,rho_k,contract)
    family_thr=contract["interpretation"]["family_reference_threshold"]
    substantial_thr=contract["interpretation"]["substantial_reordering_threshold"]
    strong_thr=contract["interpretation"]["strong_reordering_threshold"]
    axes={}
    for axis,rhok in [("prune_primary","prune"),("S3_sensitivity","S3")]:
        a=architecture[axis]
        p=portability[axis]
        fc=float(a["conditional_family_repeatability"])
        rev=float(p["pair_order_reversal"]["weighted_reversal_probability"])
        abs_pred=p["absolute_portability"]
        rank=p["rank_portability"]
        family=fc>family_thr
        substantial=rev>=substantial_thr
        strong=rev>=strong_thr
        axes[axis]={
          "family_repeatability":fc,
          "family_reference_exceeded":family,
          "reversal_probability":rev,
          "number_of_trait_pairs":p["pair_order_reversal"]["n_trait_pairs"],
          "substantial_reordering":substantial,
          "strong_reordering":strong,
          "K_absolute_trait_gain":abs_pred["gain"],
          "K_absolute_trait_blocked_p":abs_pred["p_one_sided"],
          "K_absolute_trait_portability_pass":abs_pred["axis_pass"],
          "K_rank_gain":rank["gain"],
          "K_rank_blocked_p":rank["p_one_sided"],
          "K_rank_portability_pass":rank["axis_pass"],
          "rho_K_system_spearman":rho_k[rhok]["overall_spearman_K_vs_rho"],
          "rho_K_within_family_mean_rank_spearman":rho_k[rhok]["mean_within_family_rank_correlation"],
          "architecture_strong_correspondence":family and strong,
          "architecture_substantial_correspondence":family and substantial,
        }
    strong_axes=sum(x["architecture_strong_correspondence"] for x in axes.values())
    substantial_axes=sum(x["architecture_substantial_correspondence"] for x in axes.values())
    if strong_axes==2:decision="K_ARCHITECTURE_CONCORDANT_BOTH_TREES"
    elif substantial_axes==2:decision="K_ARCHITECTURE_SUBSTANTIAL_BOTH_TREES"
    elif strong_axes==1 or substantial_axes==1:decision="K_ARCHITECTURE_TREE_DEPENDENT"
    else:decision="K_ARCHITECTURE_NOT_CORROBORATED"
    return {
      "version":"v0.1",
      "status":"AUSTRAITS_BLOMBERG_K_INTERPRETATION_COMPLETED",
      "post_rho_outcome_K_sensitivity":True,
      "matched_systems":254,
      "decision":decision,
      "axes":axes,
      "nonclaims":[
        "K and rho are distinct estimands and their values must not be substituted for each other.",
        "This K sensitivity is exploratory after inspecting the rho outcomes.",
        "Higher rho is not evidence of faster evolution or lower evolutionary conservatism.",
        "The architecture does not identify the ecological or genetic driver of reordering."
      ]
    }

def main():
    p=argparse.ArgumentParser()
    for name in ["contract","architecture","portability","rho-k","out"]:
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    result=classify(
      json.loads(a.architecture.read_text()),
      json.loads(a.portability.read_text()),
      json.loads(a.rho_k.read_text()),
      json.loads(a.contract.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "decision":result["decision"],
      "axes":{key:{"K_family_repeatability":v["family_repeatability"],
                    "K_rank_reversal":v["reversal_probability"],
                    "K_rho_correlation":v["rho_K_system_spearman"]} for key,v in result["axes"].items()}
    },indent=2))
if __name__=="__main__":
    main()
