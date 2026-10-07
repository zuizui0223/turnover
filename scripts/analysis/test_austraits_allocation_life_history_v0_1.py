#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from itertools import combinations
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr

def disagreement_table(df,col,min_shared):
    prof={f:dict(zip(g.trait_name,g[col].astype(float))) for f,g in df[['family','trait_name',col]].dropna().groupby('family')}
    rows=[]
    for a,b in combinations(sorted(prof),2):
        shared=sorted(set(prof[a])&set(prof[b]))
        if len(shared)<min_shared:continue
        den=disc=0
        for x,y in combinations(shared,2):
            da=prof[a][x]-prof[a][y];db=prof[b][x]-prof[b][y]
            if da==0 or db==0:continue
            den+=1
            if (da>0)!=(db>0):disc+=1
        if den:
            rows.append({'family1':a,'family2':b,'shared_traits':len(shared),
                         'trait_pair_comparisons':den,'rank_disagreement':disc/den})
    return pd.DataFrame(rows)

def perm_test(pairs,pred,values,B,seed):
    fams=sorted(values)
    def v(a,b,mp):
        xa,xb=mp[a],mp[b]
        if pred=='perennial_distance':
            if xa['perennial_fraction'] is None or xb['perennial_fraction'] is None:return None
            return abs(xa['perennial_fraction']-xb['perennial_fraction'])
        if pred=='woody_distance':
            if xa['woody_fraction'] is None or xb['woody_fraction'] is None:return None
            return abs(xa['woody_fraction']-xb['woody_fraction'])
        if pred=='combined_strategy_distance':
            if any(xa[k] is None or xb[k] is None for k in ['perennial_z','woody_z']):return None
            return ((xa['perennial_z']-xb['perennial_z'])**2+(xa['woody_z']-xb['woody_z'])**2)**0.5
        raise KeyError(pred)
    def stat(mp):
        xs=[];ys=[]
        for r in pairs.itertuples(index=False):
            z=v(r.family1,r.family2,mp)
            if z is None or not np.isfinite(z):continue
            xs.append(float(z));ys.append(float(r.rank_disagreement))
        if len(xs)<3:return np.nan,len(xs)
        return float(spearmanr(xs,ys).statistic),len(xs)
    obs,n=stat(values)
    rng=np.random.default_rng(seed);null=np.empty(B)
    original=[values[f] for f in fams]
    for i in range(B):
        p=rng.permutation(len(fams))
        mp={f:original[p[j]] for j,f in enumerate(fams)}
        null[i]=stat(mp)[0]
    ok=np.isfinite(null)
    ppos=float((1+np.sum(null[ok]>=obs))/(1+ok.sum()))
    return {'n_family_pairs':int(n),'spearman':obs,'p_one_sided_positive':ppos,
            'null_median':float(np.nanmedian(null)),'null_q025':float(np.nanquantile(null,.025)),
            'null_q975':float(np.nanquantile(null,.975))}

ap=argparse.ArgumentParser()
ap.add_argument('--effects',type=Path,required=True)
ap.add_argument('--family-predictors',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
ap.add_argument('--permutations',type=int,default=9999)
ap.add_argument('--seed',type=int,default=20261007)
a=ap.parse_args()

e=pd.read_csv(a.effects)
e=e[e.log_domain_pass==True].copy()
p=pd.read_csv(a.family_predictors)
p=p[p.family.isin(e.family.unique())].copy()
for col in ['perennial_fraction','woody_fraction']:
    p[col]=pd.to_numeric(p[col],errors='coerce')
p['perennial_z']=(p.perennial_fraction-p.perennial_fraction.mean())/p.perennial_fraction.std(ddof=1)
wp=p.woody_fraction.dropna()
p['woody_z']=(p.woody_fraction-wp.mean())/wp.std(ddof=1)
vals={}
for r in p.itertuples(index=False):
    vals[r.family]={
      'perennial_fraction':None if pd.isna(r.perennial_fraction) else float(r.perennial_fraction),
      'woody_fraction':None if pd.isna(r.woody_fraction) else float(r.woody_fraction),
      'perennial_z':None if pd.isna(r.perennial_z) else float(r.perennial_z),
      'woody_z':None if pd.isna(r.woody_z) else float(r.woody_z)
    }

out={'version':'v0.1','status':'AUSTRAITS_ALLOCATION_DRIVER_LIFE_HISTORY_EXPLORATORY_ESTIMATED',
     'post_outcome_exploratory':True,'n_families':int(e.family.nunique()),'axes':{}}
for ai,(name,col) in enumerate([('log_S3','S3_log_rho'),('log_prune','prune_log_rho')]):
    out['axes'][name]={}
    for min_shared in [4,3]:
        pairs=disagreement_table(e,col,min_shared)
        block={}
        for pi,pred in enumerate(['perennial_distance','woody_distance','combined_strategy_distance']):
            block[pred]=perm_test(pairs,pred,vals,a.permutations,a.seed+100*ai+10*min_shared+pi)
        out['axes'][name][f'shared{min_shared}']=block

a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
