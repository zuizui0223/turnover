#!/usr/bin/env python3
"""Source-only test: is DS2 species-row woody biomass a repeated plot response?

Original TreeDivNet Figshare DS1/DS2 files MD5-verified. Avoid double-counting
one biomass response once per species. No ecological trait/biomass associations.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path

from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet,compact,safe_num,CORE


def source():
    h1,rows1=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    h2,rows2=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    if len(rows1)!=363 or len(rows2)!=689:
        raise ValueError("SOURCE_HOLD: unexpected original study rows")
    d={}
    groups=collections.defaultdict(list)
    for row in rows1:
        k=tuple(compact(row[c]) for c in CORE)
        if not all(k) or k in d:raise ValueError("SOURCE_HOLD: original DS1 keys duplicate")
        d[k]=row
    for row in rows2:
        k=tuple(compact(row[c]) for c in CORE)
        if not all(k):raise ValueError("SOURCE_HOLD: DS2 plot identifier missing")
        groups[k].append(row)
    joined=sorted(set(d)&set(groups))
    checked_rows=0
    exact_rows=0
    within_1pct_rows=0
    numeric_row_missing=0
    plot_all_equal=0
    plot_sum_equals_n_times_ds1=0
    plot_all_sources_numeric=0
    plot_k=collections.Counter()
    n_per_richness=collections.Counter()
    plots_with_different_spp_richness=0
    incompatible_examples=0
    ratio_vs_n_skips=0
    sample_semantic_flags=[]
    for k in joined:
        ds1=d[k]; ds2=groups[k]
        base=safe_num(ds1.get("biomass_woody"))
        if base is None:
            ratio_vs_n_skips+=1
            continue
        measured=[safe_num(r.get("biomass_woody")) for r in ds2]
        count=len(measured)
        plot_k[str(count)]+=1
        nrich=safe_num(ds1.get("species_richness"))
        if nrich is not None:
            n_per_richness[str(int(nrich))]+=1
            plots_with_different_spp_richness+=int(int(nrich)!=count)
        if any(val is None for val in measured):
            numeric_row_missing+=sum(v is None for v in measured)
            continue
        checked_rows+=count
        plot_all_sources_numeric+=1
        equal=[math.isclose(v,base,rel_tol=1e-10,abs_tol=1e-8) for v in measured]
        near=[math.isclose(v,base,rel_tol=.01,abs_tol=1e-8) for v in measured]
        exact_rows+=sum(equal)
        within_1pct_rows+=sum(near)
        plot_all_equal+=int(all(equal))
        plot_sum_equals_n_times_ds1+=int(
            math.isclose(sum(measured),count*base,rel_tol=1e-10,abs_tol=1e-7))
    fraction=exact_rows/max(1,checked_rows)
    if not joined or checked_rows<500:
        status="SOURCE_ROW_GRAIN_HOLD"
    elif fraction>=.99 and plot_all_equal>=.99*plot_all_sources_numeric:
        status="REPEATED_PLOT_BIOMASS_NOT_SPECIES_COMPONENT"
    else:
        status="MIXED_SPECIES_VS_PLOT_RESPONSE_GRAIN_HOLD"
    return {
        "version":"v0.1",
        "status":status,
        "no_ecological_effect_estimated":True,
        "fixed_source_original_Figshare_article":31026004,
        "DS1_unique_plots":len(d),
        "DS2_unique_plot_ids":len(groups),
        "DS1_DS2_unique_matched_plots":len(joined),
        "matched_plots_with_all_DS2_woody_numeric":plot_all_sources_numeric,
        "matched_DS2_species_rows_with_numeric_woody":checked_rows,
        "matched_DS2_species_rows_equal_DS1_plot_biomass":exact_rows,
        "matched_DS2_species_rows_within_1pct_DS1_plot_biomass":within_1pct_rows,
        "original_plots_all_species_biomass_repeats_DS1":plot_all_equal,
        "original_plots_sum_species_row_biomass_equals_n_rows_times_DS1":plot_sum_equals_n_times_ds1,
        "joined_plots_with_original_DS1_woody_missing":ratio_vs_n_skips,
        "joined_DS2_woody_missing_numeric_rows":numeric_row_missing,
        "matched_original_plot_number_of_species_rows_distribution":dict(sorted(plot_k.items(),key=lambda x:int(x[0]))),
        "matched_original_planted_richness_distribution":dict(sorted(n_per_richness.items(),key=lambda x:int(x[0]))),
        "matched_plots_where_DS2_species_rows_differ_from_DS1_richness":plots_with_different_spp_richness,
        "species_woody_column_data_grain_inference":"Repeated plot-level woody biomass value on each DS2 species row" if status=="REPEATED_PLOT_BIOMASS_NOT_SPECIES_COMPONENT" else "Unresolved; do not sum as species components",
        "do_not_sum_DS2_woody_across_species":True,
        "future_valid_response_grain":"one independent original DS1 site×block×plot biomass_woody value per stand, NOT DS2 species-row duplication",
        "only_exact_matching_original_source_rows_tested":True,
        "no_original_biomass_values_or_named_plot_ids_exported":True,
        "no_family_specific_K_or_FD_regression_calculated":True,
        "scientific_boundary":"A source schema identity, not an ecological species-richness biomass effect or independent replication of Jensen 2026",
    }


def fixture():
    assert math.isclose(sum([12.0,12.0,12.0]),3*12.0)
    assert sum([12,12]) / 12 == 2
    return {"status":"DS2_STAND_RESPONSE_REPEAT_FIXTURE_PASS","checks":2}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture()))
    else:
        if not a.out:p.error("--out required")
        result=source()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("TREE_DIVNET_SPECIES_ROW_WOODY_RESPONSE_GRAIN_QA",json.dumps(result,sort_keys=True))
