#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr

ap=argparse.ArgumentParser()
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--permutations",type=int,default=9999)
ap.add_argument("--seed",type=int,default=20261006)
a=ap.parse_args()
df=pd.read_csv(a.effects)
req={"family","trait_name","S3_rho","prune_only_rho"}
if not req.issubset(df.columns):raise SystemExit(f"missing columns {sorted(req-set(df.columns))}")
if df.family.nunique()<12 or df.trait_name.nunique()<4:raise SystemExit("final core below frozen minimum")

def rank_frame(d,col):
    parts=[]
    for fam,g in d.groupby("family",sort=True):
        if len(g)<2:continue
        h=g[["family","trait_name",col]].copy()
        r=rankdata(h[col].to_numpy(float),method="average")
        h["rank01"]=(r-1.0)/(len(g)-1.0);parts.append(h[["family","trait_name","rank01"]])
    if not parts:raise SystemExit("no rankable families")
    return pd.concat(parts,ignore_index=True)

ref=rank_frame(df,"S3_rho")
traits=sorted(ref.trait_name.unique());families=sorted(ref.family.unique())
tm={t:i for i,t in enumerate(traits)}
tc=ref.trait_name.map(tm).to_numpy(int)
counts=np.bincount(tc,minlength=len(traits))
if np.any(counts[tc]<=1):raise SystemExit("trait lacks out-of-family rank training observation")
fg=[np.asarray(idx,dtype=int) for idx in ref.groupby("family",sort=True).indices.values()]
rng=np.random.default_rng(a.seed)
orders=[np.argsort(rng.random((a.permutations,len(idx))),axis=1) for idx in fg]

def gain_only(d,col):
    z=rank_frame(d,col);trs=sorted(z.trait_name.unique());mp={t:i for i,t in enumerate(trs)}
    t=z.trait_name.map(mp).to_numpy(int);y=z.rank01.to_numpy(float);cnt=np.bincount(t,minlength=len(trs))
    ok=cnt[t]>1;y=y[ok];t=t[ok]
    sm=np.bincount(t,weights=y,minlength=len(trs));pred=(sm[t]-y)/(cnt[t]-1)
    s0=float(np.sum((y-.5)**2))
    return 1-float(np.sum((y-pred)**2))/s0

def analyse(col):
    z=rank_frame(df,col)
    if not np.array_equal(z[["family","trait_name"]].to_numpy(),ref[["family","trait_name"]].to_numpy()):
        raise SystemExit("rank graph differs across tree axes")
    y=z.rank01.to_numpy(float)
    sm=np.bincount(tc,weights=y,minlength=len(traits));pred=(sm[tc]-y)/(counts[tc]-1)
    s0=float(np.sum((y-.5)**2));s1=float(np.sum((y-pred)**2));gain=1-s1/s0
    yp=np.empty((a.permutations,len(y)),float)
    for idx,ordr in zip(fg,orders):yp[:,idx]=y[idx][ordr]
    tsum=np.zeros((a.permutations,len(traits)),float)
    for t in range(len(traits)):tsum[:,t]=yp[:,tc==t].sum(axis=1)
    pp=(tsum[:,tc]-yp)/(counts[tc]-1)
    null=1-np.sum((yp-pp)**2,axis=1)/s0
    p=float((1+np.sum(null>=gain))/(a.permutations+1))
    lot=[gain_only(df[df.trait_name!=t],col) for t in sorted(df.trait_name.unique())]
    lof=[gain_only(df[df.family!=f],col) for f in sorted(df.family.unique())]
    return {
      "gain":float(gain),"spearman_observed_vs_predicted":float(spearmanr(y,pred).statistic),
      "p_one_sided":p,"null_median":float(np.median(null)),
      "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
      "axis_pass":bool(gain>0 and p<=0.05),
      "leave_one_trait_gain_range":[float(min(lot)),float(max(lot))],
      "leave_one_family_gain_range":[float(min(lof)),float(max(lof))]
    }

s3=analyse("S3_rho");pr=analyse("prune_only_rho")
if s3["axis_pass"] and pr["axis_pass"]:decision="ROBUST_RANK_PORTABILITY"
elif s3["axis_pass"]:decision="BACKBONE_SENSITIVE_RANK_TENDENCY"
else:decision="NO_REPLICATED_RANK_PORTABILITY"
out={
  "version":"v0.1","status":"AUSTRAITS_RANK_PORTABILITY_ESTIMATED",
  "austraits_memory_effects_opened":True,
  "n_systems":len(df),"n_families":df.family.nunique(),"n_traits":df.trait_name.nunique(),
  "permutations":a.permutations,"seed":a.seed,
  "S3":s3,"prune_only":pr,
  "robust_rank_portability":bool(s3["axis_pass"] and pr["axis_pass"]),
  "decision":decision
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
