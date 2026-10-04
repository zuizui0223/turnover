#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--input-dir",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
ap.add_argument("--trait-out",type=Path,required=True)
a=ap.parse_args()

rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    if x.get("status")=="PHYLO_MEMORY_BALANCE_NORMALIZED_SYSTEM_ESTIMATED":
        rows.append(x)
df=pd.DataFrame(rows)
if len(df)!=276:
    raise SystemExit(f"expected 276 systems, got {len(df)}")
for col in ["balance_normalized_eta","balance_normalized_pilot_median","balance_normalized_pilot_valid_fraction","balance_normalized_pilot_median_rho","balance_normalized_pilot_median_mismatch_pair_fraction","factorization_max_identity_error"]:
    df[col]=pd.to_numeric(df[col],errors="coerce")

mk=df.original_mk2_rho_calibrated.astype(bool)
bn=df.balance_normalized_calibrated.astype(bool)
if int((~mk).sum())!=170 or int(mk.sum())!=106:
    raise SystemExit("Mk2 reference counts changed")
rescue=(~mk)&bn
loss=mk&(~bn)
err=df.factorization_max_identity_error[np.isfinite(df.factorization_max_identity_error)]
if not len(err) or float(err.max())>1e-10:
    raise SystemExit("factorization identity check failed")

def med(s):
    x=pd.to_numeric(s,errors="coerce")
    x=x[np.isfinite(x)]
    return float(x.median()) if len(x) else None

trait=(df.groupby("trait_name",sort=True)
         .agg(n=("system_id","size"),
              mk2_rho_no_bracket_rate=("original_mk2_rho_no_bracket","mean"),
              balance_normalized_no_bracket_rate=("balance_normalized_no_bracket","mean"),
              median_eta_calibrated=("balance_normalized_eta","median"))
         .reset_index())
hold=df.balance_normalized_hold_reason.fillna("").value_counts().to_dict()
out={
 "version":"v0.5",
 "status":"PHYLO_MEMORY_BALANCE_NORMALIZED_AGGREGATED",
 "outcome_type":"known_truth_state_balance_mechanism_only",
 "real_trait_values_used":False,
 "real_memory_effects_used":False,
 "n_systems":276,
 "target_rank_separation":0.30,
 "mk2_rho_reference":{"n_calibrated":int(mk.sum()),"n_no_bracket":int((~mk).sum()),"no_bracket_rate":float((~mk).mean())},
 "balance_normalized":{"n_calibrated":int(bn.sum()),"n_no_bracket":int((~bn).sum()),"no_bracket_rate":float((~bn).mean()),"median_eta_calibrated":med(df.loc[bn,"balance_normalized_eta"]),"median_pilot_valid_fraction_calibrated":med(df.loc[bn,"balance_normalized_pilot_valid_fraction"]),"median_pilot_rho_at_rank_separation_calibration":med(df.loc[bn,"balance_normalized_pilot_median_rho"]),"median_mismatch_pair_fraction_at_calibration":med(df.loc[bn,"balance_normalized_pilot_median_mismatch_pair_fraction"]),"hold_reason_counts":{str(k):int(v) for k,v in hold.items()}},
 "paired_balance_comparison":{"rescued_n":int(rescue.sum()),"rescued_fraction_of_mk2_rho_no_bracket":float(rescue.sum()/(~mk).sum()),"new_failure_n":int(loss.sum()),"discordant_rescue_minus_loss":int(rescue.sum()-loss.sum())},
 "factorization_check":{"max_absolute_identity_error":float(err.max()),"identity":"rho = Delta_rank * sqrt(p*(1-p))"}
}
a.table_out.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(a.table_out,index=False)
trait.to_csv(a.trait_out,index=False)
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
