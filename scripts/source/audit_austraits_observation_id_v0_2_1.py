#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import duckdb
ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"austraits_observation_id_audit_v0_2_1.json"
def dig(p,a):
    h=hashlib.new(a)
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--parquet",type=Path,required=True); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    d=json.loads(DESIGN.read_text())
    expected_sha="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
    if dig(a.parquet,"sha256")!=expected_sha: raise RuntimeError("source integrity mismatch")
    con=duckdb.connect(database=":memory:")
    row=con.execute("""
      WITH ids AS (
        SELECT trim(CAST(observation_id AS VARCHAR)) AS observation_id,
               trim(CAST(dataset_id AS VARCHAR)) AS dataset_id
        FROM read_parquet(?)
        WHERE observation_id IS NOT NULL AND trim(CAST(observation_id AS VARCHAR))<>''
          AND dataset_id IS NOT NULL AND trim(CAST(dataset_id AS VARCHAR))<>''
      ),
      per_id AS (
        SELECT observation_id,count(DISTINCT dataset_id) AS n_datasets
        FROM ids GROUP BY observation_id
      )
      SELECT
        (SELECT count(*) FROM ids) AS rows_with_ids,
        (SELECT count(DISTINCT observation_id) FROM ids) AS distinct_observation_ids,
        (SELECT count(DISTINCT dataset_id || chr(31) || observation_id) FROM ids) AS distinct_composite_ids,
        count(*) FILTER (WHERE n_datasets>1) AS cross_dataset_colliding_ids,
        max(n_datasets) AS max_datasets_per_observation_id
      FROM per_id
    """,[str(a.parquet)]).fetchone()
    con.close()
    collisions=int(row[3] or 0)
    valid=collisions==0
    out={
      "version":"v0.2.1",
      "status":"AUSTRAITS_OBSERVATION_ID_GLOBAL_UNIQUENESS_PASS" if valid else "HOLD_AUSTRAITS_OBSERVATION_ID_NOT_GLOBAL",
      "outcome_blind":True,
      "raw_rows_returned":False,
      "raw_trait_values_opened":False,
      "biological_turnover_outcomes_opened":False,
      "rows_with_ids":int(row[0]),
      "distinct_observation_ids":int(row[1]),
      "distinct_composite_ids":int(row[2]),
      "cross_dataset_colliding_ids":collisions,
      "max_datasets_per_observation_id":int(row[4] or 0),
      "v0_2_record_identity_validated":valid,
      "next_gate":d["decision"]["zero_cross_dataset_collisions"] if valid else d["decision"]["any_cross_dataset_collision"]
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
