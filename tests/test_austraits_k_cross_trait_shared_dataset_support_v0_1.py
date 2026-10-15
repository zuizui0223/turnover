#!/usr/bin/env python3
"""Verify K-blind 760 original source pair graph and true shared-dataset logic.

Synthetic source records test same dataset_id vs same observation_id, and
family×pair totals without ever accessing empirical K magnitudes.
"""
from __future__ import annotations
import argparse,json,tempfile
from pathlib import Path
import duckdb,pandas as pd
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_austraits_k_cross_trait_shared_dataset_support_v0_1 import (
  STATUS,read_inputs,query_counts,adjudicate)

p=argparse.ArgumentParser()
for flag in ("core","observed-K","traits-yml","support","design"):
    p.add_argument("--"+flag,required=True,type=Path)
x=p.parse_args()
design=json.loads(x.design.read_text())
support=json.loads(x.support.read_text())
cand,pairs,ref,orig,repro,veg=read_inputs(x.__dict__["observed_K"],
    x.core,x.__dict__["traits_yml"],support,design)
assert len(cand)==254 and len(pairs)==760 and len(ref)==760
original_rows=[(k,v["n"]) for k,v in orig.items()]
rr=[]
for fam,a,b,sa,sb in pairs:
    n=ref[(fam,a,b)]["n_common_species_same_genus"]
    same=22 if n>=22 and a in repro and b in veg else 0
    rr.append((fam,a,b,sa,sb,n,same,min(same,10)))
test=adjudicate(original_rows,rr,orig,ref,repro,veg,design)
assert test["status"]==STATUS
assert test["cross_organ"]["n_original_family_trait_pairs"]==406
assert test["all_pairs"]["n_original_family_trait_pairs"]==760
assert test["cross_organ"]["n_pairs_with_at_least_20_same_dataset_species"]>0
assert test["all_pairs"]["n_pairs_with_at_least_20_same_record_key_species"]==0
assert not test["K_outcomes_opened_or_reestimated"]
assert not test["TRY_v7_independent_source_qualified"]
assert not test["public_species_names_or_measurement_values_emitted"]
try:
    adjudicate(original_rows,rr[:-1],orig,ref,repro,veg,design)
except ValueError as ex:
    assert "not all 760" in str(ex)
else:raise AssertionError("incomplete pair source graph passed")
broken=list(rr)
z=broken[0]
broken[0]=(*z[:5],z[5],z[5]+1,z[7])
try:adjudicate(original_rows,broken,orig,ref,repro,veg,design)
except ValueError as ex:
    assert "impossible" in str(ex)
else:raise AssertionError("same-source support > common species passed")

# Mini real parquet verifies source-native positivity, duplicated records,
# same DatasetID (not necessarily same ObservationID), and same record key.
data=[]
for j in range(25):
    name=f"Genus species{j:03d}"
    for tr,sid in [("fruit_width","A"),("leaf_width","B")]:
        same_dataset=(j<22)
        ds="shared_study" if same_dataset else "fruit_only" if tr=="fruit_width" else "leaf_only"
        observation=f"species{j}" if j<10 else f"{tr}_{j}"
        data.append(dict(family="FamilyX",trait_name=tr,genus="Genus",binomial=name,
                         dataset_id=ds,observation_id=observation,
                         value=float(j+1),taxon_rank="species",unit="mm"))
# An incompatible different-unit duplicate must be ignored by eligibility.
data.append(dict(**{**data[0],"unit":"cm","observation_id":"bad_unit","value":10.0}))
with tempfile.TemporaryDirectory() as tmp:
    df=pd.DataFrame(data)
    c=duckdb.connect(":memory:")
    c.register("tiny_source",df)
    parquet=Path(tmp)/"tiny.parquet"
    c.execute(f"COPY tiny_source TO '{parquet}' (FORMAT PARQUET)")
    c.close()
    old,counts=query_counts(parquet,[("A","FamilyX","fruit_width","mm"),
       ("B","FamilyX","leaf_width","mm")],
       [("FamilyX","fruit_width","leaf_width","A","B")])
    assert dict(old)=={"A":25,"B":25}
    assert len(counts)==1
    assert counts[0][5:]==(25,22,10),counts
print("PASS: original 254 systems, 760 K-blind source pairs and real native-unit dataset/record join")
