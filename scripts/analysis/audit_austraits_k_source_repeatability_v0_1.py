#!/usr/bin/env python3
"""Predeclared source-replication feasibility audit for the exact AusTraits K core.

Reads frozen original source compilation and K graph, but NEVER uses observed
K values to calibrate an error parameter or choose a cohort. Species-level
values and dataset identifiers do not enter the aggregate output.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
import duckdb
import yaml

EXPECTED = (254, 42, 13)
DESIGN_STATUS = "POST_K_AND_SHARED_OU_OUTCOME_PRE_SOURCE_COVERAGE_AUDIT_FROZEN"
RESULT_STATUS = "AUSTRAITS_K_SOURCE_REPLICATE_FEASIBILITY_AUDITED"


def summarize_coverage(rows, expected, design):
    """Pure summary of group-level replicate counts; no K or rho response."""
    bysys = defaultdict(list)
    for item in rows:
        sid, fam, trait, species, state, nrecord, ndata, npos, nposdata = item
        bysys[str(sid)].append((str(fam), str(trait), str(species),
                               float(state), int(nrecord), int(ndata),
                               int(npos), int(nposdata)))
    if set(bysys) != set(expected):
        raise ValueError(f"source coverage changed observed graph: {len(bysys)} vs {len(expected)} systems")
    traits = defaultdict(lambda: {"species_cells": 0, "positive_record_replicates": 0,
                                 "multi_dataset_species": 0, "families": set(),
                                 "family_multi_counts": Counter()})
    for sid, meta in expected.items():
        rr = bysys[sid]
        if len(rr) != meta["n_input_species"]:
            raise ValueError(f"source-native K species count differs: {sid} {len(rr)} vs {meta['n_input_species']}")
        if any(not (item[3] > 0) for item in rr):
            raise ValueError(f"nonpositive median in original K core: {sid}")
        fam, trait = meta["family"], meta["trait_name"]
        if any((r[0], r[1]) != (fam, trait) for r in rr):
            raise ValueError("unexpected family trait from source")
        tr = traits[trait]
        tr["species_cells"] += len(rr)
        tr["families"].add(fam)
        for r in rr:
            if r[6] >= 2:
                tr["positive_record_replicates"] += 1
            if r[7] >= 2:
                tr["multi_dataset_species"] += 1
                tr["family_multi_counts"][fam] += 1
    rules = design["predeclared_feasibility"]
    result = {}
    for trait in sorted(traits):
        r = traits[trait]
        fam5 = sum(x >= 5 for x in r["family_multi_counts"].values())
        eligible = (r["multi_dataset_species"] >= rules["minimum_multidataset_species_per_trait"]
                    and fam5 >= rules["minimum_families_per_trait_with_5_multidataset_species"])
        result[trait] = {
            "species_system_cells": r["species_cells"],
            "families": len(r["families"]),
            "species_with_two_observations": r["positive_record_replicates"],
            "species_with_two_datasets": r["multi_dataset_species"],
            "families_with_at_least_5_multi_dataset_species": fam5,
            "qualifies_source_calibration_coverage": bool(eligible)
        }
    if len(result) != EXPECTED[2]:
        raise ValueError(f"source traits missing: {len(result)}")
    nqual = sum(r["qualifies_source_calibration_coverage"] for r in result.values())
    return {
        "version": "v0.1",
        "status": RESULT_STATUS,
        "design_status": DESIGN_STATUS,
        "graph": {"systems": EXPECTED[0], "families": EXPECTED[1], "traits": EXPECTED[2]},
        "predeclared_coverage_rules": rules,
        "qualifying_traits": int(nqual),
        "go_to_external_reliability_calibration": bool(nqual >= rules["minimum_qualifying_traits"]),
        "traits": result,
        "scientific_boundary": "Replicate coverage is source-/intraspecific heterogeneity, not calibrated pure measurement error. No observed-K-derived noise parameters."
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--traits-yml", type=Path, required=True)
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--observed-K", type=Path, required=True)
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    design = json.loads(args.design.read_text())
    if design.get("status") != DESIGN_STATUS:
        raise ValueError("source-coverage decision not frozen")
    k = pd.read_csv(args.observed_K)
    core = pd.read_csv(args.core)
    if (len(k), k.family.nunique(), k.trait_name.nunique()) != EXPECTED:
        raise ValueError("changed original K graph")
    merged = k[["system_id","family","trait_name"]].merge(
        core[["family","trait_name","n_input_species"]],
        how="inner", on=["family","trait_name"], validate="one_to_one")
    if len(merged) != EXPECTED[0] or merged.system_id.nunique() != EXPECTED[0]:
        raise ValueError("non-unique source-native K core join")
    cfg = yaml.safe_load(args.traits_yml.read_text())["traits"]["elements"]
    expected = {}
    cands = []
    for row in merged.itertuples(index=False):
        unit = "" if cfg[row.trait_name].get("units") is None else str(cfg[row.trait_name].get("units")).strip()
        if not unit:
            raise ValueError("trait lacks source-native unit")
        sid = str(row.system_id)
        expected[sid] = {"family": str(row.family), "trait_name": str(row.trait_name),
                         "n_input_species": int(row.n_input_species)}
        cands.append((sid,str(row.family),str(row.trait_name),unit))
    con = duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE candidates (system_id VARCHAR, family_name VARCHAR, trait_name VARCHAR, expected_unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES (?,?,?,?)", cands)
    # Match the original K pipeline eligibility and de-duplication BEFORE
    # counting records. Dataset+observation is a unique observation ID.
    query = r"""
    WITH base AS (
       SELECT c.system_id,
              c.family_name,
              c.trait_name,
              trim(CAST(a.genus AS VARCHAR)) AS genus,
              trim(CAST(a.binomial AS VARCHAR)) AS species,
              trim(CAST(a.dataset_id AS VARCHAR)) AS dataset_id,
              trim(CAST(a.observation_id AS VARCHAR)) AS observation_id,
              try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) AS value_num,
              c.expected_unit,
              coalesce(trim(CAST(a.unit AS VARCHAR)),'') AS unit
       FROM read_parquet(?) a JOIN candidates c
         ON trim(CAST(a.family AS VARCHAR))=c.family_name
        AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
       WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
         AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
         AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
         AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
         AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
         AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
    ), dedup AS (
       SELECT DISTINCT system_id,family_name,trait_name,genus,species,
              dataset_id,observation_id,value_num
       FROM base WHERE value_num IS NOT NULL AND isfinite(value_num)
         AND expected_unit<>'' AND unit=expected_unit
    ), states AS (
       SELECT system_id,family_name,trait_name,species,
              median(value_num) AS median_state,
              count(DISTINCT dataset_id||chr(31)||observation_id) AS n_record,
              count(DISTINCT dataset_id) AS n_dataset,
              count(DISTINCT CASE WHEN value_num>0 THEN dataset_id||chr(31)||observation_id END) AS n_positive_record,
              count(DISTINCT CASE WHEN value_num>0 THEN dataset_id END) AS n_positive_dataset
       FROM dedup
       GROUP BY system_id,family_name,trait_name,species
       HAVING count(DISTINCT genus)=1
    )
    SELECT system_id,family_name,trait_name,species,median_state,
           n_record,n_dataset,n_positive_record,n_positive_dataset
    FROM states ORDER BY system_id,species
    """
    try:
        rows = con.execute(query, [str(args.parquet)]).fetchall()
    finally:
        con.close()
    result = summarize_coverage(rows, expected, design)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({
        "status": result["status"],
        "qualifying_traits": result["qualifying_traits"],
        "go_to_external_reliability_calibration": result["go_to_external_reliability_calibration"],
        "graph": result["graph"]
    }, sort_keys=True))

if __name__ == "__main__":
    main()
