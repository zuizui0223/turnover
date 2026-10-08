#!/usr/bin/env python3
"""Compare AusTraits observed K to identical shared-OU process on exact tree sets.

There are exactly three predefined OU alpha scenarios; do not select the best
null post hoc. Reuses the frozen absolute, rank and reversal prediction rules.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from aggregate_austraits_k_brownian_null_v0_1 import (
    rank_gain,absolute_gain,reversal
)

SCENARIOS=('c0p25','c1','c4')
AXES={'S3':'S3_logK','prune_only':'prune_logK'}
N=254
B=256

def verify_archived_K_identity(sid:str,axis:str,meta:dict,r,col:str)->None:
    """Check OU reassembly against its exact frozen K, allowing only known
    independent 4-decimal rounding of the separately archived logK column.
    """
    frozen_K = float(getattr(r, 'S3_K' if axis == 'S3' else 'prune_K'))
    frozen_logK = float(getattr(r,col))
    reconstructed_logK = float(meta['observed_logK'])
    if not (np.isfinite(frozen_K) and frozen_K > 0 and
            np.isfinite(frozen_logK) and np.isfinite(reconstructed_logK)):
        raise ValueError('OU K identity has nonfinite values '+sid+' '+axis)
    if abs(reconstructed_logK - np.log(frozen_K)) > 3e-10:
        raise ValueError('OU logK differs from archived K '+sid+' '+axis)
    # Four-decimal K and four-decimal log(K) were rounded independently;
    # on the original K scale, combine their strict rounding allowances.
    tolerance = 0.00006 * (1.0 + max(1.0, frozen_K))
    if abs(np.exp(frozen_logK) - frozen_K) > tolerance:
        raise ValueError('inconsistent archived K and logK '+sid+' '+axis)


def normalize(rows:pd.DataFrame,expected:pd.DataFrame)->pd.DataFrame:
    z=rows.sort_values(['family','trait_name']).reset_index(drop=True)
    if not z[['system_id','family','trait_name']].equals(
         expected[['system_id','family','trait_name']]):
        raise ValueError("OU system graph is not the fixed observed K graph")
    return z

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-dir',type=Path,required=True)
    ap.add_argument('--observed-K',type=Path,required=True)
    ap.add_argument('--time-reference',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--tables-dir',type=Path,required=True)
    a=ap.parse_args()
    observed=pd.read_csv(a.observed_K)
    if (len(observed),observed.family.nunique(),observed.trait_name.nunique())!=(254,42,13):
        raise ValueError('K observed matrix changed')
    observed=observed.sort_values(['family','trait_name']).reset_index(drop=True)
    reference=json.loads(a.time_reference.read_text())
    if reference.get('status')!='AUSTRAITS_REAL_TREE_OU_TIME_REFERENCE_FROZEN' or reference.get('n_systems')!=254:
        raise ValueError('invalid OU time reference')
    o_map={r.system_id:r for r in observed.itertuples(index=False)}
    systems={}
    for file in sorted(a.input_dir.glob("*.json")):
        z=json.loads(file.read_text())
        sid=z.get('system_id')
        if z.get('status')!='AUSTRAITS_REAL_TREE_SHARED_OU_NULL_SYSTEM_ESTIMATED':
            raise ValueError('bad OU input '+str(file))
        if sid in systems or sid not in o_map:
            raise ValueError('unexpected/duplicate OU system '+str(sid))
        r=o_map[sid]
        if (z['family'],z['trait_name'])!=(r.family,r.trait_name):
            raise ValueError('fixed OU trait-family identity failure')
        if abs(z['T_ref']-reference['T_ref'])>1e-8*reference['T_ref']:
            raise ValueError('OU alpha reference differs among systems')
        for axis,col in AXES.items():
            meta=z['axes'][axis]
            verify_archived_K_identity(sid,axis,meta,r,col)
            if meta['relative_fast_K_error']>.00021:
                raise ValueError('fast OU K failed K validation')
            for label in SCENARIOS:
                scenario=meta['scenarios'][label]
                if len(scenario['logK'])!=B:
                    raise ValueError('incomplete null K draws')
                if abs(scenario['alpha']-reference['absolute_alpha_grid'][label])>1e-10*scenario['alpha']:
                    raise ValueError('OU alpha differs across trait systems')
        systems[sid]=z
    if set(systems)!=set(o_map):
        raise ValueError(f"missing OU system results: {len(set(o_map)-set(systems))}")

    out={
      'version':'v0.1',
      'status':'AUSTRAITS_REAL_TREE_SHARED_OU_K_METRIC_NULL_ESTIMATED',
      'observed_graph':{'systems':254,'families':42,'traits':13},
      'replicates_per_scenario':B,
      'scenarios':{},
      'post_BM_outcome_pre_OU_outcome_design':True,
      'time_reference':reference,
      'hard_nonclaims':['Equal OU is one specified alternative; its acceptance does not prove OU is the true process.',
                        'Null draws are independent across traits and ignore among-trait evolutionary covariance.',
                        'Observed exact trees and trait tip support are conditioned on, not inferred jointly.']
    }
    a.tables_dir.mkdir(parents=True,exist_ok=True)
    for label in SCENARIOS:
        items=[]
        for rep in range(B):
            for r in observed.itertuples(index=False):
                z=systems[r.system_id]
                items.append({
                  'scenario':label,'replicate':rep,
                  'system_id':r.system_id,
                  'family':r.family,
                  'trait_name':r.trait_name,
                  'S3_logK':float(z['axes']['S3']['scenarios'][label]['logK'][rep]),
                  'prune_logK':float(z['axes']['prune_only']['scenarios'][label]['logK'][rep])
                })
        df=pd.DataFrame(items).sort_values(['replicate','family','trait_name'])
        assert (len(df),df.family.nunique(),df.trait_name.nunique())==(254*B,42,13)
        if not np.isfinite(df[['S3_logK','prune_logK']].to_numpy()).all():
            raise ValueError('nonfinite OU K')
        outfile=a.tables_dir/f"null_effects_{label}.csv"
        df.to_csv(outfile,index=False)
        scenario_out={
          'dimensionless_alpha':{'c0p25':.25,'c1':1.,'c4':4.}[label],
          'absolute_alpha':reference['absolute_alpha_grid'][label],
          'axes':{}
        }
        for axis,col in AXES.items():
            obs={'rank_gain':rank_gain(observed,col),
                 'absolute_gain':absolute_gain(observed,col)}
            obs['reversal_probability'],obs['n_trait_pairs']=reversal(observed,col)
            draws=[]
            for rep,g in df.groupby('replicate',sort=True):
                row={'replicate':int(rep),'rank_gain':rank_gain(g,col),
                     'absolute_gain':absolute_gain(g,col)}
                row['reversal_probability'],row['n_trait_pairs']=reversal(g,col)
                draws.append(row)
            nul={}
            for metric in ['rank_gain','absolute_gain','reversal_probability']:
                x=np.array([row[metric] for row in draws],float)
                nul[metric]={
                  'mean':float(x.mean()),
                  'q025':float(np.quantile(x,.025)),
                  'q975':float(np.quantile(x,.975)),
                  'p_null_ge_observed':float((1+(x>=obs[metric]).sum())/(B+1)),
                  'p_null_le_observed':float((1+(x<=obs[metric]).sum())/(B+1))
                }
            scenario_out['axes'][axis]={'observed':obs,'null':nul}
        out['scenarios'][label]=scenario_out
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],
         'n_scenarios':len(out['scenarios']),
         'K_rank_gain_observed':out['scenarios']['c1']['axes']['prune_only']['observed']['rank_gain']},
         indent=2))
if __name__=='__main__':main()
