#!/usr/bin/env python3
"""Audit split-half variance scaling and conditional bootstrap uncertainty.

The high-support 158-system population and primary AusTraits decisions remain fixed.
Uses exact Gaussian REML likelihood via the Woodbury identity.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.linalg import cho_factor,cho_solve
from scipy.optimize import minimize
from scipy.stats import spearmanr

def prepare(e,s,axis):
    e=e[(e.log_domain_pass==True)&(e.n_species_prune>=40)].sort_values(['family','trait_name']).reset_index(drop=True)
    col='S3_log_rho' if axis=='S3' else 'prune_log_rho'
    if (len(e),e.family.nunique(),e.trait_name.nunique())!=(158,30,13):
        raise ValueError('high-support fixed core changed')
    q=s[s.axis==axis].copy()
    q['variance_contribution']=(q.rho_A-q.rho_B)**2/4
    if not q.groupby('system_id').size().eq(3).all():
        raise ValueError('expected three split replicates for every system')
    vmap=q.groupby('system_id').variance_contribution.mean()
    if set(vmap.index)!=set(e.system_id):
        raise ValueError('measurement-variance system graph mismatch')
    v=e.system_id.map(vmap).to_numpy(float)
    ff=pd.Categorical(e.family);tt=pd.Categorical(e.trait_name)
    nf=len(ff.categories);nt=len(tt.categories)
    Z=np.zeros((len(e),nf+nt))
    Z[np.arange(len(e)),ff.codes]=1
    Z[np.arange(len(e)),nf+tt.codes]=1
    return e,col,Z,v,nf,nt

def fit_ma(y,Z,v,nf,nt,starts=None):
    n=len(y);one=np.ones(n)
    def obj(eta):
        vf,vt,vu=np.exp(eta)
        d=vu+v
        invd=1/d
        A=np.diag(np.r_[np.repeat(1/vf,nf),np.repeat(1/vt,nt)])+(Z.T*invd)@Z
        try:
            ch=cho_factor(A,lower=True,check_finite=False)
            ldA=2*np.log(np.diag(ch[0])).sum()
            ldV=np.log(d).sum()+nf*np.log(vf)+nt*np.log(vt)+ldA
            def solve(arr):
                t=invd*arr
                return t-invd*(Z@cho_solve(ch,Z.T@t,check_finite=False))
            vi1=solve(one);viy=solve(y)
            den=one@vi1
            beta=(one@viy)/den
            resid=y-beta*one
            quad=resid@solve(resid)
            return .5*(ldV+np.log(den)+quad+(n-1)*np.log(2*np.pi))
        except Exception:
            return 1e20
    if starts is None:
        starts=[[.006,.001,.012],[.003,.003,.012],[.01,.0005,.015]]
    sol=[]
    for start in starts:
        r=minimize(obj,np.log(start),method='L-BFGS-B',bounds=[(-15,0)]*3,
                   options={'maxiter':400,'ftol':1e-11})
        if np.isfinite(r.fun):
            sol.append(r)
    if not sol:
        raise RuntimeError('no finite REML fit')
    best=min(sol,key=lambda r:r.fun)
    if not best.success:
        raise RuntimeError('REML optimization did not converge: '+str(best.message))
    sf,st,su=np.exp(best.x)
    A=st/(st+su);L=sf/(sf+su)
    return {
      'sigma2_family':float(sf),'sigma2_trait':float(st),'sigma2_system':float(su),
      'L':float(L),'A':float(A),'L_minus_A':float(L-A),
      'model_implied_reversal':float(math.acos(np.clip(A,-1,1))/math.pi),
      'mean_sampling_variance':float(v.mean()),
      'sampling_share':float(v.mean()/(sf+st+su+v.mean())),
      'optimizer_success':bool(best.success),'objective':float(best.fun)
    }

def bootstrap(y,Z,v,nf,nt,fit,B,seed):
    rng=np.random.default_rng(seed)
    n=len(y); vals=[]
    sf,st,su=[fit[k] for k in ['sigma2_family','sigma2_trait','sigma2_system']]
    initial=[[sf,st,su]]
    for i in range(B):
        F=rng.normal(0,np.sqrt(sf),nf)
        T=rng.normal(0,np.sqrt(st),nt)
        pseudo=y.mean()+Z@np.r_[F,T]+rng.normal(0,np.sqrt(su+v),n)
        try:
            r=fit_ma(pseudo,Z,v,nf,nt,starts=initial)
            vals.append((r['L'],r['A'],r['L_minus_A'],r['model_implied_reversal']))
        except RuntimeError:
            continue
    x=np.asarray(vals,float)
    if len(x)<.95*B:
        raise RuntimeError('insufficient valid bootstrap fits')
    return {
      'replicates_requested':B,'replicates_valid':int(len(x)),'seed':seed,
      'conditional_on_fixed_split_half_variances':True,
      'L_ci95':np.quantile(x[:,0],[.025,.975]).tolist(),
      'A_ci95':np.quantile(x[:,1],[.025,.975]).tolist(),
      'L_minus_A_ci95':np.quantile(x[:,2],[.025,.975]).tolist(),
      'reversal_ci95':np.quantile(x[:,3],[.025,.975]).tolist(),
      'fraction_L_gt_A':float(np.mean(x[:,2]>0)),
      'warning':'Parametric interval is conditional on v_i and the Gaussian crossed model; it is not a test p-value.'
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--effects',type=Path,required=True)
    p.add_argument('--split-rhos',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--bootstrap',type=int,default=999)
    p.add_argument('--seed',type=int,default=20261008)
    a=p.parse_args()
    e=pd.read_csv(a.effects);s=pd.read_csv(a.split_rhos)
    out={
      'version':'v0.2',
      'status':'AUSTRAITS_MEASUREMENT_AWARE_ROBUSTNESS_ESTIMATED',
      'post_outcome_exploratory':True,
      'population':{'systems':158,'families':30,'traits':13},
      'variance_multipliers':[0,.25,.5,1,2,4],
      'axes':{},
      'hard_nonclaims':['split-half variances are approximations, not exact independent sampling variances',
                        'bootstrap is conditional on v_i and the Gaussian crossed model',
                        'these are not reclassifications of prospective tests']
    }
    for i,axis in enumerate(['S3','prune']):
        d,col,Z,v,nf,nt=prepare(e,s,axis)
        variants={f'scale_{x:g}':v*x for x in [0,.25,.5,1,2,4]}
        variants['cap95']=np.minimum(v,np.quantile(v,.95))
        med=pd.DataFrame({'trait':d.trait_name,'v':v}).groupby('trait').v.median()
        variants['trait50']=.5*v+.5*d.trait_name.map(med).to_numpy(float)
        variants['global_median']=np.full_like(v,np.median(v))
        fits={name:fit_ma(d[col].to_numpy(float),Z,w,nf,nt) for name,w in variants.items()}
        ref=fits['scale_1']
        bt=bootstrap(d[col].to_numpy(float),Z,v,nf,nt,ref,a.bootstrap,a.seed+1000*i)
        out['axes'][axis]={
          'sampling_variance_distribution':{
            'mean':float(v.mean()),'median':float(np.median(v)),
            'q95':float(np.quantile(v,.95)),
            'top_10_fraction':float(np.sort(v)[-10:].sum()/v.sum()),
            'spearman_sampling_variance_vs_native_tip_count':float(spearmanr(v,d.n_species_prune).statistic)
          },
          'fits':fits,'conditional_bootstrap':bt,
          'all_sensitivity_fits_L_gt_A':bool(all(z['L']>z['A'] for z in fits.values())),
          'min_L_minus_A_over_sensitivities':float(min(z['L_minus_A'] for z in fits.values()))
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({
       axis:{'base_L':z['fits']['scale_1']['L'],
             'base_A':z['fits']['scale_1']['A'],
             'all_L_gt_A':z['all_sensitivity_fits_L_gt_A'],
             'bootstrap_delta_ci':z['conditional_bootstrap']['L_minus_A_ci95'],
             'bootstrap_fraction_L_gt_A':z['conditional_bootstrap']['fraction_L_gt_A']}
       for axis,z in out['axes'].items()},indent=2))
if __name__=='__main__':
    main()
