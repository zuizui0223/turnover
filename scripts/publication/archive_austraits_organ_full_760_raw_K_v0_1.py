#!/usr/bin/env python3
"""Permanently preserve the successful fresh 760-pair AusTraits K replay.

This is a provenance-only copy/verification of already produced Actions output.
No biological models, raw records, or new source data are processed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

RUN_ID = 39713644617
SOURCE_SHA = "5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
BATCHES = tuple(f"B{k:02d}" for k in range(1,25))
FINAL_STATUS = "PASS_ALL_760_RAW_SOURCE_K_RECOMPUTED_AND_MATCHED"
PART_STATUS = "PASS_FROZEN_ORIGINAL_BATCH_K_NUMERIC_PARITY"
ARCHIVE_STATUS = "PASS_PERMANENT_FULL_760_CLEAN_SOURCE_K_REPLAY_ARCHIVE_V0_1"

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def store(src: Path, dst: Path) -> str:
    raw = src.read_bytes()
    if dst.exists():
        require(dst.read_bytes() == raw, "Archived replay file changed: " + str(dst))
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return checksum(raw)

def archive(input_dir: Path, original_verdict: Path, dest: Path, replay_run_id: int):
    require(replay_run_id == RUN_ID, "Only verified original full K run is eligible")
    v = json.loads(original_verdict.read_text(encoding="utf-8"))
    expected_axes = {
        "S3": {"pass": 760, "hold": 0, "cross": 406, "wins": 313},
        "prune_only": {"pass": 747, "hold": 13, "cross": 397, "wins": 314}
    }
    require(v["status"] == FINAL_STATUS, "Original independent aggregation never passed")
    require(v["original_source"] == "AusTraits v7.0.0" and
            v["original_public_parquet_sha256"] == SOURCE_SHA,
            "Source release/version is not original")
    require(v["original_source_qualified_pairs"] == 760
            and v["recomputed_batch_count"] == 24
            and v["full_native_S3_and_prune_K_recomputed"] is True,
            "Full native K replay not complete")
    require(v["axes"] == expected_axes, "Original K cohort signs or denominators changed")
    require(v["independent_original_measurement_replication"] is False
            and v["new_trait_discovery_or_selection_tests"] == 0
            and v["raw_source_species_measurements_archived"] is False,
            "Unexpected independent biological claim or source observation disclosure")
    require(math.isfinite(float(v["max_absolute_numeric_K_or_logK_difference"]))
            and float(v["max_absolute_numeric_K_or_logK_difference"]) >= 0,
            "Missing actual numerical discrepancy")
    require(set(v["batch_source_sha256"]) == set(BATCHES),
            "The final comparison did not cite exactly 24 original R batches")
    filenames = set(x.name for x in input_dir.iterdir() if x.is_file())
    expected_files = {f"{bid}_{suffix}.json" for bid in BATCHES
                      for suffix in ("fresh", "audit")}
    require(filenames == expected_files,
            "Input must contain exactly 24 raw-K and 24 audit files")
    total, native_counts = 0, {"S3": 0, "prune_only": 0}
    staged_sha = {}
    for bid in BATCHES:
        p = input_dir / f"{bid}_fresh.json"
        a = input_dir / f"{bid}_audit.json"
        fresh_raw = p.read_bytes()
        require(checksum(fresh_raw) == v["batch_source_sha256"][bid],
                "Archived original full-run manifest does not match K file " + bid)
        fresh = json.loads(fresh_raw)
        audit = json.loads(a.read_text(encoding="utf-8"))
        require(fresh["status"] == "AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
                and fresh["no_species_names_or_raw_values_persisted"] is True,
                "Fresh per-pair K output invalid")
        require(audit["status"] == PART_STATUS
                and audit["batch"] == bid
                and audit["n_pair_ids"] == fresh["n_family_trait_pairs"]
                and audit["n_pair_ids"] == len(fresh["pairs"]),
                "Per-batch original K regression did not pass")
        require(audit["full_760_biological_independent_validation"] is False,
                "Invalid independent validation claim")
        total += audit["n_pair_ids"]
        for axis in native_counts:
            native_counts[axis] += audit["axes"][axis]["pass"]
        for x in fresh["pairs"]:
            require(not any(k in x for k in ("species", "genus", "binomial",
                                          "raw_value", "observation_id", "dataset_id")),
                    "Original species/source observation leaked into archive")
        for src in (p, a):
            staged_sha[src.name] = store(src, dest/src.name)
    require(total == 760 and native_counts == {"S3": 760, "prune_only": 747},
            "Fresh per-pair files do not reconstruct the original cohort")
    staged_sha["all_760_native_K_regression.json"] = store(
        original_verdict, dest/"all_760_native_K_regression.json")
    result = {
        "status": ARCHIVE_STATUS,
        "source_workflow_url":
            "https://github.com/zuizui0223/turnover/actions/runs/39713644617",
        "original_actions_run_id": RUN_ID,
        "source": "AusTraits v7.0.0, DOI 10.5281/zenodo.15718081",
        "raw_source_parquet_sha256": SOURCE_SHA,
        "historical_original_batch_count": 24,
        "n_recomputed_original_pairs": total,
        "native_axes": v["axes"],
        "max_absolute_numeric_K_or_logK_difference":
            v["max_absolute_numeric_K_or_logK_difference"],
        "permanent_file_sha256": staged_sha,
        "files_permanently_preserved": len(staged_sha),
        "complete_clean_source_K_replay": True,
        "independent_biological_source_validation": False,
        "new_K_or_evolutionary_models_fitted_during_this_archive": 0,
        "raw_species_measurements_committed": False,
        "paper_inference_and_post_selection_limits_unchanged": True
    }
    manifest = dest/"reproduction_archive_manifest.json"
    rendered = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if manifest.exists():
        require(manifest.read_text(encoding="utf-8") == rendered,
                "Full replay preservation manifest unexpectedly changed")
    else:
        manifest.write_text(rendered, encoding="utf-8")
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True, type=Path)
    p.add_argument("--original-verdict", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--run-id", required=True, type=int)
    a = p.parse_args()
    z = archive(a.input_dir, a.original_verdict, a.out_dir, a.run_id)
    print(json.dumps({"status":z["status"],
                      "permanent_files":z["files_permanently_preserved"],
                      "n_pairs":z["n_recomputed_original_pairs"],
                      "max_absolute_numeric_difference":
                          z["max_absolute_numeric_K_or_logK_difference"]}, sort_keys=True))
if __name__=="__main__":
    main()
