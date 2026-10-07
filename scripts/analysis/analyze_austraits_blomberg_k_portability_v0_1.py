#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from itertools import combinations
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import rankdata,spearmanr

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True);ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--permutations",type=int,default=9999);ap.add_argument("--seed",type=int,default=20261007)
a=ap.parse_args();df=pd.read_csv(a.effects)

def abs_port(col,seed):
    fams=sorted(df.family.unique());trs=sorted(df.trait_name.unique())
    fm={f:i for i,f in enumerate(fams)};tm={t:i for i,t in enumerate(trs)}
    fi=np.array([fm[z] for z in df.family]);ti=np.array([tm[z] for z in df.trait_name]);y=df[col].to_numpy(float)
    fg=[np.flatnonzero(fi==i) for i in range(len(fams))]
    fc=np.bincount(fi,minlength=len(fams));tc=np.bincount(ti,minlength=len(trs))
    total=y.sum();fs=np.bincount(fi,weights=y,minlength=len(fams));ts=np.bincount(ti,weights=y,minlength=len(trs))
    base=(total-fs[fi])/(len(y)-fc[fi]);pred=(ts[ti]-y)/(tc[ti]-1)
    s0=np.sum((y-base)**2);gain=1-np.sum((y-pred)**2)/s0
    rng=np.random.default_rng(seed);null=np.empty(a.permutations)
    yp=np.empty_like(y)
    for b in range(a.permutations):
        for idx in fg:yp[idx]=rng.permutation(y[idx])
        ss=np.bincount(ti,weights=yp,minlength=len(trs));pp=(ss[ti]-yp)/(tc[ti]-1)
        null[b]=1-np.sum((yp-pp)**2)/s0
    p=(1+np.sum(null>=gain))/(a.permutations+1)
    return {"gain":float(gain),"p_one_sided":float(p),"axis_pass":bool(gain>0 and p<=.05)}

def rank_port(col,seed):
    parts=[]
    for fam,g in df.groupby("family",sort=True):
        h=g[["family","trait_name",col]].copy();r=rankdata(h[col].to_numpy(float),method="average")
        h["rank"]=(r-1)/(len(h)-1);parts.append(h[["family","trait_name","rank"]])
    z=pd.concat(parts,ignore_index=True);trs=sorted(z.trait_name.unique());tm={t:i for i,t in enumerate(trs)}
    ti=z.trait_name.map(tm).to_numpy(int);y=z["rank"].to_numpy(float);cnt=np.bincount(ti,minlength=len(trs))
    sm=np.bincount(ti,weights=y,minlength=len(trs));pred=(sm[ti]-y)/(cnt[ti]-1)
    s0=np.sum((y-.5)**2);gain=1-np.sum((y-pred)**2)/s0
    groups=[np.asarray(idx,dtype=int) for idx in z.groupby("family",sort=True).indices.values()]
    rng=np.random.default_rng(seed);null=np.empty(a.permutations);yp=np.empty_like(y)
    for b in range(a.permutations):
        for idx in groups:yp[idx]=rng.permutation(y[idx])
        ss=np.bincount(ti,weights=yp,minlength=len(trs));pp=(ss[ti]-yp)/(cnt[ti]-1)
        null[b]=1-np.sum((yp-pp)**2)/s0
    p=(1+np.sum(null>=gain))/(a.permutations+1)
    return {"gain":float(gain),"p_one_sided":float(p),"spearman_observed_vs_predicted":float(spearmanr(y,pred).statistic),
            "axis_pass":bool(gain>0 and p<=.05)}

def reversal(col,minco=10):
    obs=den=maxobs=0;npairs=0
    for A,B in combinations(sorted(df.trait_name.unique()),2):
        da=df[df.trait_name==A][["family",col]].rename(columns={col:"a"})
        db=df[df.trait_name==B][["family",col]].rename(columns={col:"b"})
        m=da.merge(db,on="family")
        if len(m)<minco:continue
        d=m.a-m.b;pos=int((d>0).sum());neg=int((d<0).sum());n=pos+neg
        if n<2:continue
        obs+=pos*neg;den+=n*(n-1)/2;maxobs+=(n//2)*(n-n//2);npairs+=1
    return {"n_trait_pairs":npairs,"weighted_reversal_probability":float(obs/den),
            "fraction_pair_specific_maximum":float(obs/maxobs)}

out={"version":"v0.1","status":"AUSTRAITS_BLOMBERG_K_PORTABILITY_ESTIMATED","prune_primary":{}, "S3_sensitivity":{}}
for name,col,seed in [("prune_primary","prune_logK",a.seed),("S3_sensitivity","S3_logK",a.seed+1)]:
    out[name]={"absolute_portability":abs_port(col,seed),
               "rank_portability":rank_port(col,seed+100),
               "pair_order_reversal":reversal(col,10)}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
