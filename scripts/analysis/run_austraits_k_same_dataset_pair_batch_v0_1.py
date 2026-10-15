#!/usr/bin/env python3
"""Post-discovery source-composition robustness for K on original AusTraits.

For each frozen reproductive/vegetative pair with >=20 species possessing
positive source-native observations for BOTH traits in the SAME contributing
AusTraits dataset, calculate full-source medians and source-INTERSECTION
medians of each trait on EXACTLY the same species. Send ephemeral numerical
species states to native phylogeny R implementation. NEVER export source
dataset_id/species/observation IDs or raw measurement values.
"""
from __future__ import annotations
import argparse,csv,json,subprocess,tempfile
from pathlib import Path
from collections import defaultdict
import duckdb,pandas as pd,yaml

STATUS="AUSTRAITS_K_SAME_DATASET_PAIR_BATCH_COMPLETE"
FROZEN="POST_ORGAN_K_DISCOVERY_AND_SOURCE_SUPPORT_PRE_SAME_SOURCE_RESTRICTED_K_OUTCOME_FROZEN"
SOURCE_STATUS="AUSTRAITS_CROSS_TRAIT_COMMON_DATASET_SUPPORT_AUDITED"
K_SUPPORT="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"

def qualify(source,original,design):
    if design.get("status")!=FROZEN:
        raise ValueError("same-source K contrast rules were not frozen before calculation")
    if source.get("status")!=SOURCE_STATUS or source["cross_organ"]["n_pairs_with_at_least_20_same_dataset_species"]!=279:
        raise ValueError("changed original K-blind common dataset support")
    if original.get("status")!=K_SUPPORT or original.get("qualifying_family_trait_pairs")!=760:
        raise ValueError("not exact original K-blind 760 same-tip K eligibility")
    ref={(r["family"],r["trait_A"],r["trait_B"]):r
         for r in original["family_trait_pair_support"]
         if r["qualifies_20_common_species"]}
    selected=[]
    for row in source["cross_organ_family_trait_pair_support"]:
        if not row["qualifies_same_dataset_20_species"]:continue
        key=(row["family"],row["trait_A"],row["trait_B"])
        if key not in ref:
            raise ValueError("unqualified pair not in original K-blind source graph")
        prior=ref[key]
        if row["n_original_shared_species"]!=prior["n_common_species_same_genus"]:
            raise ValueError("original K-blind shared positive species support changed")
        z={**row,
            "system_A":prior["system_A"],"system_B":prior["system_B"],
            "n_original_A":prior["n_original_A"],"n_original_B":prior["n_original_B"]}
        selected.append(z)
    if len(selected)!=279 or len({r["family"] for r in selected})!=32:
        raise ValueError("original 279 pre-K selected common source family-pairs changed")
    if len({(r["family"],r["trait_A"],r["trait_B"]) for r in selected})!=279:
        raise ValueError("duplicate original common-source pair")
    return sorted(selected,key=lambda r:(r["family"],r["trait_A"],r["trait_B"]))

def validate_batch(batch,source,orig,design):
    eligible={(r["family"],r["trait_A"],r["trait_B"]):r
              for r in qualify(source,orig,design)}
    if not batch:raise ValueError("empty source-matched K batch")
    keys=set()
    for row in batch:
        key=(row["family"],row["trait_A"],row["trait_B"])
        if key in keys or key not in eligible:
            raise ValueError("duplicate or unknown same-source family-pair")
        keys.add(key)
        if row!=eligible[key]:
            raise ValueError("source eligibility or original taxon support changed")
    return True

def source_medians(parquet,units,selected):
    cfg=yaml.safe_load(Path(units).read_text())["traits"]["elements"]
    systems={}
    for r in selected:
        for suff in ("A","B"):
            sid=r["system_"+suff]
            meta={"family":r["family"],"trait":r["trait_"+suff],"n":int(r["n_original_"+suff])}
            if sid in systems and systems[sid]!=meta:
                raise ValueError("same original K system has inconsistent source eligibility")
            systems[sid]=meta
    cand=[]
    for sid,z in systems.items():
        u=cfg[z["trait"]].get("units")
        if not u or not str(u).strip():
            raise ValueError("original unit not identified for "+z["trait"])
        cand.append((sid,z["family"],z["trait"],str(u).strip()))
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE cand (sid VARCHAR,family VARCHAR,trait VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO cand VALUES(?,?,?,?)",cand)
    con.execute("CREATE TEMP TABLE pairs (family VARCHAR,a VARCHAR,b VARCHAR,sa VARCHAR,sb VARCHAR)")
    con.executemany("INSERT INTO pairs VALUES(?,?,?,?,?)",
       [(z["family"],z["trait_A"],z["trait_B"],z["system_A"],z["system_B"]) for z in selected])
    try:
        con.execute(r"""
        CREATE TEMP TABLE dedup AS
        WITH base AS (
           SELECT c.sid,c.family,c.trait,
              trim(CAST(v.genus AS VARCHAR)) genus,
              trim(CAST(v.binomial AS VARCHAR)) species,
              trim(CAST(v.dataset_id AS VARCHAR)) dataset_id,
              trim(CAST(v.observation_id AS VARCHAR)) observation_id,
              try_cast(trim(CAST(v.value AS VARCHAR)) AS DOUBLE) val,
              c.unit expected_unit,
              coalesce(trim(CAST(v.unit AS VARCHAR)),'') native_unit
           FROM read_parquet(?) v JOIN cand c
            ON trim(CAST(v.family AS VARCHAR))=c.family
           AND trim(CAST(v.trait_name AS VARCHAR))=c.trait
           WHERE lower(trim(CAST(v.taxon_rank AS VARCHAR)))='species'
             AND v.genus IS NOT NULL AND trim(CAST(v.genus AS VARCHAR))<>''
             AND v.binomial IS NOT NULL AND trim(CAST(v.binomial AS VARCHAR))<>''
             AND v.dataset_id IS NOT NULL AND trim(CAST(v.dataset_id AS VARCHAR))<>''
             AND v.observation_id IS NOT NULL AND trim(CAST(v.observation_id AS VARCHAR))<>''
             AND v.value IS NOT NULL AND trim(CAST(v.value AS VARCHAR))<>''
        )
        SELECT DISTINCT sid,family,trait,genus,species,dataset_id,observation_id,val
        FROM base WHERE val IS NOT NULL AND isfinite(val)
           AND expected_unit<>'' AND native_unit=expected_unit
        """,[str(parquet)])
        con.execute("""
        CREATE TEMP TABLE native_median AS
        SELECT sid,family,trait,species,min(genus) AS genus,
               median(val) full_state
        FROM dedup GROUP BY sid,family,trait,species
        HAVING count(DISTINCT genus)=1 AND median(val)>0
        """)
        sizes=con.execute("SELECT sid,count(*) FROM native_median GROUP BY sid").fetchall()
        if {x[0]:int(x[1]) for x in sizes}!={sid:int(z["n"]) for sid,z in systems.items()}:
            raise ValueError("native source median K eligible original species counts changed")
        con.execute("""
          CREATE TEMP TABLE positive_source_datasets AS
          SELECT DISTINCT d.sid,d.species,d.genus,d.dataset_id
          FROM dedup d JOIN native_median m
           ON d.sid=m.sid AND d.species=m.species AND d.genus=m.genus
          WHERE d.val>0
        """)
        con.execute("""
          CREATE TEMP TABLE shared_datasets AS
          SELECT p.family,p.a,p.b,p.sa,p.sb,aa.species,aa.genus,
                 da.dataset_id
          FROM pairs p
          JOIN native_median aa ON aa.sid=p.sa
          JOIN native_median bb
            ON bb.sid=p.sb AND aa.species=bb.species
               AND aa.genus=bb.genus
          JOIN positive_source_datasets da ON da.sid=p.sa
           AND da.species=aa.species AND da.genus=aa.genus
          JOIN positive_source_datasets db ON db.sid=p.sb
           AND db.species=aa.species AND db.genus=aa.genus
           AND db.dataset_id=da.dataset_id
        """)
        con.execute("""
          CREATE TEMP TABLE srcA AS
          SELECT s.family,s.a,s.b,s.species,s.genus,
                 median(d.val) source_state_A
          FROM shared_datasets s JOIN dedup d
           ON d.sid=s.sa AND d.species=s.species
           AND d.genus=s.genus AND d.dataset_id=s.dataset_id
          GROUP BY s.family,s.a,s.b,s.species,s.genus
        """)
        con.execute("""
          CREATE TEMP TABLE srcB AS
          SELECT s.family,s.a,s.b,s.species,s.genus,
                 median(d.val) source_state_B
          FROM shared_datasets s JOIN dedup d
           ON d.sid=s.sb AND d.species=s.species
           AND d.genus=s.genus AND d.dataset_id=s.dataset_id
          GROUP BY s.family,s.a,s.b,s.species,s.genus
        """)
        result=con.execute("""
           SELECT s.family,s.a,s.b,s.sa,s.sb,
                  s.species,s.genus,
                  mA.full_state,mB.full_state,
                  a.source_state_A,b.source_state_B
           FROM srcA a JOIN srcB b USING(family,a,b,species,genus)
           JOIN shared_datasets s USING(family,a,b,species,genus)
           JOIN native_median mA
                ON mA.sid=s.sa AND mA.species=s.species AND mA.genus=s.genus
           JOIN native_median mB
                ON mB.sid=s.sb AND mB.species=s.species AND mB.genus=s.genus
           GROUP BY s.family,s.a,s.b,s.sa,s.sb,s.species,s.genus,
                    mA.full_state,mB.full_state,a.source_state_A,b.source_state_B
           ORDER BY s.family,s.a,s.b,s.species
        """).fetchall()
        # Dataset joins can repeat one species if it has more than one
        # shared original dataset. The final group removes that duplication.
        return result
    finally:
        con.close()

def write_ephemeral_states(rows,batch,tempdir):
    groups=defaultdict(list)
    for fam,a,b,sa,sb,species,genus,fullA,fullB,srcA,srcB in rows:
        groups[(str(fam),str(a),str(b))].append(
          (str(sa),str(sb),str(species),str(genus),
           float(fullA),float(fullB),float(srcA),float(srcB)))
    manifest=[]
    for idx,z in enumerate(batch,1):
        key=(z["family"],z["trait_A"],z["trait_B"])
        entries=groups.get(key,[])
        if len(entries)!=int(z["n_same_AusTraits_dataset_species"]):
            raise ValueError("common AusTraits source identity count differs from pre-outcome support on "+str(key))
        good=[v for v in entries if v[4]>0 and v[5]>0 and v[6]>0 and v[7]>0]
        if any((a,b)!=(z["system_A"],z["system_B"]) for a,b,*rest in entries):
            raise ValueError("source median pairs differ from frozen K-blind original source IDs")
        record={
          "pair_id":f"Q{idx:03d}","family":z["family"],
          "trait_A":z["trait_A"],"trait_B":z["trait_B"],
          "system_A":z["system_A"],"system_B":z["system_B"],
          "n_source_positive_dataset_common":len(entries),
          "n_pair_native_positive_source_median":len(good),
          "n_lost_after_source_median":len(entries)-len(good),
          "status":"READY" if len(good)>=20 else "HOLD_SOURCE_NATIVE_MEDIANS_BELOW_20_AFTER_SAME_DATASET_RESTRICTION"
        }
        if record["status"]=="READY":
            f=Path(tempdir)/f"Q{idx:03d}.csv"
            with f.open("w",newline="",encoding="utf-8") as fh:
                writer=csv.writer(fh)
                writer.writerow(("family","genus","species","all_A","all_B","source_A","source_B"))
                for sa,sb,species,genus,fa,fb,a,b in good:
                    writer.writerow((z["family"],genus,species,fa,fb,a,b))
            record["state_table"]=str(f)
        manifest.append(record)
    return manifest

def validate_R_results(manifest,result):
    if result.get("status")!=STATUS or len(result.get("pairs",[]))!=len(manifest):
        raise ValueError("incomplete/source-changed K batch")
    inputs={v["pair_id"]:v for v in manifest}
    if len(inputs)!=len(manifest):raise ValueError("duplicate source-pair IDs")
    for out in result["pairs"]:
        pair=inputs.get(out["pair_id"])
        if not pair or (out["family"],out["trait_A"],out["trait_B"])!=(
            pair["family"],pair["trait_A"],pair["trait_B"]):
            raise ValueError("not original source candidate pair identity")
        if out["n_same_source_positive_species"]!=pair["n_pair_native_positive_source_median"]:
            raise ValueError("changed original same-dataset species count")
        for axis in ("S3","prune_only"):
            vals=out["axes"][axis]
            if vals["status"]=="PASS":
                if vals["n_tips"]<20 or vals["n_tips"]>pair["n_pair_native_positive_source_median"]:
                    raise ValueError("under-supported source K PASS")
                for name in ("K_full_A","K_full_B","K_source_A","K_source_B",
                             "delta_full","delta_source","delta_source_measurements"):
                    import math
                    if not math.isfinite(float(vals[name])):raise ValueError("nonfinite source-contrast K")
                import math
                if not math.isclose(math.log(vals["K_full_A"]/vals["K_full_B"]),vals["delta_full"],abs_tol=2e-9):
                    raise ValueError("full-source on paired tips K sign mismatch")
                if not math.isclose(math.log(vals["K_source_A"]/vals["K_source_B"]),vals["delta_source"],abs_tol=2e-9):
                    raise ValueError("source-only on paired tips K sign mismatch")
                if not math.isclose(vals["delta_source"]-vals["delta_full"],vals["delta_source_measurements"],abs_tol=2e-9):
                    raise ValueError("measurement-only same-tip logK contrast shift mismatch")
            elif not str(vals["status"]).startswith("HOLD_"):
                raise ValueError("unrecognized source-only K tree hold")
    return True

def main():
    p=argparse.ArgumentParser()
    for arg in ("batch-json","source-support","original-pair-support",
                "parquet","traits-yml","design","r-script","out"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    source=json.loads(a.__dict__["source_support"].read_text())
    original=json.loads(a.__dict__["original_pair_support"].read_text())
    design=json.loads(a.design.read_text())
    batch=json.loads(a.__dict__["batch_json"].read_text())
    validate_batch(batch,source,original,design)
    rr=source_medians(a.parquet,a.__dict__["traits_yml"],batch)
    with tempfile.TemporaryDirectory(prefix="aust_K_common_dataset_") as tmp:
        manifest=write_ephemeral_states(rr,batch,tmp)
        j=Path(tmp)/"manifest.json";j.write_text(json.dumps(manifest,indent=2))
        dest=Path(tmp)/"result.json"
        subprocess.run(["Rscript",str(a.__dict__["r_script"]),
                        "--manifest",str(j),"--out",str(dest)],check=True)
        result=json.loads(dest.read_text())
        validate_R_results(manifest,result)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,"pair_count":len(manifest),
        "S3_pass":sum(x["axes"]["S3"]["status"]=="PASS" for x in result["pairs"]),
        "prune_pass":sum(x["axes"]["prune_only"]["status"]=="PASS" for x in result["pairs"])}))

if __name__=="__main__":main()
