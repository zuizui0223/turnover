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
if not systems:raise SystemExit("empty batch")
a.out_dir.mkdir(parents=True,exist_ok=True);a.species_dir.mkdir(parents=True,exist_ok=True)

con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE candidates(system_id VARCHAR,family VARCHAR,trait_name VARCHAR,config_type VARCHAR,expected_unit VARCHAR)")
con.executemany("INSERT INTO candidates VALUES (?,?,?,?,?)",[(s["system_id"],s["family"],s["trait_name"],s["config_type"],s["expected_unit"]) for s in systems])
sql=r"""
WITH base AS (
 SELECT c.system_id,trim(CAST(a.family AS VARCHAR)) AS family_name,trim(CAST(a.genus AS VARCHAR)) AS genus,
        trim(CAST(a.binomial AS VARCHAR)) species,c.config_type,c.expected_unit,
        trim(CAST(a.dataset_id AS VARCHAR))||chr(31)||trim(CAST(a.observation_id AS VARCHAR)) record_key,
        trim(CAST(a.value AS VARCHAR)) value_text,coalesce(trim(CAST(a.unit AS VARCHAR)),'') unit
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
 SELECT DISTINCT system_id,family_name,genus,species,config_type,expected_unit,record_key,value_text,unit FROM base
),
num AS (
 SELECT system_id,family_name,species,min(genus) genus
 FROM dedup
 WHERE config_type='numeric'
   AND try_cast(value_text AS DOUBLE) IS NOT NULL
   AND isfinite(try_cast(value_text AS DOUBLE))
   AND expected_unit<>'' AND unit=expected_unit
 GROUP BY system_id,family_name,species
 HAVING count(DISTINCT genus)=1
),
cc AS (
 SELECT system_id,family_name,species,value_text,count(*) n
 FROM dedup
 WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY system_id,family_name,species,value_text
),
cr AS (
 SELECT *,max(n) OVER(PARTITION BY system_id,species) max_n FROM cc
),
cm AS (
 SELECT system_id,family_name,species,count(*) FILTER(WHERE n=max_n) n_modal
 FROM cr GROUP BY system_id,family_name,species
),
cg AS (
 SELECT system_id,family_name,species,min(genus) genus
 FROM dedup
 WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY system_id,family_name,species
 HAVING count(DISTINCT genus)=1
),
cat AS (
 SELECT m.system_id,m.family_name,m.species,g.genus
 FROM cm m JOIN cg g USING(system_id,family_name,species)
 WHERE m.n_modal=1
)
SELECT system_id,family_name,genus,species FROM num
UNION ALL
SELECT system_id,family_name,genus,species FROM cat
ORDER BY system_id,species,genus
"""
cur=con.execute(sql,[str(a.parquet)]);rows=cur.fetchall();con.close()
by={}
for sid,fam,genus,species in rows:by.setdefault(sid,[]).append({"species":species,"genus":genus,"family":fam})

for s in systems:
    rr=by.get(s["system_id"],[])
    if len(rr)!=int(s["n_input_species"]):raise SystemExit(f"species mismatch {s['system_id']}: {len(rr)} != {s['n_input_species']}")
    p=a.species_dir/f"{s['system_id']}.csv"
    with p.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=["species","genus","family"]);w.writeheader();w.writerows(rr)
    cmd=["Rscript",str(a.r_script),"--system-id",s["system_id"],"--family",s["family"],"--trait",s["trait_name"],
         "--species-table",str(p),"--expected-prune",str(s["n_prune"]),"--expected-bind",str(s["n_bind"]),
         "--out",str(a.out_dir/f"{s['system_id']}.json")]
    subprocess.run(cmd,check=True)
print(json.dumps({"status":"AUSTRAITS_TREE_GEOMETRY_BATCH_COMPLETE","n_systems":len(systems)},indent=2))
