#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--repeatability",type=Path,required=True)
ap.add_argument("--portability",type=Path,required=True)
ap.add_argument("--lineage",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()

def read(path):
    with path.open(newline="") as fh:
        rows=list(csv.DictReader(fh))
    rows.sort(key=lambda r:(r["family"],r["trait_name"]))
    return rows

sets={
  "repeatability":read(a.repeatability),
  "portability":read(a.portability),
  "lineage":read(a.lineage)
}
for name,rows in sets.items():
    if len(rows)!=201:
        raise SystemExit(f"{name}: expected 201 rows, got {len(rows)}")

keycols=["family","trait_name"]
numcols=["n_species_S3","n_species_prune","S3_rho","prune_only_rho",
         "informativeness_n_input_species","informativeness_n_prune","informativeness_s3_lambda"]
textcols=["semantic_class"]

base=sets["repeatability"]
checks={}
for name in ["portability","lineage"]:
    other=sets[name]
    same_keys=all(all(x[k]==y[k] for k in keycols) for x,y in zip(base,other))
    if not same_keys:
        raise SystemExit(f"{name}: system keys differ")
    maxdiff={}
    for col in numcols:
        diffs=[abs(float(x[col])-float(y[col])) for x,y in zip(base,other)]
        maxdiff[col]=max(diffs) if diffs else 0.0
        if maxdiff[col]!=0:
            raise SystemExit(f"{name}: nonzero diff {col}={maxdiff[col]}")
    same_text={col:all(x[col]==y[col] for x,y in zip(base,other)) for col in textcols}
    if not all(same_text.values()):
        raise SystemExit(f"{name}: text metadata differs")
    checks[f"repeatability_vs_{name}"]={
      "same_201_system_keys":same_keys,
      "same_text_columns":same_text,
      "max_absolute_differences":maxdiff
    }

out={
  "version":"v0.1",
  "status":"TRAIT_MEMORY_REAL_EFFECT_IDENTITY_VERIFIED",
  "n_systems":201,
  "checks":checks,
  "all_numeric_differences_exactly_zero":True,
  "new_biological_inference":False
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
