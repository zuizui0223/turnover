#!/usr/bin/env python3
"""Source-only original EDI 538 annual SLA measurement-year eligibility."""
from __future__ import annotations
import argparse
import collections
import csv
import io
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

URL = ("https://pasta.lternet.edu/package/data/eml/knb-lter-cdr/538/9/"
       "d6a22544411064d397041a9548f73074")
OUT = Path("results/biocon_e141_edi538_original_SLA_measurement_year_gate_20261124_v0_1.json")
REQUIRED = ("CountOfSpecies","measured.species","CO2.Treatment","Nitrogen.Treatment","SLA..cm2.g.")
YEAR_CANDIDATES = ("Year","year","Sampling.Year","Sample.Year","Measurement.Year")

def get(url, limit=12000000):
    req=urllib.request.Request(url,headers={"User-Agent":"BioCON-E141-source-only-original-EDI/0.1"})
    with urllib.request.urlopen(req, timeout=35) as r:
        raw=r.read(limit+1)
    if len(raw)>limit:
        raise ValueError("source exceeds predeclared byte cap")
    return raw

def inspect(raw:bytes):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""),delimiter="\t")
    fields=list(reader.fieldnames or [])
    if len(fields)!=len(set(fields)) or len(fields)>300 or not set(REQUIRED).issubset(fields):
        raise ValueError("required original author source fields absent or ambiguous")
    year_fields=[x for x in YEAR_CANDIDATES if x in fields]
    if len(year_fields)!=1:
        raise ValueError("missing or multiple original year columns; source time HOLD")
    year_key=year_fields[0]
    yrs=collections.Counter()
    earliest={}
    n_total=n_mono=n_missing=0
    for row in reader:
        n_total+=1
        if (row.get("CountOfSpecies") or "").strip() not in ("1","1.0"):
            continue
        n_mono+=1
        # Do not parse any numeric SLA value; only test original source field presence.
        v=(row.get("SLA..cm2.g.") or "").strip()
        if v in ("","NA","NaN","-9999","-9999.0"):
            n_missing+=1
            continue
        date=(row.get(year_key) or "").strip()
        if not re.fullmatch(r"(?:19|20)\d{2}",date) or not 1997<=int(date)<=2025:
            raise ValueError("undated original SLA observation, no posthoc year mapping")
        sp=(row.get("measured.species") or "").strip()
        if sp=="Koleria cristata":sp="Koeleria cristata"  # exact author code correction
        co2=(row.get("CO2.Treatment") or "").strip()
        n=(row.get("Nitrogen.Treatment") or "").strip()
        if not sp or co2 not in ("Camb","Cenrich") or n not in ("Namb","Nenrich"):
            raise ValueError("original SLA source species or CO2/N treatment ambiguous")
        key=(sp,co2,n)
        earliest[key]=min(earliest.get(key,int(date)),int(date))
        yrs[date]+=1
    if not earliest:
        raise ValueError("no valid original dated monoculture SLA source cells")
    by_earliest=collections.Counter(earliest.values())
    return {
      "original_source_package":"knb-lter-cdr.538.9",
      "original_year_field":year_key,
      "source_raw_rows_parsed_as_metadata_only":n_total,
      "source_mono_rows":n_mono,
      "source_mono_missing_SLA_value_presence":n_missing,
      "source_mono_direct_species_CO2_N_cells":len(earliest),
      "source_first_observation_year_cell_histogram":dict(sorted(by_earliest.items())),
      "source_monoculture_SLA_observation_years":dict(sorted(yrs.items())),
      "direct_source_cells_available_strictly_before_each_outcome_year":{
          str(year):sum(yr<year for yr in earliest.values())
          for year in range(1998,2022)},
      "numeric_trait_values_opened":False,
      "numeric_biomass_values_opened":False,
      "new_statistical_outcomes_fitted":0
    }

def synthetic():
    fields=list(REQUIRED)+["Year"]
    src=("\t".join(fields)+"\n"+"1\tKoeleria cristata\tCamb\tNamb\t123.4\t2001\n").encode()
    a=inspect(src)
    assert a["source_mono_direct_species_CO2_N_cells"]==1
    assert a["direct_source_cells_available_strictly_before_each_outcome_year"]["2001"]==0
    assert a["direct_source_cells_available_strictly_before_each_outcome_year"]["2002"]==1
    print("SYNTHETIC_ORIGINAL_EDI_MEASUREMENT_YEAR_GATE_PASS")

def main():
    output={"as_of_jst":"2026-11-24","original_edi_package":"knb-lter-cdr.538.9",
            "source_status":"EDI_ACCESS_OR_YEAR_SOURCE_HOLD",
            "original_numeric_trait_values_opened":False,
            "original_numeric_biomass_opened":False,
            "new_FD_effects_fitted":0}
    try:
        data=get(URL)
        output["verified_public_original_source_bytes"]=len(data)
        output["source_date_only"]=inspect(data)
        output["source_status"]="ORIGINAL_EDI_SLA_DATE_GRAIN_PASS_PLOT_JOIN_HOLD"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
            UnicodeError,ValueError,csv.Error,KeyError,TypeError) as exc:
        output["failure_class"]=type(exc).__name__
        if isinstance(exc,urllib.error.HTTPError):
            output["http_status"]=exc.code
        if isinstance(exc,ValueError):
            output["schema_or_date_hold_reason"]=str(exc)[:150]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--source",action="store_true")
    args=p.parse_args()
    if args.selftest:synthetic()
    elif args.source:main()
    else:p.error("Choose --selftest or --source")
