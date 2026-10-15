#!/usr/bin/env python3
"""Post-outcome ecological module K and leave-ONE-FAMILY-out prediction audit.

Data: ALL 24 immutable K outputs from matched identical species and trees,
validated against the frozen source-only 760-pair graph. Never pool within
family correlated pairs as independent biological evolutionary replicates.

Reproductive seed/fruit traits vs vegetative leaf/plant-height morphology;
all scientific interpretations are exploratory. Does not reopen BM/OU null,
the 201-system BIEN rho project, or imply TRY v7 source independence.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from audit_austraits_k_shared_tip_margin_sensitivity_v0_1 import load_rows

STATUS="AUSTRAITS_K_REPRODUCTIVE_VEGETATIVE_LOFO_EXPLORATORY_V0_1"
EXPECTED={"S3":760,"prune_only":747}

def source_data(support,batches,design,source_margin_design):
    if design.get("status")!="POST_760_K_OUTCOMES_FUNCTIONAL_MODULE_EXPLORATORY_AUDIT_FROZEN_BEFORE_NEW_RESULTS":
        raise ValueError("functional grouping was not frozen for this post-outcome analysis")
    if not design["hard_nonclaims"]:
        raise ValueError("missing exploratory nonclaims")
    a=set(design["fixed_organ_classes"]["reproductive"])
    b=set(design["fixed_organ_classes"]["vegetative"])
    if len(a)!=6 or len(b)!=6 or a&b or "seed_height" in a|b:
        raise ValueError("wrong functional class categories")
    traits={x for r in support["family_trait_pair_support"] for x in (r["trait_A"],r["trait_B"])}
    if a|b!=traits or len(traits)!=12:
        raise ValueError("module names do not match original 12-trait source graph")
    data=load_rows(support,batches,source_margin_design)
    data=data.copy()
    data["repro_A"]=data.trait_A.isin(a)
    data["repro_B"]=data.trait_B.isin(a)
    data["intermodule"]=data.repro_A!=data.repro_B
    data["repro_wins"]=np.where(
       data.repro_A,data.matched>0,data.matched<0).astype(int)
    data["y"]= (data.matched>0).astype(int)
    data["named_pair"]=data.trait_A+"__"+data.trait_B
    return data,a,b

def boot_over_families(g,draws,seed):
    fams=sorted(g.family.unique())
    if not fams:raise ValueError("no eligible families")
    tab=g.groupby("family").repro_wins.agg(["sum","count"]).reindex(fams)
    c=tab.to_numpy(float)
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(fams),(draws,len(fams)))
    draws_c=c[idx].sum(axis=1)
    pair_rate=draws_c[:,0]/draws_c[:,1]
    per_fam=(c[:,0]/c[:,1])
    fam_rate=per_fam[idx].mean(axis=1)
    return {
      "n_supported_family_pair_observations":len(g),
      "n_independent_families_with_cross_organ_comparisons":len(fams),
      "n_reproductive_K_higher":int(g.repro_wins.sum()),
      "pair_weighted_reproductive_K_higher_rate":float(g.repro_wins.mean()),
      "family_cluster_pair_rate_CI95":list(map(float,np.quantile(pair_rate,[.025,.975]))),
      "equal_family_mean_reproductive_higher_rate":float(per_fam.mean()),
      "family_bootstrap_equal_family_CI95":list(map(float,np.quantile(fam_rate,[.025,.975])))
    }

def module_summary(df,design):
    out={}
    draws=design["matched_tip"]["family_cluster_bootstrap_draws"]
    seed=design["matched_tip"]["bootstrap_seed"]
    if draws!=5000 or seed!=20261015:
        raise ValueError("functional class uncertainty design changed")
    for j,axis in enumerate(EXPECTED):
        g=df[(df.axis==axis)&df.intermodule].copy()
        if g.family.nunique()!=34 or g.named_pair.nunique()!=36:
            raise ValueError("not original 34-family/36 cross-organ-pair cohort")
        item=boot_over_families(g,draws,seed+j)
        bypair=g.groupby("named_pair").repro_wins.agg(["size","mean"])
        supported=bypair[bypair["size"]>=5]
        item["n_reproductive_vegetative_named_pair_types"]=len(bypair)
        item["equal_named_pair_type_rate"]=float(bypair["mean"].mean())
        item["equal_pair_type_rate_ge5_families"]=float(supported["mean"].mean())
        item["pair_types_with_at_least_5_family_systems"]=len(supported)
        defs={
           "exclude_seed_dry_mass": ~g.trait_A.eq("seed_dry_mass")&~g.trait_B.eq("seed_dry_mass"),
           "exclude_leaf_area":~g.trait_A.eq("leaf_area")&~g.trait_B.eq("leaf_area"),
           "fruits_only_vs_vegetative":(~g.trait_A.str.startswith("seed"))&(~g.trait_B.str.startswith("seed")),
           "seeds_only_vs_vegetative":(~g.trait_A.str.startswith("fruit"))&(~g.trait_B.str.startswith("fruit")),
        }
        subset={}
        for nm,mask in defs.items():
            h=g[mask]
            if len(h)<100:
                raise ValueError("unexpected undersupported organ-specific sensitivity "+nm)
            subset[nm]={"n_pairs":len(h),"n_family_clusters":int(h.family.nunique()),
                "n_reproductive_higher":int(h.repro_wins.sum()),
                "reproductive_higher_rate":float(h.repro_wins.mean()),
                "equal_family_rate":float(h.groupby("family").repro_wins.mean().mean())}
        item["source_module_exclusion_sensitivities"]=subset
        traits=sorted(set(g.trait_A)|set(g.trait_B))
        loo=[]
        for t in traits:
            h=g[(g.trait_A!=t)&(g.trait_B!=t)]
            loo.append({"excluded_trait":t,"n_pairs":len(h),
              "reproductive_higher_rate":float(h.repro_wins.mean())})
        item["leave_one_named_trait_out"]=loo
        item["leave_one_trait_out_min_rate"]=min(z["reproductive_higher_rate"] for z in loo)
        item["leave_one_trait_out_max_rate"]=max(z["reproductive_higher_rate"] for z in loo)
        out[axis]=item
    X=df[df.intermodule].pivot_table(
        index=["family","trait_A","trait_B"],columns="axis",
        values="repro_wins",aggfunc="first")
    both=X.dropna(subset=["S3","prune_only"])
    if len(both)!=397:raise ValueError("not exact original both-tree cross-module population")
    both_axes={"n_evaluable_on_both_trees":len(both),
       "n_reproductive_higher_on_both":int(((both.S3==1)&(both.prune_only==1)).sum()),
       "n_vegetative_higher_on_both":int(((both.S3==0)&(both.prune_only==0)).sum()),
       "n_tree_axis_disagreements":int((both.S3!=both.prune_only).sum())}
    return out,both_axes

def accuracy_credit(y,p):
    pred=(p>.5).astype(float)
    return np.where(np.isclose(p,.5,rtol=0,atol=1e-12),.5,(pred==y).astype(float))

def score_fold_predictions(g,model_cols,draws,seed):
    scores={}
    fams=sorted(g.family.unique())
    if len(fams)!=42:raise ValueError("LOFO test lost family cluster")
    rng=np.random.default_rng(seed)
    draws_i=rng.integers(0,len(fams),(draws,len(fams)))
    for model in model_cols:
        p=g[model].to_numpy(float)
        y=g.y.to_numpy(int)
        if np.any(~np.isfinite(p)) or np.any(p<=0) or np.any(p>=1):
            raise ValueError("probability out of range")
        g[model+"_accuracy"]=accuracy_credit(y,p)
        g[model+"_brier"]=(p-y)**2
        g[model+"_logloss"]=-(y*np.log(p)+(1-y)*np.log1p(-p))
        m=g.groupby("family")
        mm=m[[model+"_accuracy",model+"_brier",model+"_logloss"]].mean()
        scores[model]={
          "heldout_family_pair_rows":len(g),
          "hard_sign_accuracy_with_half_credit_for_ties":float(g[model+"_accuracy"].mean()),
          "family_equal_accuracy":float(mm[model+"_accuracy"].mean()),
          "Brier_loss":float(g[model+"_brier"].mean()),
          "binary_log_loss":float(g[model+"_logloss"].mean())}
    for model in model_cols:
        if model=="pooled_other_families":continue
        tab=g.assign(
            delta_brier=g["pooled_other_families_brier"]-g[model+"_brier"],
            delta_accuracy=g[model+"_accuracy"]-g["pooled_other_families_accuracy"]
        ).groupby("family").agg(
            delta_brier_sum=("delta_brier","sum"),
            delta_accuracy_sum=("delta_accuracy","sum"),
            n=("delta_brier","size"))
        count=tab["n"].reindex(fams).to_numpy(float)
        if np.any(count==0):raise ValueError("LOFO evaluation family absent")
        vals={}
        for col in ("delta_brier","delta_accuracy"):
            sums=tab[col+"_sum"].reindex(fams).to_numpy(float)
            draws_sum=sums[draws_i].sum(axis=1)
            draws_num=count[draws_i].sum(axis=1)
            z=draws_sum/draws_num
            vals[col+"_gain_over_global"]=float(sums.sum()/count.sum())
            vals[col+"_family_cluster_95CI"]=list(map(float,np.quantile(z,[.025,.975])))
        scores[model].update(vals)
    return scores

def predictive_lofo(df,design):
    traits=sorted(design["fixed_organ_classes"]["reproductive"]+
                  design["fixed_organ_classes"]["vegetative"])
    tid={name:i for i,name in enumerate(traits)}
    reps=set(design["fixed_organ_classes"]["reproductive"])
    out={}
    for ax in EXPECTED:
        g=df[df.axis==ax].copy().reset_index(drop=True)
        if len(g)!=EXPECTED[ax] or g.family.nunique()!=42:
            raise ValueError("not original fixed LOFO evaluation cohort")
        n=len(g)
        features=np.zeros((n,12),float)
        mod=np.zeros((n,1),float)
        for ix,r in enumerate(g.itertuples(index=False)):
            features[ix,tid[r.trait_A]]=1
            features[ix,tid[r.trait_B]]=-1
            mod[ix,0]=int(r.trait_A in reps)-int(r.trait_B in reps)
        models=("pooled_other_families","reproductive_vegetative",
                "named_trait_Bradley_Terry","named_pair_Laplace")
        for model in models:g[model]=np.nan
        for fam in sorted(g.family.unique()):
            te=(g.family==fam).to_numpy()
            tr=~te
            if te.sum()<1 or tr.sum()<1:
                raise ValueError("invalid held-out-family fold")
            original_y=g.y.to_numpy(int)
            train=g.loc[tr]
            base=(int(train.y.sum())+1)/(len(train)+2)
            g.loc[te,"pooled_other_families"]=base
            for mat,label in ((mod,"reproductive_vegetative"),
                              (features,"named_trait_Bradley_Terry")):
                fit=LogisticRegression(C=1.0,fit_intercept=False,
                       solver="lbfgs",max_iter=1000).fit(mat[tr],original_y[tr])
                g.loc[te,label]=fit.predict_proba(mat[te])[:,1]
            # Exact-pair posterior smoothed on training families ONLY.
            tm=train.groupby("named_pair").y.agg(["sum","count"])
            for row in g.index[te]:
                pair=g.at[row,"named_pair"]
                if pair in tm.index:
                    v=tm.loc[pair]
                    prob=(int(v["sum"])+1)/(int(v["count"])+2)
                else:prob=.5
                g.at[row,"named_pair_Laplace"]=prob
        slices={
          "all_source_eligible_pairs":g,
          "pair_types_supported_in_at_least_5_families":
             g[g.named_pair.map(g.groupby("named_pair").family.nunique())>=5].copy()}
        out[ax]={}
        for j,(label,h) in enumerate(slices.items()):
            out[ax][label]={
              "n_named_trait_pair_types":int(h.named_pair.nunique()),
              "n_families":int(h.family.nunique()),
              "scores":score_fold_predictions(h,models,
                   design["predictive_models"]["bootstrap_42_families"],
                   design["matched_tip"]["bootstrap_seed"]+j+2*(ax=="prune_only"))}
        # Family held out in every fold, no same-family training rows.
        out[ax]["prediction_design"]="LOFO: every predictor trained on all other families only; no original K of the heldout family is accessed as a covariate."
    return out

def audit(support,batches,design,margin_design):
    data,repro,veg=source_data(support,batches,design,margin_design)
    module,both=module_summary(data,design)
    out={"version":"v0.1","status":STATUS,
         "post_original_K_and_760_outcomes_exploratory":True,
         "biology_classes":{"reproductive":sorted(repro),"vegetative":sorted(veg)},
         "source_data_provenance":{"original_249_family_trait_systems":249,
                   "source_eligible_family_pair_comparisons":760,
                   "S3_valid_K_pairs":760,"prune_valid_K_pairs":747,
                   "plant_families":42},
         "reproductive_vegetative_matched_tip":module,
         "reproductive_vegetative_both_trees":both,
         "left_one_whole_family_out_prediction":predictive_lofo(data,design),
         "independent_TRY_v7_validation":False,
         "new_OU_Brownian_process_parameters_fitted":False,
         "no_raw_trait_values_species_ids_exported":True,
         "scientific_boundary":"All results are post-discovery original AusTraits. Matched tip K and LOFO transfer cannot attribute biological causation or independent evolutionary constraint; module-based source-OU posterior-predictive adequacy is a distinct original-tip check."}
    return out

def main():
    p=argparse.ArgumentParser()
    for key in ("batch-dir","support","design","margin-design","out"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    batches=[json.loads(path.read_text()) for path in
             sorted(a.__dict__["batch_dir"].glob("B*.json"))]
    result=audit(json.loads(a.support.read_text()),batches,
       json.loads(a.design.read_text()),
       json.loads(a.__dict__["margin_design"].read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,
        "module_frequency":{ax:result["reproductive_vegetative_matched_tip"][ax]["pair_weighted_reproductive_K_higher_rate"] for ax in EXPECTED},
        "LOFO_Brier_models":{ax:{name:v["Brier_loss"] for name,v in result["left_one_whole_family_out_prediction"][ax]["all_source_eligible_pairs"]["scores"].items()} for ax in EXPECTED}},indent=2))

if __name__=="__main__":
    main()
