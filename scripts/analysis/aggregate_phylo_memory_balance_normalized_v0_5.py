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
ap.add_argument("--trait-out",type=Path,required=True)
a=ap.parse_args()

ok_rows=[]
hold_rows=[]
for p in sorted(a.input_dir.glob("*.json")):
    x=json.loads(p.read_text())
    st=x.get("status","")
    if st=="PHYLO_MEMORY_BALANCE_NORMALIZED_SYSTEM_ESTIMATED":
        ok_rows.append(x)
    elif st=="HOLD_PHYLO_MEMORY_BALANCE_NORMALIZED_GEOMETRY_DRIFT":
        hold_rows.append(x)

all_rows=ok_rows+hold_rows
if len(all_rows)!=276:
    raise SystemExit(f"expected 276 accounted systems, got {len(all_rows)}")
ids=[x["system_id"] for x in all_rows]
if len(set(ids))!=276:
    raise SystemExit("system IDs are not unique")

full=pd.DataFrame([{
    "system_id":x["system_id"],
    "family":x["family"],
    "trait_name":x["trait_name"],
    "status":x["status"],
    "original_mk2_rho_calibrated":bool(x["original_mk2_rho_calibrated"]),
    "original_mk2_rho_no_bracket":bool(x["original_mk2_rho_no_bracket"])
} for x in all_rows])
if int(full.original_mk2_rho_calibrated.sum())!=106 or int(full.original_mk2_rho_no_bracket.sum())!=170:
    raise SystemExit("full frozen Mk2 reference counts changed")

df=pd.DataFrame(ok_rows)
held=pd.DataFrame(hold_rows)
if len(df)==0:
    raise SystemExit("no geometry-matched systems available")
for col in [
    "balance_normalized_eta","balance_normalized_pilot_median",
    "balance_normalized_pilot_valid_fraction","balance_normalized_pilot_median_rho",
    "balance_normalized_pilot_median_mismatch_pair_fraction",
    "factorization_max_identity_error"
]:
    df[col]=pd.to_numeric(df[col],errors="coerce")

mk=df.original_mk2_rho_calibrated.astype(bool)
bn=df.balance_normalized_calibrated.astype(bool)
mk_nb=~mk
rescue=mk_nb & bn
loss=mk & (~bn)
err=df.factorization_max_identity_error[np.isfinite(df.factorization_max_identity_error)]
if not len(err) or float(err.max())>1e-10:
    raise SystemExit("factorization identity check failed")

held_mk_cal=int(held.original_mk2_rho_calibrated.astype(bool).sum()) if len(held) else 0
held_mk_nb=int(held.original_mk2_rho_no_bracket.astype(bool).sum()) if len(held) else 0
matched_mk_cal=int(mk.sum())
matched_mk_nb=int(mk_nb.sum())
if matched_mk_cal+held_mk_cal!=106 or matched_mk_nb+held_mk_nb!=170:
    raise SystemExit("geometry availability accounting failed")

def med(s):
    x=pd.to_numeric(s,errors="coerce")
    x=x[np.isfinite(x)]
    return float(x.median()) if len(x) else None

trait_ok=(df.groupby("trait_name",sort=True)
            .agg(n_analyzed=("system_id","size"),
                 mk2_rho_no_bracket_rate=("original_mk2_rho_no_bracket","mean"),
                 balance_normalized_no_bracket_rate=("balance_normalized_no_bracket","mean"),
                 median_eta_calibrated=("balance_normalized_eta","median"))
            .reset_index())
hold_trait=(held.groupby("trait_name").size().rename("n_geometry_hold").reset_index()
            if len(held) else pd.DataFrame(columns=["trait_name","n_geometry_hold"]))
trait=trait_ok.merge(hold_trait,on="trait_name",how="outer").fillna({"n_analyzed":0,"n_geometry_hold":0})
trait["n_analyzed"]=trait["n_analyzed"].astype(int)
trait["n_geometry_hold"]=trait["n_geometry_hold"].astype(int)
trait["n_population"]=trait["n_analyzed"]+trait["n_geometry_hold"]

bn_no=int((~bn).sum())
n_hold=len(held)
full_rate_lower=bn_no/276
full_rate_upper=(bn_no+n_hold)/276
rescue_n=int(rescue.sum())
rescue_lower=rescue_n/170
rescue_upper=(rescue_n+held_mk_nb)/170

out={
  "version":"v0.5.1",
  "status":"PHYLO_MEMORY_BALANCE_NORMALIZED_AGGREGATED_WITH_GEOMETRY_HOLDS",
  "outcome_type":"known_truth_state_balance_mechanism_only",
  "real_trait_values_used":False,
  "real_memory_effects_used":False,
  "n_population":276,
  "target_rank_separation":0.30,
  "geometry_availability":{
    "n_analyzed":int(len(df)),
    "n_geometry_hold":int(n_hold),
    "held_original_mk2_calibrated":held_mk_cal,
    "held_original_mk2_no_bracket":held_mk_nb,
    "rule":"Exact frozen-geometry identity only; held systems have no balance-normalized outcome."
  },
  "mk2_rho_reference_full":{"n_calibrated":106,"n_no_bracket":170,"no_bracket_rate":170/276},
  "matched_subset_reference":{
    "n_calibrated":matched_mk_cal,
    "n_no_bracket":matched_mk_nb
  },
  "balance_normalized_matched_subset":{
    "n_calibrated":int(bn.sum()),
    "n_no_bracket":bn_no,
    "no_bracket_rate":float((~bn).mean()),
    "median_eta_calibrated":med(df.loc[bn,"balance_normalized_eta"]),
    "median_pilot_valid_fraction_calibrated":med(df.loc[bn,"balance_normalized_pilot_valid_fraction"]),
    "median_pilot_rho_at_rank_separation_calibration":med(df.loc[bn,"balance_normalized_pilot_median_rho"]),
    "median_mismatch_pair_fraction_at_calibration":med(df.loc[bn,"balance_normalized_pilot_median_mismatch_pair_fraction"])
  },
  "paired_balance_comparison_matched_subset":{
    "rescued_n":rescue_n,
    "rescued_denominator_mk2_rho_no_bracket":matched_mk_nb,
    "rescued_fraction":float(rescue_n/matched_mk_nb) if matched_mk_nb else None,
    "new_failure_n":int(loss.sum()),
    "new_failure_denominator_mk2_rho_calibrated":matched_mk_cal,
    "discordant_rescue_minus_loss":int(rescue.sum()-loss.sum())
  },
  "full_population_bounds_from_geometry_holds":{
    "balance_normalized_no_bracket_rate_lower_if_all_holds_calibrate":full_rate_lower,
    "balance_normalized_no_bracket_rate_upper_if_all_holds_fail":full_rate_upper,
    "rescue_fraction_of_original_170_lower_if_no_held_no_bracket_rescued":rescue_lower,
    "rescue_fraction_of_original_170_upper_if_all_held_no_bracket_rescued":rescue_upper
  },
  "factorization_check":{
    "max_absolute_identity_error":float(err.max()),
    "identity":"rho = Delta_rank * sqrt(p*(1-p))"
  },
  "interpretation_guard":"Geometry-HOLD systems are excluded only by a frozen pre-outcome identity gate and are explicitly accounted for. The balance-normalized statistic removes one algebraic state-balance attenuation term; it is a mechanism diagnostic, not a universal estimator recommendation."
}
a.table_out.parent.mkdir(parents=True,exist_ok=True)
pd.DataFrame(all_rows).to_csv(a.table_out,index=False)
a.trait_out.parent.mkdir(parents=True,exist_ok=True)
trait.to_csv(a.trait_out,index=False)
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
