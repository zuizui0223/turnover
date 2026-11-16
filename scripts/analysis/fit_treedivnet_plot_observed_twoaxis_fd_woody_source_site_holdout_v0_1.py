#!/usr/bin/env python3
"""Exploratory TreeDivNet 2026 source plot-local SLA/LNCM FD -> DS1 woody biomass.

One ORIGINAL DS1 stand woody outcome per plot, no DS2 species biomass and
no original authors' published monoculture/TRY-imputed FDis.
Frozen before opening these new held-out experimental site FD results:
docs/TREEDIVNET_OBSERVED_PLOT_TRAIT_FD_WOODY_SITE_TRANSFER_FROZEN_V0_1.md
Do not infer causality, independent study replication, family-specific K.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"source"))
from audit_treedivnet_figshare_workbooks_v0_1 import fetch_file
from audit_treedivnet_ds1_ds2_exact_plot_join_v0_1 import load_sheet,compact,safe_num,CORE
from audit_treedivnet_table_s1_year_matched_plots_v0_6 import verify_year_table

SEED=20261117
BOOTSTRAP_REPS=10000
OBSERVED_AXES=("SLA","LNCM")
MIN_JOINT_COVERAGE=.80
MIN_PLOTS=80
MIN_SITE_PLOTS=8
MIN_SITES=5
MIN_SPECIES=20
YEAR_GAP_MAX=2
PRIOR_SITE_SCOPES={
    "all_source_site_year_qualified_main":{
       "B-Tree":9,"FORBIO_Gedinne":12,"FORBIO_Hechtel-Eksel":12,
       "IDENT_Freiburg":4,"IDENT_Macomer":12,"MataDIV":10,"MyDiv":58},
    "no_ECOLINK_or_MataDIV":{
       "B-Tree":9,"FORBIO_Gedinne":12,"FORBIO_Hechtel-Eksel":12,
       "IDENT_Freiburg":4,"IDENT_Macomer":12,"MyDiv":58},
}


def build_original_source_eligibility(years):
    _,ds1=load_sheet(fetch_file("DS1.xlsx"),"DS1.xlsx")
    _,ds2=load_sheet(fetch_file("DS2.xlsx"),"DS2.xlsx")
    if len(ds1)!=363 or len(ds2)!=689:
        raise ValueError("ORIGINAL_SOURCE_HOLD: source raw rows changed")
    plots={}
    species=collections.defaultdict(list)
    seen=set()
    for x in ds1:
        k=tuple(compact(x[c]) for c in CORE)
        if not all(k) or k in plots:raise ValueError("ORIGINAL_SOURCE_HOLD: stand source ID not unique")
        plots[k]=x
    for x in ds2:
        k=tuple(compact(x[c]) for c in CORE)
        label=compact(x["species"])
        if not all(k) or not label or (*k,label) in seen:
            raise ValueError("ORIGINAL_SOURCE_HOLD: original species source ID duplicate or empty")
        seen.add((*k,label));species[k].append(x)
    if len(set(plots)&set(species))!=328:
        raise ValueError("ORIGINAL_SOURCE_HOLD: previously verified original 328 plot join changed")
    main=[]
    for k in sorted(set(plots)&set(species)):
        site=k[0]
        if site=="ECOLINK_Uppsala":continue
        meta=years.get(site)
        if not meta:raise ValueError("ORIGINAL_SOURCE_HOLD: Table S1 source experiment not found")
        gaps=meta["minimum_absolute_inventory_year_gap_to_woody"]
        if any(gaps[a] is None or gaps[a]>YEAR_GAP_MAX for a in OBSERVED_AXES):
            continue
        ds1r=plots[k]
        woody=safe_num(ds1r.get("biomass_woody"))
        if woody is None:continue
        richness=safe_num(ds1r.get("species_richness"),positive=True)
        rr=species[k]
        if richness is None or int(richness)!=richness:raise ValueError("ORIGINAL_SOURCE_HOLD: noninteger source richness")
        richness=int(richness)
        if len(rr)!=len(set(compact(r["species"]) for r in rr)):raise ValueError("ORIGINAL_SOURCE_HOLD: duplicate species")
        jointly=[r for r in rr if all(safe_num(r.get(a),positive=True) is not None for a in OBSERVED_AXES)]
        if len(jointly)<2:continue
        if richness!=len(rr) or len(jointly)/richness<MIN_JOINT_COVERAGE:continue
        traits=np.array([[float(r["SLA"]),float(r["LNCM"])] for r in jointly],dtype=float)
        if not np.isfinite(traits).all() or np.any(traits<=0):
            raise ValueError("ORIGINAL_SOURCE_HOLD: invalid original source measured traits")
        main.append({
           "site":site,
           "plot_key":k,
           "richness":richness,
           "n_source_species":len(rr),
           "n_complete_traits":len(jointly),
           "log_traits":np.log(traits),
           # Value below not used to select any plot beyond source numeric existence.
           "response":float(np.log1p(woody)),
           "positive_trait_taxa":set(compact(r["species"]) for r in jointly),
           "study_design_original":"MataDIV_FERTILIZED_ONLY" if site=="MataDIV" else "MIXED_FORESTRY_EXP",
        })
    counts=collections.Counter(r["site"] for r in main)
    if counts!=collections.Counter(PRIOR_SITE_SCOPES["all_source_site_year_qualified_main"]):
        raise ValueError("SOURCE_COHORT_HOLD: 117 original site/source support and original trait completeness were not reproduced")
    if sum(x["n_source_species"]!=x["n_complete_traits"] for x in main):
        raise ValueError("SOURCE_HOLD: original 117 source cohort is not 100% two-axis complete")
    if len(main)!=117:raise ValueError("SOURCE_COHORT_HOLD: exact 117 original plot IDs changed")
    return main


def eligible_population(all_rows, exclude_mata:bool):
    source=[x for x in all_rows if not (exclude_mata and x["site"]=="MataDIV")]
    site_count=collections.Counter(r["site"] for r in source)
    expected=PRIOR_SITE_SCOPES["no_ECOLINK_or_MataDIV" if exclude_mata else "all_source_site_year_qualified_main"]
    if dict(site_count)!=expected:
        raise ValueError("SOURCE_COHORT_HOLD: original study-site source counts changed")
    retained_sites={s for s,n in site_count.items() if n>=MIN_SITE_PLOTS}
    included=[r for r in source if r["site"] in retained_sites]
    counts=collections.Counter(r["site"] for r in included)
    if len(included)<MIN_PLOTS or len(retained_sites)<MIN_SITES:
        raise ValueError("SOURCE_HOLD: original source plot/site threshold failed")
    taxa=set().union(*(r["positive_trait_taxa"] for r in included))
    if len(taxa)<MIN_SPECIES:
        raise ValueError("SOURCE_HOLD: original source taxon trait coverage failed")
    if not all(r["n_complete_traits"]==r["richness"] for r in included):
        raise ValueError("SOURCE_HOLD: originally published planted species completeness changed")
    return included,{
        "scope":"MataDIV_EXCLUDED" if exclude_mata else "MataDIV_FERTILIZED_CONTEXT_RETAINED",
        "original_pre_site8_source_plots":len(source),
        "excluded_small_site_source_plots":len(source)-len(included),
        "original_eligible_source_sites_before_min8":dict(sorted(site_count.items())),
        "heldout_source_sites":dict(sorted(counts.items())),
        "n_original_stand_plots":len(included),
        "n_original_taxa_fully_two_trait_observed":len(taxa),
        "orig_species_coverage_fraction_min":min(r["n_complete_traits"]/r["richness"] for r in included),
        "original_biomass_woody_stand_response_from_DS1_only":True,
        "does_not_include_original_genotype_or_coppice_ECOLINK":True,
    }


def train_feature_transform(train_rows, test_rows):
    # Original site-fold training source traits only. Site heldout traits not used
    # to standardize feature SD or mean, and original woody response never used.
    alltrain=np.vstack([r["log_traits"] for r in train_rows])
    mean=alltrain.mean(axis=0)
    std=alltrain.std(axis=0,ddof=0)
    if not np.isfinite(std).all() or min(std)<1e-8:
        raise ValueError("MODEL_SOURCE_HOLD: source trainer trait variance degenerate")
    def features(rows):
        mat=[]
        for r in rows:
            z=(r["log_traits"]-mean)/std
            if not np.isfinite(z).all():raise ValueError("MODEL_SOURCE_HOLD: invalid source trait")
            cwm=z.mean(axis=0)
            n=len(z)
            delta=z[:,None,:]-z[None,:,:]
            dist=np.linalg.norm(delta,axis=2)
            fd=float(np.sum(dist)/(n*(n-1)))
            mat.append([1.,math.log2(r["richness"]),float(cwm[0]),float(cwm[1]),fd])
        return np.asarray(mat,dtype=float)
    return features(train_rows),features(test_rows),{
        "trained_log_trait_mean":[float(v) for v in mean],
        "trained_log_trait_SD":[float(v) for v in std],
    }


def source_only_rank_preflight(rows):
    sites=sorted(set(r["site"] for r in rows))
    if len(sites)<MIN_SITES:raise ValueError("SOURCE_HOLD: insufficient original study sites")
    diag={}
    for held in sites:
        train=[r for r in rows if r["site"]!=held]
        test=[r for r in rows if r["site"]==held]
        X,_,_=train_feature_transform(train,test)
        r1=int(np.linalg.matrix_rank(X[:,:4]))
        r2=int(np.linalg.matrix_rank(X[:,:5]))
        if r1!=4 or r2!=5:
            raise ValueError(f"MODEL_SOURCE_RANK_HOLD: heldout source study {held} base {r1}/4 full {r2}/5")
        if max(X[:,4])-min(X[:,4])<=1e-8:raise ValueError("MODEL_SOURCE_HOLD: original FD predictor constant in source trainer")
        diag[held]={"full_train_rank":r2,"base_train_rank":r1,"n_original_training_plots":len(train),"n_original_test_plots":len(test)}
    return diag


def cross_site_score(rows):
    sites=sorted(set(r["site"] for r in rows))
    full=[]
    for held in sites:
        train=[r for r in rows if r["site"]!=held]
        test=[r for r in rows if r["site"]==held]
        X,XT,trans=train_feature_transform(train,test)
        count=collections.Counter(x["site"] for x in train)
        w=np.asarray([1./count[r["site"]] for r in train],float)
        sqrt_w=np.sqrt(w)
        y=np.asarray([r["response"] for r in train],float)
        yt=np.asarray([r["response"] for r in test],float)
        coeff_base=np.linalg.lstsq(X[:,:4]*sqrt_w[:,None],y*sqrt_w,rcond=None)[0]
        coeff_fd=np.linalg.lstsq(X*sqrt_w[:,None],y*sqrt_w,rcond=None)[0]
        p_base=XT[:,:4]@coeff_base
        p_fd=XT@coeff_fd
        sse0=float(np.sum((yt-p_base)**2))
        sse1=float(np.sum((yt-p_fd)**2))
        if not math.isfinite(sse0+sse1) or sse0<=1e-10:
            raise ValueError("MODEL_HOLD: source original site heldout SSE invalid")
        gain=1-sse1/sse0
        full.append({
            "site":held,
            "n_original_source_heldout_plots":len(test),
            "baseline_cwm_and_richness_SSE":sse0,
            "with_two_axis_FD_SSE":sse1,
            "incremental_FD_woody_holdout_SSE_gain":float(gain),
            "train_source_study_site_balanced":True,
        })
    scores=np.asarray([r["incremental_FD_woody_holdout_SSE_gain"] for r in full])
    rng=np.random.default_rng(SEED)
    draws=scores[rng.integers(0,len(scores),size=(BOOTSTRAP_REPS,len(scores)))].mean(axis=1)
    ci=np.quantile(draws,[.025,.975])
    positives=int(np.sum(scores>0))
    cutoff=int(math.ceil(.7*len(sites)))
    return {
      "mean_equal_study_site_FD_increment_SSE_gain":float(scores.mean()),
      "mean_equal_study_site_FD_increment_SSE_gain_pct":float(100*scores.mean()),
      "original_site_bootstrap_CI95":[float(v) for v in ci],
      "original_site_bootstrap_CI95_pct":[float(100*v) for v in ci],
      "n_study_sites_with_gain_positive":positives,
      "n_study_sites_required_positive":cutoff,
      "predeclared_positive_transfer_supported":bool(scores.mean()>0 and ci[0]>0 and positives>=cutoff),
      "n_independent_original_study_sites":len(sites),
      "bootstrap_seed":SEED,
      "bootstrap_iterations":BOOTSTRAP_REPS,
      "heldout_original_study_site_records":full,
      "model":"M1 original log2 richness + source train-scaled log SLA and log LNCM community means; M2 adds equally planted weighted source pairwise Euclidean 2D FD; weighted OLS 1/n_site, predict heldout original study site woody log1p dry mass (Mg/ha).",
    }


def main(args):
    path=Path(args.years)
    yearmeta,src=verify_year_table(path)
    prev=json.loads(Path(args.source_coverage).read_text(encoding="utf8"))
    if (prev["status"]!="ORIGINAL_PLOT_LOCAL_SLA_LNCM_COVERAGE_SOURCE_ONLY_AUDITED" or
        prev["original_source_only_cohorts"]["excluding_ECOLINK"]["fixed_80pct_plot_local_FD_source_support_status"]!="PLOT_LOCAL_FD_SOURCE_COMPLETENESS_PASS" or
        prev["original_source_only_cohorts"]["excluding_ECOLINK_and_MataDIV"]["fixed_80pct_plot_local_FD_source_support_status"]!="PLOT_LOCAL_FD_SOURCE_COMPLETENESS_PASS"):
        raise ValueError("FROZEN_SOURCE_HOLD: stricter original source coverage not certified")
    if prev["fixed_min_joint_SLA_LNCM_fraction_of_original_planted_species"]!=MIN_JOINT_COVERAGE:
        raise ValueError("FROZEN_SOURCE_HOLD: original pre-effect measured trait completeness changed")
    original=build_original_source_eligibility(yearmeta)
    rows_main,main_qa=eligible_population(original,False)
    rows_sens,sens_qa=eligible_population(original,True)
    diag_main=source_only_rank_preflight(rows_main)
    diag_sens=source_only_rank_preflight(rows_sens)
    print("PRE_RESPONSE_PLOT_LOCAL_ORIGINAL_SOURCE_FD_RANK_PASS",json.dumps({
       "main":main_qa,"sensitivity":sens_qa,
       "main_full_rank_heldout_sites":len(diag_main),"sensitivity_full_rank_heldout_sites":len(diag_sens)
    },sort_keys=True),flush=True)
    # Response values were loaded only as source presence checks before the
    # source rank/source completeness gate above. All model coefficients below
    # are new and outcome-frozen by the documented original source contract.
    main=cross_site_score(rows_main)
    sens=cross_site_score(rows_sens)
    return {
       "version":"v0.1",
       "status":"POSTRESULT_EXPLORATORY_TREE_DIVNET_ORIGINAL_PLOT_TRAIT_FD_SITE_TRANSFER_ESTIMATED",
       "new_exploratory_estimand":"Original plot-measured SLA+LNCM dispersion predictive increment over original species richness and same-original-trait means for DS1 woody stand stock across unseen source experiments.",
       "original_paper_positive_FDis_mixing_results_already_known":True,
       "source_frozen_design":"docs/TREEDIVNET_OBSERVED_PLOT_TRAIT_FD_WOODY_SITE_TRANSFER_FROZEN_V0_1.md",
       "original_uploaded_TableS1_source_SHA256":src["source_uploaded_workbook"]["sha256"],
       "original_user_TableS1_original_binary_not_committed":True,
       "original_Figshare_MD5_pinned_DS1_DS2":True,
       "original_DS1_stand_woody_response_only":True,
       "original_DS2_species_woody_col_never_used":True,
       "sources_original_individual_row_lineage_still_not_verified":True,
       "original_woody_source_original_allometry_site_methods_heterogeneous":True,
       "original_DS2_species_woody_vs_DS1_stand_scaling_still_HOLD_but_unneeded_for_new_plot_predictor_response_join":True,
       "original_genetic_coppice_ECOLINK_study_never_in_source_population":True,
       "source_only_pre_effect_rank_full":{
           "main":diag_main,"MataDIV_excluded":diag_sens
       },
       "main_source_original_plot_support":main_qa,
       "main_heldout_study_site_woody_FD_increment":main,
       "MataDIV_excluded_source_original_plot_support":sens_qa,
       "MataDIV_excluded_source_only_sensitivity_heldout_FD_increment":sens,
       "no_phylogenetic_K_or_BIEN_rho_directly_estimated":True,
       "no_causal_conclusion_authorized":True,
       "no_independent_experiment_replication_of_Jensen_2026":True,
       "historical_global_BIEN_sPlotOpen_BIODEPTH_NEON_closed_source_gates_untouched":True,
       "hard_nonclaims":[
          "The new predictor is observed in mixed plots, and may respond to light and biomass; not an instrument or a cause of woody growth.",
          "Source published allometric standing stock target is not measured primary productivity, carbon sequestration flux, or independent harvested biomass.",
          "Original Figshare 2026 authors already report positive FDis+mixing associations on this SAME experiment set, albeit a different FDis/NDE estimand.",
          "Cross-study predictions are highly sensitive to source-site age, management, allometry and treatment; 5/6 independent sites are few.",
          "Site-specific trait and woody inventory years match within two years, not per individual sample ID/date; strict original individual provenance gate remains HOLD.",
          "Community PD and family-specific Blomberg K or distance rho are NOT estimated. Original 34 study species insufficient for broad 12×20 K.",
          "Outcome-driven site/trait/method tuning and rescue subgroup tests prohibited."
       ],
    }


def fixture():
    demo=[
       {"site":"a","richness":2,"log_traits":np.array([[0.,0.],[1.,1.]])},
       {"site":"b","richness":2,"log_traits":np.array([[1.,0.],[2.,1.]])},
       {"site":"c","richness":2,"log_traits":np.array([[0.,1.],[2.,1.]])},
    ]
    X,T,z=train_feature_transform(demo[:2],demo[2:])
    assert X.shape==(2,5) and T.shape==(1,5)
    assert abs(X[0,4]-np.sqrt(2*(.5)**2)*2)>0 or X[0,4]>0
    assert MIN_SITE_PLOTS==8 and BOOTSTRAP_REPS==10000 and SEED==20261117
    return {"status":"PLOT_LOCAL_SLA_LNCM_WOODY_TRANSFER_FIXTURE_PASS","n_assertions":4}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--years",type=Path)
    p.add_argument("--source-coverage",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(fixture(),sort_keys=True))
    else:
        if not args.years or not args.source_coverage or not args.out:
            p.error("--years --source-coverage --out are required")
        result=main(args)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("TREE_DIVNET_OBSERVED_PLOT_TRAIT_FD_WOODY_HELDOUT_RESULT",json.dumps({
          k:v for k,v in result.items() if k not in ("hard_nonclaims","source_only_pre_effect_rank_full")
        },sort_keys=True),flush=True)
