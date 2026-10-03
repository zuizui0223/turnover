#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import duckdb,yaml

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"austraits_memory_semantic_v0_3.json"
MASTER=ROOT/"data"/"austraits_memory_context_replication_v0_1.json"

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--parquet",type=Path,required=True)
    ap.add_argument("--traits-yml",type=Path,required=True)
    ap.add_argument("--support-table",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--table-out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.table_out.parent.mkdir(parents=True,exist_ok=True)
    d=json.loads(DESIGN.read_text()); master=json.loads(MASTER.read_text())
    if sha256(a.parquet)!=master["source"]["parquet"]["sha256"]:
        raise RuntimeError("pinned AusTraits parquet integrity mismatch")

    cfg=yaml.safe_load(a.traits_yml.read_text())["traits"]["elements"]
    meta={}
    for name,m in cfg.items():
        typ=str(m.get("type","")).strip().lower()
        if typ not in {"numeric","categorical"}: continue
        unit=m.get("units")
        unit="" if unit is None else str(unit).strip()
        meta[name]=(typ,unit)

    candidates=[]
    with a.support_table.open(newline="",encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if str(r["structural_pass"]).strip().lower() not in {"true","t","1"}: continue
            tr=r["trait_name"]
            if tr not in meta: raise RuntimeError(f"candidate trait missing config: {tr}")
            typ,unit=meta[tr]
            candidates.append((r["family"],tr,typ,unit))
    if not candidates: raise RuntimeError("no structural candidates")

    con=duckdb.connect(database=":memory:")
    con.execute("CREATE TEMP TABLE candidates(family VARCHAR,trait_name VARCHAR,config_type VARCHAR,expected_unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES (?,?,?,?)",candidates)

    sql="""
    WITH base AS (
      SELECT
        trim(CAST(a.family AS VARCHAR)) AS family,
        trim(CAST(a.binomial AS VARCHAR)) AS species,
        trim(CAST(a.trait_name AS VARCHAR)) AS trait_name,
        c.config_type,
        c.expected_unit,
        trim(CAST(a.dataset_id AS VARCHAR)) || chr(31) || trim(CAST(a.observation_id AS VARCHAR)) AS record_key,
        trim(CAST(a.value AS VARCHAR)) AS value_text,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') AS unit
      FROM read_parquet(?) a
      JOIN candidates c
        ON trim(CAST(a.family AS VARCHAR))=c.family
       AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
      WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
        AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
        AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
        AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
        AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
    ),
    dedup AS (
      SELECT DISTINCT family,species,trait_name,config_type,expected_unit,record_key,value_text,unit
      FROM base
    ),
    num_rows AS (
      SELECT *,
        try_cast(value_text AS DOUBLE) AS value_num
      FROM dedup WHERE config_type='numeric'
    ),
    num_sys AS (
      SELECT family,trait_name,
        count(*) AS n_records,
        count(*) FILTER (WHERE value_num IS NULL OR NOT isfinite(value_num)) AS n_invalid_value,
        count(*) FILTER (WHERE unit='' OR expected_unit='' OR unit<>expected_unit) AS n_invalid_unit,
        count(DISTINCT unit) AS distinct_units,
        string_agg(DISTINCT unit,' | ' ORDER BY unit) AS unit_labels
      FROM num_rows GROUP BY family,trait_name
    ),
    num_state AS (
      SELECT family,trait_name,species,median(value_num) AS species_state
      FROM num_rows
      WHERE value_num IS NOT NULL AND isfinite(value_num)
      GROUP BY family,trait_name,species
    ),
    num_temporal AS (
      SELECT family,trait_name,
        count(*) AS resolvable_species,
        count(DISTINCT species_state) AS distinct_states
      FROM num_state GROUP BY family,trait_name
    ),
    cat_rows AS (
      SELECT * FROM dedup WHERE config_type='categorical'
    ),
    cat_sys AS (
      SELECT family,trait_name,
        count(*) AS n_records,
        0::BIGINT AS n_invalid_value,
        count(*) FILTER (WHERE expected_unit<>'' OR unit<>'') AS n_invalid_unit,
        count(DISTINCT unit) AS distinct_units,
        string_agg(DISTINCT unit,' | ' ORDER BY unit) AS unit_labels
      FROM cat_rows GROUP BY family,trait_name
    ),
    cat_counts AS (
      SELECT family,trait_name,species,value_text,count(*) AS n
      FROM cat_rows GROUP BY family,trait_name,species,value_text
    ),
    cat_ranked AS (
      SELECT *,max(n) OVER(PARTITION BY family,trait_name,species) AS max_n
      FROM cat_counts
    ),
    cat_modes AS (
      SELECT family,trait_name,species,
        count(*) FILTER (WHERE n=max_n) AS n_modal,
        min(value_text) FILTER (WHERE n=max_n) AS mode_internal
      FROM cat_ranked GROUP BY family,trait_name,species
    ),
    cat_temporal AS (
      SELECT family,trait_name,
        count(*) FILTER (WHERE n_modal=1) AS resolvable_species,
        count(DISTINCT mode_internal) FILTER (WHERE n_modal=1) AS distinct_states,
        count(*) FILTER (WHERE n_modal>1) AS tied_mode_species
      FROM cat_modes GROUP BY family,trait_name
    ),
    allsys AS (
      SELECT c.family,c.trait_name,c.config_type,c.expected_unit,
        coalesce(ns.n_records,cs.n_records,0) AS n_records,
        coalesce(ns.n_invalid_value,cs.n_invalid_value,0) AS n_invalid_value,
        coalesce(ns.n_invalid_unit,cs.n_invalid_unit,0) AS n_invalid_unit,
        coalesce(ns.distinct_units,cs.distinct_units,0) AS distinct_units,
        coalesce(ns.unit_labels,cs.unit_labels,'') AS unit_labels,
        coalesce(nt.resolvable_species,ct.resolvable_species,0) AS resolvable_species,
        coalesce(nt.distinct_states,ct.distinct_states,0) AS distinct_states,
        coalesce(ct.tied_mode_species,0) AS tied_mode_species
      FROM candidates c
      LEFT JOIN num_sys ns USING(family,trait_name)
      LEFT JOIN num_temporal nt USING(family,trait_name)
      LEFT JOIN cat_sys cs USING(family,trait_name)
      LEFT JOIN cat_temporal ct USING(family,trait_name)
    )
    SELECT * FROM allsys ORDER BY family,trait_name
    """
    cur=con.execute(sql,[str(a.parquet)])
    cols=[x[0] for x in cur.description]
    rows=[dict(zip(cols,r)) for r in cur.fetchall()]
    con.close()

    for r in rows:
        reasons=[]
        typ=r["config_type"]
        if int(r["n_invalid_value"])!=0: reasons.append("INVALID_VALUE")
        if int(r["n_invalid_unit"])!=0: reasons.append("UNIT_MISMATCH")
        if typ=="numeric" and int(r["distinct_units"])!=1: reasons.append("NUMERIC_UNIT_COUNT_NOT_ONE")
        if typ=="categorical" and str(r["expected_unit"])!="": reasons.append("CATEGORICAL_CONFIG_HAS_UNIT")
        if int(r["resolvable_species"])<20: reasons.append("RESOLVABLE_SPECIES_LT20")
        if int(r["distinct_states"])<2: reasons.append("DISTINCT_STATES_LT2")
        r["semantic_pass"]=not reasons
        r["hold_reason"]=";".join(reasons)

    fields=[
      "family","trait_name","config_type","expected_unit","n_records","n_invalid_value",
      "n_invalid_unit","distinct_units","unit_labels","resolvable_species","distinct_states",
      "tied_mode_species","semantic_pass","hold_reason"
    ]
    with a.table_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)

    passing=[r for r in rows if r["semantic_pass"]]
    families=sorted({r["family"] for r in passing})
    traits=sorted({r["trait_name"] for r in passing})
    gate=len(families)>=12 and len(traits)>=4
    from collections import Counter
    hc=Counter()
    for r in rows:
        if not r["semantic_pass"]:
            for q in filter(None,str(r["hold_reason"]).split(";")): hc[q]+=1
    out={
      "version":"v0.3",
      "status":"AUSTRAITS_MEMORY_SEMANTIC_PASS" if gate else "HOLD_AUSTRAITS_MEMORY_SEMANTIC",
      "outcome_blind":True,
      "austraits_memory_effects_opened":False,
      "n_structural_candidates":len(rows),
      "n_semantic_pass":len(passing),
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
