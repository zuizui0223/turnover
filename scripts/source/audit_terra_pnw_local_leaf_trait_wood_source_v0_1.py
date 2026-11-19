#!/usr/bin/env python3
"""ORNL TERRA-PNW exact-source-only eligibility: no biological effect may be fitted."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import re
import statistics
import urllib.error
import urllib.request
from pathlib import Path

DOI = "10.3334/ORNLDAAC/1292"
# Legacy *official ORNL* data distribution pattern, probed once without credentials.
# If redirected to Earthdata auth / controlled archive, fail closed.
ROOT = "https://daac.ornl.gov/daacdata/nacp/NACP_TERRA-PNW/data/"
FILENAMES = {
    "leaf": "NACP_TERRA_PNW_leaf_trait_dataset.csv",
    "stand": "NACP_TERRA_PNW_forest_biomass_productivity_dataset.csv",
}
MAX_BYTES = 8_000_000
REQUIRED_LEAF = {"PROJECT", "YEAR", "PLOT_ID", "GENUS", "SPECIES", "SLA_PSA", "LEAF_NITROGEN"}
REQUIRED_STAND = {"PROJECT", "YEAR", "PLOT_ID", "CLUSTER", "ECOREGION",
                  "AG_BIOMASS_TREE_WOOD_AS_CARBON"}
GROUP_MIN = 5
PLOT_MIN = 80
SITES_PER_GROUP = 8
SPECIES_MIN = 30
COVER_MIN = 0.80
YEAR_DIFF_MAX = 2


def canon(column):
    return re.sub(r"[^A-Z0-9]+", "_", column.strip().upper()).strip("_")


def source_fetch(kind):
    url = ROOT + FILENAMES[kind]
    req = urllib.request.Request(url, headers={
        "User-Agent": "turnover-terra-pnw-original-source-preflight/0.1",
        "Accept": "text/csv,application/octet-stream",
    })
    with urllib.request.urlopen(req, timeout=45) as resp:
        if resp.status != 200:
            raise RuntimeError("ANONYMOUS_SOURCE_NON_200")
        final_host = urllib.request.urlparse(resp.url).hostname or ""
        if ("urs.earthdata.nasa.gov" in final_host or "login" in resp.url.lower()):
            raise RuntimeError("EARTHDATA_LOGIN_REQUIRED")
        payload = resp.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise RuntimeError("SOURCE_FILE_EXCEEDS_FIXED_BYTE_CAP")
    if not payload.lstrip(b"\xef\xbb\xbf").startswith(b"PROJECT,"):
        raise RuntimeError("DOWNLOADED_BYTES_NOT_ORIGINAL_CSV")
    return payload


def source_table(payload, required):
    # First CSV row carries field names, second may carry author unit descriptions.
    text = payload.decode("utf-8-sig")
    rd = csv.DictReader(io.StringIO(text))
    if not rd.fieldnames:
        raise RuntimeError("SOURCE_MISSING_CSV_HEADER")
    keys = [canon(x) for x in rd.fieldnames]
    if len(keys) != len(set(keys)) or not required.issubset(set(keys)):
        raise RuntimeError("SOURCE_FIELDS_MISMATCH")
    out = []
    n_units = 0
    for source_row in rd:
        row = {canon(k): (v or "").strip() for k, v in source_row.items() if k}
        year = integer(row.get("YEAR"))
        if year is None:
            n_units += 1
            continue
        if year < 1999 or year > 2014:
            raise RuntimeError("SOURCE_YEAR_OUT_OF_PUBLISHED_RANGE")
        out.append(row)
    return out, n_units, keys


def integer(v):
    if v is None or str(v).strip() in ("", "-9999", "NA"):
        return None
    try:
        t = float(str(v).strip())
        return int(t) if math.isfinite(t) and t == int(t) else None
    except (ValueError, OverflowError):
        return None


def positive(v):
    if v is None or str(v).strip() in ("", "-9999", "NA"):
        return None
    try:
        n = float(v)
        return n if math.isfinite(n) and n > 0 else None
    except ValueError:
        return None


def source_identity(row):
    p = row.get("PROJECT", "")
    k = row.get("PLOT_ID", "")
    if not p or not k or k in ("-9999", "NA"):
        return None
    return (p, k)


def taxon(row):
    g = row.get("GENUS", "").strip()
    s = row.get("SPECIES", "").strip()
    if not re.fullmatch(r"[A-Za-z]{3,}", g) or not re.fullmatch(r"[A-Za-z]{3,}", s):
        return None
    return (g.casefold(), s.casefold())


def six_code(t):
    return (t[0][:3] + t[1][:3]).upper()


def inspect(leaf, stand):
    # Original source only, no trait index, no biomass model.
    scoped_leaf = collections.defaultdict(list)
    unique_taxa = set()
    code_map = collections.defaultdict(set)
    for r in leaf:
        key, t = source_identity(r), taxon(r)
        if key is None or t is None:
            continue
        v1, v2 = positive(r.get("SLA_PSA")), positive(r.get("LEAF_NITROGEN"))
        if v1 is None or v2 is None:
            continue
        unique_taxa.add(t)
        code_map[six_code(t)].add(t)
        scoped_leaf[(key, t)].append(integer(r.get("YEAR")))
    collisions = [v for v in code_map.values() if len(v) != 1]
    supported = collections.defaultdict(list)
    year_gaps = collections.Counter()
    stand_keys = collections.Counter()
    source_projects = collections.Counter()
    n_nonpositive_mass = 0
    n_dates_out = 0
    n_subtwo = 0
    n_lowcover = 0
    n_fraction_missing = 0
    for r in stand:
        key = source_identity(r)
        year = integer(r.get("YEAR"))
        if key is None or year is None:
            continue
        stand_keys[(key, year)] += 1
        if positive(r.get("AG_BIOMASS_TREE_WOOD_AS_CARBON")) is None:
            n_nonpositive_mass += 1
            continue
        pairs = []
        for i in range(1, 5):
            abbrev = (r.get(f"SPP_O{i}_ABBREV", "") or "").upper().strip()
            frac = positive(r.get(f"SPP_O{i}_BASAL_AREA_FRACTION"))
            if not abbrev or abbrev in ("NA", "-9999") or frac is None:
                continue
            if not re.fullmatch(r"[A-Z]{6}", abbrev):
                n_fraction_missing += 1
                continue
            t = next(iter(code_map[abbrev])) if len(code_map[abbrev]) == 1 else None
            if t is None:
                continue
            source_dates = [x for x in scoped_leaf.get((key, t), []) if x is not None
                            and abs(x - year) <= YEAR_DIFF_MAX]
            if not source_dates:
                continue
            gap = min(abs(x - year) for x in source_dates)
            pairs.append((t, frac, gap))
        all_positive_fraction = sum(
            positive(r.get(f"SPP_O{i}_BASAL_AREA_FRACTION")) or 0 for i in range(1, 5)
        )
        matched_fraction = sum(frac for _, frac, _ in pairs)
        coverage = matched_fraction / all_positive_fraction if all_positive_fraction > 0 else 0
        n_direct_species = len({t for t, _, _ in pairs})
        if n_direct_species < 2:
            n_subtwo += 1
        if coverage < COVER_MIN:
            n_lowcover += 1
        if n_direct_species >= 2 and coverage >= COVER_MIN:
            supported[key].append((year, r.get("PROJECT", ""), list(pairs)))
            for _, _, gap in pairs:
                year_gaps[gap] += 1
        else:
            n_dates_out += 1
    repeated_stand_plotyears = sum(max(0, x - 1) for x in stand_keys.values())
    if repeated_stand_plotyears:
        status = "DUPLICATE_PROJECT_PLOT_YEAR_HOLD"
    elif collisions:
        status = "ORIGINAL_TAXON_ABBREVIATION_COLLISION_HOLD"
    else:
        # Consecutive years from the same original field plot count once.
        for key, rows in supported.items():
            source_projects[key[0]] += 1
        eligible_taxa = set()
        for rows in supported.values():
            chosen = sorted(rows, key=lambda x: x[0])[0]
            eligible_taxa.update(t for t, _, _ in chosen[2])
        n_projects_ok = sum(n >= SITES_PER_GROUP for n in source_projects.values())
        status = ("SOURCE_GRANULARITY_PROVISIONAL_PASS_NEEDS_RESAMPLE_AUDIT"
                  if len(supported) >= PLOT_MIN and len(eligible_taxa) >= SPECIES_MIN
                  and n_projects_ok >= GROUP_MIN
                  else "SOURCE_SUPPORT_HOLD")
    return {
        "status": status,
        "n_original_leaf_individual_rows": len(leaf),
        "n_original_stand_rows": len(stand),
        "n_source_qualified_unique_project_plot_keys": len(supported),
        "n_qualified_project_groups": sum(n >= SITES_PER_GROUP for n in source_projects.values()),
        "n_original_project_groups_total": len({r.get("PROJECT") for r in stand}),
        "n_original_unique_local_dual_trait_taxa": len(unique_taxa),
        "n_unique_six_character_taxon_code_collisions": len(collisions),
        "n_duplicate_project_plot_year_source_keys": repeated_stand_plotyears,
        "n_original_nonpositive_or_missing_wood_stocks": n_nonpositive_mass,
        "n_original_stand_rows_with_below_two_source_measured_species": n_subtwo,
        "n_original_stand_rows_with_below_80pct_source_measured_trait_cover": n_lowcover,
        "n_unusable_abbreviated_basal_area_source_entries": n_fraction_missing,
        "year_gap_frequency_for_paired_species": dict(sorted(year_gaps.items())),
        "qualified_project_plot_counts_by_project_anonymized": sorted(source_projects.values()),
        "repeated_PLOT_ID_ALT_spatial_identity_audit": "NOT_YET_VERIFIED",
        "source_only": True,
        "biological_effect_fitted": False,
    }


def self_test():
    assert canon("SPP_O1_ ABBREV") == "SPP_O1_ABBREV"
    assert canon("AG_BIOMASS_TREE_WOOD_AS_CARBON") == "AG_BIOMASS_TREE_WOOD_AS_CARBON"
    assert positive("-9999") is None and positive("0") is None
    assert taxon({"GENUS": "Pseudotsuga", "SPECIES": "menziesii"}) == (
        "pseudotsuga", "menziesii"
    )
    assert six_code(("pseudotsuga", "menziesii")) == "PSEMEN"
    assert source_identity({"PROJECT": "A", "PLOT_ID": "1"}) == ("A", "1")
    # This fixture has only one plant and must never admit source FD.
    leaf = [{"PROJECT": "A", "PLOT_ID": "1", "YEAR": "2000",
             "GENUS": "Pseudotsuga", "SPECIES": "menziesii",
             "SLA_PSA": "150", "LEAF_NITROGEN": "1.2"}]
    stand = [{"PROJECT": "A", "PLOT_ID": "1", "YEAR": "2000",
              "AG_BIOMASS_TREE_WOOD_AS_CARBON": "2000",
              "SPP_O1_ABBREV": "PSEMEN", "SPP_O1_BASAL_AREA_FRACTION": "100"}]
    d = inspect(leaf, stand)
    assert d["status"] == "SOURCE_SUPPORT_HOLD"
    assert d["n_source_qualified_unique_project_plot_keys"] == 0
    print(json.dumps({"status": "TERRA_PNW_SOURCE_FIXTURE_PASS", "checks": 8}))


def main(out):
    summary = {
        "dataset_doi": DOI,
        "official_archive_catalogue": "https://doi.org/" + DOI,
        "original_source_access": "UNVERIFIED",
        "status": "SOURCE_ACCESS_HOLD",
        "reported_paper_descriptors_not_raw_source_counts": {
            "leaf_individual_rows": 1296, "stand_records": 266,
            "tree_shrub_taxa": 35, "project_programmes": 6,
        },
        "frozen_minimums": {
            "plot_keys": PLOT_MIN, "independent_project_groups": GROUP_MIN,
            "plots_per_project": SITES_PER_GROUP, "original_species": SPECIES_MIN,
            "local_dual_trait_cover": COVER_MIN, "trait_stock_year_gap": YEAR_DIFF_MAX,
        },
        "source_wood_response": "AG_BIOMASS_TREE_WOOD_AS_CARBON [g C m^-2]",
        "no_phylogenetic_family_K_estimated": True,
        "no_original_rows_republished": True,
        "no_biological_effect_estimated": True,
    }
    for kind in ("leaf", "stand"):
        try:
            contents = source_fetch(kind)
            summary[f"{kind}_source_sha256"] = hashlib.sha256(contents).hexdigest()
            if kind == "leaf":
                leaf, units, header = source_table(contents, REQUIRED_LEAF)
            else:
                stand, units, header = source_table(contents, REQUIRED_STAND)
            summary[f"{kind}_original_rows"] = len(leaf if kind == "leaf" else stand)
            summary[f"{kind}_column_count"] = len(header)
            summary[f"{kind}_noncalendar_source_unit_or_invalid_rows"] = units
            summary[f"{kind}_source_anonymous_access"] = "BYTES_HEADER_AND_SCHEMA_PASS"
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                RuntimeError, ValueError, UnicodeError) as exc:
            summary["status"] = "SOURCE_ACCESS_OR_SCHEMA_HOLD"
            summary[f"{kind}_audit_exception_type"] = type(exc).__name__
            if isinstance(exc, urllib.error.HTTPError):
                summary[f"{kind}_anonymous_http_code"] = exc.code
            elif isinstance(exc, RuntimeError):
                summary[f"{kind}_source_validation_gate"] = str(exc)[:100]
            break
    else:
        summary["original_source_access"] = "BOTH_CSV_SOURCE_BYTES_AND_SCHEMA_VERIFIED"
        summary.update(inspect(leaf, stand))
    assert summary["no_biological_effect_estimated"]
    assert summary["status"].endswith(("HOLD", "RESAMPLE_AUDIT"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("TERRA_PNW_ORIGINAL_SOURCE_ONLY", json.dumps({
        "status": summary["status"],
        "original_source_access": summary["original_source_access"],
        "leaf_http": summary.get("leaf_anonymous_http_code"),
        "stand_http": summary.get("stand_anonymous_http_code"),
        "n_matched_plot_keys": summary.get("n_source_qualified_unique_project_plot_keys"),
        "biological_effect_fitted": False,
    }, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.out:
        main(a.out)
    else:
        p.error("Specify --self-test or --out")
