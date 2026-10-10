#!/usr/bin/env python3
"""Computationally optimized, scientifically identical source-noise OU aggregation.

Reuses original 249-system exact-graph, K, eta and alpha identity validation
and frozen scientific contract from aggregate_austraits_k_source_noise_ou_v0_1.py.
Only the three metric-evaluation kernels are replaced. To avoid any apparent
post-outcome method change, tests must independently compare these optimized
metrics against the original slow pandas/scipy reference functions.
"""
from __future__ import annotations
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from scipy.stats import rankdata

import aggregate_austraits_k_source_noise_ou_v0_1 as original
from aggregate_austraits_k_brownian_null_v0_1 import (
    rank_gain as baseline_rank,
    absolute_gain as baseline_absolute,
    reversal as baseline_reversal,
)

@lru_cache(maxsize=8)
def build_structure(pairs:tuple[tuple[str,str],...]):
    families={}
    traits={}
    for i,(fam,trait) in enumerate(pairs):
        families.setdefault(fam,[]).append(i)
        traits.setdefault(trait,[]).append(i)
    fam_ix=[np.asarray(x,dtype=int) for x in families.values()]
    tr_ix=[np.asarray(x,dtype=int) for x in traits.values()]
    trait_names=list(traits)
    family_names=list(families)
    tr_id={t:i for i,t in enumerate(trait_names)}
    ti=np.asarray([tr_id[t] for _,t in pairs],dtype=int)
    tc=np.bincount(ti,minlength=len(traits))
    if np.any(tc<2):raise ValueError("LOFO rank has unrepresented trait")
    family_id={f:i for i,f in enumerate(family_names)}
    fi=np.asarray([family_id[f] for f,_ in pairs],dtype=int)
    fc=np.bincount(fi,minlength=len(families))
    compare=[]
    lookup={(f,t):i for i,(f,t) in enumerate(pairs)}
    for a,b in combinations(sorted(traits),2):
        shared=sorted(set(f for f,t in pairs if t==a)&set(f for f,t in pairs if t==b))
        if len(shared)<10:continue
        compare.append((
            np.asarray([lookup[f,a] for f in shared],dtype=int),
            np.asarray([lookup[f,b] for f in shared],dtype=int)))
    return fam_ix,tr_ix,ti,tc,fi,fc,compare

def idx(z):
    graph=tuple((str(f),str(t)) for f,t in zip(z.family,z.trait_name))
    return build_structure(graph)

def rank_gain(z,col):
    x=z[col].to_numpy(dtype=float)
    fam_ix,tr_ix,ti,tc,fi,fc,compare=idx(z)
    ranks=np.empty(len(x),float)
    for g in fam_ix:
        ranks[g]=(rankdata(x[g],method="average")-1)/(len(g)-1)
    sums=np.bincount(ti,weights=ranks,minlength=len(tc))
    pred=(sums[ti]-ranks)/(tc[ti]-1)
    return float(1-np.square(ranks-pred).sum()/np.square(ranks-.5).sum())

def absolute_gain(z,col):
    x=z[col].to_numpy(dtype=float)
    fam_ix,tr_ix,ti,tc,fi,fc,compare=idx(z)
    trait_sums=np.bincount(ti,weights=x,minlength=len(tc))
    family_sums=np.bincount(fi,weights=x,minlength=len(fc))
    pred=(trait_sums[ti]-x)/(tc[ti]-1)
    base=(x.sum()-family_sums[fi])/(len(x)-fc[fi])
    return float(1-np.square(x-pred).sum()/np.square(x-base).sum())

def reversal(z,col,min_cooccurrence=10):
    if min_cooccurrence!=10:
        return baseline_reversal(z,col,min_cooccurrence=min_cooccurrence)
    x=z[col].to_numpy(dtype=float)
    fam_ix,tr_ix,ti,tc,fi,fc,compare=idx(z)
    opposite=0
    n=0
    for ai,bi in compare:
        d=x[ai]-x[bi]
        p=int(np.sum(d>0));q=int(np.sum(d<0))
        if p+q<2:continue
        opposite+=p*q
        n+=(p+q)*(p+q-1)//2
    if n==0:raise ValueError("no comparable trait-pairs")
    return float(opposite/n),len(compare)

def verify_parity(observed:pd.DataFrame,seed:int=20261008):
    rng=np.random.default_rng(seed)
    candidates=[observed]
    for _ in range(4):
        simulated=observed.copy()
        simulated["S3_logK"]=rng.normal(size=len(observed))
        simulated["prune_logK"]=rng.normal(size=len(observed))
        candidates.append(simulated)
    for z in candidates:
        for col in ("S3_logK","prune_logK"):
            checks=[
                (rank_gain(z,col),baseline_rank(z,col),"rank_gain"),
                (absolute_gain(z,col),baseline_absolute(z,col),"absolute_gain"),
                (reversal(z,col),baseline_reversal(z,col),"reversal")]
            for new,old,name in checks:
                if isinstance(new,tuple):
                    if new[1]!=old[1] or abs(new[0]-old[0])>2e-12:
                        raise ValueError("fast/reference "+name+" mismatch")
                elif not np.isclose(new,old,atol=2e-12,rtol=2e-12):
                    raise ValueError("fast/reference "+name+" mismatch")
    print("PASS: optimized rank/absolute/reversal kernels equal original references on 5 complete graphs")

if __name__=="__main__":
    p=argparse.ArgumentParser(add_help=False)
    p.add_argument("--observed-K",type=Path,required=True)
    args,_=p.parse_known_args()
    full=pd.read_csv(args.__dict__["observed_K"])
    if (len(full),full.family.nunique(),full.trait_name.nunique())!=(254,42,13):
        raise ValueError("original source K graph changed before parity verification")
    matched=full[full.trait_name!="seed_height"].sort_values(["family","trait_name"]).reset_index(drop=True)
    if (len(matched),matched.family.nunique(),matched.trait_name.nunique())!=(249,42,12):
        raise ValueError("source-eligible trait graph not original 249 systems")
    verify_parity(matched)
    original.rank_gain=rank_gain
    original.absolute_gain=absolute_gain
    original.reversal=reversal
    original.main()
