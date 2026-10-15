#!/usr/bin/env python3
"""Full frozen-graph SYNTHETIC K orientation test, no actual K outcomes used.

Ensures family-only LOFO, both-tree tip holds, functional module grouping,
and 42-family bootstrap graphs do not silently change the 760 source cohort.
"""
import argparse,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_k_functional_module_lofo_v0_1 import (
    audit,source_data,STATUS)

p=argparse.ArgumentParser()
p.add_argument("--support",required=True,type=Path)
arg=p.parse_args()
support=json.loads(arg.support.read_text())
design=json.loads((ROOT/"data"/"austraits_k_functional_module_portability_v0_1.json").read_text())
margin=json.loads((ROOT/"data"/"austraits_k_shared_tip_margin_sensitivity_v0_1.json").read_text())
rows=sorted((x for x in support["family_trait_pair_support"]
             if x["qualifies_20_common_species"]),
             key=lambda x:(x["family"],x["trait_A"],x["trait_B"]))
assert len(rows)==760
rng=np.random.default_rng(20261015)
flip3=set(map(int,rng.choice(760,151,replace=False)))
within_prune=[];between_prune=[]
rep=set(design["fixed_organ_classes"]["reproductive"])
for i,z in enumerate(rows):
    if z["family"]=="Fabaceae":
        (between_prune if (z["trait_A"] in rep)!=(z["trait_B"] in rep) else within_prune).append(i)
holds=set(between_prune[:9]+within_prune[:4])
assert len(holds)==13
allow_prune=[i for i in range(760) if i not in holds]
flipP=set(map(int,rng.choice(allow_prune,137,replace=False)))
batches=[]
for start in range(0,760,32):
    pp=[]
    for i,z in enumerate(rows[start:start+32],start):
        repA=(z["trait_A"] in rep); repB=(z["trait_B"] in rep)
        target=repA if repA!=repB else (i%3==0)
        y=target if i%11!=0 else not target
        delta=(0.4 if y else -0.4)
        axis={}
        for ax in ("S3","prune_only"):
            if ax=="prune_only" and i in holds:
                axis[ax]={"status":"HOLD_FEWER_THAN_20_MATCHED_TIPS","n_tips":19}
                continue
            orig=-delta if (i in (flip3 if ax=="S3" else flipP)) else delta
            axis[ax]={"status":"PASS","n_tips":int(z["n_common_species_same_genus"]),
                      "K_A":math.exp(delta),"K_B":1.0,
                      "delta_shared_logK":delta,
                      "delta_original_logK":orig,
                      "delta_support_shift":delta-orig}
        pp.append({"pair_id":f"P{i+1:04d}",
           "family":z["family"],"trait_A":z["trait_A"],"trait_B":z["trait_B"],
           "system_A":z["system_A"],"system_B":z["system_B"],
           "n_shared_species":z["n_common_species_same_genus"],
           "axes":axis})
    batches.append({"status":"AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED",
        "post_original_K_outcome_exploratory":True,
        "n_family_trait_pairs":len(pp),"pairs":pp})
assert len(batches)==24
result=audit(support,batches,design,margin)
assert result["status"]==STATUS
m=result["reproductive_vegetative_matched_tip"]
assert m["S3"]["n_supported_family_pair_observations"]==406
assert m["prune_only"]["n_supported_family_pair_observations"]==397
assert m["S3"]["n_independent_families_with_cross_organ_comparisons"]==34
assert result["reproductive_vegetative_both_trees"]["n_evaluable_on_both_trees"]==397
s=result["left_one_whole_family_out_prediction"]
assert s["S3"]["all_source_eligible_pairs"]["n_families"]==42
assert s["prune_only"]["all_source_eligible_pairs"]["scores"]["reproductive_vegetative"]["heldout_family_pair_rows"]==747
assert not result["independent_TRY_v7_validation"]
assert not result["new_OU_Brownian_process_parameters_fitted"]
assert result["no_raw_trait_values_species_ids_exported"]
print("PASS: synthetic 760 shared-tree K pairs, 34 family module graph, 42 leave-one-family folds, no independent source claim")
