#!/usr/bin/env python3
"""BioCON 2021 FD geometry independent aggregate and claim-boundary QA."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"results/biocon_e141_2021_secondary_SLA_predictor_identifiability_v0_1.json"
DOC=ROOT/"docs/BIOCON_E141_2021_SOURCE_FD_IDENTIFIABILITY_RESULTS_20261124.md"
def run():
    j=json.loads(DATA.read_text(encoding="utf-8"))
    a=j["source_only_results"]
    assert a["original_source_plots"]==46 and a["richness4_plots"]+a["richness9_plots"]==46
    assert a["independent_CO2_rings"]==len(a["original_ring_plot_counts_unlabeled"])==6
    assert sum(a["original_ring_plot_counts_unlabeled"])==46
    assert a["M0_parameter_count"]==9 and a["M1_parameter_count"]==10
    assert abs(a["FD_weighted_R2_given_M0"]+a["FD_residual_fraction_given_M0"]-1)<1e-12
    assert abs(a["FD_VIF"]*a["FD_residual_fraction_given_M0"]-1)<1e-12
    assert 0<a["FD_weighted_R2_given_M0"]<0.5
    assert a["full_46_fold_M1_weighted_design_condition_max"]<10
    assert a["full_46_fold_M1_weighted_design_condition_median"]>a["full_46_fold_M0_weighted_design_condition_median"]
    assert a["folds_leverage_ratio_above_1_5"]==4 and a["folds_leverage_ratio_above_2"]==1
    assert a["original_biomass_NDE_values_opened"] is False
    assert a["original_B_NDE_model_refitted"] is False
    assert j["conditional_interpretation"]["strong_collinearity_explanation_supported"] is False
    assert j["conditional_interpretation"]["no_change_to_prior_effects_or_uncertainty"] is True
    assert j["conditional_interpretation"]["no_FD_causal_negative_effect_inference"] is True
    d=DOC.read_text(encoding="utf-8")
    for value in ("24.21%","75.79%","1.32","46","HTTP 403","−3.89%","−9.09%"):
        assert value in d,value
    print("PASS: original 46 source plot/6 ring and predictor source geometry pinned")
    print("PASS: FD VIF, weighted partial source R2, 46-fold condition numbers arithmetic")
    print("PASS: 4 leverage >1.5x and 1 >2x as original source-only diagnostic")
    print("PASS: EDI HTTP403 and original B/NDE numeric effects remain unchanged")
if __name__=="__main__":
    run()
