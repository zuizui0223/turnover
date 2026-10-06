#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr

AXES={
  "cleaned_raw_S3":"S3_raw_rho",
  "cleaned_raw_prune":"prune_raw_rho",
  "cleaned_log_S3":"S3_log_rho",
  "cleaned_log_prune":"prune_log_rho"
}

def ranks(df,col):
    out=[]
    for fam,g in df[["family","trait_name",col]].dropna().groupby("family",sort=True):
        if len(g)<2: continue
        r=rankdata(g[col].to_numpy(float),method="average")
        h=g[["family","trait_name"]].copy()
        h["rank01"]=(r-1)/(len(g)-1)
        out.append(h)
    return pd.concat(out,ignore_index=True)

def portability(df,col,B,seed):
    z=ranks(df,col); traits=sorted(z.trait_name.unique()); tm={t:i for i,t in enumerate(traits)}
    tc=z.trait_name.map(tm).to_numpy(int); y=z.rank01.to_numpy(float)
    n=np.bincount(tc,minlength=len(traits)); famidx=[np.asarray(v,dtype=int) for v in z.groupby("family",sort=True).indices.values()]
    if np.any(n[tc]<=1): raise RuntimeError("trait lacks held-out-family training value")
    def gain(yy):
        s=np.bincount(tc,weights=yy,minlength=len(traits)); pred=(s[tc]-yy)/(n[tc]-1)
        return 1-float(np.sum((yy-pred)**2))/float(np.sum((yy-.5)**2)),float(spearmanr(yy,pred).statistic)
    obs,sp=gain(y); rng=np.random.default_rng(seed); yp=np.empty_like(y); null=np.empty(B)
    for b in range(B):
        for idx in famidx: yp[idx]=rng.permutation(y[idx])
        null[b]=gain(yp)[0]
    lot=[portability_gain(df[df.trait_name!=t],col) for t in sorted(df.trait_name.unique())]
    lof=[portability_gain(df[df.family!=f],col) for f in sorted(df.family.unique())]
    return {
      "gain":obs,"spearman_observed_vs_predicted":sp,
      "p_one_sided":float((1+np.sum(null>=obs))/(B+1)),
      "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
      "leave_one_trait_gain_range":[float(min(lot)),float(max(lot))],
      "leave_one_family_gain_range":[float(min(lof)),float(max(lof))]
    }

def portability_gain(df,col):
    z=ranks(df,col); traits=sorted(z.trait_name.unique()); tm={t:i for i,t in enumerate(traits)}
    tc=z.trait_name.map(tm).to_numpy(int); y=z.rank01.to_numpy(float)
    n=np.bincount(tc,minlength=len(traits)); s=np.bincount(tc,weights=y,minlength=len(traits))
    ok=n[tc]>1; y=y[ok]; tc=tc[ok]; pred=(s[tc]-y)/(n[tc]-1)
    return 1-float(np.sum((y-pred)**2))/float(np.sum((y-.5)**2))

def direct_reversal(df,col,min_co):
    vals=[]; w=[]
    tr=sorted(df.trait_name.unique())
    for i,a in enumerate(tr):
        da=df[df.trait_name==a][["family",col]].rename(columns={col:"a"})
        for b in tr[i+1:]:
            db=df[df.trait_name==b][["family",col]].rename(columns={col:"b"})
            m=da.merge(db,on="family")
            if len(m)<min_co: continue
            d=m.a-m.b; pos=int((d>0).sum()); neg=int((d<0).sum()); n=pos+neg
            if n<2: continue
            vals.append(2*pos*neg/(n*(n-1))); w.append(n*(n-1)/2)
    return {"n_trait_pairs":len(vals),"weighted_probability":float(np.average(vals,weights=w)),
            "mean_unweighted":float(np.mean(vals)),"median":float(np.median(vals))}

def family_pair_rank(df,col,min_shared):
    fs=sorted(df.family.unique()); vals=[]
    for i,a in enumerate(fs):
        da=df[df.family==a][["trait_name",col]]
        for b in fs[i+1:]:
            db=df[df.family==b][["trait_name",col]]
            m=da.merge(db,on="trait_name",suffixes=("_a","_b"))
            if len(m)>=min_shared: vals.append(float(spearmanr(m[col+"_a"],m[col+"_b"]).statistic))
    return {"n_family_pairs":len(vals),"mean_spearman":float(np.mean(vals))}

def latent(st,ss):
    r=st/(st+ss)
    return {"contrast_correlation":r,"expected_reversal_probability":math.acos(r)/math.pi}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--effects",type=Path,required=True)
    ap.add_argument("--measurement-json",type=Path,required=True)
    ap.add_argument("--measurement-bootstrap",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--permutations",type=int,default=9999)
    ap.add_argument("--seed",type=int,default=20261006)
    a=ap.parse_args()
    df=pd.read_csv(a.effects); m=json.loads(a.measurement_json.read_text())
    out={"version":"v0.2","rank_portability":{},"direct_reversal":{},"family_pair_rank_similarity":{}}
    for j,(name,col) in enumerate(AXES.items()):
        out["rank_portability"][name]=portability(df,col,a.permutations,a.seed+j)
        out["direct_reversal"][name]={"min2":direct_reversal(df,col,2),"min10":direct_reversal(df,col,10)}
        out["family_pair_rank_similarity"][name]={"min3":family_pair_rank(df,col,3),"min4":family_pair_rank(df,col,4)}
    means={k:ranks(df,c).groupby("trait_name").rank01.mean() for k,c in AXES.items()}
    def rc(a,b):
        x=pd.concat([means[a],means[b]],axis=1).dropna()
        return float(spearmanr(x.iloc[:,0],x.iloc[:,1]).statistic)
    out["global_trait_spectrum"]={
      "raw_S3_vs_prune":rc("cleaned_raw_S3","cleaned_raw_prune"),
      "log_S3_vs_prune":rc("cleaned_log_S3","cleaned_log_prune"),
      "S3_raw_vs_log":rc("cleaned_raw_S3","cleaned_log_S3"),
      "prune_raw_vs_log":rc("cleaned_raw_prune","cleaned_log_prune")
    }
    out["latent_reordering"]={
      "cleaned_raw_S3":latent(m["measurement_aware"]["S3"]["sigma2_trait"],m["measurement_aware"]["S3"]["sigma2_system"]),
      "cleaned_raw_prune":latent(m["measurement_aware"]["prune_only"]["sigma2_trait"],m["measurement_aware"]["prune_only"]["sigma2_system"]),
      "cleaned_log_S3":latent(m["log_scale"]["measurement_aware_S3"]["sigma2_trait"],m["log_scale"]["measurement_aware_S3"]["sigma2_system"]),
      "cleaned_log_prune":latent(m["log_scale"]["measurement_aware_prune_only"]["sigma2_trait"],m["log_scale"]["measurement_aware_prune_only"]["sigma2_system"])
    }
    if a.measurement_bootstrap and a.measurement_bootstrap.exists():
        b=pd.read_csv(a.measurement_bootstrap); b=b[b.success.astype(bool)]
        rr=b.sigma2_trait/(b.sigma2_trait+b.sigma2_system); p=np.arccos(np.clip(rr,0,1))/np.pi
        out["latent_reordering"]["cleaned_raw_S3_bootstrap"]={
          "replicates":int(len(p)),"median":float(np.median(p)),
          "q025":float(np.quantile(p,.025)),"q975":float(np.quantile(p,.975)),
          "fraction_gt_one_third":float(np.mean(p>1/3))
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

if __name__=="__main__": main()
