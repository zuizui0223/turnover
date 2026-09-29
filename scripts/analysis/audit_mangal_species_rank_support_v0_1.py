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
DESIGN=ROOT/"data"/"mangal_species_rank_support_design_v0_1.json"
SEM=ROOT/"results"/"mangal_semantic_adjudication_v0_2"/"result.json"
BASE="https://mangal.io/api/v2"


def get_json(endpoint:str, params:dict[str,object], retries:int=4):
    url=BASE+"/"+endpoint+"?"+urllib.parse.urlencode(params)
    last=None
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"turnover-mangal-species-rank/0.1"})
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
    ap.add_argument("--species-dir",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.species_dir.mkdir(parents=True,exist_ok=True)

    d=json.loads(DESIGN.read_text())
    sem=json.loads(SEM.read_text())
    if sem["status"]!="MANGAL_SOURCE_SEMANTICS_PASS":
        raise RuntimeError("semantic prerequisite did not pass")

    candidates={int(x["dataset_id"]):x for x in sem["adjudications"]}

    networks=paginate("network")
    network_to_dataset={}
    geo_counts=Counter()
    for row in networks:
        if row.get("public") is False or not has_geom(row):
            continue
        did=row.get("dataset_id")
        nid=row.get("id")
        if did is None or nid is None or int(did) not in candidates:
            continue
        network_to_dataset[int(nid)]=int(did)
        geo_counts[int(did)]+=1

    nodes=paginate("node")
    seen=defaultdict(lambda:defaultdict(set))
    names=defaultdict(dict)
    rank_counts=defaultdict(Counter)
    missing_name=Counter()
    missing_rank=Counter()

    for row in nodes:
        nid=row.get("network_id")
        if nid is None or int(nid) not in network_to_dataset:
            continue
        if row.get("node_level")!="taxon":
            continue
        did=network_to_dataset[int(nid)]
        tax=row.get("taxonomy") or {}
        rank=tax.get("rank")
        tid=row.get("taxonomy_id")
        if rank is None:
            missing_rank[did]+=1
            continue
        rank_counts[did][str(rank)]+=1
        if str(rank)!="species" or tid is None:
            continue
        name=str(tax.get("name") or "").strip()
        if not name:
            missing_name[did]+=1
            continue
        tid=int(tid)
        seen[did][tid].add(int(nid))
        names[did][tid]=name

    q=d["qualification"]
    rows=[]
    passing=[]
    for did in sorted(candidates):
        species_ids=sorted(seen.get(did,{}))
        repeated=[tid for tid in species_ids if len(seen[did][tid])>=2]
        all_names=sorted({names[did][tid] for tid in species_ids})
        repeated_names=sorted({names[did][tid] for tid in repeated})
        ok=(
            geo_counts[did]>=q["minimum_georeferenced_networks"]
            and len(species_ids)>=q["minimum_unique_species_rank_taxa"]
            and len(repeated)>=q["minimum_repeated_species_rank_taxa"]
        )
        stem=f"dataset_{did}"
        (a.species_dir/f"{stem}_species.txt").write_text("\n".join(all_names)+("\n" if all_names else ""))
        (a.species_dir/f"{stem}_repeated_species.txt").write_text("\n".join(repeated_names)+("\n" if repeated_names else ""))
        row={
          "dataset_id":did,
          "dataset_name":candidates[did]["dataset_name"],
          "interaction_family":candidates[did]["interaction_family"],
          "focal_guild":candidates[did]["focal_guild"],
          "georeferenced_networks":int(geo_counts[did]),
          "unique_species_rank_taxa":len(species_ids),
          "repeated_species_rank_taxa":len(repeated),
          "missing_species_names":int(missing_name[did]),
          "rank_row_counts":dict(rank_counts[did]),
          "species_file":str((a.species_dir/f"{stem}_species.txt").relative_to(a.out.parent.parent)),
          "repeated_species_file":str((a.species_dir/f"{stem}_repeated_species.txt").relative_to(a.out.parent.parent)),
          "species_rank_support_pass":ok
        }
        rows.append(row)
        if ok:
            passing.append(row)

    gate=len(passing)>=q["minimum_qualifying_programmes"]
    status="MANGAL_SPECIES_RANK_SUPPORT_PASS" if gate else "HOLD_MANGAL_SPECIES_RANK_SUPPORT"
    out={
      "version":"v0.1",
      "status":status,
      "design":str(DESIGN.relative_to(ROOT)),
      "outcome_blind":True,
      "endpoints_called":["network","node"],
      "forbidden_endpoints_called":[],
      "interaction_edges_opened":False,
      "interaction_types_opened":False,
      "taxon_names_opened":True,
      "taxonomy_ranks_opened":True,
      "candidate_programmes":len(candidates),
      "qualification":q,
      "programme_support":rows,
      "n_species_rank_support_pass":len(passing),
      "passing_programmes":passing,
      "gate_pass":gate,
      "next_gate":d["next_gate_if_pass"] if gate else d["next_gate_if_hold"],
      "interpretation":(
        "Enough source-semantic programmes retain repeated species-rank taxa to justify a dated-phylogeny coverage audit before edge opening."
        if gate else
        "Species-rank taxonomic resolution is insufficient under the frozen programme-level gate; do not use genus/higher-rank nodes to rescue the result."
      )
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
