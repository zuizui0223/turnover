#!/usr/bin/env python3
"""Post-result BIODEPTH height-label test, prospectively frozen for THIS null in
docs/BIODEPTH_HEIGHT_TRAIT_LABEL_RANDOMIZATION_DESIGN_V0_1.md.

Keeps original field site/plots, planted species occurrences, guilds, height
distribution within each unambiguously source-inferred guild, and original
2010 Community response unchanged. Never estimates phylogenetic memory.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from audit_biodepth_103_taxa_gift_height_v0_1 import source, geometry
from audit_biodepth_gift_height_references_v0_1 import run as provenance
from fit_biodepth_2010_sown_height_fd_biomass_v0_1 import (
    DESIGN_SHA, composition, fit_predict, evaluate,
)

SEED = 20261116
REPS = 999
GUILDS = ("grass", "legume", "forb")
FLAGS = {"grass": "grasses", "legume": "legumes", "forb": "forbs"}
GROUP_MIN = 5
TOTAL_MIN = 45
PLOTS_WITH_TWO_MIN = 80
ORIGANUM = "origanum vulgare"


def published_design(path: str) -> dict:
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != DESIGN_SHA:
        raise ValueError("SOURCE_HOLD: original Design.txt SHA mismatch")
    parsed = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter="\t"))
    design = {r["plot"]: r for r in parsed}
    if len(parsed) != 480 or len(design) != 480:
        raise ValueError("SOURCE_HOLD: original Design.txt 480 unique plots not recovered")
    for plot, row in design.items():
        if any(row[c] not in ("Yes", "No") for c in FLAGS.values()):
            raise ValueError("SOURCE_HOLD: invalid source treatment guild flags")
        if not any(row[c] == "Yes" for c in FLAGS.values()):
            raise ValueError("SOURCE_HOLD: plot lacks all planned guilds")
    return design


def inferred_guilds(plots: dict, plan: dict) -> tuple[dict, list, list]:
    candidates = {}
    for (site, plot), species in sorted(plots.items()):
        treatment = plan.get(plot)
        if treatment is None or treatment["location"] != site:
            raise ValueError("SOURCE_HOLD: source plot site and Design mismatch")
        if int(treatment["species.richness"]) != len(species):
            raise ValueError("SOURCE_HOLD: source planted richness and Design mismatch")
        allowed = {g for g in GUILDS if treatment[FLAGS[g]] == "Yes"}
        for sp in species:
            if sp not in candidates:
                candidates[sp] = set(GUILDS)
            candidates[sp].intersection_update(allowed)
    unique = {sp: next(iter(c)) for sp, c in candidates.items() if len(c) == 1}
    ambiguous = sorted(sp for sp, c in candidates.items() if len(c) > 1)
    contradictory = sorted(sp for sp, c in candidates.items() if len(c) == 0)
    return unique, ambiguous, contradictory


def features(plots: dict, height: dict) -> dict:
    ans = {}
    for key, original in plots.items():
        valid = [name for name in original if name in height]
        if len(valid) < 3 or len(valid) / len(original) < .8:
            raise ValueError("SOURCE_HOLD: permutation changed original trait completeness")
        h = np.log(np.array([height[n] for n in valid], dtype=float))
        if not np.isfinite(h).all() or len(h) < 3:
            raise ValueError("SOURCE_HOLD: nonpositive/invalid height")
        mpd = float(np.abs(h[:, None] - h[None, :]).sum() / (len(h) * (len(h) - 1)))
        ans[key] = (float(h.mean()), mpd)
    return ans


def apply_features(cells: list, computed: dict) -> list:
    out = []
    for r in cells:
        cwm, mpd = computed[(r["site"], r["plot"])]
        out.append({**r, "cwm": cwm, "mpd": mpd})
    return out


def fast_site_gains(cells: list, sites: list) -> np.ndarray:
    gs = []
    for site in sites:
        train = [r for r in cells if r["site"] != site]
        test = [r for r in cells if r["site"] == site]
        y = np.asarray([r["response"] for r in test], dtype=float)
        pred1 = fit_predict(train, test, 1)
        pred2 = fit_predict(train, test, 2)
        sse1 = float(((y - pred1) ** 2).sum())
        sse2 = float(((y - pred2) ** 2).sum())
        if not np.isfinite(sse1) or not np.isfinite(sse2) or sse1 <= 0:
            raise ValueError("MODEL_HOLD: degeneracy in seven site holdout")
        gs.append(1.0 - sse2 / sse1)
    return np.asarray(gs)


def check_gates(pools: dict, eligible_plot_species: dict) -> dict:
    covered = {sp for names in pools.values() for sp in names}
    two = sum(len(set(planted) & covered) >= 2
              for planted in eligible_plot_species.values())
    result = {
        "inferred_unambiguous_GIFT_height_species": len(covered),
        "height_species_per_guild": {g: len(pools[g]) for g in GUILDS},
        "source_eligible_plots_with_at_least_two_permutable_species": two,
        "ambiguous_species_heights_held_fixed": None,
        "original_GIFT_height_taxa_count": None,
        "thresholds": {"min_unique_guild_height_species": TOTAL_MIN,
                       "min_each_guild_height_species": GROUP_MIN,
                       "min_original_plots_with_two_permutable_species": PLOTS_WITH_TWO_MIN},
    }
    if len(covered) < TOTAL_MIN or any(len(pools[g]) < GROUP_MIN for g in GUILDS) or two < PLOTS_WITH_TWO_MIN:
        raise ValueError("SOURCE_HOLD: guild-inference informativeness gate " + json.dumps(result))
    return result


def permute_map(original: dict, pools: dict, rng: np.random.Generator) -> dict:
    result = original.copy()
    for guild in GUILDS:
        names = pools[guild]
        values = np.asarray([original[n] for n in names], dtype=float)
        shuffled = rng.permutation(values)
        for name, value in zip(names, shuffled):
            result[name] = float(value)
        if sorted(result[n] for n in names) != sorted(float(v) for v in values):
            raise AssertionError("Stratified trait permutation did not preserve guild marginal")
    if set(result) != set(original):
        raise AssertionError("Source trait-map keys changed")
    return result


def fixture() -> dict:
    demo = {
        ("North", "a"): {"alpha", "beta", "gamma"},
        ("South", "b"): {"alpha", "beta", "delta"},
    }
    h = {"alpha": .5, "beta": 1, "gamma": 2, "delta": 3}
    f = features(demo, h)
    assert len(f) == 2 and all(v[1] > 0 for v in f.values())
    small = {"grass": ["alpha", "beta"], "legume": ["gamma"], "forb": ["delta"]}
    np.random.seed(0)
    p1 = permute_map(h, small, np.random.default_rng(SEED))
    p2 = permute_map(h, small, np.random.default_rng(SEED))
    assert p1 == p2 and sorted(p1.values()) == sorted(h.values())
    assert p1["gamma"] == 2 and p1["delta"] == 3
    assert GUILDS == ("grass", "legume", "forb") and REPS == 999
    return {"status": "FIXTURE_PASS", "checks": 5, "permutations": REPS}


def main(args: argparse.Namespace) -> dict:
    old = json.loads(Path(args.prior).read_text(encoding="utf-8"))
    corrected = json.loads(Path(args.corrected).read_text(encoding="utf-8"))
    saved = json.loads(Path(args.provenance).read_text(encoding="utf-8"))
    if old["status"] != "POSTRESULT_BIODEPTH_HEIGHT_FD_OUT_OF_SITE_VALIDATION_ESTIMATED":
        raise ValueError("PRIOR_HOLD: original observed effect source status changed")
    if saved["status"] != "GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":
        raise ValueError("SOURCE_HOLD: saved GIFT reference gate")
    if corrected["status"] != "POSTRESULT_BIODEPTH_ORIGANUM_GIFT_HEIGHT_SOURCE_SENSITIVITY_VERIFIED":
        raise ValueError("PRIOR_HOLD: botanical corrected archive status")
    if corrected["n_original_plots"] != 174 or corrected["n_source_2010_Community_plot_years"] != 521:
        raise ValueError("PRIOR_HOLD: corrected sample changed")
    if corrected["comparison"]["original_GIFT_13m"]["FD_site_equal_gain"] != old["primary"]["primary_equal_site_FD_incremental_holdout_SSE_gain"]:
        raise ValueError("PRIOR_HOLD: original and corrected archive values disagree")
    srows = source(args.species, "species")
    crows = source(args.codes, "codes")
    names, original_sown, original_metadata = geometry(srows, crows)
    qa, original_h = provenance(srows, crows, return_values=True)
    if qa["status"] != "GIFT_HEIGHT_REFERENCE_PROVENANCE_PASS":
        raise ValueError("SOURCE_HOLD: live GIFT current reference gate")
    if (qa["GIFT_original_target_species_height_and_reference_fingerprint_sha256"] !=
         saved["GIFT_original_target_species_height_and_reference_fingerprint_sha256"] or
        qa["GIFT_bibliography_content_sha256"] != saved["GIFT_bibliography_content_sha256"]):
        raise ValueError("SOURCE_HOLD: original live GIFT source drift")
    if len(original_h) != 88 or original_h.get(ORIGANUM) != 13.0:
        raise ValueError("SOURCE_HOLD: expected original 88 heights/13m oregano not reproduced")
    plan = published_design(args.design)
    unique, ambiguous, contradictory = inferred_guilds(original_sown, plan)
    observed_h = dict(original_h)
    observed_h[ORIGANUM] = 0.90
    pools = {g: sorted(sp for sp in original_h if unique.get(sp) == g) for g in GUILDS}

    # Eligibility is calculated only from original *planting*, no biomass.
    # Structural check is performed before opening plot responses or null scores.
    original_plot_eligible = {}
    for (site, plot), roster in original_sown.items():
        n = sum(s in observed_h for s in roster)
        if n >= 3 and n / len(roster) >= .8:
            original_plot_eligible[(site, plot)] = roster
    structural = check_gates(pools, original_plot_eligible)
    structural["ambiguous_species_heights_held_fixed"] = sum(x in original_h for x in ambiguous)
    structural["contradictory_species_heights_held_fixed"] = sum(x in original_h for x in contradictory)
    structural["original_GIFT_height_taxa_count"] = len(original_h)
    structural["original_original_sown_taxa_count"] = len(names)
    structural["source_sites_for_eligible_plots"] = dict(sorted(Counter(s for s, p in original_plot_eligible).items()))
    if len(original_plot_eligible) != 174 or len(structural["source_sites_for_eligible_plots"]) != 7:
        raise ValueError("SOURCE_HOLD: original 174 eligible plots/7 sites not reproduced")
    print("PRE_NULL_SOURCE_GUILD_SUPPORT_PASS", json.dumps(structural, sort_keys=True), flush=True)

    # The historical source/response workflow verifies original sha256 and
    # that identical 174/521 cohort replays when Kew repair is applied.
    plots, cells, missing, sitepop = composition(srows, crows, args.design, args.community, observed_h, qa)
    if len(plots) != 174 or len(cells) != 521 or missing != 1 or len(sitepop) != 7:
        raise ValueError("SOURCE_HOLD: source responses did not recover original 174/521/7")
    sites = sorted(sitepop)
    predicted = apply_features(cells, features(original_plot_eligible, observed_h))
    for left, right in zip(cells, predicted):
        if abs(left["cwm"] - right["cwm"]) > 1e-12 or abs(left["mpd"] - right["mpd"]) > 1e-12:
            raise ValueError("MODEL_HOLD: planned height features not identical to parent code")
    original_score = evaluate(cells, sites)
    obs = fast_site_gains(cells, sites)
    ref = corrected["comparison"]["Kew_0_90m"]
    if (abs(float(obs.mean()) - ref["FD_site_equal_gain"]) > 1e-10 or
        abs(original_score["primary_equal_site_FD_incremental_holdout_SSE_gain"] - ref["FD_site_equal_gain"]) > 1e-10 or
        int((obs > 0).sum()) != ref["positive_sites"]):
        raise ValueError("MODEL_HOLD: 7-site Kew observed effect not identically reproduced")
    if any(abs(x - y["height_fd_increment_over_cwm"]) > 1e-10 for x, y in
           zip(obs, original_score["site_holdout_records"])):
        raise ValueError("MODEL_HOLD: fast vs source original site estimation differs")

    rng = np.random.default_rng(SEED)
    null = np.empty((REPS, len(sites)), dtype=float)
    for i in range(REPS):
        shuffled_h = permute_map(observed_h, pools, rng)
        random_features = features(original_plot_eligible, shuffled_h)
        randomized_cells = apply_features(cells, random_features)
        null[i, :] = fast_site_gains(randomized_cells, sites)
        if not np.isfinite(null[i, :]).all():
            raise ValueError("MODEL_HOLD: nonfinite randomized source fit")
    null_agg = null.mean(axis=1)
    p_upper = (1 + int(np.sum(null_agg >= np.mean(obs)))) / (REPS + 1)
    null_q = np.quantile(null_agg, [.025, .5, .975])
    null_site = {
        site: {"observed_gain": float(obs[j]),
               "label_null_median": float(np.median(null[:, j])),
               "label_null_q025": float(np.quantile(null[:, j], .025)),
               "label_null_q975": float(np.quantile(null[:, j], .975))}
        for j, site in enumerate(sites)
    }
    return {
        "version": "v0.1",
        "status": "POSTRESULT_GUILD_STRATIFIED_SPECIES_HEIGHT_LABEL_NULL_COMPLETED",
        "design": "docs/BIODEPTH_HEIGHT_TRAIT_LABEL_RANDOMIZATION_DESIGN_V0_1.md",
        "historical_response_plots": len(plots),
        "historical_response_plotyears": len(cells),
        "historical_source_field_sites": sites,
        "source_eligibility": structural,
        "GIFT_bibliography_sha256": qa["GIFT_bibliography_content_sha256"],
        "source_GIFT_height_species_fingerprint_sha256": qa["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
        "source_original_response_editions": "Hector2010 Community only; never Spehn2005 Shoots",
        "model": "M2 over M1: CWM-adjusted mean absolute pairwise log maximum-height diversity; original M0 includes planted richness, guild flags, original year",
        "seed": SEED, "n_permutations": REPS,
        "observed_site_equal_gain": float(obs.mean()),
        "observed_gains_by_site": {s: float(x) for s, x in zip(sites, obs)},
        "observed_site_count_positive": int((obs > 0).sum()),
        "previous_source_bootstrap_ci95": ref["FD_CI95"],
        "null_site_equal_mean": float(null_agg.mean()),
        "null_site_equal_median": float(np.median(null_agg)),
        "null_site_equal_q025_q50_q975": [float(v) for v in null_q],
        "null_site_equal_min_max": [float(np.min(null_agg)), float(np.max(null_agg))],
        "obs_minus_label_null_median": float(obs.mean() - np.median(null_agg)),
        "upper_tail_p_with_plus_one": p_upper,
        "null_reference_top_2p5pct": bool(obs.mean() > null_q[2] and p_upper <= .025),
        "site_diagnostics": null_site,
        "versions": {"python": platform.python_version(), "numpy": np.__version__},
        "nonclaims": [
          "New null outcome is retrospective/exploratory after original FD biomass response and GIFT source correction were observed",
          "No causal inference from one guild-stratified trait-label null; species pools, study sites and species mixtures are non-exchangeable for some mechanisms",
          "No result here estimates or explains family-specific Blomberg K, phylogenetic rho, evolutionary lability or functional-trait evolution",
          "Even a strong label-null result is not an independent positive out-of-site FD effect: the existing 4/7 positive sites and bootstrap interval crossing 0 remain",
          "Original strict BIODEPTH 6-site, global BIEN/sPlotOpen K/FD and NEON authentication gates remain HOLD"
        ],
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for k in ("species", "codes", "design", "community", "provenance", "prior", "corrected", "out"):
        p.add_argument("--" + k)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(fixture()))
    else:
        keys = ("species", "codes", "design", "community", "provenance", "prior", "corrected", "out")
        if not all(getattr(args, k) for k in keys):
            p.error("All eight source/certification paths and --out are required")
        result = main(args)
        dest = Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("POSTRESULT_GUILD_STRATIFIED_SOURCE_NULL", json.dumps({
            k: v for k, v in result.items() if k not in ("site_diagnostics", "nonclaims")
        }, sort_keys=True))
