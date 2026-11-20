#!/usr/bin/env python3
"""Numerical/claim QA for single-source retrospective 2017 FD/NDE pilot.
No source re-fitting or new outcome tests.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
SOURCE=BASE/"results/cadotte_2017_same_mixture_fd_nde_pilot_v0_1.json"

def check(v,msg):
    if not v:raise AssertionError(msg)

def run():
    x=json.loads(SOURCE.read_text(encoding="utf-8"))
    check(x["source_status"]=="ORIGINAL_SOURCE_IDENTITIES_AND_JOIN_PASS","source gate false")
    check(x["analysis_status"]=="RETROSPECTIVE_EXPLORATORY_CV_PILOT_COMPLETE","no completed fit")
    check(x["outcome_preview_and_published_directions_seen_before_pilot_protocol"] is True,
          "retrospective design provenance lost")
    check(x["no_causal_FD_mediation_claim"] and x["no_global_generalization_claim"],"unwarranted inference")
    check(x["no_original_species_rows_redistributed"],"raw data redistribution")
    assert len(x["original_MD5_provenance"])==4
    ss=x["source_counts"]
    check(ss["source_joined_mixture_rows"]==40 and ss["unique_source_composition_groups"]==34,
          "support count drift")
    check(ss["source_original_trait_taxa"]==14,"source trait roster drift")
    for k in ("biomass_original_cross_source_failures","component_identity_failures",
              "sown_vs_realized_richness_mismatches"):
        check(ss[k]==0,"original response/source identity mismatch: "+k)
    e=x["effect"]
    check(e["composition_bootstrap_replicates"]==1000 and e["source_group_holdout_count"]==34,
          "bootstrap contract drift")
    check(set(e["endpoint_predictive_gain"])=={"mass","NDE","COMP","SELECT"},
          "selected outcome axes drifted")
    checks=0
    for label,z in e["endpoint_predictive_gain"].items():
        pred=1-z["sse_fd_added"]/z["sse_baseline"]
        check(math.isclose(pred,z["gain"],rel_tol=0,abs_tol=1e-12),
              f"original SSE arithmetic drift: {label}")
        ci=z["composition_bootstrap_ci95"]
        check(len(ci)==2 and all(math.isfinite(v) for v in ci) and ci[0]<=ci[1],
              "invalid original bootstrap CI")
        checks+=2
    diff=e["endpoint_predictive_gain"]["NDE"]["gain"]-e["endpoint_predictive_gain"]["mass"]["gain"]
    check(math.isclose(diff,e["descriptive_gain_difference_NDE_minus_absolute_mass"],abs_tol=1e-14),
          "paired gain difference drift")
    check(e["paired_group_bootstrap_ci95"][0]<0<e["paired_group_bootstrap_ci95"][1],
          "the descriptive paired 95% interval no longer straddles zero")
    check(e["endpoint_predictive_gain"]["mass"]["gain"]>0 and
          e["endpoint_predictive_gain"]["NDE"]["gain"]<0,
          "expected direction discrepancy: report and investigate, do not conceal")
    out={"status":"CADOTTE_SINGLE_STUDY_FROZEN_OUTCOME_QA_PASS",
         "source_validated_mixtures":ss["source_joined_mixture_rows"],
         "original_composition_groups":ss["unique_source_composition_groups"],
         "original_MD5_verified":len(x["original_MD5_provenance"]),
         "n_outcomes":len(e["endpoint_predictive_gain"]),
         "arithmetic_checks":checks+3,
         "gain_absolute":e["endpoint_predictive_gain"]["mass"]["gain"],
         "gain_NDE":e["endpoint_predictive_gain"]["NDE"]["gain"],
         "paired_gain_difference":diff,
         "paired_ci95":e["paired_group_bootstrap_ci95"],
         "only_retrospective_single_site":True,"all_confidence_intervals_include_zero":all(
           a["composition_bootstrap_ci95"][0]<=0<=a["composition_bootstrap_ci95"][1]
           for a in e["endpoint_predictive_gain"].values()),
         "causal_effect_identified":False,
         "novel_independent_replication":False}
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":run()
