#!/usr/bin/env python3
"""Original-AusTraits-v7 primary/secondary/compiled source attribution audit.

Read-only: reconstruct source-native species median support from fixed 254
single-trait K systems, original 760 matched family/trait pairs, and 142 strict
same-remaining-DatasetID pairs. Persist ONLY aggregate dataset/trait/citation
metadata and diagnostic counts. Never persist species, observations, values,
phylogenetic K, or biological effect estimates.

A DatasetID is NOT proof of an independent primary study/specimen.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import zipfile
from collections import Counter,defaultdict
from pathlib import Path
import duckdb
import yaml

RELEASE="AusTraits v7.0.0"
PARQUET_SHA="5825d326c8236f5c86e9793d152d6ac5f83c1287a14255b6cf2b77ae2e804c99"
ZIP_SHA="2995fb9e5eebf9271f9241b5a6c2e2cbb7b45e8eda5ce4db43c14c68f95e2f3f"
EXCLUDED=("ABRS_2023","NHNSW_2023","RBGV_2023","NTH_2023","SAH_2023")
BASE=Path("results/austraits_organ_paper_frozen_rebuild_inputs_v0_1")
NONFLORA=Path("results/austraits_organ_paper_original_nonflora_K_references_v0_1")
FIELDS=("source_primary_key","source_secondary_key","source_original_dataset_key")
CITATIONS=("source_primary_citation","source_secondary_citation","source_original_dataset_citation")
TABLE=("dataset_id","trait_name","method_id")
STATUS="PASS_PUBLIC_V7_ORIGINAL_K_CONTRIBUTING_SOURCE_INVENTORY_WITH_HUMAN_ATTRIBUTION_GAPS"

def need(ok,why):
    if not ok:raise AssertionError(why)

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def read_table(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def norm(v):
    return str(v or "").strip()

def methods_and_bib(zip_path):
    with zipfile.ZipFile(zip_path) as f:
        names=f.namelist()
        matches=[x for x in names if x.endswith("/methods.csv")]
        bib=[x for x in names if x.endswith("/sources.bib")]
        need(len(matches)==len(bib)==1,"Compiled public v7 method/BibTeX source metadata absent")
        text=f.read(matches[0]).decode("utf-8-sig")
        rows=list(csv.DictReader(io.StringIO(text)))
        need(rows and set(TABLE+FIELDS+CITATIONS).issubset(rows[0]),"Actual v7 methods source schema changed")
        # Not redistributing full underlying release methods or sources.bib here.
        return rows,{"methods_member":matches[0],"sources_bib_member":bib[0],
                     "methods_csv_sha256":hashlib.sha256(f.read(matches[0])).hexdigest(),
                     "original_sources_bib_sha256":hashlib.sha256(f.read(bib[0])).hexdigest(),
                     "n_compiled_methods_rows":len(rows)}

def source_graph():
    original=read_table(BASE/"original_K_effects.csv")
    core=read_table(BASE/"core_systems.csv")
    need(len(original)==254 and len(core)==259,"Original historical 254/259 core changed")
    coremap={(r["family"],r["trait_name"]):r for r in core}
    need(len(coremap)==259,"Original core has repeated family/trait")
    refs={}
    for r in original:
        k=(r["family"],r["trait_name"])
        need(k in coremap and k not in refs,"Original 254 source systems changed")
        refs[k]={"system_id":r["system_id"],
                 "family":r["family"],"trait":r["trait_name"],
                 "expected":int(coremap[k]["n_input_species"])}
    need(len(refs)==254 and len({r["family"] for r in original})==42
         and len({r["trait_name"] for r in original})==13,
         "Original K family/trait cohort changed")
    support=json.loads((BASE/"shared_taxon_pair_support.json").read_text())
    need(support["status"]=="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"
         and support["qualifying_family_trait_pairs"]==760,
         "Original K-blind 760 paired source cohort changed")
    fixed=[r for r in support["family_trait_pair_support"] if r["qualifies_20_common_species"]]
    need(len(fixed)==760,"Original matched species 760 family/trait IDs missing")
    nonflora=json.loads((NONFLORA/"source_support_excluding_five_floras.json").read_text())
    need(nonflora["status"]=="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_SOURCE_SUPPORT_AUDITED"
         and nonflora["subsets"]["cross_organ"]["qualifying_20_same_nonflora_dataset_pairs"]==142,
         "Original 142 strict same-DatasetID source cohort changed")
    strict=nonflora["cross_organ_same_nonflora_dataset_supported_family_trait_pairs"]
    need(len(strict)==142,"Original strict 142 family/trait pairs missing")
    return refs,fixed,strict

def compile_states(c,parquet,units,refs):
    cfg=yaml.safe_load(units.read_text())["traits"]["elements"]
    c.execute("CREATE TEMP TABLE candidates(sid VARCHAR,family VARCHAR,trait VARCHAR,expected_unit VARCHAR)")
    entries=[]
    for k,x in refs.items():
        u=norm(cfg[x["trait"]].get("units"))
        need(u,"Original source native unit missing for "+str(k))
        entries.append((x["system_id"],x["family"],x["trait"],u))
    c.executemany("INSERT INTO candidates VALUES (?,?,?,?)",entries)
    c.execute("""
    CREATE TEMP TABLE raw_meta AS
    SELECT candidate.sid,candidate.family,candidate.trait,
      trim(CAST(p.genus AS VARCHAR)) genus,
      trim(CAST(p.binomial AS VARCHAR)) species,
      trim(CAST(p.dataset_id AS VARCHAR)) ds,
      trim(CAST(p.observation_id AS VARCHAR)) obs,
      try_cast(trim(CAST(p.value AS VARCHAR)) AS DOUBLE) val,
      coalesce(trim(CAST(p.source_id AS VARCHAR)),'') source_id,
      coalesce(trim(CAST(p.method_id AS VARCHAR)),'') method_id,
      coalesce(trim(CAST(p.basis_of_value AS VARCHAR)),'') basis_of_value,
      coalesce(trim(CAST(p.value_type AS VARCHAR)),'') value_type,
      coalesce(trim(CAST(p.source_primary_key AS VARCHAR)),'') source_primary_key,
      coalesce(trim(CAST(p.source_primary_citation AS VARCHAR)),'') source_primary_citation,
      coalesce(trim(CAST(p.source_secondary_key AS VARCHAR)),'') source_secondary_key,
      coalesce(trim(CAST(p.source_secondary_citation AS VARCHAR)),'') source_secondary_citation,
      coalesce(trim(CAST(p.source_original_dataset_key AS VARCHAR)),'') source_original_dataset_key,
      coalesce(trim(CAST(p.source_original_dataset_citation AS VARCHAR)),'') source_original_dataset_citation
    FROM read_parquet(?) p JOIN candidates candidate
      ON trim(CAST(p.family AS VARCHAR))=candidate.family
      AND trim(CAST(p.trait_name AS VARCHAR))=candidate.trait
    WHERE lower(trim(CAST(p.taxon_rank AS VARCHAR)))='species'
      AND p.genus IS NOT NULL AND trim(CAST(p.genus AS VARCHAR))<>''
      AND p.binomial IS NOT NULL AND trim(CAST(p.binomial AS VARCHAR))<>''
      AND p.dataset_id IS NOT NULL AND trim(CAST(p.dataset_id AS VARCHAR))<>''
      AND p.observation_id IS NOT NULL AND trim(CAST(p.observation_id AS VARCHAR))<>''
      AND p.value IS NOT NULL AND trim(CAST(p.value AS VARCHAR))<>''
      AND candidate.expected_unit<>''
      AND coalesce(trim(CAST(p.unit AS VARCHAR)),'')=candidate.expected_unit
      AND try_cast(trim(CAST(p.value AS VARCHAR)) AS DOUBLE) IS NOT NULL
      AND isfinite(try_cast(trim(CAST(p.value AS VARCHAR)) AS DOUBLE))
    """,[str(parquet)])
    # The original source-state logic deduplicates EXACT record identity
    # without citation fields, so metadata multiplicity cannot change medians.
    c.execute("""CREATE TEMP TABLE records AS SELECT DISTINCT
      sid,family,trait,genus,species,ds,obs,val FROM raw_meta""")
    c.execute("""CREATE TEMP TABLE states AS
       SELECT sid,family,trait,species,min(genus) genus
       FROM records GROUP BY sid,family,trait,species
       HAVING count(DISTINCT genus)=1 AND median(val)>0""")
    observed=dict(c.execute("SELECT sid,count(*) FROM states GROUP BY sid").fetchall())
    expected={x["system_id"]:x["expected"] for x in refs.values()}
    need(observed==expected,"Original K species positive-median support changed")
    return len(entries)

def make_pairs(c,pairs,strict):
    c.execute("CREATE TEMP TABLE target(family VARCHAR, trait_A VARCHAR, trait_B VARCHAR, system_A VARCHAR, system_B VARCHAR, n_species INT)")
    c.executemany("INSERT INTO target VALUES (?,?,?,?,?,?)",[
        (r["family"],r["trait_A"],r["trait_B"],
         r["system_A"],r["system_B"],int(r["n_common_species_same_genus"])) for r in pairs])
    c.execute("""CREATE TEMP TABLE matched AS
        SELECT DISTINCT t.family,t.trait_A,t.trait_B,t.system_A,t.system_B,
                        a.species,a.genus
        FROM target t
        JOIN states a ON a.sid=t.system_A
        JOIN states b ON b.sid=t.system_B
          AND a.species=b.species AND a.genus=b.genus""")
    check=c.execute("""SELECT t.family,t.trait_A,t.trait_B,t.n_species,count(m.species)
                       FROM target t LEFT JOIN matched m
                         ON t.family=m.family AND t.trait_A=m.trait_A
                         AND t.trait_B=m.trait_B
                       GROUP BY 1,2,3,4""").fetchall()
    need(len(check)==760 and all(n==found for _,_,_,n,found in check),
         "Original 760 paired same-species K-blind source support not reconstructed")
    c.execute("""CREATE TEMP TABLE matched_active AS
        SELECT DISTINCT system_A sid,species,genus FROM matched
        UNION SELECT DISTINCT system_B sid,species,genus FROM matched""")
    c.execute("""CREATE TEMP TABLE nonflora_records AS SELECT r.*
        FROM records r WHERE r.ds NOT IN ('ABRS_2023','NHNSW_2023','RBGV_2023','NTH_2023','SAH_2023')""")
    c.execute("""CREATE TEMP TABLE nonflora_states AS
        WITH m AS (
          SELECT sid,family,trait,species,min(genus) genus
          FROM nonflora_records GROUP BY sid,family,trait,species
          HAVING count(DISTINCT genus)=1 AND median(val)>0
        ) SELECT m.* FROM m JOIN states s
          ON m.sid=s.sid AND m.species=s.species AND m.genus=s.genus""")
    c.execute("""CREATE TEMP TABLE positive_nonflora AS
        SELECT DISTINCT r.sid,r.species,r.genus,r.ds
        FROM nonflora_records r JOIN nonflora_states s
          ON r.sid=s.sid AND r.species=s.species AND r.genus=s.genus
        WHERE r.val>0""")
    c.execute("CREATE TEMP TABLE strict_targets(family VARCHAR,trait_A VARCHAR,trait_B VARCHAR,system_A VARCHAR,system_B VARCHAR,n_species INT)")
    c.executemany("INSERT INTO strict_targets VALUES (?,?,?,?,?,?)",[
      (r["family"],r["trait_A"],r["trait_B"],r["system_A"],r["system_B"],
       int(r["n_same_nonflora_dataset_shared_positive_species"])) for r in strict])
    c.execute("""CREATE TEMP TABLE same_dataset AS
       SELECT DISTINCT t.family,t.trait_A,t.trait_B,t.system_A,t.system_B,
                       a.species,a.genus,da.ds
       FROM strict_targets t
       JOIN nonflora_states a ON a.sid=t.system_A
       JOIN nonflora_states b ON b.sid=t.system_B
         AND a.species=b.species AND a.genus=b.genus
       JOIN positive_nonflora da
         ON da.sid=t.system_A AND da.species=a.species AND da.genus=a.genus
       JOIN positive_nonflora db
         ON db.sid=t.system_B AND db.species=a.species AND db.genus=a.genus AND db.ds=da.ds""")
    actual=c.execute("""SELECT t.family,t.trait_A,t.trait_B,t.n_species,
       count(DISTINCT s.species)
       FROM strict_targets t LEFT JOIN same_dataset s
         ON t.family=s.family AND t.trait_A=s.trait_A AND t.trait_B=s.trait_B
       GROUP BY 1,2,3,4""").fetchall()
    need(len(actual)==142 and all(n==k for _,_,_,n,k in actual),
         "Same-nonflora-DatasetID original 142 species support not reproduced")
    c.execute("""CREATE TEMP TABLE strict_active AS
        SELECT DISTINCT system_A sid,species,genus,ds FROM same_dataset
        UNION SELECT DISTINCT system_B sid,species,genus,ds FROM same_dataset""")

def aggregate_tiers(c):
    c.execute("""CREATE TEMP TABLE tier_records AS
        SELECT 'original_254_systems' tier, r.* FROM records r
          JOIN states s ON r.sid=s.sid AND r.species=s.species AND r.genus=s.genus
        UNION ALL
        SELECT 'original_760_matched_pairs' tier, r.* FROM records r
          JOIN matched_active a ON r.sid=a.sid AND r.species=a.species AND r.genus=a.genus
        UNION ALL
        SELECT 'strict_142_same_DatasetID' tier,r.* FROM records r
          JOIN strict_active a ON r.sid=a.sid AND r.species=a.species
           AND r.genus=a.genus AND r.ds=a.ds""")
    summary=c.execute("""SELECT tier,ds,trait,
         count(*) dedup_source_rows,count(DISTINCT sid) n_systems,
         count(DISTINCT species) n_species
       FROM tier_records GROUP BY 1,2,3 ORDER BY 1,2,3""").fetchall()
    recs=[{"tier":tier,"dataset_id":ds,"trait_name":trait,
           "original_deduplicated_source_measurement_rows":n,
           "system_count":systems,"distinct_species_in_this_dataset_trait":species}
          for tier,ds,trait,n,systems,species in summary]
    # Preserve a categorical metadata summary, never rows with specimen or trait values.
    categories=c.execute("""SELECT tier,ds,basis_of_value,value_type,count(*)
       FROM (
         SELECT DISTINCT t.tier,t.sid,t.genus,t.species,t.ds,t.obs,t.val,
                m.basis_of_value,m.value_type
         FROM tier_records t JOIN raw_meta m
           ON t.sid=m.sid AND t.genus=m.genus AND t.species=m.species
           AND t.ds=m.ds AND t.obs=m.obs AND t.val=m.val
       ) q GROUP BY 1,2,3,4 ORDER BY 1,2,3,4""").fetchall()
    category_rows=[{"tier":a,"dataset_id":b,"basis_of_value":c0 or "(unreported)",
                    "value_type":d or "(unreported)","source_rows":e}
                   for a,b,c0,d,e in categories]
    metadata=c.execute("""SELECT DISTINCT t.tier,m.ds,m.trait,m.method_id,m.source_id,
       m.source_primary_key,m.source_secondary_key,m.source_original_dataset_key,
       m.source_primary_citation,m.source_secondary_citation,
       m.source_original_dataset_citation
       FROM tier_records t JOIN raw_meta m
       ON t.sid=m.sid AND t.genus=m.genus AND t.species=m.species
          AND t.ds=m.ds AND t.obs=m.obs AND t.val=m.val
       ORDER BY 1,2,3,4,5,6,7,8""").fetchall()
    attribution=[]
    cols=("tier","dataset_id","trait_name","method_id","source_id",
          "source_primary_key","source_secondary_key","source_original_dataset_key",
          "source_primary_citation","source_secondary_citation","source_original_dataset_citation")
    for row in metadata:attribution.append(dict(zip(cols,row)))
    return recs,category_rows,attribution

def audit_methods(methods,attribution):
    index=defaultdict(list)
    for row in methods:
        k=(norm(row["dataset_id"]),norm(row["trait_name"]),norm(row["method_id"]))
        index[k].append(row)
    flags=Counter()
    out=[]
    for r in attribution:
        ds=r["dataset_id"]; tr=r["trait_name"]; mid=norm(r["method_id"])
        matches=index.get((ds,tr,mid),[])
        if not matches and not mid:
            matches=[r for (a,b,_),vals in index.items() if (a,b)==(ds,tr) for r in vals]
        different=False
        if matches:
            for field in FIELDS:
                val=norm(r[field])
                if val and all(norm(x[field])!=val for x in matches):
                    different=True
        if not matches:flags["missing_matching_compiled_methods_row"]+=1
        if different:flags["flattened_citation_key_disagrees_with_compiled_methods"]+=1
        if not norm(r["source_primary_key"]):flags["missing_primary_citation_key"]+=1
        if not norm(r["source_primary_citation"]):flags["missing_primary_citation_text"]+=1
        if norm(r["source_id"]):flags["nonempty_source_id_requires_original_record_source_review"]+=1
        r2=dict(r)
        r2["method_table_match"]=bool(matches)
        r2["method_source_key_mismatch"]=different
        r2["requires_secondary_original_source_review"]=bool(norm(r["source_id"]) or
                                                            norm(r["source_secondary_key"]) or
                                                            norm(r["source_original_dataset_key"]))
        out.append(r2)
    return out,dict(flags)

def write_csv(path,rows):
    cols=list(rows[0])
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=cols)
        writer.writeheader();writer.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--parquet",required=True,type=Path)
    p.add_argument("--compiled-zip",required=True,type=Path)
    p.add_argument("--traits-yml",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    need(digest(a.parquet)==PARQUET_SHA,"AusTraits raw trait source release SHA changed")
    need(digest(a.compiled_zip)==ZIP_SHA,"Compiled public AusTraits v7 metadata SHA changed")
    methods,meta=methods_and_bib(a.compiled_zip)
    refs,pairs,strict=source_graph()
    c=duckdb.connect(":memory:")
    try:
        compile_states(c,a.parquet,a.traits_yml,refs)
        make_pairs(c,pairs,strict)
        counts,categories,details=aggregate_tiers(c)
    finally:c.close()
    need(counts and details,"No qualifying original K source citation exposure")
    details,flags=audit_methods(methods,details)
    tiers=defaultdict(lambda:{"dataset_ids":set(),"n_source_rows":0,"n_dataset_trait_rows":0})
    for r in counts:
        z=tiers[r["tier"]]
        z["dataset_ids"].add(r["dataset_id"])
        z["n_source_rows"]+=r["original_deduplicated_source_measurement_rows"]
        z["n_dataset_trait_rows"]+=1
    summary={tier:{"n_distinct_datasets":len(x["dataset_ids"]),
                   "n_original_deduplicated_measurement_rows_in_qualified_states":x["n_source_rows"],
                   "dataset_by_trait_entries":x["n_dataset_trait_rows"]}
             for tier,x in tiers.items()}
    need(set(summary)=={"original_254_systems","original_760_matched_pairs",
                       "strict_142_same_DatasetID"},"All three historical K provenance tiers not rebuilt")
    a.out_dir.mkdir(parents=True,exist_ok=True)
    write_csv(a.out_dir/"original_K_dataset_trait_source_exposure.csv",counts)
    write_csv(a.out_dir/"original_K_basis_of_value_counts.csv",categories)
    write_csv(a.out_dir/"original_K_used_dataset_citation_candidates.csv",details)
    files={f.name:digest(f) for f in a.out_dir.iterdir() if f.suffix==".csv"}
    report={
     "status":STATUS,"original_public_data_release":RELEASE,
     "original_parquet_sha256":PARQUET_SHA,"compiled_v7_metadata_zip_sha256":ZIP_SHA,
     "original_fixed_qualified_systems":254,"original_matched_pair_identities":760,
     "original_strict_source_pair_identities":142,
     "original_excluded_online_floras":list(EXCLUDED),
     "compiled_citation_metadata":meta,
     "exposure_by_original_K_analysis_tier":summary,
     "original_method_citation_candidate_rows":len(details),
     "source_attribution_review_flags":flags,
     "aggregate_inventory_files_sha256":files,
     "no_raw_species_names_observation_ids_trait_values_exported":True,
     "no_new_K_or_biological_models_fitted":True,
     "dataset_id_not_proof_of_independent_publication_or_specimen":True,
     "source_id_method_id_and_primary_secondary_original_keys_require_study_level_review":True,
     "citation_selection_currently_human_approved":False,
     "journal_data_metadata_code_submitted_or_archived_under_DOI":False,
     "independent_primary_study_validation":False
    }
    (a.out_dir/"original_K_source_citation_audit_verdict.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":report["status"],"tiers":summary,
                      "citation_candidate_rows":len(details),"flags":flags},
                     sort_keys=True))
if __name__=="__main__":
    main()
