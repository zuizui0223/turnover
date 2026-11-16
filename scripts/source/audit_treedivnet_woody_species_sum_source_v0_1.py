#!/usr/bin/env python3
"""Check Figshare TreeDivNet 2026 DS1 stand woody mass vs DS2 species sum.

A source-only original data hierarchy audit, not an FD or biomass effect test.
Original plot IDs, species-level values and numeric biomass are never logged
or persisted. Read original source through MD5 pinned book XML in memory only.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
from pathlib import Path

from audit_treedivnet_figshare_original_join_v0_1 import load_table,key,num,norm,usable

MIN_SOURCE_NUMERIC_PLOT_KEYS=300
MIN_MASS_PASS_RATE=.90
MIN_SPECIES_RICHNESS_MATCH_RATE=.90
ABS_TOL=.001
REL_TOL=.01


def sample()->dict:
    ds1,cols1,_=load_table("DS1.xlsx")
    ds2,cols2,_=load_table("DS2.xlsx")
    assert len(ds1)==363 and len(ds2)==689
    A={}
    B=collections.defaultdict(list)
    for row in ds1:
        k=key(row)
        if k in A: raise ValueError("SOURCE_HOLD: duplicate original plot")
        A[k]=row
    pairkeys=set()
    for row in ds2:
        k=key(row)
        pair=(k,norm(row.get("species")))
        if not pair[1] or pair in pairkeys:
            raise ValueError("SOURCE_HOLD: species-per-plot identity duplicates")
        pairkeys.add(pair); B[k].append(row)
    common=set(A)&set(B)
    numeric=0
    positive_stand=0
    source_mass_match=0
    source_richness_match=0
    species_perplot_missing_mass=0
    plot_count_discrepancies=collections.Counter()
    site=collections.defaultdict(collections.Counter)
    slas=0
    sla_2species=0
    trait_valid_byplot={}
    for k in sorted(common):
        row=A[k];rows=B[k]
        counted=len(rows)
        r0=num(row.get("biomass_woody"))
        # DS1 original richness encoded as a number; strictly check integer.
        rr=num(row.get("species_richness"))
        if rr is None or not math.isclose(rr,round(rr),abs_tol=1e-9):
            raise ValueError("SOURCE_HOLD: malformed original plotted richness")
        expn=int(round(rr))
        sc=site[k[0]]
        sc["joined_plot_keys"]+=1
        if counted==expn:
            source_richness_match+=1
            sc["original_species_richness_matched_plots"]+=1
        else:
            plot_count_discrepancies[str(counted-expn)]+=1
            sc["original_species_richness_mismatch_plots"]+=1
        ids={norm(r["species"]) for r in rows}
        if len(ids)!=counted:
            raise ValueError("SOURCE_HOLD: original species duplicate within plot")
        perplot_mass=[num(r.get("biomass_woody")) for r in rows]
        if r0 is None or any(m is None for m in perplot_mass):
            species_perplot_missing_mass+=1
            sc["original_numeric_woody_mass_incomplete_plots"]+=1
            continue
        sc["numeric_woody_mass_comparable_plots"]+=1
        numeric+=1
        if r0>0:positive_stand+=1
        total=sum(perplot_mass)
        if math.isclose(r0,total,rel_tol=0,abs_tol=max(ABS_TOL,REL_TOL*abs(r0))):
            source_mass_match+=1
            sc["woody_mass_sum_matches_plots"]+=1
        else:
            sc["woody_mass_sum_mismatches_plots"]+=1
        covered={norm(r["species"]) for r in rows if usable(r,"SLA")}
        slas+=len(covered)
        if len(covered)>=2:
            sla_2species+=1
            sc["plots_with_two_original_SLA_species_in_numeric_mass_comparison"]+=1
    denom=len(common)
    mass_pct=source_mass_match/numeric if numeric else 0.
    richness_pct=source_richness_match/denom if denom else 0.
    good=(numeric>=MIN_SOURCE_NUMERIC_PLOT_KEYS and
          mass_pct>=MIN_MASS_PASS_RATE and richness_pct>=MIN_SPECIES_RICHNESS_MATCH_RATE)
    return {
        "version":"v0.1",
        "status":"ORIGINAL_SPECIES_PLOT_MASS_HIERARCHY_PASS" if good else "SOURCE_SPECIES_MASS_INTEGRITY_HOLD",
        "source":"TreeDivNet Jensen et al. 2026, Figshare 10.6084/m9.figshare.31026004.v1",
        "source_only":True,
        "source_plot_keys_DS1":len(A),
        "source_plot_keys_DS2":len(B),
        "original_joined_plot_keys":denom,
        "original_numeric_mass_hierarchy_eligible_plots":numeric,
        "original_mass_numeric_source_incomplete_plot_keys":species_perplot_missing_mass,
        "original_positive_woody_stand_mass_comparable_plots":positive_stand,
        "species_sum_mass_matched_plots":source_mass_match,
        "species_sum_mass_mismatched_plots":numeric-source_mass_match,
        "source_woody_mass_reconciled_fraction":mass_pct,
        "original_richness_equals_ds2_distinct_species_plots":source_richness_match,
        "original_richness_mismatch_count_plots":denom-source_richness_match,
        "source_original_richness_match_fraction":richness_pct,
        "original_DS2_species_count_minus_DS1_richness_distribution":dict(sorted(plot_count_discrepancies.items())),
        "SLA_two_species_plots_with_numeric_woody_mass":sla_2species,
        "original_SLA_positive_species_plot_occurrences_in_mass_comparable_plots":slas,
        "original_source_site_audit":{n:dict(v) for n,v in sorted(site.items())},
        "predetermined_quality_gate":{"min_numeric_comparable_plots":MIN_SOURCE_NUMERIC_PLOT_KEYS,
           "min_source_mass_sum_match_fraction":MIN_MASS_PASS_RATE,
           "min_original_richness_match_fraction":MIN_SPECIES_RICHNESS_MATCH_RATE,
           "mass_absolute_tolerance_Mg_per_ha":ABS_TOL,
           "mass_relative_tolerance":REL_TOL},
        "old_family_K_and_PD_rho_not_opened":True,
        "no_ecological_biomass_model_estimated":True,
        "no_original_plot_species_response_rows_exported":True,
        "new_biological_effect_authorized":False,
        "interpretation":"Source-only additive integrity/roster equality; no FD/biomass biological association fitted. Actual tree measurement/source year remains unverified."
    }


def fixture():
    assert math.isclose(100,100.9,rel_tol=0,abs_tol=max(.001,.01*100))
    assert not math.isclose(100,102,rel_tol=0,abs_tol=max(.001,.01*100))
    assert MIN_SOURCE_NUMERIC_PLOT_KEYS==300
    return {"status":"ORIGINAL_MASS_ROSTER_QA_FIXTURE_PASS","checks":3}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture()))
    else:
        if not args.out:p.error("--out required")
        r=sample()
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("TREEDIVNET_WOODY_BIOMASS_SOURCE_HIERARCHY_QA",json.dumps(r,sort_keys=True),flush=True)
