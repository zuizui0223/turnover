#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--crosswalk",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

rows=[]
with a.crosswalk.open(newline="") as fh:
    for r in csv.DictReader(fh):
        if str(r["crosswalk_pass"]).strip().lower() in {"true","t","1"}:
            rows.append(dict(r))

edge_rows={(r["family"],r["trait_name"]):r for r in rows}
edges=set(edge_rows)
changed=True
iterations=0
while changed:
    iterations+=1
    famdeg=defaultdict(int); trdeg=defaultdict(int)
    for f,t in edges:
        famdeg[f]+=1; trdeg[t]+=1
    badf={f for f,d in famdeg.items() if d<2}
    badt={t for t,d in trdeg.items() if d<5}
    new={(f,t) for f,t in edges if f not in badf and t not in badt}
    changed=new!=edges
    edges=new

selected=[edge_rows[k] for k in sorted(edges)]
families=sorted({f for f,t in edges})
traits=sorted({t for f,t in edges})

a.table_out.parent.mkdir(parents=True,exist_ok=True)
if selected:
    fields=list(selected[0])
    with a.table_out.open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(selected)
else:
    a.table_out.write_text("")

out={
  "version":"v0.5.1",
  "status":"TRAIT_MEMORY_PRE_INFORMATIVENESS_CORE_READY" if selected else "HOLD_TRAIT_MEMORY_PRE_INFORMATIVENESS_CORE",
  "outcome_blind":True,
  "real_memory_effects_opened":False,
  "n_crosswalk_pass_systems":len(rows),
  "n_simulation_candidate_systems":len(selected),
  "n_candidate_families":len(families),
  "n_candidate_traits":len(traits),
  "candidate_families":families,
  "candidate_traits":traits,
  "iterations":iterations,
  "minimum_family_degree":2,
  "minimum_trait_degree":5,
  "gate_pass":len(families)>=12 and len(traits)>=4,
  "next_gate":"Run inherited temporal informativeness on these necessary-core systems only." if selected else "Stop before memory effects."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
