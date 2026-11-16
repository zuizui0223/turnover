#!/usr/bin/env python3
"""TreeDivNet original Figshare DS1×DS2 plot/species data-quality gate.

NO FD, phylogenetic K, trait→biomass regression or effect estimates.
Uses only stdlib XLSX ZIP/XML reader, pinned original Figshare source MD5.
Original plot/species-level rows never printed or persisted in Git.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import io

from audit_treedivnet_figshare_workbooks_v0_1 import (
    EXPECTED, NS, MAX_XLSX_UNCOMPRESSED, fetch_file, get_xml,
    shared_strings, source_sheets, texts,
)

TAXON_COLUMNS=("species",)
TR=("SLA","WD","LNCM","LNCA","LPCM","height_increment")
CORE=("site","block","plot")
COMMON=("site","block","plot","treatment","species_richness","species_composition")
N_MIN_PLOTS=80
N_MIN_SITES=5
N_MIN_PER_SITE=8
N_MIN_SPECIES=20
PLACEHOLDERS={"", "na", "n/a", "nan", "null", "none", "-9999", "-9999.0", "-999", "missing"}


def compact(v)->str:
    s=" ".join(str(v or "").strip().split())
    # Do not invent aliases for site, block or plot. Canonicalize only
    # number-formatted identifiers, e.g. Excel 2.0 vs 2.
    if re.fullmatch(r"[-+]?[0-9]+(?:\.0+)?",s):
        return str(int(float(s)))
    return s


def safe_num(v,positive=False):
    if v is None or str(v).strip().casefold() in PLACEHOLDERS:return None
    try:
        x=float(str(v).strip())
        return x if math.isfinite(x) and x>=0 and (x>0 if positive else True) else None
    except (ValueError,TypeError,OverflowError):
        return None


def col_id(ref:str)->int:
    m=re.match(r"^([A-Z]+)",ref)
    if not m:raise ValueError("XLSX_SCHEMA_HOLD: invalid cell reference")
    n=0
    for char in m.group(1):
        n=26*n+ord(char)-64
    if n<1 or n>200:raise ValueError("XLSX_SCHEMA_HOLD: invalid source column")
    return n-1


def value(cell:ET.Element,shared:list[str]):
    t=cell.attrib.get("t","")
    if t=="s":
        x=cell.find("m:v",NS)
        if x is None or x.text is None:return None
        i=int(x.text)
        if i<0 or i>=len(shared):raise ValueError("XLSX_SCHEMA_HOLD: bad shared string")
        return shared[i]
    if t=="inlineStr":return texts(cell)
    if t=="e":return None
    v=cell.find("m:v",NS)
    if v is None or v.text is None:return None
    return v.text.strip()


def load_sheet(raw:bytes,file_name:str):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(m.file_size for m in z.infolist())>MAX_XLSX_UNCOMPRESSED:
            raise ValueError("XLSX_SCHEMA_HOLD: original workbook unexpectedly expanded")
        shared=shared_strings(z)
        sheets=source_sheets(z)
        if len(sheets)!=1:
            raise ValueError("XLSX_SCHEMA_HOLD: require one original Sheet1")
        _,xmlpath=sheets[0]
        root=get_xml(z,xmlpath)
        data=root.find("m:sheetData",NS)
        if data is None:raise ValueError("XLSX_SCHEMA_HOLD: sheetData missing")
        rows=[]
        for xmlrow in data.findall("m:row",NS):
            record={}
            for cell in xmlrow.findall("m:c",NS):
                ref=cell.attrib.get("r","")
                j=col_id(ref)
                if j in record:raise ValueError("XLSX_SCHEMA_HOLD: duplicate coordinate")
                record[j]=value(cell,shared)
            if record:rows.append(record)
        if not rows:
            raise ValueError("XLSX_SCHEMA_HOLD: empty "+file_name)
        head=[str(rows[0].get(i) or "").strip() for i in range(max(rows[0])+1)]
        if not head or len(head)!=len(set(head)) or any(not k for k in head):
            raise ValueError("XLSX_SCHEMA_HOLD: missing or duplicated header")
        # Preserve true source original cells in temporary memory only.
        data=[{col:row.get(i) for i,col in enumerate(head)} for row in rows[1:]]
        return head,data


def audit():
    meta={"version":"v0.1","status":"SOURCE_JOIN_GEOMETRY_HOLD",
          "contract":"docs/TREEDIVNET_DS1_DS2_ORIGINAL_SOURCE_JOIN_GATE_V0_1.md",
          "original_dataset":"Jensen 2026 Figshare 31026004.v1",
          "original_figure_article_id":31026004,
          "source_readme_checked":False,
          "biological_effect_estimated":False,
          "source_only":True,
          "no_original_plot_or_taxon_identifiers_exported":True,
          "source_file_checksum_pass":False}
    files={name:fetch_file(name) for name in ("README.txt","DS1.xlsx","DS2.xlsx")}
    readme=files["README.txt"].decode("utf-8-sig",errors="replace")
    meta["source_readme_checked"]=True
    meta["readme_mentions_monoculture"]=bool(re.search("monocultur",readme,re.I))
    meta["readme_mentions_literature"]=bool(re.search("literatur|database|missing|imput",readme,re.I))
    headers1,ds1=load_sheet(files["DS1.xlsx"],"DS1.xlsx")
    headers2,ds2=load_sheet(files["DS2.xlsx"],"DS2.xlsx")
    meta["source_file_checksum_pass"]=True
    meta["original_DS1_rows"]=len(ds1)
    meta["original_DS2_rows"]=len(ds2)
    meta["original_DS1_columns"]=headers1
    meta["original_DS2_columns"]=headers2
    if len(ds1)!=363 or len(ds2)!=689 or any(k not in headers1 for k in COMMON) or any(k not in headers2 for k in (*COMMON,"species","biomass_woody",*TR)) or "biomass_woody" not in headers1:
        meta["status"]="SCHEMA_OR_ACCESS_HOLD"
        meta["reason"]="Original 363/689 row or mandatory source schema identities changed"
        return meta

    ids1={}
    ids2=collections.defaultdict(list)
    duplicates_ds1=0
    duplicates_ds2=0
    missing_keys1=0
    missing_keys2=0
    species_seen=set()
    ds2_row_seen=set()
    ds1_site_plots=collections.Counter()
    for row in ds1:
        k=tuple(compact(row[x]) for x in CORE)
        if not all(k):
            missing_keys1+=1
            continue
        if k in ids1:
            duplicates_ds1+=1
        else:
            ids1[k]=row
        ds1_site_plots[k[0]]+=1

    species_row_completeness=collections.Counter()
    trait_presence_rows=collections.Counter()
    trait_invalid_nonempty_rows=collections.Counter()
    for row in ds2:
        k=tuple(compact(row[x]) for x in CORE)
        sp=compact(row["species"])
        if not all(k) or not sp:
            missing_keys2+=1
            continue
        unique=(*k,sp)
        if unique in ds2_row_seen:
            duplicates_ds2+=1
        ds2_row_seen.add(unique)
        ids2[k].append(row)
        species_seen.add(sp)
        for tr in TR:
            raw=row.get(tr)
            if safe_num(raw,positive=True) is not None:
                trait_presence_rows[tr]+=1
            elif raw is not None and str(raw).strip().casefold() not in PLACEHOLDERS:
                trait_invalid_nonempty_rows[tr]+=1

    original_1=set(ids1)
    original_2=set(ids2)
    common=original_1&original_2
    only_1=original_1-original_2
    only_2=original_2-original_1
    data_agreement=collections.Counter()
    biomass_presence=collections.Counter()
    by_trait=collections.defaultdict(list)
    eligible_site=collections.defaultdict(set)
    biomass_site=collections.defaultdict(set)
    at_least_two_any=0
    sameplot_biomass_consistency=[]
    plausible_species_match=0
    site_totals=collections.Counter()
    for k in sorted(common):
        q=ids1[k]
        observed=ids2[k]
        site_totals[k[0]]+=1
        for col in ("treatment","species_richness","species_composition"):
            text1=compact(q.get(col))
            data_agreement[col+"_nonmissing_comparable"]+=int(bool(text1) and all(compact(r.get(col)) for r in observed))
            data_agreement[col+"_matched_exact"]+=int(bool(text1) and all(text1==compact(r.get(col)) for r in observed))
        out=safe_num(q.get("biomass_woody"))
        if out is None:
            if str(q.get("biomass_woody") or "").strip():
                biomass_presence["nonempty_invalid_or_negative"]+=1
            else:
                biomass_presence["blank_or_source_missing"]+=1
        else:
            biomass_presence["nonnegative_numeric"]+=1
            biomass_site[k[0]].add(k)
        species_for_trait=collections.defaultdict(set)
        for r in observed:
            sp=compact(r["species"])
            for tr in TR:
                if safe_num(r.get(tr),positive=True) is not None:
                    species_for_trait[tr].add(sp)
        cnt={name:len(species_for_trait[name]) for name in TR}
        for tr in TR:
            by_trait[tr].append(cnt[tr])
        max_trait=max(cnt.get(tr,0) for tr in ("SLA","WD","LNCM"))
        if max_trait>=2 and out is not None:
            at_least_two_any+=1
            eligible_site[k[0]].add(k)
        n_rich=safe_num(q.get("species_richness"))
        if n_rich is not None and int(n_rich)==len({compact(r["species"]) for r in observed}):
            plausible_species_match+=1
        # This checks data-source identities only, not a fitted biomass outcome;
        # sum species-level woody biomass where *all* component values exist.
        components=[safe_num(r.get("biomass_woody")) for r in observed]
        if out is not None and components and all(x is not None for x in components):
            combined=sum(components)
            sameplot_biomass_consistency.append({
                "abs":abs(combined-out),
                "relative":abs(combined-out)/max(1,abs(out)),
            })

    eligible_species=set()
    for k in eligible_site.values():
        for plot in k:
            for r in ids2[plot]:
                if any(safe_num(r.get(tr),positive=True) is not None
                       for tr in ("SLA","WD","LNCM")):
                    eligible_species.add(compact(r["species"]))

    site_name_counts=dict(sorted(site_totals.items()))
    # Do not export site names from original data as potentially identifying
    # original source plot/site geography; only sorted anonymous site counts.
    meta.update({
        "DS1_unique_site_block_plot":len(ids1),
        "DS2_unique_site_block_plot":len(ids2),
        "DS1_missing_primary_keys":missing_keys1,
        "DS2_missing_primary_keys":missing_keys2,
        "DS1_duplicate_primary_keys":duplicates_ds1,
        "DS2_duplicate_site_block_plot_species_rows":duplicates_ds2,
        "original_distinct_DS2_species_labels":len(species_seen),
        "source_DS1_unique_sites":len({k[0] for k in ids1}),
        "source_DS2_unique_sites":len({k[0] for k in ids2}),
        "source_matched_unique_sites":len(site_name_counts),
        "source_joined_unique_site_block_plot":len(common),
        "source_unmatched_DS1_plot_ids":len(only_1),
        "source_unmatched_DS2_plot_ids":len(only_2),
        "source_matched_site_plot_count_sorted":sorted(site_totals.values()),
        "plot_metadata_agreement":dict(sorted(data_agreement.items())),
        "matched_DS1_biomass_woody_numeric_presence":dict(sorted(biomass_presence.items())),
        "per_species_trait_positive_rows":dict(sorted(trait_presence_rows.items())),
        "per_species_trait_invalid_nonempty_rows":dict(sorted(trait_invalid_nonempty_rows.items())),
        "per_plot_number_species_with_positive_trait":{
          tr:{"n_matched_plots_with_atleast2":sum(x>=2 for x in vals),
              "n_matched_plots_with_atleast1":sum(x>=1 for x in vals),
              "max_per_plot":max(vals) if vals else 0}
          for tr,vals in sorted(by_trait.items())},
        "plots_with_2plus_identical_axis_species_and_valid_DS1_woody_biomass":at_least_two_any,
        "positive_numeric_trait_species_labels_on_eligible_plots":len(eligible_species),
        "number_eligible_sites_with_atleast8_plots":sum(len(v)>=8 for v in eligible_site.values()),
        "eligible_site_plot_count_sorted":sorted(len(v) for v in eligible_site.values()),
        "DS1_species_richness_matches_number_of_DS2_species_rows_on_joined_plots":plausible_species_match,
        "species_woody_biomass_components_all_numeric_plots":len(sameplot_biomass_consistency),
        "species_to_plot_biomass_additivity_within_1pct_count":sum(x["relative"]<=0.01 for x in sameplot_biomass_consistency),
        "original_columns_expose_tree_or_sample_ID_for_trait_lineage":any(
            re.search(r"individual|tree[_ ]?id|sample[_ ]?id|source[_ ]?type|provenance|imput|literature|citation",h,re.I)
            for h in headers2),
        "original_columns_expose_trait_measurement_year":any(
            re.search(r"(^year$|date|trait[_ ]?year|measurement[_ ]?year)",h,re.I)
            for h in headers2),
        "original_columns_expose_biomass_measurement_year":any(
            re.search(r"(^year$|date|biomass[_ ]?year|measurement[_ ]?year)",h,re.I)
            for h in headers1),
    })
    geometry=(
        missing_keys1==0 and missing_keys2==0
        and duplicates_ds1==0 and duplicates_ds2==0
        and len(common)>=N_MIN_PLOTS
        and sum(len(v)>=N_MIN_PER_SITE for v in eligible_site.values())>=N_MIN_SITES
        and len(eligible_species)>=N_MIN_SPECIES
        and at_least_two_any>=N_MIN_PLOTS
        and all(data_agreement[k+"_matched_exact"]==len(common)
                for k in ("treatment","species_richness","species_composition"))
    )
    meta["geometry_gate_thresholds"]={
        "min_source_eligible_plots":N_MIN_PLOTS,
        "min_sites_each_atleast_8":N_MIN_SITES,
        "min_species_original_record_positive_trait":N_MIN_SPECIES,
        "require_original_source_keys_nonmissing_unique":True,
        "require_original_treatment_richness_composition_exact_identity":True,
    }
    meta["geometry_status"]="SOURCE_JOIN_GEOMETRY_PASS" if geometry else "SOURCE_JOIN_GEOMETRY_HOLD"
    provenance=meta["original_columns_expose_tree_or_sample_ID_for_trait_lineage"]
    timing=meta["original_columns_expose_trait_measurement_year"] and meta["original_columns_expose_biomass_measurement_year"]
    meta["trait_measurement_provenance"]="POTENTIALLY_TRACEABLE_REQUIRES_ORIGINAL_RECORD_AUDIT" if provenance else "TRAIT_PROVENANCE_HOLD"
    meta["temporal_alignment"]="POTENTIALLY_TRACEABLE_REQUIRES_ORIGINAL_RECORD_AUDIT" if timing else "TEMPORAL_ALIGNMENT_HOLD"
    meta["study_admissible_for_independent_direct_field_trait_to_biomass_effect"]=bool(geometry and provenance and timing)
    meta["status"]="SOURCE_ONLY_JOIN_AUDITED"
    meta["decision"]="NEW_ECOLOGICAL_MODEL_NOT_AUTHORIZED" if not meta["study_admissible_for_independent_direct_field_trait_to_biomass_effect"] else "ADDITIONAL_MEASUREMENT_PROVENANCE_REVIEW_REQUIRED_BEFORE_ANY_OUTCOME_MODEL"
    meta["nonclaims"]=[
        "Exact plot join does not prove field-measured plot-local individual trait provenance",
        "Published species-level plot traits can be site-specific monoculture-transfer or external imputed values",
        "No observed woody biomass effect, FD association, phylogenetic K or PD prediction tested",
        "Original matched years not inferred from missing date columns",
        "Do not treat already published TreeDivNet diversity/carbon effect as independent replication",
    ]
    return meta


def fixture():
    assert compact("  2.0 ")=="2"
    assert compact("B2")=="B2"
    assert safe_num("-9999")==None and safe_num("0")==0
    assert safe_num("0",positive=True) is None and safe_num("2.4",positive=True)==2.4
    assert col_id("AB22")==27
    return {"status":"TREE_DIVNET_SOURCE_ROW_JOIN_FIXTURE_PASS","checks":5}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture()))
    else:
        if not args.out:p.error("--out required")
        r=audit()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
        print("TREE_DIVNET_SOURCE_ROW_JOIN_RESULT",json.dumps(r,sort_keys=True),flush=True)
