#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"globi_parquet_schema_design_v0_2.json"


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)

    d=json.loads(DESIGN.read_text())
    url=d["primary_file"]["url"]

    con=duckdb.connect(database=":memory:")
    transport_error=None
    schema_rows=[]
    schema_columns=[]
    try:
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")
        cur=con.execute("SELECT * FROM parquet_schema(?)",[url])
        schema_columns=[x[0] for x in cur.description]
        raw=cur.fetchall()
        name_idx=schema_columns.index("name")
        type_idx=schema_columns.index("type") if "type" in schema_columns else None
        for row in raw:
            name=row[name_idx]
            if not name or str(name).lower()=="schema":
                continue
            schema_rows.append({
                "name":str(name),
                "type":None if type_idx is None else str(row[type_idx])
            })
    except Exception as exc:
        transport_error=f"{type(exc).__name__}: {exc}"

    names={x["name"] for x in schema_rows}
    checks={}
    missing={}
    if transport_error is None:
        for group,requirements in d["required_semantic_fields"].items():
            group_missing=[]
            for alternatives in requirements:
                found=[x for x in alternatives if x in names]
                if not found:
                    group_missing.append(alternatives)
            checks[group]=(len(group_missing)==0)
            if group_missing:
                missing[group]=group_missing

    if transport_error is not None:
        status="HOLD_GLOBI_PARQUET_SCHEMA_TRANSPORT_TSV_FALLBACK_AUTHORIZED"
        passed=False
        next_gate=d["next_gate_if_parquet_transport_hold"]
    else:
        passed=all(checks.values()) if checks else False
        status="GLOBI_PARQUET_SCHEMA_PASS" if passed else "HOLD_GLOBI_REQUIRED_SCHEMA_MISSING"
        next_gate=d["next_gate_if_pass"] if passed else "Stop GloBI primary route unless the missing field is an alias explicitly frozen before row opening."

    out={
      "version":"v0.2",
      "status":status,
      "design":str(DESIGN.relative_to(ROOT)),
      "schema_only":True,
      "row_returning_query_executed":False,
      "interaction_rows_opened":False,
      "parquet_file":d["primary_file"],
      "transport_error":transport_error,
      "parquet_schema_function_columns":schema_columns,
      "schema_fields":schema_rows,
      "required_group_checks":checks,
      "missing_required_alias_groups":missing,
      "gate_pass":passed,
      "next_gate":next_gate
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
