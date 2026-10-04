#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path

import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--novel-dir", type=Path, required=True)
ap.add_argument("--out", type=Path, required=True)
ap.add_argument("--table-out", type=Path, required=True)
a = ap.parse_args()

BENCHMARK = 0.15
VALID_MIN = 0.90

rows = []
grid_rows = []

def spearman_xy(x, y):
    x = pd.Series(x, dtype=float)
    y = pd.Series(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    if int(ok.sum()) < 3:
        return np.nan
    xr = x[ok].rank(method="average")
    yr = y[ok].rank(method="average")
    if xr.nunique() < 2 or yr.nunique() < 2:
        return np.nan
    return float(xr.corr(yr))

for p in sorted(a.novel_dir.glob("*.json")):
    x = json.loads(p.read_text())
    s3 = x["temporal_s3"]
    cal = s3.get("calibration", {})
    grid = cal.get("grid", []) if isinstance(cal, dict) else []
    pts = []
    for g in grid:
        lam = g.get("lambda")
        med = g.get("median_effect")
        vf = g.get("valid_fraction")
        if lam is None or med is None or vf is None:
            continue
        lam = float(lam); med = float(med); vf = float(vf)
        if not (math.isfinite(lam) and math.isfinite(med) and math.isfinite(vf)):
            continue
        pts.append((lam, med, vf))
        grid_rows.append({
            "system_id": x["system_id"],
            "family": x["family"],
            "trait_name": x["trait_name"],
            "semantic_class": x["semantic_class"],
            "lambda": lam,
            "median_effect": med,
            "valid_fraction": vf,
            "admissible": vf >= VALID_MIN
        })

    if not pts:
        continue
    pts.sort(key=lambda z: z[0])
    lams = np.array([z[0] for z in pts], dtype=float)
    meds = np.array([z[1] for z in pts], dtype=float)
    vfs = np.array([z[2] for z in pts], dtype=float)

    imax = int(np.nanargmax(meds))
    admiss = vfs >= VALID_MIN
    max_adm = float(np.nanmax(meds[admiss])) if admiss.any() else np.nan
    lam_adm = float(lams[np.where(admiss)[0][np.nanargmax(meds[admiss])]]) if admiss.any() else np.nan

    reason = s3.get("hold_reason", "")
    no_bracket = reason == "CALIBRATION_NO_BRACKET"
    unc_ge = bool(meds[imax] >= BENCHMARK)
    adm_ge = bool(np.isfinite(max_adm) and max_adm >= BENCHMARK)

    if no_bracket:
        if unc_ge and not adm_ge:
            mechanism = "VALIDITY_COLLAPSE"
        elif not unc_ge:
            mechanism = "EFFECT_CEILING"
        else:
            mechanism = "OTHER_NO_BRACKET"
    else:
        mechanism = "CALIBRATED_OR_OTHER"

    rows.append({
        "system_id": x["system_id"],
        "family": x["family"],
        "trait_name": x["trait_name"],
        "semantic_class": x["semantic_class"],
        "n_input_species": int(x["n_input_species"]),
        "n_prune": int(x["n_prune"]),
        "s3_no_bracket": no_bracket,
        "s3_hold_reason": reason,
        "max_unconstrained_median_effect": float(meds[imax]),
        "lambda_at_unconstrained_max": float(lams[imax]),
        "valid_fraction_at_unconstrained_max": float(vfs[imax]),
        "max_admissible_median_effect": max_adm,
        "lambda_at_admissible_max": lam_adm,
        "unconstrained_reaches_benchmark": unc_ge,
        "admissible_reaches_benchmark": adm_ge,
        "mechanism_class": mechanism,
        "spearman_loglambda_valid_fraction": spearman_xy(np.log(lams), vfs),
        "spearman_loglambda_median_effect": spearman_xy(np.log(lams), meds),
        "valid_fraction_at_largest_lambda": float(vfs[-1]),
        "median_effect_at_largest_lambda": float(meds[-1])
    })

df = pd.DataFrame(rows)
if len(df) != 683:
    raise SystemExit(f"expected 683 novel systems, got {len(df)}")
cat = df[df.semantic_class == "nominal_categorical"].copy()
cont = df[df.semantic_class == "continuous_scalar"].copy()
if len(cat) != 265 or len(cont) != 418:
    raise SystemExit(f"unexpected class counts categorical={len(cat)} continuous={len(cont)}")

nb = cat[cat.s3_no_bracket].copy()
if len(nb) != 251:
    raise SystemExit(f"expected 251 categorical no-bracket systems, got {len(nb)}")

def finite_median(s):
    x = pd.to_numeric(s, errors="coerce")
    x = x[np.isfinite(x)]
    return float(x.median()) if len(x) else None

mech = nb.mechanism_class.value_counts().to_dict()
summary = {
    "version": "v0.3.1",
    "status": "PHYLO_MEMORY_BINARY_VALIDITY_TRADEOFF_AUDITED",
    "outcome_type": "known_truth_pilot_calibration_only",
    "real_trait_values_used": False,
    "real_memory_effects_used": False,
    "benchmark": BENCHMARK,
    "calibration_valid_fraction_min": VALID_MIN,
    "n_systems": int(len(df)),
    "n_categorical": int(len(cat)),
    "n_continuous": int(len(cont)),
    "categorical": {
        "n_no_bracket": int(len(nb)),
        "fraction_no_bracket": float(len(nb) / len(cat)),
        "no_bracket_mechanism_counts": {k: int(v) for k, v in mech.items()},
        "no_bracket_mechanism_fractions": {k: float(v / len(nb)) for k, v in mech.items()},
        "fraction_no_bracket_unconstrained_reaches_benchmark": float(nb.unconstrained_reaches_benchmark.mean()),
        "fraction_no_bracket_admissible_reaches_benchmark": float(nb.admissible_reaches_benchmark.mean()),
        "median_max_unconstrained_effect_no_bracket": finite_median(nb.max_unconstrained_median_effect),
        "median_max_admissible_effect_no_bracket": finite_median(nb.max_admissible_median_effect),
        "median_valid_fraction_at_unconstrained_max_no_bracket": finite_median(nb.valid_fraction_at_unconstrained_max),
        "median_valid_fraction_at_largest_lambda_all": finite_median(cat.valid_fraction_at_largest_lambda),
        "median_spearman_loglambda_valid_fraction": finite_median(cat.spearman_loglambda_valid_fraction),
        "median_spearman_loglambda_median_effect": finite_median(cat.spearman_loglambda_median_effect)
    },
    "continuous_sanity": {
        "median_valid_fraction_at_unconstrained_max": finite_median(cont.valid_fraction_at_unconstrained_max),
        "median_valid_fraction_at_largest_lambda": finite_median(cont.valid_fraction_at_largest_lambda),
        "median_spearman_loglambda_valid_fraction": finite_median(cont.spearman_loglambda_valid_fraction)
    },
    "interpretation_rule": {
        "VALIDITY_COLLAPSE": "The unconstrained pilot grid reaches rho>=0.15, but only after binary effects lose the predeclared >=0.90 valid-replicate requirement.",
        "EFFECT_CEILING": "Even the unconstrained pilot grid never reaches rho=0.15; loss of polymorphism alone cannot explain the ceiling.",
        "OTHER_NO_BRACKET": "The grid reaches the benchmark at an admissible point but still does not satisfy the frozen bracketing algorithm; inspect only as an algorithmic edge case."
    },
    "interpretation_guard": "valid_fraction is a generator/estimator diagnostic. For binary mismatch effects, invalid pilot replicates occur when thresholded states are monomorphic, so this analysis tests a measurement tradeoff rather than biological trait conservatism."
}

a.table_out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(a.table_out, index=False)
pd.DataFrame(grid_rows).to_csv(a.table_out.with_name("grid_points.csv"), index=False)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2, sort_keys=True))
