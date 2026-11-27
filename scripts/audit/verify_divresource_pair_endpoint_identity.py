#!/usr/bin/env python3
"""Verify exact balanced pair design endpoint degeneracy; no original row values."""
import itertools,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
source=json.loads((ROOT/"results/divresource_2013_pool_transfer_v0_1.json").read_text())
assert source["status"]=="COMPLETE_EXPLORATORY_TWO_POOL_TRANSFER"
classes=np.array(list(itertools.product([0.,1.],repeat=2)))
pairs=list(itertools.combinations(range(4),2))
Z=np.array([[.5*(j in p) for j in range(4)] for p in pairs])
D=np.array([np.abs(classes[a]-classes[b]).sum()/2 for a,b in pairs])
# 6*d integer, exact incidence arithmetic
d6=np.rint(6*(D-2/3)).astype(int)
incidence=(Z*2).astype(int)
assert np.array_equal(d6@incidence,np.zeros(4,dtype=int))
X0=[];X1=[];Z4=[]
for t in range(4):
    for i in range(6):
        X0.append([1,*[float(t==u) for u in range(1,4)],*(Z[i]@classes)])
        X1.append([*X0[-1],D[i]])
        row=np.zeros(16);row[t*4:t*4+4]=Z[i];Z4.append(row)
X0=np.array(X0);X1=np.array(X1);Z4=np.array(Z4)
assert np.linalg.matrix_rank(X0)==6 and np.linalg.matrix_rank(X1)==7
d=np.tile(d6/6,4)
assert np.allclose(d@X0,0,atol=1e-12)
assert np.allclose(d@Z4,0,atol=1e-12)
def change(y):
    result=[]
    for i,j in ((0,1),(1,0)):
        error=[]
        for a in (X0,X1):
            r=y[j]-a@np.linalg.lstsq(a,y[i],rcond=None)[0]
            error.append(r@r)
        result.append(error[1]-error[0])
    return np.array(result)
rng=np.random.default_rng(20261126);max_error=0.
for _ in range(1000):
    B=[rng.uniform(20,1000,24) for k in range(2)]
    E=[Z4@rng.uniform(1,800,16) for k in range(2)]
    N=[B[i]-E[i] for i in range(2)]
    max_error=max(max_error,float(np.max(np.abs(change(B)-change(N)))))
assert max_error<1e-6
for fold in source["post_result_design_diagnostic"]["source_original_deltas"]:
    assert abs(fold["delta_SSE_B"]-fold["delta_SSE_NDE"])<1e-6
print(json.dumps({"status":"BALANCED_PAIR_ENDPOINT_SSE_IDENTITY_PASS","exact_integer_incidence_orthogonality":True,"synthetic_cases":1000,"maximum_synthetic_numerical_delta_difference":max_error,"original_fold_aggregate_deltas_agree":True,"no_new_empirical_outcomes_fit":True}))
