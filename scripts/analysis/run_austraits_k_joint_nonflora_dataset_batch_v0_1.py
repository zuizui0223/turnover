#!/usr/bin/env python3
"""Final within-AusTraits post-discovery K robustness: exclude FIVE online flora
DatasetIDs, THEN compare reproductive/vegetative native K on the same species,
same native plant tree and strictly common REMAINING DatasetIDs.

The 142 eligible family×pair entities were defined in the original 760 K-blind
source overlap graph before THIS joint-source K result was opened. This never
certifies independent original specimens or cross-study replication. Raw
species, individual measurements and study identifiers remain runner-local.
"""
from __future__ import annotations
import argparse,csv,json,subprocess,tempfile
from pathlib import Path
from collections import defaultdict
import duckdb,pandas as pd,yaml

STATUS="AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_BATCH_COMPLETE"
SUPPORT="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_SOURCE_SUPPORT_AUDITED"
ORIGINAL="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"
FROZEN="POST_AUSTRAITS_K_DISCOVERY_AND_FIVE_FLORA_K_PRE_JOINT_SOURCE_K_RESULTS_FROZEN"
R_OUTPUT="AUSTRAITS_K_SAME_DATASET_PAIR_BATCH_COMPLETE"
EXCLUDED=("ABRS_2023","NHNSW_2023","RBGV_2023","NTH_2023","SAH_2023")

def cohort(support,original,design):
    if design.get("status")!=FROZEN or tuple(design.get("excluded_original_AusTraits_DatasetIDs",[]))!=EXCLUDED:
        raise ValueError("original five electronic flora exclusion and K freeze changed")
    if support.get("status")!=SUPPORT or support["subsets"]["cross_organ"]["qualifying_20_same_nonflora_dataset_pairs"]!=142:
        raise ValueError("nonflora source-only 142-pair cohort not fixed")
    if original.get("status")!=ORIGINAL or original.get("qualifying_family_trait_pairs")!=760:
        raise ValueError("original 760 pair K-blind graph is not pinned")
    refs={(r["family"],r["trait_A"],r["trait_B"]):r for r in original["family_trait_pair_support"]
          if r["qualifies_20_common_species"]}
    selection=[]
    for r in support["cross_organ_same_nonflora_dataset_supported_family_trait_pairs"]:
        k=(r["family"],r["trait_A"],r["trait_B"])
        old=refs.get(k)
        if old is None or (r["system_A"],r["system_B"])!=(old["system_A"],old["system_B"]):
            raise ValueError("selected pair has no original K-blind source/taxon support")
        if r["n_original_shared_positive_species"]!=old["n_common_species_same_genus"]:
            raise ValueError("original K-blind original species overlap changed")
        if not 20<=r["n_same_nonflora_dataset_shared_positive_species"]<=r["n_nonflora_positive_median_shared_species"]:
            raise ValueError("selected source pair below fixed 20-species nonflora gate")
        selection.append({**r,
           "n_original_A":old["n_original_A"],"n_original_B":old["n_original_B"],
           "n_same_AusTraits_dataset_species":r["n_same_nonflora_dataset_shared_positive_species"]})
    if len(selection)!=142 or len({x["family"] for x in selection})!=24:
        raise ValueError("not 142 pairs across 24 families")
    keys={(x["family"],x["trait_A"],x["trait_B"]) for x in selection}
    if len(keys)!=142:raise ValueError("duplicate K-blind family×pair")
    return sorted(selection,key=lambda x:(x["family"],x["trait_A"],x["trait_B"]))

def batch_guard(batch,support,original,design):
    allowed={(x["family"],x["trait_A"],x["trait_B"]):x for x in cohort(support,original,design)}
    if not batch:raise ValueError("no joint nonflora source pairs")
    seen=set()
    for z in batch:
        k=(z["family"],z["trait_A"],z["trait_B"])
        if k not in allowed or k in seen or z!=allowed[k]:
            raise ValueError("joint source support candidate altered or repeated")
        seen.add(k)
    return True

def source_medians(parquet,units,selected):
    cfg=yaml.safe_load(Path(units).read_text())["traits"]["elements"]
    systems={}
    for r in selected:
        for arm in ("A","B"):
            sid=r["system_"+arm]
            expected={"family":r["family"],"trait":r["trait_"+arm],
                      "n_original":int(r["n_original_"+arm])}
            if sid in systems and systems[sid]!=expected:
                raise ValueError("original family system has inconsistent species support")
            systems[sid]=expected
    candidates=[]
    for sid,s in systems.items():
        unit=cfg[s["trait"]].get("units")
        if unit is None or not str(unit).strip():
            raise ValueError("original trait/native units missing")
        candidates.append((sid,s["family"],s["trait"],str(unit).strip()))
    c=duckdb.connect(":memory:")
    c.execute("CREATE TEMP TABLE candidates(sid VARCHAR,family VARCHAR,trait VARCHAR,unit VARCHAR)")
    c.executemany("INSERT INTO candidates VALUES (?,?,?,?)",candidates)
    c.execute("CREATE TEMP TABLE target(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR,system_A VARCHAR,system_B VARCHAR)")
    c.executemany("INSERT INTO target VALUES (?,?,?,?,?)",[
      (z["family"],z["trait_A"],z["trait_B"],z["system_A"],z["system_B"]) for z in selected])
    c.execute("CREATE TEMP TABLE excluded(ds VARCHAR)")
    c.executemany("INSERT INTO excluded VALUES (?)",[(z,) for z in EXCLUDED])
    try:
        c.execute(r"""
          CREATE TEMP TABLE allrecords AS WITH r AS (
              SELECT cand.sid,cand.family,cand.trait,
                 trim(CAST(o.genus AS VARCHAR)) genus,
                 trim(CAST(o.binomial AS VARCHAR)) species,
                 trim(CAST(o.dataset_id AS VARCHAR)) ds,
                 trim(CAST(o.observation_id AS VARCHAR)) obs,
                 try_cast(trim(CAST(o.value AS VARCHAR)) AS DOUBLE) val,
                 cand.unit expected_unit,coalesce(trim(CAST(o.unit AS VARCHAR)),'') unit
              FROM read_parquet(?) o JOIN candidates cand
                ON trim(CAST(o.family AS VARCHAR))=cand.family
               AND trim(CAST(o.trait_name AS VARCHAR))=cand.trait
              WHERE lower(trim(CAST(o.taxon_rank AS VARCHAR)))='species'
                AND o.genus IS NOT NULL AND trim(CAST(o.genus AS VARCHAR))<>''
                AND o.binomial IS NOT NULL AND trim(CAST(o.binomial AS VARCHAR))<>''
                AND o.dataset_id IS NOT NULL AND trim(CAST(o.dataset_id AS VARCHAR))<>''
                AND o.observation_id IS NOT NULL AND trim(CAST(o.observation_id AS VARCHAR))<>''
                AND o.value IS NOT NULL AND trim(CAST(o.value AS VARCHAR))<>''
          ) SELECT DISTINCT sid,family,trait,genus,species,ds,obs,val
            FROM r WHERE val IS NOT NULL AND isfinite(val) AND unit=expected_unit
                AND expected_unit<>''
        """,[str(parquet)])
        c.execute("""
           CREATE TEMP TABLE original AS
           SELECT sid,family,trait,species,min(genus) genus
           FROM allrecords GROUP BY sid,family,trait,species
           HAVING count(DISTINCT genus)=1 AND median(val)>0
        """)
        original_counts=dict(c.execute(
           "SELECT sid,count(*) FROM original GROUP BY sid").fetchall())
        if original_counts!={sid:s["n_original"] for sid,s in systems.items()}:
            raise ValueError("original K source native medians cohort changed")
        c.execute("""
            CREATE TEMP TABLE nonflora_records AS
            SELECT a.* FROM allrecords a
            LEFT JOIN excluded e ON a.ds=e.ds WHERE e.ds IS NULL
        """)
        c.execute("""
            CREATE TEMP TABLE nonflora_states AS
            WITH m AS (
              SELECT sid,family,trait,species,min(genus) genus,
                     median(val) nonflora_state
              FROM nonflora_records GROUP BY sid,family,trait,species
              HAVING count(DISTINCT genus)=1 AND median(val)>0
            ) SELECT m.* FROM m JOIN original o
               ON m.sid=o.sid AND m.species=o.species AND m.genus=o.genus
        """)
        c.execute("""
            CREATE TEMP TABLE positive_nonflora AS
            SELECT DISTINCT d.sid,d.species,d.genus,d.ds
            FROM nonflora_records d JOIN nonflora_states n
               ON d.sid=n.sid AND d.species=n.species AND d.genus=n.genus
            WHERE d.val>0
        """)
        c.execute("""
            CREATE TEMP TABLE common_source AS
            SELECT DISTINCT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
                            a.species,a.genus,da.ds
            FROM target p
            JOIN nonflora_states a ON a.sid=p.system_A
            JOIN nonflora_states b
               ON b.sid=p.system_B AND a.species=b.species AND a.genus=b.genus
            JOIN positive_nonflora da ON da.sid=p.system_A
               AND da.species=a.species AND da.genus=a.genus
            JOIN positive_nonflora db ON db.sid=p.system_B
               AND db.species=a.species AND db.genus=a.genus AND db.ds=da.ds
        """)
        c.execute("""
            CREATE TEMP TABLE source_values AS
            SELECT s.family,s.trait_A,s.trait_B,s.system_A,s.system_B,
                   s.species,s.genus,
                   median(r.val) FILTER(WHERE r.sid=s.system_A) AS common_A,
                   median(r.val) FILTER(WHERE r.sid=s.system_B) AS common_B
            FROM common_source s JOIN nonflora_records r
              ON r.species=s.species AND r.genus=s.genus AND r.ds=s.ds
             AND r.sid IN (s.system_A,s.system_B)
            GROUP BY s.family,s.trait_A,s.trait_B,s.system_A,s.system_B,s.species,s.genus
        """)
        result=c.execute("""
            SELECT s.family,s.trait_A,s.trait_B,s.system_A,s.system_B,
               s.species,s.genus,fa.nonflora_state,fb.nonflora_state,
               s.common_A,s.common_B
            FROM source_values s
            JOIN nonflora_states fa ON fa.sid=s.system_A
              AND fa.species=s.species AND fa.genus=s.genus
            JOIN nonflora_states fb ON fb.sid=s.system_B
              AND fb.species=s.species AND fb.genus=s.genus
            ORDER BY s.family,s.trait_A,s.trait_B,s.species
        """).fetchall()
    finally:
        c.close()
    return result

def main():
    p=argparse.ArgumentParser()
    for k in ("batch-json","source-support","original-pair-support","parquet",
              "traits-yml","design","r-script","out"):
        p.add_argument("--"+k,required=True,type=Path)
    x=p.parse_args()
    support=json.loads(x.source_support.read_text())
    original=json.loads(x.original_pair_support.read_text())
    design=json.loads(x.design.read_text())
    batch=json.loads(x.batch_json.read_text())
    batch_guard(batch,support,original,design)
    rows=source_medians(x.parquet,x.traits_yml,batch)
    # The SOURCE-ONLY R parser was independently parity-validated against
    # phytools::phylosig(K); reusing it avoids changing the K estimator.
    from run_austraits_k_same_dataset_pair_batch_v0_1 import (
        write_ephemeral_states,validate_R_results)
    with tempfile.TemporaryDirectory(prefix="source_matching_nonflora_") as td:
        manifest=write_ephemeral_states(rows,batch,td)
        mf=Path(td)/"manifest.json";mf.write_text(json.dumps(manifest))
        out=Path(td)/"result.json"
        subprocess.run(["Rscript",str(x.r_script),"--manifest",str(mf),
                        "--out",str(out)],check=True)
        result=json.loads(out.read_text())
        validate_R_results(manifest,result)
    result["status"]=STATUS
    result["source_arm_semantics"]={
      "full_A_B":"All remaining nonflora DatasetIDs for each retained native species, NOT the original all-AusTraits full-source state",
      "source_A_B":"Only the remaining DatasetIDs with positive measurements of BOTH organs on each SAME species",
      "same_matched_taxa_and_native_phylogeny_for_both_source_arms":True}
    result["joint_nonflora_and_identical_source_post_outcome_exploratory"]=True
    result["not_independent_primary_measurement_validation"]=True
    result["five_flora_source_exclusion_fixed"]=[*EXCLUDED]
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,
      "n_original_K_blind_joint_source_pairs":len(result["pairs"]),
      "S3_pass":sum(z["axes"]["S3"]["status"]=="PASS" for z in result["pairs"]),
      "prune_pass":sum(z["axes"]["prune_only"]["status"]=="PASS" for z in result["pairs"])}))
if __name__=="__main__":main()
