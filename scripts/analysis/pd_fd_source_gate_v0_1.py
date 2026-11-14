#!/usr/bin/env python3
"""Pre-outcome structural gate for prospective community PD–FD study.

Requires *normalized* CSV/TSV tables, never imputes species/traits and never
calculates an ecological outcome. Standard library only.

plot_species: plot_id,species,abundance
taxonomy:     species,family
traits:       species,trait,value,source_id
memory:       family,trait,rho_s3,rho_prune
plot_meta:    plot_id,dataset,biome,area_m2

A real data PASS is structural support only. Phylogeny, source independence,
effect-scale and data-use rights must be audited separately.
"""
import argparse
import collections
import csv
import json
import math
import re
from pathlib import Path

MIN_COVERAGE = 0.80
MIN_N_EFF = 2.5
MIN_SPECIES = 3
MIN_FAMILY_PLOTS = 20
MIN_FAMILIES = 12
MIN_CELLS = 500
MIN_DATASETS = 5

def _read(path, fields):
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
        absent = set(fields).difference(reader.fieldnames or [])
        if absent:
            raise ValueError(f"{path.name}: missing required columns {sorted(absent)}")
        return list(reader)

def _binomial(raw):
    name = " ".join(str(raw or "").strip().split())
    if re.fullmatch(r"[A-Z][A-Za-z-]+ [a-z][a-z-]+", name):
        return name
    return None

def _finite(s):
    try:
        x = float(s)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None

def _unique_map(rows, key_col, val_col, description):
    result = {}
    for row in rows:
        key, val = row[key_col].strip(), row[val_col].strip()
        if not key or not val:
            continue
        if key in result and result[key] != val:
            raise ValueError(f"ambiguous {description}: {key}")
        result[key] = val
    return result

def audit(plots, taxonomy, traits, memory, metadata):
    tax_rows = [
        {"species": _binomial(r["species"]), "family": r["family"].strip()}
        for r in taxonomy
    ]
    tax = _unique_map(
        [r for r in tax_rows if r["species"]], "species", "family", "family assignment"
    )
    trait_index = {}
    for r in traits:
        s, t = _binomial(r["species"]), r["trait"].strip()
        value = _finite(r["value"])
        if not s or not t or value is None:
            continue
        if not r["source_id"].strip():
            continue
        key = (s, t)
        if key in trait_index and trait_index[key] != value:
            raise ValueError(f"conflicting source-aggregated trait: {key}")
        trait_index[key] = value

    memory_index = {}
    traits_by_family = collections.defaultdict(set)
    for r in memory:
        f, t = r["family"].strip(), r["trait"].strip()
        s3, prune = _finite(r["rho_s3"]), _finite(r["rho_prune"])
        if not f or not t or s3 is None or prune is None:
            continue
        if abs(s3) > 1 or abs(prune) > 1:
            raise ValueError(f"rho outside [-1,1]: {f}/{t}")
        k = (f, t)
        if k in memory_index and memory_index[k] != (s3, prune):
            raise ValueError(f"conflicting memory system: {k}")
        memory_index[k] = (s3, prune)
        traits_by_family[f].add(t)

    meta = {}
    for r in metadata:
        plot_id = r["plot_id"].strip()
        if not plot_id:
            continue
        cur = (r["dataset"].strip(), r["biome"].strip(), _finite(r["area_m2"]))
        if plot_id in meta and cur != meta[plot_id]:
            raise ValueError(f"conflicting plot metadata: {plot_id}")
        meta[plot_id] = cur

    abundance = collections.defaultdict(float)
    all_species = set()
    all_plots = set()
    invalid_rows = 0
    for r in plots:
        p, s = r["plot_id"].strip(), _binomial(r["species"])
        x = _finite(r["abundance"])
        if not p or not s or x is None or x <= 0:
            invalid_rows += 1
            continue
        all_plots.add(p)
        all_species.add(s)
        abundance[(p, s)] += x

    group = collections.defaultdict(dict)
    for (p, s), x in abundance.items():
        if s in tax:
            group[(p, tax[s])][s] = x

    eligible = []
    by_family_plots = collections.defaultdict(set)
    by_dataset = collections.Counter()
    by_trait = collections.Counter()
    candidates = 0
    bad_meta = 0
    for (p, f), sp in group.items():
        info = meta.get(p)
        if not info or not info[0] or not info[1] or info[2] is None or info[2] <= 0:
            bad_meta += 1
            continue
        total = sum(sp.values())
        for t in traits_by_family.get(f, set()):
            candidates += 1
            measured = [v for s, v in sp.items() if (s, t) in trait_index]
            if len(measured) < MIN_SPECIES or total <= 0:
                continue
            covered = sum(measured)
            fraction = covered / total
            n_eff = covered * covered / sum(v * v for v in measured)
            if fraction < MIN_COVERAGE or n_eff < MIN_N_EFF:
                continue
            eligible.append((p, f, t))
            by_family_plots[f].add(p)
            by_dataset[info[0]] += 1
            by_trait[t] += 1

    qualified_families = sorted(
        f for f, plots_for_family in by_family_plots.items()
        if len(plots_for_family) >= MIN_FAMILY_PLOTS
    )
    qualified_set = set(qualified_families)
    qualified_cells = [(p, f, t) for p, f, t in eligible if f in qualified_set]
    qualified_datasets = {
        meta[p][0] for p, f, t in qualified_cells
    }
    pass_support = (len(qualified_families) >= MIN_FAMILIES
                    and len(qualified_cells) >= MIN_CELLS
                    and len(qualified_datasets) >= MIN_DATASETS)
    match_rate = len(all_species.intersection(tax)) / len(all_species) if all_species else 0
    return {
        "status": ("STRUCTURAL_PASS_ONLY_PHYLOGENY_AND_PROVENANCE_PENDING"
                   if pass_support and match_rate >= 0.90
                   else "PRE_OUTCOME_HOLD_STRUCTURAL_SUPPORT"),
        "definition": "No PD, FD, biomass, causal or predictive outcome is calculated",
        "source_quality": "NOT_VERIFIED: taxon names/trait sources/phylogeny must be audited",
        "unique_plot_ids": len(all_plots),
        "unique_plot_species": len(abundance),
        "unique_binomial_species": len(all_species),
        "species_taxonomy_exact_match": len(all_species.intersection(tax)),
        "species_taxonomy_exact_match_fraction": round(match_rate, 6),
        "invalid_community_rows_skipped": invalid_rows,
        "plot_family_groups_missing_complete_metadata": bad_meta,
        "memory_family_trait_systems": len(memory_index),
        "plot_family_trait_candidates": candidates,
        "eligible_plot_family_trait_cells_before_family_floor": len(eligible),
        "eligible_families_with_at_least_20_distinct_plots": len(qualified_families),
        "qualified_plot_family_trait_cells": len(qualified_cells),
        "qualified_source_datasets": len(qualified_datasets),
        "qualified_aggregated_trait_counts": dict(
            sorted(collections.Counter(t for _, f, t in qualified_cells).items())
        ),
        "required_thresholds": {
            "min_taxonomy_exact_match_fraction": 0.90,
            "min_species_per_plot_family_trait": MIN_SPECIES,
            "min_abundance_coverage": MIN_COVERAGE,
            "min_effective_species": MIN_N_EFF,
            "min_distinct_plots_per_family": MIN_FAMILY_PLOTS,
            "min_families": MIN_FAMILIES,
            "min_qualified_cells": MIN_CELLS,
            "min_source_datasets": MIN_DATASETS,
        },
        "next_required": [
            "Confirm original sampling/source permissions and source-study overlap",
            "Audit all family-specific phylogeny native tips and branch lengths",
            "Verify independent species-trait measurements and taxon crosswalk",
            "Only then calculate held-out-community FD/MPD responses",
        ],
    }

def _self_test():
    ps = [{"plot_id": "p1", "species": x, "abundance": "1"} for x in (
        "Acacia alpha", "Acacia beta", "Acacia gamma"
    )]
    ps += [{"plot_id": "p2", "species": "Acacia alpha", "abundance": "2"}]
    tax = [{"species": x["species"], "family": "Fabaceae"} for x in ps]
    traits = [{"species": x["species"], "trait": "plant_height",
               "value": "2", "source_id": "independent-test"} for x in ps]
    mem = [{"family": "Fabaceae", "trait": "plant_height",
            "rho_s3": "0.1", "rho_prune": "0.09"}]
    meta = [{"plot_id": p, "dataset": "test", "biome": "test", "area_m2": "100"}
            for p in ("p1", "p2")]
    report = audit(ps, tax, traits, mem, meta)
    assert report["eligible_plot_family_trait_cells_before_family_floor"] == 1, report
    assert report["unique_plot_ids"] == 2, report
    assert report["status"] == "PRE_OUTCOME_HOLD_STRUCTURAL_SUPPORT", report
    return {"status": "SELF_TEST_PASS", "checks": 3}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    for arg in ("plot-species", "taxonomy", "traits", "memory", "plot-meta", "out"):
        parser.add_argument("--" + arg)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(_self_test(), indent=2))
        return
    required_args = ("plot_species", "taxonomy", "traits", "memory", "plot_meta", "out")
    if any(getattr(args, name) is None for name in required_args):
        parser.error("all five input files and --out are required")
    report = audit(
        _read(args.plot_species, ("plot_id", "species", "abundance")),
        _read(args.taxonomy, ("species", "family")),
        _read(args.traits, ("species", "trait", "value", "source_id")),
        _read(args.memory, ("family", "trait", "rho_s3", "rho_prune")),
        _read(args.plot_meta, ("plot_id", "dataset", "biome", "area_m2")),
    )
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
