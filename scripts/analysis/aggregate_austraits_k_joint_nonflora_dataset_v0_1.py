#!/usr/bin/env python3
"""Final original-source sensitivity across 142 K-blind family×organ pairs.

Remove five electronic Flora datasets; on exactly matched original eligible
taxa/trees, compare all remaining nonflora source medians to original values
from only identical remaining DatasetIDs. Bootstrap by whole plant family.

This is a POST-OUTCOME original AusTraits check, NOT new independent sources,
a phylogenetic rate estimator or natural-selection evidence.
"""
from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path
from statistics import median
import numpy as np

from run_austraits_k_joint_nonflora_dataset_batch_v0_1 import (
    cohort,STATUS as BATCH_STATUS)

STATUS="AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_SENSITIVITY_AGGREGATED_V0_1"
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
    if design.get("status")!="POST_AUSTRAITS_K_DISCOVERY_AND_FIVE_FLORA_K_PRE_JOINT_SOURCE_K_RESULTS_FROZEN":
        raise ValueError("original source-restricted family K study was not frozen")
    selected=cohort(source,original,design)
    original_index={(z["family"],z["trait_A"],z["trait_B"]):z for z in selected}
    seen={}
    for batch in batches:
        if (batch.get("status")!=BATCH_STATUS or not batch.get("joint_nonflora_and_identical_source_post_outcome_exploratory")
            or not batch.get("source_arm_semantics",{}).get("same_matched_taxa_and_native_phylogeny_for_both_source_arms")):
            raise ValueError("unknown nonflora-identical-DatasetID K batch provenance")
        if not batch.get("not_independent_primary_measurement_validation"):
            raise ValueError("original source analysis mislabelled independent")
        for row in batch.get("pairs",[]):
            key=(row["family"],row["trait_A"],row["trait_B"])
            if key in seen or key not in original_index:
                raise ValueError("unexpected/repeated K-selected same-source organ pair")
            prior=original_index[key]
            if (row["system_A"],row["system_B"])!=(prior["system_A"],prior["system_B"]):
                raise ValueError("K result has mutated pre-K source trait pair systems")
            if row["n_source_positive_dataset_common"]!=prior["n_same_AusTraits_dataset_species"]:
                raise ValueError("K result does not match original shared DatasetID cohort")
            if row["n_same_source_positive_species"]>prior["n_same_AusTraits_dataset_species"]:
                raise ValueError("same-source median species count exceeds source-eligible graph")
            if row["n_lost_after_source_median"]!=(
                  row["n_source_positive_dataset_common"]-row["n_same_source_positive_species"]):
                raise ValueError("source native median loss differs from initial feasibility")
            for ax in ("S3","prune_only"):
                d=row["axes"][ax]
                if d["status"]=="PASS":
                    if d["n_tips"]<20 or d["n_tips"]>row["n_same_source_positive_species"]:
                        raise ValueError("accepted K with insufficient original tree tips")
                    for k in ("K_full_A","K_full_B","K_source_A","K_source_B",
                              "delta_full","delta_source","delta_source_measurements"):
                        if not math.isfinite(float(d[k])):raise ValueError("nonfinite source K")
                    if min(d["K_full_A"],d["K_full_B"],d["K_source_A"],d["K_source_B"])<=0:
                        raise ValueError("nonpositive K output")
                    if not math.isclose(math.log(d["K_full_A"]/d["K_full_B"]),d["delta_full"],abs_tol=2e-9):
                        raise ValueError("wrong all-source same-tip pair K direction")
                    if not math.isclose(math.log(d["K_source_A"]/d["K_source_B"]),d["delta_source"],abs_tol=2e-9):
                        raise ValueError("wrong same-nonflora-dataset pair K direction")
                    if not math.isclose(d["delta_source"]-d["delta_full"],d["delta_source_measurements"],abs_tol=2e-9):
                        raise ValueError("wrong source-only measurement delta on matched tips")
                elif not str(d["status"]).startswith("HOLD_"):
                    raise ValueError("invalid pinned same-source species or tree HOLD label")
            seen[key]=row
    if set(seen)!=set(original_index):
        raise ValueError(f"missing K outcome for frozen 142 common-dataset source-eligible pairs: {len(seen)}/142")
    B=design["bootstrap"]["draws"]
    seed=design["bootstrap"]["seed"]
    if B!=5000 or seed!=20261017:raise ValueError("family bootstrap config was mutated")
    result={"version":"v0.1","status":STATUS,
       "original_source_blind_pair_universe":760,
       "original_cross_organ_pairs":406,
       "joint_nonflora_source_qualified_before_K_pairs":142,
       "original_joint_source_qualified_families":24,
       "after_original_K_and_organ_discovery":True,
       "prior_source_blind_eligibility_before_this_joint_K":True,
       "source_arm_semantics":{"all_nonflora_sources_same_tips":"Medians from every remaining original AusTraits dataset except five electronic Floras","identical_nonflora_dataset_same_tips":"Medians from only a remaining DatasetID shared by both organs on the same species","species_and_native_tree_fixed_between_source_arms":True},
       "identical_nonflora_dataset_id_does_not_prove_same_primary_specimen":True,
       "not_external_TRY_v7_independent_source_validation":True,
       "axes":{},
       "hard_nonclaims":[
          "Source-composition-only effects are estimated on the same native taxon tips and tree WITHIN each source-qualified pair. Family/trait pair membership was already selected by source availability before K re-estimation.",
          "A common dataset_id may contain compiled datasets and distinct protocols; it is not guaranteed to identify a shared physical specimen or independent primary origin.",
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
                         "n_source_species":row["n_same_source_positive_species"]})
                continue
            af=row["trait_A"] in REPRO
            bf=row["trait_B"] in REPRO
            if af==bf:raise ValueError("source-restricted organ pair no longer cross-organ")
            sign=1 if af else -1
            df=sign*float(d["delta_full"])
            ds=sign*float(d["delta_source"])
            scored.append({
              "family":row["family"],"trait_A":row["trait_A"],"trait_B":row["trait_B"],
              "n_same_source_species":row["n_same_source_positive_species"],
              "n_native_tree_tips":int(d["n_tips"]),
              "delta_all_nonflora_sources":df,"delta_identical_nonflora_dataset":ds,"delta_measurement_only":ds-df,
              "reproductive_K_higher_all_nonflora_medians":int(df>0),
              "reproductive_K_higher_identical_nonflora_dataset_medians":int(ds>0),
              "sign_reversal_due_to_measurement_source":int(df*ds<0),
              "subtype":"seed_vs_vegetative" if row["trait_A"].startswith("seed_") or row["trait_B"].startswith("seed_") else "fruit_vs_vegetative"
            })
        if len(scored)+len(holds)!=142:raise ValueError("source K all prequalified pairs not adjudicated")
        min_families=design["decision_boundary"]["min_source_qualified_families_for_pooled_exploratory_reporting"]
        min_sub=min(design["decision_boundary"]["min_fruit_vs_vegetative_families"],
                    design["decision_boundary"]["min_seed_vs_vegetative_families"])
        families={x["family"] for x in scored}
        fruit=[x for x in scored if x["subtype"]=="fruit_vs_vegetative"]
        seedonly=[x for x in scored if x["subtype"]=="seed_vs_vegetative"]
        supported=(len(families)>=min_families and
           len({x["family"] for x in fruit})>=min_sub and
           len({x["family"] for x in seedonly})>=min_sub)
        summary={
           "n_preK_source_qualified_pairs":142,
           "n_valid_real_tree_K_pairs":len(scored),
           "n_species_median_or_phylo_K_holds":len(holds),
           "n_families_valid":len(families),
           "passes_descriptive_minimum_family_support":bool(supported),
           "n_nonflora_dataset_alignment_K_sign_flips":int(sum(x["sign_reversal_due_to_measurement_source"] for x in scored)),
           "fraction_nonflora_dataset_alignment_K_sign_flips":
                float(np.mean([x["sign_reversal_due_to_measurement_source"] for x in scored])) if scored else None,
           "same_nonflora_dataset_change_in_cross_organ_logK_median":
                float(median(x["delta_measurement_only"] for x in scored)) if scored else None,
           "same_nonflora_dataset_change_in_cross_organ_logK_mean":
                float(np.mean([x["delta_measurement_only"] for x in scored])) if scored else None,
           "all_nonflora_sources_same_tips":_family_rate(scored,"reproductive_K_higher_all_nonflora_medians",B,seed+ia) if scored else None,
           "identical_nonflora_dataset_same_tips":_family_rate(scored,"reproductive_K_higher_identical_nonflora_dataset_medians",B,seed+ia+2) if scored else None,
           "same_nonflora_dataset_alignment_sign_reversals":_family_rate(scored,"sign_reversal_due_to_measurement_source",B,seed+ia+4) if scored else None,
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
                "all_nonflora_source_reproductive_K_higher_fraction":
                     float(np.mean([x["reproductive_K_higher_all_nonflora_medians"] for x in xx])) if xx else None,
                "identical_nonflora_dataset_reproductive_K_higher_fraction":
                     float(np.mean([x["reproductive_K_higher_identical_nonflora_dataset_medians"] for x in xx])) if xx else None,
                "n_measurement_only_K_sign_flips":
                     int(sum(x["sign_reversal_due_to_measurement_source"] for x in xx))
            }
        for family in sorted(families):
            xs=[x for x in scored if x["family"]==family]
            summary["individual_families"][family]={
               "n_valid_pairs":len(xs),
               "n_reproductive_win_all_nonflora_sources":sum(x["reproductive_K_higher_all_nonflora_medians"] for x in xs),
               "n_reproductive_win_identical_nonflora_dataset":sum(x["reproductive_K_higher_identical_nonflora_dataset_medians"] for x in xs),
               "n_measurement_only_sign_flips":sum(x["sign_reversal_due_to_measurement_source"] for x in xs),
               "min_same_dataset_species":min(x["n_same_source_species"] for x in xs)}
        result["axes"][axis]=summary
    # On both tree axes where full/restricted-source K is successfully
    # identified; check whether the same-source organ winner agrees.
    A={(x["family"],x["trait_A"],x["trait_B"]):x for x in result["axes"]["S3"]["pair_level_K_decisions_no_species_names"]}
    P={(x["family"],x["trait_A"],x["trait_B"]):x for x in result["axes"]["prune_only"]["pair_level_K_decisions_no_species_names"]}
    both=set(A)&set(P)
    result["two_tree_joint_source_effect"]={
      "n_pairs_native_K_supported_on_both":len(both),
      "n_reproductive_higher_in_common_dataset_on_both":sum(
         A[k]["reproductive_K_higher_identical_nonflora_dataset_medians"] and
         P[k]["reproductive_K_higher_identical_nonflora_dataset_medians"] for k in both),
      "n_vegetative_higher_in_common_dataset_on_both":sum(
         not A[k]["reproductive_K_higher_identical_nonflora_dataset_medians"] and
         not P[k]["reproductive_K_higher_identical_nonflora_dataset_medians"] for k in both),
      "n_native_tree_discordant_common_dataset_winner":sum(
         A[k]["reproductive_K_higher_identical_nonflora_dataset_medians"]!=
         P[k]["reproductive_K_higher_identical_nonflora_dataset_medians"] for k in both)
    }
    return result

def main():
    p=argparse.ArgumentParser()
    for nm in ("batch-dir","source-support","original-pair-support","design","out"):
        p.add_argument("--"+nm,required=True,type=Path)
    args=p.parse_args()
    reports=[json.loads(f.read_text()) for f in
             sorted(args.__dict__["batch_dir"].glob("B*.json"))]
    if len(reports)!=12:
        raise ValueError("not all 12 pinned same-nonflora-source organ K batches returned")
    d=json.loads(args.design.read_text())
    source=json.loads(args.__dict__["source_support"].read_text())
    orig=json.loads(args.__dict__["original_pair_support"].read_text())
    result=calculate(source,orig,d,reports)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({axis:{
      "n":result["axes"][axis]["n_valid_real_tree_K_pairs"],
      "matched_dataset_reproductive_rate":result["axes"][axis]["identical_nonflora_dataset_same_tips"]["pair_weighted_rate"],
      "full_source_reproductive_rate":result["axes"][axis]["all_nonflora_sources_same_tips"]["pair_weighted_rate"],
      "sign_flips":result["axes"][axis]["n_nonflora_dataset_alignment_K_sign_flips"]}
      for axis in ("S3","prune_only")},indent=2))
if __name__=="__main__":main()
