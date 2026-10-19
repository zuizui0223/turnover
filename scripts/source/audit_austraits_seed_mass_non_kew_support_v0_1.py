#!/usr/bin/env python3
"""Exact native-source K species-support audit after excluding Kew SID data.

A POST-OUTCOME source-only feasibility diagnostic. K effect columns are never
accessed except original system_id/family/trait identity; no K recomputation,
trait values or species names appear in the archived output.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import duckdb,yaml

STATUS="AUSTRAITS_SEED_MASS_NO_KEW_SOURCE_SUPPORT_AUDITED"
DESIGN="AFTER_KEW_EXPOSURE_BEFORE_SOURCE_EXCLUSION_SUPPORT_OUTCOME_FROZEN"

def prepare(orig_K,core,units,contract):
    if contract.get("status")!=DESIGN:raise ValueError("support design missing")
    k=pd.read_csv(orig_K,usecols=["system_id","family","trait_name"])
    c=pd.read_csv(core,usecols=["family","trait_name","n_input_species"])
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(254,42,13):
        raise ValueError("modified original 254 K family×trait graph")
    joined=k.merge(c,on=["family","trait_name"],validate="one_to_one")
    if joined.system_id.nunique()!=254 or len(joined)!=254:
        raise ValueError("wrong original K source graph join")
    if (joined.trait_name=="seed_dry_mass").sum()!=15:
        raise ValueError("unexpected original seed dry mass systems")
    cfg=yaml.safe_load(Path(units).read_text())["traits"]["elements"]
    candidates=[];expected={}
    for r in joined.itertuples(index=False):
        unit=cfg[r.trait_name].get("units")
        if not unit or not str(unit).strip():raise ValueError("missing source-native unit")
        sid=str(r.system_id)
        expected[sid]={"family":str(r.family),"trait":str(r.trait_name),"n":int(r.n_input_species)}
        candidates.append((sid,str(r.family),str(r.trait_name),str(unit).strip()))
    if sum(v["n"] for v in expected.values() if v["trait"]=="seed_dry_mass")!=4242:
        raise ValueError("original seed mass cohort size changed")
    return candidates,expected

def source_counts(parquet,candidates):
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE candidates (system_id VARCHAR, family_name VARCHAR, trait_name VARCHAR, expected_unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES(?,?,?,?)",candidates)
    sql=r"""
    WITH base AS (
       SELECT c.system_id,c.family_name,c.trait_name,
          trim(CAST(a.genus AS VARCHAR)) AS genus,
          trim(CAST(a.binomial AS VARCHAR)) AS species,
          trim(CAST(a.dataset_id AS VARCHAR)) AS dataset_id,
          trim(CAST(a.observation_id AS VARCHAR)) AS observation_id,
          try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) AS value_num,
          c.expected_unit AS expected_unit,
          coalesce(trim(CAST(a.unit AS VARCHAR)),'') AS unit
       FROM read_parquet(?) a
       JOIN candidates c
         ON trim(CAST(a.family AS VARCHAR))=c.family_name
        AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
       WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
         AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
         AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
         AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
         AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
         AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
    ), dedup AS (
       SELECT DISTINCT system_id,family_name,trait_name,genus,species,
              dataset_id,observation_id,value_num
       FROM base
       WHERE value_num IS NOT NULL AND isfinite(value_num)
         AND expected_unit<>'' AND unit=expected_unit
    ), original_species AS (
       SELECT system_id,family_name,trait_name,species
       FROM dedup
       GROUP BY system_id,family_name,trait_name,species
       HAVING count(DISTINCT genus)=1 AND median(value_num)>0
    ), nonkew_species AS (
       SELECT system_id,family_name,trait_name,species
       FROM dedup
       WHERE dataset_id<>'Kew_2019_1'
       GROUP BY system_id,family_name,trait_name,species
       HAVING count(DISTINCT genus)=1 AND median(value_num)>0
    ), restricted_support AS (
       SELECT o.system_id,o.family_name,o.trait_name,o.species,
          CASE WHEN k.species IS NOT NULL THEN 1 ELSE 0 END has_nonkew
       FROM original_species o
       LEFT JOIN nonkew_species k
         ON o.system_id=k.system_id AND o.species=k.species
    )
    SELECT system_id,family_name,trait_name,
       count(*) n_original,
       sum(has_nonkew) n_nonkew
    FROM restricted_support
    GROUP BY system_id,family_name,trait_name
    ORDER BY system_id
    """
    try:return con.execute(sql,[str(parquet)]).fetchall()
    finally:con.close()

def summarize(rows,expected):
    if len(rows)!=254:raise ValueError("original 254-system support not preserved")
    seen=set()
    per_seed=[]
    nall=0
    for sid,fam,trait,n_orig,n_nonkew in rows:
        sid=str(sid)
        if sid in seen:raise ValueError("duplicate original K system")
        seen.add(sid)
        meta=expected.get(sid)
        if meta is None or (fam,trait)!=(meta["family"],meta["trait"]):
            raise ValueError("source K system identity changed")
        original,nonkew=int(n_orig),int(n_nonkew)
        if original!=meta["n"] or not 0<=nonkew<=original:
            raise ValueError("original species support changed or invalid")
        nall+=original
        if trait!="seed_dry_mass":
            if nonkew!=original:
                raise ValueError("exclusion of Kew SID altered another trait")
            continue
        per_seed.append({
          "family":fam,"system_id":sid,
          "n_original_species":original,
          "n_non_kew_positive_median_species":nonkew,
          "n_lost_species_after_excluding_kew":original-nonkew,
          "retention_fraction":nonkew/original if original>0 else None,
          "meets_20_species_descriptive_gate":nonkew>=20
        })
    if len(per_seed)!=15 or len(seen)!=254 or nall!=66330:
        raise ValueError("original 15-family/66,330-cell support changed")
    retained=sum(x["n_non_kew_positive_median_species"] for x in per_seed)
    if retained>4242:raise ValueError("non-Kew support exceeds original")
    return {
      "version":"v0.1","status":STATUS,
      "original_graph":{"systems":254,"families":42,"traits":13},
      "original_seed_mass_families":15,
      "original_seed_mass_species_system_cells":4242,
      "nonkew_supported_seed_mass_species_system_cells":retained,
      "species_system_cells_lost_due_to_kew_exclusion":4242-retained,
      "retention_fraction":retained/4242,
      "families_with_at_least_20_remaining_seed_mass_species":sum(x["meets_20_species_descriptive_gate"] for x in per_seed),
      "family_support":sorted(per_seed,key=lambda x:x["family"]),
      "K_effect_values_opened":False,
      "TRY_v7_measurements_opened":False,
      "not_independent_replication":True,
      "biological_boundary":"Exclusion-only source support sensitivity on the original cohort; no conclusions about K changes, selection, trait-specific OU rates or independent TRY v7 source lineage."
    }

def main():
    p=argparse.ArgumentParser()
    for opt in ("parquet","core","observed-K","traits-yml","design","out"):
        p.add_argument("--"+opt,required=True,type=Path)
    a=p.parse_args()
    d=json.loads(a.design.read_text())
    candidates,expected=prepare(a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],d)
    result=summarize(source_counts(a.parquet,candidates),expected)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,
         "nonkew_supported_species_cells":result["nonkew_supported_seed_mass_species_system_cells"],
         "original_species_cells":4242,
         "families_meeting_20_species":result["families_with_at_least_20_remaining_seed_mass_species"]}))
if __name__=="__main__":main()
