#!/usr/bin/env python3
"""Retrospective 3-stage K-rank sampling-vs-source diagnostic on unchanged
original AusTraits reproductive/vegetative named organ pair identities.

Use TWO fully verified, frozen, real-tree K output archives:
(1) 283 no-electronic-flora pairs (broader species per pair),
(2) 142 no-flora + identical source DatasetID K pairs (smaller same-source tips).

Within a pair, stage 1→2 is a *change in available matched taxa/tree geometry*
using the SAME nonflora measurement sources. Stage 2→3 substitutes common-
DatasetID numeric values on EXACTLY the same stage-2 tip set/tree. This
decomposes dependence on observational support, NOT underlying causality.

Original source selection was K-blind for each test but the organ categories,
this comparison and both source restrictions were designed after original K
was seen. The 142 pair types are NOT independent evolutionary replicates.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np

STATUS="AUSTRAITS_K_NONFLORA_COHORT_TRANSITION_EXPLORATORY_VERIFIED"
SOURCE283="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_ORGAN_SENSITIVITY_AGGREGATED_V0_1"
SOURCE142="AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_SENSITIVITY_AGGREGATED_V0_1"
STAGES=("broad_nonflora_tips","same_dataset_eligible_tips_all_nonflora",
        "same_dataset_eligible_tips_identical_dataset_medians")
EDGES=(("broad_nonflora_tips","same_dataset_eligible_tips_all_nonflora"),
       ("same_dataset_eligible_tips_all_nonflora","same_dataset_eligible_tips_identical_dataset_medians"),
       ("broad_nonflora_tips","same_dataset_eligible_tips_identical_dataset_medians"))
EXPECTED={"S3":(283,142,24,221),"prune_only":(233,101,18,180)}

def validate_and_join(broad,joint,design):
    if design.get("status")!="POST_COMPLETE_283_AND_142_K_RESULTS_THREE_STAGE_SUPPORT_SOURCE_DECOMPOSITION":
        raise ValueError("post-outcome comparison provenance missing or not frozen")
    if broad.get("status")!=SOURCE283 or joint.get("status")!=SOURCE142:
        raise ValueError("not the two verified original K scenario artifacts")
    if (broad.get("original_source_blind_pair_universe")!=760
      or joint.get("original_source_blind_pair_universe")!=760
      or broad.get("nonflora_supported_before_K_pairs")!=283
      or joint.get("joint_nonflora_source_qualified_before_K_pairs")!=142):
        raise ValueError("original K-blind graph or 283/142 source qualification changed")
    if not (broad.get("not_external_TRY_v7_independent_source_validation") and
            joint.get("not_external_TRY_v7_independent_source_validation")):
        raise ValueError("improper source independence statement")
    outputs={}
    for axis,(Nwide,Njoint,Nfam,Npositive) in EXPECTED.items():
        a=broad["axes"][axis]
        b=joint["axes"][axis]
        if (a.get("n_valid_real_tree_K_pairs")!=Nwide
           or b.get("n_valid_real_tree_K_pairs")!=Njoint):
            raise ValueError("original K native axis valid pairs changed")
        wide={}
        for z in a["pair_level_K_decisions_no_species_names"]:
            k=(z["family"],z["trait_A"],z["trait_B"])
            if k in wide:raise ValueError("duplicate original broad nonflora pair")
            wide[k]=z
        if len(wide)!=Nwide:raise ValueError("original broad nonflora axis incomplete")
        narrow={}
        for z in b["pair_level_K_decisions_no_species_names"]:
            k=(z["family"],z["trait_A"],z["trait_B"])
            if k in narrow:raise ValueError("duplicate original narrow same-DatasetID pair")
            narrow[k]=z
        if len(narrow)!=Njoint:raise ValueError("strict source native K output incomplete")
        if not set(narrow).issubset(wide):
            raise ValueError("strict same-source pair missing from broad K-blind cohort")
        rows=[]
        for k,z in sorted(narrow.items()):
            old=wide[k]
            if old["subtype"]!=z["subtype"]:
                raise ValueError("original reproductive/vegetative trait subtype mismatched")
            if z["n_same_source_species"]>old["n_nonflora_species"]:
                raise ValueError("same-source selected tips exceed wider nonflora source graph")
            if z["n_native_tree_tips"]>old["n_native_tree_tips"]:
                raise ValueError("strict original native tree retains MORE taxa than broad graph")
            values={
               STAGES[0]:float(old["delta_five_flora_removed"]),
               STAGES[1]:float(z["delta_all_nonflora_sources"]),
               STAGES[2]:float(z["delta_identical_nonflora_dataset"])
            }
            for v in values.values():
                if not math.isfinite(v):raise ValueError("nonfinite original K pair contrast")
            checks=(
              int(old["reproductive_K_higher_nonflora_medians"]),
              int(z["reproductive_K_higher_all_nonflora_medians"]),
              int(z["reproductive_K_higher_identical_nonflora_dataset_medians"]))
            if tuple(int(values[s]>0) for s in STAGES)!=checks:
                raise ValueError("original pre-recorded pair K signs inconsistent with logK")
            if not math.isclose(
               values[STAGES[2]]-values[STAGES[1]],
               float(z["delta_measurement_only"]),abs_tol=2e-9):
                raise ValueError("strict identical-tip source arm K contrast mismatch")
            rows.append({
              "family":k[0],"trait_A":k[1],"trait_B":k[2],
              "organ_subtype":old["subtype"],
              "n_nonflora_species_broad":int(old["n_nonflora_species"]),
              "n_identical_dataset_species":int(z["n_same_source_species"]),
              "n_native_tree_tips_broad":int(old["n_native_tree_tips"]),
              "n_native_tree_tips_source":int(z["n_native_tree_tips"]),
              "logK_by_stage":values,
              "reproductive_higher_by_stage":dict(zip(STAGES,checks))})
        if len(rows)!=Njoint or len({z["family"] for z in rows})!=Nfam:
            raise ValueError("original strict 142 K family cohort mutated")
        if sum(z["reproductive_higher_by_stage"][STAGES[2]] for z in rows)!=(120 if axis=="S3" else 81):
            raise ValueError("original strict K source sign counts changed")
        if sum(z["reproductive_higher_by_stage"][STAGES[1]] for z in rows)!=(121 if axis=="S3" else 83):
            raise ValueError("original strict full-nonflora source signs changed")
        if sum(int(z["reproductive_K_higher_nonflora_medians"]) for z in wide.values())!=Npositive:
            raise ValueError("original full nonflora 283-source result signs changed")
        outputs[axis]={"selected":rows,
                       "full_broad_n":len(wide),
                       "full_broad_repro_wins":Npositive}
    return outputs

def clustered_summary(rows,draws,seed):
    fams=sorted(set(r["family"] for r in rows))
    rng=np.random.default_rng(seed)
    inds=rng.integers(len(fams),size=(draws,len(fams)))
    sums=np.asarray([[len([r for r in rows if r["family"]==fam])]
         +[sum(r["reproductive_higher_by_stage"][s] for r in rows if r["family"]==fam)
           for s in STAGES] for fam in fams],dtype=float)
    if not np.all(sums[:,0]>0):raise ValueError("bootstrap family with no comparisons")
    t=sums[inds].sum(axis=1)
    n=t[:,0]
    out={"n_pair_identities":len(rows),"n_plant_families":len(fams),
         "stage_rates":{},"paired_steps":{}}
    for i,s in enumerate(STAGES,1):
        r=sums[:,i].sum()/sums[:,0].sum()
        famrates=sums[:,i]/sums[:,0]
        bpair=t[:,i]/n
        bfamily=(sums[:,i]/sums[:,0])[inds].mean(axis=1)
        out["stage_rates"][s]={
          "n_reproductive_K_higher":int(sums[:,i].sum()),
          "pair_weighted_fraction":float(r),
          "equal_family_mean_fraction":float(famrates.mean()),
          "family_bootstrap_pair_weighted_CI95":list(map(float,np.quantile(bpair,[.025,.975]))),
          "family_bootstrap_equal_family_CI95":list(map(float,np.quantile(bfamily,[.025,.975])))}
    for stage_a,stage_b in EDGES:
        ia=STAGES.index(stage_a)+1;ib=STAGES.index(stage_b)+1
        p1=np.asarray([r["reproductive_higher_by_stage"][stage_a] for r in rows],int)
        p2=np.asarray([r["reproductive_higher_by_stage"][stage_b] for r in rows],int)
        delta=np.asarray([r["logK_by_stage"][stage_b]-r["logK_by_stage"][stage_a] for r in rows],float)
        nflip=int(np.sum(p1!=p2))
        fam_dif=(sums[:,ib]-sums[:,ia])/sums[:,0]
        fam_ci=fam_dif[inds].mean(axis=1)
        pair_ci=(t[:,ib]-t[:,ia])/n
        out["paired_steps"][stage_a+"_TO_"+stage_b]={
          "n_pairwise_K_sign_reversals":nflip,
          "fraction_pairwise_K_sign_reversals":float(nflip/len(rows)),
          "n_vegetative_to_reproductive_switch":int(((p1==0)&(p2==1)).sum()),
          "n_reproductive_to_vegetative_switch":int(((p1==1)&(p2==0)).sum()),
          "pair_weighted_change_in_reproductive_higher_rate":float(np.mean(p2-p1)),
          "equal_family_mean_change_in_reproductive_higher_rate":float(fam_dif.mean()),
          "family_bootstrap_pair_weighted_rate_change_CI95":list(map(float,np.quantile(pair_ci,[.025,.975]))),
          "family_bootstrap_equal_family_rate_change_CI95":list(map(float,np.quantile(fam_ci,[.025,.975]))),
          "median_absolute_delta_logK":float(np.median(np.abs(delta))),
          "median_signed_delta_logK":float(np.median(delta)),
          "mean_signed_delta_logK":float(np.mean(delta))}
    return out

def audit(broad,joint,design):
    axes=validate_and_join(broad,joint,design)
    draws=design["statistical_accounting"]["bootstrap_draws"]
    if draws!=5000 or design["statistical_accounting"]["bootstrap_seed"]!=20261019:
        raise ValueError("original post-outcome family-resampling plan modified")
    out={"version":"v0.1","status":STATUS,
      "source_runs":{"full_nonflora":38922133371,"strict_nonflora_same_dataset":39006469805},
      "after_original_reproductive_K_organ_results":True,
      "source_and_K_blind_eligibility_not_changed":True,
      "not_new_evolutionary_process_hypothesis_or_independent_external_validation":True,
      "source_qualification_does_not_prove_primary_independence":True,
      "axes":{}}
    for i,ax in enumerate(("S3","prune_only")):
        z=axes[ax]
        data=clustered_summary(z["selected"],draws,design["statistical_accounting"]["bootstrap_seed"]+i)
        data["original_broad_nonflora_valid_pairs"]=z["full_broad_n"]
        data["original_broad_nonflora_reproductive_K_higher"]=z["full_broad_repro_wins"]
        data["original_broad_nonflora_pair_weighted_fraction"]=z["full_broad_repro_wins"]/z["full_broad_n"]
        data["n_frozen_shared_dataset_family_trait_pair_identities"]=len(z["selected"])
        data["research_population_warning"]="Original 283/233 and strict 142/101 sets differ in family×trait pairs. Rates must be compared in matched 142/101 identities before discussing tip restriction versus source medians."
        out["axes"][ax]=data
    out["scientific_boundary"]="Stage I vs II changes taxa/tip support and geometry; stage II vs III is the identical-tip measurement-source contrast. Neither isolates an evolutionary constraint nor validates source independence. Reproductive/vegetative organ classes and these diagnostics were selected after the original AusTraits outcomes."
    return out

def main():
    p=argparse.ArgumentParser()
    for name in ("broad","joint","design","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    out=audit(json.loads(a.broad.read_text()),json.loads(a.joint.read_text()),
              json.loads(a.design.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":STATUS,
      "axes":{ax:{"n":out["axes"][ax]["n_pair_identities"],
                  "rates":{k:round(v["pair_weighted_fraction"],4)
                           for k,v in out["axes"][ax]["stage_rates"].items()},
                  "flips":{k:v["n_pairwise_K_sign_reversals"]
                           for k,v in out["axes"][ax]["paired_steps"].items()}}
               for ax in ("S3","prune_only")}},sort_keys=True))

if __name__=="__main__":
    main()
