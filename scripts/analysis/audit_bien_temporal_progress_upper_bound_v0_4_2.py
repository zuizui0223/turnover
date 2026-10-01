#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--crosswalk",type=Path,required=True)
ap.add_argument("--results-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()

systems=[]
with a.crosswalk.open(newline="") as fh:
    for i,r in enumerate(csv.DictReader(fh),start=1):
        if str(r["crosswalk_pass"]).strip().lower() not in {"true","t","1"}:
            continue
        systems.append({
            "system_id":f"S{len(systems)+1:03d}",
            "family":r["family"],
            "trait_name":r["trait_name"],
        })

by_id={s["system_id"]:s for s in systems}
family_systems={}
for s in systems:
    family_systems.setdefault(s["family"],[]).append(s["system_id"])

completed={}
for p in sorted(a.results_dir.glob("S*.json")):
    x=json.loads(p.read_text())
    sid=x["system_id"]
    if sid not in by_id:
        raise SystemExit(f"unexpected system id {sid}")
    completed[sid]=bool(x.get("system_temporal_pass",False))

pass_families=[]
dead_families=[]
unresolved_families=[]
for fam,ids in sorted(family_systems.items()):
    vals=[completed.get(i) for i in ids]
    if any(v is True for v in vals):
        pass_families.append(fam)
    elif all(v is not None for v in vals):
        dead_families.append(fam)
    else:
        unresolved_families.append(fam)

upper_bound=len(pass_families)+len(unresolved_families)
terminal_impossible=upper_bound<12
out={
  "version":"v0.4.2-progress",
  "n_total_systems":len(systems),
  "n_completed_systems":len(completed),
  "n_total_families":len(family_systems),
  "n_pass_families":len(pass_families),
  "n_dead_families":len(dead_families),
  "n_unresolved_families":len(unresolved_families),
  "pass_families":pass_families,
  "dead_families":dead_families,
  "upper_bound_final_pass_families":upper_bound,
  "minimum_required_families":12,
  "terminal_impossible":terminal_impossible,
  "decision":"TEMPORAL_GATE_MATHEMATICALLY_IMPOSSIBLE" if terminal_impossible else "CONTINUE_TEMPORAL_MATRIX"
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
