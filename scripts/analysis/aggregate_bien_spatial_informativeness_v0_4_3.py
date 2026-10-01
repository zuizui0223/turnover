#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

files=sorted(a.input_dir.glob("*.json"))
if not files:
    raise SystemExit("no spatial system results")

rows=[]
for p in files:
    x=json.loads(p.read_text())
    rows.append({
      "system_id":x["system_id"],
      "family":x["family"],
      "trait_name":x["trait_name"],
      "semantic_class":x["semantic_class"],
      "n_spatial_species":x["n_spatial_species"],
      "min_unique_nodes":x.get("min_unique_nodes"),
      "max_unique_nodes":x.get("max_unique_nodes"),
      "min_records":x.get("min_records"),
      "max_records":x.get("max_records"),
      "lambda":x.get("lambda"),
      "mae":x.get("median_absolute_recovery_error"),
      "directional":x.get("directional_recovery"),
      "valid_fraction":x.get("valid_replicate_fraction"),
      "system_spatial_pass":bool(x.get("system_spatial_pass",False)),
      "status":x["status"]
    })

a.table_out.parent.mkdir(parents=True,exist_ok=True)
with a.table_out.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

passing=[r for r in rows if r["system_spatial_pass"]]
families=sorted({r["family"] for r in passing})
gate=len(families)>=12
out={
  "version":"v0.4.3",
  "status":"BIEN_SPATIAL_INFORMATIVENESS_PASS" if gate else "HOLD_BIEN_SPATIAL_INFORMATIVENESS",
  "outcome_blind":True,
  "real_trait_values_opened":False,
  "biological_turnover_outcomes_opened":False,
  "n_temporal_pass_candidate_systems":len(rows),
  "n_spatial_pass_systems":len(passing),
  "n_independent_families":len(families),
  "qualifying_families":families,
  "minimum_required_families":12,
  "gate_pass":gate,
  "next_gate":"Freeze and execute real BIEN trait turnover extraction/estimation only for final informativeness-PASS systems." if gate else "Close generalized trait route pre-outcome: AusTraits is already terminal HOLD and no third primary trait source is allowed."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
