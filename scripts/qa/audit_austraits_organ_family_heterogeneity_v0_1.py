#!/usr/bin/env python3
"""Frozen-aggregate family heterogeneity audit for the post-discovery organ-K paper.

This is a descriptive REPORTING audit, not a new biological K fit, test,
independent replication, or family-specific evolutionary-mechanism inference.
Uses only immutable pre-existing per-family counts, never trait records.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

INPUT = Path("results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/reproductive_vegetative_lofo.json")
MANIFEST = Path("results/austraits_organ_paper_frozen_aggregate_inputs_v0_1/frozen_input_manifest.json")
EXPECTED = {"S3": (406, 313, 34, 27, 23), "prune_only": (397, 314, 34, 30, 23)}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def axis_summary(axis, counts):
    items = counts["per_family_descriptive"]
    require(isinstance(items, dict) and items, "missing per-family counts: " + axis)
    rows = []
    for family, v in sorted(items.items()):
        n = v["n_cross_organ_pair_comparisons"]
        wins = v["n_reproductive_K_higher"]
        require(type(n) is int and type(wins) is int and 0 <= wins <= n and n > 0,
                "invalid family counts: " + family)
        rate = wins / n
        require(math.isclose(rate, v["reproductive_K_higher_rate"], abs_tol=1e-12),
                "per-family rate mismatch: " + family)
        rows.append({"family": family, "n": n, "wins": wins, "rate": rate})
    n_total = sum(r["n"] for r in rows)
    wins_total = sum(r["wins"] for r in rows)
    require(n_total == counts["n_supported_family_pair_observations"], "pair total mismatch")
    require(wins_total == counts["n_reproductive_K_higher"], "wins total mismatch")
    require(len(rows) == counts["n_independent_families_with_cross_organ_comparisons"],
            "family count mismatch")
    require(math.isclose(wins_total / n_total, counts["pair_weighted_reproductive_K_higher_rate"],
                         abs_tol=1e-12), "pair rate mismatch")
    family_mean = sum(r["rate"] for r in rows) / len(rows)
    require(math.isclose(family_mean, counts["equal_family_mean_reproductive_higher_rate"],
                         abs_tol=1e-12), "family-equal rate mismatch")
    majority = [r for r in rows if 2 * r["wins"] > r["n"]]
    inverse = [r for r in rows if 2 * r["wins"] < r["n"]]
    tied = [r for r in rows if 2 * r["wins"] == r["n"]]
    n5 = [r for r in rows if r["n"] >= 5]
    n10 = [r for r in rows if r["n"] >= 10]
    expected = EXPECTED[axis]
    require((n_total, wins_total, len(rows), len(majority), len(n5)) == expected,
            "frozen source cohort or family-majority audit drift: " + axis)
    leave_out = [
        {"family": r["family"], "remaining_n": n_total - r["n"],
         "remaining_wins": wins_total - r["wins"],
         "remaining_rate": (wins_total - r["wins"]) / (n_total - r["n"])}
        for r in rows
    ]
    leave_out.sort(key=lambda r: (r["remaining_rate"], r["family"]))
    require(len(leave_out) == 34 and all(x["remaining_n"] > 0 for x in leave_out),
            "invalid deletion diagnostics")
    representative = {}
    for family in ("Asteraceae", "Casuarinaceae", "Fabaceae", "Poaceae"):
        r = next(z for z in rows if z["family"] == family)
        representative[family] = {"wins": r["wins"], "n": r["n"], "rate": r["rate"]}
    return {
        "tree": axis,
        "family_count": len(rows),
        "comparison_count": n_total,
        "reproductive_higher_count": wins_total,
        "pair_weighted_rate": wins_total / n_total,
        "family_equal_mean_rate": family_mean,
        "original_family_cluster_bootstrap_CI95":
            counts["family_bootstrap_equal_family_CI95"],
        "families_with_reproductive_majority": len(majority),
        "families_with_vegetative_majority": len(inverse),
        "families_tied": len(tied),
        "families_with_5_or_more_comparisons": len(n5),
        "family_equal_rate_n_ge5": sum(r["rate"] for r in n5) / len(n5),
        "families_with_10_or_more_comparisons": len(n10),
        "family_equal_rate_n_ge10": sum(r["rate"] for r in n10) / len(n10),
        "kish_family_weight_equivalent": n_total ** 2 / sum(r["n"] ** 2 for r in rows),
        "leave_one_family_out_pair_rate_low": leave_out[0],
        "leave_one_family_out_pair_rate_high": leave_out[-1],
        "vegetative_majority_families_n_ge5": [
            r for r in inverse if r["n"] >= 5
        ],
        "illustrative_families_post_hoc": representative
    }


def audit(data):
    d = data["reproductive_vegetative_matched_tip"]
    summaries = {k: axis_summary(k, d[k]) for k in ("S3", "prune_only")}
    fams = {
        k: d[k]["per_family_descriptive"] for k in ("S3", "prune_only")
    }
    require(set(fams["S3"]) == set(fams["prune_only"]), "family support differs")
    flips = []
    consistently_inverse_n5 = []
    xs, ys = [], []
    for family in sorted(fams["S3"]):
        a, b = fams["S3"][family], fams["prune_only"][family]
        p, q = a["reproductive_K_higher_rate"], b["reproductive_K_higher_rate"]
        xs.append(p)
        ys.append(q)
        ma = 2 * a["n_reproductive_K_higher"] > a["n_cross_organ_pair_comparisons"]
        mb = 2 * b["n_reproductive_K_higher"] > b["n_cross_organ_pair_comparisons"]
        if ma != mb:
            flips.append(family)
        if (not ma and not mb
                and a["n_reproductive_K_higher"] * 2 < a["n_cross_organ_pair_comparisons"]
                and b["n_reproductive_K_higher"] * 2 < b["n_cross_organ_pair_comparisons"]
                and min(a["n_cross_organ_pair_comparisons"],
                        b["n_cross_organ_pair_comparisons"]) >= 5):
            consistently_inverse_n5.append(family)
    require(flips == ["Elaeocarpaceae", "Lauraceae", "Phyllanthaceae"],
            "unexpected cross-tree majority-direction differences")
    require(consistently_inverse_n5 == ["Casuarinaceae", "Rubiaceae"],
            "unexpected supported inverse-majority families")
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    numer = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom = math.sqrt(sum((x - mean_x) ** 2 for x in xs) *
                      sum((y - mean_y) ** 2 for y in ys))
    require(denom > 0, "no variation in family rates")
    joint = data["reproductive_vegetative_both_trees"]
    require(
        joint["n_reproductive_higher_on_both"] +
        joint["n_vegetative_higher_on_both"] +
        joint["n_tree_axis_disagreements"] == joint["n_evaluable_on_both_trees"] == 397,
        "cross-tree contrast totals inconsistent"
    )
    return {
        "status": "PASS_FROZEN_AGGREGATE_FAMILY_DESCRIPTIVE_AUDIT",
        "source": str(INPUT),
        "post_discovery_exploratory": True,
        "raw_trait_values_used": False,
        "new_K_or_OU_models_fitted": 0,
        "independent_external_validation": False,
        "nominal_family_specific_significance_tests": 0,
        "axes": summaries,
        "cross_tree_descriptive": {
            "families_in_both": len(xs),
            "family_rate_pearson_r_not_independent_replication": numer / denom,
            "families_with_majority_direction_change": flips,
            "families_with_inverse_majority_on_both_n_ge5": consistently_inverse_n5,
            "individual_pair_common_tree_comparisons": joint["n_evaluable_on_both_trees"],
            "individual_pair_tree_direction_disagreements": joint["n_tree_axis_disagreements"],
            "individual_pair_tree_direction_disagreement_rate":
                joint["n_tree_axis_disagreements"] / joint["n_evaluable_on_both_trees"]
        },
        "limits": [
            "Named trait pairs within one family reuse taxa, traits and sources; family counts are not independent evolutionary transitions.",
            "Prune and S3 use overlapping observations and do not constitute independent datasets.",
            "A n>=5 screen describes reporting support, not a confirmatory discovery threshold.",
            "K is relative phylogenetic covariance, not evolutionary velocity, OU alpha, or proof of selection.",
            "All organ classes and displayed families were considered after the source outcomes; no new hypothesis-testing p values were generated."
        ]
    }


def self_test(data):
    good = audit(data)
    require(good["status"].startswith("PASS_"), "positive control failed")
    mutated = copy.deepcopy(data)
    p = mutated["reproductive_vegetative_matched_tip"]["S3"]["per_family_descriptive"]["Asteraceae"]
    p["n_reproductive_K_higher"] += 1
    try:
        audit(mutated)
    except AssertionError:
        pass
    else:
        raise AssertionError("corrupted source was not rejected")
    mutated = copy.deepcopy(data)
    mutated["reproductive_vegetative_both_trees"]["n_tree_axis_disagreements"] += 1
    try:
        audit(mutated)
    except AssertionError:
        pass
    else:
        raise AssertionError("cross-tree total corruption was not rejected")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    raw = args.input.read_bytes()
    m = json.loads(args.manifest.read_text(encoding="utf-8"))
    name = args.input.name
    require(hashlib.sha256(raw).hexdigest() == m["file_sha256"][name],
            "source SHA256 does not match permanent frozen-input manifest")
    d = json.loads(raw)
    if args.self_test:
        self_test(d)
    result = audit(d)
    result["source_sha256_verified"] = True
    result["source_sha256"] = m["file_sha256"][name]
    content = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "S3": {k: result["axes"]["S3"][k] for k in (
            "reproductive_higher_count", "comparison_count",
            "families_with_reproductive_majority")},
        "prune": {k: result["axes"]["prune_only"][k] for k in (
            "reproductive_higher_count", "comparison_count",
            "families_with_reproductive_majority")},
        "cross_tree": result["cross_tree_descriptive"]
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
