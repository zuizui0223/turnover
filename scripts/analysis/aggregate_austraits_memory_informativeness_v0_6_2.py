#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from collections import Counter,defaultdict,deque
from pathlib import Path

def truth(v): return str(v).strip().lower() in {"true","t","1"}

ap=argparse.ArgumentParser()
ap.add_argument("--systems-map",type=Path,required=True)
ap.add_argument("--geometry-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
ap.add_argument("--core-out",type=Path,required=True)
ap.add_argument("--core-table-out",type=Path,required=True)
a=ap.parse_args()
systems=list(csv.DictReader(a.systems_map.open(newline="",encoding="utf-8")))
geo={}
for p in sorted(a.geometry_dir.glob("G*.json")):
    x=json.loads(p.read_text())
    geo[x["geometry_hash"]]=x
if len(geo)!=1442:
    raise SystemExit(f"incomplete geometry results {len(geo)} != 1442")

rows=[]
for s in systems:
    x=geo.get(s["geometry_hash"])
    if x is None: raise SystemExit(f"missing geometry {s['geometry_hash']}")
    passed=bool(x.get("geometry_temporal_pass",False))
    rows.append({
      "family":s["family"],"trait_name":s["trait_name"],"config_type":s["config_type"],
      "n_input_species":s["n_input_species"],"n_prune":s["n_prune"],"n_bind":s["n_bind"],
      "geometry_hash":s["geometry_hash"],"canonical_family":s["canonical_family"],
      "canonical_trait_name":s["canonical_trait_name"],"geometry_group_size":s["geometry_group_size"],
      "prune_lambda":x.get("temporal_prune_only",{}).get("lambda"),
      "prune_mae":x.get("temporal_prune_only",{}).get("median_absolute_recovery_error"),
      "prune_directional":x.get("temporal_prune_only",{}).get("directional_recovery"),
      "prune_valid_fraction":x.get("temporal_prune_only",{}).get("valid_replicate_fraction"),
      "prune_pass":bool(x.get("temporal_prune_only",{}).get("pass",False)),
      "s3_lambda":x.get("temporal_s3",{}).get("lambda"),
      "s3_mae":x.get("temporal_s3",{}).get("median_absolute_recovery_error"),
      "s3_directional":x.get("temporal_s3",{}).get("directional_recovery"),
      "s3_valid_fraction":x.get("temporal_s3",{}).get("valid_replicate_fraction"),
      "s3_pass":bool(x.get("temporal_s3",{}).get("pass",False)),
      "system_temporal_pass":passed
    })
rows.sort(key=lambda r:(r["family"],r["trait_name"]))
a.table_out.parent.mkdir(parents=True,exist_ok=True)
with a.table_out.open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

passing=[r for r in rows if r["system_temporal_pass"]]
families=sorted({r["family"] for r in passing}); traits=sorted({r["trait_name"] for r in passing})

# Final crossed core: iterative simultaneous family degree >=2 and trait degree >=5.
edge_row={(r["family"],r["trait_name"]):r for r in passing}
edges=set(edge_row); iterations=0
while True:
    iterations+=1
    fd=Counter(f for f,t in edges); td=Counter(t for f,t in edges)
    nxt={(f,t) for f,t in edges if fd[f]>=2 and td[t]>=5}
    if nxt==edges: break
    edges=nxt
core=[edge_row[k] for k in sorted(edges)]
cf=sorted({f for f,t in edges}); ct=sorted({t for f,t in edges})

adj=defaultdict(set)
for f,t in edges:
    fn=("F",f); tn=("T",t); adj[fn].add(tn); adj[tn].add(fn)
connected=False
components=0
seen=set()
for n in adj:
    if n in seen: continue
    components+=1
    q=deque([n]); seen.add(n)
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in seen: seen.add(v); q.append(v)
connected=(components==1 and bool(adj))
gate=len(cf)>=12 and len(ct)>=4 and connected

a.core_table_out.parent.mkdir(parents=True,exist_ok=True)
if core:
    with a.core_table_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(core[0])); w.writeheader(); w.writerows(core)
else:
    a.core_table_out.write_text("")

out={
  "version":"v0.6.2",
  "status":"AUSTRAITS_MEMORY_TEMPORAL_INFORMATIVENESS_COMPLETE",
  "outcome_blind":True,
  "austraits_memory_effects_opened":False,
  "n_candidate_systems":len(rows),
  "n_unique_geometries":len(geo),
  "n_temporal_pass_systems":len(passing),
  "n_pass_families_before_final_core":len(families),
  "n_pass_traits_before_final_core":len(traits),
  "next_gate":"Apply frozen final crossed-core and provenance/model-informativeness gates before real rho."
}
core_result={
  "version":"v0.6.2",
  "status":"AUSTRAITS_MEMORY_CROSSED_CORE_PASS" if gate else "HOLD_AUSTRAITS_MEMORY_CROSSED_CORE",
  "outcome_blind":True,
  "austraits_memory_effects_opened":False,
  "n_input_temporal_pass_systems":len(passing),
  "n_core_systems":len(core),
  "n_core_families":len(cf),
  "n_core_traits":len(ct),
  "core_families":cf,"core_traits":ct,
  "iterations":iterations,"connected":connected,"connected_components":components,
  "minimum_families":12,"minimum_traits":4,"gate_pass":gate,
  "next_gate":"Run provenance-overlap audit and graph-specific lineage-repeatability model-informativeness." if gate else "Stop AusTraits replication before real memory effects."
}
for p,obj in [(a.out,out),(a.core_out,core_result)]:
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps({"informativeness":out,"core":core_result},indent=2,sort_keys=True))
