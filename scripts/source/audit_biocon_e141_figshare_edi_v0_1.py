#!/usr/bin/env python3
"""Outcome-blind original-source preflight for Cedar Creek BioCON E141.

Check official Figshare v3 and EDI EML manifests/column names; do not download
raw biomass, species rows, trait values or fit ecological models.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FIGSHARE_ARTICLE_ID = 26841637
FIGSHARE_VERSION = 3
FIGSHARE_API = f"https://api.figshare.com/v2/articles/{FIGSHARE_ARTICLE_ID}/versions/{FIGSHARE_VERSION}"
EDI_IDS = (301, 302)
ENDPOINTS = (
    "https://pasta.lternet.edu/package/metadata/eml/knb-lter-cdr/{n}/newest",
    "https://api.edirepository.org/package/metadata/eml/knb-lter-cdr/{n}/newest",
)
MAX_METADATA_BYTES = 2_000_000
OUTPUT = Path("results/biocon_e141_figshare_edi_original_source_gate_20261124_v0_1.json")

def get(url: str, max_bytes: int=MAX_METADATA_BYTES) -> bytes:
    request = urllib.request.Request(url, headers={
        "User-Agent": "turnover-biocon-e141-source-audit/0.1",
        "Accept": "application/json, application/xml, text/xml, */*",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        blob = response.read(max_bytes+1)
    if len(blob)>max_bytes:
        raise ValueError("Source metadata exceeds fixed safe size cap")
    return blob

def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]

def nested_text(parent: ET.Element, key: str) -> str:
    for c in parent.iter():
        if local(c.tag) == key:
            return (c.text or "").strip()
    return ""

def parse_eml_metadata(blob: bytes) -> dict:
    root = ET.fromstring(blob)
    # EML metadata only; do not retrieve any dataTable CSV/TSV download URLs.
    pkg = root.attrib.get("packageId","")
    tabs=[]
    for node in root.iter():
        if local(node.tag) != "dataTable":
            continue
        cols=[]
        for c in node.iter():
            if local(c.tag) == "attribute":
                name = nested_text(c,"attributeName")
                if name:
                    cols.append(name[:120])
        if cols or nested_text(node,"entityName"):
            tabs.append({"name":nested_text(node,"entityName")[:160],"source_column_names":cols[:150],
                        "source_column_count":len(cols)})
    return {
        "xml_root": local(root.tag),
        "source_package_id":pkg,
        "original_package_title":nested_text(root,"title")[:180],
        "data_table_schemas":tabs[:40],
        "schema_table_count":len(tabs),
        "metadata_bytes_sha256":hashlib.sha256(blob).hexdigest(),
    }

def synthetic_test() -> None:
    xml = b'<eml packageId="knb-lter-cdr.302.1"><dataset><title>Synthetic</title><dataTable><entityName>test.csv</entityName><attributeList><attribute><attributeName>plot</attributeName></attribute><attribute><attributeName>biomass</attributeName></attribute></attributeList></dataTable></dataset></eml>'
    result=parse_eml_metadata(xml)
    assert result["source_package_id"]=="knb-lter-cdr.302.1"
    assert result["schema_table_count"]==1
    assert result["data_table_schemas"][0]["source_column_names"]==["plot","biomass"]
    print("SYNTHETIC_EML_SCHEMA_PARSER_PASS")

def audit() -> None:
    out={
        "as_of_jst":"2026-11-24",
        "candidate":"Cedar Creek BioCON e141 distinct from Cedar Creek E120",
        "novelty_boundary":"Independent field experiment from E120, but NOT independent replication of previously published BioCON CE/SE results",
        "original_figshare": {
            "article_id":FIGSHARE_ARTICLE_ID,"required_version":FIGSHARE_VERSION,
            "cited_doi":"10.6084/m9.figshare.26841637.v3", "access_state":"UNVERIFIED",
        },
        "original_edi":{},
        "source_design": {
            "experiment_e141_original_field_study_count":1,
            "published_original_main_random_assemblage_plots":296,
            "published_total_plots_with_subexperiments":371,
            "source_species_pool":16,
            "experimental_whole_plot_units":"6 CO2 rings (3 per CO2 treatment)",
            "original_N_subplot_randomization":True,
            "source_coverage_claim":"24 survey years 1998–2021 by published source, not source-year join proof",
            "no_new_independent_meta_study_cohorts_inferred":True,
        },
        "additional_frozen_source_requirements":[
            "Original E141 plot assignment vs E120 identity separate and original treatment tables linked to original plot IDs",
            "Monoculture yield E matched within year, ambient/elevated CO2 and N and ring design without pooling incompatible baselines",
            "Original species-level aboveground mass vs total biomass and original planted rather than observed-only species cover",
            "A truly measured original monoculture or otherwise source-verified baseline trait table (not imputed)",
            "Trait measurement year preceding modeled response, no postmixing plastic traits passed as preplant FD",
            "Whole CO2 ring split-plot assignment honored: 6 rings, never 371 independent CO2 units",
            "Data from prior Nature Communications paper not represented as independent 2026 discovery",
            "No direct plant-family phylogenetic K mediation with only 16 original species"
        ],
        "status":"SOURCE_ACCESS_OR_ORIGINAL_JOIN_HOLD",
        "raw_biomass_rows_opened":False,
        "raw_trait_values_opened":False,
        "original_data_downloads":0,
        "statistical_models_fitted":0,
    }
    try:
        obj=json.loads(get(FIGSHARE_API,600_000).decode("utf-8"))
        if int(obj.get("id",-1)) != FIGSHARE_ARTICLE_ID:
            raise ValueError("Figshare canonical article ID mismatch")
        actual_ver=obj.get("version")
        if int(actual_ver or -1) != FIGSHARE_VERSION:
            raise ValueError("Figshare original required version unavailable; do not silently use latest")
        files=obj.get("files",[])
        if not isinstance(files,list):
            raise ValueError("Figshare file manifest is not list")
        out["original_figshare"].update({
            "access_state":"ORIGINAL_VERSION_METADATA_PASS",
            "title":str(obj.get("title",""))[:180],
            "license":obj.get("license",{}).get("name") if isinstance(obj.get("license"),dict) else None,
            "original_manifest_file_count":len(files),
            "original_files":[{"id":x.get("id"),"name":x.get("name"),"size":x.get("size"),
                "is_link_only":x.get("is_link_only",False),"checksum":x.get("computed_md5") or x.get("supplied_md5")}
                for x in files[:80]],
        })
    except (urllib.error.HTTPError, urllib.error.URLError,ValueError,KeyError,TypeError,TimeoutError) as exc:
        out["original_figshare"]["access_state"]="FIGSHARE_METADATA_HOLD"
        out["original_figshare"]["failure_class"]=type(exc).__name__
    for n in EDI_IDS:
        result={"id":f"knb-lter-cdr.{n}.newest", "access_state":"EDI_METADATA_HOLD"}
        for url in ENDPOINTS:
            try:
                blob=get(url.format(n=n))
                obj=parse_eml_metadata(blob)
                pkg=obj["source_package_id"]
                if pkg and not re.match(rf"^knb-lter-cdr\\.{n}\\.[0-9]+$",pkg):
                    raise ValueError(f"EDI package ID unexpected: {pkg}")
                result.update({"access_state":"EDI_EML_SCHEMA_PASS", **obj})
                break
            except (urllib.error.HTTPError, urllib.error.URLError,ValueError,ET.ParseError,TimeoutError) as exc:
                result.setdefault("attempt_error_classes",[]).append(type(exc).__name__)
        out["original_edi"][str(n)]=result
    if (out["original_figshare"]["access_state"]=="ORIGINAL_VERSION_METADATA_PASS"
        and all(v["access_state"]=="EDI_EML_SCHEMA_PASS" for v in out["original_edi"].values())):
        out["status"]="SOURCE_METADATA_PASS_ORIGINAL_CROSSWALK_AND_TRAITS_HOLD"
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "audit_status":out["status"],
        "figshare_access":out["original_figshare"]["access_state"],
        "figshare_files":out["original_figshare"].get("original_files",[]),
        "edi_schemas":{k:{"access":v["access_state"],"title":v.get("original_package_title"),
            "tables":v.get("data_table_schemas",[]),"errors":v.get("attempt_error_classes",[])}
            for k,v in out["original_edi"].items()},
        "biomass_response_rows_opened":0,
        "models_fitted":0
    },ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--selftest",action="store_true")
    parser.add_argument("--source",action="store_true")
    args=parser.parse_args()
    if args.selftest: synthetic_test()
    elif args.source: audit()
    else: parser.error("choose --selftest or --source")
