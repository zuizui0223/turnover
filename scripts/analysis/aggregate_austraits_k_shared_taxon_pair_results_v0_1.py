#!/usr/bin/env python3
"""Combine all frozen, original 12-trait family×pair K comparisons after
comparing exactly identical species and phylogenetic trees within each pair.

Only descriptive science: no newly invented significance thresholds, adaptive
trait selection or process null refit. Paired taxon intersections differ among
different trait pairs and are NOT one global 12-trait ranking.
"""
from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path
from statistics import median
STATUS="AUSTRAITS_K_SHARED_TAXON_PAIR_COMPARISON_AUDITED"
INPUT="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
SUPPORT="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"

def audit_support_and_results(support:dict,batches:list[dict],design:dict):
    if design.get("status")!="POST_EMPIRICAL_K_AND_SOURCE_DIAGNOSTICS_PRE_SHARED_TAXON_OVERLAP_RESULTS_FROZEN":
        raise ValueError("design not frozen before source support")
    if support.get("status")!=SUPPORT or support.get("qualifying_family_trait_pairs")!=760:
        raise ValueError("missing original K-blind 760 paired-support graph")
    if len(support.get("trait_pairs",{}))!=66:
        raise ValueError("incomplete source-supported 12-trait pair types")
    qualified={
        (r["family"],r["trait_A"],r["trait_B"]):r
        for r in support["family_trait_pair_support"]
        if r["qualifies_20_common_species"]
    }
    if len(qualified)!=760:
        raise ValueError("not exactly 760 qualifying family×pair systems")
    result={}
    for batch in batches:
        if batch.get("status")!=INPUT or not batch.get("post_original_K_outcome_exploratory"):
            raise ValueError("invalid matched-source result provenance")
        if len(batch["pairs"])!=batch["n_family_trait_pairs"]:
            raise ValueError("incomplete batch output")
        for p in batch["pairs"]:
            key=(p["family"],p["trait_A"],p["trait_B"])
            if key not in qualified or key in result:
                raise ValueError("unexpected or duplicate same-species trait pair")
            ref=qualified[key]
            for k,k2 in [("system_A","system_A"),("system_B","system_B"),
                          ("n_shared_species","n_common_species_same_genus")]:
                if p[k]!=ref[k2]:raise ValueError("source-native shared-tip identity mismatch "+k)
            for axis in ("S3","prune_only"):
                d=p["axes"][axis]
                if d["status"]=="PASS":
                    if int(d["n_tips"])<20 or int(d["n_tips"])>p["n_shared_species"]:
                        raise ValueError("nonmatching tree tip support under paired K")
                    for name in ("K_A","K_B","delta_shared_logK",
                                 "delta_original_logK","delta_support_shift"):
                        if not math.isfinite(float(d[name])):
                            raise ValueError("nonfinite same-species K output")
                    if not math.isclose(math.log(d["K_A"]/d["K_B"]),
                                        d["delta_shared_logK"],abs_tol=2e-9):
                        raise ValueError("shared-tip K identity inconsistent")
                    if not math.isclose(d["delta_shared_logK"]-d["delta_original_logK"],
                                        d["delta_support_shift"],abs_tol=2e-9):
                        raise ValueError("support versus original K contrast inconsistent")
                elif not str(d["status"]).startswith("HOLD_"):
                    raise ValueError("unrecognized R tree hold status")
            result[key]=p
    if set(result)!=set(qualified):
        raise ValueError(f"incomplete matched original pair graph {len(result)}/760")
    types=defaultdict(list)
    allaxis={}
    for axis in ("S3","prune_only"):
        passrows=[r for r in result.values() if r["axes"][axis]["status"]=="PASS"]
        agreement=sum(r["axes"][axis]["delta_shared_logK"]*
                      r["axes"][axis]["delta_original_logK"]>0 for r in passrows)
        flips=sum(r["axes"][axis]["delta_shared_logK"]*
                  r["axes"][axis]["delta_original_logK"]<0 for r in passrows)
        for r in passrows:types[(r["trait_A"],r["trait_B"],axis)].append(r)
        allaxis[axis]={
            "n_supported_pairs":len(passrows),
            "n_axis_holds":760-len(passrows),
            "n_matched_versus_original_pair_sign_agreement":agreement,
            "n_matched_versus_original_pair_sign_reversals":flips,
            "n_pair_comparisons_with_ties_or_nearzero_reference":len(passrows)-agreement-flips,
            "sign_agreement_fraction_of_nonzero_contrasts":
                agreement/(agreement+flips) if agreement+flips>0 else None,
            "median_absolute_shared_logK_difference":
                float(median(abs(r["axes"][axis]["delta_shared_logK"]) for r in passrows))
                if passrows else None,
            "median_absolute_support_change_to_pair_difference":
                float(median(abs(r["axes"][axis]["delta_support_shift"]) for r in passrows))
                if passrows else None
        }
    pair_summaries={}
    for key,original in sorted(support["trait_pairs"].items()):
        a,b=original["trait_A"],original["trait_B"]
        z={k:original[k] for k in ("trait_A","trait_B","present_families","families_20_species","common_species_cells","qualifies_multi_family_descriptive_comparison")}
        z["axes"]={}
        for axis in ("S3","prune_only"):
            rr=types[(a,b,axis)]
            vals=[r["axes"][axis]["delta_shared_logK"] for r in rr]
            source=[r["axes"][axis]["delta_original_logK"] for r in rr]
            positive=sum(v>0 for v in vals)
            negative=sum(v<0 for v in vals)
            compare=sum(x*y>0 for x,y in zip(vals,source))
            flips=sum(x*y<0 for x,y in zip(vals,source))
            z["axes"][axis]={
                "n_family_pairs_with_valid_K":len(rr),
                "n_family_pairs_below_shared_tip_or_K_support":original["families_20_species"]-len(rr),
                "n_trait_A_higher_K":positive,
                "n_trait_B_higher_K":negative,
                "n_equal_or_nearzero":len(vals)-positive-negative,
                "median_shared_tip_delta_logK":float(median(vals)) if vals else None,
                "median_original_separate_tip_delta_logK":float(median(source)) if source else None,
                "n_matched_original_sign_agree":compare,
                "n_matched_original_sign_reverse":flips,
                "supports_five_family_generalization":len(vals)>=5
            }
        pair_summaries[key]=z
    if len(pair_summaries)!=66:
        raise ValueError("not 66 complete named-trait pairs")
    target=("seed_width","leaf_area","seed_dry_mass","leaf_width","petiole_length")
    target_pairs={
        key:pair_summaries[key] for key in pair_summaries
        if pair_summaries[key]["trait_A"] in target
           and pair_summaries[key]["trait_B"] in target
    }
    if len(target_pairs)!=10:
        raise ValueError("original five named predictions not contained in pair universe")
    return {
       "version":"v0.1","status":STATUS,
       "design_status":design["status"],"after_original_K_outcomes":True,
       "matched_source_graph":{"systems":249,"families":42,"traits":12,
                               "eligible_family_trait_pairs":760,"possible_trait_pairs":66},
       "axes":allaxis,"trait_pair_summaries":pair_summaries,
       "five_frozen_discovery_named_trait_pairs":target_pairs,
       "not_a_new_process_null":True,
       "external_independent_validation":False,
       "trait_values_or_species_ids_persisted":False,
       "scientific_boundary":"Pairwise shared species and trees isolate within-pair sampling geometry, but different pairs use different species sets; these results cannot demonstrate a universal shared 12-trait K rank, evolutionary constraint, selection or TRY data independence."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--batch-dir",required=True,type=Path)
    p.add_argument("--support",required=True,type=Path)
    p.add_argument("--design",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    batches=[json.loads(path.read_text()) for path in sorted(a.batch_dir.glob("*.json"))]
    if not batches:raise ValueError("no archive batch results")
    result=audit_support_and_results(json.loads(a.support.read_text()),batches,
                                      json.loads(a.design.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,
      "S3":result["axes"]["S3"],
      "prune_only":result["axes"]["prune_only"],
      "pair_types_generalizable":sum(v["qualifies_multi_family_descriptive_comparison"] for v in result["trait_pair_summaries"].values())},sort_keys=True))

if __name__=="__main__":main()
