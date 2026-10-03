#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--core-candidates",type=Path,required=True)
ap.add_argument("--prior-results",type=Path,required=True)
ap.add_argument("--novel-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

with a.core_candidates.open(newline="") as fh:
    candidates=list(csv.DictReader(fh))
keys={(r["family"],r["trait_name"]):r for r in candidates}

with a.prior_results.open(newline="") as fh:
    prior=list(csv.DictReader(fh))
prior_map={(r["family"],r["trait_name"]):r for r in prior}

fields=[
 "system_id","family","trait_name","semantic_class","n_input_species","n_prune","n_bind",
 "s3_lambda","s3_mae","s3_directional","s3_valid_fraction","s3_pass",
 "prune_lambda","prune_mae","prune_directional","prune_valid_fraction","prune_pass",
 "system_temporal_pass","provenance"
]
rows=[]
n_reused=0
for k,cand in sorted(keys.items()):
    if k not in prior_map:
        continue
    r=prior_map[k]
    rows.append({
      "system_id":r["system_id"],"family":r["family"],"trait_name":r["trait_name"],
      "semantic_class":r["semantic_class"],"n_input_species":r["n_input_species"],
      "n_prune":r["n_prune"],"n_bind":r["n_bind"],
      "s3_lambda":r["s3_lambda"],"s3_mae":r["s3_mae"],"s3_directional":r["s3_directional"],
      "s3_valid_fraction":r["s3_valid_fraction"],"s3_pass":r["s3_pass"],
      "prune_lambda":r["prune_lambda"],"prune_mae":r["prune_mae"],"prune_directional":r["prune_directional"],
      "prune_valid_fraction":r["prune_valid_fraction"],"prune_pass":r["prune_pass"],
      "system_temporal_pass":r["system_temporal_pass"],"provenance":"REUSED_PRIOR_FROZEN_RESULT"
    })
    n_reused+=1

novel_files=sorted(a.novel_dir.glob("*.json"))
n_novel=0
for p in novel_files:
    x=json.loads(p.read_text())
    k=(x["family"],x["trait_name"])
    if k not in keys:
        raise SystemExit(f"novel result not in core candidates: {k}")
    s3=x["temporal_s3"]; pr=x["temporal_prune_only"]
    rows.append({
      "system_id":x["system_id"],"family":x["family"],"trait_name":x["trait_name"],
      "semantic_class":x["semantic_class"],"n_input_species":x["n_input_species"],
      "n_prune":x["n_prune"],"n_bind":x["n_bind"],
      "s3_lambda":s3.get("lambda"),"s3_mae":s3.get("median_absolute_recovery_error"),
      "s3_directional":s3.get("directional_recovery"),"s3_valid_fraction":s3.get("valid_replicate_fraction"),
      "s3_pass":bool(s3.get("pass",False)),
      "prune_lambda":pr.get("lambda"),"prune_mae":pr.get("median_absolute_recovery_error"),
      "prune_directional":pr.get("directional_recovery"),"prune_valid_fraction":pr.get("valid_replicate_fraction"),
      "prune_pass":bool(pr.get("pass",False)),
      "system_temporal_pass":bool(x["system_temporal_pass"]),
      "provenance":"NEW_IDENTICAL_CONTRACT_SIMULATION"
    })
    n_novel+=1

if len(rows)!=len(keys):
    seen={(r["family"],r["trait_name"]) for r in rows}
    missing=sorted(set(keys)-seen)
    raise SystemExit(f"incomplete informativeness results: {len(rows)} != {len(keys)}, missing {missing[:10]}")

rows.sort(key=lambda r:(r["family"],r["trait_name"]))
a.table_out.parent.mkdir(parents=True,exist_ok=True)
with a.table_out.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)

def truth(v):
    return str(v).strip().lower() in {"true","t","1"}
passing=[r for r in rows if truth(r["system_temporal_pass"])]
families=sorted({r["family"] for r in passing})
traits=sorted({r["trait_name"] for r in passing})
out={
  "version":"v0.5",
  "status":"TRAIT_MEMORY_TEMPORAL_INFORMATIVENESS_COMPLETE",
  "outcome_blind":True,
  "real_trait_values_opened":False,
  "real_memory_effects_opened":False,
  "n_candidate_systems":len(rows),
  "n_reused_prior_systems":n_reused,
  "n_newly_simulated_systems":n_novel,
  "n_temporal_pass_systems":len(passing),
  "n_pass_families_before_final_core":len(families),
  "n_pass_traits_before_final_core":len(traits),
  "qualifying_families":families,
  "qualifying_traits":traits,
  "next_gate":"Apply frozen crossed-core degree/connectivity gate before real memory rho."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
