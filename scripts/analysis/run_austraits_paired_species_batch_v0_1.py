#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,subprocess,tempfile
from pathlib import Path
import duckdb

ap=argparse.ArgumentParser()
ap.add_argument("--batch-json",type=Path,required=True)
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
ap.add_argument("--r-script",type=Path,required=True)
a=ap.parse_args()
cells=json.loads(a.batch_json.read_text())
if not cells:raise SystemExit("empty batch")
a.out_dir.mkdir(parents=True,exist_ok=True)

# Extract all required family-trait numeric species states once.
keys=sorted({(c["family"],c["trait_a"],c["unit_a"]) for c in cells}|{(c["family"],c["trait_b"],c["unit_b"]) for c in cells})
con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE candidates(family_name VARCHAR,trait_name VARCHAR,expected_unit VARCHAR)")
con.executemany("INSERT INTO candidates VALUES (?,?,?)",keys)
sql=r"""
WITH base AS (
 SELECT trim(CAST(a.family AS VARCHAR)) AS family_name,
        trim(CAST(a.genus AS VARCHAR)) AS genus,
        trim(CAST(a.binomial AS VARCHAR)) AS species,
        trim(CAST(a.trait_name AS VARCHAR)) AS trait_name,
        c.expected_unit,
        trim(CAST(a.dataset_id AS VARCHAR))||chr(31)||trim(CAST(a.observation_id AS VARCHAR)) AS record_key,
        try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) AS value_num,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') AS unit
 FROM read_parquet(?) a JOIN candidates c
 ON trim(CAST(a.family AS VARCHAR))=c.family_name
 AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
 WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
   AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
   AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
   AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
   AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
   AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
),
dedup AS (
 SELECT DISTINCT family_name,genus,species,trait_name,expected_unit,record_key,value_num,unit FROM base
),
states AS (
 SELECT family_name,trait_name,species,min(genus) AS genus,median(value_num) AS state_num
 FROM dedup
 WHERE value_num IS NOT NULL AND isfinite(value_num)
   AND expected_unit<>'' AND unit=expected_unit
 GROUP BY family_name,trait_name,species
 HAVING count(DISTINCT genus)=1
)
SELECT family_name,trait_name,species,genus,state_num
FROM states
WHERE state_num>0
ORDER BY family_name,trait_name,species
"""
cur=con.execute(sql,[str(a.parquet)]);rows=cur.fetchall();con.close()
by={}
for fam,tr,sp,gen,val in rows:
    by.setdefault((fam,tr),{})[sp]={"genus":gen,"state":float(val)}

with tempfile.TemporaryDirectory(prefix="paired_species_") as td:
    td=Path(td)
    for c in cells:
        A=by.get((c["family"],c["trait_a"]),{})
        B=by.get((c["family"],c["trait_b"]),{})
        shared=sorted(set(A)&set(B))
        out=a.out_dir/f"{c['cell_id']}.json"
        if len(shared)<20:
            out.write_text(json.dumps({
              "version":"v0.1","status":"HOLD_SHARED_SPECIES_LT20","cell_id":c["cell_id"],
              "family":c["family"],"trait_a":c["trait_a"],"trait_b":c["trait_b"],
              "n_shared_species":len(shared)
            },indent=2)+"\n")
            continue
        p=td/f"{c['cell_id']}.csv"
        with p.open("w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=["species","genus","family","state_a","state_b"])
            w.writeheader()
            for sp in shared:
                # genus should agree because species identity is shared; enforce it.
                if A[sp]["genus"]!=B[sp]["genus"]:
                    raise SystemExit(f"genus mismatch {c['cell_id']} {sp}")
                w.writerow({"species":sp,"genus":A[sp]["genus"],"family":c["family"],
                            "state_a":A[sp]["state"],"state_b":B[sp]["state"]})
        cmd=["Rscript",str(a.r_script),"--cell-id",c["cell_id"],"--family",c["family"],
             "--trait-a",c["trait_a"],"--trait-b",c["trait_b"],
             "--state-table",str(p),"--out",str(out)]
        subprocess.run(cmd,check=True)
print(json.dumps({"status":"PAIRED_SPECIES_BATCH_COMPLETE","n_cells":len(cells)},indent=2))
