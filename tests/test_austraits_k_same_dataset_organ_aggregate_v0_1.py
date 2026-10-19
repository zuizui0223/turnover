#!/usr/bin/env python3
"""Synthetic complete 279 frozen source-cohort K outputs, no empirical K needed.

Protect against family×pair K selection, changed positive source supports,
missing source batches and arithmetic inconsistency between K arms.
"""
import argparse,json,math,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from aggregate_austraits_k_same_dataset_organ_sensitivity_v0_1 import (
    calculate,STATUS)
from run_austraits_k_same_dataset_pair_batch_v0_1 import qualify
p=argparse.ArgumentParser()
for x in ("source-support","original-pair-support","design"):
    p.add_argument("--"+x,required=True,type=Path)
args=p.parse_args()
source=json.loads(args.__dict__["source_support"].read_text())
original=json.loads(args.__dict__["original_pair_support"].read_text())
design=json.loads(args.design.read_text())
selected=qualify(source,original,design)
assert len(selected)==279 and len({r["family"] for r in selected})==32
B=[]
for i in range(0,279,18):
    pp=[]
    for j,r in enumerate(selected[i:i+18],i):
        reproA=r["trait_A"].startswith(("fruit_","seed_"))
        sign=1 if reproA else -1
        full=sign*(0.40 if j%4!=0 else -0.25)
        restricted=sign*(0.5 if j%5!=0 else -0.1)
        d3={"status":"PASS","n_tips":r["n_same_AusTraits_dataset_species"],
            "K_full_A":math.exp(full),"K_full_B":1.0,
            "K_source_A":math.exp(restricted),"K_source_B":1.0,
            "delta_full":full,"delta_source":restricted,
            "delta_source_measurements":restricted-full}
        if j in range(13):
            pr={"status":"HOLD_FEWER_THAN_20_NATIVE_TREE_TIPS","n_tips":19}
        else:pr=copy.deepcopy(d3)
        pp.append({
           "pair_id":f"Q{j+1:03d}",
           "family":r["family"],"trait_A":r["trait_A"],"trait_B":r["trait_B"],
           "system_A":r["system_A"],"system_B":r["system_B"],
           "n_source_positive_dataset_common":r["n_same_AusTraits_dataset_species"],
           "n_same_source_positive_species":r["n_same_AusTraits_dataset_species"],
           "n_lost_after_source_median":0,
           "axes":{"S3":d3,"prune_only":pr}})
    B.append({"status":"AUSTRAITS_K_SAME_DATASET_PAIR_BATCH_COMPLETE",
        "pairs":pp,"post_organ_and_760_K_outcome_source_robustness":True,
        "NOT_independent_primary_measurement_validation":True,
        "n_original_K_blind_source_selected_pairs":len(pp)})
assert len(B)==16
x=calculate(source,original,design,B)
assert x["status"]==STATUS and x["source_qualified_before_K_pairs"]==279
assert x["axes"]["S3"]["n_valid_real_tree_K_pairs"]==279
assert x["axes"]["prune_only"]["n_valid_real_tree_K_pairs"]==266
assert x["axes"]["S3"]["common_dataset_source_same_tips"]["n_distinct_plant_families"]==32
assert x["axes"]["S3"]["subtypes"]["fruit_vs_vegetative"]["n_valid_pairs"]==159
assert x["axes"]["S3"]["subtypes"]["seed_vs_vegetative"]["n_valid_pairs"]==120
assert x["not_external_TRY_v7_independent_source_validation"]
assert x["same_dataset_id_not_same_primary_specimen"]
assert x["two_tree_joint_source_effect"]["n_pairs_native_K_supported_on_both"]==266
assert len(x["axes"]["S3"]["individual_families"])==32
for mutate,partial in [
    (lambda b:b.pop(),"missing K outcome"),
    (lambda b:b[0]["pairs"][0]["axes"]["S3"].update(
       delta_source_measurements=.99),"measurement delta"),
    (lambda b:b[0]["pairs"][0].update(
       n_source_positive_dataset_common=999999),"K result does not match")
]:
    bad=copy.deepcopy(B)
    mutate(bad)
    try:calculate(source,original,design,bad)
    except ValueError as exc:assert partial in str(exc),str(exc)
    else:raise AssertionError("mutated source-restricted K outcome accepted")
print("PASS: 279 frozen source-eligible organ K pairs, 32 families, 16 batches, whole-family bootstrap and K-value arithmetic integrity")
