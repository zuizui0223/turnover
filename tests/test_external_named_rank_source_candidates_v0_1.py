#!/usr/bin/env python3
"""All first-stage metadata candidates remain unqualified by the original gates."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_external_named_rank_source_candidates_v0_1 import audit,STATUS

p=ROOT/"data"/"austraits_named_rank_external_source_candidates_v0_1.json"
raw=json.loads(p.read_text())
r=audit(raw)
assert r["status"]==STATUS
assert r["candidate_count"]==3
assert r["qualified_independent_validation_sources"]==0
assert r["hard_total_species_ineligible"]==2
assert r["holds_require_new_source_metadata_or_qualified_raw_input"]==1
assert r["candidates"]["TRY7"]["verdict"]=="HOLD_PRIMARY_PROVENANCE_TRAIT_SEMANTICS_AND_FAMILY_SUPPORT"
assert r["candidates"]["MORFUNSEED2026"]["verdict"]=="FAIL_HARD_TOTAL_SPECIES_UPPER_BOUND"
assert r["candidates"]["WGINDIA2025"]["verdict"]=="FAIL_HARD_TOTAL_SPECIES_UPPER_BOUND"
assert all(not item["K_outcome_accessed"] and
               not item["permission_to_claim_independent_validation"] for item in r["candidates"].values())
# An apparently complete source cannot be declared independent based on a
# compilation-wide taxonomy count or the presence of trait names alone.
spoof=json.loads(p.read_text())
spoof["sources"][0]["reported_all_taxa"]=9999999
spoof["sources"][0]["primary_DOI_overlap_with_AusTraits_verified"]=True
assert audit(spoof)["candidates"]["TRY7"]["verdict"].startswith("HOLD_")
# No loosening post-metadata outcomes.
bad=json.loads(p.read_text())
bad["frozen_primary_minimums"]["min_families_per_trait"]=3
try:
    audit(bad)
except ValueError as e:
    assert "changed frozen" in str(e)
else:
    raise AssertionError("weakened family gate incorrectly accepted")
print("PASS: metadata triage 2 structural fails, TRY7 provenance HOLD, no K outcomes")
