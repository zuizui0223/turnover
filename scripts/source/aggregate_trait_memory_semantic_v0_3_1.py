#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()
files=sorted(a.input_dir.glob("*.csv"))
if not files: raise SystemExit("no semantic partitions")
rows=[]
for p in files:
    with p.open(newline="") as fh:
        rows.extend(csv.DictReader(fh))
rows.sort(key=lambda r:(r["family"],r["trait_name"]))
a.table_out.parent.mkdir(parents=True,exist_ok=True)
fields=list(rows[0])
with a.table_out.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
passing=[r for r in rows if str(r["semantic_pass"]).strip().lower() in {"true","t","1"}]
families=sorted({r["family"] for r in passing})
traits=sorted({r["trait_name"] for r in passing})
gate=len(families)>=12 and len(traits)>=4
result={
  "version":"v0.3.1",
  "status":"TRAIT_MEMORY_SEMANTIC_PASS" if gate else "HOLD_TRAIT_MEMORY_SEMANTIC",
  "queryplan_fallback":"data/trait_memory_semantic_queryplan_fallback_v0_3_1.json",
  "outcome_blind":True,
  "real_trait_values_opened":False,
  "real_memory_effects_opened":False,
  "n_structural_candidates":len(rows),
  "n_semantic_pass":len(passing),
  "n_independent_families":len(families),
  "n_distinct_traits":len(traits),
  "qualifying_families":families,
  "qualifying_traits":traits,
  "gate_pass":gate,
  "next_gate":"Run frozen temporal phylogeny crosswalk." if gate else "Stop temporal follow-up before memory effects."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps(result,indent=2,sort_keys=True))
