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
        vf = g.get("valid_fraction")
        med = g.get("median_effect")
        if lam is None or vf is None:
            continue
        lam = float(lam); vf = float(vf)
        medf = float(med) if med is not None and math.isfinite(float(med)) else np.nan
        if not (math.isfinite(lam) and math.isfinite(vf)):
            continue
        pts.append((lam, medf, vf))
        grid_rows.append({
            "system_id": x["system_id"],
            "family": x["family"],
            "trait_name": x["trait_name"],
            "semantic_class": x["semantic_class"],
            "lambda": lam,
            "median_effect": medf,
            "valid_fraction": vf,
            "admissible": vf >= VALID_MIN
        })

    reason = s3.get("hold_reason", "")
    no_bracket = reason == "CALIBRATION_NO_BRACKET"

    if pts:
        pts.sort(key=lambda z: z[0])
        lams = np.array([z[0] for z in pts], dtype=float)
        meds = np.array([z[1] for z in pts], dtype=float)
        vfs = np.array([z[2] for z in pts], dtype=float)
        finite = np.isfinite(meds)
        admiss = (vfs >= VALID_MIN) & finite

        if finite.any():
            finite_idx = np.where(finite)[0]
            imax = int(finite_idx[np.argmax(meds[finite])])
            max_unc = float(meds[imax])
            lam_unc = float(lams[imax])
            vf_unc = float(vfs[imax])
        else:
            max_unc = np.nan; lam_unc = np.nan; vf_unc = np.nan

        if admiss.any():
            adm_idx = np.where(admiss)[0]
            iadm = int(adm_idx[np.argmax(meds[admiss])])
            max_adm = float(meds[iadm])
            lam_adm = float(lams[iadm])
        else:
            max_adm = np.nan; lam_adm = np.nan

        unc_ge = bool(np.isfinite(max_unc) and max_unc >= BENCHMARK)
        adm_ge = bool(np.isfinite(max_adm) and max_adm >= BENCHMARK)
        n_finite = int(finite.sum())
        n_admiss = int(admiss.sum())
        min_vf = float(np.min(vfs))
        vf_largest = float(vfs[-1])
        med_largest = float(meds[-1]) if np.isfinite(meds[-1]) else np.nan
        rho_lam_vf = spearman_xy(np.log(lams), vfs)
        rho_lam_med = spearman_xy(np.log(lams[finite]), meds[finite]) if n_finite >= 3 else np.nan
    else:
        max_unc = lam_unc = vf_unc = max_adm = lam_adm = np.nan
        unc_ge = adm_ge = False
        n_finite = n_admiss = 0
        min_vf = vf_largest = med_largest = rho_lam_vf = rho_lam_med = np.nan

    if no_bracket:
        if len(pts) == 0:
            mechanism = "GRID_NOT_STORED"
        elif n_finite == 0:
            mechanism = "COMPLETE_VALIDITY_COLLAPSE"
        elif unc_ge and not adm_ge:
            mechanism = "VALIDITY_COLLAPSE"
        elif not unc_ge:
            mechanism = "EFFECT_CEILING"
        else:
            mechanism = "OTHER_NO_BRACKET"
    else:
        mechanism = "NOT_NO_BRACKET"

    rows.append({
        "system_id": x["system_id"],
        "family": x["family"],
        "trait_name": x["trait_name"],
        "semantic_class": x["semantic_class"],
        "n_input_species": int(x["n_input_species"]),
        "n_prune": int(x["n_prune"]),
        "s3_no_bracket": no_bracket,
        "s3_hold_reason": reason,
        "n_grid_points_stored": int(len(pts)),
        "n_finite_median_points": n_finite,
        "n_admissible_finite_points": n_admiss,
        "max_unconstrained_median_effect": max_unc,
        "lambda_at_unconstrained_max": lam_unc,
        "valid_fraction_at_unconstrained_max": vf_unc,
        "max_admissible_median_effect": max_adm,
        "lambda_at_admissible_max": lam_adm,
        "unconstrained_reaches_benchmark": unc_ge,
        "admissible_reaches_benchmark": adm_ge,
        "minimum_grid_valid_fraction": min_vf,
        "valid_fraction_at_largest_lambda": vf_largest,
        "median_effect_at_largest_lambda": med_largest,
        "spearman_loglambda_valid_fraction": rho_lam_vf,
        "spearman_loglambda_median_effect": rho_lam_med,
        "mechanism_class": mechanism
    })

df = pd.DataFrame(rows)
if len(df) != 683:
    raise SystemExit(f"expected 683 novel systems, got {len(df)}")
cat = df[df.semantic_class == "nominal_categorical"].copy()
cont = df[df.semantic_class == "continuous_scalar"].copy()
if len(cat) != 276 or len(cont) != 407:
    raise SystemExit(f"unexpected class counts categorical={len(cat)} continuous={len(cont)}")

nb = cat[cat.s3_no_bracket].copy()
cont_nb = cont[cont.s3_no_bracket].copy()
if len(nb) != 220:
    raise SystemExit(f"expected 220 categorical no-bracket systems, got {len(nb)}")
if len(cont_nb) != 60:
    raise SystemExit(f"expected 60 continuous no-bracket systems, got {len(cont_nb)}")

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
    "storage_note": "Full pilot grids are persisted for S3 calibration failures, not for successful calibrations. Primary mechanism inference therefore conditions on the 220 categorical CALIBRATION_NO_BRACKET systems.",
    "categorical_no_bracket": {
        "n": int(len(nb)),
        "mechanism_counts": {k: int(v) for k, v in mech.items()},
        "mechanism_fractions": {k: float(v / len(nb)) for k, v in mech.items()},
        "fraction_unconstrained_reaches_benchmark": float(nb.unconstrained_reaches_benchmark.mean()),
        "fraction_admissible_reaches_benchmark": float(nb.admissible_reaches_benchmark.mean()),
        "fraction_with_no_finite_pilot_median": float((nb.n_finite_median_points == 0).mean()),
        "median_max_unconstrained_effect": finite_median(nb.max_unconstrained_median_effect),
        "median_max_admissible_effect": finite_median(nb.max_admissible_median_effect),
        "median_valid_fraction_at_unconstrained_max": finite_median(nb.valid_fraction_at_unconstrained_max),
        "median_minimum_grid_valid_fraction": finite_median(nb.minimum_grid_valid_fraction),
        "median_valid_fraction_at_largest_lambda": finite_median(nb.valid_fraction_at_largest_lambda),
        "median_spearman_loglambda_valid_fraction": finite_median(nb.spearman_loglambda_valid_fraction),
        "median_spearman_loglambda_median_effect": finite_median(nb.spearman_loglambda_median_effect)
    },
    "continuous_no_bracket_sanity": {
        "n": int(len(cont_nb)),
        "fraction_with_no_finite_pilot_median": float((cont_nb.n_finite_median_points == 0).mean()),
        "median_max_unconstrained_effect": finite_median(cont_nb.max_unconstrained_median_effect),
        "median_minimum_grid_valid_fraction": finite_median(cont_nb.minimum_grid_valid_fraction),
        "median_valid_fraction_at_largest_lambda": finite_median(cont_nb.valid_fraction_at_largest_lambda),
        "median_spearman_loglambda_valid_fraction": finite_median(cont_nb.spearman_loglambda_valid_fraction)
    },
    "interpretation_rule": {
        "COMPLETE_VALIDITY_COLLAPSE": "A stored calibration grid exists but no lambda yields a finite binary mismatch effect in the pilot replicates.",
        "VALIDITY_COLLAPSE": "The unconstrained grid reaches rho>=0.15, but only at grid points failing the predeclared valid_fraction>=0.90 requirement.",
        "EFFECT_CEILING": "Even finite unconstrained pilot medians never reach rho=0.15; monomorphism alone is insufficient to explain the calibration ceiling.",
        "OTHER_NO_BRACKET": "An admissible grid point reaches the benchmark but the frozen bracketing algorithm still fails; treat as an algorithmic edge case."
    },
    "interpretation_guard": "valid_fraction is a generator/estimator diagnostic. For binary mismatch effects, invalid pilot replicates occur when thresholded states are monomorphic, so this analysis tests a measurement tradeoff rather than biological trait conservatism."
}

a.table_out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(a.table_out, index=False)
pd.DataFrame(grid_rows).to_csv(a.table_out.with_name("grid_points.csv"), index=False)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2, sort_keys=True))
