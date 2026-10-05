#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
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
clar=loadj("data/phylo_memory_structural_claim_clarification_v0_3_2.json")
plan=loadj("data/phylo_memory_figure_plan_v0_1.json")

abstract=(root/"docs/PHYLO_MEMORY_ABSTRACT_V0_1.md").read_text()
paper=(root/"docs/PHYLO_MEMORY_ASSIGNABILITY_MANUSCRIPT_V0_2.md").read_text()
caps=(root/"docs/PHYLO_MEMORY_FIGURE_CAPTIONS_V0_1.md").read_text()
boundary=(root/"docs/PHYLO_MEMORY_NOVELTY_BOUNDARY_V0_1.md").read_text()
supp=(root/"docs/PHYLO_MEMORY_SUPPLEMENTARY_METHODS_V0_1.md").read_text()
titlepage=(root/"docs/PHYLO_MEMORY_MEE_TITLE_PAGE_TEMPLATE_V0_1.md").read_text()

assert z["status"]=="PHYLO_MEMORY_PRIMARY_MECHANISM_PROGRAMME_CLOSED"
assert clar["status"]=="INTERPRETATION_CLARIFICATION_NO_NEW_ANALYSIS"
assert clar["new_outcomes_computed"] is False and clar["new_system_level_analysis"] is False
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
 "56.2%": [paper],
 "2.15%": [paper],
 "14.7%": [abstract,paper,caps],
 "13.3%": [abstract,paper,caps],
 "13.8%": [abstract,paper,caps],
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

assert ("220/220" in paper or "all 220" in paper), "paper must retain the all-220 one-sided structural witness result"
assert ("220/220" in boundary or "all 220" in boundary), "novelty boundary must retain the 220-system structural witness claim"
assert ("prohibited additional generator" in supp.lower() or "prohibited additional" in supp.lower() or ("additional generator" in supp.lower() and "outcome-defined subgroup" in supp.lower())), "supplement must preserve the closed mechanism stop rule"
assert "structural feasibility" in abstract and "generator accessibility" in abstract and "recovery" in abstract
assert "Supplementary Methods S1" in paper
assert "## S1. Exact binary state-balance attenuation identity" in supp
assert "## S2. Prospective mechanism sequence and stop rule" in supp
assert "docs/PHYLO_MEMORY_" not in paper
assert "data/phylo_memory_" not in paper
assert "## Figure mapping" not in paper and "## Analysis closure" not in paper
abstract_body=paper.split("## Abstract",1)[1].split("## Data and code for peer review",1)[0]
word_re=re.compile(r"\b[\w’'-]+\b",re.UNICODE)
assert len(word_re.findall(abstract_body)) <= 350
kw_line=paper.split("## Keywords",1)[1].split("## Introduction",1)[0].strip().splitlines()[0]
keywords=[x.strip() for x in kw_line.split(";") if x.strip()]
assert len(keywords) <= 8
assert keywords == sorted(keywords,key=str.casefold)
combined_words=len(word_re.findall(paper))+len(word_re.findall(caps))
assert combined_words <= 8000
headline=titlepage.split("## Running headline",1)[1].split("##",1)[0].strip()
assert len(headline) <= 45
assert all(f"\n{i}. " in abstract for i in range(1,5)), "MEE abstract must contain numbered points 1-4"
assert "65.0 percentage points" in abstract
assert "Structural feasibility does not guarantee generator accessibility" in abstract
assert "feasibility" in boundary.lower() and "generator accessibility" in boundary.lower()
assert "failed known-truth simulation" in abstract and "low statistical power" in abstract
assert "one-sided" in paper.lower() and "calibration tolerance" in paper.lower()
assert "identical categorical target" not in caps.lower()
assert "delta_rank = 0.30 rather than rho" in caps.lower()
assert "diagnostic re-expression rather than the identical rho estimand" in paper.lower()
assert "51/220" in abstract and "1/56" in abstract
assert "paired reversal directly demonstrates generator-specific target accessibility" in abstract.lower()
assert "does not by itself prove exact target attainability" in caps.lower()
assert "hard one-transition" in abstract.lower()
for forbidden in [
    "all 276 categorical trees could structurally express the target",
    "target was explicitly realizable on every tree",
    "structurally realizable on every categorical tree"
]:
    assert forbidden not in paper.lower()
    assert forbidden not in abstract.lower()
assert [f["id"] for f in plan["figures"]]==["Fig1","Fig2","Fig3"]
assert plan["figures"][0]["primary_values"]["continuous_no_bracket"]==60
assert plan["figures"][0]["primary_values"]["continuous_recovery_fail_after_assignment"]==54
assert plan["figures"][0]["primary_values"]["continuous_s3_recovery_pass"]==293
assert plan["figures"][0]["primary_values"]["categorical_no_bracket"]==220
assert plan["figures"][0]["primary_values"]["categorical_recovery_fail_after_assignment"]==38
assert plan["figures"][0]["primary_values"]["categorical_s3_recovery_pass"]==18
assert plan["figures"][2]["primary_values"]["mk2_to_balance_rescue_n"]==50
assert plan["figures"][2]["primary_values"]["mk2_to_balance_new_failure_n"]==0

print(json.dumps({
  "status":"PHYLO_MEMORY_PAPER_PACKAGE_VERIFIED",
  "manuscript":"docs/PHYLO_MEMORY_ASSIGNABILITY_MANUSCRIPT_V0_2.md",
  "figures":["Fig1","Fig2","Fig3"],
  "mechanism_closed":True
},indent=2))
