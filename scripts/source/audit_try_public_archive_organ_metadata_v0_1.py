#!/usr/bin/env python3
"""TRY public File Archive catalogue: source-only paired-organ screen.

Downloads are limited to the publicly readable DATASET METADATA page. Do not
access registered/restricted trait files. This program reads only advertised
"Field list", taxonomic coverage and source descriptions; it never opens trait
values or computes phylogenetic K. The existing external validation protocol
remains unchanged.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

EXPECTED_ENTRIES = 122  # public catalogue seen on 2026-10-19; fail closed if it changes
EXPECTED_CANDIDATE_IDS = (10, 17, 113)
SOURCE_URL = "https://www.try-db.org/TryWeb/Data.php"

LEAF_FIELD_RE = re.compile(
    r"\b(?:leaf\s+(?:length|width|area|mass|dry\s+matter)|"
    r"specific\s+leaf\s+area|blade\s+(?:length|width))\b", re.I)
REPRODUCTIVE_FIELD_RE = re.compile(
    r"\b(?:seed|fruit|nutlet|propagule)\s+"
    r"(?:dry\s+)?(?:length|width|diameter|mass|weight)\b", re.I)


def parse_catalogue(raw: bytes):
    soup=BeautifulSoup(raw, "html.parser")
    items=[]
    for table in soup.find_all("table"):
        cells={}
        for tr in table.find_all("tr"):
            td=tr.find_all("td",recursive=False)
            if len(td)!=2:
                continue
            label=" ".join(td[0].stripped_strings).strip().rstrip(":")
            value=" ".join(td[1].stripped_strings).strip()
            if label:
                cells[label]=value
        if not re.fullmatch(r"\d+",cells.get("TRY File Archive ID","")):
            continue
        id_=int(cells["TRY File Archive ID"])
        fields=cells.get("Field list","")
        leaf=bool(LEAF_FIELD_RE.search(fields))
        rep=bool(REPRODUCTIVE_FIELD_RE.search(fields))
        items.append({
            "archive_id":id_,
            "title":cells.get("Title",""),
            "publication_date":cells.get("Publication Date",""),
            "rights_of_use_advertised":cells.get("Rights of use",""),
            "format_advertised":cells.get("Format",""),
            "taxonomic_coverage":cells.get("Taxonomic coverage","")[:500],
            "description":cells.get("Description","")[:1400],
            "field_list":fields[:2600],
            "leaf_size_column_advertised":leaf,
            "seed_or_fruit_size_column_advertised":rep,
            "paired_module_columns_advertised":leaf and rep,
        })
    return items


def classify(candidate):
    n=candidate["archive_id"]
    if n==10:
        return {
            "primary_species_measurement_eligibility": "HOLD",
            "reason":"Advertises plot/community weighted mean rather than primary species-level measurements; 692 plots are not 692 independent species."
        }
    if n==17:
        return {
            "primary_species_measurement_eligibility":"STRUCTURAL_HOLD",
            "reason":"Title advertises 34 herbaceous species; cannot supply 12 families of 20 distinct species (at least 240 species) as a stand-alone source."
        }
    if n==113:
        return {
            "primary_species_measurement_eligibility":"STRUCTURAL_HOLD_FOR_12_FAMILY_REPLICATION",
            "reason":"Direct specimen measurements across 209 Scleria species; taxonomic scope is genus Scleria, family Cyperaceae only. Separate one-family study is possible but not prospective cross-family confirmation.",
            "known_related_public_versions":[
                {"record":"10.5281/zenodo.10533114","version":"v1","catalogue_file_access":"open_older_version"},
                {"record":"10.5281/zenodo.12755860","version":"v2","catalogue_file_access":"restricted_latest_version"}
            ]
        }
    return {"primary_species_measurement_eligibility":"UNKNOWN",
            "reason":"Metadata-only selection: no source independence, original measurement, family support or tree status verified."}


def audit(raw):
    items=parse_catalogue(raw)
    ids=[i["archive_id"] for i in items]
    if len(items)!=EXPECTED_ENTRIES or len(set(ids))!=len(ids):
        raise ValueError(f"Catalogue schema gate HOLD: n={len(items)} unique={len(set(ids))} source_sha256={hashlib.sha256(raw).hexdigest()} ids_first={ids[:12]}; no outcome opened")
    candidates=[x for x in items if x["paired_module_columns_advertised"]]
    candids=tuple(sorted(x["archive_id"] for x in candidates))
    if candids!=EXPECTED_CANDIDATE_IDS:
        raise ValueError("Public field-list screen has drifted; candidate class must be independently re-adjudicated before any outcomes.")
    for x in candidates:
        x["source_gate"]=classify(x)
    return {
        "status":"HOLD_PRE_OUTCOME_ORIGINAL_PRIMARY_SOURCE",
        "catalogue_url":SOURCE_URL,
        "screen_timestamp_date":"2026-10-19",
        "catalogue_sha256":hashlib.sha256(raw).hexdigest(),
        "catalogue_dataset_count":len(items),
        "screen_definition":{
            "leaf_column_regex":LEAF_FIELD_RE.pattern,
            "reproductive_column_regex":REPRODUCTIVE_FIELD_RE.pattern,
            "searches_only_public_field_lists":True,
            "does_not_require_registered_data_access":True,
        },
        "paired_size_candidates":candidates,
        "paired_size_candidate_count":len(candidates),
        "single_archive_candidate_satisfies_frozen_12_family_primary_measurement_contract":False,
        "not_a_complete_global_absence_claim":True,
        "reviewed_dataset_ids":ids,
        "no_numeric_trait_values_read":True,
        "no_K_estimated":True,
        "hard_nonclaims":[
            "A publicly listed dataset is not the same as an independently verified original measurement set.",
            "Multiple archives might eventually be assembled if each passes independent record-level audit; this single-dataset screen cannot rule them out.",
            "Neither the independent cross-family external organ-K test nor the distinct BIEN 201-system study is reopened.",
            "Do not download TRY registration-gated files without authorized access.",
            "Do not access Zenodo latest v2 restricted files by assuming an older open version confers access rights to v2."
        ]
    }


def self_test():
    synthetic=b"""<html><table><tr><td>Title:</td><td>Test</td></tr>
    <tr><td>TRY File Archive ID:</td><td>4</td></tr>
    <tr><td>Field list:</td><td>Species, Leaf width, Fruit length</td></tr></table></html>"""
    items=parse_catalogue(synthetic)
    if len(items)!=1 or items[0]["archive_id"]!=4 or not items[0]["paired_module_columns_advertised"]:
        raise RuntimeError("Source header parsing smoke failed")
    # Do not make naive substring "fruit" or "leaf" in titles qualify fields.
    single=b"""<html><table><tr><td>TRY File Archive ID:</td><td>7</td></tr>
    <tr><td>Title:</td><td>Leaf seed review</td></tr>
    <tr><td>Field list:</td><td>Species, Plot, LAI</td></tr></table></html>"""
    if parse_catalogue(single)[0]["paired_module_columns_advertised"]:
        raise RuntimeError("Title leakage into candidate classifier")
    print("SELF_TEST=PASS")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.html or not a.output:
        p.error("--html and --output required except for --self-test")
    result=audit(a.html.read_bytes())
    a.output.parent.mkdir(exist_ok=True,parents=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TRY_ARCHIVE_SOURCE_ONLY="+json.dumps({
        "status":result["status"],
        "catalogue_dataset_count":result["catalogue_dataset_count"],
        "catalogue_sha256":result["catalogue_sha256"],
        "paired_size_candidate_count":result["paired_size_candidate_count"],
        "candidates":[{
            "archive_id":x["archive_id"],
            "title":x["title"],
            "source_gate":x["source_gate"]["primary_species_measurement_eligibility"]
        } for x in result["paired_size_candidates"]],
        "external_12_family_pass":result["single_archive_candidate_satisfies_frozen_12_family_primary_measurement_contract"]
    },ensure_ascii=False))

if __name__=="__main__":
    main()
