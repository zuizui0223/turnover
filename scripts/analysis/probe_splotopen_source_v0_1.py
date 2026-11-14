#!/usr/bin/env python3
"""Audit a pinned public sPlotOpen ZIP without recording any species identities.

Use on a fresh official public archive (not a Git-LFS pointer).
This is an input/schema audit only; no PD, FD or ecosystem output is fitted.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import tempfile
import zipfile
from pathlib import Path

NAME_MAP = {
    "composition": re.compile(r"(?:^|/)sPlotOpen_DT(?:\([^)]*\))?\.txt$", re.I),
    "plot_metadata": re.compile(r"(?:^|/)sPlotOpen_header(?:\([^)]*\))?\.txt$", re.I),
    "derived_trait_cwm": re.compile(r"(?:^|/)sPlotOpen_CWM_CWV(?:\([^)]*\))?\.txt$", re.I),
}
EXPECTED_UNIQUE_PLOTS = 95104

def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def inspect(archive):
    archive = Path(archive)
    if not zipfile.is_zipfile(archive):
        return {"status": "HOLD_INVALID_OR_NON_ZIP_INPUT",
                "archive_bytes": archive.stat().st_size if archive.exists() else 0}
    with zipfile.ZipFile(archive) as z:
        manifest = {}
        for role, pattern in NAME_MAP.items():
            matches = [m for m in z.infolist() if not m.is_dir() and pattern.search(m.filename)]
            if len(matches) != 1:
                manifest[role] = {"status": "HOLD_EXPECTED_EXACTLY_ONE_MEMBER",
                                  "n_matches": len(matches)}
                continue
            member = matches[0]
            with z.open(member) as raw, io.TextIOWrapper(
                raw, encoding="utf-8-sig", errors="replace", newline=""
            ) as handle:
                reader = csv.reader(handle, delimiter="\t")
                header = next(reader, [])
                rows = 0
                plot_ids = set()
                plot_id_idx = header.index("PlotObservationID") if "PlotObservationID" in header else -1
                for row in reader:
                    if not row or all(not v.strip() for v in row):
                        continue
                    rows += 1
                    if plot_id_idx >= 0 and len(row) > plot_id_idx and row[plot_id_idx]:
                        plot_ids.add(row[plot_id_idx])
            manifest[role] = {
                "status": "MEMBER_READ_PASS",
                "member_name": member.filename,
                "uncompressed_bytes": member.file_size,
                "n_rows": rows,
                "n_columns": len(header),
                "column_names": header,
                "unique_PlotObservationID_if_present": len(plot_ids) if plot_id_idx >= 0 else None,
            }
        accepted = all(
            item.get("status") == "MEMBER_READ_PASS" for item in manifest.values()
        )
        header = manifest.get("plot_metadata", {})
        observed_unique = header.get("unique_PlotObservationID_if_present")
        result = {
            "status": (
                "SCHEMA_SOURCE_PASS_STILL_NO_TRAIT_OR_PHYLOGENY"
                if accepted and observed_unique == EXPECTED_UNIQUE_PLOTS
                else "HOLD_SOURCE_SCHEMA_OR_IDENTITY"
            ),
            "source": "sPlotOpen public ZIP, pin the original URL and version outside this script",
            "archive_bytes": archive.stat().st_size,
            "archive_sha256": _hash(archive),
            "required_reference_unique_plots": EXPECTED_UNIQUE_PLOTS,
            "members": manifest,
            "warning": (
                "Published CWM/CWV uses gap-filled TRY and is not independent "
                "measured multivariate FD. No raw species/plot rows or effect estimates exported."
            ),
        }
        return result

def self_test():
    with tempfile.TemporaryDirectory() as root:
        p = Path(root) / "test.zip"
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("d/sPlotOpen_DT(1).txt",
                       "PlotObservationID\tTaxon\np1\tAcacia alpha\np1\tAcacia beta\n")
            z.writestr("d/sPlotOpen_header.txt",
                       "PlotObservationID\tDataset\np1\td1\n")
            z.writestr("d/sPlotOpen_CWM_CWV(1).txt",
                       "PlotObservationID\tCWM\np1\t2.0\n")
        result = inspect(p)
        assert result["members"]["composition"]["n_rows"] == 2, result
        assert result["members"]["plot_metadata"]["unique_PlotObservationID_if_present"] == 1
        assert result["status"] == "HOLD_SOURCE_SCHEMA_OR_IDENTITY", result
    return {"status": "SELF_TEST_PASS", "checks": 3}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))
        return
    if not args.archive or not args.out:
        parser.error("--archive and --out required")
    result = inspect(args.archive)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["status"].startswith("SCHEMA_SOURCE_PASS"):
        raise SystemExit(2)

if __name__ == "__main__":
    main()
