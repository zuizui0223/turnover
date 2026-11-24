#!/usr/bin/env python3
"""Outcome-blind BioCON E141 original plot×year×sown-composition source gate.

Read ONLY original assignment/identifier/treatment columns of the official
Figshare v3 MD5-pinned CSV. Explicitly skip biomass, species biomass, cover,
CE/SE and all trait values; emit aggregate-only counts, not plot keys.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import urllib.request
import urllib.error
from pathlib import Path

ARTICLE=26841637
VERSION=3
FILE_ID=54836267
FILE_NAME="BioCON_biomass_cover_data_Sep2022.csv"
MD5="8185b8effca37c8740ad065c53eb75d2"
URL=f"https://ndownloader.figshare.com/files/{FILE_ID}"
API=f"https://api.figshare.com/v2/articles/{ARTICLE}/versions/{VERSION}"
OUTPUT=Path("results/biocon_e141_original_plot_planting_key_gate_20261124_v0_1.json")
DESIGN_FIELDS=("Sampling #","year","Season","Ring","Plot","CO2 Treatment",
               "Nitrogen Treatment","C and N treatment","Water Treatment","Water trt",
               "Temp Treatment","Temp trt","CountOfSpecies","CountOfGroup","Experiment",
               "monospecies","Monogroup")
REQUIRED=("year","Ring","Plot","CO2 Treatment","Nitrogen Treatment",
          "CountOfSpecies","Experiment")
def fetch(url,max_bytes=4_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"turnover-e141-source-key-only/0.1"})
    with urllib.request.urlopen(req,timeout=45) as resp:
        raw=resp.read(max_bytes+1)
    if len(raw)>max_bytes: raise ValueError("Source over cap")
    return raw

def parse_flag(value: str):
    v=str(value).strip().lower()
    if v in ("1","1.0","yes","true","y"): return 1
    if v in ("0","0.0","no","false","n"): return 0
    return None

def audit_design(raw: bytes):
    txt=raw.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(txt,newline=""))
    headers=list(reader.fieldnames or [])
    if len(headers)!=70: raise ValueError("Original column-schema changed")
    missing=[x for x in REQUIRED if x not in headers]
    if missing: raise ValueError("Missing original predeclared design columns")
    plant_cols=[x for x in headers if x.endswith(" planted")]
    if len(plant_cols)!=16: raise ValueError("Expected 16 distinct original planted flags")
    banned_response=[x for x in headers if "(g/m^2)" in x or x.startswith("% cover")]
    # The dict reader parses each raw CSV record structurally; NEVER touch the
    # banned response keys in the value object or emit original rows/plot IDs.
    years=collections.Counter()
    experiments=collections.Counter()
    richness=collections.Counter()
    flag_richness=collections.Counter()
    treatments=collections.Counter()
    ring_co2=collections.defaultdict(set)
    plot_rich=collections.defaultdict(set)
    plot_experiment=collections.defaultdict(set)
    source_annual_keys=collections.Counter()
    source_full_keys=collections.Counter()
    invalid_planted_rows=0
    nonmatching_planted_count=0
    no_ids=0
    rows=0
    no_co2_or_n=0
    for row in reader:
        rows+=1
        # Only predeclared identifier/treatment fields and source planted flags.
        d={x:(row.get(x) or "").strip() for x in DESIGN_FIELDS}
        yr=d["year"]; ring=d["Ring"]; plot=d["Plot"]; season=d["Season"]
        sampling=d["Sampling #"]
        years[yr]+=1
        exp=d["Experiment"];experiments[exp or "<missing>"]+=1
        richness[d["CountOfSpecies"] or "<missing>"]+=1
        treatments[(d["CO2 Treatment"] or "<missing>",d["Nitrogen Treatment"] or "<missing>")]+=1
        if ring and d["CO2 Treatment"]:ring_co2[ring].add(d["CO2 Treatment"])
        if not d["CO2 Treatment"] or not d["Nitrogen Treatment"]:no_co2_or_n+=1
        if not ring or not plot or not yr:
            no_ids+=1
        else:
            identity=(ring,plot)
            source_annual_keys[(ring,plot,yr)]+=1
            source_full_keys[(ring,plot,yr,season,sampling)]+=1
            plot_experiment[identity].add(exp)
        flags=[parse_flag(row.get(c,"")) for c in plant_cols]
        if any(x is None for x in flags):
            invalid_planted_rows+=1
        else:
            s=sum(flags)
            flag_richness[str(s)]+=1
            if d["CountOfSpecies"]:
                try:
                    if int(float(d["CountOfSpecies"]))!=s:nonmatching_planted_count+=1
                except ValueError:
                    nonmatching_planted_count+=1
            if ring and plot:
                plot_rich[(ring,plot)].add(tuple(flags))
    if rows==0:raise ValueError("Zero original source rows")
    rings=len(ring_co2)
    plotids=set(source_annual_keys)
    distinct_plots={k[:2] for k in plotids}
    # Do not treat repeated harvests/years as independent plots.
    return {
        "source_identity":"Original Figshare 26841637.v3 file 54836267",
        "original_source_md5":MD5,
        "verified_original_source_file_bytes":len(raw),
        "original_csv_record_count_including_repeated_years":rows,
        "design_header_names":[x for x in headers if x in DESIGN_FIELDS],
        "original_planted_indicator_field_count":len(plant_cols),
        "original_year_value_counts":dict(sorted(years.items())),
        "source_experiment_label_row_counts":dict(sorted(experiments.items())),
        "source_CountOfSpecies_row_counts":dict(sorted(richness.items())),
        "inferred_flag_sum_distribution_after_strict_0_1_parse":dict(sorted(flag_richness.items())),
        "rows_with_uninterpretable_plant_flags":invalid_planted_rows,
        "rows_where_count_species_differs_from_16_flag_sum":nonmatching_planted_count,
        "original_CO2_by_N_row_counts":[{"co2_label":a,"n_label":b,"source_rows":c}
             for (a,b),c in sorted(treatments.items())],
        "physical_ring_id_count":rings,
        "rings_with_multiple_CO2_label_values":sum(len(s)>1 for s in ring_co2.values()),
        "original_distinct_ring_plot_source_keys":len(distinct_plots),
        "original_distinct_ring_plot_year_keys":len(source_annual_keys),
        "source_rows_missing_ring_plot_year":no_ids,
        "original_ring_plot_year_keys_with_repeated_measurements":
            sum(c>1 for c in source_annual_keys.values()),
        "original_ring_plot_year_season_sampling_keys_with_duplicates":
            sum(c>1 for c in source_full_keys.values()),
        "physical_plots_with_nonconstant_sown_16_flag_vector_across_years":
            sum(len(v)>1 for v in plot_rich.values()),
        "physical_plots_with_nonconstant_Experiment_label_across_years":
            sum(len(v)>1 for v in plot_experiment.values()),
        "rows_missing_original_CO2_or_N_label":no_co2_or_n,
        "the_16_species_biomass_and_cover_numeric_columns_were_not_read":True,
        "banned_numeric_response_field_count":len(banned_response),
        "raw_species_biomass_values_opened":False,
        "original_total_biomass_values_opened":False,
        "original_cover_values_opened":False,
        "new_ecological_models_fitted":0,
        "one_field_experiment_not_independent_cross_site_replication":True,
    }

def test():
    assert parse_flag("1")==1 and parse_flag("0.0")==0 and parse_flag("Yes")==1
    assert parse_flag("bad") is None
    print("SYNTHETIC_DESIGN_FLAG_PARSER_PASS")

def run():
    out={"status":"SOURCE_ACCESS_OR_ASSIGNMENT_HOLD","original_eligible_effects_opened":0}
    try:
        m=json.loads(fetch(API,800_000))
        if int(m.get("id",-1))!=ARTICLE or int(m.get("version") or -1)!=VERSION:
            raise ValueError("Official Figshare original release ID/version changed")
        f=next(x for x in m["files"] if x["id"]==FILE_ID and x["name"]==FILE_NAME)
        assert (f.get("computed_md5") or f.get("supplied_md5") or "").lower()==MD5
        raw=fetch(URL)
        if hashlib.md5(raw).hexdigest()!=MD5:
            raise ValueError("Original CSV byte integrity failed")
        out["original_design_only"]=audit_design(raw)
        out["status"]="ORIGINAL_DESIGN_KEY_COUNTS_PASS_MONOCULTURE_TRAIT_SOURCE_JOIN_HOLD"
        # This stage audits source grain only, never claims ecological eligibility.
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,
            AssertionError,StopIteration,csv.Error,UnicodeError,KeyError,TypeError) as exc:
        out["source_exception_class"]=type(exc).__name__
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    a=p.parse_args()
    if a.selftest:test()
    elif a.source:run()
    else:p.error("choose --selftest or --source")
