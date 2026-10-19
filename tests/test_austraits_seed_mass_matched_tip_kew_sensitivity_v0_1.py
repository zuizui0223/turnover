#!/usr/bin/env python3
"""Synthetic matched-tip source K sensitivity schema checks; no real K outcomes."""
import json,math,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from run_austraits_seed_mass_matched_tip_kew_sensitivity_v0_1 import (
  read_support,validate_states_and_write,aggregate,STATUS)
meta=[]
for i in range(15):
    meta.append({"family":f"F{i:02d}","system_id":f"A{i+1:04d}",
       "n_original_species":35,
       "n_non_kew_positive_median_species":25 if i<13 else 12,
       "meets_20_species_descriptive_gate":i<13})
protocol={"status":"AUSTRAITS_SEED_MASS_NO_KEW_SOURCE_SUPPORT_AUDITED",
          "original_graph":{"systems":254,"families":42,"traits":13},
          "original_seed_mass_families":15,
          "families_with_at_least_20_remaining_seed_mass_species":13,
          "family_support":meta}
expected={}
rows=[]
for m in meta:
  sid=m["system_id"]
  expected[sid]={"family":m["family"],"n_original":35,
                 "n_retained":m["n_non_kew_positive_median_species"],
                 "support_eligible":m["meets_20_species_descriptive_gate"]}
  for i in range(35):
    rows.append((sid,m["family"],"genus",f"genus sp{i}",math.exp(i/100),
                 math.exp((i+1)/100) if i<m["n_non_kew_positive_median_species"] else None))
with tempfile.TemporaryDirectory(prefix="synthetic_aust_sourceK_") as t:
  file=Path(t)/"support.json"
  file.write_text(json.dumps(protocol))
  lookup=read_support(file)
  assert len(lookup)==15
  inputs=validate_states_and_write(rows,expected,t)
  assert len(inputs)==13
  result=[]
  for sid,m,path in inputs:
      result.append({"status":"AUSTRAITS_SEED_MASS_MATCHED_TIP_K_PAIR_CALCULATED",
       "system_id":sid,"family":m["family"],"n_retained_source_species":m["n_retained"],
       "axes":{
         "S3":{"status":"PASS","n_tips":25,"K_full_sources_matched_tips":.4,
               "K_nonkew_matched_tips":.5,"delta_source_logK":math.log(.5/.4),
               "delta_support_geometry_logK":.1,
               "delta_total_logK":math.log(.5/.4)+.1},
         "prune_only":{"status":"HOLD_FEWER_THAN_20_MATCHED_TIPS","n_tips":14}
       }})
  output=aggregate(result,expected)
  assert output["status"]==STATUS
  assert output["axes"]["S3"]["n_paired_supported_families"]==13
  assert output["axes"]["prune_only"]["n_axis_holds"]==13
  assert not output["trait_values_or_species_ids_persisted"]
  assert output["not_independent_validation"] is True
  bad=result[:-1]
  try:aggregate(bad,expected)
  except ValueError as e:assert "incomplete no-Kew sensitivity" in str(e)
  else:raise AssertionError("missing family improperly accepted")
print("PASS: 13 presupported reduced-tip systems, separated S3/prune holds, no independent-source claim")
