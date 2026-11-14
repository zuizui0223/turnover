#!/usr/bin/env python3
"""Descriptive family sensitivity of original AusTraits 142/101 fixed-tree null.

Use ONLY SHA256-verified, already-computed 128 family-correlated rank draws
and unchanged original K results; no new K fitting, no trait reclassification,
no new biological group selection, no independent studies and no raw records.
Family-held-out p values are diagnostics, not multiple confirmatory tests.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path

SRC=Path("results/austraits_organ_paper_public_v7_tip_loss_null_v0_1")
STATUS="PASS_ORIGINAL_142_101_TIP_LOSS_NULL_FAMILY_AND_PHYLOGENETIC_PD_SENSITIVITY_ONLY"
N=128
AXES=("S3","prune_only")

def need(flag,msg):
    if not flag:raise AssertionError(msg)
def sha(x):return hashlib.sha256(x).hexdigest()
def quant(x):return statistics.median(x) if x else None
def probability(counts, observed):
    return (1+sum(z>=observed for z in counts))/(len(counts)+1)

def report(outdir):
    manifest=json.loads((SRC/"original_tip_loss_null_archive_manifest.json").read_text())
    need(manifest["status"]==
         "PASS_DURABLE_ORIGINAL_142_101_FIXED_BROAD_TREE_SIZE_MATCHED_PRUNING_NULL_ARCHIVE"
         and manifest["n_nonraw_K_null_outputs_preserved"]==38
         and manifest["original_142_S3_pair_contexts"]==142
         and manifest["original_101_prune_pair_contexts"]==101
         and manifest["family_correlated_equal_n_random_subset_draws"]==N,
         "Original full 12-batch null permanent archival metadata changed")
    for path,digest in manifest["derived_files_SHA256"].items():
        fp=SRC/path
        need(fp.is_file() and sha(fp.read_bytes())==digest,
             "Original 142/101 source-family K null result not SHA256-exact: "+path)
    orig=json.loads((SRC/"original_142_101_fixed_tree_tip_loss_null_verdict.json").read_text())
    need(orig["status"]==
         "PASS_ORIGINAL_142_101_BROAD_TREE_FIXED_SIZE_MATCHED_TIP_LOSS_NULL"
         and orig["n_null_draws"]==N and orig["n_original_family_clusters"]==24
         and orig["number_original_family_trait_pairs"]==142
         and orig["original_prune_supported_pair_ids"]==101
         and orig["null_distribution_conditioned_on_K_estimable_across_each_original_family"] is True,
         "Not the original source-conditioned full null result")
    pairs=[]
    for i in range(1,13):
        path=SRC/"results"/f"P{i:02d}_null.json"
        z=json.loads(path.read_text())
        need(z["status"]=="PASS_ORIGINAL_142_TIP_LOSS_FROZEN_BROAD_TREE_NULL_BATCH"
             and z["null_replicates"]==N,"Original family-correlated null batch incomplete")
        pairs+=z["pairs"]
    need(len(pairs)==142 and len({(x["family"],x["trait_A"],x["trait_B"]) for x in pairs})==142,
         "Original same-source pair identity population changed")
    fams=sorted({x["family"] for x in pairs})
    need(len(fams)==24,"Original 24 families not represented")
    axes={}; family_rows=[]
    for ax in AXES:
        rows=[(x,x["axes"][ax]) for x in pairs if x["axes"][ax]["status"]=="PASS"]
        target=142 if ax=="S3" else 101
        need(len(rows)==target,"Original native-tree source K null population changed")
        observed=sum(int(z["actual_strict_survivor_flip_on_fixed_broad_tree"]) for x,z in rows)
        simulated=[sum(int(z["null_flip_bits"][r]) for x,z in rows)
                   for r in range(N)]
        need(observed==orig["axes"][ax]["actual_strict_survivors_on_fixed_broad_tree_K_flips"]
             and math.isclose(sum(simulated)/N,
                              orig["axes"][ax]["mean_family_correlated_random_taxon_loss_K_flips"],
                              rel_tol=0,abs_tol=1e-10)
             and probability(simulated,observed)==
                 orig["axes"][ax]["empirical_upper_tail_p_actual_fixed_tree_flips"],
             "Original fixed-tree full-sample random null probability changed")
        family=pd=defaultdict(list)
        for pair,z in rows:family[pair["family"]].append(z)
        extras=[]
        for fam in fams:
            vec=family[fam]
            actual=sum(int(z["actual_strict_survivor_flip_on_fixed_broad_tree"]) for z in vec)
            nullfamily=[sum(int(z["null_flip_bits"][r]) for z in vec) for r in range(N)]
            tail=[a-b for a,b in zip(simulated,nullfamily)]
            lofo_p=probability(tail,observed-actual)
            family_rows.append({
              "axis":ax,"family":fam,"n_original_pair_ids":len(vec),
              "actual_K_sign_flips":actual,
              "expected_K_sign_flips_equal_n_random_taxon_loss":sum(nullfamily)/N,
              "excess_observed_over_random_flips":actual-sum(nullfamily)/N,
              "original_full_total_flips":observed,
              "leave_one_family_out_observed_flips":observed-actual,
              "leave_one_family_out_null_average_flips":sum(tail)/N,
              "leave_one_family_out_upper_tail_p_exploratory":lofo_p,
              "n_actual_PD_fraction_below_2_5pct_random_null":
                 sum(z["actual_survivor_PD_fraction_of_broad_tree"]<
                     z["random_tree_PD_fraction_of_broad_tree"]["q025"] for z in vec),
              "n_actual_PD_fraction_above_97_5pct_random_null":
                 sum(z["actual_survivor_PD_fraction_of_broad_tree"]>
                     z["random_tree_PD_fraction_of_broad_tree"]["q975"] for z in vec)})
            extras.append({"family":fam,"n_pairs":len(vec),
                           "actual_flips":actual,"random_mean":sum(nullfamily)/N,
                           "excess":actual-sum(nullfamily)/N,
                           "LOFO_upper_tail_p":lofo_p})
        flipped=[z for x,z in rows if z["actual_strict_survivor_flip_on_fixed_broad_tree"]]
        stable=[z for x,z in rows if not z["actual_strict_survivor_flip_on_fixed_broad_tree"]]
        pd_low=lambda a:sum(z["actual_survivor_PD_fraction_of_broad_tree"]<
                 z["random_tree_PD_fraction_of_broad_tree"]["q025"] for z in a)
        pd_high=lambda a:sum(z["actual_survivor_PD_fraction_of_broad_tree"]>
                 z["random_tree_PD_fraction_of_broad_tree"]["q975"] for z in a)
        lofo=[z["LOFO_upper_tail_p"] for z in extras if z["n_pairs"]>0]
        axes[ax]={
          "original_pair_contexts":target,
          "actual_source_qualified_fixed_broad_tree_flips":observed,
          "random_same_n_K_flips_mean":sum(simulated)/N,
          "family_shared_rank_random_draws":N,
          "empirical_upper_tail_p_full_original_24family_context":probability(simulated,observed),
          "n_families_with_native_supported_pairs":sum(z["n_pairs"]>0 for z in extras),
          "leave_one_family_out_exploratory_upper_tail_p_min":min(lofo),
          "leave_one_family_out_exploratory_upper_tail_p_median":quant(lofo),
          "leave_one_family_out_exploratory_upper_tail_p_max":max(lofo),
          "n_family_deletions_with_p_le_0_05":sum(z<=.05 for z in lofo),
          "n_family_deletions_with_p_le_0_1":sum(z<=.10 for z in lofo),
          "n_family_deletions_with_p_gt_0_1":sum(z>.10 for z in lofo),
          "n_pair_contexts_with_PD_below_2_5pct_null":pd_low([z for x,z in rows]),
          "n_pair_contexts_with_PD_above_97_5pct_null":pd_high([z for x,z in rows]),
          "among_actual_flipped_pairs_PD_below_2_5pct":pd_low(flipped),
          "among_actual_nonflipped_pairs_PD_below_2_5pct":pd_low(stable),
          "median_actual_PD_fraction_over_random_mean_all":quant([
             z["actual_survivor_PD_fraction_of_broad_tree"]/
             z["random_tree_PD_fraction_of_broad_tree"]["mean"] for x,z in rows]),
          "top_families_excess_flips_over_random":sorted(
             (z for z in extras if z["n_pairs"]>0),key=lambda x:-x["excess"])[:8],
          "families_where_removal_most_weakens_full_tail":
             sorted((z for z in extras if z["n_pairs"]>0),
                    key=lambda x:-x["LOFO_upper_tail_p"])[:8],
          "family_LOFO_is_posthoc_sensitivity_not_selection_adjusted_inference":True}
    outdir.mkdir(parents=True,exist_ok=True)
    csvout=outdir/"original_K_null_leave_one_family_out_and_PD.csv"
    fields=list(family_rows[0])
    with csvout.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(family_rows)
    outcome={
      "status":STATUS,
      "original_run":manifest["original_full_tip_loss_null_CI_run_id"],
      "original_full_null_verdict_sha256":sha((SRC/"original_142_101_fixed_tree_tip_loss_null_verdict.json").read_bytes()),
      "original_archive_manifest_sha256":sha((SRC/"original_tip_loss_null_archive_manifest.json").read_bytes()),
      "axes":axes,
      "family_by_native_axis_review_rows":len(family_rows),
      "family_review_csv_sha256":sha(csvout.read_bytes()),
      "number_original_K_phylogenetic_fits":0,
      "number_new_original_trait_observations":0,
      "no_source_species_names_or_raw_original_trait_values_exported":True,
      "original_128_family_correlated_rank_draws_not_recomputed":True,
      "comparison_preserves_source_qualified_original_fixed_K_pair_population":True,
      "multiple_interdependent_pair_and_tree_treatments_not_independent_validation":True,
      "all_family_PDs_are_original_broad_native_tree_length_fractions":True,
      "original_post_selected_organ_categories_not_covered_by_family_LOFO":True,
      "no_new_plant_biomass_allocation_or_causal_selection_measured":True}
    (outdir/"original_K_null_family_PD_sensitivity_verdict.json").write_text(
      json.dumps(outcome,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"axes":axes},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",type=Path,required=True)
    z=p.parse_args()
    report(z.out_dir)
