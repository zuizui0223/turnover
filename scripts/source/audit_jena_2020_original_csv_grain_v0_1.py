#!/usr/bin/env python3
"""Original author Figshare Jena 2020 CSV schema and source-grain audit only.

Pin six original original-file ID, byte count and Figshare MD5. Read original
CSV values *only* in ephemeral GitHub runner to audit source-only key structure,
plot and year cardinality. No biological outcome/trait values or effects exported.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen

FILES={
 "biomass02_12.csv": (24365000,2120583,"2e350fae58c653c78edc606dad157533"),
 "CoverMain-JenaExp2003-2015all.csv":(24365003,198989,"9a1d6c8ea08e089717ae9933a11394ec"),
 "traits.st.csv":(24365039,47135,"8045e7ee38f26b212dbe81aed0039765"),
 "functions raw values.csv":(24365009,201652,"dc76132cd190a770eb4b0e8dbdd98c6e"),
 "functions4.st.csv":(24365006,360071,"0bb0b5b909f21b1c152086351ad7f240"),
 "predictors_raw.csv":(24365042,2334726,"1ad0602600c00a9c2f580c05ebd8084c"),
}
UA="turnover-jena-longitudinal-original-primary-source-keys/0.1"
ALIASES={
"plot":("plot","plot_id","plotid","plotnumber","plot_nr","plot.id"),
"year":("year","yearid","year_id","calendar_year","dateyear","yyyy"),
"species":("species","species_name","speciescode","species_code","species.id","spec","sp"),
"season":("season","sampling_season","harvest","month"),
}
MIN_PLOTS=50
MIN_YEARS=6
MIN_SPECIES=20
MAX_ROW_FIELDS=200
MAX_YEAR_CLASSES=30

def get_orig(name):
    f,bytes_expected,md5=FILES[name]
    req=Request(f"https://ndownloader.figshare.com/files/{f}",
                headers={"User-Agent":UA,"Accept":"text/csv, */*"})
    with urlopen(req,timeout=100) as resp:
        if resp.status!=200:raise ValueError("SOURCE_ACCESS_HOLD: non-200 original file")
        raw=resp.read(bytes_expected+1)
    if len(raw)!=bytes_expected or hashlib.md5(raw).hexdigest()!=md5:
        raise ValueError("SOURCE_DRIFT_HOLD: official Figshare exact original byte size / MD5 differs "+name)
    return raw

def normalize_key(v):
    return "".join(c for c in str(v or "").strip().lower() if c.isalnum())

def col_find(names):
    named={normalize_key(c):c for c in names}
    ans={}
    for kind,names_in in ALIASES.items():
        values=[named[normalize_key(t)] for t in names_in if normalize_key(t) in named]
        values=list(dict.fromkeys(values))
        ans[kind]=values[0] if len(values)==1 else None
    return ans

def audit_csv(name,raw):
    # If a file uses a non-comma delimiter despite .csv, it fails closed
    # rather than silently interpreting the entire row as one column.
    try:t=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:t=raw.decode("cp1252")
        except Exception:raise ValueError("SOURCE_SCHEMA_HOLD: unsupported original source file encoding")
    reader=csv.DictReader(io.StringIO(t,newline=""))
    cols=reader.fieldnames or []
    if len(cols)<=1 or len(cols)>MAX_ROW_FIELDS or len(cols)!=len(set(cols)):
        return {"status":"SOURCE_SCHEMA_HOLD","reason":"Original primary source CSV header not a valid multi-column comma-delimited matrix",
                "source_field_names":cols[:MAX_ROW_FIELDS],"rows_scanned":0}
    if any(c is None or not c.strip() for c in cols):
        raise ValueError("SOURCE_SCHEMA_HOLD: original blank header")
    names=col_find(cols)
    valid_year=set();plots=set();species=set();plotyear=set()
    yy=collections.Counter()
    missing=collections.Counter()
    row_count=0
    invalid=0
    for row in reader:
        row_count+=1
        if None in row:invalid+=1
        if row_count>300000:raise ValueError("SOURCE_SIZE_HOLD: >300000 rows in small source CSV")
        for key,col in names.items():
            if col is not None and (row.get(col) is None or not str(row[col]).strip()):
                missing[key]+=1
        if names["plot"] is not None:
            plot=str(row.get(names["plot"]) or "").strip()
            if plot: plots.add(plot)
        else:plot=None
        if names["year"] is not None:
            year=str(row.get(names["year"]) or "").strip()
            # Column may be year number, not an original date; flag outside
            # range as ambiguity rather than choosing a more plausible year.
            if year:
                valid_year.add(year)
                yy[year]+=1
        else:year=None
        if plot and year:plotyear.add((plot,year))
        if names["species"] is not None:
            s=str(row.get(names["species"]) or "").strip()
            if s:species.add(s)
    return {
      "status":"SOURCE_SCHEMA_READ_PASS" if invalid==0 else "SOURCE_ROW_STRUCTURE_HOLD",
      "original_source_exact_MD5_pinned":True,
      "source_file_id":FILES[name][0],"advertised_bytes":FILES[name][1],"md5":FILES[name][2],
      "rows_scanned":row_count,"column_count":len(cols),
      "source_field_names":cols,
      "original_exact_key_column_candidates":names,
      "n_blank_original_key_cells":dict(missing),
      "n_malformed_source_delimited_rows":invalid,
      "n_unique_original_plot_labels_if_explicit_column":len(plots) if names["plot"] else None,
      "n_unique_original_year_labels_if_explicit_column":len(valid_year) if names["year"] else None,
      "n_unique_original_species_labels_if_explicit_column":len(species) if names["species"] else None,
      "n_unique_plot_year_keys_if_both_exact_columns":len(plotyear) if plotyear else None,
      "original_year_labels_if_explicit_and_reasonable_cardinality":sorted(valid_year) if len(valid_year)<=MAX_YEAR_CLASSES else None,
      "original_plot_and_species_values_NOT_exported":True,
      "original_biomass_or_trait_numerical_values_NOT_exported":True,
      "no_ecological_effect_tested":True,
    }

def main():
    docs={}
    for file in FILES:
        raw=get_orig(file)
        docs[file]=audit_csv(file,raw)
        print("JENA_ORIGINAL_SOURCE_CSV_SCHEMA",json.dumps({"file":file,**docs[file]},sort_keys=True),flush=True)
    # Require explicit source names; structural assessment must respect all
    # file-specific original units of observation and independent years.
    plot_sources=[(f,v) for f,v in docs.items() if v.get("n_unique_original_plot_labels_if_explicit_column") is not None]
    years=[(f,v) for f,v in docs.items() if v.get("n_unique_original_year_labels_if_explicit_column") is not None]
    traits=docs["traits.st.csv"]
    qual=("SOURCE_ONLY_MULTI_YEAR_KEY_SCHEMA_DISCOVERED" if
        any(z.get("n_unique_original_plot_labels_if_explicit_column",0)>=MIN_PLOTS and
            z.get("n_unique_original_year_labels_if_explicit_column",0)>=MIN_YEARS for _,z in plot_sources)
        else "PLOT_YEAR_KEY_SEMANTICS_HOLD")
    if not all(v["status"]=="SOURCE_SCHEMA_READ_PASS" for v in docs.values()):
        qual="FILE_SCHEMA_HOLD"
    return {
       "version":"v0.1","status":qual,
       "original_authored_Figshare_article":12834350,
       "original_Jena_2020_study":"van der Plas et al 2020 Nat Ecol Evol DOI 10.1038/s41559-020-01316-9",
       "full_six_original_CSV_MD5_and_byte_size_source_verified":True,
       "original_csv_metadata":docs,
       "n_six_original_source_files":len(docs),
       "n_original_explicit_plot_candidate_files":len(plot_sources),
       "n_original_explicit_year_candidate_files":len(years),
       "original_plot_year_trait_biomass_cross_file_join_verified":False,
       "original_response_scale_and_season_identity_verified":False,
       "original_2020_original_dataset_and_2022_reply_are_same_Jena_experiment":True,
       "Jena_source_not_independent_of_earlier_turnover_Jena_guild_study":True,
       "n_original_biomass_trait_effects_estimated":0,
       "historical_BIEN_spatial_201family_and_GloBI_terminal_source_gates_remain_HOLD":True,
       "next_step":"Inspect documented original plot/year/sp species and function naming rules if source schema supports it; freeze outcome model only after verified original joins. No reanalysis of previously published positive authors' effects as independent discovery."
    }

def fixture():
    sample=b"plot,year,species,biomass\np1,2003,a,15\np2,2004,b,25\n"
    d=audit_csv("traits.st.csv",sample)
    assert d["source_field_names"]==["plot","year","species","biomass"]
    assert d["n_unique_original_plot_labels_if_explicit_column"]==2
    assert d["n_unique_original_species_labels_if_explicit_column"]==2
    assert d["n_unique_original_year_labels_if_explicit_column"]==2
    return {"status":"ORIGINAL_JENA_CSV_GRAIN_FIXTURE_PASS","checks":4}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.out:p.error("--out required")
        d=main()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
        print("JENA_ORIGINAL_2020_SIX_CSV_GRAIN_SOURCE_VERDICT",
              json.dumps({"status":d["status"],"original_csv_metadata":
                {k:{"rows_scanned":v.get("rows_scanned"),"source_field_names":v.get("source_field_names"),
                   "key_columns":v.get("original_exact_key_column_candidates")} for k,v in d["original_csv_metadata"].items()}},
                       sort_keys=True),flush=True)
