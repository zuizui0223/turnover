#!/usr/bin/env python3
"""Reproducible NHM plant-organ trait source-coverage study.

Source-first and phenotype-outcome-blind: use only non-empty trait-value
indicators. Never parse value magnitudes, compute K, assign an evolutionary
mechanism, or infer direct primary measurement from a flora description.
One WFO species is counted once per family × pair × floristic source.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict, Counter
from pathlib import Path

SOURCE_SHA = "4843c22bb2fc91018d9828dcddebf067c83b1097"
SHA256 = {
    "wfo": "4f6aee584d91e3cc50989192890281b2bfb35d91d66fc12d467fec2316b24287",
    "combined": "7548836b788ad5c9a3a6eaf382c05646ac2b0be73d889092228a3fba9dea5e0b",
    "cv": "14188d4c9691e99ebe11b4e2448af54f59a25657a4fa30140222a76b918edeef",
}
REPRODUCTIVE = {
    "seed_length": "seed max. length [mm]",
    "seed_width": "seed max. width [mm]",
}
VEGETATIVE = {
    "leaf_length": "leaf max. length [cm]",
    "leaf_width": "leaf max. width [cm]",
    "plant_height": "plant max. height [m]",
}
CV_VEGETATIVE = {
    "herbarium_leaf_length": "length_LM",
    "herbarium_leaf_width": "width_LM",
    "herbarium_leaf_area": "area",
}
SOURCES = ("combined", "bhl", "eflora_china", "eflora_north_america",
           "eflora_pakistan", "ecoflora")
FLORA_REPLICATION_SOURCES = ("eflora_china", "eflora_north_america",
                             "eflora_pakistan", "ecoflora")
EMPTY = {"", "NA", "N/A", "nan", "null", "None", "NaN", "-", "missing"}


def binomial(v):
    """No fuzzy synonym collapsing; exactly two original Latin name tokens."""
    t = " ".join(str(v or "").strip().split())
    if not re.fullmatch(r"[A-Za-z][A-Za-z-]* [a-z][a-z-]*", t):
        return None
    return t.lower()


def is_present(v):
    # Does not parse phenotype magnitude or consult sign/distribution/K.
    return str(v or "").strip() not in EMPTY


def check(path, target=None):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    got = h.hexdigest()
    if target is not None and got != target:
        raise ValueError(f"Source identity mismatch {path}")
    return got


def family_map(path):
    map_ = {}
    conflict = set()
    missing_family = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"binomial", "family"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("WFO source schema mismatch")
        for row in reader:
            n = binomial(row["binomial"])
            family = (row["family"] or "").strip()
            if not n or not family:
                missing_family += 1
                continue
            if n in map_ and map_[n] != family:
                conflict.add(n)
            else:
                map_[n] = family
    for n in conflict:
        map_.pop(n, None)
    return map_, len(conflict), missing_family


def source_presence(path, family):
    # One matched taxon can occur in multiple source description rows; species
    # presence is unioned *within that source*, not interpreted as one primary.
    states = defaultdict(set)
    raw_rows = accepted_names = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        target = set(REPRODUCTIVE.values()) | set(VEGETATIVE.values()) | {"taxon"}
        if not target.issubset(reader.fieldnames or []):
            raise ValueError("NHM description source missing one of frozen schema columns")
        for row in reader:
            raw_rows += 1
            sp = binomial(row["taxon"])
            if sp is None or sp not in family:
                continue
            accepted_names += 1
            for trait, col in {**REPRODUCTIVE, **VEGETATIVE}.items():
                if is_present(row[col]):
                    states[sp].add(trait)
    return states, raw_rows, accepted_names


def cv_presence(path, family):
    states = defaultdict(set)
    count = unknown_sheet_taxon = accepted_sheets = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not {"herbarium_sheet", *CV_VEGETATIVE.values()}.issubset(reader.fieldnames or []):
            raise ValueError("NHM herbarium leaf schema mismatch")
        for row in reader:
            count += 1
            sheet = str(row["herbarium_sheet"] or "").strip()
            m = re.fullmatch(r"(.+)_([0-9]+)", sheet)
            parts = m.group(1).split("_") if m else []
            if len(parts) != 2:
                unknown_sheet_taxon += 1
                continue
            sp = binomial(" ".join(parts))
            if not sp or sp not in family:
                unknown_sheet_taxon += 1
                continue
            accepted_sheets += 1
            for trait, col in CV_VEGETATIVE.items():
                if is_present(row[col]):
                    states[sp].add(trait)
    return states, count, unknown_sheet_taxon, accepted_sheets


def pair_support(states, family, reps, vegs, source):
    pairs = defaultdict(set)
    for sp, traits in states.items():
        for r in reps:
            if r not in traits:
                continue
            for v in vegs:
                if v in traits:
                    pairs[(family[sp], r, v)].add(sp)
    qualified = [
        {"family": k[0], "reproductive": k[1], "vegetative": k[2],
         "matched_species": len(species)}
        for k, species in sorted(pairs.items()) if len(species) >= 20
    ]
    all_families = sorted(set(r["family"] for r in qualified))
    return {
        "source": source,
        "source_type": "aggregated-botanical-descriptions" if source in ("combined","bhl")
            else "single-flora-source" if not source.startswith("herbarium")
            else "herbarium-image-morphometrics",
        "matched_pairs_with_20plus_species": len(qualified),
        "families_with_pair": len(all_families),
        "families_with_seed_width_pair": len({q["family"] for q in qualified
                                            if q["reproductive"] == "seed_width"}),
        "families": all_families,
        "pairs": qualified,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--wfo", type=Path, required=True)
    p.add_argument("--cv", type=Path, required=True)
    for source in SOURCES:
        p.add_argument("--" + source.replace("_","-"),type=Path,required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    sourcefiles = {s: getattr(a,s) for s in SOURCES}
    fingerprints = {
        "wfo": check(a.wfo, SHA256["wfo"]),
        "cv": check(a.cv, SHA256["cv"]),
    }
    for s, path in sourcefiles.items():
        fingerprints[s] = check(path, SHA256.get(s))
    family,conflict,missing=family_map(a.wfo)
    result={
        "status":"HOLD_EXTERNAL_PRIMARY_SOURCE_PROVENANCE",
        "source":"NaturalHistoryMuseum/plant-traits",
        "pin_git_commit": SOURCE_SHA,
        "fingerprints": fingerprints,
        "WFO_taxon_crosswalk": {
            "unique_exact_binomials": len(family),
            "conflicting_family_labels_excluded": conflict,
            "invalid_names_or_missing_family": missing,
        },
        "no_numeric_trait_magnitude_used_for_inference": True,
        "no_K_or_phylogenetic_process_estimated":True,
        "source_results":{},
        "frozen_original_external_organ_protocol":
            "data/austraits_reproductive_vegetative_k_external_validation_protocol_v0_1.json",
    }
    all_states={}
    for source,path in sourcefiles.items():
        states,rows,accepted=source_presence(path,family)
        all_states[source]=states
        entry=pair_support(states,family,list(REPRODUCTIVE),list(VEGETATIVE),source)
        entry["source_rows"]=rows
        entry["wfo_matched_rows"]=accepted
        result["source_results"][source]=entry

    leaf_states,rows,unknown,accepted=cv_presence(a.cv,family)
    joint=defaultdict(set)
    for sp,tr in all_states["combined"].items():
        joint[sp].update(tr)
    for sp,tr in leaf_states.items():
        joint[sp].update(tr)
    entry=pair_support(joint,family,list(REPRODUCTIVE),list(CV_VEGETATIVE),"herbarium_with_description")
    entry.update({
        "herbarium_leaf_rows":rows,
        "unresolved_herbarium_taxon_rows":unknown,
        "matched_WFO_taxon_leaf_rows":accepted,
        "herbarium_unique_species_with_measurement_presence":len(leaf_states)
    })
    result["source_results"]["herbarium_with_description"]=entry
    supported_per_flora=Counter()
    for source in FLORA_REPLICATION_SOURCES:
        for family_ in result["source_results"][source]["families"]:
            supported_per_flora[family_] += 1
    result["family_support_across_flora_types"]={
        "families_in_2plus_flora_types":sum(n>=2 for n in supported_per_flora.values()),
        "names_in_2plus_flora_types":sorted(f for f,n in supported_per_flora.items() if n>=2),
        "number_of_qualifying_flora_sources":len(FLORA_REPLICATION_SOURCES)
    }
    result["original_full_organ_external_protocol_status"]={
        "numeric_fruit_morphology_in_nhm_description_schema":False,
        "independent_primary_observation_lineage_confirmed":False,
        "matched_S3_and_prune_tree_support_confirmed":False,
        "decision":"HOLD_PRE_OUTCOME. Broad seed-vs-leaf *structural* coverage does not pass the original fruit+seed primary-source validation."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Summary only; do not log taxon-level observations or data values.
    summary = {k:{m:v[m] for m in (
        "source_rows","matched_pairs_with_20plus_species","families_with_pair",
        "families_with_seed_width_pair"
    ) if m in v} for k,v in result["source_results"].items()}
    print("NHM_ORGAN_PRESENCE_GATE="+json.dumps({
        "status":result["status"],"by_source":summary,
        "families_in_2plus_flora_types":
            result["family_support_across_flora_types"]["families_in_2plus_flora_types"],
        "original_protocol_decision":result["original_full_organ_external_protocol_status"]["decision"]
    },ensure_ascii=False))


if __name__=="__main__":
    main()
