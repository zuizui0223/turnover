#!/usr/bin/env python3
"""Post hoc DESCRIPTIVE context for ORIGINAL 142/101 AusTraits K sign flips.

Use only the SHA256-pinned original public-v7 full source-stage K aggregates,
not new phylogenetic fits, additional trait data, new statistical significance
tests or new source-based cohort selection. Family×named trait pairs are
dependent; the two native trees are NOT biological replications.
"""
import argparse,csv,hashlib,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path("results/austraits_organ_paper_public_v7_nonflora_3stage_replay_v0_1")
STATUS="PASS_POSTHOC_ORIGINAL_142_101_TAXON_FLIP_DESCRIPTIVE_COMMONALITIES"
EXPECTED={"S3":{"pairs":142,"wins":[110,121,120],"taxon_flips":23,"value_flips":9,"families":24},
          "prune_only":{"pairs":101,"wins":[82,83,81],"taxon_flips":13,"value_flips":12,"families":18}}

def need(ok,msg):
    if not ok:raise AssertionError(msg)
def digest(b):return hashlib.sha256(b).hexdigest()
def read(name):
    with (ROOT/name).open(encoding="utf-8") as f:return json.load(f)
def median(x):return statistics.median(x) if x else None
def summary(values):
    return {"n":len(values),"median":median(values),
            "minimum":min(values) if values else None,
            "maximum":max(values) if values else None}

def typed(z):
    rep=[x for x in (z["trait_A"],z["trait_B"]) if x.startswith(("fruit_","seed_"))]
    veg=[x for x in (z["trait_A"],z["trait_B"]) if x not in rep]
    need(len(rep)==len(veg)==1,"Not an original reproductive/vegetative trait pair")
    return rep[0],veg[0]

def go(out):
    manifest=read("nonflora_replay_archive_manifest.json")
    checks=manifest["preserved_file_sha256"]
    for name in ("broad_283_aggregate.json","strict_142_aggregate.json"):
        need(digest((ROOT/name).read_bytes())==checks[name],
             "Published original nonflora source K SHA256 changed: "+name)
    broad=read("broad_283_aggregate.json")
    strict=read("strict_142_aggregate.json")
    need(broad["status"]=="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_ORGAN_SENSITIVITY_AGGREGATED_V0_1"
         and strict["status"]=="AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_SENSITIVITY_AGGREGATED_V0_1",
         "Not complete original nonflora K raw-source aggregates")
    records=[]
    axes={}
    for axis,target in EXPECTED.items():
        old={ (z["family"],z["trait_A"],z["trait_B"]):z
             for z in broad["axes"][axis]["pair_level_K_decisions_no_species_names"]}
        narrow=strict["axes"][axis]["pair_level_K_decisions_no_species_names"]
        need(len(narrow)==target["pairs"],"Strict original K graph count changed")
        current=[]
        for z in narrow:
            k=(z["family"],z["trait_A"],z["trait_B"])
            need(k in old,"Strict source-qualified pair not in original broad graph")
            x=old[k]
            rep,veg=typed(z)
            need(x["subtype"]==z["subtype"] and
                 20<=z["n_same_source_species"]<=x["n_nonflora_species"],
                 "Original K source species/cohort switched")
            need(0<z["n_native_tree_tips"]<=x["n_native_tree_tips"],
                 "Original narrow S3/prune tip support changed")
            d=[float(x["delta_five_flora_removed"]),
               float(z["delta_all_nonflora_sources"]),
               float(z["delta_identical_nonflora_dataset"])]
            need(all(math.isfinite(v) and v!=0 for v in d),"Original K zero/nonfinite")
            signs=[int(v>0) for v in d]
            need(signs==[
              x["reproductive_K_higher_nonflora_medians"],
              z["reproductive_K_higher_all_nonflora_medians"],
              z["reproductive_K_higher_identical_nonflora_dataset_medians"]],
              "Original source K sign/observed status mismatch")
            rec={
              "axis":axis,"family":z["family"],
              "trait_reproductive":rep,"trait_vegetative":veg,
              "organ_subtype":z["subtype"],
              "broad_species":x["n_nonflora_species"],
              "strict_species":z["n_same_source_species"],
              "species_retention_fraction":z["n_same_source_species"]/x["n_nonflora_species"],
              "broad_native_tree_tips":x["n_native_tree_tips"],
              "strict_native_tree_tips":z["n_native_tree_tips"],
              "native_tree_tip_retention_fraction":z["n_native_tree_tips"]/x["n_native_tree_tips"],
              "broad_K_log_difference":d[0],
              "strict_tips_full_nonflora_K_log_difference":d[1],
              "strict_tips_same_source_K_log_difference":d[2],
              "abs_original_K_log_margin":abs(d[0]),
              "abs_taxon_change_in_K_log_difference":abs(d[1]-d[0]),
              "abs_value_change_in_K_log_difference":abs(d[2]-d[1]),
              "stage1_reproductive_K_higher":signs[0],
              "stage2_reproductive_K_higher":signs[1],
              "stage3_reproductive_K_higher":signs[2],
              "reversal_taxon_plus_tree":int(signs[0]!=signs[1]),
              "reversal_measurement_same_tips":int(signs[1]!=signs[2])}
            current.append(rec)
        flip=[r for r in current if r["reversal_taxon_plus_tree"]]
        same=[r for r in current if not r["reversal_taxon_plus_tree"]]
        value=[r for r in current if r["reversal_measurement_same_tips"]]
        totals=[sum(x[f"stage{i}_reproductive_K_higher"] for x in current) for i in (1,2,3)]
        need(len(current)==target["pairs"] and totals==target["wins"]
             and len(flip)==target["taxon_flips"] and len(value)==target["value_flips"]
             and len({r["family"] for r in current})==target["families"],
             "Original full K results three-stage graph changed")
        fam=defaultdict(lambda:{"pairs":0,"taxon_plus_tree_reversals":0,
                                "measurement_reversals":0})
        veg_groups=defaultdict(lambda:{"pairs":0,"taxon_plus_tree_reversals":0,
                                       "measurement_reversals":0})
        for z in current:
            for dest,key in ((fam,z["family"]),(veg_groups,z["trait_vegetative"])):
                dest[key]["pairs"]+=1
                dest[key]["taxon_plus_tree_reversals"]+=z["reversal_taxon_plus_tree"]
                dest[key]["measurement_reversals"]+=z["reversal_measurement_same_tips"]
        axes[axis]={
          "n_original_identical_K_pair_ids":len(current),
          "n_original_contributing_families":len(fam),
          "original_reproductive_wins_three_stages":totals,
          "n_taxon_plus_tree_K_sign_reversals":len(flip),
          "n_same_tips_measurement_source_K_sign_reversals":len(value),
          "n_families_with_one_or_more_taxon_plus_tree_reversals":len({z["family"] for z in flip}),
          "retained_source_species_fraction":{
             "all":summary([r["species_retention_fraction"] for r in current]),
             "reversed":summary([r["species_retention_fraction"] for r in flip]),
             "not_reversed":summary([r["species_retention_fraction"] for r in same])},
          "retained_native_K_tree_tips_fraction":{
             "all":summary([r["native_tree_tip_retention_fraction"] for r in current]),
             "reversed":summary([r["native_tree_tip_retention_fraction"] for r in flip]),
             "not_reversed":summary([r["native_tree_tip_retention_fraction"] for r in same])},
          "absolute_original_log_K_margin":{
             "all":summary([r["abs_original_K_log_margin"] for r in current]),
             "reversed":summary([r["abs_original_K_log_margin"] for r in flip]),
             "not_reversed":summary([r["abs_original_K_log_margin"] for r in same])},
          "all_pairs_median_abs_taxon_tree_change":median([r["abs_taxon_change_in_K_log_difference"] for r in current]),
          "all_pairs_median_abs_same_tips_source_value_change":median([r["abs_value_change_in_K_log_difference"] for r in current]),
          "by_vegetative_trait":dict(sorted(veg_groups.items())),
          "family_reversal_counts":dict(sorted(fam.items())),
          "taxon_tree_reversal_direction":{
             "vegetative_higher_to_reproductive_higher":
                  sum(r["stage1_reproductive_K_higher"]==0 and r["stage2_reproductive_K_higher"]==1 for r in current),
             "reproductive_higher_to_vegetative_higher":
                  sum(r["stage1_reproductive_K_higher"]==1 and r["stage2_reproductive_K_higher"]==0 for r in current)},
          "measurement_reversal_direction":{
             "vegetative_higher_to_reproductive_higher":
                  sum(r["stage2_reproductive_K_higher"]==0 and r["stage3_reproductive_K_higher"]==1 for r in current),
             "reproductive_higher_to_vegetative_higher":
                  sum(r["stage2_reproductive_K_higher"]==1 and r["stage3_reproductive_K_higher"]==0 for r in current)}
        }
        records+=current
    need(len(records)==243,"Original S3 + prune pair-tree observations missing")
    out.mkdir(parents=True,exist_ok=True)
    csvpath=out/"original_nonflora_pairwise_flip_context_no_species_names.csv"
    with csvpath.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader();w.writerows(sorted(records,key=lambda z:(z["axis"],z["family"],z["trait_reproductive"],z["trait_vegetative"])))
    result={
      "status":STATUS,
      "source":"exact original SHA256-pinned AusTraits v7 nonflora K raw-source replays",
      "original_source_broad_sha256":checks["broad_283_aggregate.json"],
      "original_source_strict_sha256":checks["strict_142_aggregate.json"],
      "axes":axes,
      "n_axis_specific_pair_level_context_rows":len(records),
      "post_hoc_descriptive_not_hypothesis_confirming":True,
      "n_new_phylogenetic_K_fits":0,
      "n_new_external_datasets_joined":0,
      "not_independent_biological_family_trait_replicates":True,
      "organ_grouping_originally_selected_after_K_outcomes":True,
      "retention_does_not_isolate_loss_of_sample_size_from_lineage_identity":True,
      "baseline_K_margin_related_flip_is_descriptive_and_tautology_risk":True,
      "same_source_DatasetID_does_not_prove_independent_primary_specimens":True,
      "species_names_or_original_measurements_exported":False,
      "future_mechanistic_test":"Fixed broad tree and trait states; compare actual strict survivor subset to equal-n random tip subsets, controlling baseline K margin and shared family; record source-lineage and growth form."
    }
    result["output_csv_sha256"]=digest(csvpath.read_bytes())
    target=out/"original_nonflora_flip_context_verdict.json"
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"axis_summary":{
        a:{"n":v["n_original_identical_K_pair_ids"],
           "taxon_flips":v["n_taxon_plus_tree_K_sign_reversals"],
           "source_flips":v["n_same_tips_measurement_source_K_sign_reversals"],
           "retained_species_fraction_flip":v["retained_source_species_fraction"]["reversed"]["median"],
           "retained_species_fraction_other":v["retained_source_species_fraction"]["not_reversed"]["median"],
           "abs_baseline_logK_flip":v["absolute_original_log_K_margin"]["reversed"]["median"],
           "abs_baseline_logK_other":v["absolute_original_log_K_margin"]["not_reversed"]["median"]
           } for a,v in axes.items()}},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args()
    go(args.out_dir)
