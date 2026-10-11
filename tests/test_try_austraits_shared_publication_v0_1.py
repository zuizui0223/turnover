#!/usr/bin/env python3
"""Synthetic positive shared-study flag, negative independence and corruption guards."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_try_austraits_shared_publication_v0_1 import match_sources,STATUS
design=json.loads((ROOT/"data"/"try_austraits_public_author_year_overlap_contract_v0_1.json").read_text())
t=[{"try_dataset_id":str(i),"try_dataset_title":f"Random clean source {i}","try_source_link_dois":""}
   for i in range(1,110)]
t[50]={"try_dataset_id":"625","try_dataset_title":"Tng et al 2013 Traits","try_source_link_dois":""}
t[51]={"try_dataset_id":"63","try_dataset_title":"Fonseca/Wright New South Wales Database","try_source_link_dois":""}
a=[{"austraits_dataset_id":f"Unknown_{2000+i}",
    "austraits_primary_doi":"","source_metadata_status":"READABLE"}
    for i in range(1,111)]
a[20]={"austraits_dataset_id":"Tng_2013","austraits_primary_doi":"10.1371/journal.pone.0084378"}
a[21]={"austraits_dataset_id":"Fonseca_2000","austraits_primary_doi":"10.1000/xyz"}
out,strong,weak=match_sources(t,a,design)
assert out["status"]==STATUS
assert out["strong_author_year_publication_candidates"]==1
assert out["weak_author_only_candidates"]==1
assert out["try_v7_independent_validation_sources_qualified"]==0
assert out["no_matched_primary_measurement_ids_claimed"]
assert strong[0]["austraits_source_id"]=="Tng_2013"
assert strong[0]["try_public_dataset_id"]==625
assert strong[0]["austraits_source_primary_doi"]=="10.1371/journal.pone.0084378"
assert strong[0]["try_public_direct_doi_links"]==""
assert weak[0]["austraits_source_id"]=="Fonseca_2000"
bad=json.loads(json.dumps(design))
bad["status"]="NOT_FROZEN"
try:
    match_sources(t,a,bad)
except ValueError as exc:
    assert "nonfrozen" in str(exc)
else:raise AssertionError("unfrozen author-year matching allowed")
try:
    match_sources(t,[*a,a[0]],design)
except ValueError as exc:
    assert "duplicate" in str(exc)
else:raise AssertionError("duplicate source IDs allowed")
print("PASS: shared-publication candidate despite no DOI hyperlinks; never measurement overlap or TRY7 PASS")
