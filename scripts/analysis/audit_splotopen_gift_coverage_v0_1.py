#!/usr/bin/env python3
"""Source-only GIFT 3.1 x sPlotOpen exact accepted-name / trait coverage audit.

Read public raw sPlotOpen composition (not gap-filled CWM/CWV); query GIFT 3.1
accepted species and public woodiness, growth form and height. Emit aggregate
coverage only. Does NOT assess FD, biomass, phylogenetic signal or independence.
"""
import argparse
import collections
import csv
import io
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

API = "https://gift.uni-goettingen.de/api/extended/index3.1.php"
BATCH = 10000
TRAITS = {"woodiness": "1.1.1", "growth_form": "1.2.1",
          "plant_height_max": "1.6.2"}

def norm(s):
    return " ".join(str(s or "").replace("_", " ").casefold().strip().split())

def binomial(s):
    val = norm(s)
    return val if re.fullmatch(r"[a-z-]+ [a-z-]+", val) else None

def safe_num(x):
    try:
        y = float(x)
        return y if math.isfinite(y) else None
    except (TypeError, ValueError):
        return None

def gift_request(query, **opts):
    url = API + "?" + urllib.parse.urlencode({"query": query, **opts})
    problem = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "turnover-community-PD-FD-source-gate/0.1",
                "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=110) as response:
                body = json.load(response)
            if not isinstance(body, list):
                raise ValueError("Unexpected GIFT API response root")
            return body
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            problem = str(exc)
            time.sleep(min(2 ** attempt, 5))
    raise RuntimeError(f"GIFT 3.1 API unavailable: {problem}")

def paged(query, max_rows=600000, **opts):
    offset = 0
    first = None
    for _ in range(100):
        rows = gift_request(query, startat=offset, limit=BATCH, **opts)
        if len(rows) > BATCH:
            raise ValueError("GIFT API returned more than pinned page size")
        if rows:
            signature = json.dumps(rows[0], sort_keys=True)
            if signature == first:
                raise ValueError("GIFT API repeated a paginated first row")
            first = signature
        yield from rows
        if len(rows) < BATCH:
            return
        offset += len(rows)
        if offset >= max_rows:
            raise ValueError("GIFT pagination exceeded frozen maximum")
        time.sleep(0.05)
    raise ValueError("GIFT pagination exceeded pages")

def gift_lookup():
    ids = collections.defaultdict(set)
    count = 0
    for row in paged("species"):
        name, work_id = binomial(row.get("work_species")), str(row.get("work_ID") or "")
        if name and work_id:
            ids[name].add(work_id)
        count += 1
    mapping = {name: next(iter(values)) for name, values in ids.items()
               if len(values) == 1}
    if count < 100000:
        raise ValueError("GIFT species paging unexpectedly short")
    values = {}
    trait_records = {}
    for trait, id_ in TRAITS.items():
        by_id = collections.defaultdict(set)
        nrows = 0
        for row in paged("traits", max_rows=500000,
                         traitid=id_, biasref=0, biasderiv=0):
            work_id = str(row.get("work_ID") or "")
            val = str(row.get("trait_value") or "").strip()
            if work_id and val:
                by_id[work_id].add(val)
            nrows += 1
        values[trait] = set(k for k, v in by_id.items() if len(v) == 1)
        trait_records[trait] = {
            "source_trait_id": id_, "records": nrows,
            "unique_unambiguous_work_IDs": len(values[trait]),
            "conflicting_work_IDs_excluded": sum(len(v) > 1 for v in by_id.values()),
        }
    return mapping, values, {"gift_species_rows": count,
                             "distinct_accepted_names": len(ids),
                             "ambiguous_accepted_names_excluded": sum(len(s)>1 for s in ids.values()),
                             "traits": trait_records}

def open_dt(zipfile_obj):
    matches = [name for name in zipfile_obj.namelist()
               if re.search(r"(?:^|/)sPlotOpen_DT(?:\([^)]*\))?\.txt$", name, re.I)]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one sPlotOpen DT member, got {len(matches)}")
    handle = io.TextIOWrapper(zipfile_obj.open(matches[0]),
                              encoding="utf-8-sig", errors="replace", newline="")
    reader = csv.DictReader(handle, delimiter="\t")
    required = {"PlotObservationID", "Species", "Relative_cover"}
    if not required.issubset(set(reader.fieldnames or [])):
        handle.close()
        raise ValueError("Missing native sPlotOpen composition fields")
    return handle, reader

def audit(archive, mapping, trait_ids, gift_info):
    unique = set()
    seen_plots = set()
    all_cover = collections.defaultdict(float)
    exact_cover = collections.defaultdict(float)
    trait_cover = {t: collections.defaultdict(float) for t in TRAITS}
    genus_species = collections.defaultdict(set)
    rows = numeric_cover = nonnumeric_cover = matched_rows = 0

    with zipfile.ZipFile(archive) as z:
        handle, reader = open_dt(z)
        try:
            for rec in reader:
                rows += 1
                plot = str(rec.get("PlotObservationID") or "").strip()
                species = binomial(rec.get("Species"))
                weight = safe_num(rec.get("Relative_cover"))
                if not plot:
                    continue
                seen_plots.add(plot)
                if species is None:
                    continue
                unique.add(species)
                genus_species[(plot, species.split()[0])].add(species)
                if weight is None or weight <= 0:
                    nonnumeric_cover += 1
                    continue
                numeric_cover += 1
                all_cover[plot] += weight
                work_id = mapping.get(species)
                if work_id is None:
                    continue
                matched_rows += 1
                exact_cover[plot] += weight
                for t, ids in trait_ids.items():
                    if work_id in ids:
                        trait_cover[t][plot] += weight
        finally:
            handle.close()
    plot_ids = set(seen_plots)
    valid_plots = [p for p in plot_ids if all_cover.get(p, 0) > 0]
    def cover_report(covered):
        fractions = [covered.get(p, 0) / all_cover[p] for p in valid_plots]
        return {
            "n_plots_with_valid_cover": len(fractions),
            "n_plots_cover_fraction_at_least_0_8": sum(v >= 0.8 for v in fractions),
            "mean_fraction": sum(fractions) / len(fractions) if fractions else None,
        }
    triple = {p for (p, genus), species in genus_species.items() if len(species) >= 3}
    known_unique = set(unique).intersection(mapping)
    return {
        "status": "SOURCE_SPECIES_TRAIT_COVERAGE_ONLY_NO_FD_BIOMASS",
        "source_mirror": "ezequielscott/sPlotOpen commit 1bfcad669ae1a7e6f0a419159dd3051e83bdd26b",
        "GIFT_version": "3.1",
        "GIFT_source": gift_info,
        "composition_rows": rows,
        "unique_plot_ids_in_composition": len(plot_ids),
        "unique_exact_binomial_species_in_composition": len(unique),
        "unique_exact_GIFT_accepted_name_matches": len(known_unique),
        "fraction_unique_species_exact_GIFT_match": len(known_unique)/len(unique) if unique else None,
        "composition_rows_with_positive_numeric_relative_cover": numeric_cover,
        "composition_rows_with_missing_or_invalid_relative_cover": nonnumeric_cover,
        "composition_rows_with_positive_cover_and_exact_GIFT_match": matched_rows,
        "plots_with_three_or_more_distinct_same_genus_species": len(triple),
        "matched_species_cover": cover_report(exact_cover),
        "trait_cover": {t: cover_report(covered) for t, covered in trait_cover.items()},
        "hard_nonclaims": [
            "Within-genus 3-species plots are only a lower-bound geometry for within-family support",
            "Source joins do not prove biological independence of GIFT and TRY/AusTraits/BIEN records",
            "This does not calculate phylogenetic diversity, functional diversity, biomass or an ecological coefficient",
            "Missing family mapping, phylogeny and trait-source audits preclude primary PD-FD inference"
        ],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    mapping, trait_ids, gift_info = gift_lookup()
    report = audit(args.archive, mapping, trait_ids, gift_info)
    if report["composition_rows"] != 1943306 or report["unique_plot_ids_in_composition"] != 95104:
        raise ValueError("Pinned public mirror plot or species row identity changed")
    dst = Path(args.out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True, ensure_ascii=False))

if __name__ == "__main__":
    main()
