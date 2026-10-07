#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np,pandas as pd
from scipy import linalg
from scipy.optimize import minimize

def sampling_var(split,axis):
    q=split[split.axis==axis].copy()
    q['diff2']=(q.rho_A-q.rho_B)**2
    return q.groupby('system_id').diff2.mean()/4.0

def fit(df,col,vmap):
    d=df.sort_values(['family','trait_name']).reset_index(drop=True)
    y=d[col].to_numpy(float)
    fams=sorted(d.family.unique());traits=sorted(d.trait_name.unique())
    fm={f:i for i,f in enumerate(fams)};tm={t:i for i,t in enumerate(traits)}
    Zf=np.zeros((len(d),len(fams)));Zt=np.zeros((len(d),len(traits)))
    for i,(f,t) in enumerate(zip(d.family,d.trait_name)):
        Zf[i,fm[f]]=1;Zt[i,tm[t]]=1
    Kf=Zf@Zf.T;Kt=Zt@Zt.T
    v=np.array([float(vmap.loc[s]) for s in d.system_id],float)
    X=np.ones((len(d),1));n=len(y);p=1
    def obj(logvars):
        sf,st,su=np.exp(logvars)
        V=sf*Kf+st*Kt+np.diag(su+v)
        try:
            L=linalg.cholesky(V,lower=True,check_finite=False)
            ViX=linalg.cho_solve((L,True),X,check_finite=False)
            Viy=linalg.cho_solve((L,True),y,check_finite=False)
            XtViX=X.T@ViX
            beta=linalg.solve(XtViX,X.T@Viy,assume_a='pos')
            r=y-X@beta
            Vir=linalg.cho_solve((L,True),r,check_finite=False)
            return 0.5*(2*np.log(np.diag(L)).sum()+np.linalg.slogdet(XtViX)[1]+r@Vir+(n-p)*np.log(2*np.pi))
        except Exception:return 1e100
    res=minimize(obj,np.log([0.006,0.001,0.012]),method='L-BFGS-B',bounds=[(-15,0),(-15,0),(-15,0)],options={'maxiter':1000})
    if not res.success:raise RuntimeError(res.message)
    sf,st,su=np.exp(res.x)
    total=sf+st+su+v.mean()
    A=st/(st+su);Lidx=sf/(sf+su)
    return {
      'n_systems':len(d),'n_families':len(fams),'n_traits':len(traits),
      'sigma2_family':float(sf),'sigma2_trait':float(st),'sigma2_system':float(su),
      'mean_sampling_variance':float(v.mean()),
      'mean_sampling_share_total':float(v.mean()/total),
      'memory_level_stability_L':float(Lidx),
      'allocation_stability_A':float(A),
      'gaussian_pair_order_reversal':float(math.acos(max(-1,min(1,A)))/math.pi)
    }

ap=argparse.ArgumentParser()
ap.add_argument('--effects',type=Path,required=True);ap.add_argument('--split-rhos',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
e=pd.read_csv(a.effects);s=pd.read_csv(a.split_rhos)
e=e[(e.log_domain_pass==True)&(e.n_species_prune>=40)].copy()
if len(e)!=158 or e.family.nunique()!=30 or e.trait_name.nunique()!=13:raise SystemExit('unexpected high-support subset')
vs=sampling_var(s,'S3');vp=sampling_var(s,'prune')
if set(e.system_id)!=set(vs.index) or set(e.system_id)!=set(vp.index):raise SystemExit('split/effect system identity mismatch')
out={
  'version':'v0.1','status':'AUSTRAITS_SPLIT_HALF_MEASUREMENT_AWARE_ESTIMATED','post_outcome_exploratory':True,
  'sampling_variance_rule':'mean((rho_A-rho_B)^2)/4 across three split replicates',
  'S3':fit(e,'S3_log_rho',vs),
  'prune_only':fit(e,'prune_log_rho',vp)
}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
