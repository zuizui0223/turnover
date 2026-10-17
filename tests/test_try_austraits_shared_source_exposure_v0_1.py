#!/usr/bin/env python3
"""Synthetic 254-system source-only graph and strict Tng metadata identity tests."""
import sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_try_austraits_shared_source_exposure_v0_1 import summarize,STATUS
settings={}
rows=[]
names=["seed_width","leaf_area","seed_dry_mass","leaf_width","petiole_length",
       "fruit_width","fruit_length","fruit_height","leaf_length","plant_height",
       "seed_length","seed_height","leaf_mass_per_area"]
for i in range(254):
    sid=f"A{i+1:04d}";fam=f"F{i%42:02d}";trait=names[i%13]
    settings[sid]={"family":fam,"trait_name":trait,"n_input_species":20}
    strong=(2 if trait=="leaf_area" else 0)
    weak=3 if i%7==0 else 0
    both=1 if strong and weak else 0
    rows.append((sid,fam,trait,20,20,strong,weak,both,strong*4,weak*2))
result=summarize(rows,settings,{"Tng_2013"},{"Dong_2017","Wright_2001"})
assert result["status"]==STATUS
assert result["graph"]=={"systems":254,"families":42,"traits":13}
assert result["overall"]["species_system_cells"]==5080
assert result["traits"]["leaf_area"]["strong_shared_publication_lead_species_system_cells"]>0
assert result["traits"]["seed_width"]["strong_shared_publication_lead_species_system_cells"]==0
assert result["overall"]["n_external_named_traits_with_any_strong_study_source"]==1
assert not result["K_effect_values_opened"] and not result["TRY_v7_measurements_opened"]
def bad(rr,part):
    try:summarize(rr,settings,{"Tng_2013"},{"Wright_2001"})
    except ValueError as e:assert part in str(e),str(e)
    else:raise AssertionError("accepted invalid source cohort")
bad(rows[:-1],"254")
bad([(*rows[0][:3],19,*rows[0][4:])]+rows[1:],"cohort changed")
bad([(*rows[0][:5],21,*rows[0][6:])]+rows[1:],"impossible")
print("PASS: original 254-system support, signed 5-trait exposure, source-only and corruption guards")
