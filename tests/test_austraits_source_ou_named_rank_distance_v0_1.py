#!/usr/bin/env python3
"""Synthetic schema/adequacy tests (not a biological null result)."""
from pathlib import Path
import json,math,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_source_ou_named_rank_distance_v0_1 import analyze,profile,STATUS
rng=np.random.default_rng(20261010)
families=[f"F{i:02d}" for i in range(42)]
traits=[f"T{i:02d}" for i in range(12)]
rows=[]
for f in families:
    for j in range(5+(int(f[1:])<39)):
        t=traits[(7*int(f[1:])+j)%12]
        rows.append({"system_id":f"A{len(rows)+1:04d}","family":f,
                     "trait_name":t,"S3_logK":float(rng.normal()),
                     "prune_logK":float(rng.normal())})
assert len(rows)==249
for f in families[:5]:
    rows.append({"system_id":f"A{len(rows)+1:04d}","family":f,
                 "trait_name":"seed_height","S3_logK":0.0,"prune_logK":0.0})
raw=pd.DataFrame(rows)
sim={}
for r in rows[:249]:
    sim[r["system_id"]]={
        "status":"AUSTRAITS_K_SOURCE_NOISE_OU_SYSTEM_ESTIMATED",
        "family":r["family"],"trait_name":r["trait_name"],
        "axes":{axis:{"scenarios":{c:{"models":{
            m:{"logK":rng.normal(size=256).tolist()}
             for m in ("trait_global","system_local")}}
             for c in ("c0p25","c1","c4")}}
             for axis in ("S3","prune_only")}
    }
out=analyze(raw,sim)
assert out["status"]==STATUS
assert out["fixed_graph"]=={"systems":249,"families":42,"traits":12}
assert out["post_source_ou_outcome_exploratory"] is True
for m in ("trait_global","system_local"):
  for c in ("c0p25","c1","c4"):
    for a in ("S3","prune_only"):
      x=out["models"][m][c][a]
      assert math.isfinite(x["observed_named_rank_squared_distance"])
      assert x["null_distance_mean"]>0
      assert len(x["named_traits"])==12
      assert 1/257<=x["descriptive_p_null_ge_observed"]<=1
missing=sim.pop(next(iter(sim)))
try:
    analyze(raw,sim)
except ValueError as e:
    assert "all 249" in str(e)
else:
    raise AssertionError("Accepted incomplete original source graph")
print("PASS: synthetic exact 249-system named-profile distance and 12-condition null checks")
