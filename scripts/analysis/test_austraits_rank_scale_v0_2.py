#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--matched-core",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--permutations",type=int,default=9999)
ap.add_argument("--seed",type=int,default=20261006)
a=ap.parse_args()
df=pd.read_csv(a.effects)
mc=pd.read_csv(a.matched_core)
keys=set(zip(mc.family,mc.trait_name))
x=df[[ (f,t) in keys for f,t in zip(df.family,df.trait_name) ]].copy()
if len(x)!=len(keys):raise SystemExit("matched-core/effect identity mismatch")
if x.family.nunique()<12 or x.trait_name.nunique()<4:raise SystemExit("matched core below frozen minimum")
for c in ["S3_raw_rho","prune_raw_rho","S3_log_rho","prune_log_rho"]:
    if x[c].isna().any():raise SystemExit(f"missing matched effect {c}")

def make_rank(d,col):
    parts=[]
    for fam,g in d.groupby("family",sort=True):
        if len(g)<2:continue
        z=g[["family","trait_name",col]].copy()
        rr=rankdata(z[col].to_numpy(float),method="average")
        z["rank01"]=(rr-1)/(len(z)-1);parts.append(z[["family","trait_name","rank01"]])
    return pd.concat(parts,ignore_index=True)

rank_ref=make_rank(x,"S3_raw_rho")
families=sorted(rank_ref.family.unique());traits=sorted(rank_ref.trait_name.unique())
fm={f:i for i,f in enumerate(families)};tm={t:i for i,t in enumerate(traits)}
fi=rank_ref.family.map(fm).to_numpy(int);ti=rank_ref.trait_name.map(tm).to_numpy(int)
fg=[np.flatnonzero(fi==k) for k in range(len(families))]
tc=np.bincount(ti,minlength=len(traits))
rng=np.random.default_rng(a.seed)
orders={f:np.argsort(rng.random((a.permutations,len(idx))),axis=1) for f,idx in enumerate(fg)}

def rank_test(col):
    r=make_rank(x,col)
    if not np.array_equal(r[["family","trait_name"]].to_numpy(),rank_ref[["family","trait_name"]].to_numpy()):
        raise SystemExit("rank graph changed across scales")
    y=r.rank01.to_numpy(float);s=np.bincount(ti,weights=y,minlength=len(traits))
    pred=(s[ti]-y)/(tc[ti]-1);s0=float(np.sum((y-.5)**2));gain=1-float(np.sum((y-pred)**2))/s0
    yp=np.empty((a.permutations,len(y)),float)
    for f,idx in enumerate(fg):yp[:,idx]=y[idx][orders[f]]
    tsum=np.zeros((a.permutations,len(traits)))
    for t in range(len(traits)):tsum[:,t]=yp[:,ti==t].sum(axis=1)
    pp=(tsum[:,ti]-yp)/(tc[ti]-1);null=1-np.sum((yp-pp)**2,axis=1)/s0
    p=(1+np.sum(null>=gain))/(a.permutations+1)
    return {"gain":float(gain),"spearman_observed_vs_predicted":float(spearmanr(y,pred).statistic),
            "p_one_sided":float(p),"null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
            "axis_pass":bool(gain>0 and p<=.05)}

def reversal(col,minco):
    vals=[];weights=[];trs=sorted(x.trait_name.unique())
    for i,A in enumerate(trs):
        da=x[x.trait_name==A][["family",col]].rename(columns={col:"a"})
        for B in trs[i+1:]:
            db=x[x.trait_name==B][["family",col]].rename(columns={col:"b"})
            m=da.merge(db,on="family")
            if len(m)<minco:continue
            d=m.a-m.b;pos=int((d>0).sum());neg=int((d<0).sum());n=pos+neg
            if n<2:continue
            vals.append(2*pos*neg/(n*(n-1)));weights.append(n*(n-1)/2)
    return {"n_trait_pairs":len(vals),"weighted_probability":float(np.average(vals,weights=weights)) if vals else None}

def meanrank(col):
    return make_rank(x,col).groupby("trait_name").rank01.mean()
axes={"raw_S3":"S3_raw_rho","raw_prune":"prune_raw_rho","log_S3":"S3_log_rho","log_prune":"prune_log_rho"}
out={"version":"v0.2","status":"AUSTRAITS_MATCHED_RAW_LOG_RANK_ANALYSIS_ESTIMATED","austraits_memory_effects_opened":True,
     "n_systems":len(x),"n_families":x.family.nunique(),"n_traits":x.trait_name.nunique(),
     "permutations":a.permutations,"seed":a.seed,"rank_portability":{},"direct_reordering":{}}
for name,col in axes.items():
    out["rank_portability"][name]=rank_test(col)
    out["direct_reordering"][name]={"min2":reversal(col,2),"min10":reversal(col,10)}
mr={k:meanrank(c) for k,c in axes.items()}
out["mean_rank_correlations"]={
 "raw_S3_vs_prune":float(spearmanr(mr["raw_S3"],mr["raw_prune"]).statistic),
 "log_S3_vs_prune":float(spearmanr(mr["log_S3"],mr["log_prune"]).statistic),
 "S3_raw_vs_log":float(spearmanr(mr["raw_S3"],mr["log_S3"]).statistic),
 "prune_raw_vs_log":float(spearmanr(mr["raw_prune"],mr["log_prune"]).statistic)
}
out["scale_decision"]="SCALE_ROBUST" if all(out["rank_portability"][k]["axis_pass"] for k in axes) or all(not out["rank_portability"][k]["axis_pass"] for k in axes) else "SCALE_SENSITIVE"
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
