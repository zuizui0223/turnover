#!/usr/bin/env python3
"""Original 142/101 K matched-tip GENUS-COUNT conditioned null aggregation.

Verify every original source-derived pair and native tree status from the
SHA256-frozen broad and strict original K results and equal-n null archive.
The 128 draws now preserve observed surviving numbers WITHIN EACH GENUS
instead of keeping only global pair native-tip n. Retrospective sensitivity,
not biological causal inference or independent source validation.
"""
import argparse,hashlib,json,math,statistics,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_austraits_original_nonflora_tip_loss_null_v0_1 import validate,STATUS_BATCH

OLD=Path("results/austraits_organ_paper_public_v7_tip_loss_null_v0_1")
STATUS="PASS_ORIGINAL_142_101_GENUS_QUOTA_CONDITIONAL_SIZE_MATCHED_K_NULL"
N=128
BATCHES=12

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for z in iter(lambda:f.read(1024*1024),b""):h.update(z)
    return h.hexdigest()

def read(path):return json.loads(path.read_text())

def rate(vec,v):return (1+sum(x>=v for x in vec))/(len(vec)+1)

def run(plan_dir,genus_dir,outfile):
    oldmanifest=read(OLD/"original_tip_loss_null_archive_manifest.json")
    need(oldmanifest["status"]==
         "PASS_DURABLE_ORIGINAL_142_101_FIXED_BROAD_TREE_SIZE_MATCHED_PRUNING_NULL_ARCHIVE"
         and oldmanifest["n_nonraw_K_null_outputs_preserved"]==38,
         "Original random equal-n null SHA archive no longer pinned")
    for name,h in oldmanifest["derived_files_SHA256"].items():
        need(sha(OLD/name)==h,"Original 128 draw K null source changed "+name)
    old_final=read(OLD/"original_142_101_fixed_tree_tip_loss_null_verdict.json")
    need(old_final["status"]==
         "PASS_ORIGINAL_142_101_BROAD_TREE_FIXED_SIZE_MATCHED_TIP_LOSS_NULL"
         and old_final["n_null_draws"]==N
         and old_final["null_seed"]==20261114,
         "Original random K null comparison changed")
    plan=read(plan_dir/"original_null_plan.json")
    need(plan["status"]=="PASS_K_BLIND_ORIGINAL_142_PAIRS_TIP_LOSS_NULL_FIXED_BATCHES"
         and plan["original_qualified_pairs"]==142
         and plan["original_prune_native_supported_pairs"]==101,
         "Original source/taxon K 142/101 plan was changed")
    all_genus=[]
    n_rej=n_attempt=0
    for i in range(1,BATCHES+1):
        name=f"P{i:02d}"
        original_plan=OLD/"plan"/(name+".json")
        need(sha(plan_dir/(name+".json"))==oldmanifest["derived_files_SHA256"]["plan/"+name+".json"],
             "Genus-conditioned source plan differs from original K-blind pair identities")
        need(original_plan.read_bytes()==(plan_dir/(name+".json")).read_bytes(),
             "Genus conditional pruning different 142/101 family pair workload")
        result=genus_dir/(name+"_genus_null.json")
        qa=genus_dir/(name+"_audit.json")
        need(result.is_file() and qa.is_file(),"Missing original family paired genus null result "+name)
        z=read(result);audit=read(qa)
        need(z["status"]==STATUS_BATCH and z["null_replicates"]==N
             and z["null_seed"]==20261114
             and z["null_preserves_original_strict_survivor_count_within_each_genus"] is True
             and z["original_family_tips_and_broad_tree_fixed_and_only_within_genus_identity_random"] is True
             and z["genus_strata_extracted_from_same_original_public_v7_source_without_new_measurements"] is True
             and z["null_inference_conditioned_on_phylogenetic_K_estimable_in_every_family_pair"] is True
             and z["no_original_species_names_or_measurement_values_persisted"] is True
             and z["no_per_pair_independent_resampling_after_K_variance_hold"] is True,
             "Original genus-conditioned K randomization semantics not verified")
        need(audit==validate(plan_dir/(name+".json"),result),
             "Independent original 142 K baseline/audit failed on genus-conditioned run")
        prior=read(OLD/"results"/(name+"_null.json"))
        old={z["null_pair_id"]:z for z in prior["pairs"]}
        need(len(old)==len(z["pairs"]),"Genus-conditioned K pair batch not original K")
        for row in z["pairs"]:
            ref=old[row["null_pair_id"]]
            need((row["family"],row["trait_A"],row["trait_B"])==
                 (ref["family"],ref["trait_A"],ref["trait_B"]),
                 "Original family/trait identity changed in genus-conditioned null")
            for ax in ("S3","prune_only"):
                x=row["axes"][ax];y=ref["axes"][ax]
                need(x["status"]==y["status"],
                     "Genus null native source tree hold changed")
                if x["status"]!="PASS":continue
                for v in ("n_baseline_tips","n_actual_strict_tips",
                          "baseline_logK_contrast",
                          "actual_strict_survivors_logK_on_fixed_broad_tree",
                          "actual_strict_survivor_flip_on_fixed_broad_tree",
                          "historical_stage2_rebuilt_logK_contrast",
                          "actual_survivor_PD_fraction_of_broad_tree"):
                    need(math.isclose(x[v],y[v],rel_tol=1e-12,abs_tol=1e-10),
                         "Original same source and K fixed tree stage was changed: "+v)
                need(len(x["null_flip_bits"])==N
                     and set(x["null_flip_bits"])<=set("01"),
                     "Genus-conditioned random K sign flips incomplete")
        all_genus.extend(z["pairs"])
        n_rej+=int(z["n_rejected_family_priorities_due_to_undefined_K"])
        n_attempt+=int(z["n_total_candidate_family_priorities_evaluated"])
    need(len(all_genus)==142 and len(set((v["family"],v["trait_A"],v["trait_B"]) for v in all_genus))==142,
         "Original complete 142 strict K source pair cohort incomplete")
    axes={}
    for ax in ("S3","prune_only"):
        pairs=[(p,p["axes"][ax]) for p in all_genus if p["axes"][ax]["status"]=="PASS"]
        expected=142 if ax=="S3" else 101
        need(len(pairs)==expected,"Original native axis no longer same 142/101 K cohort")
        actual=sum(int(x["actual_strict_survivor_flip_on_fixed_broad_tree"]) for p,x in pairs)
        need(actual==(23 if ax=="S3" else 13),
             "Original actual strict survivor K reversal count changed")
        null_flips=[sum(int(x["null_flip_bits"][r]) for p,x in pairs) for r in range(N)]
        by_fam=defaultdict(list)
        for p,x in pairs:by_fam[p["family"]].append(x)
        lofo=[]
        for fam,arr in by_fam.items():
            n_actual=sum(z["actual_strict_survivor_flip_on_fixed_broad_tree"] for z in arr)
            other_null=[q-sum(int(z["null_flip_bits"][r]) for z in arr)
                        for r,q in enumerate(null_flips)]
            lofo.append({"family":fam,"n_original_pairs":len(arr),"n_original_actual_flips":n_actual,
                         "upper_tail_leave_one_family_out":rate(other_null,actual-n_actual)})
        lofo=sorted(lofo,key=lambda z:-z["upper_tail_leave_one_family_out"])
        orig=old_final["axes"][ax]
        axes[ax]={
          "n_same_original_K_pair_identities":expected,
          "source_survivor_fixed_broad_tree_flips":actual,
          "genus_quota_preserved_random_null_mean_K_flips":sum(null_flips)/N,
          "genus_quota_preserved_random_null_median_K_flips":statistics.median(null_flips),
          "genus_quota_preserved_random_total_K_flips_min":min(null_flips),
          "genus_quota_preserved_random_total_K_flips_max":max(null_flips),
          "genus_quota_preserved_empirical_upper_tail_probability":rate(null_flips,actual),
          "unstratified_equal_n_original_random_mean_K_flips":
             orig["mean_family_correlated_random_taxon_loss_K_flips"],
          "unstratified_equal_n_original_upper_tail_probability":
             orig["empirical_upper_tail_p_actual_fixed_tree_flips"],
          "genus_quota_preserved_vs_original_unstratified_random_mean_difference":
             sum(null_flips)/N-orig["mean_family_correlated_random_taxon_loss_K_flips"],
          "n_original_families":len(by_fam),
          "genus_conditioned_leave_one_family_out_upper_tail_max":max(z["upper_tail_leave_one_family_out"] for z in lofo),
          "genus_conditioned_leave_one_family_out_p_le_0_05":sum(z["upper_tail_leave_one_family_out"]<=.05 for z in lofo),
          "genus_conditioned_leave_one_family_out_highest_tail_families":lofo[:6],
          "original_source_phylogeny_broad_tree_kept_fixed_and_original_K_unchanged":True}
    result={
      "status":STATUS,
      "original_public_v7_source_parquet_sha256":"5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99",
      "original_unstratified_full_128_null_SHA256":sha(OLD/"original_142_101_fixed_tree_tip_loss_null_verdict.json"),
      "original_unstratified_archive_manifest_SHA256":sha(OLD/"original_tip_loss_null_archive_manifest.json"),
      "genus_conditioned_AusTraits_Rcpp_native_K_derived_results":axes,
      "original_pair_identities":142,
      "original_native_prune_supported_pair_identities":101,
      "number_frozen_family_batches":BATCHES,
      "number_family_correlated_replicates":N,
      "original_family_wide_random_rank_seed":20261114,
      "number_rejected_original_family_priorities_for_undefined_K":n_rej,
      "number_attempted_family_priorities":n_attempt,
      "genus_quota_actual_strict_survivors_fixed_for_each_original_pair":True,
      "original_broad_tree_and_original_phenotype_values_fixed":True,
      "original_organ_classification_post_selected":True,
      "no_external_GIFT_or_TRY_original_measurement_rows_joined":True,
      "original_source_species_names_or_raw_trait_measurements_exported":False,
      "same_trait_pair_and_family_dependence_not_separate_biological_replicates":True,
      "conditional_descriptive_not_preregistered_multiple_hypothesis_test":True,
      "genus_quota_conditioning_cannot_identify_mechanistic_causality":True}
    outfile.parent.mkdir(parents=True,exist_ok=True)
    outfile.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":STATUS,"axes":axes,"n_family_candidate_rejections":n_rej},sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan-dir",type=Path,required=True)
    p.add_argument("--results-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.plan_dir,a.results_dir,a.output)
if __name__=="__main__":main()
