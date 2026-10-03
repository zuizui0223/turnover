#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict,deque
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--input",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

rows=[]
with a.input.open(newline="") as fh:
    for r in csv.DictReader(fh):
        if str(r["system_temporal_pass"]).strip().lower() in {"true","t","1"}:
            rows.append(dict(r))
edges={(r["family"],r["trait_name"]) for r in rows}

changed=True
while changed:
    famdeg=defaultdict(int); trdeg=defaultdict(int)
    for f,t in edges:
        famdeg[f]+=1; trdeg[t]+=1
    badf={f for f,d in famdeg.items() if d<2}
    badt={t for t,d in trdeg.items() if d<5}
    new={(f,t) for f,t in edges if f not in badf and t not in badt}
    changed=new!=edges
    edges=new

families=sorted({f for f,t in edges})
traits=sorted({t for f,t in edges})

# Connectedness of the final bipartite graph.
adj=defaultdict(set)
for f,t in edges:
    fn=("F",f); tn=("T",t)
    adj[fn].add(tn); adj[tn].add(fn)
nodes=set(adj)
connected=False
if nodes:
    start=next(iter(nodes)); seen={start}; q=deque([start])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    connected=seen==nodes

selected=[]
keyset=set(edges)
for r in rows:
    if (r["family"],r["trait_name"]) in keyset:
        selected.append(r)

a.table_out.parent.mkdir(parents=True,exist_ok=True)
if selected:
    with a.table_out.open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(selected[0]))
        w.writeheader(); w.writerows(selected)
else:
    a.table_out.write_text("")

gate=len(families)>=12 and len(traits)>=4 and connected
out={
  "version":"v0.6",
  "status":"TRAIT_MEMORY_CROSSED_CORE_PASS" if gate else "HOLD_TRAIT_MEMORY_CROSSED_CORE",
  "outcome_blind":True,
  "real_memory_effects_opened":False,
  "n_input_temporal_pass_systems":len(rows),
  "n_core_systems":len(selected),
  "n_core_families":len(families),
  "n_core_traits":len(traits),
  "core_families":families,
  "core_traits":traits,
  "connected":connected,
  "minimum_families":12,
  "minimum_traits":4,
  "gate_pass":gate,
  "next_gate":"Execute the pre-frozen real temporal memory estimator only for crossed-core systems." if gate else "Stop the variance-partition follow-up before real memory effects."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
