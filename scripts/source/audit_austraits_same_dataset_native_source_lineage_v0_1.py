#!/usr/bin/env python3
"""Metadata-only provenance concentration in the frozen 279 same-dataset
reproductive-vs-vegetative AusTraits K comparisons.

Exact original native source species medians and both-trait positive source
record presence determine eligibility. NEVER uses K values to select/weight
sources, NEVER exports individual species, measurement IDs or trait values.
Every source description classification is provisional (flora/compilation/
measurement-annotated/unknown); no class is independent-source certification.
"""
from __future__ import annotations
import argparse,concurrent.futures,json,re,urllib.parse
from collections import defaultdict
from pathlib import Path
import duckdb,pandas as pd,requests,yaml
import sys

# Source and analytical audits have separate command-line entry directories.
# Keep the original frozen 279-pair eligibility function, not a copied rule.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from run_austraits_k_same_dataset_pair_batch_v0_1 import qualify

DESIGN="POST_ORGAN_K_SAME_SOURCE_DISCOVERY_NATIVE_PROVENANCE_AUDIT_EXPLORATORY_FROZEN"
STATUS="AUSTRAITS_279_COMMON_DATASET_NATIVE_SOURCE_PROVENANCE_AUDITED"

FLORA=re.compile(r"\b(?:flora|plantnet|species profile|taxonomic description|plant information network|herbarium species descriptions)\b",re.I)
COMPILED=re.compile(r"\b(?:database|compiled|compilation|collation|aggregated data|secondary source)\b",re.I)

def category(meta):
    src=(meta.get("source") or {}).get("primary") or {}
    d=meta.get("dataset") or {}
    if not isinstance(src,dict) or not isinstance(d,dict):
        raise ValueError("native source metadata missing citation/dataset fields")
    label=" | ".join(str(x or "") for x in (src.get("title"),d.get("description"),
                                                d.get("notes")))
    if FLORA.search(label):
        return "EXPLICIT_FLORISTIC_SPECIES_PROFILE_METADATA_INDICATOR"
    if COMPILED.search(label):
        return "EXPLICIT_DATABASE_OR_COMPILATION_METADATA_INDICATOR"
    basis=str(d.get("basis_of_record") or "").strip().lower()
    for_tr=[t for t in meta.get("traits",[]) if isinstance(t,dict)
            and t.get("trait_name") in ("fruit_height","fruit_length","fruit_width",
             "seed_dry_mass","seed_length","seed_width","leaf_area","leaf_length",
             "leaf_mass_per_area","leaf_width","petiole_length","plant_height")]
    if basis in ("field","preserved_specimen") and for_tr and all(
          str(t.get("basis_of_value") or "").lower()=="measurement" for t in for_tr):
        return "METADATA_CONSISTENT_WITH_DIRECT_MEASUREMENT_NOT_VALIDATED"
    return "SOURCE_MODALITY_UNDETERMINED_BY_PUBLIC_METADATA"

def metadata_one(dataset_id,commit):
    url=(f"https://raw.githubusercontent.com/traitecoevo/austraits.build/{commit}/data/"+
           urllib.parse.quote(dataset_id,safe="")+"/metadata.yml")
    response=requests.get(url,timeout=28,headers={"User-Agent":"turnover-native-trait-source-provenance/0.1"})
    response.raise_for_status()
    meta=yaml.safe_load(response.text)
    if not isinstance(meta,dict):raise ValueError("native source original metadata unavailable")
    src=(meta.get("source") or {}).get("primary") or {}
    data=meta.get("dataset") or {}
    traits=meta.get("traits") or []
    if not isinstance(src,dict) or not isinstance(data,dict) or not isinstance(traits,list):
        raise ValueError("malformed original source metadata")
    labels={}
    for t in traits:
        if isinstance(t,dict) and isinstance(t.get("trait_name"),str):
            labels.setdefault(t["trait_name"],set()).add(str(t.get("var_in") or ""))
    return {
      "dataset_id":dataset_id,
      "public_metadata_url":url,
      "source_citation_title":str(src.get("title") or "")[:350],
      "source_primary_doi":str(src.get("doi") or ""),
      "description":str(data.get("description") or "")[:650],
      "basis_of_record":str(data.get("basis_of_record") or ""),
      "provisional_source_modality":category(meta),
      "original_native_trait_variables":{k:sorted(v)[:8] for k,v in labels.items()},
      "original_source_dataset_id_may_combine_other_primary_studies":True,
      "same_specimen_or_protocol_verified":False,
      "independent_primary_measurement_verified":False
    }

def source_cells(parquet,unitfile,pairs):
    cfg=yaml.safe_load(Path(unitfile).read_text())["traits"]["elements"]
    systems={}
    for r in pairs:
        for side in ("A","B"):
            sid=r["system_"+side]
            obj={"family":r["family"],"trait":r["trait_"+side],"n":r["n_original_"+side]}
            if sid in systems and systems[sid]!=obj:raise ValueError("inconsistent original K system")
            systems[sid]=obj
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE cand(sid VARCHAR,family VARCHAR,trait VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO cand VALUES(?,?,?,?)",[
       (sid,z["family"],z["trait"],str(cfg[z["trait"]]["units"]).strip())
       for sid,z in systems.items()])
    con.execute("CREATE TEMP TABLE pairs(family VARCHAR,a VARCHAR,b VARCHAR,sa VARCHAR,sb VARCHAR)")
    con.executemany("INSERT INTO pairs VALUES(?,?,?,?,?)",[
        (r["family"],r["trait_A"],r["trait_B"],r["system_A"],r["system_B"])
        for r in pairs])
    try:
        con.execute(r"""
          CREATE TEMP TABLE d AS WITH base AS (
            SELECT c.sid,c.family,c.trait,
              trim(CAST(v.genus AS VARCHAR)) genus,
              trim(CAST(v.binomial AS VARCHAR)) species,
              trim(CAST(v.dataset_id AS VARCHAR)) ds,
              trim(CAST(v.observation_id AS VARCHAR)) obs,
              try_cast(trim(CAST(v.value AS VARCHAR)) AS DOUBLE) value_num,
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
          SELECT DISTINCT sid,family,trait,genus,species,ds,obs,value_num
          FROM base WHERE value_num IS NOT NULL AND isfinite(value_num)
                AND expected_unit<>'' AND native_unit=expected_unit
        """,[str(parquet)])
        con.execute("""
          CREATE TEMP TABLE native AS
          SELECT sid,family,trait,species,min(genus) AS genus
          FROM d GROUP BY sid,family,trait,species
          HAVING count(DISTINCT genus)=1 AND median(value_num)>0
        """)
        count=dict(con.execute("SELECT sid,count(*) FROM native GROUP BY sid").fetchall())
        if count!={sid:int(z["n"]) for sid,z in systems.items()}:
            raise ValueError("original K source-native species support changed")
        con.execute("""
          CREATE TEMP TABLE positive AS
          SELECT DISTINCT d.sid,d.species,d.genus,d.ds
          FROM d JOIN native n ON d.sid=n.sid AND d.species=n.species AND d.genus=n.genus
          WHERE d.value_num>0
        """)
        con.execute("""
          CREATE TEMP TABLE common_source AS
          SELECT DISTINCT p.family,p.a,p.b,A.species,A.ds
          FROM pairs p JOIN native na ON na.sid=p.sa
           JOIN native nb ON nb.sid=p.sb AND na.species=nb.species AND na.genus=nb.genus
          JOIN positive A ON A.sid=p.sa AND A.species=na.species AND A.genus=na.genus
          JOIN positive B ON B.sid=p.sb AND B.species=na.species AND B.genus=na.genus AND B.ds=A.ds
        """)
        pair_cnt=con.execute("""
          SELECT family,a,b,count(DISTINCT species) FROM common_source
          GROUP BY family,a,b ORDER BY family,a,b
        """).fetchall()
        by_ds=con.execute("""
          SELECT ds,count(*) AS pair_species_cells,
                 count(DISTINCT family||chr(31)||a||chr(31)||b) AS family_trait_pairs,
                 count(DISTINCT family) AS families
          FROM common_source GROUP BY ds ORDER BY pair_species_cells DESC,ds
        """).fetchall()
        dataset_size=con.execute("""
          SELECT count(*) n_species_pair_cells,
             sum(CASE WHEN n_sources>1 THEN 1 ELSE 0 END) n_multi_source_cells
          FROM (
            SELECT family,a,b,species,count(*) n_sources FROM common_source
            GROUP BY family,a,b,species
          )
        """).fetchone()
        return pair_cnt,by_ds,dataset_size
    finally:con.close()

def summarize(pair_cnt,by_ds,dataset_size,pairs,metas):
    expected={(r["family"],r["trait_A"],r["trait_B"]):r["n_same_AusTraits_dataset_species"]
             for r in pairs}
    seen={}
    for f,a,b,n in pair_cnt:
        k=(f,a,b)
        if k in seen or k not in expected:raise ValueError("unknown or duplicate original same-source pair")
        if int(n)!=int(expected[k]):raise ValueError(f"source-count changed from K-blind eligibility: {k}")
        seen[k]=int(n)
    if set(seen)!=set(expected) or len(seen)!=279:
        raise ValueError("missing original 279 K-blind source pair population")
    if len(metas)!=len(by_ds):raise ValueError("missing native source metadata for contributing studies")
    total,multi=map(int,dataset_size)
    if total!=sum(seen.values()) or not 0<=multi<=total:
        raise ValueError("source species×pair support cells changed")
    derived=[]
    for ds,cells,npairs,nfams in by_ds:
        meta=metas.get(str(ds))
        if meta is None:raise ValueError("original public metadata unavailable for a source")
        derived.append({**meta,
          "n_species_pair_support_cells":int(cells),
          "n_family_trait_pairs":int(npairs),
          "n_families":int(nfams),
          "fraction_of_unique_pair_species_cells_with_dataset":float(cells/total)})
    modalities=defaultdict(lambda:{"dataset_ids":0,"species_pair_source_links":0})
    for row in derived:
        cls=row["provisional_source_modality"]
        modalities[cls]["dataset_ids"]+=1
        modalities[cls]["species_pair_source_links"]+=row["n_species_pair_support_cells"]
    return {
      "version":"v0.1","status":STATUS,
      "all_original_279_K_blind_source_qualified_family_pair_counts_reproduced":True,
      "n_source_eligible_family_trait_pairs":279,
      "n_source_positive_species_pair_cells":total,
      "n_cells_with_multiple_shared_original_dataset_ids":multi,
      "fraction_cells_with_multiple_shared_dataset_ids":multi/total,
      "n_original_contributing_AusTraits_dataset_IDs":len(derived),
      "provisional_metadata_modality_counts":dict(modalities),
      "source_concentration_by_original_dataset":derived,
      "K_effects_reestimated_or_source_selected_from_K":False,
      "raw_species_observation_or_measurement_values_exported":False,
      "independent_source_or_specimen_confirmed":False,
      "scientific_boundary":"Flora or compilation source metadata indicates publication lineage, NOT absence of original observation, true identity of plant organ, or independence. Classification based on native public metadata, selected after biological discovery; no new K effects tested."
    }

def main():
    p=argparse.ArgumentParser()
    for n in ("parquet","traits-yml","source-support","original-pair-support","design","out"):
        p.add_argument("--"+n,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    if design.get("status")!=DESIGN:
        raise ValueError("source provenance modality contract not frozen")
    source=json.loads(a.__dict__["source_support"].read_text())
    original=json.loads(a.__dict__["original_pair_support"].read_text())
    # This source-only eligibility was already fixed before source K outcome.
    base_design=json.loads(Path("data/austraits_k_same_dataset_organ_matched_tip_sensitivity_v0_1.json").read_text())
    pairs=qualify(source,original,base_design)
    pair_cnt,by_ds,n=source_cells(a.parquet,a.__dict__["traits_yml"],pairs)
    ids=[str(z[0]) for z in by_ds]
    commit=design["inputs"]["native_metadata_commit"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        rows=list(pool.map(lambda ds:metadata_one(ds,commit),ids))
    meta={r["dataset_id"]:r for r in rows}
    result=summarize(pair_cnt,by_ds,n,pairs,meta)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,
       "sources":result["n_original_contributing_AusTraits_dataset_IDs"],
       "pair_species_cells":result["n_source_positive_species_pair_cells"],
       "modalities":result["provisional_metadata_modality_counts"]},sort_keys=True))
if __name__=="__main__":main()
