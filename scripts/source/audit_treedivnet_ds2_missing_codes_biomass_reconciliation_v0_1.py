#!/usr/bin/env python3
"""Additional source-only QA for TreeDivNet original DS2 trait missing codes and
DS1 stand woody vs DS2 species woody mass aggregation. No trait–mass inference.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
from pathlib import Path

import numpy as np

from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import (
    load_sheet, compact, safe_num, TR, CORE, PLACEHOLDERS,
)

def kind(v):
    if v is None or str(v).strip()=="":
        return "source_empty"
    s=str(v).strip().casefold()
    if s in PLACEHOLDERS:
        return "source_missing_code"
    try:
        x=float(s)
    except (TypeError,ValueError):
        return "nonnumeric_text_or_error"
    if not math.isfinite(x):return "nonfinite"
    if x==0:return "numeric_zero"
    if x<0:return "negative_numeric_or_sentinel"
    return "positive_numeric"

def quant(vals):
    if not vals:return None
    xs=np.array(vals,float)
    return {"n":len(xs),"min":float(xs.min()),"p05":float(np.quantile(xs,.05)),
            "median":float(np.median(xs)),"p95":float(np.quantile(xs,.95)),"max":float(xs.max())}

def run():
    rows1,ds1=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    rows2,ds2=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    if len(ds1)!=363 or len(ds2)!=689:
        raise ValueError("SOURCE_HOLD: original rows changed")
    map1={}
    multi=collections.defaultdict(list)
    for row in ds1:
        k=tuple(compact(row[x]) for x in CORE)
        if not all(k) or k in map1:raise ValueError("SOURCE_HOLD: source plot duplicate")
        map1[k]=row
    for row in ds2:
        k=tuple(compact(row[x]) for x in CORE)
        if not all(k):raise ValueError("SOURCE_HOLD: missing DS2 original plot identity")
        multi[k].append(row)
    cc={tr:collections.Counter(kind(r[tr]) for r in ds2) for tr in TR}
    response_codes={
        "DS1_woody":dict(sorted(collections.Counter(kind(r["biomass_woody"]) for r in ds1).items())),
        "DS2_woody":dict(sorted(collections.Counter(kind(r["biomass_woody"]) for r in ds2).items()))
    }
    matched=set(map1)&set(multi)
    ratios=[]
    differences=[]
    n_species_match=0
    by_site=collections.defaultdict(list)
    for k in matched:
        plant=map1[k]
        rich=safe_num(plant.get("species_richness"))
        n_species=len(multi[k])
        n_species_match+=int(rich is not None and rich==n_species)
        y=safe_num(plant.get("biomass_woody"))
        components=[safe_num(r.get("biomass_woody")) for r in multi[k]]
        if y is None or not components or not all(v is not None for v in components):continue
        s=sum(components)
        # Diagnostic only, not an ecological trait→biomass association.
        diff=abs(s-y)
        differences.append(diff)
        if y>0:
            ratios.append(s/y)
            by_site[k[0]].append(s/y)
    n=len(differences)
    r1=sum(abs(v-1)<=.01 for v in ratios)
    r5=sum(abs(v-1)<=.05 for v in ratios)
    offsite=[{"n_plots":len(v),"median_species_to_stand_ratio":float(np.median(v)),
              "within_5pct_count":sum(abs(z-1)<=.05 for z in v)}
             for v in by_site.values()]
    allcat={t:dict(sorted(v.items())) for t,v in cc.items()}
    return {"version":"v0.1",
            "status":"ORIGINAL_NONRAW_SOURCE_MISSINGNESS_AND_MASS_IDENTITY_AUDITED",
            "no_ecological_outcomes_fitted":True,
            "no_original_rows_or_source_plot_ids_exported":True,
            "figshare_article":"31026004.v1",
            "source_MD5_original_workbook_files_verified":True,
            "original_DS1_rows":len(ds1),"original_DS2_rows":len(ds2),
            "original_exact_joined_plots":len(matched),
            "original_trait_value_categories":allcat,
            "original_woody_source_categories":response_codes,
            "original_matched_plots_with_source_richness_equal_DS2_rows":n_species_match,
            "original_DS2_species_woody_components_all_numeric":n,
            "original_DS2_species_to_DS1_plot_woody_ratio":quant(ratios),
            "original_DS2_to_DS1_woody_absolute_difference_Mg_ha":quant(differences),
            "original_matched_positive_woody_plot_within_1pct_ratio":r1,
            "original_matched_positive_woody_plot_within_5pct_ratio":r5,
            "per_site_component_sum_ratio_summaries_anonymized":sorted(
                offsite,key=lambda x:(x["n_plots"],x["median_species_to_stand_ratio"])),
            "source_consistency_flag":"POTENTIAL_STOCK_HIERARCHY_MISMATCH"
                    if n>0 and r5/max(1,len(ratios))<.9 else "STOCK_SOURCE_CONSISTENCY_WITHIN_5PCT_FOR_MOST",
            "limits":[
                "A zero in positive SLA/WD/leaf nutrient source should not be mistaken for an observed biological zero",
                "Species woody biomass values are not used to construct any same-year trait predictor",
                "A difference between species and stand woody biomass totals could reflect original study reporting rules, missing taxa, or source aggregation; causes remain unverified",
                "No phylogenetic K, FD–biomass regression, PD model, or carbon effect estimated"
            ]}


def fixture():
    x=["","-9999.0","0","0.2","-2","ND",None]
    assert [kind(v) for v in x]==[
        "source_empty","source_missing_code","numeric_zero","positive_numeric",
        "negative_numeric_or_sentinel","nonnumeric_text_or_error","source_empty"]
    assert quant([1,2,3])["median"]==2
    return {"status":"SOURCE_MISSINGNESS_STOCK_RECONCILIATION_FIXTURE_PASS","checks":2}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture()))
    else:
        if not args.out:p.error("--out needed")
        result=run()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("TREEDIVNET_SOURCE_NUMERIC_CODES_MASS_RECONCILIATION",
            json.dumps(result,sort_keys=True),flush=True)
