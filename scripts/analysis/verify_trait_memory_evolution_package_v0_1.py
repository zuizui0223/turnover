#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
from __future__ import annotations
import json,re
from pathlib import Path

root=Path(".")
paper=(root/"docs/TRAIT_MEMORY_EVOLUTION_MANUSCRIPT_V0_3.md").read_text()
abstract=(root/"docs/TRAIT_MEMORY_EVOLUTION_ABSTRACT_V0_1.md").read_text()
caps=(root/"docs/TRAIT_MEMORY_FIGURE_CAPTIONS_V0_2.md").read_text()
nov=(root/"docs/TRAIT_MEMORY_NOVELTY_BOUNDARY_V0_2.md").read_text()
syn=json.loads((root/"results/trait_memory_context_synthesis_v0_2/result.json").read_text())
meas=json.loads((root/"results/trait_memory_measurement_aware_v0_3/result.json").read_text())
corr=json.loads((root/"results/trait_memory_correlated_trait_null_v0_3/result.json").read_text())
blup=json.loads((root/"results/trait_memory_portability_blup_v0_3/result.json").read_text())
plan=json.loads((root/"data/trait_memory_figure_plan_v0_1.json").read_text())

assert syn["status"]=="TRAIT_MEMORY_CONTEXT_SYNTHESIS_POST_ROBUSTNESS"
assert syn["hypotheses"]["H1_trait_intrinsic_memory"]["decision"]=="NOT_SUPPORTED"
assert syn["hypotheses"]["H2_family_context_memory"]["decision"]=="SUPPORTED_AS_MODEST_REPEATABLE_PATTERN"
assert meas["status"]=="TRAIT_MEMORY_MEASUREMENT_AWARE_ESTIMATED"
assert corr["status"]=="TRAIT_MEMORY_CORRELATED_TRAIT_NULL_ESTIMATED"
assert blup["status"]=="TRAIT_MEMORY_BLUP_PORTABILITY_SENSITIVITY_ESTIMATED"

for heading in ["## Teaser text","## Abstract","## Keywords","## Introduction","## Materials and Methods","## Results","## Discussion"]:
    assert heading in paper, heading

for token in [
    "201 family × trait systems",
    "45 vascular-plant families",
    "12 continuous traits",
    "0.006",
    "−0.0048",
    "0.017",
    "0.009",
    "24.2%",
    "lineage-contingent"
]:
    assert token in paper, token

for token in [
    "S3 gain = 0.006",
    "prune-only = −0.0048",
    "S3 p = 0.017",
    "prune-only p = 0.009"
]:
    assert token in abstract, token

for forbidden in [
    "most phylogenetic memory is system-specific",
    "family context dominates trait identity",
    "family effects dominate trait effects",
    "raw-scale result is robust to log transformation"
]:
    assert forbidden not in paper.lower(), forbidden
    assert forbidden not in abstract.lower(), forbidden

assert "there is little portable trait-level memory information to borrow" in paper.lower()
assert "trait identity provides almost no robust information" in paper.lower() or "trait identity carried little robust information" in paper.lower()
assert "do not state that:" in paper.lower() and "trait identity is anti-portable" in paper.lower()

assert "distance-based memory descriptor" in paper
assert "not a claim to replace standard phylogenetic-signal metrics" in paper
assert "log-scale sensitivity" in paper
assert "post-outcome" in paper.lower()

word_re=re.compile(r"\b[\w’'−-]+\b",re.UNICODE)
# Evolution format limits.
abstract_body=paper.split("## Abstract",1)[1].split("## Keywords",1)[0]
teaser_body=paper.split("## Teaser text",1)[1].split("## Abstract",1)[0]
keywords_line=paper.split("## Keywords",1)[1].split("## Introduction",1)[0].strip().splitlines()[0]
keywords=[x.strip() for x in keywords_line.split(";") if x.strip()]
assert len(word_re.findall(abstract_body)) <= 200, len(word_re.findall(abstract_body))
assert len(word_re.findall(teaser_body)) <= 100, len(word_re.findall(teaser_body))
assert 3 <= len(keywords) <= 6, keywords
for abbr in ["S3","BLUP"]:
    assert abbr not in abstract_body, abbr
assert "GPT-5.6 Sol" in paper
assert "accessed 5 October 2026" in paper
assert "Prompts were conversational natural-language instructions" in paper
assert "no fixed prompt template or external application programming interface was used" in paper
body=paper.split("## Introduction",1)[1]
if "## References" in body:
    body=body.split("## References",1)[0]
word_count=len(word_re.findall(body))
assert word_count <= 7500, word_count

assert plan["version"]=="v0.2"
assert "measurement-aware" in str(plan["figures"]["figure1"]).lower()
assert "correlated-trait" in str(plan["figures"]["figure2"]).lower()
assert "blup" in str(plan["figures"]["figure3"]).lower()

assert "estimated strength of evolutionary memory for a named trait is itself transferable across clades" in nov
assert "lineage-level repeatability persists" in nov
assert "trait identity supplies almost no robust held-out-family predictive gain" in nov
assert "Figure 1." in caps and "Figure 2." in caps and "Figure 3." in caps
assert "## Keywords" in abstract
assert "S3" not in abstract and "BLUP" not in abstract

print(json.dumps({
  "status":"TRAIT_MEMORY_EVOLUTION_PACKAGE_VERIFIED",
  "manuscript_body_words":word_count,
  "central_claim":syn["central_claim"],
  "figures":["Fig1","Fig2","Fig3"]
},indent=2))
