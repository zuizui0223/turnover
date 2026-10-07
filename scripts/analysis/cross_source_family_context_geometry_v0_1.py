#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,warnings
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr
warnings.filterwarnings("ignore")

ap=argparse.ArgumentParser()
ap.add_argument("--bien",type=Path,required=True)
ap.add_argument("--austraits",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--permutations",type=int,default=9999)
ap.add_argument("--seed",type=int,default=20261007)
a=ap.parse_args()
b=pd.read_csv(a.bien);u=pd.read_csv(a.austraits);u=u[u.log_domain_pass==True].copy()
def z(v):
    v=np.asarray(v,float);return (v-v.mean())/v.std(ddof=0)
b["z_log_n_s3"]=z(np.log(b.cleaned_n_species_S3))
b["z_prune_fraction"]=z(b.cleaned_n_species_prune/b.cleaned_n_species_S3)
b["z_log_n_prune"]=z(np.log(b.cleaned_n_species_prune))
u["z_log_n_s3"]=z(np.log(u.n_species_S3))
u["z_prune_fraction"]=z(u.n_species_prune/u.n_species_S3)
u["z_log_n_prune"]=z(np.log(u.n_species_prune))
def fit(df,col,axis,adjusted):
    cov=("" if not adjusted else (" + z_log_n_s3 + z_prune_fraction" if axis=="S3" else " + z_log_n_prune"))
    m=smf.mixedlm(f"{col} ~ 0 + C(trait_name){cov}",df,groups=df.family)
    for method in ["lbfgs","powell","cg","bfgs","nm"]:
        try:
            f=m.fit(reml=True,method=method,maxiter=4000,disp=False)
            if float(f.cov_re.iloc[0,0])>1e-10:
                return {fam:float(np.asarray(v).ravel()[0]) for fam,v in f.random_effects.items()}
        except Exception:pass
    raise RuntimeError("mixed model failed")
def compare(axis,adjusted,seed):
    bc="S3_log_rho" if axis=="S3" else "prune_log_rho"
    uc=bc
    rb=fit(b,bc,axis,adjusted);ru=fit(u,uc,axis,adjusted)
    fams=sorted(set(rb)&set(ru));x=np.array([rb[f] for f in fams]);y=np.array([ru[f] for f in fams])
    obs=float(spearmanr(x,y).statistic)
    rng=np.random.default_rng(seed);null=np.array([spearmanr(x,rng.permutation(y)).statistic for _ in range(a.permutations)])
    return {"n_shared_families":len(fams),"spearman":obs,
            "p_one_sided_positive":float((1+np.sum(null>=obs))/(a.permutations+1)),
            "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975))}
res={"version":"v0.1","status":"CROSS_SOURCE_FAMILY_CONTEXT_GEOMETRY_SENSITIVITY_ESTIMATED","post_outcome_exploratory":True,
     "unadjusted":{"S3":compare("S3",False,a.seed),"prune":compare("prune",False,a.seed+1)},
     "coverage_adjusted":{"S3":compare("S3",True,a.seed+2),"prune":compare("prune",True,a.seed+3)},
     "interpretation":"The unadjusted cross-source family-context correspondence attenuates after source-specific species-support/native-tip coverage adjustment. Treat cross-source family identity correspondence as suggestive, not robust.",
     "hard_nonclaims":["Within-source family repeatability remains separately supported; this sensitivity addresses only portability of family-specific context values across compilations."]}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
print(json.dumps(res,indent=2,sort_keys=True))
