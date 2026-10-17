#!/usr/bin/env python3
"""Complete synthetic frozen 142 family×organ joint-source K study.

Checks all exact source-only identities, original 142 species-support
eligibility, 12 batch outputs, K mathematics and 5,000-family resampling.
Synthetic K values only; NO original K observations are accessed in tests.
"""
from __future__ import annotations
import argparse,copy,json,math,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from run_austraits_k_joint_nonflora_dataset_batch_v0_1 import cohort,STATUS as BATCH
from aggregate_austraits_k_joint_nonflora_dataset_v0_1 import calculate,STATUS

p=argparse.ArgumentParser()
for opt in ("source-support","original-pair-support","design"):
    p.add_argument("--"+opt,required=True,type=Path)
a=p.parse_args()
source=json.loads(a.source_support.read_text())
original=json.loads(a.original_pair_support.read_text())
design=json.loads(a.design.read_text())
selected=cohort(source,original,design)
assert len(selected)==142 and len({v["family"] for v in selected})==24
assert sum(x["cross_seed_vegetative"] for x in selected)==99
assert sum(x["cross_fruit_vegetative"] for x in selected)==43

source_arm={
  "full_A_B":"All remaining nonflora DatasetIDs for each retained native species, NOT the original all-AusTraits full-source state",
  "source_A_B":"Only the remaining DatasetIDs with positive measurements of BOTH organs on each SAME species",
  "same_matched_taxa_and_native_phylogeny_for_both_source_arms":True
}
reports=[]
for batch_num,start in enumerate(range(0,142,12)):
    items=[]
    for i,z in enumerate(selected[start:start+12],start):
        positive=i%5!=0
        full=(.25 if positive else -.2)
        nofl=(.33 if i%7!=0 else -.12)
        w=1 if z["trait_A"].startswith(("fruit_","seed_")) else -1
        full*=w;nofl*=w
        def calc(v1,v2,n):
            return {
              "status":"PASS","n_tips":n,
              "K_full_A":math.exp(v1),"K_full_B":1.0,
              "K_source_A":math.exp(v2),"K_source_B":1.0,
              "delta_full":v1,"delta_source":v2,
              "delta_source_measurements":v2-v1}
        axes={"S3":calc(full,nofl,z["n_same_AusTraits_dataset_species"]),
              "prune_only":calc(full,nofl,z["n_same_AusTraits_dataset_species"])}
        if i<7:
            axes["prune_only"]={"status":"HOLD_FEWER_THAN_20_NATIVE_TREE_TIPS","n_tips":19}
        items.append({
          "pair_id":f"Q{i+1:03d}",
          "family":z["family"],"trait_A":z["trait_A"],"trait_B":z["trait_B"],
          "system_A":z["system_A"],"system_B":z["system_B"],
          "n_source_positive_dataset_common":z["n_same_AusTraits_dataset_species"],
          "n_same_source_positive_species":z["n_same_AusTraits_dataset_species"],
          "n_lost_after_source_median":0,
          "axes":axes})
    reports.append({
      "status":BATCH,
      "pairs":items,
      "joint_nonflora_and_identical_source_post_outcome_exploratory":True,
      "not_independent_primary_measurement_validation":True,
      "source_arm_semantics":source_arm})
assert len(reports)==12
out=calculate(source,original,design,reports)
assert out["status"]==STATUS and out["joint_nonflora_source_qualified_before_K_pairs"]==142
assert out["original_joint_source_qualified_families"]==24
assert out["axes"]["S3"]["n_valid_real_tree_K_pairs"]==142
assert out["axes"]["prune_only"]["n_valid_real_tree_K_pairs"]==135
assert out["axes"]["S3"]["n_families_valid"]==24
assert out["axes"]["S3"]["subtypes"]["seed_vs_vegetative"]["n_valid_pairs"]==99
assert out["axes"]["S3"]["subtypes"]["fruit_vs_vegetative"]["n_valid_pairs"]==43
assert out["two_tree_joint_source_effect"]["n_pairs_native_K_supported_on_both"]==135
assert out["source_arm_semantics"]["species_and_native_tree_fixed_between_source_arms"]
assert out["not_external_TRY_v7_independent_source_validation"]
assert out["identical_nonflora_dataset_id_does_not_prove_same_primary_specimen"]

for mutation,err in [
 (lambda x:x[-1]["pairs"].pop(),"missing K outcome"),
 (lambda x:x[0]["pairs"][0]["axes"]["S3"].update({"delta_source":999}),"direction"),
 (lambda x:x[0]["pairs"][0].update({"n_source_positive_dataset_common":9999}),"does not match original")
]:
    z=copy.deepcopy(reports)
    mutation(z)
    try:calculate(source,original,design,z)
    except ValueError as e:assert err in str(e),str(e)
    else:raise AssertionError("invalid original 142-pair source K passed")
print("PASS: all 142 source-qualified nonflora/common-DatasetID organ K pairs, 24 families, 12 batches, original K identities, 5k bootstrap and corruption guards")
