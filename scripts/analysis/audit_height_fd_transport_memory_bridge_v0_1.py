#!/usr/bin/env python3
"""Source-checked posthoc influence audit for BIODEPTH FD site transport.

Uses ONLY frozen nonraw JSON aggregates and a previously published rounded table.
No biological association, significance test, or new data source is introduced.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SITES = ("Germany", "Ireland", "Portugal", "Sheffield", "Silwood", "Sweden", "Switzerland")


def report(root: Path) -> dict:
    folder = root / "results" / "biodepth_2010_species_source_v0_1"
    original = json.loads((folder / "height_pairwise_dispersion_biomass_site_holdout_v0_1.json").read_text(encoding="utf-8"))
    corrected = json.loads((folder / "origanum_botanical_height_source_correction_summary_v0_1.json").read_text(encoding="utf-8"))
    doc = (root / "docs" / "BIODEPTH_ORIGANUM_SOURCE_HEIGHT_CORRECTION_RESULTS_V0_1.md").read_text(encoding="utf-8")
    displayed = {}
    for line in doc.splitlines():
        fields = [s.strip().replace("**", "").replace("−", "-") for s in line.split("|")[1:-1]]
        if len(fields) == 3 and fields[0] in SITES and fields[1].endswith("%") and fields[2].endswith("%"):
            if fields[0] in displayed:
                raise ValueError("Duplicated site in published result table")
            displayed[fields[0]] = (float(fields[1][:-1]), float(fields[2][:-1]))
    if set(displayed) != set(SITES):
        raise ValueError("Site names or source markdown layout changed")
    raw = {r["heldout_site"]: r["height_fd_increment_over_cwm"] for r in original["primary"]["site_holdout_records"]}
    if set(raw) != set(SITES):
        raise ValueError("Original site population changed")
    if original["population"]["provenance_quality_eligible_plots"] != 174 or original["population"]["complete_2010_Community_plot_year_rows"] != 521:
        raise ValueError("Original sample size changed")
    if corrected["n_original_plots"] != 174 or corrected["n_source_2010_Community_plot_years"] != 521 or corrected["n_original_sites"] != 7:
        raise ValueError("Correction source sample changed")
    old = corrected["comparison"]["original_GIFT_13m"]
    kew = corrected["comparison"]["Kew_0_90m"]
    mean = lambda seq: sum(seq) / len(seq)
    old_mean = mean([raw[s] for s in SITES])
    if abs(old_mean - original["primary"]["primary_equal_site_FD_incremental_holdout_SSE_gain"]) > 1e-10 or abs(old_mean - old["FD_site_equal_gain"]) > 1e-10:
        raise ValueError("Published original site mean mismatch")
    for s in SITES:
        if abs(displayed[s][0] / 100 - raw[s]) > 0.000051:
            raise ValueError("Published original site score mismatch: " + s)
    kew_mean_from_display = mean([displayed[s][1] / 100 for s in SITES])
    if abs(kew_mean_from_display - kew["FD_site_equal_gain"]) > 0.0001:
        raise ValueError("Published rounded Kew site scores incompatible with archived model")
    if sum(displayed[s][1] > 0 for s in SITES) != kew["positive_sites"]:
        raise ValueError("Positive-site count changed")
    loo = {s: mean([displayed[t][1] for t in SITES if t != s]) for s in SITES}
    shifts = {s: displayed[s][1] - displayed[s][0] for s in SITES}

    # Under equal-rate Brownian evolution, differences on tree distance d:
    # E(|Xi-Xj|) = sigma sqrt(2d/pi), E((Xi-Xj)^2) = sigma^2 d.
    # K and distance–disparity Spearman rho remain invariant under a
    # uniform positive rescaling of trait measurements.
    expected_within = math.sqrt(2 * 2.0 / math.pi)
    expected_between = math.sqrt(2 * 4.0 / math.pi)
    assert math.isclose(expected_between / expected_within, math.sqrt(2), rel_tol=1e-12)
    return {
        "status": "POSTHOC_SOURCE_ROUNDED_SITE_AUDIT_NOT_NEW_ECOLOGICAL_TEST",
        "original_source_plots": 174,
        "original_plot_years": 521,
        "original_sites": 7,
        "source_fingerprint": original["source_fingerprint"],
        "original_exact_site_equal_gain_pct": 100 * old_mean,
        "archived_Kew_site_equal_gain_pct": 100 * kew["FD_site_equal_gain"],
        "recomputed_Kew_site_equal_gain_from_rounded_scores_pct": 100 * kew_mean_from_display,
        "original_Kew_site_bootstrap_CI95_pct": [100 * v for v in kew["FD_CI95"]],
        "Kew_positive_sites": kew["positive_sites"],
        "Kew_leave_one_site_out_gain_pct_approximately": {s: round(loo[s], 6) for s in SITES},
        "Kew_LOO_range_pct_approximately": [min(loo.values()), max(loo.values())],
        "Kew_LOO_negative_if_exclude": [s for s in SITES if loo[s] < 0],
        "original_to_Kew_gain_shift_pp_approximately": {s: round(shifts[s], 6) for s in SITES},
        "expected_BM_absFD_for_pair": "sigma * sqrt(2 * phylogenetic_distance / pi)",
        "expected_BM_squaredFD_for_pair": "sigma**2 * phylogenetic_distance",
        "balanced_tree_cross_vs_within_expected_absFD_ratio": expected_between / expected_within,
        "K_or_rho_to_community_FD_or_biomass": "NOT_IDENTIFIABLE_WITHOUT_TRAIT_SCALE_COMMUNITY_COMPOSITION_AND_RESPONSE",
        "precision": "Kew per-site numbers copied from source Markdown rounded to 0.01 percentage points; all LOO estimates are approximate.",
        "nonclaims": [
            "Not a new positive biodiversity effect or a prospective site validation",
            "No association between K and FD or biomass has been estimated",
            "Existing source gates for global BIEN/sPlotOpen and original 6-site BIODEPTH qualification remain HOLD"
        ]
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = json.dumps(report(args.root), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
