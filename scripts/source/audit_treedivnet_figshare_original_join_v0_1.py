#!/usr/bin/env python3
"""Source-only original Figshare XLSX DS1×DS2 exact field/plot/species join audit.

No ecological effect, no plot-derived FD, no phylogenetic K, no biomass
prediction. Original XLSX rows/traits/carbon responses never exported or
logged; only source-key, numeric-field completeness and support summaries.
"""
from __future__ import annotations

import argparse
import collections
import csv
import io
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from audit_treedivnet_figshare_workbooks_v0_1 import (
    EXPECTED,NS,fetch_file,shared_strings,source_sheets,get_xml,texts
)

FIELDS_DS1=("site","block","plot","species_richness","species_composition","biomass_woody")
FIELDS_DS2=("site","block","plot","species","species_richness","biomass_woody",
           "SLA","WD","LNCM")
TRAITS=("SLA","WD","LNCM","LNCA","LPCM","height_increment")
MAX_ROW=30000
SENTINELS={"","na","n/a","-9999","-9999.0","nan","null","none","nd"}


def colnum(cellref:str)->int:
    letters=re.match(r"^([A-Z]+)[0-9]+$",str(cellref))
    if not letters:raise ValueError("SOURCE_SCHEMA_HOLD: invalid XLSX original coordinate")
    n=0
    for x in letters[1]:n=n*26+ord(x)-ord("A")+1
    return n-1


def extract_cell(c:ET.Element,sh:list[str])->str:
    typ=c.attrib.get("t") or ""
    if typ=="s":
        v=c.find("m:v",NS)
        return sh[int(v.text)] if v is not None and v.text is not None else ""
    if typ=="inlineStr":
        return texts(c)
    v=c.find("m:v",NS)
    return (v.text or "").strip() if v is not None else ""


def load_table(name:str)->tuple[list[dict],list[str],str]:
    raw=fetch_file(name)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        shared=shared_strings(z)
        sheets=source_sheets(z)
        if len(sheets)!=1:
            raise ValueError("SOURCE_SCHEMA_HOLD: expected one original data sheet in "+name)
        sheetname,sheetpath=sheets[0]
        root=get_xml(z,sheetpath)
        data=root.find("m:sheetData",NS)
        if data is None:raise ValueError("SOURCE_SCHEMA_HOLD: original workbook no sheetData")
        rs=data.findall("m:row",NS)
        if len(rs)>MAX_ROW:raise ValueError("SOURCE_SCHEMA_HOLD: too many original workbook rows")
        rows=[]
        for r in rs:
            dd={}
            for cell in r.findall("m:c",NS):
                k=colnum(cell.attrib.get("r",""))
                if k in dd:raise ValueError("SOURCE_SCHEMA_HOLD: duplicate original cell")
                dd[k]=extract_cell(cell,shared)
            rows.append(dd)
    if not rows:raise ValueError("SOURCE_SCHEMA_HOLD: original empty XLSX")
    first=rows[0]
    header=[str(first.get(i,"")).strip() for i in range(max(first)+1)]
    if not header or any(not s for s in header) or len(header)!=len(set(header)):
        raise ValueError("SOURCE_SCHEMA_HOLD: empty or duplicate original first-row header")
    output=[]
    for row in rows[1:]:
        if not any(str(v).strip() for v in row.values()):continue
        if any(k>=len(header) and str(v).strip() for k,v in row.items()):
            raise ValueError("SOURCE_SCHEMA_HOLD: data columns outside header")
        output.append({h:str(row.get(i,"")).strip() for i,h in enumerate(header)})
    if len(output)!=len(rows)-1:
        raise ValueError("SOURCE_SCHEMA_HOLD: blank original internal data rows")
    return output,header,sheetname


def norm(s:str)->str:
    return " ".join(str(s or "").strip().casefold().split())


def key(row:dict)->tuple:
    return (norm(row.get("site")),norm(row.get("block")),norm(row.get("plot")))


def num(s:str,positive=False):
    if norm(s) in SENTINELS:return None
    try:
        x=float(s)
    except Exception:return None
    if not math.isfinite(x) or x<0 or (positive and x<=0):return None
    return x


def usable(row,trait):
    return num(row.get(trait,""),positive=True) is not None


def audit()->dict:
    ds1,c1,sh1=load_table("DS1.xlsx")
    ds2,c2,sh2=load_table("DS2.xlsx")
    ds3,c3,sh3=load_table("DS3.xlsx")
    for field in FIELDS_DS1:
        if field not in c1:raise ValueError("SOURCE_SCHEMA_HOLD: required DS1 field missing: "+field)
    for field in FIELDS_DS2:
        if field not in c2:raise ValueError("SOURCE_SCHEMA_HOLD: required DS2 field missing: "+field)
    if len(ds1)!=363 or len(ds2)!=689 or len(ds3)!=224:
        raise ValueError("SOURCE_DRIFT_HOLD: published original workbook row population changed")
    # Original 3-column block×plot key is used; no positional join, synonyms or
    # post-outcome-based data selection, and no original plot identity is exported.
    d1=collections.defaultdict(list)
    d2=collections.defaultdict(list)
    d3=collections.defaultdict(list)
    for row in ds1:d1[key(row)].append(row)
    for row in ds2:d2[key(row)].append(row)
    for row in ds3:d3[key(row)].append(row)
    if ("site" not in c3 or "block" not in c3 or "plot" not in c3):
        raise ValueError("SOURCE_SCHEMA_HOLD: DS3 source key differs")
    dup1=sum(len(v)-1 for v in d1.values())
    dup3=sum(len(v)-1 for v in d3.values())
    dup2=0
    species_key_counts=collections.Counter()
    for row in ds2:
        species_key_counts[(key(row),norm(row["species"]))]+=1
    dup2=sum(v-1 for v in species_key_counts.values())
    a=set(d1); b=set(d2); c=set(d3)
    sites=set(k[0] for k in a)
    site_ds2=set(k[0] for k in b)
    joined=a&b
    ids_by_site=collections.Counter(k[0] for k in joined)
    d1_mass={k for k,rr in d1.items() if any(num(r["biomass_woody"]) is not None for r in rr)}
    d2_mass={k for k,rr in d2.items() if any(num(r["biomass_woody"]) is not None for r in rr)}
    leaf_plots=collections.defaultdict(lambda:collections.defaultdict(set))
    native_trait_plots=collections.defaultdict(set)
    for row in ds2:
        ident=key(row)
        sp=norm(row["species"])
        if not sp:continue
        for t in TRAITS:
            if usable(row,t):leaf_plots[ident][t].add(sp)
        if any(usable(row,t) for t in TRAITS):
            native_trait_plots[ident].add(sp)
    joined_mass=joined&d1_mass&d2_mass
    eligible_traits=collections.defaultdict(set)
    bytrait={}
    for trait in TRAITS:
        pairs={k for k in joined_mass if len(leaf_plots[k][trait])>=2}
        spp={sp for k in pairs for sp in leaf_plots[k][trait]}
        bytrait[trait]={"mass_and_trait_plot_keys_with_two_species":len(pairs),
            "source_site_counts":dict(sorted(collections.Counter(k[0] for k in pairs).items())),
            "unique_species_with_positive_original_values":len(spp)}
        eligible_traits[trait]=pairs
    any2={k for k in joined_mass if len(native_trait_plots[k])>=2}
    core_species={s for k in any2 for s in native_trait_plots[k]}
    eligible_site=collections.Counter(k[0] for k in any2)
    source_fields=len([s for s,n in eligible_site.items() if n>=8])
    missing_original_provenance={
       name:[h for h in headers if any(q in h.casefold() for q in
           ("source","origin","measured","imputed","literature","provenance","dataset","reference"))]
       for name,headers in [("DS1",c1),("DS2",c2),("DS3",c3)]
    }
    has_trait_provenance=bool(missing_original_provenance["DS2"])
    yearfields={name:[h for h in headers if any(q in h.casefold() for q in ("year","date","time"))]
           for name,headers in [("DS1",c1),("DS2",c2)]}
    has_year=bool(yearfields["DS1"]) and bool(yearfields["DS2"])
    # Original authors' README is not a biological-response row. Preserve
    # only bounded source documentation around provenance/measurement
    # descriptions to assess whether published DS2 values are individual,
    # plot-aggregated, monoculture-based or literature-filled.
    readme=fetch_file("README.txt").decode("utf-8-sig",errors="replace").splitlines()
    related=set()
    for i,line in enumerate(readme):
        if re.search(r"\\bDS[123]\\b|measure|source|literature|mono|trait|species|biomass|year|missing|plot|experiment",line,re.I):
            related.update(range(max(i-1,0),min(i+2,len(readme))))
    documentation=[{"line":i+1,"text":" ".join(readme[i].split())[:180]} for i in sorted(related)
                   if readme[i].strip()]
    source_structure=(len(any2)>=80 and len(core_species)>=20 and source_fields>=5)
    # Do not mark original *primary measurements* as confirmed by mere presence
    # of plot-level species trait values: the publication says some traits
    # are monoculture estimates and 17 source replacements are literature.
    final_status=("ORIGINAL_SOURCE_PLOT_SUPPORT_PASS_PROVENANCE_HOLD" if source_structure
                  else "SOURCE_COVERAGE_HOLD")
    if not has_trait_provenance or not has_year:
        final_status=("ORIGINAL_SOURCE_PLOT_SUPPORT_PASS_PROVENANCE_HOLD" if source_structure
                      else "SOURCE_COVERAGE_HOLD")
    return {
      "version":"v0.1","status":final_status,
      "study":"Jensen et al 2026 Figshare v1 TreeDivNet original DS1×DS2×DS3",
      "figshare_doi":"10.6084/m9.figshare.31026004.v1",
      "source_checksum_verified_files":{n:EXPECTED[n]["md5"] for n in ("DS1.xlsx","DS2.xlsx","DS3.xlsx")},
      "original_source_row_counts":{"DS1":len(ds1),"DS2":len(ds2),"DS3":len(ds3)},
      "source_original_site_by_block_by_plot_key_used":True,
      "source_DS1_unique_plot_keys":len(d1),
      "source_DS2_unique_plot_keys":len(d2),
      "source_DS3_unique_plot_keys":len(d3),
      "duplicated_source_DS1_plot_records":dup1,
      "duplicated_source_DS2_plot_by_species_records":dup2,
      "duplicated_source_DS3_plot_records":dup3,
      "source_DS1_original_sites":len(sites),
      "source_DS2_original_sites":len(site_ds2),
      "source_all_file_plot_overlap":len(a&b&c),
      "source_DS1_DS2_exact_original_plot_overlap":len(joined),
      "source_site_counts_of_DS1_DS2_overlap":dict(sorted(ids_by_site.items())),
      "source_DS1_mass_numeric_plot_keys":len(d1_mass),
      "source_DS2_mass_numeric_plot_keys":len(d2_mass),
      "source_DS1_DS2_coincident_mass_numeric_plot_keys":len(joined_mass),
      "original_plots_with_two_species_at_least_one_positive_trait_and_mass":len(any2),
      "unique_species_in_two_species_plus_plot_cohort":len(core_species),
      "original_experiments_with_at_least8_coincident_trait_mass_plots":source_fields,
      "source_sites_eligible_ge8":dict(sorted((s,n) for s,n in eligible_site.items() if n>=8)),
      "by_individual_trait_positive_presence":bytrait,
      "source_schema_trait_origin_flags":missing_original_provenance,
      "has_original_trait_measurement_source_indicator":has_trait_provenance,
      "source_explicit_observation_year_fields":yearfields,
      "has_plot_species_trait_and_woody_mass_year_matched":has_year,
      "source_plot_support_thresholds":{"min_eligible_plot_ids":80,
               "min_experiments_with_8plots":5,"min_unique_species":20,
               "min_eligible_species_per_plot":2},
      "source_structural_plot_support_pass":source_structure,
      "original_source_readme_measurement_documentation":documentation[:90],
      "source_first_effect_gate_pass":False,
      "reason":"Original species-plot traits and plot woody biomass can be structurally joined, but source direct-vs-monoculture-vs-literature trait provenance and original observation-year alignment cannot be proven from DS2/DS1 workbook fields alone. Supplementary measurement provenance and dated study documentation required before novel effect.",
      "biological_effect_estimated":False,
      "original_numeric_biomass_values_exported":False,
      "original_species_plot_rows_exported":False,
      "original_2026_paper_already_analysed_diversity_mass":True,
      "no_12family20species_K_test_possible":True,
    }


def fixture():
    assert colnum("AZ14")==51
    assert num("0") == 0 and num("NaN") is None and num("-9999") is None
    assert num("2.7",positive=True)==2.7
    assert key({"site":"A","block":"2","plot":"003"})==("a","2","003")
    return {"status":"FIGSHARE_EXACT_SOURCE_JOIN_FIXTURE_PASS","checks":4}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture()))
    else:
        if not a.out:p.error("--out required")
        result=audit()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("TREEDIVNET_ORIGINAL_EXACT_PLOT_SPECIES_JOIN",json.dumps(result,sort_keys=True),flush=True)
