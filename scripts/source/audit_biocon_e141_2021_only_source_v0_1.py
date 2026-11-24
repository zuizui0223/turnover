#!/usr/bin/env python3
"""Post-access-HOLD alternative 2021-only source support, zero ecological values.

The earlier original row-dated EDI538 source gate returned 403. This NEVER
relabels it as passed. Published 1998-2020 trait-date upper bound motivates a
distinct *exploratory* 2021 temporal eligibility candidate only.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import urllib.error
import urllib.request
from pathlib import Path

URL="https://ndownloader.figshare.com/files/54836267"
SOURCE_MD5="8185b8effca37c8740ad065c53eb75d2"
OUT=Path("results/biocon_e141_2021_only_nonnumeric_source_design_gate_20261124_v0_1.json")
BAD={"","NA","NaN","nan","-9999","-9999.0"}
MISSING_DIRECT_SLA={"Bouteloua gracilis","Poa pratensis"}
YEAR="2021"
MIN_DIRECT_COVERAGE=0.80
MIN_OBSERVED_SLA_SPECIES=2
MIN_DISTINCT_PLOTS=40
MIN_DISTINCT_COMPOSITIONS_BY_RICHNESS=8

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"turnover-E141-2021-retrospective-source-support/0.1"})
    with urllib.request.urlopen(req,timeout=35) as res:
        raw=res.read(4000001)
    if len(raw)>4000000:raise ValueError("original source unexpectedly large")
    if hashlib.md5(raw).hexdigest()!=SOURCE_MD5:
        raise ValueError("original author source identity mismatch")
    return raw

def inspect(raw):
    f=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
    h=list(f.fieldnames or [])
    if len(h)!=70:raise ValueError("unexpected original source column count")
    plant_cols=[x for x in h if x.endswith(" planted")]
    a=h.index("Monogroup")+1
    b=h.index("AbovegroundTotal Biomass (g/m^2)")
    full=[x.removesuffix(" (g/m^2)") for x in h[a:b]]
    if len(plant_cols)!=16 or len(full)!=16:
        raise ValueError("source original plant count mismatch")
    predicted=[x.split()[0][:3].casefold()+"."+x.split()[1][:3].casefold() for x in full]
    flag_abbrev=[x.removesuffix(" planted").casefold() for x in plant_cols]
    if predicted!=flag_abbrev or not MISSING_DIRECT_SLA.issubset(set(full)):
        raise ValueError("source original flag-to-full-species name mapping unverified")
    direct_index={i for i,x in enumerate(full) if x not in MISSING_DIRECT_SLA}
    mono=collections.defaultdict(set)
    mixes=[]
    seasons=collections.Counter()
    management=collections.Counter()
    for row in f:
        if (row.get("year") or "").strip()!=YEAR: continue
        def val(k):return (row.get(k) or "").strip()
        exp=val("Experiment")
        season,c,n=val("Season"),val("CO2 Treatment"),val("Nitrogen Treatment")
        ring,plot=val("Ring"),val("Plot")
        richness=int(val("CountOfSpecies"))
        fl=[1 if val(x)=="1" else (0 if val(x)=="" else None) for x in plant_cols]
        if any(z is None for z in fl) or sum(fl)!=richness:
            raise ValueError("original 2021 planting assignments failed")
        key=(ring,plot)
        present=val("AbovegroundTotal Biomass (g/m^2)") not in BAD
        seasons[season]+=1
        management[(val("Water trt"),val("Temp trt"))]+=1
        if exp=="M" and richness==1 and present:
            mono[(season,c,n,fl.index(1))].add(key)
        if exp=="M" and richness in (4,9,16):
            mixes.append((key,season,c,n,richness,tuple(fl),present,
                          val("Water trt"),val("Temp trt")))
    valid=[]
    fullmix=collections.Counter()
    failures=collections.Counter()
    for id,season,c,n,k,fl,b_present,water,temp in mixes:
        source_covered=sum(fl[i] for i in direct_index)
        direct_ok=(source_covered>=MIN_OBSERVED_SLA_SPECIES and
                   source_covered/k>=MIN_DIRECT_COVERAGE)
        monos_ok=all(len(mono.get((season,c,n,i),set()))>=2 for i,z in enumerate(fl) if z)
        unmanaged=water in ("0","0.0") and temp in ("0","0.0")
        if not b_present:failures["mixture_outcome_missing"]+=1
        if not monos_ok:failures["matched_mono_absent"]+=1
        if not direct_ok:failures["candidate_direct_SLA_coverage_failed"]+=1
        if not unmanaged:failures["later_additional_climate_manipulation"]+=1
        if all((b_present,monos_ok,direct_ok,unmanaged)):
            valid.append((id,season,c,n,k,fl))
        fullmix[(k,season)]+=1
    counts=collections.Counter()
    uniq_plots=collections.defaultdict(set)
    uniq_comp=collections.defaultdict(set)
    per_context=collections.Counter()
    per_ring=collections.defaultdict(set)
    for id,season,c,n,k,fl in valid:
        counts[(k,season)]+=1
        uniq_plots[k].add(id)
        uniq_comp[k].add(fl)
        per_context[(k,c,n,season)]+=1
        per_ring[c].add(id[0])
    actual_compositions={str(k):len(s) for k,s in uniq_comp.items()}
    total_unique=len(set().union(*uniq_plots.values())) if uniq_plots else 0
    pass_design=(total_unique>=MIN_DISTINCT_PLOTS and
                 all(len(uniq_comp[k])>=MIN_DISTINCT_COMPOSITIONS_BY_RICHNESS for k in (4,9))
                 and len(per_ring["Camb"])>=2 and len(per_ring["Cenrich"])>=2)
    return {
     "target_only_year":int(YEAR),"source_observed_season_records":dict(sorted(seasons.items())),
     "source_2021_original_management_flags":[{"water":w,"temperature":t,"records":num}
                                           for (w,t),num in sorted(management.items())],
     "all_original_M_2021_mixture_source_harvest_records":len(mixes),
     "source_2021_source_factors_only_exclusion_counts":dict(sorted(failures.items())),
     "qualified_original_source_harvest_records_after_all_gates":len(valid),
     "qualified_original_distinct_physical_mixture_plots":total_unique,
     "qualified_original_distinct_physical_mixtures_by_richness":{
       str(k):len(v) for k,v in sorted(uniq_plots.items())},
     "qualified_original_composition_groups_by_richness":actual_compositions,
     "qualified_source_harvest_records_by_richness_and_season":[
       {"richness":k,"season":ss,"n_records":v} for (k,ss),v in sorted(counts.items())],
     "qualified_source_harvest_records_by_richness_CO2_N_season":[
       {"richness":k,"CO2":c,"N":n,"season":ss,"n_records":v}
       for (k,c,n,ss),v in sorted(per_context.items())],
     "distinct_original_CO2_ring_ids_under_retrospective_source_selection":{
       k:len(v) for k,v in per_ring.items()},
     "pre_frozen_year2021_exploratory_source_minimums":{
       "physical_plots":MIN_DISTINCT_PLOTS,
       "unique_compositions_each_richness4_and9":MIN_DISTINCT_COMPOSITIONS_BY_RICHNESS,
       "rings_each_CO2":2,
       "trait_coverage":MIN_DIRECT_COVERAGE},
     "post_access_HOLD_retrospective_design_support_pass":pass_design,
     "original_EDI_538_direct_trait_dates_recovered":False,
     "no_change_to_primary_temporal_source_hold":True,
     "original_biomass_numeric_values_parsed":False,
     "original_SLA_trait_numeric_values_parsed":False,
     "biological_models_fitted":0
    }

def selftest():
    assert MIN_DIRECT_COVERAGE==0.80 and MIN_DISTINCT_PLOTS==40
    assert len(MISSING_DIRECT_SLA)==2 and YEAR=="2021"
    print("SYNTHETIC_2021_TEMPORAL_SOURCE_ALTERNATIVE_CONTRACT_PASS")

def main():
    out={"as_of_jst":"2026-11-24","status":"SOURCE_OR_COHORT_HOLD",
         "purpose":"post-403 retrospective year2021-only source design eligibility",
         "original_EDI_time_hard_gate":"HTTP403_HOLD_PRESERVED",
         "original_biomass_values_opened":False,"new_fd_effect_fits":0}
    try:
        a=inspect(fetch())
        out["source_only_support"]=a
        out["status"]=("2021_SOURCE_ONLY_RETROSPECTIVE_DESIGN_PASS_DIRECT_TRAIT_YEAR_NOT_VERIFIED"
                       if a["post_access_HOLD_retrospective_design_support_pass"]
                       else "2021_SOURCE_ONLY_RETROSPECTIVE_DESIGN_THRESHOLD_HOLD")
    except (urllib.error.HTTPError,urllib.error.URLError,ValueError,TimeoutError,
            KeyError,TypeError,UnicodeError,csv.Error) as exc:
        out["failure_class"]=type(exc).__name__
        if isinstance(exc,ValueError):out["source_stop_reason"]=str(exc)[:160]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    opts=p.parse_args()
    if opts.selftest:selftest()
    elif opts.source:main()
    else:p.error("choose --selftest or --source")
