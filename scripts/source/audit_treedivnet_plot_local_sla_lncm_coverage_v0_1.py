#!/usr/bin/env python3
"""Original-source-only FD support for plot-local SLA+LNCM tree species.

Excludes ECOLINK (genotype/cumulative coppice), predeclares >=80% joint
same-species original plot trait coverage, original richness source exact,
and original Table S1 woody/trait inventory year <=2. No biomass model.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet,compact,safe_num,CORE
from audit_treedivnet_table_s1_year_matched_plots_v0_6 import verify_year_table

JOINT_AXES=("SLA","LNCM")
MIN_COVERAGE=0.8
MIN_SOURCE_PLOTS=80
MIN_SITES=5
MIN_SITE_PLOTS=8
MIN_TAXA=20
YEAR_GAP_MAX=2

def counts_for_scope(plots:dict, detail:dict, years:dict, without: set[str], label:str):
    initial=[]
    exact=[]
    chosen=[]
    species_all=set()
    sites=collections.Counter()
    richness_errors=collections.Counter()
    coverage_hist=collections.Counter()
    n_any=0
    for key,plot in sorted(plots.items()):
        site=key[0]
        if site in without or key not in detail:
            continue
        year=years[site]["minimum_absolute_inventory_year_gap_to_woody"]
        if any(year[t] is None or year[t]>YEAR_GAP_MAX for t in JOINT_AXES):
            continue
        biomass=safe_num(plot.get("biomass_woody"))
        if biomass is None:continue
        ds2=detail[key]
        present={compact(row.get("species")) for row in ds2}
        rich=safe_num(plot.get("species_richness"),positive=True)
        if rich is None or not present:raise ValueError("SOURCE_HOLD: source richness or taxon labels invalid")
        rr=int(rich)
        if rr!=rich:raise ValueError("SOURCE_HOLD: source richness noninteger")
        joint={compact(row.get("species")) for row in ds2 if all(
            safe_num(row.get(t),positive=True) is not None for t in JOINT_AXES)}
        if len(joint)<2:continue
        initial.append(key)
        if rr!=len(present):
            richness_errors[site]+=1
            continue
        exact.append(key)
        if rr<2 or len(joint)>rr:
            raise ValueError("SOURCE_HOLD: original trait taxa or planted richness inconsistent")
        cov=len(joint)/rr
        coverage_hist["100pct" if cov==1 else "80to99pct" if cov>=.8 else
                      "60to79pct" if cov>=.6 else "under60pct"]+=1
        if cov<MIN_COVERAGE:continue
        chosen.append(key)
        sites[site]+=1
        species_all.update(joint)
    nsites=sum(x>=MIN_SITE_PLOTS for x in sites.values())
    return {
      "source_population":label,
      "source_original_year_aligned_plot_with_2plus_joint_axis_species":len(initial),
      "original_source_richness_equals_unique_DS2_species_rows":len(exact),
      "original_source_plots_rejected_richness_mismatch":len(initial)-len(exact),
      "n_original_source_plots_full_joint_axis_trait_coverage_ge80pct":len(chosen),
      "n_original_study_sites_any_source_eligible":len(sites),
      "n_original_study_sites_8plus_source_eligible":nsites,
      "source_public_study_site_eligible_plot_counts":dict(sorted(sites.items())),
      "n_original_species_with_positive_full_joint_axis_source_trait_in_final_plots":len(species_all),
      "original_source_paired_trait_completeness_distribution_before_ge80pct":dict(sorted(coverage_hist.items())),
      "original_richness_mismatches_by_public_experiment":dict(sorted(richness_errors.items())),
      "fixed_80pct_plot_local_FD_source_support_status":
         "PLOT_LOCAL_FD_SOURCE_COMPLETENESS_PASS" if len(chosen)>=MIN_SOURCE_PLOTS
             and nsites>=MIN_SITES and len(species_all)>=MIN_TAXA
          else "PLOT_LOCAL_FD_SOURCE_COMPLETENESS_HOLD",
      "original_DS1_woody_values_fit_or_correlated_with_traits":False,
      "original_DS2_species_woody_values_accessed_or_used":False,
      "original_source_row_identifiers_saved":False,
    }

def main(args):
    years,source_meta=verify_year_table(args.years)
    _,ds1=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    _,ds2=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    if len(ds1)!=363 or len(ds2)!=689:
        raise ValueError("SOURCE_HOLD: original Figshare immutable row counts drift")
    plots={}
    details=collections.defaultdict(list)
    duplicates=set()
    source_spec=set()
    for r in ds1:
        k=tuple(compact(r[c]) for c in CORE)
        if not all(k) or k in plots:raise ValueError("SOURCE_HOLD: DS1 primary key missing/duplicate")
        plots[k]=r
    for r in ds2:
        k=tuple(compact(r[c]) for c in CORE)
        spp=compact(r.get("species"))
        if not all(k) or not spp:raise ValueError("SOURCE_HOLD: DS2 keys/taxon missing")
        if (*k,spp) in source_spec:raise ValueError("SOURCE_HOLD: DS2 duplicate site×plot×species")
        source_spec.add((*k,spp))
        details[k].append(r)
    join=set(plots)&set(details)
    if len(join)!=328 or len(set(k[0] for k in join))!=11 or set(k[0] for k in join)!=set(years):
        raise ValueError("SOURCE_HOLD: previous 328 source plot /11 source site crosswalk drift")
    if "ECOLINK_Uppsala" not in years or "MataDIV" not in years:
        raise ValueError("SOURCE_HOLD: original fixed study design labels missing")
    cohorts={
      "all_original_studies_diagnostic_only":counts_for_scope(plots,details,years,set(),"All 11 source experiments only as diagnostic"),
      "excluding_ECOLINK":counts_for_scope(plots,details,years,{"ECOLINK_Uppsala"},"Tree-species diversity × single woody stand primary source scope"),
      "excluding_ECOLINK_and_MataDIV":counts_for_scope(plots,details,years,{"ECOLINK_Uppsala","MataDIV"},"Source-defined no-genotype no-fertilized sensitivity"),
    }
    # Prevent a numerical biology effect from being opened here.
    assert cohorts["excluding_ECOLINK"]["source_original_year_aligned_plot_with_2plus_joint_axis_species"]==117
    assert cohorts["excluding_ECOLINK_and_MataDIV"]["source_original_year_aligned_plot_with_2plus_joint_axis_species"]==107
    return {
      "version":"v0.1",
      "status":"ORIGINAL_PLOT_LOCAL_SLA_LNCM_COVERAGE_SOURCE_ONLY_AUDITED",
      "original_public_figshare_article":31026004,
      "original_public_DS1_DS2_MD5_source_checked":True,
      "uploaded_original_Table_S1_SHA256":source_meta["source_uploaded_workbook"]["sha256"],
      "original_DS1_unique_stand_plot_rows":len(ds1),
      "original_DS2_species_plot_rows":len(ds2),
      "exact_DS1_DS2_original_source_joins":len(join),
      "source_plot_min_trait_species":2,
      "fixed_min_joint_SLA_LNCM_fraction_of_original_planted_species":MIN_COVERAGE,
      "source_support_thresholds":{"min_plots":MIN_SOURCE_PLOTS,"min_sites_with_8":MIN_SITES,"min_species":MIN_TAXA,"year_gap_max":YEAR_GAP_MAX},
      "original_source_only_cohorts":cohorts,
      "no_FD_PD_K_or_biomass_prediction_computed":True,
      "original_DS2_woody_aggregation_gate_remains_HOLD":True,
      "original_individual_sample_ID_gate_remains_HOLD":True,
      "scientific_contract":"docs/TREEDIVNET_PLOT_LOCAL_TRAIT_COMPLETENESS_SOURCE_GATE_V0_1.md",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--years",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        assert 2/2>=MIN_COVERAGE and not 2/3>=MIN_COVERAGE
        assert MIN_SOURCE_PLOTS==80 and MIN_SITES==5 and MIN_TAXA==20
        assert set(JOINT_AXES)=={"SLA","LNCM"}
        print("PLOT_LOCAL_SOURCE_COVERAGE_FIXTURE_PASS")
    else:
        if not args.years or not args.out:p.error("--years --out mandatory")
        result=main(args)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("TREE_DIVNET_PLOT_LOCAL_80PCT_SOURCE_COMPLETENESS",
              json.dumps(result,sort_keys=True),flush=True)
