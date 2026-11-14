#!/usr/bin/env python3
"""Frozen independent Jena 2003 group-richness / measured dry biomass pilot.

Uses 82 *plot means*, not 820 raw rows. No phylogenetic MPD or Rao FD.
Requires original source byte hashes and tier1 group metadata gate.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from pathlib import Path
from collections import defaultdict
import numpy as np
import statsmodels.api as sm
from probe_jena_2003_direct_biomass_v0_1 import parse_table

SOURCE_SHA="70606a050293b34e0cacc3311e10980a2e640cea29703dc8b7fbb4306aa67079"
PLOTINFO_SHA="7b7f1af497959a77a5ddefea5148b8d784b5d1b50a19f2925f9353426a83da70"
BIOMASS_COL="Sown plant biom dw [g/m**2]"
SEED=20261114
B=2000

def read(source,plotinfo,tier1):
    data=Path(source).read_bytes()
    infodata=Path(plotinfo).read_bytes()
    if hashlib.sha256(data).hexdigest()!=SOURCE_SHA:raise ValueError("PANGAEA_2003_SHA_MISMATCH")
    if hashlib.sha256(infodata).hexdigest()!=PLOTINFO_SHA:raise ValueError("PLOTINFO_SHA_MISMATCH")
    q=json.loads(Path(tier1).read_text(encoding="utf-8"))
    if q["status"]!="TIER1_JENA_GROUP_DESIGN_PASS" or q["plot_functional_group_sowing_mask_agreement_fraction"]<.95:
        raise ValueError("TIER1_JENA_SOURCE_GATE_NOT_PASS")
    if q["source_2003_sha256"]!=SOURCE_SHA or q["plotinfo_sha256"]!=PLOTINFO_SHA:
        raise ValueError("TIER1_SOURCE_IDENTITY_MISMATCH")
    cols,raw,_=parse_table(data)
    if BIOMASS_COL not in cols or len(raw)!=820:
        raise ValueError("UNEXPECTED_BIOMASS_FORMAT")
    info=list(csv.DictReader(io.StringIO(infodata.decode("utf-8-sig")),delimiter="\t"))
    meta={r["plotcode"].strip():r for r in info}
    if len(meta)!=82:raise ValueError("PLOTINFO_ID_DUPLICATE_OR_MISSING")
    means={}
    for row in raw:
        if row["Repl"].strip()!="mean":continue
        plot=row["Experimental plot"].strip()
        month=row["Date/time start"].strip()[:7]
        key=(plot,month)
        if key in means:raise ValueError("MEAN_DUPLICATE_PLOT_MONTH")
        try: value=float(row[BIOMASS_COL])
        except ValueError:raise ValueError("INVALID_NUMERIC_MEAN")
        if not np.isfinite(value) or value<0 or value==-9999:
            raise ValueError("MISSING_NEGATIVE_PLOT_DRY_BIOMASS")
        means[key]=value
    if len(means)!=164 or {i for i,j in means}!=set(meta):
        raise ValueError("MISSING_PLOT_MONTH_MEANS")
    if sum(j=="2003-05" for _,j in means)!=82 or sum(j=="2003-08" for _,j in means)!=82:
        raise ValueError("UNEXPECTED_CAMPAIGNS")
    blocks=sorted({x["block"] for x in info})
    if len(blocks)!=4:raise ValueError("NOT_FOUR_BLOCKS")
    rows=[]
    for p in sorted(meta):
        r=meta[p]
        row={
            "plot":p, "block":r["block"],
            "richness":int(r["NumberSownSpecies"]),
            "fg":int(r["NumberFunctionalGroups"]),
            "legumes":int(r["PresenceLegumes"]),
            "may":means[(p,"2003-05")], "aug":means[(p,"2003-08")],
        }
        rows.append(row)
    if len(rows)!=82 or {x["richness"] for x in rows}!={1,2,4,8,16,60} or {x["fg"] for x in rows}!={1,2,3,4}:
        raise ValueError("INVALID_FROZEN_DESIGN_DISTRIBUTION")
    return rows,blocks

def Xmatrix(rows,blocks,include_fg=True,include_legumes=False,include_block=True):
    values=[[1.0,math.log2(r["richness"])] for r in rows]
    names=["intercept","log2_sown_richness"]
    if include_fg:
        for a,r in zip(values,rows):a.append(float(r["fg"]))
        names.append("functional_group_richness")
    if include_legumes:
        for a,r in zip(values,rows):a.append(float(r["legumes"]))
        names.append("legumes_present")
    if include_block:
        for b in blocks[1:]:
            for a,r in zip(values,rows):a.append(float(r["block"]==b))
            names.append("block_"+b)
    return np.asarray(values,dtype=float),names

def fit(rows,blocks,month="may",include_fg=True,include_legumes=False,include_block=True):
    x,names=Xmatrix(rows,blocks,include_fg,include_legumes,include_block)
    y=np.log1p(np.asarray([r[month] for r in rows],dtype=float))
    if not np.all(np.isfinite(y)) or np.linalg.matrix_rank(x)!=x.shape[1]:
        raise ValueError("DESIGN_RANK_OR_RESPONSE_INVALID")
    model=sm.OLS(y,x).fit(cov_type="HC3")
    idx=names.index("functional_group_richness") if include_fg else None
    result={
        "n_plots":len(rows),
        "predictors":names,
        "response":"log1p measured sown aboveground dry mass g/m^2",
        "r2_in_sample":float(model.rsquared),
        "aic_descriptive":float(model.aic),
        "model_condition_number":float(np.linalg.cond(x)),
    }
    if idx is not None:
        effect=float(model.params[idx]);ci=model.conf_int(alpha=.05)[idx]
        result["functional_group_beta"]=effect
        result["functional_group_HC3_SE"]=float(model.bse[idx])
        result["functional_group_HC3_p_two_sided"]=float(model.pvalues[idx])
        result["functional_group_HC3_ci95"]=[float(ci[0]),float(ci[1])]
        result["approx_percent_change_in_one_plus_biomass_per_FG"]=float((math.exp(effect)-1)*100)
    return result

def boot(rows,blocks):
    rng=np.random.default_rng(SEED)
    byblock={b:[i for i,r in enumerate(rows) if r["block"]==b] for b in blocks}
    original_x,names=Xmatrix(rows,blocks)
    y=np.log1p(np.array([r["may"] for r in rows],dtype=float))
    fg_index=names.index("functional_group_richness")
    est=[]
    invalid=0
    for i in range(B):
        ids=np.concatenate([
            rng.choice(ix,size=len(ix),replace=True) for ix in byblock.values()
        ])
        x=original_x[ids]
        if np.linalg.matrix_rank(x)!=x.shape[1]:
            invalid+=1
            continue
        coeff=np.linalg.lstsq(x,y[ids],rcond=None)[0]
        est.append(coeff[fg_index])
    if len(est)<1900:raise ValueError("BOOTSTRAP_LESS_THAN_95_PERCENT_VALID")
    return {"replicates_planned":B,"replicates_valid":len(est),
            "replicates_singular":invalid,"seed":SEED,
            "plot_stratified_within_original_blocks":True,
            "beta_ci95_percentile":[float(np.percentile(est,2.5)),float(np.percentile(est,97.5))]}

def cross_validation(rows,blocks):
    y=np.log1p(np.asarray([r["may"] for r in rows],dtype=float))
    obs=[];p0=[];p1=[]
    for held in blocks:
        tr=[r for r in rows if r["block"]!=held]
        te=[r for r in rows if r["block"]==held]
        for fg,dest in [(False,p0),(True,p1)]:
            xtr,_=Xmatrix(tr,blocks,fg,include_block=False)
            xte,_=Xmatrix(te,blocks,fg,include_block=False)
            if np.linalg.matrix_rank(xtr)!=xtr.shape[1]:
                raise ValueError("CV_FOLD_TRAIN_RANK_FAIL")
            beta=np.linalg.lstsq(xtr,np.log1p(np.asarray([r["may"] for r in tr])),rcond=None)[0]
            dest.extend((xte@beta).tolist())
        obs.extend([math.log1p(r["may"]) for r in te])
    q=np.asarray(obs);sse0=float(np.sum((q-np.asarray(p0))**2));sse1=float(np.sum((q-np.asarray(p1))**2))
    if sse0<=0:raise ValueError("BASELINE_CV_ERROR_DEGENERATE")
    return {"heldout_group":"whole Jena experimental block",
            "number_blocks":len(blocks),"heldout_plot_predictions_once":len(obs),
            "block_fixed_effects_omitted_from_both_cv_models":True,
            "gain_1_minus_full_over_baseline_SSE":1-sse1/sse0,
            "sse_baseline":sse0,"sse_functional_groups":sse1}

def analyse(rows,blocks):
    baseline=fit(rows,blocks,include_fg=False)
    main=fit(rows,blocks)
    b=boot(rows,blocks)
    cv=cross_validation(rows,blocks)
    august=fit(rows,blocks,month="aug")
    no_60=fit([r for r in rows if r["richness"]!=60],blocks)
    legume=fit(rows,blocks,include_legumes=True)
    positive=(main["functional_group_beta"]>0
        and b["beta_ci95_percentile"][0]>0
        and main["functional_group_HC3_p_two_sided"]<.05)
    return {
      "version":"v0.1","status":"JENA_2003_INDEPENDENT_GROUP_RICHNESS_BIOMASS_SENTINEL_ESTIMATED",
      "primary_scope":"Single randomized Jena site, 82 plot means, May 2003, g/m^2 directly dried standing vegetation",
      "base_sha256":SOURCE_SHA,"plotinfo_sha256":PLOTINFO_SHA,
      "n_plots":82,"n_plots_with_may_and_aug_mean":82,
      "response":"log1p(May 2003 sown aboveground standing dry mass in g/m^2)",
      "baseline_log_richness_plus_block":baseline,"full_plus_planned_functional_group_richness":main,
      "block_stratified_plot_bootstrap":b,
      "leave_one_block_out_prediction":cv,
      "primary_positive_support_criterion_pass":bool(positive),
      "secondary_august":august,"secondary_exclude_whole_pool_60_species":no_60,
      "secondary_adjust_legume_group_presence":legume,
      "hard_nonclaims":[
        "Functional-group richness is a coarse planned sowing-design diversity metric, not multi-axis trait FD, hypervolume or Rao Q.",
        "Standing dry mass after harvest is not net primary production or all plant-root biomass.",
        "The original 201-system BIEN PD–FD source gate remains HOLD, no evolutionary memory tested here.",
        "Inference is within one Jena grassland field experiment and cannot establish a global/multiple-family macroecological relationship.",
        "The four sampled blocks are few; HC3 and within-block bootstrap do not create four independent regions.",
        "Legume-presence adjustment is an exploratory alternative functional identity check, not a causal mediation estimate."
      ]}
def synthetic_test():
    # Deterministic design-check logic only, not a synthetic biological result.
    demo=[{"plot":str(i),"block":"B"+str(i%4),"richness":2**(i%4),
           "fg":1+(i%3),"legumes":int(i%2==0),"may":float(i+1),"aug":float(i+2)}
          for i in range(24)]
    x,n=Xmatrix(demo,["B0","B1","B2","B3"])
    assert x.shape==(24,6) and len(n)==6
    assert np.linalg.matrix_rank(x)==6
    assert all(x[:,0]==1)
    return {"status":"JENA_EFFECT_CODE_FIXTURE_PASS","checks":3}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source");p.add_argument("--plotinfo")
    p.add_argument("--tier1");p.add_argument("--out");p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:print(json.dumps(synthetic_test()))
    else:
        if not all((a.source,a.plotinfo,a.tier1,a.out)):
            p.error("--source --plotinfo --tier1 --out required")
        rows,blocks=read(a.source,a.plotinfo,a.tier1)
        result=analyse(rows,blocks)
        out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
        print("JENA_GROUP_BIOMASS_EFFECT",json.dumps(result,ensure_ascii=False))
