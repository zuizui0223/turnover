#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from itertools import combinations
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr

def disagreement(a,b,min_shared):
    shared=sorted(set(a)&set(b))
    if len(shared)<min_shared:return None,len(shared),0
    disc=den=0
    for x,y in combinations(shared,2):
        da=a[x]-a[y];db=b[x]-b[y]
        if da==0 or db==0:continue
        den+=1
        if (da>0)!=(db>0):disc+=1
    return (None if den==0 else disc/den),len(shared),den

def pair_table(df,col,min_shared):
    profiles={f:dict(zip(g.trait_name,g[col].astype(float))) for f,g in df[['family','trait_name',col]].dropna().groupby('family')}
    rows=[]
    for a,b in combinations(sorted(profiles),2):
        d,n,k=disagreement(profiles[a],profiles[b],min_shared)
        rows.append((a,b,n,k,d))
    return profiles,rows

def stat(dist,lookup,assignment):
    xs=[];ys=[]
    for r in dist.itertuples(index=False):
        a=assignment[r.family1];b=assignment[r.family2];z=lookup.get(tuple(sorted((a,b))))
        if z is None or not np.isfinite(z):continue
        xs.append(float(r.patristic_distance));ys.append(float(z))
    return (float(spearmanr(xs,ys).statistic) if len(xs)>=3 else np.nan),len(xs)

def run(df,dist,col,min_shared,B,seed):
    prof,rows=pair_table(df,col,min_shared)
    lookup={tuple(sorted((a,b))):float(d) for a,b,n,k,d in rows if d is not None and np.isfinite(d)}
    fams=sorted(prof);tree=sorted(set(dist.family1)|set(dist.family2))
    if fams!=tree:raise RuntimeError(f'family mismatch profiles={len(fams)} tree={len(tree)}')
    obs,n=stat(dist,lookup,{f:f for f in fams})
    rng=np.random.default_rng(seed);null=np.empty(B)
    arr=np.asarray(fams,dtype=object)
    for i in range(B):
        perm=rng.permutation(arr);null[i]=stat(dist,lookup,dict(zip(fams,perm.tolist())))[0]
    ok=np.isfinite(null);p=float((1+np.sum(null[ok]>=obs))/(1+ok.sum()))
    return {'column':col,'minimum_shared_traits':min_shared,'n_eligible_family_pairs':int(n),
            'spearman_distance_vs_rank_disagreement':obs,'permutation':{
            'replicates':B,'valid_replicates':int(ok.sum()),'p_one_sided_positive':p,
            'null_median':float(np.nanmedian(null)),'null_q025':float(np.nanquantile(null,.025)),'null_q975':float(np.nanquantile(null,.975))}}

ap=argparse.ArgumentParser()
ap.add_argument('--effects',type=Path,required=True);ap.add_argument('--distances',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True);ap.add_argument('--permutations',type=int,default=9999);ap.add_argument('--seed',type=int,default=20261007)
a=ap.parse_args()
df=pd.read_csv(a.effects);dist=pd.read_csv(a.distances)
if len(df)!=259 or df.family.nunique()!=42 or df.trait_name.nunique()!=14:raise RuntimeError('unexpected AusTraits final core')
out={'version':'v0.1','status':'AUSTRAITS_RANK_PHYLOGENY_EXPLORATORY_ESTIMATED','post_outcome_exploratory':True,
     'n_systems':len(df),'n_families':df.family.nunique(),'n_traits':df.trait_name.nunique(),
     'source_native':{
       'S3_shared4':run(df,dist,'S3_rho',4,a.permutations,a.seed),
       'prune_shared4':run(df,dist,'prune_only_rho',4,a.permutations,a.seed+1),
       'S3_shared3':run(df,dist,'S3_rho',3,a.permutations,a.seed+2),
       'prune_shared3':run(df,dist,'prune_only_rho',3,a.permutations,a.seed+3)
     }}
log=df[df.log_domain_pass==True].copy()
out['matched_log']={
 'S3_shared4':run(log,dist,'S3_log_rho',4,a.permutations,a.seed+4),
 'prune_shared4':run(log,dist,'prune_log_rho',4,a.permutations,a.seed+5)
}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
