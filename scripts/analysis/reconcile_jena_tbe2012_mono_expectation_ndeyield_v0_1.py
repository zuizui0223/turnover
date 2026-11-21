#!/usr/bin/env python3
"""Post-result, same-source arithmetic proof: Y_observed=Y_mono_expected+NDE.

All three quantities use IDENTICAL original 84 planted mixtures, same source
3-prefix proxy and same pool×richness WLS. This is not causal inference.
"""
from __future__ import annotations
import argparse,collections,json,math,sys
from pathlib import Path
import numpy as np

sys.path.insert(0,"scripts/analysis")
import jena_tbe2012_original_monoculture_CE_SE_partition_v0_1 as m

SEED=20261121
BOOT=2000
FROZEN="docs/JENA_TBE2012_ANNUAL_MASS_EXPECTED_MONO_NDE_RECONCILIATION_POSTHOC_20261121.md"
OLD_ANNUAL=35.3417884482801
OLD_NDE=68.96079640366669
OLD_CE=27.814900839689546
OLD_SE=41.14589556397725

def check(ok,msg):
    if not ok:raise AssertionError(msg)

def data():
    chosen,mono,source=m.assemble_source()
    partition,maxdiff=m.partition(chosen,mono)
    check(len(chosen)==len(partition)==84,"source cohorts not identical")
    out=[]
    maxidentity=0
    for r,z in zip(chosen,partition):
        check(r["pool"]==z["pool"] and r["rich"]==z["rich"] and r["prefix"]==z["prefix"] and
              int(r["fd"]>=3)==z["FD_high"],"original source plot order changed")
        observed=sum(r["mass"].values())
        expected=sum(mono[(r["pool"],sp)][0] for sp in r["mass"])/r["rich"]
        delta=observed-expected-z["NDE"]
        maxidentity=max(maxidentity,abs(delta))
        check(abs(delta)<=1e-8*max(1,abs(observed)),
              "original annual observed does not equal monoyield expectation+NDE")
        out.append({**z,"observed_mass":observed,"expected_mono":expected})
    check(maxdiff<1e-8,"original CE SE NDE identity failed")
    return out,source,maxidentity

def fit(rows):
    X,w=m.design(rows)
    sw=np.sqrt(w)
    xp=X*sw[:,None]
    out={}
    for k in ("observed_mass","expected_mono","NDE","CE","SE"):
        y=np.array([r[k] for r in rows],float)
        out[k]=float(np.linalg.lstsq(xp,y*sw,rcond=None)[0][-1])
    check(abs(out["observed_mass"]-out["expected_mono"]-out["NDE"])<1e-8,
          "model WLS expected plus NDE identity mismatch")
    check(abs(out["NDE"]-out["CE"]-out["SE"])<1e-8,
          "model WLS complementarity plus selection identity mismatch")
    return out

def main(out):
    rows,source,maxidentity=data()
    fit_point=fit(rows)
    for key,old in (("observed_mass",OLD_ANNUAL),("NDE",OLD_NDE),
                    ("CE",OLD_CE),("SE",OLD_SE)):
        check(abs(fit_point[key]-old)<1e-8,f"separate original frozen fit mismatch {key}")
    groups=collections.defaultdict(list)
    for r in rows:groups[(r["pool"],r["rich"],r["FD_high"])].append(r)
    check(len(groups)==12,"original 12 source treatment cells changed")
    rng=np.random.default_rng(SEED)
    draws={k:[] for k in fit_point}
    failures=0
    for b in range(BOOT):
        sample=[]
        for key,grp in sorted(groups.items()):
            sample.extend(grp[int(i)] for i in rng.integers(0,len(grp),len(grp)))
        try:
            yy=fit(sample)
        except m.Stop:
            failures+=1;continue
        for key in draws:draws[key].append(yy[key])
    check(len(draws["NDE"])>=.9*BOOT,"paired plot bootstrap failed rank")
    ci={k:np.quantile(v,[.025,.975]).tolist() for k,v in draws.items()}
    report={
      "status":"JENA_TBE_ORIGINAL_84PLOT_OBSERVED_EXPECTED_MONO_NDE_ACCOUNTING_REPRODUCED",
      "original_source_doi":"10.1594/PANGAEA.876725",
      "source_plot_units":len(rows),
      "source_unique_pool_specific_monos":source["source_mono_plots"],
      "source_original_plot_prefix_A_B_C_physically_certified":False,
      "original_literal_Block_source_gate_still_HOLD":True,
      "computation_posthoc_after_original_annual_result":True,
      "model_and_source_identity_exactly_reproduced":True,
      "maximum_source_plot_accounting_identity_error":maxidentity,
      "effects_g_dry_mass_m2_high_minus_low":fit_point,
      "paired_original_plot_bootstrap_95CI":ci,
      "original_bootstrap_requested":BOOT,
      "original_bootstrap_successful":len(draws["NDE"]),
      "original_bootstrap_failed":failures,
      "source_plot_strata":"six original pool×richness + three candidate prefix classes",
      "biological_FD_effect_causally_identified":False,
      "additional_ecological_hypothesis_tests":0,
      "all_original_species_plot_and_biomass_rows_omitted":True,
      "interpretation":"Biomass high-low point contrast = monoculture expectation contrast + NDE point contrast. This is algebra of the original mixture and same-pool monocultures, not new independent causal mediation. Bootstrap conditional on fixed estimated monoculture yields; no physical block certification."
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("JENA_TBE_MATCHED_BIOMASS_EXPECTED_NDE_SOURCE_IDENTITY",json.dumps({
      "status":report["status"],
      "n":len(rows),
      "observed_beta":fit_point["observed_mass"],
      "mono_expected_beta":fit_point["expected_mono"],
      "NDE_beta":fit_point["NDE"],
      "expected_CI":ci["expected_mono"],
      "bootstrap":len(draws["NDE"]),
      "causal_mediation":False},sort_keys=True))

def test():
    assert OLD_ANNUAL-OLD_NDE <0
    assert abs(OLD_CE+OLD_SE-OLD_NDE)<1e-10
    assert BOOT==2000 and SEED==20261121
    print('{"status":"JENA_TBE_MONO_NDE_ACCOUNTING_FIXTURE_PASS","checks":3}')

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.self_test:test()
    elif a.out:main(a.out)
    else:p.error("--self-test or --out required")
