#!/usr/bin/env python3
"""Synthetic process-null interpretation scenarios: no empirical K opened."""
import copy
import runpy
from pathlib import Path

mod=runpy.run_path('scripts/analysis/interpret_austraits_k_real_tree_bm_v0_1.py')
assess=mod['assess']
contract={
 'status':'POST_RHO_K_OUTCOME_BUT_PRE_REAL_TREE_BM_NULL_INTERPRETATION',
 'fixed_graph':{'systems':254,'families':42,'traits':13},
 'source_run':'37746671909'
}
metric={
 'status':'AUSTRAITS_REAL_TREE_EQUAL_BM_K_NULL_AGGREGATED',
 'observed_graph':copy.deepcopy(contract['fixed_graph']),
 'null_replicates':64,
 'axes':{}
}
family={
 'status':'AUSTRAITS_REAL_TREE_EQUAL_BM_K_FAMILY_REPEATABILITY_CALIBRATED',
 'n_null_replicates':64,'axes':{}
}
for ax,part in [('S3','S3_logK'),('prune_only','prune_logK')]:
 metric['axes'][ax]={
    'observed':{'rank_gain':0.15,'absolute_gain':0.12,
                'reversal_probability':0.43,'n_trait_pairs':15},
    'null':{
      'rank_gain':{'mean':-0.04,'q025':-0.12,'q975':0.02,'p_null_ge_observed':1/65},
      'absolute_gain':{'mean':-0.03,'q025':-0.10,'q975':0.03,'p_null_ge_observed':1/65},
      'reversal_probability':{'mean':0.5,'q025':0.46,'q975':0.52,'p_null_ge_observed':1.0}
    }
 }
 family['axes'][part]={
    'valid_null_replicates':64,
    'observed_family_repeatability':0.6,
    'null_family_repeatability':{
       'mean':0.05,'q025':0,'q975':0.21,
       'p_null_ge_observed':1/65
    }
 }
r=assess(metric,family,contract)
assert r['decision']=='BEYOND_IDENTICAL_BM_K_NULL_ON_BOTH_AXES'
assert all(x['strong_axis'] for x in r['axes'].values())

f=copy.deepcopy(family)
f['axes']['S3_logK']['observed_family_repeatability']=0.03
assert assess(metric,f,contract)['decision']=='PARTIAL_BM_NULL_EXCEEDANCE'

m=copy.deepcopy(metric)
f=copy.deepcopy(family)
for ax,p in [('S3','S3_logK'),('prune_only','prune_logK')]:
 m['axes'][ax]['observed']['rank_gain']=-0.05
 m['axes'][ax]['observed']['absolute_gain']=-0.05
 f['axes'][p]['observed_family_repeatability']=0.1
assert assess(m,f,contract)['decision']=='NOT_BEYOND_IDENTICAL_BM_K_NULL'

bad=copy.deepcopy(metric)
bad['observed_graph']['systems']=253
try:
 assess(bad,f,contract)
except ValueError as e:
 assert 'graph' in str(e)
else:
 raise AssertionError('Changed empirical graph did not hard stop')

bad=copy.deepcopy(family)
bad['axes']['prune_logK']['valid_null_replicates']=59
try:
 assess(metric,bad,contract)
except ValueError as e:
 assert 'valid' in str(e)
else:
 raise AssertionError('Incomplete family-null did not hard stop')

print('PASS: strong, partial, not-supported, source identity and incomplete-null guards')
