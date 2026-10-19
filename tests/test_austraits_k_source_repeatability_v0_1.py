#!/usr/bin/env python3
"""Synthetic process guards; NOT observed source-repeatability evidence."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_k_source_repeatability_v0_1 import summarize_coverage,RESULT_STATUS

design=json.loads((ROOT/"data"/"austraits_k_source_repeatability_feasibility_v0_1.json").read_text())
assert design["status"]=="POST_K_AND_SHARED_OU_OUTCOME_PRE_SOURCE_COVERAGE_AUDIT_FROZEN"
assert design["predeclared_feasibility"]["minimum_qualifying_traits"]==6
expected={}
rows=[]
for i in range(254):
    sid=f"A{i+1:04d}"
    fam=f"F{i%42:02d}"
    trait=f"T{i%13:02d}"
    expected[sid]={"family":fam,"trait_name":trait,"n_input_species":6}
    for j in range(6):
        multidataset=int(i%13<6)
        rows.append((sid,fam,trait,f"Species_{i}_{j}",1.0,2 if multidataset else 1,
                    2 if multidataset else 1,2 if multidataset else 1,2 if multidataset else 1))
r=summarize_coverage(rows,expected,design)
assert r["status"]==RESULT_STATUS
assert r["qualifying_traits"]==6
assert r["go_to_external_reliability_calibration"] is True
assert all(r["traits"][f"T{i:02d}"]["qualifies_source_calibration_coverage"] for i in range(6))
assert all(not r["traits"][f"T{i:02d}"]["qualifies_source_calibration_coverage"] for i in range(6,13))
# Audit rejects hidden source-grain changes and invalid log-eligible states.
for altered,needle in [
    (rows[:-1],"species count differs"),
    ([(*rows[0][:4],-1.0,*rows[0][5:])]+rows[1:],"nonpositive median"),
    ([(rows[0][0],"WRONG",*rows[0][2:])]+rows[1:],"unexpected family trait")
]:
    try:
        summarize_coverage(altered,expected,design)
    except ValueError as e:
        assert needle in str(e),str(e)
    else:
        raise AssertionError("Source audit accepted corrupt K matching")
print("PASS: 254-system/42-family/13-trait source-replication coverage firewall and fixed rules")
