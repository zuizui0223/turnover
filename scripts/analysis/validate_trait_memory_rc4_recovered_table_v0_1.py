#!/usr/bin/env python3
"""Reassemble and verify *only* original published aggregate rho/SE records from pinned Actions job stdout.

No raw BIEN records, species names, species states, taxa-by-plot rows or model refits.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "results/trait_memory_positive_only_cleaning_impact_v0_2"
PARTS = [
    "recovered_original_robust_R001_R014.json",
    "recovered_original_robust_R015_R028.json",
    "recovered_original_robust_R029_R032.json",
]
STAGE_B = "recovered_stage_b_cleaned_C01_C08.json"
CSV_PATH = "effects_positive_only_cleaned_recovered_v0_2.csv"

def check(ok, message):
    if not ok:
        raise AssertionError(message)

def load(name):
    return json.loads((D / name).read_text(encoding="utf-8"))

def qlinear(values, probability):
    values = sorted(values)
    x = (len(values) - 1) * probability
    lo, hi = math.floor(x), math.ceil(x)
    return values[lo] + (values[hi] - values[lo]) * (x-lo)

def rank(values):
    ordered = sorted(enumerate(values), key=lambda p: p[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i+1
        while j < len(values) and ordered[j][1] == ordered[i][1]:
            j += 1
        mid = (i+j-1)/2 + 1
        for k in range(i, j):
            out[ordered[k][0]] = mid
        i = j
    return out

def summary(rows, axis):
    old = [float(r[f"original_{axis}_raw_rho"]) for r in rows]
    new = [float(r[f"{axis}_raw_rho"]) for r in rows]
    diff = [b-a for a,b in zip(old,new)]
    ad = [abs(x) for x in diff]
    return {
        "max_abs_delta": max(ad),
        "median_abs_delta": qlinear(ad,.5),
        "n_abs_delta_ge_0_01": sum(v >= .01 for v in ad),
        "n_abs_delta_ge_0_05": sum(v >= .05 for v in ad),
        "n_abs_delta_ge_0_10": sum(v >= .10 for v in ad),
        "n_sign_changes": sum((a>0)-(a<0) != (b>0)-(b<0) for a,b in zip(old,new)),
        "p90_abs_delta": qlinear(ad,.90),
        "pearson_original_cleaned": statistics.correlation(old,new),
        "spearman_original_cleaned": statistics.correlation(rank(old),rank(new)),
    }

def main(out):
    original = []
    for name in PARTS:
        part = load(name)
        check(part["status"] == "RECOVERED_ORIGINAL_V03_FROM_SUCCESSFUL_JOB_STDOUT", "incorrect original source")
        check(part["run_id"] == 37281031394, "original run ID mismatch")
        check(len(part["values"]) == part["n_systems"], "source fragment count mismatch")
        original.extend(part["values"])
    stage = load(STAGE_B)
    check(stage["status"] == "RECOVERED_CLEANED_STAGE_B_FROM_SUCCESSFUL_JOB_STDOUT", "Stage B status mismatch")
    check(stage["run_id"] == 37443037590 and len(stage["values"]) == 49, "Stage B job recovery incomplete")
    c = {x["system_id"]:x for x in stage["values"]}
    orig = {x["system_id"]:x for x in original}
    check(len(original) == len(orig) == 201, "original 201 IDs not recovered")
    check(len(c) == 49 and set(c).issubset(orig), "corrected 49 IDs inconsistent")
    check(len({x["family"] for x in original}) == 45, "family denominator drift")
    check(len({x["trait_name"] for x in original}) == 12, "trait denominator drift")
    check(len({(x["family"],x["trait_name"]) for x in original}) == 201, "original crossed core changed")
    target = load("result.json")
    check(target["status"] == "TRAIT_MEMORY_POSITIVE_ONLY_CLEANING_IMPACT_COMPLETE", "source aggregated outcome unknown")
    with (D / CSV_PATH).open(newline="",encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    check(len(rows) == 201, "cleaned CSV not 201 rows")
    check(len({r["system_id"] for r in rows}) == 201, "CSV duplicate IDs")
    check(sum(r["cleaning_status"]=="CLEANED_STAGE_B" for r in rows)==49, "corrected count changed")
    check(sum(r["cleaning_status"]=="CLEAN_UNCHANGED_STAGE_A" for r in rows)==152, "inherited count changed")
    check(all(r["S3_log_status"]=="LOG_POSITIVE" and r["prune_log_status"]=="LOG_POSITIVE" for r in rows), "log cleaning not complete")
    max_abs_source_rho_diff = 0.0
    species_removed = {"S3_total":0,"prune_total":0,"max_per_system_S3":0,"max_per_system_prune":0}
    for row in rows:
        sid = row["system_id"]
        check(sid in orig, "system missing from original source")
        source = orig[sid]
        changed = c.get(sid)
        check(source["family"]==row["family"] and source["trait_name"]==row["trait_name"], f"system identity mismatch {sid}")
        check(row["cleaning_status"]==("CLEANED_STAGE_B" if changed else "CLEAN_UNCHANGED_STAGE_A"),f"source cleaning status mismatch {sid}")
        if changed:
            check(source["family"]==changed["family"] and source["trait_name"]==changed["trait_name"],f"Stage B source family/trait identity drift {sid}")
        for axis,stem in (("S3","S3"),("prune_only","prune")):
            origin = source[axis]
            corr = changed[axis] if changed else None
            if corr:
                max_abs_source_rho_diff = max(max_abs_source_rho_diff,abs(origin["raw_rho"]-corr["original_raw_rho"]))
                check(origin["raw_rho"] == corr["original_raw_rho"],f"Stage B original rho not byte-exact on {sid}:{axis}")
                check(origin["n_nonpositive"] == corr["original_nonpositive_species"],f"Stage B original nonpositive count drift {sid}:{axis}")
                expected_n = corr["cleaned_n_species"]
                expected_original_n = corr["original_n_species"]
                expected_removed = corr["n_species_removed_for_no_positive_state"]
                raw_rho = corr["cleaned_raw_rho"]; raw_se = corr["cleaned_raw_se"]
                log_rho = corr["cleaned_log_rho"]; log_se = corr["cleaned_log_se"]
                raw_valid = corr["cleaned_raw_boot_valid_fraction"]
                log_valid = corr["cleaned_log_boot_valid_fraction"]
            else:
                expected_n = expected_original_n = origin["n_species"]
                expected_removed=0
                raw_rho = origin["raw_rho"]; raw_se = origin["raw_bootstrap_se"]
                log_rho = origin["log_rho"]; log_se = origin["log_bootstrap_se"]
                raw_valid = origin["raw_bootstrap_valid_fraction"]
                log_valid = origin["log_bootstrap_valid_fraction"]
                check(origin["n_nonpositive"] == 0, f"not truly unchanged {sid}:{axis}")
            for field,value in (
                (f"original_n_species_{stem}",expected_original_n),
                (f"cleaned_n_species_{stem}",expected_n),
                (f"removed_species_{stem}",expected_removed),
                (f"{stem}_raw_rho",raw_rho),(f"{stem}_raw_se",raw_se),
                (f"{stem}_log_rho",log_rho),(f"{stem}_log_se",log_se),
                (f"{stem}_boot_valid",raw_valid),(f"{stem}_log_boot_valid",log_valid),
                (f"original_{stem}_raw_rho",origin["raw_rho"]),
                (f"{stem}_n_nonpositive",0),
            ):
                check(value is not None and math.isfinite(float(value)),f"unexpected missing original source metric {sid} {field}")
                check(math.isclose(float(row[field]),float(value),rel_tol=0,abs_tol=1e-14),f"recovered CSV does not reproduce original source metric {sid} {field}")
            check(expected_n >= 20, "source stage support <20")
            check(math.isclose(float(row[f"delta_{stem}_raw_rho"]),float(row[f"{stem}_raw_rho"])-float(row[f"original_{stem}_raw_rho"]),abs_tol=1e-14),f"delta arithmetic drift {sid}:{stem}")
            species_removed[stem+"_total"] += expected_removed
            species_removed["max_per_system_"+stem] = max(species_removed["max_per_system_"+stem],expected_removed)
    check(species_removed == target["species_removed"],"species-removal metadata differs from audited Stage B")
    impact = {}
    for axis in ("S3","prune"):
        calculated=summary(rows,axis)
        for key,value in calculated.items():
            claimed=target["effect_impact"][axis][key]
            check(math.isclose(value,claimed,rel_tol=0,abs_tol=1e-10),f"Stage B effect-impact mismatch {axis} {key}: {value} vs {claimed}")
        impact[axis] = calculated
    # This also proves that the sampling-error inputs used by the downstream crossed
    # meta-analysis are recovered, not merely the published point-gradient changes.
    sampling_variance_source_checks = {}
    for scale in ("raw", "log"):
        for axis,stem in (("S3","S3"),("prune_only","prune")):
            key = f"{stem}_{scale}_se"
            reconstructed = sum(float(r[key])**2 for r in rows) / len(rows)
            original = target["cleaned_"+scale]["measurement_aware"][axis]["mean_sampling_variance"]
            check(math.isclose(reconstructed,original,rel_tol=0,abs_tol=1e-12),
                  f"Stage B mean sampling variance drift {scale} {axis}")
            sampling_variance_source_checks[f"{stem}_{scale}"] = {
                "recovered_mean_SE_squared": reconstructed,
                "original_Stage_B_mean_sampling_variance": original,
                "difference": reconstructed-original,
            }
    check(max_abs_source_rho_diff==0,"reference original rho values differ between runs")
    report = {
        "status":"REPAIRED_201_LOG_RECOVERY_IDENTITY_PASS",
        "201_systems_complete":True,
        "49_corrected_and_152_inherited":True,
        "original_robust_v0_3_source_run":37281031394,
        "original_stage_b_corrected_source_run":37443037590,
        "original_corrected_49_rho_identical":True,
        "all_original_rows_source_rederived":False,
        "number_source_species_state_records_republished":0,
        "manuscript_or_figure_submission_approved":False,
        "n_families":45,"n_traits":12,"n_row_columns":len(rows[0]),
        "species_removed":species_removed,
        "impact_exactly_matches_original_successful_Stage_B":True,
        "SE_squared_means_match_original_Stage_B_all_four_axes":True,
        "SE_squared_mean_qa":sampling_variance_source_checks,
        "impact":impact,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True))

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("build/trait_memory_rc4_recovery_validation.json"))
    a=p.parse_args()
    main(a.out)
