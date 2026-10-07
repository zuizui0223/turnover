#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True);ap.add_argument("--out-csv",type=Path,required=True);ap.add_argument("--out-json",type=Path,required=True)
a=ap.parse_args()
rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x.get("status")!="AUSTRAITS_BLOMBERG_K_SYSTEM_ESTIMATED":raise SystemExit(f"bad K result {p}")
    for k in ["S3_K","prune_K","S3_logK","prune_logK"]:
        if not math.isfinite(float(x[k])):raise SystemExit(f"nonfinite {k}")
    rows.append({k:x[k] for k in ["system_id","family","trait_name","n_species_S3","n_species_prune","S3_K","prune_K","S3_logK","prune_logK"]})
if len(rows)!=254:raise SystemExit(f"expected 254 systems, got {len(rows)}")
if len({r["family"] for r in rows})!=42 or len({r["trait_name"] for r in rows})!=13:raise SystemExit("unexpected K graph")
rows.sort(key=lambda r:(r["family"],r["trait_name"]))
a.out_csv.parent.mkdir(parents=True,exist_ok=True)
with a.out_csv.open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
out={"version":"v0.1","status":"AUSTRAITS_BLOMBERG_K_AGGREGATED","n_systems":254,"n_families":42,"n_traits":13,
     "S3_K_range":[min(float(r["S3_K"]) for r in rows),max(float(r["S3_K"]) for r in rows)],
     "prune_K_range":[min(float(r["prune_K"]) for r in rows),max(float(r["prune_K"]) for r in rows)]}
a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
