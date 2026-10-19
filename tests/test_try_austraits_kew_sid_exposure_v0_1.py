#!/usr/bin/env python3
"""Synthetic 254-system same-named seed source family exposure guard."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_try_austraits_kew_sid_exposure_v0_1 import (
    summarize_kew,certify_public_metadata,STATUS)
names=("fruit_height","fruit_length","fruit_width","leaf_area","leaf_length",
       "leaf_mass_per_area","leaf_width","petiole_length","plant_height",
       "seed_dry_mass","seed_height","seed_length","seed_width")
design=json.loads((ROOT/"data"/"try_austraits_kew_sid_lineage_exposure_v0_1.json").read_text())
d=[{"try_dataset_id":i,"try_dataset_title":f"Unknown {i}"}
   for i in range(1,112)]
d[20]["try_dataset_title"]="KEW Seed Information Database (SID)"
d[564] if False else None
d.append({"try_dataset_id":565,
          "try_dataset_title":"Seed Information Database, Royal Botanic Gardens, Kew"})
meta={"source":{"primary":{"key":"Kew_2019_1",
                             "title":"Seed Information Database (SID) and Seed Bank Database"}},
      "dataset":{"source_id":"original_dataset_id",
                 "custom_R_code":"original_dataset_id = refshort"},
      "traits":[{"trait_name":"seed_dry_mass"}]}
import tempfile,yaml
with tempfile.TemporaryDirectory() as td:
    path=Path(td)/"metadata.yml"
    path.write_text(yaml.safe_dump(meta))
    identity=certify_public_metadata(design,d,path)
    assert identity["try_public_historical_ids"]==[21,565]
    assert identity["austraits_original_nested_source_field"]=="original_dataset_id"
    rows=[];expected={}
    for i in range(254):
        sid=f"A{i+1:04d}"
        f=f"Family{i%42:02d}"
        t=names[i%13]
        expected[sid]={"family":f,"trait_name":t,"n_input_species":20}
        kew=6 if t=="seed_dry_mass" else 0
        rows.append((sid,f,t,20,20,kew,0,0,kew*2,0))
    out=summarize_kew(rows,expected,identity)
    assert out["status"]==STATUS
    assert out["original_species_system_cells"]==254*20
    assert out["traits"]["seed_dry_mass"]["source_exposure_fraction"]==.3
    assert out["traits"]["leaf_area"]["kew_sid_source_species_system_cells"]==0
    assert not out["external_try_v7_independent_validation_qualified"]
    assert not out["K_effects_or_trait_values_exported"]
    try:
        summarize_kew(rows[:-1],expected,identity)
    except ValueError as e:
        assert "254" in str(e)
    else:raise AssertionError("incomplete graph accepted")
    try:
        cert_bad=json.loads(json.dumps(design))
        cert_bad["source_identity"]["try_historical_candidate_ids"]=[21,566]
        certify_public_metadata(cert_bad,d,path)
    except ValueError as e:
        assert "changed" in str(e)
    else:raise AssertionError("relaxed source lineage ID accepted")
print("PASS: same Kew SID named-source family, exact 254 cohorts, no measurements/K effects")
