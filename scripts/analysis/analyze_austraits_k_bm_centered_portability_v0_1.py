#!/usr/bin/env python3
"""Calibrate AusTraits log(K) trait portability against observed-tree Brownian expectations.

Uses the frozen 254-system, 42-family, 13-trait graph and 64 Brownian
replicates per system. Null replicate r is centered/scaled ONLY by the
remaining 63 null draws, so its own realization never determines its
normalizing reference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata

AXES={'S3':'S3_logK','prune_only':'prune_logK'}

def prediction_gains(graph:pd.DataFrame, values:np.ndarray)->dict:
    """Match frozen held-out-family trait prediction and within-family rank gain."""
    if len(values)!=len(graph):
        raise ValueError('effect length differs from frozen graph')
    if not np.isfinite(values).all():
        raise ValueError('nonfinite effect')
    fs=pd.Categorical(graph['family'])
    ts=pd.Categorical(graph['trait_name'])
    family=fs.codes
    trait=ts.codes
    nf=len(fs.categories)
    nt=len(ts.categories)
    n=len(graph)
    fc=np.bincount(family,minlength=nf)
    tc=np.bincount(trait,minlength=nt)
    if np.any(fc[family]<2) or np.any(tc[trait]<2):
        raise ValueError('held-out family/trait support unavailable')
    fam_sum=np.bincount(family,weights=values,minlength=nf)
    trait_sum=np.bincount(trait,weights=values,minlength=nt)
    baseline=(values.sum()-fam_sum[family])/(n-fc[family])
    trait_pred=(trait_sum[trait]-values)/(tc[trait]-1)
    denom=np.sum((values-baseline)**2)
    if denom<=0:raise ValueError('zero absolute prediction denominator')
    absolute_gain=1-float(np.sum((values-trait_pred)**2))/denom

    ranks=np.empty(n,dtype=float)
    for f in range(nf):
        ids=np.flatnonzero(family==f)
        if len(ids)<2:raise ValueError('family rank undefined')
        ranks[ids]=(rankdata(values[ids],method='average')-1)/(len(ids)-1)
    rank_sum=np.bincount(trait,weights=ranks,minlength=nt)
    rank_pred=(rank_sum[trait]-ranks)/(tc[trait]-1)
    rank_baseline=np.sum((ranks-0.5)**2)
    if rank_baseline<=0:raise ValueError('zero rank prediction denominator')
    rank_gain=1-float(np.sum((ranks-rank_pred)**2))/rank_baseline
    return {'absolute_gain':float(absolute_gain),'rank_gain':float(rank_gain)}

def audited_arrays(observed:pd.DataFrame,
                   null:pd.DataFrame,axis:str,replicates:int)->tuple[pd.DataFrame,np.ndarray,np.ndarray]:
    col=AXES[axis]
    keys=['system_id','family','trait_name']
    if observed[keys].duplicated().any():
        raise ValueError('duplicate empirical graph cell')
    if (len(observed),observed.family.nunique(),observed.trait_name.nunique())!=(254,42,13):
        raise ValueError('unexpected empirical graph')
    if null[keys+['replicate']].duplicated().any():
        raise ValueError('duplicate null system-replicate cell')
    if len(null)!=254*replicates:
        raise ValueError('incomplete null graph')
    if set(null.system_id)!=set(observed.system_id):
        raise ValueError('null and observed system sets differ')
    nmap=observed.set_index('system_id')[['family','trait_name']]
    matches=null[['system_id','family','trait_name']].drop_duplicates().set_index('system_id')
    if not nmap.sort_index().equals(matches.sort_index()):
        raise ValueError('null family/trait identity changed')
    if set(null.replicate)!=set(range(replicates)):
        raise ValueError('incorrect null replicate identities')
    observed=observed.sort_values(['family','trait_name']).reset_index(drop=True)
    null_pivot=null.pivot(index='system_id',columns='replicate',values=col)
    null_pivot=null_pivot.loc[observed.system_id,range(replicates)]
    y=observed[col].to_numpy(float)
    m=null_pivot.to_numpy(float)
    if not np.isfinite(y).all() or not np.isfinite(m).all():
        raise ValueError('nonfinite K values')
    return observed,y,m

def one_axis(graph:pd.DataFrame,y:np.ndarray,m:np.ndarray)->dict:
    B=m.shape[1]
    mu=m.mean(axis=1)
    var=m.var(axis=1,ddof=1)
    if np.any(var<=1e-12):
        raise ValueError('zero Brownian reference variance')
    v=np.sqrt(var)
    observed={'excess':prediction_gains(graph,y-mu),
              'standardized_excess':prediction_gains(graph,(y-mu)/v)}
    null_records={norm:[] for norm in observed}
    for b in range(B):
        z=m[:,b]
        m0=(B*mu-z)/(B-1)
        remaining_sumsq=((B-1)*var+B*mu*mu-z*z)
        remaining_var=(remaining_sumsq-(B-1)*m0*m0)/(B-2)
        if np.any(remaining_var<=1e-12):
            raise ValueError('invalid leave-one-replicate-out reference variance')
        excess=z-m0
        null_records['excess'].append(prediction_gains(graph,excess))
        null_records['standardized_excess'].append(
             prediction_gains(graph,excess/np.sqrt(remaining_var)))
    results={}
    for norm,empirical in observed.items():
        comparisons={}
        for k in ['rank_gain','absolute_gain']:
            x=np.array([z[k] for z in null_records[norm]])
            comparisons[k]={
              'observed':empirical[k],
              'null_mean':float(x.mean()),
              'null_q025':float(np.quantile(x,.025)),
              'null_q975':float(np.quantile(x,.975)),
              'p_null_ge_observed':float((1+np.sum(x>=empirical[k]))/(B+1)),
              'exceeds_null_q975':bool(empirical[k]>np.quantile(x,.975))
            }
        results[norm]=comparisons
    return {'normalizations':results,
            'distribution_of_Brownian_reference_sd':{
              'min':float(v.min()),'median':float(np.median(v)),
              'max':float(v.max())},
            'same_process_reference_replicates':B}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--observed-K',type=Path,required=True)
    p.add_argument('--null-table',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--replicates',type=int,default=64)
    a=p.parse_args()
    observed=pd.read_csv(a.observed_K)
    null=pd.read_csv(a.null_table)
    result={
      'version':'v0.1',
      'status':'AUSTRAITS_REAL_TREE_BM_CENTERED_K_PORTABILITY_ESTIMATED',
      'fixed_graph':{'systems':254,'families':42,'traits':13},
      'replicates':a.replicates,
      'post_outcome_exploratory':True,
      'axes':{},
      'hard_nonclaims':[
        'Centering and scaling remove only features predicted by the chosen equal-rate Brownian reference model.',
        'Leave-one-simulation-out centering prevents self-referential null calibration.',
        'A significant result cannot by itself identify adaptive or genetic mechanisms.'
      ]
    }
    for axis in AXES:
        graph,y,m=audited_arrays(observed,null,axis,a.replicates)
        result['axes'][axis]=one_axis(graph,y,m)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({
      axis:{norm:{k:vals['observed'] for k,vals in stats.items()}
            for norm,stats in d['normalizations'].items()}
      for axis,d in result['axes'].items()},indent=2))
if __name__=='__main__':
    main()
