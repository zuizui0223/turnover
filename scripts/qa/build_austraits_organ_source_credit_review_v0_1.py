#!/usr/bin/env python3
"""Compact coauthor citation-review index from verified original AusTraits v7.

Strictly derives aggregated DatasetID/trait-level citation candidates and
original basis_of_value summaries from the already archived source audit.
No raw species, specimen, observation, values, or new phylogenetic analyses.
No inferred permission or human citation approval.
"""
import argparse,csv,hashlib,io,json,zipfile
from collections import defaultdict,Counter
from pathlib import Path
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

EXPECTED_STATUS="PASS_PUBLIC_V7_ORIGINAL_K_CONTRIBUTING_SOURCE_INVENTORY_WITH_HUMAN_ATTRIBUTION_GAPS"
STATUS="PASS_COMPACT_DATASET_CITATION_REVIEW_INDEX_WITH_HUMAN_GATES"
SOURCE_SHA="2995fb9e5eebf9271f9241b5a6c2e2cbb7b45e8eda5ce4db43c14c68f95e2f3f"
TIERS=("original_254_systems","original_760_matched_pairs","strict_142_same_DatasetID")
ROLES=(
 ("primary","source_primary_key","source_primary_citation"),
 ("secondary","source_secondary_key","source_secondary_citation"),
 ("original_dataset","source_original_dataset_key","source_original_dataset_citation")
)
def need(t,msg):
    if not t:raise AssertionError(msg)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def readcsv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def outputcsv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:w.writerow({k:r.get(k,"") for k in fields})

def good(x):
    return str(x or "").strip()

def bib_references(zippath,used_keys,output):
    need(sha(zippath)==SOURCE_SHA,"Compiled v7 source metadata ZIP changed")
    with zipfile.ZipFile(zippath) as z:
        p=[p for p in z.namelist() if p.endswith("/sources.bib")]
        need(len(p)==1,"Original compiled primary/secondary citations bibliography absent")
        orig=z.read(p[0])
    source=bibtexparser.loads(orig.decode("utf-8-sig"))
    keys={e["ID"]:e for e in source.entries}
    present=sorted(set(used_keys)&set(keys))
    missing=sorted(set(used_keys)-set(keys))
    database=BibDatabase()
    database.entries=[keys[k] for k in present]
    w=BibTexWriter()
    w.indent="  "
    w.order_entries_by=("ID",)
    output.write_text(w.write(database),encoding="utf-8")
    return {"n_original_bib_entries":len(source.entries),
            "n_used_unique_original_bib_keys":len(set(used_keys)),
            "n_source_bibtex_entries_exported":len(present),
            "unresolved_source_bibtex_keys":missing,
            "source_bib_sha256":hashlib.sha256(orig).hexdigest(),
            "full_compiled_bibtex_file_exported":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-audit-dir",type=Path,required=True)
    p.add_argument("--compiled-zip",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    base=a.source_audit_dir
    origin=json.loads((base/"original_K_source_citation_audit_verdict.json").read_text())
    need(origin["status"]==EXPECTED_STATUS
         and origin["original_fixed_qualified_systems"]==254
         and origin["original_matched_pair_identities"]==760
         and origin["original_strict_source_pair_identities"]==142,
         "Original public AusTraits source K citation inventory is invalid")
    for name,checksum in origin["aggregate_inventory_files_sha256"].items():
        need(sha(base/name)==checksum,
             "Original source audit content changed: "+name)
    need(sha(a.compiled_zip)==SOURCE_SHA,
         "Citations are not from the original AusTraits public 7.0.0 release")
    exposure=readcsv(base/"original_K_dataset_trait_source_exposure.csv")
    citations=readcsv(base/"original_K_used_dataset_citation_candidates.csv")
    basis=readcsv(base/"original_K_basis_of_value_counts.csv")
    needs=defaultdict(lambda:defaultdict(int))
    traitcounts=defaultdict(lambda:defaultdict(set))
    for r in exposure:
        tier=r["tier"];ds=r["dataset_id"]
        need(tier in TIERS,"Unexpected original K analysis tier")
        needs[ds][tier]+=int(r["original_deduplicated_source_measurement_rows"])
        traitcounts[ds][tier].add(r["trait_name"])
    need(len(needs)==190,"Original source audit 190 DatasetID cohort changed")
    strict={ds for ds,v in needs.items() if v["strict_142_same_DatasetID"]>0}
    need(len(strict)==44,"Original strict nonflora source support not 44 DatasetIDs")
    roles=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
    refs=defaultdict(dict)
    source_ids=defaultdict(set)
    method_ids=defaultdict(set)
    metadata_flags=defaultdict(Counter)
    for r in citations:
        ds=r["dataset_id"]
        need(ds in needs,"Method citation candidate outside K-eligible source cohort")
        if good(r["source_id"]):source_ids[ds].add(good(r["source_id"]))
        if good(r["method_id"]):method_ids[ds].add(good(r["method_id"]))
        if r["method_table_match"]!="True":metadata_flags[ds]["missing_compiled_method_row"]+=1
        if r["method_source_key_mismatch"]=="True":
            metadata_flags[ds]["flattened_vs_compiled_citation_key_mismatch"]+=1
        for role,kfield,cfield in ROLES:
            key=good(r[kfield]);text=good(r[cfield])
            if key:
                roles[ds][role][key].add(r["tier"])
                if text:refs[(ds,role)][key]=text
            elif role=="primary":metadata_flags[ds]["missing_primary_source_key"]+=1
    primary_missing=sum(not roles[ds]["primary"] for ds in needs)
    used_keys={key for ds in needs for role in ("primary","secondary","original_dataset")
               for key in roles[ds][role]}
    a.out_dir.mkdir(parents=True,exist_ok=True)
    bib=bib_references(a.compiled_zip,used_keys,
                       a.out_dir/"original_AusTraits_v7_contributing_citations.bib")
    bib_missing=set(bib["unresolved_source_bibtex_keys"])
    records=[]
    cited=[]
    for ds in sorted(needs, key=lambda ds:(-int(ds in strict),
                     -needs[ds]["strict_142_same_DatasetID"],
                     -needs[ds]["original_760_matched_pairs"],ds)):
        keys={role:sorted(roles[ds][role]) for role,_,_ in ROLES}
        flags=[]
        if not keys["primary"]:flags.append("PRIMARY_CITATION_KEY_MISSING")
        if len(keys["primary"])>1:flags.append("MULTIPLE_PRIMARY_CITATION_KEYS")
        if len(source_ids[ds])>1:flags.append("MULTIPLE_SOURCE_IDS")
        if keys["secondary"] or keys["original_dataset"]:
            flags.append("SECONDARY_OR_ORIGINAL_DATASET_CREDIT_NEEDED")
        if set(sum(keys.values(),[]))&bib_missing:flags.append("UNRESOLVED_BIBTEX_REFERENCE")
        if metadata_flags[ds].get("missing_compiled_method_row"):
            flags.append("METHOD_TABLE_KEY_MISSING")
        if metadata_flags[ds].get("flattened_vs_compiled_citation_key_mismatch"):
            flags.append("METADATA_CITATION_CONFLICT")
        priority="P0_STRICT_142" if ds in strict else "P1_MATCHED_760"
        out={"dataset_id":ds,"review_priority":priority,
             "n_source_rows_original_254":needs[ds]["original_254_systems"],
             "n_source_rows_matched_760":needs[ds]["original_760_matched_pairs"],
             "n_source_rows_strict_142":needs[ds]["strict_142_same_DatasetID"],
             "n_used_traits_matched_760":len(traitcounts[ds]["original_760_matched_pairs"]),
             "n_source_ids":len(source_ids[ds]),
             "n_method_ids":len(method_ids[ds]),
             "n_primary_citation_keys":len(keys["primary"]),
             "primary_citation_keys":"; ".join(keys["primary"]),
             "secondary_citation_keys":"; ".join(keys["secondary"]),
             "compiled_original_dataset_citation_keys":"; ".join(keys["original_dataset"]),
             "source_attribution_review_flags":"; ".join(flags),
             "human_citation_approval":False}
        records.append(out)
        for role in ("primary","secondary","original_dataset"):
            for key in keys[role]:
                cited.append({"dataset_id":ds,"review_priority":priority,
                              "citation_role":role,"source_bibtex_key":key,
                              "source_bibtex_entry_resolved":key not in bib_missing,
                              "citation_as_recorded_by_original_v7":refs[(ds,role)].get(key,""),
                              "appears_in_original_K_tiers":"; ".join(sorted(roles[ds][role][key])),
                              "requires_human_primary_source_check":True})
    outputcsv(a.out_dir/"dataset_priority_and_credit_gaps.csv",records,list(records[0]))
    outputcsv(a.out_dir/"cited_original_publication_candidates.csv",cited,list(cited[0]))
    current=defaultdict(Counter)
    for r in basis:
        tier=r["tier"]
        current[tier][good(r["basis_of_value"]) or "(unreported)"]+=int(r["source_rows"])
    by_basis=[]
    for tier in TIERS:
        total=sum(current[tier].values())
        orig=origin["exposure_by_original_K_analysis_tier"][tier]["n_original_deduplicated_measurement_rows_in_qualified_states"]
        # These two may differ if public source metadata repeats one accepted record
        # under different basis values. This is a citation/row-multiplicity diagnostic.
        for label,n in sorted(current[tier].items(),key=lambda v:(-v[1],v[0])):
            by_basis.append({"analysis_tier":tier,"basis_of_value":label,
                             "metadata_labeled_source_rows":n,
                             "fraction_of_all_basis_labeled_rows":round(n/total,8) if total else None,
                             "distinct_original_record_rows_in_tier":orig,
                             "metadata_row_count_minus_dedup_source_rows":total-orig})
    outputcsv(a.out_dir/"basis_of_value_review_summary.csv",by_basis,list(by_basis[0]))
    samples=Counter(x for ds in needs for x in
        next((r["source_attribution_review_flags"] for r in records if r["dataset_id"]==ds),"").split("; ") if x)
    output_names=("dataset_priority_and_credit_gaps.csv",
                  "cited_original_publication_candidates.csv",
                  "basis_of_value_review_summary.csv",
                  "original_AusTraits_v7_contributing_citations.bib")
    files={n:sha(a.out_dir/n) for n in output_names}
    report={
      "status":STATUS,
      "original_source_audit_sha256":
       sha(base/"original_K_source_citation_audit_verdict.json"),
      "pinned_original_compiled_v7_zip_sha256":SOURCE_SHA,
      "all_original_K_dataset_ids":len(needs),
      "source_DatasetIDs_in_strict_142_K":len(strict),
      "source_DatasetIDs_in_original_matched_760_K":
       sum(v["original_760_matched_pairs"]>0 for v in needs.values()),
      "n_compact_dataset_credit_review_rows":len(records),
      "original_citation_roles_review_rows":len(cited),
      "dataset_credit_flag_count_by_kind":dict(samples),
      "source_basis_of_value_summary":
       {tier:dict(current[tier]) for tier in TIERS},
      "original_basis_metadata_row_multiplicity_by_tier":
       {t:sum(current[t].values()) -
        origin["exposure_by_original_K_analysis_tier"][t]["n_original_deduplicated_measurement_rows_in_qualified_states"]
        for t in TIERS},
      "missing_primary_citation_datasets":primary_missing,
      "source_reference_BibTeX":bib,
      "files_sha256":files,
      "no_original_source_species_or_observation_ids_or_values_released":True,
      "no_new_evolutionary_process_or_K_fits":True,
      "same_DatasetID_does_not_certify_independent_primary_study_or_specimen":True,
      "citation_selection_author_confirmed":False,
      "journal_citable_code_DOI_created":False,
      "journal_full_data_metadata_requirements_verified":False
    }
    (a.out_dir/"original_source_citation_priority_verdict.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],
                      "datasets":len(needs),"strict_datasets":len(strict),
                      "references":len(cited),"unresolved_bibtex":len(bib_missing),
                      "basis_of_value":report["source_basis_of_value_summary"],
                      "flags":report["dataset_credit_flag_count_by_kind"]},sort_keys=True))
if __name__=="__main__":
    main()
