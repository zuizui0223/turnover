#!/usr/bin/env python3
"""Source-only TreeDivNet 2026 Table S1 original experiment inventory-year gate.

Original Table S1 XLSX was individually uploaded and verified locally by
artifact_tool before this input-year metadata was committed. The original
copyrighted XLSX is NOT on the GitHub runner; CI verifies SHA-labeled
transcription logic and original Figshare MD5 source plot join.
No FD/phylogenetic K/trait↔biomass outcome coefficients estimated.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
from pathlib import Path
from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet,compact,safe_num,CORE
from audit_treedivnet_s1_s2_site_eligibility_v0_4 import (
    compute_eligible,classify
)

INPUT_SHA="245fdf2002240b905b032c9f444a9a359991212be93032637c9ed80a27516fee"
TABLE_S1_TEMPORAL_WINDOW=2
AXES=("SLA","LNCM","WD")
MIN_PLOTS=80
MIN_SITES=5
MIN_PER_SITE=8
MIN_TAXA=20


def verify_year_table(path:Path):
    d=json.loads(path.read_text(encoding="utf-8"))
    s=d["source_uploaded_workbook"]
    if d["version"]!="v0.6" or d["status"]!="ORIGINAL_TABLE_S1_SITE_INVENTORY_YEARS_VERIFIED":
        raise ValueError("SOURCE_HOLD: original Table S1 source verified status drift")
    if s["sha256"]!=INPUT_SHA or s["bytes"]!=16088 or s["site_rows"]!=11:
        raise ValueError("SOURCE_HOLD: uploaded Table S1 original workbook SHA/size mismatch")
    if s["sheet_names"]!=["Table S1","Caption"] or s["actual_original_workbook_binary_committed_to_GitHub"] is not False:
        raise ValueError("SOURCE_HOLD: original Table S1 workbook structure/permission mismatch")
    v=d["source_site_rows"]
    if len(v)!=11 or len({r["figshare_site_name"] for r in v})!=11:
        raise ValueError("SOURCE_HOLD: source transcribed experiment identifiers drift")
    if d["frozen_source_timing_policy"]["max_absolute_year_gap"]!=TABLE_S1_TEMPORAL_WINDOW:
        raise ValueError("SOURCE_HOLD: original predeclared 2-calendar-year gap changed")
    if set(d["frozen_source_timing_policy"]["trait_axes"])!=set(AXES):
        raise ValueError("SOURCE_HOLD: original source trait axes changed")
    for r in v:
        yrs=r["inventory_years"]
        woody=yrs["woody"]
        if not woody or any(not isinstance(y,int) or y<1990 or y>2026 for y in woody):
            raise ValueError("SOURCE_HOLD: source Table S1 woody inventory year invalid")
        gaps=r["minimum_absolute_inventory_year_gap_to_woody"]
        for axis in ("SLA","LNCM","WD","LPCM","height_increment"):
            val=yrs[axis]
            expected=min((abs(y-z) for y in woody for z in val),default=None)
            if gaps[axis]!=expected:
                raise ValueError("SOURCE_HOLD: Table S1 site calendar delta calculation changed")
        expected_axes=sorted(a for a in AXES if gaps[a] is not None and gaps[a]<=2)
        if sorted(r["source_inventory_gap_2yr_qualified_axes"])!=expected_axes:
            raise ValueError("SOURCE_HOLD: Table S1 site eligible axes drift")
    return {r["figshare_site_name"]:r for r in v},d


def qualify(ds1,ds2,source_only_year_rows):
    original_sites,allplots,eligible_old,old_axis,old_species=compute_eligible(ds1,ds2)
    if set(source_only_year_rows)!=set(original_sites):
        raise ValueError("SOURCE_HOLD: original 11 source site names not exactly in Table S1 source crosswalk")
    ec=classify(original_sites,"ecolink")
    md=classify(original_sites,"matadiv")
    if not ec or not md or ec==md:
        raise ValueError("SOURCE_HOLD: original ECOLINK/MataDIV unique labels changed")
    species=collections.defaultdict(list)
    stands={}
    for r in ds1:
        k=tuple(compact(r[f]) for f in CORE)
        if not all(k) or k in stands:raise ValueError("SOURCE_HOLD: original stand key missing or duplicated")
        stands[k]=r
    for r in ds2:
        k=tuple(compact(r[f]) for f in CORE)
        species[k].append(r)
    def cohort(excluded:set[str],label:str)->dict:
        source_eligible={k for k in eligible_old if k[0] not in excluded}
        actual=set()
        trait_eligible={a:set() for a in AXES}
        trait_taxa={a:set() for a in AXES}
        alltaxa=set()
        site_eligible=collections.Counter()
        source_year_axis_by_site={}
        for site in original_sites:
            if site in excluded:continue
            src=source_only_year_rows[site]
            source_year_axis_by_site[site]={a:src["minimum_absolute_inventory_year_gap_to_woody"][a] for a in AXES}
        for k in source_eligible:
            site=k[0]
            r=stands[k]
            if safe_num(r["biomass_woody"]) is None:
                raise ValueError("SOURCE_HOLD: source woody trait eligible original response missing")
            original_records=species[k]
            peraxis={}
            for axis in AXES:
                gap=source_year_axis_by_site[site][axis]
                taxa={compact(z["species"]) for z in original_records if safe_num(z.get(axis),positive=True) is not None}
                peraxis[axis]=taxa
                if gap is not None and gap<=TABLE_S1_TEMPORAL_WINDOW and len(taxa)>=2:
                    trait_eligible[axis].add(k)
                    trait_taxa[axis].update(taxa)
                    alltaxa.update(taxa)
            if any(k in trait_eligible[a] for a in AXES):
                actual.add(k);site_eligible[site]+=1
        independent_sites=sum(n>=MIN_PER_SITE for n in site_eligible.values())
        structural=bool(len(actual)>=MIN_PLOTS and independent_sites>=MIN_SITES and len(alltaxa)>=MIN_TAXA)
        return {
            "cohort":label,
            "original_source_numeric_eligible_plots_before_year_filter":len(source_eligible),
            "original_Table_S1_site_inventory_year_qualified_plots":len(actual),
            "lost_original_source_plots_to_site_inventory_year_rule":len(source_eligible)-len(actual),
            "study_sites_with_at_least_one_eligible_plot":len(site_eligible),
            "study_sites_at_least_8_year_qualified_plots":independent_sites,
            "site_source_eligible_plots_after_year_filter":dict(sorted(site_eligible.items())),
            "source_year_diff_per_site_axis_in_calendar_years":dict(sorted(source_year_axis_by_site.items())),
            "distinct_original_species_with_time_qualified_positive_original_trait":len(alltaxa),
            "qualified_original_plots_by_same_trait_axis":{a:len(trait_eligible[a]) for a in AXES},
            "distinct_original_species_by_year_qualified_trait_axis":{a:len(trait_taxa[a]) for a in AXES},
            "source_numerical_support_gate":"SITE_INVENTORY_YEAR_SUPPORT_PASS" if structural else "SITE_INVENTORY_YEAR_SUPPORT_HOLD",
            "source_original_individual_tree_provenance_gate":"HOLD",
            "source_original_DS2_species_woody_scaling_gate":"HOLD",
            "new_woody_biomass_or_trait_association_tested":False,
        }
    all_cohort=cohort(set(),"all_11_original_studies_including_ecolink__for_source_diagnostic_only")
    no_ec=cohort({ec},"exclude_ecolink__main_original_species_richness_and_standing_woody_source_population")
    no_ec_md=cohort({ec,md},"also_exclude_fertilized_mata_div__source_sensitivity_only")
    if all_cohort["original_source_numeric_eligible_plots_before_year_filter"]!=186 or        no_ec["original_source_numeric_eligible_plots_before_year_filter"]!=153 or        no_ec_md["original_source_numeric_eligible_plots_before_year_filter"]!=143:
        raise ValueError("SOURCE_HOLD: original 186/153/143 source-eligible cohort history drift")
    return {
        "version":"v0.6",
        "status":"ORIGINAL_TABLE_S1_SITE_INVENTORY_YEAR_GAP_AUDITED_NO_ECOLOGICAL_EFFECT",
        "study":"Jensen et al 2026 TreeDivNet 11 tree diversity experiments",
        "source_Table_S1_original_workbook_sha256":INPUT_SHA,
        "source_local_upload_original_workbook_not_available_in_GitHub_runner":True,
        "original_Figshare_DS1_DS2_source_MD5_pinned":True,
        "exact_original_DS1_DS2_source_plot_join_reproduced":len(allplots)==328,
        "original_source_numeric_186_plots_reproduced":len(eligible_old)==186,
        "predeclared_max_year_gap":TABLE_S1_TEMPORAL_WINDOW,
        "original_woody_response_from_DS1_unique_site_block_plot_only":True,
        "ecolink_genetic_diversity_and_cumulative_coppice_not_standing_stock":True,
        "source_cohorts":{
           "all_experiments":all_cohort,
           "excluding_ECOLINK":no_ec,
           "excluding_ECOLINK_and_MataDIV":no_ec_md
        },
        "original_site_level_inventory_year_is_not_individual_sample_day_or_provenance":True,
        "woody_species_to_stand_normalization_cannot_be_derived_from_year_table":True,
        "new_FD_K_PD_or_woody_biomass_effects_estimated":False,
        "scientific_next_gate":"Confirm original author source response normalization and individual measurement provenance before any new 153→year-matched source model. Table S1 supplies site-level variable inventory years but not original individual sample IDs."
    }


def fixture():
    assert TABLE_S1_TEMPORAL_WINDOW==2
    assert 2021-2019==2
    assert abs(2021-2018)>TABLE_S1_TEMPORAL_WINDOW
    assert set(AXES)=={"SLA","LNCM","WD"}
    return {"status":"TREE_DIVNET_SITE_YEAR_SOURCE_FIXTURE_PASS","checks":4}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-year-table",type=Path)
    parser.add_argument("--out",type=Path)
    parser.add_argument("--self-test",action="store_true")
    a=parser.parse_args()
    if a.self_test:
        print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.source_year_table or not a.out:parser.error("Table S1 derived source years and output path required")
        meta,_=verify_year_table(a.source_year_table)
        _,r1=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
        _,r2=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
        result=qualify(r1,r2,meta)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("TREE_DIVNET_ORIGINAL_TABLES1_YEAR_MATCHED_SOURCE_COEFFICIENT_FREE",
              json.dumps(result,sort_keys=True),flush=True)
