#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
from __future__ import annotations
import argparse,csv,json,math,random
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ap=argparse.ArgumentParser()
ap.add_argument("--input",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--bootstrap-table",type=Path,required=True)
a=ap.parse_args()

df=pd.read_csv(a.input)
assert len(df)==722
assert set(df["semantic_class"])=={"continuous_scalar","nominal_categorical"}
df["pass_int"]=df["system_temporal_pass"].astype(str).str.lower().isin(["true","t","1"]).astype(int)
df["log_n"]=np.log(df["n_input_species"].astype(float))
df["prune_fraction"]=df["n_prune"].astype(float)/df["n_input_species"].astype(float)
mean_log=float(df["log_n"].mean()); sd_log=float(df["log_n"].std(ddof=0))
mean_pf=float(df["prune_fraction"].mean()); sd_pf=float(df["prune_fraction"].std(ddof=0))
df["z_log_n"]=(df["log_n"]-mean_log)/sd_log
df["z_prune_fraction"]=(df["prune_fraction"]-mean_pf)/sd_pf

formula="pass_int ~ C(semantic_class) * z_log_n + z_prune_fraction"
fit=smf.logit(formula,data=df).fit(disp=False,maxiter=200)

# Multiway cluster bootstrap: independently resample family labels and trait labels
# with replacement, then weight each observed edge by the product of family and trait
# resampling multiplicities. This preserves the observed bipartite incidence while
# allowing uncertainty from both clustering dimensions.
families=sorted(df["family"].unique())
traits=sorted(df["trait_name"].unique())
B=2000
rng=np.random.default_rng(20261004)
terms=list(fit.params.index)
boot=[]
for b in range(B):
    fs=rng.choice(families,size=len(families),replace=True)
    ts=rng.choice(traits,size=len(traits),replace=True)
    fcount=pd.Series(fs).value_counts()
    tcount=pd.Series(ts).value_counts()
    w=df["family"].map(fcount).fillna(0).to_numpy()*df["trait_name"].map(tcount).fillna(0).to_numpy()
    keep=w>0
    try:
        fb=smf.glm(formula,data=df.loc[keep],family=sm.families.Binomial(),
                   freq_weights=w[keep]).fit(maxiter=200,disp=0)
        vals={t:float(fb.params.get(t,np.nan)) for t in terms}
        valid=all(np.isfinite(list(vals.values())))
    except Exception:
        vals={t:np.nan for t in terms}; valid=False
    vals["replicate"]=b+1; vals["valid"]=valid
    boot.append(vals)

bt=pd.DataFrame(boot)
a.bootstrap_table.parent.mkdir(parents=True,exist_ok=True)
bt.to_csv(a.bootstrap_table,index=False)
valid=bt["valid"]
if valid.mean()<0.90:
    raise SystemExit(f"bootstrap valid fraction {valid.mean():.3f} < 0.90")

cis={}
for t in terms:
    v=bt.loc[valid,t].to_numpy(dtype=float)
    cis[t]=[float(np.quantile(v,0.025)),float(np.quantile(v,0.975))]

params={k:float(v) for k,v in fit.params.items()}
ors={k:float(math.exp(v)) for k,v in params.items()}

def threshold_n(cls):
    b0=params["Intercept"]
    bn=params["z_log_n"]
    if cls=="nominal_categorical":
        b0+=params.get("C(semantic_class)[T.nominal_categorical]",0)
        bn+=params.get("C(semantic_class)[T.nominal_categorical]:z_log_n",0)
    if abs(bn)<1e-12: return None
    z=-b0/bn
    n=math.exp(mean_log+z*sd_log)
    return float(n) if math.isfinite(n) else None

cont=df[df.semantic_class=="continuous_scalar"]
cat=df[df.semantic_class=="nominal_categorical"]
contfit=smf.logit("pass_int ~ z_log_n + z_prune_fraction",data=cont).fit(disp=False,maxiter=200)

out={
  "version":"v0.1",
  "status":"PHYLO_MEMORY_MEASURABILITY_MODEL_ESTIMATED",
  "outcome_type":"known_truth_recovery_only",
  "real_trait_values_used":False,
  "real_memory_effects_used":False,
  "n_systems":len(df),
  "n_families":int(df.family.nunique()),
  "n_traits":int(df.trait_name.nunique()),
  "pass_rate_overall":float(df.pass_int.mean()),
  "pass_rate_continuous":float(cont.pass_int.mean()),
  "pass_rate_categorical":float(cat.pass_int.mean()),
  "median_n_species_pass":float(df.loc[df.pass_int==1,"n_input_species"].median()),
  "median_n_species_hold":float(df.loc[df.pass_int==0,"n_input_species"].median()),
  "median_prune_fraction_pass":float(df.loc[df.pass_int==1,"prune_fraction"].median()),
  "median_prune_fraction_hold":float(df.loc[df.pass_int==0,"prune_fraction"].median()),
  "primary_model":{
    "formula":formula,
    "coefficients":params,
    "odds_ratios":ors,
    "bootstrap_ci95_logit_scale":cis,
    "bootstrap_valid_fraction":float(valid.mean()),
    "mcfadden_pseudo_r2":float(fit.prsquared)
  },
  "continuous_only_model":{
    "coefficients":{k:float(v) for k,v in contfit.params.items()},
    "odds_ratios":{k:float(math.exp(v)) for k,v in contfit.params.items()},
    "mcfadden_pseudo_r2":float(contfit.prsquared)
  },
  "predicted_n_species_for_p50_at_mean_prune_fraction":{
    "continuous_scalar":threshold_n("continuous_scalar"),
    "nominal_categorical":threshold_n("nominal_categorical")
  },
  "interpretation_guard":"Representation effects describe measurability under the frozen Spearman-rho benchmark and generator, not biological conservatism of categorical versus continuous traits."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
