#!/usr/bin/env python3
"""Year-aligned same-species multivariate FD source COVERAGE, no numerical FD or response fit.

Read original Figshare DS1/DS2 original MD5 bytes and locally transcribed,
SHA-labeled user-uploaded original Table S1 woody/trait inventory years.
No plot/species IDs, original biological values or source copyrighted XLSX exported.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path

from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet,compact,safe_num,CORE
from audit_treedivnet_s1_s2_site_eligibility_v0_4 import compute_eligible,classify
from audit_treedivnet_table_s1_year_matched_plots_v0_6 import verify_year_table

BUNDLES={
  "SLA+LNCM":("SLA","LNCM"),
  "SLA+WD":("SLA","WD"),
  "SLA+LNCM+WD":("SLA","LNCM","WD"),
}
MIN_PLOTS=80
MIN_SITES_8=5
MIN_TAXA=20

def coverage(base_eligible,details,years,exclude:set[str],label:str)->dict:
    keys=[k for k in base_eligible if k[0] not in exclude]
    answer={}
    for name,traits in BUNDLES.items():
        plots=set()
        taxa=set()
        counts=collections.Counter()
        for key in keys:
            site=key[0]
            gap=years[site]["minimum_absolute_inventory_year_gap_to_woody"]
            if any(gap[a] is None or gap[a]>2 for a in traits):
                continue
            species={compact(row["species"]) for row in details[key]
                if all(safe_num(row.get(tr),positive=True) is not None for tr in traits)}
            if len(species)>=2:
                plots.add(key)
                taxa.update(species)
                counts[site]+=1
        passing=(len(plots)>=MIN_PLOTS and
                  sum(n>=8 for n in counts.values())>=MIN_SITES_8 and
                  len(taxa)>=MIN_TAXA)
        answer[name]={
          "number_source_original_site_plots_with_two_same_species_full_multiaxis_year_match":len(plots),
          "number_original_study_sites_with_any_source_plot":len(counts),
          "number_original_study_sites_with_8_or_more_original_source_plots":sum(n>=8 for n in counts.values()),
          "number_original_study_species_with_full_multiaxis_source_traits_on_valid_plots":len(taxa),
          "original_study_site_plot_counts":dict(sorted(counts.items())),
          "fixed_source_support_decision":"MULTIAXIS_SOURCE_NUMERIC_SUPPORT_PASS" if passing else "MULTIAXIS_SOURCE_NUMERIC_SUPPORT_HOLD",
          "no_original_raw_trait_or_biomass_values_exported":True,
        }
    return {
       "source_population":label,
       "original_pre_TableS1_year_numeric_source_plots":len(keys),
       "trait_bundle_source_support":answer,
    }

def main(args):
    years,meta=verify_year_table(args.years)
    _,r1=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    _,r2=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    sites,common,eligible,axis,species=compute_eligible(r1,r2)
    if len(common)!=328 or len(eligible)!=186 or set(sites)!=set(years):
       raise ValueError("SOURCE_HOLD: original source geometry/taxonomy drift")
    ec=classify(sites,"ecolink")
    md=classify(sites,"matadiv")
    if ec is None or md is None or ec==md:
       raise ValueError("SOURCE_HOLD: original ECOLINK/MataDIV source site classification")
    detailed=collections.defaultdict(list)
    for row in r2:
       k=tuple(compact(row[x]) for x in CORE)
       detailed[k].append(row)
    result={
      "version":"v0.6",
      "status":"SOURCE_ONLY_ORIGINAL_YEAR_MATCHED_SAME_SPECIES_MULTIAXIS_TRAITS_AUDITED",
      "original_uploaded_TableS1_sha256":meta["source_uploaded_workbook"]["sha256"],
      "public_Figshare_original_DS1_DS2_MD5_verified":True,
      "original_unique_source_joined_plots":len(common),
      "original_single_axis_or_one_of_three_axes_eligible_plots":len(eligible),
      "method":"Require two DIFFERENT original species rows with positive values for ALL requested axes at each original plot, and <=2 years Table S1 biomass/trait inventory for EACH axis.",
      "limits":{"min_plots":MIN_PLOTS,"min_sites_with_8":MIN_SITES_8,"min_species":MIN_TAXA,"year_gap":2},
      "source_groups":{
         "all_experiments_source_diagnostic_only":coverage(eligible,detailed,years,set(),"all experiments incl genotype/cumulative-coppice ECOLINK for source diagnostics only"),
         "excluding_ECOLINK":coverage(eligible,detailed,years,{ec},"Exclude ECOLINK genotype diversity + cumulative harvested coppice"),
         "excluding_ECOLINK_and_MataDIV":coverage(eligible,detailed,years,{ec,md},"Plus exclude fertilized-only MataDIV as separate source-design sensitivity")
      },
      "no_woody_biomass_FD_PD_or_K_effects_estimated":True,
      "source_individual_trait_record_provenance":"HOLD",
      "source_DS2_species_woody_to_DS1_plot_woody_normalization":"HOLD",
      "no_user_uploaded_original_table_s1_XLSX_redistributed":True,
      "original_FDis_from_283_monoculture_and_17_external_values_not_used":True
    }
    if result["source_groups"]["excluding_ECOLINK"]["original_pre_TableS1_year_numeric_source_plots"]!=153 or result["source_groups"]["excluding_ECOLINK_and_MataDIV"]["original_pre_TableS1_year_numeric_source_plots"]!=143:
        raise ValueError("SOURCE_HOLD: original source group qualified plot counts drift")
    return result

def fixture():
    assert MIN_PLOTS==80 and MIN_SITES_8==5 and MIN_TAXA==20
    assert set(BUNDLES)=={"SLA+LNCM","SLA+WD","SLA+LNCM+WD"}
    return {"status":"ORIGINAL_MULTIAXIS_YEAR_SUPPORT_FIXTURE_PASS","checks":3}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-year-table",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.source_year_table or not a.out:p.error("--source-year-table and --out are required")
        r=main(argparse.Namespace(years=a.source_year_table))
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("TREE_DIVNET_S1_MULTIAXIS_SOURCE_QUALIFICATION",json.dumps(r,sort_keys=True),flush=True)
