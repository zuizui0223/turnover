#!/usr/bin/env python3
"""K-blind original-source common-dataset support for 760 native K trait pairs.

- Recreate ORIGINAL 254 family×trait source-native positive-median eligible
  species using AusTraits release 7.0.0 and its original unit definitions.
- Pair only exact originally validated >=20-species common trait-pair cohorts.
- On each such species, test whether BOTH traits have a positive original
  measurement with the SAME AusTraits dataset_id, and separately same
  dataset_id+observation_id. Neither proves shared specimens nor independent
  primary records.
- Output ONLY aggregate family/trait-pair counts; no species IDs, trait values
  or contributing dataset identifiers persist to user-visible artifacts.
"""
from __future__ import annotations
import argparse
import json
from itertools import combinations
from pathlib import Path
from collections import Counter,defaultdict
import duckdb
import pandas as pd
import yaml

STATUS="AUSTRAITS_CROSS_TRAIT_COMMON_DATASET_SUPPORT_AUDITED"
FROZEN="POST_K_AND_MODULE_DISCOVERY_PRE_SHARED_DATASET_SUPPORT_OUTCOME_FROZEN"

def read_inputs(kfile,corefile,unitfile,support,design):
    if design.get("status")!=FROZEN:
        raise ValueError("original shared-source support protocol not frozen")
    if support.get("status")!="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED":
        raise ValueError("source-blind 760-pair support audit missing")
    if support.get("qualifying_family_trait_pairs")!=760 or len(support.get("trait_pairs",{}))!=66:
        raise ValueError("not all frozen 760/66 trait pair support identities present")
    k=pd.read_csv(kfile,usecols=["system_id","family","trait_name"])
    core=pd.read_csv(corefile,usecols=["family","trait_name","n_input_species"])
    if (len(k),k.family.nunique(),k.trait_name.nunique())!=(254,42,13):
        raise ValueError("original K graph changed")
    joined=k.merge(core,on=["family","trait_name"],validate="one_to_one")
    if len(joined)!=254 or joined.system_id.nunique()!=254:
        raise ValueError("original source-system join changed")
    units=yaml.safe_load(Path(unitfile).read_text())["traits"]["elements"]
    original={}
    cand=[]
    for r in joined.itertuples(index=False):
        sid=str(r.system_id)
        u=units[r.trait_name].get("units")
        if not u or not str(u).strip():raise ValueError("missing original native unit for "+r.trait_name)
        original[sid]={"family":str(r.family),"trait":str(r.trait_name),"n":int(r.n_input_species)}
        cand.append((sid,str(r.family),str(r.trait_name),str(u).strip()))
    if (len(cand),len(set(x[0] for x in cand)))!=(254,254):
        raise ValueError("original repeated system IDs")
    pairs=[]
    reference={}
    for row in support["family_trait_pair_support"]:
        if not row["qualifies_20_common_species"]:continue
        fam,a,b,sa,sb=(row[x] for x in ("family","trait_A","trait_B","system_A","system_B"))
        if sa not in original or sb not in original:
            raise ValueError("pair system absent from original 254 K graph")
        if (original[sa]["family"],original[sa]["trait"])!=(fam,a) or (original[sb]["family"],original[sb]["trait"])!=(fam,b):
            raise ValueError("family/trait source graph mismatched")
        if (row["n_original_A"],row["n_original_B"])!=(original[sa]["n"],original[sb]["n"]):
            raise ValueError("original species support changed for pair")
        if row["n_common_species_same_genus"]<20 or row["n_common_binomial_conflicting_genus"]<0:
            raise ValueError("original shared-species eligibility changed")
        key=(fam,a,b)
        if key in reference:raise ValueError("duplicate frozen family×pair ID")
        reference[key]=row
        pairs.append((fam,a,b,sa,sb))
    if len(pairs)!=760:
        raise ValueError("not all original source-only 760 family×pair identities retained")
    cls=design["identity_rules"]["cross_organ_classes"]
    reps=set(cls["reproductive"]);veg=set(cls["vegetative"])
    if (len(reps),len(veg),len(reps&veg))!=(6,6,0):
        raise ValueError("12 organ classes changed from frozen analysis")
    if {r["trait"] for r in original.values()}!=reps|veg|{"seed_height"}:
        raise ValueError("original trait universe changed")
    return cand,pairs,reference,original,reps,veg

def query_counts(parquet,candidates,pairs):
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE cand(system_id VARCHAR,family_name VARCHAR,trait_name VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO cand VALUES (?,?,?,?)",candidates)
    con.execute("CREATE TEMP TABLE pairs(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR,system_A VARCHAR,system_B VARCHAR)")
    con.executemany("INSERT INTO pairs VALUES (?,?,?,?,?)",pairs)
    sql=r"""
    CREATE TEMP TABLE original_dedup AS
    WITH base AS (
       SELECT c.system_id,c.family_name,c.trait_name,
          trim(CAST(a.genus AS VARCHAR)) genus,
          trim(CAST(a.binomial AS VARCHAR)) species,
          trim(CAST(a.dataset_id AS VARCHAR)) dataset_id,
          trim(CAST(a.observation_id AS VARCHAR)) observation_id,
          try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) val,
          c.unit expected_unit,coalesce(trim(CAST(a.unit AS VARCHAR)),'') source_unit
       FROM read_parquet(?) a JOIN cand c
        ON trim(CAST(a.family AS VARCHAR))=c.family_name
       AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
       WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
        AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
        AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
        AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
        AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
        AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
    )
    SELECT DISTINCT system_id,family_name,trait_name,genus,species,
                    dataset_id,observation_id,val
    FROM base
    WHERE val IS NOT NULL AND isfinite(val) AND expected_unit<>''
      AND source_unit=expected_unit
    """
    try:
        con.execute(sql,[str(parquet)])
        con.execute("""
           CREATE TEMP TABLE eligible_species AS
           SELECT system_id,family_name,trait_name,species,min(genus) genus
           FROM original_dedup
           GROUP BY system_id,family_name,trait_name,species
           HAVING count(DISTINCT genus)=1 AND median(val)>0
        """)
        original_counts=con.execute(
           "SELECT system_id,count(*) FROM eligible_species GROUP BY system_id").fetchall()
        con.execute("""
          CREATE TEMP TABLE valid_positive_source_keys AS
          SELECT DISTINCT d.system_id,d.family_name,d.trait_name,
                 d.species,d.genus,d.dataset_id,d.observation_id
          FROM original_dedup d JOIN eligible_species v
            ON d.system_id=v.system_id AND d.species=v.species
               AND d.genus=v.genus
          WHERE d.val>0
        """)
        con.execute("""
          CREATE TEMP TABLE matched_original_species AS
          SELECT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
                 a.species,a.genus
          FROM pairs p
          JOIN eligible_species a ON a.system_id=p.system_A
          JOIN eligible_species b ON b.system_id=p.system_B
           AND a.species=b.species AND a.genus=b.genus
        """)
        con.execute("""
          CREATE TEMP TABLE same_dataset_species AS
          SELECT DISTINCT p.family,p.trait_A,p.trait_B,p.species
          FROM matched_original_species p
          JOIN valid_positive_source_keys a
            ON a.system_id=p.system_A AND a.species=p.species
               AND a.genus=p.genus
          JOIN valid_positive_source_keys b
            ON b.system_id=p.system_B AND b.species=p.species
               AND b.genus=p.genus AND a.dataset_id=b.dataset_id
        """)
        con.execute("""
          CREATE TEMP TABLE same_record_key_species AS
          SELECT DISTINCT p.family,p.trait_A,p.trait_B,p.species
          FROM matched_original_species p
          JOIN valid_positive_source_keys a
           ON a.system_id=p.system_A AND a.species=p.species
              AND a.genus=p.genus
          JOIN valid_positive_source_keys b
           ON b.system_id=p.system_B AND b.species=p.species
              AND b.genus=p.genus AND a.dataset_id=b.dataset_id
              AND a.observation_id=b.observation_id
        """)
        pair_counts=con.execute("""
          SELECT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
                 count(*) original_same_species,
                 sum(CASE WHEN d.species IS NOT NULL THEN 1 ELSE 0 END) same_dataset_species,
                 sum(CASE WHEN k.species IS NOT NULL THEN 1 ELSE 0 END) same_record_key_species
          FROM matched_original_species p
          LEFT JOIN same_dataset_species d
           ON p.family=d.family AND p.trait_A=d.trait_A
              AND p.trait_B=d.trait_B AND p.species=d.species
          LEFT JOIN same_record_key_species k
           ON p.family=k.family AND p.trait_A=k.trait_A
              AND p.trait_B=k.trait_B AND p.species=k.species
          GROUP BY p.family,p.trait_A,p.trait_B,p.system_A,p.system_B
          ORDER BY p.family,p.trait_A,p.trait_B
        """).fetchall()
        return original_counts,pair_counts
    finally:
        con.close()

def adjudicate(original_counts,pair_counts,expected,pairs,repro,veg,design):
    actual={}
    for sid,n in original_counts:
        if sid not in expected or sid in actual or int(n)!=expected[sid]["n"]:
            raise ValueError("original source-native species median cohort changed")
        actual[sid]=int(n)
    if set(actual)!=set(expected):raise ValueError("lost original 254 K systems")
    outcomes={}
    for fam,a,b,sa,sb,ncommon,nsame,nkey in pair_counts:
        key=(str(fam),str(a),str(b))
        if key in outcomes or key not in pairs:raise ValueError("unknown or duplicate family trait pair")
        ref=pairs[key]
        if (sa,sb)!=(ref["system_A"],ref["system_B"]):
            raise ValueError("source pair IDs altered")
        if int(ncommon)!=ref["n_common_species_same_genus"]:
            raise ValueError("original K-blind matched-species count changed")
        ncommon,nsame,nkey=map(int,(ncommon,nsame,nkey))
        if not 0<=nkey<=nsame<=ncommon:raise ValueError("impossible same-source support counts")
        cross=(a in repro)!=(b in repro)
        if not ((a in repro|veg) and (b in repro|veg)):
            raise ValueError("unidentified original organ class")
        outcomes[key]={
           "family":str(fam),"trait_A":str(a),"trait_B":str(b),
           "n_original_shared_species":ncommon,
           "n_same_AusTraits_dataset_species":nsame,
           "n_same_AusTraits_dataset_and_observation_key_species":nkey,
           "fraction_original_shared_species_with_same_dataset":nsame/ncommon,
           "cross_organ":cross,
           "qualifies_same_dataset_20_species":nsame>=20,
           "qualifies_same_record_key_20_species":nkey>=20,
           "contains_seed_dry_mass":a=="seed_dry_mass" or b=="seed_dry_mass",
           "cross_seed_vs_vegetative":cross and (a.startswith("seed_") or b.startswith("seed_")),
           "cross_fruit_vs_vegetative":cross and (a.startswith("fruit_") or b.startswith("fruit_"))
        }
    if set(outcomes)!=set(pairs):raise ValueError("not all 760 original same-tip pairs audited")
    rows=list(outcomes.values())
    cross=[r for r in rows if r["cross_organ"]]
    if len(cross)!=406:raise ValueError("not original 406 source-supported cross-organ S3 pairs")
    if len(set(r["family"] for r in cross))!=34:raise ValueError("original 34 families missing")
    strong=[r for r in cross if r["qualifies_same_dataset_20_species"]]
    fruit=[r for r in strong if r["cross_fruit_vs_vegetative"]]
    seed=[r for r in strong if r["cross_seed_vs_vegetative"]]
    by_type=defaultdict(list)
    for row in cross:
        by_type[row["trait_A"]+"__"+row["trait_B"]].append(row)
    if len(by_type)!=36:raise ValueError("not original 36 cross-organ types")
    families_all=sorted({r["family"] for r in strong})
    gates=design["gates"]
    descriptive_ok=(
      len(families_all)>=gates["min_independent_family_clusters_for_cross_organ_descriptive_generalization"]
      and len(set(r["family"] for r in fruit))>=gates["min_fruit_vs_vegetative_families"]
      and len(set(r["family"] for r in seed))>=gates["min_seed_vs_vegetative_families"]
    )
    def stats_group(subset):
        return {
          "n_original_family_trait_pairs":len(subset),
          "n_original_shared_species_cells":int(sum(r["n_original_shared_species"] for r in subset)),
          "n_same_dataset_species_cells":int(sum(r["n_same_AusTraits_dataset_species"] for r in subset)),
          "n_same_observation_key_species_cells":int(sum(r["n_same_AusTraits_dataset_and_observation_key_species"] for r in subset)),
          "n_pairs_with_at_least_20_same_dataset_species":int(sum(r["qualifies_same_dataset_20_species"] for r in subset)),
          "n_pairs_with_at_least_20_same_record_key_species":int(sum(r["qualifies_same_record_key_20_species"] for r in subset)),
          "n_independent_families_with_20_same_dataset_species":len({r["family"] for r in subset if r["qualifies_same_dataset_20_species"]})
        }
    out={
       "version":"v0.1","status":STATUS,
       "source_support_original_graph":{"systems":254,"families":42,"traits":13},
       "source_calibrated_original_K_graph":{"systems":249,"families":42,"traits":12},
       "original_pair_support_cohort":760,
       "all_pairs":stats_group(rows),
       "cross_organ":stats_group(cross),
       "within_organ":stats_group([r for r in rows if not r["cross_organ"]]),
       "seed_versus_vegetative":stats_group([r for r in cross if r["cross_seed_vs_vegetative"]]),
       "fruit_versus_vegetative":stats_group([r for r in cross if r["cross_fruit_vs_vegetative"]]),
       "cross_organ_family_trait_pair_support":sorted(cross,key=lambda r:(r["family"],r["trait_A"],r["trait_B"])),
       "cross_organ_trait_type_support":{
           name:{"n_families_qualified_same_dataset":len({r["family"] for r in rr if r["qualifies_same_dataset_20_species"]}),
                 "n_original_families":len(rr),
                 "n_same_dataset_species_cells":sum(r["n_same_AusTraits_dataset_species"] for r in rr)}
           for name,rr in sorted(by_type.items())},
       "gates":{"minimum_20_same_dataset_species_per_pair":20,
                "minimum_10_families_both_organs":10,
                "minimum_5_fruit_and_5_seed_families":5,
                "descriptive_cross_organ_same_dataset_K_comparison_supports":bool(descriptive_ok)},
       "scientific_verdict":"SOURCE_DATASET_ID_MATCH_ONLY_NOT_INDEPENDENT_OR_SAME_SPECIMEN",
       "K_outcomes_opened_or_reestimated":False,
       "public_species_names_or_measurement_values_emitted":False,
       "TRY_v7_independent_source_qualified":False,
       "hard_nonclaim":"Shared AusTraits dataset_id is not proof of independent primary records or same physical specimen. A source dataset may be a derivative compilation; do not interpret same-source K support as verified experimental control."
    }
    return out

def main():
    p=argparse.ArgumentParser()
    for name in ("parquet","core","observed-K","traits-yml","support","design","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    d=json.loads(a.design.read_text())
    s=json.loads(a.support.read_text())
    c,p,refs,expected,repro,veg=read_inputs(
       a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],s,d)
    orig,counts=query_counts(a.parquet,c,p)
    result=adjudicate(orig,counts,expected,refs,repro,veg,d)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
      "status":STATUS,"all_pairs":result["all_pairs"],
      "cross_organ":result["cross_organ"],
      "seed_versus_vegetative":result["seed_versus_vegetative"],
      "fruit_versus_vegetative":result["fruit_versus_vegetative"],
      "support_gate_pass":result["gates"]["descriptive_cross_organ_same_dataset_K_comparison_supports"]
    },sort_keys=True))

if __name__=="__main__":main()
