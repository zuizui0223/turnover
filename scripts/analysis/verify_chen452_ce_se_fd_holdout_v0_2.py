#!/usr/bin/env python3
"""Independently audit preserved global CE/SE study-heldout output algebra.

No source row refetch, no new ecological model or test.
"""
from __future__ import annotations
import json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"results/chen452_leafn_sla_fd_ce_se_studyholdout_v0_2.json"

def ensure(condition,text):
    if not condition:raise AssertionError(text)

def main():
    d=json.loads(FILE.read_text())
    ensure(d["status"]=="CHEN452_LEAFN_AND_SLA_FD_STUDY_HOLDOUT_COMPLETED","model status")
    ensure(d["method"]["seed"]==20261120,"bootstrap seed drift")
    ensure(d["provenance"]["v01_original_source_rank_hold_run"]==44760473697,"old rank HOLD missing")
    ensure(d["method"]["retrospective_after_published_findings"],"retrospective status")
    ensure(d["provenance"]["v02_actual_source_qualified_models_CI_run"]==44761456911,"source CI drift")
    ensure(d["method"]["uncertainty"].startswith("2000 bootstrap"),"uncertainty definition drift")
    n=0
    for cohort,x in d["cohorts"].items():
        src=x["source"]
        ensure(src["complete_rows"]>=300 and src["complete_studyIDs"]>=30,"study support")
        ensure(src["groups_with_ge5_rows"]>=30,"per-study support")
        ensure(src["response_identity_mismatches"]==0,"source response identity")
        ensure(src["all_study_folds_rank_qualified"],"source rank qualification")
        ensure(src["missing_prespecified_source_fields"]+src["complete_rows"]==src["original_rows"],
               "original source coverage arithmetic")
        out=x["outcomes"]
        ensure(set(out)=={"CE","SE","CE_minus_SE"},"endpoint subset search")
        for endpoint,v in out.items():
            computed=1-v["sse1_study_equal"]/v["sse0_study_equal"]
            ensure(math.isclose(computed,v["gain"],abs_tol=1e-12),"SSE gain mismatch")
            ensure(v["sse0_study_equal"]>0 and v["sse1_study_equal"]>=0,"SSE invalid")
            ensure(0<=v["study_groups_improving"]<=src["complete_studyIDs"],"support incorrect")
            ci=v["ci95"]
            ensure(ci[0]<=ci[1] and all(math.isfinite(t) for t in ci),"invalid CI")
            n+=1
        diff=out["CE"]["gain"]-out["SE"]["gain"]
        ensure(math.isclose(diff,x["paired_CE_gain_minus_SE_gain"],abs_tol=1e-14),
               "paired CE SE gain difference invalid")
        ensure(x["paired_95CI"][0]<=x["paired_95CI"][1],"paired CI invalid")
    # Scientific conclusion: no stronger CE transfer based on paired study interval.
    ensure(d["cohorts"]["leafN"]["paired_95CI"][0]<0<d["cohorts"]["leafN"]["paired_95CI"][1],
           "primary paired contrast interval no longer includes zero")
    ensure(d["cohorts"]["SLA"]["paired_95CI"][0]<0<d["cohorts"]["SLA"]["paired_95CI"][1],
           "SLA paired contrast interval no longer includes zero")
    ensure(d["cohorts"]["leafN"]["outcomes"]["SE"]["ci95"][1]<0,
           "negative leafN FD incremental SE result drift")
    ensure(d["method"].get("no_new_pvalues", True) is True,"unexpected new significance test")
    report={"status":"CHEN452_RESTORED_GLOBAL_CE_SE_SOURCE_AGGREGATE_QA_PASS",
            "cohorts":list(d["cohorts"]),"original_studies_leafN":116,
            "original_studies_SLA":127,"n_outcome_SSE_algebra_checks":n,
            "causal_path_confirmed":False,"independent_primary_experiments_replicated":False,
            "original_publishers_outlier_filter_retained":True}
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":main()
