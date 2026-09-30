#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "data" / "bien_trait_support_design_v0_1.json"


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def hold(out_path: Path, design: dict, status: str, diagnosis: str, **extra) -> int:
    out = {
        "version": "v0.1",
        "status": status,
        "design": str(DESIGN.relative_to(ROOT)),
        "outcome_blind": True,
        "biological_trait_values_opened": False,
        "biological_turnover_outcomes_opened": False,
        "gate_pass": False,
        "diagnosis": diagnosis,
        "next_gate": design["next_gate_if_hold"],
        **extra,
    }
    write_json(out_path, out)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--support-table", type=Path, required=True)
    ap.add_argument("--trait-list", type=Path, required=True)
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.support_table.parent.mkdir(parents=True, exist_ok=True)
    args.trait_list.parent.mkdir(parents=True, exist_ok=True)

    d = json.loads(DESIGN.read_text())
    src = d["source"]["public_database_contract_from_pinned_rbien"]

    try:
        con = psycopg2.connect(
            host=src["host"],
            dbname=src["dbname"],
            user=src["user"],
            password="bien_public",
            connect_timeout=30,
        )
    except Exception as exc:
        return hold(
            args.out, d, "HOLD_BIEN_SOURCE_ACCESS",
            "Could not connect to the public BIEN PostgreSQL service.",
            transport_error=f"{type(exc).__name__}: {exc}",
        )

    try:
        with con.cursor() as cur:
            cur.execute("SET statement_timeout = '45min';")

            cur.execute("""
                SELECT db_version::text, db_release_date::text
                FROM bien_metadata a
                JOIN (
                    SELECT MAX(bien_metadata_id) AS max_id
                    FROM bien_metadata
                ) b
                ON a.bien_metadata_id = b.max_id;
            """)
            version_row = cur.fetchone()
            if version_row is None:
                return hold(
                    args.out, d, "HOLD_BIEN_VERSION_UNRESOLVED",
                    "BIEN metadata table did not return a current database version."
                )
            db_version, db_release_date = version_row
            if str(db_version).strip() != d["source"]["expected_database_version"]:
                return hold(
                    args.out, d, "HOLD_BIEN_VERSION_DRIFT",
                    "The live BIEN database is not the pre-frozen BIEN 4.2 release.",
                    observed_database_version=db_version,
                    observed_release_date=db_release_date,
                )

            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'agg_traits'
                ORDER BY ordinal_position;
            """)
            schema_rows = cur.fetchall()
            schema = {str(name): str(dtype) for name, dtype in schema_rows}
            missing = [x for x in d["required_agg_traits_fields"] if x not in schema]
            if missing:
                return hold(
                    args.out, d, "HOLD_BIEN_REQUIRED_SCHEMA_MISSING",
                    "Required agg_traits fields are absent in BIEN 4.2.",
                    observed_database_version=db_version,
                    observed_release_date=db_release_date,
                    missing_required_fields=missing,
                    observed_agg_traits_fields=sorted(schema),
                )

            try:
                cur.execute("SELECT postgis_version();")
                postgis_version = str(cur.fetchone()[0])
            except Exception as exc:
                con.rollback()
                return hold(
                    args.out, d, "HOLD_BIEN_POSTGIS_UNAVAILABLE",
                    "The frozen EPSG:6933 25-km cell rule cannot be executed because PostGIS is unavailable.",
                    observed_database_version=db_version,
                    observed_release_date=db_release_date,
                    postgis_error=f"{type(exc).__name__}: {exc}",
                )

            # Metadata only: enumerate trait names, never trait values.
            cur.execute("""
                SELECT DISTINCT trait_name
                FROM agg_traits
                WHERE trait_name IS NOT NULL
                  AND btrim(trait_name) <> ''
                ORDER BY trait_name;
            """)
            trait_names = [str(x[0]) for x in cur.fetchall()]
            with args.trait_list.open("w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["trait_name"])
                for x in trait_names:
                    w.writerow([x])

            # Support-only aggregate. No trait_value, unit, method or provenance
            # field is selected or used for qualification.
            support_sql = """
                WITH temporal AS (
                    SELECT
                        scrubbed_family,
                        trait_name,
                        COUNT(DISTINCT scrubbed_species_binomial) AS temporal_species
                    FROM agg_traits
                    WHERE id IS NOT NULL
                      AND scrubbed_family IS NOT NULL
                      AND btrim(scrubbed_family) <> ''
                      AND scrubbed_species_binomial IS NOT NULL
                      AND btrim(scrubbed_species_binomial) <> ''
                      AND trait_name IS NOT NULL
                      AND btrim(trait_name) <> ''
                    GROUP BY scrubbed_family, trait_name
                ),
                eligible_temporal AS (
                    SELECT scrubbed_family, trait_name
                    FROM temporal
                    WHERE temporal_species >= %s
                ),
                geo_record_counts AS (
                    SELECT
                        a.scrubbed_family,
                        a.trait_name,
                        a.scrubbed_species_binomial,
                        COUNT(DISTINCT a.id) AS georeferenced_records
                    FROM agg_traits a
                    INNER JOIN eligible_temporal e
                      ON a.scrubbed_family = e.scrubbed_family
                     AND a.trait_name = e.trait_name
                    WHERE a.id IS NOT NULL
                      AND a.scrubbed_species_binomial IS NOT NULL
                      AND btrim(a.scrubbed_species_binomial) <> ''
                      AND a.latitude IS NOT NULL
                      AND a.longitude IS NOT NULL
                      AND a.latitude BETWEEN -90 AND 90
                      AND a.longitude BETWEEN -180 AND 180
                    GROUP BY
                        a.scrubbed_family,
                        a.trait_name,
                        a.scrubbed_species_binomial
                    HAVING COUNT(DISTINCT a.id) >= %s
                ),
                geo_coords AS (
                    SELECT DISTINCT
                        a.scrubbed_family,
                        a.trait_name,
                        a.scrubbed_species_binomial,
                        a.latitude,
                        a.longitude
                    FROM agg_traits a
                    INNER JOIN geo_record_counts g
                      ON a.scrubbed_family = g.scrubbed_family
                     AND a.trait_name = g.trait_name
                     AND a.scrubbed_species_binomial = g.scrubbed_species_binomial
                    WHERE a.id IS NOT NULL
                      AND a.latitude IS NOT NULL
                      AND a.longitude IS NOT NULL
                      AND a.latitude BETWEEN -90 AND 90
                      AND a.longitude BETWEEN -180 AND 180
                ),
                geo_cells AS (
                    SELECT
                        c.scrubbed_family,
                        c.trait_name,
                        c.scrubbed_species_binomial,
                        COUNT(DISTINCT (
                            floor(ST_X(p.geom) / 25000.0)::bigint::text
                            || ':' ||
                            floor(ST_Y(p.geom) / 25000.0)::bigint::text
                        )) AS unique_25km_cells
                    FROM geo_coords c
                    CROSS JOIN LATERAL (
                        SELECT ST_Transform(
                            ST_SetSRID(ST_MakePoint(c.longitude, c.latitude), 4326),
                            6933
                        ) AS geom
                    ) p
                    GROUP BY
                        c.scrubbed_family,
                        c.trait_name,
                        c.scrubbed_species_binomial
                ),
                spatial AS (
                    SELECT
                        scrubbed_family,
                        trait_name,
                        COUNT(*) FILTER (
                            WHERE unique_25km_cells >= %s
                        ) AS spatial_species
                    FROM geo_cells
                    GROUP BY scrubbed_family, trait_name
                )
                SELECT
                    t.scrubbed_family,
                    t.trait_name,
                    t.temporal_species,
                    COALESCE(s.spatial_species, 0) AS spatial_species
                FROM temporal t
                LEFT JOIN spatial s
                  ON t.scrubbed_family = s.scrubbed_family
                 AND t.trait_name = s.trait_name
                ORDER BY t.scrubbed_family, t.trait_name;
            """
            forbidden_tokens = [x.lower() for x in d["forbidden_support_query_fields"]]
            sql_lower = support_sql.lower()
            accidental = [x for x in forbidden_tokens if x in sql_lower]
            if accidental:
                raise RuntimeError(f"support SQL contains forbidden fields: {accidental}")

            q = d["eligibility"]
            cur.execute(
                support_sql,
                (
                    int(q["temporal_min_species_per_family_trait"]),
                    int(q["spatial_min_georeferenced_records_per_species"]),
                    int(q["spatial_min_unique_25km_cells_per_species"]),
                ),
            )
            support_rows = cur.fetchall()

    except Exception as exc:
        try:
            con.rollback()
        except Exception:
            pass
        return hold(
            args.out, d, "HOLD_BIEN_SUPPORT_QUERY",
            "BIEN 4.2 support-only aggregate query did not complete.",
            observed_database_version=(db_version if "db_version" in locals() else None),
            observed_release_date=(db_release_date if "db_release_date" in locals() else None),
            query_error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        try:
            con.close()
        except Exception:
            pass

    rows = []
    for family, trait, temporal_species, spatial_species in support_rows:
        temporal_species = int(temporal_species)
        spatial_species = int(spatial_species)
        passed = (
            temporal_species >= int(q["temporal_min_species_per_family_trait"])
            and spatial_species >= int(q["spatial_min_species_per_family_trait"])
        )
        rows.append({
            "family": str(family),
            "trait_name": str(trait),
            "temporal_species": temporal_species,
            "spatial_species": spatial_species,
            "family_trait_pass": passed,
        })

    fields = ["family", "trait_name", "temporal_species", "spatial_species", "family_trait_pass"]
    with args.support_table.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    passing = [x for x in rows if x["family_trait_pass"]]
    passing_families = sorted({x["family"] for x in passing})
    passing_traits = sorted({x["trait_name"] for x in passing})

    vg = d["source_viability_gate"]
    gate = (
        len(passing_families) >= int(vg["minimum_distinct_passing_families"])
        and len(passing_traits) >= int(vg["minimum_distinct_passing_traits"])
    )

    out = {
        "version": "v0.1",
        "status": "BIEN_TRAIT_SUPPORT_PASS" if gate else "HOLD_BIEN_TRAIT_SUPPORT",
        "design": str(DESIGN.relative_to(ROOT)),
        "outcome_blind": True,
        "biological_trait_values_opened": False,
        "biological_turnover_outcomes_opened": False,
        "database_version": db_version,
        "database_release_date": db_release_date,
        "postgis_version": postgis_version,
        "required_schema_pass": True,
        "n_trait_names": len(trait_names),
        "n_family_trait_systems_audited": len(rows),
        "n_family_trait_systems_pass": len(passing),
        "n_distinct_passing_families": len(passing_families),
        "n_distinct_passing_traits": len(passing_traits),
        "passing_families": passing_families,
        "passing_traits": passing_traits,
        "passing_systems": passing,
        "gate_pass": gate,
        "support_table": str(args.support_table),
        "trait_list": str(args.trait_list),
        "next_gate": d["next_gate_if_pass"] if gate else d["next_gate_if_hold"],
        "interpretation": (
            "BIEN 4.2 contains enough family-level and trait-level structural support to proceed to trait representation, phylogeny crosswalk and informativeness gates without having opened trait values."
            if gate else
            "BIEN 4.2 does not meet the frozen prospective family/trait replication gate. Do not inspect trait values; the finite-family design allows a pre-outcome switch to AusTraits."
        ),
    }
    write_json(args.out, out)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
