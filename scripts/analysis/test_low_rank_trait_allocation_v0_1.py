#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd

def assign_folds(df,K,seed):
    rng=np.random.default_rng(seed)
    folds=np.full(len(df),-1,dtype=int)
    for fam,idx in df.groupby('family').indices.items():
        idx=np.asarray(idx,dtype=int)
        idx=idx[rng.permutation(len(idx))]
        for j,i in enumerate(idx):folds[i]=j%K
    for k in range(K):
        tr=df[folds!=k];te=df[folds==k]
        if not set(te.family).issubset(set(tr.family)):return None
        if not set(te.trait_name).issubset(set(tr.trait_name)):return None
    return folds

def fit_als(df,col,train,k,lam,seed,maxiter=120,tol=1e-9):
    fams=sorted(df.family.unique());trs=sorted(df.trait_name.unique())
    fm={f:i for i,f in enumerate(fams)};tm={t:i for i,t in enumerate(trs)}
    fi=np.array([fm[x] for x in df.family],int);ti=np.array([tm[x] for x in df.trait_name],int);y=df[col].to_numpy(float)
    ftr=fi[train];ttr=ti[train];ytr=y[train]
    nf,nt=len(fams),len(trs)
    byf=[np.flatnonzero(ftr==i) for i in range(nf)];byt=[np.flatnonzero(ttr==j) for j in range(nt)]
    mu=float(ytr.mean());a=np.zeros(nf);b=np.zeros(nt)
    rng=np.random.default_rng(seed)
    U=rng.normal(0,0.01,(nf,k)) if k else np.empty((nf,0));V=rng.normal(0,0.01,(nt,k)) if k else np.empty((nt,0))
    I=np.eye(k) if k else None;prev=np.inf
    for _ in range(maxiter):
        inter=np.sum(U[ftr]*V[ttr],axis=1) if k else 0.0
        mu=float(np.mean(ytr-a[ftr]-b[ttr]-inter))
        for i,idx in enumerate(byf):
            if not len(idx):continue
            r=ytr[idx]-mu-b[ttr[idx]]
            if k:r-=V[ttr[idx]]@U[i]
            a[i]=r.sum()/(len(idx)+lam)
        for j,idx in enumerate(byt):
            if not len(idx):continue
            r=ytr[idx]-mu-a[ftr[idx]]
            if k:r-=U[ftr[idx]]@V[j]
            b[j]=r.sum()/(len(idx)+lam)
        if k:
            for i,idx in enumerate(byf):
                if not len(idx):continue
                X=V[ttr[idx]];r=ytr[idx]-mu-a[i]-b[ttr[idx]]
                U[i]=np.linalg.solve(X.T@X+lam*I,X.T@r)
            for j,idx in enumerate(byt):
                if not len(idx):continue
                X=U[ftr[idx]];r=ytr[idx]-mu-a[ftr[idx]]-b[j]
                V[j]=np.linalg.solve(X.T@X+lam*I,X.T@r)
        pred=mu+a[ftr]+b[ttr]+(np.sum(U[ftr]*V[ttr],axis=1) if k else 0.0)
        loss=float(np.mean((ytr-pred)**2))
        if abs(prev-loss)<tol:break
        prev=loss
    return mu,a,b,U,V,fi,ti,y

def one_cv(df,col,k,lam,seed,K=5):
    folds=assign_folds(df,K,seed)
    if folds is None:return None
    pred=np.full(len(df),np.nan)
    y=df[col].to_numpy(float)
    for fold in range(K):
        train=folds!=fold
        mu,a,b,U,V,fi,ti,_=fit_als(df,col,train,k,lam,seed+1000*fold+100*k)
        idx=np.flatnonzero(folds==fold)
        p=mu+a[fi[idx]]+b[ti[idx]]
        if k:p+=np.sum(U[fi[idx]]*V[ti[idx]],axis=1)
        pred[idx]=p
    if np.any(~np.isfinite(pred)):return None
    return float(np.sum((y-pred)**2)),float(np.corrcoef(y,pred)[0,1])

def analyse(df,col,reps,lams,ks):
    rows=[]
    for rep in range(reps):
        seed=20261007+10000*rep
        for k in ks:
            for lam in lams:
                z=one_cv(df,col,k,lam,seed)
                if z is None:continue
                rows.append({'replicate':rep,'k':k,'lambda':lam,'sse':z[0],'correlation':z[1]})
    d=pd.DataFrame(rows)
    summary={}
    for k in ks:
        g=d[d.k==k]
        bylam=g.groupby('lambda').agg(mean_sse=('sse','mean'),median_sse=('sse','median'),mean_correlation=('correlation','mean')).reset_index()
        best=bylam.sort_values('mean_sse').iloc[0]
        summary[str(k)]={'best_lambda':float(best['lambda']),'mean_sse':float(best['mean_sse']),
                         'median_sse':float(best['median_sse']),'mean_correlation':float(best['mean_correlation']),
                         'grid':bylam.to_dict(orient='records')}
    base=summary['0']['mean_sse']
    for k in ks:
        summary[str(k)]['relative_sse_improvement_vs_best_additive']=float(1-summary[str(k)]['mean_sse']/base)
    bestlatent=max((summary[str(k)]['relative_sse_improvement_vs_best_additive'],k) for k in ks if k>0)
    return {'replicates':reps,'valid_rows':int(len(d)),'models':summary,
            'best_latent_k':int(bestlatent[1]),'best_latent_relative_sse_improvement':float(bestlatent[0])}

ap=argparse.ArgumentParser()
ap.add_argument('--bien-effects',type=Path,required=True);ap.add_argument('--austraits-effects',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True);ap.add_argument('--replicates',type=int,default=20)
a=ap.parse_args()
b=pd.read_csv(a.bien_effects);u=pd.read_csv(a.austraits_effects);u=u[u.log_domain_pass==True].reset_index(drop=True)
lams=[0.001,0.003,0.01,0.03,0.1,0.3,1.0,3.0,10.0];ks=[0,1,2,3,4]
out={'version':'v0.1','status':'LOW_RANK_TRAIT_ALLOCATION_EXPLORATORY_ESTIMATED','post_outcome_exploratory':True,
     'BIEN_log_S3':analyse(b,'S3_log_rho',a.replicates,lams,ks),
     'BIEN_log_prune':analyse(b,'prune_log_rho',a.replicates,lams,ks),
     'AusTraits_log_S3':analyse(u,'S3_log_rho',a.replicates,lams,ks),
     'AusTraits_log_prune':analyse(u,'prune_log_rho',a.replicates,lams,ks)}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:{'best_latent_k':v['best_latent_k'],'best_latent_relative_sse_improvement':v['best_latent_relative_sse_improvement']} for k,v in out.items() if isinstance(v,dict) and 'best_latent_k' in v},indent=2))
