#!/usr/bin/env python3
"""Pre-K-output matched-species trait-pair support audit for the original 254
AusTraits phylogenetic K systems.

Only input species/source-trait identity and source-native positive eligibility
are read. Outputs contain family×trait-pair COUNTS, never species names, trait
values, observed K, numerical tree metrics, or phylogenetic K predictions.
"""
from __future__ import annotations
import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

import duckdb
import pandas as pd
import yaml

STATUS = "AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"
DESIGN = "POST_EMPIRICAL_K_AND_SOURCE_DIAGNOSTICS_PRE_SHARED_TAXON_OVERLAP_RESULTS_FROZEN"


def graph_from_original(kframe,coreframe,units,design):
    if design.get("status")!=DESIGN:
        raise ValueError("shared-tip source support protocol not frozen")
    if (len(kframe),kframe.family.nunique(),kframe.trait_name.nunique())!=(254,42,13):
        raise ValueError("changed original 254-system K graph")
    merged=kframe.merge(coreframe,on=["family","trait_name"],validate="one_to_one")
    if len(merged)!=254 or merged.system_id.nunique()!=254:
        raise ValueError("invalid original core system join")
    cfg=yaml.safe_load(Path(units).read_text())["traits"]["elements"]
    all_expected={}
    candidates=[]
    for row in merged.itertuples(index=False):
        unit=cfg[row.trait_name].get("units")
        if not unit or not str(unit).strip():
            raise ValueError("unidentified original source-native trait unit")
        sid=str(row.system_id)
        all_expected[sid]={
            "family":str(row.family),"trait":str(row.trait_name),
            "n_original":int(row.n_input_species)}
        candidates.append((sid,str(row.family),str(row.trait_name),str(unit).strip()))
    named=set(design["source"]["expected_named_traits"])
    if named!=set(kframe.trait_name)-{"seed_height"} or len(named)!=12:
        raise ValueError("named trait cohort differs from frozen 12")
    selected=merged[merged.trait_name.isin(named)]
    if (len(selected),selected.family.nunique(),selected.trait_name.nunique())!=(249,42,12):
        raise ValueError("source-eligible original 249-system subgraph changed")
    pairs=[]
    for family,g in selected.groupby("family"):
        ordered=sorted((str(r.trait_name),str(r.system_id)) for r in g.itertuples(index=False))
        for (a,sa),(b,sb) in itertools.combinations(ordered,2):
            pairs.append((family,a,b,sa,sb))
    if not pairs:raise ValueError("no original same-family trait pairs")
    return candidates,all_expected,pairs,sorted(named)


def audit_support(count_rows,pair_rows,expected,pairs,traits,design):
    n_original={}
    for sid,n in count_rows:
        sid=str(sid)
        if sid in n_original or sid not in expected:
            raise ValueError("duplicate/unexpected original K system")
        if int(n)!=expected[sid]["n_original"]:
            raise ValueError(f"original input species support mutated: {sid}")
        n_original[sid]=int(n)
    if set(n_original)!=set(expected):
        raise ValueError("lost original 254 system species cohort")
    pair_id={(fam,a,b):(sa,sb) for fam,a,b,sa,sb in pairs}
    by_pair={}
    totals=defaultdict(lambda:{"present_families":0,"families_20_species":0,
                               "common_species_cells":0,"genus_conflict_species_cells":0})
    qualifying=[]
    minimum=int(design["eligibility"]["min_shared_original_species_for_R_tree"])
    if minimum!=20:raise ValueError("source-blind shared taxon minimum changed")
    for fam,a,b,sa,sb,ncommon,nconflict in pair_rows:
        key=(str(fam),str(a),str(b))
        if key in by_pair or key not in pair_id:
            raise ValueError("duplicate or unexpected family×trait pair")
        if (str(sa),str(sb))!=pair_id[key]:
            raise ValueError("pair system IDs changed after freezing original graph")
        ncommon=int(ncommon);nconflict=int(nconflict)
        if min(ncommon,nconflict)<0 or ncommon+nconflict>min(n_original[sa],n_original[sb]):
            raise ValueError("impossible shared species/genus support counts")
        row={"family":str(fam),"trait_A":str(a),"trait_B":str(b),
             "system_A":str(sa),"system_B":str(sb),
             "n_common_species_same_genus":ncommon,
             "n_common_binomial_conflicting_genus":nconflict,
             "n_original_A":n_original[sa],"n_original_B":n_original[sb],
             "qualifies_20_common_species":ncommon>=minimum}
        by_pair[key]=row
        totals[(a,b)]["present_families"]+=1
        totals[(a,b)]["families_20_species"]+=ncommon>=minimum
        totals[(a,b)]["common_species_cells"]+=ncommon
        totals[(a,b)]["genus_conflict_species_cells"]+=nconflict
        if ncommon>=minimum:qualifying.append(row)
    if set(by_pair)!=set(pair_id):
        raise ValueError("not all original family trait pair counts recovered")
    summaries={}
    for a,b in itertools.combinations(traits,2):
        z=totals[(a,b)]
        summaries[a+"__"+b]={
            "trait_A":a,"trait_B":b,
            **z,
            "qualifies_multi_family_descriptive_comparison":
                z["families_20_species"]>=design["eligibility"]["pair_level_generalization_min_families"]
        }
    if len(summaries)!=66:raise ValueError("incomplete 12-trait pair universe")
    return {
       "version":"v0.1","status":STATUS,
       "scientific_status":"POST_K_OUTCOME_SOURCE_SUPPORT_ONLY_NO_MATCHED_K_MEASURED",
       "original_graph":{"systems":254,"families":42,"traits":13},
       "named_graph":{"systems":249,"families":42,"traits":12},
       "minimum_common_species":minimum,
       "total_family_trait_pairs_present":len(by_pair),
       "qualifying_family_trait_pairs":len(qualifying),
       "qualifying_pair_types":sum(v["families_20_species"]>0 for v in summaries.values()),
       "pair_types_with_at_least_5_qualified_families":
           sum(v["qualifies_multi_family_descriptive_comparison"] for v in summaries.values()),
       "trait_pairs":summaries,
       "family_trait_pair_support":list(by_pair.values()),
       "no_K_effect_magnitudes_opened":True,
       "no_species_or_trait_values_persisted":True,
       "external_independent_validation":False,
       "scientific_boundary":"Pairwise shared tips control geometry within comparisons only; pair-specific intersections differ across comparisons and cannot be pooled as a full 12-trait ranking."
    }


def main():
    p=argparse.ArgumentParser()
    for key in ("parquet","core","observed-K","traits-yml","design","out"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    k=pd.read_csv(a.__dict__["observed_K"],usecols=["system_id","family","trait_name"])
    core=pd.read_csv(a.core,usecols=["family","trait_name","n_input_species"])
    candidates,expected,pairs,traits=graph_from_original(k,core,a.__dict__["traits_yml"],design)
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE candidates(system_id VARCHAR,family_name VARCHAR,trait_name VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO candidates VALUES (?,?,?,?)",candidates)
    con.execute("CREATE TEMP TABLE pairs(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR,system_A VARCHAR,system_B VARCHAR)")
    con.executemany("INSERT INTO pairs VALUES (?,?,?,?,?)",pairs)
    query=r"""
    CREATE TEMP TABLE source_states AS
    WITH base AS (
      SELECT c.system_id,c.family_name,c.trait_name,
        trim(CAST(a.genus AS VARCHAR)) AS genus,
        trim(CAST(a.binomial AS VARCHAR)) AS species,
        trim(CAST(a.dataset_id AS VARCHAR)) AS dataset_id,
        trim(CAST(a.observation_id AS VARCHAR)) AS observation_id,
        try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) AS value_num,
        c.unit AS expected_unit,
        coalesce(trim(CAST(a.unit AS VARCHAR)),'') AS source_unit
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
      SELECT DISTINCT system_id,family_name,trait_name,genus,species,
        dataset_id,observation_id,value_num FROM base
      WHERE value_num IS NOT NULL AND isfinite(value_num)
        AND expected_unit<>'' AND source_unit=expected_unit
    )
    SELECT system_id,family_name,trait_name,species,min(genus) AS genus
    FROM dedup
    GROUP BY system_id,family_name,trait_name,species
    HAVING count(DISTINCT genus)=1 AND median(value_num)>0
    """
    try:
        con.execute(query,[str(a.parquet)])
        count_rows=con.execute(
            "SELECT system_id,count(*) FROM source_states GROUP BY system_id").fetchall()
        pair_rows=con.execute("""
          SELECT p.family,p.trait_A,p.trait_B,p.system_A,p.system_B,
            count(*) FILTER(WHERE a.genus=b.genus AND b.species IS NOT NULL) AS n_common,
            count(*) FILTER(WHERE a.genus<>b.genus AND b.species IS NOT NULL) AS n_conflicts
          FROM pairs p
          LEFT JOIN source_states a ON p.system_A=a.system_id
          LEFT JOIN source_states b ON p.system_B=b.system_id AND a.species=b.species
          GROUP BY p.family,p.trait_A,p.trait_B,p.system_A,p.system_B
          ORDER BY p.family,p.trait_A,p.trait_B
        """).fetchall()
    finally:
        con.close()
    report=audit_support(count_rows,pair_rows,expected,pairs,traits,design)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in
          ("status","total_family_trait_pairs_present","qualifying_family_trait_pairs",
           "qualifying_pair_types","pair_types_with_at_least_5_qualified_families")},sort_keys=True))

if __name__=="__main__":main()
