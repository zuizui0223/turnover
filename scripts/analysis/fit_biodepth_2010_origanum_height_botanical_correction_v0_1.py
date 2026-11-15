#!/usr/bin/env python3
"""POST-RESULT source-only botanical correction sensitivity for BIODEPTH height FD.

Original GIFT height 13m for Origanum vulgare retained as primary historical
record. Refit same 174 original 2010 plots using independent published .7/.9/1m
as exploratory quality scenarios. No plot or model selection by outcome.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from audit_biodepth_gift_height_references_v0_1 import run as provenance
from audit_biodepth_103_taxa_gift_height_v0_1 import source
from fit_biodepth_2010_sown_height_fd_biomass_v0_1 import composition,evaluate

ALTERNATIVES={"Pladias_0_70m":0.70,"Kew_0_90m":0.90,"RHS_1_00m":1.00}
ORIGINAL_HEIGHT=13.0
SPECIES="origanum vulgare"

def finiteplot(cells):
    return hashlib.sha256(json.dumps(
       sorted([(r["site"],r["plot"],r["year"],repr(r["response"])) for r in cells]),
       separators=(",",":"),sort_keys=True).encode()).hexdigest()

def ood(plots,site="Sheffield"):
    test=np.array([x["mpd"] for x in plots if x["site"]==site],float)
    train=np.array([x["mpd"] for x in plots if x["site"]!=site],float)
    if len(test)!=20 or len(train)!=154:raise ValueError("Original source Sheffield/other eligibility changed")
    mean=float(train.mean());sd=float(train.std(ddof=0))
    if sd<=0:raise ValueError("Training source dispersion degenerate")
    return {"n_source_original_test_plots":len(test),
        "source_test_minmax_logheight_MPD":[float(test.min()),float(test.max())],
        "source_train_minmax_logheight_MPD":[float(train.min()),float(train.max())],
        "source_train_mean_logheight_MPD":mean,
        "source_test_mean_logheight_MPD":float(test.mean()),
        "source_test_plots_outside_train_range":int(((test<train.min())|(test>train.max())).sum()),
        "source_test_plots_abs_z_gt3":int((np.abs((test-mean)/sd)>3).sum()),
        "source_test_max_abs_z":float(np.abs((test-mean)/sd).max())}

def main(a):
    prior=json.loads(Path(a.prior).read_text())
    gate=json.loads(Path(a.provenance).read_text())
    anomaly=json.loads(Path(a.anomaly).read_text())
    if prior["status"]!="POSTRESULT_BIODEPTH_HEIGHT_FD_OUT_OF_SITE_VALIDATION_ESTIMATED":
        raise ValueError("Original primary prior site holdout result not verified")
    if gate["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":
        raise ValueError("Original GIFT bibliography source gate not passed")
    if (anomaly["original_GIFT_aggregate_max_height_m"]!=13 or
        anomaly["raw_reference_1997_13m_ref_ID"]!=263 or
        anomaly["external_Kew_upper_height_m"]!=.9):
        raise ValueError("Source published anomalous Origanum value not verified")
    s_rows=source(a.species,"species")
    c_rows=source(a.codes,"codes")
    current,h=provenance(s_rows,c_rows,return_values=True)
    if (current["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS" or
        current["GIFT_original_target_species_height_and_reference_fingerprint_sha256"]!=
        gate["GIFT_original_target_species_height_and_reference_fingerprint_sha256"] or
        current["GIFT_bibliography_content_sha256"]!=gate["GIFT_bibliography_content_sha256"]):
        raise ValueError("GIFT original max-height trait source fingerprint changed")
    if len(h)!=88 or h.get(SPECIES)!=ORIGINAL_HEIGHT:
        raise ValueError("Original Origanum GIFT 13m among 88 original taxa not reproduced")
    treatments={}
    response_hash=None
    baseline=None
    for label,value in [("original_GIFT_13m",ORIGINAL_HEIGHT),*ALTERNATIVES.items()]:
        adjusted=dict(h);adjusted[SPECIES]=value
        plots,cells,missing,sites=composition(s_rows,c_rows,a.design,a.community,adjusted,current)
        if len(plots)!=174 or len(cells)!=521 or missing!=1 or len(sites)!=7:
            raise ValueError("All source botanical scenarios require identical 174 original plots and 521 response rows")
        source_hash=finiteplot(cells)
        if response_hash is None:response_hash=source_hash
        elif source_hash!=response_hash:
            raise ValueError("Original biomass response sample changed under height correction")
        r=evaluate(cells,sorted(sites))
        if label=="original_GIFT_13m":
            baseline=r
            if abs(r["primary_equal_site_FD_incremental_holdout_SSE_gain"]-
                    prior["primary"]["primary_equal_site_FD_incremental_holdout_SSE_gain"])>1e-10:
                raise ValueError("Original seven-site source-trained FD failed to replay prior frozen result")
            for x in r["site_holdout_records"]:
                saved=next(z for z in prior["primary"]["site_holdout_records"] if z["heldout_site"]==x["heldout_site"])
                if abs(x["M1_sse"]-saved["M1_sse"])>1e-7 or abs(x["M2_sse"]-saved["M2_sse"])>1e-7:
                    raise ValueError("Original seven-site source SSE not numerically reproduced")
        else:
            for x in r["site_holdout_records"]:
                saved=next(z for z in baseline["site_holdout_records"] if z["heldout_site"]==x["heldout_site"])
                if abs(x["M0_sse"]-saved["M0_sse"])>1e-7:
                    raise ValueError("Height change cannot change source baseline M0 error")
        treatments[label]={
          "source_substitution_m":value,
          "source_botanical_reference":
              "Kew POWO original plant profile upper 0.9m" if label=="Kew_0_90m"
              else "Pladias original Czech flora upper 0.7m" if label=="Pladias_0_70m"
              else "Royal Horticultural Society upper 1.0m" if label=="RHS_1_00m"
              else "Original GIFT3.1 species source max across referenced traits, ref263=13m",
          "heldout_biomass_result":r,
          "Sheffield_source_mpd_geometry":ood(plots)}
    return {
      "version":"v0.1",
      "status":"BIODEPTH_POSTRESULT_ORIGANUM_SOURCE_HEIGHT_SENSITIVITY_ESTIMATED",
      "original_source_GIFT_Origanum_vulgare_maxheight_m":ORIGINAL_HEIGHT,
      "GIFT_source_reference_original_1997_ref_ID":263,
      "Kew_original_species_upper_height_m":.9,
      "original_2010_Community_response_plot_year_fingerprint_sha256":response_hash,
      "source_original_GIFT_88_height_references_fingerprint_sha256":current["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
      "n_original_plots_unchanged":174,"n_source_plot_year_response_unchanged":521,
      "n_original_sites_unchanged":7,
      "primary_unmodified_source_remains_historical_frozen":True,
      "external_source_based_scenarios_and_original":treatments,
      "original_source_GIFT_exclusion_or_replacement_applied_to_repository_raw_data":False,
      "nonclaims":[
         "A source-specific botanical correction after a model failure is retrospective sensitivity, not new original ecological confirmation",
         "Source citation ref263 GIFT recorded 13m; 1997 original book itself was not checked",
         "Kew/Pladias/RHS height ranges refer species in general, not realized height of original BIODEPTH site plants",
         "Original 2010 Hector Community response only, not original 2005 Shoots edition",
         "No same-year species biomass predictor leakage, original 174 site plot/year sample unchanged",
         "Seven sites exclude Greece; do not extrapolate to eight or worldwide grasslands",
         "No phylogenetic memory rho or causal trait complementarity mechanism identified",
         "Original global sPlotOpen BIEN/source and BIODEPTH strict six sites, NEON authenticated gates unchanged"]
    }

def fixture():
    plots=[{"site":"Sheffield","mpd":.4} for _ in range(20)]
    plots +=[{"site":"Germany","mpd":.2+i/100} for i in range(154)]
    a=ood(plots)
    assert a["n_source_original_test_plots"]==20 and a["source_test_plots_abs_z_gt3"]==0
    assert set(ALTERNATIVES.values())=={.7,.9,1.0}
    return {"status":"BOTANICAL_HEIGHT_CORRECTION_FIXTURE_PASS","checks":2}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("species","codes","design","community","provenance","anomaly","prior","out"):
        p.add_argument("--"+arg)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture()))
    else:
        if not all(getattr(a,arg) for arg in ("species","codes","design","community","provenance","anomaly","prior","out")):
            p.error("All eight source and prior result paths required")
        result=main(a)
        out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
        brief={k:{"m":v["source_substitution_m"],
                  "FD_site_equal_gain":v["heldout_biomass_result"]["primary_equal_site_FD_incremental_holdout_SSE_gain"],
                  "FD_CI95":v["heldout_biomass_result"]["primary_site_bootstrap_10000_ci95"],
                  "positive_sites":v["heldout_biomass_result"]["sites_positive_incremental_gain"],
                  "Sheffield_gain":next(x["height_fd_increment_over_cwm"] for x in v["heldout_biomass_result"]["site_holdout_records"] if x["heldout_site"]=="Sheffield"),
                  "Sheffield_mpd_ood":v["Sheffield_source_mpd_geometry"]}
                for k,v in result["external_source_based_scenarios_and_original"].items()}
        print("BIODEPTH_ORIGANUM_MAXHEIGHT_SOURCE_REPAIR",json.dumps(brief,sort_keys=True))
