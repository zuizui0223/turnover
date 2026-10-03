#!/usr/bin/env python3
from __future__ import annotations
import json, math

def average_ranks(v):
    order=sorted(range(len(v)),key=lambda i:(v[i],i))
    out=[0.0]*len(v); i=0
    while i<len(order):
        j=i+1
        while j<len(order) and v[order[j]]==v[order[i]]:
            j+=1
        r=((i+1)+j)/2
        for k in range(i,j): out[order[k]]=r
        i=j
    return out

def pearson(x,y,w=None):
    if w is None: w=[1.0]*len(x)
    W=sum(w)
    mx=sum(a*z for a,z in zip(x,w))/W
    my=sum(a*z for a,z in zip(y,w))/W
    sxx=sum(z*(a-mx)**2 for a,z in zip(x,w))
    syy=sum(z*(b-my)**2 for b,z in zip(y,w))
    if sxx<=0 or syy<=0: return None
    return sum(z*(a-mx)*(b-my) for a,b,z in zip(x,y,w))/math.sqrt(sxx*syy)

def spearman(x,y):
    return pearson(average_ranks(x),average_ranks(y))

def weighted_midrank(v,w):
    order=sorted(range(len(v)),key=lambda i:(v[i],i))
    out=[0.0]*len(v)
    before=0.0; k=0
    while k<len(order):
        j=k+1
        while j<len(order) and v[order[j]]==v[order[k]]:
            j+=1
        gw=sum(w[order[t]] for t in range(k,j))
        rank=before+(gw+1)/2
        for t in range(k,j): out[order[t]]=rank
        before+=gw
        k=j
    return out

def compressed_continuous(coords,mult,states):
    d=[]; y=[]; w=[]
    n=len(coords)
    for i in range(n):
        for j in range(i+1,n):
            d.append(abs(coords[i]-coords[j]))
            y.append(abs(states[i]-states[j]))
            w.append(mult[i]*mult[j])
        if mult[i]>=2:
            d.append(0.0); y.append(0.0); w.append(mult[i]*(mult[i]-1)/2)
    rx=weighted_midrank(d,w); ry=weighted_midrank(y,w)
    return pearson(rx,ry,w)

def compressed_binary(coords,mult,states):
    d=[]; mismatch=[]; w=[]
    n=len(coords)
    for i in range(n):
        for j in range(i+1,n):
            d.append(abs(coords[i]-coords[j]))
            mismatch.append(states[i]!=states[j])
            w.append(mult[i]*mult[j])
        if mult[i]>=2:
            d.append(0.0); mismatch.append(False); w.append(mult[i]*(mult[i]-1)/2)
    rx=weighted_midrank(d,w)
    M=sum(w); mx=(M+1)/2
    sxx=sum(z*(r-mx)**2 for r,z in zip(rx,w))
    K=sum(z for m,z in zip(mismatch,w) if m)
    cross=sum(z*r for m,z,r in zip(mismatch,w,rx) if m)
    den=math.sqrt(sxx*K*(M-K)/M)
    return (cross-K*mx)/den

def expand(nodes,mult):
    x=[]
    for a,m in zip(nodes,mult): x += [a]*m
    return x

def main():
    coords=[0.0,1.0,2.0]
    mult=[2,1,2]
    cont=[0.2,1.0,2.0]
    binary=[False,True,True]
    ex_coord=expand(coords,mult)
    ex_cont=expand(cont,mult)
    ex_bin=expand(binary,mult)
    sep=[]; dy=[]; db=[]
    for i in range(len(ex_coord)):
        for j in range(i+1,len(ex_coord)):
            sep.append(abs(ex_coord[i]-ex_coord[j]))
            dy.append(abs(ex_cont[i]-ex_cont[j]))
            db.append(0 if ex_bin[i]==ex_bin[j] else 1)
    exact_cont=spearman(sep,dy)
    exact_bin=spearman(sep,db)
    cmp_cont=compressed_continuous(coords,mult,cont)
    cmp_bin=compressed_binary(coords,mult,binary)
    if abs(exact_cont-cmp_cont)>1e-12:
        raise AssertionError((exact_cont,cmp_cont))
    if abs(exact_bin-cmp_bin)>1e-12:
        raise AssertionError((exact_bin,cmp_bin))
    out={
      "version":"v0.4.3",
      "status":"SPATIAL_WEIGHTED_PAIR_COMPRESSION_VERIFIED",
      "continuous_expanded":exact_cont,
      "continuous_compressed":cmp_cont,
      "binary_expanded":exact_bin,
      "binary_compressed":cmp_bin,
      "tolerance":1e-12,
      "expanded_records":sum(mult),
      "expanded_pairs":sum(mult)*(sum(mult)-1)//2
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
