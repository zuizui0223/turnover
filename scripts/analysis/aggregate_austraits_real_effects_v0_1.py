#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

def truth(x): return str(x).strip().lower() in {"true","t","1"}

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--core-table",type=Path,required=True)
ap.add_argument("--matched-core",type=Path,required=True)
ap.add_argument("--out-json",type=Path,required=True)
ap.add_argument("--out-csv",type=Path,required=True)
a=ap.parse_args()
for p in [a.out_json,a.out_csv]:p.parent.mkdir(parents=True,exist_ok=True)
core=list(csv.DictReader(a.core_table.open(newline="",encoding="utf-8")))
expected={(r["family"],r["trait_name"]):r for r in core}
matched=set()
if a.matched_core.exists() and a.matched_core.stat().st_size:
    for r in csv.DictReader(a.matched_core.open(newline="",encoding="utf-8")):
        matched.add((r["family"],r["trait_name"]))
rows=[]
seen=set()
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x.get("status")!="AUSTRAITS_REAL_EFFECT_SYSTEM_ESTIMATED": raise SystemExit(f"bad system result {p}")
    k=(x["family"],x["trait_name"])
    if k not in expected: raise SystemExit(f"unexpected system {k}")
    if k in seen: raise SystemExit(f"duplicate system {k}")
    seen.add(k)
    logpass=bool(x.get("log_domain_pass",False))
    if logpass != (k in matched): raise SystemExit(f"log-domain membership mismatch {k}")
    for q in ["S3_rho","prune_only_rho"]:
        if not math.isfinite(float(x[q])): raise SystemExit(f"nonfinite {q} {k}")
    if logpass:
        for q in ["S3_log_rho","prune_log_rho"]:
            if x.get(q) is None or not math.isfinite(float(x[q])): raise SystemExit(f"missing log rho {q} {k}")
    rows.append({
      "system_id":x["system_id"],"family":x["family"],"trait_name":x["trait_name"],"config_type":x["config_type"],
      "S3_rho":x["S3_rho"],"prune_only_rho":x["prune_only_rho"],
      "S3_raw_rho":x["S3_raw_rho"],"prune_raw_rho":x["prune_raw_rho"],
      "log_domain_pass":logpass,
      "S3_log_rho":x.get("S3_log_rho"),"prune_log_rho":x.get("prune_log_rho"),
      "n_species_S3":x["n_species_S3"],"n_species_prune":x["n_species_prune"]
    })
if seen!=set(expected):
    miss=set(expected)-seen;raise SystemExit(f"incomplete real effects: {len(miss)} missing")
rows.sort(key=lambda r:(r["family"],r["trait_name"]))
fields=list(rows[0])
with a.out_csv.open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)
out={
  "version":"v0.1","status":"AUSTRAITS_REAL_EFFECTS_AGGREGATED",
  "austraits_memory_effects_opened":True,
  "n_systems":len(rows),"n_families":len({r["family"] for r in rows}),"n_traits":len({r["trait_name"] for r in rows}),
  "n_matched_log_systems":sum(r["log_domain_pass"] for r in rows),
  "all_primary_effects_finite":True,
  "raw_trait_measurements_persisted":False,"species_states_persisted":False,"species_names_persisted":False
}
a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
