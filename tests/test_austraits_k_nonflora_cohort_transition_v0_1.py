#!/usr/bin/env python3
"""Verify three-stage 283→142 original K comparison and reject mutated input.

Tests never fit a new evolutionary process or select species/trait pairs.
Independently check original published counts, signed K identities, strict
142 within 283 original source eligible graph, and 42-family dependence.
"""
from __future__ import annotations
import argparse,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"/"analysis"))
from audit_austraits_k_nonflora_cohort_transition_v0_1 import audit,STATUS,STAGES

p=argparse.ArgumentParser()
for s in ("broad","joint","design"):
    p.add_argument("--"+s,required=True,type=Path)
a=p.parse_args()
B=json.loads(a.broad.read_text());J=json.loads(a.joint.read_text());D=json.loads(a.design.read_text())
out=audit(B,J,D)
assert out["status"]==STATUS
expected={
  "S3":{"n":142,"family":24,"stage":[110,121,120],"step_flips":[23,9,26]},
  "prune_only":{"n":101,"family":18,"stage":[82,83,81],"step_flips":[13,12,15]}
}
for axis,exp in expected.items():
    z=out["axes"][axis]
    assert (z["n_pair_identities"],z["n_plant_families"])==(exp["n"],exp["family"])
    assert [z["stage_rates"][s]["n_reproductive_K_higher"] for s in STAGES]==exp["stage"]
    assert [w["n_pairwise_K_sign_reversals"] for w in z["paired_steps"].values()]==exp["step_flips"]
    for stat in z["stage_rates"].values():
        assert 0<stat["pair_weighted_fraction"]<1
        assert 0<=stat["family_bootstrap_pair_weighted_CI95"][0]<=stat["family_bootstrap_pair_weighted_CI95"][1]<=1
    assert z["paired_steps"][STAGES[1]+"_TO_"+STAGES[2]]["median_absolute_delta_logK"] < z["paired_steps"][STAGES[0]+"_TO_"+STAGES[1]]["median_absolute_delta_logK"]
assert out["after_original_reproductive_K_organ_results"]
assert not out["not_new_evolutionary_process_hypothesis_or_independent_external_validation"] is False

def must_fail(b,j,fragment):
    try:audit(b,j,D)
    except ValueError as ex:
        assert fragment in str(ex),repr(ex)
    else:raise AssertionError("bad source K data accepted: "+fragment)

bad=copy.deepcopy(J)
bad["axes"]["S3"]["pair_level_K_decisions_no_species_names"].pop()
must_fail(B,bad,"incomplete")
bad=copy.deepcopy(J)
z=bad["axes"]["S3"]["pair_level_K_decisions_no_species_names"][0]
z["n_same_source_species"]+=100000
must_fail(B,bad,"strict original native tree retains MORE" if False else "same-source selected tips exceed")
bad=copy.deepcopy(J)
z=bad["axes"]["S3"]["pair_level_K_decisions_no_species_names"][0]
z["delta_identical_nonflora_dataset"]+=.2
must_fail(B,bad,"original pre-recorded pair K signs inconsistent" if z["delta_identical_nonflora_dataset"]* (z["delta_identical_nonflora_dataset"]-.2) < 0 else "strict identical-tip source arm K contrast mismatch")
bad=copy.deepcopy(B)
bad["status"]="NOT_FROZEN"
must_fail(bad,J,"not the two verified")
print("PASS: exact 283/142 original K graph, 3-stage 24/18-family sensitivity, flip decomposition and corruption tests")
