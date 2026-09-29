#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "data" / "globi_joint_support_design_v0_4.json"
AMENDMENT = ROOT / "data" / "globi_support_transport_amendment_v0_6.json"
PREREQ = ROOT / "results" / "globi_parquet_schema_v0_3" / "result.json"
PREDECESSOR = ROOT / "results" / "globi_joint_support_v0_5" / "result.json"


SQL = r"""
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
  FROM read_parquet(?)
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
    ns,
    itid,
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
    ns,
    itid,
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
    ns,
    itid,
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


def file_md5_and_size(path: Path) -> tuple[str, int]:
    digest = hashlib.md5()
    size = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(16 * 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(8 * 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def download_once(local_file: Path, amendment: dict) -> dict:
    p = amendment["transport_protocol"]
    local_file.parent.mkdir(parents=True, exist_ok=True)
    local_file.unlink(missing_ok=True)

    cmd = [
        "curl",
        "--location",
        "--fail",
        "--silent",
        "--show-error",
        "--retry",
        str(int(p["download_retries"])),
        "--retry-all-errors",
        "--retry-max-time",
        str(int(p["retry_max_time_seconds"])),
        "--connect-timeout",
        str(int(p["connect_timeout_seconds"])),
        "--user-agent",
        str(p["user_agent"]),
        "--output",
        str(local_file),
        str(p["url"]),
    ]
    completed = subprocess.run(cmd, text=True, capture_output=True)
    if completed.returncode != 0:
        local_file.unlink(missing_ok=True)
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"curl exit {completed.returncode}: {detail}")

    md5, size = file_md5_and_size(local_file)
    expected_size = int(p["expected_size_bytes"])
    expected_md5 = str(p["expected_md5"]).lower()
    if size != expected_size:
        local_file.unlink(missing_ok=True)
        raise RuntimeError(f"size mismatch: expected {expected_size}, observed {size}")
    if md5.lower() != expected_md5:
        local_file.unlink(missing_ok=True)
        raise RuntimeError(f"md5 mismatch: expected {expected_md5}, observed {md5}")

    return {
        "size_bytes": size,
        "md5": md5,
        "user_agent": p["user_agent"],
        "custom_accept_header": p["custom_accept_header"],
        "source_url": p["url"],
    }


def query_support(local_file: Path, threads: int) -> list[dict]:
    con = duckdb.connect(database=":memory:", config={"threads": str(int(threads))})
    cur = con.execute(SQL, [str(local_file)])
    columns = [x[0] for x in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    con.close()
    return rows


def write_support_table(rows: list[dict], path: Path, q: dict) -> tuple[list[dict], list[str]]:
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
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    passing = [row for row in rows if row["joint_support_pass"]]
    namespaces = sorted({str(row["source_namespace"]) for row in passing})
    return passing, namespaces


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--table-out", type=Path, required=True)
    ap.add_argument("--cache-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.table_out.parent.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    design = json.loads(DESIGN.read_text())
    amendment = json.loads(AMENDMENT.read_text())
    prereq = json.loads(PREREQ.read_text())
    predecessor = json.loads(PREDECESSOR.read_text())

    if prereq["status"] != "GLOBI_PARQUET_SCHEMA_ALIAS_PASS":
        raise RuntimeError("GloBI schema prerequisite did not pass")
    if predecessor["scientific_gate_adjudicated"] is not False:
        raise RuntimeError("v0.5 unexpectedly adjudicated the scientific gate")

    unchanged = [
        "source_changed",
        "file_changed",
        "checksum_changed",
        "projected_columns_changed",
        "support_thresholds_changed",
        "system_definition_changed",
        "species_rank_rule_changed",
        "spatial_support_proxy_changed",
        "biological_outcomes_opened",
    ]
    if any(amendment[key] is not False for key in unchanged):
        raise RuntimeError("v0.6 transport amendment changed a frozen scientific field")

    local_file = args.cache_dir / "interactions.parquet"
    receipt = None
    transport_error = None
    rows: list[dict] = []

    try:
        receipt = download_once(local_file, amendment)
        rows = query_support(
            local_file,
            amendment["transport_protocol"]["post_download_scan"]["threads"],
        )
    except Exception as exc:
        transport_error = f"{type(exc).__name__}: {exc}"
    finally:
        local_file.unlink(missing_ok=True)

    if transport_error is not None:
        result = {
            "version": "v0.6",
            "status": "HOLD_GLOBI_SUPPORT_TRANSPORT",
            "design": str(DESIGN.relative_to(ROOT)),
            "transport_amendment": str(AMENDMENT.relative_to(ROOT)),
            "outcome_blind": True,
            "scientific_gate_adjudicated": False,
            "support_query_executed": False,
            "interaction_rows_opened_for_support_only": False,
            "raw_edge_identities_persisted": False,
            "biological_turnover_outcomes_opened": False,
            "download_receipt": receipt,
            "transport_error": transport_error,
            "gate_pass": None,
            "next_gate": "The scientific support gate remains unadjudicated. Do not interpret transport failure as a biological result.",
        }
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    q = design["qualification"]
    passing, namespaces = write_support_table(rows, args.table_out, q)
    gate = len(namespaces) >= int(q["minimum_independent_source_namespaces"])

    result = {
        "version": "v0.6",
        "status": "GLOBI_JOINT_SUPPORT_PASS" if gate else "HOLD_GLOBI_JOINT_SUPPORT",
        "design": str(DESIGN.relative_to(ROOT)),
        "transport_amendment": str(AMENDMENT.relative_to(ROOT)),
        "outcome_blind": True,
        "scientific_gate_adjudicated": True,
        "transport_mode": amendment["transport_protocol"]["mode"],
        "download_receipt": receipt,
        "transport_error": None,
        "projected_columns": design["projected_columns"],
        "support_query_executed": True,
        "interaction_rows_opened_for_support_only": True,
        "raw_edge_identities_persisted": False,
        "biological_turnover_outcomes_opened": False,
        "qualification": q,
        "n_candidate_systems": len(rows),
        "n_joint_support_systems": len(passing),
        "n_qualifying_source_namespaces": len(namespaces),
        "qualifying_source_namespaces": namespaces,
        "qualifying_systems": passing,
        "support_table": str(args.table_out),
        "support_table_sha256": sha256_file(args.table_out),
        "gate_pass": gate,
        "next_gate": design["next_gate_if_pass"] if gate else design["next_gate_if_hold"],
        "interpretation": (
            "The final GloBI route has enough structurally supported independent source namespaces to justify a source-semantic network audit. This is not evidence of turnover or rewiring."
            if gate
            else
            "The final GloBI route fails the frozen scientific support requirement. Do not lower thresholds or add a third primary interaction source."
        ),
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
