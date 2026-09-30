#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import math
from statistics import mean


def average_ranks(values):
    order=sorted(range(len(values)), key=lambda i:(values[i],i))
    ranks=[0.0]*len(values)
    i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:
            j+=1
        avg=((i+1)+j)/2.0
        for k in range(i,j):
            ranks[order[k]]=avg
        i=j
    return ranks


def pearson(x,y):
    mx,my=mean(x),mean(y)
    dx=[v-mx for v in x]; dy=[v-my for v in y]
    sx=sum(v*v for v in dx); sy=sum(v*v for v in dy)
    if sx<=0 or sy<=0:
        return None
    return sum(a*b for a,b in zip(dx,dy))/math.sqrt(sx*sy)


def spearman(x,y):
    return pearson(average_ranks(x),average_ranks(y))


def edges(n):
    return [(i,j) for i in range(n) for j in range(i+1,n)]


def exact_null_mean(coords,states,kind):
    e=edges(len(states))
    separation=[abs(coords[i]-coords[j]) for i,j in e]
    vals=[]
    for p in itertools.permutations(range(len(states))):
        if kind=="continuous":
            diss=[abs(states[p[i]]-states[p[j]]) for i,j in e]
        elif kind=="categorical":
            diss=[0 if states[p[i]]==states[p[j]] else 1 for i,j in e]
        else:
            raise ValueError(kind)
        r=spearman(separation,diss)
        if r is not None:
            vals.append(r)
    if not vals:
        raise RuntimeError("no valid permutations")
    return sum(vals)/len(vals),len(vals)


def main():
    coords=[0.0,1.0,2.0,4.0,7.0]
    tests=[
        ("continuous",[0.1,0.3,1.2,2.0,4.0]),
        ("continuous",[0.0,0.0,1.0,1.0,2.0]),
        ("categorical",["a","a","b","b","c"]),
        ("categorical",["a","a","a","b","b"]),
    ]
    results=[]
    for kind,states in tests:
        m,n=exact_null_mean(coords,states,kind)
        if abs(m)>1e-12:
            raise AssertionError(f"{kind} exact permutation mean not zero: {m}")
        results.append({"kind":kind,"states":states,"n_permutations":n,"mean_spearman":m})
    out={
        "version":"v0.4.1",
        "status":"TRAIT_PERMUTATION_NULL_ZERO_VERIFIED",
        "complete_pair_set":True,
        "tests":results,
        "tolerance":1e-12,
    }
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
