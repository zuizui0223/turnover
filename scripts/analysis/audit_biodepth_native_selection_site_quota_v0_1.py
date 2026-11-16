#!/usr/bin/env python3
"""Retrospective BIODEPTH native-102 plot selection benchmark, source anchored.

New random-subset results frozen in
docs/BIODEPTH_NATIVE_PLOT_SELECTION_NULL_FROZEN_V0_1.md prior to outcomes.
Original 150 and native102 source-site SSEs must replay exactly first.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from fit_biodepth_2010_sown_height_fd_biomass_v0_1 import composition
from fit_biodepth_matched_pd_fd_biomass_transport_v0_1 import source_checks,score_sites
from audit_biodepth_native_vs_s3_fixed_cohort_v0_1 import (
    NATIVE_SITES,SITES,ABS_TOL,rank_check_before_response,compare_exact_results
)

N_RANDOM=499
SEED_SITE=20261116
SEED_MATCH=20261117
MIN_VALID=475
MIN_PARTIAL_SELECTED=10
MIN_PARTIAL_SITES=3


def cohort_key(plot: dict) -> tuple:
    return (plot["site"],int(plot["richness"]),
            int(plot["grass"]),int(plot["forbs"]),int(plot["legumes"]))


def features_summary(plots: dict) -> dict:
    sites=dict(sorted(Counter(k[0] for k in plots).items()))
    group=Counter()
    richness=Counter()
    for plot in plots.values():
        key="g"+str(plot["grass"])+"f"+str(plot["forbs"])+"l"+str(plot["legumes"])
        group[key]+=1
        richness[str(plot["richness"])]+=1
    def stats(k):
        x=np.asarray([p[k] for p in plots.values()],float)
        if not np.isfinite(x).all() or len(x)==0:
            raise ValueError("SOURCE_HOLD: source features invalid")
        return {"mean":float(np.mean(x)),
                "median":float(np.median(x)),
                "min":float(np.min(x)),
                "max":float(np.max(x))}
    return {
      "original_plots":len(plots),
      "original_field_site_plot_counts":sites,
      "planted_species_richness_distribution":dict(sorted(richness.items(),key=lambda x:int(x[0]))),
      "source_planned_guild_vector_distribution":dict(sorted(group.items())),
      "plot_mean_log_max_height":stats("cwm"),
      "plot_pairwise_log_height_dispersion":stats("mpd"),
      "plot_mean_pairwise_S3_patristic_distance":stats("pd"),
    }


def plan_sampling(all150:dict,native102:dict):
    pool=defaultdict(list)
    exact=defaultdict(list)
    selected_by_stratum=Counter()
    for key,p in sorted(all150.items()):
        pool[p["site"]].append(key)
        exact[cohort_key(p)].append(key)
    for key,p in native102.items():
        selected_by_stratum[cohort_key(p)]+=1
    if set(pool)!=set(SITES) or dict(Counter(k[0] for k in native102))!=NATIVE_SITES:
        raise ValueError("SOURCE_HOLD: original frozen field quota mismatch")
    partial=[(s,k,len(exact[s])) for s,k in sorted(selected_by_stratum.items())
             if 0<k<len(exact[s])]
    movable=sum(k for _,k,n in partial)
    sites=sorted({s[0] for s,k,n in partial})
    structural={
        "site_quotas":dict(sorted(NATIVE_SITES.items())),
        "original_source150_site_capacities":dict(sorted({s:len(v) for s,v in pool.items()}.items())),
        "native102_source_plots":len(native102),
        "source150_plots":len(all150),
        "number_exact_source_strata":len(exact),
        "number_strata_with_nontrivial_alternatives":len(partial),
        "selected_source_plots_in_nontrivial_strata":movable,
        "sites_with_nontrivial_exact_strata":sites,
        "secondary_structural_support":bool(movable>=MIN_PARTIAL_SELECTED and
                                             len(sites)>=MIN_PARTIAL_SITES)
    }
    return pool,exact,selected_by_stratum,structural


def sample(rng:np.random.Generator,pools:dict,quota:dict)->set:
    out=set()
    for k in sorted(pools):
        source=sorted(pools[k])
        n=int(quota.get(k,0))
        if n<0 or n>len(source):
            raise ValueError("SOURCE_HOLD: randomization quota exceeds eligible source")
        idx=rng.choice(len(source),size=n,replace=False)
        for index in idx:
            out.add(source[int(index)])
    if len(out)!=sum(quota.values()):
        raise AssertionError("Duplicate source plot or incomplete sampling")
    return out


def draw_benchmark(cells:list,source_pools:dict,quotas:dict,seed:int,
                   observed_gain:float, label:str) -> dict:
    rng=np.random.default_rng(seed)
    values=[]
    invalid=Counter()
    sample_year_n=Counter()
    for iteration in range(N_RANDOM):
        pick=sample(rng,source_pools,quotas)
        selected=[r for r in cells if (r["site"],r["plot"]) in pick]
        sample_year_n[str(len(selected))]+=1
        try:
            folds=score_sites(selected,SITES,method="mass")
            value=float(np.mean([x["pd_incremental_SSE_gain"] for x in folds]))
            if not math.isfinite(value):
                raise ValueError("MODEL_HOLD: nonfinite site equal gain")
            values.append(value)
        except ValueError as exc:
            m=str(exc)
            if ("MODEL_HOLD" in m or "RANK_DEFICIENT_TRAINING_MODEL" in m or
                "Training species-height predictor scale degenerate" in m):
                invalid[m[:90]]+=1
                continue
            raise
    valid=len(values)
    out={
        "benchmark":label,"seed":seed,"n_predeclared_draws":N_RANDOM,
        "n_valid_model_draws":valid,"n_invalid_model_draws":N_RANDOM-valid,
        "invalid_source_model_reasons":dict(invalid),
        "sampled_numeric_plot_year_row_counts":dict(sorted(sample_year_n.items())),
        "frozen_minimum_valid_draws":MIN_VALID,
        "status":"MODEL_INFORMATIVENESS_PASS" if valid>=MIN_VALID else "MODEL_INFORMATIVENESS_HOLD"
    }
    if valid<MIN_VALID:
        out["interpretation"]="Model geometry invalid for too many predeclared samples: no null tail or quantitative conclusion"
        return out
    v=np.asarray(values,float)
    out.update({
        "observed_native102_fullS3_gain":observed_gain,
        "benchmark_mean":float(np.mean(v)),
        "benchmark_median":float(np.median(v)),
        "benchmark_q025_q50_q975":[float(x) for x in np.quantile(v,[.025,.5,.975])],
        "benchmark_min_max":[float(v.min()),float(v.max())],
        "native_observed_minus_benchmark_median_pp":float(100*(observed_gain-np.median(v))),
        "count_draws_at_or_below_native_observed_gain":int((v<=observed_gain).sum()),
        "conditional_descriptive_lower_tail_reference_p":float((1+(v<=observed_gain).sum())/(valid+1)),
        "n_positive_gain_draws":int((v>0).sum()),
        "interpretation":"Source-stratified descriptive resampling reference, NOT a causal treatment randomization or prospective independent null."
    })
    return out


def run(args) -> dict:
    old=json.loads(Path(args.previous).read_text(encoding="utf8"))
    if (old["status"]!="POSTRESULT_PAIRED_102_NATIVE_S3_COHORT_DIAGNOSTIC_ESTIMATED" or
        old["original_150_cohort"]["plots"]!=150 or
        old["new_102_cohort_full_S3"]["plots"]!=102):
        raise ValueError("SOURCE_HOLD: controlling prior result not exact")
    srows,crows,all150,native102,height,qa=source_checks(args)
    rank_check_before_response(all150,native102)
    original={k:all150[k] for k in native102}
    dropped={k:all150[k] for k in all150 if k not in native102}
    if len(dropped)!=48 or len(original)!=102:
        raise ValueError("SOURCE_HOLD: 150 and 102 nonoverlapping source cohorts not reproduced")
    sitepool,stratapool,quota,struct=plan_sampling(all150,native102)
    source_audit={
      "source_no_outcome_plots":150,
      "native_selected_original_plots":102,
      "not_selected_source_eligible_original_plots":48,
      "full150_source_features":features_summary(all150),
      "fixed_native102_source_features":features_summary(original),
      "omitted48_source_features":features_summary(dropped),
      "selection_strata_eligibility":struct
    }
    print("BEFORE_SELECTION_NULL_SOURCE_PLOT_SUPPORT",
          json.dumps(source_audit,sort_keys=True),flush=True)

    old_plots,original_cells,missing,sitepop=composition(
        srows,crows,args.design,args.community,height,qa)
    if len(old_plots)!=174 or len(original_cells)!=521 or missing!=1:
        raise ValueError("SOURCE_HOLD: source Community 174/521 changed")
    cells=[{**r,**all150[(r["site"],r["plot"])]}
           for r in original_cells if (r["site"],r["plot"]) in all150]
    native=[r for r in cells if (r["site"],r["plot"]) in native102]
    if len(cells)!=449 or len(native)!=305:
        raise ValueError("SOURCE_HOLD: source Community 150/449 native102/305 mismatch")
    s150=score_sites(cells,SITES,method="mass")
    s102=score_sites(native,SITES,method="mass")
    compare_exact_results(s150,old["original_150_cohort"]["mass_PD_increment"]["site_records"],"PR52-full150")
    compare_exact_results(s102,old["new_102_cohort_full_S3"]["mass_PD_increment"]["site_records"],"PR52-full102")
    obs=float(np.mean([r["pd_incremental_SSE_gain"] for r in s102]))
    if abs(obs-(-0.04008463029040919))>1e-10:
        raise ValueError("PARENT_SOURCE_HOLD: original native-selected full S3 gain changed")
    print("PR52_150_AND_102_ORIGINAL_SSE_REPLAY_PASS",
          json.dumps({"original_full150_gain":float(np.mean([r["pd_incremental_SSE_gain"] for r in s150])),
            "original_native102_fullS3_gain":obs},sort_keys=True),flush=True)

    primary=draw_benchmark(cells,sitepool,NATIVE_SITES,SEED_SITE,obs,
                           "Fixed per-site native102 quotas; random original plot IDs within each original field")
    if struct["secondary_structural_support"]:
        secondary=draw_benchmark(cells,stratapool,quota,SEED_MATCH,obs,
             "Fixed site × exact planted species richness × planned grass/forb/legume vector")
    else:
        secondary={
          "status":"SECONDARY_DESIGN_SUPPORT_HOLD",
          "seed":SEED_MATCH,
          "n_predeclared_draws":N_RANDOM,
          "reason":"fewer than 10 movable selected source plots or fewer than 3 sites with alternative plots after exact matching",
          "source_only_structural_support":struct
        }
    return {
        "version":"v0.1",
        "status":"POSTRESULT_NATIVE_102_SOURCE_SELECTION_BENCHMARK_COMPLETED" if primary["status"]=="MODEL_INFORMATIVENESS_PASS" else "MODEL_INFORMATIVENESS_HOLD",
        "design":"docs/BIODEPTH_NATIVE_PLOT_SELECTION_NULL_FROZEN_V0_1.md",
        "source_project":"Hector 2010 original Community, 150 original GIFT×GBOTB plots, seven field sites",
        "original_150_plot_years":449,"native102_plot_years":305,
        "historical_150_allS3_gain":float(np.mean([r["pd_incremental_SSE_gain"] for r in s150])),
        "historical_102_fullS3_gain":obs,
        "prior_source_150_and_102_SSE_replayed_exact":True,
        "source_original_GIFT_fingerprint":qa["GIFT_original_target_species_height_and_reference_fingerprint_sha256"],
        "original_source_selection_eligibility":source_audit,
        "site_quotas_primary":primary,
        "site_exact_richness_guild_secondary":secondary,
        "original_Community2010_response_used":True,
        "old_BIEN_family_K_and_rho_not_compared":True,
        "original_six_high_density_BIODEPTH_and_global_BIEN_NEON_source_gates":"HOLD",
        "hard_nonclaims":[
          "Prior 102 subset gain was known before these random-selection benchmarks were designed; not a prospective hypothesis test",
          "Source tip eligibility was not randomly assigned; tail is descriptive reference only",
          "Every repeated plot-year remains nested within an original field and plot",
          "All randomized site-quota 102 plots are historical data subsets of the SAME 150 original BIODEPTH plots; not independent field replication",
          "One-axis height FD uses species maxima and cannot be equated with actual competition/complementarity",
          "No lineage-specific Blomberg K or BIEN memory rho joined and no causal PD→FD→mass mechanism tested",
          "Existing 201-family GIFT/sPlotOpen BIEN, strict six-site BIODEPTH and NEON authenticated source gates remain HOLD"
        ],
    }


def fixture():
    source={"x":[("x","p1"),("x","p2")],"y":[("y","p3")]}
    quota={"x":1,"y":1}
    a=sample(np.random.default_rng(SEED_SITE),source,quota)
    b=sample(np.random.default_rng(SEED_SITE),source,quota)
    assert a==b and len(a)==2
    assert sorted(k[0] for k in a)==["x","y"]
    assert N_RANDOM==499 and MIN_VALID==475
    assert SEED_MATCH!=SEED_SITE
    return {"status":"PLOT_SELECTION_BENCHMARK_FIXTURE_PASS","checks":5}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    for key in ("species","codes","design","community","provenance","phylogeny-gate",
                "joint-gate","tree-crosswalk","tree-distances","previous","out"):
        p.add_argument("--"+key)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        print(json.dumps(fixture()))
    else:
        required=("species","codes","design","community","provenance","phylogeny-gate",
                  "joint-gate","tree-crosswalk","tree-distances","previous","out")
        if not all(getattr(a,key.replace("-","_")) for key in required):
            p.error("Every original source path and prior source-result file is required")
        result=run(a)
        d=Path(a.out);d.parent.mkdir(parents=True,exist_ok=True)
        d.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("BIODEPTH_NATIVE_SELECTION_BENCHMARK_RESULT",
              json.dumps({k:v for k,v in result.items()
                  if k not in ("hard_nonclaims",)},sort_keys=True),flush=True)
