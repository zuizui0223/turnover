#!/usr/bin/env python3
"""Build fixed AusTraits K-eligible shared-species two-trait state pairs.

All input species values and species IDs are ephemeral GitHub runner files.
A K effect reference is read ONLY after the independently K-blind overlap
cohort has been validated; it is never used to select a family/trait pair.
"""
from __future__ import annotations
import argparse,csv,json,subprocess,tempfile
from collections import defaultdict
from pathlib import Path
import duckdb,pandas as pd,yaml

STATUS="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
DESIGN="POST_EMPIRICAL_K_AND_SOURCE_DIAGNOSTICS_PRE_SHARED_TAXON_OVERLAP_RESULTS_FROZEN"

def validate_batch(batch,support,design):
    if design.get("status")!=DESIGN:
        raise ValueError("same-species pair design not frozen")
    if support.get("status")!="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED":
        raise ValueError("missing K-blind source overlap results")
    if (support.get("original_graph")!={"systems":254,"families":42,"traits":13}
        or support.get("named_graph")!={"systems":249,"families":42,"traits":12}
        or support.get("qualifying_family_trait_pairs")!=760):
        raise ValueError("changed original eligible same-species pairs")
    valid={(z["family"],z["trait_A"],z["trait_B"]):z for z in support["family_trait_pair_support"]
           if z["qualifies_20_common_species"]}
    ids=set()
    for z in batch:
        key=(z["family"],z["trait_A"],z["trait_B"])
        if key not in valid:raise ValueError("unqualified or altered named trait pair")
        if key in ids:raise ValueError("duplicate pair in same batch")
        ids.add(key)
        ref=valid[key]
        for name in ("system_A","system_B","n_common_species_same_genus","n_original_A","n_original_B"):
            if z.get(name)!=ref[name]:raise ValueError("pair support identity changed: "+name)
    if not batch:raise ValueError("empty same-species K batch")
    return valid

def source_states(parquet,systems,unit_config):
    cfg=yaml.safe_load(Path(unit_config).read_text())["traits"]["elements"]
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE cand (system_id VARCHAR,family_name VARCHAR,trait_name VARCHAR,expected_unit VARCHAR)")
    cands=[]
    for sid,meta in systems.items():
        u=cfg[meta["trait"]].get("units")
        if not u or not str(u).strip():raise ValueError("missing original native unit")
        cands.append((sid,meta["family"],meta["trait"],str(u).strip()))
    con.executemany("INSERT INTO cand VALUES (?,?,?,?)",cands)
    sql=r"""
    WITH base AS (
      SELECT c.system_id,c.family_name,c.trait_name,
        trim(CAST(a.genus AS VARCHAR)) AS genus,
        trim(CAST(a.binomial AS VARCHAR)) AS species,
        trim(CAST(a.dataset_id AS VARCHAR)) AS dataset_id,
        trim(CAST(a.observation_id AS VARCHAR)) AS observation_id,
        try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) AS value_num,
        c.expected_unit,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') AS source_unit
      FROM read_parquet(?) a JOIN cand c
        ON trim(CAST(a.family AS VARCHAR))=c.family_name
       AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
      WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
        AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
        AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
        AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
        AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
        AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
    ),dedup AS (
      SELECT DISTINCT system_id,family_name,trait_name,genus,species,
             dataset_id,observation_id,value_num
      FROM base WHERE value_num IS NOT NULL AND isfinite(value_num)
         AND expected_unit<>'' AND source_unit=expected_unit
    )
    SELECT system_id,family_name,trait_name,species,min(genus) AS genus,
           median(value_num) AS state_num
    FROM dedup GROUP BY system_id,family_name,trait_name,species
    HAVING count(DISTINCT genus)=1 AND median(value_num)>0
    ORDER BY system_id,species
    """
    try:rows=con.execute(sql,[str(parquet)]).fetchall()
    finally:con.close()
    by=defaultdict(dict)
    for sid,fam,trait,species,genus,value in rows:
        by[str(sid)][str(species)]=(str(fam),str(trait),str(genus),float(value))
    for sid,meta in systems.items():
        if len(by[sid])!=meta["n_original"]:
            raise ValueError("changed original K-eligible species support in "+sid)
    return by

def prepare_local(batch,support,K,states,dir_):
    Kidx={str(r.system_id):r for r in K.itertuples(index=False)}
    manifest=[]
    for num,item in enumerate(batch,1):
        a,b=item["system_A"],item["system_B"]
        A,B=states[a],states[b]
        matched=[]
        genus_conflicts=0
        for species in sorted(A.keys()&B.keys()):
            va,vb=A[species],B[species]
            if va[2]!=vb[2]:
                genus_conflicts+=1
                continue
            if va[:2]!=(item["family"],item["trait_A"]) or vb[:2]!=(item["family"],item["trait_B"]):
                raise ValueError("original shared binomial family/trait mismatched")
            matched.append((item["family"],va[2],species,va[3],vb[3]))
        if len(matched)!=item["n_common_species_same_genus"] or genus_conflicts!=item["n_common_binomial_conflicting_genus"]:
            raise ValueError("shared species/discordant genus count differs from K-blind support audit")
        if len(matched)<20:raise ValueError("qualified pair lacks 20 shared species")
        rowA,rowB=Kidx.get(a),Kidx.get(b)
        if rowA is None or rowB is None:
            raise ValueError("missing original archived K reference")
        if (rowA.family,rowA.trait_name,rowB.family,rowB.trait_name)!=(
            item["family"],item["trait_A"],item["family"],item["trait_B"]):
            raise ValueError("original K reference pair identity corrupted")
        pid=f"P{num:03d}"
        statefile=Path(dir_)/(pid+".csv")
        with statefile.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(("family","genus","species","state_A","state_B"))
            w.writerows(matched)
        manifest.append({
           "pair_id":pid,"family":item["family"],
           "trait_A":item["trait_A"],"trait_B":item["trait_B"],
           "system_A":a,"system_B":b,"n_shared_species":len(matched),
           "state_file":str(statefile),
           "original_S3_K_A":float(rowA.S3_K),
           "original_S3_K_B":float(rowB.S3_K),
           "original_prune_K_A":float(rowA.prune_K),
           "original_prune_K_B":float(rowB.prune_K)})
    return manifest

def validate_batch_output(result,manifest):
    if result.get("status")!=STATUS:raise ValueError("invalid output status")
    pairs=result.get("pairs",[])
    if len(pairs)!=len(manifest):
        raise ValueError("incomplete paired K evaluation")
    ids={i["pair_id"] for i in manifest}
    if {r["pair_id"] for r in pairs}!=ids:
        raise ValueError("paired K outcomes not identical to fixed eligible graph")
    for r in pairs:
        if r["trait_A"]==r["trait_B"]:
            raise ValueError("same-trait contrast invalid")
        for axis in ("S3","prune_only"):
            d=r["axes"][axis]
            if d["status"]=="PASS":
                if d["n_tips"]<20:raise ValueError("under-supported K PASS")
                for v in ("K_A","K_B","delta_shared_logK","delta_original_logK","delta_support_shift"):
                    import math
                    if not math.isfinite(float(d[v])):raise ValueError("nonfinite same-tree K contrast")
            elif not str(d["status"]).startswith("HOLD_"):
                raise ValueError("invalid same-tree K support outcome")
    return True

def main():
    p=argparse.ArgumentParser()
    for nm in ("batch-json","support","parquet","traits-yml","observed-K","design","r-script","out"):
        p.add_argument("--"+nm,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    support=json.loads(a.support.read_text())
    batch=json.loads(a.__dict__["batch_json"].read_text())
    validate_batch(batch,support,design)
    k=pd.read_csv(a.__dict__["observed_K"])
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(254,42,13):
        raise ValueError("reference original K graph changed")
    systems={}
    for x in batch:
        for suffix in ("A","B"):
            sid=x["system_"+suffix]
            meta={"family":x["family"],"trait":x["trait_"+suffix],
                  "n_original":int(x["n_original_"+suffix])}
            if sid in systems and systems[sid]!=meta:
                raise ValueError("original same-trait system support inconsistent")
            systems[sid]=meta
    states=source_states(a.parquet,systems,a.__dict__["traits_yml"])
    with tempfile.TemporaryDirectory(prefix="aust_K_common_species_") as td:
        manifest=prepare_local(batch,support,k,states,td)
        mfile=Path(td)/"manifest.json"
        mfile.write_text(json.dumps(manifest,indent=2))
        output=Path(td)/"paired_result.json"
        subprocess.run([
            "Rscript",str(a.__dict__["r_script"]),
            "--manifest",str(mfile),"--out",str(output)
        ],check=True)
        result=json.loads(output.read_text())
        validate_batch_output(result,manifest)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"n_pairs":len(manifest),
                      "S3_pass":sum(z["axes"]["S3"]["status"]=="PASS" for z in result["pairs"]),
                      "prune_pass":sum(z["axes"]["prune_only"]["status"]=="PASS" for z in result["pairs"])}))

if __name__=="__main__":main()
