#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import duckdb

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"austraits_trait_support_design_v0_2.json"
PRE=ROOT/"results"/"austraits_metadata_preflight_v0_1"/"result.json"

def digest(path:Path, algo:str)->str:
    h=hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--parquet",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--table-out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.table_out.parent.mkdir(parents=True,exist_ok=True)
    d=json.loads(DESIGN.read_text())
    pre=json.loads(PRE.read_text())
    if pre["status"]!="AUSTRAITS_SCHEMA_PREFLIGHT_PASS" or pre["raw_trait_values_opened"] is not False:
        raise RuntimeError("AusTraits schema prerequisite did not pass cleanly")

    integrity=(
      a.parquet.stat().st_size==d["source"]["parquet"]["size_bytes"]
      and digest(a.parquet,"sha256")==d["source"]["parquet"]["sha256"]
      and digest(a.parquet,"md5")==d["source"]["parquet"]["md5"]
    )
    if not integrity:
        raise RuntimeError("pinned AusTraits parquet integrity mismatch")

    q=d["spatial_support"]
    R=float(q["projection"]["earth_radius_m"])
    std=30.0
    cell=int(q["cell_size_m"])
    min_temp=int(d["temporal_support"]["minimum_species_per_family_trait"])
    min_geo=int(q["minimum_georeferenced_records_per_species"])
    min_cells=int(q["minimum_cells_per_species"])
    min_spatial=int(q["minimum_spatial_species_per_family_trait"])

    sql=f"""
    WITH base AS (
      SELECT
        trim(CAST(family AS VARCHAR)) AS family,
        trim(CAST(binomial AS VARCHAR)) AS species,
        trim(CAST(trait_name AS VARCHAR)) AS trait_name,
        trim(CAST(observation_id AS VARCHAR)) AS observation_id,
        trim(CAST(unit AS VARCHAR)) AS unit,
        trim(CAST(dataset_id AS VARCHAR)) AS dataset_id,
        try_cast("latitude (deg)" AS DOUBLE) AS lat,
        try_cast("longitude (deg)" AS DOUBLE) AS lon
      FROM read_parquet(?)
      WHERE lower(trim(CAST(taxon_rank AS VARCHAR)))='species'
        AND family IS NOT NULL AND trim(CAST(family AS VARCHAR))<>''
        AND binomial IS NOT NULL AND trim(CAST(binomial AS VARCHAR))<>''
        AND trait_name IS NOT NULL AND trim(CAST(trait_name AS VARCHAR))<>''
        AND observation_id IS NOT NULL AND trim(CAST(observation_id AS VARCHAR))<>''
        AND value IS NOT NULL AND trim(CAST(value AS VARCHAR))<>''
    ),
    records AS (
      SELECT DISTINCT family, species, trait_name, observation_id, unit, dataset_id, lat, lon
      FROM base
    ),
    temporal_species AS (
      SELECT family,trait_name,species,count(DISTINCT observation_id) AS n_records
      FROM records
      GROUP BY family,trait_name,species
    ),
    temporal_ft AS (
      SELECT family,trait_name,count(*) AS temporal_species
      FROM temporal_species
      GROUP BY family,trait_name
    ),
    geo_records AS (
      SELECT DISTINCT
        family,trait_name,species,observation_id,
        floor(({R}*radians(lon)*cos(radians({std})))/{cell})::BIGINT AS cell_x,
        floor(({R}*sin(radians(lat))/cos(radians({std})))/{cell})::BIGINT AS cell_y
      FROM records
      WHERE lat BETWEEN -90 AND 90 AND lon BETWEEN -180 AND 180
    ),
    spatial_species AS (
      SELECT family,trait_name,species,
        count(DISTINCT observation_id) AS georef_records,
        count(DISTINCT concat(cell_x,':',cell_y)) AS occupied_cells
      FROM geo_records
      GROUP BY family,trait_name,species
    ),
    spatial_ft AS (
      SELECT family,trait_name,
        count(*) AS georeferenced_species,
        count(*) FILTER (WHERE georef_records>={min_geo} AND occupied_cells>={min_cells}) AS spatial_qualifying_species
      FROM spatial_species
      GROUP BY family,trait_name
    ),
    diagnostics AS (
      SELECT family,trait_name,
        count(DISTINCT unit) FILTER (WHERE unit IS NOT NULL AND unit<>'') AS distinct_units,
        string_agg(DISTINCT unit,' | ' ORDER BY unit) FILTER (WHERE unit IS NOT NULL AND unit<>'') AS unit_labels,
        count(DISTINCT dataset_id) FILTER (WHERE dataset_id IS NOT NULL AND dataset_id<>'') AS distinct_datasets
      FROM records
      GROUP BY family,trait_name
    )
    SELECT
      t.family,t.trait_name,t.temporal_species,
      coalesce(s.georeferenced_species,0) AS georeferenced_species,
      coalesce(s.spatial_qualifying_species,0) AS spatial_qualifying_species,
      coalesce(g.distinct_units,0) AS distinct_units,
      g.unit_labels,
      coalesce(g.distinct_datasets,0) AS distinct_datasets,
      (t.temporal_species>={min_temp} AND coalesce(s.spatial_qualifying_species,0)>={min_spatial}) AS joint_support_pass
    FROM temporal_ft t
    LEFT JOIN spatial_ft s USING(family,trait_name)
    LEFT JOIN diagnostics g USING(family,trait_name)
    ORDER BY t.family,t.trait_name
    """
    # Value is permitted only in the WHERE presence predicate; it must never be returned.
    select_tail=sql.lower().split("select",1)[-1]
    con=duckdb.connect(database=":memory:")
    cur=con.execute(sql,[str(a.parquet)])
    cols=[x[0] for x in cur.description]
    if "value" in {x.lower() for x in cols}:
        raise RuntimeError("raw-value firewall violated")
    rows=[dict(zip(cols,r)) for r in cur.fetchall()]
    con.close()

    fields=["family","trait_name","temporal_species","georeferenced_species",
            "spatial_qualifying_species","distinct_units","unit_labels",
            "distinct_datasets","joint_support_pass"]
    with a.table_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    passing=[r for r in rows if bool(r["joint_support_pass"])]
    families=sorted({str(r["family"]) for r in passing})
    gate=len(families)>=int(d["joint_gate"]["minimum_independent_families"])
    systems=[{
      "family":str(r["family"]),
      "trait_name":str(r["trait_name"]),
      "temporal_species":int(r["temporal_species"]),
      "georeferenced_species":int(r["georeferenced_species"]),
      "spatial_qualifying_species":int(r["spatial_qualifying_species"]),
      "distinct_units":int(r["distinct_units"]),
      "unit_labels":r["unit_labels"],
      "distinct_datasets":int(r["distinct_datasets"])
    } for r in passing]

    result={
      "version":"v0.2",
      "status":"AUSTRAITS_TRAIT_SUPPORT_PASS" if gate else "HOLD_AUSTRAITS_TRAIT_SUPPORT",
      "design":str(DESIGN.relative_to(ROOT)),
      "outcome_blind":True,
      "raw_trait_values_opened":False,
      "biological_turnover_outcomes_opened":False,
      "trait_value_presence_only":True,
      "trait_value_returned":False,
      "row_level_species_returned":False,
      "row_level_coordinates_returned":False,
      "source_version":"7.0.0",
      "file_integrity_pass":True,
      "thresholds":{
        "temporal_min_species":min_temp,
        "spatial_min_species":min_spatial,
        "spatial_min_georeferenced_records":min_geo,
        "spatial_min_cells":min_cells,
        "cell_size_m":cell,
        "minimum_independent_families":int(d["joint_gate"]["minimum_independent_families"])
      },
      "n_family_trait_systems":len(rows),
      "n_joint_support_family_trait_systems":len(passing),
      "n_independent_qualifying_families":len(families),
      "qualifying_families":families,
      "qualifying_systems":systems,
      "gate_pass":gate,
      "next_gate":d["next_gate_if_pass"] if gate else d["next_gate_if_hold"]
    }
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
