#!/usr/bin/env python3
"""Aggregate equal-rate Brownian K nulls on the frozen 254-system AusTraits graph."""
from __future__ import annotations
import argparse,csv,json
from itertools import combinations
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import rankdata

AXES={"S3":"S3_logK","prune_only":"prune_logK"}
def rank_gain(z,col):
    chunks=[]
    for fam,g in z.groupby("family",sort=True):
        if len(g)<2:continue
        a=g[["family","trait_name",col]].copy()
        a["r"]=(rankdata(a[col].to_numpy(float),method="average")-1)/(len(a)-1)
        chunks.append(a[["family","trait_name","r"]])
    d=pd.concat(chunks,ignore_index=True)
    sums=d.groupby("trait_name").r.agg(["sum","count"])
    tc=d.trait_name.map(sums["count"]).to_numpy()
    if np.any(tc<2):raise ValueError("LOFO rank has unrepresented trait")
    y=d.r.to_numpy(float)
    pred=(d.trait_name.map(sums["sum"]).to_numpy(float)-y)/(tc-1)
    return float(1-np.sum((y-pred)**2)/np.sum((y-.5)**2))

def absolute_gain(z,col):
    d=z[["family","trait_name",col]]
    y=d[col].to_numpy(float)
    f=d.groupby("family")[col].agg(["sum","count"])
    t=d.groupby("trait_name")[col].agg(["sum","count"])
    baseline=(y.sum()-d.family.map(f["sum"]).to_numpy(float)) / (len(d)-d.family.map(f["count"]).to_numpy(int))
    tc=d.trait_name.map(t["count"]).to_numpy(int)
    if np.any(tc<2):raise ValueError("unrepresented trait in absolute LOFO")
    pred=(d.trait_name.map(t["sum"]).to_numpy(float)-y)/(tc-1)
    return float(1-np.sum((y-pred)**2)/np.sum((y-baseline)**2))

def reversal(z,col,min_cooccurrence=10):
    total_contrasts=0
    total_pairs=0
    nr=0
    traits=sorted(z.trait_name.unique())
    for a,b in combinations(traits,2):
        g=z[z.trait_name==a][["family",col]].merge(
          z[z.trait_name==b][["family",col]],on="family",suffixes=("_a","_b"))
        if len(g)<min_cooccurrence:continue
        delta=g[col+"_a"]-g[col+"_b"]
        p=int(np.sum(delta>0));n=int(np.sum(delta<0))
        if p+n<2:continue
        total_contrasts+=p*n
        total_pairs+=(p+n)*(p+n-1)//2
        nr+=1
    if not total_pairs:raise ValueError("no comparable trait-pairs")
    return float(total_contrasts/total_pairs),nr

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--observed-K",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--null-table-out",type=Path,required=True)
    p.add_argument("--n-replicates",type=int,default=64)
    a=p.parse_args()
    observed=pd.read_csv(a.observed_K).sort_values(["family","trait_name"]).reset_index(drop=True)
    if (len(observed),observed.family.nunique(),observed.trait_name.nunique())!=(254,42,13):
        raise ValueError("frozen observed K matrix changed")
    expected={r.system_id:(r.family,r.trait_name,r.S3_logK,r.prune_logK) for r in observed.itertuples(index=False)}
    sys={}
    for filepath in sorted(a.input_dir.glob("*.json")):
        x=json.loads(filepath.read_text())
        sid=x.get("system_id")
        if x.get("status")!="AUSTRAITS_REAL_TREE_BROWNIAN_NULL_SYSTEM_ESTIMATED":
            raise ValueError("bad null system "+str(filepath))
        if sid in sys or sid not in expected:raise ValueError("duplicate/unexpected null system "+str(sid))
        fam,trait,k3,kp=expected[sid]
        if (x["family"],x["trait_name"])!=(fam,trait):
            raise ValueError("system K graph identity mismatch")
        for ax,frozen in [("S3",k3),("prune_only",kp)]:
            if len(x[ax]["null_logK"])!=a.n_replicates:raise ValueError("wrong null replicates")
            if abs(x[ax]["observed_logK"]-frozen)>3e-5:raise ValueError("observed K reconstruction mismatch")
            # Cached-reference recovery inherits phytools K from the completed
            # frozen K run, which was persisted to finite decimal precision.
            cached=x.get("K_equality_reference_kind")=="previous_exact_phytools_K_rounded_JSON"
            atol=2e-4 if cached else 1e-5
            if x[ax]["rel_error_manual_vs_phytools"]>atol:
                raise ValueError("manual K not validated against frozen phytools result")
        sys[sid]=x
    if set(sys)!=set(expected):raise ValueError(f"missing null systems {len(set(expected)-set(sys))}")
    null_rows=[]
    for rep in range(a.n_replicates):
        for x in sys.values():
            null_rows.append({
              "replicate":rep,
              "system_id":x["system_id"],
              "family":x["family"],
              "trait_name":x["trait_name"],
              "S3_logK":float(x["S3"]["null_logK"][rep]),
              "prune_logK":float(x["prune_only"]["null_logK"][rep])
            })
    df=pd.DataFrame(null_rows).sort_values(["replicate","family","trait_name"])
    if not np.isfinite(df[["S3_logK","prune_logK"]].to_numpy()).all():
        raise ValueError("nonfinite null")
    a.null_table_out.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(a.null_table_out,index=False)
    out={"version":"v0.1","status":"AUSTRAITS_REAL_TREE_EQUAL_BM_K_NULL_AGGREGATED",
         "observed_graph":{"systems":254,"families":42,"traits":13},
         "null_replicates":a.n_replicates,"source_native_phylogeny_held_fixed":True,
         "common_evolutionary_rate_across_all_traits_and_families":True,
         "axes":{}}
    for axis,col in AXES.items():
        ob={"rank_gain":rank_gain(observed,col),
            "absolute_gain":absolute_gain(observed,col)}
        ob["reversal_probability"],ob["n_trait_pairs"]=reversal(observed,col)
        null=[]
        for rep,g in df.groupby("replicate"):
            row={"replicate":int(rep),"rank_gain":rank_gain(g,col),
                 "absolute_gain":absolute_gain(g,col)}
            row["reversal_probability"],row["n_trait_pairs"]=reversal(g,col)
            null.append(row)
        vals={k:np.asarray([r[k] for r in null],float)
              for k in ["rank_gain","absolute_gain","reversal_probability"]}
        distribution={k:{
            "mean":float(v.mean()),
            "q025":float(np.quantile(v,.025)),
            "q975":float(np.quantile(v,.975)),
            "p_null_ge_observed":float((1+np.sum(v>=ob[k]))/(1+len(v))),
            "p_null_le_observed":float((1+np.sum(v<=ob[k]))/(1+len(v)))
        } for k,v in vals.items()}
        out["axes"][axis]={"observed":ob,"null":distribution}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v["observed"] for k,v in out["axes"].items()},indent=2))
if __name__=="__main__":main()
