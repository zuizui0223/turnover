#!/usr/bin/env python3
"""Jena original 2003–2012 plot×year×season key/campaign quality gate.

No FD-versus-biomass correlation, model, effect, or predictive score calculated.
Uses source-native author month mapping and flags all-zero campaigns.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from collections import defaultdict,Counter
from pathlib import Path
from audit_jena_923591_longitudinal_source_v0_1 import (load_zip,PLOT_HASH,FROZEN_TRAITS,nonempty_number)

SEASON={"May":"spring","Jun":"spring","Aug":"summer","Sept":"summer"}
YEARS={str(x) for x in range(2003,2013)}

def inspect(predzip,biomzip,plotinfo):
    pcols,p_rows,_=load_zip(predzip,"predictors_raw.zip")
    bcols,b_rows,_=load_zip(biomzip,"biomass02_12.zip")
    raw=Path(plotinfo).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PLOT_HASH:raise ValueError("Jena plot info SHA mismatch")
    info=list(csv.DictReader(raw.decode("utf-8-sig").splitlines(),delimiter="\t"))
    good_plots={r["plotcode"] for r in info}
    if len(good_plots)!=82:raise ValueError("Original Jena plot information not 82")
    expected_fd=["FD_"+x for x in FROZEN_TRAITS]
    if any(x not in pcols for x in ["plot","year","season"]+expected_fd):raise ValueError("FD source column missing")
    if any(x not in bcols for x in ["plotcode","year","month","subsample","target.biomass"]):raise ValueError("biomass source column missing")
    predictors={}
    for r in p_rows:
        plot=r["plot"].strip();year=str(r["year"]).strip();season=str(r["season"]).strip()
        if year not in YEARS or plot not in good_plots:continue
        if season not in ("spring","summer"):raise ValueError("unrecognized Jena predictor season")
        k=(plot,year,season)
        if k in predictors:raise ValueError("duplicated plot-year-season FD predictor")
        predictors[k]={t:nonempty_number(r.get("FD_"+t)) for t in FROZEN_TRAITS}
    groups=defaultdict(list)
    months=defaultdict(set)
    counter=Counter()
    year_biom=defaultdict(lambda:{"valid_sample_rows":0,"valid_plot_seasons":0,"zero_only_plot_seasons":0})
    for r in b_rows:
        plot=r["plotcode"].strip();year=str(r["year"]).strip();month=r["month"].strip()
        if year not in YEARS or plot not in good_plots:continue
        if month not in SEASON:raise ValueError("unrecognized Jena biomass month "+month)
        season=SEASON[month]
        k=(plot,year,season)
        months[k].add(month)
        value=r.get("target.biomass")
        if not nonempty_number(value):
            counter["invalid_or_missing_target_biomass_subsamples"]+=1
            continue
        f=float(value)
        if f<0:raise ValueError("negative biomass observation other than source missing sentinel")
        groups[k].append(f)
        counter["valid_target_biomass_subsamples"]+=1
        if f==0:counter["zero_target_biomass_subsamples"]+=1
    diag=Counter()
    join=set(groups)&set(predictors)
    for k,vals in groups.items():
        year,season=k[1:]
        label=f"{year}_{season}"
        if vals:
            year_biom[label]["valid_plot_seasons"]+=1
            if all(v==0 for v in vals):year_biom[label]["zero_only_plot_seasons"]+=1
    allzero_year_season=[]
    for label,ct in sorted(year_biom.items()):
        if ct["valid_plot_seasons"]>=30 and ct["zero_only_plot_seasons"]==ct["valid_plot_seasons"]:
            allzero_year_season.append(label)
    positive_join={k for k in join if not (k[1]+"_"+k[2] in allzero_year_season)}
    byseason=Counter()
    distinct_plots=set()
    years=set()
    trait_coverage=Counter()
    for k in positive_join:
        byseason[k[2]]+=1
        distinct_plots.add(k[0]);years.add(k[1])
        for t,valid in predictors[k].items():
            if valid:trait_coverage[t]+=1
    multi_month={k:sorted(ms) for k,ms in months.items() if len(ms)>1}
    floor=all(trait_coverage[t]/len(positive_join)>=.60 for t in FROZEN_TRAITS) if positive_join else False
    pass_structural=(
        len(distinct_plots)>=50 and len(years)>=4 and len(positive_join)>=100 and floor
        and len(multi_month)==0
    )
    out={
      "version":"v0.1",
      "status":"TIER0_JENA_LONGITUDINAL_JOIN_SOURCE_PASS" if pass_structural else "TIER0_JENA_LONGITUDINAL_JOIN_SOURCE_HOLD",
      "source":"PANGAEA 923591 published source native biomass and derived FD predictors; no FD relation estimated",
      "original_plots":len(good_plots),
      "year_range_scoped":[2003,2012],
      "n_predictor_plot_year_seasons":len(predictors),
      "n_biomass_plot_year_seasons_with_valid_subsample":len(groups),
      "n_overlap_plot_year_season_keys_before_all_zero_campaign_filter":len(join),
      "n_overlap_keys_after_documented_all_zero_campaign_filter":len(positive_join),
      "n_distinct_joined_plots":len(distinct_plots),
      "n_distinct_joined_years":len(years),
      "joined_year_labels":sorted(years),
      "seasonal_qualifying_join_cells":dict(byseason),
      "source_month_to_season_mapping":SEASON,
      "n_plot_year_seasons_with_multiple_original_sampling_months":len(multi_month),
      "n_all_zero_year_season_campaigns":len(allzero_year_season),
      "all_zero_campaign_labels":allzero_year_season,
      "valid_subsample_and_zero_row_counts":dict(counter),
      "per_year_season_source_quality":dict(sorted(year_biom.items())),
      "preselected_fd_axes_coverage":{
          t:{"candidate_rows":len(positive_join),"nonmissing":trait_coverage[t],
             "fraction":trait_coverage[t]/len(positive_join) if positive_join else None}
          for t in FROZEN_TRAITS},
      "specimen_sampled_area_and_biomass_units":"NOT AUDITED; cannot yet claim g/m² source normalization",
      "hard_nonclaims":[
        "No FD~biomass effect or group difference fitted",
        "Original 41-trait values were PCA imputed in source author script",
        "Same-year composition-based FD not causal or prospective biomarker",
        "Multiple subsamples are not independent plot replicates",
        "The same one-site Jena experiment used in earlier published trait analysis",
      ]
    }
    return out

def self_test():
    assert SEASON["May"]=="spring" and SEASON["Jun"]=="spring"
    assert SEASON["Aug"]=="summer" and SEASON["Sept"]=="summer"
    assert sorted(YEARS)[0]=="2003"
    return {"status":"SELF_TEST_PASS","checks":3}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--predictors");p.add_argument("--biomass");p.add_argument("--plotinfo");p.add_argument("--out")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(self_test()))
    else:
        if not all((a.predictors,a.biomass,a.plotinfo,a.out)):p.error("all four arguments required")
        out=inspect(a.predictors,a.biomass,a.plotinfo)
        dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
        print("JENA_PLOT_YEAR_JOIN_SOURCE_QA",json.dumps(out,sort_keys=True))
        if not out["status"].endswith("PASS"):raise SystemExit(2)
