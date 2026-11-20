#!/usr/bin/env python3
"""Check frozen R scripts replay the original Stage B model summaries on restored 201-row inputs."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"results/trait_memory_positive_only_cleaning_impact_v0_2/result.json"

def must(cond,text):
    if not cond: raise AssertionError(text)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def check_number(label,actual,expected,diagnostics,tol=1e-5):
    a=float(actual);b=float(expected)
    diagnostics[label]={"replayed":a,"original_stage_b":b,"absolute_difference":abs(a-b)}
    must(math.isfinite(a) and abs(a-b) <= tol,f"Original Stage B numerical replay mismatch: {label}, diff={a-b}")

def main():
    a=argparse.ArgumentParser()
    for name in ("measurement","blup","null","out"):
        a.add_argument("--"+name,type=Path,required=True)
    args=a.parse_args()
    source=load(SOURCE)
    meas=load(args.measurement);blup=load(args.blup);null=load(args.null)
    must(source["status"]=="TRAIT_MEMORY_POSITIVE_ONLY_CLEANING_IMPACT_COMPLETE","source stage B not original qualified")
    must(meas["status"]=="TRAIT_MEMORY_MEASUREMENT_AWARE_ESTIMATED","replayed measurement model failed")
    must(blup["status"]=="TRAIT_MEMORY_BLUP_PORTABILITY_SENSITIVITY_ESTIMATED","replayed BLUP model failed")
    must(null["status"]=="TRAIT_MEMORY_CORRELATED_TRAIT_NULL_ESTIMATED","replayed null model failed")
    must(meas["log_scale"]["complete_all_201"] is True,"replayed all-201 log missing")
    checks={}
    for axis in ("S3","prune_only"):
        for field in ("R_family","R_trait","R_residual"):
            check_number(f"naive_raw_{axis}_{field}",
                meas["recomputed_naive"][axis][field],source["cleaned_raw"]["naive_repeatability"][axis][field],checks)
        for field in ("sigma2_family","sigma2_trait","sigma2_system","mean_sampling_variance"):
            check_number(f"model_raw_{axis}_{field}",
                meas["measurement_aware"][axis][field],source["cleaned_raw"]["measurement_aware"][axis][field],checks)
        for field in ("sigma2_family","sigma2_trait","sigma2_system","mean_sampling_variance"):
            check_number(f"model_log_{axis}_{field}",
                meas["log_scale"]["measurement_aware_"+axis][field],source["cleaned_log"]["measurement_aware"][axis][field],checks)
        check_number(f"naive_log_{axis}_family",
            meas["log_scale"]["naive_"+axis]["R_family"],source["cleaned_log"]["naive_repeatability"][axis]["R_family"],checks)
    for axis,rt in (("S3","S3"),("prune_only","prune")):
        check_number(f"BLUP_raw_{axis}",blup[rt+"_raw"]["gain_blup"],
            source["cleaned_raw"]["portability"][axis]["gain_blup"],checks)
        check_number(f"BLUP_log_{axis}",blup[rt+"_log"]["gain_blup"],
            source["cleaned_log"]["portability"][axis]["gain_blup"],checks)
        check_number(f"null_{axis}",null[axis]["p_family_ge_observed"],
            source["cleaned_raw"]["correlated_trait_null"][axis]["p_family_ge_observed"],checks,tol=1e-12)
    must(meas["measurement_aware"]["primary_S3_cluster_bootstrap"]["success_fraction"]>=.9,
         "Original 500-replicate crossed uncertainty gate failed on recovered inputs")
    result={"status":"FROZEN_R_MODELS_REPLAY_MATCH_ORIGINAL_STAGE_B",
            "source_corrected_201_table":"effects_positive_only_cleaned_recovered_v0_2.csv",
            "scientific_parameters_or_seeds_reselected":False,
            "models_refitted_only_for_reproducibility":True,
            "n_numeric_checks":len(checks),
            "maximum_absolute_difference":max(x["absolute_difference"] for x in checks.values()),
            "checks":checks,"submission_ready":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"n_checks":result["n_numeric_checks"],
                     "max_abs_difference":result["maximum_absolute_difference"]},sort_keys=True))

if __name__=="__main__":
    main()
