#!/usr/bin/env python3
"""Synthetic, outcome-free tests for BM-normalized trait rank prediction."""
from __future__ import annotations
import copy
import runpy
import numpy as np
import pandas as pd

ns=runpy.run_path('scripts/analysis/analyze_austraits_k_bm_centered_portability_v0_1.py')
get_arrays=ns['audited_arrays']
one_axis=ns['one_axis']
rng=np.random.default_rng(20261008)
edges=[(f,t) for f in range(42) for t in range(13) if (f+t)%13<6]
edges.extend([(0,6),(1,5)])
assert len(edges)==254
data=[]
null=[]
B=64
for i,(f,t) in enumerate(edges):
    sid=f'T{i:04d}'
    mu=.6*np.sin(f*.7)+.4*np.cos(i*.3)
    samples=mu+rng.normal(0,.6,B)
    obs=mu+(t-6)*.18+rng.normal(0,.08)
    data.append({'system_id':sid,'family':f'F{f:02d}','trait_name':f'T{t:02d}',
                 'S3_logK':obs,'prune_logK':obs})
    for rep,z in enumerate(samples):
        null.append({'system_id':sid,'family':f'F{f:02d}','trait_name':f'T{t:02d}',
                     'replicate':rep,'S3_logK':z,'prune_logK':z})
obs=pd.DataFrame(data);sim=pd.DataFrame(null)
graph,y,m=get_arrays(obs,sim,'S3',B)
assert len(graph)==254 and m.shape==(254,64)
result=one_axis(graph,y,m)
for norm in ['excess','standardized_excess']:
    assert result['normalizations'][norm]['rank_gain']['observed']>0
    assert result['normalizations'][norm]['rank_gain']['p_null_ge_observed']<=.05
    assert result['normalizations'][norm]['absolute_gain']['observed']>0

bad=sim.iloc[:-1]
try:
    get_arrays(obs,bad,'S3',B)
    raise AssertionError('missing Brownian draw accepted')
except ValueError as e:
    assert 'incomplete' in str(e)
bad=copy.deepcopy(sim)
bad.loc[0,'family']='INCORRECT'
try:
    get_arrays(obs,bad,'S3',B)
    raise AssertionError('incorrect family identity accepted')
except ValueError as e:
    assert 'identity' in str(e)

print('PASS: fixed 254-system graph, latent trait prior, self-heldout null, missing draw and identity guards')
