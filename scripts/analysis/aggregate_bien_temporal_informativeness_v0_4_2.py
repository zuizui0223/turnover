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
if not files: raise SystemExit("no system results")
rows=[]
for p in files:
    x=json.loads(p.read_text())
    rows.append({
      "system_id":x["system_id"],"family":x["family"],"trait_name":x["trait_name"],
      "semantic_class":x["semantic_class"],"n_input_species":x["n_input_species"],
      "n_prune":x["n_prune"],"n_bind":x["n_bind"],
      "s3_lambda":x["temporal_s3"].get("lambda"),
      "s3_mae":x["temporal_s3"].get("median_absolute_recovery_error"),
      "s3_directional":x["temporal_s3"].get("directional_recovery"),
      "s3_valid_fraction":x["temporal_s3"].get("valid_replicate_fraction"),
      "s3_pass":bool(x["temporal_s3"].get("pass",False)),
      "prune_lambda":x["temporal_prune_only"].get("lambda"),
      "prune_mae":x["temporal_prune_only"].get("median_absolute_recovery_error"),
      "prune_directional":x["temporal_prune_only"].get("directional_recovery"),
      "prune_valid_fraction":x["temporal_prune_only"].get("valid_replicate_fraction"),
      "prune_pass":bool(x["temporal_prune_only"].get("pass",False)),
      "system_temporal_pass":bool(x["system_temporal_pass"])
    })
a.table_out.parent.mkdir(parents=True,exist_ok=True)
with a.table_out.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]))
    w.writeheader();w.writerows(rows)
passing=[r for r in rows if r["system_temporal_pass"]]
families=sorted({r["family"] for r in passing})
gate=len(families)>=12
out={
  "version":"v0.4.2",
  "status":"BIEN_TEMPORAL_INFORMATIVENESS_PASS" if gate else "HOLD_BIEN_TEMPORAL_INFORMATIVENESS",
  "outcome_blind":True,
  "real_trait_values_opened":False,
  "biological_turnover_outcomes_opened":False,
  "n_candidate_systems":len(rows),
  "n_temporal_pass_systems":len(passing),
  "n_independent_families":len(families),
  "qualifying_families":families,
  "minimum_required_families":12,
  "gate_pass":gate,
  "next_gate":"Run frozen spatial informativeness only for temporal-PASS systems." if gate else "Stop BIEN generalized trait route before spatial/real outcomes; AusTraits is already terminal HOLD and no third source is allowed."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
