#!/usr/bin/env python3
"""Synthetic metadata-only TRY directory parser and strict provenance gates."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_try_austraits_public_catalog_v0_1 import (
    parse_try_catalog, normalized_doi, name_overlap, audit,STATUS)
contract=json.loads((ROOT/"data"/"try_austraits_public_source_registry_design_v0_1.json").read_text())
html="""<html><body>
<table><tr><th>Other</th></tr><tr><td>1</td></tr></table>
<table><tr><th>DatasetID</th><th>Dataset</th><th>Main Custodian</th><th>Institution</th><th>Availability</th></tr>
<tr><td>562</td><td>1000Seedweight</td><td>Custodian A</td><td>University</td><td>public</td></tr>
<tr><td>733</td><td>Proteaceae_traits</td><td>Custodian B</td><td>University</td><td>public</td></tr>
<tr><td>920</td><td>Prof. Chaeho Plant Trait Data</td><td>Custodian C</td><td>University</td><td>restricted 2026-09-04</td></tr>
</table></body></html>"""
items=parse_try_catalog(html)
assert len(items)==3
assert [r["try_dataset_id"] for r in items]==[562,733,920]
assert items[2]["public_explorer_access_status"].startswith("restricted")
assert normalized_doi("https://doi.org/10.1038/s41597-021-01006-6")=="10.1038/s41597-021-01006-6"
assert normalized_doi("NO_DOI") is None
assert name_overlap("Proteaceae_traits","Proteaceae traits")>0.8
aus=[{"austraits_dataset_id":"Proteaceae_traits",
      "austraits_primary_doi":"10.1234/example",
      "source_metadata_status":"READABLE"}]
try:
    audit(items,aus,contract)
except ValueError as e:
    assert "partial TRY" in str(e)
else:
    raise AssertionError("partial catalog accepted")
expanded=[{"try_dataset_id":i+1000,"try_dataset_title":f"metadata public dataset {i}",
           "public_explorer_access_status":"public"} for i in range(105)]
expanded.extend(items)
out,hits=audit(expanded,aus,contract)
assert out["status"]==STATUS
assert out["external_independent_validation_sources_qualified"]==0
assert out["final_status"].startswith("HOLD_")
assert any(h["try_public_directory_dataset_id"]==733 for h in hits)
try:
    parse_try_catalog("<h2>Login required</h2>")
except ValueError as e:
    assert "no DatasetID" in str(e)
else:
    raise AssertionError("empty/login page incorrectly treated as a catalogue")
assert all("trait value" not in str(x).lower() for x in out["hard_boundaries"] if "No TRY" not in x)
print("PASS: public TRY parser, partial index failure, lexical warning only, version firewall")
