#!/usr/bin/env python3
"""Retrospective Wagg 2017 2012 Jena TBE designed high/low FD vs annual sown biomass.

Source fixed and MD5/sha-gated, 84 original plot units, no original raw rows
or species names published. This is a noncausal original-composition contrast,
not a newly independent site or FD-only intervention.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,re,sys
from pathlib import Path
import numpy as np

sys.path.insert(0,"scripts/source")
import audit_jena_tbe_2012_assigned_fd_biomass_v0_1 as a

SOURCE_SHA="458f61307df217d285c972f894ca5cf23709c3524dc6e13bb4d9dd3c26c2ab56"
N_BOOT=2000
SEED=20261121
PAT=re.compile(r"^B0B([ABC])[0-9]{3}$")
PRECONTRACT="docs/JENA_TBE2012_ASSIGNED_HIGHLOW_FD_ANNUAL_BIOMASS_RETROSPECTIVE_V0_2.md"

class SourceHold(Exception):pass
def check(x,why):
    if not x:raise SourceHold(why)

def origin_table():
    original=a.public_bytes()
    check(hashlib.sha256(original).hexdigest()==SOURCE_SHA,"ORIGINAL_PANGAEA_BYTES_CHANGED")
    headers,raw=a.parse_source(original)
    audit=a.inspect(headers,raw)
    # Original failed gate is not retroactively changed by this new estimator.
    check(audit["status"]=="ORIGINAL_TBE_SOURCE_OR_DESIGN_HOLD"
          and audit["source_field_blocks_distinct"]==1,
          "ORIGINAL_V01_LITERAL_BLOCK_GATE_WAS_NOT_THE_SAME")
    check(audit["source_unique_plot_IDs"]==138 and audit["source_harvest_rows"]==276,
          "ORIGINAL_FROZEN_COHORT_CHANGED")
    check(audit["source_unique_eligible_multispecies_plots"]==114
          and audit["source_matched_high_vs_low_FD_strata_n"]==6
          and audit["source_matched_high_vs_low_FD_plot_count"]==84,
          "SOURCE_FD_RICHNESS_STRATUM_SUPPORT_CHANGED")
    labels={
      "plot":a.find_col(headers,("plot",)),
      "month":a.find_col(headers,("month",)),
      "fd":a.find_col(headers,("wfdc","functional diversity")),
      "rich":a.find_col(headers,("spec no","number of species")),
      "pool":a.find_col(headers,("species pool",)),
      "block":a.find_col(headers,("block",))
    }
    planted=[x for x in headers if "biom" in x.lower() and "dw" in x.lower()
             and not any(k in x.lower() for k in ("weed","unid","dead"))]
    check(len(planted)==20,"ORIGINAL_PLANTED_SPECIES_COLUMN_SET_CHANGED")
    byplot=collections.defaultdict(list)
    for row in raw:
        pid=(row[labels["plot"]] or "").strip()
        code=PAT.fullmatch(pid)
        check(code is not None,"PLOT_ID_NOT_ORIGINAL_FIXED_PREFIX")
        month=row[labels["month"]].strip()
        rich=a.parsed_number(row[labels["rich"]],integer=True)
        fd=a.parsed_number(row[labels["fd"]],integer=True)
        pool=row[labels["pool"]].strip()
        literal=row[labels["block"]].strip()
        check(month in ("May","Aug"),"SOURCE_MONTH_NOT_MAY_AUG")
        check(rich in (1,2,3,4,8),"SOURCE_ORIGINAL_RICHNESS_SET_CHANGED")
        check(fd in (0,1,2,3,4),"SOURCE_FD_CATEGORIES_CHANGED")
        sown=[k for k in planted if (row.get(k) or "").strip()!=""]
        check(len(sown)==rich,"SOURCE_SOWN_ROSTER_DRIFT")
        biomass=[a.parsed_number(row[k]) for k in sown]
        check(all(n is not None and n>=0 for n in biomass),"SOURCE_MISSING_PLANTED_BIOMASS")
        byplot[pid].append({
            "prefix":code.group(1),"month":month,"pool":pool,"literal":literal,
            "richness":rich,"fd":fd,"sown_roster":frozenset(sown),
            "biomass_for_year":sum(biomass)
        })
    check(len(byplot)==138,"SOURCE_ORIGINAL_138_PLOTS_CHANGED")
    prefixes=collections.Counter()
    candidate=[]
    for pid,rs in byplot.items():
        check(len(rs)==2 and set(x["month"] for x in rs)=={"May","Aug"},
              "PLOT_TWO_MONTHS_INCOMPLETE")
        check(len({(r["prefix"],r["pool"],r["literal"],r["richness"],r["fd"],r["sown_roster"]) for r in rs})==1,
              "ORIGINAL_PLOT_TREATMENT_METADATA_DISAGREES_ACROSS_MONTHS")
        r=rs[0];prefixes[r["prefix"]]+=1
        if r["richness"]<2:continue
        candidate.append({"pool":r["pool"],"rich":r["richness"],"fd":r["fd"],
            "prefix":r["prefix"],"annual_sown_dry_mass_g_m2":sum(x["biomass_for_year"] for x in rs)})
    check(sorted(prefixes.values())==[46,46,46],
          "PANGAEA_CANDIDATE_BLOCK_PREFIX_BALANCE_HOLD")
    check(len(candidate)==114,"SOURCE_2012_TWO_HARVEST_MIXTURE_COUNT_CHANGED")
    groups=collections.defaultdict(list)
    for z in candidate:groups[(z["pool"],z["rich"])].append(z)
    qualkeys=[]
    for key,rs in groups.items():
        low=sum(z["fd"]<=2 for z in rs)
        high=sum(z["fd"]>=3 for z in rs)
        if low>=4 and high>=4:qualkeys.append(key)
    check(len(qualkeys)==6,"ORIGINAL_COMPARISON_POOL_RICHNESS_SUPPORT_HOLD")
    eligible=[r for key in qualkeys for r in groups[key]]
    check(len(eligible)==84,"ORIGINAL_84_MIXTURE_CONTRAST_SUPPORT_DRIFT")
    check(len({r["pool"] for r in eligible})==3 and len({r["prefix"] for r in eligible})==3,
          "ORIGINAL_SOURCE_THREE_POOL_OR_PREFIX_CLASSES_CHANGED")
    support=collections.Counter((r["pool"],r["rich"],r["fd"]>=3) for r in eligible)
    check(all(support[(pool,rich,group)]>=4 for pool,rich in qualkeys for group in (False,True)),
          "SOWN_FD_HIGH_LOW_CELL_MINIMUM_FAILED")
    summary={
      "source_unique_plot_units":len(byplot),
      "source_monthly_original_rows":len(raw),
      "source_complete_mixture_plots":len(candidate),
      "source_matched_high_low_mixture_plot_units":len(eligible),
      "source_high_low_sown_FD_pool_x_richness_strata":len(qualkeys),
      "source_prefix_class_count":len(prefixes),
      "original_source_Block_column_distinct_values":1,
      "prefix_plot_counts_anonymized":sorted(prefixes.values()),
      "six_stratum_plot_counts_anonymized":sorted(len(groups[k]) for k in qualkeys),
      "two_harvests_exactly_May_Aug":True,
      "physical_randomized_block_identity_author_certified":False,
    }
    return eligible,summary

def xmatrix(data):
    strata=sorted({(r["pool"],r["rich"]) for r in data})
    prefixes=sorted({r["prefix"] for r in data})
    check(len(strata)==6 and len(prefixes)==3,"ANALYSIS_SOURCE_STRATA_CHANGED")
    X=np.zeros((len(data),1+(len(strata)-1)+(len(prefixes)-1)+1))
    for i,r in enumerate(data):
        X[i,0]=1
        s=(r["pool"],r["rich"])
        if s!=strata[0]:X[i,1+strata.index(s)-1]=1
        if r["prefix"]!=prefixes[0]:X[i,1+len(strata)-1+prefixes.index(r["prefix"])-1]=1
        X[i,-1]=int(r["fd"]>=3)
    return X

def fit(rows,raw=False):
    X=xmatrix(rows)
    groupcount=collections.Counter((r["pool"],r["rich"]) for r in rows)
    w=np.asarray([1/groupcount[(r["pool"],r["rich"])] for r in rows],float)
    y=np.asarray([r["annual_sown_dry_mass_g_m2"] for r in rows],float)
    if not raw:y=np.log1p(y)
    check(np.linalg.matrix_rank(X)==X.shape[1],"SOURCE_TREATMENT_ESTIMATOR_NOT_FULLRANK")
    check(np.linalg.cond(X)<1e8,"SOURCE_TREATMENT_DESIGN_ILL_CONDITIONED")
    xw=X*np.sqrt(w)[:,None]
    yw=y*np.sqrt(w)
    return float(np.linalg.lstsq(xw,yw,rcond=None)[0][-1])

def strat_boot(rows,raw=False):
    grouped=collections.defaultdict(list)
    for r in rows:grouped[(r["pool"],r["rich"],r["fd"]>=3)].append(r)
    check(len(grouped)==12,"BOOTSTRAP_ORIGINAL_HIGHLOW_STRATA_CHANGED")
    rng=np.random.default_rng(SEED)
    point=fit(rows,raw=raw)
    draws=[]
    nfail=0
    for _ in range(N_BOOT):
        drawn=[]
        for key,rr in sorted(grouped.items()):
            for i in rng.integers(0,len(rr),size=len(rr)):
                drawn.append(rr[int(i)])
        try:draws.append(fit(drawn,raw=raw))
        except SourceHold:nfail+=1
    check(len(draws)>=N_BOOT*.9,"BOOTSTRAP_REFIT_SOURCE_SUPPORT_HOLD")
    return {"original_annual_biomass_scale":"raw_g_dry_mass_m2" if raw else "log1p_g_dry_mass_m2",
        "estimated_high_FD_minus_low_FD_coefficient":point,
        "stratified_plot_bootstrap_95CI":np.quantile(draws,[.025,.975]).tolist(),
        "bootstrap_successful_fixed_model_refits":len(draws),
        "bootstrap_failed_rank_or_condition":nfail,
        "bootstrap_replicates_predeclared":N_BOOT}

def main(out):
    result={"status":"SOURCE_OR_DESCRIPTIVE_FD_CONTRAST_HOLD",
       "source_doi":"10.1594/PANGAEA.876725",
       "frozen_analyzing_document":"docs/JENA_TBE2012_ASSIGNED_HIGHLOW_FD_ANNUAL_BIOMASS_RETROSPECTIVE_V0_2.md",
       "original_v01_literal_3_Block_levels_HOLD_preserved":True,
       "original_JEXIS_739_physical_block_crosswalk_HOLD":True,
       "causal_FD_specific_effect_claimed":False,
       "independent_out_of_study_replication":False,
       "biomass_annual_sown_harvest_not_NDE":True,
       "source_raw_plot_species_biomass_rows_redistributed":False,
       "source_results_from_original_published_study_already_known":True}
    try:
        rows,source=origin_table()
        result["source_only_matched_support"]=source
        result["primary"]=strat_boot(rows,raw=False)
        result["secondary_raw_mass"]=strat_boot(rows,raw=True)
        result["primary"]["log1p_treatment_multiplicative_contrast_percent"]=100*(math.exp(result["primary"]["estimated_high_FD_minus_low_FD_coefficient"])-1)
        result["status"]="JENA_TBE2012_RETROSPECTIVE_DESCRIPTIVE_HIGHLOW_FD_BIOMASS_FIT_COMPLETE"
    except (SourceHold,ValueError,urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError) as exc:
        result["hold_reason_class"]=type(exc).__name__
        if isinstance(exc,SourceHold):result["hold_reason"]=str(exc)[:110]
        if isinstance(exc,urllib.error.HTTPError):result["source_http"]=exc.code
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("JENA_TBE_DESCRIPTIVE_FD_2012",json.dumps({
        "status":result["status"],
        "original_plot_count":result.get("source_only_matched_support",{}).get("source_unique_plot_units"),
        "matched_plot_count":result.get("source_only_matched_support",{}).get("source_matched_high_low_mixture_plot_units"),
        "log_diff":result.get("primary",{}).get("estimated_high_FD_minus_low_FD_coefficient"),
        "log_ci":result.get("primary",{}).get("stratified_plot_bootstrap_95CI"),
        "causal_claim":False}))

def selftest():
    cases=[{"pool":"S","rich":2,"prefix":"A","fd":1,"annual_sown_dry_mass_g_m2":200},
           {"pool":"P","rich":3,"prefix":"B","fd":3,"annual_sown_dry_mass_g_m2":400}]
    assert len(cases)==2 and cases[0]["fd"]<=2 and cases[1]["fd"]>=3
    assert N_BOOT==2000 and SEED==20261121
    assert math.isclose(math.log1p(0),0)
    print('{"status":"JENA_TBE_V02_FIXED_DESCRIPTIVE_FIXTURE_PASS","checks":3}')

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.self_test:selftest()
    elif args.out:main(args.out)
    else:p.error("Choose --self-test or --out")
