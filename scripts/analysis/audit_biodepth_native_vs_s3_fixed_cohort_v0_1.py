#!/usr/bin/env python3
"""BIODEPTH source-corrected S3 vs direct-tip only paired 102-plot reanalysis.

Follows pre-outcome-of-this-new-diagnostic design in
docs/BIODEPTH_PAIRED_NATIVE_GRAFT_COHORT_DIAGNOSTIC_V0_1.md
The existing 150-plot and 102-plot results are first exactly reverified.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
import numpy as np

from fit_biodepth_2010_sown_height_fd_biomass_v0_1 import composition,baseline
from fit_biodepth_matched_pd_fd_biomass_transport_v0_1 import (
    source_checks,score_sites,bootstrap_verdict,SEED,REPS,ORIGINAL_SITES
)

NATIVE_SITES={"Germany":14,"Ireland":26,"Portugal":8,"Sheffield":18,
              "Silwood":14,"Sweden":14,"Switzerland":8}
SITES=sorted(NATIVE_SITES)
ABS_TOL=1e-10


def compare_exact_results(now:list, prior:list, label:str):
    earlier={r["site"]:r for r in prior}
    if set(r["site"] for r in now)!=set(earlier) or len(now)!=7:
        raise ValueError("PARENT_SOURCE_HOLD: original site identities differed "+label)
    for row in now:
        previous=earlier[row["site"]]
        for key in ("baseline_sse","with_pd_sse","pd_incremental_SSE_gain"):
            if not math.isclose(row[key],previous[key],rel_tol=0,abs_tol=ABS_TOL):
                raise ValueError("PARENT_SOURCE_HOLD: original source model not replayed "+label+" "+row["site"]+" "+key)
        if row["n_units"]!=previous["n_units"]:
            raise ValueError("PARENT_SOURCE_HOLD: response count changed "+label+" "+row["site"])


def scores_summary(rows:list)->dict:
    return bootstrap_verdict(rows)


def paired(a:list,b:list,name:str)->dict:
    """Site-paired b−a difference; each site same original named field."""
    x={r["site"]:r for r in a}
    y={r["site"]:r for r in b}
    if set(x)!=set(y) or set(x)!=set(SITES):
        raise ValueError("SITE_HOLD: paired comparison missing original fields "+name)
    delta=np.array([y[s]["pd_incremental_SSE_gain"]-x[s]["pd_incremental_SSE_gain"] for s in SITES])
    rng=np.random.default_rng(SEED)
    draw=delta[rng.integers(0,7,size=(REPS,7))].mean(axis=1)
    bounds=np.quantile(draw,[.025,.975])
    return {"name":name,
            "mean_gains_difference":float(delta.mean()),
            "mean_gains_difference_pp":float(100*delta.mean()),
            "site_paired_bootstrap_ci95_pp":[float(100*bounds[0]),float(100*bounds[1])],
            "per_site_difference_pp":{s:float(100*v) for s,v in zip(SITES,delta)},
            "n_sites_difference_positive":int((delta>0).sum()),
            "site_resampling_iterations":REPS,
            "bootstrap_seed":SEED,
            "interpretation":"Descriptive within-original-source-site comparison, not independent causal intervention"}


def rank_check_before_response(source_plots:dict,native_plots:dict):
    if set(native_plots)-set(source_plots):
        raise ValueError("SOURCE_HOLD: native source cohort not subset of full S3 cohort")
    affected=0
    pd_changed=0
    fd_changed=0
    for key in native_plots:
        f=source_plots[key];n=native_plots[key]
        if f["source_joint_species"]!=n["source_joint_species"]:affected+=1
        if abs(f["pd"]-n["pd"])>1e-10:pd_changed+=1
        if abs(f["cwm"]-n["cwm"])>1e-10 or abs(f["mpd"]-n["mpd"])>1e-10:fd_changed+=1
    # The native 102 cohort was defined *before* the earlier 102-outcome opening.
    counts=Counter(k[0] for k in native_plots)
    if len(native_plots)!=102 or dict(counts)!=NATIVE_SITES:
        raise ValueError("SOURCE_HOLD: original preexisting 102 native plots 7 field counts changed")
    for held in SITES:
        train=[{**source_plots[k],"year":year,"response":0.}
               for k in native_plots for year in (1,2,3) if k[0]!=held]
        baseline_x,_,_=baseline(train,include_mean=True,include_disp=True)
        if np.linalg.matrix_rank(baseline_x)!=baseline_x.shape[1]:
            raise ValueError("MODEL_SOURCE_HOLD: 102-full S3 M2 rank deficient")
        for source_name,pd in [
           ("full",np.array([r["pd"] for r in train],dtype=float)),
           ("native",np.array([native_plots[(r["site"],r["plot"])]["pd"] for r in train],dtype=float))
        ]:
            spread=pd.std(ddof=0)
            if spread<=1e-9 or not np.isfinite(spread):
                raise ValueError("MODEL_SOURCE_HOLD: 102 source PD has no variability "+source_name)
            augmented=np.column_stack([baseline_x,(pd-pd.mean())/spread])
            if np.linalg.matrix_rank(augmented)!=augmented.shape[1]:
                raise ValueError("MODEL_SOURCE_HOLD: 102 source training model rank deficient "+source_name)
    return {
      "native_source_plots":len(native_plots),
      "native_source_plots_by_site":dict(sorted(counts.items())),
      "n_102_plots_with_more_S3_tip_coverage_than_native":affected,
      "n_102_plots_with_different_PD_value":pd_changed,
      "n_102_plots_with_different_CWM_or_FD":fd_changed,
      "full_vs_native_plot_year_identity_fixed":True,
      "all_seven_source_site_baselines_rank_qualified":True}


def main(args:argparse.Namespace)->dict:
    parent=json.loads(Path(args.previous).read_text(encoding="utf8"))
    if (parent["status"]!="POSTRESULT_BIODEPTH_MATCHED_PD_FD_BIOMASS_ESTIMATED"
        or parent["source_original_matched_plots"]!=150
        or parent["source_matched_plot_year_numeric_responses"]!=449
        or parent["mandatory_native_only_sensitivity"]["n_plots"]!=102
        or parent["mandatory_native_only_sensitivity"]["source_plot_years"]!=305):
        raise ValueError("PARENT_SOURCE_HOLD: original PD cohort/source response changed")
    srows,crows,all150,native102,height,qa=source_checks(args)
    support=rank_check_before_response(all150,native102)
    print("PRE_RESPONSE_PAIRED_102_SOURCE_GATE_PASS",json.dumps(support,sort_keys=True),flush=True)

    original_plots,original_cells,missing,orig_sites=composition(
        srows,crows,args.design,args.community,height,qa)
    if len(original_plots)!=174 or len(original_cells)!=521 or missing!=1:
        raise ValueError("PARENT_SOURCE_HOLD: original 174/521 Community result not reproduced")
    full150=[{**r,**all150[(r["site"],r["plot"])]} for r in original_cells
              if (r["site"],r["plot"]) in all150]
    native_fixed=[{**r,**native102[(r["site"],r["plot"])]} for r in original_cells
                  if (r["site"],r["plot"]) in native102]
    full_fixed=[{**r,**all150[(r["site"],r["plot"])]} for r in original_cells
                if (r["site"],r["plot"]) in native102]
    if len(full150)!=449 or len(full_fixed)!=305 or len(native_fixed)!=305:
        raise ValueError("PARENT_SOURCE_HOLD: historical response source record counts changed")
    if [(r["site"],r["plot"],r["year"],r["response"]) for r in full_fixed] != [
        (r["site"],r["plot"],r["year"],r["response"]) for r in native_fixed]:
        raise ValueError("RESPONSE_HOLD: full/native source responses not strictly identical")

    original_full=score_sites(full150,SITES,method="mass")
    original_native=score_sites(native_fixed,SITES,method="mass")
    compare_exact_results(original_full,parent["primary_biomass_incremental_PD_over_FD_and_CWM"]["site_records"],"full150")
    compare_exact_results(original_native,parent["mandatory_native_only_sensitivity"]["prediction"]["site_records"],"native102")
    print("PARENT_EFFECT_REPLAY_EXACT_PASS",json.dumps({
        "full_150_mean":float(np.mean([r["pd_incremental_SSE_gain"] for r in original_full])),
        "native_102_mean":float(np.mean([r["pd_incremental_SSE_gain"] for r in original_native])),
        "unchanged_original_response":"exact 150 and 102 response cohorts",
    },sort_keys=True),flush=True)

    # NEW previously uncomputed original S3 full trait/PD coverage on same 102 plots.
    full102=score_sites(full_fixed,SITES,method="mass")
    full_cwmfd_native_pd=[
        {**r,"pd":native102[(r["site"],r["plot"])]["pd"]}
        for r in full_fixed
    ]
    native_PD_with_full_FD=score_sites(full_cwmfd_native_pd,SITES,method="mass")
    for a,b in zip(full102,native_PD_with_full_FD):
        if a["site"]!=b["site"] or not math.isclose(a["baseline_sse"],b["baseline_sse"],rel_tol=0,abs_tol=ABS_TOL):
            raise ValueError("MODEL_HOLD: PD-only contrast did not retain exact same CWM/FD M2 reference SSE")
    return {
        "status":"POSTRESULT_PAIRED_102_NATIVE_S3_COHORT_DIAGNOSTIC_ESTIMATED",
        "design":"docs/BIODEPTH_PAIRED_NATIVE_GRAFT_COHORT_DIAGNOSTIC_V0_1.md",
        "original_current_source_response":"Hector2010 Community only, equal species planned weights; no same-year response-derived trait weighting",
        "original_150_cohort":{"plots":150,"plot_years":449,
                               "source_tree_and_trait":"all S3 source-covered taxa (84 candidate species)",
                               "mass_PD_increment":scores_summary(original_full)},
        "replayed_102_native_cohort":{"plots":102,"plot_years":305,
                                      "source_tree_and_trait":"only native backbone species (78 candidate species)",
                                      "mass_PD_increment":scores_summary(original_native)},
        "new_102_cohort_full_S3":{"plots":102,"plot_years":305,
                                   "source_tree_and_trait":"full S3 species/tip coverage but exact native-supported plots",
                                   "mass_PD_increment":scores_summary(full102)},
        "new_102_cohort_full_CWM_FD_with_native_PD":{"plots":102,"plot_years":305,
                                   "source_tree_and_trait":"full-S3 CWM/FD fixed; native-only PD predictor",
                                   "mass_PD_increment":scores_summary(native_PD_with_full_FD)},
        "paired_comparison_A_full_150_to_full_102":paired(original_full,full102,"sample restriction holding source S3 feature definition"),
        "paired_comparison_B_full_102_to_native_102":paired(full102,original_native,"native-tip traits+PD with 102 plots fixed"),
        "paired_comparison_C_full_102_PD_to_native_102_PD_given_same_CWM_FD":paired(full102,native_PD_with_full_FD,"only PD predictor species subset changed with full-S3 CWM and FD baseline held exactly fixed"),
        "source_structure":support,
        "n_distinct_original_source_sites":7,
        "source_original_GIFT_fingerprint":qa["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
        "parent_original_150_and_102_site_sse_verified_exact":True,
        "all_models_heldout_by_entire_original_field":True,
        "historical_outcomes_seen_prior_to_new_design":True,
        "no_original_family_K_or_BIEN_rho_matched":True,
        "nonclaims":[
           "Post-result retrospective diagnosis: sample definition and S3 source tip inclusion are not randomized ecological treatments",
           "The main direct-backbone-only -3.50% result is reproduced, not an independent second trial",
           "Paired 102 design fixes plot responses but all-native CWM/FD/PD change together in B",
           "PD-only C compares different plotted species contributions to dated distance, not independent phylogenetic backbone",
           "Source GIFT heights are species maximum reference reports, not biomass-weighted or actual measured site heights",
           "Seven original field experiments are the true independent units; bootstrap uncertainty is descriptive",
           "Does not estimate lineage-specific trait Blomberg K or infer PD→FD→mass mediation",
           "Global BIEN×sPlotOpen 201-system, original BIODEPTH six-site source, and NEON auth studies remain HOLD"
        ]}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("species","codes","design","community","provenance","phylogeny-gate",
                 "joint-gate","tree-crosswalk","tree-distances","previous","out"):
        p.add_argument("--"+name)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        x=[{"site":s,"baseline_sse":2.0,"with_pd_sse":1.5,"pd_incremental_SSE_gain":.25} for s in SITES]
        y=[{"site":s,"baseline_sse":2.0,"with_pd_sse":1.6,"pd_incremental_SSE_gain":.20} for s in SITES]
        o=paired(x,y,"test")
        assert abs(o["mean_gains_difference_pp"]+5.0)<1e-10
        assert sum(NATIVE_SITES.values())==102 and len(NATIVE_SITES)==7
        assert REPS==10000
        print("PAIRED_102_SITE_DIAGNOSTIC_FIXTURE_PASS")
    else:
        names=("species","codes","design","community","provenance","phylogeny-gate",
               "joint-gate","tree-crosswalk","tree-distances","previous","out")
        if not all(getattr(a,n.replace("-","_")) for n in names):
            p.error("Need all original source/parent JSON paths and output")
        result=main(a)
        path=Path(a.out)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("BIODEPTH_PAIRED_NATIVE_FULL_S3_RESULT",
              json.dumps({k:v for k,v in result.items()
                          if k not in ("nonclaims",)},sort_keys=True),flush=True)
