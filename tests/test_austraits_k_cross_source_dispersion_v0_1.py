#!/usr/bin/env python3
"""Synthetic graph and no-K-response test for source dispersion estimator."""
from pathlib import Path
import math
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from estimate_austraits_k_cross_source_dispersion_v0_1 import summarize,STATUS

systems={}
rows=[]
traits={}
for t in range(13):
    traits[f"T{t:02d}"]={"qualifies_source_calibration_coverage":t<12,
                        "species_with_two_datasets":200}
for i in range(254):
    sid=f"A{i+1:04d}"
    fam=f"F{i%42:02d}"
    trait=f"T{i%13:02d}"
    systems[sid]={"family":fam,"trait_name":trait,"n_input_species":6}
    for j in range(6):
        rows.append((sid,fam,trait,f"sp{i}_{j}",math.exp(j/10),2,.125))
coverage={"traits":traits}
design={"status":"POST_COVERAGE_PRE_CROSS_SOURCE_DISPERSION_FROZEN"}
out=summarize(rows,systems,coverage,design)
assert out["status"]==STATUS
assert out["eligible_traits"]==12
assert out["graph"]=={"systems":254,"families":42,"traits":13}
assert len(out["systems"])==254
assert out["traits"]["T12"]["calibratable_for_followon_process_null"] is False
assert out["traits"]["T00"]["source_log_variance_ratio_median"]>0
assert all(r["calibratable"] for r in out["systems"])
assert "observed_K" not in str(out)
for bad,why in [
    (rows[:-1],"support changed"),
    ([(rows[0][0],"WRONG",*rows[0][2:])]+rows[1:],"family/trait"),
    ([(*rows[0][:4],-1,*rows[0][5:])]+rows[1:],"nonpositive"),
    ([(*rows[0][:6],-0.1)]+rows[1:],"invalid cross-source")
]:
    try:
        summarize(bad,systems,coverage,design)
    except ValueError as e:
        assert why in str(e),str(e)
    else:
        raise AssertionError("accepted corrupt source rows")
print("PASS: K-blind source dispersion on 254 synthetic systems, 12/13 gate and identity guards")
