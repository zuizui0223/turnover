#!/usr/bin/env python3
"""BIODEPTH 8-site grass+legume vs grass+forb source-pinned retrospective replay.

This exploratory analysis is pre-described in
docs/BIODEPTH_TWO_GUILD_MATCHED_LEGUME_VS_FORB_V0_1.md
but was chosen AFTER seeing Jena/Cedar and BIODEPTH guild-count outcomes.
It does not reopen the original 6-site within-one-richness source gate.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import t as student_t

SOURCE = {
    "Design.txt": (5640240, "a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a"),
    "Shoots.txt": (5640249, "cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135"),
}
FIXED_SITE_RESULTS = {
    "Germany": 0.5520192722216909,
    "Greece": -0.8327173725338246,
    "Ireland": 0.202010584695319,
    "Portugal": -1.6639502194192242,
    "Sheffield": 0.15608247102702766,
    "Silwood": 0.134930860101924,
    "Sweden": 2.223093694782824,
    "Switzerland": 0.6003190743330235,
}
SEED = 20261116
REPS = 10000


def source_tables():
    tables = {}
    for name, (file_id, digest) in SOURCE.items():
        url = f"https://ndownloader.figshare.com/files/{file_id}"
        request = urllib.request.Request(
            url, headers={"User-Agent": "turnover-original-biodepth-matched-replay/0.1"})
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read(2000000)
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("PUBLISHED_FIGSHARE_ORIGINAL_SOURCE_DIGEST_MISMATCH_" + name)
        tables[name] = pd.read_csv(io.BytesIO(data), sep="\t")
        print("ORIGINAL_BIODEPTH_SHA256_PASS", name, len(data), digest)
    return tables


def take_matched_treatments(design):
    d = design.copy()
    if len(d) != 480 or d["plot"].nunique() != 480:
        raise ValueError("ORIGINAL_480_DESIGN_PLOTS_NOT_FOUND")
    for field in ("grasses", "legumes", "forbs"):
        if set(d[field].unique()) != {"Yes", "No"}:
            raise ValueError("EXPECTED_LITERAL_YES_NO_GUILD_FIELDS")
        d[field] = (d[field] == "Yes").astype(int)
    if not (d[["grasses", "legumes", "forbs"]].sum(axis=1)
            == d["functional.richness"]).all():
        raise ValueError("SOURCE_DESIGN_GUILD_COUNT_CONTRADICTION")
    selected = d[(d["grasses"] == 1) & (d["functional.richness"] == 2)].copy()
    if len(selected) != 114 or not (selected["legumes"] + selected["forbs"] == 1).all():
        raise ValueError("SOURCE_PREMATCHED_ORIGINAL_GUILD_SUPPORT_CHANGED")
    keys = ["location", "species.richness", "block"]
    matched = selected.groupby(keys).filter(lambda g: g["legumes"].nunique() == 2)
    if len(matched) != 110 or matched.groupby(keys).ngroups != 35:
        raise ValueError("PREDECLARED_110_PLOTS_35_MATCHED_STRATA_CHANGED")
    return matched


def site_effect_from_paired_years(paired, site):
    sub = paired[paired["site"] == site]
    if sub.empty:
        raise ValueError("SOURCE_SITE_MISSING_MATCHED_YEAR_COMPARISONS_" + site)
    per_stratum = sub.groupby(["richness", "block"])["log_difference"].mean()
    return float(per_stratum.mean())


def derive(tables):
    design = tables["Design.txt"]
    shoots = tables["Shoots.txt"]
    if len(shoots) != 1440 or shoots["plot"].nunique() != 480:
        raise ValueError("ORIGINAL_480_PLOTS_BY_3_YEAR_RESPONSE_CHANGED")
    chosen = take_matched_treatments(design)
    obs = shoots.merge(
        chosen, on="plot", how="inner", validate="many_to_one",
        suffixes=("_shoot", "_design"))
    if len(obs) != 330:
        raise ValueError("ORIGINAL_330_PLOT_YEAR_MATCH_COUNT_CHANGED")
    for k in ("block", "composition", "species.richness", "functional.richness"):
        if not obs[k + "_shoot"].eq(obs[k + "_design"]).all():
            raise ValueError("SOURCE_RESPONSE_TREATMENT_MISMATCH_" + k)
    if not obs["legumes_shoot"].eq(
        obs["legumes_design"].map({0: "No", 1: "Yes"})).all():
        raise ValueError("SOURCE_LEGUME_FIELD_MISMATCH")
    if (obs["biomass"].dropna() < 0).any():
        raise ValueError("NEGATIVE_SOURCE_BIOMASS_IS_INVALID")
    d = obs.assign(
        site=obs["location_design"],
        richness=obs["species.richness_design"].astype(int),
        block=obs["block_design"].astype(int),
        composition=obs["composition_design"].astype(int),
        legume_companion=obs["legumes_design"].astype(int),
    )
    d["missing_biomass"] = d["biomass"].isna()
    valid = d[~d["missing_biomass"]].copy()
    valid["y"] = np.log1p(valid["biomass"])
    if len(valid) != 327 or int(d["missing_biomass"].sum()) != 3:
        raise ValueError("FIXED_NUMERIC_SOURCE_POPULATION_327_CHANGED")
    diff_rows = []
    for (site, richness, block, year), group in valid.groupby(
            ["site", "richness", "block", "year"], sort=True):
        if group["legume_companion"].nunique() != 2:
            continue
        lg = float(group.loc[group["legume_companion"] == 1, "y"].mean())
        fb = float(group.loc[group["legume_companion"] == 0, "y"].mean())
        diff_rows.append({
            "site": site, "richness": int(richness), "block": int(block),
            "year": int(year), "log_difference": lg - fb})
    paired = pd.DataFrame(diff_rows)
    if len(paired) != 105 or set(paired["site"]) != set(FIXED_SITE_RESULTS):
        raise ValueError("ORIGINAL_105_MATCHED_STRATUM_YEAR_RESPONSE_SUPPORT_CHANGED")
    site_rows = []
    for site, design_site in chosen.groupby("location", sort=True):
        src = valid[valid["site"] == site].copy()
        source_strata = design_site.groupby(["species.richness", "block"]).ngroups
        number_st = paired.loc[paired["site"] == site].groupby(
            ["richness", "block"]).ngroups
        if source_strata != number_st:
            raise ValueError("SOURCE_MATCHED_STRATUM_LOSS_" + site)
        mean = site_effect_from_paired_years(paired, site)
        if abs(mean - FIXED_SITE_RESULTS[site]) > 1e-11:
            raise ValueError("NUMERIC_REPLAY_CONFLICT_" + site)
        site_year = {
            str(yr): float(paired.loc[(paired["site"] == site)
                                  & (paired["year"] == yr), "log_difference"].mean())
            for yr in (1, 2, 3)}
        arm_quality = {}
        for code, label in ((1, "grass_plus_legume"), (0, "grass_plus_forb")):
            sub = d[(d["site"] == site) & (d["legume_companion"] == code)]
            arm_quality[label] = {
                "n_original_plot_year_rows": int(len(sub)),
                "missing_biomass_rows": int(sub["missing_biomass"].sum()),
                "observed_zeros": int((sub["biomass"] == 0).sum())}
        src["rich_block"] = (src["richness"].astype(str)
                             + "|" + src["block"].astype(str))
        model = smf.ols(
            "y ~ C(rich_block) + C(year) + legume_companion", data=src).fit(
            cov_type="cluster",
            cov_kwds={"groups": src["composition"], "use_correction": True})
        nc = int(src["composition"].nunique())
        if nc < 4 or np.linalg.matrix_rank(model.model.exog) < model.model.exog.shape[1]:
            secondary = {
                "status": "SOURCE_OR_DESIGN_HOLD",
                "reason": "Less than four original planted-composition clusters or deficient design rank"}
        else:
            beta, se = float(model.params["legume_companion"]), float(model.bse["legume_companion"])
            ci = float(student_t.ppf(.975, nc - 1)) * se
            secondary = {
                "status": "ESTIMABLE", "legume_companion_beta": beta,
                "cluster_SE": se, "t_cluster_ci95": [beta - ci, beta + ci],
                "t_clusters_minus1_p_two_sided": float(2 * student_t.sf(abs(beta / se), nc - 1))}
        site_rows.append({
            "site": site,
            "n_matched_original_plots": int(len(design_site)),
            "n_planted_composition_clusters": nc,
            "n_original_matched_strata": int(source_strata),
            "n_observed_stratum_year_contrasts": int((paired["site"] == site).sum()),
            "n_valid_plot_year_rows": int(len(src)),
            "matched_stratum_equal_weight_mean_log_difference": mean,
            "site_year_mean_log_difference": site_year,
            "arm_source_quality": arm_quality,
            "fixed_strata_composition_cluster_model": secondary,
        })
    values = np.asarray([r["matched_stratum_equal_weight_mean_log_difference"]
                         for r in site_rows], dtype=float)
    random = np.random.default_rng(SEED)
    draw = values[random.integers(0, len(values), size=(REPS, len(values)))].mean(axis=1)
    orig_mean = float(values.mean())
    ci = [float(v) for v in np.quantile(draw, [.025, .975])]
    expected_ci = [-0.5483165023631258, 0.9183743892614635]
    if abs(orig_mean - 0.17147354565109507) > 1e-11 or any(
            abs(ci[i] - expected_ci[i]) > 1e-11 for i in (0, 1)):
        raise ValueError("FIXED_EIGHT_SITE_SOURCE_BOOTSTRAP_REPLAY_MISMATCH")
    years = {
        str(yr): {
            "equal_site_mean_log_difference": float(np.mean(
                [r["site_year_mean_log_difference"][str(yr)] for r in site_rows])),
            "positive_sites": sum(r["site_year_mean_log_difference"][str(yr)] > 0
                                  for r in site_rows)}
        for yr in (1, 2, 3)}
    loo = {
        site: float(np.mean([x["matched_stratum_equal_weight_mean_log_difference"]
                             for x in site_rows if x["site"] != site]))
        for site in sorted(FIXED_SITE_RESULTS)}
    return {
        "version": "v0.1",
        "status": "SOURCE_PINNED_EIGHT_SITE_GUILD_REPLACEMENT_REPLAY_PASS",
        "source_doi": "https://doi.org/10.6084/m9.figshare.3565170.v1",
        "source_sha256": {k: v[1] for k, v in SOURCE.items()},
        "original_primary_source_gate": "HOLD: only one of eight sites passes fixed >=20 plots in single richness",
        "origin": "Source-original BIODEPTH eight sites; original 2005 study already reported guild effects",
        "source_selected_population": {
            "original_480_plots": 480, "grass_two_guild_plots": 114,
            "matched_original_plots": 110, "matched_strata": 35,
            "original_matched_plot_year_rows": 330,
            "observed_numeric_plot_year_rows": 327,
            "observed_paired_stratum_year_contrasts": 105,
            "n_independent_geographic_sites": 8},
        "site_results": site_rows,
        "equal_site_summary": {
            "mean_log_difference": orig_mean,
            "median_log_difference": float(np.median(values)),
            "between_site_sd": float(values.std(ddof=1)),
            "positive_sites": int((values > 0).sum()),
            "n_sites": 8,
            "bootstrap_site_draws": REPS, "bootstrap_seed": SEED,
            "bootstrap_ci95": ci},
        "year_sensitivity_descriptive": years,
        "leave_one_site_out_descriptive": loo,
        "hard_nonclaims": [
            "Original strict high-support gate is HOLD; this is separately declared retrospective exploration",
            "Difference is association with original sown guild/species mixtures; no pure legume or N-fixation causality",
            "Same site/year/plot repeated; only 8 geographic sites, not a worldwide random sample",
            "Source field biomass is not homogeneous annual NPP across original site harvest schedules",
            "No cross-site average distinguishable from zero at site-resampled 95% interval",
            "No quantified continuous trait FD, BIEN rho or family-level evolutionary memory tested",
        ]}
def fixture():
    synthetic = pd.DataFrame([
        {"site": "A", "richness": 2, "block": 1, "year": 1,
         "log_difference": 0.5},
        {"site": "A", "richness": 2, "block": 1, "year": 2,
         "log_difference": 1.0},
        {"site": "A", "richness": 4, "block": 1, "year": 1,
         "log_difference": -0.5},
    ])
    assert abs(site_effect_from_paired_years(synthetic, "A") - 0.125) < 1e-12
    return {"status": "MATCHED_CONTRAST_FIXTURE_PASS", "checks": 1}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--out")
    a = p.parse_args()
    if a.self_test:
        print(json.dumps(fixture()))
    else:
        if not a.out:
            p.error("--out is required")
        result = derive(source_tables())
        target = Path(a.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
        print("BIODEPTH_MATCHED_GUILD_REPLAY",
              json.dumps({k: v for k, v in result.items() if k != "site_results"},
                         ensure_ascii=False, sort_keys=True))
        for row in result["site_results"]:
            print("BIODEPTH_MATCHED_SITE_REPLAY",
                  json.dumps({k: v for k, v in row.items() if k != "arm_source_quality"},
                             ensure_ascii=False, sort_keys=True))
