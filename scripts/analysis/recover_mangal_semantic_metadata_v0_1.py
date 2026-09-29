#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"mangal_semantic_metadata_design_v0_1.json"
BASE="https://mangal.io/api/v2"


def get_json(url:str,retries:int=4):
    last=None
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"turnover-mangal-semantic-metadata/0.1"})
            with urllib.request.urlopen(req,timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last=exc
            time.sleep(1.5*(attempt+1))
    raise RuntimeError(f"GET failed after {retries}: {url}: {type(last).__name__}: {last}")


def project(row:dict,fields:list[str])->dict:
    return {k:row.get(k) for k in fields}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    d=json.loads(DESIGN.read_text())
    datasets=[]
    references={}
    for did in d["candidate_dataset_ids"]:
        row=get_json(f"{BASE}/dataset/{did}")
        if isinstance(row,list):
            if len(row)!=1:
                raise RuntimeError(f"dataset/{did} returned {len(row)} rows")
            row=row[0]
        p=project(row,d["allowed_dataset_fields"])
        if int(p["id"])!=int(did):
            raise RuntimeError(f"dataset identity mismatch {did} -> {p.get('id')}")
        datasets.append(p)
        rid=p.get("ref_id")
        if rid is not None and str(rid) not in references:
            rr=get_json(f"{BASE}/reference/{rid}")
            if isinstance(rr,list):
                if len(rr)!=1:
                    raise RuntimeError(f"reference/{rid} returned {len(rr)} rows")
                rr=rr[0]
            references[str(rid)]=project(rr,d["allowed_reference_fields"])

    rows=[]
    for ds in datasets:
        rid=ds.get("ref_id")
        ref=references.get(str(rid),{}) if rid is not None else {}
        rows.append({
          "dataset_id":ds.get("id"),
          "dataset_name":ds.get("name"),
          "dataset_date":ds.get("date"),
          "dataset_description":ds.get("description"),
          "ref_id":rid,
          "reference_doi":ref.get("doi"),
          "reference_author":ref.get("author"),
          "reference_year":ref.get("year"),
          "reference_bibtex":ref.get("bibtex"),
          "paper_url":ref.get("paper_url"),
          "data_url":ref.get("data_url")
        })

    out={
      "version":"v0.1",
      "status":"MANGAL_SOURCE_SEMANTIC_METADATA_RECOVERED",
      "design":str(DESIGN.relative_to(ROOT)),
      "outcome_blind":True,
      "endpoints_called":["dataset","reference"],
      "forbidden_endpoints_called":[],
      "interaction_edges_opened":False,
      "interaction_types_opened":False,
      "node_names_opened":False,
      "taxon_names_opened":False,
      "candidate_programmes":len(rows),
      "programme_metadata":rows,
      "adjudication_vocabulary":d["adjudication_vocabulary"],
      "semantic_gate":d["semantic_gate"],
      "semantic_adjudication_completed":False,
      "note":"This file contains source metadata only. Interaction family and focal guild must be adjudicated and frozen in a separate committed result before any edge endpoint is opened."
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
