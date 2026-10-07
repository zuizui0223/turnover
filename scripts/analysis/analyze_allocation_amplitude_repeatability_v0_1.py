#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,itertools
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy.stats import spearmanr

def amp_for_subset(g,col,trait_mean,subset):
    z=g[g.trait_name.isin(subset)]
    if len(z)<2:return None
    vals=np.array([float(v)-trait_mean[t] for t,v in zip(z.trait_name,z[col])],float)
    vals=vals-vals.mean()
    return float(np.sqrt(np.mean(vals**2))),len(z)

def partitions(traits):
    traits=sorted(traits);n=len(traits);k=n//2
    if n%2==0:
        first=traits[0]
        for comb in itertools.combinations(traits[1:],k-1):
            A=frozenset((first,)+comb);B=frozenset(set(traits)-set(A))
            yield A,B
    else:
        for comb in itertools.combinations(traits,k):
            A=frozenset(comb);B=frozenset(set(traits)-set(A))
            yield A,B

def resid(y,X):
    X=sm.add_constant(pd.DataFrame(X),has_constant='add')
    return sm.OLS(np.asarray(y,float),X).fit().resid

def within_source(df,col,support_col):
    tm=df.groupby('trait_name')[col].mean().to_dict()
    groups={f:g.copy() for f,g in df.groupby('family')}
    vals=[]
    for A,B in partitions(df.trait_name.unique()):
        rows=[]
        for fam,g in groups.items():
            aa=amp_for_subset(g,col,tm,A);bb=amp_for_subset(g,col,tm,B)
            if aa is None or bb is None:continue
            za=g[g.trait_name.isin(A)];zb=g[g.trait_name.isin(B)]
            rows.append({
              'family':fam,'ampA':aa[0],'nA':aa[1],'ampB':bb[0],'nB':bb[1],
              'supA':float(np.mean(np.log(za[support_col].to_numpy(float)))),
              'supB':float(np.mean(np.log(zb[support_col].to_numpy(float))))
            })
        z=pd.DataFrame(rows)
        if len(z)<8:continue
        raw=float(spearmanr(z.ampA,z.ampB).statistic)
        ra=resid(z.ampA,{'n':z.nA,'support':z.supA})
        rb=resid(z.ampB,{'n':z.nB,'support':z.supB})
        adj=float(spearmanr(ra,rb).statistic)
        if np.isfinite(raw) and np.isfinite(adj):
            vals.append((len(z),raw,adj))
    a=np.asarray(vals,float)
    return {
      'n_valid_partitions':int(len(a)),
      'median_families_per_partition':float(np.median(a[:,0])),
      'raw_correlation':{
        'median':float(np.median(a[:,1])),'mean':float(np.mean(a[:,1])),
        'q025':float(np.quantile(a[:,1],.025)),'q975':float(np.quantile(a[:,1],.975)),
        'fraction_positive':float(np.mean(a[:,1]>0))
      },
      'support_count_adjusted_correlation':{
        'median':float(np.median(a[:,2])),'mean':float(np.mean(a[:,2])),
        'q025':float(np.quantile(a[:,2],.025)),'q975':float(np.quantile(a[:,2],.975)),
        'fraction_positive':float(np.mean(a[:,2]>0))
      }
    }

def full_amp(df,col):
    tm=df.groupby('trait_name')[col].mean().to_dict()
    rows=[]
    for fam,g in df.groupby('family'):
        a=amp_for_subset(g,col,tm,set(g.trait_name))
        rows.append({'family':fam,'amplitude':a[0],'n_traits':a[1]})
    return pd.DataFrame(rows)

def cross_source(b,u,bcol,ucol,bsup,usup,bse=None):
    ba=full_amp(b,bcol);ua=full_amp(u,ucol)
    bs=b.groupby('family').agg(mean_log_support=(bsup,lambda x:float(np.mean(np.log(x.astype(float)))))).reset_index()
    us=u.groupby('family').agg(mean_log_support=(usup,lambda x:float(np.mean(np.log(x.astype(float)))))).reset_index()
    if bse:
        se=b.groupby('family')[bse].mean().rename('mean_se').reset_index()
        ba=ba.merge(bs,on='family').merge(se,on='family')
    else:ba=ba.merge(bs,on='family')
    ua=ua.merge(us,on='family')
    Xb={'n_traits':ba.n_traits,'support':ba.mean_log_support}
    if bse:Xb['mean_se']=ba.mean_se
    ba['resid']=resid(ba.amplitude,Xb)
    ua['resid']=resid(ua.amplitude,{'n_traits':ua.n_traits,'support':ua.mean_log_support})
    m=ba.merge(ua,on='family',suffixes=('_BIEN','_AusTraits'))
    raw=spearmanr(m.amplitude_BIEN,m.amplitude_AusTraits)
    adj=spearmanr(m.resid_BIEN,m.resid_AusTraits)
    return {
      'n_shared_families':int(len(m)),
      'raw_spearman':float(raw.statistic),'raw_p_two_sided':float(raw.pvalue),
      'adjusted_spearman':float(adj.statistic),'adjusted_p_two_sided':float(adj.pvalue)
    }

ap=argparse.ArgumentParser()
ap.add_argument('--bien-effects',type=Path,required=True);ap.add_argument('--austraits-effects',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
b=pd.read_csv(a.bien_effects);u=pd.read_csv(a.austraits_effects);u=u[u.log_domain_pass==True].copy()
out={'version':'v0.1','status':'ALLOCATION_AMPLITUDE_REPEATABILITY_EXPLORATORY_ESTIMATED','post_outcome_exploratory':True,'axes':{}}
for name,bc,uc,bs,us,se in [
 ('log_S3','S3_log_rho','S3_log_rho','cleaned_n_species_S3','n_species_S3','S3_log_se'),
 ('log_prune','prune_log_rho','prune_log_rho','cleaned_n_species_prune','n_species_prune','prune_log_se')]:
    out['axes'][name]={
      'BIEN_within_source':within_source(b,bc,bs),
      'AusTraits_within_source':within_source(u,uc,us),
      'cross_source':cross_source(b,u,bc,uc,bs,us,se)
    }
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
