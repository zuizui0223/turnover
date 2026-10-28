#!/usr/bin/env python3
"""Preserve complete public-v7 original 254 single-system phytools K replay.

The archived 254 original per-system K values and their SHA256 are the only
historical references. This archival step fits no trait K or biological model;
it verifies all new native-tree K reports and their batch QA, then preserves
only derived K and numeric-reproducibility evidence, not original observations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

ORIGINAL=Path("results/austraits_organ_paper_original_254_single_K_v0_1")
SOURCE=Path("results/austraits_organ_paper_frozen_rebuild_inputs_v0_1")
RUN_ID=40541276639
SOURCE_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
STATUS="PASS_DURABLE_PUBLIC_V7_ORIGINAL_254_SINGLE_K_NUMERICAL_REPLAY"

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def digest(content):
    return hashlib.sha256(content).hexdigest()

def archive(src:Path,verdict:Path,plan_dir:Path,dest:Path,run_id:int):
    need(run_id==RUN_ID,"Unverified workflow ID for original 254 native K replay")
    m=json.loads((ORIGINAL/"original_single_K_archive_manifest.json").read_text())
    need(m["status"]=="PASS_PRESERVED_254_ORIGINAL_SINGLE_TRAIT_K_SYSTEM_REFERENCES"
         and m["system_count"]==254 and m["historical_files_preserved"]==254
         and m["source_parquet_sha256"]==SOURCE_SHA,
         "Original phytools K archive and source release invalid")
    expected_original=m["historical_k_source_file_sha256"]
    for file,sha in expected_original.items():
        need(digest((ORIGINAL/file).read_bytes())==sha,"Original K value hash drift: "+file)
    v=json.loads(verdict.read_text())
    need(v["status"]=="PASS_PUBLIC_V7_ALL_254_ORIGINAL_PHYTOOLS_SINGLE_K_REBUILT"
         and v["original_single_trait_system_count"]==254
         and v["original_families"]==42 and v["original_named_traits"]==13
         and v["historical_original_K_run_id"]==37725935020
         and v["all_16_original_K_batches_recomputed_and_numerically_checked"] is True
         and v["original_public_v7_parquet_sha256"]==SOURCE_SHA
         and v["original_reference_sha256_validated"] is True
         and v["raw_species_measurements_saved"] is False
         and v["independent_biological_original_study_replication"] is False,
         "Full independent S3/prune phytools K numerical replay not complete")
    maxdiff=float(v["max_absolute_numeric_K_or_logK_discrepancy"])
    need(math.isfinite(maxdiff) and 0<=maxdiff<=5.1e-5,
         "Recomputed old K differs more than original jsonlite rounding precision")
    expected={f"A{i:04d}.json" for i in []}
    expected=set(expected_original)
    expected.update(f"K{i:02d}_audit.json" for i in range(1,17))
    seen={x.name for x in src.iterdir() if x.is_file()}
    need(seen==expected and len(seen)==270,
         "Single-K replay archive needs exactly 254 fresh K and 16 original batch QA files")
    # Original archive SHA keys are A0001.json filenames; full R K replay
    # SHA keys are A0001 system IDs. Canonicalize IDs, never change file SHA.
    original_ids={Path(filename).stem for filename in expected_original}
    need(len(original_ids)==254
         and set(v["fresh_single_system_file_sha256"])==original_ids,
         "Full verifier missing SHA digests for exactly the original 254 K systems")
    sums={"systems":0,"native_S3":0,"native_prune":0}
    hashes={}
    dest.mkdir(parents=True,exist_ok=True)
    for name in sorted(expected):
        raw=(src/name).read_bytes()
        z=json.loads(raw)
        if name.startswith("A"):
            need(z["status"]=="AUSTRAITS_BLOMBERG_K_SYSTEM_ESTIMATED"
                 and name==z["system_id"]+".json"
                 and digest(raw)==v["fresh_single_system_file_sha256"][z["system_id"]],
                 "Source-native original per-system K integrity lost "+name)
            need(not any(x in z for x in
                         ("species","genus","binomial","dataset_id","observation_id","value")),
                 "An original AusTraits species measurement field entered the archive")
            sums["systems"]+=1
            sums["native_S3"]+=int(z["n_species_S3"])
            sums["native_prune"]+=int(z["n_species_prune"])
        else:
            need(z["status"]=="PASS_ORIGINAL_254_SINGLE_TRAIT_K_BATCH_NUMERICAL_REGRESSION"
                 and z["n_original_K_systems"]>0,
                 "Historical per-batch K source verification has not passed")
        target=dest/name
        if target.exists():need(target.read_bytes()==raw,"Archived fresh R K system differs: "+name)
        else:shutil.copyfile(src/name,target)
        hashes[name]=digest(raw)
    need(sums["systems"]==254,"Original 254 K audit lacks one or more systems")
    evidence=verdict.read_bytes()
    out=dest/"all_254_original_single_trait_K_verdict.json"
    if out.exists():need(out.read_bytes()==evidence,"Numerical K final audit changed")
    else:shutil.copyfile(verdict,out)
    hashes[out.name]=digest(evidence)
    report={
        "status":STATUS,
        "original_full_clean_source_R_K_workflow_run_id":RUN_ID,
        "original_full_clean_source_R_K_workflow_url":
            "https://github.com/zuizui0223/turnover/actions/runs/40541276639",
        "source_dataset":"AusTraits v7.0.0",
        "original_source_parquet_sha256":SOURCE_SHA,
        "original_historical_single_K_manifest_sha256":
            digest((ORIGINAL/"original_single_K_archive_manifest.json").read_bytes()),
        "original_K_systems_recomputed":254,
        "original_families":42,
        "original_traits":13,
        "independent_source_R_K_execution_complete":True,
        "reported_max_abs_numeric_K_or_logK_discrepancy":maxdiff,
        "all_original_S3_prune_native_tips_reproduced":True,
        "n_source_K_replay_files":len(hashes),
        "all_K_and_QA_file_sha256":hashes,
        "sum_reported_S3_and_prune_native_tips":sums,
        "original_K_numeric_precision_note":
            "Original jsonlite K and logK were saved to 4 decimal places, numerical tolerance <=5.1e-5.",
        "source_species_measurement_rows_persisted":False,
        "new_biological_hypothesis_tests":0,
        "independent_primary_measurement_validation":False,
        "scientific_results_unchanged":True,
        "explicit_author_submitting_approved":False
    }
    mp=dest/"all_254_single_K_replay_archive_manifest.json"
    serialized=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if mp.exists():need(mp.read_text()==serialized,"Permanent original K archive manifest changed")
    else:mp.write_text(serialized)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--verdict",type=Path,required=True)
    p.add_argument("--plan-dir",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--run-id",type=int,required=True)
    a=p.parse_args()
    r=archive(a.source,a.verdict,a.plan_dir,a.out_dir,a.run_id)
    print(json.dumps({"status":r["status"],
                      "original_K_systems":r["original_K_systems_recomputed"],
                      "n_K_and_QA_artifacts":r["n_source_K_replay_files"],
                      "max_abs":r["reported_max_abs_numeric_K_or_logK_discrepancy"]}))
if __name__=="__main__":
    main()
