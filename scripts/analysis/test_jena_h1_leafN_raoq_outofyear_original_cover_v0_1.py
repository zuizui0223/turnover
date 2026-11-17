#!/usr/bin/env python3
"""Post-result exploratory Jena 2003-09 -> 2010-12 conditional same-year cover
trait H1+leafN RaoQ, beyond richness and CWM, against original annual target
biomass average. Design frozen before new biomass prediction opening:
docs/JENA_HEIGHT_LEAFN_FD_2010_2012_HELDOUT_YEARS_DESIGN_V0_1.md

Original public Figshare files MD5 pinned. No original author biomass-conditioned
predictor rows, no 2022 same-study reply rows, and no prior TreeDivNet reuse.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"source"))
from audit_jena_2020_original_canonical_keys_v0_2 import (
    BIO,COVER,TRAIT,FUNCTION,PRECOMPUTED,csv_rows,canonical,code,float_presence
)

TRAIN_YEARS=set(range(2003,2010))
HOLD_YEARS=(2010,2011,2012)
TWO_TRAITS=("h1","leafN")
MIN_WEIGHT_COVERAGE=.80
MIN_SOURCE_PLOTS=60
MIN_TRAIN_YEARS=6
MIN_SOURCE_SPECIES=20
N_BOOT=10000
SEED=20261117


def raw_trait_map(rows):
    d={}
    for row in rows:
        name=code(row.get("sp"))
        if not name or name in d:
            raise ValueError("SOURCE_HOLD: original trait source duplicate/unnamed species")
        numeric=[]
        for trait in TWO_TRAITS:
            try:
                val=float(str(row.get(trait) or "").strip())
                if not math.isfinite(val) or val<=0:
                    numeric=[]
                    break
                numeric.append(math.log(val))
            except Exception:
                numeric=[]
                break
        if numeric:d[name]=np.asarray(numeric,dtype=float)
    return d


def original_cover(x):
    s=canonical(x)
    if s is None:return 0.
    try:y=float(s)
    except Exception:return 0.
    if not math.isfinite(y) or y==-9999:return 0.
    if y<0:raise ValueError("SOURCE_HOLD: unexpected original negative cover")
    if y==1:return .5
    if y==2:return 3.
    return y


def read_original():
    bh,biomass=csv_rows(BIO)
    ch,cover=csv_rows(COVER)
    th,traits=csv_rows(TRAIT)
    fh,functions=csv_rows(FUNCTION)
    if len(biomass)!=5544 or len(cover)!=2214 or len(traits)!=59 or len(functions)!=851:
        raise ValueError("SOURCE_HOLD: original authored biomass/cover/trait/functions rows changed")
    biomass_plots={canonical(r["plotcode"]) for r in biomass}
    coverspecies={code(c):c for c in ch[3:]}
    if len(coverspecies)!=60:raise ValueError("SOURCE_HOLD: original source cover species identity no longer unique")
    trait_map=raw_trait_map(traits)
    source_traits=collections.defaultdict(list)
    for r in cover:
        plot=canonical(r["Plot"])
        yr=canonical(r["Year"])
        if not plot or yr is None or not yr.isdigit():raise ValueError("SOURCE_HOLD: original cover key invalid")
        year=int(yr)
        if year not in TRAIN_YEARS and year not in HOLD_YEARS:
            continue
        vals={sp:original_cover(r[col]) for sp,col in coverspecies.items()}
        source_traits[(plot,year)].append(vals)
    original_functions={}
    for r in functions:
        plot=canonical(r["plot"]);yr=canonical(r["year"])
        if not plot or yr is None or not yr.isdigit():raise ValueError("SOURCE_HOLD: original functions key invalid")
        year=int(yr)
        if year not in TRAIN_YEARS and year not in HOLD_YEARS:
            continue
        key=(plot,year)
        if key in original_functions:raise ValueError("SOURCE_HOLD: original function source plot×year duplicated")
        original_functions[key]=r
    if len({p for p,y in original_functions})!=78:
        raise ValueError("SOURCE_HOLD: original 78 named main grassland plots not reproduced")
    if not {p for p,y in original_functions}.issubset(biomass_plots):
        raise ValueError("SOURCE_HOLD: original source biomass.plotcode does not match functions.plot")
    return original_functions,source_traits,trait_map,coverspecies


def source_features(functions, cover, trait_map):
    rows=[]
    diagnostic=collections.Counter()
    present_species=set()
    coverage=[]
    original_response_label_counts=collections.Counter()
    keys=sorted(functions)
    for plot,year in keys:
        row=functions[(plot,year)]
        observed=cover.get((plot,year),[])
        if not observed:
            diagnostic["missing_original_cover_plotyear"]+=1
            continue
        all_species=set(observed[0])
        if any(set(z)!=all_species for z in observed):
            raise ValueError("SOURCE_HOLD: source cover species columns drift across original repeated months")
        # One original source plot×year species abundance: average original
        # source-adjusted cover over available months. No biomass used.
        mean={sp:sum(r[sp] for r in observed)/len(observed) for sp in all_species}
        total=sum(x for x in mean.values() if x>0)
        if not math.isfinite(total) or total<=0:
            diagnostic["no_positive_original_cover"]+=1
            continue
        known={sp:v for sp,v in mean.items() if v>0 and sp in trait_map}
        total_known=sum(known.values())
        frac=total_known/total
        coverage.append(frac)
        if frac<MIN_WEIGHT_COVERAGE:
            diagnostic["less_than_80pct_original_cover_trait_weight"]+=1
            continue
        if len(known)<2:
            diagnostic["less_than_two_complete_original_trait_species"]+=1
            continue
        try:rich=float(str(row["sowndiv"]).strip())
        except Exception:
            diagnostic["missing_original_planted_richness"]+=1
            continue
        if not math.isfinite(rich) or rich<=0 or rich!=int(rich):
            diagnostic["invalid_original_sown_richness"]+=1
            continue
        ids=sorted(known)
        observed_cov=np.array([known[s] for s in ids],dtype=float)
        pp=observed_cov/observed_cov.sum()
        vals=np.vstack([trait_map[s] for s in ids])
        if not np.isfinite(vals).all() or len(vals)<2 or abs(sum(pp)-1)>1e-8:
            raise ValueError("SOURCE_HOLD: invalid weighted source-species traits")
        present_species.update(ids)
        response_state=float_presence(row["target_biomass_average"])
        original_response_label_counts[response_state]+=1
        rows.append({
           "plot":plot,"year":year,"planted_richness":int(rich),
           "plotyear_source_trait_weight_coverage":frac,
           "source_trait_species":len(ids),
           "log_trait_values":vals,
           "relative_cover_species_weights":pp,
           "response_raw":row["target_biomass_average"],
           "response_state":response_state,
        })
    counts=collections.Counter(r["year"] for r in rows)
    train={r["plot"] for r in rows if r["year"] in TRAIN_YEARS}
    heldout_years={y:{r["plot"] for r in rows if r["year"]==y} for y in HOLD_YEARS}
    numeric_years={y for y in TRAIN_YEARS if any(r["year"]==y and r["response_state"] in ("SOURCE_POSITIVE","SOURCE_ZERO") for r in rows)}
    structural=(len(train)>=MIN_SOURCE_PLOTS and len(numeric_years)>=MIN_TRAIN_YEARS and
                all(len(s)>=MIN_SOURCE_PLOTS for s in heldout_years.values()) and
                len(present_species)>=MIN_SOURCE_SPECIES)
    pre={
       "status":"ORIGINAL_COVER_PLUS_REFERENCE_TRAIT_GEOMETRY_PASS" if structural else "SOURCE_SUPPORT_HOLD",
       "original_source_plot_years_any_origin_2003to2012":len(functions),
       "original_source_plotyears_with_cover_and_trait_covariates":len(rows),
       "source_original_year_coverage":dict(sorted(counts.items())),
       "n_training_years_with_numeric_outcome_presence_only":len(numeric_years),
       "source_training_unique_original_main_plots":len(train),
       "source_heldout_source_year_plot_counts":{str(k):len(v) for k,v in heldout_years.items()},
       "source_distinct_trait_species":len(present_species),
       "source_original_complete_height_leafN_trait_taxa":len(trait_map),
       "source_original_biomass_response_label_presence_only":dict(original_response_label_counts),
       "original_source_plot_years_with_no_cover_or_missing_trait":dict(diagnostic),
       "source_trait_cover_weight_coverage_min":float(min(coverage)) if coverage else None,
       "source_trait_cover_weight_coverage_median":float(np.median(coverage)) if coverage else None,
       "source_80pct_threshold":MIN_WEIGHT_COVERAGE,
       "source_plot_threshold":MIN_SOURCE_PLOTS,
       "source_year_threshold":MIN_TRAIN_YEARS,
       "source_distinct_species_threshold":MIN_SOURCE_SPECIES,
       "no_trait_biomass_model_fitted":True,
       "no_source_response_value_used_to_select_original_species_or_covariates":True
    }
    return rows,pre


def train_transform(rows):
    original_species_ivs=np.vstack([r["log_trait_values"] for r in rows if r["year"] in TRAIN_YEARS])
    if len(original_species_ivs)==0:raise ValueError("MODEL_SOURCE_HOLD: no training reference trait values")
    mu=original_species_ivs.mean(axis=0)
    sd=original_species_ivs.std(axis=0,ddof=0)
    if not np.isfinite(sd).all() or min(sd)<=1e-10:
        raise ValueError("MODEL_SOURCE_HOLD: trait scale no training variance")
    # Predictor construction does not read or condition on biomass outcomes.
    X=[]
    for r in rows:
        vals=(r["log_trait_values"]-mu)/sd
        p=r["relative_cover_species_weights"]
        means=p@vals
        disp=np.linalg.norm(vals[:,None,:]-vals[None,:,:],axis=2)
        q=float(.5*np.sum((p[:,None]*p[None,:])*disp))
        if not math.isfinite(q) or q<0:
            raise ValueError("MODEL_SOURCE_HOLD: FD source invalid")
        X.append([1.,math.log2(r["planted_richness"]),float(means[0]),float(means[1]),q])
    return np.asarray(X,dtype=float),{"train_log_trait_mean":list(map(float,mu)),
                                     "train_log_trait_SD":list(map(float,sd))}


def source_model_rank_preflight(rows):
    XX,scale=train_transform(rows)
    train=[i for i,r in enumerate(rows) if r["year"] in TRAIN_YEARS]
    Xt=XX[train,:]
    r0=int(np.linalg.matrix_rank(Xt[:,:4]))
    r1=int(np.linalg.matrix_rank(Xt))
    if r0!=4 or r1!=5:
        raise ValueError("MODEL_GEOMETRY_HOLD: original train M0/M1 rank invalid")
    if float(np.std(Xt[:,4]))<1e-10:
        raise ValueError("MODEL_GEOMETRY_HOLD: original training FD near constant")
    return XX,{
      "full_rank_M0":r0,"full_rank_M1":r1,
      "n_original_training_covariate_rows":len(train),
      "original_train_FD_Q_min":float(Xt[:,4].min()),
      "original_train_FD_Q_max":float(Xt[:,4].max()),
      "n_distinct_original_training_plots":len({rows[i]["plot"] for i in train}),
      "all_scaling_based_only_on_preheldout_years":True,
      "no_response_values_opened_for_rank_gate":True,
    }


def valid_y(row):
    if row["response_state"] not in ("SOURCE_POSITIVE","SOURCE_ZERO"):
        return None
    try:v=float(str(row["response_raw"]).strip())
    except Exception:return None
    if not math.isfinite(v) or v<0:return None
    return float(np.log1p(v))


def run(args):
    funcs,cover,traits,sp=read_original()
    rows,source=source_features(funcs,cover,traits)
    if source["status"]!="ORIGINAL_COVER_PLUS_REFERENCE_TRAIT_GEOMETRY_PASS":
        return {"version":"v0.1","status":"SOURCE_SUPPORT_HOLD","source_only_support":source,
           "new_biomass_effect_estimated":False}
    XX,rank=source_model_rank_preflight(rows)
    print("PRE_OUTCOME_JENA_2003_2009_TRAIN_2010_2012_TEST_SOURCE_PASS",
          json.dumps({"source_only_support":source,"model_source_rank":rank},sort_keys=True),flush=True)
    train=[i for i,r in enumerate(rows) if r["year"] in TRAIN_YEARS and valid_y(r) is not None]
    future=[i for i,r in enumerate(rows) if r["year"] in HOLD_YEARS and valid_y(r) is not None]
    if len(train)<350 or len(future)<170:
        return {"version":"v0.1","status":"RESPONSE_SOURCE_NUMERIC_SUPPORT_HOLD",
                 "source_only_support":source,"n_train_numeric":len(train),
                 "n_heldout_numeric":len(future),"new_biomass_effect_estimated":False}
    # Response opens ONLY after all above exact source and train-only feature
    # rank/source support tests pass. Fixed OLS full train only; no test refit.
    y0=np.asarray([valid_y(rows[i]) for i in train],float)
    yT=np.asarray([valid_y(rows[i]) for i in future],float)
    count=collections.Counter(rows[i]["plot"] for i in train)
    wt=np.array([1/count[rows[i]["plot"]] for i in train],float)
    W=np.sqrt(wt)
    beta0=np.linalg.lstsq(XX[train,:4]*W[:,None],y0*W,rcond=None)[0]
    beta1=np.linalg.lstsq(XX[train,:5]*W[:,None],y0*W,rcond=None)[0]
    pred0=XX[future,:4]@beta0
    pred1=XX[future,:5]@beta1
    e0=(yT-pred0)**2
    e1=(yT-pred1)**2
    if np.any(~np.isfinite(e0+e1)) or np.sum(e0)<=1e-12:
        raise ValueError("MODEL_HOLD: future plot score invalid")
    score=float(1-e1.sum()/e0.sum())
    annual=[]
    for year in HOLD_YEARS:
        idx=np.array([k for k,i in enumerate(future) if rows[i]["year"]==year],dtype=int)
        if not len(idx) or e0[idx].sum()<=1e-12:raise ValueError("MODEL_HOLD: year scored missing")
        gain=float(1-e1[idx].sum()/e0[idx].sum())
        annual.append({"source_heldout_calendar_year":year,"n_original_plotyear_predictions":len(idx),
                       "M0_sse":float(e0[idx].sum()),"M1_sse":float(e1[idx].sum()),
                       "FD_RaoQ_added_predicted_SSE_gain":gain})
    # Original PLOT bootstrap; entire future-year histories move together.
    # Conditional on 3 test years and fixed fitted coefficients: NOT uncertainty
    # for unseen new studies or a population distribution of calendar years.
    futures=sorted({rows[i]["plot"] for i in future})
    perplot={p:(sum(e0[j] for j,i in enumerate(future) if rows[i]["plot"]==p),
                 sum(e1[j] for j,i in enumerate(future) if rows[i]["plot"]==p))
             for p in futures}
    pairs=np.asarray([perplot[p] for p in futures],float)
    rng=np.random.default_rng(SEED)
    ids=rng.integers(0,len(futures),size=(N_BOOT,len(futures)))
    s0=pairs[ids,0].sum(axis=1);s1=pairs[ids,1].sum(axis=1)
    if np.any(s0<=0):raise ValueError("MODEL_HOLD: bootstrap zero baseline SSE")
    gains=1-s1/s0
    CI=np.quantile(gains,[.025,.975])
    return {
       "version":"v0.1",
       "status":"POSTRESULT_EXPLORATORY_JENA_2003_2009_TO_2010_2012_CONDITIONAL_COVER_NOWCAST_ESTIMATED",
       "original_frozen_design":"docs/JENA_HEIGHT_LEAFN_FD_2010_2012_HELDOUT_YEARS_DESIGN_V0_1.md",
       "no_same_year_biomass_used_for_predictor_or_case_eligibility":True,
       "original_cover_is_contemporaneously_measured_so_this_is_not_preseason_forecasting":True,
       "source_MD5_original_Figshare_2020":True,
       "source_only_pre_effect_support":source,
       "original_model_source_rank":rank,
       "original_training_years":sorted(TRAIN_YEARS),
       "original_heldout_future_years":list(HOLD_YEARS),
       "n_original_training_plotyears_with_numeric_target":len(train),
       "n_original_future_plotyears_with_numeric_target":len(future),
       "original_source_training_unique_plots":len({rows[i]["plot"] for i in train}),
       "original_source_heldout_unique_plots":len(futures),
       "original_target":"functions raw values.csv target_biomass_average, original authors plot-year average dry matter [g m−2]",
       "original_reference_species_trait_axis":"h1 (plant height), leafN (leaf nitrogen), positive original species references only; no TRY additional source",
       "source_predictor":"within-same-year average corrected species cover -> relative cover weights -> log h1 and log leafN CWM and 2-axis Rao Q",
       "prediction_models":"M0 intercept+log2(sownrichness)+CWM_h1+CWM_leafN vs M1 M0+one Rao Q FD, training source plot-equal weighted OLS",
       "pooled_three_future_years_M0_SSE":float(e0.sum()),
       "pooled_three_future_years_M1_SSE":float(e1.sum()),
       "pooled_future_year_FD_incremental_SSE_gain":score,
       "pooled_future_year_FD_incremental_SSE_gain_pct":float(score*100),
       "future_year_records":annual,
       "n_future_years_with_positive_increment":sum(x["FD_RaoQ_added_predicted_SSE_gain"]>0 for x in annual),
       "predeclared_directional_future_year_transfer_supported":bool(score>0 and all(x["FD_RaoQ_added_predicted_SSE_gain"]>0 for x in annual)),
       "whole_original_plot_future_year_resampling_ci95":[float(x) for x in CI],
       "whole_original_plot_future_year_resampling_ci95_pct":[float(100*x) for x in CI],
       "original_plot_cluster_bootstrap_draws":N_BOOT,
       "source_bootstrap_seed":SEED,
       "bootstrap_is_plot_conditional_not_separate_year_population_uncertainty":True,
       "no_global_independent_phylogenetic_K_rho_association_tested":True,
       "no_causal_inference_from_current_year_trait_composition":True,
       "no_independent_site_or_study_replication_of_earlier_Jena_source":True,
       "previous_BIEN_GloBI_BIODEPTH_NEON_strict_source_HOLDs_unchanged":True,
       "hard_nonclaims":[
          "Original Jena 2020 authors 32.6% within-year / 12.7% across-year R2 are distinct model explanatory estimands; these new heldout SSE gains are not directly comparable.",
          "The 2022 reply is same original Jena study, not independent replication; earlier turnover Jena guild dataset also overlaps same experiment.",
          "Original species traits include literature/pot/monoculture and are NOT directly measured each current plot, unlike TreeDivNet 2026 field leaf traits.",
          "Current-year cover is observed contemporaneously with biomass; model is a conditional nowcast and cannot forecast community assembly prospectively.",
          "No independent family-specific phylogenetic signal K, BIEN rho, selection, or direct K→FD→biomass causal mediation.",
          "One original grassland field experiment with 78 plot clusters and three future years, hence plot resampling does not establish across-study generalization.",
          "Do not retune traits, years, cover thresholds or source case selection after results are opened."
       ],
    }


def fixture():
    assert original_cover("1")==.5
    assert original_cover("2")==3.
    assert original_cover("-9999")==0
    assert original_cover("NULL")==0
    assert sum(TRAIN_YEARS)==sum(range(2003,2010))
    assert HOLD_YEARS==(2010,2011,2012)
    assert MIN_WEIGHT_COVERAGE==.80
    return {"status":"ORIGINAL_JENA_2D_RAO_TIME_SOURCE_FIXTURE_PASS","checks":7}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.out:p.error("--out needed")
        result=run(a)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("JENA_ORIGINAL_REFERENCE_TRAIT_RAO_FD_NEXT_YEAR_BIOMASS_RESULT",
              json.dumps({k:v for k,v in result.items() if k not in ('hard_nonclaims',)},sort_keys=True),flush=True)
