#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()

rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x.get("status")=="PHYLO_MEMORY_MK2_GENERATOR_SYSTEM_ESTIMATED":
        rows.append(x)
df=pd.DataFrame(rows)
if len(df)!=276: raise SystemExit(f"expected 276 systems, got {len(df)}")
if not (df.real_trait_values_used.eq(False).all() and df.real_memory_effects_used.eq(False).all()):
    raise SystemExit("outcome firewall violated")
for col in ["mk2_eta","mk2_pilot_median","mk2_pilot_valid_fraction","mk2_valid_fraction",
            "mk2_median_absolute_recovery_error","mk2_directional_recovery"]:
    df[col]=pd.to_numeric(df[col],errors="coerce")

ou_nb=df.original_ou_no_bracket.astype(bool)
mk_cal=df.mk2_calibrated.astype(bool)
mk_pass=df.mk2_s3_pass.astype(bool)
rescue=ou_nb & mk_cal
new_fail=(~ou_nb) & (~mk_cal)
discord_rescue=int(rescue.sum())
discord_loss=int(new_fail.sum())
cal=df[mk_cal]
recovery_fail=cal[~mk_pass]

reason=df.mk2_hold_reason.fillna("").value_counts().to_dict()

def finite_median(s):
    x=pd.to_numeric(s,errors="coerce")
    x=x[np.isfinite(x)]
    return float(x.median()) if len(x) else None

out={
  "version":"v0.4.1",
  "status":"PHYLO_MEMORY_MK2_GENERATOR_AGGREGATED",
  "outcome_type":"known_truth_generator_substitution_only",
  "real_trait_values_used":False,
  "real_memory_effects_used":False,
  "n_systems":int(len(df)),
  "benchmark":0.15,
  "ou_reference":{
    "n_no_bracket":int(ou_nb.sum()),
    "no_bracket_rate":float(ou_nb.mean())
  },
  "mk2":{
    "n_calibrated":int(mk_cal.sum()),
    "n_no_bracket":int((~mk_cal).sum()),
    "no_bracket_rate":float((~mk_cal).mean()),
    "n_s3_pass":int(mk_pass.sum()),
    "s3_pass_rate":float(mk_pass.mean()),
    "n_recovery_fail_after_calibration":int(len(recovery_fail)),
    "recovery_fail_rate_given_calibrated":float(len(recovery_fail)/len(cal)) if len(cal) else None,
    "median_eta_calibrated":finite_median(cal.mk2_eta),
    "median_pilot_valid_fraction_calibrated":finite_median(cal.mk2_pilot_valid_fraction),
    "hold_reason_counts":{str(k):int(v) for k,v in reason.items()}
  },
  "paired_generator_comparison":{
    "ou_no_bracket_mk2_calibrated_rescued_n":discord_rescue,
    "ou_no_bracket_mk2_calibrated_rescued_fraction_of_ou_no_bracket":float(discord_rescue/ou_nb.sum()),
    "ou_calibrated_mk2_no_bracket_new_failure_n":discord_loss,
    "discordant_rescue_minus_loss":int(discord_rescue-discord_loss)
  },
  "interpretation_guard":"This paired comparison changes the categorical generator while holding the same trees, target and binary mismatch Spearman estimator fixed. It diagnoses truth accessibility, not the biological correctness of Mk2 for observed traits."
}
a.table_out.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(a.table_out,index=False)
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
