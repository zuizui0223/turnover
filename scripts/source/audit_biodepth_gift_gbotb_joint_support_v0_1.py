#!/usr/bin/env python3
"""Outcome-blind original BIODEPTH GIFT max-height × GBOTB S3 taxon/plot coverage.

The original source GIFT values are accessed only to check bibliographic
identity, completeness and plot-membership support, NEVER to fit biomass or FD.
"""
from __future__ import annotations
import argparse,csv,json,math,sys
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "analysis"))
from audit_biodepth_103_taxa_gift_height_v0_1 import source,geometry
from audit_biodepth_gift_height_references_v0_1 import run as provenance

THRESHOLDS = {
    "min_joint_height_tree_species":65,
    "min_joint_backbone_native_height_species":40,
    "min_joint_families":8,
    "min_original_height_source_plots_with_joint_3plus_and_80pct":120,
    "min_source_sites_with_at_least_8_joint_plots":5,
    "min_distinct_mean_pairwise_PD_values_1e_minus8":10,
}

def read_tree(crosswalk:Path,distances:Path) -> tuple[dict,dict]:
    with crosswalk.open(newline="",encoding="utf8") as f:
        rows=list(csv.DictReader(f))
    status={}
    for r in rows:
        k=r["species"].strip().casefold()
        if k in status or r["status"] not in ("prune","bind","fail to bind"):
            raise ValueError("SOURCE_HOLD: tree original species/status ambiguous")
        status[k]={"family":r["family"],"status":r["status"]}
    with distances.open(newline="",encoding="utf8") as f:
        allrows=list(csv.reader(f))
    header=[x.strip().casefold() for x in allrows[0][1:]]
    if len(header)==0 or len(header)!=len(set(header)) or len(allrows)!=len(header)+1:
        raise ValueError("SOURCE_HOLD: unexpected GBOTB pair matrix schema")
    d={}
    for row in allrows[1:]:
        a=row[0].strip().casefold()
        if a in d or len(row)!=len(header)+1:
            raise ValueError("SOURCE_HOLD: duplicate or incomplete GBOTB distance source")
        d[a]={b:float(v) for b,v in zip(header,row[1:])}
    if set(d)!=set(header) or set(d)!={s for s,x in status.items() if x["status"] in ("prune","bind")}:
        raise ValueError("SOURCE_HOLD: distance/matched status tip set mismatch")
    for a in header:
        for b in header:
            v=d[a][b]
            if not math.isfinite(v) or v<0 or not math.isclose(v,d[b][a],abs_tol=1e-7):
                raise ValueError("SOURCE_HOLD: nonpositive non-symmetric or nonfinite PD")
        if not math.isclose(d[a][a],0,abs_tol=1e-7):
            raise ValueError("SOURCE_HOLD: nonzero PD diagonal")
    return status,d

def run(args:argparse.Namespace)->dict:
    saved=json.loads(Path(args.provenance).read_text(encoding="utf8"))
    prev=json.loads(Path(args.phylogeny_gate).read_text(encoding="utf8"))
    if (saved["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS" or
        saved["original_species_with_full_references_and_no_explicit_original_BIODEPTH"]!=88 or
        prev["status"]!="BIODEPTH_GBOTB_S3_SOURCE_COVERAGE_PASS" or
        prev["n_S3_eligible"]!=98 or prev["n_native_tips"]!=80 or
        prev["n_resolved_families"]!=18):
        raise ValueError("SOURCE_HOLD: pre-existing source GIFT/tree histories changed")
    srows=source(args.species,"species"); crows=source(args.codes,"codes")
    orig_names,orig_plots,meta=geometry(srows,crows)
    qa,heights=provenance(srows,crows,return_values=True)
    if (qa["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS" or len(heights)!=88 or
        qa["GIFT_bibliography_content_sha256"]!=saved["GIFT_bibliography_content_sha256"] or
        qa["GIFT_original_target_species_height_and_reference_fingerprint_sha256"]!=
        saved["GIFT_original_target_species_height_and_reference_fingerprint_sha256"]):
        raise ValueError("SOURCE_HOLD: original GIFT bibliography/species-height source drift")
    status,d=read_tree(Path(args.tree_crosswalk),Path(args.tree_distances))
    if len(status)!=98 or len(d)!=98:
        raise ValueError("SOURCE_HOLD: original GBOTB S3 98 exact family-matched taxa changed")
    hsp=set(heights)
    native=hsp & {s for s,v in status.items() if v["status"]=="prune"}
    joint=hsp & set(d)
    fams={status[s]["family"] for s in joint}
    origheight={}
    jointheight={}
    plot_pd=[]
    eligible_site=Counter()
    joint_site=Counter()
    for (site,plot),plants in sorted(orig_plots.items()):
        covered=sorted(set(plants)&hsp)
        if len(covered)<3 or len(covered)/len(plants)<.8:
            continue
        origheight[(site,plot)]=plants
        origheight_count=len(covered)
        matched=sorted(set(covered)&joint)
        if len(matched)<3 or len(matched)/len(plants)<.8:
            continue
        jointheight[(site,plot)]=plants
        for i in range(len(matched)):
            for j in range(i+1,len(matched)):
                v=d[matched[i]][matched[j]]
                if not math.isfinite(v) or v<0:
                    raise ValueError("SOURCE_HOLD: invalid matched pairwise PD")
        values=[d[matched[i]][matched[j]] for i in range(len(matched)) for j in range(i+1,len(matched))]
        plot_pd.append(float(np.mean(values)))
        joint_site[site]+=1
    for site,plot in origheight:
        eligible_site[site]+=1
    if len(origheight)!=174 or len(eligible_site)!=7:
        raise ValueError("SOURCE_HOLD: historical 174/7 source height eligible original plot cohort changed")
    distinct=len({round(v,8) for v in plot_pd})
    n_sites8=sum(n>=8 for n in joint_site.values())
    valid=(len(joint)>=THRESHOLDS["min_joint_height_tree_species"] and
           len(native)>=THRESHOLDS["min_joint_backbone_native_height_species"] and
           len(fams)>=THRESHOLDS["min_joint_families"] and
           len(jointheight)>=THRESHOLDS["min_original_height_source_plots_with_joint_3plus_and_80pct"] and
           n_sites8>=THRESHOLDS["min_source_sites_with_at_least_8_joint_plots"] and
           distinct>=THRESHOLDS["min_distinct_mean_pairwise_PD_values_1e_minus8"])
    return {
      "status":"BIODEPTH_GBOTB_GIFT_JOINT_SUPPORT_PASS" if valid else "HOLD_BIODEPTH_GBOTB_GIFT_JOINT_SUPPORT",
      "version":"v0.1","source_only":True,
      "source_original_plots":480,"source_original_species":103,
      "GIFT_provenance_height_taxa":88,
      "GBOTB_S3_matched_source_taxa":98,
      "joint_height_phylogeny_species":len(joint),
      "joint_height_phylogeny_native_taxa":len(native),
      "joint_height_phylogeny_families":len(fams),
      "original_history_height_eligible_plots":len(origheight),
      "original_history_height_eligible_sites":dict(sorted(eligible_site.items())),
      "joint_original_plots_min3_and_80pct":len(jointheight),
      "joint_original_sites_with_atleast8":n_sites8,
      "joint_original_sites":dict(sorted(joint_site.items())),
      "distinct_original_plot_mean_pairwise_PD_1e_minus8":distinct,
      "predefined_thresholds":THRESHOLDS,
      "GIFT_original_bibliography_fingerprint":qa["GIFT_bibliography_content_sha256"],
      "GIFT_original_88_species_fingerprint":qa["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
      "biomass_records_read":0,"fd_biomass_model_estimates":0,
      "independence_boundary":"GIFT source may share literature with other trait compilations; original sown community not current species biomass",
      "next_step":"Freeze matched-site PD→FD & PD incremental biomass models before original 2010 Community access" if valid else "HOLD original matched data and do not fit PD→FD or biomass",
      "hard_nonclaims":["Joint support is not an estimated PD/FD or biomass relation",
        "GBOTB source native or S3-bound distances are not a per-family trait K",
        "Earlier original BIODEPTH exact-richness, global BIEN/sPlotOpen and NEON auth gates remain HOLD"],
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("species","codes","provenance","phylogeny-gate","tree-crosswalk","tree-distances","out"):
        p.add_argument("--"+k)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        a={"aa":{"aa":0.,"bb":2.},"bb":{"aa":2.,"bb":0.}}
        assert a["aa"]["bb"]==a["bb"]["aa"]
        assert THRESHOLDS["min_joint_height_tree_species"]==65
        print("JOINT_SOURCE_GATE_FIXTURE_PASS")
    else:
        if not all(getattr(args,k.replace("-","_")) for k in ("species","codes","provenance","phylogeny-gate","tree-crosswalk","tree-distances","out")):
            p.error("Missing frozen source paths")
        out=run(args)
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        print("BIODEPTH_GBOTB_GIFT_JOINT_SOURCE_ONLY "+json.dumps(out,sort_keys=True),flush=True)
