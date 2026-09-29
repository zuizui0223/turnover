#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"globi_parquet_schema_design_v0_3.json"


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
    resolved={}
    missing={}
    if transport_error is None:
        for group,requirements in d["alias_contract"].items():
            group_missing=[]
            group_resolved=[]
            for alternatives in requirements:
                found=[x for x in alternatives if x in names]
                if not found:
                    group_missing.append(alternatives)
                else:
                    group_resolved.append({
                        "alternatives":alternatives,
                        "resolved_field":found[0],
                        "all_present_aliases":found
                    })
            checks[group]=(len(group_missing)==0)
            resolved[group]=group_resolved
            if group_missing:
                missing[group]=group_missing

    passed=(transport_error is None and bool(checks) and all(checks.values()))
    if transport_error is not None:
        status="HOLD_GLOBI_PARQUET_SCHEMA_TRANSPORT"
        next_gate="Use only the already-frozen TSV header fallback; do not inspect data rows."
    elif passed:
        status="GLOBI_PARQUET_SCHEMA_ALIAS_PASS"
        next_gate=d["next_gate_if_pass"]
    else:
        status="HOLD_GLOBI_REQUIRED_SCHEMA_ALIAS_MISSING"
        next_gate="Primary GloBI route stops unless a new alias is justified solely from schema metadata before any row opening."

    out={
      "version":"v0.3",
      "status":status,
      "design":str(DESIGN.relative_to(ROOT)),
      "schema_only":True,
      "row_count_query_executed":False,
      "row_sample_query_executed":False,
      "row_returning_query_executed":False,
      "interaction_rows_opened":False,
      "parquet_file":d["primary_file"],
      "transport_error":transport_error,
      "parquet_schema_function_columns":schema_columns,
      "schema_fields":schema_rows,
      "required_group_checks":checks,
      "resolved_aliases":resolved,
      "missing_required_alias_groups":missing,
      "gate_pass":passed,
      "next_gate":next_gate
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
