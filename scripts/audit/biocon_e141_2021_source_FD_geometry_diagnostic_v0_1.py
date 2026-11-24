#!/usr/bin/env python3
"""Post-result, response-blind design-identifiability audit of BioCON E141 2021.

Uses the *same pinned* source header/trait/candidate cohort as PR #77 to
quantify CWM+FD collinearity and held-out extrapolation leverage.
NO biomass, signed NDE, species-yield numeric responses or model outcomes used.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"scripts/source/audit_biocon_e141_2021_secondary_SLA_geometry_v0_1.py"
OUT=ROOT/"results/biocon_e141_2021_secondary_SLA_predictor_identifiability_v0_1.json"

def load_frozen_source():
    spec=importlib.util.spec_from_file_location("original_e141_2021_geometry_source",str(SOURCE))
    if not spec or not spec.loader: raise ValueError("Original source frozen geometry module absent")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def reconstruct_source_X(module):
    traits=module.source_traits()
    b=module.get(module.ORIGINAL_CSV)
    if hashlib.md5(b).hexdigest()!=module.SOURCE_MD5:
        raise ValueError("Original dataset MD5 mismatch")
    source=csv.DictReader(io.StringIO(b.decode("utf-8-sig"),newline=""))
    h=list(source.fieldnames or [])
    if len(h)!=70:raise ValueError("Frozen 70 source header count no longer valid")
    flags=[z for z in h if z.endswith(" planted")]
    sp0=h.index("Monogroup")+1
    sp1=h.index("AbovegroundTotal Biomass (g/m^2)")
    species=[z.removesuffix(" (g/m^2)") for z in h[sp0:sp1]]
    if len(species)!=16 or len(flags)!=16:
        raise ValueError("Original 16 source plant taxon count not qualified")
    predicted=[s.split()[0][:3].casefold()+"."+s.split()[1][:3].casefold() for s in species]
    if predicted!=[z.removesuffix(" planted").casefold() for z in flags]:
        raise ValueError("Sown species source code mapping not one to one")
    monos=collections.defaultdict(set)
    mixes=[]
    for row in source:
        def v(k): return (row.get(k) or "").strip()
        if v("year")!="2021": continue
        planted=[1 if v(f)=="1" else (0 if v(f)=="" else None) for f in flags]
        if None in planted or sum(planted)!=int(v("CountOfSpecies")):
            raise ValueError("Planted flags do not match source original richness")
        ctx=(v("Season"),v("CO2 Treatment"),v("Nitrogen Treatment"))
        physical=(v("Ring"),v("Plot"))
        has_b=v("AbovegroundTotal Biomass (g/m^2)") not in module.MISSING
        if v("Experiment")=="M" and sum(planted)==1 and has_b:
            monos[ctx+(planted.index(1),)].add(physical)
        if v("Experiment")!="M" or sum(planted) not in (4,9) or not has_b:
            continue
        if v("Water trt")!="0" or v("Temp trt")!="0":
            continue
        mixes.append((physical,ctx,tuple(planted)))
    accepted=[]
    for physical,(season,c,n),planted in mixes:
        if not all(len(monos[(season,c,n,i)])==2 for i,x in enumerate(planted) if x):
            continue
        vals=[traits[(c,n)][sp] for sp,x in zip(species,planted) if x and sp in traits[(c,n)]]
        if len(vals)<2 or len(vals)/sum(planted)<0.80:
            continue
        accepted.append({
            "composition":planted,
            "richness":sum(planted),
            "ring":physical[0],
            "N":n,
            "CO2":c,
            "CWM":sum(vals)/len(vals),
            "FD":sum(abs(x-y) for x in vals for y in vals)/(len(vals)**2),
        })
    nrich=collections.Counter(x["richness"] for x in accepted)
    ringids=sorted({x["ring"] for x in accepted})
    if (len(accepted)!=46 or nrich!={4:36,9:10} or len({x["composition"] for x in accepted})!=46 or len(ringids)!=6):
        raise ValueError("Prior 46 plot composition cohort changed; no retrospective resampling")
    x=np.asarray([
        [1.,float(z["richness"]==9),float(z["N"]=="Nenrich")]
        +[float(z["ring"]==r) for r in ringids if r!=ringids[0]]
        +[z["CWM"],z["FD"]]
        for z in accepted
    ],dtype=float)
    if x.shape!=(46,10):raise ValueError("Frozen M1 matrix geometry changed")
    return x,accepted,ringids

def deciles(vals):
    return [float(v) for v in np.quantile(np.asarray(vals,dtype=float),[0.10,0.50,0.90])]

def diagnose(x,rows,rings):
    counts=collections.Counter(r["ring"] for r in rows)
    weight=np.asarray([1./counts[r["ring"]] for r in rows],dtype=float)
    m0=x[:,:-1]
    fd=x[:,-1]
    tr=np.sqrt(weight)
    coef=np.linalg.lstsq(m0*tr[:,None],fd*tr,rcond=None)[0]
    residual=fd-m0@coef
    sd0=float(np.average((fd-np.average(fd,weights=weight))**2,weights=weight))
    unexpl=float(np.average(residual**2,weights=weight))
    if sd0<=0:raise ValueError("Source FD has zero variation")
    partial_r2=1.-unexpl/sd0
    vif=1./(1.-partial_r2) if partial_r2<1. else math.inf
    fold_stats=[]
    for i in range(len(rows)):
        train=[j for j in range(len(rows)) if j!=i]
        m0_tr=x[train,:-1].copy()
        m1_tr=x[train,:].copy()
        m0_test=x[i:i+1,:-1].copy()
        m1_test=x[i:i+1,:].copy()
        for k in (8,9):
            mu=float(np.mean(m1_tr[:,k]))
            std=float(np.std(m1_tr[:,k]))
            if std<=1e-12:raise ValueError("Frozen source fold lacks trait predictor variance")
            m1_tr[:,k]=(m1_tr[:,k]-mu)/std
            m1_test[:,k]=(m1_test[:,k]-mu)/std
            if k==8:
                m0_tr[:,8]=(m0_tr[:,8]-mu)/std
                m0_test[:,8]=(m0_test[:,8]-mu)/std
        w_counts=collections.Counter(rows[j]["ring"] for j in train)
        w=np.sqrt(np.asarray([1./w_counts[rows[j]["ring"]] for j in train]))
        if np.linalg.matrix_rank(m0_tr)!=9 or np.linalg.matrix_rank(m1_tr)!=10:
            raise ValueError("Original frozen regression design lacks full rank")
        d0=m0_tr*w[:,None]
        d1=m1_tr*w[:,None]
        # Predictive leverage of the left-out data point under ring-equal WLS.
        lev0=float(m0_test@np.linalg.pinv(d0.T@d0)@m0_test.T)
        lev1=float(m1_test@np.linalg.pinv(d1.T@d1)@m1_test.T)
        if lev0<=0 or lev1<lev0-1e-6:
            raise ValueError("FD addition unexpectedly decreases pure-model leverage")
        fold_stats.append({"condition_m0":float(np.linalg.cond(d0)),
                           "condition_m1":float(np.linalg.cond(d1)),
                           "incremental_leverage_ratio":lev1/lev0,
                           "incremental_leverage_abs":lev1-lev0,
                           "richness":rows[i]["richness"]})
    result={
     "original_field_experiments":1,
     "physical_CO2_ring_units":6,
     "original_holdout_compositions":len(rows),
     "richness_plot_count":dict(sorted(collections.Counter(r["richness"] for r in rows).items())),
     "ring_plot_counts_unlabeled":sorted(counts.values()),
     "FD_weighted_explained_R2_by_M0_predictors":partial_r2,
     "FD_weighted_variance_inflation_factor_given_M0":vif,
     "FD_weighted_residual_variance_fraction_given_M0":unexpl/sd0,
     "FD_raw_global_std":float(np.std(fd)),
     "FD_within_richness_candidate_aggregate_quantiles":[
       {"richness":k,"n":sum(r["richness"]==k for r in rows),
         "FD_10_50_90_quantile":deciles([z["FD"] for z in rows if z["richness"]==k]),
         "CWM_10_50_90_quantile":deciles([z["CWM"] for z in rows if z["richness"]==k])}
         for k in (4,9)],
     "train_weighted_condition_M0_median_max":[
         float(np.median([f["condition_m0"] for f in fold_stats])),
         float(max(f["condition_m0"] for f in fold_stats]))],
     "train_weighted_condition_M1_median_max":[
         float(np.median([f["condition_m1"] for f in fold_stats])),
         float(max(f["condition_m1"] for f in fold_stats]))],
     "new_FD_predictor_heldout_leverage_ratio_median_max":[
         float(np.median([f["incremental_leverage_ratio"] for f in fold_stats])),
         float(max(f["incremental_leverage_ratio"] for f in fold_stats]))],
     "source_folds_M1_extra_predictor_increases_leverage_above_2x":
         sum(f["incremental_leverage_ratio"]>2.0 for f in fold_stats),
     "source_folds_M1_extra_predictor_increases_leverage_above_1_5x":
         sum(f["incremental_leverage_ratio"]>1.5 for f in fold_stats),
     "model_dimension_M0":9,"model_dimension_M1":10,
     "original_biomass_or_signed_NDE_numeric_source_values_read":False,
     "source_trait_numeric_values_used_for_predictor_geometry_only":True,
     "no_FD_predictive_effects_refitted":True,
     "source_E141_direct_EDI_trait_year_http403_hold_preserved":True,
     "post_result_diagnostic_not_a_prospective_source_gate":True,
     "interpretation":"Predictor identifiability, not a test of a new ecological FD effect; original six-ring/single-field limitations remain."
    }
    return result

def synthetic():
    X=np.array([[1.,0.,1.],[1.,1.,0.],[1.,1.,1.]])
    assert np.linalg.matrix_rank(X)==3
    assert deciles([0.,1.,2.])[1]==1.0
    print("SYNTHETIC_FD_GEOMETRY_DIAGNOSTIC_PASS")

def main():
    out={"as_of_jst":"2026-11-24",
         "status":"SOURCE_OR_PREDICTOR_GEOMETRY_HOLD",
         "original_fitted_biomass_NDE_predictions_unchanged":True}
    try:
        mod=load_frozen_source()
        X,rows,rings=reconstruct_source_X(mod)
        out["predictor_geometry"]=diagnose(X,rows,rings)
        out["status"]="RETROSPECTIVE_SOURCE_ONLY_FD_PREDICTOR_IDENTIFIABILITY_AUDITED"
    except (ValueError,TypeError,KeyError,ImportError,IndexError,
            np.linalg.LinAlgError,ArithmeticError) as exc:
        out["failure_class"]=type(exc).__name__
        if isinstance(exc,ValueError):out["source_failure"]=str(exc)[:160]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    a=p.parse_args()
    if a.selftest:synthetic()
    elif a.source:main()
    else:p.error("Choose --selftest or --source")
