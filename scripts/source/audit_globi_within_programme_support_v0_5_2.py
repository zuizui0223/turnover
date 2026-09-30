#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "data" / "globi_source_semantic_amendment_v0_5_2.json"
V04 = ROOT / "results" / "globi_joint_support_v0_4" / "result_summary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local-tsv-gz", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--table-out", type=Path, required=True)
    a = ap.parse_args()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.table_out.parent.mkdir(parents=True, exist_ok=True)

    d = json.loads(DESIGN.read_text())
    prior = json.loads(V04.read_text())
    if prior["status"] != "GLOBI_JOINT_SUPPORT_PASS":
        raise RuntimeError("v0.4 prerequisite did not pass")
    if prior["biological_turnover_outcomes_opened"] is not False:
        raise RuntimeError("v0.4 unexpectedly opened biological outcomes")
    if not a.local_tsv_gz.exists():
        raise RuntimeError(f"missing local TSV: {a.local_tsv_gz}")

    # Header-only verification before the programme-support query.
    import gzip
    with gzip.open(a.local_tsv_gz, "rt", encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh, delimiter="\t"))
    required = [
        "sourceNamespace", "interactionTypeId", "interactionTypeName",
        "sourceTaxonSpeciesName", "targetTaxonSpeciesName",
        "decimalLatitude", "decimalLongitude", "eventDate",
        "referenceDoi", "referenceCitation", "sourceDOI", "sourceCitation"
    ]
    missing = [x for x in required if x not in header]
    if missing:
        out = {
            "version": "v0.5.2",
            "status": "HOLD_GLOBI_PROGRAMME_HEADER_MISSING",
            "outcome_blind": True,
            "biological_turnover_outcomes_opened": False,
            "missing_fields": missing,
            "gate_pass": False,
            "next_gate": d["next_if_below_12"],
        }
        a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0

    candidates = prior["qualifying_source_namespaces"]
    con = duckdb.connect(database=":memory:")
    con.execute("CREATE TEMP TABLE candidates(ns VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES (?)", [(x,) for x in candidates])

    source = "read_csv_auto(?, delim='\t', header=true, all_varchar=true, compression='gzip')"
    sql = f"""
    WITH raw AS (
      SELECT
        trim(CAST(g.sourceNamespace AS VARCHAR)) AS ns,
        trim(CAST(g.interactionTypeId AS VARCHAR)) AS itid,
        trim(CAST(g.interactionTypeName AS VARCHAR)) AS itname,
        trim(CAST(g.sourceTaxonSpeciesName AS VARCHAR)) AS focal,
        trim(CAST(g.targetTaxonSpeciesName AS VARCHAR)) AS partner,
        try_cast(g.decimalLatitude AS DOUBLE) AS lat,
        try_cast(g.decimalLongitude AS DOUBLE) AS lon,
        try_cast(regexp_extract(CAST(g.eventDate AS VARCHAR), '^([0-9]{{4}})', 1) AS INTEGER) AS yr,
        trim(CAST(g.referenceDoi AS VARCHAR)) AS refdoi,
        trim(CAST(g.referenceCitation AS VARCHAR)) AS refcite,
        trim(CAST(g.sourceDOI AS VARCHAR)) AS srcdoi,
        trim(CAST(g.sourceCitation AS VARCHAR)) AS srccite
      FROM {source} g
      INNER JOIN candidates c
        ON trim(CAST(g.sourceNamespace AS VARCHAR)) = c.ns
      WHERE g.interactionTypeId IS NOT NULL
        AND g.sourceTaxonSpeciesName IS NOT NULL
        AND g.targetTaxonSpeciesName IS NOT NULL
        AND trim(CAST(g.interactionTypeId AS VARCHAR)) <> ''
        AND trim(CAST(g.sourceTaxonSpeciesName AS VARCHAR)) <> ''
        AND trim(CAST(g.targetTaxonSpeciesName AS VARCHAR)) <> ''
    ),
    keyed AS (
      SELECT *,
        CASE
          WHEN refdoi IS NOT NULL AND refdoi <> '' THEN
            'doi:' || regexp_replace(
              regexp_replace(lower(refdoi), '^https?://(dx\\.)?doi\\.org/', ''),
              '^doi:[ ]*', ''
            )
          WHEN refcite IS NOT NULL AND refcite <> '' THEN
            'citation:' || regexp_replace(refcite, '[[:space:]]+', ' ', 'g')
          WHEN srcdoi IS NOT NULL AND srcdoi <> '' THEN
            'doi:' || regexp_replace(
              regexp_replace(lower(srcdoi), '^https?://(dx\\.)?doi\\.org/', ''),
              '^doi:[ ]*', ''
            )
          WHEN srccite IS NOT NULL AND srccite <> '' THEN
            'sourcecitation:' || regexp_replace(srccite, '[[:space:]]+', ' ', 'g')
          ELSE NULL
        END AS programme_key
      FROM raw
    ),
    base AS (
      SELECT * FROM keyed WHERE programme_key IS NOT NULL
    ),
    names AS (
      SELECT ns, itid, programme_key,
        min(itname) FILTER (WHERE itname IS NOT NULL AND itname <> '') AS interaction_type_name,
        count(*) AS species_rank_edge_rows
      FROM base
      GROUP BY ns, itid, programme_key
    ),
    fp AS (
      SELECT DISTINCT ns, itid, programme_key, focal, partner
      FROM base
    ),
    fpn AS (
      SELECT ns, itid, programme_key, focal, count(*) AS n_partners
      FROM fp
      GROUP BY ns, itid, programme_key, focal
    ),
    temporal AS (
      SELECT ns, itid, programme_key,
        count(*) AS focal_taxa,
        count(*) FILTER (WHERE n_partners >= 3) AS focal_taxa_3plus_partners
      FROM fpn
      GROUP BY ns, itid, programme_key
    ),
    geo AS (
      SELECT DISTINCT ns, itid, programme_key, focal, lat, lon, yr
      FROM base
      WHERE lat BETWEEN -90 AND 90
        AND lon BETWEEN -180 AND 180
        AND yr BETWEEN 1000 AND 2026
    ),
    sites AS (
      SELECT DISTINCT ns, itid, programme_key, lat, lon, yr
      FROM geo
    ),
    spatial AS (
      SELECT ns, itid, programme_key, count(*) AS site_year_strata
      FROM sites
      GROUP BY ns, itid, programme_key
    ),
    fsites AS (
      SELECT ns, itid, programme_key, focal, count(*) AS n_site_year_strata
      FROM geo
      GROUP BY ns, itid, programme_key, focal
    ),
    repeated AS (
      SELECT ns, itid, programme_key,
        count(*) FILTER (WHERE n_site_year_strata >= 2) AS repeated_focal_taxa
      FROM fsites
      GROUP BY ns, itid, programme_key
    )
    SELECT
      n.ns AS source_namespace,
      n.itid AS interaction_type_id,
      n.interaction_type_name,
      n.programme_key,
      n.species_rank_edge_rows,
      coalesce(t.focal_taxa, 0) AS focal_taxa,
      coalesce(t.focal_taxa_3plus_partners, 0) AS focal_taxa_3plus_partners,
      coalesce(s.site_year_strata, 0) AS site_year_strata,
      coalesce(r.repeated_focal_taxa, 0) AS repeated_focal_taxa
    FROM names n
    LEFT JOIN temporal t USING (ns, itid, programme_key)
    LEFT JOIN spatial s USING (ns, itid, programme_key)
    LEFT JOIN repeated r USING (ns, itid, programme_key)
    ORDER BY n.ns, n.itid, n.programme_key
    """

    cur = con.execute(sql, [str(a.local_tsv_gz)])
    cols = [x[0] for x in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    con.close()

    q = d["within_programme_gate"]
    for row in rows:
        row["within_programme_pass"] = (
            int(row["focal_taxa_3plus_partners"]) >= int(q["temporal_min_focal_taxa_with_3plus_partners"])
            and int(row["site_year_strata"]) >= int(q["spatial_min_site_year_strata"])
            and int(row["repeated_focal_taxa"]) >= int(q["spatial_min_repeated_focal_taxa"])
        )

    fields = [
        "source_namespace", "interaction_type_id", "interaction_type_name",
        "programme_key", "species_rank_edge_rows", "focal_taxa",
        "focal_taxa_3plus_partners", "site_year_strata",
        "repeated_focal_taxa", "within_programme_pass"
    ]
    with a.table_out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    passing = [x for x in rows if x["within_programme_pass"]]
    passing_ns = sorted({x["source_namespace"] for x in passing})
    n = len(passing_ns)
    possible = n >= 12
    status = "GLOBI_WITHIN_PROGRAMME_SUPPORT_PASS" if possible else "HOLD_GLOBI_WITHIN_PROGRAMME_SUPPORT"

    out = {
        "version": "v0.5.2",
        "status": status,
        "design": str(DESIGN.relative_to(ROOT)),
        "outcome_blind": True,
        "biological_turnover_outcomes_opened": False,
        "v0_4_candidate_namespaces": len(candidates),
        "n_programme_blocks_audited": len(rows),
        "n_programme_blocks_pass": len(passing),
        "n_namespaces_with_programme_pass_before_mirror_dedup": n,
        "namespaces_with_programme_pass_before_mirror_dedup": passing_ns,
        "minimum_required": 12,
        "pre_semantic_gate_possible": possible,
        "support_table": str(a.table_out),
        "support_table_sha256": sha256(a.table_out),
        "gate_pass": possible,
        "next_gate": d["next_if_at_least_12"] if possible else d["next_if_below_12"],
        "interpretation": (
            "At least 12 v0.4 namespaces contain a provenance-resolved programme that independently satisfies the same structural thresholds. Proceed to source-method/effort adjudication; mirror deduplication may still reduce the independent count."
            if possible else
            "Fewer than 12 v0.4 namespaces contain any provenance-resolved programme that independently satisfies the frozen structural thresholds. The aggregate GloBI PASS was created partly by pooling unrelated programmes; stop the primary joint interaction arm before opening turnover outcomes."
        )
    }
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
