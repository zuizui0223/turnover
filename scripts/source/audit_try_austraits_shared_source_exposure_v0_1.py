#!/usr/bin/env python3
"""Quantify exposure of ORIGINAL AusTraits K species cells to possible shared
TRY historical-publication studies. No TRY v7 measurements, K effect magnitudes,
trait-value outputs, original species IDs or observation IDs are persisted.
"""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
import duckdb
import pandas as pd
import yaml

STATUS="TRY_AUSTRAITS_POSSIBLE_SHARED_SOURCE_K_COHORT_EXPOSURE_AUDITED"
GRAPH={"systems":254,"families":42,"traits":13}
FIVE={"seed_width","leaf_area","seed_dry_mass","leaf_width","petiole_length"}

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as fp:
        return list(csv.DictReader(fp))

def build_candidates(effects,core,unit_config,design,strong,weak):
    if design.get("status")!="POST_PUBLICATION_LINKAGE_PRE_SOURCE_EXPOSURE_OUTCOME_FROZEN":
        raise ValueError("source exposure contract not frozen")
    k=pd.read_csv(effects,usecols=["system_id","family","trait_name"])
    c=pd.read_csv(core,usecols=["family","trait_name","n_input_species"])
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(254,42,13):
        raise ValueError("original effects K graph changed")
    joined=k.merge(c,on=["family","trait_name"],validate="one_to_one")
    if len(joined)!=254 or joined.system_id.nunique()!=254:
        raise ValueError("original source cohort changed")
    cfg=yaml.safe_load(Path(unit_config).read_text())["traits"]["elements"]
    settings={}
    candidate_rows=[]
    for r in joined.itertuples(index=False):
        unit=cfg[r.trait_name].get("units")
        if not unit or not str(unit).strip():
            raise ValueError("missing original source-native unit for "+r.trait_name)
        sid=str(r.system_id)
        settings[sid]={"family":str(r.family),"trait_name":str(r.trait_name),
                        "n_input_species":int(r.n_input_species)}
        candidate_rows.append((sid,str(r.family),str(r.trait_name),str(unit).strip()))
    strong_ids=set()
    for r in strong:
        if (r["austraits_source_id"]=="Tng_2013" and
            r["try_public_dataset_id"]=="625" and
            r["austraits_source_primary_doi"]=="10.1371/journal.pone.0084378" and
            r["interpretation"]=="POSSIBLE_SHARED_ORIGINAL_PUBLICATION_NOT_IDENTICAL_RECORDS"):
            strong_ids.add(r["austraits_source_id"])
        else:
            raise ValueError("unexpected strong source identity, stop to preserve interpretation")
    if strong_ids!={"Tng_2013"} or len(strong)!=1:
        raise ValueError("missing fixed strong Tng shared-publication source")
    weak_ids={r["austraits_source_id"] for r in weak}
    if len(weak)!=18 or not weak_ids or "Tng_2013" in weak_ids:
        raise ValueError("weak author-only historical leads changed")
    return candidate_rows,settings,strong_ids,weak_ids

def summarize(rows,settings,strong_ids,weak_ids):
    """Consumes aggregated SQL source counts only; does not receive species names."""
    if len(rows)!=254:raise ValueError("not all 254 original systems recovered")
    observed={}
    for row in rows:
        sid,fam,trait,n_species,observed_source,n_strong,n_weak,n_both,n_strong_records,n_weak_records=row
        if sid in observed:raise ValueError("duplicated original system in exposure report")
        ref=settings.get(str(sid))
        if ref is None or (str(fam),str(trait))!=(ref["family"],ref["trait_name"]):
            raise ValueError("source original graph mismatch")
        n_species=int(n_species)
        if n_species!=ref["n_input_species"]:
            raise ValueError(f"K source-native median cohort changed: {sid}: {n_species} vs {ref['n_input_species']}")
        vals=[int(observed_source),int(n_strong),int(n_weak),int(n_both),
              int(n_strong_records),int(n_weak_records)]
        if any(x<0 for x in vals) or any(x>n_species for x in vals[1:4]) or vals[3]>min(vals[1:3]):
            raise ValueError("impossible source exposure counts")
        if vals[0]>n_species:raise ValueError("source-positive cohort exceeds K tip support")
        observed[str(sid)]={
          "family":str(fam),"trait_name":str(trait),"n_original_species":n_species,
          "n_species_with_positive_source":vals[0],
          "n_species_with_strong_study_source":vals[1],
          "n_species_with_weak_author_source":vals[2],
          "n_species_with_both_source_types":vals[3],
          "n_strong_positive_observation_keys":vals[4],
          "n_weak_positive_observation_keys":vals[5]
        }
    if set(observed)!=set(settings):raise ValueError("missing K systems")
    traits=defaultdict(lambda:{"systems":0,"families":set(),"species_system_cells":0,
                               "strong_exposed_systems":0,"weak_exposed_systems":0,
                               "strong_exposed_families":set(),"weak_exposed_families":set(),
                               "strong_exposed_species_system_cells":0,
                               "weak_exposed_species_system_cells":0,
                               "positive_strong_source_record_keys":0,
                               "positive_weak_source_record_keys":0})
    all_families=set()
    for sid,r in observed.items():
        fam,trait=r["family"],r["trait_name"]
        all_families.add(fam)
        tr=traits[trait]
        tr["systems"]+=1
        tr["families"].add(fam)
        tr["species_system_cells"]+=r["n_original_species"]
        tr["strong_exposed_species_system_cells"]+=r["n_species_with_strong_study_source"]
        tr["weak_exposed_species_system_cells"]+=r["n_species_with_weak_author_source"]
        tr["positive_strong_source_record_keys"]+=r["n_strong_positive_observation_keys"]
        tr["positive_weak_source_record_keys"]+=r["n_weak_positive_observation_keys"]
        if r["n_species_with_strong_study_source"]>0:
            tr["strong_exposed_systems"]+=1
            tr["strong_exposed_families"].add(fam)
        if r["n_species_with_weak_author_source"]>0:
            tr["weak_exposed_systems"]+=1
            tr["weak_exposed_families"].add(fam)
    if len(all_families)!=42 or len(traits)!=13:
        raise ValueError("changed original trait/family graph")
    out={}
    for t,r in sorted(traits.items()):
        out[t]={
           "systems":r["systems"],"families":len(r["families"]),
           "species_system_cells":r["species_system_cells"],
           "strong_shared_publication_lead_families":len(r["strong_exposed_families"]),
           "strong_shared_publication_lead_systems":r["strong_exposed_systems"],
           "strong_shared_publication_lead_species_system_cells":r["strong_exposed_species_system_cells"],
           "strong_source_positive_observation_keys":r["positive_strong_source_record_keys"],
           "weak_author_only_lead_families":len(r["weak_exposed_families"]),
           "weak_author_only_lead_systems":r["weak_exposed_systems"],
           "weak_author_only_lead_species_system_cells":r["weak_exposed_species_system_cells"],
           "weak_source_positive_observation_keys":r["positive_weak_source_record_keys"],
           "is_frozen_external_named_trait":t in FIVE
        }
    def sumfield(f):return sum(z[f] for z in out.values())
    return {
      "status":STATUS,"version":"v0.1","graph":GRAPH,
      "strong_source_ids":sorted(strong_ids),
      "weak_source_ids":sorted(weak_ids),
      "source_exposure_is_not_independent_record_match":True,
      "K_effect_values_opened":False,"TRY_v7_measurements_opened":False,
      "overall":{"species_system_cells":sumfield("species_system_cells"),
                 "strong_study_source_species_system_cells":sumfield("strong_shared_publication_lead_species_system_cells"),
                 "weak_author_source_species_system_cells":sumfield("weak_author_only_lead_species_system_cells"),
                 "strong_study_positive_observation_keys":sumfield("strong_source_positive_observation_keys"),
                 "weak_author_positive_observation_keys":sumfield("weak_source_positive_observation_keys"),
                 "n_external_named_traits_with_any_strong_study_source":sum(
                    t in FIVE and r["strong_shared_publication_lead_species_system_cells"]>0 for t,r in out.items())},
      "traits":out,
      "hard_nonclaim":"A source record belonging to a citation that TRY historically indexed does not prove that same record was incorporated into TRY v6/v7; this cannot be used as an external validation PASS."
    }

def query_source(parquet,candidates,strong_ids,weak_ids):
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE candidates (system_id VARCHAR,family_name VARCHAR,trait_name VARCHAR,expected_unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES(?,?,?,?)",candidates)
    con.execute("CREATE TEMP TABLE source_labels (dataset_id VARCHAR,class VARCHAR)")
    con.executemany("INSERT INTO source_labels VALUES (?,?)",[(x,"strong") for x in sorted(strong_ids)]
                    +[(x,"weak") for x in sorted(weak_ids)])
    # Same original-source median species eligibility as frozen K source
    # repeatability feasibility audit. The final output is grouped by system,
    # family and trait; nothing species- or observation-level is persisted.
    sql=r"""
    WITH base AS (
      SELECT c.system_id,c.family_name,c.trait_name,
        trim(CAST(a.genus AS VARCHAR)) genus,
        trim(CAST(a.binomial AS VARCHAR)) species,
        trim(CAST(a.dataset_id AS VARCHAR)) dataset_id,
        trim(CAST(a.observation_id AS VARCHAR)) observation_id,
        try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) value_num,
        c.expected_unit expected_unit,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') unit
      FROM read_parquet(?) a JOIN candidates c
        ON trim(CAST(a.family AS VARCHAR))=c.family_name
       AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
      WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
        AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
        AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
        AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
        AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
        AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
    ), dedup AS (
      SELECT DISTINCT system_id,family_name,trait_name,genus,species,dataset_id,observation_id,value_num
      FROM base
      WHERE value_num IS NOT NULL AND isfinite(value_num)
        AND expected_unit<>'' AND unit=expected_unit
    ), states AS (
      SELECT system_id,family_name,trait_name,species
      FROM dedup
      GROUP BY system_id,family_name,trait_name,species
      HAVING count(DISTINCT genus)=1 AND median(value_num)>0
    ), per_species AS (
      SELECT s.system_id,s.family_name,s.trait_name,s.species,
        max(CASE WHEN d.value_num>0 THEN 1 ELSE 0 END) has_positive,
        max(CASE WHEN d.value_num>0 AND lab.class='strong' THEN 1 ELSE 0 END) has_strong,
        max(CASE WHEN d.value_num>0 AND lab.class='weak' THEN 1 ELSE 0 END) has_weak,
        count(DISTINCT CASE WHEN d.value_num>0 AND lab.class='strong'
           THEN d.dataset_id||chr(31)||d.observation_id END) strong_keys,
        count(DISTINCT CASE WHEN d.value_num>0 AND lab.class='weak'
           THEN d.dataset_id||chr(31)||d.observation_id END) weak_keys
      FROM states s JOIN dedup d USING(system_id,family_name,trait_name,species)
      LEFT JOIN source_labels lab ON d.dataset_id=lab.dataset_id
      GROUP BY s.system_id,s.family_name,s.trait_name,s.species
    )
    SELECT system_id,family_name,trait_name,count(*) n_original_species,
      sum(has_positive) n_positive,
      sum(has_strong) n_strong,sum(has_weak) n_weak,
      sum(CASE WHEN has_strong=1 AND has_weak=1 THEN 1 ELSE 0 END) n_both,
      sum(strong_keys) strong_positive_record_keys,
      sum(weak_keys) weak_positive_record_keys
    FROM per_species
    GROUP BY system_id,family_name,trait_name
    ORDER BY system_id
    """
    try:return con.execute(sql,[str(parquet)]).fetchall()
    finally:con.close()

def main():
    p=argparse.ArgumentParser()
    for k in ("parquet","core","observed-K","traits-yml","strong-links",
              "weak-leads","design","out"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    strong=read_csv(a.__dict__["strong_links"])
    weak=read_csv(a.__dict__["weak_leads"])
    candidates,settings,strong_ids,weak_ids=build_candidates(
      a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],design,strong,weak)
    source_counts=query_source(a.parquet,candidates,strong_ids,weak_ids)
    output=summarize(source_counts,settings,strong_ids,weak_ids)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":STATUS,"overall":output["overall"]},sort_keys=True))

if __name__=="__main__":main()
