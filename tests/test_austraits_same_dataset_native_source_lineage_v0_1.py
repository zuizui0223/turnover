#!/usr/bin/env python3
"""Exact frozen 279 K-blind source-eligible graph plus synthetic provenance.

Neither biological original K effects nor observed fruit/leaf state measurements
are accessed for a source mode classification or source concentration estimate.
"""
from __future__ import annotations
import argparse,json,tempfile
from pathlib import Path
import pandas as pd,duckdb,yaml
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_same_dataset_native_source_lineage_v0_1 import (
    category,source_cells,summarize,STATUS)
from run_austraits_k_same_dataset_pair_batch_v0_1 import qualify
p=argparse.ArgumentParser()
p.add_argument("--source-support",type=Path,required=True)
p.add_argument("--original-pair-support",type=Path,required=True)
a=p.parse_args()
source=json.loads(a.source_support.read_text())
original=json.loads(a.original_pair_support.read_text())
design=json.loads((ROOT/"data"/"austraits_k_same_dataset_organ_matched_tip_sensitivity_v0_1.json").read_text())
selected=qualify(source,original,design)
assert len(selected)==279
sample={
  "source":{"primary":{"title":"Flora of Australia"}},
  "dataset":{"description":"Species profiles extracted from flora online"},
  "traits":[{"trait_name":"leaf_length","basis_of_value":"measurement"}]
}
assert category(sample)=="EXPLICIT_FLORISTIC_SPECIES_PROFILE_METADATA_INDICATOR"
sample["source"]["primary"]["title"]="Seed Information Database"
sample["dataset"]["description"]="Original compiled source"
assert category(sample)=="EXPLICIT_DATABASE_OR_COMPILATION_METADATA_INDICATOR"
sample["source"]["primary"]["title"]="Measured seed and leaf traits"
sample["dataset"]={"description":"Field collections","basis_of_record":"field"}
assert category(sample)=="METADATA_CONSISTENT_WITH_DIRECT_MEASUREMENT_NOT_VALIDATED"
sample["dataset"]["basis_of_record"]="unknown"
assert category(sample)=="SOURCE_MODALITY_UNDETERMINED_BY_PUBLIC_METADATA"
fixture={r["dataset_id"]:r for r in []}
tot=sum(x["n_same_AusTraits_dataset_species"] for x in selected)
meta={"test_dataset":{
  "dataset_id":"test_dataset",
  "public_metadata_url":"https://example.org/source",
  "source_citation_title":"Flora of Australia",
  "source_primary_doi":"",
  "description":"Flora native trait entries",
  "basis_of_record":"species",
  "provisional_source_modality":"EXPLICIT_FLORISTIC_SPECIES_PROFILE_METADATA_INDICATOR",
  "original_native_trait_variables":{},
  "original_source_dataset_id_may_combine_other_primary_studies":True,
  "same_specimen_or_protocol_verified":False,
  "independent_primary_measurement_verified":False
}}
paircounts=[(x["family"],x["trait_A"],x["trait_B"],x["n_same_AusTraits_dataset_species"])
            for x in selected]
out=summarize(paircounts,[("test_dataset",tot,279,32)],(tot,0),selected,meta)
assert out["status"]==STATUS
assert out["n_original_contributing_AusTraits_dataset_IDs"]==1
assert out["n_source_positive_species_pair_cells"]==tot
assert not out["K_effects_reestimated_or_source_selected_from_K"]
assert not out["raw_species_observation_or_measurement_values_exported"]
assert not out["independent_source_or_specimen_confirmed"]
invalid=list(paircounts)
f,a,b,n=invalid[0]
invalid[0]=(f,a,b,n-1)
try:summarize(invalid,[("test_dataset",tot,279,32)],(tot,0),selected,meta)
except ValueError as ex:assert "source-count changed" in str(ex)
else:raise AssertionError("post-K source eligibility mutated")

# Native positive source and genus species cohort reconstruction on synthetic
# two organs. A repeated observed value in a common dataset cannot multiply
# source-pair cells; a wrong unit can never enter original source eligibility.
with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    data=[]
    for j in range(25):
        for sid,trait in (("X","fruit_length"),("Y","leaf_length")):
            ds=("sameFlora" if j<22 else "fruit_only" if sid=="X" else "leaf_only")
            data.append({
               "family":"FamilyX","trait_name":trait,"genus":"Genus",
               "binomial":f"Genus sample{j}","dataset_id":ds,
               "observation_id":f"record{j}_{sid}","value":float(j+1),
               "unit":"mm","taxon_rank":"species"})
    data.append({**data[0],"unit":"cm","value":1000.0})
    parquet=d/"mini.parquet"
    cx=duckdb.connect(":memory:");cx.register("records",pd.DataFrame(data))
    cx.execute(f"COPY records TO '{parquet}' (FORMAT PARQUET)");cx.close()
    dictfile=d/"units.yml"
    dictfile.write_text(yaml.safe_dump({"traits":{"elements":{
      "fruit_length":{"units":"mm"},"leaf_length":{"units":"mm"}}}}))
    cnt,sources,dimensions=source_cells(parquet,dictfile,[{
      "family":"FamilyX","trait_A":"fruit_length","trait_B":"leaf_length",
      "system_A":"X","system_B":"Y","n_original_A":25,"n_original_B":25
    }])
    assert cnt==[("FamilyX","fruit_length","leaf_length",22)],cnt
    assert len(sources)==1 and sources[0][0]=="sameFlora" and sources[0][1]==22
    assert dimensions==(22,0),dimensions
print("PASS: exact frozen 279 source pairs, floristic/database/direct/unknown metadata categories, 22 true common-dataset native-source species")
