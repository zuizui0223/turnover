#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,subprocess,tempfile
from pathlib import Path
import duckdb,yaml

def truth(x): return str(x).strip().lower() in {"true","t","1"}

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--traits-yml",type=Path,required=True)
ap.add_argument("--matched-core",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
ap.add_argument("--r-script",type=Path,required=True)
a=ap.parse_args()
systems=json.loads(a.batch_json.read_text())
if not systems: raise SystemExit("empty batch")
a.out_dir.mkdir(parents=True,exist_ok=True)
cfg=yaml.safe_load(a.traits_yml.read_text())["traits"]["elements"]
matched=set()
if a.matched_core.exists() and a.matched_core.stat().st_size:
    for r in csv.DictReader(a.matched_core.open(newline="",encoding="utf-8")):
        matched.add((r["family"],r["trait_name"]))

cand=[]
for s in systems:
    tr=s["trait_name"]; typ=s["config_type"]
    if tr not in cfg: raise SystemExit(f"trait missing config: {tr}")
    cfgtyp=str(cfg[tr].get("type","")).strip().lower()
    if cfgtyp!=typ: raise SystemExit(f"config type mismatch: {tr}")
    unit="" if cfg[tr].get("units") is None else str(cfg[tr].get("units")).strip()
    cand.append((s["system_id"],s["family"],tr,typ,unit))

con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE candidates(system_id VARCHAR,family VARCHAR,trait_name VARCHAR,config_type VARCHAR,expected_unit VARCHAR)")
con.executemany("INSERT INTO candidates VALUES (?,?,?,?,?)",cand)
sql=r"""
WITH base AS (
 SELECT c.system_id,
        trim(CAST(a.family AS VARCHAR)) AS "family",
        trim(CAST(a.genus AS VARCHAR)) genus,
        trim(CAST(a.binomial AS VARCHAR)) species,
        c.trait_name,c.config_type,c.expected_unit,
        trim(CAST(a.dataset_id AS VARCHAR))||chr(31)||trim(CAST(a.observation_id AS VARCHAR)) record_key,
        trim(CAST(a.value AS VARCHAR)) value_text,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') unit
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
 SELECT DISTINCT system_id,family,genus,species,trait_name,config_type,expected_unit,record_key,value_text,unit
 FROM base
),
num_state AS (
 SELECT system_id,family,trait_name,config_type,species,
        min(genus) genus,
        median(try_cast(value_text AS DOUBLE)) state_num
 FROM dedup
 WHERE config_type='numeric'
   AND try_cast(value_text AS DOUBLE) IS NOT NULL
   AND isfinite(try_cast(value_text AS DOUBLE))
   AND expected_unit<>'' AND unit=expected_unit
 GROUP BY system_id,family,trait_name,config_type,species
 HAVING count(DISTINCT genus)=1
),
cat_counts AS (
 SELECT system_id,family,trait_name,config_type,species,value_text,count(*) n
 FROM dedup
 WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY system_id,family,trait_name,config_type,species,value_text
),
cat_ranked AS (
 SELECT *,max(n) OVER(PARTITION BY system_id,species) max_n FROM cat_counts
),
cat_modes AS (
 SELECT system_id,family,trait_name,config_type,species,
        count(*) FILTER(WHERE n=max_n) n_modal,
        min(value_text) FILTER(WHERE n=max_n) state_cat
 FROM cat_ranked GROUP BY system_id,family,trait_name,config_type,species
),
cat_genus AS (
 SELECT system_id,species,min(genus) genus
 FROM dedup
 WHERE config_type='categorical' AND expected_unit='' AND unit=''
 GROUP BY system_id,species
 HAVING count(DISTINCT genus)=1
),
cat_state AS (
 SELECT m.system_id,m.family,m.trait_name,m.config_type,m.species,g.genus,m.state_cat
 FROM cat_modes m JOIN cat_genus g USING(system_id,species)
 WHERE m.n_modal=1
)
SELECT system_id,family,trait_name,config_type,species,genus,
       state_num,CAST(NULL AS VARCHAR) state_cat
FROM num_state
UNION ALL
SELECT system_id,family,trait_name,config_type,species,genus,
       CAST(NULL AS DOUBLE) state_num,state_cat
FROM cat_state
ORDER BY system_id,species
"""
cur=con.execute(sql,[str(a.parquet)])
cols=[x[0] for x in cur.description]
rows=[dict(zip(cols,r)) for r in cur.fetchall()]
con.close()
by={}
for r in rows: by.setdefault(r["system_id"],[]).append(r)

with tempfile.TemporaryDirectory(prefix="austraits_states_") as td:
    td=Path(td)
    for s in systems:
        sid=s["system_id"]; rr=by.get(sid,[])
        expected=int(s["n_input_species"])
        if len(rr)!=expected:
            raise SystemExit(f"species-state count mismatch {sid}: {len(rr)} != {expected}")
        log_enabled=(s["family"],s["trait_name"]) in matched
        if log_enabled:
            if s["config_type"]!="numeric": raise SystemExit(f"matched log system not numeric: {sid}")
            if any(r["state_num"] is None or float(r["state_num"])<=0 for r in rr):
                raise SystemExit(f"matched log system contains nonpositive state: {sid}")
        state_path=td/f"{sid}.csv"
        fields=["species","genus","family","state_num","state_cat"]
        with state_path.open("w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=fields);w.writeheader()
            for r in rr:
                w.writerow({k:r[k] for k in fields})
        out=a.out_dir/f"{sid}.json"
        cmd=[
          "Rscript",str(a.r_script),
          "--system-id",sid,"--family",s["family"],"--trait",s["trait_name"],
          "--config-type",s["config_type"],"--state-table",str(state_path),
          "--expected-prune",str(s["n_prune"]),"--expected-bind",str(s["n_bind"]),
          "--log-enabled","true" if log_enabled else "false",
          "--out",str(out)
        ]
        subprocess.run(cmd,check=True)

print(json.dumps({"status":"AUSTRAITS_REAL_EFFECT_BATCH_COMPLETE","n_systems":len(systems)},indent=2))
