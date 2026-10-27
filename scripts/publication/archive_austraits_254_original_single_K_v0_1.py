#!/usr/bin/env python3
"""Preserve the original 254 *single-trait* phytools Blomberg-K systems.

This archive is derived-only, never a second biological hypothesis test.
Refuse absent, duplicated, shifted tree/status, raw-observation, or K outputs.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import shutil
from pathlib import Path

ROOT = Path("results/austraits_organ_paper_frozen_rebuild_inputs_v0_1")
ORIGINAL_RUN = 37725935020
SOURCE_SHA = "5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
STATUS = "PASS_PRESERVED_254_ORIGINAL_SINGLE_TRAIT_K_SYSTEM_REFERENCES"
K_FIELDS = ("S3_K", "prune_K", "S3_logK", "prune_logK")
EXPECTED = {"n_systems":254, "n_families":42, "n_traits":13,
            "n_historical_batches":16}

def need(ok, msg):
    if not ok:
        raise AssertionError(msg)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def table(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def archive(src: Path, dest: Path):
    original = table(ROOT / "original_K_effects.csv")
    core = table(ROOT / "core_systems.csv")
    need(len(original)==254 and len(core)==259, "Original 254 K or 259 core graph changed")
    ci = {(z["family"],z["trait_name"]):z for z in core}
    need(len(ci)==259, "Original core unique family×trait keys changed")
    index = {z["system_id"]:z for z in original}
    need(len(index)==254 and
         len({z["family"] for z in original})==42 and
         len({z["trait_name"] for z in original})==13,
         "Original single K system cohort changed")
    files = sorted(src.glob("A????.json"))
    need(len(files)==254 and len(list(src.iterdir()))==254,
         "Historical original 16 R K batch artifacts incomplete or contain other files")
    copied = {}
    found = set()
    for f in files:
        old = json.loads(f.read_text())
        sid = f.stem
        need(sid in index and sid not in found and old["system_id"]==sid
             and old["status"]=="AUSTRAITS_BLOMBERG_K_SYSTEM_ESTIMATED",
             "Original K file system identity/status mismatch "+sid)
        found.add(sid)
        expected = index[sid]
        need((old["family"],old["trait_name"])==
             (expected["family"],expected["trait_name"]),
             "Historical K system family/trait identity changed")
        need((old["family"],old["trait_name"]) in ci,
             "Historical K single-trait system not in fixed core")
        c = ci[(old["family"],old["trait_name"])]
        # Original core includes taxa classed 'fail to bind' by V.PhyloMaker2.
        # Native S3 K excludes them: S3 tip count = prune + bind, NOT n_input.
        s3_core=int(c["n_prune"])+int(c["n_bind"])
        need(int(old["n_species_S3"])==int(expected["n_species_S3"])==
             s3_core
             and int(old["n_species_prune"])==int(expected["n_species_prune"])==
             int(c["n_prune"]) and int(c["n_input_species"])>=s3_core,
             "Historical native tip support mismatch for %s (%s/%s): "
             "S3 old/CSV/(prune+bind)/input=%s/%s/%s/%s; prune old/CSV/core=%s/%s/%s" % (
              sid,old["family"],old["trait_name"],old["n_species_S3"],
              expected["n_species_S3"],s3_core,c["n_input_species"],
              old["n_species_prune"],expected["n_species_prune"],c["n_prune"]))
        for field in K_FIELDS:
            a=float(old[field]); b=float(expected[field])
            need(math.isfinite(a) and math.isfinite(b),
                 "Historical K nonfinite "+sid+" "+field)
            if field in ("S3_K","prune_K"):need(a>0,"Historical K nonpositive "+sid)
            need(math.isclose(a,b,rel_tol=1e-9,abs_tol=5.1e-5),
                 "Historical K differs from original archived 254 CSV "+sid+" "+field)
        need(not any(x in old for x in
                     ("species","binomial","genus","observation_id","dataset_id","value")),
             "Species or original observation content in historical K system")
        dest.mkdir(parents=True,exist_ok=True)
        target=dest/f.name
        if target.exists():
            need(target.read_bytes()==f.read_bytes(),"Original K archived bytes changed "+sid)
        else:
            shutil.copyfile(f,target)
        copied[f.name]=sha(target.read_bytes())
    need(found==set(index),"Original 254 source systems not all archived")
    m={
      "status":STATUS, "original_run_id":ORIGINAL_RUN,
      "original_source_release":"AusTraits v7.0.0",
      "source_parquet_sha256":SOURCE_SHA,
      "original_aggregate_csv_sha256":sha((ROOT/"original_K_effects.csv").read_bytes()),
      "original_core_csv_sha256":sha((ROOT/"core_systems.csv").read_bytes()),
      "system_count":254, "family_count":42, "named_trait_count":13,
      "historical_batch_count":16,
      "historical_k_source_file_sha256":copied,
      "historical_files_preserved":len(copied),
      "nonraw_derived_single_trait_K_only":True,
      "new_K_fits_in_archive":0,
      "independent_original_study_replication":False,
      "full_fresh_original_single_K_replay_verified":False
    }
    manifest=dest/"original_single_K_archive_manifest.json"
    serialized=json.dumps(m,sort_keys=True,indent=2)+"\n"
    if manifest.exists():
        need(manifest.read_text()==serialized,"Single-trait K frozen manifest drift")
    else:manifest.write_text(serialized)
    return m

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    m=archive(a.source,a.out_dir)
    print(json.dumps({"status":m["status"],"n_K":m["historical_files_preserved"],
                      "source_run":m["original_run_id"]}))
if __name__=="__main__":
    main()
