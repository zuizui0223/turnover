#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--core-table",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()

with a.core_table.open(newline="") as fh:
    core=list(csv.DictReader(fh))
core_map={(r["family"],r["trait_name"]):r for r in core}
core_keys=set(core_map)
rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x["status"]!="TRAIT_MEMORY_REAL_EFFECT_SYSTEM_ESTIMATED":
        raise SystemExit(f"bad system status in {p}")
    k=(x["family"],x["trait_name"])
    if k not in core_keys:
        raise SystemExit(f"effect outside frozen core: {k}")
    cr=core_map[k]
    rows.append({
      "system_id":x["system_id"],
      "family":x["family"],
      "trait_name":x["trait_name"],
      "semantic_class":x["semantic_class"],
      "n_species_S3":x["n_species_S3"],
      "n_species_prune":x["n_species_prune"],
      "S3_rho":x["S3_rho"],
      "prune_only_rho":x["prune_only_rho"],
      "informativeness_n_input_species":cr["n_input_species"],
      "informativeness_n_prune":cr["n_prune"],
      "informativeness_s3_lambda":cr["s3_lambda"]
    })
if len(rows)!=len(core):
    seen={(r["family"],r["trait_name"]) for r in rows}
    missing=sorted(core_keys-seen)
    raise SystemExit(f"incomplete real effects {len(rows)} != {len(core)} missing={missing[:10]}")
rows.sort(key=lambda r:(r["family"],r["trait_name"]))
a.out.parent.mkdir(parents=True,exist_ok=True)
with a.out.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps({
  "status":"TRAIT_MEMORY_REAL_EFFECTS_AGGREGATED",
  "n_systems":len(rows),
  "n_families":len({r["family"] for r in rows}),
  "n_traits":len({r["trait_name"] for r in rows})
},indent=2))
