#!/usr/bin/env python3
"""Synthetic frozen-rule tests: no simulation/observed-data scientific outcome."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from interpret_austraits_k_source_noise_ou_v0_1 import compare,FINAL_STATUS

M=("trait_global","system_local");S=("c0p25","c1","c4");A=("S3","prune_only")
meta={
    "status":"AUSTRAITS_K_SOURCE_NOISE_OU_METRIC_NULL_ESTIMATED",
    "observed_graph":{"systems":249,"families":42,"traits":12},
    "replicates":256,"hard_nonclaims":["synthetic only"],"models":{}
}
families={}
for m in M:
    meta["models"][m]={}
    for s in S:
        axes={}
        for a in A:
            axes[a]={
                "observed":{"rank_gain":.12,"reversal_probability":.43},
                "null":{"rank_gain":{"mean":-.05,"q975":.03,"p_null_ge_observed":1/257},
                        "reversal_probability":{"mean":.5}}
            }
            families[(m,s,a)]={
                "status":"AUSTRAITS_SOURCE_NOISE_OU_FAMILY_REPEATABILITY_CALIBRATED",
                "model":m,"scenario":s,"axis":a,"n_null_replicates":256,
                "valid_null_replicates":256,
                "observed_family_repeatability":.50,
                "null_family_repeatability":{"mean":.2,"q975":.4,"p_null_ge_observed":1/257}
            }
        meta["models"][m][s]={"axes":axes}
design={"status":"POST_OBSERVED_K_AND_SHARED_OU_PRE_SOURCE_DISPERSION_OUTCOMES_FROZEN"}
a=compare(meta,families,design)
assert a["status"]==FINAL_STATUS
assert a["decision"]=="RANK_PORTABILITY_BEYOND_TESTED_INDEPENDENT_OU_SOURCE_ENVELOPES"
# One sufficiently source-noisy scenario explains rank => no strong claim.
meta["models"]["system_local"]["c4"]["axes"]["S3"]["null"]["rank_gain"]["q975"]=.14
b=compare(meta,families,design)
assert b["decision"]=="RANK_PORTABILITY_NOT_BEYOND_ALL_SOURCE_OU_ENVELOPES"
assert b["at_least_one_predeclared_model_accommodates_rank"] is True
# Bad family-ICC alone does NOT rewrite the declared rank-primary decision.
meta["models"]["system_local"]["c4"]["axes"]["S3"]["null"]["rank_gain"]["q975"]=.03
families[("system_local","c4","S3")]["null_family_repeatability"]["q975"]=.6
c=compare(meta,families,design)
assert c["decision"]=="RANK_PORTABILITY_BEYOND_TESTED_INDEPENDENT_OU_SOURCE_ENVELOPES"
bad=families.pop(("trait_global","c1","S3"))
try:
    compare(meta,families,design)
except ValueError as e:
    assert "missing" in str(e)
else:
    raise AssertionError("partial REML run incorrectly accepted")
print("PASS: 12 rank-primary tests, source accommodation, ICC secondary, and complete model identity")
