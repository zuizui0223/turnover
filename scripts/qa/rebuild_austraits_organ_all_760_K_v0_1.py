#!/usr/bin/env python3
"""Recompute the original AusTraits 760 K pairs and check every archived result.

Reproducibility only: all 760 already-qualified pairs, same release, trees,
source units and unchanged R/C++ kernel. No new biological observations/tests.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = Path("results/austraits_organ_paper_frozen_rebuild_inputs_v0_1")
HISTORY = Path("results/austraits_organ_paper_original_pair_K_v0_1")
SHA = "5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
BATCHES = ["B%02d" % k for k in range(1,25)]
REPRO = set(["fruit_height","fruit_length","fruit_width",
             "seed_dry_mass","seed_length","seed_width"])
FIELDS = ("K_A","K_B","delta_shared_logK","delta_original_logK","delta_support_shift")
FINAL = "PASS_ALL_760_RAW_SOURCE_K_RECOMPUTED_AND_MATCHED"

def require(test, why):
    if not test:
        raise AssertionError(why)

def key(x):
    return x["family"],x["trait_A"],x["trait_B"]

def frozen():
    manifest=json.loads((SOURCE/"frozen_rebuild_manifest.json").read_text())
    require(manifest["status"]=="PASS_FROZEN_ORIGINAL_AGGREGATE_REBUILD_REFERENCES_V0_1"
            and manifest["source_parquet_sha256"]==SHA
            and manifest["matched_supported_pairs"]==760,
            "Original source archive invalid")
    for n,digest in manifest["source_byte_sha256"].items():
        require(hashlib.sha256((SOURCE/n).read_bytes()).hexdigest()==digest,
                "Historical source changed: "+n)
    historical_manifest=json.loads((HISTORY/"original_pair_k_reference_manifest.json").read_text())
    require(historical_manifest["status"]=="PASS_PRESERVED_760_ORIGINAL_MATCHED_TIP_K_REGRESSION_REFERENCES"
            and historical_manifest["n_original_matched_pairs"]==760,
            "Historical native K manifest invalid")
    require(historical_manifest["parent_rebuild_manifest_sha256"]==
            hashlib.sha256((SOURCE/"frozen_rebuild_manifest.json").read_bytes()).hexdigest(),
            "Historical K and source support belong to different cohorts")
    require(set(historical_manifest["files"])==set(x+".json" for x in BATCHES),
            "The original historical K archive has incomplete batches")
    support=json.loads((SOURCE/"shared_taxon_pair_support.json").read_text())
    require(support["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"
            and support["qualifying_family_trait_pairs"]==760,
            "Historical source-only support invalid")
    qualified={key(x):x for x in support["family_trait_pair_support"]
               if x["qualifies_20_common_species"]}
    require(len(qualified)==760,"Original source-only pair IDs duplicated")
    historical={}
    membership={}
    for batch in BATCHES:
        name=batch+".json"
        raw=(HISTORY/name).read_bytes()
        require(hashlib.sha256(raw).hexdigest()==historical_manifest["files"][name],
                "Original K batch source SHA256 drift: "+name)
        obj=json.loads(raw)
        require(obj["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
                and len(obj["pairs"])==obj["n_family_trait_pairs"]
                and obj["no_species_names_or_raw_values_persisted"] is True,
                "Historical batch not a qualified K archive")
        membership[batch]=[]
        for x in obj["pairs"]:
            idx=key(x)
            require(idx in qualified and idx not in historical,
                    "Historical pair duplicate/unqualified: "+str(idx))
            ref=qualified[idx]
            require(x["n_shared_species"]==ref["n_common_species_same_genus"]
                    and x["system_A"]==ref["system_A"]
                    and x["system_B"]==ref["system_B"],
                    "Historical K and source-only species identity differ")
            historical[idx]=x
            membership[batch].append(idx)
    require(set(historical)==set(qualified),"All 760 original K pairs not archived")
    return qualified,historical,membership

def prepare(batch_dir,output):
    qualified,historical,membership=frozen()
    batch_dir.mkdir(parents=True,exist_ok=True)
    counts={}
    for batch in BATCHES:
        src=[qualified[idx] for idx in membership[batch]]
        require(src,"Original batch empty")
        (batch_dir/(batch+".json")).write_text(json.dumps(src,indent=2,sort_keys=True)+"\n")
        counts[batch]=len(src)
    require(sum(counts.values())==760,"Source-only batch plan incomplete")
    result={"status":"PASS_ORIGINAL_24_BATCH_760_PAIR_SOURCE_ONLY_PLAN",
            "original_qualified_pairs":760,"batch_sizes":counts,
            "new_outcome_dependent_pair_selection":False,
            "species_or_raw_measurements_saved":False}
    save(output,result)
    return result

def compare(batch,fresh_file,output):
    require(batch in BATCHES,"Unknown original K batch ID")
    qualified,old,membership=frozen()
    d=json.loads(fresh_file.read_text())
    require(d["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
            and d["no_species_names_or_raw_values_persisted"] is True,
            "Fresh R/C++ K computation output invalid")
    pairs=d["pairs"]
    require(len(pairs)==d["n_family_trait_pairs"]==len(membership[batch])
            and {key(x) for x in pairs}==set(membership[batch]),
            "Fresh raw-source R result dropped or substituted original pairs")
    counts={ax:{"pass":0,"hold":0,"cross":0,"wins":0} for ax in ("S3","prune_only")}
    maxdiff=0.0
    for x in pairs:
        idx=key(x)
        y=old[idx]
        require(x["n_shared_species"]==y["n_shared_species"]
                and x["system_A"]==y["system_A"] and x["system_B"]==y["system_B"],
                "Source reconstruction changed pair identity: "+str(idx))
        for axis in ("S3","prune_only"):
            a,b=x["axes"][axis],y["axes"][axis]
            require(a["status"]==b["status"] and a["n_tips"]==b["n_tips"],
                    "Native tree support changed: "+str((idx,axis)))
            if a["status"]=="PASS":
                counts[axis]["pass"]+=1
                for field in FIELDS:
                    left,right=float(a[field]),float(b[field])
                    require(math.isfinite(left) and math.isfinite(right),
                            "Invalid reconstructed native K value")
                    error=abs(left-right)
                    maxdiff=max(maxdiff,error)
                    require(math.isclose(left,right,rel_tol=1e-7,abs_tol=2e-8),
                            "Actual original K mismatch at "+str((idx,axis,field,left,right)))
                ra,rb=x["trait_A"] in REPRO,x["trait_B"] in REPRO
                if ra!=rb:
                    counts[axis]["cross"]+=1
                    diff=float(a["K_A"])-float(a["K_B"])
                    require(diff!=0,"Original cross-organ contrast became tied")
                    counts[axis]["wins"]+=int((ra and diff>0) or (rb and diff<0))
            else:
                require(a["status"].startswith("HOLD_"),"Malformed historical hold")
                counts[axis]["hold"]+=1
    report={"status":"PASS_FROZEN_ORIGINAL_BATCH_K_NUMERIC_PARITY",
            "batch":batch,"n_pair_ids":len(pairs),"axes":counts,
            "max_absolute_numeric_K_or_logK_difference":maxdiff,
            "full_760_biological_independent_validation":False}
    save(output,report)
    return report

def summarize(output_dir,audit_dir,report_file):
    # Recheck all uploaded fresh K outputs again in the aggregation job.
    ax={a:{"pass":0,"hold":0,"cross":0,"wins":0} for a in ("S3","prune_only")}
    files={}
    total=0
    maxdiff=0.0
    for b in BATCHES:
        fresh=output_dir/(b+"_fresh.json")
        audit=audit_dir/(b+"_audit.json")
        require(fresh.is_file() and audit.is_file(),"Missing full source-K R pair batch: "+b)
        documented=json.loads(audit.read_text())
        checked=compare(b,fresh,audit_dir/(b+"_rechecked.json"))
        require(documented==checked,"Original batch verification claims changed: "+b)
        total+=checked["n_pair_ids"]
        maxdiff=max(maxdiff,checked["max_absolute_numeric_K_or_logK_difference"])
        for tree in ax:
            for field in ax[tree]:
                ax[tree][field]+=checked["axes"][tree][field]
        files[b]=hashlib.sha256(fresh.read_bytes()).hexdigest()
    require(total==760,"Not all 760 original family×trait-pair K fits regenerated")
    require(ax=={
        "S3":{"pass":760,"hold":0,"cross":406,"wins":313},
        "prune_only":{"pass":747,"hold":13,"cross":397,"wins":314}},
        "Original empirical K support/counts not reproduced by raw-v7 rerun")
    result={"status":FINAL,"original_source":"AusTraits v7.0.0",
            "original_public_parquet_sha256":SHA,
            "original_source_qualified_pairs":760,
            "full_native_S3_and_prune_K_recomputed":True,
            "recomputed_batch_count":len(BATCHES),
            "axes":ax,"max_absolute_numeric_K_or_logK_difference":maxdiff,
            "batch_source_sha256":files,
            "new_trait_discovery_or_selection_tests":0,
            "independent_original_measurement_replication":False,
            "raw_source_species_measurements_archived":False}
    save(report_file,result)
    return result

def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("prepare","compare","summarize"),required=True)
    p.add_argument("--batch-dir",type=Path)
    p.add_argument("--batch")
    p.add_argument("--fresh",type=Path)
    p.add_argument("--fresh-dir",type=Path)
    p.add_argument("--audit-dir",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.mode=="prepare":
        require(a.batch_dir is not None,"Source-only original batch output path needed")
        result=prepare(a.batch_dir,a.output)
    elif a.mode=="compare":
        require(a.batch and a.fresh,"One-batch comparison requires fresh K output")
        result=compare(a.batch,a.fresh,a.output)
    else:
        require(a.fresh_dir and a.audit_dir,"Full aggregation requires 24 fresh K batches")
        result=summarize(a.fresh_dir,a.audit_dir,a.output)
    print(json.dumps({"status":result["status"],"batch":result.get("batch"),
                      "n_pairs":result.get("n_pair_ids",result.get("original_source_qualified_pairs")),
                      "axes":result.get("axes")},sort_keys=True))
if __name__=="__main__":
    main()
