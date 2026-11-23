#!/usr/bin/env python3
"""Fail-closed provenance/causal-edge audit for turnover, no original biological data."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "data/turnover_causal_bridge_audit_20261124.json"

def git_blob_sha(contents: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(contents)).encode("ascii") + b"\0" + contents).hexdigest()

def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    raw = (ROOT / audit["registry_path"]).read_bytes()
    registry = json.loads(raw.decode("utf-8"))
    assert git_blob_sha(raw) == audit["registry_git_blob_sha"], "Registry changed: review source mapping before accepting"
    original = registry["claims"]
    expected_ids = [x["id"] for x in original]
    mapped = audit["claim_programmes"]
    actual_ids = [x["claim_id"] for x in mapped]
    assert len(expected_ids) == len(set(expected_ids)) == 21
    assert len(actual_ids) == len(set(actual_ids)) == 21
    assert set(actual_ids) == set(expected_ids)
    groups = {x["claim_id"]: x["source_programme"] for x in mapped}
    for same_source in (
        ("BIEN-FAMILY-COMPONENT","BIEN-RAW-PORTABILITY","BIEN-ERROR-ROBUSTNESS","BIEN-LOG-EXPLORATORY","BIEN-STAGEB-CORRECTED"),
        ("AUSTRAITS-RHO-FAMILY","AUSTRAITS-K-ALLOCATION","ORGAN-K"),
        ("BIODEPTH-HEIGHT-FD","BIODEPTH-PD"),
    ):
        assert len({groups[k] for k in same_source}) == 1, "Reused original source counted multiple times"
    assert groups["JENA-ORIGINAL-SOURCE"] != groups["JENA-TBE-2012-ASSIGNED-FD-MONO-NDE-ACCOUNTING"]
    assert groups["JENA-TBE-2012-ASSIGNED-FD-MONO-NDE-ACCOUNTING"] == "Jena-TBE-Wagg2017"
    roles = {x["claim_id"]: x["audit_role"] for x in mapped}
    for item in original:
        if item["status"] == "source_hold":
            assert roles[item["id"]] in ("source_hold_only", "multi_source_gate_only")
    allowed = {"not_identified","positive_generalization_not_supported","arithmetic_identity_not_causal","published_total_treatment_evidence_only"}
    edges = {x["edge"]: x["status"] for x in audit["edge_gates"]}
    assert len(edges) == len(audit["edge_gates"]) == 7
    assert all(x in allowed for x in edges.values()), "Unapproved causal upgrade"
    assert edges["family_trait_memory_to_plot_functional_diversity"] == "not_identified"
    assert edges["designed_preplant_FD_to_signed_NDE"] == "not_identified"
    assert edges["FD_to_absolute_biomass"] == "not_identified"
    z = audit["jena_tbe_rounded_checks"]
    d = z["estimates_g_dry_m2"]
    assert abs(d["delta_B"] - (d["delta_E"] + d["delta_NDE"])) < 0.011
    assert abs(d["delta_NDE"] - (d["delta_CE"] + d["delta_SE"])) < 0.011
    assert all(lo < 0 < hi for lo, hi in z["bootstrap_95ci_g_dry_m2"].values())
    assert z["n_matched_mixture_plots"] == 84 and z["n_monoculture_plots"] == 24
    assert audit["new_biological_effect_fits"] == 0
    statuses = Counter(x["status"] for x in original)
    assert sum(statuses.values()) == 21
    print("PASS: 21 claims exhaustively mapped to sources; shared experiments not multiplied")
    print("PASS: 7 directed-edge statements prevent FD-only or K-to-biomass causal promotion")
    print("PASS: Jena TBE adjusted contrasts satisfy two accounting identities; all five CIs cross zero")
    print("PASS: no new effect fits; original source registry SHA pinned")

if __name__ == "__main__":
    main()
