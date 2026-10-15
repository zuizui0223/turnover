#!/usr/bin/env python3
"""Original K graph/units and synthetic metadata-tagged floristic records.

No actual observed K is used beyond system ID/family/trait. Synthetic method
contexts verify that genus/family inference labels are NEVER confused with
actual independent biological observations or absence of evidence.
"""
import argparse,json,tempfile,sys
from pathlib import Path
import pandas as pd,duckdb,yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_austraits_k_taxonomic_context_record_v0_1 import (
    prepare,fetch_counts,audit,STATUS)

p=argparse.ArgumentParser()
for nm in ("observed-K","core","traits-yml","design"):
    p.add_argument("--"+nm,required=True,type=Path)
a=p.parse_args()
d=json.loads(a.design.read_text())
candidates,expected=prepare(a.__dict__["observed_K"],a.core,a.__dict__["traits_yml"],d)
assert len(expected)==254 and len(candidates)==254
assert sum(x["n"] for x in expected.values())==66330
orig=[(sid,z["n"]) for sid,z in expected.items()]
flagged=[("ABRS_2023","fruit_length",25,22,1,1,0,3,2,0,0,12,5,16,5)]
z=audit(orig,flagged,expected,d)
assert z["status"]==STATUS and z["total_higher_taxon_inference_flagged_original_positive_source_records"]==5
assert z["trait_dataset_results"][0]["n_inferred_from_genus_records"]==3
assert z["trait_dataset_results"][0]["n_inferred_from_family_records"]==0
assert not z["K_reestimated_or_selected_using_context"]
assert not z["species_names_measurement_values_or_ids_exported"]
try:
    audit(orig[:-1],flagged,expected,d)
except ValueError as e:
    assert "missing" in str(e)
else:raise AssertionError("original 254 native K species count mismatch accepted")
with tempfile.TemporaryDirectory() as td:
    path=Path(td)
    rows=[]
    for i in range(25):
      method='{"trait scoring method":"inferred_from_genus"}' if i<3 else (
          '{"trait scoring method":"inferred_from_family"}' if i==3 else (
          '{"trait scoring method":"scored from text"}' if i<15 else ''))
      rows.append(dict(family="Sampleaceae",trait_name="fruit_length",
            genus="Genus",binomial=f"Genus sample{i}",
            dataset_id="ABRS_2023",observation_id=f"obs{i}",
            value=float(i+1),unit="mm",taxon_rank="species",
            method_context_properties=method))
    # The one wrong-unit original measurement must not leak into original
    # species median support or method-context inference counts.
    rows.append({**rows[5],"unit":"cm","value":9999.0,
          "observation_id":"wrong_unit","method_context_properties":"inferred_from_taxonomy"})
    df=pd.DataFrame(rows)
    c=duckdb.connect(":memory:");c.register("source",df)
    parquet=path/"mini.parquet"
    c.execute(f"COPY source TO '{parquet}' (FORMAT PARQUET)");c.close()
    original,result=fetch_counts(parquet,[("SID","Sampleaceae","fruit_length","mm")],d)
    assert original==[("SID",25)],original
    assert len(result)==1,result
    src,trait,n_record,n_cell,n_system,n_fam,n_faminfer,n_genus,n_taxon,n_species,n_trait,n_scored,n_higher,n_context,n_higher_cells=result[0]
    assert (src,trait,n_record,n_cell,n_system,n_fam)==("ABRS_2023","fruit_length",25,25,1,1)
    assert (n_faminfer,n_genus,n_taxon,n_higher,n_higher_cells)==(1,3,0,4,4)
    assert n_scored==11 and n_context==15
print("PASS: frozen original 254 K source median graph, native inferred-from-genus/family/specific context and wrong-unit exclusion")
