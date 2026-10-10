#!/usr/bin/env python3
"""K-blind influence audit on the already-frozen source-dispersion archive.

Purely descriptive post-dispersion sensitivity; never re-estimates K, chooses
a source-error multiplier or changes the pre-frozen OU+source null model.
"""
from __future__ import annotations
import argparse, json, math, statistics
from collections import defaultdict
from pathlib import Path

RESULT_STATUS = "AUSTRAITS_K_SOURCE_DISPERSION_INFLUENCE_AUDITED"
EXPECTED_GRAPH = {"systems":254,"families":42,"traits":13}


def analyze(source:dict)->dict:
    if source.get("status")!="AUSTRAITS_K_CROSS_SOURCE_DISPERSION_ESTIMATED":
        raise ValueError("not frozen source dispersion")
    if source.get("no_K_response_used") is not True:
        raise ValueError("source/K separation not verified")
    if source.get("graph")!=EXPECTED_GRAPH or len(source.get("systems",[]))!=254:
        raise ValueError("source graph changed")
    if len(source.get("traits",{}))!=13:
        raise ValueError("source traits incomplete")
    grouped=defaultdict(list)
    calibrated=0
    zero_count=0
    for r in source["systems"]:
        if r.get("calibratable") is not True:
            continue
        v=r.get("relative_source_dispersion")
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
            raise ValueError("invalid source variance ratio")
        calibrated+=1
        zero_count+= v==0
        grouped[r["trait_name"]].append((r["family"],float(v)))
    if set(grouped)!=set(source["traits"]):
        raise ValueError("source traits missing calibrated systems")
    summaries={}
    for trait in sorted(grouped):
        rr=grouped[trait]
        fams=[r[0] for r in rr]
        if len(fams)!=len(set(fams)):
            raise ValueError("nonunique family source ratio per trait")
        vals=[r[1] for r in rr]
        median=float(statistics.median(vals))
        frozen=source["traits"][trait]["source_log_variance_ratio_median"]
        if frozen is None or abs(median-frozen)>1e-9*max(1,median):
            raise ValueError("source ratio no longer matches archived trait median")
        jack=[statistics.median([x for j,x in enumerate(vals) if j!=i])
              for i in range(len(vals))] if len(vals)>=2 else []
        summaries[trait]={
            "calibrated_family_systems":len(vals),
            "median_ratio":median,
            "zero_ratio_systems":sum(v==0 for v in vals),
            "leave_one_family_out_median_min":float(min(jack)) if jack else None,
            "leave_one_family_out_median_max":float(max(jack)) if jack else None,
            "min_family_specific_ratio":float(min(vals)),
            "max_family_specific_ratio":float(max(vals)),
            "qualified_for_forward_model":bool(source["traits"][trait]["calibratable_for_followon_process_null"]),
        }
    return {
        "status":RESULT_STATUS,"version":"v0.1",
        "source_input_status":source["status"],
        "graph":source["graph"],
        "calibrated_systems":calibrated,
        "zero_ratio_systems":zero_count,
        "zero_ratio_fraction":zero_count/calibrated,
        "trait_influence":summaries,
        "original_OU_source_parameters_unchanged":True,
        "interpretation":"Post-dispersion K-blind robustness summary; does not reclassify the original pre-frozen source OU process null."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    r=analyze(json.loads(a.source.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":RESULT_STATUS,"calibrated_systems":r["calibrated_systems"],
                      "zero_ratio_systems":r["zero_ratio_systems"],
                      "traits":len(r["trait_influence"])},sort_keys=True))

if __name__=="__main__":
    main()
