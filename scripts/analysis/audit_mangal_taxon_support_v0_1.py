#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"mangal_taxon_support_design_v0_1.json"
PREFLIGHT=ROOT/"results"/"mangal_metadata_preflight_v0_1"/"result.json"
BASE="https://mangal.io/api/v2"


def get_json(endpoint:str, params:dict[str,object], retries:int=4):
    url=BASE+"/"+endpoint+"?"+urllib.parse.urlencode(params)
    last=None
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"turnover-mangal-taxon-support/0.1"})
            with urllib.request.urlopen(req,timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last=exc
            time.sleep(1.5*(attempt+1))
    raise RuntimeError(f"GET failed after {retries}: {url}: {type(last).__name__}: {last}")


def paginate(endpoint:str,count:int=1000,max_pages:int=200)->list[dict]:
    rows=[]
    for page in range(max_pages):
        payload=get_json(endpoint,{"count":count,"page":page})
        if isinstance(payload,dict) and "data" in payload:
            payload=payload["data"]
        if not isinstance(payload,list):
            raise RuntimeError(f"unexpected {endpoint} response: {type(payload).__name__}")
        rows.extend(payload)
        if len(payload)<count:
            return rows
    raise RuntimeError(f"{endpoint} exceeded max_pages={max_pages}")


def has_geom(row:dict)->bool:
    geom=row.get("geom")
    if not geom:
        return False
    return bool(geom.get("coordinates")) if isinstance(geom,dict) else True


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    design=json.loads(DESIGN.read_text())
    pre=json.loads(PREFLIGHT.read_text())
    if pre["status"]!="MANGAL_METADATA_SPATIAL_SUPPORT_PASS":
        raise RuntimeError("metadata prerequisite did not pass")

    qualified={int(x["dataset_id"]):x["dataset_name"] for x in pre["qualifying_dataset_metadata"]}
    network_rows=paginate("network")
    geo_network_to_dataset={}
    dataset_geo_networks=Counter()
    for row in network_rows:
        if row.get("public") is False or not has_geom(row):
            continue
        did=row.get("dataset_id")
        nid=row.get("id")
        if did is None or nid is None or int(did) not in qualified:
            continue
        geo_network_to_dataset[int(nid)]=int(did)
        dataset_geo_networks[int(did)]+=1

    node_rows=paginate("node")
    taxa_by_dataset=defaultdict(set)
    networks_by_taxon=defaultdict(lambda:defaultdict(set))
    taxon_node_rows=0
    taxonomy_id_missing=0
    for row in node_rows:
        nid=row.get("network_id")
        if nid is None or int(nid) not in geo_network_to_dataset:
            continue
        if row.get("node_level")!="taxon":
            continue
        taxon_node_rows+=1
        tid=row.get("taxonomy_id")
        if tid is None:
            taxonomy_id_missing+=1
            continue
        did=geo_network_to_dataset[int(nid)]
        tid=int(tid)
        taxa_by_dataset[did].add(tid)
        networks_by_taxon[did][tid].add(int(nid))

    q=design["qualification"]
    per_dataset=[]
    passing=[]
    for did in sorted(qualified):
        unique=len(taxa_by_dataset.get(did,set()))
        repeated=sum(1 for nets in networks_by_taxon.get(did,{}).values() if len(nets)>=2)
        geo=int(dataset_geo_networks.get(did,0))
        ok=(geo>=q["minimum_georeferenced_networks"] and
            unique>=q["minimum_unique_taxa"] and
            repeated>=q["minimum_repeated_taxa"])
        row={
          "dataset_id":did,
          "dataset_name":qualified[did],
          "georeferenced_networks":geo,
          "unique_taxonomy_ids":unique,
          "repeated_taxonomy_ids":repeated,
          "support_prefilter_pass":ok
        }
        per_dataset.append(row)
        if ok:
            passing.append(row)

    gate=len(passing)>=q["minimum_qualifying_datasets"]
    status="MANGAL_TAXON_SUPPORT_PREFILTER_PASS" if gate else "HOLD_MANGAL_TAXON_SUPPORT"
    out={
      "version":"v0.1",
      "status":status,
      "design":str(DESIGN.relative_to(ROOT)),
      "prerequisite":str(PREFLIGHT.relative_to(ROOT)),
      "outcome_blind":True,
      "endpoints_called":["network","node"],
      "forbidden_endpoints_called":[],
      "node_names_opened":False,
      "taxonomy_names_opened":False,
      "interaction_edges_opened":False,
      "interaction_types_opened":False,
      "trait_values_opened":False,
      "environment_values_opened":False,
      "metadata_qualified_datasets":len(qualified),
      "georeferenced_networks_in_scope":len(geo_network_to_dataset),
      "node_rows_retrieved_total":len(node_rows),
      "taxon_level_node_rows_in_scope":taxon_node_rows,
      "taxon_rows_missing_taxonomy_id":taxonomy_id_missing,
      "qualification":q,
      "dataset_support":per_dataset,
      "n_support_prefilter_pass":len(passing),
      "passing_dataset_metadata":passing,
      "gate_pass":gate,
      "next_gate":design["next_gate_if_pass"] if gate else design["next_gate_if_hold"],
      "interpretation":(
        "Mangal has enough dataset programmes with repeated taxonomy-ID support to justify freezing focal-guild and interaction-type semantics before any edge opening."
        if gate else
        "Mangal lacks enough repeated taxonomic support under the frozen necessary-support gate; do not inspect interaction edges to rescue the route."
      )
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
