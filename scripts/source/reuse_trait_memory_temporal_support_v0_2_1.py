#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--prior-result",type=Path,required=True)
ap.add_argument("--prior-table",type=Path,required=True)
ap.add_argument("--semantic-contract",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

prior=json.loads(a.prior_result.read_text())
assert prior["status"]=="BIEN_TRAIT_SUPPORT_PASS"
assert prior["observed_database_version"]=="4.2.8"
assert prior["outcome_blind"] is True
assert prior["generalized_trait_values_opened"] is False
assert prior["biological_turnover_outcomes_opened"] is False
assert prior["n_family_trait_systems"]==8215

sem=json.loads(a.semantic_contract.read_text())
continuous=list(sem["representation_rules"]["continuous_scalar"]["traits"])
categorical=list(sem["representation_rules"]["nominal_categorical"]["traits"])
allowed=set(continuous)|set(categorical)
assert len(allowed)==52
classmap={t:"continuous_scalar" for t in continuous}
classmap.update({t:"nominal_categorical" for t in categorical})

rows=[]
with a.prior_table.open(newline="") as fh:
    for r in csv.DictReader(fh):
        if r["trait_name"] not in allowed:
            continue
        out=dict(r)
        out["semantic_class"]=classmap[r["trait_name"]]
        out["structural_pass"]=int(float(r["temporal_species"]))>=20
        rows.append(out)

a.table_out.parent.mkdir(parents=True,exist_ok=True)
fields=["family","trait_name","semantic_class","temporal_species","structural_pass"]
with a.table_out.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({k:r[k] for k in fields})

passing=[r for r in rows if r["structural_pass"]]
families=sorted({r["family"] for r in passing})
traits=sorted({r["trait_name"] for r in passing})
observed_traits=sorted({r["trait_name"] for r in rows})
missing=sorted(allowed-set(observed_traits))
gate=len(families)>=12 and len(traits)>=4
result={
  "version":"v0.2.1",
  "status":"TRAIT_MEMORY_TEMPORAL_SUPPORT_PASS" if gate else "HOLD_TRAIT_MEMORY_TEMPORAL_SUPPORT",
  "reuse_contract":"data/trait_memory_support_reuse_v0_2_1.json",
  "outcome_blind":True,
  "real_trait_values_opened":False,
  "real_memory_effects_opened":False,
  "n_preclassified_traits":52,
  "n_traits_with_any_prior_aggregate_row":len(observed_traits),
  "traits_with_no_aggregate_rows":missing,
  "n_family_trait_systems":len(rows),
  "n_structural_pass_systems":len(passing),
  "n_independent_families":len(families),
  "n_distinct_traits":len(traits),
  "qualifying_families":families,
  "qualifying_traits":traits,
  "minimum_families":12,
  "minimum_traits":4,
  "gate_pass":gate,
  "next_gate":"Run temporal-only semantic validity on all structural PASS systems." if gate else "Stop follow-up before real memory effects."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps(result,indent=2,sort_keys=True))
