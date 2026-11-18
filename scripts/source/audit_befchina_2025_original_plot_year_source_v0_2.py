#!/usr/bin/env python3
"""Exact-source BEF-China Deng PNAS 2025 Figshare source-only repeated plot-year
grain check. Never run ecological AGB or trait-biomass effect models.
"""
from __future__ import annotations
import argparse,collections,hashlib,io,json,math,re,urllib.request,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

FIGSHARE_FILES={
 "H1H2":{"id":56354972,"bytes":119953,"md5":"d045623a427b076d529cadb12c025242"},
 "H3":{"id":56354975,"bytes":111578,"md5":"a39eb71df9bf507892213a1d3891bc23"}
}
M="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
UA="turnover-2026-11-18-BEFChina-source-plot-year-id-QA/0.2"


def original_file(which):
    x=FIGSHARE_FILES[which]
    req=urllib.request.Request(f'https://ndownloader.figshare.com/files/{x["id"]}',
      headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=105) as r:
        b=r.read(x["bytes"]+1)
    if len(b)!=x["bytes"] or hashlib.md5(b).hexdigest()!=x["md5"]:
        raise ValueError("SOURCE_HOLD: original official Figshare source byte MD5 drift")
    return b


def col_num(ref):
    m=re.match(r"([A-Z]+)",ref)
    if not m:raise ValueError("SOURCE_XLSX_COLUMN_HOLD")
    k=0
    for c in m.group(1):k=k*26+ord(c)-64
    return k-1


def main_rows(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(i.file_size for i in z.infolist())>8_000_000:raise ValueError("SOURCE_XLSX_ZIP_HOLD")
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            tree=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for item in tree.findall("{"+M+"}si"):
                shared.append("".join(v.text or "" for v in item.iter("{"+M+"}t")))
        sheet="xl/worksheets/sheet1.xml"
        if sheet not in z.namelist():raise ValueError("SOURCE_XLSX_SHEET_HOLD")
        root=ET.fromstring(z.read(sheet))
        xmlrows=root.findall(".//{"+M+"}sheetData/{"+M+"}row")
        def cells(row):
            result={}
            for cell in row.findall("{"+M+"}c"):
                i=col_num(cell.attrib.get("r",""))
                t=cell.attrib.get("t","")
                val=cell.find("{"+M+"}v")
                if t=="s":
                    n=int(val.text) if val is not None and val.text is not None else -1
                    result[i]=shared[n] if 0<=n<len(shared) else ""
                elif t=="inlineStr":
                    result[i]="".join(v.text or "" for v in cell.iter("{"+M+"}t"))
                elif val is not None:result[i]=val.text
                else:result[i]=""
            return result
        head=cells(xmlrows[0])
        labels={i:str(v).strip() for i,v in head.items() if str(v).strip()}
        rows=[{v:cells(row).get(i,"") for i,v in labels.items()} for row in xmlrows[1:]]
        return labels,rows,len(xmlrows)


def val(row,col):
    t=str(row.get(col) or "").strip()
    if not t:return None
    try:
        v=float(t)
        return v if math.isfinite(v) else None
    except (ValueError,TypeError):return None


def qa(which):
    labels,rows,element_count=main_rows(original_file(which))
    expected=(1928 if which=="H1H2" else 1252)
    if element_count!=expected:
        raise ValueError("SOURCE_GRAIN_HOLD: original worksheet source row count changed")
    required={"Plot","year","TREE_R"}
    if which=="H1H2":required|={"AGB"}
    else:required|={"NE","SE","CE"}
    if not required.issubset(labels.values()):
        raise ValueError("SOURCE_SCHEMA_HOLD: original source header structure changed")
    pyear=collections.Counter()
    plotyear=set()
    plots=set()
    years=collections.Counter()
    missing=collections.Counter()
    duplicated=0
    for r in rows:
        key=str(r["Plot"] or "").strip()
        year=val(r,"year")
        if not key or year is None:
            missing["plot_ID_or_year_missing"]+=1
            continue
        if not year.is_integer():missing["noninteger_year"]+=1;continue
        yr=int(year)
        composite=(key,yr)
        if composite in plotyear:duplicated+=1
        plotyear.add(composite)
        plots.add(key)
        years[str(yr)]+=1
        for field in required-{"Plot","year"}:
            if val(r,field) is None:missing["invalid_numeric_"+field]+=1
    return {
      "original_figure_table":which,
      "original_MD5_source":FIGSHARE_FILES[which]["md5"],
      "original_file_id":FIGSHARE_FILES[which]["id"],
      "original_sheet_xml_row_elements":element_count,
      "original_data_rows":len(rows),
      "original_column_names":[labels[k] for k in sorted(labels)],
      "original_unique_plot_ID_count":len(plots),
      "original_unique_plot_year_key_count":len(plotyear),
      "duplicate_original_plot_year_keys":duplicated,
      "original_year_row_counts":dict(sorted(years.items())),
      "invalid_or_missing_key_and_response_numeric_counts":dict(sorted(missing.items())),
      "contains_original_tree_species_identity_column":any(k.casefold() in ("species","scientific_name","taxon","tree_id","species_name") for k in labels.values()),
      "contains_original_leaf_trait_measurement_column":any(re.search(r"(^SLA$|leaf nitrogen|wood density|leaf_n$)",k,re.I) for k in labels.values()),
      "source_biomass_plot_year_model_target_col_available":which=="H1H2",
      "source_rows_or_plot_IDs_exported":False,
    }


def audit():
    a,b=qa("H1H2"),qa("H3")
    out={
      "version":"v0.2",
      "status":"BEFCHINA_PUBLISHED_ORIGINAL_PLOT_YEAR_GRAIN_VERIFIED__DIRECT_SPECIES_TRAIT_SOURCE_HOLD",
      "official_original_Figshare_29592203_version":1,
      "two_original_source_tables":{"H1H2":a,"H3":b},
      "published_original_reported_independent_experiment_sites":2,
      "original_source_tabular_rows_unique_plot_years_confirmed":a["duplicate_original_plot_year_keys"]==0,
      "original_source_species_name_and_direct_leaf_trait_absent":not (a["contains_original_tree_species_identity_column"] or a["contains_original_leaf_trait_measurement_column"] or b["contains_original_tree_species_identity_column"] or b["contains_original_leaf_trait_measurement_column"]),
      "original_source_H1H2_and_H3_year_plot_sets_are_different_targets":True,
      "not_phylogenetic_K_or_original_field_trait_source":True,
      "biological_effects_opened":False,
      "original_raw_binary_not_committed":True,
      "main_scientific_conclusion":"Original article files contain time-repeated plot/year already aggregated AGB/canopy and mixture-source variables; no original tree species identity and leaf trait observational rows; 482 plots over 4 years are not 482 spatially independent ecosystems."
    }
    return out


def fixture():
    assert col_num("A22")==0 and col_num("AB12")==27
    assert val({"year":"2023"},"year")==2023
    assert val({"x":""},"x") is None
    return {"status":"BEFCHINA_PLOT_YEAR_SOURCE_QA_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.out:p.error("--out required")
        res=audit()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("BEFCHINA_2025_ORIGINAL_PLOT_YEAR_SOURCE_GRANULARITY",json.dumps(res,sort_keys=True),flush=True)
