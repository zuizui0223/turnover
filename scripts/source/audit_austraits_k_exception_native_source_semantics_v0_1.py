#!/usr/bin/env python3
"""Post-outcome exception-family original AusTraits metadata/ontology inspection.

Read ONLY original finite-native-unit record eligibility to discover which
public contributing source dataset IDs provided both leaf length and fruit
length for a common originally K-eligible species. Fetch the original public
source methods, not new phenotypic outcomes. Any leaf-scale/branchlet or
fruit/samara/infructescence ontology remains UNVERIFIED unless documented.
"""
from __future__ import annotations
import argparse,json,urllib.parse
from pathlib import Path
from collections import defaultdict
import duckdb,requests,yaml

STATUS="AUSTRAITS_K_EXCEPTION_ORGAN_NATIVE_SOURCE_METADATA_AUDITED"
DESIGN="POST_DISCOVERY_EXCEPTION_FAMILIES_PRE_NATIVE_SOURCE_METADATA_AUDIT_FROZEN"

def query_source_ids(parquet,units,design):
    if design.get("status")!=DESIGN or not design.get("pre_K_output_only"):
        raise ValueError("source trait ontology metadata audit not frozen")
    targets=design["family_trait_pairs"]
    if {t["family"] for t in targets}!={"Casuarinaceae","Rubiaceae","Fabaceae"} or len(targets)!=3:
        raise ValueError("exception/reference family identities changed")
    cfg=yaml.safe_load(Path(units).read_text())["traits"]["elements"]
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE targets(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR)")
    con.executemany("INSERT INTO targets VALUES(?,?,?)",
       [(x["family"],x["trait_A"],x["trait_B"]) for x in targets])
    con.execute("CREATE TEMP TABLE cand(family VARCHAR,trait VARCHAR,unit VARCHAR)")
    cand=[]
    for x in targets:
        for t in (x["trait_A"],x["trait_B"]):
            u=cfg[t].get("units")
            if not u or not str(u).strip():
                raise ValueError("original source-native unit absent")
            cand.append((x["family"],t,str(u).strip()))
    if len(set(cand))!=len(cand):raise ValueError("duplicate source-native family trait")
    con.executemany("INSERT INTO cand VALUES(?,?,?)",cand)
    try:
        con.execute(r"""
        CREATE TEMP TABLE dedup AS
        WITH base AS (
           SELECT c.family,c.trait,
              trim(CAST(a.genus AS VARCHAR)) genus,
              trim(CAST(a.binomial AS VARCHAR)) species,
              trim(CAST(a.dataset_id AS VARCHAR)) dataset_id,
              trim(CAST(a.observation_id AS VARCHAR)) observation_id,
              try_cast(trim(CAST(a.value AS VARCHAR)) AS DOUBLE) val,
              c.unit expected_unit,
              coalesce(trim(CAST(a.unit AS VARCHAR)),'') native_unit
           FROM read_parquet(?) a JOIN cand c
            ON trim(CAST(a.family AS VARCHAR))=c.family
           AND trim(CAST(a.trait_name AS VARCHAR))=c.trait
           WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
             AND a.genus IS NOT NULL AND trim(CAST(a.genus AS VARCHAR))<>''
             AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
             AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
             AND a.observation_id IS NOT NULL AND trim(CAST(a.observation_id AS VARCHAR))<>''
             AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
        )
        SELECT DISTINCT family,trait,genus,species,dataset_id,observation_id,val
        FROM base WHERE val IS NOT NULL AND isfinite(val) AND expected_unit<>''
             AND native_unit=expected_unit
        """,[str(parquet)])
        con.execute("""
        CREATE TEMP TABLE positive_states AS
        SELECT family,trait,species,min(genus) AS genus
        FROM dedup GROUP BY family,trait,species
        HAVING count(DISTINCT genus)=1 AND median(val)>0
        """)
        con.execute("""
        CREATE TEMP TABLE positive_original AS
        SELECT DISTINCT d.family,d.trait,d.species,d.genus,
                        d.dataset_id,d.observation_id
        FROM dedup d JOIN positive_states p
         ON d.family=p.family AND d.trait=p.trait
           AND d.species=p.species AND d.genus=p.genus
        WHERE d.val>0
        """)
        rows=con.execute("""
          SELECT t.family,t.trait_A,t.trait_B,a.dataset_id,
            count(DISTINCT a.species) AS n_species_per_shared_dataset
          FROM targets t
          JOIN positive_original a
           ON a.family=t.family AND a.trait=t.trait_A
          JOIN positive_original b
           ON b.family=t.family AND b.trait=t.trait_B
            AND a.species=b.species AND a.genus=b.genus
            AND a.dataset_id=b.dataset_id
          GROUP BY t.family,t.trait_A,t.trait_B,a.dataset_id
          ORDER BY t.family,n_species_per_shared_dataset DESC,a.dataset_id
        """).fetchall()
        unions=con.execute("""
          SELECT family,trait_A,trait_B,count(*) AS shared_distinct_species
          FROM (
            SELECT DISTINCT t.family,t.trait_A,t.trait_B,a.species
            FROM targets t
            JOIN positive_original a
             ON a.family=t.family AND a.trait=t.trait_A
            JOIN positive_original b
             ON b.family=t.family AND b.trait=t.trait_B
              AND a.species=b.species AND a.genus=b.genus
              AND a.dataset_id=b.dataset_id
          ) q GROUP BY family,trait_A,trait_B
          ORDER BY family
        """).fetchall()
    finally:con.close()
    union={(f,a,b):int(n) for f,a,b,n in unions}
    expected={(z["family"],z["trait_A"],z["trait_B"]):z["original_source_shared_species"] for z in targets}
    if union!=expected:
        raise ValueError(f"changed original positive shared-DatasetID support: {union} vs {expected}")
    results={}
    for f,a,b,ds,n in rows:
        key=f+"__"+a+"__"+b
        results.setdefault(key,[]).append({"original_AusTraits_dataset_id":str(ds),
              "n_positive_pair_species_from_dataset":int(n)})
    return results,sorted({str(x[3]) for x in rows})

def fetch_native_public_metadata(ids,traits,commit):
    cached={}
    root=f"https://raw.githubusercontent.com/traitecoevo/austraits.build/{commit}/data/"
    for ds in ids:
        if ds in cached:continue
        url=root+urllib.parse.quote(ds,safe="")+"/metadata.yml"
        r=requests.get(url,timeout=30,headers={"User-Agent":"turnover-source-ontology-audit/0.1"})
        r.raise_for_status()
        x=yaml.safe_load(r.text)
        if not isinstance(x,dict):raise ValueError("native source metadata is not YAML dict")
        src=(x.get("source") or {}).get("primary") or {}
        dataset=x.get("dataset") or {}
        if not isinstance(src,dict) or not isinstance(dataset,dict):
            raise ValueError("original data source metadata schema unexpectedly changed")
        matched=[]
        for trait in x.get("traits",[]) or []:
            if isinstance(trait,dict) and trait.get("trait_name") in traits:
                matched.append({
                  "trait_name":str(trait.get("trait_name")),
                  "original_variable_name":str(trait.get("var_in") or ""),
                  "original_variable_unit":str(trait.get("unit_in") or ""),
                  "measurement_methods":str(trait.get("methods") or "")[:2500],
                  "entity_type":str(trait.get("entity_type") or ""),
                  "value_type":str(trait.get("value_type") or ""),
                  "replicates":str(trait.get("replicates") or "")
                })
        cached[ds]={
          "original_dataset_id":ds,
          "original_dataset_metadata_url":url,
          "original_primary_citation_title":str(src.get("title") or "")[:500],
          "original_primary_author":str(src.get("author") or "")[:400],
          "original_primary_DOI":str(src.get("doi") or ""),
          "dataset_description":str(dataset.get("description") or "")[:1200],
          "source_contains_individual_organ_definition":bool(matched),
          "traits":matched,
          "homology_and_measurement_protocol_verified":False
        }
    return cached

def main():
    p=argparse.ArgumentParser()
    for k in ("parquet","traits-yml","design","out"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    source,ids=query_source_ids(a.parquet,a.__dict__["traits_yml"],design)
    metadata=fetch_native_public_metadata(ids,
         {"fruit_length","leaf_length"},
         design["source_reference"]["original_source_build_commit"])
    for key,rr in source.items():
        for row in rr:
            if row["original_AusTraits_dataset_id"] not in metadata:
                raise ValueError("published native source metadata missing")
            row["published_source_metadata"]=metadata[row["original_AusTraits_dataset_id"]]
    summary={
     "version":"v0.1","status":STATUS,
     "source_exception_pairs_selected_after_original_K_discovery":True,
     "original_selected_family_pairs":len(design["family_trait_pairs"]),
     "all_three_original_shared_positive_species_counts_reproduced":True,
     "total_original_AusTraits_dataset_IDs_with_public_native_metadata":len(metadata),
     "pairs":source,
     "no_trait_state_values_or_species_names_persisted":True,
     "K_effects_read_or_reestimated":False,
     "publication_linkage_not_identical_specimen_evidence":True,
     "scientific_boundary":"Family trait pairing and original-study interpretation were selected after the organ-K observation; original methods and homology must be manually assessed. Shared dataset record IDs never guarantee same physical specimen or identical protocol."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,
         "datasets_with_native_public_metadata":len(metadata),
         "pairs":{k:len(v) for k,v in source.items()}},sort_keys=True))
if __name__=="__main__":main()
