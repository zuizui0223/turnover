#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import duckdb

ap=argparse.ArgumentParser()
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
a=ap.parse_args()
expected="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
h=hashlib.sha256()
with a.parquet.open("rb") as fh:
    for b in iter(lambda:fh.read(1024*1024),b""): h.update(b)
if h.hexdigest()!=expected: raise SystemExit("source integrity mismatch")

con=duckdb.connect(database=":memory:")
rows=con.execute("""
WITH base AS (
 SELECT trim(CAST(family AS VARCHAR)) AS family,
        trim(CAST(binomial AS VARCHAR)) AS species,
        trim(CAST(trait_name AS VARCHAR)) AS trait_name
 FROM read_parquet(?)
 WHERE lower(trim(CAST(taxon_rank AS VARCHAR)))='species'
   AND family IS NOT NULL AND trim(CAST(family AS VARCHAR))<>''
   AND binomial IS NOT NULL AND trim(CAST(binomial AS VARCHAR))<>''
   AND trait_name IS NOT NULL AND trim(CAST(trait_name AS VARCHAR))<>''
   AND value IS NOT NULL AND trim(CAST(value AS VARCHAR))<>''
),
agg AS (
 SELECT family,trait_name,count(DISTINCT species) AS temporal_species
 FROM base GROUP BY family,trait_name
)
SELECT family,trait_name,temporal_species,(temporal_species>=20) AS structural_pass
FROM agg ORDER BY family,trait_name
""",[str(a.parquet)]).fetchall()
con.close()

fields=["family","trait_name","temporal_species","structural_pass"]
a.table_out.parent.mkdir(parents=True,exist_ok=True)
with a.table_out.open("w",newline="") as fh:
    w=csv.writer(fh); w.writerow(fields); w.writerows(rows)
passing=[r for r in rows if r[3]]
families=sorted({r[0] for r in passing}); traits=sorted({r[1] for r in passing})
out={
 "version":"v0.1",
 "status":"AUSTRAITS_TEMPORAL_SUPPORT_PASS" if len(families)>=12 and len(traits)>=4 else "HOLD_AUSTRAITS_TEMPORAL_SUPPORT",
 "outcome_blind":True,
 "raw_trait_values_opened":False,
 "memory_effects_opened":False,
 "n_family_trait_systems":len(rows),
 "n_structural_pass_systems":len(passing),
 "n_independent_families":len(families),
 "n_distinct_traits":len(traits),
 "qualifying_traits":traits,
 "minimum_families":12,
 "minimum_traits":4,
 "gate_pass":len(families)>=12 and len(traits)>=4
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
