#!/usr/bin/env python3
"""Preserve original nonflora 283 and strict 142 paired-K outputs, byte for byte.

Does not download or redistribute raw species measurements. No K fit, new tests
or independent primary-study validation occur in this archive-only script.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

SUPPORT_RUN=38920414545
BROAD_RUN=38922133371
STRICT_RUN=39006469805
TRANSITION_RUN=39202352075
RAW_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"

def require(ok,msg):
    if not ok: raise AssertionError(msg)

def archive(args):
    sup=json.loads(args.support.read_text())
    joint=json.loads(args.strict_summary.read_text())
    broad=json.loads(args.broad_summary.read_text())
    transition=json.loads(args.transition.read_text())
    original=json.loads(args.original_pair_support.read_text())
    design=json.loads(args.design.read_text())
    require(sup["status"]=="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_SOURCE_SUPPORT_AUDITED",
            "Not original source-only flora restriction")
    require(sup["subsets"]["cross_organ"]["qualifying_20_same_nonflora_dataset_pairs"]==142,
            "Original strict K-blind 142 cohort changed")
    require(original["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED" and
            original["qualifying_family_trait_pairs"]==760,"Original 760 support changed")
    require(design["independent_eligibility"]["original_parquet_sha256"]==RAW_SHA,
            "Incorrect versioned original AusTraits v7")
    require(joint["status"]=="AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_SENSITIVITY_AGGREGATED_V0_1"
            and joint["axes"]["S3"]["n_valid_real_tree_K_pairs"]==142
            and joint["axes"]["prune_only"]["n_valid_real_tree_K_pairs"]==101,
            "Historical joint narrow output changed")
    require(broad["status"]=="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_ORGAN_SENSITIVITY_AGGREGATED_V0_1"
            and broad["axes"]["S3"]["n_valid_real_tree_K_pairs"]==283
            and broad["axes"]["prune_only"]["n_valid_real_tree_K_pairs"]==233,
            "Historical five-flora broad output changed")
    require(transition["status"]=="AUSTRAITS_K_NONFLORA_COHORT_TRANSITION_EXPLORATORY_VERIFIED",
            "Original three-stage source/tip transition not fixed")
    expect={"S3":(142,110,121,120),"prune_only":(101,82,83,81)}
    for axis,(n,a,b,c) in expect.items():
        s=transition["axes"][axis]
        require(s["n_pair_identities"]==n and
                [r["n_reproductive_K_higher"] for r in s["stage_rates"].values()]==[a,b,c],
                "Original 3-stage K source and tip transitions changed")
    # Historical original batch output file structure and per-axis statuses.
    aggregate_counts={}
    files={}
    inputs={"source_support_excluding_five_floras.json":args.support,
            "five_flora_exclusion_organ_K.json":args.broad_summary,
            "joint_nonflora_shared_source_K.json":args.strict_summary,
            "nonflora_283_to_142_source_support_transition.json":args.transition}
    for prefix, directory, count, expected_status, passed in [
        ("strict",args.strict_dir,142,"AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_BATCH_COMPLETE",
         {"S3":142,"prune_only":101}),
        ("broad",args.broad_dir,283,"AUSTRAITS_K_FIVE_FLORA_EXCLUSION_PAIR_BATCH_COMPLETE",
         {"S3":283,"prune_only":233})]:
        length=12 if prefix=="strict" else 16
        seen=set()
        axis_pass={"S3":0,"prune_only":0}
        for i in range(1,length+1):
            filename=f"B{i:02d}.json"
            path=directory/filename
            require(path.is_file(),"Original nonflora K batch missing "+prefix+filename)
            v=json.loads(path.read_text())
            require(v["status"]==expected_status and len(v.get("pairs",[]))>0,
                    "Original source K batch malformed "+prefix+filename)
            if prefix=="strict":
                require(v["n_original_K_blind_source_selected_pairs"]==len(v["pairs"]),
                        "Original strict source batch pair count changed")
            for item in v["pairs"]:
                key=item["family"],item["trait_A"],item["trait_B"]
                require(key not in seen,"Repeated original nonflora pair "+str(key))
                seen.add(key)
                require(not any(x in item for x in
                                ("species","binomial","genus","dataset_id","observation_id","value")),
                        "Source K batch contains row-level original measurement")
                for axis in axis_pass:
                    status=item["axes"][axis]["status"]
                    require(status=="PASS" or status.startswith("HOLD_"),
                            "Original nonflora K tree status invalid")
                    axis_pass[axis]+=int(status=="PASS")
            inputs[f"{prefix}_{filename}"]=path
        require(len(seen)==count and axis_pass==passed,
                f"Original {prefix} nonflora K batch count/status drift: {len(seen)} {axis_pass}")
        aggregate_counts[prefix]={"pairs":len(seen),"native_pass":axis_pass,
                                  "batches":length}
    args.out_dir.mkdir(parents=True,exist_ok=True)
    for name,path in inputs.items():
        dest=args.out_dir/name
        if dest.exists():require(dest.read_bytes()==path.read_bytes(),
                                 "Historical archive bytes changed: "+name)
        else:shutil.copyfile(path,dest)
        files[name]=hashlib.sha256(dest.read_bytes()).hexdigest()
    report={"status":"PASS_PERMANENT_AUSTRAITS_ORIGINAL_NONFLORA_SOURCE_K_REFERENCE",
            "original_source_support_run_id":SUPPORT_RUN,
            "original_broad_K_run_id":BROAD_RUN,
            "original_strict_K_run_id":STRICT_RUN,
            "original_transition_run_id":TRANSITION_RUN,
            "original_public_v7_sha256":RAW_SHA,
            "source_only_eligible_strict_pairs":142,
            "historical_original_batch_counts":aggregate_counts,
            "original_three_stage_reproductive_wins":
                {ax:[x["n_reproductive_K_higher"] for x in transition["axes"][ax]["stage_rates"].values()]
                 for ax in expect},
            "file_sha256":files,
            "file_count":len(files),
            "raw_original_species_measurements_archived":False,
            "new_K_estimation":False,
            "independent_source_replication":False,
            "note":"Retrospective original AusTraits source/tip cohort, not a new trait mechanism."}
    out=args.out_dir/"original_nonflora_reference_manifest.json"
    rendered=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if out.exists():require(out.read_text()==rendered,"Nonflora archive manifest drift")
    else:out.write_text(rendered)
    return report

def main():
    p=argparse.ArgumentParser()
    for key in ["support","original-pair-support","design","broad-dir","strict-dir",
                "broad-summary","strict-summary","transition","out-dir"]:
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    result=archive(a)
    print(json.dumps({"status":result["status"],
                      "n_files":result["file_count"],
                      "counts":result["historical_original_batch_counts"]},sort_keys=True))
if __name__=="__main__":main()
