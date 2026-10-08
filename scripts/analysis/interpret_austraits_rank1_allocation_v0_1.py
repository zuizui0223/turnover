#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr

GROUPS={
 'vegetative_dimension':['leaf_length','leaf_width','leaf_area','petiole_length'],
 'reproductive_size':['fruit_length','fruit_width','fruit_height','seed_length','seed_width','seed_height','seed_dry_mass'],
 'other':['plant_height','leaf_mass_per_area']
}

def fit(df,col,lam=0.3,seed=20261007,maxiter=2000,tol=1e-12):
    fams=sorted(df.family.unique());trs=sorted(df.trait_name.unique())
    fm={f:i for i,f in enumerate(fams)};tm={t:i for i,t in enumerate(trs)}
    fi=np.array([fm[x] for x in df.family],int);ti=np.array([tm[x] for x in df.trait_name],int)
    y=df[col].to_numpy(float);nf,nt=len(fams),len(trs)
    byf=[np.flatnonzero(fi==i) for i in range(nf)];byt=[np.flatnonzero(ti==j) for j in range(nt)]
    mu=float(y.mean());a=np.zeros(nf);b=np.zeros(nt)
    rng=np.random.default_rng(seed);U=rng.normal(0,.01,(nf,1));V=rng.normal(0,.01,(nt,1))
    prev=np.inf
    for it in range(maxiter):
        inter=(U[fi,0]*V[ti,0])
        mu=float(np.mean(y-a[fi]-b[ti]-inter))
        for i,idx in enumerate(byf):
            r=y[idx]-mu-b[ti[idx]]-V[ti[idx],0]*U[i,0]
            a[i]=r.sum()/(len(idx)+lam)
        for j,idx in enumerate(byt):
            r=y[idx]-mu-a[fi[idx]]-U[fi[idx],0]*V[j,0]
            b[j]=r.sum()/(len(idx)+lam)
        for i,idx in enumerate(byf):
            X=V[ti[idx],0]
            r=y[idx]-mu-a[i]-b[ti[idx]]
            U[i,0]=(X@r)/(X@X+lam)
        for j,idx in enumerate(byt):
            X=U[fi[idx],0]
            r=y[idx]-mu-a[fi[idx]]-b[j]
            V[j,0]=(X@r)/(X@X+lam)
        pred=mu+a[fi]+b[ti]+U[fi,0]*V[ti,0]
        loss=float(np.mean((y-pred)**2))
        if abs(prev-loss)<tol:break
        prev=loss
    scale=np.sqrt(np.mean(U[:,0]**2))
    if scale>0:
        U[:,0]/=scale;V[:,0]*=scale
    return {'fams':fams,'traits':trs,'U':U[:,0],'V':V[:,0],'loss':loss,'iterations':it+1}

ap=argparse.ArgumentParser()
ap.add_argument('--effects',type=Path,required=True)
ap.add_argument('--family-predictors',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
ap.add_argument('--trait-loadings-out',type=Path,required=True)
ap.add_argument('--family-scores-out',type=Path,required=True)
a=ap.parse_args()
df=pd.read_csv(a.effects);df=df[df.log_domain_pass==True].reset_index(drop=True)
if len(df)!=254 or df.family.nunique()!=42 or df.trait_name.nunique()!=13:raise SystemExit('unexpected matched log core')
s=fit(df,'S3_log_rho',seed=20261007);p=fit(df,'prune_log_rho',seed=20261008)
if np.corrcoef(s['V'],p['V'])[0,1]<0:
    p['V']=-p['V'];p['U']=-p['U']
traits=s['traits'];fams=s['fams']
ld=pd.DataFrame({'trait':traits,'S3_loading':s['V'],'prune_loading':p['V']})
ld['mean_loading']=(ld.S3_loading+ld.prune_loading)/2
ld['organ_group']='other'
for g,ts in GROUPS.items():ld.loc[ld.trait.isin(ts),'organ_group']=g
a.trait_loadings_out.parent.mkdir(parents=True,exist_ok=True);ld.to_csv(a.trait_loadings_out,index=False)

fs=pd.DataFrame({'family':fams,'S3_score':s['U'],'prune_score':p['U']})
fs['mean_score']=(fs.S3_score+fs.prune_score)/2
pred=pd.read_csv(a.family_predictors)
fs=fs.merge(pred,on='family',how='left');a.family_scores_out.parent.mkdir(parents=True,exist_ok=True);fs.to_csv(a.family_scores_out,index=False)

group_means={}
for g in GROUPS:
    z=ld[ld.organ_group==g]
    group_means[g]={'n_traits':int(len(z)),'S3_mean_loading':float(z.S3_loading.mean()),
                    'prune_mean_loading':float(z.prune_loading.mean()),'mean_loading':float(z.mean_loading.mean())}

def scorr(x,y):
    z=pd.DataFrame({'x':x,'y':y}).dropna()
    q=spearmanr(z.x,z.y)
    return {'n':int(len(z)),'rho':float(q.statistic),'p_two_sided':float(q.pvalue)}

out={
 'version':'v0.1','status':'AUSTRAITS_RANK1_ALLOCATION_AXIS_INTERPRETED','post_outcome_exploratory':True,
 'lambda':0.3,
 'CV_context':{'S3_relative_sse_improvement':0.032318978929991804,'prune_relative_sse_improvement':0.0765512118556485},
 'S3_prune_trait_loading_correlation':scorr(ld.S3_loading,ld.prune_loading),
 'S3_prune_family_score_correlation':scorr(fs.S3_score,fs.prune_score),
 'organ_group_mean_loadings':group_means,
 'family_score_correlates':{
   'perennial_fraction':scorr(fs.mean_score,fs.perennial_fraction),
   'woody_fraction':scorr(fs.mean_score,fs.woody_fraction)
 },
 'trait_loadings_sorted':ld.sort_values('mean_loading').to_dict(orient='records'),
 'interpretation':'The AusTraits-specific rank-1 factor is highly stable across S3 and prune. Its negative end is dominated by leaf dimensions and petiole length, while its positive end is dominated by seed/fruit dimensions and seed dry mass. It is descriptively consistent with a vegetative-versus-reproductive size allocation axis, but this interpretation is post-outcome and does not replicate in BIEN.',
 'hard_nonclaims':['No universal latent regime claim','No causal developmental tradeoff claim','Factor sign is arbitrary and was aligned across tree treatments']
}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
