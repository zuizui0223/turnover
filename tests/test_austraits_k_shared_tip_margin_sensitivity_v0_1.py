#!/usr/bin/env python3
"""Synthetic K signs on EXACT frozen 760 family×pair support: no real matched
K outcomes required for this correctness test. Missing/corrupt graph fails.
"""
from __future__ import annotations
import argparse,copy,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_k_shared_tip_margin_sensitivity_v0_1 import (
    load_rows,run,STATUS)

p=argparse.ArgumentParser()
p.add_argument("--support",required=True,type=Path)
args=p.parse_args()
support=json.loads(args.support.read_text())
design=json.loads((ROOT/"data"/"austraits_k_shared_tip_margin_sensitivity_v0_1.json").read_text())
qualified=sorted((z for z in support["family_trait_pair_support"]
                  if z["qualifies_20_common_species"]),
                 key=lambda z:(z["family"],z["trait_A"],z["trait_B"]))
assert len(qualified)==760
rng=np.random.default_rng(20261015)
s3flip=set(map(int,rng.choice(760,151,replace=False)))
pruneholds=set(i for i,z in enumerate(qualified) if z["family"]=="Fabaceae")
pruneholds=set(sorted(pruneholds)[:13])
assert len(pruneholds)==13
pruneflip=set(map(int,rng.choice([i for i in range(760) if i not in pruneholds],137,replace=False)))
batches=[]
for start in range(0,760,32):
    batch=[]
    for i,z in enumerate(qualified[start:start+32],start):
        orig=float(.05+.1*(i%23))
        axes={}
        for axis in ("S3","prune_only"):
            if axis=="prune_only" and i in pruneholds:
                axes[axis]={"status":"HOLD_FEWER_THAN_20_MATCHED_TIPS",
                            "n_tips":19}
                continue
            isflip=(i in s3flip if axis=="S3" else i in pruneflip)
            matched=-.5*orig if isflip else .75*orig
            axes[axis]={"status":"PASS",
               "n_tips":int(z["n_common_species_same_genus"]),
               "K_A":float(math.exp(matched)),
               "K_B":1.0,
               "delta_shared_logK":matched,
               "delta_original_logK":orig,
               "delta_support_shift":matched-orig}
        batch.append({"family":z["family"],"trait_A":z["trait_A"],
            "trait_B":z["trait_B"],"system_A":z["system_A"],
            "system_B":z["system_B"],
            "n_shared_species":z["n_common_species_same_genus"],
            "axes":axes})
    batches.append({"status":"AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED",
        "post_original_K_outcome_exploratory":True,
        "n_family_trait_pairs":len(batch),"pairs":batch})
data=load_rows(support,batches,design)
assert len(data)==1507
assert data[data.axis=="S3"].flip.sum()==151
assert data[data.axis=="prune_only"].flip.sum()==137
x=run(support,batches,design)
assert x["status"]==STATUS and x["source_support_graph"]["families"]==42
assert x["both_axes"]["paired_family_trait_pairs"]==747
assert x["axes"]["S3"]["total"]["n_flips"]==151
assert x["axes"]["prune_only"]["total"]["n_flips"]==137
assert len(x["axes"]["S3"]["strata"]["original_abs_logK"])==5
assert len(x["axes"]["S3"]["strata"]["shared_fraction_larger"])==5
assert x["no_Try_independent_validation"] and x["post_outcome_exploratory"]
for mutate,expect in [
 (lambda b:b.pop(),"not 24"),
 (lambda b:b[0]["pairs"][0]["axes"]["S3"].update({"delta_shared_logK":99}),"nonmatching"),
 (lambda b:b[0]["pairs"][0].update({"n_shared_species":99999}),"identity")
]:
    corrupted=copy.deepcopy(batches)
    mutate(corrupted)
    try:load_rows(support,corrupted,design)
    except ValueError as e:assert expect in str(e),str(e)
    else:raise AssertionError("malformed simulation should fail: "+expect)
print("PASS: 760 fixed pair synthetic K identity, 42-family resampling, 12 pair types, 747 prune, fail-closed inputs")
