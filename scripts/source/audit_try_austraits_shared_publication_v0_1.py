#!/usr/bin/env python3
"""Audit likely shared *publications* across historical TRY and fixed AusTraits sources.

A matching author/year citation is NOT proof of identical primary observations.
No trait values, phylogenetic K, rankings or external validation outcomes.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from pathlib import Path

STATUS="TRY_AUSTRAITS_POSSIBLE_SHARED_PUBLICATIONS_AUDITED"
SOURCE_RE=re.compile(r"^([A-Za-z]+)_((?:19|20)[0-9]{2})(?:_|$)")
TOKENS=re.compile(r"[A-Za-z]+")
YEAR=re.compile(r"(?<![0-9])(?:19|20)[0-9]{2}(?![0-9])")

def match_sources(try_rows, aus_rows, design):
    if design.get("status")!="POST_PUBLIC_METADATA_INSPECTION_PRE_AUTOMATED_AUTHOR_YEAR_AUDIT_FROZEN":
        raise ValueError("nonfrozen shared-publication audit")
    if len(try_rows)<100:raise ValueError("incomplete historical TRY directory")
    if len(aus_rows)<100:raise ValueError("incomplete original AusTraits source metadata")
    ids=[str(t["try_dataset_id"]) for t in try_rows]
    if len(ids)!=len(set(ids)):raise ValueError("duplicate TRY public dataset ID")
    names=[x["austraits_dataset_id"] for x in aus_rows]
    if len(names)!=len(set(names)):raise ValueError("duplicate AusTraits source ID")
    min_letters=int(design["matching_rules"]["surname_min_letters"])
    strong,weak=[],[]
    for a in aus_rows:
        sid=a["austraits_dataset_id"]
        m=SOURCE_RE.match(sid)
        if not m:continue
        surname,year=m.group(1).lower(),m.group(2)
        if len(surname)<min_letters:continue
        for t in try_rows:
            tokens={s.lower() for s in TOKENS.findall(t["try_dataset_title"])}
            if surname not in tokens:continue
            present_years=set(YEAR.findall(t["try_dataset_title"]))
            entry={
              "austraits_source_id":sid,
              "austraits_source_primary_doi":a.get("austraits_primary_doi") or None,
              "try_public_dataset_id":int(t["try_dataset_id"]),
              "try_historical_title":t["try_dataset_title"],
              "try_public_direct_doi_links":t.get("try_source_link_dois") or "",
              "matched_author_token":surname,
              "austraits_source_id_year":year,
              "try_title_years":sorted(present_years),
            }
            if year in present_years:
                entry["interpretation"]="POSSIBLE_SHARED_ORIGINAL_PUBLICATION_NOT_IDENTICAL_RECORDS"
                strong.append(entry)
            else:
                entry["interpretation"]="WEAK_AUTHOR_ONLY_LEXICAL_LEAD"
                weak.append(entry)
    strong=sorted(strong,key=lambda r:(r["austraits_source_id"],r["try_public_dataset_id"]))
    weak=sorted(weak,key=lambda r:(r["austraits_source_id"],r["try_public_dataset_id"]))
    summary={
      "version":"v0.1","status":STATUS,
      "try_catalog_version":"PUBLIC_HISTORICAL_TRY_EXPLORER_V6_NOT_TRY_V7",
      "try_catalog_ids":len(try_rows),"austraits_core_contributing_source_ids":len(aus_rows),
      "strong_author_year_publication_candidates":len(strong),
      "weak_author_only_candidates":len(weak),
      "strong_matches_with_known_austraits_primary_doi":sum(bool(x["austraits_source_primary_doi"]) for x in strong),
      "no_matched_primary_measurement_ids_claimed":True,
      "try_v7_independent_validation_sources_qualified":0,
      "hold":"HOLD_CURRENT_TRY_V7_PRIMARY_MEASUREMENT_IDENTIFIERS_TRAIT_SUPPORT_AND_SEMANTICS",
      "interpretation":"This metadata-only author/year audit can uncover common underlying study citations omitted from public direct-DOI hyperlink comparisons; it cannot test measurement-level duplication or independent replication.",
      "no_source_nonoverlap_conclusion_from_unmatched_titles":True,
    }
    return summary,strong,weak

def rows(path):
    with open(path,encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def write_rows(path,items,columns):
    with open(path,"w",encoding="utf-8",newline="") as f:
        out=csv.DictWriter(f,fieldnames=columns)
        out.writeheader()
        out.writerows(items)

def main():
    p=argparse.ArgumentParser()
    for name in ("try-catalog","austraits-source","design","output-dir"):
        p.add_argument("--"+name,required=True,type=Path)
    args=vars(p.parse_args())
    design=json.loads(args["design"].read_text())
    result,strong,weak=match_sources(
        rows(args["try_catalog"]),rows(args["austraits_source"]),design)
    dest=args["output_dir"]
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    cols=["austraits_source_id","austraits_source_primary_doi","try_public_dataset_id",
          "try_historical_title","try_public_direct_doi_links",
          "matched_author_token","austraits_source_id_year","try_title_years","interpretation"]
    write_rows(dest/"strong_publication_candidates.csv",strong,cols)
    write_rows(dest/"weak_author_only_leads.csv",weak,cols)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
