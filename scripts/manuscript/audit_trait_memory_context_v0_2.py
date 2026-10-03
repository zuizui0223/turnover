#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "paper" / "trait_memory_context_manuscript_v0_2.md"
EFFECTS = ROOT / "results" / "trait_memory_context_synthesis_v0_1" / "effects.csv"
SYN = ROOT / "results" / "trait_memory_context_synthesis_v0_1" / "result.json"
REP = ROOT / "results" / "trait_memory_repeatability_v0_2" / "result.json"
PORT = ROOT / "results" / "trait_memory_portability_v0_2" / "result.json"
LIN = ROOT / "results" / "lineage_memory_repeatability_v0_2" / "result.json"
MANIFEST = ROOT / "data" / "trait_memory_context_submission_manifest_v0_1.json"

EXPECTED_EFFECT_SHA = "5fffdfbc9ab50ff7bf568e80537a290e11c2bfde02f1d5484c7e896ed5f9415b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    with EFFECTS.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert sha256(EFFECTS) == EXPECTED_EFFECT_SHA
    assert len(rows) == 201
    assert len({r["family"] for r in rows}) == 45
    assert len({r["trait_name"] for r in rows}) == 12
    assert all(r["semantic_class"] == "continuous_scalar" for r in rows)

    syn = json.loads(SYN.read_text())
    rep = json.loads(REP.read_text())
    port = json.loads(PORT.read_text())
    lin = json.loads(LIN.read_text())
    manifest = json.loads(MANIFEST.read_text())

    assert syn["common_core"]["systems"] == 201
    assert syn["common_core"]["families"] == 45
    assert syn["common_core"]["traits"] == 12
    assert syn["common_core"]["S3_effect_identity_across_three_execution_routes"]["max_absolute_difference"] == 0
    assert syn["common_core"]["prune_only_effect_identity_across_three_execution_routes"]["max_absolute_difference"] == 0

    assert abs(rep["primary_S3"]["R_family"] - 0.1504) < 1e-12
    assert abs(rep["primary_S3"]["R_trait"] - 0.0433) < 1e-12
    assert abs(rep["primary_S3"]["R_residual"] - 0.8063) < 1e-12
    assert rep["dominance_comparison_performed"] is False

    assert abs(port["S3"]["gain"] - (-0.024170328345234804)) < 1e-12
    assert abs(port["S3"]["p_value"] - 0.091) < 1e-12
    assert abs(port["prune_only"]["gain"] - (-0.032420909192963476)) < 1e-12
    assert abs(port["prune_only"]["p_value"] - 0.193) < 1e-12
    assert port["robust_portability_pass"] is False

    assert abs(lin["primary_S3"]["conditional_family_repeatability"] - 0.1825) < 1e-12
    assert lin["bootstrap"]["ci95_conditional_family_repeatability"] == [0.0285, 0.3369]
    assert lin["interpretation"] == "UNCERTAIN_RELATIVE_TO_10_PERCENT_REFERENCE"

    assert manifest["canonical_effects"]["sha256"] == EXPECTED_EFFECT_SHA
    assert manifest["canonical_effects"]["rows"] == 201

    required_text = [
        "201 family x trait systems",
        "45 vascular-plant families",
        "12 continuous traits",
        "gain = -0.0242",
        "p = 0.091",
        "gain = -0.0324",
        "p = 0.193",
        "0.150",
        "0.043",
        "0.806",
        "0.183",
        "0.029-0.337",
        "Spearman rho = 0.832",
        "## Data and code availability",
        "## Figure captions",
        "**Figure 1.",
        "**Figure 2.",
        "**Figure 3.",
        "**Figure 4.",
    ]
    for needle in required_text:
        assert needle in text, f"missing manuscript text: {needle}"

    prohibited = [
        "family effects dominate trait effects",
        "trait effects are zero",
        "80.6% is family x trait interaction",
        "80.6% is family × trait interaction",
        "family repeatability confidently exceeds 10%",
        "phylogenetic memory is mainly a family property",
    ]
    claim_text = text.split("## Hard nonclaims", 1)[0].lower()
    for phrase in prohibited:
        assert phrase.lower() not in claim_text, f"prohibited claim found in inferential prose: {phrase}"

    figdir = ROOT / "figures" / "trait_memory_context_v0_2"
    for name in [
        "figure1_crossed_design.png",
        "figure1_crossed_design.pdf",
        "figure2_memory_matrix.png",
        "figure2_memory_matrix.pdf",
        "figure3_triangulation.png",
        "figure3_triangulation.pdf",
        "figure4_backbone_sensitivity.png",
        "figure4_backbone_sensitivity.pdf",
    ]:
        path = figdir / name
        assert path.exists() and path.stat().st_size > 0, f"missing/empty figure {name}"

    out = {
        "status": "TRAIT_MEMORY_MANUSCRIPT_AUDIT_PASS",
        "canonical_effect_sha256": EXPECTED_EFFECT_SHA,
        "n_systems": 201,
        "n_families": 45,
        "n_traits": 12,
        "figures_verified": 8,
        "prohibited_claims_checked": len(prohibited),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
