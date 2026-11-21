#!/usr/bin/env python3
"""QA original two independent Wagg source-derived outputs and posthoc identity.

No original biomass source download, no new hypothesis fit, no new p values.
"""
from __future__ import annotations
import json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"results/jena_tbe2012_mono_based_84plot_NDE_CE_SE_v0_1.json"
B=ROOT/"results/jena_tbe2012_original_84plot_expected_mono_NDE_mass_accounting_v0_1.json"
OLD_ANNUAL_POINT=35.3417884482801
OLD_ANNUAL_BOOT_CI=[-76.27843095189692,146.7342674382457]

def must(test,msg):
    if not test:raise AssertionError(msg)

def main():
    a=json.loads(A.read_text())
    b=json.loads(B.read_text())
    assert a["status"]=="JENA_TBE_2012_MONO_BASED_CE_SE_NDE_DESCRIPTIVE_PARTITION_COMPLETE"
    assert b["status"]=="JENA_TBE_ORIGINAL_84PLOT_OBSERVED_EXPECTED_MONO_NDE_ACCOUNTING_REPRODUCED"
    must(a["source_eligibility"]["mono_original_plot_ids"]==24,"mono source drift")
    must(a["source_eligibility"]["matched_primary_mixtures"]==84,"mix source drift")
    must(b["n_original_mixture_plot_units"]==84 and b["n_mono_plot_units"]==24,"source source-gate drift")
    must(a["source_original_sha256"]==b["source_original_sha256"],"original PANGAEA SHA mismatch")
    effects=b["highFD_minus_lowFD_g_dry_m2"]
    must(math.isclose(effects["observed_sown_mass"],OLD_ANNUAL_POINT,abs_tol=1e-11),"source older absolute g/m2 does not replay")
    must(math.isclose(effects["observed_sown_mass"],
            effects["monoculture_expected_baseline"]+effects["net_diversity_effect"],abs_tol=1e-11),
         "absolute biomass ≠ source matched mono expectation + NDE")
    must(math.isclose(effects["net_diversity_effect"],
            effects["Loreau_Hector_complementarity"]+effects["Loreau_Hector_selection"],abs_tol=1e-11),
         "original NDE ≠ CE+SE")
    for old,new in (
        ("NDE_high_minus_low_g_dry_m2","net_diversity_effect"),
        ("CE_high_minus_low_g_dry_m2","Loreau_Hector_complementarity"),
        ("SE_high_minus_low_g_dry_m2","Loreau_Hector_selection")):
        must(math.isclose(a["primary"][old],effects[new],abs_tol=1e-11),"source component drift "+old)
    cis=b["paired_stratified_plot_bootstrap_95CI_g_dry_m2"]
    assert set(cis)==set(effects)
    for label,interval in cis.items():
        must(len(interval)==2 and interval[0]<0<interval[1],f"uncertain source {label} CI changed")
    must(all(math.isclose(x,y,abs_tol=1e-11) for x,y in zip(cis["observed_sown_mass"],OLD_ANNUAL_BOOT_CI)),
         "source absolute biomass source plot-bootstrap changed")
    for old,new in (
        ("NDE_CI95","net_diversity_effect"),
        ("CE_CI95","Loreau_Hector_complementarity"),
        ("SE_CI95","Loreau_Hector_selection")):
        must(all(math.isclose(x,y,abs_tol=1e-11) for x,y in zip(a["primary"][old],cis[new])),
             "source CE SE NDE bootstrap changed "+old)
    must(b["source_original_plot_bootstrap_refits"]==a["uncertainty"]["successful_refits"]==2000,
         "original paired bootstrap refits drift")
    must(not b["randomized_spatial_block_identity_verified"]
         and not a["scientific_guard"]["FD_specific_causal_effect_identified"],"causal overreach")
    must(b["posthoc_source_accounting_after_numerical_results"],"post outcome chronology hidden")
    must(b["source_original_sown_species_and_plot_rows_redistributed"] is False,"source row redistribution")
    result={"status":"JENA_TBE_ORIGINAL_84_SOURCE_COMPONENT_ACCOUNTING_QA_PASS",
           "original_24_monocultures":True,"same_84_mixtures":True,
           "observed_equals_expected_plus_NDE_exact":True,
           "NDE_equals_CE_plus_SE_exact":True,
           "all_five_paired_bootstrap_intervals_include_zero":True,
           "NDE_CE_SE_CIs_match_independently_committed_original_run":True,
           "original_2000_same_plot_bootstrap_refits_match":True,
           "source_original_plot_prefix_only":True,
           "new_ecological_model_fits":0,"causal_mediation_claim":False}
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
