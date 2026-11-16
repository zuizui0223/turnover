#!/usr/bin/env python3
"""Source-only explanation test for published TreeDivNet 2026 DS1/DS2 woody
plot-scale identity, avoiding all original ecological outcome fitting.

Test posthoc mathematical candidates previously recorded: mean(DS2 species)
matched 321/328 plots, 6 of seven exceptions have DS2 rowcount != DS1 richness.
Here check sum(DS2 woody)/DS1 original planned richness, including those six.
"""
from __future__ import annotations
import argparse,collections,json,math
from pathlib import Path
from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet,compact,safe_num,CORE

EXPECTED_JOIN=328
SOURCE_MD5_PINNED=True

def run():
    _,stand_rows=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    _,species_rows=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    if len(stand_rows)!=363 or len(species_rows)!=689:raise ValueError("SOURCE_HOLD: historical exact original source geometry")
    stand={}
    sp=collections.defaultdict(list)
    for r in stand_rows:
        k=tuple(compact(r[x]) for x in CORE)
        if not all(k) or k in stand:raise ValueError("SOURCE_HOLD: invalid unique stand key")
        stand[k]=r
    for r in species_rows:
        k=tuple(compact(r[x]) for x in CORE)
        if not all(k):raise ValueError("SOURCE_HOLD: original species plot key blank")
        sp[k].append(r)
    keys=set(stand)&set(sp)
    if len(keys)!=EXPECTED_JOIN:raise ValueError("SOURCE_HOLD: 328 original source plot keys not reproduced")
    counters=collections.Counter()
    details=collections.Counter()
    errors_invariants=collections.Counter()
    for k in keys:
        q=stand[k];rr=sp[k]
        y=safe_num(q.get("biomass_woody"))
        n=safe_num(q.get("species_richness"),positive=True)
        x=[safe_num(z.get("biomass_woody")) for z in rr]
        if y is None or n is None or int(n)!=n or any(v is None for v in x):
            raise ValueError("SOURCE_HOLD: original source scalar biomass/richness invalid")
        m=len(x);n=int(n)
        assert n>=1 and m>=1
        total=sum(x)
        mean=total/m
        corrected=total/n
        exact_mean=math.isclose(mean,y,rel_tol=1e-10,abs_tol=1e-8)
        exact_rich=math.isclose(corrected,y,rel_tol=1e-10,abs_tol=1e-8)
        exact_sum=math.isclose(total,y,rel_tol=1e-10,abs_tol=1e-8)
        counters["joined_plots"]+=1
        counters["rowcount_equal_original_richness"]+=int(n==m)
        counters["DS2_mean_equals_DS1"]+=int(exact_mean)
        counters["DS2_sum_over_original_richness_equals_DS1"]+=int(exact_rich)
        counters["DS2_sum_equals_DS1"]+=int(exact_sum)
        counters["within_1pct_DS2_sum_over_richness"]+=int(math.isclose(corrected,y,rel_tol=.01,abs_tol=1e-8))
        counters["within_5pct_DS2_sum_over_richness"]+=int(math.isclose(corrected,y,rel_tol=.05,abs_tol=1e-8))
        if n!=m:
            details["reported_richness_not_equal_DS2_rows"]+=1
            details["difference_resolved_by_original_richness_denominator"]+=int(exact_rich)
            details["difference_not_resolved_by_original_richness_denominator"]+=int(not exact_rich)
        if not exact_rich:
            errors_invariants["n_remaining_bad_plots"]+=1
            errors_invariants["with_rowcount_equal_richness"]+=int(n==m)
            errors_invariants["original_woody_is_zero"]+=int(y==0)
            errors_invariants["original_richness_is_1"]+=int(n==1)
            errors_invariants["within_1pct"]+=int(math.isclose(corrected,y,rel_tol=.01,abs_tol=1e-8))
    status=("WOODY_SUM_DIVIDED_BY_PLANTED_RICHNESS_RECONCILES_ALL_SOURCE_PLOTS"
            if counters["DS2_sum_over_original_richness_equals_DS1"]==EXPECTED_JOIN
            else "WOODY_PLANTED_RICHNESS_NORMALIZATION_NOT_EXACT_ALL_PLOTS")
    return {
      "version":"v0.3",
      "status":status,
      "original_2026_Figshare_source_MD5_verified":True,
      "study":"Jensen et al. 2026 TreeDivNet",
      "original_file_raw_rows":{"DS1":363,"DS2":689},
      "source_identical_site_block_plot_joins":len(keys),
      "source_arithmetic_counts":dict(counters),
      "original_richness_vs_species_row_count_mismatch":dict(details),
      "remaining_plots_when_sum_div_original_richness_not_equal_DS1":dict(errors_invariants),
      "response_source_grain":"single original DS1 woody dry biomass Mg/ha per site×block×plot",
      "observed_mathematical_identity_is_not_author_confirmed_transform":True,
      "do_not_reinterpret_species_row_woody_as_raw_species_mass_contribution":True,
      "do_not_duplicate_DS1_mass_per_species_as_independent_rows":True,
      "no_original_plot_taxon_mass_values_exported":True,
      "no_trait_FD_K_PD_or_biomass_effect_estimated":True,
      "interpretation":"Mathematical reconciliation of original exported tables; underlying formula/biological normalization convention still requires published author source Methods S2, not inferred from empirical equality."
    }

def fixture():
    source_response=12
    richness=4
    species_scaled=[10,14,16,8]
    assert sum(species_scaled)/richness==source_response
    assert sum(species_scaled)/len(species_scaled)==source_response
    assert (10+14+16)/richness!=source_response
    return {"status":"RICHNESS_NORMALIZER_SOURCE_FIXTURE_PASS","checks":3}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.self_test:print(json.dumps(fixture()))
    else:
        if not a.out:p.error("--out required")
        result=run()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("TREEDIVNET_RICHNESS_NORMALIZED_WOODY_SOURCE_IDENTITY",json.dumps(result,sort_keys=True),flush=True)
