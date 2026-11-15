#!/usr/bin/env python3
"""Post-result BIODEPTH original maximum-height FD site OOD diagnostic.

Uses exact source-fingerprinted GIFT and Hector 2010 original biomass; refuses
to change the original frozen heldout model or select/omit observed plots.
Exports only site-level numeric summaries and error-concentration counts.
"""
from __future__ import annotations
import argparse,json,math,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from audit_biodepth_gift_height_references_v0_1 import run as provenance
from audit_biodepth_103_taxa_gift_height_v0_1 import source,geometry
from fit_biodepth_2010_sown_height_fd_biomass_v0_1 import baseline,composition

MODEL_EPS=1e-6
def core(a):
    p=json.loads(Path(a.provenance).read_text())
    if p["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":
        raise ValueError("GIFT attested bibliography source gate not passed")
    main=json.loads(Path(a.prior).read_text())
    if main["status"]!="POSTRESULT_BIODEPTH_HEIGHT_FD_OUT_OF_SITE_VALIDATION_ESTIMATED":
        raise ValueError("No original fixed 7-site heldout output to explain")
    s_rows=source(a.species,"species");c_rows=source(a.codes,"codes")
    pr,height=provenance(s_rows,c_rows,return_values=True)
    if (pr["GIFT_original_target_species_height_and_reference_fingerprint_sha256"]!=p["GIFT_original_target_species_height_and_reference_fingerprint_sha256"]
       or pr["GIFT_bibliography_content_sha256"]!=p["GIFT_bibliography_content_sha256"]):
        raise ValueError("GIFT provenance source drift, diagnostic stopped")
    plots,cells,missing,sites_counts=composition(s_rows,c_rows,a.design,a.community,height,pr)
    if len(plots)!=174 or len(cells)!=521 or missing!=1 or len(sites_counts)!=7:
        raise ValueError("Original fixed 174plots/521rows source population changed")
    bysite={r["heldout_site"]:r for r in main["primary"]["site_holdout_records"]}
    if set(bysite)!=set(sites_counts):
        raise ValueError("Site roster changed since original heldout experiment")
    _,original_planted_roster,_=geometry(s_rows,c_rows)
    too_tall={n:v for n,v in height.items() if v>10}
    if len(too_tall)!=1:
        raise ValueError("Previous source one species max-height above 10m flag changed")
    results=[]
    for held in sorted(sites_counts):
        train=[r for r in cells if r["site"]!=held]
        test=[r for r in cells if r["site"]==held]
        x1,mu1,sd1=baseline(train,True,False)
        x2,mu2,sd2=baseline(train,True,True)
        xx1,_,_=baseline(test,True,False,mu1,sd1)
        xx2,_,_=baseline(test,True,True,mu2,sd2)
        if np.linalg.matrix_rank(x1)!=x1.shape[1] or np.linalg.matrix_rank(x2)!=x2.shape[1]:
            raise ValueError("Frozen model source geometry lost full rank")
        y=np.array([r["response"] for r in train])
        z=np.array([r["response"] for r in test])
        b1=np.linalg.lstsq(x1,y,rcond=None)[0]
        b2=np.linalg.lstsq(x2,y,rcond=None)[0]
        pred1=xx1@b1;pred2=xx2@b2
        sq1=(z-pred1)**2;sq2=(z-pred2)**2
        sse1=float(sq1.sum());sse2=float(sq2.sum())
        prev=bysite[held]
        if (abs(sse1-prev["M1_sse"])>MODEL_EPS or abs(sse2-prev["M2_sse"])>MODEL_EPS):
            raise ValueError("Original source/model numerical replay disagrees for "+held)
        sitep=[r for r in plots if r["site"]==held]
        trainp=[r for r in plots if r["site"]!=held]
        tr=np.array([r["mpd"] for r in trainp]);te=np.array([r["mpd"] for r in sitep])
        if tr.size<50 or te.size<8:
            raise ValueError("Original site plot source support differs")
        mean=float(tr.mean());sd=float(tr.std(ddof=0))
        if sd<=0:raise ValueError("Training-only FD distribution has zero variation")
        outs=((te<tr.min())|(te>tr.max()))
        extreme=np.abs((te-mean)/sd)>3
        fd_z=x2[:,-1];proj=x1@np.linalg.lstsq(x1,fd_z,rcond=None)[0]
        denom=float(np.sum((fd_z-fd_z.mean())**2))
        r2=1-float(np.sum((fd_z-proj)**2))/denom if denom>0 else float("nan")
        vif=1/max(1-r2,1e-12) if math.isfinite(r2) else None
        deltas=defaultdict(float)
        for i,rec in enumerate(test):
            deltas[rec["plot"]]+=float(sq2[i]-sq1[i])
        positive=np.array(sorted((max(0,x) for x in deltas.values()),reverse=True))
        excess=float(positive.sum())
        negative=sum(v<0 for v in deltas.values())
        original_test_plots={r["plot"] for r in sitep}
        tall_plots=sum(any(n in too_tall for n in planted)
            for (site,p),planted in original_planted_roster.items()
            if site==held and p in original_test_plots)
        row={
            "site":held,"n_original_test_plots":len(sitep),"n_heldout_plot_years":len(test),
            "n_orig_train_plots":len(trainp),
            "train_source_FD_mpd_minmax":[float(tr.min()),float(tr.max())],
            "test_source_FD_mpd_minmax":[float(te.min()),float(te.max())],
            "train_source_FD_mpd_mean":mean,"train_source_FD_mpd_sd":sd,
            "test_source_FD_mpd_mean":float(te.mean()),
            "n_test_plots_mpd_outside_training_observed_range":int(outs.sum()),
            "n_test_plots_mpd_abs_z_gt3":int(extreme.sum()),
            "test_mpd_z_mean":float(((te-mean)/sd).mean()),
            "test_mpd_max_abs_z":float(np.max(np.abs((te-mean)/sd))),
            "train_original_M1_design_condition_number":float(np.linalg.cond(x1)),
            "train_original_M2_design_condition_number":float(np.linalg.cond(x2)),
            "train_M2_standardized_FD_beta":float(b2[-1]),
            "train_M2_FD_conditional_R_squared":float(r2),
            "train_M2_FD_conditional_VIF":float(vif) if vif is not None else None,
            "M1_source_SSE":sse1,"M2_source_SSE":sse2,
            "heldout_original_SSE_gain_FD_over_M1":1-sse2/sse1,
            "n_test_plots_FD_model_better_than_M1":negative,
            "n_test_plots_FD_model_worse_than_M1":sum(x>0 for x in deltas.values()),
            "top1_test_plot_share_of_positive_added_SSE":float(positive[0]/excess) if excess>0 else None,
            "top3_test_plots_share_of_positive_added_SSE":float(positive[:3].sum()/excess) if excess>0 else None,
            "source_original_sown_eligible_plots_with_above10m_maxheight_species":tall_plots,
        }
        results.append(row)
    return {
       "version":"v0.1","status":"BIODEPTH_ORIGINAL_7SITE_FD_FAILURE_MODEL_AND_PREDICTOR_GEOMETRY_AUDITED",
       "source_roster":"Original 2010 BIODEPTH species and Community source; GIFT 3.1 original accepted maxheight",
       "source_fingerprint":pr["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
       "source_ref_fingerprint":pr["GIFT_bibliography_content_sha256"],
       "original_heldout_result_reproduced_all_sites":True,
       "original_site_count":len(results),"original_plot_count":len(plots),"plot_year_rows":len(cells),
       "original_height_max_above_10m_taxon_names_source_only":sorted(too_tall),
       "site_failure_diagnostics":results,
       "hard_nonclaims":[
         "Sheffield selected for diagnosis after its huge heldout loss; not new confirmatory site test",
         "Predictor feature extrapolation and regression collinearity are statistical failure modes, not biodiversity ecology mechanisms",
         "No heldout-site/plot selection changed the original negative global site-equal result",
         "No causal light competition, maximum-height selection or trait phylogenetic memory established",
         "Original GIFT height source maxima have nonzero cross-reference CV and may have height-record biases",
         "2010/2005 original source biomass editions are not numerically interchangeable",
         "Original global BIODEPTH, sPlotOpen BIEN and NEON gates remain HOLD"]
    }
def fixture():
    p=[{"richness":4,"grass":1,"forbs":1,"legumes":0,"year":i%3+1,
         "cwm":0.3*i,"mpd":.11*i} for i in range(15)]
    x,mu,sd=baseline(p,True,True)
    assert x.shape==(15,10) and np.isfinite(x).all()
    return {"status":"SITE_FAILURE_DIAGNOSTIC_FIXTURE_PASS","checks":2}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for x in ("species","codes","design","community","provenance","prior","out"):
        p.add_argument("--"+x)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture()))
    else:
        if not all(getattr(args,x) for x in ("species","codes","design","community","provenance","prior","out")):
            p.error("all seven source/report paths required")
        result=core(args)
        out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("BIODEPTH_HEIGHT_FD_SOURCE_OOD_DIAGNOSTIC",json.dumps(result,sort_keys=True))
