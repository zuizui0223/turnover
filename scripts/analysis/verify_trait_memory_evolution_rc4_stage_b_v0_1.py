#!/usr/bin/env python3
"""No-outcome check of manuscript against frozen Stage B aggregate-only CI evidence."""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/"results/trait_memory_positive_only_cleaning_impact_v0_2/result.json"
MANUSCRIPT=ROOT/"docs/TRAIT_MEMORY_EVOLUTION_MANUSCRIPT_RC4_CLEANED_V0_1.md"
GATE=ROOT/"submission/EVOLUTION_RC4_STAGE_B_CLEANED_GATE.json"
def need(q, reason):
    if not q: raise AssertionError(reason)

def main():
    d=json.loads(RESULT.read_text(encoding="utf-8"))
    g=json.loads(GATE.read_text(encoding="utf-8"))
    m=MANUSCRIPT.read_text(encoding="utf-8")
    need(d["status"]=="TRAIT_MEMORY_POSITIVE_ONLY_CLEANING_IMPACT_COMPLETE","stage B incomplete")
    need(d["all_201_support_retained"] is True and d["all_201_cleaned_log_available"] is True,"cleaned support fails")
    need(d["data_contract_decision"]=="CLEANED_POSITIVE_ONLY_BECOMES_PRIMARY","primary source contract drift")
    need(g["status"]=="HOLD_ANONYMOUS_FORMATTED_PACKAGE_AND_AUTHOR_REVIEW","submission gate not HOLD")
    need(g["primary_evidence"]["original_successful_actions_run"]==37443037590,"source run drift")
    need(g["primary_evidence"]["systems"]==201 and g["primary_evidence"]["families"]==45 and g["primary_evidence"]["traits"]==12,"core drift")
    need("201/201" in m and "49" in m and "152" in m,"cleaning denominator missing")
    for scale in ("cleaned_raw","cleaned_log"):
        v=d[scale]
        for axis,name in (("S3","S3"),("prune_only","prune-only")):
            r=v["naive_repeatability"][axis]["R_family"]
            need(f"{r:.4f}" in m,f"missing {scale} {name} family R")
            p=v["portability"][axis]["gain_blup"]
            need(f"{p*100:.2f}%" in m,f"missing {scale} {name} BLUP gain")
    need("## References" in m and "## Materials and Methods" in m and "## Discussion" in m,"manuscript sections missing")
    for t in ("raw", "log", "species", "family", "trait", "uncertainty", "HOLD"):
        need(t.lower() in m.lower(),f"mandatory text missing: {t}")
    for old in (
        "### The planned log-scale sensitivity could not be completed on the frozen population",
        "The raw-versus-log scale sensitivity remains unresolved",
        "trait identity provides almost no robust information",
        "This source is submission ready",
        "the scale of trait memory is inherently unportable",
    ):
        need(old not in m,f"stale / overly strong scientific claim: {old}")
    for k in ("S3","prune"):
        p=d["effect_impact"][k]
        need(0<=p["median_abs_delta"]<=p["max_abs_delta"]<1,"nonfinite effect change")
        need(p["n_abs_delta_ge_0_05"]<=p["n_abs_delta_ge_0_01"]<=49,"effect-change count drift")
    for scale in ("cleaned_raw","cleaned_log"):
        for key in ("S3_total_point_shares","prune_total_point_shares"):
            vals=d[scale]["measurement_aware"][key]
            need(math.isclose(sum(vals.values()),1,abs_tol=1e-9),"variance-share arithmetic drift")
    need(g["manuscript"]["cleaned_201_source_row_effects_restored"] is True,"validated source effects not marked recovered")
    need(g["manuscript"]["figure_source_validation_success"] is True,"source figure gate not recorded")
    need(g["manuscript"]["formal_submission_ready"] is False,"unreviewed submission gate changed")
    need(g["manuscript"]["old_RC3_submission_HOLD_preserved"] is True,"RC3 HOLD unexpectedly overridden")
    out={
        "status":"EVOLUTION_RC4_STAGE_B_EDITORIAL_QA_PASS",
        "source_result":str(RESULT.relative_to(ROOT)),
        "primary_design":"201 systems, 45 families, 12 continuous traits",
        "reproduced_claims_from_same_json":True,
        "raw_vs_log_required":True,
        "submission_ready":False,
        "scientific_model_fits":0,
    }
    print(json.dumps(out,indent=2))
if __name__=="__main__":
    main()
