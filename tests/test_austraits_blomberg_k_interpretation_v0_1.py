#!/usr/bin/env python3
"""Synthetic, outcome-free contract tests for the Blomberg-K audit."""
import copy
import runpy
from pathlib import Path

ns=runpy.run_path(str(Path("scripts/analysis/interpret_austraits_blomberg_k_v0_1.py")))
classify=ns["classify"]
contract={
 "status":"POST_RHO_PRE_K_OUTCOME_INTERPRETATION_CONTRACT",
 "interpretation":{
   "family_reference_threshold":0.10,
   "substantial_reordering_threshold":1/3,
   "strong_reordering_threshold":0.40
 }
}
architecture={"status":"AUSTRAITS_BLOMBERG_K_MIXED_MODELS_ESTIMATED"}
portability={"status":"AUSTRAITS_BLOMBERG_K_PORTABILITY_ESTIMATED"}
rho_k={"n_matched_systems":254}
for axis,rho_axis in [("prune_primary","prune"),("S3_sensitivity","S3")]:
  architecture[axis]={"conditional_family_repeatability":0.30}
  portability[axis]={
    "pair_order_reversal":{"weighted_reversal_probability":0.46,"n_trait_pairs":15},
    "absolute_portability":{"gain":0.012,"p_one_sided":0.01,"axis_pass":True},
    "rank_portability":{"gain":-0.02,"p_one_sided":0.4,"axis_pass":False}
  }
  rho_k[rho_axis]={
    "overall_spearman_K_vs_rho":0.5,
    "mean_within_family_rank_correlation":0.2
  }

def decision(a=architecture,p=portability,ref=rho_k,c=contract):
  return classify(a,p,ref,c)["decision"]

assert decision()=="K_ARCHITECTURE_CONCORDANT_BOTH_TREES"

a=copy.deepcopy(architecture)
a["S3_sensitivity"]["conditional_family_repeatability"]=0.03
assert decision(a=a)=="K_ARCHITECTURE_TREE_DEPENDENT"

p=copy.deepcopy(portability)
for axis in ["prune_primary","S3_sensitivity"]:
    p[axis]["pair_order_reversal"]["weighted_reversal_probability"]=0.38
assert decision(p=p)=="K_ARCHITECTURE_SUBSTANTIAL_BOTH_TREES"

p=copy.deepcopy(portability)
for axis in ["prune_primary","S3_sensitivity"]:
    p[axis]["pair_order_reversal"]["weighted_reversal_probability"]=0.23
assert decision(p=p)=="K_ARCHITECTURE_NOT_CORROBORATED"

bad=copy.deepcopy(rho_k)
bad["n_matched_systems"]=253
try:
  decision(ref=bad)
  raise AssertionError("failure to reject changed core")
except AssertionError as exc:
  if str(exc)=="failure to reject changed core":raise

print("PASS: fixed graph, concordant, substantial, tree-dependent and non-corroborated verdicts")
