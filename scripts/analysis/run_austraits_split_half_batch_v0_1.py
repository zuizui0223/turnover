#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,subprocess
from pathlib import Path
import duckdb

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
ap.add_argument("--state-dir",type=Path,required=True)
ap.add_argument("--r-script",type=Path,required=True)
a=ap.parse_args()
systems=json.loads(a.batch_json.read_text())
if not systems:raise SystemExit("empty batch")
a.out_dir.mkdir(parents=True,exist_ok=True);a.state_dir.mkdir(parents=True,exist_ok=True)

con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE candidates(system_id VARCHAR,family VARCHAR,trait_name VARCHAR,expected_unit VARCHAR)")
con.executemany("INSERT INTO candidates VALUES (?,?,?,?)",[(s["system_id"],s["family"],s["trait_name"],s["expected_unit"]) for s in systems])
sql=r"""
WITH base AS (
 SELECT c.system_id,trim(CAST(a.family AS VARCHAR)) family,trim(CAST(a.genus AS VARCHAR)) genus,
        trim(CAST(a.binomial AS VARCHAR)) species,c.expected_unit,
        trim(CAST(a.dataset_id AS VARCHAR))||chr(31)||trim(CAST(a.observation_id AS VARCHAR)) record_key,
        try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) value_num,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') unit
 FROM read_parquet(?) a JOIN candidates c
 ON trim(CAST(a.family AS VARCHAR))=c.family AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
 WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
   AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
   AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
   AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
   AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
   AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
),
dedup AS (
 SELECT DISTINCT system_id,family,genus,species,expected_unit,record_key,value_num,unit FROM base
),
states AS (
 SELECT system_id,family,species,min(genus) genus,median(value_num) state_num
 FROM dedup
 WHERE value_num IS NOT NULL AND isfinite(value_num)
   AND expected_unit<>'' AND unit=expected_unit
 GROUP BY system_id,family,species
 HAVING count(DISTINCT genus)=1
)
SELECT system_id,family,genus,species,state_num
FROM states ORDER BY system_id,species,genus
"""
cur=con.execute(sql,[str(a.parquet)]);rows=cur.fetchall();con.close()
by={}
for sid,fam,genus,species,state in rows:
    by.setdefault(sid,[]).append({"species":species,"genus":genus,"family":fam,"state_num":float(state)})

for s in systems:
    rr=by.get(s["system_id"],[])
    if len(rr)!=int(s["n_input_species"]):raise SystemExit(f"species mismatch {s['system_id']}: {len(rr)} != {s['n_input_species']}")
    if any(r["state_num"]<=0 for r in rr):raise SystemExit(f"nonpositive matched-log state {s['system_id']}")
    p=a.state_dir/f"{s['system_id']}.csv"
    with p.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=["species","genus","family","state_num"]);w.writeheader();w.writerows(rr)
    cmd=["Rscript",str(a.r_script),
         "--system-id",s["system_id"],"--family",s["family"],"--trait",s["trait_name"],
         "--state-table",str(p),"--expected-prune",str(s["n_prune"]),"--expected-bind",str(s["n_bind"]),
         "--frozen-s3",str(s["S3_log_rho"]),"--frozen-prune",str(s["prune_log_rho"]),
         "--out",str(a.out_dir/f"{s['system_id']}.json")]
    subprocess.run(cmd,check=True)
print(json.dumps({"status":"AUSTRAITS_SPLIT_HALF_BATCH_COMPLETE","n_systems":len(systems)},indent=2))
