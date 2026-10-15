#!/usr/bin/env python3
"""Synthetic original 249-system stationary OU + observation-noise data.

Tests original observed-K and source-OU identity against unchanged original
graph without interpreting artificial null outcomes as biological results.
"""
import argparse,copy,json,sys
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_k_organ_modules_source_ou_null_v0_1 import (
    analyze,metric_summary,STATUS,VALID_STATUS)
p=argparse.ArgumentParser()
p.add_argument("--observed-K",required=True,type=Path)
args=p.parse_args()
K=pd.read_csv(args.__dict__["observed_K"])
cfg=json.loads((ROOT/"data"/"austraits_k_functional_module_portability_v0_1.json").read_text())
assert len(K)==254
rng=np.random.default_rng(20261015)
null={}
for r in K.itertuples(index=False):
    if r.trait_name=="seed_height":continue
    axis={}
    for name,column in (("S3","S3_logK"),("prune_only","prune_logK")):
        scenarios={}
        for c in ("c0p25","c1","c4"):
            scenarios[c]={"models":{
                m:{"logK":rng.normal(loc=0,scale=1,size=256).tolist()}
                for m in ("trait_global","system_local")}}
        axis[name]={"observed_logK":float(getattr(r,column)),
                    "scenarios":scenarios}
    null[r.system_id]={
       "status":VALID_STATUS,"system_id":r.system_id,
       "family":r.family,"trait_name":r.trait_name,
       "replicates_per_model":256,"axes":axis}
result=analyze(K,null,cfg)
assert result["status"]==STATUS and result["observed_original_tip_inter_organ_pairs"]==410
assert result["families_with_inter_organ_pairs"]==34
assert result["NOT_applicable_to_760_matched_taxon_null_distribution"]
assert result["after_observed_K_OU_source_and_matched_tip_K"]
assert result["independent_TRY_v7_validation"] is False
for model in ("trait_global","system_local"):
 for c in ("c0p25","c1","c4"):
  for ax in ("S3","prune_only"):
   z=result["model_results"][model][c][ax]
   assert z["n_inter_organ_family_pairs"]==410 and z["n_families"]==34
   for name in ("pair_weighted","equal_family"):
    d=z[name]
    assert 0<=d["observed"]<=1
    assert 0<=d["null_q025"]<=d["null_q975"]<=1
    assert 1/257<=d["descriptive_Monte_Carlo_p_one_sided"]<=1
invalid=dict(null);invalid.pop(next(iter(invalid)))
try:analyze(K,invalid,cfg)
except ValueError as e:assert "not every original" in str(e)
else:raise AssertionError("incomplete original 249 graph accepted")
orig=np.array([1,0,1,0])
sim=np.array([[1]*256,[0]*256,[0]*256,[0]*256],float)
unit=metric_summary(orig,sim,["F1","F1","F2","F2"])
assert unit["n_families"]==2 and unit["n_inter_organ_family_pairs"]==4
assert unit["pair_weighted"]["observed"]==.5
print("PASS: original 249 system + 410 functional pair OU parity, 12 scenarios, record identity guards")
