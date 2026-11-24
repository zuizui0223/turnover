#!/usr/bin/env python3
"""Fail closed on 2021 E141 original source biomass component audit claims.
No new original raw data or models; independent aggregate QA.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"results/biocon_e141_original_2021_biomass_components_accounting_v0_1.json"
REPORT=ROOT/"docs/BIOCON_E141_2021_BIOMASS_COMPONENT_ACCOUNTING_RESULTS_20261124.md"

def main():
    j=json.loads(ART.read_text(encoding="utf-8"))
    txt=REPORT.read_text(encoding="utf-8")
    a=j["verified_source_matches"]
    assert a["original_main_four_species_mixture_plots"]==36
    assert a["four_species_plots_with_no_reported_source_species_specific_mass"]==36
    assert a["four_species_plant_species_direct_mass_sum_auditable"]==0
    assert a["original_main_nine_species_mixture_plots"]==10
    assert a["nine_species_B_equals_sum_of_sown_species_masses"]==10
    assert a["original_distinct_monoculture_plots"]==128
    assert a["monoculture_B_equals_originally_sown_one_species_mass"]==128
    assert a["source_original_alternate_Total_Biomass_compared_rows"]==174
    assert a["original_alternate_Total_Biomass_equal_to_B_rows"]==0
    assert a["original_alternate_Total_Biomass_equal_to_B_plus_misc_litter_rows"]==0
    assert a["original_alternate_Total_Biomass_equal_to_B_minus_misc_litter_rows"]==0
    assert a["planted_species_sum_exact_accounting_mismatches_when_auditable"]==0
    assert a["planted_source_components_missing_for_all_36_original_four_species_mixtures"]
    assert not j["source_original_numeric_values_published"] and not j["original_plot_species_IDs_published"]
    s=j["statistical_result_status"]
    assert s["no_new_FD_model_fitted"] and s["no_new_CE_SE_effect_fitted"]
    assert s["original_EDI538_source_year_access_hard_HOLD"]
    assert s["original_field_experiments"]==1 and s["original_CO2_whole_rings"]==6
    for key in ("36","10","128","174","−3.89%","−9.09%","Loreau"):
        assert key in txt
    print("PASS: 46 original B mixture sources, 128 mono, all source component identity denominators")
    print("PASS: no planted-only equivalence claim for 36 unsorted four-species mixtures")
    print("PASS: 174 separate Total Biomass mismatches not treated as biological results")
    print("PASS: original FD results frozen, no causal interpretation or new model refit")

if __name__=="__main__":
    main()
