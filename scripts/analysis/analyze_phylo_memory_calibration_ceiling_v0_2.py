#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

ap=argparse.ArgumentParser()
ap.add_argument("--novel-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

rows=[]
for p in sorted(a.novel_dir.glob("*.json")):
    x=json.loads(p.read_text())
    s3=x["temporal_s3"]
    cal=s3.get("calibration",{})
    reason=s3.get("hold_reason","")
    grid=cal.get("grid",[]) if isinstance(cal,dict) else []
    meds=[g.get("median_effect") for g in grid if g.get("median_effect") is not None and math.isfinite(float(g.get("median_effect")))]
    maxmed=max(map(float,meds)) if meds else np.nan
    rows.append({
      "system_id":x["system_id"],"family":x["family"],"trait_name":x["trait_name"],
      "semantic_class":x["semantic_class"],"n_input_species":int(x["n_input_species"]),
      "n_prune":int(x["n_prune"]),
      "system_temporal_pass":bool(x["system_temporal_pass"]),
      "s3_pass":bool(s3.get("pass",False)),
      "s3_hold_reason":reason,
      "s3_no_bracket":reason=="CALIBRATION_NO_BRACKET",
      "s3_calibrated":("lambda" in s3 and s3.get("lambda") is not None),
      "s3_max_grid_median":maxmed,
      "s3_mae":s3.get("median_absolute_recovery_error"),
      "s3_directional":s3.get("directional_recovery"),
      "s3_valid_fraction":s3.get("valid_replicate_fraction")
    })
df=pd.DataFrame(rows)
if len(df)!=683: raise SystemExit(f"expected 683 novel systems, got {len(df)}")
df["prune_fraction"]=df.n_prune/df.n_input_species
df["log_n"]=np.log(df.n_input_species)
df["z_log_n"]=(df.log_n-df.log_n.mean())/df.log_n.std(ddof=0)
df["z_prune_fraction"]=(df.prune_fraction-df.prune_fraction.mean())/df.prune_fraction.std(ddof=0)
df["no_bracket_int"]=df.s3_no_bracket.astype(int)

# Frozen primary contrast plus the same predeclared sampling covariates.
fit=smf.logit("no_bracket_int ~ C(semantic_class) + z_log_n + z_prune_fraction",data=df).fit(disp=False,maxiter=200)
params={k:float(v) for k,v in fit.params.items()}
ors={k:float(math.exp(v)) for k,v in params.items()}

summary={}
for cls,g in df.groupby("semantic_class"):
    nb=g[g.s3_no_bracket]
    calibrated=g[g.s3_calibrated]
    recovery_fail=calibrated[~calibrated.s3_pass]
    summary[cls]={
      "n":len(g),
      "n_no_bracket":int(g.s3_no_bracket.sum()),
      "no_bracket_rate":float(g.s3_no_bracket.mean()),
      "n_calibrated":len(calibrated),
      "n_s3_pass":int(g.s3_pass.sum()),
      "s3_pass_rate":float(g.s3_pass.mean()),
      "n_recovery_fail_after_calibration":len(recovery_fail),
      "recovery_fail_rate_given_calibrated":float(len(recovery_fail)/len(calibrated)) if len(calibrated) else None,
      "median_max_grid_median_no_bracket":float(nb.s3_max_grid_median.median()) if len(nb) else None,
      "q90_max_grid_median_no_bracket":float(nb.s3_max_grid_median.quantile(.9)) if len(nb) else None,
      "fraction_no_bracket_max_below_0_10":float((nb.s3_max_grid_median<0.10).mean()) if len(nb) else None,
      "fraction_no_bracket_max_below_0_15":float((nb.s3_max_grid_median<0.15).mean()) if len(nb) else None
    }

# Failure decomposition, S3 only.
failure_counts=df.groupby(["semantic_class","s3_hold_reason"],dropna=False).size().reset_index(name="n")
a.table_out.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(a.table_out,index=False)

out={
  "version":"v0.2",
  "status":"PHYLO_MEMORY_CALIBRATION_CEILING_DECOMPOSED_NOVEL683",
  "outcome_type":"known_truth_recovery_only",
  "real_trait_values_used":False,
  "real_memory_effects_used":False,
  "n_systems":len(df),
  "scope":"683 novel systems only; the 39 prior-overlap systems are excluded from the primary v0.2 decomposition because their per-system calibration grids reside in the earlier run. This scope was chosen for data availability, not by outcome.",
  "semantic_summary":summary,
  "no_bracket_model":{
    "formula":"S3_no_bracket ~ semantic_class + z_log_n_species + z_prune_fraction",
    "coefficients":params,
    "odds_ratios":ors,
    "mcfadden_pseudo_r2":float(fit.prsquared)
  },
  "failure_counts":[{k:(int(v) if k=="n" else v) for k,v in r.items()} for r in failure_counts.to_dict("records")],
  "benchmark":0.15,
  "interpretation_guard":"Calibration ceilings diagnose the frozen generator-estimator-tree combination. They do not measure biological phylogenetic signal."
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
