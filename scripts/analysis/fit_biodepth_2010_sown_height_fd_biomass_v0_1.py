#!/usr/bin/env python3
"""Exploratory original BIODEPTH 2010 planted max-height FD -> biomass transport.

CRITICAL: requires the bibliographic provenance gate PASS, exact source
fingerprint, 2010 community-only biomass and original 2005 sown treatments.
Height predictors use equal *planted species* weights, never response biomass.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np

from audit_biodepth_gift_height_references_v0_1 import run as provenance,coverage
from audit_biodepth_103_taxa_gift_height_v0_1 import source,geometry
from audit_biodepth_2005_2010_biomass_hierarchy_v0_1 import source as source_other,val,key

DESIGN_SHA="a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a"
MIXED_SHA="9d95e65295bf6014e753f474dffa09036718b6b54ad5e1d4eea41c1dde76f886"
REPS=10000;SEED=20261115

def baseline(plots,include_mean=False,include_disp=False,mu=None,sd=None):
    if include_disp and not include_mean:raise AssertionError("FD dispersion added only after CWM height")
    columns=[]
    for r in plots:
        z=math.log2(r["richness"])
        a=[1.,z,z*z,float(r["grass"]),float(r["forbs"]),float(r["legumes"]),
           float(r["year"]==2),float(r["year"]==3)]
        if include_mean:a.append(r["cwm"])
        if include_disp:a.append(r["mpd"])
        columns.append(a)
    x=np.asarray(columns,dtype=float)
    if not np.isfinite(x).all():raise ValueError("NONFINITE_SOURCE_BASELINE")
    if include_mean:
        if mu is None:
            mu=x[:,8:].mean(axis=0)
            sd=x[:,8:].std(axis=0,ddof=0)
        if np.any(sd<=1e-9):raise ValueError("Training species-height predictor scale degenerate")
        x[:,8:]=(x[:,8:]-mu)/sd
    else:
        mu=np.array([],dtype=float);sd=np.array([],dtype=float)
    return x,mu,sd

def fit_predict(training,test,M):
    k=0 if M==0 else 1 if M==1 else 2
    x,mu,sd=baseline(training,include_mean=k>=1,include_disp=k>=2)
    if x.shape[0]<x.shape[1]+10 or np.linalg.matrix_rank(x)!=x.shape[1]:
        raise ValueError("RANK_DEFICIENT_TRAINING_MODEL_"+str(M))
    y=np.asarray([r["response"] for r in training])
    beta=np.linalg.lstsq(x,y,rcond=None)[0]
    xt,_,_=baseline(test,include_mean=k>=1,include_disp=k>=2,mu=mu,sd=sd)
    return xt@beta

def composition(data2010,codes2010,design_file,community_file,height,qa):
    names,plot_species,geometry_meta=geometry(data2010,codes2010)
    if qa["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":
        raise ValueError("SOURCE_BIBLIOGRAPHIC_PROVENANCE_HOLD")
    if len(height)!=qa["original_species_with_full_references_and_no_explicit_original_BIODEPTH"]:
        raise ValueError("PROVENANCE_HEIGHT_MAPPING_VERSUS_SUMMARY_COUNT_MISMATCH")
    b=Path(design_file).read_bytes()
    if hashlib.sha256(b).hexdigest()!=DESIGN_SHA:raise ValueError("Original 2005 design source SHA mismatch")
    D=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig")),delimiter="\t"))
    plan={r["plot"]:r for r in D}
    if len(plan)!=480:raise ValueError("Original 480 design plot IDs changed")
    data=[]
    eligible_plots=set()
    for (site,plot),sown in sorted(plot_species.items()):
        q=sorted([math.log(height[n]) for n in sown if n in height])
        if len(q)<3 or len(q)/len(sown)<.8:continue
        if len(sown)!=int(plan[plot]["species.richness"]) or site!=plan[plot]["location"]:
            raise ValueError("Sown roster does not reconcile with original study source")
        d=np.asarray(q,dtype=float)
        # n>=3 planted height-observed species, no realized-biomass weighting.
        mpd=float(np.abs(d[:,None]-d[None,:]).sum()/(len(d)*(len(d)-1)))
        if mpd<0 or not np.isfinite(mpd):raise ValueError("Invalid nonnegative height distance")
        r=plan[plot]
        for field in ("grasses","forbs","legumes"):
            if r[field] not in ("Yes","No"):raise ValueError("Original planted guild assignment malformed")
        data.append({"site":site,"plot":plot,"richness":len(sown),
             "height_observed_count":len(q),"height_coverage":len(q)/len(sown),
             "grass":int(r["grasses"]=="Yes"),"forbs":int(r["forbs"]=="Yes"),
             "legumes":int(r["legumes"]=="Yes"),
             "cwm":float(d.mean()),"mpd":mpd})
        eligible_plots.add(plot)
    if len(eligible_plots)!=qa["bibliography_eligible_original_plots"]:
        raise ValueError("Provenance source 80% plot cohort identity changed")
    c=Path(community_file).read_bytes()
    if hashlib.sha256(c).hexdigest()!=MIXED_SHA:raise ValueError("2010 Community source SHA mismatch")
    community=source_other(community_file,"mixed2010")
    means={}
    for r in community:
        if str(r["level"]).strip().casefold()!="community":continue
        k=key(r)
        if k in means:raise ValueError("Duplicate 2010 Community plot-year")
        means[k]=val(r["biomass"])
    if len(means)!=1440:raise ValueError("Original 2010 Community plot-years changed")
    cells=[]
    missing=0
    for p in data:
        for year in (1,2,3):
            raw=means.get((p["plot"],year))
            if raw is None:missing+=1;continue
            cells.append({**p,"year":year,"response":math.log1p(raw)})
    sites=sorted({x["site"] for x in data})
    site_pop=Counter(x["site"] for x in data)
    supported=[s for s in sites if site_pop[s]>=8]
    if len(eligible_plots)<100 or len(supported)<5 or len(cells)<280:
        raise ValueError("FROZEN_BIODEPTH_HEIGHT_EFFECT_SAMPLE_SIZE_GATE_HOLD")
    if set(sites)!=set(supported):
        # source uses only site-qualified plots, not 3-plot site artifacts
        raise ValueError("At least one site has less than 8 original eligible plots")
    if len(sites)<5:
        raise ValueError("Insufficient independent geographic sites for cross-site transport")
    return data,cells,missing,site_pop

def evaluate(cells,sites):
    records=[]
    for held in sites:
        training=[r for r in cells if r["site"]!=held]
        test=[r for r in cells if r["site"]==held]
        y=np.asarray([r["response"] for r in test],dtype=float)
        sses={}
        for m in range(3):
            pred=fit_predict(training,test,m)
            sses[f"M{m}"]=float(np.sum((y-pred)**2))
        if sses["M1"]<=0 or sses["M0"]<=0:
            raise ValueError("Out-of-site predictive error degenerate")
        records.append({"heldout_site":held,
             "n_test_plot_years":len(test),
             "n_test_original_plots":len({r["plot"] for r in test}),
             "M0_sse":sses["M0"],"M1_sse":sses["M1"],"M2_sse":sses["M2"],
             "height_cwm_increment_over_context":1-sses["M1"]/sses["M0"],
             "height_fd_increment_over_cwm":1-sses["M2"]/sses["M1"],
             "height_cwm_fd_increment_over_context":1-sses["M2"]/sses["M0"]})
    returns=np.asarray([r["height_fd_increment_over_cwm"] for r in records])
    rng=np.random.default_rng(SEED)
    bootstrap=returns[rng.integers(0,len(returns),size=(REPS,len(returns)))].mean(axis=1)
    pooled_M1=sum(r["M1_sse"] for r in records)
    pooled_M2=sum(r["M2_sse"] for r in records)
    ci=[float(v) for v in np.quantile(bootstrap,[.025,.975])]
    primary=float(returns.mean())
    verdict=primary>0 and ci[0]>0 and int((returns>0).sum())>=5
    return {
       "primary_equal_site_FD_incremental_holdout_SSE_gain":primary,
       "primary_site_bootstrap_10000_ci95":ci,
       "primary_positive_gain_supported":bool(verdict),
       "sites_positive_incremental_gain":int((returns>0).sum()),
       "pooled_test_SSE_gain_descriptive":1-pooled_M2/pooled_M1,
       "M1_CWM_increase_equal_site_mean":float(np.mean([r["height_cwm_increment_over_context"] for r in records])),
       "M2_FD_CWM_increase_equal_site_mean":float(np.mean([r["height_cwm_fd_increment_over_context"] for r in records])),
       "site_holdout_records":records,
       "source_site_bootstrap_seed":SEED,
       "biological_site_replication":len(sites)}
def run(s_rows,c_rows,design_file,community_file,source_qa_path):
    saved=json.loads(Path(source_qa_path).read_text(encoding="utf-8"))
    if saved["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":
        raise ValueError("Source references gate was not approved")
    result,height=provenance(s_rows,c_rows,return_values=True)
    if result["status"]!="GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":
        raise ValueError("Current original GIFT source attribution HOLD")
    if (saved["GIFT_original_target_species_height_and_reference_fingerprint_sha256"]!=
        result["GIFT_original_target_species_height_and_reference_fingerprint_sha256"] or
        saved["GIFT_bibliography_content_sha256"]!=result["GIFT_bibliography_content_sha256"]):
        raise ValueError("Published GIFT bibliography/source value fingerprint changed; no outcome model")
    plots,cells,missing,sitepop=composition(s_rows,c_rows,design_file,community_file,height,result)
    full=evaluate(cells,sorted(sitepop))
    complete_plots={r["plot"] for r in plots if r["height_coverage"]==1}
    sensitivity={"n_100pct_trait_coverage_plots":len(complete_plots)}
    full_100=[r for r in cells if r["plot"] in complete_plots]
    full_site_counts=Counter(x["site"] for x in plots if x["plot"] in complete_plots)
    if len(complete_plots)>=40 and len(full_site_counts)>=4 and all(v>=8 for v in full_site_counts.values()):
        sensitivity.update({"status":"FULL_TRAIT_COVERAGE_SUBSET_ESTIMATED","prediction":
          evaluate(full_100,sorted(full_site_counts))})
    else:
        sensitivity["status"]="FULL_TRAIT_COVERAGE_SENSITIVITY_UNDERPOWERED_HOLD"
    return {"version":"v0.1","status":"POSTRESULT_BIODEPTH_HEIGHT_FD_OUT_OF_SITE_VALIDATION_ESTIMATED",
      "population":{"original_source_2010_plots":480,
        "provenance_quality_eligible_plots":len(plots),
        "complete_2010_Community_plot_year_rows":len(cells),
        "excluded_missing_original_2010_Community_rows":missing,
        "independent_original_sites":len(sitepop),
        "site_eligible_plots":dict(sitepop)},
      "predictors":"Original sown 103 species roster, GIFT Plant_height_max metres from traceable bibliography; equal planted-species log height CWM and log-height mean pairwise dissimilarity, never 2010 species biomass weights.",
      "response":"2010 Hector original Community aboveground biomass g/m2, log1p; not uniform annual NPP",
      "design":"M0 log2 planned richness + squared + 3 planted guild flags + year; M1 + train-standardized mean log height; M2 + train-standardized mean pairwise absolute log-height difference. Seven-source-site holdout, repeated original plot-year records.",
      "primary":full,"complete_height_species_sensitivity":sensitivity,
      "source_provenance_qa_sha256":hashlib.sha256(Path(source_qa_path).read_bytes()).hexdigest(),
      "source_fingerprint":result["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
      "hard_nonclaims":["The original BIODEPTH 2005–2010 source editions are not interchangeable",
             "The same seven original sites do not represent global grasslands, and Greece lacks qualifying height coverage",
             "GIFT references are not proven literature-independent of TRY/BIEN and source height values are species maxima",
             "This is post-outcome exploratory source response analysis, not a new causal height mechanism",
             "No evolutionary phylogenetic signal rho or family×trait PD–FD model was tested",
             "Original BIODEPTH six-site exact-richness source gate and sPlotOpen global source gate stay HOLD"]}
def fixture():
    demo=[{"richness":4,"grass":1,"forbs":1,"legumes":1,
           "year":i%3+1,"cwm":i*.1,"mpd":i*.02} for i in range(11)]
    x,_,_=baseline(demo,True,True)
    assert x.shape==(11,10) and np.isfinite(x).all()
    return {"status":"BIODEPTH_HEIGHT_FD_MODEL_SOURCE_FIXTURE_PASS","checks":2}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("species","codes","design","community","provenance","out"):p.add_argument("--"+k)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture()))
    else:
        if not all(getattr(a,k) for k in ("species","codes","design","community","provenance","out")):
            p.error("All 6 source inputs required")
        out=run(source(a.species,"species"),source(a.codes,"codes"),a.design,a.community,a.provenance)
        dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print("BIODEPTH_HEIGHT_FD_BIOMASS_CROSS_SITE",json.dumps(
          {k:v for k,v in out.items() if k not in ("complete_height_species_sensitivity",)},sort_keys=True))
