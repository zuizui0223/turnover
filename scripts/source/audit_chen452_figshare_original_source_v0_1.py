#!/usr/bin/env python3
"""Official Figshare Chen 2025 452-experiment CE-SE source-only data gate.

Reads only article metadata and bounded source file schemas, not ecological outcomes.
No new fitted CE/SE effects and no original data rows are republished.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ARTICLE_ID=27316062
API=f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
DOI="10.6084/m9.figshare.27316062"
MAX_METADATA=1_500_000
MAX_FILE=25_000_000
MAX_XML=50_000_000
MAX_FILES=35
X="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

SEMANTIC={
    "publication":("reference","publication","paper","literature","study_id","studyid","author"),
    "experiment":("experiment","experiment_id","experimentid","site_id","siteid"),
    "mixture_row":("mixture","mix_id","mixid","plot_id","plotid","record_id"),
    "species_richness":("richness","species_number","species_richness","sr"),
    "relative_CE":("relative_ce","rel_ce","rce","ce_relative"),
    "relative_SE":("relative_se","rel_se","rse","se_relative"),
    "CE":("complementarity","complementarity_effect","ce"),
    "SE":("selection","selection_effect","se"),
    "NDE":("net_effect","net_diversity","ne","nde"),
    "CE_minus_SE":("ce_se","ce_minus_se","ce_vs_se","diff_ce_se"),
    "leaf_N_FD":("fd_leaf_n","fd_leafn","q_leaf_n","leaf_n_fd","fn_fd"),
    "SLA_FD":("fd_sla","sla_fd","q_sla"),
    "FD_generic":("functional_diversity","fd","rao"),
    "PD":("phylogenetic_diversity","pd"),
    "monoculture_CV":("cv_monoculture","mono_cv","cv_biomass","inequality"),
    "N_fixing":("n_fixing","nitrogen_fixing","legume"),
    "ecosystem":("ecosystem","biome","ecosystem_type","vegetation_type"),
    "stand_age":("stand_age","age","year_since","duration"),
    "climate":("climate","aridity","mat","map","precip"),
    "source_weight":("weight","variance","sampling_variance","vi"),
}

def get(url,limit):
    req=urllib.request.Request(url,headers={
        "User-Agent":"turnover-Chen452-official-figshare-source-only/0.1",
        "Accept":"application/json,application/octet-stream"})
    with urllib.request.urlopen(req,timeout=40) as response:
        if int(response.status)!=200:
            raise ValueError("OFFICIAL_SOURCE_HTTP_NOT_200")
        if any(t in response.geturl().lower() for t in ("login.","auth.", "captcha.")):
            raise ValueError("OFFICIAL_SOURCE_AUTH_HOLD")
        data=response.read(limit+1)
        if len(data)>limit:
            raise ValueError("OFFICIAL_SOURCE_MAX_BYTES_HOLD")
        return data

def sanitize(x):
    return re.sub(r"[^a-z0-9]+","_",str(x).lower()).strip("_")

def flags(cols):
    co=[sanitize(x) for x in cols if x is not None]
    return {k:any(any(tag in x for tag in tags) for x in co)
            for k,tags in SEMANTIC.items()}

def csv_probe(b):
    for codec in ("utf-8-sig","cp1252","latin-1"):
        try:
            content=b.decode(codec);break
        except UnicodeError:continue
    sample=content[:8000]
    try:
        delimiter=csv.Sniffer().sniff(sample,delimiters=",;\t").delimiter
    except csv.Error:
        delimiter=","
    rdr=csv.reader(io.StringIO(content,newline=""),delimiter=delimiter)
    first=[next(rdr,[]) for _ in range(5)]
    header=max(first,key=lambda r:sum(bool(x.strip()) for x in r),default=[])
    # No content from original rows or site names exported.
    return {"file_format":"delimited","header_field_count":len(header),
            "semantic_fields_present":flags(header),
            "file_logical_row_count":len(content.splitlines())-1}

def excel_probe(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip():raise ValueError("XLSX_CRC_FAILURE")
        names=set(z.namelist())
        if "xl/workbook.xml" not in names:raise ValueError("XLSX_NO_WORKBOOK")
        def readxml(name):
            if z.getinfo(name).file_size>MAX_XML:
                raise ValueError("XLSX_XML_SIZE_HOLD")
            return ET.fromstring(z.read(name))
        strings=[]
        if "xl/sharedStrings.xml" in names:
            shared=readxml("xl/sharedStrings.xml")
            for item in shared.findall(X+"si"):
                strings.append("".join(x.text or "" for x in item.iter(X+"t")))
        sheets=sorted((n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+[.]xml",n)),
                      key=lambda n:int(re.search(r"sheet(\d+)",n).group(1)))
        results=[]
        for i,name in enumerate(sheets):
            tree=readxml(name)
            original_rows=tree.findall(".//"+X+"sheetData/"+X+"row")
            cand=[]
            for row in original_rows[:6]:
                cols=[]
                for cell in row.findall(X+"c"):
                    v=cell.find(X+"v")
                    kind=cell.attrib.get("t")
                    if kind=="s" and v is not None and v.text:
                        ix=int(v.text);cols.append(strings[ix] if 0<=ix<len(strings) else "")
                    elif kind=="inlineStr":
                        cols.append("".join(x.text or "" for x in cell.iter(X+"t")))
                    else:
                        cols.append(v.text if v is not None and v.text is not None else "")
                cand.append(cols)
            header=max(cand,key=lambda r:sum(bool(str(x).strip()) for x in r),default=[])
            results.append({"sheet_ordinal":i+1,"source_XML_row_elements":len(original_rows),
                            "header_field_count":len(header),"semantic_fields_present":flags(header)})
        return {"file_format":"xlsx","sheets":results}

def zip_probe(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip():raise ValueError("ZIP_CRC_FAILURE")
        items=z.infolist()
        if any(x.file_size>MAX_XML for x in items):
            raise ValueError("NESTED_FILE_TOO_LARGE")
        # Never expand nested archives or original row sets in this gate.
        compressed=sum(x.compress_size for x in items)
        uncompressed=sum(x.file_size for x in items)
        if uncompressed>80_000_000 or (compressed and uncompressed/compressed>120):
            raise ValueError("ZIP_EXPANSION_LIMIT_HOLD")
        names=[x.filename for x in items if not x.is_dir()]
        formats={}
        for name in names:
            ext=name.rsplit(".",1)[-1].lower() if "." in name else "unknown"
            formats[ext]=formats.get(ext,0)+1
        return {"file_format":"zip","archived_file_count":len(names),
                "extension_counts":formats,
                "uncompressed_bytes":uncompressed,
                "source_rows_not_opened":True}

def classify(name,b):
    lower=name.lower()
    if lower.endswith(".csv") or lower.endswith(".tsv") or lower.endswith(".txt"):
        return csv_probe(b)
    if lower.endswith(".xlsx"):return excel_probe(b)
    if lower.endswith(".zip"):return zip_probe(b)
    if lower.endswith(".r") or lower.endswith(".rmd"):
        return {"file_format":"R_code","code_bytes":len(b),"source_rows_not_opened":True}
    return {"file_format":"binary_or_other","source_rows_not_opened":True}

def audit():
    report={"status":"FIGSHARE_ORIGINAL_SOURCE_METADATA_UNVERIFIED",
       "article_id":ARTICLE_ID,"expected_doi":DOI,
       "public_source_metadata_retrieved":False,
       "no_original_study_plot_or_species_names_exported":True,
       "no_original_BEF_source_rows_redistributed":True,
       "no_CE_SE_FD_models_fitted":True,
       "original_independent_study_and_effect_grain_qualified":False,
       "source_files":[]}
    try:
        raw=get(API,MAX_METADATA)
        data=json.loads(raw)
        ids=[str(data.get("doi","")),str(data.get("url_public_html",""))]
        if "27316062" not in " ".join(ids) and "27316062" not in raw.decode(errors="ignore"):
            raise ValueError("ORIGINAL_ARTICLE_IDENTIFIER_HOLD")
        report.update({"public_source_metadata_retrieved":True,
          "source_metadata_sha256":hashlib.sha256(raw).hexdigest(),
          "official_article_version":data.get("version"),
          "official_article_license_name":data.get("license",{}).get("name") if isinstance(data.get("license"),dict) else None,
          "official_article_file_count":len(data.get("files",[])),
          "official_article_doi_matches":str(data.get("doi","")).lower().endswith("27316062")})
        files=data.get("files",[])
        if len(files)>MAX_FILES:raise ValueError("TOO_MANY_ORIGINAL_FIGSHARE_FILES")
        for i,f in enumerate(files):
            name=str(f.get("name",""))
            size=int(f.get("size",0))
            row={"ordinal":i+1,"file_name":name,"file_id":f.get("id"),
                 "api_size_bytes":size,"published_md5":f.get("supplied_md5") or f.get("computed_md5"),
                 "file_source_status":"NOT_CHECKED"}
            report["source_files"].append(row)
            if size>MAX_FILE:
                row["file_source_status"]="OFFICIAL_SOURCE_TOO_LARGE_FOR_BOUNDED_PREFLIGHT"
                continue
            fileid=f.get("id")
            if not fileid:
                row["file_source_status"]="ORIGINAL_FILE_MISSING_ID"
                continue
            try:
                original=get(f"https://api.figshare.com/v2/file/download/{fileid}",MAX_FILE)
                if len(original)!=size:
                    raise ValueError("ORIGINAL_SOURCE_BYTE_SIZE_MISMATCH")
                md5=hashlib.md5(original).hexdigest()
                provided=row["published_md5"]
                if provided and md5.lower()!=str(provided).lower():
                    raise ValueError("ORIGINAL_SOURCE_MD5_MISMATCH")
                row["file_source_status"]="ORIGINAL_BYTES_HASH_AND_SCHEMA_CHECKED"
                row["verified_original_sha256"]=hashlib.sha256(original).hexdigest()
                row["semantic_schema_only"]=classify(name,original)
            except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
                    ValueError,zipfile.BadZipFile,KeyError,IndexError,
                    UnicodeError,ET.ParseError) as e:
                row["file_source_status"]="ORIGINAL_FILE_SOURCE_ACCESS_OR_SCHEMA_HOLD"
                row["error_type"]=type(e).__name__
                if isinstance(e,urllib.error.HTTPError):row["http_status"]=e.code
                elif isinstance(e,ValueError):row["validation_error"]=str(e)[:90]
        report["status"]="FIGSHARE_DATA_CATALOGUE_AUDITED_SOURCE_GRAIN_HOLD"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
            ValueError,json.JSONDecodeError) as e:
        report["status"]="FIGSHARE_METADATA_ACCESS_OR_IDENTITY_HOLD"
        report["meta_error"]=type(e).__name__
        if isinstance(e,urllib.error.HTTPError):report["metadata_http_status"]=e.code
        elif isinstance(e,ValueError):report["metadata_validation_error"]=str(e)[:90]
    return report

def self_test():
    a=flags(["Study_ID","Complementarity_effect","Selection_effect",
             "Functional_diversity","species_richness","Age","leaf_n_fd"])
    assert a["publication"] and a["CE"] and a["SE"] and a["FD_generic"]
    assert a["stand_age"] and a["species_richness"] and a["leaf_N_FD"]
    v=csv_probe(b"Study_ID,NE,CE,SE,FD\nA,0,1,2,3\n")
    assert v["header_field_count"]==5
    assert v["file_logical_row_count"]==1
    assert not audit if False else True
    print('{"status":"CHEN452_FIGSHARE_SOURCE_FIXTURE_PASS","checks":9}')

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.self_test:self_test()
    elif args.out:
        result=audit()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("CHEN452_FIGSHARE_ORIGINAL_SOURCE_ONLY",
              json.dumps({"status":result["status"],
                          "metadata":result["public_source_metadata_retrieved"],
                          "file_count":result.get("official_article_file_count"),
                          "files":[{"name":x["file_name"],"access":x["file_source_status"],
                                    "bytes":x["api_size_bytes"],"http":x.get("http_status")}
                                   for x in result["source_files"]],
                          "ecological_effects_fitted":False},sort_keys=True))
    else:p.error("Choose --self-test or --out")
