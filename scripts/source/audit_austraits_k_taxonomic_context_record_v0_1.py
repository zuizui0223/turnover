#!/usr/bin/env python3
"""Original AusTraits K-eligible floristic record method-context validity check.

Read ORIGINAL 254 species/rank/native-unit phenotype source records only to
reconstruct eligible species and identify whether a positive original numeric
record used for K has a method_context_properties label inferred from genus,
family, taxonomy, species, another trait or scored directly from species text.

NEVER outputs species, observations, numeric K or source measurements. Never
concludes that context label absence proves independently measured organisms.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import duckdb,pandas as pd,yaml

STATUS="AUSTRAITS_K_NATIVE_TAXONOMIC_INFERENCE_CONTEXT_AUDITED"
DESIGN="POST_ORGAN_K_SOURCE_PROVENANCE_PRE_NATIVE_CONTEXT_COUNTS_FROZEN"
FIELDS=("from_family","from_genus","from_taxonomy","from_species","from_trait","scored_text","higher_taxon")

def prepare(observed,core,units,design):
    if design.get("status")!=DESIGN:
        raise ValueError("post-outcome original K input audit protocol missing")
    x=pd.read_csv(observed,usecols=["system_id","family","trait_name"])
    c=pd.read_csv(core,usecols=["family","trait_name","n_input_species"])
    if (len(x),x.family.nunique(),x.trait_name.nunique())!=(254,42,13):
        raise ValueError("original 254 original trait/family K source graph changed")
    allx=x.merge(c,on=["family","trait_name"],validate="one_to_one")
    if len(allx)!=254 or allx.system_id.nunique()!=254:
        raise ValueError("original source-system identity changed")
    cfg=yaml.safe_load(Path(units).read_text())["traits"]["elements"]
    expected={}
    cand=[]
    for z in allx.itertuples(index=False):
        unit=cfg[z.trait_name].get("units")
        if not unit or not str(unit).strip():
            raise ValueError("source-native unit missing")
        sid=str(z.system_id)
        expected[sid]={"family":str(z.family),
                       "trait":str(z.trait_name),"n":int(z.n_input_species)}
        cand.append((sid,str(z.family),str(z.trait_name),str(unit).strip()))
    if sum(z["n"] for z in expected.values())!=66330:
        raise ValueError("pinned original eligible source-native species support changed")
    return cand,expected

def fetch_counts(parquet,candidates,design):
    flora_ids=design["source_ids"]
    named=design["target_traits"]
    if len(flora_ids)!=5 or len(set(flora_ids))!=5 or len(named)!=12 or len(set(named))!=12:
        raise ValueError("five original provenance families or 12 source-calibrated target traits changed")
    con=duckdb.connect(":memory:")
    con.execute("CREATE TEMP TABLE cand(sid VARCHAR,family VARCHAR,trait VARCHAR,unit VARCHAR)")
    con.executemany("INSERT INTO cand VALUES(?,?,?,?)",candidates)
    con.execute("CREATE TEMP TABLE audited_sources(ds VARCHAR)")
    con.executemany("INSERT INTO audited_sources VALUES (?)",[(ds,) for ds in flora_ids])
    try:
        con.execute(r"""
          CREATE TEMP TABLE base AS
          SELECT c.sid,c.family,c.trait,
            trim(CAST(v.genus AS VARCHAR)) genus,
            trim(CAST(v.binomial AS VARCHAR)) species,
            trim(CAST(v.dataset_id AS VARCHAR)) ds,
            trim(CAST(v.observation_id AS VARCHAR)) obs,
            try_cast(trim(CAST(v.value AS VARCHAR)) AS DOUBLE) numeric_value,
            lower(coalesce(trim(CAST(v.method_context_properties AS VARCHAR)),'')) AS context,
            c.unit expected_unit,
            coalesce(trim(CAST(v.unit AS VARCHAR)),'') AS source_unit
          FROM read_parquet(?) v
          JOIN cand c ON trim(CAST(v.family AS VARCHAR))=c.family
            AND trim(CAST(v.trait_name AS VARCHAR))=c.trait
          WHERE lower(trim(CAST(v.taxon_rank AS VARCHAR)))='species'
            AND v.genus IS NOT NULL AND trim(CAST(v.genus AS VARCHAR))<>''
            AND v.binomial IS NOT NULL AND trim(CAST(v.binomial AS VARCHAR))<>''
            AND v.dataset_id IS NOT NULL AND trim(CAST(v.dataset_id AS VARCHAR))<>''
            AND v.observation_id IS NOT NULL AND trim(CAST(v.observation_id AS VARCHAR))<>''
            AND v.value IS NOT NULL AND trim(CAST(v.value AS VARCHAR))<>''
        """,[str(parquet)])
        con.execute("""
          CREATE TEMP TABLE eligible_base AS
          SELECT DISTINCT sid,family,trait,genus,species,ds,obs,numeric_value
          FROM base
          WHERE numeric_value IS NOT NULL AND isfinite(numeric_value)
            AND expected_unit<>'' AND source_unit=expected_unit
        """)
        con.execute("""
          CREATE TEMP TABLE original_species AS
          SELECT sid,family,trait,species,min(genus) AS genus
          FROM eligible_base GROUP BY sid,family,trait,species
          HAVING count(DISTINCT genus)=1 AND median(numeric_value)>0
        """)
        per_original=con.execute(
          "SELECT sid,count(*) FROM original_species GROUP BY sid").fetchall()
        # Context flags must be collapsed at original unique source record key
        # so repeat metadata context records do not create false replicates.
        con.execute("""
          CREATE TEMP TABLE positive_flora_keys AS
          SELECT b.sid,b.family,b.trait,b.genus,b.species,b.ds,b.obs,b.numeric_value,
            max(CASE WHEN b.context LIKE '%inferred_from_family%' THEN 1 ELSE 0 END) AS from_family,
            max(CASE WHEN b.context LIKE '%inferred_from_genus%' THEN 1 ELSE 0 END) AS from_genus,
            max(CASE WHEN b.context LIKE '%inferred_from_taxonomy%' THEN 1 ELSE 0 END) AS from_taxonomy,
            max(CASE WHEN b.context LIKE '%inferred_from_species%' THEN 1 ELSE 0 END) AS from_species,
            max(CASE WHEN b.context LIKE '%inferred_from_trait%' THEN 1 ELSE 0 END) AS from_trait,
            max(CASE WHEN b.context LIKE '%scored from text%' OR b.context LIKE '%scored_from_text%' THEN 1 ELSE 0 END) AS scored_text,
            max(CASE WHEN length(b.context)>2 THEN 1 ELSE 0 END) AS nonempty_context
          FROM base b
          JOIN original_species v ON b.sid=v.sid
              AND b.species=v.species AND b.genus=v.genus
          JOIN audited_sources ds ON b.ds=ds.ds
          WHERE b.trait<>'seed_height'
             AND b.numeric_value IS NOT NULL AND isfinite(b.numeric_value)
             AND b.numeric_value>0
             AND b.expected_unit<>'' AND b.source_unit=b.expected_unit
          GROUP BY b.sid,b.family,b.trait,b.genus,b.species,b.ds,b.obs,b.numeric_value
        """)
        con.execute("""
          CREATE TEMP TABLE flagged AS
          SELECT *,CASE WHEN from_family=1 OR from_genus=1 OR from_taxonomy=1
             THEN 1 ELSE 0 END AS higher_taxon
          FROM positive_flora_keys
        """)
        rows=con.execute("""
          SELECT ds,trait,count(*) AS n_positive_record_keys,
            count(DISTINCT sid||chr(31)||species) AS n_species_system_cells,
            count(DISTINCT sid) AS n_family_trait_systems,
            count(DISTINCT family) AS n_families,
            sum(from_family),sum(from_genus),sum(from_taxonomy),
            sum(from_species),sum(from_trait),sum(scored_text),
            sum(higher_taxon),sum(nonempty_context),
            count(DISTINCT CASE WHEN higher_taxon=1
               THEN sid||chr(31)||species ELSE NULL END)
          FROM flagged GROUP BY ds,trait
          ORDER BY ds,trait
        """).fetchall()
        return per_original,rows
    finally:
        con.close()

def audit(original_counts,flagged_counts,expected,design):
    original={}
    for sid,n in original_counts:
        if sid not in expected or sid in original or int(n)!=expected[sid]["n"]:
            raise ValueError("original native species graph not reconstructed")
        original[sid]=int(n)
    if set(original)!=set(expected):
        raise ValueError("missing some of 254 original K-support systems")
    flora=set(design["source_ids"])
    traits=set(design["target_traits"])
    rows=[]
    for (ds,tr,record_count,cells,systems,families,
         family,genus,taxonomy,species,other_trait,scored_text,
         higher,nonempty,higher_cells) in flagged_counts:
        if ds not in flora or tr not in traits:
            raise ValueError("unrecognized source or morphology trait")
        values=list(map(int,(record_count,cells,systems,families,family,
                        genus,taxonomy,species,other_trait,scored_text,
                        higher,nonempty,higher_cells)))
        if any(v<0 for v in values) or not 0<=higher<=record_count:
            raise ValueError("impossible native context record counts")
        if not 0<=higher_cells<=cells or any(int(v)>int(record_count)
            for v in (family,genus,taxonomy,species,other_trait,scored_text,higher,nonempty)):
            raise ValueError("invalid context positive record counts")
        rows.append({
           "source_dataset_id":ds,"trait_name":tr,
           "n_original_positive_record_value_keys":int(record_count),
           "n_original_positive_species_system_cells":int(cells),
           "n_family_trait_systems":int(systems),"n_families":int(families),
           "n_inferred_from_family_records":int(family),
           "n_inferred_from_genus_records":int(genus),
           "n_inferred_from_taxonomy_records":int(taxonomy),
           "n_inferred_from_species_records":int(species),
           "n_inferred_from_other_trait_records":int(other_trait),
           "n_scored_from_text_records":int(scored_text),
           "n_any_higher_taxon_inference_records":int(higher),
           "n_any_higher_taxon_inference_species_system_cells":int(higher_cells),
           "n_nonempty_method_context_records":int(nonempty)
        })
    if not rows:raise ValueError("no positive original flora K records")
    out={
      "version":"v0.1","status":STATUS,
      "original_254_K_native_species_state_graph_recovered":True,
      "original_graph":{"systems":254,"families":42,"traits":13,"source_calibratable_traits":12},
      "audited_floristic_dataset_ids":sorted(flora),
      "native_method_context_field":"method_context_properties",
      "total_original_positive_source_record_value_keys":sum(r["n_original_positive_record_value_keys"] for r in rows),
      "total_higher_taxon_inference_flagged_original_positive_source_records":sum(r["n_any_higher_taxon_inference_records"] for r in rows),
      "total_original_positive_source_record_keys_with_method_context":sum(r["n_nonempty_method_context_records"] for r in rows),
      "trait_dataset_results":rows,
      "after_original_K_and_organ_discovery":True,
      "K_reestimated_or_selected_using_context":False,
      "species_names_measurement_values_or_ids_exported":False,
      "scientific_nonclaim":"Categories refer only to actually present native method_context_properties of ORIGINAL K-eligible positive record values; unknown context does not prove non-inference, species data from flora descriptions are not independently measured organisms, and no evolutionary process or K outcome follows from this source-only incidence."
    }
    return out

def positive_control_all_trait_contexts(parquet,design):
    """Verify the native method-context text can actually expose higher-taxon
    inference in ALL original trait records, not only the 12 numerical K
    traits. This QA does not open or report trait values/species identities.
    """
    sources=list(design["source_ids"])
    if len(sources)!=5:
        raise ValueError("not the fixed five floristic sources")
    con=duckdb.connect(":memory:")
    placeholders=",".join(["?"]*len(sources))
    query=f"""
       SELECT trim(CAST(dataset_id AS VARCHAR)) ds,
         count(*) n_all_original_trait_records,
         sum(CASE WHEN lower(coalesce(method_context_properties,'')) LIKE '%inferred_from_genus%' THEN 1 ELSE 0 END) genus,
         sum(CASE WHEN lower(coalesce(method_context_properties,'')) LIKE '%inferred_from_family%' THEN 1 ELSE 0 END) AS family_infer,
         sum(CASE WHEN lower(coalesce(method_context_properties,'')) LIKE '%inferred_from_taxonomy%' THEN 1 ELSE 0 END) taxonomy,
         sum(CASE WHEN lower(coalesce(method_context_properties,'')) LIKE '%scored from text%' THEN 1 ELSE 0 END) scored,
         sum(CASE WHEN length(coalesce(method_context_properties,''))>2 THEN 1 ELSE 0 END) nonempty
       FROM read_parquet(?)
       WHERE trim(CAST(dataset_id AS VARCHAR)) IN ({placeholders})
       GROUP BY ds ORDER BY ds
    """
    try:
        rows=con.execute(query,[str(parquet)]+sources).fetchall()
    finally:con.close()
    if len(rows)!=5:
        raise ValueError("original source context control lost source dataset")
    result={}
    for ds,n,g,f,t,s,c in rows:
        result[ds]={
          "all_record_types_count":int(n),
          "records_with_genus_inference_label":int(g),
          "records_with_family_inference_label":int(f),
          "records_with_taxonomic_inference_label":int(t),
          "records_with_scored_text_label":int(s),
          "records_with_nonempty_method_context":int(c)}
    result["positive_control_higher_taxon_labels_detected_elsewhere"]=bool(
       sum(r["records_with_genus_inference_label"]+
           r["records_with_family_inference_label"]+
           r["records_with_taxonomic_inference_label"] for r in result.values())>0)
    return result


def main():
    p=argparse.ArgumentParser()
    for arg in ("parquet","observed-K","core","traits-yml","design","out"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    design=json.loads(a.design.read_text())
    candidates,expected=prepare(
        a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],design)
    original,rows=fetch_counts(a.parquet,candidates,design)
    result=audit(original,rows,expected,design)
    result["all_trait_method_context_positive_control"]=positive_control_all_trait_contexts(a.parquet,design)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,
         "total_positive_original_record_keys":result["total_original_positive_source_record_value_keys"],
         "any_higher_taxon_inference_flagged_records":result["total_higher_taxon_inference_flagged_original_positive_source_records"],
         "nonempty_method_context":result["total_original_positive_source_record_keys_with_method_context"],
         "all_trait_positive_control_detected":result["all_trait_method_context_positive_control"]["positive_control_higher_taxon_labels_detected_elsewhere"]}))
if __name__=="__main__":
    main()
