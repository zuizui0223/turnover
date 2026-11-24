#!/usr/bin/env python3
"""Source-only audit of Su et al. 2026 maize cultivar mixing (Zenodo 22655228).

No biological numeric response opened, no fitted effect, no source rows exported.
Cultivar effects cannot be relabeled as between-species FD or phylogenetic K.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import posixpath
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

RECORD_ID = 22655228
DOI = "10.5281/zenodo.22655228"
FILE_NAME = "experimental data.xlsx"
MD5 = "26308df4b66c10527749ccb8bfa50bc9"
API_URL = f"https://zenodo.org/api/records/{RECORD_ID}"
FILE_URL = "https://zenodo.org/records/22655228/files/experimental%20data.xlsx?download=1"
MAX_BYTES = 1_500_000
MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOCREL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKGREL = "http://schemas.openxmlformats.org/package/2006/relationships"
CLASSES = {
    "site": r"\b(site|field|location|region|experiment)\b",
    "plot_or_block": r"\b(plot|block|replicate|rep)\b",
    "cultivar": r"\b(cultivar|variety|genotype|accession|hybrid)\b",
    "mixture_or_monoculture": r"\b(mix(?:ture|ed)?|monoculture|pure.?stand|sown|seeding|treatment)\b",
    "biomass": r"\b(biomass|above.?ground|shoot|dry.?weight)\b",
    "grain_yield": r"\b(grain|yield)\b",
    "root_trait": r"\b(root|depth|rwd|weight.?density)\b",
    "fd_proxy": r"\b(dissimilarity|diversity|dispersion|trait.?distance)\b",
    "CE_SE_NDE": r"\b(complementarity|selection|overyield|net.?diversity|relative.?yield)\b",
    "year": r"\b(year|season|date|harvest)\b",
}

def http_get(url: str, max_bytes: int = MAX_BYTES) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "turnover-source-audit/0.1 (uncredentialed research)",
                      "Accept": "application/octet-stream, application/json;q=0.8, */*;q=0.5"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError("size exceeds bounded source-only audit limit")
        return body

def source_record():
    meta = json.loads(http_get(API_URL, 500_000).decode("utf-8"))
    if int(meta.get("id", -1)) != RECORD_ID:
        raise ValueError("record ID mismatch")
    meta_doi = meta.get("doi") or meta.get("pids", {}).get("doi", {}).get("identifier")
    if meta_doi and str(meta_doi).lower() != DOI.lower():
        raise ValueError("record DOI mismatch")
    files_value = meta.get("files", {})
    entries = files_value.get("entries", {}) if isinstance(files_value, dict) else {}
    if not entries and isinstance(files_value, list):
        entries = {x.get("key", ""): x for x in files_value}
    entry = entries.get(FILE_NAME) or next(
        (x for x in entries.values() if x.get("key") == FILE_NAME), None)
    if not entry:
        raise ValueError("original workbook name not present in official manifest")
    checksum = str(entry.get("checksum", "")).lower().replace("md5:", "")
    if checksum and checksum != MD5:
        raise ValueError("original manifest checksum mismatch")
    links = entry.get("links", {})
    candidates = [links.get("content"), links.get("self"), FILE_URL]
    urls = [x for i, x in enumerate(candidates) if x and x not in candidates[:i]]
    return meta, entry, urls

def read_shared_strings(zf):
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    return ["".join(node.itertext()) for node in root.findall(f"{{{MAIN}}}si")]

def literal_cell_string(cell, shared):
    typ = cell.attrib.get("t")
    if typ == "s":
        v = cell.find(f"{{{MAIN}}}v")
        if v is None or not v.text:
            return ""
        idx = int(v.text)
        return shared[idx] if 0 <= idx < len(shared) else ""
    if typ == "inlineStr":
        node = cell.find(f"{{{MAIN}}}is")
        return "".join(node.itertext()) if node is not None else ""
    if typ == "str":
        v = cell.find(f"{{{MAIN}}}v")
        return v.text or "" if v is not None else ""
    return ""  # NEVER read numeric yield, biomass or CE/SE response values

def inspect_workbook(blob: bytes):
    if not zipfile.is_zipfile(io.BytesIO(blob)):
        raise ValueError("original source is not a valid XLSX zip container")
    report = []
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        if "xl/workbook.xml" not in zf.namelist() or "xl/_rels/workbook.xml.rels" not in zf.namelist():
            raise ValueError("XLSX workbook metadata is missing")
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        relxml = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel = {x.attrib.get("Id"): x.attrib.get("Target", "") for x in relxml.findall(f"{{{PKGREL}}}Relationship")}
        shared = read_shared_strings(zf)
        sheets = wb.find(f"{{{MAIN}}}sheets")
        if sheets is None:
            raise ValueError("no workbook sheet metadata")
        for i, sheet in enumerate(list(sheets)):
            rid = sheet.attrib.get(f"{{{DOCREL}}}id")
            target = rel.get(rid, "")
            if not target:
                raise ValueError("missing worksheet relationship")
            if target.startswith("/"):
                path = target.lstrip("/")
            elif target.startswith("xl/"):
                path = target
            else:
                path = posixpath.normpath(posixpath.join("xl", target))
            if path not in zf.namelist():
                raise ValueError("worksheet missing from XLSX archive")
            root = ET.fromstring(zf.read(path))
            rows = root.findall(f".//{{{MAIN}}}sheetData/{{{MAIN}}}row")
            semantic = set()
            top_rows = rows[:8]
            for row in top_rows:
                for cell in row.findall(f"{{{MAIN}}}c"):
                    value = literal_cell_string(cell, shared).strip().lower()
                    # Header detection only; no raw source text or original row values emitted.
                    if not value or len(value) > 120:
                        continue
                    for cls, pattern in CLASSES.items():
                        if re.search(pattern, value, re.I):
                            semantic.add(cls)
            report.append({
                "worksheet_index": i + 1,
                "worksheet_name": sheet.attrib.get("name", "")[:80],
                "physical_row_elements": len(rows),
                "semantic_header_tags_first_8_rows_only": sorted(semantic),
                "has_original_numeric_cells_unopened": any(
                    cell.attrib.get("t") not in ("s", "inlineStr", "str")
                    for row in top_rows for cell in row.findall(f"{{{MAIN}}}c")
                ),
            })
    return report

def selftest():
    wb = '<workbook xmlns="' + MAIN + '" xmlns:r="' + DOCREL + '"><sheets><sheet name="Synthetic" sheetId="1" r:id="rId1"/></sheets></workbook>'
    rel = '<Relationships xmlns="' + PKGREL + '"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>'
    ss = '<sst xmlns="' + MAIN + '"><si><t>Site</t></si><si><t>Cultivar</t></si><si><t>Plot</t></si><si><t>Biomass</t></si></sst>'
    x = '<worksheet xmlns="' + MAIN + '"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c><c r="D1" t="s"><v>3</v></c></row><row r="2"><c r="D2"><v>123.4</v></c></row></sheetData></worksheet>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for path, content in (("xl/workbook.xml", wb), ("xl/_rels/workbook.xml.rels", rel), ("xl/sharedStrings.xml", ss), ("xl/worksheets/sheet1.xml", x)):
            zf.writestr(path, content)
    got = inspect_workbook(buf.getvalue())
    assert got[0]["physical_row_elements"] == 2
    assert set(("site", "cultivar", "plot_or_block", "biomass")).issubset(
        set(got[0]["semantic_header_tags_first_8_rows_only"])
    )
    assert got[0]["has_original_numeric_cells_unopened"]
    print("SYNTHETIC_SOURCE_HEADER_PARSER_PASS")

def audit():
    out = {
        "dataset_doi": DOI,
        "original_record_id": RECORD_ID,
        "original_file_name": FILE_NAME,
        "expected_original_md5": MD5,
        "study_level": "MAIZE_CULTIVAR_WITHIN_SPECIES_ONLY",
        "published_descriptors_not_verified_original_keys": {
            "field_locations": ["Zhangye, China", "Lishu, China"],
            "treatments": "cultivar monocultures and up to eight-cultivar mixtures",
            "outcomes_in_public_description": "grain yield, aboveground biomass, root traits, relative complementarity and selection",
        },
        "separateness_from_plant_species_evolutionary_memory": "NOT_A_SPECIES_LEVEL_OR_K_REPLICATION",
        "new_ecological_effects_fitted": 0,
        "access_checks": [],
        "source_verdict": "SOURCE_ACCESS_OR_GRAIN_HOLD",
        "never_use_this_source_for": ["species-level functional diversity meta-analysis",
                                      "family phylogenetic K", "plant trait memory mediation"],
    }
    try:
        _, entry, urls = source_record()
        out["original_manifest_checksum_validated"] = True
        out["original_manifest_size_bytes"] = entry.get("size")
        original = None
        for url in urls:
            try:
                data = http_get(url)
                got_md5 = hashlib.md5(data).hexdigest()
                if got_md5 != MD5:
                    raise ValueError("original bytes MD5 mismatch")
                original = data
                out["access_checks"].append({"endpoint": "official_public_record_file", "outcome": "verified_MD5"})
                break
            except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError) as exc:
                out["access_checks"].append({"endpoint": "official_public_record_file", "outcome": type(exc).__name__})
        if original is None:
            out["source_verdict"] = "SOURCE_ACCESS_HOLD"
        else:
            sheets = inspect_workbook(original)
            out["original_workbook_size_bytes"] = len(original)
            out["sheet_metadata_only"] = sheets
            out["source_verdict"] = "SOURCE_BYTES_MD5_PASS_DESIGN_GRAIN_UNVERIFIED"
            out["unverified_requirements"] = [
                "correctly identify original experimental site, plot, block and harvest year in source",
                "differentiate premixing monoculture root traits from plastic postmixing responses",
                "original cultivar assignment and composition at fixed richness",
                "biomass and mono controls in matching site/year/measurement units",
                "definition of original relative vs signed CE/SE (not interchangeable)",
                "at least two site-specific admissible designs and nondegenerate predictors",
            ]
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError, KeyError, json.JSONDecodeError, ET.ParseError, zipfile.BadZipFile) as exc:
        out["access_checks"].append({"endpoint": "official_public_record_metadata", "outcome": type(exc).__name__})
        out["source_verdict"] = "SOURCE_ACCESS_OR_SCHEMA_HOLD"
    out_path = Path("results/maize_cultivar_zenodo22655228_source_gate_20261124_v0_1.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_verdict": out["source_verdict"],
        "verified_md5": out.get("original_workbook_size_bytes") is not None,
        "sheet_count": len(out.get("sheet_metadata_only", [])),
        "outcome_models_fitted": 0,
        "source_artifact": str(out_path),
    }))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--source", action="store_true")
    args = p.parse_args()
    if args.selftest:
        selftest()
    elif args.source:
        audit()
    else:
        p.error("choose --selftest or --source")
