#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"austraits_metadata_preflight_design_v0_1.json"

def digest(path:Path,algo:str)->str:
    h=hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--parquet",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    d=json.loads(DESIGN.read_text())

    size=a.parquet.stat().st_size
    sha=digest(a.parquet,"sha256")
    md5=digest(a.parquet,"md5")
    integrity=(
        size==int(d["primary_file"]["size_bytes"])
        and sha==d["primary_file"]["github_release_sha256"]
        and md5==d["primary_file"]["zenodo_md5"]
    )

    con=duckdb.connect(database=":memory:")
    # DESCRIBE resolves Parquet schema; no row-returning or row-count query is executed.
    cur=con.execute("DESCRIBE SELECT * FROM read_parquet(?)",[str(a.parquet)])
    schema=[{"column_name":str(r[0]),"column_type":str(r[1])} for r in cur.fetchall()]
    con.close()

    by_lower={x["column_name"].lower():x["column_name"] for x in schema}
    def resolve(groups):
        out={}
        for group,aliases in groups.items():
            hits=[]
            for alias in aliases:
                x=by_lower.get(alias.lower())
                if x is not None and x not in hits:
                    hits.append(x)
            out[group]=hits
        return out

    required=resolve(d["required_semantic_groups"])
    optional=resolve(d["optional_semantic_groups"])
    missing=[g for g,h in required.items() if not h]
    gate=integrity and not missing
    result={
        "version":"v0.1",
        "status":"AUSTRAITS_SCHEMA_PREFLIGHT_PASS" if gate else "HOLD_AUSTRAITS_SCHEMA_PREFLIGHT",
        "design":str(DESIGN.relative_to(ROOT)),
        "outcome_blind":True,
        "raw_trait_values_opened":False,
        "biological_turnover_outcomes_opened":False,
        "row_count_query_executed":False,
        "row_returning_query_executed":False,
        "row_level_coordinates_returned":False,
        "source_record":{
            "version":d["release"]["version"],
            "zenodo_record":d["release"]["zenodo_record"],
            "zenodo_doi":d["release"]["zenodo_doi"],
            "github_tag_commit":d["release"]["github_tag_commit"]
        },
        "file_integrity":{
            "size_bytes":size,
            "sha256":sha,
            "md5":md5,
            "pass":integrity
        },
        "schema":schema,
        "n_schema_columns":len(schema),
        "required_group_matches":required,
        "optional_group_matches":optional,
        "missing_required_groups":missing,
        "gate_pass":gate,
        "next_gate":d["next_gate_if_pass"] if gate else d["next_gate_if_hold"]
    }
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
