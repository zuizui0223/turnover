#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from itertools import combinations
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy.stats import spearmanr
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups

def predictions(df,col):
    sums=df.groupby('trait_name')[col].sum().to_dict()
    counts=df.groupby('trait_name')[col].count().to_dict()
    rows=[]
    for fam,g in df.groupby('family'):
        vals=dict(zip(g.trait_name,g[col].astype(float)))
        for a,b in combinations(sorted(vals),2):
            if counts[a]-1<2 or counts[b]-1<2:continue
            ma=(sums[a]-vals[a])/(counts[a]-1)
            mb=(sums[b]-vals[b])/(counts[b]-1)
            pred=ma-mb;obs=vals[a]-vals[b]
            if pred==0 or obs==0:continue
            rows.append({'family':fam,'trait_a':a,'trait_b':b,'pred_margin':pred,
                         'abs_margin':abs(pred),'agree':int(np.sign(pred)==np.sign(obs))})
    return pd.DataFrame(rows)

def analyse(df,col):
    d=predictions(df,col)
    d['trait_pair']=d.apply(lambda r:'||'.join(sorted((r.trait_a,r.trait_b))),axis=1)
    z=(d.abs_margin-d.abs_margin.mean())/d.abs_margin.std(ddof=1)
    X=sm.add_constant(pd.DataFrame({'zmargin':z}))
    fit=sm.OLS(d.agree.astype(float),X).fit()
    fam=pd.Categorical(d.family).codes
    pair=pd.Categorical(d.trait_pair).codes
    cov,_,_=cov_cluster_2groups(fit,fam,pair)
    beta=float(fit.params['zmargin']);se=float(math.sqrt(cov[1,1]))
    sp=spearmanr(d.abs_margin,d.agree)
    try:
        d['quartile']=pd.qcut(d.abs_margin,4,labels=False,duplicates='drop')+1
    except Exception:
        d['quartile']=1
    bins=[]
    for q,g in d.groupby('quartile',sort=True):
        bins.append({'quartile':int(q),'n':int(len(g)),'agreement':float(g.agree.mean()),
                     'median_abs_margin':float(g.abs_margin.median())})
    return {
      'n_pair_predictions':int(len(d)),
      'overall_agreement':float(d.agree.mean()),
      'spearman_abs_margin_vs_agreement':float(sp.statistic),
      'spearman_p_two_sided':float(sp.pvalue),
      'linear_probability_beta_per_1sd_margin':beta,
      'two_way_cluster_se':se,
      'z_value':beta/se if se>0 else None,
      'quartiles':bins
    }

ap=argparse.ArgumentParser()
ap.add_argument('--bien-effects',type=Path,required=True)
ap.add_argument('--austraits-effects',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
b=pd.read_csv(a.bien_effects)
u=pd.read_csv(a.austraits_effects)
ul=u[u.log_domain_pass==True].copy()
out={
 'version':'v0.1',
 'status':'TRAIT_PRIOR_MARGIN_CALIBRATION_EXPLORATORY_ESTIMATED',
 'post_outcome_exploratory':True,
 'BIEN_log_S3':analyse(b,'S3_log_rho'),
 'BIEN_log_prune':analyse(b,'prune_log_rho'),
 'AusTraits_log_S3':analyse(ul,'S3_log_rho'),
 'AusTraits_log_prune':analyse(ul,'prune_log_rho')
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
