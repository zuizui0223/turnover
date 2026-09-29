#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "data" / "globi_joint_support_design_v0_4.json"
AMENDMENT = ROOT / "data" / "globi_support_transport_amendment_v0_5.json"
PREREQ = ROOT / "results" / "globi_parquet_schema_v0_3" / "result.json"


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


def canonical_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configure_remote(con: duckdb.DuckDBPyConnection, amendment: dict) -> None:
    p = amendment["transport_protocol"]
    r = p["remote_scan"]
    ua = p["user_agent"].replace("'", "''")
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute(f"SET custom_user_agent = '{ua}'")
    con.execute(f"SET threads = {int(r['duckdb_threads'])}")
    con.execute(f"SET http_retries = {int(r['http_retries'])}")
    con.execute(f"SET http_retry_wait_ms = {int(r['http_retry_wait_ms'])}")
    con.execute(f"SET http_retry_backoff = {float(r['http_retry_backoff'])}")
    con.execute(f"SET http_timeout = {int(r['http_timeout_seconds'])}")
    con.execute(
        "SET disable_parquet_prefetching = "
        + ("true" if r["disable_parquet_prefetching"] else "false")
    )


def query_support(path_or_url: str, amendment: dict, remote: bool) -> list[dict]:
    con = duckdb.connect(database=":memory:")
    if remote:
        configure_remote(con, amendment)
    cur = con.execute(SQL, [path_or_url])
    cols = [x[0] for x in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    con.close()
    return rows


def parse_retry_after(value: str | None, fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return max(1, min(int(value), 180))
    except ValueError:
        return fallback


def download_verified(url: str, dest: Path, amendment: dict, expected_size: int, expected_md5: str) -> dict:
    p = amendment["transport_protocol"]
    f = p["fallback_on_http_429_or_remote_failure"]
    ua = p["user_agent"]
    retries = int(f["download_retries"])
    part = dest.with_suffix(dest.suffix + ".part")
    dest.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    for attempt in range(1, retries + 1):
        part.unlink(missing_ok=True)
        md5 = hashlib.md5()
        size = 0
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": ua,
                    "Accept": "application/octet-stream",
                },
            )
            with urllib.request.urlopen(req, timeout=180) as resp, part.open("wb") as fh:
                while True:
                    chunk = resp.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    fh.write(chunk)
                    md5.update(chunk)
                    size += len(chunk)

            observed_md5 = md5.hexdigest()
            if size != expected_size:
                raise RuntimeError(f"size mismatch: expected {expected_size}, observed {size}")
            if observed_md5.lower() != expected_md5.lower():
                raise RuntimeError(
                    f"md5 mismatch: expected {expected_md5}, observed {observed_md5}"
                )
            part.replace(dest)
            return {
                "download_attempts": attempt,
                "download_size": size,
                "download_md5": observed_md5,
                "download_errors": errors,
            }
        except urllib.error.HTTPError as exc:
            errors.append(f"attempt {attempt}: HTTP {exc.code} {exc.reason}")
            if attempt < retries:
                fallback = min(15 * (2 ** (attempt - 1)), 120)
                time.sleep(parse_retry_after(exc.headers.get("Retry-After"), fallback))
        except Exception as exc:
            errors.append(f"attempt {attempt}: {type(exc).__name__}: {exc}")
            if attempt < retries:
                time.sleep(min(15 * (2 ** (attempt - 1)), 120))

    part.unlink(missing_ok=True)
    raise RuntimeError("verified download failed: " + " | ".join(errors))


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

    passing = [r for r in rows if r["joint_support_pass"]]
    namespaces = sorted({str(r["source_namespace"]) for r in passing})
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

    if prereq["status"] != "GLOBI_PARQUET_SCHEMA_ALIAS_PASS":
        raise RuntimeError("GloBI schema prerequisite did not pass")
    if amendment["support_thresholds_changed"] is not False:
        raise RuntimeError("transport amendment changed support thresholds")
    if amendment["source_changed"] is not False or amendment["file_changed"] is not False:
        raise RuntimeError("transport amendment changed source or file")

    url = design["primary_file"]["url"]
    expected_size = int(design["primary_file"]["size"])
    expected_md5 = str(design["primary_file"]["checksum"]).split(":", 1)[1]
    q = design["qualification"]

    remote_error = None
    fallback_error = None
    rows: list[dict] = []
    transport_mode = None
    download_receipt = None

    try:
        rows = query_support(url, amendment, remote=True)
        transport_mode = "remote_range_with_custom_user_agent"
    except Exception as exc:
        remote_error = f"{type(exc).__name__}: {exc}"
        local_file = args.cache_dir / "interactions.parquet"
        try:
            download_receipt = download_verified(
                url, local_file, amendment, expected_size, expected_md5
            )
            rows = query_support(str(local_file), amendment, remote=False)
            transport_mode = "local_verified_sequential_download"
            local_file.unlink(missing_ok=True)
        except Exception as fallback_exc:
            fallback_error = f"{type(fallback_exc).__name__}: {fallback_exc}"
            local_file.unlink(missing_ok=True)

    if transport_mode is None:
        result = {
            "version": "v0.5",
            "status": "HOLD_GLOBI_SUPPORT_TRANSPORT",
            "design": str(DESIGN.relative_to(ROOT)),
            "transport_amendment": str(AMENDMENT.relative_to(ROOT)),
            "outcome_blind": True,
            "scientific_gate_adjudicated": False,
            "support_query_executed": False,
            "interaction_rows_opened_for_support_only": False,
            "raw_edge_identities_persisted": False,
            "biological_turnover_outcomes_opened": False,
            "remote_transport_error": remote_error,
            "fallback_transport_error": fallback_error,
            "gate_pass": None,
            "next_gate": "Retry only the same frozen source/file under the transport amendment; do not interpret this as scientific support failure.",
        }
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    passing, namespaces = write_support_table(rows, args.table_out, q)
    gate = len(namespaces) >= int(q["minimum_independent_source_namespaces"])

    result = {
        "version": "v0.5",
        "status": "GLOBI_JOINT_SUPPORT_PASS" if gate else "HOLD_GLOBI_JOINT_SUPPORT",
        "design": str(DESIGN.relative_to(ROOT)),
        "transport_amendment": str(AMENDMENT.relative_to(ROOT)),
        "outcome_blind": True,
        "scientific_gate_adjudicated": True,
        "transport_mode": transport_mode,
        "remote_transport_error": remote_error,
        "fallback_transport_error": fallback_error,
        "download_receipt": download_receipt,
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
        "support_table_sha256": canonical_sha256(args.table_out),
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
