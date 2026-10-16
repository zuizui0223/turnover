#!/usr/bin/env python3
"""Reconcile 283 K-blind selected original organ comparisons re-estimated on
same-species, same-tree, and records except five preselected electronic flora DatasetIDs.

Report SAME TAXA full-source median vs five-flora-excluded median arms in
parallel. 5,000 family bootstraps preserve within-family pairing. This is an
original AusTraits POST-OUTCOME robustness diagnostic, never independent TRY
validation, a process model, selection, or evolutionary speed inference.
"""
from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path
from statistics import median
import numpy as np

from run_austraits_k_five_flora_exclusion_batch_v0_1 import (
    cohort,validate_result, BATCH_STATUS)

STATUS="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_ORGAN_SENSITIVITY_AGGREGATED_V0_1"
REPRO={"fruit_height","fruit_length","fruit_width",
       "seed_dry_mass","seed_length","seed_width"}

def _family_rate(rows,field,B,seed):
    if not rows:return None
    fam=sorted({x["family"] for x in rows})
    v=np.array([[sum(x[field] for x in rows if x["family"]==f),
                 sum(x["family"]==f for x in rows)] for f in fam],float)
    if np.any(v[:,1]==0):raise ValueError("empty original plant family")
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(fam),(B,len(fam)))
    z=v[idx].sum(axis=1)
    pair_rate=z[:,0]/z[:,1]
    fam_mean=(v[:,0]/v[:,1])[idx].mean(axis=1)
    return {
      "n_valid_individual_family_pairs":len(rows),
      "n_distinct_plant_families":len(fam),
      "positive_comparisons":int(sum(x[field] for x in rows)),
      "pair_weighted_rate":float(sum(x[field] for x in rows)/len(rows)),
      "family_bootstrap_pair_rate_CI95":list(map(float,np.quantile(pair_rate,[.025,.975]))),
      "equal_family_mean_rate":float(np.mean(v[:,0]/v[:,1])),
      "family_bootstrap_equal_family_rate_CI95":list(map(float,np.quantile(fam_mean,[.025,.975])))
    }

def calculate(source,original,design,batches):
    if design.get("status")!="POST_279_K_AND_FLORA_LINEAGE_OUTCOMES_PRE_FLORA_EXCLUSION_SUPPORT_COUNTS_FROZEN":
        raise ValueError("original source-restricted family K study was not frozen")
    selected=cohort(source,original,design)
    original_index={(z["family"],z["trait_A"],z["trait_B"]):z for z in selected}
    seen={}
    for batch in batches:
        if batch.get("status")!=BATCH_STATUS or not batch.get("post_organ_and_760_K_outcome_source_robustness"):
            raise ValueError("unknown five-flora-exclusion K batch provenance")
        if not batch.get("NOT_independent_primary_measurement_validation"):
            raise ValueError("original source analysis mislabelled independent")
        for row in batch.get("pairs",[]):
            key=(row["family"],row["trait_A"],row["trait_B"])
            if key in seen or key not in original_index:
                raise ValueError("unexpected/repeated K-selected five-flora-excluded organ pair")
            prior=original_index[key]
            if (row["system_A"],row["system_B"])!=(prior["system_A"],prior["system_B"]):
                raise ValueError("K result has mutated pre-K source trait pair systems")
            if row["n_initial_nonflora_positive_median_species"]!=prior["n_nonflora_positive_median_shared_species"]:
                raise ValueError("K result does not match original frozen 283-pair nonflora-positive median cohort")
            if row["n_nonflora_positive_species"]>prior["n_nonflora_positive_median_shared_species"]:
                raise ValueError("five-flora-excluded median species count exceeds source-eligible graph")
            if row["n_lost_after_source_median"]!=(
                  row["n_initial_nonflora_positive_median_species"]-row["n_nonflora_positive_species"]):
                raise ValueError("source native median loss differs from initial feasibility")
            for ax in ("S3","prune_only"):
                d=row["axes"][ax]
                if d["status"]=="PASS":
                    if d["n_tips"]<20 or d["n_tips"]>row["n_nonflora_positive_species"]:
                        raise ValueError("accepted K with insufficient original tree tips")
                    for k in ("K_full_A","K_full_B","K_source_A","K_source_B",
                              "delta_full","delta_source","delta_source_measurements"):
                        if not math.isfinite(float(d[k])):raise ValueError("nonfinite source K")
                    if min(d["K_full_A"],d["K_full_B"],d["K_source_A"],d["K_source_B"])<=0:
                        raise ValueError("nonpositive K output")
                    if not math.isclose(math.log(d["K_full_A"]/d["K_full_B"]),d["delta_full"],abs_tol=2e-9):
                        raise ValueError("wrong all-source same-tip pair K direction")
                    if not math.isclose(math.log(d["K_source_A"]/d["K_source_B"]),d["delta_source"],abs_tol=2e-9):
                        raise ValueError("wrong five-flora-excluded pair K direction")
                    if not math.isclose(d["delta_source"]-d["delta_full"],d["delta_source_measurements"],abs_tol=2e-9):
                        raise ValueError("wrong source-exclusion-only measurement delta on matched tips")
                elif not str(d["status"]).startswith("HOLD_"):
                    raise ValueError("invalid pinned five-flora-excluded species or tree HOLD label")
            seen[key]=row
    if set(seen)!=set(original_index):
        raise ValueError(f"missing K outcome for frozen 283 common-dataset source-eligible pairs: {len(seen)}/283")
    B=design["reporting"]["family_cluster_bootstrap_draws"]
    seed=design["reporting"]["seed"]
    if B!=5000 or seed!=20261015:raise ValueError("family bootstrap config was mutated")
    result={"version":"v0.1","status":STATUS,
       "original_source_blind_pair_universe":760,
       "original_cross_organ_pairs":406,
       "nonflora_supported_before_K_pairs":283,
       "original_nonflora_supported_families":29,
       "after_original_K_and_organ_discovery":True,
       "remaining_AusTraits_source_IDs_not_independent_primary_measurements":True,
       "not_external_TRY_v7_independent_source_validation":True,
       "axes":{},
       "hard_nonclaims":[
          "Source-composition-only effects are estimated on the same native taxon tips and tree WITHIN each source-qualified pair. Family/trait pair membership was already selected by source availability before K re-estimation.",
          "A excluded-flora source medians_id may contain compiled datasets and distinct protocols; it is not guaranteed to identify a shared physical specimen or independent primary origin.",
          "Source-qualified subset selection and differential trait measurement protocols can themselves bias direction; family/bootstrap intervals are descriptive within AusTraits.",
          "Original post-outcome organ grouping has no external independent empirical validation and cannot identify evolutionary selection or alpha.",
          "The signed pair sets are not a global 12-trait ranking. Closed BIEN rho study not reopened."]}
    for ia,axis in enumerate(("S3","prune_only")):
        scored=[];holds=[]
        for key,row in sorted(seen.items()):
            d=row["axes"][axis]
            if d["status"]!="PASS":
                holds.append({"family":row["family"],"trait_A":row["trait_A"],
                         "trait_B":row["trait_B"],"status":d["status"],
                         "n_source_species":row["n_nonflora_positive_species"]})
                continue
            af=row["trait_A"] in REPRO
            bf=row["trait_B"] in REPRO
            if af==bf:raise ValueError("source-restricted organ pair no longer cross-organ")
            sign=1 if af else -1
            df=sign*float(d["delta_full"])
            ds=sign*float(d["delta_source"])
            scored.append({
              "family":row["family"],"trait_A":row["trait_A"],"trait_B":row["trait_B"],
              "n_same_source_species":row["n_nonflora_positive_species"],
              "n_native_tree_tips":int(d["n_tips"]),
              "delta_full":df,"delta_shared_dataset":ds,"delta_measurement_only":ds-df,
              "reproductive_K_higher_full_medians":int(df>0),
              "reproductive_K_higher_nonflora_medians":int(ds>0),
              "sign_reversal_due_to_measurement_source":int(df*ds<0),
              "subtype":"seed_vs_vegetative" if row["trait_A"].startswith("seed_") or row["trait_B"].startswith("seed_") else "fruit_vs_vegetative"
            })
        if len(scored)+len(holds)!=283:raise ValueError("source K all prequalified pairs not adjudicated")
        min_families=design["eligibility_and_stop"]["minimum_independent_families_for_pooled_cross_organ_summary"]
        min_sub=design["eligibility_and_stop"]["minimum_families_fruit_and_seed_separately"]
        families={x["family"] for x in scored}
        fruit=[x for x in scored if x["subtype"]=="fruit_vs_vegetative"]
        seedonly=[x for x in scored if x["subtype"]=="seed_vs_vegetative"]
        supported=(len(families)>=min_families and
           len({x["family"] for x in fruit})>=min_sub and
           len({x["family"] for x in seedonly})>=min_sub)
        summary={
           "n_preK_nonflora_qualified_pairs":283,
           "n_valid_real_tree_K_pairs":len(scored),
           "n_nonflora_median_or_phylo_K_holds":len(holds),
           "n_families_valid":len(families),
           "passes_descriptive_minimum_family_support":bool(supported),
           "n_five_flora_source_removal_sign_flips":int(sum(x["sign_reversal_due_to_measurement_source"] for x in scored)),
           "fraction_five_flora_source_removal_sign_flips":
                float(np.mean([x["sign_reversal_due_to_measurement_source"] for x in scored])) if scored else None,
           "five_flora_removal_change_in_cross_organ_logK_median":
                float(median(x["delta_measurement_only"] for x in scored)) if scored else None,
           "five_flora_removal_change_in_cross_organ_logK_mean":
                float(np.mean([x["delta_measurement_only"] for x in scored])) if scored else None,
           "full_sources_same_tips":_family_rate(scored,"reproductive_K_higher_full_medians",B,seed+ia) if scored else None,
           "nonflora_source_same_tips":_family_rate(scored,"reproductive_K_higher_nonflora_medians",B,seed+ia+2) if scored else None,
           "source_only_K_sign_reversals":_family_rate(scored,"sign_reversal_due_to_measurement_source",B,seed+ia+4) if scored else None,
           "subtypes":{},
           "individual_families":{},
           "pair_level_K_decisions_no_species_names":scored,
           "axis_specific_holds":holds
        }
        for name,xx in (("fruit_vs_vegetative",fruit),
                        ("seed_vs_vegetative",seedonly),
                        ("excluding_seed_dry_mass",[x for x in scored if
                           "seed_dry_mass" not in (x["trait_A"],x["trait_B"])])):
            summary["subtypes"][name]={
                "n_valid_pairs":len(xx),
                "n_plant_families":len({x["family"] for x in xx}),
                "full_source_reproductive_K_higher_fraction":
                     float(np.mean([x["reproductive_K_higher_full_medians"] for x in xx])) if xx else None,
                "nonflora_reproductive_K_higher_fraction":
                     float(np.mean([x["reproductive_K_higher_nonflora_medians"] for x in xx])) if xx else None,
                "n_measurement_only_K_sign_flips":
                     int(sum(x["sign_reversal_due_to_measurement_source"] for x in xx))
            }
        for family in sorted(families):
            xs=[x for x in scored if x["family"]==family]
            summary["individual_families"][family]={
               "n_valid_pairs":len(xs),
               "n_reproductive_win_full_source":sum(x["reproductive_K_higher_full_medians"] for x in xs),
               "n_reproductive_win_nonflora":sum(x["reproductive_K_higher_nonflora_medians"] for x in xs),
               "n_measurement_only_sign_flips":sum(x["sign_reversal_due_to_measurement_source"] for x in xs),
               "min_nonflora_species":min(x["n_same_source_species"] for x in xs)}
        result["axes"][axis]=summary
    # On both tree axes where full/restricted-source K is successfully
    # identified; check whether the five-flora-excluded organ winner agrees.
    A={(x["family"],x["trait_A"],x["trait_B"]):x for x in result["axes"]["S3"]["pair_level_K_decisions_no_species_names"]}
    P={(x["family"],x["trait_A"],x["trait_B"]):x for x in result["axes"]["prune_only"]["pair_level_K_decisions_no_species_names"]}
    both=set(A)&set(P)
    result["two_tree_joint_source_effect"]={
      "n_pairs_native_K_supported_on_both":len(both),
      "n_reproductive_higher_in_nonflora_on_both":sum(
         A[k]["reproductive_K_higher_nonflora_medians"] and
         P[k]["reproductive_K_higher_nonflora_medians"] for k in both),
      "n_vegetative_higher_in_nonflora_on_both":sum(
         not A[k]["reproductive_K_higher_nonflora_medians"] and
         not P[k]["reproductive_K_higher_nonflora_medians"] for k in both),
      "n_native_tree_discordant_nonflora_winner":sum(
         A[k]["reproductive_K_higher_nonflora_medians"]!=
         P[k]["reproductive_K_higher_nonflora_medians"] for k in both)
    }
    return result

def main():
    p=argparse.ArgumentParser()
    for nm in ("batch-dir","source-support","original-pair-support","design","out"):
        p.add_argument("--"+nm,required=True,type=Path)
    args=p.parse_args()
    reports=[json.loads(f.read_text()) for f in
             sorted(args.__dict__["batch_dir"].glob("B*.json"))]
    if len(reports)!=16:
        raise ValueError("not all 16 pinned five-flora-excluded organ K batches returned")
    d=json.loads(args.design.read_text())
    source=json.loads(args.__dict__["source_support"].read_text())
    orig=json.loads(args.__dict__["original_pair_support"].read_text())
    result=calculate(source,orig,d,reports)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({axis:{
      "n":result["axes"][axis]["n_valid_real_tree_K_pairs"],
      "matched_dataset_reproductive_rate":result["axes"][axis]["nonflora_source_same_tips"]["pair_weighted_rate"],
      "full_source_reproductive_rate":result["axes"][axis]["full_sources_same_tips"]["pair_weighted_rate"],
      "sign_flips":result["axes"][axis]["n_five_flora_source_removal_sign_flips"]}
      for axis in ("S3","prune_only")},indent=2))
if __name__=="__main__":main()
