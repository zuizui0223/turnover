#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

root=Path(".")
def loadj(p):
    return json.loads((root/p).read_text())

m=loadj("results/phylo_memory_measurability_v0_1/result.json")
c=loadj("results/phylo_memory_calibration_ceiling_v0_2/result.json")
e=loadj("results/phylo_memory_binary_ceiling_v0_3_1/result.json")
v=loadj("results/phylo_memory_binary_validity_tradeoff_v0_3_1/result.json")
k=loadj("results/phylo_memory_mk2_generator_v0_4_1/result.json")
b=loadj("results/phylo_memory_balance_normalized_v0_5/result.json")
z=loadj("data/phylo_memory_mechanism_close_v0_5_3.json")
plan=loadj("data/phylo_memory_figure_plan_v0_1.json")

abstract=(root/"docs/PHYLO_MEMORY_ABSTRACT_V0_1.md").read_text()
paper=(root/"docs/PHYLO_MEMORY_ASSIGNABILITY_MANUSCRIPT_V0_2.md").read_text()
caps=(root/"docs/PHYLO_MEMORY_FIGURE_CAPTIONS_V0_1.md").read_text()
boundary=(root/"docs/PHYLO_MEMORY_NOVELTY_BOUNDARY_V0_1.md").read_text()

assert z["status"]=="PHYLO_MEMORY_PRIMARY_MECHANISM_PROGRAMME_CLOSED"
assert m["n_systems"]==722
assert c["semantic_summary"]["nominal_categorical"]["n"]==276
assert e["original_no_bracket"]["n"]==220
assert v["categorical_no_bracket"]["mechanism_counts"]=={"EFFECT_CEILING":195,"VALIDITY_COLLAPSE":25}
assert k["mk2"]["n_no_bracket"]==170
assert b["geometry_availability"]=={
  "n_analyzed":272,
  "n_geometry_hold":4,
  "held_original_mk2_calibrated":1,
  "held_original_mk2_no_bracket":3,
  "rule":"Exact frozen-geometry identity only; held systems have no balance-normalized outcome."
}

required={
 "722": [abstract,paper],
 "56.2%": [abstract,paper],
 "2.15%": [abstract,paper],
 "79.7%": [abstract,paper,caps,boundary],
 "61.6%": [abstract,paper,caps,boundary],
 "42.4–43.8%": [abstract,paper,caps,boundary],
 "34.9%": [abstract,paper,caps],
 "195": [paper,caps],
 "25": [paper,caps],
 "51": [paper,caps],
 "50": [paper,caps],
 "8.88": [paper]
}
for token,docs in required.items():
    for doc in docs:
        assert token in doc, f"missing {token}"

for stale in [
    "The active v0.5 test",
    "active gate is now",
    "next test keeps Mk2",
    "next mechanism test",
    "v0.5 test therefore keeps"
]:
    assert stale not in paper, f"stale forward-looking wording in paper: {stale}"

assert ("all 220" in paper or "220/220" in paper), "paper must state that all 220 OU no-bracket systems were structurally realizable"
assert ("220/220" in boundary or "all 220" in boundary), "novelty boundary must retain the 220-system structural witness claim"
assert "No additional generator, estimator, target, grid extension or outcome-based subgroup search" in paper
assert "structural realizability" in abstract and "generator accessibility" in abstract and "recovery" in abstract
assert "failed known-truth simulation" in abstract and "low statistical power" in abstract
assert [f["id"] for f in plan["figures"]]==["Fig1","Fig2","Fig3"]
assert plan["figures"][2]["primary_values"]["mk2_to_balance_rescue_n"]==50
assert plan["figures"][2]["primary_values"]["mk2_to_balance_new_failure_n"]==0

print(json.dumps({
  "status":"PHYLO_MEMORY_PAPER_PACKAGE_VERIFIED",
  "manuscript":"docs/PHYLO_MEMORY_ASSIGNABILITY_MANUSCRIPT_V0_2.md",
  "figures":["Fig1","Fig2","Fig3"],
  "mechanism_closed":True
},indent=2))
