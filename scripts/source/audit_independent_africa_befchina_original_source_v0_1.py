#!/usr/bin/env python3
"""Original source-only data-grain inspection of two INDEPENDENT forest datasets.

A. Open Zenodo archived Noulekoun 2023 African forests, 276 plots, 207 species
   https://zenodo.org/records/10045492
B. Deng 2025 BEF-China tree diversity and 4-y repeated biomass, 482 plots,
   Figshare https://api.figshare.com/v2/articles/29592203.

NO ecological models. Only official original source metadata and small
SHA/MD5-pinned tabular original files opened on ephemeral GitHub CI runner.
No source row values, individual original tree coordinates or identities exported.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import posixpath
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

ZENODO_ID=10045492
FIGSHARE_ID=29592203
FIGSHARE_DOI_ROOT="10.6084/m9.figshare.29592203"
MAX_FILE=10_000_000
MAX_TOTAL=30_000_000
MAX_META=2_500_000
MAX_UNCOMPRESSED=30_000_000
UA="turnover-independent-FD-BEFChina-Africa-published-source-audit/2026-11-18"
EXPECTED_ZENODO_FILE_MD5={
 "dataall_Noulekoun_GEB.csv":"60fc555c8e2942af432b09d3aeb84d57",
 "Description_abbreviations_Noulekoun.xlsx":"6779d4c95a31e254f33e6c2e421d1f38",
 "R_script_Noulekoun_GEB.r":"f3763db40ac72598e1138a0ce48006f4"
}
EXPECTED_ZENODO_BIOMASS_PLOTS=276
EXPECTED_BEFC_PLOTS=482
XLSX_MAIN="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
XLSX_REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XLSX_PK="http://schemas.openxmlformats.org/package/2006/relationships"


def fetch(url: str, max_bytes:int=MAX_META):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json, text/csv, application/octet-stream, */*"})
    try:
        with urllib.request.urlopen(req,timeout=80) as r:
            body=r.read(max_bytes+1)
            if len(body)>max_bytes:raise ValueError("SOURCE_SIZE_CAP_HOLD")
            status=getattr(r,"status",200)
            return status,body,r.headers.get("Content-Type","")
    except urllib.error.HTTPError as e:
        return int(e.code),b"",""
    except (urllib.error.URLError,TimeoutError,OSError,ValueError) as e:
        return type(e).__name__+"_HOLD",b"",""


def get_json(url):
    status,raw,typ=fetch(url,max_bytes=MAX_META)
    if status!=200:return status,None
    try:
        d=json.loads(raw.decode("utf8"))
        if not isinstance(d,dict):return "JSON_SHAPE_HOLD",None
        return 200,d
    except (ValueError,UnicodeDecodeError):
        return "JSON_PARSE_HOLD",None


def normkey(value):
    return " ".join(str(value or "").strip().casefold().split())


def parse_csv_profile(raw:bytes)->dict:
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text=raw.decode("latin-1")
    reader=csv.DictReader(io.StringIO(text))
    columns=reader.fieldnames or []
    if len(columns)>300 or len(columns)!=len(set(columns)):
        raise ValueError("SOURCE_CSV_SCHEMA_HOLD: column count/duplicates")
    samples=[]
    distinct={x:set() for x in columns
              if any(x.casefold() in opts for opts in (
                ("plot_uniq_id","plot_id","plot","plotid"),
                ("country","site","experiment","forest","forest_type","region","growth","year","inventory_year"),
                ("species","scientific_name","taxon","species_name","genus_species","binomial")
              ))}
    source_nonempty=Counter()
    n=0
    for row in reader:
        n+=1
        if n>300000:raise ValueError("SOURCE_CSV_ROW_LIMIT_HOLD")
        if None in row:raise ValueError("SOURCE_CSV_MALFORMED_ROW_HOLD")
        for k,val in row.items():
            if str(val or "").strip() not in ("","NA","N/A","n/a","NaN","-9999"):source_nonempty[k]+=1
        for k in distinct:
            val=normkey(row.get(k))
            if val and len(distinct[k])<250000:distinct[k].add(val)
    if n==0:raise ValueError("SOURCE_CSV_EMPTY_HOLD")
    grouped=[name for name in columns if name.lower() in ("country","site","experiment","forest","forest_type","region","year","inventory_year","growth")]
    taxa=[name for name in columns if name.lower() in ("species","scientific_name","taxon","species_name","genus_species","binomial")]
    has_species_numerical_measurement=bool(taxa) and any(
        key.lower() in ("sla","leaf_n","wd","wood_density","leaf_nitrogen","trait_value","height","leaf_p","specific_leaf_area")
        for key in columns)
    source_woody_columns=[k for k in columns if re.search(r"(^agb(?:$|[._])|biomass|^woody|wood_mass|prod)",k,re.I)]
    cwm_columns=[k for k in columns if re.search(r"^(cwm|fdis|fd_|functional.disp|sd_fdis)",k,re.I)]
    return {
      "format":"csv",
      "actual_original_source_rows":n,
      "original_source_columns":columns,
      "number_original_source_columns":len(columns),
      "original_source_unique_values_for_categorical_or_identity_fields":{k:len(v) for k,v in distinct.items()},
      "original_source_woody_or_biomass_columns":source_woody_columns,
      "original_source_CWM_or_precomputed_FD_columns":cwm_columns,
      "original_source_explicit_taxon_name_columns":taxa,
      "original_source_per_species_measured_trait_and_species_column_same_row":has_species_numerical_measurement,
      "source_nonempty_row_counts_for_data_columns":dict(source_nonempty),
      "source_rows_values_exported":False
    }


def xml_sheet_aggregate(raw:bytes)->dict:
    """Original xlsx schema only; no original species/tree/plot data values exported."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info=z.infolist()
        if len(info)>800 or sum(x.file_size for x in info)>MAX_UNCOMPRESSED:
            raise ValueError("SOURCE_XLSX_SIZE_CAP_HOLD")
        if any(".." in x.filename or x.filename.startswith("/") for x in info):
            raise ValueError("SOURCE_XLSX_PATH_HOLD")
        names=set(z.namelist())
        if "xl/workbook.xml" not in names or "xl/_rels/workbook.xml.rels" not in names:
            raise ValueError("SOURCE_XLSX_SCHEMA_HOLD")
        ss=[]
        if "xl/sharedStrings.xml" in names:
            q=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for x in q.findall("{"+XLSX_MAIN+"}si"):
                ss.append("".join(t.text or "" for t in x.iter("{"+XLSX_MAIN+"}t")))
            if len(ss)>100000:raise ValueError("SOURCE_XLSX_SHARED_STR_LIMIT_HOLD")
        wb=ET.fromstring(z.read("xl/workbook.xml"))
        rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        lookup={}
        for row in rel.findall("{"+XLSX_PK+"}Relationship"):
            target=row.attrib.get("Target","")
            if target.startswith("/"):
                path=posixpath.normpath(target.lstrip("/"))
            else:path=posixpath.normpath(posixpath.join("xl",target))
            lookup[row.attrib.get("Id","")]=path
        out=[]
        for sheet in wb.findall(".//{"+XLSX_MAIN+"}sheet"):
            title=sheet.attrib.get("name","")
            linkid=sheet.attrib.get("{"+XLSX_REL+"}id","")
            path=lookup.get(linkid)
            if not path or not path.startswith("xl/worksheets/") or path not in names:
                continue
            root=ET.fromstring(z.read(path))
            body=root.find(".//{"+XLSX_MAIN+"}sheetData")
            if body is None:continue
            rows=body.findall("{"+XLSX_MAIN+"}row")
            if len(rows)>300000:raise ValueError("SOURCE_XLSX_ROWS_LIMIT_HOLD")
            headings=[]
            for r in rows[:8]:
                vals=[]
                for cell in r.findall("{"+XLSX_MAIN+"}c")[:200]:
                    typ=cell.attrib.get("t")
                    v=cell.find("{"+XLSX_MAIN+"}v")
                    if typ=="s" and v is not None and v.text is not None:
                        idx=int(v.text);val=ss[idx] if 0<=idx<len(ss) else ""
                    elif typ=="inlineStr":
                        val="".join(t.text or "" for t in cell.iter("{"+XLSX_MAIN+"}t"))
                    else:
                        val="" # not exporting original numerical values
                    vals.append(val.strip()[:100])
                score=sum(bool(re.search(r"plot|site|country|species|spp|taxon|trait|SLA|biomass|AGB|year|tree|dbh|height|nitrogen|richness",x,re.I)) for x in vals)
                if score>=2:headings.append({"source_row_number":r.attrib.get("r"),"n_scientific_key_columns":score,"header_column_names":[x for x in vals if x][:80]})
            out.append({"sheet_name":title,"original_sheet_row_elements":len(rows),
                        "source_only_header_candidates":headings[:3],
                        "source_rows_not_exported":True})
        return {"format":"xlsx","sheets":out,"n_original_sheets":len(out)}


def zenodo():
    out={
        "name":"Noulekoun et al 2023 African forest GEB source",
        "official_public_url":"https://zenodo.org/records/10045492",
        "original_study_doi":"10.1111/geb.13800",
        "original_archived_dryad_doi":"10.5061/dryad.dfn2z3582",
        "expected_public_original_plots_from_article":276,
        "expected_original_species_from_article":207,
        "expected_original_5_countries":5,
        "expected_inventory_period":"2014–2020",
        "metadata_status":"SOURCE_METADATA_ACCESS_HOLD",
        "source_only":True,"ecological_effect_opened":False
    }
    status,record=get_json(f"https://zenodo.org/api/records/{ZENODO_ID}")
    out["official_api_http_status"]=status
    if status!=200 or record is None:
        out["reason"]="Official Zenodo API not available; file/access not inferred"
        return out
    ident=record.get("id")
    if ident is not None and int(ident)!=ZENODO_ID:
        out["reason"]="Zenodo record id mismatch"
        return out
    meta=record.get("metadata") or {}
    out["record_id"]=ident
    out["record_version"]=meta.get("version")
    out["record_DOI"]=meta.get("doi") or record.get("doi")
    out["source_license"]=(meta.get("license") or {}).get("id") if isinstance(meta.get("license"),dict) else meta.get("license")
    files=record.get("files") or []
    if not isinstance(files,list):files=[]
    if len(files)>30:
        out["reason"]="More than 30 source files; manual audit"
        return out
    table=[]
    accessed=[]
    for f in files:
        name=str(f.get("key") or f.get("filename") or "")
        src_checks=f.get("checksum") or ""
        size=f.get("size") or 0
        links=f.get("links") or {}
        file_rec={"filename":name,"advertised_size":size,"source_checksum":src_checks}
        if name in EXPECTED_ZENODO_FILE_MD5:
            url=links.get("content") or links.get("self") or ""
            parsed=urllib.parse.urlparse(url)
            if parsed.scheme=="https" and parsed.hostname=="zenodo.org" and int(size)<=MAX_FILE:
                s,blob,typ=fetch(url,max_bytes=MAX_FILE)
                file_rec["public_original_file_http"]=s
                if s==200:
                    md5=hashlib.md5(blob).hexdigest()
                    file_rec["retrieved_md5"]=md5
                    if md5!=EXPECTED_ZENODO_FILE_MD5[name]:
                        file_rec["original_source_checksum_status"]="CHECKSUM_DRIFT_HOLD"
                    else:
                        file_rec["original_source_checksum_status"]="PASS"
                        accessed.append(name)
                        if name.endswith(".csv"):
                            out["original_primary_plot_CSV_grain"]=parse_csv_profile(blob)
                        elif name.endswith(".xlsx"):
                            out["original_source_variable_description_XLSX_schema"]=xml_sheet_aggregate(blob)
                        else:
                            out["original_author_R_script_available"]=True
                else:file_rec["original_source_checksum_status"]="DATA_ACCESS_HOLD"
            else:
                file_rec["original_source_checksum_status"]="UNTRUSTED_OR_LARGE_LINK_HOLD"
        table.append(file_rec)
    out["original_manifest"]=table
    out["n_original_files_md5_pass"]=len(accessed)
    plot=out.get("original_primary_plot_CSV_grain")
    if not plot:
        out["metadata_status"]="ORIGINAL_SOURCE_FILE_ACCESS_HOLD"
    elif plot["original_source_per_species_measured_trait_and_species_column_same_row"]:
        out["metadata_status"]="ORIGINAL_SPECIES_TRAIT_SOURCE_POSSIBLE_NEEDS_ID_JOIN"
    else:
        out["metadata_status"]="ORIGINAL_SPECIES_TRAIT_GRAIN_HOLD"
        out["reason"]="Source database is published plot-level CWM/FD, biomass and covariates but no original per-plot named species and directly measured trait rows; no independent K→FD→mass derivation from this file."
    return out


def figshare():
    out={
      "name":"Deng et al 2025 BEF-China woody canopy/biomass PNAS source",
      "official_public_url":"https://doi.org/10.6084/m9.figshare.29592203",
      "published_article":"10.1073/pnas.2506750122",
      "original_reported_plots":482,"original_reported_tree_individuals":38088,
      "original_reported_survey_years":[2021,2022,2023,2024],
      "original_reported_independent_experiment_sites":2,
      "original_allometric_WD_source_policy":"constant assumed 0.52 for all tree species",
      "metadata_status":"SOURCE_METADATA_ACCESS_HOLD",
      "source_only":True,"ecological_effect_opened":False
    }
    status,rec=get_json(f"https://api.figshare.com/v2/articles/{FIGSHARE_ID}")
    out["official_figshare_metadata_http"]=status
    if status!=200 or rec is None:
        out["reason"]="Exact public article API not available"
        return out
    found=str(rec.get("doi") or "").lower().strip()
    if rec.get("id")!=FIGSHARE_ID or not re.fullmatch(re.escape(FIGSHARE_DOI_ROOT)+r"(?:\.v[1-9][0-9]*)?",found):
        out["metadata_status"]="SOURCE_IDENTITY_HOLD"
        out["reason"]="Public DOI or article ID differs from article's official source reference"
        out["found_doi"]=found
        return out
    out["original_article_doi"]=found
    out["figshare_article_version"]=rec.get("version")
    out["figshare_original_published_date"]=rec.get("published_date")
    out["figshare_license"]=(rec.get("license") or {}).get("name") if isinstance(rec.get("license"),dict) else None
    files=rec.get("files") or []
    if not isinstance(files,list) or len(files)>100:
        out["metadata_status"]="SOURCE_FILE_MANIFEST_HOLD"
        return out
    out["n_original_article_files"]=len(files)
    table=[]
    accessed=0
    running_bytes=0
    for f in files:
        name=str(f.get("name") or "")
        fid=f.get("id")
        size=f.get("size") or 0
        md5=str(f.get("computed_md5") or f.get("supplied_md5") or "").lower()
        url=str(f.get("download_url") or "")
        info={"name":name,"original_file_id":fid,"advertised_bytes":size,
              "original_advertised_md5":md5 or None}
        if not isinstance(fid,int) or not name:
            info["access_status"]="FILE_METADATA_HOLD"
        elif not (re.fullmatch(r"https://ndownloader\.figshare\.com/files/"+str(fid)+r"(?:[?].*)?",url) or
                  re.fullmatch(r"https://figshare\.com/ndownloader/files/"+str(fid)+r"(?:[?].*)?",url)):
            info["access_status"]="UNTRUSTED_DOWNLOAD_URL_HOLD"
        elif int(size)>MAX_FILE or (running_bytes+int(size))>MAX_TOTAL or len(table)>=70:
            info["access_status"]="LARGE_OR_LIMIT_SKIPPED"
        elif name.lower().endswith((".csv",".tsv",".xlsx")):
            s,blob,mime=fetch(url,max_bytes=MAX_FILE)
            info["http_status"]=s
            if s==200 and len(blob)==int(size) and hashlib.md5(blob).hexdigest()==md5:
                running_bytes+=len(blob)
                info["access_status"]="ORIGINAL_FILE_MD5_PASS"
                accessed+=1
                if name.lower().endswith((".csv",".tsv")):
                    profile=parse_csv_profile(blob) if name.lower().endswith(".csv") else None
                else:profile=xml_sheet_aggregate(blob)
                info["original_source_schema_only"]=profile
            else:
                info["access_status"]="FILE_ACCESS_OR_MD5_HOLD"
        else:info["access_status"]="NON_TABULAR_FILE_NOT_OPENED"
        table.append(info)
    out["original_source_file_manifest"]=table
    out["n_small_tabular_original_files_md5_pass"]=accessed
    out["bytes_original_tabular_read_ephemeral"]=running_bytes
    out["original_tree_traits_present_from_source_schema"]=any(
      any("trait" in h.lower() or "SLA" in h or "leaf_n" in h.lower()
          for sheet in item.get("original_source_schema_only",{}).get("sheets",[])
          for head in sheet.get("source_only_header_candidates",[])
          for h in head.get("header_column_names",[]))
      or bool(item.get("original_source_schema_only",{}).get("original_source_per_species_measured_trait_and_species_column_same_row"))
      for item in table if "original_source_schema_only" in item)
    if accessed==0:
        out["metadata_status"]="SOURCE_FILE_MANIFEST_PASS_BUT_ORIGINAL_SOURCE_ACCESS_HOLD"
    else:
        out["metadata_status"]="SMALL_ORIGINAL_TABULAR_SOURCE_SCHEMA_PASS__TRAIT_OR_STOCK_GRAIN_UNQUALIFIED"
    out["strict_independent_source_site_threshold_pass"]=False
    out["strict_independent_source_site_reason"]="Two original BEF-China experimental sites, not five independent field environments; four repeated years cannot serve as independent sites."
    return out


def selftest():
    a=b"site,plot,agb,cwmsla,fdis\nA,001,10,2,0.8\nB,002,20,3,0.5\n"
    d=parse_csv_profile(a)
    assert d["actual_original_source_rows"]==2
    assert d["original_source_explicit_taxon_name_columns"]==[]
    assert d["original_source_per_species_measured_trait_and_species_column_same_row"] is False
    assert "cwmsla" in d["original_source_CWM_or_precomputed_FD_columns"]
    assert EXPECTED_BEFC_PLOTS==482 and EXPECTED_ZENODO_BIOMASS_PLOTS==276
    return {"status":"INDEPENDENT_ORIGINAL_FOREST_SOURCE_FIXTURE_PASS","checks":5}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(selftest(),sort_keys=True));return
    if not args.out:p.error("--out required")
    audits=[]
    for lab,func in (("Africa_Zenodo",zenodo),("BEFChina_Figshare",figshare)):
        try:
            r=func()
        except Exception as exc:
            r={"name":lab,"metadata_status":"TECHNICAL_HOLD",
               "error_type":type(exc).__name__,
               "error_note":str(exc)[:300],
               "source_only":True,"ecological_effect_opened":False}
        audits.append(r)
        print("INDEPENDENT_ORIGINAL_FOREST_SOURCE_CANDIDATE",
              json.dumps(r,sort_keys=True),flush=True)
    result={
      "version":"v0.1","source_only":True,
      "design":"docs/INDEPENDENT_FOREST_TRAIT_BIOMASS_AFRICA_BEFCHINA_SOURCE_GATE_20261118.md",
      "candidates":audits,"ecological_FD_K_PD_or_biomass_effect_estimated":False,
      "historical_global_BIEN_BIODEPTH_NEON_source_gates_unchanged":True,
      "original_source_file_contents_not_committed":True,
      "direct_same_source_family_specific_K_min_species":240,
      "conclusion":"Metadata/field-grain source screening only. Original tree traits and plot biomass must join exactly and independently before any new model."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf8")
    print("INDEPENDENT_ORIGINAL_FOREST_SOURCE_PREFLIGHT_FINISHED",
          json.dumps({x["name"]:x["metadata_status"] for x in audits},sort_keys=True),flush=True)


if __name__=="__main__":
    main()
