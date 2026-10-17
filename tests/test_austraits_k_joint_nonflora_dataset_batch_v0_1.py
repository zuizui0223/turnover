#!/usr/bin/env python3
"""Synthetic original records verify joint five-flora removal + same remaining
DatasetID matched-species K state logic and fail-closed 142 pair source gate.
Observed original K effect values are not accessed for selection/testing.
"""
from __future__ import annotations
import argparse,json,sys,tempfile
from pathlib import Path
import duckdb,pandas as pd,yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from run_austraits_k_joint_nonflora_dataset_batch_v0_1 import (
    cohort,batch_guard,source_medians,STATUS)
from run_austraits_k_same_dataset_pair_batch_v0_1 import write_ephemeral_states

p=argparse.ArgumentParser()
for v in ("source-support","original-pair-support","design"):
    p.add_argument("--"+v,type=Path,required=True)
a=p.parse_args()
source=json.loads(a.source_support.read_text())
original=json.loads(a.original_pair_support.read_text())
cfg=json.loads(a.design.read_text())
selected=cohort(source,original,cfg)
assert len(selected)==142 and len({x["family"] for x in selected})==24
assert batch_guard(selected[:2],source,original,cfg)
corrupt=[{**selected[0],"n_same_AusTraits_dataset_species":99999}]
try:batch_guard(corrupt,source,original,cfg)
except ValueError as e:assert "altered" in str(e)
else:raise AssertionError("mutated 142-pair K-blind cohort allowed")

# 25 original positive species: 22 have a real same-nonflora-dataset
# measurement for both organs, 2 have independent nonflora datasets,
# 1 survives only in the electronic Flora. Original and nonflora medians
# are identical for none of the shared 22 except by construction.
records=[]
for i in range(25):
    species=f"Genus s{i}"
    for trait,name,value in (("fruit_length","A",2.0+i*.03),
                             ("leaf_length","B",5.0+i*.02)):
        records.append({"family":"Testaceae","trait_name":trait,
           "genus":"Genus","binomial":species,"dataset_id":"ABRS_2023",
           "observation_id":f"electronic_{name}_{i}",
           "value":value+11.0,"unit":"mm","taxon_rank":"species"})
        if i<24:
            sourceid="CommonNonFlora" if i<22 else f"Separate_{name}"
            records.append({"family":"Testaceae","trait_name":trait,
              "genus":"Genus","binomial":species,"dataset_id":sourceid,
              "observation_id":f"original_{name}_{i}",
              "value":value,"unit":"mm","taxon_rank":"species"})
            records.append({"family":"Testaceae","trait_name":trait,
              "genus":"Genus","binomial":species,"dataset_id":f"Extra_{name}",
              "observation_id":f"extra_{name}_{i}",
              "value":value+3.0,"unit":"mm","taxon_rank":"species"})
records.append({**records[0],"unit":"cm","value":999999,
                "observation_id":"incompatible"})
with tempfile.TemporaryDirectory(prefix="joint_nonflora_K_fixture_") as t:
    p=Path(t)/"source.parquet"
    con=duckdb.connect(":memory:")
    con.register("source_data",pd.DataFrame(records))
    con.execute(f"COPY source_data TO '{p}' (FORMAT PARQUET)")
    con.close()
    unit=Path(t)/"units.yml"
    unit.write_text(yaml.safe_dump({"traits":{"elements":{
       "fruit_length":{"units":"mm"},"leaf_length":{"units":"mm"}}}}))
    inp=[{
       "family":"Testaceae","trait_A":"fruit_length","trait_B":"leaf_length",
       "system_A":"A","system_B":"B","n_original_A":25,"n_original_B":25,
       "n_same_AusTraits_dataset_species":22}]
    result=source_medians(p,unit,inp)
    assert len(result)==22,(len(result),result[:2])
    assert all(x[:5]==("Testaceae","fruit_length","leaf_length","A","B") for x in result)
    assert all(x[7]>x[9] and x[8]>x[10] for x in result),result[:3]
    items=write_ephemeral_states(result,inp,t)
    assert len(items)==1 and items[0]["status"]=="READY"
    assert items[0]["n_pair_native_positive_source_median"]==22
    assert items[0]["n_source_positive_dataset_common"]==22
print("PASS: fixed 142 source-only pairs, no-flora medians and identical surviving DatasetID median on original K-eligible positive native species")
