#!/usr/bin/env python3
"""Archive a complete, verified original public-v7 142/101 equal-n pruning null.

This script is gated by CI success and NEVER downloads original raw species
phenotypes, specimen IDs, external TRY/GIFT traits, or changes paper's K.
"""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from run_austraits_original_nonflora_tip_loss_null_v0_1 import combine,NUM_BATCH,STATUS_FULL,SEED,DRAW_COUNT

SOURCE_RUN=43563549840
SOURCE_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
STATUS="PASS_DURABLE_ORIGINAL_142_101_FIXED_BROAD_TREE_SIZE_MATCHED_PRUNING_NULL_ARCHIVE"

def need(x,msg):
    if not x:raise AssertionError(msg)
def sha(x):return hashlib.sha256(x).hexdigest()

def go(plan,outcomes,original_final,dest,run):
    need(run==SOURCE_RUN,"Wrong completed source CI for original tip-loss null archive")
    need(plan.is_dir() and outcomes.is_dir() and original_final.is_file(),
         "Plan, all 12 results or independent final K null missing")
    expected_plan={f"P{i:02d}.json" for i in range(1,NUM_BATCH+1)}
    expected_plan.add("original_null_plan.json")
    expected_out={f"P{i:02d}_{kind}.json" for i in range(1,NUM_BATCH+1)
                  for kind in ("null","audit")}
    need({p.name for p in plan.glob("*.json")}==expected_plan,
         "Original family-balanced null plans not complete")
    need({p.name for p in outcomes.glob("*.json")}==expected_out,
         "All 12 original null K result and 12 independent audit files required")
    res=json.loads(original_final.read_text())
    need(res["status"]==STATUS_FULL and res["n_null_draws"]==DRAW_COUNT
         and res["null_seed"]==SEED and res["number_original_family_trait_pairs"]==142
         and res["original_prune_supported_pair_ids"]==101
         and res["original_source_parquet_SHA256"]==SOURCE_SHA
         and res["family_clustered_random_priority_across_overlapping_original_pairs"] is True
         and res["original_post_K_organ_grouping_and_selection_bias_unchanged"] is True
         and res["no_K_source_data_or_GIFT_or_TRY_raw_trait_measurements_exported"] is True,
         "Source-run global null not verified or inferences overstated")
    for axis,n,flips in (("S3",142,23),("prune_only",101,13)):
        z=res["axes"][axis]
        need(z["original_frozen_strict_K_pairs"]==n
             and z["original_historical_broad_to_strict_tree_rebuilt_K_flips"]==flips
             and z["null_draws"]==DRAW_COUNT
             and z["family_correlated_null_sampling_same_species_priorities_within_family"] is True
             and z["original_same_source_phenotype_values_and_broad_tree_kept_fixed"] is True
             and z["stage2_rebuilt_tree_not_equated_to_broad_tree_pruning"] is True
             and 0<=z["actual_strict_survivors_on_fixed_broad_tree_K_flips"]<=n,
             "Full original size-matched native K null failed independent archived check")
    dest.mkdir(parents=True,exist_ok=True)
    hashes={}
    for f in sorted(plan.glob("*.json")):
        target=dest/"plan"/f.name
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():need(target.read_bytes()==f.read_bytes(),"Revising prior original plan source "+f.name)
        else:shutil.copyfile(f,target)
        hashes["plan/"+f.name]=sha(target.read_bytes())
    for f in sorted(outcomes.glob("*.json")):
        target=dest/"results"/f.name
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():need(target.read_bytes()==f.read_bytes(),"Revising original tip pruning result "+f.name)
        else:shutil.copyfile(f,target)
        hashes["results/"+f.name]=sha(target.read_bytes())
    target=dest/"original_142_101_fixed_tree_tip_loss_null_verdict.json"
    if target.exists():need(target.read_bytes()==original_final.read_bytes(),
                            "Original null aggregate changed in archival path")
    else:shutil.copyfile(original_final,target)
    hashes[target.name]=sha(target.read_bytes())
    need(len(hashes)==38,"Unexpected number of saved original 142/101 null files")
    m={
     "status":STATUS,
     "original_full_tip_loss_null_CI_run_id":SOURCE_RUN,
     "original_data_release":"AusTraits v7.0.0",
     "original_parquet_sha256":SOURCE_SHA,
     "original_source_evolutionary_process_recomputed":False,
     "original_142_S3_pair_contexts":142,
     "original_101_prune_pair_contexts":101,
     "family_correlated_equal_n_random_subset_draws":DRAW_COUNT,
     "original_broad_tree_fixed_during_pruning":True,
     "original_nonflora_species_state_values_fixed":True,
     "original_stage2_native_tree_rebuilt_not_equated_to_subset_pruning":True,
     "all_12_family_K_null_batches_and_numerical_original_values_verified":True,
     "n_nonraw_K_null_outputs_preserved":len(hashes),
     "derived_files_SHA256":hashes,
     "independent_original_study_trait_measurement_replication":False,
     "post_original_K_hypothesis_selected":True,
     "no_raw_original_species_names_trait_measurements_or_dataset_records_preserved":True,
     "new_reproductive_vs_vegetative_K_effect_fit_or_K_source_selection":False,
     "explicit_author_submission_approval":False}
    fn=dest/"original_tip_loss_null_archive_manifest.json"
    msg=json.dumps(m,sort_keys=True,indent=2)+"\n"
    if fn.exists():need(fn.read_text()==msg,"Original permanent null manifest SHA drift")
    else:fn.write_text(msg)
    return m

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan-dir",type=Path,required=True)
    p.add_argument("--results-dir",type=Path,required=True)
    p.add_argument("--verdict",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--run-id",type=int,required=True)
    a=p.parse_args()
    m=go(a.plan_dir,a.results_dir,a.verdict,a.out_dir,a.run_id)
    print(json.dumps({"status":m["status"],"source_run":SOURCE_RUN,
                      "file_count":m["n_nonraw_K_null_outputs_preserved"]}))

if __name__=="__main__":main()
