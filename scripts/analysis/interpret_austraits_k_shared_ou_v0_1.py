#!/usr/bin/env python3
"""Interpret fixed equal-OU process null without altering rho/K results.

One OU model shared by all 254 family-trait systems is simulated at three
predeclared dimensionless attraction strengths. A strong process-level
exceedance requires rank portability and conditional family repeatability
to be beyond the 97.5% null quantile on BOTH trees under ALL 3 scenarios.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

AXES={'S3':'S3','prune_only':'prune_only'}
SCENARIOS=('c0p25','c1','c4')

def compare(metric:dict,family_by_key:dict,design:dict):
    if design.get('status')!='POST_EQUAL_BM_OUTCOME_PRE_EQUAL_OU_NULL_DESIGN_FROZEN':
        raise ValueError('OU interpretation design not fixed')
    if metric.get('status')!='AUSTRAITS_REAL_TREE_SHARED_OU_K_METRIC_NULL_ESTIMATED':
        raise ValueError('OU metrics not completed')
    if metric.get('observed_graph')!={'systems':254,'families':42,'traits':13}:
        raise ValueError('OU graph does not match observed K graph')
    if metric.get('replicates_per_scenario')!=256:
        raise ValueError('OU replicate count mismatch')
    result={'version':'v0.1',
        'status':'AUSTRAITS_SHARED_OU_PROCESS_NULL_INTERPRETED',
        'post_BM_outcome_pre_OU_outcome_frozen':True,
        'fixed_graph':metric['observed_graph'],
        'scenarios':{},
        'hard_nonclaims':[
          'Equal OU is one of several possible homogeneous models, not a proof of process history.',
          'No adaptive trade-off or selection inference from null exceedance.',
          'Nulls ignore correlation between traits and uncertainties in source phylogenies.']
    }
    strong=True
    partial=False
    any_homogeneous_accommodation=False
    for scen in SCENARIOS:
        z=metric['scenarios'][scen]
        out={}
        allaxes=True
        for axis in AXES:
            v=z['axes'][axis]
            f=family_by_key[(scen,axis)]
            if f['status']!='AUSTRAITS_SHARED_OU_FAMILY_REPEATABILITY_CALIBRATED':
                raise ValueError('OU family-null status wrong')
            if f['scenario']!=scen or f['axis']!=axis or f['n_null_replicates']!=256:
                raise ValueError('OU family-null identity mismatch')
            if f['valid_null_replicates']<243:
                raise ValueError('insufficient valid OU REML null replicates')
            obs=v['observed']
            nc=v['null']
            fam=f['observed_family_repeatability']
            fn=f['null_family_repeatability']
            exceed_rank=obs['rank_gain']>nc['rank_gain']['q975']
            exceed_fam=fam>fn['q975']
            partial|=exceed_rank or exceed_fam
            allaxes &= exceed_rank and exceed_fam
            out[axis]={
                'empirical_rank_gain':obs['rank_gain'],
                'null_rank_mean':nc['rank_gain']['mean'],
                'null_rank_interval':[nc['rank_gain']['q025'],nc['rank_gain']['q975']],
                'rank_p_null_ge':nc['rank_gain']['p_null_ge_observed'],
                'rank_exceeds_null':exceed_rank,
                'empirical_family_repeatability':fam,
                'null_family_mean':fn['mean'],
                'null_family_interval':[fn['q025'],fn['q975']],
                'family_p_null_ge':fn['p_null_ge_observed'],
                'family_exceeds_null':exceed_fam,
                'empirical_reversal':obs['reversal_probability'],
                'null_reversal_mean':nc['reversal_probability']['mean'],
                'null_reversal_interval':[nc['reversal_probability']['q025'],nc['reversal_probability']['q975']]
            }
        strong &= allaxes
        any_homogeneous_accommodation |= not allaxes
        result['scenarios'][scen]={
            'dimensionless_alpha':z['dimensionless_alpha'],
            'both_axes_beyond_family_and_rank':allaxes,
            'axes':out
        }
    if strong:
        decision='K_STRUCTURE_BEYOND_ALL_THREE_EQUAL_OU_SCENARIOS'
    elif partial:
        decision='K_STRUCTURE_NOT_BEYOND_ALL_EQUAL_OU_SCENARIOS'
    else:
        decision='NO_EVIDENCE_BEYOND_EQUAL_OU_SCENARIOS'
    result['decision']=decision
    result['at_least_one_shared_OU_scenario_accommodates_data']=any_homogeneous_accommodation
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--metrics',type=Path,required=True)
    p.add_argument('--family-dir',type=Path,required=True)
    p.add_argument('--design',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    family={}
    for file in sorted(a.family_dir.glob('*.json')):
        d=json.loads(file.read_text())
        key=(d.get('scenario'),d.get('axis'))
        if key in family:raise ValueError('duplicate OU family-null axis/scenario')
        family[key]=d
    assert len(family)==6, len(family)
    r=compare(json.loads(a.metrics.read_text()),family,json.loads(a.design.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':r['status'],'decision':r['decision'],
                      'any_shared_OU_accommodation':r['at_least_one_shared_OU_scenario_accommodates_data']},indent=2))
if __name__=='__main__':main()
