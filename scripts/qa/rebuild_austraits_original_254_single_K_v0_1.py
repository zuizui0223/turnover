#!/usr/bin/env python3
"""Recompute original 254 single-trait AusTraits Blomberg K, with original phytools.

Original family×trait candidate set, tree and source are FIXED, not selected by
K. The R estimator stays unchanged. Numerical comparison against all 254
historical SHA256-stored single-system results is an algorithm reproducibility
audit, not a new biological result or an independent original study.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SOURCE = Path("results/austraits_organ_paper_frozen_rebuild_inputs_v0_1")
ORIGINAL = Path("results/austraits_organ_paper_original_254_single_K_v0_1")
RELEASE_SHA = "5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
KEYS = ("S3_K","prune_K","S3_logK","prune_logK")
BATCHES = tuple(f"K{k:02d}" for k in range(1,17))
PASS_BATCH = "PASS_ORIGINAL_254_SINGLE_TRAIT_K_BATCH_NUMERICAL_REGRESSION"
PASS_FINAL = "PASS_PUBLIC_V7_ALL_254_ORIGINAL_PHYTOOLS_SINGLE_K_REBUILT"

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r=list(csv.DictReader(f))
    return r

def archives():
    manifest=json.loads((ORIGINAL/"original_single_K_archive_manifest.json").read_text())
    require(manifest["status"] ==
            "PASS_PRESERVED_254_ORIGINAL_SINGLE_TRAIT_K_SYSTEM_REFERENCES"
            and manifest["system_count"]==254 and manifest["family_count"]==42
            and manifest["named_trait_count"]==13
            and manifest["historical_batch_count"]==16
            and manifest["source_parquet_sha256"]==RELEASE_SHA,
            "Original native single-system K SHA manifest absent or source changed")
    require(hashlib.sha256((SOURCE/"original_K_effects.csv").read_bytes()).hexdigest()
            ==manifest["original_aggregate_csv_sha256"],
            "Original 254 K source matrix mutated")
    require(hashlib.sha256((SOURCE/"core_systems.csv").read_bytes()).hexdigest()
            ==manifest["original_core_csv_sha256"],
            "Original 259 source-core systems mutated")
    hashes=manifest["historical_k_source_file_sha256"]
    require(len(hashes)==manifest["historical_files_preserved"]==254,
            "Original 254 system K observations incomplete")
    old={}
    for name, expected_sha in hashes.items():
        fn=ORIGINAL/name
        require(fn.is_file() and hashlib.sha256(fn.read_bytes()).hexdigest()==expected_sha,
                "Historical K reference bytes not original "+name)
        d=json.loads(fn.read_text())
        key=fn.stem
        require(d["status"]=="AUSTRAITS_BLOMBERG_K_SYSTEM_ESTIMATED"
                and d["system_id"]==key and key not in old,
                "Wrong original native phylogeny K identity")
        old[key]=d
    require(len(old)==254,"Original 254 single K reference IDs incomplete")
    table=rows(SOURCE/"original_K_effects.csv")
    core={(x["family"],x["trait_name"]):x
          for x in rows(SOURCE/"core_systems.csv")}
    require(len(core)==259,"Original 259 source-core identities changed")
    kref={x["system_id"]:x for x in table}
    require(set(kref)==set(old),"Original source CSV and historical K outputs disagree")
    return old,kref,core,manifest

def prepare(plan_dir,report):
    previous,kref,core,archive=archives()
    groups=[{"weight":0,"systems":[]} for _ in range(16)]
    systems=[]
    for sid,original in kref.items():
        key=original["family"],original["trait_name"]
        require(key in core,"Original K family/trait absent from source-core graph")
        source=core[key]
        weight=int(original["n_species_S3"])**3
        require(weight>0,"Original S3 system K size invalid")
        systems.append({
            "system_id":sid,"family":original["family"],
            "trait_name":original["trait_name"],
            "n_input_species":int(source["n_input_species"]),
            "n_prune":int(source["n_prune"]),
            "n_bind":int(source["n_bind"]),
            "_weight":weight})
    require(len(systems)==254 and
            len({x["family"] for x in systems})==42
            and len({x["trait_name"] for x in systems})==13,
            "Original system set changed")
    # Preserve original 16-bin nS3^3 workload strategy from historical workflow.
    for original in sorted(systems,key=lambda x:(-x["_weight"],x["family"],x["trait_name"])):
        i=min(range(16),key=lambda j:(groups[j]["weight"],j))
        groups[i]["weight"]+=original["_weight"]
        groups[i]["systems"].append({k:original[k] for k in (
            "system_id","family","trait_name","n_input_species","n_prune","n_bind")})
    plan_dir.mkdir(parents=True,exist_ok=True)
    totals={}
    for i,group in enumerate(groups,1):
        bid=f"K{i:02d}"
        require(group["systems"],"Empty original source-system group "+bid)
        (plan_dir/(bid+".json")).write_text(
            json.dumps(group["systems"],sort_keys=True,indent=2)+"\n")
        totals[bid]=len(group["systems"])
    require(sum(totals.values())==254,"Original 254 system batch plan incomplete")
    output={"status":"PASS_ORIGINAL_254_SINGLE_K_SOURCE_ONLY_BATCH_PLAN",
            "original_K_systems":254,"n_families":42,"n_traits":13,
            "original_batch_count":16,"batch_sizes":totals,
            "original_outcome_K_used_to_select_cohort":False,
            "preexisting_historical_original_K_references_SHA256_verified":True,
            "raw_source_species_measurements_exported":False}
    save(report,output)
    return output

def compare(bid,plan,actual_dir,report):
    require(bid in BATCHES,"Unrecognized K batch ID")
    old,refs,core,manifest=archives()
    expected=json.loads(plan.read_text())
    require(expected and len({x["system_id"] for x in expected})==len(expected),
            "Source-only original K workload has duplicate systems")
    max_abs=0.0
    error_count=0
    for row in expected:
        sid=row["system_id"]
        require(sid in old and (row["family"],row["trait_name"])==
                (old[sid]["family"],old[sid]["trait_name"]),
                "Original K system identity shifted: "+sid)
        path=actual_dir/(sid+".json")
        require(path.is_file(),"Fresh public-v7 phytools original K output missing: "+sid)
        z=json.loads(path.read_text())
        y=old[sid]
        require(z["status"]==y["status"]=="AUSTRAITS_BLOMBERG_K_SYSTEM_ESTIMATED"
                and z["system_id"]==y["system_id"]
                and z["family"]==y["family"]
                and z["trait_name"]==y["trait_name"],
                "Historical single-trait K record altered for "+sid)
        require(z["n_species_S3"]==y["n_species_S3"] and
                z["n_species_prune"]==y["n_species_prune"],
                "Original native K S3/prune tree tip count changed for "+sid)
        require(not any(k in z for k in
                        ("binomial","genus","species","dataset_id","observation_id","value")),
                "Individual original AusTraits observations leaked into R K output")
        for field in KEYS:
            a,b=float(z[field]),float(y[field])
            require(math.isfinite(a) and math.isfinite(b),
                    "Nonfinite reconstructed original phytools K or log K "+sid)
            if field in ("S3_K","prune_K"):
                require(a>0 and b>0,"Original K nonpositive "+sid)
            err=abs(a-b)
            max_abs=max(max_abs,err)
            # Original jsonlite default saves 4 decimals; compare actual original
            # *reported* values, not invented numerical precision beyond archive.
            require(math.isclose(a,b,rel_tol=1e-7,abs_tol=5.1e-5),
                    "Public v7 original phytools numerical regression failed for %s %s: "
                    "new %.10g, old %.10g" % (sid,field,a,b))
    result={"status":PASS_BATCH,"batch":bid,"n_original_K_systems":len(expected),
            "max_absolute_K_or_logK_difference":max_abs,
            "all_original_system_ids_and_native_tree_tip_counts_same":True,
            "numeric_comparison_at_source_stored_precision_4_decimals":True,
            "new_biological_effect_tests":0,
            "external_original_study_replication":False}
    save(report,result)
    return result

def summarize(original_dir,fresh_dir,qa_dir,report):
    old,refs,core,manifest=archives()
    seen=set()
    max_abs=0.0
    file_sha={}
    for bid in BATCHES:
        batch=original_dir/(bid+".json")
        audited=qa_dir/(bid+"_audit.json")
        require(batch.is_file() and audited.is_file(),
                "One of the 16 original phytools K batches missing: "+bid)
        items=json.loads(batch.read_text())
        result=json.loads(audited.read_text())
        require(result["status"]==PASS_BATCH and result["batch"]==bid and
                result["n_original_K_systems"]==len(items),"Per-batch source-K audit missing")
        # Aggregator recomputes every comparison using the same original archive.
        retest=compare(bid,batch,fresh_dir,qa_dir/(bid+"_recheck.json"))
        require(result==retest,"Per-batch K audit disagreed on fresh recheck: "+bid)
        max_abs=max(max_abs,retest["max_absolute_K_or_logK_difference"])
        for x in items:
            sid=x["system_id"]
            require(sid not in seen,"Duplicate original fresh single-trait K result "+sid)
            seen.add(sid)
            file_sha[sid]=hashlib.sha256((fresh_dir/(sid+".json")).read_bytes()).hexdigest()
    require(seen==set(old) and len(file_sha)==254,
            "Full fresh original 254 K cohort incomplete")
    res={
        "status":PASS_FINAL,
        "source_dataset":"AusTraits v7.0.0",
        "original_public_v7_parquet_sha256":RELEASE_SHA,
        "historical_original_K_run_id":37725935020,
        "original_single_trait_system_count":254,
        "original_families":42,"original_named_traits":13,
        "all_16_original_K_batches_recomputed_and_numerically_checked":True,
        "all_original_native_S3_prune_tip_counts_reproduced":True,
        "max_absolute_numeric_K_or_logK_discrepancy":max_abs,
        "original_reference_sha256_validated":True,
        "fresh_single_system_file_sha256":file_sha,
        "raw_species_measurements_saved":False,
        "independent_biological_original_study_replication":False,
        "post_discovery_selection_in_original_paper_unaffected":True
    }
    save(report,res)
    return res

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("prepare","compare","summarize"),required=True)
    p.add_argument("--batch")
    p.add_argument("--batch-plan",type=Path)
    p.add_argument("--plan-dir",type=Path)
    p.add_argument("--fresh-dir",type=Path)
    p.add_argument("--audit-dir",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.mode=="prepare":
        require(a.plan_dir,"Plan output directory missing")
        d=prepare(a.plan_dir,a.output)
    elif a.mode=="compare":
        require(a.batch and a.batch_plan and a.fresh_dir,"Batch inputs missing")
        d=compare(a.batch,a.batch_plan,a.fresh_dir,a.output)
    else:
        require(a.plan_dir and a.fresh_dir and a.audit_dir,"Full source-K replay output missing")
        d=summarize(a.plan_dir,a.fresh_dir,a.audit_dir,a.output)
    print(json.dumps({"status":d["status"],"batch":d.get("batch"),
                      "n_original_systems":d.get("original_single_trait_system_count",
                                                d.get("n_original_K_systems")),
                      "max_absolute_K_difference":d.get("max_absolute_numeric_K_or_logK_discrepancy",
                                                       d.get("max_absolute_K_or_logK_difference"))},
                     sort_keys=True))

if __name__=="__main__":
    main()
