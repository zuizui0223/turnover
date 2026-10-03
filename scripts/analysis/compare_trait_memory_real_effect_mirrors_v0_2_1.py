#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--a",type=Path,required=True)
ap.add_argument("--b",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()

def read(p):
    with p.open(newline="") as fh:
        rows=list(csv.DictReader(fh))
    return {(r["family"],r["trait_name"]):r for r in rows}
A=read(a.a); B=read(a.b)
if set(A)!=set(B): raise SystemExit("system key sets differ")
max_s3=max(abs(float(A[k]["S3_rho"])-float(B[k]["S3_rho"])) for k in A)
max_pr=max(abs(float(A[k]["prune_only_rho"])-float(B[k]["prune_only_rho"])) for k in A)
ok=max_s3<=1e-12 and max_pr<=1e-12
out={"status":"REAL_EFFECT_TECHNICAL_MIRROR_MATCH" if ok else "HOLD_REAL_EFFECT_TECHNICAL_MIRROR_MISMATCH",
     "n_systems":len(A),"max_abs_diff_S3":max_s3,"max_abs_diff_prune_only":max_pr,"tolerance":1e-12,"match":ok}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
if not ok: raise SystemExit(1)
