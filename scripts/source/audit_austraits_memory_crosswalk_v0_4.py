#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,re
from collections import Counter
from pathlib import Path
import duckdb

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"austraits_memory_phylogeny_crosswalk_v0_4.json"
MASTER=ROOT/"data"/"austraits_memory_context_replication_v0_1.json"

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def norm_species(x:str)->str:
    s="_".join(str(x).strip().split())
    return s[:1].upper()+s[1:] if s else s
def norm_one(x:str)->str:
    s=str(x).strip()
    return s[:1].upper()+s[1:] if s else s

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--parquet",type=Path,required=True)
    ap.add_argument("--semantic-table",type=Path,required=True)
    ap.add_argument("--tree-tips",type=Path,required=True)
    ap.add_argument("--nodes",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--table-out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True); a.table_out.parent.mkdir(parents=True,exist_ok=True)
    d=json.loads(DESIGN.read_text()); master=json.loads(MASTER.read_text())
    if sha256(a.parquet)!=master["source"]["parquet"]["sha256"]:
        raise RuntimeError("AusTraits parquet integrity mismatch")

    candidates=[]
    with a.semantic_table.open(newline="",encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if str(r["semantic_pass"]).strip().lower() not in {"true","t","1"}: continue
            candidates.append((r["family"],r["trait_name"],r["config_type"],r["expected_unit"]))
    if not candidates: raise RuntimeError("no semantic PASS candidates")

    tree_tips={line.strip() for line in a.tree_tips.read_text().splitlines() if line.strip()}
    node_genus=set(); node_family=set()
    with a.nodes.open(newline="",encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            lvl=str(r.get("level",""))
            if lvl=="G" and r.get("genus"): node_genus.add(str(r["genus"]).strip())
            if lvl=="F" and r.get("family"): node_family.add(str(r["family"]).strip())
    if not tree_tips or not node_genus or not node_family:
        raise RuntimeError("pinned phylogeny metadata missing")

    con=duckdb.connect(database=":memory:")
    con.execute("CREATE TEMP TABLE candidates(family VARCHAR,trait_name VARCHAR,config_type VARCHAR,expected_unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES (?,?,?,?)",candidates)
    sql="""
    WITH base AS (
      SELECT
        trim(CAST(a.family AS VARCHAR)) AS family,
        trim(CAST(a.genus AS VARCHAR)) AS genus,
        trim(CAST(a.binomial AS VARCHAR)) AS species,
        trim(CAST(a.trait_name AS VARCHAR)) AS trait_name,
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
      SELECT DISTINCT family,genus,species,trait_name,config_type,expected_unit,record_key,value_text,unit
      FROM base
    ),
    num_species AS (
      SELECT DISTINCT family,trait_name,config_type,species,genus
      FROM dedup
      WHERE config_type='numeric'
        AND try_cast(value_text AS DOUBLE) IS NOT NULL
        AND isfinite(try_cast(value_text AS DOUBLE))
        AND unit=expected_unit AND expected_unit<>''
    ),
    cat_counts AS (
      SELECT family,trait_name,config_type,species,genus,value_text,count(*) AS n
      FROM dedup
      WHERE config_type='categorical' AND unit='' AND expected_unit=''
      GROUP BY family,trait_name,config_type,species,genus,value_text
    ),
    cat_ranked AS (
      SELECT *,max(n) OVER(PARTITION BY family,trait_name,species) AS max_n FROM cat_counts
    ),
    cat_species AS (
      SELECT family,trait_name,config_type,species,genus,
        count(*) FILTER (WHERE n=max_n) AS n_modal
      FROM cat_ranked GROUP BY family,trait_name,config_type,species,genus
    ),
    cat_unique AS (
      SELECT family,trait_name,config_type,species,genus
      FROM cat_species WHERE n_modal=1
    )
    SELECT * FROM num_species
    UNION ALL
    SELECT family,trait_name,config_type,species,genus FROM cat_unique
    ORDER BY family,trait_name,species
    """
    cur=con.execute(sql,[str(a.parquet)])
    cols=[x[0] for x in cur.description]
    sp=[dict(zip(cols,r)) for r in cur.fetchall()]
    con.close()

    by={}
    for r in sp:
        by.setdefault((r["family"],r["trait_name"],r["config_type"]),[]).append(r)
    rows=[]
    for fam,tr,typ,unit in candidates:
        rr=by.get((fam,tr,typ),[])
        prune=bind=fail=0
        for r in rr:
            ns=norm_species(r["species"])
            ng=norm_one(r["genus"])
            nf=norm_one(r["family"])
            if ns in tree_tips: prune+=1
            elif ng in node_genus or nf in node_family: bind+=1
            else: fail+=1
        primary=prune+bind
        reasons=[]
        if primary<20: reasons.append("PRIMARY_RESOLVABLE_LT20")
        if prune<20: reasons.append("PRUNE_ONLY_LT20")
        rows.append({
          "family":fam,"trait_name":tr,"config_type":typ,
          "n_input_species":len(rr),"n_prune":prune,"n_bind":bind,"n_fail_to_bind":fail,
          "primary_resolvable_species":primary,
          "crosswalk_pass":not reasons,
          "hold_reason":";".join(reasons)
        })

    fields=["family","trait_name","config_type","n_input_species","n_prune","n_bind","n_fail_to_bind","primary_resolvable_species","crosswalk_pass","hold_reason"]
    with a.table_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
    passing=[r for r in rows if r["crosswalk_pass"]]
    families=sorted({r["family"] for r in passing}); traits=sorted({r["trait_name"] for r in passing})
    hc=Counter()
    for r in rows:
        if not r["crosswalk_pass"]:
            for q in filter(None,r["hold_reason"].split(";")): hc[q]+=1
    gate=len(families)>=12 and len(traits)>=4
    out={
      "version":"v0.4",
      "status":"AUSTRAITS_MEMORY_PHYLOGENY_CROSSWALK_PASS" if gate else "HOLD_AUSTRAITS_MEMORY_PHYLOGENY_CROSSWALK",
      "outcome_blind":True,
      "austraits_memory_effects_opened":False,
      "n_candidate_systems":len(rows),
      "n_crosswalk_pass":len(passing),
      "n_independent_families":len(families),
      "n_distinct_traits":len(traits),
      "hold_reason_counts":dict(sorted(hc.items())),
      "gate_pass":gate,
      "next_gate":d["next_gate_if_pass"] if gate else d["next_gate_if_hold"]
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
