#!/usr/bin/env python3
"""Read only original Figshare Excel workbook schema, not original trait/AGB values.

Implements source gate from docs/TREEDIVNET_2026_FIGSHARE_SOURCE_GATE_V0_1.md.
Uses only Python stdlib XLSX ZIP/XML header inspection; no workbook modifications,
no biological outcomes, no original plot/species/data rows exported.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import posixpath
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

EXPECTED={
    "README.txt":{"id":61014400,"bytes":8130,"md5":"8fd3551d0a2b69fb9dca54b7cdbca422"},
    "DS1.xlsx":{"id":61014562,"bytes":103401,"md5":"ab691e410093885d08ad8738cbdedf91"},
    "DS2.xlsx":{"id":61014565,"bytes":92898,"md5":"571e0ef965e28b8b31dd27f971efeff6"},
    "DS3.xlsx":{"id":61014568,"bytes":51698,"md5":"888d7a3d156be451966be3ca34b7892f"},
}
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p":"http://schemas.openxmlformats.org/package/2006/relationships"}
MAX_XLSX_UNCOMPRESSED=25_000_000
KEYWORDS=("plot","site","experiment","species","spp","trait","sla","leaf",
          "biomass","wood","carbon","nitrogen","litter","year","treat","replicat")
UA="turnover-TreedivNet2026-original-source-schema-numeric-outcome-blind/0.1"


def fetch_file(name:str)->bytes:
    meta=EXPECTED[name]
    url="https://ndownloader.figshare.com/files/"+str(meta["id"])
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=105) as resp:
        if resp.status!=200:raise ValueError("SOURCE_ACCESS_HOLD: unexpected status "+name)
        raw=resp.read(meta["bytes"]+1)
    if len(raw)!=meta["bytes"]:
        raise ValueError("SOURCE_DRIFT_HOLD: byte count mismatch "+name)
    if hashlib.md5(raw).hexdigest()!=meta["md5"]:
        raise ValueError("SOURCE_DRIFT_HOLD: original Figshare md5 mismatch "+name)
    return raw


def get_xml(z:zipfile.ZipFile,name:str)->ET.Element:
    if name not in z.namelist():
        raise ValueError("XLSX_SCHEMA_HOLD: missing "+name)
    file=z.getinfo(name)
    if file.file_size>MAX_XLSX_UNCOMPRESSED:
        raise ValueError("XLSX_SCHEMA_HOLD: XML original source unexpectedly huge")
    return ET.fromstring(z.read(name))


def texts(node:ET.Element)->str:
    s="".join((t.text or "") for t in node.findall(".//m:t",NS))
    return " ".join(s.strip().split())


def shared_strings(z:zipfile.ZipFile)->list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=get_xml(z,"xl/sharedStrings.xml")
    values=[texts(si) for si in root.findall("m:si",NS)]
    if len(values)>200_000:raise ValueError("XLSX_SCHEMA_HOLD: huge shared strings")
    return values


def cell_text(cell:ET.Element,shared:list[str])->str:
    k=cell.attrib.get("t")
    if k=="s":
        v=cell.find("m:v",NS)
        if v is None or v.text is None:return ""
        idx=int(v.text)
        if idx<0 or idx>=len(shared):raise ValueError("XLSX_SCHEMA_HOLD: shared string out of range")
        return shared[idx]
    if k in ("inlineStr","str"):
        return texts(cell)
    # Numeric data values are *never* exposed or needed for schema.
    # Return a numeric placeholder so data rows do not leak.
    return "__numeric__" if cell.find("m:v",NS) is not None else ""


def source_sheets(z:zipfile.ZipFile)->list[tuple[str,str]]:
    root=get_xml(z,"xl/workbook.xml")
    rel=get_xml(z,"xl/_rels/workbook.xml.rels")
    mappings={}
    for r in rel.findall("p:Relationship",NS):
        rid=r.attrib.get("Id");target=r.attrib.get("Target","")
        if rid and target:
            canonical=(posixpath.normpath(target.lstrip("/")) if target.startswith("/") else
                       posixpath.normpath(posixpath.join("xl",target)))
            mappings[rid]=canonical
    sheets=[]
    for sheet in root.findall("m:sheets/m:sheet",NS):
        rid=sheet.attrib.get("{"+NS["r"]+"}id")
        sname=sheet.attrib.get("name","")
        if rid is None or rid not in mappings:raise ValueError("XLSX_SCHEMA_HOLD: missing sheet relationship")
        path=mappings[rid]
        if not path.startswith("xl/worksheets/") or ".." in path:
            raise ValueError("XLSX_SCHEMA_HOLD: untrusted workbook sheet path")
        sheets.append((sname,path))
    return sheets


def summarize_sheet(root:ET.Element,name:str,shared:list[str])->dict:
    data=root.find("m:sheetData",NS)
    if data is None:return {"sheet":name,"status":"NO_SOURCE_ROWS"}
    rows=data.findall("m:row",NS)
    n_original_rows=len(rows)
    if n_original_rows>60000:raise ValueError("XLSX_SCHEMA_HOLD: huge number of original sheet rows")
    best=None
    # First dozen rows may include title and units; do not reveal original
    # species, numeric biomass, plot IDs, or source numeric measurements.
    for row in rows[:12]:
        cells=[cell_text(c,shared).strip() for c in row.findall("m:c",NS)]
        labels=[v for v in cells if v and v!="__numeric__"]
        indicators=sum(any(key in v.casefold() for key in KEYWORDS) for v in labels)
        score=(indicators,len(labels),-int(row.attrib.get("r","0")))
        if best is None or score>best[0]:
            best=(score,row.attrib.get("r"),cells,indicators)
    if best is None:return {"sheet":name,"status":"NO_VISIBLE_HEADERS","sheet_rows":n_original_rows}
    _,rid,cells,score=best
    # Expose header names only if >=2 science identifiers, otherwise hold rather
    # than accidentally logging actual source row values (species/plot numbers).
    if score<2:
        return {"sheet":name,"status":"HEADER_UNDETERMINED",
                "original_nonempty_rows":n_original_rows,
                "header_row_candidate":rid,
                "header_keyword_hits":score}
    clean=[v[:80] if v!="__numeric__" else "" for v in cells[:70]]
    return {"sheet":name,"status":"HEADER_CANDIDATE",
            "original_nonempty_rows":n_original_rows,
            "header_row_candidate":rid,
            "header_keyword_hits":score,
            "header_candidate":clean,
            "n_columns_in_header":len(cells),
            "has_exact_site_or_experiment_col":any(("site" in v.casefold() or "experiment" in v.casefold())
                                                  for v in clean),
            "has_exact_plot_col":any("plot" in v.casefold() for v in clean),
            "has_species_col":any("species" in v.casefold() for v in clean),
            "has_woody_biomass_col":any("biomass" in v.casefold() or "agb" in v.casefold()
                                        for v in clean),
            "original_source_rows_not_exported":True}


def audit()->dict:
    result={"version":"v0.1","status":"SCHEMA_ONLY_NOT_ELIGIBILITY_PASS",
            "study":"Jensen et al 2026 TreeDivNet",
            "figshare_doi":"10.6084/m9.figshare.31026004.v1",
            "figshare_article_id":31026004,
            "source_only":True,
            "biological_effect_estimated":False,
            "filename_metadata":[],
            "source_sheets":[]}
    for fname in ("README.txt","DS1.xlsx","DS2.xlsx","DS3.xlsx"):
        raw=fetch_file(fname)
        result["filename_metadata"].append({"filename":fname,"figshare_file_id":EXPECTED[fname]["id"],
                  "verified_md5":hashlib.md5(raw).hexdigest(),"bytes":len(raw),"verified":True})
        if fname.endswith(".txt"):
            content=raw.decode("utf-8-sig",errors="replace")
            matches=[(" ".join(ln.split()))[:185] for ln in content.splitlines()
                     if re.search(r"DS[123]|SLA|biomass|tree\b|woody|trait",ln,re.I)]
            result["readme_source_descriptive_lines"]=matches[:18]
            result["readme_text_verified"]=True
            continue
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            if sum(i.file_size for i in z.infolist())>MAX_XLSX_UNCOMPRESSED or                 any(".." in i.filename or i.filename.startswith("/") for i in z.infolist()):
                raise ValueError("XLSX_SCHEMA_HOLD: expanded original XLSX source invalid")
            shared=shared_strings(z)
            for sname,path in source_sheets(z):
                sh=get_xml(z,path)
                rec=summarize_sheet(sh,sname,shared)
                rec["source_file"]=fname
                result["source_sheets"].append(rec)
    result["original_source_workbooks"]=3
    result["original_file_checksum_identity_pass"]=True
    result["all_original_source_files_accessible_without_auth"]=True
    result["no_original_sp_species_rows_or_biomass_values_exported"]=True
    result["status"]="ORIGINAL_XLSX_SCHEMA_INSPECTED"
    result["next_gate"]="Use exact header/schema, official README, and immutable source files to determine original site×plot×species trait vs plot woody biomass exact join; do not infer ecological effect yet."
    return result


def fixture()->dict:
    assert sum(x["bytes"] for x in EXPECTED.values())==256127
    assert sorted(EXPECTED)==["DS1.xlsx","DS2.xlsx","DS3.xlsx","README.txt"]
    assert cell_text(ET.fromstring('<c xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" t="s"><v>0</v></c>'),["site"])=="site"
    return {"status":"SOURCE_XLSX_SCHEMA_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test: print(json.dumps(fixture()))
    else:
        if not args.out:p.error("--out required")
        result=audit()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("TREEDIVNET_ORIGINAL_XLSX_SCHEMA_ONLY",json.dumps(result,sort_keys=True),flush=True)
