#!/usr/bin/env python3
"""Synthetic exact original 254-system paired-tip support and science firewalls."""
import itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_k_shared_taxon_pair_support_v0_1 import audit_support,STATUS
d=json.loads((ROOT/"data"/"austraits_k_shared_taxa_cross_trait_design_v0_1.json").read_text())
traits=sorted(d["source"]["expected_named_traits"])
expected={}
family_traits={}
for i in range(254):
    family=f"F{i%42:02d}"
    trait=traits[(i//42+i%42)%12] if i<249 else "seed_height"
    sid=f"A{i+1:04d}"
    # Keep family×trait unique, independent of synthetic trait allocation.
    family_traits.setdefault(family,[])
    while trait in {x[0] for x in family_traits[family]}:
        trait=traits[(traits.index(trait)+1)%12]
    family_traits[family].append((trait,sid))
    expected[sid]={"family":family,"trait":trait,"n_original":50}
pairs=[]
for family,ts in family_traits.items():
    for (t1,s1),(t2,s2) in itertools.combinations(sorted([v for v in ts if v[0]!="seed_height"]),2):
        pairs.append((family,t1,t2,s1,s2))
rows=[]
for family,t1,t2,s1,s2 in pairs:
    overlap=22 if t1 in traits[:3] else 8
    rows.append((family,t1,t2,s1,s2,overlap,0))
r=audit_support([(sid,50) for sid in expected],rows,expected,pairs,traits,d)
assert r["status"]==STATUS and len(r["trait_pairs"])==66
assert r["total_family_trait_pairs_present"]==len(pairs)
assert r["qualifying_family_trait_pairs"]==sum(z[5]>=20 for z in rows)
assert r["no_K_effect_magnitudes_opened"] and r["no_species_or_trait_values_persisted"]
assert all(x["n_common_species_same_genus"]<=50 for x in r["family_trait_pair_support"])
def bad(counts,pair_data,fragment):
    try:audit_support(counts,pair_data,expected,pairs,traits,d)
    except ValueError as e:assert fragment in str(e),str(e)
    else:raise AssertionError("corrupt pair support passed")
bad([(sid,50) for sid in expected][:-1],rows,"254")
bad([(sid,50) for sid in expected],[(*rows[0][:5],53,0)]+rows[1:],"impossible")
bad([(sid,50) for sid in expected],rows[:-1],"not all")
print("PASS: 66 fixed pair types, exact 254-system support, incomplete/invalid graph guards")
