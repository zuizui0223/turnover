#!/usr/bin/env python3
"""BioCON E141 source-only matched mono/mixture biomass PRESENCE (not values).

Never parse biomass numeric values. Only inspect whether the original official
aboveground source column has a missing token. No effect estimates are fitted.
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
MD5="8185b8effca37c8740ad065c53eb75d2"
OUT=Path("results/biocon_e141_original_mono_mixture_annual_biomass_presence_20261124_v0_1.json")
BASE_FIELDS=("year","Season","Ring","Plot","CO2 Treatment","Nitrogen Treatment",
             "CountOfSpecies","Experiment","Water trt","Temp trt",
             "AbovegroundTotal Biomass (g/m^2)")
BAD={"","NA","NaN","nan","-9999","-9999.0"}

def get():
    req=urllib.request.Request(URL,headers={"User-Agent":"turnover-biocon-e141-biomas-presence/0.1"})
    with urllib.request.urlopen(req,timeout=40) as res:
        data=res.read(4000001)
    if len(data)>4000000:raise ValueError("Official author source cap exceeded")
    if hashlib.md5(data).hexdigest()!=MD5:raise ValueError("Original MD5 changed")
    return data

def present(value):
    # Never float or interpret signs, levels, effect or taxon yield.
    return (value or "").strip() not in BAD

def inspect(data):
    f=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    header=list(f.fieldnames or [])
    if len(header)!=70 or not set(BASE_FIELDS).issubset(header):
        raise ValueError("Original E141 source schema changed")
    plant_cols=[x for x in header if x.endswith(" planted")]
    if len(plant_cols)!=16:raise ValueError("Original source species flags changed")
    mono=collections.defaultdict(set)
    rows=[]
    seasons=collections.Counter()
    management=collections.Counter()
    source_mono_rows=collections.Counter()
    observed_original_response=collections.Counter()
    for row in f:
        def src(k):return (row.get(k) or "").strip()
        yr,season,ring,plot=src("year"),src("Season"),src("Ring"),src("Plot")
        c,n=src("CO2 Treatment"),src("Nitrogen Treatment")
        richness=src("CountOfSpecies")
        exp=src("Experiment")
        w,t=src("Water trt"),src("Temp trt")
        if not all((yr,season,ring,plot,c,n,richness,exp)):
            raise ValueError("Incomplete source calendar/season/treatment key")
        planted=[1 if src(z)=="1" else (0 if src(z)=="" else None) for z in plant_cols]
        if None in planted or sum(planted)!=int(richness):
            raise ValueError("Original sown species flags differ from registered source")
        # Read *presence* of whole-community biomass only; never its value.
        usable=present(row.get("AbovegroundTotal Biomass (g/m^2)"))
        seasons[season]+=1
        management[(w or "<missing>",t or "<missing>")]+=1
        if exp=="M" and richness=="1":
            index=planted.index(1)
            source_mono_rows[("present" if usable else "missing")]+=1
            if usable:
                mono[(yr,season,c,n,index)].add((ring,plot))
        if exp=="M" and richness in ("4","9","16"):
            rows.append({"year":yr,"season":season,"c":c,"n":n,
                         "richness":richness,"planted":tuple(planted),
                         "present":usable,"water":w,"temp":t})
            observed_original_response[("present" if usable else "missing")]+=1
    years=sorted({x["year"] for x in rows})
    seasons_unique=sorted(seasons)
    cats=("Camb","Cenrich")
    ncats=("Namb","Nenrich")
    mono_counts=collections.Counter()
    for year in years:
        for seas in seasons_unique:
            for c in cats:
                for n in ncats:
                    for i in range(16):
                        mono_counts[str(len(mono.get((year,seas,c,n,i),set())))]+=1
    mix_result=collections.Counter()
    mix_by_rich=collections.Counter()
    mix_by_year=collections.Counter()
    management_unknown=0
    for x in rows:
        nrep=[len(mono.get((x["year"],x["season"],x["c"],x["n"],i),set()))
              for i,v in enumerate(x["planted"]) if v]
        mono_available=all(v>=2 for v in nrep)
        valid_management=(x["water"] in ("0","0.0") and x["temp"] in ("0","0.0"))
        if x["water"] not in ("0","0.0","1","1.0") or x["temp"] not in ("0","0.0","1","1.0"):
            management_unknown+=1
        good=x["present"] and mono_available
        strict=good and valid_management
        mix_result["raw_source_rows"]+=1
        mix_result["own_biomass_present"]+=int(x["present"])
        mix_result["all_sown_mono_2rep_same_year_season_context"]+=int(mono_available)
        mix_result["own_biomass_and_all_mono"]+=int(good)
        mix_result["own_biomass_mono_and_no_water_temp_subexperiment"]+=int(strict)
        mix_by_rich[(x["richness"],"total")]+=1
        mix_by_rich[(x["richness"],"same_harvest_source_presence")]+=int(good)
        mix_by_rich[(x["richness"],"management_restricted_presence")]+=int(strict)
        mix_by_year[(x["year"],"total")]+=1
        mix_by_year[(x["year"],"management_restricted_presence")]+=int(strict)
    return {
      "original_source":"Figshare 26841637.v3 file 54836267",
      "original_byte_md5_confirmed":MD5,
      "source_season_label_row_counts":dict(sorted(seasons.items())),
      "source_management_indicator_pair_counts":[
        {"water_flag":w,"temperature_flag":t,"original_rows":k}
        for (w,t),k in sorted(management.items())
      ],
      "original_mono_aboveground_total_presence_counts":dict(source_mono_rows),
      "mono_year_season_treatment_species_cell_physical_plot_valid_replication_histogram":dict(sorted(mono_counts.items())),
      "source_main_mixture_source_response_presence_counts":dict(mix_result),
      "original_main_mixture_response_presences_by_sown_richness":[
        {"sown_richness":n,"total_harvest_records":mix_by_rich[(n,"total")],
         "same_harvest_with_mono_source_present":mix_by_rich[(n,"same_harvest_source_presence")],
         "also_without_other_climate_intervention_flags":mix_by_rich[(n,"management_restricted_presence")]}
        for n in ("4","9","16")],
      "original_management_flag_ambiguous_source_records":management_unknown,
      "restricted_mixture_source_response_count_by_year":[
        {"year":y,"original_mixture_harvest_records":mix_by_year[(y,"total")],
         "management_restricted_complete_source_presence":mix_by_year[(y,"management_restricted_presence")]}
        for y in years],
      "original_biomass_numeric_values_parsed":False,
      "original_species_yield_numeric_values_parsed":False,
      "original_NDE_CE_SE_numeric_values_parsed":False,
      "statistical_ecological_effects_fitted":0,
      "source_caveat":"Existence of nonmissing original source strings is not a numeric biomass validity check or positive FD effect.",
    }

def synthetic():
    assert present("0")
    assert present("1.2")
    assert not present("")
    assert not present("NA")
    print("SYNTHETIC_BIOMASS_PRESENCE_ONLY_GATE_PASS")

def main():
    out={"as_of_jst":"2026-11-24","source_status":"SOURCE_ACCESS_OR_YEAR_SEASON_JOIN_HOLD",
         "original_biomass_values_opened":False,"model_fits":0}
    try:
        source=get()
        out["source_only_qualifier"]=inspect(source)
        out["source_status"]="ORIGINAL_BIOMASS_PRESENCE_GRAIN_AUDITED_FD_EFFECT_HOLD"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,
            UnicodeError,csv.Error,TypeError,KeyError) as exc:
        out["failure_class"]=type(exc).__name__
        if isinstance(exc,ValueError):
            out["source_stop_reason"]=str(exc)[:170]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    opts=p.parse_args()
    if opts.selftest:synthetic()
    elif opts.source:main()
    else:p.error("Choose --selftest or --source")
