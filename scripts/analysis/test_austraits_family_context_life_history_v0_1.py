#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,warnings
from pathlib import Path
import duckdb,numpy as np,pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr
warnings.filterwarnings("ignore")

ap=argparse.ArgumentParser()
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--effects",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--predictors-out",type=Path,required=True)
a=ap.parse_args()
eff=pd.read_csv(a.effects)
families=sorted(eff.family.unique())
con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE fam(family VARCHAR)")
con.executemany("INSERT INTO fam VALUES (?)",[(f,) for f in families])
sql=r"""
WITH base AS (
 SELECT trim(CAST(a.family AS VARCHAR)) AS family,
        trim(CAST(a.binomial AS VARCHAR)) AS species,
        trim(CAST(a.trait_name AS VARCHAR)) AS trait_name,
        trim(CAST(a.dataset_id AS VARCHAR))||chr(31)||trim(CAST(a.observation_id AS VARCHAR)) AS record_key,
        trim(CAST(a.value AS VARCHAR)) AS value_text
 FROM read_parquet(?) a
 JOIN fam f ON trim(CAST(a.family AS VARCHAR))=f.family
 WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
   AND trim(CAST(a.trait_name AS VARCHAR)) IN ('woodiness','life_history')
   AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
   AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
   AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
   AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
),
dedup AS (
 SELECT DISTINCT family,species,trait_name,record_key,value_text FROM base
),
counts AS (
 SELECT family,species,trait_name,value_text,count(*) n
 FROM dedup GROUP BY family,species,trait_name,value_text
),
ranked AS (
 SELECT *,max(n) OVER(PARTITION BY family,species,trait_name) max_n FROM counts
),
modes AS (
 SELECT family,species,trait_name,
        count(*) FILTER(WHERE n=max_n) n_modal,
        min(value_text) FILTER(WHERE n=max_n) state
 FROM ranked GROUP BY family,species,trait_name
)
SELECT family,species,trait_name,state FROM modes WHERE n_modal=1
"""
states=con.execute(sql,[str(a.parquet)]).df();con.close()
rows=[]
for fam in families:
    w=states[(states.family==fam)&(states.trait_name=="woodiness")]
    lh=states[(states.family==fam)&(states.trait_name=="life_history")]
    rows.append({
      "family":fam,
      "n_woodiness_species":int(len(w)),
      "woody_fraction":None if len(w)<20 else float((w.state=="woody").mean()),
      "n_life_history_species":int(len(lh)),
      "perennial_fraction":None if len(lh)<20 else float(lh.state.isin(["perennial","short_lived_perennial"]).mean())
    })
pred=pd.DataFrame(rows)
a.predictors_out.parent.mkdir(parents=True,exist_ok=True);pred.to_csv(a.predictors_out,index=False)

def blup(df,col):
    d=df[["family","trait_name",col]].dropna().rename(columns={col:"rho"}).copy()
    m=smf.mixedlm("rho ~ 0 + C(trait_name)",d,groups=d.family)
    fit=None
    for method in ["lbfgs","powell","cg","bfgs","nm"]:
        try:
            z=m.fit(reml=True,method=method,maxiter=2000,disp=False)
            if float(z.cov_re.iloc[0,0])>1e-10:
                fit=z;break
        except Exception:pass
    if fit is None:raise RuntimeError(f"mixed model failed {col}")
    return pd.DataFrame({"family":list(fit.random_effects),
                         "context":[float(np.asarray(v).ravel()[0]) for v in fit.random_effects.values()]})

def test(df,col):
    s=blup(df,col).merge(pred,on="family")
    out={}
    for p in ["woody_fraction","perennial_fraction"]:
        z=s[["context",p]].dropna()
        if len(z)<12:
            out[p]={"n_families":int(len(z)),"rho":None,"p_two_sided":None}
        else:
            q=spearmanr(z.context,z[p])
            out[p]={"n_families":int(len(z)),"rho":float(q.statistic),"p_two_sided":float(q.pvalue)}
    return out

log=eff[eff.log_domain_pass==True].copy()
res={
 "version":"v0.1","status":"AUSTRAITS_FAMILY_CONTEXT_LIFE_HISTORY_EXPLORATORY_ESTIMATED",
 "post_outcome_exploratory":True,
 "source_native":{"S3":test(eff,"S3_rho"),"prune":test(eff,"prune_only_rho")},
 "matched_log":{"S3":test(log,"S3_log_rho"),"prune":test(log,"prune_log_rho")},
 "predictor_coverage":{
   "families_woody_fraction":int(pred.woody_fraction.notna().sum()),
   "families_perennial_fraction":int(pred.perennial_fraction.notna().sum())
 },
 "interpretation":"These tests screen two organismal-strategy correlates of family-wide memory context. They are exploratory and Australian-flora composition may not represent each family globally."
}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
print(json.dumps(res,indent=2,sort_keys=True))
