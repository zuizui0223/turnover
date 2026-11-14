#!/usr/bin/env python3
"""Locked 2003–2007 train to 2008–2012 holdout Jena FD->biomass model.

Same-site temporal transport only. No trait selection or phylogenetic inference.
Source hashes and plot/year/season QA must pass BEFORE opening outcome.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from audit_jena_923591_longitudinal_source_v0_1 import load_zip,PLOT_HASH,FROZEN_TRAITS,nonempty_number
from audit_jena_923591_longitudinal_join_v0_1 import inspect as inspect_source,SEASON

SEED=20261114
BOOT=2000
TRAIN_YEARS=set(range(2003,2008))
TEST_YEARS=set(range(2008,2013))
TRAITS=FROZEN_TRAITS

def table_rows(predictors_zip,biomass_zip,plotinfo,qa_path):
    q=json.loads(Path(qa_path).read_text())
    if q.get("status")!="TIER0_JENA_LONGITUDINAL_JOIN_SOURCE_PASS":
        raise ValueError("Tier0 source join must PASS prior to opening outcome")
    # Recalculate gate on exact same bytes and check frozen source population
    chk=inspect_source(predictors_zip,biomass_zip,plotinfo)
    if chk["status"]!="TIER0_JENA_LONGITUDINAL_JOIN_SOURCE_PASS" or chk["n_overlap_keys_after_documented_all_zero_campaign_filter"]!=1541 or chk["n_distinct_joined_plots"]!=78:
        raise ValueError("Jena source cohort changed or failed gate")
    if q["n_overlap_keys_after_documented_all_zero_campaign_filter"]!=chk["n_overlap_keys_after_documented_all_zero_campaign_filter"]:
        raise ValueError("tier0 source gate population mismatch")
    pcols,p_rows,_=load_zip(predictors_zip,"predictors_raw.zip")
    bcols,b_rows,_=load_zip(biomass_zip,"biomass02_12.zip")
    raw=Path(plotinfo).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PLOT_HASH:raise ValueError("Plot info source changed")
    meta={r["plotcode"].strip():r for r in csv.DictReader(raw.decode("utf-8-sig").splitlines(),delimiter="\t")}
    if len(meta)!=82:raise ValueError("Invalid plot info count")
    req=["FD_"+t for t in TRAITS]+["FI_"+t for t in TRAITS]
    if any(x not in pcols for x in req):raise ValueError("Frozen trait FD/FI column absent")
    pred={}
    for r in p_rows:
        try:year=int(r["year"])
        except (ValueError,TypeError):continue
        if year not in TRAIN_YEARS|TEST_YEARS:continue
        plot=r["plot"].strip()
        if plot not in meta:continue
        season=r["season"].strip()
        if season not in ("spring","summer"):raise ValueError("Unexpected Jena predictor season")
        key=(plot,year,season)
        if key in pred:raise ValueError("Source contains duplicate predictor plot year season")
        vals={}
        for t in req:
            text=str(r.get(t) or "").strip()
            try:v=float(text)
            except ValueError:v=float("nan")
            vals[t]=v if np.isfinite(v) and v!=-9999 else None
        pred[key]=vals
    mass=defaultdict(list)
    seen_month=defaultdict(set)
    for r in b_rows:
        plot=r["plotcode"].strip()
        try:year=int(r["year"])
        except (ValueError,TypeError):continue
        if year not in TRAIN_YEARS|TEST_YEARS or plot not in meta:continue
        month=r["month"].strip()
        if month not in SEASON:raise ValueError("Unrecognized source month")
        key=(plot,year,SEASON[month])
        seen_month[key].add(month)
        rawvalue=str(r.get("target.biomass") or "").strip()
        try:v=float(rawvalue)
        except ValueError:continue
        if v==-9999 or not np.isfinite(v):continue
        if v<0:raise ValueError("Unexpected negative mass in original source")
        mass[key].append(v)
    if any(len(v)>1 for v in seen_month.values()):
        raise ValueError("More than one source campaign month mapped to same plot-year-season")
    keys=sorted(set(pred)&set(mass))
    if len(keys)!=1541:raise ValueError("Expected unchanged plot-year-season source cohort")
    output=[]
    exclusions=Counter()
    for plot,year,season in keys:
        r=meta[plot]
        vals=pred[(plot,year,season)]
        if any(v is None for v in vals.values()):
            exclusions["missing_fd_or_fi_original"]+=1
            continue
        row={
          "plot":plot,"year":year,"season":season,"block":r["block"].strip(),
          "richness":int(r["NumberSownSpecies"]),
          "fg":int(r["NumberFunctionalGroups"]),
          "y":math.log1p(statistics.median(mass[(plot,year,season)])),
        }
        row.update(vals)
        output.append(row)
    train=[r for r in output if r["year"] in TRAIN_YEARS]
    test=[r for r in output if r["year"] in TEST_YEARS]
    if (len(train)<300 or len(test)<300 or
        len({r["plot"] for r in train})<50 or len({r["plot"] for r in test})<50 or
        len({r["year"] for r in train})!=5 or len({r["year"] for r in test})!=5):
        raise ValueError("Temporal population coverage below predeclared gates")
    blocks=sorted({r["block"] for r in output})
    if len(blocks)!=4:raise ValueError("Unexpected original Jena block taxonomy")
    return train,test,blocks,dict(exclusions)

def x_matrix(data,blocks,selected,means=None,sd=None):
    cols=["intercept","log2_sown_species","sown_functional_groups",
          "summer_indicator","year_since_2003"]+["block_"+b for b in blocks[1:]]+list(selected)
    design=[]
    for r in data:
        d=[1.,math.log2(r["richness"]),float(r["fg"]),float(r["season"]=="summer"),
           float(r["year"]-2003)]+[float(r["block"]==b) for b in blocks[1:]]
        d.extend([r[t] for t in selected])
        design.append(d)
    x=np.array(design,dtype=float)
    if not np.all(np.isfinite(x)):raise ValueError("Nonfinite design")
    baselen=5+len(blocks)-1
    if selected:
        if means is None:
            means=x[:,baselen:].mean(axis=0)
            sd=x[:,baselen:].std(axis=0,ddof=0)
        if len(means)!=len(selected) or not np.all(sd>1e-10):
            raise ValueError("No usable training-only trait scale/variance")
        x[:,baselen:]=(x[:,baselen:]-means)/sd
    else:
        means=np.array([],dtype=float);sd=np.array([],dtype=float)
    if x.shape[1] !=len(cols):raise ValueError("Design column count mismatch")
    return x,cols,means,sd

def fit_predict(train,test,blocks,selected):
    x,names,mean,sd=x_matrix(train,blocks,selected)
    if np.linalg.matrix_rank(x)!=x.shape[1]:
        raise ValueError("Rank deficient locked model "+str(selected))
    outcome=np.array([r["y"] for r in train],dtype=float)
    beta=np.linalg.lstsq(x,outcome,rcond=None)[0]
    xt,names_test,_,_=x_matrix(test,blocks,selected,mean,sd)
    if names!=names_test:raise ValueError("Train/test matrix columns differ")
    pred=xt@beta
    sse=float(np.sum((pred-np.array([r["y"] for r in test]))**2))
    return {
      "prediction":pred,"train_prediction":x@beta,
      "coefficients":{name:float(coeff) for name,coeff in zip(names,beta)},
      "sse":sse,"rmse":float(np.sqrt(sse/len(test))),
      "train_rows":len(train),"test_rows":len(test),
      "n_coefficients":len(names)
    }

def cluster_bootstrap(test,preds):
    rng=np.random.default_rng(SEED)
    ids=sorted({r["plot"] for r in test})
    y=np.array([r["y"] for r in test])
    err0=(y-preds["M0"])**2
    err1=(y-preds["M1_FD"])**2
    by={s:np.array([i for i,r in enumerate(test) if r["plot"]==s],dtype=int) for s in ids}
    est=[]
    for _ in range(BOOT):
        sample=rng.choice(ids,size=len(ids),replace=True)
        idx=np.concatenate([by[i] for i in sample])
        denom=float(err0[idx].sum())
        if denom<=0:continue
        est.append(1-float(err1[idx].sum())/denom)
    if len(est)<1900:raise ValueError("Insufficient non-degenerate cluster resamples")
    return {
       "seed":SEED,"number_plot_bootstrap_samples":BOOT,
       "valid_replicates":len(est),"sample_unit":"original plot ID, all holdout dates of a plot resampled together",
       "gain_FD_percentile_CI95":[float(np.quantile(est,.025)),float(np.quantile(est,.975))]
    }

def main(a):
    train,test,blocks,exclusions=table_rows(a.predictors,a.biomass,a.plotinfo,a.tier0)
    traits={"M0":[],"M1_FD":["FD_"+s for s in TRAITS],
            "M2_FI":["FI_"+s for s in TRAITS],
            "M3_FD_FI":["FD_"+s for s in TRAITS]+["FI_"+s for s in TRAITS]}
    full={}
    preds={}
    for name,tt in traits.items():
        fit=fit_predict(train,test,blocks,tt)
        preds[name]=fit.pop("prediction")
        fit.pop("train_prediction")
        full[name]=fit
    sse0=full["M0"]["sse"]
    if sse0<=0:raise ValueError("No baseline test residual")
    gains={key:float(1-v["sse"]/sse0) for key,v in full.items() if key!="M0"}
    bootstrap=cluster_bootstrap(test,preds)
    positive=(gains["M1_FD"]>0 and bootstrap["gain_FD_percentile_CI95"][0]>0)
    seasonal={}
    for ss in ("spring","summer"):
        ix=[i for i,r in enumerate(test) if r["season"]==ss]
        if len(ix)<100:raise ValueError("Too few heldout rows in "+ss)
        y=np.array([test[i]["y"] for i in ix])
        denom=np.sum((y-preds["M0"][ix])**2)
        seasonal[ss]={
          "n_test_plot_year_seasons":len(ix),
          "M1_FD_vs_M0_test_SSE_gain":float(1-np.sum((y-preds["M1_FD"][ix])**2)/denom)
        }
    out={
       "version":"v0.1",
       "status":"JENA_LONGITUDINAL_RETROSPECTIVE_FD_TRANSPORT_ESTIMATED",
       "research_scope":"retrospective one-experiment temporal transfer, not novel independent site validation",
       "source":"PANGAEA 923591; original authors' imputed cover-based Rao FD, processed harvested biomass",
       "sowing_information":"Original Jena plot information, treatment assignment not inferred from biomass",
       "train_years":sorted(TRAIN_YEARS),"test_years":sorted(TEST_YEARS),
       "train_observations":len(train),"test_observations":len(test),
       "train_independent_plot_ids":len({r["plot"] for r in train}),
       "test_independent_plot_ids":len({r["plot"] for r in test}),
       "complete_case_exclusions":exclusions,
       "n_original_blocks":len(blocks),
       "models":full,"holdout_gains_relative_to_planned_diversity_baseline":gains,
       "primary_FD_gain":gains["M1_FD"],"plot_bootstrap":bootstrap,
       "primary_positive_predictive_gain_CI_excludes_zero":bool(positive),
       "seasonal_holdout_FD_gains_descriptive":seasonal,
       "target_scale":"log1p(median original author-processed target.biomass per plot×year×season), physical units unverified",
       "hard_nonclaims":[
         "Functional diversity is the original authors' source-derived/imputed Rao FD, not new independent measurements",
         "Same plots appear in train and test; this is time-transfer, not independent site/family transport",
         "Concurrent annual cover-derived FD uses contemporaneous community information and is not ex-ante prediction",
         "No p-values inferred from individual plot×year rows as independent clusters",
         "No evidence about evolutionary phylogenetic-memory rhos or islands",
         "Original 2020 and 2023 literature already debated long-term trait predictability",
       ]
    }
    return out

def selftest():
    d=[]
    for i in range(40):
        d.append({"plot":str(i),"year":2003+i%5,"season":"summer" if i%2 else "spring",
                  "richness":2**((i//3)%5),"fg":1+(i%4),"block":"B"+str(i%4),
                  "FD_h1":.1*i, "FD_sla":.2*i, "FD_leafN":.3*i, "FD_SeedsTCW":.4*i,
                  "FI_h1":.1*i, "FI_sla":.2*i, "FI_leafN":.3*i, "FI_SeedsTCW":.4*i,
                  "y":i/100})
    x,n,mu,sd=x_matrix(d,["B0","B1","B2","B3"],["FD_h1","FD_sla"])
    assert x.shape==(40,10) and np.isclose(x[:,8:].mean(axis=0),0).all()
    return {"status":"MODEL_CONTRACT_FIXTURE_PASS","checks":2}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for opt in ("predictors","biomass","plotinfo","tier0","out"):p.add_argument("--"+opt)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(selftest()))
    else:
        if not all(getattr(args,x) for x in ("predictors","biomass","plotinfo","tier0","out")):
            p.error("all five inputs required")
        res=main(args)
        dst=Path(args.out);dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
        print("JENA_DECADE_FD_BIOMASS_TRANSPORT",json.dumps(res,sort_keys=True))
