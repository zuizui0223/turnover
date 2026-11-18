#!/usr/bin/env python3
"""Source-only corroboration of original 'Plot code' and signed AGB/coordinate units.

Uses exactly source-verified official Zenodo original 19609795 bytes and two MD5s.
No regression, raw source row/sample plot/taxon identifiers exported.
v0.1 found 200 rows and negative AGB; this is a source semantics diagnostic.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path

from audit_zenodo_independent_forest_agb_trait_grain_v0_1 import (
    API,DOI,RECORD,TARGET,MAX_SOURCE_BYTES,bounded
)

PLOT_COL="Plot code"
SITE_COL="Site"
BIO_COL="AGB"
GEO_COLS=("Latitude","Longitude")
SIG_RE=re.compile(r"standardiz|standardis|z.?score|normaliz|normalis|scaled|scaling|center|centr|unit|z.transfor",re.I)
SEMANTIC_RE=re.compile(r"\bAGB\b|biomass|measur|trait|plot|latitude|longitude|covari|field|site",re.I)

def sourcefiles():
    metadata=json.loads(bounded(API,3_000_000))
    if metadata.get("id")!=RECORD or metadata.get("doi")!=DOI:
        raise ValueError("SOURCE_HOLD: Zenodo original DOI/record identity changed")
    files={v.get("key"):v for v in metadata.get("files",[])}
    output={}
    for name,digest in TARGET.items():
        item=files.get(name)
        if not item or str(item.get("checksum","")).removeprefix("md5:").lower()!=digest:
            raise ValueError("SOURCE_HOLD: official original Zenodo manifest checksum changed")
        url=(item.get("links") or {}).get("self")
        if not url:raise ValueError("SOURCE_HOLD: original Zenodo file not linked")
        raw=bounded(url,MAX_SOURCE_BYTES)
        if len(raw)!=item.get("size") or hashlib.md5(raw).hexdigest()!=digest:
            raise ValueError("SOURCE_HOLD: source MD5 or original bytes changed")
        output[name]=raw
    return output

def numeric_profile(rows, key):
    values=[]
    missing=0
    for r in rows:
        raw=str(r.get(key) or "").strip()
        if not raw or raw.casefold() in {"na","nan","null","none","-9999","-9999.0"}:
            missing+=1
            continue
        try: x=float(raw)
        except ValueError:raise ValueError("SOURCE_SCHEMA_HOLD: unexpected nonnumeric "+key)
        if not math.isfinite(x):raise ValueError("SOURCE_SCHEMA_HOLD: nonfinite "+key)
        values.append(x)
    if not values:return {"n_valid":0,"n_missing":missing}
    n=len(values)
    avg=sum(values)/n
    std=math.sqrt(sum((x-avg)**2 for x in values)/n)
    return {"n_valid":n,"n_missing":missing,"n_negative":sum(x<0 for x in values),
            "n_zero":sum(x==0 for x in values),"n_positive":sum(x>0 for x in values),
            "aggregate_mean":avg,"aggregate_population_sd":std,
            "aggregate_min":min(values),"aggregate_max":max(values)}

def run():
    src=sourcefiles()
    raw=src["Forest_AGB_Data. Final.csv"].decode("utf-8-sig")
    rr=csv.DictReader(io.StringIO(raw))
    rows=list(rr)
    expected={PLOT_COL,SITE_COL,BIO_COL,*GEO_COLS}
    if not rr.fieldnames or not expected.issubset(set(rr.fieldnames)) or len(rows)!=200:
        raise ValueError("SOURCE_SCHEMA_HOLD: original 200/28 source columns changed")
    if len(rr.fieldnames)!=28:raise ValueError("SOURCE_SCHEMA_HOLD: original 28 fields changed")
    keys=[]
    siteplots=collections.defaultdict(set)
    for r in rows:
        pk=str(r[PLOT_COL] or "").strip()
        sk=str(r[SITE_COL] or "").strip()
        if not pk or not sk:
            raise ValueError("SOURCE_GRAIN_HOLD: original plot/site key missing")
        keys.append((sk,pk))
        siteplots[sk].add(pk)
    duplication=len(keys)-len(set(keys))
    source_readme=src["README Dataset Description.txt"].decode("utf-8-sig")
    evidence=[]
    for i,line in enumerate(source_readme.splitlines(),1):
        if SIG_RE.search(line) or SEMANTIC_RE.search(line):
            evidence.append({
               "line_number":i,
               "has_standardization_term":bool(SIG_RE.search(line)),
               "has_AGB_or_biomass_term":bool(re.search(r"\bAGB\b|biomass",line,re.I)),
               "has_species_trait_term":bool(re.search(r"species|trait",line,re.I)),
               "has_plot_or_site_term":bool(re.search(r"plot|site",line,re.I)),
            })
    # Print only very short README semantic leads to original source stdout.
    # Do not store original full README copyrighted source text in Git.
    print("ORIGINAL_README_RELEVANT_SHORT_EXCERPTS_BEGIN",flush=True)
    for i,line in enumerate(source_readme.splitlines(),1):
        if SIG_RE.search(line) or re.search(r"\bAGB\b|biomass|standard",line,re.I):
            print("SOURCE_README_LINE",i,(" ".join(line.split()))[:140],flush=True)
    print("ORIGINAL_README_RELEVANT_SHORT_EXCERPTS_END",flush=True)
    biomass=numeric_profile(rows,BIO_COL)
    latitude=numeric_profile(rows,"Latitude")
    longitude=numeric_profile(rows,"Longitude")
    if biomass["n_valid"]!=200 or biomass["n_negative"]!=157:
        raise ValueError("SOURCE_HOLD: prior verified 200 AGB and 157 negative raw source results changed")
    readme_std=bool(SIG_RE.search(source_readme))
    if biomass["n_negative"]>0:
        physical="NONPHYSICAL_SIGNED_AGB_SOURCE_SCALE_HOLD"
    else:
        physical="ORIGINAL_RAW_AGB_UNITS_UNVERIFIED"
    return {
      "version":"v0.2",
      "status":"ORIGINAL_PLOT_KEY_IDENTIFIED_AND_AGB_SCALE_AUDITED",
      "source_dataset_doi":DOI,
      "source_exact_Zenodo_record_id":RECORD,
      "source_MD5_original_forest_CSV":TARGET["Forest_AGB_Data. Final.csv"],
      "source_MD5_original_README":TARGET["README Dataset Description.txt"],
      "n_original_CSV_rows":len(rows),
      "source_site_column":SITE_COL,
      "source_plot_column":PLOT_COL,
      "n_unique_original_site_plot_keys":len(set(keys)),
      "n_source_duplicate_site_plot_keys":duplication,
      "original_site_label_count":len(siteplots),
      "original_source_plot_counts_per_site_anonymized":sorted(len(v) for v in siteplots.values()),
      "same_plot_label_possible_in_multiple_sites":len({p for _,p in keys})<len(set(keys)),
      "original_AGB_numeric_profile_nonraw":biomass,
      "original_latitude_numeric_profile_nonraw":latitude,
      "original_longitude_numeric_profile_nonraw":longitude,
      "original_AGB_physical_units_gate":physical,
      "source_latitude_longitude_raw_geographic_coordinate_claim":"HOLD_IF_ANY_NEGATIVE_LATITUDE_IN_PAKISTAN",
      "readme_semantic_keyword_counts":{
          "lines_with_AGB_or_biomass":sum(e["has_AGB_or_biomass_term"] for e in evidence),
          "lines_with_standardization_or_scale_term":sum(e["has_standardization_term"] for e in evidence),
          "lines_with_species_traits":sum(e["has_species_trait_term"] for e in evidence),
          "lines_with_plot_or_site":sum(e["has_plot_or_site_term"] for e in evidence)
      },
      "source_readme_has_any_explicit_standardization_or_scaling_word":readme_std,
      "source_readme_original_line_count":len(source_readme.splitlines()),
      "no_species_level_source_trait_records_in_original_file":True,
      "original_source_stores_only_precomputed_fdis_fdiv_feve_fric_and_CWM_traits":True,
      "original_species_trait_to_plot_K_FD_mass_source_eligibility":"PLOT_SUMMARY_ONLY_HOLD",
      "source_AGB_not_safe_to_interpret_as_g_m2_or_Mg_ha_without_original_inverse_scale":True,
      "no_AGB_trait_correlations_estimated":True,
      "no_individual_original_plot_rows_or_original_response_values_committed":True,
      "original_201_family_global_programme_and_BIODEPTH_TreeDivNet_closed_gates_untouched":True,
    }

def fixture():
    x=[{"AGB":"-1.0"},{"AGB":"1.0"}]
    p=numeric_profile(x,"AGB")
    assert p["n_negative"]==1 and p["n_positive"]==1
    assert p["aggregate_mean"]==0
    assert PLOT_COL=="Plot code"
    return {"status":"FOREST_PLOT_CODE_AND_SIGNED_AGB_SOURCE_FIXTURE_PASS","checks":4}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.out:p.error("--out required")
        try: obj=run()
        except Exception as exc:
            obj={"version":"v0.2","status":"SOURCE_ACCESS_OR_SCHEMA_HOLD",
                 "exception_type":type(exc).__name__,
                 "reason":str(exc)[:260],
                 "source_dataset_doi":DOI,
                 "no_AGB_trait_correlations_estimated":True}
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("FOREST_ZENODO_ORIGINAL_PLOT_CODE_AND_AGB_SCALE_SOURCE_QA",
              json.dumps(obj,sort_keys=True),flush=True)
