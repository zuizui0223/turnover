#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import duckdb,yaml

ROOT=Path(__file__).resolve().parents[2]
DESIGN=ROOT/"data"/"austraits_memory_temporal_support_v0_2.json"
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
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--table-out",type=Path,required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.table_out.parent.mkdir(parents=True,exist_ok=True)
    d=json.loads(DESIGN.read_text()); master=json.loads(MASTER.read_text())
    if sha256(a.parquet)!=master["source"]["parquet"]["sha256"]:
        raise RuntimeError("AusTraits parquet SHA256 mismatch")
    cfg=yaml.safe_load(a.traits_yml.read_text())
    traits=cfg["traits"]["elements"]
    cmap={}
    for name,meta in traits.items():
        t=str(meta.get("type","")).strip().lower()
        if t in {"numeric","categorical"}: cmap[name]=t
    if not cmap: raise RuntimeError("no numeric/categorical traits parsed from config")

    con=duckdb.connect(database=":memory:")
    cur=con.execute("""
      SELECT
        trim(CAST(family AS VARCHAR)) AS family,
        trim(CAST(trait_name AS VARCHAR)) AS trait_name,
        count(DISTINCT trim(CAST(binomial AS VARCHAR))) AS temporal_species
      FROM read_parquet(?)
      WHERE lower(trim(CAST(taxon_rank AS VARCHAR)))='species'
        AND family IS NOT NULL AND trim(CAST(family AS VARCHAR))<>''
        AND genus IS NOT NULL AND trim(CAST(genus AS VARCHAR))<>''
        AND binomial IS NOT NULL AND trim(CAST(binomial AS VARCHAR))<>''
        AND trait_name IS NOT NULL AND trim(CAST(trait_name AS VARCHAR))<>''
        AND value IS NOT NULL AND trim(CAST(value AS VARCHAR))<>''
      GROUP BY family,trait_name
      ORDER BY family,trait_name
    """,[str(a.parquet)])
    cols=[x[0] for x in cur.description]
    raw=[dict(zip(cols,r)) for r in cur.fetchall()]
    con.close()

    rows=[]
    unknown=set()
    for r in raw:
        tr=str(r["trait_name"])
        if tr not in cmap:
            unknown.add(tr); continue
        n=int(r["temporal_species"])
        rows.append({
          "family":str(r["family"]),
          "trait_name":tr,
          "config_type":cmap[tr],
          "temporal_species":n,
          "structural_pass":n>=20
        })

    fields=["family","trait_name","config_type","temporal_species","structural_pass"]
    with a.table_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)

    passing=[r for r in rows if r["structural_pass"]]
    families=sorted({r["family"] for r in passing})
    ptr=sorted({r["trait_name"] for r in passing})
    edges={(r["family"],r["trait_name"]) for r in passing}
    changed=True; iterations=0
    while changed:
        iterations+=1
        fd=defaultdict(int); td=defaultdict(int)
        for f,t in edges: fd[f]+=1; td[t]+=1
        badf={f for f,n in fd.items() if n<2}
        badt={t for t,n in td.items() if n<5}
        nxt={(f,t) for f,t in edges if f not in badf and t not in badt}
        changed=nxt!=edges; edges=nxt

    gate=len(families)>=12 and len(ptr)>=4
    out={
      "version":"v0.2",
      "status":"AUSTRAITS_MEMORY_TEMPORAL_SUPPORT_PASS" if gate else "HOLD_AUSTRAITS_MEMORY_TEMPORAL_SUPPORT",
      "outcome_blind":True,
      "austraits_memory_effects_opened":False,
      "source_version":"7.0.0",
      "n_config_traits_numeric_or_categorical":len(cmap),
      "n_unknown_parquet_trait_names":len(unknown),
      "unknown_parquet_trait_names":sorted(unknown),
      "n_family_trait_systems":len(rows),
      "n_structural_pass_systems":len(passing),
      "n_independent_families":len(families),
      "n_distinct_traits":len(ptr),
      "diagnostic_necessary_core":{
        "iterations":iterations,
        "systems":len(edges),
        "families":len({f for f,t in edges}),
        "traits":len({t for f,t in edges})
      },
      "minimum_families":12,
      "minimum_traits":4,
      "gate_pass":gate,
      "next_gate":d["next_gate_if_pass"] if gate else d["next_gate_if_hold"]
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
