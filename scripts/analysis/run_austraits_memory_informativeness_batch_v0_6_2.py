#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,subprocess
from pathlib import Path
import duckdb

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
ap.add_argument("--species-dir",type=Path,required=True)
ap.add_argument("--r-script",type=Path,required=True)
a=ap.parse_args()
systems=json.loads(a.batch_json.read_text())
a.out_dir.mkdir(parents=True,exist_ok=True); a.species_dir.mkdir(parents=True,exist_ok=True)
if not systems: raise SystemExit("empty batch")

con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE candidates(geometry_id VARCHAR,family VARCHAR,trait_name VARCHAR,config_type VARCHAR,expected_unit VARCHAR)")
con.executemany("INSERT INTO candidates VALUES (?,?,?,?,?)",[(s["geometry_id"],s["family"],s["trait_name"],s["config_type"],s["expected_unit"]) for s in systems])
sql="""
WITH base AS (
 SELECT c.geometry_id,
        trim(CAST(a.family AS VARCHAR)) AS family,
        trim(CAST(a.genus AS VARCHAR)) AS genus,
        trim(CAST(a.binomial AS VARCHAR)) AS species,
        c.config_type,c.expected_unit,
        trim(CAST(a.dataset_id AS VARCHAR)) || chr(31) || trim(CAST(a.observation_id AS VARCHAR)) AS record_key,
        trim(CAST(a.value AS VARCHAR)) AS value_text,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') AS unit
 FROM read_parquet(?) a
 JOIN candidates c
   ON trim(CAST(a.family AS VARCHAR))=c.family
  AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
 WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
   AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
   AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
   AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
   AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
   AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
),
dedup AS (
 SELECT DISTINCT geometry_id,family,genus,species,config_type,expected_unit,record_key,value_text,unit FROM base
),
num_species AS (
 SELECT geometry_id,family,species,min(genus) AS genus
 FROM dedup
 WHERE config_type='numeric'
   AND try_cast(value_text AS DOUBLE) IS NOT NULL
   AND isfinite(try_cast(value_text AS DOUBLE))
   AND expected_unit<>'' AND unit=expected_unit
 GROUP BY geometry_id,family,species
 HAVING count(DISTINCT genus)=1
),
cat_counts AS (
 SELECT geometry_id,family,species,value_text,count(*) AS n
 FROM dedup
 WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY geometry_id,family,species,value_text
),
cat_ranked AS (
 SELECT *,max(n) OVER(PARTITION BY geometry_id,species) AS max_n FROM cat_counts
),
cat_species AS (
 SELECT geometry_id,family,species,count(*) FILTER(WHERE n=max_n) AS n_modal
 FROM cat_ranked GROUP BY geometry_id,family,species
),
cat_genus AS (
 SELECT geometry_id,family,species,min(genus) AS genus
 FROM dedup
 WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY geometry_id,family,species
 HAVING count(DISTINCT genus)=1
),
cat_unique AS (
 SELECT s.geometry_id,s.family,s.species,g.genus
 FROM cat_species s
 JOIN cat_genus g USING(geometry_id,family,species)
 WHERE s.n_modal=1
)
SELECT geometry_id,family,genus,species FROM num_species
UNION ALL
SELECT geometry_id,family,genus,species FROM cat_unique
ORDER BY geometry_id,species,genus
"""
cur=con.execute(sql,[str(a.parquet)])
rows=cur.fetchall(); con.close()
by={}
for gid,fam,genus,species in rows:
    by.setdefault(gid,[]).append({"species":species,"genus":genus,"family":fam})

for s in systems:
    rr=by.get(s["geometry_id"],[])
    if len(rr)!=int(s["n_input_species"]):
        raise SystemExit(f"species count mismatch {s['geometry_id']}: {len(rr)} != {s['n_input_species']}")
    spath=a.species_dir/f"{s['geometry_id']}.csv"
    with spath.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=["species","genus","family"]); w.writeheader(); w.writerows(rr)
    out=a.out_dir/f"{s['geometry_id']}.json"
    cmd=[
      "Rscript",str(a.r_script),
      "--family",s["family"],"--trait",s["trait_name"],"--config-type",s["config_type"],
      "--geometry-id",s["geometry_id"],"--geometry-hash",s["geometry_hash"],
      "--species-table",str(spath),
      "--expected-prune",str(s["n_prune"]),"--expected-bind",str(s["n_bind"]),
      "--out",str(out)
    ]
    subprocess.run(cmd,check=True)
print(json.dumps({"status":"BATCH_COMPLETE","n_geometries":len(systems),"ids":[s["geometry_id"] for s in systems]},indent=2))
