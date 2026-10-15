#!/usr/bin/env python3
"""Post-760-result descriptive same-tip K rank reversal sensitivity.

Reads the COMPLETE original 24 validated 760 family×trait pair simulations,
re-matches them to source-only pair eligibility (before any original K outcome
selection), and estimates reversal versus original absolute K contrast and
shared taxon fraction. Families are the unit of resampling (42 clusters).

This is NOT a new process null, external validation, trait-specific
evolutionary rate, or new pre-outcome prediction. Bins/models are exploratory.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

STATUS="AUSTRAITS_K_SHARED_TIP_MARGIN_COVERAGE_EXPLORATORY_AUDITED"
INPUT="AUSTRAITS_K_SHARED_TAXON_PAIR_BATCH_REESTIMATED"
SUPPORT="AUSTRAITS_K_SHARED_TAXON_PAIR_SUPPORT_AUDITED"
EXPECTED={"S3":(760,609,151),"prune_only":(747,610,137)}
AXES=("S3","prune_only")
FIVE={"seed_width","seed_dry_mass","leaf_width","leaf_area","petiole_length"}


def load_rows(source_support,outputs,design):
    if design.get("status")!="POST_760_MATCHED_K_OUTCOME_EXPLORATORY_MARGIN_AND_SUPPORT_AUDIT":
        raise ValueError("post-outcome marginal robustness rules not archived")
    if source_support.get("status")!=SUPPORT or source_support.get("qualifying_family_trait_pairs")!=760:
        raise ValueError("not the original source-blind 760 eligible graph")
    if source_support.get("original_graph")!={"systems":254,"families":42,"traits":13}:
        raise ValueError("original 254 K system cohort changed")
    if len(source_support.get("trait_pairs",{}))!=66:
        raise ValueError("incomplete 66-pair source support")
    expected={(v["family"],v["trait_A"],v["trait_B"]):v
              for v in source_support["family_trait_pair_support"]
              if v["qualifies_20_common_species"]}
    if len(expected)!=760:raise ValueError("missing fixed 760 family-pair identities")
    if len(outputs)!=24:raise ValueError("not 24 original archived K batches")
    seen=set()
    rows=[]
    for batch in outputs:
        if batch.get("status")!=INPUT or not batch.get("post_original_K_outcome_exploratory"):
            raise ValueError("unexpected simulation provenance")
        if len(batch["pairs"])!=batch.get("n_family_trait_pairs"):
            raise ValueError("incomplete K batch outcome")
        for q in batch["pairs"]:
            fam,a,b=q["family"],q["trait_A"],q["trait_B"]
            key=(fam,a,b)
            if key in seen or key not in expected:
                raise ValueError("duplicate or unexpected original pair K")
            seen.add(key)
            ref=expected[key]
            if (q["system_A"],q["system_B"],q["n_shared_species"])!=(
               ref["system_A"],ref["system_B"],ref["n_common_species_same_genus"]):
                raise ValueError("original shared-species identity changed")
            ns=int(q["n_shared_species"])
            na=int(ref["n_original_A"]);nb=int(ref["n_original_B"])
            if min(ns,na,nb)<20 or ns>min(na,nb):
                raise ValueError("impossible original same-tip support")
            for axis in AXES:
                d=q["axes"][axis]
                if d["status"]=="PASS":
                    if d["n_tips"]<20 or d["n_tips"]>ns:
                        raise ValueError("bad matched original tree tip support")
                    vals=[d[x] for x in ("K_A","K_B","delta_shared_logK",
                              "delta_original_logK","delta_support_shift")]
                    if not all(math.isfinite(float(v)) for v in vals):
                        raise ValueError("nonfinite paired source K")
                    K_A,K_B,shared,original,shift=map(float,vals)
                    if K_A<=0 or K_B<=0 or not math.isclose(
                       math.log(K_A/K_B),shared,abs_tol=2e-9):
                        raise ValueError("nonmatching phylogenetic K ratio")
                    if not math.isclose(shared-original,shift,abs_tol=2e-9):
                        raise ValueError("wrong source-vs-tip change")
                    rows.append({
                        "family":fam,"trait_A":a,"trait_B":b,"axis":axis,
                        "n_shared":ns,"n_tips":int(d["n_tips"]),
                        "n_original_A":na,"n_original_B":nb,
                        "frac_small":ns/min(na,nb),"frac_large":ns/max(na,nb),
                        "orig":original,"matched":shared,"shift":shift,
                        "abs_orig":abs(original),"abs_shift":abs(shift),
                        "flip":int(original*shared<0)})
                elif not str(d["status"]).startswith("HOLD_"):
                    raise ValueError("unexpected native tree decision")
    if seen!=set(expected):
        raise ValueError("missing archived family×trait K pair outcomes")
    data=pd.DataFrame(rows)
    if data.family.nunique()!=42:raise ValueError("family cluster graph mutated")
    for axis,(n,agree,flip) in EXPECTED.items():
        g=data[data.axis==axis]
        if len(g)!=n or int(g.flip.sum())!=flip or n-flip!=agree:
            raise ValueError("does not reproduce original official K flip counts")
    return data


def family_bootstrap(g,group_id,resampling_draws,rng,mask):
    fams=sorted(g.family.unique())
    counts=np.zeros((len(fams),2),float)
    for i,f in enumerate(fams):
        q=g[(g.family==f)&mask]
        counts[i]=[q.flip.sum(),len(q)]
    if not len(counts) or not counts[:,1].sum():
        return None
    idx=rng.integers(len(fams),size=(resampling_draws,len(fams)))
    draw=counts[idx].sum(axis=1)
    valid=draw[:,1]>0
    if np.mean(valid)<.99:
        raise ValueError("unstable bootstrap denominator for pre-archived stratum")
    samples=draw[valid,0]/draw[valid,1]
    return {"pair_weighted_rate":float(counts[:,0].sum()/counts[:,1].sum()),
            "family_cluster_bootstrap_q025":float(np.quantile(samples,.025)),
            "family_cluster_bootstrap_q975":float(np.quantile(samples,.975)),
            "n_pairs":int(counts[:,1].sum()),
            "n_flips":int(counts[:,0].sum()),
            "n_families_represented":int((counts[:,1]>0).sum())}


def audit_axis(g,design,rng):
    fams=sorted(g.family.unique())
    B=design["uncertainty"]["cluster_resampling_draws"]
    if B!=5000 or len(fams)!=42:raise ValueError("post-outcome uncertainty configuration changed")
    g=g.copy()
    g["absent_large"]=1-g["frac_large"]
    g["log_n"]=np.log(g["n_shared"])
    g["traitpair"]=g.trait_A+"__"+g.trait_B
    overall=family_bootstrap(g,"family",B,rng,np.ones(len(g),dtype=bool))
    fam_stats=g.groupby("family").flip.agg(["mean","size"])
    ids=rng.integers(0,len(fams),size=(B,len(fams)))
    fam_rate=fam_stats.reindex(fams)["mean"].to_numpy(float)
    famboots=fam_rate[ids].mean(axis=1)
    overall["equal_family_rate"]=float(fam_rate.mean())
    overall["equal_family_bootstrap_q025"]=float(np.quantile(famboots,.025))
    overall["equal_family_bootstrap_q975"]=float(np.quantile(famboots,.975))
    out={"total":overall,"strata":{}}
    for label,variable,edges in (
        ("original_abs_logK","abs_orig",design["exploratory_strata"]["original_abs_logK_edges"]),
        ("shared_fraction_larger","frac_large",design["exploratory_strata"]["fraction_of_larger_original_cohort_edges"]),
        ("n_shared_species","n_shared",design["exploratory_strata"]["common_species_count_edges"])):
        boundaries=[float("inf") if x is None else float(x) for x in edges]
        if boundaries!=sorted(boundaries):
            raise ValueError("nonordered frozen descriptive margin bins")
        out["strata"][label]=[]
        for lo,hi in zip(boundaries[:-1],boundaries[1:]):
            q=(g[variable].to_numpy()>=lo)&(g[variable].to_numpy()<hi)
            z=family_bootstrap(g,"family",B,rng,q)
            if z is None:raise ValueError("empty frozen descriptive bin")
            z["low_inclusive"]=lo
            z["high_exclusive"]=hi if math.isfinite(hi) else None
            out["strata"][label].append(z)

    # GEE treats comparisons within a family as dependent. Its coefficients
    # are *exploratory associations*, not adjusted causal effects.
    formula="flip ~ abs_orig + absent_large + log_n"
    fit=smf.gee(formula,groups="family",data=g,family=sm.families.Binomial(),
                cov_struct=sm.cov_struct.Exchangeable()).fit()
    parameters={}
    for p in ("abs_orig","absent_large","log_n"):
        if not (np.isfinite(fit.params[p]) and np.isfinite(fit.bse[p])):
            raise ValueError("nonfinite GEE estimate")
        lo,hi=fit.conf_int().loc[p]
        parameters[p]={"coefficient":float(fit.params[p]),
                       "robust_se":float(fit.bse[p]),
                       "ci95":list(map(float,(lo,hi))),
                       "exploratory_p":float(fit.pvalues[p])}
    z=parameters["absent_large"]
    z["odds_ratio_per_10_percentage_points_missing_from_larger_cohort"]=float(math.exp(z["coefficient"]*.1))
    z["odds_ratio_ci95_per_10pp"]=list(map(float,np.exp(np.asarray(z["ci95"])*.1)))
    out["adjusted_exploratory_gee"]=parameters

    # Sensitivity to confounding by family and named-trait-pair identity.
    # A family FE model may weaken an association seen between families;
    # report this even if it disagrees with the simpler GEE.
    fit2=smf.ols(formula+" + C(family) + C(traitpair)",data=g).fit(
          cov_type="cluster",cov_kwds={"groups":g.family},use_t=True)
    out["within_family_and_named_pair_fixed_effects_linear_probability"]={
        p:{"coefficient":float(fit2.params[p]),
           "family_cluster_se":float(fit2.bse[p]),
           "exploratory_p":float(fit2.pvalues[p])}
         for p in ("abs_orig","absent_large","log_n")}
    return out


def run(support,batches,design):
    data=load_rows(support,batches,design)
    rng=np.random.default_rng(design["uncertainty"]["seed"])
    out={"version":"v0.1","status":STATUS,
         "source_support_graph":{"systems":249,"families":42,
                                 "trait_pair_types":66,"eligible_family_trait_pairs":760},
         "axes":{},"post_outcome_exploratory":True,
         "original_equal_BM_OU_source_decision_not_modified":True,
         "no_Try_independent_validation":True,
         "no_species_or_trait_values_persisted":True,
         "hard_nonclaims":[
           "Original K contrast size is mathematically related to the sign-flip threshold; a negative margin association is not an identified evolutionary mechanism.",
           "Higher taxon overlap associates with sign stability but cannot be interpreted as a causal intervention or a source-quality correction.",
           "Family-clustered associations may differ when explicit family and trait-pair fixed effects are used.",
           "The 760 pairs share only 42 families and distinct pair-specific taxa: this is not a global transitive 12-trait ranking.",
           "The five focal signed deviations are post-AusTraits discovery and lack independent external TRY v7 measurement validation."]}
    for axis in AXES:
        g=data[data.axis==axis]
        out["axes"][axis]=audit_axis(g,design,rng)
    a=data[data.axis=="S3"].set_index(["family","trait_A","trait_B"])
    b=data[data.axis=="prune_only"].set_index(["family","trait_A","trait_B"])
    both=a.join(b,lsuffix="_S3",rsuffix="_prune",how="inner")
    if len(both)!=747:
        raise ValueError("prune valid pairs not subset of S3 valid original graph")
    out["both_axes"]={
      "paired_family_trait_pairs":len(both),
      "n_reversed_in_both":int(((both.flip_S3==1)&(both.flip_prune==1)).sum()),
      "n_reversed_in_S3_only":int(((both.flip_S3==1)&(both.flip_prune==0)).sum()),
      "n_reversed_in_prune_only":int(((both.flip_S3==0)&(both.flip_prune==1)).sum()),
      "n_stable_in_both":int(((both.flip_S3==0)&(both.flip_prune==0)).sum())
    }
    return out


def main():
    p=argparse.ArgumentParser()
    for flag in ("support","batch-dir","design","out"):
        p.add_argument("--"+flag,required=True,type=Path)
    a=p.parse_args()
    batches=[]
    for path in sorted(a.__dict__["batch_dir"].glob("*.json")):
        batches.append(json.loads(path.read_text()))
    result=run(json.loads(a.support.read_text()),batches,json.loads(a.design.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,"overall":{
         axis:{"n":result["axes"][axis]["total"]["n_pairs"],
               "reversals":result["axes"][axis]["total"]["n_flips"],
               "equal_family_rate":result["axes"][axis]["total"]["equal_family_rate"]}
          for axis in AXES}},sort_keys=True))

if __name__=="__main__":
    main()
