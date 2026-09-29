#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "data" / "mangal_metadata_preflight_design_v0_1.json"
BASE = "https://mangal.io/api/v2"


def get_json(endpoint: str, params: dict[str, object], retries: int = 4):
    url = BASE + "/" + endpoint + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "turnover-mangal-metadata-preflight/0.1"},
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(
        f"GET failed after {retries} attempts: {url}: "
        f"{type(last).__name__}: {last}"
    )


def paginate(endpoint: str, count: int = 1000, max_pages: int = 20) -> list[dict]:
    rows: list[dict] = []
    for page in range(max_pages):
        payload = get_json(endpoint, {"count": count, "page": page})
        if isinstance(payload, dict) and "data" in payload:
            payload = payload["data"]
        if not isinstance(payload, list):
            raise RuntimeError(
                f"Unexpected response for {endpoint}: {type(payload).__name__}"
            )
        rows.extend(payload)
        if len(payload) < count:
            return rows
    raise RuntimeError(f"{endpoint} pagination exceeded max_pages={max_pages}")


def has_geometry(row: dict) -> bool:
    geom = row.get("geom")
    if not geom:
        return False
    if isinstance(geom, dict):
        coords = geom.get("coordinates")
        return bool(coords)
    return True


def allowed_projection(row: dict, fields: list[str]) -> dict:
    return {field: row.get(field) for field in fields}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    allowed = design["allowed_fields"]
    gate = design["qualification"]

    datasets_raw = paginate("dataset")
    networks_raw = paginate("network")

    datasets = [
        allowed_projection(x, allowed["dataset"])
        for x in datasets_raw
        if x.get("public") is not False
    ]
    networks = [
        allowed_projection(x, allowed["network"])
        for x in networks_raw
        if x.get("public") is not False
    ]

    dataset_name = {
        str(x.get("id")): str(x.get("name") or "")
        for x in datasets
        if x.get("id") is not None
    }

    all_counts: Counter[str] = Counter()
    geo_counts: Counter[str] = Counter()
    geo_dated_counts: Counter[str] = Counter()

    for net in networks:
        did = net.get("dataset_id")
        if did is None:
            continue
        key = str(did)
        all_counts[key] += 1
        if has_geometry(net):
            geo_counts[key] += 1
            if net.get("date"):
                geo_dated_counts[key] += 1

    min_geo = int(gate["minimum_georeferenced_networks_per_dataset"])
    qualifying = []
    for did in sorted(geo_counts, key=lambda x: int(x)):
        if geo_counts[did] < min_geo:
            continue
        qualifying.append(
            {
                "dataset_id": int(did),
                "dataset_name": dataset_name.get(did, ""),
                "public_networks": int(all_counts[did]),
                "georeferenced_networks": int(geo_counts[did]),
                "georeferenced_dated_networks": int(geo_dated_counts[did]),
            }
        )

    minimum_datasets = int(gate["minimum_qualifying_datasets"])
    passed = len(qualifying) >= minimum_datasets
    status = (
        "MANGAL_METADATA_SPATIAL_SUPPORT_PASS"
        if passed
        else "HOLD_MANGAL_METADATA_SPATIAL_SUPPORT"
    )

    result = {
        "version": "v0.1",
        "status": status,
        "design": str(DESIGN.relative_to(ROOT)),
        "source_api": BASE,
        "outcome_blind": True,
        "endpoints_called": ["dataset", "network"],
        "forbidden_endpoints_called": [],
        "node_identity_opened": False,
        "interaction_edges_opened": False,
        "interaction_type_opened": False,
        "trait_values_opened": False,
        "environment_values_opened": False,
        "public_dataset_rows": len(datasets),
        "public_network_rows": len(networks),
        "georeferenced_public_networks": sum(has_geometry(x) for x in networks),
        "dated_public_networks": sum(bool(x.get("date")) for x in networks),
        "georeferenced_dated_public_networks": sum(
            has_geometry(x) and bool(x.get("date")) for x in networks
        ),
        "qualification": gate,
        "n_qualifying_datasets": len(qualifying),
        "qualifying_dataset_metadata": qualifying,
        "gate_pass": passed,
        "next_gate": (
            design["next_gate_if_pass"]
            if passed
            else design["next_gate_if_hold"]
        ),
        "interpretation": (
            "Mangal has enough replicated georeferenced network programmes to justify an identity-only node/taxon support audit. Interaction edges remain unopened."
            if passed
            else
            "Mangal does not meet the frozen programme-level spatial-support gate. Do not inspect nodes or interaction edges to rescue this source."
        ),
    }

    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
