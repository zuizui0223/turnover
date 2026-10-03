#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from collections import Counter
ap=argparse.ArgumentParser();ap.add_argument("--dir",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);ap.add_argument("--table",type=Path,required=True);a=ap.parse_args()
xs=[json.loads(p.read_text()) for p in sorted(a.dir.glob("*.json"))]
if len(xs)!=3593: raise SystemExit(f"expected 3593 systems got {len(xs)}")
fields=["family","trait_name","config_type","n_input_species","n_prune","n_bind","n_fail_to_bind","primary_resolvable_species","crosswalk_pass","hold_reason"]
a.table.parent.mkdir(parents=True,exist_ok=True)
with a.table.open("w",newline="") as fh:
 w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows({k:x[k] for k in fields} for x in sorted(xs,key=lambda z:(z["family"],z["trait_name"])))
p=[x for x in xs if x["crosswalk_pass"]]; fam=sorted({x["family"] for x in p});tr=sorted({x["trait_name"] for x in p});hc=Counter()
for x in xs:
 if not x["crosswalk_pass"]:
  for q in filter(None,x["hold_reason"].split(";")):hc[q]+=1
gate=len(fam)>=12 and len(tr)>=4
out={"version":"v0.4.3","status":"AUSTRAITS_MEMORY_PHYLOGENY_CROSSWALK_PASS" if gate else "HOLD_AUSTRAITS_MEMORY_PHYLOGENY_CROSSWALK","outcome_blind":True,"austraits_memory_effects_opened":False,"n_candidate_systems":len(xs),"n_crosswalk_pass":len(p),"n_independent_families":len(fam),"n_distinct_traits":len(tr),"hold_reason_counts":dict(hc),"exact_phylo_maker_status":True,"gate_pass":gate,"next_gate":"Rebuild necessary crossed core and geometry signatures from exact V.PhyloMaker2 statuses." if gate else "Stop replication before real effects."}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
