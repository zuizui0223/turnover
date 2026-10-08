#!/usr/bin/env python3
"""Synthetic CI for the exact-graph OU K aggregation and interpretation pipeline.

Use four draws instead of the frozen 256 solely to check schema/identity
wiring; all actual scientific runs must enforce 256 simulations per scenario.
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0,"scripts/analysis")
import aggregate_austraits_k_shared_ou_v0_1 as agg
from interpret_austraits_k_shared_ou_v0_1 import compare

rng=np.random.default_rng(20261008)
B=4
agg.B=B
with tempfile.TemporaryDirectory(prefix="aust_ou_preflight_") as temp:
    root=Path(temp)
    (root/"input").mkdir()
    observed=[]
    edges=[]
    for f in range(42):
        for k in range(6):
            edges.append((f,(5*f+k)%13))
    edges.extend([(0,6),(1,11)])
    assert len(edges)==254 and len(set(edges))==254
    reference={
      'status':'AUSTRAITS_REAL_TREE_OU_TIME_REFERENCE_FROZEN',
      'n_systems':254,'n_axis_tree_samples':508,'T_ref':100.0,
      'absolute_alpha_grid':{'c0p25':.0025,'c1':.01,'c4':.04}
    }
    (root/"time.json").write_text(json.dumps(reference))
    for i,(f,t) in enumerate(edges):
        sid=f'A{i+1:04d}'
        row={'system_id':sid,'family':f'F{f:02d}',
             'trait_name':f'T{t:02d}',
             'S3_logK':float(np.cos(t*.4)+rng.normal(0,.12)),
             'prune_logK':float(np.sin(t*.4)+rng.normal(0,.12))}
        observed.append(row)
        system={'version':'v0.1',
                'status':'AUSTRAITS_REAL_TREE_SHARED_OU_NULL_SYSTEM_ESTIMATED',
                'system_id':sid,'family':row['family'],'trait_name':row['trait_name'],
                'T_ref':100.0,'n_scenarios':3,'ou_null_replicates_per_scenario':B,
                'axes':{}}
        for ax,col in [('S3','S3_logK'),('prune_only','prune_logK')]:
            sims={}
            for label,v in reference['absolute_alpha_grid'].items():
                sims[label]={'alpha':v,'logK':list(rng.normal(0,.15,size=B))}
            system['axes'][ax]={
                'observed_logK':row[col],
                'relative_fast_K_error':0,
                'scenarios':sims
            }
        (root/"input"/f'{sid}.json').write_text(json.dumps(system))
    pd.DataFrame(observed).to_csv(root/"K.csv",index=False)
    oldarg=sys.argv
    try:
        sys.argv=['test','--input-dir',str(root/'input'),
                  '--observed-K',str(root/'K.csv'),
                  '--time-reference',str(root/'time.json'),
                  '--out',str(root/'result.json'),
                  '--tables-dir',str(root/'tables')]
        agg.main()
    finally:
        sys.argv=oldarg
    x=json.loads((root/'result.json').read_text())
    assert x['status']=='AUSTRAITS_REAL_TREE_SHARED_OU_K_METRIC_NULL_ESTIMATED'
    assert x['observed_graph']=={'systems':254,'families':42,'traits':13}
    assert set(x['scenarios'])=={'c0p25','c1','c4'}
    for scen in x['scenarios']:
        z=pd.read_csv(root/'tables'/f'null_effects_{scen}.csv')
        assert len(z)==B*254 and z.replicate.nunique()==B
        assert set(x['scenarios'][scen]['axes'])=={'S3','prune_only'}

    design={'status':'POST_EQUAL_BM_OUTCOME_PRE_EQUAL_OU_NULL_DESIGN_FROZEN'}
    family={}
    for scen in ('c0p25','c1','c4'):
        for axis in ('S3','prune_only'):
            empirical=x['scenarios'][scen]['axes'][axis]['observed']
            family[(scen,axis)]={
                'status':'AUSTRAITS_SHARED_OU_FAMILY_REPEATABILITY_CALIBRATED',
                'scenario':scen,'axis':axis,'n_null_replicates':256,
                'valid_null_replicates':256,
                'observed_family_repeatability':.7,
                'null_family_repeatability':{'mean':.02,'q025':0,'q975':.1,'p_null_ge_observed':1/257}
            }
            x['scenarios'][scen]['axes'][axis]['null']['rank_gain']['q975']=empirical['rank_gain']-.01
    verdict=compare(x,family,design)
    assert verdict['decision']=='K_STRUCTURE_BEYOND_ALL_THREE_EQUAL_OU_SCENARIOS'

    x['scenarios']['c4']['axes']['S3']['null']['rank_gain']['q975']+=.1
    assert compare(x,family,design)['decision']=='K_STRUCTURE_NOT_BEYOND_ALL_EQUAL_OU_SCENARIOS'

    altered=json.loads((root/'input'/'A0001.json').read_text())
    altered['family']='BROKEN'
    (root/'input'/'A0001.json').write_text(json.dumps(altered))
    try:
        sys.argv=['test','--input-dir',str(root/'input'),
                  '--observed-K',str(root/'K.csv'),
                  '--time-reference',str(root/'time.json'),
                  '--out',str(root/'result.json'),
                  '--tables-dir',str(root/'tables')]
        try:
            agg.main()
        except ValueError as e:
            assert 'identity' in str(e) or 'graph' in str(e)
        else:
            raise AssertionError('OU source identity mismatch not blocked')
    finally:
        sys.argv=oldarg

print("PASS: exact 254-cell graph, three scenarios, aggregated OU K metrics, verdict, source-identity stop")
