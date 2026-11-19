#!/usr/bin/env python3
"""Source-only Dryad FunDivEUROPE workbook/header audit: never estimate or export biological effects."""
from __future__ import annotations

import argparse
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

DOI = "10.5061/dryad.9ghx3ffpz"
DOI_API = "https://datadryad.org/api/v2/datasets/" + urllib.parse.quote("doi:" + DOI, safe="")
OFFICIAL_PUBLIC_FILE = "https://datadryad.org/downloads/file_stream/2691337"
EXPECTED_NAME = "FunDivEUROPE_alldata_exploratory-platform_2023.xlsx"
XML = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
LIMIT_API = 2_000_000
LIMIT_XLSX = 2_000_000
LIMIT_XML = 18_000_000


def get_public(url: str, cap: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "turnover-original-source-preflight/0.1 (public DOI; no personal credentials)",
                 "Accept": "application/json" if "/api/" in url else "application/octet-stream"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if int(response.status) != 200:
            raise ValueError("SOURCE_HTTP_NOT_200")
        payload = response.read(cap + 1)
    if len(payload) > cap:
        raise ValueError("SOURCE_FILE_SIZE_CAP_EXCEEDED")
    return payload


def xml_element(zf: zipfile.ZipFile, name: str):
    item = zf.getinfo(name)
    if item.file_size > LIMIT_XML:
        raise ValueError("SOURCE_XML_TOO_LARGE")
    return ET.fromstring(zf.read(item))


def row_headers(zf: zipfile.ZipFile):
    files = set(zf.namelist())
    if "xl/workbook.xml" not in files:
        raise ValueError("XLSX_MISSING_WORKBOOK_XML")
    workbook = xml_element(zf, "xl/workbook.xml")
    sheet_titles = [
        e.attrib.get("name", "unnamed")
        for e in workbook.findall(".//" + XML + "sheet")
    ]
    strings = []
    if "xl/sharedStrings.xml" in files:
        shared = xml_element(zf, "xl/sharedStrings.xml")
        for si in shared.findall(XML + "si"):
            strings.append("".join(t.text or "" for t in si.iter(XML + "t")))
    data = []
    sheet_paths = sorted(
        (p for p in files if re.fullmatch(r"xl/worksheets/sheet[0-9]+\.xml", p)),
        key=lambda p: int(re.search(r"sheet([0-9]+)", p).group(1)),
    )
    for i, sheet_path in enumerate(sheet_paths):
        doc = xml_element(zf, sheet_path)
        rows = doc.findall(".//" + XML + "sheetData/" + XML + "row")
        first = rows[0] if rows else None
        header_cells = []
        if first is not None:
            for cell in first.findall(XML + "c"):
                ctype = cell.attrib.get("t", "")
                v = cell.find(XML + "v")
                if ctype == "s" and v is not None and v.text is not None:
                    idx = int(v.text)
                    if 0 <= idx < len(strings):
                        header_cells.append(strings[idx])
                elif ctype == "inlineStr":
                    header_cells.append("".join(t.text or "" for t in cell.iter(XML + "t")))
                elif v is not None and v.text is not None:
                    header_cells.append(v.text)
        data.append({
            "sheet": sheet_titles[i] if i < len(sheet_titles) else sheet_path,
            "source_xml_row_elements": len(rows),
            "original_header_names": header_cells[:250],
            "header_count": len(header_cells),
        })
    return data


def inspect_xlsx(content: bytes):
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        if zf.testzip() is not None:
            raise ValueError("ZIP_CRC_ERROR")
        return row_headers(zf)


def diagnose(sheets):
    # Header patterns are only a negative source-grain screen, never evidence of direct source identity.
    data = next((s for s in sheets if s["sheet"].lower() == "data"), sheets[0] if sheets else None)
    if not data:
        return "ORIGINAL_FILE_SCHEMA_HOLD"
    headers = [re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
               for s in data["original_header_names"]]
    has_species = any(h in ("species", "species_name", "scientific_name", "taxon", "taxon_name", "sp_name")
                      for h in headers)
    has_plot = any(h in ("plot", "plot_id", "plotid", "plot_code") for h in headers)
    has_two_traits = sum(
        any(any(x in h for x in words) for h in headers)
        for words in (("sla", "specific_leaf_area"), ("leaf_n", "nitrogen"))
    ) >= 2
    if not (has_species and has_plot and has_two_traits):
        return "PLOT_AGGREGATE_OR_DIRECT_TRAIT_GRAIN_SOURCE_HOLD"
    return "HEADER_CANDIDATE_BUT_ACTUAL_SPECIES_PLOT_TRAIT_GRAIN_UNVERIFIED_HOLD"


def self_test():
    with io.BytesIO() as binary:
        with zipfile.ZipFile(binary, "w") as z:
            z.writestr("xl/workbook.xml",
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<sheets><sheet name="Data" sheetId="1"/></sheets></workbook>')
            z.writestr("xl/worksheets/sheet1.xml",
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<sheetData><row r="1">'
                '<c r="A1" t="inlineStr"><is><t>plot</t></is></c>'
                '<c r="B1" t="inlineStr"><is><t>tree_biomass</t></is></c>'
                '</row><row r="2"><c r="A2"><v>1</v></c></row></sheetData></worksheet>')
        a = inspect_xlsx(binary.getvalue())
    assert len(a) == 1 and a[0]["source_xml_row_elements"] == 2
    assert a[0]["original_header_names"] == ["plot", "tree_biomass"]
    assert diagnose(a) == "PLOT_AGGREGATE_OR_DIRECT_TRAIT_GRAIN_SOURCE_HOLD"
    print('{"status":"FUNDIVEUROPE_HEADER_FIXTURE_PASS","checks":4}')


def main(path: Path):
    result = {
        "source": "Scherer-Lorenzen et al 2023 FunDivEUROPE",
        "original_dataset_doi": DOI,
        "source_landing_page": "https://doi.org/" + DOI,
        "public_catalogue_expected_file": EXPECTED_NAME,
        "predeclared_thresholds_inherited_from_PR63": {
            "min_unique_plots": 80, "min_independent_forest_groups": 5,
            "min_source_plots_per_group": 8, "min_original_named_species": 30,
            "min_direct_species_per_plot": 2, "min_plot_species_trait_coverage": 0.80,
            "max_original_trait_biomass_date_separation_years": 2,
        },
        "reported_published_descriptors_not_verified_file_data": {
            "n_observational_plots": 209, "n_european_countries": 6,
            "n_paper_target_species_only": 15, "n_paper_inventoried_trees": 12939,
        },
        "status": "SOURCE_ACCESS_HOLD",
        "no_original_species_rows_or_biomass_outcomes_exported": True,
        "no_FD_K_biomass_regression_or_predictive_effect_fitted": True,
        "original_local_species_trait_grain_qualified": False,
        "original_12_family_x_20_species_K_qualified": False,
    }
    try:
        meta_bytes = get_public(DOI_API, LIMIT_API)
        meta = json.loads(meta_bytes)
        if DOI.lower() not in json.dumps(meta).lower():
            raise ValueError("OFFICIAL_DATASET_DOI_IDENTITY_MISMATCH")
        result["official_dryad_dataset_json_sha256"] = hashlib.sha256(meta_bytes).hexdigest()
        result["official_dryad_dataset_DOI_metadata_retrieved"] = True
        file_bytes = get_public(OFFICIAL_PUBLIC_FILE, LIMIT_XLSX)
        result["downloaded_file_byte_size"] = len(file_bytes)
        result["downloaded_file_sha256"] = hashlib.sha256(file_bytes).hexdigest()
        raw_sheets = inspect_xlsx(file_bytes)
        result["status"] = diagnose(raw_sheets)
        # Do not export arbitrary original workbook headers: wide matrices could place
        # site or taxon identities in header names. Emit nonraw semantic flags only.
        result["source_workbook_sheets"] = []
        for i, s in enumerate(raw_sheets):
            h = [re.sub(r"[^a-z0-9]+", "_", x.lower()).strip("_")
                 for x in s["original_header_names"]]
            result["source_workbook_sheets"].append({
                "sheet_ordinal": i + 1,
                "sheet_name_class": (s["sheet"] if s["sheet"] in ("Data", "Metadata") else "Other"),
                "source_xml_row_elements": s["source_xml_row_elements"],
                "header_count": s["header_count"],
                "column_concept_flags": {
                    "source_plot_id": any(x in ("plot", "plotid", "plot_id", "plot_code") for x in h),
                    "source_species_identity": any(x in ("species", "species_name", "scientific_name", "taxon", "taxon_name", "sp_name") for x in h),
                    "source_SLA": any("sla" in x or "specific_leaf_area" in x for x in h),
                    "source_leaf_N": any("leaf_n" in x or "nitrogen" in x for x in h),
                    "biomass": any("biomass" in x or x == "agb" for x in h),
                    "derived_FD": any("fdis" in x or "functional_diversity" in x for x in h),
                    "derived_CWM": any("cwm" in x for x in h),
                },
            })
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            ValueError, KeyError, zipfile.BadZipFile, ET.ParseError,
            json.JSONDecodeError) as exc:
        result["status"] = "SOURCE_ACCESS_OR_SCHEMA_HOLD"
        result["source_audit_error_type"] = type(exc).__name__
        if isinstance(exc, urllib.error.HTTPError):
            result["source_audit_http_status"] = exc.code
        if isinstance(exc, ValueError):
            result["source_audit_validation_error"] = str(exc)[:120]
    assert result["no_FD_K_biomass_regression_or_predictive_effect_fitted"]
    assert result["status"].endswith("HOLD")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("FUNDIVEUROPE_SOURCE_ONLY_VERDICT " + json.dumps({
        "status": result["status"],
        "DOI_metadata": result.get("official_dryad_dataset_DOI_metadata_retrieved", False),
        "workbook_bytes": result.get("downloaded_file_byte_size"),
        "sheet_header_counts": [(x["sheet_name_class"], x["header_count"], x["source_xml_row_elements"])
                                for x in result.get("source_workbook_sheets", [])],
        "error_type": result.get("source_audit_error_type"),
        "http_status": result.get("source_audit_http_status"),
        "biological_effects_opened": False,
    }, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.out:
        main(args.out)
    else:
        parser.error("--self-test or --out is required")
