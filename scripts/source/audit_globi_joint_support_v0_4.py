#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "data" / "globi_joint_support_design_v0_4.json"
PREREQ = ROOT / "results" / "globi_parquet_schema_v0_3" / "result.json"


def canonical_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--table-out", type=Path, required=True)
    ap.add_argument("--local-tsv-gz", type=Path)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.table_out.parent.mkdir(parents=True, exist_ok=True)

    design = json.loads(DESIGN.read_text())
    prereq = json.loads(PREREQ.read_text())
    if prereq["status"] != "GLOBI_PARQUET_SCHEMA_ALIAS_PASS":
        raise RuntimeError("GloBI schema prerequisite did not pass")
    if prereq["interaction_rows_opened"] is not False:
        raise RuntimeError("schema prerequisite unexpectedly opened rows")

    q = design["qualification"]
    local_tsv = args.local_tsv_gz
    if local_tsv is not None:
        if not local_tsv.exists():
            raise RuntimeError(f"local TSV fallback not found: {local_tsv}")
        with gzip.open(local_tsv, "rt", encoding="utf-8", newline="") as fh:
            header = next(csv.reader(fh, delimiter="\t"))
        missing_header = [x for x in design["projected_columns"] if x not in header]
        if missing_header:
            result = {
                "version": "v0.4",
                "status": "HOLD_GLOBI_TSV_HEADER_MISMATCH",
                "design": str(DESIGN.relative_to(ROOT)),
                "outcome_blind": True,
                "support_query_executed": False,
                "interaction_rows_opened_for_support_only": False,
                "raw_edge_identities_persisted": False,
                "biological_turnover_outcomes_opened": False,
                "transport": "TSV_LOCAL_FALLBACK",
                "header_field_count": len(header),
                "missing_projected_columns": missing_header,
                "gate_pass": False,
                "next_gate": design["next_gate_if_persistent_transport_hold"],
            }
            args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        source_expr = "read_csv_auto(?, delim='\\t', header=true, all_varchar=true, compression='gzip')"
        source_arg = str(local_tsv)
        transport_name = "TSV_LOCAL_FALLBACK"
    else:
        source_expr = "read_parquet(?)"
        source_arg = design["primary_file"]["url"]
        transport_name = "PARQUET_REMOTE"

    transport_error = None
    transport_errors: list[str] = []
    transport_attempts = 0
    rows: list[dict] = []

    sql = r"""
    WITH base AS (
      SELECT
        trim(CAST(sourceNamespace AS VARCHAR)) AS ns,
        trim(CAST(interactionTypeId AS VARCHAR)) AS itid,
        trim(CAST(interactionTypeName AS VARCHAR)) AS itname,
        trim(CAST(sourceTaxonSpeciesName AS VARCHAR)) AS focal,
        trim(CAST(targetTaxonSpeciesName AS VARCHAR)) AS partner,
        try_cast(decimalLatitude AS DOUBLE) AS lat,
        try_cast(decimalLongitude AS DOUBLE) AS lon,
        try_cast(regexp_extract(CAST(eventDate AS VARCHAR), '^([0-9]{4})', 1) AS INTEGER) AS yr
      FROM {SOURCE_EXPR}
      WHERE sourceNamespace IS NOT NULL
        AND interactionTypeId IS NOT NULL
        AND sourceTaxonSpeciesName IS NOT NULL
        AND targetTaxonSpeciesName IS NOT NULL
        AND trim(CAST(sourceNamespace AS VARCHAR)) <> ''
        AND trim(CAST(interactionTypeId AS VARCHAR)) <> ''
        AND trim(CAST(sourceTaxonSpeciesName AS VARCHAR)) <> ''
        AND trim(CAST(targetTaxonSpeciesName AS VARCHAR)) <> ''
    ),
    sys_names AS (
      SELECT
        ns, itid,
        min(itname) FILTER (WHERE itname IS NOT NULL AND itname <> '') AS interaction_type_name,
        count(DISTINCT itname) FILTER (WHERE itname IS NOT NULL AND itname <> '') AS interaction_name_variants,
        count(*) AS species_rank_edge_rows
      FROM base
      GROUP BY ns, itid
    ),
    focal_partner AS (
      SELECT DISTINCT ns, itid, focal, partner
      FROM base
    ),
    focal_partner_n AS (
      SELECT ns, itid, focal, count(*) AS n_partners
      FROM focal_partner
      GROUP BY ns, itid, focal
    ),
    temporal AS (
      SELECT
        ns, itid,
        count(*) AS temporal_focal_taxa,
        count(*) FILTER (WHERE n_partners >= 3) AS temporal_focal_taxa_3plus_partners
      FROM focal_partner_n
      GROUP BY ns, itid
    ),
    geo AS (
      SELECT DISTINCT ns, itid, focal, lat, lon, yr
      FROM base
      WHERE lat BETWEEN -90 AND 90
        AND lon BETWEEN -180 AND 180
        AND yr BETWEEN 1000 AND 2026
    ),
    sites AS (
      SELECT DISTINCT ns, itid, lat, lon, yr
      FROM geo
    ),
    spatial AS (
      SELECT ns, itid, count(*) AS site_year_strata
      FROM sites
      GROUP BY ns, itid
    ),
    focal_sites AS (
      SELECT ns, itid, focal, count(*) AS n_site_year_strata
      FROM geo
      GROUP BY ns, itid, focal
    ),
    repeated AS (
      SELECT
        ns, itid,
        count(*) FILTER (WHERE n_site_year_strata >= 2) AS repeated_focal_taxa
      FROM focal_sites
      GROUP BY ns, itid
    )
    SELECT
      s.ns AS source_namespace,
      s.itid AS interaction_type_id,
      s.interaction_type_name,
      s.interaction_name_variants,
      s.species_rank_edge_rows,
      coalesce(t.temporal_focal_taxa, 0) AS temporal_focal_taxa,
      coalesce(t.temporal_focal_taxa_3plus_partners, 0) AS temporal_focal_taxa_3plus_partners,
      coalesce(sp.site_year_strata, 0) AS site_year_strata,
      coalesce(r.repeated_focal_taxa, 0) AS repeated_focal_taxa
    FROM sys_names s
    LEFT JOIN temporal t USING (ns, itid)
    LEFT JOIN spatial sp USING (ns, itid)
    LEFT JOIN repeated r USING (ns, itid)
    ORDER BY s.ns, s.itid
    """
    sql = sql.replace("{SOURCE_EXPR}", source_expr)

    policy = design["transport_policy"]
    max_attempts = int(policy["maximum_attempts_per_workflow"])
    backoff = [int(x) for x in policy["backoff_seconds"]]

    def is_retriable_transport(message: str) -> bool:
        m = message.lower()
        return (
            "429" in m
            or "http 500" in m
            or "http 502" in m
            or "http 503" in m
            or "http 504" in m
            or "timeout" in m
            or "timed out" in m
            or "connection reset" in m
            or "temporary" in m
        )

    execution_attempts = max_attempts if local_tsv is None else 1
    for attempt in range(execution_attempts):
        transport_attempts = attempt + 1
        if local_tsv is None and attempt > 0:
            time.sleep(backoff[attempt])
        con = duckdb.connect(database=":memory:")
        try:
            if local_tsv is None:
                con.execute("INSTALL httpfs")
                con.execute("LOAD httpfs")
            cur = con.execute(sql, [source_arg])
            columns = [x[0] for x in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
            transport_error = None
            break
        except Exception as exc:
            transport_error = f"{type(exc).__name__}: {exc}"
            transport_errors.append(transport_error)
            if local_tsv is not None or not is_retriable_transport(transport_error):
                break
        finally:
            con.close()

    if transport_error is not None:
        result = {
            "version": "v0.4",
            "status": policy["terminal_status_after_exhaustion"],
            "design": str(DESIGN.relative_to(ROOT)),
            "transport_policy_amendment": design["transport_policy_amendment"],
            "transport": transport_name,
            "outcome_blind": True,
            "support_query_executed": False,
            "interaction_rows_opened_for_support_only": False,
            "raw_edge_identities_persisted": False,
            "biological_turnover_outcomes_opened": False,
            "transport_attempts": transport_attempts,
            "transport_errors": transport_errors,
            "transport_error": transport_error,
            "gate_pass": False,
            "next_gate": design["next_gate_if_persistent_transport_hold"],
        }
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    for row in rows:
        row["joint_support_pass"] = (
            int(row["temporal_focal_taxa_3plus_partners"]) >= int(q["temporal_min_focal_taxa"])
            and int(row["site_year_strata"]) >= int(q["spatial_min_site_year_strata"])
            and int(row["repeated_focal_taxa"]) >= int(q["spatial_min_repeated_focal_taxa"])
        )

    fields = [
        "source_namespace",
        "interaction_type_id",
        "interaction_type_name",
        "interaction_name_variants",
        "species_rank_edge_rows",
        "temporal_focal_taxa",
        "temporal_focal_taxa_3plus_partners",
        "site_year_strata",
        "repeated_focal_taxa",
        "joint_support_pass",
    ]
    with args.table_out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    passing = [r for r in rows if r["joint_support_pass"]]
    namespaces = sorted({str(r["source_namespace"]) for r in passing})
    gate = len(namespaces) >= int(q["minimum_independent_source_namespaces"])

    result = {
        "version": "v0.4",
        "status": "GLOBI_JOINT_SUPPORT_PASS" if gate else "HOLD_GLOBI_JOINT_SUPPORT",
        "design": str(DESIGN.relative_to(ROOT)),
        "outcome_blind": True,
        "projected_columns": design["projected_columns"],
        "support_query_executed": True,
        "interaction_rows_opened_for_support_only": True,
        "raw_edge_identities_persisted": False,
        "biological_turnover_outcomes_opened": False,
        "transport_error": None,
        "transport": transport_name,
        "qualification": q,
        "n_candidate_systems": len(rows),
        "n_joint_support_systems": len(passing),
        "n_qualifying_source_namespaces": len(namespaces),
        "qualifying_source_namespaces": namespaces,
        "qualifying_systems": passing,
        "support_table": str(args.table_out),
        "support_table_sha256": canonical_sha256(args.table_out),
        "gate_pass": gate,
        "next_gate": design["next_gate_if_pass"] if gate else design["next_gate_if_hold"],
        "interpretation": (
            "The final GloBI route has enough structurally supported independent source namespaces to justify a source-semantic network audit. This is not evidence of turnover or rewiring."
            if gate
            else
            "The final GloBI route does not meet the frozen independent-source support requirement. Do not lower thresholds or add a third primary interaction source."
        ),
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
