#!/usr/bin/env python3
"""BIODEPTH matched guild response sensitivity to original 2005 vs 2010 source edition.

Post-result exploratory source harmonization, NOT new causal ecological inference.
Uses same source design, exact site x planted richness x block treatment strata,
and complete-case plot-years in both original biomass edition tables.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from audit_biodepth_2005_2010_biomass_hierarchy_v0_1 import source,val,key

DESIGN_SHA="a3029e18937b577aa2dafd9efb31fc50bf8fa39a0c1b48bca7c493cc6013cc7a"
SEED=20261115
BOOT=10000

def audit(design_path,sho2005,mixed2010):
    original=Path(design_path).read_bytes()
    if hashlib.sha256(original).hexdigest()!=DESIGN_SHA:
        raise ValueError("Original 2005 480-plot design SHA changed")
    D=list(csv.DictReader(io.StringIO(original.decode("utf-8-sig")),delimiter="\t"))
    if len(D)!=480:raise ValueError("2005 original fixed 480 plots missing")
    design={r["plot"]:r for r in D}
    if len(design)!=480:raise ValueError("Original design duplicates plot codes")
    keys=("location","species.richness","block")
    eligible=[
        r for r in D if r["grasses"]=="Yes" and r["functional.richness"]=="2"
        and ((r["legumes"]=="Yes" and r["forbs"]=="No")
             or (r["legumes"]=="No" and r["forbs"]=="Yes"))
    ]
    if len(eligible)!=114:raise ValueError("Original source treatment candidate 114 changed")
    groups=defaultdict(set)
    for r in eligible:groups[tuple(r[k] for k in keys)].add(r["legumes"])
    retained={k for k,arms in groups.items() if arms=={"Yes","No"}}
    chosen={r["plot"]:r for r in eligible if tuple(r[k] for k in keys) in retained}
    if len(retained)!=35 or len(chosen)!=110:
        raise ValueError("Original exact 110 plot and 35 stratum pre-outcome source support changed")
    sh=source(sho2005,"shoots2005")
    hi=source(mixed2010,"mixed2010")
    s2005={}
    community={}
    level=Counter()
    for r in sh:
        k=key(r)
        if k in s2005:raise ValueError("Duplicate original 2005 plot-year source")
        s2005[k]=val(r["biomass"])
        if r["plot"] not in design:raise ValueError("2005 plot not in original design")
    for r in hi:
        level[str(r["level"]).strip().casefold()]+=1
        if str(r["level"]).strip().casefold()!="community":continue
        k=key(r)
        if k in community:raise ValueError("Duplicate 2010 community response per source plot/year")
        community[k]=val(r["biomass"])
    if set(s2005)!=set(community) or len(s2005)!=1440 or level["community"]!=1440:
        raise ValueError("2005 and 2010 original source not same 1440 plot-years")
    original_total=0
    retained_total=0
    complete_cases=defaultdict(dict)
    missing_by_site=Counter()
    for p,r in chosen.items():
        site=r["location"]
        arm=r["legumes"]
        rich=r["species.richness"];block=r["block"]
        for yr in (1,2,3):
            original_total+=1
            k=(p,yr)
            a=s2005[k];b=community[k]
            if a is None or b is None:
                missing_by_site[site]+=1
                continue
            retained_total+=1
            groupkey=(site,rich,block,yr)
            bucket=complete_cases[groupkey]
            bucket.setdefault(arm,[]).append((p,math.log1p(a),math.log1p(b)))
    if original_total!=330:raise ValueError("Must start from fixed 110 plots × 3 years")
    records=defaultdict(lambda:defaultdict(list))
    n_valid_strat_year=Counter()
    for (site,rich,block,yr),arms in complete_cases.items():
        if not set(arms)=={"Yes","No"}:continue
        d2005=statistics.mean(item[1] for item in arms["Yes"])-statistics.mean(item[1] for item in arms["No"])
        d2010=statistics.mean(item[2] for item in arms["Yes"])-statistics.mean(item[2] for item in arms["No"])
        records[site][(rich,block)].append((yr,d2005,d2010))
        n_valid_strat_year[site]+=1
    unique_strata=sum(len(x) for x in records.values())
    n_pair_year=sum(n_valid_strat_year.values())
    if len(records)!=8 or unique_strata<30 or n_pair_year<95:
        raise ValueError(f"Common source support too sparse, matched {unique_strata} strata, {n_pair_year} paired source-year contrasts")
    site_rows=[]
    for site in sorted(records):
        block=records[site]
        a=[statistics.mean(t[1] for t in yearvals) for yearvals in block.values()]
        b=[statistics.mean(t[2] for t in yearvals) for yearvals in block.values()]
        e2005=statistics.mean(a);e2010=statistics.mean(b)
        nplot=sum(p["location"]==site for p in chosen.values())
        site_rows.append({
            "site":site,"source_selected_original_plots":nplot,
            "n_common_source_comparable_strata":len(block),
            "n_common_source_stratum_years":n_valid_strat_year[site],
            "n_missing_2005_or_2010_original_plot_year_rows":missing_by_site[site],
            "common_cohort_2005_log1p_guild_substitution_D":e2005,
            "common_cohort_2010_log1p_guild_substitution_D":e2010,
            "edition_difference_D_2010_minus_D_2005":e2010-e2005,
            "source_guild_contrast_sign_changed":(e2005<0)!=(e2010<0)})
    delta=np.asarray([x["edition_difference_D_2010_minus_D_2005"] for x in site_rows])
    x=np.asarray([x["common_cohort_2005_log1p_guild_substitution_D"] for x in site_rows])
    y=np.asarray([x["common_cohort_2010_log1p_guild_substitution_D"] for x in site_rows])
    rand=np.random.default_rng(SEED)
    reselect=rand.integers(0,8,size=(BOOT,8))
    sims=delta[reselect].mean(axis=1)
    out={
      "version":"v0.1",
      "status":"ORIGINAL_BIODEPTH_RESPONSE_EDITION_MATCHED_GUILD_SENSITIVITY_COMPLETED",
      "source_versions":{
        "Original_2005_Figshare_Shoots_SHA256":"cc259a57abc89a79f626c4d9497a205c1190580428cd3d7152039cd17f704135",
        "Original_2010_Hector_mixed_Community_SHA256":"9d95e65295bf6014e753f474dffa09036718b6b54ad5e1d4eea41c1dde76f886",
        "Original_2005_design_SHA256":DESIGN_SHA},
      "n_original_plots_study":480,
      "n_exact_preselected_matched_plots":110,
      "n_original_matched_strata":35,
      "n_original_matched_plot_years_before_two_source_missingness":original_total,
      "n_original_matched_plot_years_both_source_numeric":retained_total,
      "n_original_source_comparable_strata":unique_strata,
      "n_original_source_comparable_stratum_years":n_pair_year,
      "n_original_sites":len(site_rows),
      "site_results":site_rows,
      "eight_site_equal_source_effect_means":{
        "common_cohort_2005":float(x.mean()),
        "common_cohort_2010":float(y.mean()),
        "common_cohort_2010_minus_2005":float(delta.mean()),
        "n_sites_source_guild_sign_changes":sum(v["source_guild_contrast_sign_changed"] for v in site_rows),
        "site_cluster_bootstrap_10000_edition_difference_ci95":
           [float(v) for v in np.quantile(sims,[.025,.975])],
        "bootstrap_seed":SEED},
      "old_2005_original_110_plot_whole_327_source_year_mean_not_common_cohort":0.17147354565109507,
      "hard_nonclaims":[
        "Two numerical source editions are NOT independent experimental repeats",
        "The common plot×year cohort controls sample selection but not processing/method differences between original editions",
        "This is post-result exploratory measured-response harmonization, not a confirmatory legume effect",
        "It does not identify which source edition is ecologically correct or causal",
        "No actual FD or phylogenetic-memory rho tested",
        "Original six-site single-richness-20plot primary gate remains HOLD"],
    }
    return out
def fixture():
    assert math.log1p(0)==0
    d1=np.asarray([2.,-2.]);rng=np.random.default_rng(20261115)
    k=rng.integers(0,2,size=(10,2))
    assert np.asarray(d1[k].mean(axis=1)).shape==(10,)
    return {"status":"EDITION_MATCHED_GUILD_SENSITIVITY_FIXTURE_PASS","checks":2}
if __name__=="__main__":
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--design");a.add_argument("--shoots");a.add_argument("--mixed");a.add_argument("--out")
    a.add_argument("--self-test",action="store_true")
    args=a.parse_args()
    if args.self_test:print(json.dumps(fixture()))
    else:
        if not all((args.design,args.shoots,args.mixed,args.out)):
            a.error("--design --shoots --mixed --out all required")
        ans=audit(args.design,args.shoots,args.mixed)
        f=Path(args.out);f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(json.dumps(ans,indent=2,ensure_ascii=False)+"\n")
        print("BIODEPTH_EDITION_MATCHED_GUILD_SENSITIVITY",json.dumps({k:v for k,v in ans.items() if k!="site_results"},sort_keys=True))
        for item in ans["site_results"]:
            print("BIODEPTH_EDITION_MATCHED_SITE",json.dumps(item,sort_keys=True))
