#!/usr/bin/env python3
"""Posthoc descriptive meta-context of the ORIGINAL 142/101 K fixed-tree null.

This is NOT a confirmatory hypothesis, new independent primary measurement,
new phylogenetic K fitting or causal mechanism identification. It only audits
already frozen 128-rank family-correlated source-specific K null results.
"""
from __future__ import annotations
import argparse,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path("results/austraits_organ_paper_public_v7_tip_loss_null_v0_1")
STATUS="PASS_SOURCE_FIXED_142_101_TIP_LOSS_NULL_PD_STATURE_AND_TREE_REBUILD_DESCRIPTION"
REPRODUCTIVE={"fruit_height","fruit_length","fruit_width","seed_dry_mass","seed_length","seed_width"}

def need(x,msg):
    if not x:raise AssertionError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def med(x):
    valid=[v for v in x if v is not None and math.isfinite(v)]
    return statistics.median(valid) if valid else None
def value_ref(z,ax):
    x=z["axes"][ax]
    if x["status"]!="PASS":return None
    a=x["baseline_logK_contrast"]
    b=x["actual_strict_survivors_logK_on_fixed_broad_tree"]
    c=x["historical_stage2_rebuilt_logK_contrast"]
    rep=(z["trait_A"] if z["trait_A"] in REPRODUCTIVE else z["trait_B"])
    veg=(z["trait_B"] if z["trait_A"] in REPRODUCTIVE else z["trait_A"])
    return {"family":z["family"],"reproductive_trait":rep,
            "vegetative_trait":veg,
            "baseline_sign":int(a>0),
            "historical_rebuilt_strict_sign":int(c>0),
            "actual_broad_pruned_strict_sign":int(b>0),
            "original_historical_tree_remake_minus_broad_prune":c-b,
            "original_historical_broad_to_strict_flip":int((a>0)!=(c>0)),
            "actual_fixed_tree_broad_to_strict_flip":x["actual_strict_survivor_flip_on_fixed_broad_tree"],
            "random_equal_n_flip_rate":x["null_K_sign_flip_probability"],
            "actual_PD_fraction":x["actual_survivor_PD_fraction_of_broad_tree"],
            "random_PD_mean":x["random_tree_PD_fraction_of_broad_tree"]["mean"],
            "random_PD_q025":x["random_tree_PD_fraction_of_broad_tree"]["q025"],
            "random_PD_q975":x["random_tree_PD_fraction_of_broad_tree"]["q975"],
            "empirical_per_pair_source_change_tail":x["empirical_null_tail_prob_abs_delta_shift"],
            "n_baseline_native_tips":x["n_baseline_tips"],
            "n_survivor_native_tips":x["n_actual_strict_tips"]}

def run(output):
    manifest=json.loads((ROOT/"original_tip_loss_null_archive_manifest.json").read_text())
    need(manifest["status"]==
         "PASS_DURABLE_ORIGINAL_142_101_FIXED_BROAD_TREE_SIZE_MATCHED_PRUNING_NULL_ARCHIVE"
         and manifest["n_nonraw_K_null_outputs_preserved"]==38,
         "Full original fixed-tree K source null archive missing")
    for f,d in manifest["derived_files_SHA256"].items():
        p=ROOT/f
        need(p.is_file() and sha(p.read_bytes())==d,
             "Original K source null SHA mismatch: "+f)
    full=json.loads((ROOT/"original_142_101_fixed_tree_tip_loss_null_verdict.json").read_text())
    need(full["status"]=="PASS_ORIGINAL_142_101_BROAD_TREE_FIXED_SIZE_MATCHED_TIP_LOSS_NULL"
         and full["n_null_draws"]==128
         and full["n_original_family_clusters"]==24
         and full["n_rejected_candidate_family_rank_draws_due_to_undefined_K"]==4
         and full["n_total_candidate_family_rank_draws"]==3076,
         "Original family-conditional random pruning K global evidence changed")
    items=[]
    for i in range(1,13):
        p=ROOT/"results"/f"P{i:02d}_null.json"
        o=json.loads(p.read_text())
        need(o["status"]=="PASS_ORIGINAL_142_TIP_LOSS_FROZEN_BROAD_TREE_NULL_BATCH"
             and o["null_inference_conditioned_on_phylogenetic_K_estimable_in_every_family_pair"] is True,
             "Random K source null batch not valid")
        items+=o["pairs"]
    need(len(items)==142 and len({(x["family"],x["trait_A"],x["trait_B"]) for x in items})==142,
         "Original 142 K pair identities not present")
    result={}
    for ax,n,expected_actual in (("S3",142,23),("prune_only",101,13)):
        d=[r for z in items if (r:=value_ref(z,ax)) is not None]
        need(len(d)==n,"Original native K supported comparison count changed")
        actual=sum(x["actual_fixed_tree_broad_to_strict_flip"] for x in d)
        original=sum(x["original_historical_broad_to_strict_flip"] for x in d)
        need(actual==original==expected_actual,
             "Actual source survivors and original reported K sign reversals differed")
        mismatch=[x for x in d if x["historical_rebuilt_strict_sign"]!=x["actual_broad_pruned_strict_sign"]]
        diffs=[abs(x["original_historical_tree_remake_minus_broad_prune"]) for x in d]
        h=[x for x in d if x["vegetative_trait"]=="plant_height"]
        nh=[x for x in d if x["vegetative_trait"]!="plant_height"]
        pd_low=[x for x in d if x["actual_PD_fraction"]<x["random_PD_q025"]]
        pd_high=[x for x in d if x["actual_PD_fraction"]>x["random_PD_q975"]]
        family=defaultdict(lambda:{"n":0,"actual":0,"expected":0.0})
        for x in d:
            a=family[x["family"]]
            a["n"]+=1;a["actual"]+=x["actual_fixed_tree_broad_to_strict_flip"]
            a["expected"]+=x["random_equal_n_flip_rate"]
        family_out=[{"family":f,"n_original_pairs":v["n"],
                     "actual_fixed_tree_flips":v["actual"],
                     "expected_random_equal_n_flips":v["expected"],
                     "excess_vs_size_matched_random":v["actual"]-v["expected"]}
                    for f,v in family.items()]
        family_out.sort(key=lambda x:-x["excess_vs_size_matched_random"])
        result[ax]={
          "original_eligible_family_trait_pair_ids":n,
          "n_original_historical_stage1_to_stage2_K_flips":original,
          "n_actual_fixed_broad_tree_strict_survivor_K_flips":actual,
          "n_original_strict_rebuilt_tree_vs_fixed_broad_pruned_tree_sign_disagreements":len(mismatch),
          "max_abs_original_stage2_strict_rebuilt_minus_broad_prune_logK":
              max(diffs),
          "median_abs_original_stage2_strict_rebuilt_minus_broad_prune_logK":
              med(diffs),
          "n_actual_retained_phylogenetic_branch_length_below_random_2point5percent":len(pd_low),
          "n_actual_retained_phylogenetic_branch_length_above_random_97point5percent":len(pd_high),
          "n_actual_flip_pairs_with_PD_below_random_2point5percent":
              sum(x["actual_fixed_tree_broad_to_strict_flip"] for x in pd_low),
          "plant_height_context":{
              "n_original_pairs":len(h),
              "actual_flip_count":sum(x["actual_fixed_tree_broad_to_strict_flip"] for x in h),
              "expected_equal_n_random_flip_count":sum(x["random_equal_n_flip_rate"] for x in h)},
          "other_vegetative_trait_context":{
              "n_original_pairs":len(nh),
              "actual_flip_count":sum(x["actual_fixed_tree_broad_to_strict_flip"] for x in nh),
              "expected_equal_n_random_flip_count":sum(x["random_equal_n_flip_rate"] for x in nh)},
          "n_per_pair_source_shift_tail_prob_0point05_or_smaller":
              sum(x["empirical_per_pair_source_change_tail"]<=0.05 for x in d),
          "n_actual_flip_pairs_with_per_pair_source_shift_tail_prob_0point05_or_smaller":
              sum(x["actual_fixed_tree_broad_to_strict_flip"] and
                  x["empirical_per_pair_source_change_tail"]<=0.05 for x in d),
          "original_family_clusters":len(family),
          "top_family_excess_flips_over_size_matched_null":family_out[:12],
          "original_source_sensitivity_and_family_trait_pair_reuse_posthoc":True
        }
    need(result["S3"]["n_original_strict_rebuilt_tree_vs_fixed_broad_pruned_tree_sign_disagreements"]==0
         and result["prune_only"]["n_original_strict_rebuilt_tree_vs_fixed_broad_pruned_tree_sign_disagreements"]==0,
         "Same original strict K reinserted source tree differs from broad-tree actual survivor pruning")
    output.parent.mkdir(parents=True,exist_ok=True)
    report={
      "status":STATUS,
      "original_source_sha256":sha((ROOT/"original_tip_loss_null_archive_manifest.json").read_bytes()),
      "source_original_142_101_K_null_CI_run":43564505854,
      "archive_CI_run":43565522112,
      "phylogenetic_axes":result,
      "null_draws_family_correlated":128,
      "family_candidates_tested_for_valid_K":3076,
      "family_candidates_rejected_for_undefined_K":4,
      "original_plant_traits_and_broad_native_tree_fixed":True,
      "source_survivors_clustering_PD_outside_null_only_descriptive":True,
      "posthoc_subgroup_plant_height_not_preregistered":True,
      "posthoc_multiple_testing_correction_not_performed":True,
      "two_trees_and_repeated_trait_pairs_not_independent":True,
      "GIFT_woodiness_does_not_equal_direct_biomass":True,
      "real_phylogenetic_original_data_repeated_not_new_independent_biology":True,
      "new_phylogenetic_K_fits_in_this_summary":0,
      "raw_species_trait_measurements_dataset_rows_exported":False,
      "human_journal_submission_approval_given":False
    }
    output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":STATUS,"axes":{
      a:{"n":z["original_eligible_family_trait_pair_ids"],
          "actual":z["n_actual_fixed_broad_tree_strict_survivor_K_flips"],
          "reconstructed_strict_vs_pruned_original_tree_sign_disagreements":
             z["n_original_strict_rebuilt_tree_vs_fixed_broad_pruned_tree_sign_disagreements"],
          "max_abs_tree_geometry_K_change":z["max_abs_original_stage2_strict_rebuilt_minus_broad_prune_logK"],
          "PD_below_random_2point5percent":
             z["n_actual_retained_phylogenetic_branch_length_below_random_2point5percent"],
          "height":z["plant_height_context"]}
      for a,z in result.items()}},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.out)
