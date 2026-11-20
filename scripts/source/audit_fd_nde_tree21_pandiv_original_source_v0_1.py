#!/usr/bin/env python3
"""Bounded DOI-qualified ORIGINAL DATA access/headers audit. Never fits ecological effects.

Only official public Dryad API and its public file_download endpoint.
If no anonymous access to original file, stop; no mirrors or authentication bypass.
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

API = "https://datadryad.org/api/v2"
MAX_META = 1_000_000
MAX_FILE = 1_300_000
MAX_XML = 22_000_000
STATS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
SOURCES = {
  "tree21_2025": {
    "doi": "10.5061/dryad.dz08kps9x",
    "expected": [
      ("DS1.xlsx",4410588),("DS2.xlsx",4410589),
      ("DS3.xlsx",4410591),("DS4.xlsx",4410592)
    ],
    "publication": "Jensen et al. 2025 GCB",
  },
  "pandiv2022": {
    "doi": "10.5061/dryad.zs7h44jbp",
    "expected": [
      ("Plot_information.csv",3581957),
      ("Biomass.csv",3581960),
      ("Species_information.csv",3581958),
    ],
    "publication": "Cappelli et al. 2022 Ecological Monographs",
  },
  "pandiv2025": {
    "doi": "10.5061/dryad.1c59zw47k",
    "expected": [("PaNDiv_biomass_2017to2023.txt",4071088)],
    "publication": "Allan and Pichon 2025 Journal of Ecology",
  },
}

def fetch_public(url, maxbytes, kind):
    req=urllib.request.Request(url,headers={
      "User-Agent":"turnover-original-data-source-preflight/0.1 (anonymous DOI source)",
      "Accept":"application/json" if kind=="json" else "application/octet-stream"})
    with urllib.request.urlopen(req,timeout=35) as resp:
        if int(resp.status)!=200: raise ValueError("ORIGINAL_SOURCE_NON_200")
        raw=resp.read(maxbytes+1)
        if len(raw)>maxbytes:raise ValueError("ORIGINAL_SOURCE_EXCEEDS_FROZEN_BYTE_CAP")
        final=resp.geturl().lower()
        if "login" in final or "auth" in final or "anubis" in final:
            raise ValueError("ORIGINAL_SOURCE_AUTH_REDIRECT_HOLD")
        return raw

def simple_api(dataset, maxbytes):
    encoded=urllib.parse.quote("doi:"+dataset["doi"],safe="")
    return fetch_public(f"{API}/datasets/{encoded}",maxbytes,"json")

def xlsx_headers(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        if z.testzip() is not None:raise ValueError("INVALID_SOURCE_ZIP_CRC")
        names=set(z.namelist())
        if "xl/workbook.xml" not in names:raise ValueError("MISSING_ORIGINAL_WORKBOOK")
        def getxml(path):
            info=z.getinfo(path)
            if info.file_size>MAX_XML:raise ValueError("XLSX_XML_TOO_LARGE")
            return ET.fromstring(z.read(path))
        ss=[]
        if "xl/sharedStrings.xml" in names:
            xml=getxml("xl/sharedStrings.xml")
            for el in xml.findall(STATS+"si"):
                ss.append("".join(t.text or "" for t in el.iter(STATS+"t")))
        wb=getxml("xl/workbook.xml")
        titles=[s.attrib.get("name","") for s in wb.findall(".//"+STATS+"sheet")]
        paths=sorted((p for p in names if re.fullmatch("xl/worksheets/sheet[0-9]+[.]xml",p)),
                     key=lambda p:int(re.search("sheet([0-9]+)",p).group(1)))
        sheets=[]
        for i,path in enumerate(paths):
            xml=getxml(path)
            rows=xml.findall(".//"+STATS+"sheetData/"+STATS+"row")
            def parse_row(element):
                cells=[]
                for c in element.findall(STATS+"c"):
                    t=c.attrib.get("t","")
                    v=c.find(STATS+"v")
                    value=""
                    if t=="s" and v is not None and v.text:
                        index=int(v.text)
                        if 0<=index<len(ss):value=ss[index]
                    elif t=="inlineStr":
                        value="".join(t.text or "" for t in c.iter(STATS+"t"))
                    elif v is not None and v.text is not None:
                        value=v.text
                    cells.append(str(value).strip())
                return cells
            first=[parse_row(row) for row in rows[:8]]
            headers=[]
            for row in first:
                if sum(bool(x) for x in row)>len(headers):
                    headers=row
            normal=[re.sub(r"[^a-z0-9]+","_",v.lower()).strip("_") for v in headers]
            sheets.append({
               "sheet_ordinal":i+1,
               "name_class":"metadata" if (titles[i] if i<len(titles) else "").lower()=="metadata" else "other",
               "source_xml_row_elements":len(rows),
               "columns_detected":len(headers),
               "semantic_flags":{
                 "experiment":any("experiment" in x for x in normal),
                 "block":any(x in ("block","bock") for x in normal),
                 "plot":any("plot" in x for x in normal),
                 "richness":any("richness" in x or "species_diversity" in x for x in normal),
                 "FD":any("fdis" in x or "mpd" in x for x in normal),
                 "CWM":any("cwm" in x for x in normal),
                 "stand_productivity":any("stand_productivity" in x for x in normal),
                 "selection":any("selection_effect" in x for x in normal),
                 "complementarity":any("complementarity_effect" in x for x in normal),
                 "NDE":any("net_diversity_effect" in x for x in normal),
                 "species":any(x=="species" for x in normal),
                 "trait_WD":any("wd" in x for x in normal),
                 "trait_LNC":any("lnc" in x for x in normal),
               }
            })
        return sheets

def delimited_header(payload):
    try:
        body=payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        body=payload.decode("latin-1")
    sample=body[:3000]
    try:sep=csv.Sniffer().sniff(sample,delimiters=",;\t").delimiter
    except csv.Error:sep=","
    reader=csv.reader(io.StringIO(body),delimiter=sep)
    first=next(reader,[])
    cols=[re.sub(r"[^a-z0-9]+","_",v.lower()).strip("_") for v in first]
    return {"n_header_fields":len(first),"source_nonblank_rows":sum(1 for r in reader if any(s.strip() for s in r)),
            "semantic_flags":{
              "plot":any("plot" in x for x in cols),
              "harvest_or_year":any("year" in x or "harvest" in x for x in cols),
              "biomass":any("biomass" in x for x in cols),
              "species":any(x=="species" for x in cols),
              "composition":any("composition" in x for x in cols),
              "functional_strategy":any("functional" in x for x in cols),
              "pre_sowing_sla":any("sown" in x and "sla" in x for x in cols),
              "pre_sowing_sla_mpd":any("mpd" in x and "sla" in x for x in cols),
              "nitrogen":any("nitrogen" in x for x in cols),
              "fungicide":any("fungicide" in x for x in cols),
            }}

def try_source(source):
    out={"doi":source["doi"],"publication":source["publication"],
         "published_dataset_source_metadata":False,
         "source_file_bytes_verified":0,
         "access_status":"SOURCE_ACCESS_HOLD",
         "biological_effects_fitted":0,
         "data_rows_redistributed":False,
         "source_data_admission_pass":False,
         "files":[]}
    try:
        raw=simple_api(source,MAX_META)
        meta=json.loads(raw)
        if source["doi"].lower() not in json.dumps(meta).lower():
            raise ValueError("ORIGINAL_DATASET_DOI_IDENTITY_MISMATCH")
        out["published_dataset_source_metadata"]=True
        out["metadata_sha256"]=hashlib.sha256(raw).hexdigest()
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
            ValueError,json.JSONDecodeError) as exc:
        out["dataset_metadata_exception_type"]=type(exc).__name__
        if isinstance(exc,urllib.error.HTTPError):out["dataset_metadata_http"]=exc.code
        elif isinstance(exc,ValueError):out["dataset_validation_error"]=str(exc)[:110]
        return out
    # Probe only one official original file before contacting further files.
    # Auth failures on one Dryad file usually affect all files: don't repeatedly hammer.
    for filename,fileid in source["expected"]:
        f={"expected_filename":filename,"landing_page_file_stream_id":fileid}
        try:
            raw=fetch_public(f"{API}/files/{fileid}/download",MAX_FILE,"file")
            f["sha256"]=hashlib.sha256(raw).hexdigest()
            f["byte_size"]=len(raw)
            if filename.endswith(".xlsx"):
                f["sheets_source_only"]=xlsx_headers(raw)
            else:
                f["source_only_schema"]=delimited_header(raw)
            f["status"]="SOURCE_BYTES_AND_SCHEMA_READ"
            out["source_file_bytes_verified"]+=1
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
                ValueError,zipfile.BadZipFile,KeyError,ET.ParseError) as exc:
            f["status"]="SOURCE_AUTH_OR_SCHEMA_HOLD"
            f["source_exception_type"]=type(exc).__name__
            if isinstance(exc,urllib.error.HTTPError):f["source_http"]=exc.code
            elif isinstance(exc,ValueError):f["source_validation_error"]=str(exc)[:100]
            out["files"].append(f)
            out["access_status"]="SOURCE_ACCESS_OR_SCHEMA_HOLD"
            break
        out["files"].append(f)
    else:
        out["access_status"]="ORIGINAL_SOURCE_HEADERS_AVAILABLE__ROW_JOIN_STILL_UNQUALIFIED"
    return out

def self_test():
    payload=b'Plot,Species,Biomass,Harvest,\\n1,a,3.1,J17\\n2,b,5,A17\\n'
    s=delimited_header(payload)
    assert s["n_header_fields"]>=4
    assert s["source_nonblank_rows"]==2
    assert s["semantic_flags"]["biomass"]
    assert s["semantic_flags"]["plot"]
    assert s["semantic_flags"]["species"]
    assert s["semantic_flags"]["harvest_or_year"]
    assert len(SOURCES)==3 and len(SOURCES["tree21_2025"]["expected"])==4
    print('{"status":"SOURCE_PARSER_SYNTHETIC_PASS","checks":7}')

def main(path):
    x={k:try_source(v) for k,v in SOURCES.items()}
    result={"status":"SOURCE_ONLY_UNVERIFIED_OR_HOLD",
            "freeze":"docs/FD_NDE_ABSOLUTE_YIELD_TREE2025_PANDIV2022_SOURCE_GATE_20261120.md",
            "sources":x,"no_original_data_rows_redistributed":True,
            "no_ecological_coefficients_fitted":True,
            "independent_experiments_confirmed_from_raw_data":False,
            "no_biological_causal_mediation_claim":True}
    assert all(v["biological_effects_fitted"]==0 for v in x.values())
    assert all(not v["source_data_admission_pass"] for v in x.values())
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("FD_NDE_SOURCE_ONLY_AUDIT "+json.dumps({
        "sources":{k:{"status":v["access_status"],
                      "metadata":v["published_dataset_source_metadata"],
                      "file_count":v["source_file_bytes_verified"],
                      "http":v["files"][-1].get("source_http") if v["files"] else v.get("dataset_metadata_http")}
                   for k,v in x.items()},
        "models_fit":0},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    if a.self_test:self_test()
    elif a.out:main(a.out)
    else:ap.error("Choose --self-test or --out")
