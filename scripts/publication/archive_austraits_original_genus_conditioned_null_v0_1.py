#!/usr/bin/env python3
"""Durable source-only original 142/101 genus-conditioned phylogenetic K null.

Only after original full 12 family-batch+final CI success. Retain original
source input and original K/phenotypes fixed; persist NO species/genus identities,
specimen observations, trait values, original raw data or new biological claims.
"""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from audit_austraits_original_genus_conditioned_tip_loss_null_v0_1 import STATUS as FINAL_STATUS

RUN=43566577755
SRC="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
STATUS="PASS_DURABLE_ORIGINAL_142_101_GENUS_QUOTA_FIXED_TREE_K_NULL_REPLAY_V0_1"

def need(ok,msg):
    if not ok:raise AssertionError(msg)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--run-id",required=True,type=int)
    p.add_argument("--plan-dir",required=True,type=Path)
    p.add_argument("--results-dir",required=True,type=Path)
    p.add_argument("--verdict",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    need(a.run_id==RUN,"Wrong original full source genus-conditioned K run")
    plan={f"P{i:02d}.json" for i in range(1,13)}
    plan.add("original_null_plan.json")
    outputs={f"P{i:02d}_{suffix}.json" for i in range(1,13)
             for suffix in ("genus_null","audit")}
    need({z.name for z in a.plan_dir.glob("*.json")}==plan and
         {z.name for z in a.results_dir.glob("*.json")}==outputs,
         "Not original 12 source cohort and 24 genus K null outputs")
    final=json.loads(a.verdict.read_text())
    need(final["status"]==FINAL_STATUS
         and final["original_public_v7_source_parquet_sha256"]==SRC
         and final["original_pair_identities"]==142
         and final["original_native_prune_supported_pair_identities"]==101
         and final["number_frozen_family_batches"]==12
         and final["number_family_correlated_replicates"]==128
         and final["original_family_wide_random_rank_seed"]==20261114
         and final["genus_quota_actual_strict_survivors_fixed_for_each_original_pair"] is True
         and final["original_broad_tree_and_original_phenotype_values_fixed"] is True
         and final["original_source_species_names_or_raw_trait_measurements_exported"] is False
         and final["conditional_descriptive_not_preregistered_multiple_hypothesis_test"] is True
         and final["genus_quota_conditioning_cannot_identify_mechanistic_causality"] is True,
         "Final source-genus-conditioned null is not a successful independent original-data audit")
    for axis,n,flips in (("S3",142,23),("prune_only",101,13)):
        z=final["genus_conditioned_AusTraits_Rcpp_native_K_derived_results"][axis]
        need(z["n_same_original_K_pair_identities"]==n
             and z["source_survivor_fixed_broad_tree_flips"]==flips
             and z["original_source_phylogeny_broad_tree_kept_fixed_and_original_K_unchanged"] is True
             and 0<=z["genus_quota_preserved_empirical_upper_tail_probability"]<=1,
             "Original native source K or genus null counts not frozen")
    target=a.out_dir
    target.mkdir(parents=True,exist_ok=True)
    fingerprint={}
    for folder,src,items in (("plan",a.plan_dir,plan),("results",a.results_dir,outputs)):
        for name in sorted(items):
            dest=target/folder/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():need(dest.read_bytes()==(src/name).read_bytes(),
                                  "Previously archived original genus K null changed: "+name)
            else:shutil.copyfile(src/name,dest)
            fingerprint[folder+"/"+name]=sha(dest)
    dest=target/"original_142_101_genus_conditioned_tip_loss_null_verdict.json"
    if dest.exists():need(dest.read_bytes()==a.verdict.read_bytes(),
                          "Original source genus K null final result was rewritten")
    else:shutil.copyfile(a.verdict,dest)
    fingerprint[dest.name]=sha(dest)
    need(len(fingerprint)==38,"Archive original 12 K null + 12 audit + 12 source plans incomplete")
    manifest={
      "status":STATUS,
      "original_complete_genus_K_null_run_id":RUN,
      "original_AusTraits_release":"v7.0.0",
      "original_parquet_sha256":SRC,
      "source_selected_original_K_pairs":142,
      "native_prune_original_pair_identities":101,
      "genus_conditioned_equal_n_family_correlated_random_draws":128,
      "native_broad_tree_retained_for_original_genus_null":True,
      "original_broad_source_trait_values_unchanged":True,
      "actual_strict_source_survivor_genus_counts_fixed":True,
      "all_12_genus_K_null_family_batches_and_original_K_audits_verified":True,
      "n_nonraw_derived_files":len(fingerprint),
      "derived_files_sha256":fingerprint,
      "never_export_source_species_genus_observation_ID_trait_median_data":True,
      "not_independent_primary_measurements":True,
      "not_confirmatory_evolutionary_selection_or_biomass_effect":True,
      "authors_have_not_authorized_journal_submission":True}
    mp=target/"original_genus_tip_loss_archive_manifest.json"
    contents=json.dumps(manifest,sort_keys=True,indent=2)+"\n"
    if mp.exists():need(mp.read_text()==contents,"Original genus K null output manifest drift")
    else:mp.write_text(contents)
    print(json.dumps({"status":STATUS,"files":len(fingerprint),
                      "run_id":RUN,"S3":final["genus_conditioned_AusTraits_Rcpp_native_K_derived_results"]["S3"][
                         "genus_quota_preserved_empirical_upper_tail_probability"],
                      "prune":final["genus_conditioned_AusTraits_Rcpp_native_K_derived_results"]["prune_only"][
                         "genus_quota_preserved_empirical_upper_tail_probability"]},sort_keys=True))

if __name__=="__main__":main()
