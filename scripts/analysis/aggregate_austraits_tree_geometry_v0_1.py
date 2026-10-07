#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x.get("status")!="AUSTRAITS_TREE_GEOMETRY_SYSTEM_ESTIMATED":raise SystemExit(f"bad result {p}")
    r={"system_id":x["system_id"],"family":x["family"],"trait_name":x["trait_name"]}
    for axis,key in [("S3","S3"),("prune","prune_only")]:
        m=x[key]
        for k in ["n_tips","polytomy_burden","multifurcating_internal_fraction","pairwise_distance_cv",
                  "pairwise_unique_fraction","max_distance_tie_share","pendant_branch_cv","zero_edge_fraction"]:
            r[f"{axis}_{k}"]=m.get(k)
    rows.append(r)
if len(rows)!=259:raise SystemExit(f"expected 259 geometry rows, got {len(rows)}")
a.out.parent.mkdir(parents=True,exist_ok=True)
with a.out.open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({"status":"AUSTRAITS_TREE_GEOMETRY_AGGREGATED","n_systems":len(rows),
                  "n_families":len({r["family"] for r in rows}),"n_traits":len({r["trait_name"] for r in rows})},indent=2))
