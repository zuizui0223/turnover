#!/usr/bin/env python3
"""Produce a fixed-graph audit of AusTraits K against the real-tree identical-BM null.

Outcome categories were specified before the 254-system empirical/null calibration
finished. This does not upgrade any retrospective comparison to prospectively
preregistered evidence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

AXES={'prune_only':'prune_logK','S3':'S3_logK'}
TOL=1e-10

def assess(metrics:dict,family:dict,design:dict)->dict:
    if design.get('status')!='POST_RHO_K_OUTCOME_BUT_PRE_REAL_TREE_BM_NULL_INTERPRETATION':
        raise ValueError('interpretation contract does not match')
    if metrics.get('status')!='AUSTRAITS_REAL_TREE_EQUAL_BM_K_NULL_AGGREGATED':
        raise ValueError('K metric null is incomplete')
    if family.get('status')!='AUSTRAITS_REAL_TREE_EQUAL_BM_K_FAMILY_REPEATABILITY_CALIBRATED':
        raise ValueError('family null is incomplete')
    if metrics.get('observed_graph')!=design.get('fixed_graph'):
        raise ValueError('matched system graph changed')
    if metrics.get('null_replicates')!=64 or family.get('n_null_replicates')!=64:
        raise ValueError('null replication count changed')
    axes={}
    for key,other in AXES.items():
        x=metrics['axes'][key]
        f=family['axes'][other]
        if f['valid_null_replicates']<61:
            raise ValueError(f'insufficient valid family null replicates: {key}')
        if x['observed']['n_trait_pairs']<10:
            raise ValueError(f'insufficient well-represented trait pairs: {key}')
        fam_obs=float(f['observed_family_repeatability'])
        fam_null=f['null_family_repeatability']
        fam_hi=fam_obs>float(fam_null['q975'])+TOL
        rank_obs=float(x['observed']['rank_gain'])
        rank_null=x['null']['rank_gain']
        rank_hi=rank_obs>float(rank_null['q975'])+TOL
        abs_obs=float(x['observed']['absolute_gain'])
        abs_null=x['null']['absolute_gain']
        abs_hi=abs_obs>float(abs_null['q975'])+TOL
        rev_obs=float(x['observed']['reversal_probability'])
        rev_null=x['null']['reversal_probability']
        rev_in_interval=float(rev_null['q025'])<=rev_obs<=float(rev_null['q975'])
        axes[key]={
          'observed_family_repeatability':fam_obs,
          'family_null_mean':fam_null['mean'],
          'family_null_95pct_range':[fam_null['q025'],fam_null['q975']],
          'family_null_p_ge_observed':fam_null['p_null_ge_observed'],
          'family_exceeds_null_upper_975':fam_hi,
          'observed_rank_portability_gain':rank_obs,
          'rank_null_mean':rank_null['mean'],
          'rank_null_95pct_range':[rank_null['q025'],rank_null['q975']],
          'rank_null_p_ge_observed':rank_null['p_null_ge_observed'],
          'rank_exceeds_null_upper_975':rank_hi,
          'observed_absolute_gain':abs_obs,
          'absolute_null_mean':abs_null['mean'],
          'absolute_null_95pct_range':[abs_null['q025'],abs_null['q975']],
          'absolute_exceeds_null_upper_975':abs_hi,
          'observed_reversal':rev_obs,
          'reversal_null_mean':rev_null['mean'],
          'reversal_null_95pct_range':[rev_null['q025'],rev_null['q975']],
          'reversal_within_null_95pct_range':rev_in_interval,
          'strong_axis':fam_hi and rank_hi,
          'n_trait_pairs':x['observed']['n_trait_pairs'],
          'valid_family_null_replicates':f['valid_null_replicates'],
        }
    both=all(z['strong_axis'] for z in axes.values())
    any_high=any(z['family_exceeds_null_upper_975'] or z['rank_exceeds_null_upper_975']
                 for z in axes.values())
    decision=('BEYOND_IDENTICAL_BM_K_NULL_ON_BOTH_AXES' if both else
              'PARTIAL_BM_NULL_EXCEEDANCE' if any_high else
              'NOT_BEYOND_IDENTICAL_BM_K_NULL')
    return {
      'version':'v0.1',
      'status':'AUSTRAITS_K_REAL_TREE_BM_NULL_INTERPRETED',
      'source_workflow_run':design['source_run'],
      'null_replicates':64,
      'fixed_graph':design['fixed_graph'],
      'decision':decision,
      'axes':axes,
      'conclusion_boundary':'Rejection of a same-rate independent Brownian process is not evidence for adaptive rewiring. Differences in trait covariance, evolutionary regime, measurement error, taxonomy or source coverage remain possibilities.',
      'post_outcome':True,
      'never_reclassify_preregistered_outcomes':True
    }

def main():
    p=argparse.ArgumentParser()
    for field in ['metrics','family','contract','out']:
        p.add_argument('--'+field,type=Path,required=True)
    a=p.parse_args()
    z=assess(json.loads(a.metrics.read_text()),
             json.loads(a.family.read_text()),
             json.loads(a.contract.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(z,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'decision':z['decision'],'axes':z['axes']},indent=2,sort_keys=True))
if __name__=='__main__':
    main()
