#!/usr/bin/env python3
"""K-blind feasibility after removing FIVE named electronic flora source IDs.

Reconstruct all 254 original positive-median eligible species-system cohorts,
and for every one of the 760 K-blind originally same-species family×trait
pairs count positive no-flora medians for both traits, optionally from at
least one identical remaining AusTraits dataset ID. No original K outcome
magnitude, raw species names, observation IDs or phenotype values exported.

The five-flora exclusion was motivated AFTER the original discovery and
279 source-restricted K results; it is NOT independent external validation.
"""
from __future__ import annotations
import argparse,json,sys
from collections import defaultdict
from pathlib import Path
import duckdb

from audit_austraits_k_cross_trait_shared_dataset_support_v0_1 import read_inputs

STATUS="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_SOURCE_SUPPORT_AUDITED"
DESIGN="POST_279_K_AND_FLORA_LINEAGE_OUTCOMES_PRE_FLORA_EXCLUSION_SUPPORT_COUNTS_FROZEN"


def check_design(design):
    if design.get("status")!=DESIGN:raise ValueError("five-flora exclusion design not frozen")
    sources=design["fixed_excluded_contributing_AusTraits_dataset_ids"]
    if sources!=["ABRS_2023","NHNSW_2023","RBGV_2023","NTH_2023","SAH_2023"]:
        raise ValueError("five electronic floristic source IDs changed")
    gates=design["eligibility"]
    if (gates["min_positive_nonflora_species_per_family_trait_pair"]!=20
        or gates["min_positive_same_nonflora_dataset_species_per_family_trait_pair"]!=20):
        raise ValueError("source-exclusion family pair support thresholds changed")
    return sources


def source_only_counts(parquet,candidates,pairs,excluded):
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE cand(sid VARCHAR,family VARCHAR,trait VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO cand VALUES (?,?,?,?)",candidates)
    con.execute("CREATE TEMP TABLE pairs(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR,system_A VARCHAR,system_B VARCHAR)")
    con.executemany("INSERT INTO pairs VALUES(?,?,?,?,?)",pairs)
    con.execute("CREATE TEMP TABLE excluded(dataset_id VARCHAR)")
    con.executemany("INSERT INTO excluded VALUES (?)",[(d,) for d in excluded])
    try:
        con.execute(r"""
        CREATE TEMP TABLE original_dedup AS
        WITH valid AS (
            SELECT c.sid,c.family,c.trait,
                   trim(CAST(v.genus AS VARCHAR)) genus,
                   trim(CAST(v.binomial AS VARCHAR)) species,
                   trim(CAST(v.dataset_id AS VARCHAR)) dataset_id,
                   trim(CAST(v.observation_id AS VARCHAR)) observation_id,
                   try_cast(trim(CAST(v.value AS VARCHAR)) AS DOUBLE) val,
                   c.unit expected_unit,
                   coalesce(trim(CAST(v.unit AS VARCHAR)),'') AS native_unit
            FROM read_parquet(?) v
            JOIN cand c ON trim(CAST(v.family AS VARCHAR))=c.family
              AND trim(CAST(v.trait_name AS VARCHAR))=c.trait
            WHERE lower(trim(CAST(v.taxon_rank AS VARCHAR)))='species'
              AND v.genus IS NOT NULL AND trim(CAST(v.genus AS VARCHAR))<>''
              AND v.binomial IS NOT NULL AND trim(CAST(v.binomial AS VARCHAR))<>''
              AND v.dataset_id IS NOT NULL AND trim(CAST(v.dataset_id AS VARCHAR))<>''
              AND v.observation_id IS NOT NULL AND trim(CAST(v.observation_id AS VARCHAR))<>''
              AND v.value IS NOT NULL AND trim(CAST(v.value AS VARCHAR))<>''
        )
        SELECT DISTINCT sid,family,trait,genus,species,dataset_id,observation_id,val
        FROM valid WHERE val IS NOT NULL AND isfinite(val)
           AND expected_unit<>'' AND native_unit=expected_unit
        """,[str(parquet)])
        con.execute("""
        CREATE TEMP TABLE eligible_original AS
        SELECT sid,family,trait,species,min(genus) AS genus
        FROM original_dedup
        GROUP BY sid,family,trait,species
        HAVING count(DISTINCT genus)=1 AND median(val)>0
        """)
        original_counts=con.execute("SELECT sid,count(*) FROM eligible_original GROUP BY sid").fetchall()
        con.execute("""
        CREATE TEMP TABLE eligible_nonflora AS
        WITH nonflora_states AS (
            SELECT d.sid,d.family,d.trait,d.species,
                   min(d.genus) AS genus
            FROM original_dedup d
            LEFT JOIN excluded x ON d.dataset_id=x.dataset_id
            WHERE x.dataset_id IS NULL
            GROUP BY d.sid,d.family,d.trait,d.species
            HAVING count(DISTINCT d.genus)=1 AND median(d.val)>0
        )
        SELECT n.sid,n.family,n.trait,n.species,n.genus
        FROM nonflora_states n
        JOIN eligible_original o
          ON n.sid=o.sid AND n.species=o.species AND n.genus=o.genus
        """)
        nonflora_counts=con.execute(
           "SELECT sid,count(*) FROM eligible_nonflora GROUP BY sid").fetchall()
        con.execute("""
        CREATE TEMP TABLE paired_original AS
        SELECT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
               a.species,a.genus
        FROM pairs p
        JOIN eligible_original a ON a.sid=p.system_A
        JOIN eligible_original b
           ON b.sid=p.system_B
          AND b.species=a.species AND b.genus=a.genus
        """)
        con.execute("""
        CREATE TEMP TABLE paired_nonflora AS
        SELECT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
               p.species,p.genus
        FROM paired_original p
        JOIN eligible_nonflora a ON a.sid=p.system_A
          AND a.species=p.species AND a.genus=p.genus
        JOIN eligible_nonflora b ON b.sid=p.system_B
          AND b.species=p.species AND b.genus=p.genus
        """)
        con.execute("""
        CREATE TEMP TABLE positive_nonflora AS
        SELECT DISTINCT d.sid,d.species,d.genus,d.dataset_id
        FROM original_dedup d
        JOIN eligible_nonflora n
          ON d.sid=n.sid AND d.species=n.species AND d.genus=n.genus
        LEFT JOIN excluded x ON d.dataset_id=x.dataset_id
        WHERE x.dataset_id IS NULL AND d.val>0
        """)
        con.execute("""
        CREATE TEMP TABLE paired_same_nonflora_dataset AS
        SELECT DISTINCT p.family,p.trait_A,p.trait_B,p.species
        FROM paired_nonflora p
        JOIN positive_nonflora a
          ON a.sid=p.system_A AND a.species=p.species AND a.genus=p.genus
        JOIN positive_nonflora b
          ON b.sid=p.system_B AND b.species=p.species AND b.genus=p.genus
         AND b.dataset_id=a.dataset_id
        """)
        results=con.execute("""
        SELECT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
            coalesce(o.n_original,0) n_original,
            coalesce(n.n_nonflora,0) n_both_no_flora,
            coalesce(s.n_same_source,0) n_both_same_nonflora_source
        FROM pairs p
        LEFT JOIN (
           SELECT family,trait_A,trait_B,count(*) n_original
           FROM paired_original GROUP BY family,trait_A,trait_B) o
         USING(family,trait_A,trait_B)
        LEFT JOIN (
           SELECT family,trait_A,trait_B,count(*) n_nonflora
           FROM paired_nonflora GROUP BY family,trait_A,trait_B) n
         USING(family,trait_A,trait_B)
        LEFT JOIN (
           SELECT family,trait_A,trait_B,count(*) n_same_source
           FROM paired_same_nonflora_dataset GROUP BY family,trait_A,trait_B) s
         USING(family,trait_A,trait_B)
        ORDER BY p.family,p.trait_A,p.trait_B
        """).fetchall()
        return original_counts,nonflora_counts,results
    finally:con.close()


def adjudicate(orig_counts,non_counts,pair_counts,original,refpairs,repro,veg,design):
    check_design(design)
    actual={}
    for sid,n in orig_counts:
        if sid not in original or sid in actual or int(n)!=int(original[sid]["n"]):
            raise ValueError("original 254 K system source species eligibility changed")
        actual[sid]=int(n)
    if set(actual)!=set(original) or len(actual)!=254:
        raise ValueError("original 254 systems not fully reconstructed")
    no={}
    for sid,n in non_counts:
        if sid not in original or sid in no or not 0<int(n)<=actual[sid]:
            raise ValueError("invalid original non-flora source support")
        no[sid]=int(n)
    for sid in original:no.setdefault(sid,0)
    expected={(f,a,b):(sa,sb) for f,a,b,sa,sb in refpairs}
    if len(expected)!=760:raise ValueError("missing original 760 pair identity")
    data={}
    for fam,a,b,sa,sb,old,nnew,nsame in pair_counts:
        key=(fam,a,b)
        if key in data or expected.get(key)!=(sa,sb):
            raise ValueError("unknown/duplicated original K-blind family/trait source pair")
        ref=int(original[sa]["n"]); ref2=int(original[sb]["n"])
        old,nnew,nsame=map(int,(old,nnew,nsame))
        if not 0<=nsame<=nnew<=old<=min(ref,ref2):
            raise ValueError("invalid paired source-removed common-species counts")
        is_cross=(a in repro)!=(b in repro)
        if a not in repro|veg or b not in repro|veg:
            raise ValueError("unrecognized source-calibrated trait")
        row={"family":fam,"trait_A":a,"trait_B":b,
             "system_A":sa,"system_B":sb,
             "n_original_shared_positive_species":old,
             "n_nonflora_positive_median_shared_species":nnew,
             "n_same_nonflora_dataset_shared_positive_species":nsame,
             "fraction_original_overlap_retained_without_floras":nnew/old if old else None,
             "qualifies_20_no_flora_median_species":nnew>=20,
             "qualifies_20_same_nonflora_dataset_species":nsame>=20,
             "cross_organ":is_cross,
             "cross_seed_vegetative":is_cross and (a.startswith("seed_") or b.startswith("seed_")),
             "cross_fruit_vegetative":is_cross and (a.startswith("fruit_") or b.startswith("fruit_"))}
        data[key]=row
    if set(data)!=set(expected):
        raise ValueError("incomplete original 760 family×pair source overlap cohort")
    if sum(z["cross_organ"] for z in data.values())!=406:
        raise ValueError("original 406 cross-organ K-blind source cohort changed")
    def group(v):
        def summarize(selector):
            rows=[r for r in v if selector(r)]
            passed=[r for r in rows if r["qualifies_20_no_flora_median_species"]]
            same=[r for r in rows if r["qualifies_20_same_nonflora_dataset_species"]]
            return {
              "original_pairs":len(rows),
              "qualifying_20_nonflora_median_pairs":len(passed),
              "qualifying_20_same_nonflora_dataset_pairs":len(same),
              "families_with_nonflora_pair_support":len({r["family"] for r in passed}),
              "families_with_same_nonflora_dataset_pair_support":len({r["family"] for r in same}),
              "n_original_shared_species_pair_cells":sum(r["n_original_shared_positive_species"] for r in rows),
              "n_nonflora_shared_species_pair_cells":sum(r["n_nonflora_positive_median_shared_species"] for r in rows),
              "n_same_nonflora_dataset_species_pair_cells":sum(r["n_same_nonflora_dataset_shared_positive_species"] for r in rows)
            }
        return summarize
    summarize=group(list(data.values()))
    by={
      "all":summarize(lambda z:True),
      "cross_organ":summarize(lambda z:z["cross_organ"]),
      "fruit_vegetative":summarize(lambda z:z["cross_fruit_vegetative"]),
      "seed_vegetative":summarize(lambda z:z["cross_seed_vegetative"]),
      "within_organ":summarize(lambda z:not z["cross_organ"])
    }
    eligible=[r for r in data.values() if r["cross_organ"] and r["qualifies_20_no_flora_median_species"]]
    fr=[r for r in eligible if r["cross_fruit_vegetative"]]
    sd=[r for r in eligible if r["cross_seed_vegetative"]]
    selected_traits={x for r in eligible for x in (r["trait_A"],r["trait_B"])}
    valid=(
      len({r["family"] for r in eligible})>=design["descriptive_support_gates"]["minimum_cross_organ_families_for_exploratory_reestimated_K"]
      and len({r["family"] for r in fr})>=design["descriptive_support_gates"]["minimum_fruit_vs_vegetative_families"]
      and len({r["family"] for r in sd})>=design["descriptive_support_gates"]["minimum_seed_vs_vegetative_families"]
      and len(selected_traits&repro)>=design["descriptive_support_gates"]["minimum_distinct_reproductive_and_vegetative_trait_names_each"]
      and len(selected_traits&veg)>=design["descriptive_support_gates"]["minimum_distinct_reproductive_and_vegetative_trait_names_each"])
    same_eligible=[r for r in data.values() if r["cross_organ"] and r["qualifies_20_same_nonflora_dataset_species"]]
    result={
      "version":"v0.1","status":STATUS,
      "K_blind_source_eligibility_frozen_before_this_support_result":True,
      "original_graph":{"systems":254,"families":42,"traits":13},
      "original_pairs":760,"original_cross_organ_pairs":406,
      "original_species_system_cells":sum(actual.values()),
      "nonflora_eligible_species_system_cells":sum(no.values()),
      "excluded_five_electronic_floras":design["fixed_excluded_contributing_AusTraits_dataset_ids"],
      "subsets":by,
      "cross_organ_nonflora_supported_family_trait_pairs":sorted(eligible,key=lambda x:(x["family"],x["trait_A"],x["trait_B"])),
      "cross_organ_same_nonflora_dataset_supported_family_trait_pairs":sorted(same_eligible,key=lambda x:(x["family"],x["trait_A"],x["trait_B"])),
      "source_support_family_traits":{
          f:{"original_family_systems":sum(o["family"]==f for o in original.values()),
             "nonflora_positive_species_system_cells":sum(no[sid] for sid,o in original.items() if o["family"]==f)}
          for f in sorted({o["family"] for o in original.values()})},
      "source_only_exclusion_supported_for_descriptive_reestimation":bool(valid),
      "scientific_decision":"NONFLORA_SUPPORT_SUFFICIENT_FOR_POST_OUTCOME_K_SENSITIVITY" if valid else "HOLD_NONFLORA_PRIMARY_MEASUREMENT_SCOPE_NOT_ESTABLISHED",
      "same_nonflora_dataset_id_not_independent_original_measurements":True,
      "post_original_K_and_organ_outcomes":True,
      "no_K_effect_values_accessed_or_recomputed":True,
      "no_species_measurement_values_or_original_record_ids_exported":True,
      "nonclaim":"Five-flora source IDs are source compilations, not the only taxonomic/compiled records. Their exclusion changes phylogenetic tip eligibility and does NOT produce a genuinely independent measurement cohort. Any future paired-K reanalysis is exploratory."
    }
    return result


def main():
    p=argparse.ArgumentParser()
    for n in ("parquet","observed-K","core","traits-yml","original-pairs","original-source-design","design","out"):
        p.add_argument("--"+n,required=True,type=Path)
    a=p.parse_args()
    original=json.loads(a.__dict__["original_pairs"].read_text())
    cfg=json.loads(a.__dict__["original_source_design"].read_text())
    design=json.loads(a.design.read_text())
    excluded=check_design(design)
    candidates,systems,pairs,original_sys,rep,veg=read_inputs(
       a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],original,cfg)
    orig,no,rows=source_only_counts(a.parquet,candidates,pairs,excluded)
    result=adjudicate(orig,no,rows,original_sys,pairs,rep,veg,design)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,
      "cross_organ":result["subsets"]["cross_organ"],
      "fruit_vs_veg":result["subsets"]["fruit_vegetative"],
      "seed_vs_veg":result["subsets"]["seed_vegetative"],
      "eligible_for_reestimated_K":result["source_only_exclusion_supported_for_descriptive_reestimation"]},sort_keys=True))

if __name__=="__main__":main()
