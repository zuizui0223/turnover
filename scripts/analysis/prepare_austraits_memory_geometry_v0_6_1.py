#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter,defaultdict,deque
from pathlib import Path
import duckdb,yaml

def truth(v)->bool:
    return str(v).strip().lower() in {"true","t","1"}

def norm_one(x:str)->str:
    s=str(x).strip()
    return s[:1].upper()+s[1:] if s else s

def norm_species(x:str)->str:
    s="_".join(str(x).strip().split())
    return norm_one(s)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--parquet",type=Path,required=True)
    ap.add_argument("--traits-yml",type=Path,required=True)
    ap.add_argument("--crosswalk",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--systems-out",type=Path,required=True)
    ap.add_argument("--groups-out",type=Path,required=True)
    a=ap.parse_args()
    for p in [a.out,a.systems_out,a.groups_out]: p.parent.mkdir(parents=True,exist_ok=True)

    cw=list(csv.DictReader(a.crosswalk.open(newline="",encoding="utf-8")))
    passed=[r for r in cw if truth(r["crosswalk_pass"])]
    edge_row={(r["family"],r["trait_name"]):r for r in passed}
    edges=set(edge_row)
    iterations=0
    while True:
        iterations+=1
        fd=Counter(f for f,t in edges); td=Counter(t for f,t in edges)
        nxt={(f,t) for f,t in edges if fd[f]>=2 and td[t]>=5}
        if nxt==edges: break
        edges=nxt
    core=[edge_row[k] for k in sorted(edges)]
    if len(core)!=1463 or len({r["family"] for r in core})!=64 or len({r["trait_name"] for r in core})!=73:
        raise RuntimeError("pre-informativeness core differs from frozen counts")

    # Connectedness check.
    adj=defaultdict(set)
    for r in core:
        f=("F",r["family"]); t=("T",r["trait_name"])
        adj[f].add(t); adj[t].add(f)
    start=next(iter(adj)); seen={start}; q=deque([start])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in seen: seen.add(v); q.append(v)
    if len(seen)!=len(adj):
        raise RuntimeError("frozen necessary core is not connected")

    cfg=yaml.safe_load(a.traits_yml.read_text())["traits"]["elements"]
    unit={}
    typ={}
    for name,m in cfg.items():
        t=str(m.get("type","")).strip().lower()
        if t not in {"numeric","categorical"}: continue
        typ[name]=t
        u=m.get("units")
        unit[name]="" if u is None else str(u).strip()

    candidates=[]
    for r in core:
        tr=r["trait_name"]
        if tr not in typ: raise RuntimeError(f"missing config trait {tr}")
        if typ[tr]!=r["config_type"]: raise RuntimeError(f"config type mismatch {tr}")
        candidates.append((r["family"],tr,r["config_type"],unit[tr]))

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
      SELECT family,trait_name,config_type,species,min(genus) AS genus
      FROM dedup
      WHERE config_type='numeric'
        AND try_cast(value_text AS DOUBLE) IS NOT NULL
        AND isfinite(try_cast(value_text AS DOUBLE))
        AND expected_unit<>'' AND unit=expected_unit
      GROUP BY family,trait_name,config_type,species
    ),
    cat_counts AS (
      SELECT family,trait_name,config_type,species,value_text,count(*) AS n
      FROM dedup
      WHERE config_type='categorical' AND expected_unit='' AND unit=''
      GROUP BY family,trait_name,config_type,species,value_text
    ),
    cat_ranked AS (
      SELECT *,max(n) OVER(PARTITION BY family,trait_name,species) AS max_n FROM cat_counts
    ),
    cat_species AS (
      SELECT family,trait_name,config_type,species,
        count(*) FILTER(WHERE n=max_n) AS n_modal
      FROM cat_ranked GROUP BY family,trait_name,config_type,species
    ),
    cat_genus AS (
      SELECT family,trait_name,config_type,species,min(genus) AS genus
      FROM dedup
      WHERE config_type='categorical' AND expected_unit='' AND unit=''
      GROUP BY family,trait_name,config_type,species
    ),
    cat_unique AS (
      SELECT s.family,s.trait_name,s.config_type,s.species,g.genus
      FROM cat_species s
      JOIN cat_genus g USING(family,trait_name,config_type,species)
      WHERE s.n_modal=1
    )
    SELECT * FROM num_species
    UNION ALL
    SELECT family,trait_name,config_type,species,genus FROM cat_unique
    ORDER BY family,trait_name,species,genus
    """
    cur=con.execute(sql,[str(a.parquet)])
    cols=[x[0] for x in cur.description]
    species_rows=[dict(zip(cols,r)) for r in cur.fetchall()]
    con.close()

    by=defaultdict(list)
    for r in species_rows:
        by[(r["family"],r["trait_name"])].append(r)

    sysrows=[]
    for r in core:
        key=(r["family"],r["trait_name"])
        ss=by.get(key,[])
        expected_n=int(r["n_input_species"])
        if len(ss)!=expected_n:
            raise RuntimeError(f"species count mismatch {key}: {len(ss)} != {expected_n}")
        lines=[]
        for z in ss:
            lines.append("\t".join([norm_one(z["family"]),norm_one(z["genus"]),norm_species(z["species"])]))
        lines.sort()
        payload=r["config_type"]+"\n"+"\n".join(lines)
        gh=hashlib.sha256(payload.encode("utf-8")).hexdigest()
        sysrows.append({
          "family":r["family"],"trait_name":r["trait_name"],"config_type":r["config_type"],
          "n_input_species":expected_n,"n_prune":int(r["n_prune"]),"n_bind":int(r["n_bind"]),
          "geometry_hash":gh
        })

    groups=defaultdict(list)
    for r in sysrows: groups[r["geometry_hash"]].append(r)
    grouprows=[]
    for gh,members in groups.items():
        members=sorted(members,key=lambda r:(r["family"],r["trait_name"]))
        canon=members[0]
        # Identical species geometry must imply identical crosswalk counts/class.
        for z in members:
            if z["config_type"]!=canon["config_type"] or z["n_input_species"]!=canon["n_input_species"] or z["n_prune"]!=canon["n_prune"] or z["n_bind"]!=canon["n_bind"]:
                raise RuntimeError(f"nonidentical crosswalk metadata inside geometry group {gh}")
        grouprows.append({
          "geometry_hash":gh,"config_type":canon["config_type"],"group_size":len(members),
          "canonical_family":canon["family"],"canonical_trait_name":canon["trait_name"],
          "n_input_species":canon["n_input_species"],"n_prune":canon["n_prune"],"n_bind":canon["n_bind"]
        })
        for z in members:
            z["canonical_family"]=canon["family"]
            z["canonical_trait_name"]=canon["trait_name"]
            z["geometry_group_size"]=len(members)
            z["is_canonical"]=(z is canon)

    grouprows.sort(key=lambda r:(-r["group_size"],r["canonical_family"],r["canonical_trait_name"]))
    sysrows.sort(key=lambda r:(r["family"],r["trait_name"]))
    sf=["family","trait_name","config_type","n_input_species","n_prune","n_bind","geometry_hash","canonical_family","canonical_trait_name","geometry_group_size","is_canonical"]
    with a.systems_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=sf); w.writeheader(); w.writerows(sysrows)
    gf=["geometry_hash","config_type","group_size","canonical_family","canonical_trait_name","n_input_species","n_prune","n_bind"]
    with a.groups_out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=gf); w.writeheader(); w.writerows(grouprows)

    sizes=[r["group_size"] for r in grouprows]
    out={
      "version":"v0.6.1",
      "status":"AUSTRAITS_MEMORY_GEOMETRY_PREP_PASS",
      "outcome_blind":True,
      "austraits_memory_effects_opened":False,
      "n_candidate_systems":len(sysrows),
      "n_unique_geometries":len(grouprows),
      "n_duplicate_systems_saved":len(sysrows)-len(grouprows),
      "n_geometry_groups_gt1":sum(s>1 for s in sizes),
      "max_geometry_group_size":max(sizes),
      "config_type_system_counts":dict(Counter(r["config_type"] for r in sysrows)),
      "config_type_geometry_counts":dict(Counter(r["config_type"] for r in grouprows)),
      "core_families":len({r["family"] for r in sysrows}),
      "core_traits":len({r["trait_name"] for r in sysrows}),
      "connected":True,
      "canonicalization":"data/austraits_memory_geometry_dedup_v0_6_1.json",
      "next_gate":"Run inherited temporal informativeness once per unique geometry, prune-only first."
    }
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
