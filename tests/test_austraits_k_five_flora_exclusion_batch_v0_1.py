#!/usr/bin/env python3
"""Synthetic five-flora-removal paired K state and arithmetic correctness.

Actual original 283 K-blind source-eligible family×trait support is used
ONLY to validate identity and support; synthetic numerical source medians
are never mistaken for independent evidence or estimated original K.
"""
from __future__ import annotations
import argparse,csv,json,math,tempfile,sys,copy
from pathlib import Path
import duckdb,pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from run_austraits_k_five_flora_exclusion_batch_v0_1 import (
    BATCH_STATUS,EXCLUDED,cohort,validate_batch,reconstruct_native_states,
    write_ephemeral,validate_result)

p=argparse.ArgumentParser()
for arg in ("nonflora-support","original-pair-support","design"):
    p.add_argument("--"+arg,required=True,type=Path)
a=p.parse_args()
source=json.loads(a.__dict__["nonflora_support"].read_text())
original=json.loads(a.__dict__["original_pair_support"].read_text())
design=json.loads(a.design.read_text())
fixed=cohort(source,original,design)
assert len(fixed)==283 and len({r["family"] for r in fixed})==29
assert sum(r["cross_fruit_vegetative"] for r in fixed)==106
assert sum(r["cross_seed_vegetative"] for r in fixed)==177
assert validate_batch(fixed[:2],source,original,design)
bad=[{**fixed[0],"n_nonflora_positive_median_shared_species":99999}]
try:validate_batch(bad,source,original,design)
except ValueError as e:assert "outcome-adjusted" in str(e)
else:raise AssertionError("changed positive source support accepted")

rows=[]
for j in range(25):
    binomial=f"Genus species{j:03d}"
    for trait,src,value in [
        ("fruit_length","DirectStudyFruit",float(2+j)/2),
        ("leaf_length","DirectStudyLeaf",float(3+j)/2)]:
        rows.append(dict(family="Testaceae",trait_name=trait,genus="Genus",
              binomial=binomial,dataset_id="ABRS_2023",
              observation_id=f"flora_{trait}_{j}",value=value*2,
              unit="mm",taxon_rank="species"))
        if j<22:
            rows.append(dict(family="Testaceae",trait_name=trait,genus="Genus",
              binomial=binomial,dataset_id=src,
              observation_id=f"nonflora_{trait}_{j}",value=value,
              unit="mm",taxon_rank="species"))
rows.append({**rows[0],"observation_id":"bad_unit","unit":"cm","value":999999.0})
with tempfile.TemporaryDirectory(prefix="synthetic_5flora_K_") as td:
    td=Path(td)
    parquet=td/"test.parquet"
    con=duckdb.connect(":memory:")
    con.register("tiny",pd.DataFrame(rows))
    con.execute(f"COPY tiny TO '{parquet}' (FORMAT PARQUET)")
    con.close()
    yml=td/"units.yml"
    yml.write_text(yaml.safe_dump({"traits":{"elements":{
       "fruit_length":{"units":"mm"},"leaf_length":{"units":"mm"}}}}))
    synthetic={
      "family":"Testaceae","trait_A":"fruit_length","trait_B":"leaf_length",
      "system_A":"A","system_B":"B",
      "n_original_A":25,"n_original_B":25,
      "n_nonflora_positive_median_shared_species":22}
    state=reconstruct_native_states(parquet,yml,[synthetic])
    assert len(state)==22
    assert all(x[:5]==("Testaceae","fruit_length","leaf_length","A","B") for x in state)
    manifest=write_ephemeral(state,[synthetic],td)
    assert manifest[0]["n_nonflora_positive_species"]==22
    assert manifest[0]["status"]=="READY"
    with Path(manifest[0]["state_table"]).open() as fh:
        r=list(csv.DictReader(fh))
    assert len(r)==22 and float(r[0]["all_A"])>float(r[0]["source_A"])
    assert float(r[0]["all_B"])>float(r[0]["source_B"])
    # The two nonflora traits are from DIFFERENT direct data sets; this is
    # deliberate and the audit must not wrongly demand common DatasetID.
    assert rows[1]["dataset_id"]=="DirectStudyFruit"
    assert rows[3]["dataset_id"]=="DirectStudyLeaf"
    K={
      "status":"PASS","n_tips":22,
      "K_full_A":2.0,"K_full_B":1.0,
      "K_source_A":3.0,"K_source_B":1.0,
      "delta_full":math.log(2.0),
      "delta_source":math.log(3.0),
      "delta_source_measurements":math.log(3/2)}
    result={
      "status":BATCH_STATUS,"NOT_independent_primary_measurement_validation":True,
      "pairs":[{"pair_id":"Q001","family":"Testaceae",
       "trait_A":"fruit_length","trait_B":"leaf_length",
       "system_A":"A","system_B":"B",
       "n_nonflora_positive_species":22,
       "axes":{"S3":K,
          "prune_only":{"status":"HOLD_FEWER_THAN_20_NATIVE_TREE_TIPS","n_tips":11}}}]}
    assert validate_result(result,manifest)
    corrupt=copy.deepcopy(result)
    corrupt["pairs"][0]["axes"]["S3"]["delta_source_measurements"]+=.1
    try:validate_result(corrupt,manifest)
    except ValueError as e:assert "source-only" in str(e)
    else:raise AssertionError("source-only K effect ratio corruption went undetected")
print("PASS: original 283 pairs, 29 families, 106 fruit, 177 seed; 25 original species->22 nonflora; exact same tip native K arithmetic")
