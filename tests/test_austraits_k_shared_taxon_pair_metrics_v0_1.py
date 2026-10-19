#!/usr/bin/env python3
"""Fixture from frozen original source-support graph; NO real K outcome needed.

Test all 760 known qualified same-species comparisons with synthetic positive
K values, falsified support/graft identities and a missing pair.
"""
import argparse,copy,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from run_austraits_k_shared_taxon_pairs_batch_v0_1 import validate_batch
from aggregate_austraits_k_shared_taxon_pair_results_v0_1 import (
    audit_support_and_results,STATUS)

p=argparse.ArgumentParser()
p.add_argument("--support",required=True,type=Path)
a=p.parse_args()
support=json.loads(a.support.read_text())
design=json.loads((ROOT/"data"/"austraits_k_shared_taxa_cross_trait_design_v0_1.json").read_text())
q=[x for x in support["family_trait_pair_support"] if x["qualifies_20_common_species"]]
assert len(q)==760
validate_batch(q[:3],support,design)

parts=[]
for i in range(0,len(q),45):
    batch=[]
    for j,z in enumerate(q[i:i+45],i):
        kval1=.4+.004*(j%100)
        kval2=.3+.003*(j%100)
        delta=math.log(kval1/kval2)
        original=delta+.05
        axes={}
        for axis in ("S3","prune_only"):
            axes[axis]={"status":"PASS","n_tips":z["n_common_species_same_genus"],
               "K_A":kval1,"K_B":kval2,"delta_shared_logK":delta,
               "delta_original_logK":original,"delta_support_shift":delta-original}
        batch.append({"pair_id":f"B{i:04d}_{j:04d}",
          "family":z["family"],"trait_A":z["trait_A"],"trait_B":z["trait_B"],
          "system_A":z["system_A"],"system_B":z["system_B"],
          "n_shared_species":z["n_common_species_same_genus"],"axes":axes})
    parts.append({"status":"AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED",
                  "post_original_K_outcome_exploratory":True,
                  "n_family_trait_pairs":len(batch),"pairs":batch})
out=audit_support_and_results(support,parts,design)
assert out["status"]==STATUS
assert out["matched_source_graph"]["eligible_family_trait_pairs"]==760
assert out["axes"]["S3"]["n_supported_pairs"]==760
assert out["axes"]["prune_only"]["n_supported_pairs"]==760
assert len(out["trait_pair_summaries"])==66
assert len(out["five_frozen_discovery_named_trait_pairs"])==10
assert not out["trait_values_or_species_ids_persisted"]
bad=copy.deepcopy(parts)
bad[-1]["pairs"]=bad[-1]["pairs"][:-1]
bad[-1]["n_family_trait_pairs"]-=1
try:audit_support_and_results(support,bad,design)
except ValueError as e:assert "incomplete matched" in str(e)
else:raise AssertionError("incomplete 760 source-K graph accepted")
bad=copy.deepcopy(parts)
bad[0]["pairs"][0]["axes"]["S3"]["delta_shared_logK"]+=.1
try:audit_support_and_results(support,bad,design)
except ValueError as e:assert "identity inconsistent" in str(e)
else:raise AssertionError("inconsistent same-tree K ratio accepted")
bad=copy.deepcopy(q[:1])
bad[0]["n_common_species_same_genus"]+=1
try:validate_batch(bad,support,design)
except ValueError as e:assert "identity changed" in str(e)
else:raise AssertionError("silently changed shared-tip K eligibility")
print("PASS: complete synthetic 760 family×trait pairs, 66 types and 10 target pairs; no trait K leakage")
