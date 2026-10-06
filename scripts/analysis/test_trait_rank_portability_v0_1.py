#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

def prepare_ranks(df: pd.DataFrame, value_col: str):
    x=df[['family','trait_name',value_col]].dropna().copy()
    chunks=[]
    for fam,g in x.groupby('family', sort=True):
        if len(g)<2:
            continue
        r=rankdata(g[value_col].to_numpy(float), method='average')
        h=g[['family','trait_name']].copy()
        h['rank01']=(r-1.0)/(len(g)-1.0)
        chunks.append(h)
    ranks=pd.concat(chunks,ignore_index=True)
    trait_names=sorted(ranks.trait_name.unique())
    tmap={t:i for i,t in enumerate(trait_names)}
    tcode=ranks.trait_name.map(tmap).to_numpy(int)
    y=ranks.rank01.to_numpy(float)
    counts=np.bincount(tcode,minlength=len(trait_names)).astype(int)
    if np.any(counts[tcode] <= 1):
        raise RuntimeError('at least one retained observation lacks an out-of-family training value')
    fam_indices=[np.asarray(idx,dtype=int) for idx in ranks.groupby('family',sort=True).indices.values()]
    return ranks, y, tcode, counts, fam_indices

def gain_from_y(y: np.ndarray, tcode: np.ndarray, counts: np.ndarray):
    sums=np.bincount(tcode,weights=y,minlength=len(counts))
    pred=(sums[tcode]-y)/(counts[tcode]-1)
    sse0=float(np.sum((y-0.5)**2))
    sse1=float(np.sum((y-pred)**2))
    gain=1.0-sse1/sse0
    sp=float(spearmanr(y,pred).statistic)
    return gain, sp, sse0, sse1

def permutation_null(y,tcode,counts,fam_indices,B,seed):
    rng=np.random.default_rng(seed)
    null=np.empty(B,float)
    yp=np.empty_like(y)
    for b in range(B):
        for idx in fam_indices:
            yp[idx]=rng.permutation(y[idx])
        null[b]=gain_from_y(yp,tcode,counts)[0]
    return null

def pair_order_summary(df,value_col,min_cooccurrence=10):
    traits=sorted(df.trait_name.dropna().unique())
    pairs=[]; cons=[]
    for i,a in enumerate(traits):
        da=df[df.trait_name==a][['family',value_col]].rename(columns={value_col:'a'})
        for b in traits[i+1:]:
            db=df[df.trait_name==b][['family',value_col]].rename(columns={value_col:'b'})
            m=da.merge(db,on='family')
            if len(m)<min_cooccurrence:
                continue
            d=m.a-m.b
            pos=int((d>0).sum()); neg=int((d<0).sum()); n=pos+neg
            if not n:
                continue
            c=max(pos,neg)/n
            cons.append(c)
            pairs.append({
                'trait_a':a,'trait_b':b,'n_families':int(len(m)),
                'a_gt_b':pos,'a_lt_b':neg,'majority_consistency':c
            })
    arr=np.asarray(cons,float)
    return {
        'min_cooccurrence':min_cooccurrence,
        'n_pairs':len(pairs),
        'median_majority_consistency':float(np.median(arr)) if len(arr) else None,
        'mean_majority_consistency':float(np.mean(arr)) if len(arr) else None,
        'fraction_consistency_ge_0_75':float(np.mean(arr>=0.75)) if len(arr) else None,
        'pairs':pairs
    }

def analyse_axis(df,value_col,B,seed,min_pair_co):
    ranks,y,tcode,counts,fam_indices=prepare_ranks(df,value_col)
    gain,sp,sse0,sse1=gain_from_y(y,tcode,counts)
    null=permutation_null(y,tcode,counts,fam_indices,B,seed)
    trait_summary=(ranks.groupby('trait_name').rank01.agg(['count','mean','std']).reset_index()
                   .rename(columns={'count':'n_families','mean':'mean_rank01','std':'sd_rank01'})
                   .sort_values('mean_rank01').to_dict(orient='records'))
    return {
        'value_column':value_col,
        'n_ranked_systems':int(len(ranks)),
        'n_families':int(ranks.family.nunique()),
        'n_traits':int(ranks.trait_name.nunique()),
        'observed':{
            'gain':gain,'spearman':sp,
            'sse_baseline':sse0,'sse_trait':sse1
        },
        'permutation':{
            'replicates':B,'seed':seed,
            'null_median':float(np.median(null)),
            'null_q025':float(np.quantile(null,.025)),
            'null_q975':float(np.quantile(null,.975)),
            'p_one_sided':float((1+np.sum(null>=gain))/(B+1))
        },
        'pair_order':pair_order_summary(df,value_col,min_pair_co),
        'trait_mean_rank':trait_summary
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--effects',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--s3-column',default='S3_raw_rho')
    ap.add_argument('--prune-column',default='prune_raw_rho')
    ap.add_argument('--permutations',type=int,default=9999)
    ap.add_argument('--seed',type=int,default=20261006)
    ap.add_argument('--min-pair-cooccurrence',type=int,default=10)
    a=ap.parse_args()
    df=pd.read_csv(a.effects)
    miss={'family','trait_name',a.s3_column,a.prune_column}-set(df.columns)
    if miss:
        raise SystemExit(f'missing columns: {sorted(miss)}')
    out={
        'version':'v0.1',
        'estimand':'leave-one-family-out portability of within-family relative lability rank',
        'rank_definition':'Within each family, average rank of raw memory-loss rho scaled to [0,1]; 0=most conservative, 1=most labile. Families with fewer than two admitted traits are excluded.',
        'prediction':'For each family x trait observation, predict rank using the mean rank of that trait in all other families.',
        'baseline_prediction':0.5,
        'gain_definition':'1 - SSE(leave-one-family-out trait-rank prediction) / SSE(0.5 baseline)',
        'null':'Permute rank values among observed trait slots within each family, preserving the admitted family-trait graph and each family rank distribution.',
        'S3':analyse_axis(df,a.s3_column,a.permutations,a.seed,a.min_pair_cooccurrence),
        'prune_only':analyse_axis(df,a.prune_column,a.permutations,a.seed+1,a.min_pair_cooccurrence)
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    main()
