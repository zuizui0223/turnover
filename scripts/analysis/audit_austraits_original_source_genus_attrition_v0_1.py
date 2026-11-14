#!/usr/bin/env python3
"""Original AusTraits v7 source-eligible genus loss for fixed 142/101 K pairs.

Compute which fraction of original taxa lost during strict same-DatasetID
qualification belong to genera that disappear ENTIRELY, versus species lost
within still-present genera. Original native K and two 128-draw nulls are
frozen; no trait fit, source search, p-value optimization or raw observations.

Persist only family×named-trait pair aggregate counts, no genus/species names,
raw individual trait measurements, observation IDs or original DatasetIDs.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,statistics,sys
from collections import defaultdict
from pathlib import Path

import duckdb
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"qa"))
from audit_austraits_organ_contributing_sources_v0_1 import (
    source_graph,compile_states,make_pairs
)
ROOT=Path("results/austraits_organ_paper_public_v7_genus_quota_tip_loss_null_v0_1")
STATUS="PASS_ORIGINAL_142_101_GENUS_LOSS_VS_WITHIN_GENUS_SOURCE_ATTRITION_DESCRIPTION"
SRC_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for z in iter(lambda:f.read(1024*1024),b""):
            h.update(z)
    return h.hexdigest()

def med(z):
    return statistics.median(z) if z else None

def original_pairs():
    m=json.loads((ROOT/"original_genus_tip_loss_archive_manifest.json").read_text())
    need(m["status"]=="PASS_DURABLE_ORIGINAL_142_101_GENUS_QUOTA_FIXED_TREE_K_NULL_REPLAY_V0_1"
         and m["n_nonraw_derived_files"]==38 and m["original_complete_genus_K_null_run_id"]==43566577755
         and m["original_parquet_sha256"]==SRC_SHA,
         "Permanent original v7 genus conditional K null proof absent")
    for name,sha in m["derived_files_sha256"].items():
        p=ROOT/name
        need(p.is_file() and digest(p)==sha,
             "Original genus-conditioned source-only K null SHA changed "+name)
    original={}
    for i in range(1,13):
        d=json.loads((ROOT/"results"/f"P{i:02d}_genus_null.json").read_text())
        need(d["status"]=="PASS_ORIGINAL_142_TIP_LOSS_FROZEN_BROAD_TREE_NULL_BATCH"
             and d["null_replicates"]==128
             and d["null_preserves_original_strict_survivor_count_within_each_genus"] is True,
             "Not original 128-draw genus conditional source K results")
        for r in d["pairs"]:
            key=r["family"],r["trait_A"],r["trait_B"]
            need(key not in original,"Original same-DatasetID K pair repeated")
            original[key]=r
    need(len(original)==142 and
         sum(z["axes"]["prune_only"]["status"]=="PASS" for z in original.values())==101,
         "Original 142/101 native K cohort changed")
    return original,m

def genuses(c):
    broad=c.execute("""
       SELECT DISTINCT t.family,t.trait_A,t.trait_B,a.species,a.genus
       FROM strict_targets t
       JOIN nonflora_states a ON a.sid=t.system_A
       JOIN nonflora_states b ON b.sid=t.system_B
         AND a.species=b.species AND a.genus=b.genus
       ORDER BY 1,2,3,4
    """).fetchall()
    strict=c.execute("""
       SELECT DISTINCT family,trait_A,trait_B,species,genus
       FROM same_dataset ORDER BY 1,2,3,4
    """).fetchall()
    bb=defaultdict(dict);ss=defaultdict(dict)
    for row in broad:
        k=(row[0],row[1],row[2])
        need(row[3] not in bb[k],"Original broad source taxon repeats")
        bb[k][row[3]]=row[4]
    for row in strict:
        k=(row[0],row[1],row[2])
        need(row[3] not in ss[k],"Strict original source species repeats")
        ss[k][row[3]]=row[4]
    need(len(bb)==len(ss)==142,"Original strict 142 family×trait pairs absent")
    return bb,ss

def analyze(parquet,units,out_dir):
    need(digest(parquet)==SRC_SHA,"AusTraits public v7 raw dataset SHA changed")
    orig,manifest=original_pairs()
    con=duckdb.connect(":memory:")
    try:
        refs,pairs,strict=source_graph()
        compile_states(con,parquet,units,refs)
        make_pairs(con,pairs,strict)
        broad,retained=genuses(con)
    finally:con.close()
    need(set(broad)==set(retained)==set(orig),
         "Original fixed K stage genus/trait pair identities differ")
    rows=[]
    for key,original in sorted(orig.items()):
        src=broad[key];surv=retained[key]
        need(set(surv).issubset(src) and
             all(src[name]==gen for name,gen in surv.items()),
             "Original strict source cohort changed genus identity")
        broad_sp=len(src);strict_sp=len(surv)
        need(broad_sp==original["original_broad_source_species"]
             and strict_sp==original["original_strict_surviving_source_species"],
             "Original broad and strict 142 K species support disagree")
        big=defaultdict(set);small=defaultdict(set)
        for species,g in src.items():big[g].add(species)
        for species,g in surv.items():small[g].add(species)
        lost_g=set(big)-set(small)
        wholly_lost=sum(len(big[g]) for g in lost_g)
        within_lost=broad_sp-strict_sp-wholly_lost
        need(0<=wholly_lost<=broad_sp-strict_sp
             and 0<=within_lost<=broad_sp-strict_sp
             and wholly_lost+within_lost==broad_sp-strict_sp,
             "Original genus loss decomposition impossible")
        for ax in ("S3","prune_only"):
            rec=original["axes"][ax]
            if rec["status"]!="PASS":continue
            result={
              "native_tree":ax,"family":key[0],
              "trait_A":key[1],"trait_B":key[2],
              "trait_reproductive":key[1] if key[1].startswith(("fruit_","seed_")) else key[2],
              "trait_vegetative":key[2] if key[1].startswith(("fruit_","seed_")) else key[1],
              "n_broad_source_species":broad_sp,
              "n_strict_source_species":strict_sp,
              "n_broad_source_genera":len(big),
              "n_strict_source_genera":len(small),
              "n_wholly_lost_genera":len(lost_g),
              "n_species_lost_with_entire_genus":wholly_lost,
              "n_species_lost_within_retained_genera":within_lost,
              "n_genera_with_within_genus_species_options":
                  sum(len(big[g])>len(small[g]) for g in small),
              "fraction_original_genera_retained":len(small)/len(big),
              "fraction_original_species_retained":strict_sp/broad_sp,
              "fraction_lost_species_from_wholly_lost_genera":
                  wholly_lost/(broad_sp-strict_sp) if broad_sp>strict_sp else None,
              "original_fixed_broad_tree_K_sign_reversed":
                  int(rec["actual_strict_survivor_flip_on_fixed_broad_tree"]),
              "original_baseline_absolute_K_log_margin":
                  abs(rec["baseline_logK_contrast"])}
            need(result["trait_reproductive"].startswith(("fruit_","seed_")),
                 "Original organ definition altered")
            rows.append(result)
    need(len(rows)==243 and sum(z["native_tree"]=="S3" for z in rows)==142
         and sum(z["native_tree"]=="prune_only" for z in rows)==101,
         "Original native K/trait genus attrition graph not exact")
    by={}
    for ax in ("S3","prune_only"):
        rr=[z for z in rows if z["native_tree"]==ax]
        ff=[z for z in rr if z["original_fixed_broad_tree_K_sign_reversed"]]
        st=[z for z in rr if not z["original_fixed_broad_tree_K_sign_reversed"]]
        need(len(ff)==(23 if ax=="S3" else 13),
             "Original K sign reversal count changed")
        by[ax]={
         "n_original_pair_identities":len(rr),
         "n_actual_original_K_sign_reversals":len(ff),
         "pairs_with_at_least_one_entire_genus_lost":sum(z["n_wholly_lost_genera"]>0 for z in rr),
         "flipped_pairs_with_entire_genus_lost":sum(z["n_wholly_lost_genera"]>0 for z in ff),
         "stable_pairs_with_entire_genus_lost":sum(z["n_wholly_lost_genera"]>0 for z in st),
         "flipped_pairs_with_no_genus_lost":sum(z["n_wholly_lost_genera"]==0 for z in ff),
         "median_fraction_genera_retained_flipped":med([z["fraction_original_genera_retained"] for z in ff]),
         "median_fraction_genera_retained_stable":med([z["fraction_original_genera_retained"] for z in st]),
         "median_fraction_species_retained_flipped":med([z["fraction_original_species_retained"] for z in ff]),
         "median_fraction_species_retained_stable":med([z["fraction_original_species_retained"] for z in st]),
         "median_wholly_lost_genus_count_flipped":med([z["n_wholly_lost_genera"] for z in ff]),
         "median_wholly_lost_genus_count_stable":med([z["n_wholly_lost_genera"] for z in st]),
         "median_fraction_lost_species_in_wholly_lost_genera_flipped":
             med([z["fraction_lost_species_from_wholly_lost_genera"] for z in ff
                  if z["fraction_lost_species_from_wholly_lost_genera"] is not None]),
         "median_fraction_lost_species_in_wholly_lost_genera_stable":
             med([z["fraction_lost_species_from_wholly_lost_genera"] for z in st
                  if z["fraction_lost_species_from_wholly_lost_genera"] is not None]),
         "median_number_genera_with_species_replacements_flipped":
             med([z["n_genera_with_within_genus_species_options"] for z in ff]),
         "median_number_genera_with_species_replacements_stable":
             med([z["n_genera_with_within_genus_species_options"] for z in st]),
         "n_original_family_groups":len({z["family"] for z in rr}),
         "not_causal_and_not_external_species_source_replication":True}
    out_dir.mkdir(parents=True,exist_ok=True)
    csvp=out_dir/"original_142_101_source_genus_attrition_pairs_without_taxon_names.csv"
    with csvp.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    verdict={
      "status":STATUS,
      "original_source_AusTraits_release":"v7.0.0",
      "original_parquet_SHA256":SRC_SHA,
      "source_genus_K_null_archive_manifest_SHA256":digest(ROOT/"original_genus_tip_loss_archive_manifest.json"),
      "n_original_native_pair_level_rows":243,
      "original_reconstruction_from_same_fixed_254_760_142_K_qualification":True,
      "native_tree_axes":by,
      "source_species_and_genus_names_or_raw_trait_values_exported":False,
      "new_plant_evolutionary_trait_K_fits":0,
      "new_evolutionary_biomass_or_selection_effect_tests":0,
      "same_species_count_null_does_not_force_same_genus_distribution":True,
      "genus_quota_randomization_conditions_on_observed_strict_genus_survival":True,
      "source_survivor_genus_loss_cannot_prove_independent_primary_study_or_biomass_mechanism":True,
      "original_genus_attrition_aggregate_csv_SHA256":digest(csvp)}
    (out_dir/"original_source_genus_attrition_verdict.json").write_text(
        json.dumps(verdict,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":STATUS,"axes":by},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--parquet",type=Path,required=True)
    p.add_argument("--traits-yml",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    analyze(a.parquet,a.traits_yml,a.out_dir)
