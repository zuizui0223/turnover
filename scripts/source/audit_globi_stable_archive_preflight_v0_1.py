#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"globi_stable_archive_preflight_design_v0_1.json"
ZENODO="https://zenodo.org/api/records"


def get_json(url:str,retries:int=4):
    last=None
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"turnover-globi-archive-preflight/0.1"})
            with urllib.request.urlopen(req,timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last=exc
            time.sleep(1.5*(attempt+1))
    raise RuntimeError(f"GET failed after {retries}: {url}: {type(last).__name__}: {last}")


def resolve_latest(concept_doi:str):
    concept_id=concept_doi.rstrip("/").split(".")[-1]
    first=get_json(f"{ZENODO}/{concept_id}")
    latest_link=(first.get("links") or {}).get("latest")
    if latest_link:
        latest=get_json(latest_link)
        return first,latest,"links.latest"

    q=urllib.parse.quote(f'conceptdoi:"{concept_doi}"')
    search=get_json(f"{ZENODO}?q={q}&sort=mostrecent&size=100")
    hits=((search.get("hits") or {}).get("hits") or [])
    if not hits:
        raise RuntimeError("No Zenodo hits for concept DOI")
    return first,hits[0],"conceptdoi_search"


def file_projection(row:dict)->dict:
    links=row.get("links") or {}
    checksum=row.get("checksum")
    if isinstance(checksum,dict):
        checksum_repr=checksum
    else:
        checksum_repr={"raw":checksum}
    return {
      "id":row.get("id"),
      "key":row.get("key"),
      "size":row.get("size"),
      "checksum":checksum_repr,
      "download":links.get("content") or links.get("self"),
    }


def is_candidate(name:str)->bool:
    x=name.lower()
    return "interaction" in x and any(
        x.endswith(s) for s in (".tsv",".tsv.gz",".csv",".csv.gz",".zip")
    )


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    d=json.loads(DESIGN.read_text())
    first,latest,route=resolve_latest(d["concept_doi"])

    meta=latest.get("metadata") or {}
    files=[file_projection(x) for x in (latest.get("files") or [])]
    candidates=[x for x in files if is_candidate(str(x.get("key") or ""))]

    resource_type=(meta.get("resource_type") or {})
    if isinstance(resource_type,dict):
        resource_type_value=resource_type.get("type")
    else:
        resource_type_value=resource_type

    title=str(meta.get("title") or "")
    gate=d["admission_gate"]

    latest_resolved=latest.get("id") is not None
    dataset_ok=(resource_type_value=="dataset")
    candidate_ok=len(candidates)>=1
    file_ok=all(
      x.get("size") not in (None,0)
      and x.get("checksum") not in (None,{},{'raw':None})
      and bool(x.get("download"))
      for x in candidates
    )
    title_ok=d["expected_title_contains"].lower() in title.lower()

    passed=all([
      latest_resolved,
      dataset_ok,
      candidate_ok,
      file_ok,
      title_ok
    ])
    status="GLOBI_STABLE_ARCHIVE_IDENTITY_PASS" if passed else "HOLD_GLOBI_STABLE_ARCHIVE_IDENTITY"

    out={
      "version":"v0.1",
      "status":status,
      "design":str(DESIGN.relative_to(ROOT)),
      "outcome_blind":True,
      "interaction_rows_opened":False,
      "archive_content_downloaded":False,
      "resolution_route":route,
      "concept_doi":d["concept_doi"],
      "concept_record_id":first.get("id"),
      "latest_record_id":latest.get("id"),
      "latest_record_doi":latest.get("doi"),
      "latest_record_conceptdoi":latest.get("conceptdoi"),
      "title":title,
      "publication_date":meta.get("publication_date"),
      "version":meta.get("version"),
      "resource_type":resource_type_value,
      "record_updated":latest.get("updated"),
      "all_files":files,
      "interaction_file_candidates":candidates,
      "checks":{
        "latest_record_resolved":latest_resolved,
        "title_matches":title_ok,
        "resource_type_dataset":dataset_ok,
        "interaction_file_candidate_present":candidate_ok,
        "candidate_file_metadata_complete":file_ok
      },
      "gate_pass":passed,
      "next_gate":d["next_gate_if_pass"] if passed else d["next_gate_if_hold"]
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
