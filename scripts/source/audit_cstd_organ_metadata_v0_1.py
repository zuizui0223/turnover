#!/usr/bin/env python3
"""CSTD v4 pre-outcome organ-support screen.

Metadata-only: reads species/family/trait/source labels and WHETHER a value exists.
Never aggregates or compares trait values, calculates K, or tests the organ hypothesis.
The report can establish structural HOLD, not source independence or scientific PASS.
"""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook

EXPECTED_MD5 = "9d02dfed7de29484d2f5c5137235cabe"
FILE_DOI = "10.6084/m9.figshare.28152035.v4"
ORGAN_TRAITS = {
    "fruitlength": ("fruit_length", "fruit"),
    "fruitwidth": ("fruit_width", "fruit"),
    "fruitheight": ("fruit_height", "fruit"),
    "seedlength": ("seed_length", "seed"),
    "seedwidth": ("seed_width", "seed"),
    "seeddrymass": ("seed_dry_mass", "seed"),
    "leafarea": ("leaf_area", "vegetative"),
    "leaflength": ("leaf_length", "vegetative"),
    "leafwidth": ("leaf_width", "vegetative"),
    "petiolelength": ("petiole_length", "vegetative"),
    "plantheight": ("plant_height", "vegetative"),
    "leafmassperarea": ("leaf_mass_per_area", "vegetative"),
}
# Seed mass without a documented drying definition must NEVER silently map to
# seed_dry_mass; likewise seed height is not one of the frozen organ traits.
AMBIGUOUS = {"seedmass", "seedfreshmass", "wholeplantheight", "height", "leafsize"}
COL_ALIASES = {
    "species": ("scientificname", "species", "speciesname", "acceptedname", "latinname", "speciesaccepted"),
    "family": ("family", "familyname", "familyaccepted"),
    "trait": ("traitname", "trait", "traitenglish", "traitnameenglish", "traittype"),
    "value": ("traitvalue", "value", "measurementvalue", "observedvalue"),
    "source": ("reference", "referenceid", "source", "sourceid", "citation", "doi"),
}


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").strip().lower())


def header_audit(sheet):
    rows = list(sheet.iter_rows(min_row=1, max_row=min(sheet.max_row, 10), values_only=True))
    parsed = [[str(c).strip() if c is not None else "" for c in row] for row in rows]
    known = {x for aliases in COL_ALIASES.values() for x in aliases}
    scored = []
    for i, cols in enumerate(parsed):
        keys = [normalized(v) for v in cols]
        score = sum(k in known for k in keys)
        scored.append((score, -i, i, cols))
    _, _, idx, header = max(scored)
    mapping = {}
    for logical, aliases in COL_ALIASES.items():
        matches = [i for i, cell in enumerate(header) if normalized(cell) in aliases]
        if len(matches) == 1:
            mapping[logical] = matches[0]
    return idx + 1, header, mapping


def evaluate(path):
    md5 = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            md5.update(chunk)
    digest = md5.hexdigest()
    if digest != EXPECTED_MD5:
        raise ValueError("Unexpected CSTD workbook MD5; version identity mismatch")

    book = load_workbook(path, read_only=True, data_only=True)
    report = {
        "status": "HOLD_PRE_OUTCOME",
        "frozen_external_protocol": "data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json",
        "input": {"doi": FILE_DOI, "md5": digest, "size": path.stat().st_size},
        "worksheets": book.sheetnames,
        "source_independence": "UNKNOWN: 694 cited sources require original-measurement and AusTraits lineage audit",
        "trait_semantics": "UNVERIFIED: names alone are not homologous organ definitions",
        "phylogeny": "UNTESTED: no source-native S3/prune matched-tip crosswalk",
        "no_phenotype_magnitudes_read_or_calculated": True,
        "no_K_computed": True,
    }
    name = next((x for x in book.sheetnames if normalized(x) == "seedtraitdata"), None)
    if not name:
        report["reason"] = "HOLD_SCHEMA: exact 'Seed trait data' worksheet absent"
        return report
    ws = book[name]
    header_row, headers, columns = header_audit(ws)
    report["schema"] = {
        "sheet": name,
        "header_row": header_row,
        "headers": headers,
        "matched_metadata_columns": {k: headers[v] for k, v in columns.items()},
        "missing_required": sorted(set(("species", "family", "trait", "value", "source")) - set(columns)),
    }
    if report["schema"]["missing_required"]:
        report["reason"] = "HOLD_SCHEMA: metadata fields not unambiguously identified; do not infer aliases from outcomes"
        return report

    by_species = defaultdict(set)
    meta_labels = Counter()
    source_refs = set()
    valid_rows = 0
    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        def cell(which):
            pos = columns[which]
            return row[pos] if pos < len(row) else None

        # Checking existence only; the numeric measurement is not read.
        pos = columns["value"]
        has_measurement = pos < len(row) and row[pos] is not None and str(row[pos]).strip() != ""
        if not has_measurement:
            continue
        family = str(cell("family") or "").strip()
        species = str(cell("species") or "").strip()
        label = normalized(cell("trait"))
        source = str(cell("source") or "").strip()
        if not family or not species or not source or not label:
            continue
        valid_rows += 1
        meta_labels[label] += 1
        source_refs.add(source)
        if label in ORGAN_TRAITS:
            named_trait, _ = ORGAN_TRAITS[label]
            by_species[(family, species)].add(named_trait)

    families = defaultdict(lambda: defaultdict(set))
    for (family, species), names in by_species.items():
        for trait in names:
            families[family][trait].add(species)
    reproductive = {trait for trait, group in ORGAN_TRAITS.values() if group in ("seed", "fruit")}
    vegetative = {trait for trait, group in ORGAN_TRAITS.values() if group == "vegetative"}
    candidates = []
    all_traits = set()
    families_fruit = set()
    families_seed = set()
    for family, sets in sorted(families.items()):
        for rep in sorted(reproductive.intersection(sets)):
            for veg in sorted(vegetative.intersection(sets)):
                overlap = len(sets[rep] & sets[veg])
                if overlap >= 20:
                    candidates.append({"family": family, "reproductive": rep, "vegetative": veg,
                                       "same_species": overlap})
                    all_traits.update((rep, veg))
                    (families_fruit if rep.startswith("fruit_") else families_seed).add(family)
    qualified_families = {c["family"] for c in candidates}
    report["metadata_support_only"] = {
        "nonempty_metadata_rows": valid_rows,
        "distinct_source_labels": len(source_refs),
        "distinct_family_species_with_mapped_trait": len(by_species),
        "mapped_trait_counts": {
            trait: sum(trait in names for names in by_species.values()) for trait in sorted(all_traits)
        },
        "observed_trait_labels_not_approved": {
            name: n for name, n in meta_labels.most_common(200) if name not in ORGAN_TRAITS
        },
        "candidate_matched_pairs_ge_20": len(candidates),
        "families_with_pair_ge_20": len(qualified_families),
        "families_fruit_with_pair": len(families_fruit),
        "families_seed_with_pair": len(families_seed),
        "matched_reproductive_names": sorted(reproductive & all_traits),
        "matched_vegetative_names": sorted(vegetative & all_traits),
        "pairs": candidates,
    }
    report["reason"] = (
        "HOLD_SOURCE_PROVENANCE_AND_SEMANTICS: raw trait values/K must remain unopened; "
        "source origin, part homology and two phylogeny crosswalks are not verified. "
        "Structural counts are CANDIDATES, never eligibility PASS."
    )
    report["structural_necessary_gate_possible_unverified"] = (
        len(qualified_families) >= 12
        and len(families_fruit) >= 6
        and len(families_seed) >= 6
        and len(reproductive & all_traits) >= 2
        and len(vegetative & all_traits) >= 2
    )
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "reason": result["reason"],
        "sheets": result["worksheets"],
        "structural": result.get("metadata_support_only", {}).get("families_with_pair_ge_20", "UNTESTED"),
        "schema": result.get("schema", {}).get("matched_metadata_columns", {}),
        "header_names_only": result.get("schema", {}).get("headers", []),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
