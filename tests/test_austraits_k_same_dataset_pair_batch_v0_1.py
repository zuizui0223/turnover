#!/usr/bin/env python3
"""Synthetic full-source versus shared-DatasetID medians and K identity guards.

Uses TRUE frozen 279-row metadata source support as an eligibility fixture,
but K/trait values are entirely synthetic and cannot affect source selection.
"""
from __future__ import annotations
import argparse,csv,json,math,tempfile,sys
from pathlib import Path
import duckdb,pandas as pd,yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from run_austraits_k_same_dataset_pair_batch_v0_1 import (
    STATUS,qualify,validate_batch,source_medians,
    write_ephemeral_states,validate_R_results)

p=argparse.ArgumentParser()
for arg in ("source-support","original-pair-support","design"):
    p.add_argument("--"+arg,required=True,type=Path)
v=p.parse_args()
src=json.loads(v.__dict__["source_support"].read_text())
original=json.loads(v.__dict__["original_pair_support"].read_text())
design=json.loads(v.design.read_text())
selected=qualify(src,original,design)
assert len(selected)==279
assert len({x["family"] for x in selected})==32
assert sum(x["cross_fruit_vs_vegetative"] for x in selected)==159
assert sum(x["cross_seed_vs_vegetative"] for x in selected)==120
assert validate_batch(selected[:3],src,original,design)
wrong=[{**selected[0],"n_same_AusTraits_dataset_species":99999}]
try:validate_batch(wrong,src,original,design)
except ValueError as ex:assert "source eligibility" in str(ex)
else:raise AssertionError("outcome-selected or source-count mutated batch accepted")

# Tiny parquet: 25 originally valid species per original trait; 22 species
# have both traits in exact same AusTraits contributing dataset; species 23-25
# have both traits but NEVER from one common dataset.
rows=[]
for j in range(25):
    sp=f"Genus sample{j+1:03d}"
    shared=j<22
    for sid,trait,base in [("A","fruit_width",2.0),("B","leaf_width",4.0)]:
        rows.append({
          "family":"Testaceae","trait_name":trait,"genus":"Genus",
          "binomial":sp,"dataset_id":"shared_original" if shared else f"only_{sid}",
          "observation_id":f"raw_{j+1}_{sid}",
          "value":base+j*.01,"taxon_rank":"species","unit":"mm"
        })
        # A second source is unique to each trait and exists for every
        # species. All-source median thus differs from common-source median.
        rows.append({
          "family":"Testaceae","trait_name":trait,"genus":"Genus",
          "binomial":sp,"dataset_id":f"unique_addition_{sid}",
          "observation_id":f"raw_{j+1}_{sid}_extra",
          "value":base+10+j*.01,"taxon_rank":"species","unit":"mm"
        })
# A wrong-unit duplicate must never enter the source-native median.
rows.append({**rows[0],"unit":"cm","observation_id":"wrong_unit","value":9999.0})
with tempfile.TemporaryDirectory(prefix="synthetic_shared_src_K_") as tmp:
    d=Path(tmp)
    datafile=d/"tiny.parquet"
    con=duckdb.connect(":memory:")
    con.register("test_source",pd.DataFrame(rows))
    con.execute(f"COPY test_source TO '{datafile}' (FORMAT PARQUET)")
    con.close()
    units={"traits":{"elements":{"fruit_width":{"units":"mm"},"leaf_width":{"units":"mm"}}}}
    cfg=d/"units.yml";cfg.write_text(yaml.safe_dump(units))
    pair={
       "family":"Testaceae","trait_A":"fruit_width","trait_B":"leaf_width",
       "system_A":"A","system_B":"B",
       "n_original_A":25,"n_original_B":25,
       "n_original_shared_species":25,
       "n_same_AusTraits_dataset_species":22}
    data=source_medians(datafile,cfg,[pair])
    assert len(data)==22,repr(data[:2])
    assert all(z[0:5]==("Testaceae","fruit_width","leaf_width","A","B") for z in data)
    assert data[0][7]>data[0][9],data[0]  # all source > source only
    manifest=write_ephemeral_states(data,[pair],d)
    assert len(manifest)==1 and manifest[0]["status"]=="READY"
    assert manifest[0]["n_pair_native_positive_source_median"]==22
    with Path(manifest[0]["state_table"]).open() as fh:
        reconstructed=list(csv.DictReader(fh))
    assert len(reconstructed)==22
    assert float(reconstructed[0]["all_A"])>float(reconstructed[0]["source_A"])
    assert float(reconstructed[0]["all_B"])>float(reconstructed[0]["source_B"])
    # The compiled artifact has one row per pair and cannot include raw
    # species names, measurement records or original contributing source IDs.
    axis={"status":"PASS","n_tips":22,
          "K_full_A":2.0,"K_full_B":1.0,
          "K_source_A":3.0,"K_source_B":1.0,
          "delta_full":math.log(2),
          "delta_source":math.log(3),
          "delta_source_measurements":math.log(3/2)}
    out={"status":STATUS,
         "pairs":[{"pair_id":manifest[0]["pair_id"],
                   "family":"Testaceae","trait_A":"fruit_width",
                   "trait_B":"leaf_width",
                   "n_same_source_positive_species":22,
                   "axes":{"S3":axis,
                     "prune_only":{"status":"HOLD_FEWER_THAN_20_NATIVE_TREE_TIPS","n_tips":12}}}]}
    assert validate_R_results(manifest,out)
    wrong=json.loads(json.dumps(out))
    wrong["pairs"][0]["axes"]["S3"]["delta_source_measurements"]+=.1
    try:validate_R_results(manifest,wrong)
    except ValueError as ex:assert "shift mismatch" in str(ex)
    else:raise AssertionError("source-only source arm K arithmetic mutation undetected")

print("PASS: 279 frozen original organ pairs, synthetic 22 native shared-source species, source-only vs original medians, R K identity invariants")
