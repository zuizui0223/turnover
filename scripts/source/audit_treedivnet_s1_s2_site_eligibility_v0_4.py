#!/usr/bin/env python3
"""Source-only subset integrity after original user-uploaded 2026 TreeDivNet Methods.

S1 ECOLINK: genotype (not species richness) manipulation.
S2 ECOLINK: cumulative three-year-cycle coppice harvested woody biomass.
S1 MataDIV: fertilized source plots only.
NO ecological biomass/FD/phylogenetic K effect estimated.
"""
from __future__ import annotations
import argparse
import collections
import json
import re
from pathlib import Path

from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet, compact, safe_num, CORE

SOURCE_SUPPLEMENT_SHA256="6e422d5bbe685e00b045634137c150e8a6824e8dd4c6f88da43beae2f2ee9ddd"
TAXON_AXES=("SLA","LNCM","WD")
META_BIOMASS="biomass_woody"
N_REPRODUCE=186
N_BASE=328
MIN_PLOTS=80
MIN_SITES=5
MIN_PLOTS_PER_SITE=8
MIN_SPECIES=20


def norm(text:str)->str:
    return re.sub(r"[^a-z0-9]","",str(text).casefold())


def classify(sites:list[str],needle:str)->str|None:
    matches=[s for s in sites if needle in norm(s)]
    return matches[0] if len(matches)==1 else None


def compute_eligible(rows1,rows2):
    if len(rows1)!=363 or len(rows2)!=689:
        raise ValueError("SOURCE_HOLD: original Figshare source row count changed")
    p={}
    s=collections.defaultdict(list)
    duplicate_plot=0
    for row in rows1:
        key=tuple(compact(row[x]) for x in CORE)
        if key in p or not all(key):duplicate_plot+=1
        p[key]=row
    for row in rows2:
        key=tuple(compact(row[x]) for x in CORE)
        if not all(key):raise ValueError("SOURCE_HOLD: original DS2 has blank plot key")
        s[key].append(row)
    common=set(p)&set(s)
    if len(common)!=N_BASE or duplicate_plot!=0:
        raise ValueError("SOURCE_HOLD: original 328 join/unique source geometry drift")
    allsites=sorted({k[0] for k in common})
    if len(allsites)!=11:
        raise ValueError("SOURCE_HOLD: original expected 11 source sites changed")
    eligible=set()
    per_axis={a:set() for a in TAXON_AXES}
    spp_per_plot={}
    for key in common:
        ds1=p[key]
        if safe_num(ds1.get(META_BIOMASS)) is None:
            continue
        by_axis={a:set() for a in TAXON_AXES}
        for sr in s[key]:
            for axis in TAXON_AXES:
                if safe_num(sr.get(axis),positive=True) is not None:
                    by_axis[axis].add(compact(sr["species"]))
        for axis, names in by_axis.items():
            if len(names)>=2:per_axis[axis].add(key)
        if any(len(names)>=2 for names in by_axis.values()):
            eligible.add(key)
            spp_per_plot[key]=set().union(*by_axis.values())
    if len(eligible)!=N_REPRODUCE or any(len(per_axis[a])!=n for a,n in
                                        {"SLA":165,"LNCM":170,"WD":77}.items()):
        raise ValueError("SOURCE_HOLD: prior numerical 186/165/170/77 trait source qualification not reproduced")
    represented=set().union(*spp_per_plot.values()) if spp_per_plot else set()
    if len(represented)!=38:
        raise ValueError("SOURCE_HOLD: original 38 trait-bearing source taxa changed")
    return allsites, common, eligible, per_axis, spp_per_plot


def coverage(name, original_sites, common, eligible, axes, sps)->dict:
    named=set(original_sites)
    keys={k for k in common if k[0] in named}
    hit={k for k in eligible if k[0] in named}
    c=collections.Counter(k[0] for k in hit)
    sp=set().union(*(sps[k] for k in hit)) if hit else set()
    return {
        "cohort":name,
        "source_site_count":len(named),
        "original_DS1_DS2_joined_plots":len(keys),
        "plots_2plus_same_axis_species_with_original_DS1_nonnegative_woody":len(hit),
        "site_eligible_original_plot_counts":dict(sorted(c.items())),
        "number_sites_with_at_least_8_eligible_original_plots":sum(n>=MIN_PLOTS_PER_SITE for n in c.values()),
        "n_distinct_positive_trait_species_in_eligible_plots":len(sp),
        "trait_qualified_plots_by_axis":{t:len(axes[t]&hit) for t in TAXON_AXES},
        "prior_frozen_structural_plot_site_species_gate_pass":bool(len(hit)>=MIN_PLOTS
            and sum(n>=MIN_PLOTS_PER_SITE for n in c.values())>=MIN_SITES
            and len(sp)>=MIN_SPECIES),
        "original_study_measurement_year_qualified":False,
        "individual_trait_sample_lineage_qualified":False,
        "DS2_species_woody_to_stand_scaling_qualified":False,
        "no_biomass_trait_association_estimated":True,
    }


def main():
    _,ds1=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    _,ds2=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    allsites,common,eligible,per_axis,spp_per_plot=compute_eligible(ds1,ds2)
    ec=classify(allsites,"ecolink")
    md=classify(allsites,"matadiv")
    status="UPLOADED_METHODS_SITE_SOURCE_COHORT_GATE_PASS"
    if not ec or not md or ec==md:
        status="UPLOADED_METHODS_SITE_CLASSIFICATION_HOLD"
    full=coverage("all original 11 experiments",allsites,common,eligible,per_axis,spp_per_plot)
    filtered=coverage("exclude genotype-manipulation and cumulative-coppice ECOLINK",
        [x for x in allsites if x!=ec],common,eligible,per_axis,spp_per_plot) if ec else None
    fertilization=coverage("exclude ECOLINK and only-fertilized MataDIV (source-design sensitivity)",
        [x for x in allsites if x not in (ec,md)],common,eligible,per_axis,spp_per_plot) if ec and md else None
    return {
        "version":"v0.4",
        "status":status,
        "user_supplied_original_supplement_SHA256":SOURCE_SUPPLEMENT_SHA256,
        "supplement_methods_s1":"ECOLINK genetically manipulated varieties; MataDIV only fertilized study plots",
        "supplement_methods_s2":"ECOLINK cumulative harvest cycles not single snapshot biomass; ORPHEE some imputed root collar diameters",
        "supplement_methods_s3":"Plot×species leaf nutrient means measured but observation year absent",
        "original_Figshare_data_MD5_verified":True,
        "site_label_ECOLINK":ec,
        "site_label_MataDIV":md,
        "remaining_source_site_labels":sorted(x for x in allsites if x not in (ec,md)),
        "original_site_count":len(allsites),
        "original_join_geometry_328_reproduced":True,
        "original_186_trait_source_gate_reproduced":True,
        "all_experiments":full,
        "excluding_ECOLINK":filtered,
        "excluding_ECOLINK_and_MataDIV":fertilization,
        "decision":"NO_NEW_ECOLOGICAL_EFFECT_AUTHORIZED___PER_SITE_MEASUREMENT_YEARS_AND_WOODY_CONVERSION_MISSING",
        "nonclaims":["This is a pre-effect original-source cohort eligibility check, not a new published or independent biomass effect.",
                     "Do not treat ECOLINK genotype diversity as species richness or sum of coppice harvests as snapshot biomass.",
                     "Do not treat MataDIV-only-fertilized as a confounding-free unfertilized control.",
                     "Numeric support alone does not unlock time alignment, individual sample-ID/lineage, and original DS2 woody normalization.",
                     "No trait phylogenetic K, distance memory rho, new FD→biomass or PD model was estimated."],
    }


def fixture()->dict:
    sites=["ECOLINK_Uppsala","MataDIV","ORPHEE","IDENT_Macomer"]
    assert classify(sites,"ecolink")=="ECOLINK_Uppsala"
    assert classify(sites,"matadiv")=="MataDIV"
    assert classify(sites,"unknown") is None
    assert norm("ECOLINK-Uppsala")==norm("ECOLINK_Uppsala")
    assert MIN_PLOTS==80 and MIN_SPECIES==20 and MIN_SITES==5
    return {"status":"METHODS_S1_S2_SITE_SOURCE_FIXTURE_PASS","checks":5}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture(),sort_keys=True))
    else:
        if not a.out:p.error("--out required")
        r=main()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
        print("TREE_DIVNET_UPLOADED_METHODS_SITE_ELIGIBILITY",json.dumps(r,sort_keys=True),flush=True)
