#!/usr/bin/env python3
"""Independent NONREFIT source-aggregate QA: BioCON 2021 secondary SLA pilot.

Checks committed immutable observation/result arithmetic and inference status
without original copyrighted raw rows, trained models or any biological refit.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/"results/biocon_e141_2021_secondary_sla_fd_B_NDE_composition_holdout_v0_1.json"
PROTOCOL=ROOT/"docs/BIOCON_E141_2021_SECONDARY_SLA_FD_NDE_PREDICTION_FROZEN_20261124.md"
REPORT=ROOT/"docs/BIOCON_E141_2021_SECONDARY_SLA_FD_B_NDE_RESULTS_20261124.md"

def check():
    j=json.loads(RESULT.read_text(encoding="utf-8"))
    p=PROTOCOL.read_text(encoding="utf-8")
    report=REPORT.read_text(encoding="utf-8")
    assert j["schema_version"]=="1.0"
    assert j["status"]=="RETROSPECTIVE_SECONDARY_2021_PREDICTION_COMPLETED_NO_CAUSAL_CLAIM"
    assert j["original_EDI538_direct_trait_year_data_HTTP_403_HOLD_preserved"] is True
    units=j["observational_units"]
    assert units["field_experiments"]==1 and units["CO2_rings"]==6
    assert units["physical_main_mixture_plots"]==units["original_heldout_planted_species_composition_groups"]==46
    assert (units["richness4_physical_plots"],units["richness9_physical_plots"])==(36,10)
    assert units["original_author_secondary_SLA_direct_E141_candidate_species"]==14
    assert units["original_source_mono_species_treatment_cells"]==64
    assert units["original_mono_replicates_each_cell"]==2
    assert "August 2021" in j["endpoint"]
    g=j["empirical_prediction"]
    for k in ("absolute_B_gain","signed_NDE_gain","NDE_minus_B_gain"):
        assert math.isfinite(g[k])
    assert abs(g["signed_NDE_gain"]-g["absolute_B_gain"]-g["NDE_minus_B_gain"])<1e-12
    intervals=g["fixed_OOF_2000_CO2stratified_6ring_cluster_bootstrap_95CI"]
    for key in ("absolute_B","signed_NDE","NDE_minus_B"):
        lo,hi=intervals[key]
        assert math.isfinite(lo) and math.isfinite(hi)
        assert lo<0<hi, "CI does not straddle zero: report must be independently rereviewed"
    assert g["absolute_B_gain"]<0 and g["signed_NDE_gain"]<0
    sens=g["original_mono_two_replicate_only_sensitivity_signed_NDE_gain"]
    assert len(sens)==2 and all(math.isfinite(x) and x<0 for x in sens.values())
    assert g["NDE_minus_B_gain"]<0
    interp=j["interpretation"]
    for label in (
        "baseline_positive_gain_supported","NDE_vs_absolute_heldout_prediction_advantage_supported",
        "no_negative_causal_FD_effect_established","no_BIEN_AusTraits_K_FD_biomass_mediation_established",
        "no_independent_field_or_publication_replication_established","no_prespecified_confirmatory_analysis_claimed"):
        expected=label.startswith("no_")
        assert interp[label] is expected
    assert j["provenance"]["raw_original_species_data_redistributed"] is False
    assert "HTTP403" in p or "HTTP 403" in p
    for s in ("−3.89%","−9.09%","−5.20","1998–2020","EDI 538","46"):
        assert s in report, "Source report missing a critical numeric/caveat claim: "+s
    print("PASS: exact 46/46 original composition folds, 6 rings and 64×2 mono design")
    print("PASS: independent numeric paired-gain arithmetic and 3 zero-spanning uncertainty intervals")
    print("PASS: 2 original monoculture baseline sensitivities directionally concordant")
    print("PASS: retrospective source/EDI403/causal-status guards and original response privacy")

if __name__=="__main__":
    check()
