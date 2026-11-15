#!/usr/bin/env python3
"""Source-only BIODEPTH 2005 Shoots vs 2010 Community rounding and outlier audit.

No ecological coefficients, no plot-level response values emitted.
2010 internal species/group/community hierarchy already validated separately.
"""
from __future__ import annotations
import argparse,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from audit_biodepth_2005_2010_biomass_hierarchy_v0_1 import source,val,key

LEVELS=(1e-5,.01,.05,.1,.25,.5,1,2,5,10,50,100,500,1000)
REL_LEVELS=(.0001,.001,.01,.05,.10,1.)
SITE={str(i+1):name for i,name in enumerate(
    ("Germany","Portugal","Switzerland","Greece",
     "Ireland","Sweden","Sheffield","Silwood"))}

def summarize(pairs):
    a=np.asarray([q[0] for q in pairs],dtype=float)
    b=np.asarray([q[1] for q in pairs],dtype=float)
    if len(a)==0:
        return {"n":0}
    d=np.abs(b-a)
    den=np.maximum(np.abs(a),np.abs(b))
    rel=np.divide(d,den,out=np.zeros_like(d),where=den>0)
    bin_labels=[f"<={v:g}" for v in LEVELS]+[f">{LEVELS[-1]:g}"]
    count=Counter()
    for v in d:
        i=next((i for i,lev in enumerate(LEVELS) if v<=lev),len(LEVELS))
        count[bin_labels[i]]+=1
    if sum(count.values())!=len(a):
        raise AssertionError("difference bins are not a disjoint partition")
    return {
      "n":len(a),
      "n_2005_positive":int((a>0).sum()),
      "n_2010_positive":int((b>0).sum()),
      "n_zero_both":int(((a==0)&(b==0)).sum()),
      "n_2005_zero_2010_positive":int(((a==0)&(b>0)).sum()),
      "n_2010_zero_2005_positive":int(((b==0)&(a>0)).sum()),
      "median_abs_diff":float(np.median(d)),
      "p90_abs_diff":float(np.quantile(d,.9)),
      "p95_abs_diff":float(np.quantile(d,.95)),
      "p99_abs_diff":float(np.quantile(d,.99)),
      "max_abs_diff":float(d.max()),
      "median_signed_2010_minus_2005":float(np.median(b-a)),
      "n_2010_greater_by_gt1":int(((b-a)>1).sum()),
      "n_2010_lower_by_gt1":int(((b-a)<-1).sum()),
      "number_cumulative_abs_tolerance":{str(t):int((d<=t).sum()) for t in LEVELS},
      "number_cumulative_rel_tolerance":{str(t):int((rel<=t).sum()) for t in REL_LEVELS},
      "number_disjoint_abs_deviation_bins":dict(count),
      "n_relative_difference_gt_1pct":int((rel>.01).sum()),
      "n_absolute_difference_gt_50gm2":int((d>50).sum()),
      "n_absolute_difference_gt_100gm2":int((d>100).sum()),
      "n_large_difference_gt_10gm2":int((d>10).sum())
    }

def audit(s2005,full2010):
    S=source(s2005,"shoots2005")
    H=source(full2010,"mixed2010")
    if len(S)!=1440 or len(H)!=9816:
        raise ValueError("Original 2005/2010 raw row count changed")
    a={};b={}
    by_sy=defaultdict(list)
    n_2010Community=0
    n_2010Other=0
    for r in S:
        k=key(r)
        if k in a:raise ValueError("Duplicated 2005 original plot×year")
        a[k]=val(r["biomass"])
        loc=str(r["location"]).strip()
        if loc not in SITE:raise ValueError("Unexpected original 2005 site code")
        by_sy[(SITE[loc],k[1])].append(k)
    for r in H:
        if str(r["level"]).strip().casefold()!="community":
            n_2010Other+=1
            continue
        k=key(r)
        if k in b:raise ValueError("Duplicated original 2010 Community plot×year")
        b[k]=val(r["biomass"])
        n_2010Community+=1
    if set(a)!=set(b) or len(a)!=1440 or n_2010Community!=1440:
        raise ValueError("Original source plot-year keys are not identical")
    keys=[k for k in a if a[k] is not None and b[k] is not None]
    if len(keys)!=1415:
        raise ValueError("Expected original 1415 paired numeric responses")
    total=summarize([(a[k],b[k]) for k in keys])
    site_year={}
    for (site,year),grp in sorted(by_sy.items()):
        both=[k for k in grp if a[k] is not None and b[k] is not None]
        site_year[f"{site}|{year}"]={
           "n_expected_plot_years":len(grp),
           "n_both_numeric":len(both),
           "n_2005_missing":sum(a[k] is None for k in grp),
           "n_2010_missing":sum(b[k] is None for k in grp),
           **summarize([(a[k],b[k]) for k in both])}
    if len(site_year)!=24 or sum(v["n_both_numeric"] for v in site_year.values())!=len(keys):
        raise ValueError("Eight site × three year data total inconsistent")
    if total["max_abs_diff"]<1000 or total["median_abs_diff"]>1:
        raise ValueError("Prior source 0.125-median and 1170.4-max discrepancy changed")
    result={
        "version":"v0.1","status":"SOURCE_EDITION_NUMERIC_DIFFERENCE_DISTRIBUTION_AUDITED",
        "source_original_2005":"Spehn et al. 2005 original Shoots.txt DOI 10.6084/m9.figshare.3565170.v1",
        "source_original_2010":"Hector et al. 2010 original mixed Species/Group/Community Biomass.txt E091-155-S1",
        "raw_source_files_independently_sha_checked":True,
        "n_original_2010_hierarchy_rows":len(H),
        "n_original_2010_other_species_and_group_rows":n_2010Other,
        "n_unique_original_plot_years":1440,
        "n_numeric_matched_plot_years":len(keys),
        "source_edition_difference":total,
        "site_year_source_quality":site_year,
        "warning":"A positive or negative source version difference is not an ecological guild effect; no individual responses exported or modified.",
        "source_compatibility":"Numeric edition audit only; no equivalence decision until large differences are traced.",
        "no_FD_biomass_effect_fitted":True,
        "hard_nonclaims":[
          "Original 2010 internal hierarchy already additive; this audit compares two data editions",
          "Absolute precision differences are not necessarily distinct biological measurements",
          "A small median discrepancy cannot guarantee a source-compatible result in the presence of large outliers",
          "Original independent 6-site within-one-richness gate remains HOLD",
          "No causal guild, N-fixation, FD, biomass prediction or trait-memory result"
        ]}
    return result

def fixture():
    p=[(10,10.0),(10,10.4),(0,0),(0,2),(3,0)]
    q=summarize(p)
    assert q["n"]==5 and q["n_zero_both"]==1
    assert q["n_2005_zero_2010_positive"]==1
    assert q["n_2010_zero_2005_positive"]==1
    assert q["number_cumulative_abs_tolerance"]["1e-05"]==2
    assert sum(q["number_disjoint_abs_deviation_bins"].values())==5
    return {"status":"SOURCE_EDITION_TOLERANCE_FIXTURE_PASS","checks":5}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shoots")
    p.add_argument("--mixed")
    p.add_argument("--out")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:print(json.dumps(fixture()))
    else:
        if not all((args.shoots,args.mixed,args.out)):
            p.error("--shoots --mixed --out required")
        out=audit(args.shoots,args.mixed)
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print("BIODEPTH_2005_2010_SOURCE_DIFFERENCES",
              json.dumps({k:v for k,v in out.items() if k!="site_year_source_quality"},sort_keys=True))
        print("BIODEPTH_2005_2010_BY_SITE_YEAR",
              json.dumps({k:{field:value for field,value in v.items() if field in
                  ("n","n_expected_plot_years","n_both_numeric","median_abs_diff",
                   "p99_abs_diff","n_absolute_difference_gt_50gm2",
                   "n_absolute_difference_gt_100gm2",
                   "n_relative_difference_gt_1pct")}
                       for k,v in out["site_year_source_quality"].items()},sort_keys=True))
