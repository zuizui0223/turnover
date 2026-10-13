#!/usr/bin/env python3
"""Synthetic original 254 K systems; Kew removal cannot touch another trait."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"source"))
from audit_austraits_seed_mass_non_kew_support_v0_1 import summarize,STATUS

traits=["fruit_height","fruit_length","fruit_width","leaf_area","leaf_length",
 "leaf_mass_per_area","leaf_width","petiole_length","plant_height",
 "seed_height","seed_length","seed_width"]
rows=[]; expected={}
for i in range(254):
    sid=f"A{i+1:04d}"; fam=f"F{i%42:02d}"
    if i<15:
        trait="seed_dry_mass"
        n=200 if i<14 else 1442
        surviving=30 if i<14 else 10
    else:
        trait=traits[(i-15)%len(traits)]
        n=260 if i<253 else 208
        surviving=n
    expected[sid]={"family":fam,"trait":trait,"n":n}
    rows.append((sid,fam,trait,n,surviving))
assert sum(r[3] for r in rows)==66330
assert sum(r[3] for r in rows if r[2]=="seed_dry_mass")==4242
out=summarize(rows,expected)
assert out["status"]==STATUS
assert out["original_seed_mass_families"]==15
assert out["nonkew_supported_seed_mass_species_system_cells"]==430
assert out["families_with_at_least_20_remaining_seed_mass_species"]==14
assert out["species_system_cells_lost_due_to_kew_exclusion"]==3812
assert out["K_effect_values_opened"] is False
assert out["TRY_v7_measurements_opened"] is False
for altered,part in [
    (rows[:-1],"254"),
    ([(rows[0][0],rows[0][1],rows[0][2],201,30)]+rows[1:],"support"),
    ([*rows[:-1],(*rows[-1][:4],0)],"altered another trait")
]:
    try:summarize(altered,expected)
    except ValueError as e:assert part in str(e),str(e)
    else:raise AssertionError("invalid source support accepted")
print("PASS: 254 native graph, 15 seed families, 20-species descriptive gate, no K leakage")
