#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

def ranked(df, col):
    chunks=[]
    for fam,g in df[['family','trait_name',col]].dropna().groupby('family',sort=True):
        if len(g)<2:
            continue
        r=rankdata(g[col].to_numpy(float),method='average')
        h=g[['family','trait_name']].copy()
        h['rank01']=(r-1.0)/(len(g)-1.0)
        chunks.append(h)
    return pd.concat(chunks,ignore_index=True)

def portability(df,col):
    z=ranked(df,col)
    traits=sorted(z.trait_name.unique()); mp={t:i for i,t in enumerate(traits)}
    tc=z.trait_name.map(mp).to_numpy(int); y=z.rank01.to_numpy(float)
    cnt=np.bincount(tc,minlength=len(traits))
    sm=np.bincount(tc,weights=y,minlength=len(traits))
    ok=cnt[tc]>1
    y=y[ok]; tc=tc[ok]
    pred=(sm[tc]-y)/(cnt[tc]-1)
    s0=float(np.sum((y-.5)**2)); s1=float(np.sum((y-pred)**2))
    return 1-s1/s0, float(spearmanr(y,pred).statistic)

def perm_null(df,col,B,seed):
    z=ranked(df,col)
    traits=sorted(z.trait_name.unique()); mp={t:i for i,t in enumerate(traits)}
    tc=z.trait_name.map(mp).to_numpy(int); y=z.rank01.to_numpy(float)
    cnt=np.bincount(tc,minlength=len(traits))
    fam_idx=[np.asarray(i,dtype=int) for i in z.groupby('family',sort=True).indices.values()]
    def gain(yy):
        sm=np.bincount(tc,weights=yy,minlength=len(traits))
        pred=(sm[tc]-yy)/(cnt[tc]-1)
        return 1-float(np.sum((yy-pred)**2))/float(np.sum((yy-.5)**2))
    obs=gain(y); rng=np.random.default_rng(seed); yp=np.empty_like(y); null=np.empty(B)
    for b in range(B):
        for idx in fam_idx:
            yp[idx]=rng.permutation(y[idx])
        null[b]=gain(yp)
    return {
        'gain':obs,
        'p_one_sided':float((1+np.sum(null>=obs))/(B+1)),
        'null_median':float(np.median(null)),
        'null_q025':float(np.quantile(null,.025)),
        'null_q975':float(np.quantile(null,.975))
    }

def omission_ranges(df,col):
    lot=[]
    for t in sorted(df.trait_name.unique()):
        lot.append(portability(df[df.trait_name!=t],col)[0])
    lof=[]
    for f in sorted(df.family.unique()):
        lof.append(portability(df[df.family!=f],col)[0])
    return {
        'leave_one_trait_gain_range':[float(min(lot)),float(max(lot))],
        'leave_one_family_gain_range':[float(min(lof)),float(max(lof))],
        'all_leave_one_trait_positive':bool(all(x>0 for x in lot)),
        'all_leave_one_trait_negative':bool(all(x<0 for x in lot)),
        'all_leave_one_family_positive':bool(all(x>0 for x in lof)),
        'all_leave_one_family_negative':bool(all(x<0 for x in lof))
    }

def pair_order(df,col,min_co=10):
    vals=[]
    trs=sorted(df.trait_name.unique())
    for i,a in enumerate(trs):
        da=df[df.trait_name==a][['family',col]].rename(columns={col:'a'})
        for b in trs[i+1:]:
            db=df[df.trait_name==b][['family',col]].rename(columns={col:'b'})
            m=da.merge(db,on='family')
            if len(m)<min_co:
                continue
            d=m.a-m.b; pos=int((d>0).sum()); neg=int((d<0).sum())
            if pos+neg:
                vals.append(max(pos,neg)/(pos+neg))
    a=np.asarray(vals,float)
    return {
        'minimum_cooccurrence_families':min_co,
        'n_pairs':len(vals),
        'median_majority_consistency':float(np.median(a)),
        'mean_majority_consistency':float(np.mean(a)),
        'fraction_consistency_ge_0_75':float(np.mean(a>=.75))
    }

def family_pair_rank(df,col,min_shared=3):
    fs=sorted(df.family.unique()); vals=[]
    for i,a in enumerate(fs):
        da=df[df.family==a][['trait_name',col]]
        for b in fs[i+1:]:
            db=df[df.family==b][['trait_name',col]]
            m=da.merge(db,on='trait_name',suffixes=('_a','_b'))
            if len(m)>=min_shared:
                vals.append(float(spearmanr(m[col+'_a'],m[col+'_b']).statistic))
    return {'minimum_shared_traits':min_shared,'n_family_pairs':len(vals),'mean_spearman':float(np.mean(vals))}

def trait_mean_rank_cross_axis(df,s3,prune):
    a=ranked(df,s3).groupby('trait_name').rank01.mean()
    b=ranked(df,prune).groupby('trait_name').rank01.mean()
    m=pd.concat([a,b],axis=1).dropna()
    return float(spearmanr(m.iloc[:,0],m.iloc[:,1]).statistic)

def latent_reversal(sigma_trait,sigma_system):
    r=float(sigma_trait/(sigma_trait+sigma_system))
    return {
        'contrast_correlation':r,
        'expected_cross_family_rank_reversal_probability':float(math.acos(r)/math.pi),
        'expected_kendall_tau_between_lineage_rankings':float(2/math.pi*math.asin(r)),
        'expected_spearman_between_lineage_rankings':float(6/math.pi*math.asin(r/2))
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--effects',type=Path,required=True)
    ap.add_argument('--measurement-json',type=Path,required=True)
    ap.add_argument('--measurement-bootstrap',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--permutations',type=int,default=9999)
    ap.add_argument('--seed',type=int,default=20261006)
    a=ap.parse_args()
    d=pd.read_csv(a.effects); mj=json.loads(a.measurement_json.read_text())
    axes={'S3':'S3_raw_rho','prune_only':'prune_raw_rho'}
    out={'version':'v0.1','status':'POST_OUTCOME_EXPLORATORY_TRAIT_RANK_REORDERING_ESTIMATED',
         'evidence':{'n_systems':int(len(d)),'n_families':int(d.family.nunique()),'n_traits':int(d.trait_name.nunique())},
         'rank_portability':{},'trait_pair_ordering':{},'family_pair_rank_correlation':{}}
    for k,col in axes.items():
        g,sp=portability(d,col); pn=perm_null(d,col,a.permutations,a.seed+(0 if k=='S3' else 1))
        out['rank_portability'][k]={'gain':g,'spearman_observed_vs_predicted':sp,**pn,**omission_ranges(d,col)}
        out['trait_pair_ordering'][k]=pair_order(d,col)
        out['family_pair_rank_correlation'][k]=family_pair_rank(d,col,3)
        out['family_pair_rank_correlation'][k+'_shared4']=family_pair_rank(d,col,4)
    out['global_trait_spectrum']={'S3_vs_prune_trait_mean_rank_spearman':trait_mean_rank_cross_axis(d,*axes.values())}
    out['measurement_aware_reordering']={}
    for k in axes:
        q=mj['measurement_aware'][k]
        out['measurement_aware_reordering'][k]={
            'sigma2_trait':q['sigma2_trait'],'sigma2_system':q['sigma2_system'],
            **latent_reversal(q['sigma2_trait'],q['sigma2_system'])
        }
    if a.measurement_bootstrap and a.measurement_bootstrap.exists():
        b=pd.read_csv(a.measurement_bootstrap)
        b=b[b.success.astype(bool)]
        r=b.sigma2_trait/(b.sigma2_trait+b.sigma2_system)
        p=np.arccos(r)/np.pi
        out['measurement_aware_reordering']['S3']['two_way_cluster_bootstrap']={
            'replicates':int(len(p)),
            'reversal_probability_median':float(np.median(p)),
            'reversal_probability_q025':float(np.quantile(p,.025)),
            'reversal_probability_q975':float(np.quantile(p,.975)),
            'fraction_reversal_gt_0_25':float(np.mean(p>.25)),
            'fraction_reversal_gt_0_333333':float(np.mean(p>(1/3))),
            'fraction_reversal_gt_0_40':float(np.mean(p>.40))
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    main()
