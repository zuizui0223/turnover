#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import duckdb,yaml

def truth(x): return str(x).strip().lower() in {"true","t","1"}

ap=argparse.ArgumentParser()
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--semantic-table",type=Path,required=True)
ap.add_argument("--traits-yml",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
ap.add_argument("--manifest",type=Path,required=True)
a=ap.parse_args()
a.out_dir.mkdir(parents=True,exist_ok=True); a.manifest.parent.mkdir(parents=True,exist_ok=True)

sem=[r for r in csv.DictReader(a.semantic_table.open(newline="")) if truth(r["semantic_pass"])]
cfg=yaml.safe_load(a.traits_yml.read_text())["traits"]["elements"]
cand=[]
for i,r in enumerate(sorted(sem,key=lambda z:(z["family"],z["trait_name"])),1):
    typ=str(cfg[r["trait_name"]].get("type","")).strip().lower()
    unit="" if cfg[r["trait_name"]].get("units") is None else str(cfg[r["trait_name"]].get("units")).strip()
    cand.append((f"X{i:04d}",r["family"],r["trait_name"],typ,unit))
con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE candidates(system_id VARCHAR,family VARCHAR,trait_name VARCHAR,config_type VARCHAR,expected_unit VARCHAR)")
con.executemany("INSERT INTO candidates VALUES (?,?,?,?,?)",cand)
sql=r"""
WITH base AS (
 SELECT c.system_id,trim(CAST(a.family AS VARCHAR)) family,trim(CAST(a.genus AS VARCHAR)) genus,
        trim(CAST(a.binomial AS VARCHAR)) species,trim(CAST(a.trait_name AS VARCHAR)) trait_name,
        c.config_type,c.expected_unit,
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
), dedup AS (
 SELECT DISTINCT * FROM base
), num AS (
 SELECT system_id,family,trait_name,config_type,species,min(genus) genus
 FROM dedup WHERE config_type='numeric'
 AND try_cast(value_text AS DOUBLE) IS NOT NULL AND isfinite(try_cast(value_text AS DOUBLE))
 AND expected_unit<>'' AND unit=expected_unit
 GROUP BY system_id,family,trait_name,config_type,species HAVING count(DISTINCT genus)=1
), cc AS (
 SELECT system_id,family,trait_name,config_type,species,value_text,count(*) n
 FROM dedup WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY system_id,family,trait_name,config_type,species,value_text
), cr AS (
 SELECT *,max(n) OVER(PARTITION BY system_id,species) max_n FROM cc
), cm AS (
 SELECT system_id,family,trait_name,config_type,species,count(*) FILTER(WHERE n=max_n) n_modal
 FROM cr GROUP BY system_id,family,trait_name,config_type,species
), cg AS (
 SELECT system_id,species,min(genus) genus FROM dedup
 WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY system_id,species HAVING count(DISTINCT genus)=1
), cat AS (
 SELECT m.system_id,m.family,m.trait_name,m.config_type,m.species,g.genus
 FROM cm m JOIN cg g USING(system_id,species) WHERE m.n_modal=1
)
SELECT * FROM num UNION ALL SELECT * FROM cat ORDER BY system_id,species,genus
"""
cur=con.execute(sql,[str(a.parquet)]); cols=[z[0] for z in cur.description]
rows=[dict(zip(cols,r)) for r in cur.fetchall()]; con.close()
by={}
for r in rows: by.setdefault(r["system_id"],[]).append(r)
manifest=[]
for sid,fam,tr,typ,unit in cand:
    rr=by.get(sid,[])
    p=a.out_dir/f"{sid}.csv"
    with p.open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=["species","genus","family"]); w.writeheader()
        for z in rr: w.writerow({"species":z["species"],"genus":z["genus"],"family":z["family"]})
    manifest.append({"system_id":sid,"family":fam,"trait_name":tr,"config_type":typ,"n_species":len(rr)})
with a.manifest.open("w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(manifest[0])); w.writeheader(); w.writerows(manifest)
print(json.dumps({"status":"AUSTRAITS_EXACT_CROSSWALK_SPECIES_LISTS_READY","n_systems":len(manifest),"n_species_rows":len(rows),"effects_opened":False},indent=2))
