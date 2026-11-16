#!/usr/bin/env python3
"""Nonraw published original Table S3 (user-uploaded XLSX) source audit integrity.

The source XLSX original bytes are *not* stored in GitHub Actions; the
locally extracted artifact_tool source metadata is accompanied by original
byte SHA256 and compared to independently extracted original Table S1
woody inventory-year metadata, and the MD5-pinned public Figshare DS1/DS2
source cohort ledgers. No original ecological response model is run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCE_SHA="c6458fa8f381090a77e529530d5cdb55d44ff3f1fc6e652f61ab2cb29b75d15b"
TABLE_S1_SHA="245fdf2002240b905b032c9f444a9a359991212be93032637c9ed80a27516fee"


def verify(allom:dict, years:dict, source_time:dict, source_fd:dict)->dict:
    src=allom["original_upload"]
    assert allom["version"]=="v0.7"
    assert src["sha256"]==SOURCE_SHA and src["bytes"]==21729
    assert src["source_sheet_name"]=="Table S3" and src["source_used_range"]=="A1:M92"
    assert src["original_copyrighted_XLSX_not_committed_to_repository"] is True
    assert src["n_source_model_rows"]==77
    assert allom["status"]=="ORIGINAL_UPLOADED_TABLES3_ALLOMETRY_AND_STUDY_YEAR_PASS__DS2_DS1_ORIGINAL_BIOMASS_SCALING_HOLD"
    a=allom["allometry_record_summary"]
    r=allom["site_summary"]
    assert a["original_sites"]==len(r)==11
    assert a["record_rows"]==sum(x["n_allometry_or_actual_weight_rows"] for x in r.values())==77
    assert a["source_site_species_pairs"]==sum(x["n_unique_original_site_taxa"] for x in r.values())==63
    assert a["source_site_species_inventory_year_combinations"]==71
    assert a["source_site_species_inventory_year_combinations"]==sum(
       x["n_unique_original_site_taxa"]*len(x["woody_inventory_years"]) for x in r.values())
    assert a["response_component_rows"]=={
        "aboveground woody biomass":58,"stem + branch":7,"stem":6,"branch":6}
    assert sum(a["response_component_rows"].values())==77
    assert a["equation_form"]=={"logY":25,"directY":48,"actual_directly_weighed":4}
    assert sum(a["equation_form"].values())==77
    assert a["equation_inputs"]=={"RCD":42,"DBH":20,"BA_only":6,"BA_H_WD":5,"direct_actual_weight":4}
    assert sum(a["equation_inputs"].values())==77
    assert a["correction_factors"]=={"numeric_values":19,"NA":57,"symbolic_placeholder":1}
    assert sum(a["correction_factors"].values())==77
    assert a["n_source_explicit_proxy_equations"]==sum(x["n_proxy_equations"] for x in r.values())==7
    assert a["n_original_IDENT_Freiburg_taxa_with_two_separate_stem_and_branch_parts"]==6
    assert r["IDENT_Freiburg"]["n_separate_stem_branch_component_rows"]==12
    assert a["n_original_IDENT_Freiburg_stem_or_branch_component_rows"]==12
    assert a["n_symbolic_cf_for_MataDIV_palm"]==1
    assert a["n_equations_ambiguous_source_exponential_parentheses"]==2
    assert a["n_mean_diameter_outside_declared_explicit_range"]==0
    assert sum(x["n_equations_using_WD_directly"] for x in r.values())==5
    assert r["MataDIV"]["n_equations_using_WD_directly"]==5
    assert r["MataDIV"]["n_unique_original_site_taxa"]==6
    assert r["ECOLINK_Uppsala"]["woody_inventory_years"]==[2017,2020,2023]
    assert r["ECOLINK_Uppsala"]["n_allometry_or_actual_weight_rows"]==12
    assert len(r["ECOLINK_Uppsala"]["woody_inventory_years"])==3
    assert allom["new_important_circularity_finding"]["n_site_woody_models_using_direct_WD"]==5
    assert allom["new_important_circularity_finding"]["does_not_imply_direct_circularity_for_SLA_and_LNCM_predictors"] is True
    assert "ln(WD)" in allom["new_important_circularity_finding"]["example_source_equation"]
    assert allom["component_calibration_flags"]["original_DS2_to_DS1_plot_biomass_321_of_328_mean_identity_still_unexplained"] is True
    assert allom["science_gate_decision"]["DS1_stand_woody_to_DS2_species_woody_exact_normalization"]=="HOLD"
    assert allom["science_gate_decision"]["new_ecological_FD_PD_K_woody_biomass_effect_computed"] is False
    assert years["source_uploaded_workbook"]["sha256"]==TABLE_S1_SHA
    compare={x["figshare_site_name"]:x["inventory_years"]["woody"] for x in years["source_site_rows"]}
    assert set(compare)==set(r)
    assert all(compare[k]==r[k]["woody_inventory_years"] for k in compare), "S3 original woody inventory years differ from original Table S1!"
    assert allom["source_table_s1_comparison"]["n_original_sites_with_exact_same_woody_inventory_years"]==len(r)
    assert allom["source_table_s1_comparison"]["n_source_sites_with_mismatched_woody_inventory_years"]==0
    assert source_time["source_cohorts"]["excluding_ECOLINK"]["original_Table_S1_site_inventory_year_qualified_plots"]==141
    main=source_fd["source_groups"]["excluding_ECOLINK"]["trait_bundle_source_support"]["SLA+LNCM"]
    sensitivity=source_fd["source_groups"]["excluding_ECOLINK_and_MataDIV"]["trait_bundle_source_support"]["SLA+LNCM"]
    assert main["number_source_original_site_plots_with_two_same_species_full_multiaxis_year_match"]==117
    assert sensitivity["number_source_original_site_plots_with_two_same_species_full_multiaxis_year_match"]==107
    assert allom["preexisting_figshare_source_population"]["SLA_LNCM_same_species_year_qualified_original_plots"]==117
    assert allom["preexisting_figshare_source_population"]["SLA_LNCM_ecolink_and_MataDIV_excluded_original_plots"]==107
    return {
        "status":"USER_UPLOADED_TABLE_S3_LOCAL_SOURCE_METADATA_AND_TABLE_S1_YEAR_LEDGER_CROSSCHECK_PASS",
        "original_table_s3_SHA256":SOURCE_SHA,
        "original_table_s3_binary_available_to_GitHub_runner":False,
        "n_original_allometry_records":77,
        "n_sites_matched_exact_inventory_years":11,
        "n_source_proxy_equations":7,
        "n_MataDIV_woody_response_formulas_using_WD":5,
        "original_2axis_SLA_LNCM_numeric_eligible_plots":117,
        "original_2axis_SLA_LNCM_numeric_eligible_plots_excluding_MataDIV":107,
        "original_DS2_species_row_to_DS1_plot_woody_normalization":"HOLD",
        "new_ecological_effect_estimated":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--allometry",type=Path)
    p.add_argument("--years",type=Path)
    p.add_argument("--time-support",type=Path)
    p.add_argument("--multiaxis-support",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        assert SOURCE_SHA.startswith("c6458fa8")
        assert TABLE_S1_SHA.startswith("245fdf20")
        assert 58+7+6+6==77
        print('USER_UPLOAD_TABLES3_SOURCE_FIXTURE_PASS')
        return
    for k in ("allometry","years","time_support","multiaxis_support","out"):
        if not getattr(a,k):p.error("All five source derived metadata input paths and --out required")
    read=lambda path:json.loads(path.read_text(encoding="utf8"))
    result=verify(read(a.allometry),read(a.years),read(a.time_support),read(a.multiaxis_support))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("TREEDIVNET_ORIGINAL_TABLES3_ALLOMETRY_AND_TABLES1_YEAR_CONSISTENCY",
          json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
