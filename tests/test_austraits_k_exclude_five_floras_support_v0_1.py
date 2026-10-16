#!/usr/bin/env python3
"""Synthetic positivity/identity and all frozen source support 760 K pairs.

The study's measured K outcomes are NEVER read by this test. Original 254
source-only effects manifest provides system IDs, family and trait names only.
"""
from __future__ import annotations
import argparse,json,tempfile
from pathlib import Path
import duckdb,pandas as pd,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_austraits_k_exclude_five_floras_support_v0_1 import (
    STATUS,check_design,source_only_counts,adjudicate)
from audit_austraits_k_cross_trait_shared_dataset_support_v0_1 import read_inputs

p=argparse.ArgumentParser()
for n in ("observed-K","core","traits-yml","original-pairs","original-source-design","design"):
    p.add_argument("--"+n,required=True,type=Path)
a=p.parse_args()
d=json.loads(a.design.read_text())
original=json.loads(a.__dict__["original_pairs"].read_text())
src_d=json.loads(a.__dict__["original_source_design"].read_text())
excluded=check_design(d)
cand,pairs,_source_pair_ref,expected,repro,veg=read_inputs(
    a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],original,src_d)
assert len(cand)==254 and len(pairs)==760
assert (len(expected),len(repro),len(veg))==(254,6,6)
all_original=[(sid,z["n"]) for sid,z in expected.items()]
all_nonflora=[(sid,max(1,z["n"]//2)) for sid,z in expected.items()]
ref={(r["family"],r["trait_A"],r["trait_B"]):r for r in original["family_trait_pair_support"] if r["qualifies_20_common_species"]}
pairrows=[]
for fam,t1,t2,sa,sb in pairs:
    n=ref[(fam,t1,t2)]["n_common_species_same_genus"]
    retained=int(n*.6)
    shared=int(retained*.8)
    pairrows.append((fam,t1,t2,sa,sb,n,retained,shared))
report=adjudicate(all_original,all_nonflora,pairrows,expected,pairs,repro,veg,d)
assert report["status"]==STATUS
assert report["original_pairs"]==760 and report["original_cross_organ_pairs"]==406
assert len(report["cross_organ_nonflora_supported_family_trait_pairs"])>0
assert report["no_K_effect_values_accessed_or_recomputed"]
assert report["no_species_measurement_values_or_original_record_ids_exported"]
assert report["excluded_five_electronic_floras"]==excluded
try:
    bad=list(pairrows);bad[0]=(*bad[0][:7],bad[0][6]+1)
    adjudicate(all_original,all_nonflora,bad,expected,pairs,repro,veg,d)
except ValueError as e:assert "invalid paired" in str(e)
else:raise AssertionError("more same-dataset than nonflora species must fail")
try:
    adjudicate(all_original[:-1],all_nonflora,pairrows,expected,pairs,repro,veg,d)
except ValueError as e:assert "254 systems" in str(e)
else:raise AssertionError("lost original K source graph accepted")

with tempfile.TemporaryDirectory() as temp:
    temp=Path(temp)
    data=[]
    for j in range(6):
        species=f"Genus sample{j}"
        for trait in ("fruit_length","leaf_length"):
            data.append({
               "family":"Testaceae","trait_name":trait,"genus":"Genus","binomial":species,
               "dataset_id":"ABRS_2023","observation_id":f"{trait}_{j}_flora",
               "value":float(j+1),"unit":"mm","taxon_rank":"species"})
            if j<5:
                ds=("CommonPrimary" if j<4 else ("PrimaryA" if trait=="fruit_length" else "PrimaryB"))
                data.append({"family":"Testaceae","trait_name":trait,"genus":"Genus",
                  "binomial":species,"dataset_id":ds,
                  "observation_id":f"{trait}_{j}_nonflora",
                  "value":float(j+11),"unit":"mm","taxon_rank":"species"})
    # Incorrect native unit, excluded by the K source native-unit policy.
    data.append({**data[0],"unit":"cm","observation_id":"wrong_unit","value":30000})
    con=duckdb.connect(":memory:")
    con.register("observed",pd.DataFrame(data))
    path=temp/"synthetic.parquet"
    con.execute(f"COPY observed TO '{path}' (FORMAT PARQUET)")
    con.close()
    orig,no,rows=source_only_counts(path,
       [("sA","Testaceae","fruit_length","mm"),("sB","Testaceae","leaf_length","mm")],
       [("Testaceae","fruit_length","leaf_length","sA","sB")],excluded)
    assert set(orig)=={("sA",6),("sB",6)}
    assert set(no)=={("sA",5),("sB",5)}
    assert rows==[("Testaceae","fruit_length","leaf_length","sA","sB",6,5,4)],rows
print("PASS: source-only 254 system + 760 pairs, five floras excluded, 6 original species ->5 nonflora ->4 same dataset")
