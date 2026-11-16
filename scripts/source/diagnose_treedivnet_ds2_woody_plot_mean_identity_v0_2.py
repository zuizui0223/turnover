#!/usr/bin/env python3
"""Post-result source-only diagnosis: plot woody response ≈ arithmetic mean of
species-row woody, rather than a sum. Unchanged original 2026 Figshare inputs.
No ecological model, biomass-richness correlation, or K/FD effect estimated.
"""
import argparse,collections,json,math
from pathlib import Path
from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet,compact,safe_num,CORE

def run():
    _,plot=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    _,spec=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    if len(plot)!=363 or len(spec)!=689:raise ValueError("SOURCE_DRIFT_HOLD")
    stand={}
    repeated=collections.defaultdict(list)
    for x in plot:
        k=tuple(compact(x[y]) for y in CORE)
        if k in stand or not all(k):raise ValueError("SOURCE_KEY_HOLD")
        stand[k]=x
    for x in spec:
        k=tuple(compact(x[y]) for y in CORE)
        if not all(k):raise ValueError("SOURCE_KEY_HOLD")
        repeated[k].append(x)
    joined=stand.keys() & repeated.keys()
    nmean=nsum=0
    counter=collections.Counter()
    mismatch=collections.Counter()
    rsite=collections.Counter()
    ratio_bins=collections.Counter()
    plot_species=collections.Counter()
    expected=collections.Counter()
    nzero=0
    for k in joined:
        ds1=stand[k]
        y=safe_num(ds1.get("biomass_woody"))
        values=[safe_num(x.get("biomass_woody")) for x in repeated[k]]
        if y is None or any(v is None for v in values):raise ValueError("SOURCE_HOLD: missing matched response")
        n=len(values); plot_species[str(n)]+=1
        planted=safe_num(ds1.get("species_richness"))
        rmatch=planted is not None and int(planted)==n
        counter["richness_same"]+=int(rmatch)
        if y==0:nzero+=1
        mean=sum(values)/n
        good=math.isclose(mean,y,rel_tol=1e-10,abs_tol=1e-8)
        nmean+=int(good)
        nsum+=int(math.isclose(sum(values),y,rel_tol=1e-10,abs_tol=1e-8))
        if good:rsite[k[0]]+=1
        if not good:
            mismatch["n_plots"]+=1
            mismatch["with_original_richness_not_equal_DS2_row_count"]+=int(not rmatch)
            mismatch["with_1_species_row"]+=int(n==1)
            mismatch["with_zero_original_stand_woody"]+=int(y==0)
            # Anonymized summary, no original response or plot identifiers
            mismatch["with_difference_leq_1pct"]+=int(math.isclose(mean,y,rel_tol=.01,abs_tol=1e-8))
    frac=nmean/len(joined)
    return {
      "version":"v0.2","status":"SPECIES_ROW_WOODY_ARITHMETIC_MEAN_MATCHES_PLOT_RESPONSE_ON_MOST_PLOTS" if frac>=.95 else "SPECIES_ROW_WOODY_MEAN_CONSISTENCY_HOLD",
      "source_original_Figshare_31026004v1":True,
      "original_source_MD5_verification":True,
      "original_DS1_plot_rows":len(plot),
      "original_DS2_species_plot_rows":len(spec),
      "exact_joined_source_plots":len(joined),
      "matched_plot_with_mean_DS2_woody_equal_DS1_woody":nmean,
      "matched_plot_with_sum_DS2_woody_equal_DS1_woody":nsum,
      "matched_plot_average_identity_fraction":frac,
      "original_plots_with_zero_DS1_woody":nzero,
      "matched_plot_richness_agrees_with_DS2_rowcount":counter["richness_same"],
      "matched_plot_source_DS2_species_row_count_distribution":dict(sorted(plot_species.items(),key=lambda x:int(x[0]))),
      "mean_mismatch_source_quality_diagnostics":dict(mismatch),
      "source_native_biological_reason_for_species_to_plot_normalization":"NOT_RESOLVED_FROM_DS1_DS2_SCHEMA; require original authors' scaling convention and README/Methods S2",
      "correct_response_unit":"one DS1 woody standing mass response per unique site × block × plot",
      "must_not_aggregate_woody_by_summing_DS2_species_rows":True,
      "no_original_species_plot_or_mass_values_exported":True,
      "no_biodiversity_ecological_effect_tested":True,
      "interpretation":"This validates numerical source hierarchy only. It is not evidence for either species complementarity or diversity-productivity effects.",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        assert math.isclose(sum((1.,3.,5.))/3.,3.)
        assert sum((1.,3.,5.))!=3.
        print('SOURCE_MEAN_IDENTITY_FIXTURE_PASS')
    else:
        if not a.out:p.error('--out required')
        r=run()
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
        print('TREE_DIVNET_DS2_PLOT_MEAN_IDENTITY',json.dumps(r,sort_keys=True))
