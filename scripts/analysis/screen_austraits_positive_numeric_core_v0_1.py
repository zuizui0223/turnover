#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from collections import Counter,defaultdict,deque
from pathlib import Path
import duckdb,yaml

def truth(x): return str(x).strip().lower() in {"true","t","1"}

ap=argparse.ArgumentParser()
ap.add_argument("--parquet",type=Path,required=True)
ap.add_argument("--traits-yml",type=Path,required=True)
ap.add_argument("--core-table",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
ap.add_argument("--table-out",type=Path,required=True)
ap.add_argument("--matched-core-out",type=Path,required=True)
a=ap.parse_args()
for p in [a.out,a.table_out,a.matched_core_out]: p.parent.mkdir(parents=True,exist_ok=True)

core=list(csv.DictReader(a.core_table.open(newline="",encoding="utf-8")))
if not core: raise SystemExit("empty final core")
cfg=yaml.safe_load(a.traits_yml.read_text())["traits"]["elements"]
numeric=[]
for r in core:
    tr=r["trait_name"]
    typ=str(cfg[tr].get("type","")).strip().lower()
    if typ!="numeric": continue
    unit="" if cfg[tr].get("units") is None else str(cfg[tr].get("units")).strip()
    if not unit: raise SystemExit(f"numeric trait missing standard unit: {tr}")
    numeric.append((r["family"],tr,unit))
if not numeric: raise SystemExit("no numeric systems in final core")

con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE candidates(family VARCHAR,trait_name VARCHAR,expected_unit VARCHAR)")
con.executemany("INSERT INTO candidates VALUES (?,?,?)",numeric)
sql=r"""
WITH base AS (
 SELECT trim(CAST(a.family AS VARCHAR)) AS "family",
        trim(CAST(a.genus AS VARCHAR)) genus,
        trim(CAST(a.binomial AS VARCHAR)) species,
        trim(CAST(a.trait_name AS VARCHAR)) trait_name,
        c.expected_unit,
        trim(CAST(a.dataset_id AS VARCHAR))||chr(31)||trim(CAST(a.observation_id AS VARCHAR)) record_key,
        try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) value_num,
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
 SELECT DISTINCT family,genus,species,trait_name,expected_unit,record_key,value_num,unit FROM base
),
states AS (
 SELECT family,trait_name,species,
        median(value_num) species_state,
        count(DISTINCT genus) n_genus
 FROM dedup
 WHERE value_num IS NOT NULL AND isfinite(value_num)
   AND unit=expected_unit
 GROUP BY family,trait_name,species
),
valid AS (
 SELECT * FROM states WHERE n_genus=1
)
SELECT family,trait_name,
       count(*) n_species,
       sum(CASE WHEN species_state<=0 THEN 1 ELSE 0 END) n_nonpositive,
       sum(CASE WHEN species_state>0 THEN 1 ELSE 0 END) n_positive
FROM valid
GROUP BY family,trait_name
ORDER BY family,trait_name
"""
cur=con.execute(sql,[str(a.parquet)])
cols=[x[0] for x in cur.description]
rows=[dict(zip(cols,r)) for r in cur.fetchall()]
con.close()
m={(r["family"],r["trait_name"]):r for r in rows}
screen=[]
coremap={(r["family"],r["trait_name"]):r for r in core}
for fam,tr,unit in numeric:
    z=m.get((fam,tr))
    if z is None: raise SystemExit(f"numeric system missing states: {fam} / {tr}")
    expected=int(coremap[(fam,tr)]["n_input_species"])
    if int(z["n_species"])!=expected:
        raise SystemExit(f"state count mismatch {fam} / {tr}: {z['n_species']} != {expected}")
    screen.append({
      "family":fam,"trait_name":tr,"n_species":int(z["n_species"]),
      "n_nonpositive_species":int(z["n_nonpositive"]),
      "log_domain_pass":int(z["n_nonpositive"])==0
    })
with a.table_out.open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(screen[0]));w.writeheader();w.writerows(screen)

eligible={(r["family"],r["trait_name"]) for r in screen if r["log_domain_pass"]}
edges=set(eligible)
iters=0
while True:
    iters+=1
    fd=Counter(f for f,t in edges);td=Counter(t for f,t in edges)
    nxt={(f,t) for f,t in edges if fd[f]>=2 and td[t]>=5}
    if nxt==edges: break
    edges=nxt

adj=defaultdict(set)
for f,t in edges:
    F=("F",f);T=("T",t);adj[F].add(T);adj[T].add(F)
seen=set();components=0
for n in adj:
    if n in seen: continue
    components+=1;dq=deque([n]);seen.add(n)
    while dq:
        u=dq.popleft()
        for v in adj[u]:
            if v not in seen:seen.add(v);dq.append(v)
connected=bool(adj) and components==1
families=sorted({f for f,t in edges});traits=sorted({t for f,t in edges})
gate=len(families)>=12 and len(traits)>=4 and connected
matched=[coremap[k] for k in sorted(edges)]
if matched:
    with a.matched_core_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(matched[0]));w.writeheader();w.writerows(matched)
else:
    a.matched_core_out.write_text("")

out={
  "version":"v0.1",
  "status":"AUSTRAITS_MATCHED_POSITIVE_NUMERIC_CORE_PASS" if gate else "HOLD_AUSTRAITS_MATCHED_POSITIVE_NUMERIC_CORE",
  "outcome_blind":True,
  "austraits_memory_effects_opened":False,
  "n_numeric_systems":len(numeric),
  "n_log_domain_pass_before_pruning":len(eligible),
  "n_systems":len(edges),"n_families":len(families),"n_traits":len(traits),
  "connected_components":components,"connected":connected,"iterations":iters,
  "gate_pass":gate,
  "n_nonpositive_systems":sum(not r["log_domain_pass"] for r in screen)
}
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
