#!/usr/bin/env python3
"""Plot three paper figures from immutable, already-opened AusTraits K aggregates.

NO new fits, trait/subgroup selection, bootstrap, K estimation or new P values.
The archive-status and exact native-S3/prune counts must match the manuscript
claim register. We plot original bootstrap intervals verbatim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MODULE_STATUS = "AUSTRAITS_K_REPRODUCTIVE_VEGETATIVE_LOFO_EXPLORATORY_V0_1"
TRANSITION_STATUS = "AUSTRAITS_K_NONFLORA_COHORT_TRANSITION_EXPLORATORY_VERIFIED"
JOINT_STATUS = "AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_SENSITIVITY_AGGREGATED_V0_1"
STAGES = (
    "broad_nonflora_tips",
    "same_dataset_eligible_tips_all_nonflora",
    "same_dataset_eligible_tips_identical_dataset_medians"
)
EDGES = ((STAGES[0], STAGES[1]), (STAGES[1], STAGES[2]))
AXES = (("S3", "S3"), ("prune", "prune_only"))
PREDICTORS = (
    ("pooled_other_families", "Pooled prior"),
    ("reproductive_vegetative", "Organ category"),
    ("named_trait_Bradley_Terry", "12 named traits"),
    ("named_pair_Laplace", "Named trait pair")
)


def verify_inputs(z, t, j, claims):
    if z.get("status") != MODULE_STATUS or not z.get("post_original_K_and_760_outcomes_exploratory"):
        raise ValueError("not the original post-discovery matched K and family holdout source")
    if t.get("status") != TRANSITION_STATUS or j.get("status") != JOINT_STATUS:
        raise ValueError("not the validated source/taxon archive")
    if claims.get("role") != "REPORTING_ONLY_NO_NEW_EMPIRICAL_EFFECTS":
        raise ValueError("reporting-only claim firewall invalid")

    paired = claims["phenotype_scope"]
    for a, ax in AXES:
        m = z["reproductive_vegetative_matched_tip"][ax]
        ref = paired["cross_organ_" + a]
        if (m["n_supported_family_pair_observations"] != ref["pairs"] or
            m["n_reproductive_K_higher"] != ref["wins"] or
            m["n_independent_families_with_cross_organ_comparisons"] != ref["families"]):
            raise ValueError("matched K source or claim count changed: " + a)
        fam = m["per_family_descriptive"]
        if len(fam) != ref["families"] or sum(v["n_cross_organ_pair_comparisons"] for v in fam.values()) != ref["pairs"]:
            raise ValueError("incomplete original family K graph: " + a)
        if sum(v["n_reproductive_K_higher"] for v in fam.values()) != ref["wins"]:
            raise ValueError("original family K wins inconsistent: " + a)
        scores = z["left_one_whole_family_out_prediction"][ax]["all_source_eligible_pairs"]["scores"]
        expected = claims["predictive_whole_family_holdout"][a]
        for name, registry in (("pooled_other_families", "pooled"), ("reproductive_vegetative", "organ"),
                               ("named_trait_Bradley_Terry", "trait")):
            actual = scores[name]["Brier_loss"]
            if abs(actual-expected[registry + "_brier"]) > 0.00003:
                raise ValueError("K LOFO Brier and archived reported value mismatch: " + a + ":" + name)
        for name, key in (("pooled_other_families","pooled_accuracy"),("reproductive_vegetative","organ_accuracy")):
            actual = scores[name]["hard_sign_accuracy_with_half_credit_for_ties"]
            if abs(actual-expected[key]) > 0.0002:
                raise ValueError("LOFO heldout accuracy mismatch: " + a)
        for val, exp in zip(
            scores["reproductive_vegetative"]["delta_brier_family_cluster_95CI"],
            expected["organ_brier_gain_ci"]
        ):
            if abs(val-exp) > 0.00003:
                raise ValueError("LOFO family bootstrap not exactly reproduced")

        strict = claims["same_pair_ID_three_stage"][a]
        stage = t["axes"][ax]
        joint = j["axes"][ax]
        if (stage["n_pair_identities"], stage["n_plant_families"]) != (strict["N"],strict["families"]):
            raise ValueError("cohort identity changed")
        if joint["n_valid_real_tree_K_pairs"] != strict["N"]:
            raise ValueError("strict native phylogeny denominator changed")
        for idx, k in enumerate(STAGES):
            wins = stage["stage_rates"][k]["n_reproductive_K_higher"]
            if wins != strict["wins"][idx]:
                raise ValueError("archive stage counts and claim register disagree")
        for idx,(first,last) in enumerate(EDGES):
            rev = stage["paired_steps"][first+"_TO_"+last]
            if rev["n_pairwise_K_sign_reversals"] != strict["flip_count"][idx]:
                raise ValueError("source K sign reversals changed")
            signed_delta = strict["wins"][idx+1]-strict["wins"][idx]
            if (rev["n_vegetative_to_reproductive_switch"] -
                rev["n_reproductive_to_vegetative_switch"]) != signed_delta:
                raise ValueError("original sign-flow algebra inconsistent")
    return True


def fig_family(z, out):
    base = z["reproductive_vegetative_matched_tip"]
    s3 = base["S3"]["per_family_descriptive"]
    pr = base["prune_only"]["per_family_descriptive"]
    fams = sorted(set(s3) | set(pr), key=lambda x: (
        -(s3.get(x, {}).get("reproductive_K_higher_rate", 0.0)), x))
    if len(fams) != 34:
        raise ValueError("wrong source cohort for 34-family main figure")
    fig, ax = plt.subplots(figsize=(10.6, 12.7))
    yy = np.arange(len(fams), dtype=float)
    for label, data, offset, marker in (
        ("S3", s3, -0.15, "o"), ("Native prune", pr, 0.15, "s")
    ):
        y = []
        x = []
        size = []
        for i, f in enumerate(fams):
            v = data.get(f)
            if v is None or v["n_cross_organ_pair_comparisons"] == 0:
                continue
            y.append(yy[i]+offset)
            x.append(100*v["reproductive_K_higher_rate"])
            size.append(20+12*np.sqrt(v["n_cross_organ_pair_comparisons"]))
        ax.scatter(x,y,s=size,marker=marker,label=label,alpha=.82,zorder=3)
    ax.axvline(50, color=".4", linestyle="--", linewidth=1)
    ax.set_yticks(yy, fams, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(-4,105)
    ax.set_xlabel("Within-family cross-organ comparisons with reproductive K higher (%)")
    ax.set_title("Functional-organ phylogenetic signal across 34 plant families",pad=15)
    ax.grid(axis="x",alpha=.16)
    ax.spines[["top","right"]].set_visible(False)
    ax.legend(loc="lower right",frameon=False,title="Phylogeny treatment")
    fig.text(.14,.025,
             "Each point is one family; symbol size reflects dependent within-family trait-pair count.\n"
             "Both organs use the same species and tree per pair. Post-discovery AusTraits study.",
             fontsize=9)
    fig.subplots_adjust(left=.27,right=.96,bottom=.09,top=.95)
    save(fig,out,"figure1_common_tips_family_organK")


def fig_lofo(z, claims, out):
    fig, ax = plt.subplots(figsize=(10.8,6.2))
    models=[x[0] for x in PREDICTORS]
    label_by=dict(PREDICTORS)
    y=np.arange(len(models), dtype=float)
    for a, axis, off, symbol in (
        ("S3","S3",-0.12,"o"), ("prune","prune_only",0.12,"s")
    ):
        scores=z["left_one_whole_family_out_prediction"][axis]["all_source_eligible_pairs"]["scores"]
        vals=[scores[k]["Brier_loss"] for k in models]
        ax.scatter(vals,y+off,marker=symbol,s=72,label=a,zorder=3)
        for ix,v in enumerate(vals):
            ax.annotate(f"{v:.3f}",(v,y[ix]+off),
                        textcoords="offset points",xytext=(7,0),fontsize=9,va="center")
    ax.set_yticks(y,[label_by[m] for m in models])
    ax.invert_yaxis()
    ax.set_xlim(.17,.31)
    ax.set_xlabel("Whole-family-held-out Brier probability loss (lower is better)")
    ax.set_title("Organ category improves K rank prediction across held-out families",pad=18)
    ax.grid(axis="x",alpha=.16)
    ax.spines[["top","right"]].set_visible(False)
    ax.legend(loc="lower right",frameon=False)
    fig.text(.13,.045,
             "S3 organ gain vs pooled: +0.0368 (family-bootstrap CI +0.0043 to +0.0639).\n"
             "Prune organ gain: +0.0435 (CI +0.0195 to +0.0634).\n"
             "42 family folds; both organ and named-trait priors are evaluated within AusTraits, not an independent new source.",
             fontsize=9.3)
    fig.subplots_adjust(left=.23,right=.94,top=.82,bottom=.28)
    save(fig,out,"figure2_family_holdout_Brier")


def fig_stages(t, claims, out):
    fig, ax = plt.subplots(figsize=(12.4,6.8))
    x=np.arange(3,dtype=float)
    labels=[
        "Broad original\nnon-flora tips",
        "Source-qualified\nnarrower tips",
        "Same narrow tips;\nshared-source values"
    ]
    for a, axis, off, marker in (
        ("S3","S3",-0.09,"o"),("prune","prune_only",.09,"s")
    ):
        n=claims["same_pair_ID_three_stage"][a]["N"]
        st=t["axes"][axis]
        rates=np.array([st["stage_rates"][k]["pair_weighted_fraction"] for k in STAGES])*100
        low=np.array([st["stage_rates"][k]["family_bootstrap_pair_weighted_CI95"][0] for k in STAGES])*100
        high=np.array([st["stage_rates"][k]["family_bootstrap_pair_weighted_CI95"][1] for k in STAGES])*100
        ax.errorbar(x+off,rates,yerr=np.vstack([rates-low,high-rates]),fmt=marker+"-",
                    capsize=4.5,elinewidth=1.6,linewidth=1.9,
                    label=f"{a}: same {n} pair identities")
        for i,k in enumerate(STAGES):
            z=st["stage_rates"][k]
            ax.annotate(f"{z['n_reproductive_K_higher']}/{n}",
                        (x[i]+off,rates[i]),textcoords="offset points",
                        xytext=(0,11 if a=="S3" else -20),ha="center",fontsize=10)
    ax.set_xticks(x,labels,fontsize=10.5)
    ax.set_xlim(-.4,2.4)
    ax.set_ylim(40,103)
    ax.axhline(50,linestyle="--",linewidth=.9,color=".45")
    ax.set_ylabel("Source-qualified comparisons with reproductive K higher (%)")
    ax.set_title("Why a stricter measurement-source rule changes the apparent organ advantage",pad=16)
    ax.grid(axis="y",alpha=.14)
    ax.legend(frameon=False,fontsize=9,loc="lower right")
    ax.spines[["top","right"]].set_visible(False)
    fig.text(.1,.038,
             "S3: 17 vs 6 reversals with tip restriction; 4 vs 5 with source-value substitution.\n"
             "Prune: 7 vs 6; 5 vs 7. Arrows mean vegetative→reproductive vs reproductive→vegetative.\n"
             "Stage 1→2 changes taxon/tree support; stage 2→3 changes only values on identical tips; neither identifies causality.",
             fontsize=9)
    fig.subplots_adjust(left=.105,right=.96,top=.88,bottom=.27)
    save(fig,out,"figure3_taxon_vs_source_stages")


def save(fig,out,basename):
    for fmt in ("svg","png"):
        fig.savefig(out/(basename+"."+fmt), dpi=240)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    for name in ("module","transition","joint","claims","out-dir"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    z=json.loads(args.module.read_text())
    t=json.loads(args.transition.read_text())
    j=json.loads(args.joint.read_text())
    claims=json.loads(args.claims.read_text())
    verify_inputs(z,t,j,claims)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    fig_family(z,args.out_dir)
    fig_lofo(z,claims,args.out_dir)
    fig_stages(t,claims,args.out_dir)
    filenames=sorted(p.name for p in args.out_dir.glob("figure[123]*"))
    if len(filenames)!=6 or any((args.out_dir/name).stat().st_size<4000 for name in filenames):
        raise ValueError("paper figure files missing or too small")
    fingerprints={name:hashlib.sha256(path.read_bytes()).hexdigest()
                  for name,path in (("module",args.module),
                                    ("transition",args.transition),
                                    ("joint",args.joint),
                                    ("claims",args.claims))}
    manifest={
        "status":"PASS_SOURCE_LINKED_REPORTING_FIGURES",
        "source_workflow_runs":{
            "module_lofo":38685668376,
            "transition":39202352075,
            "joint_source_K":39006469805,
        },
        "original_source_sha256":fingerprints,
        "outputs":filenames,
        "new_biological_effects":0,
        "matched_trees_separate":True,
        "independent_validation":"NOT_QUALIFIED",
        "posterior_selected_organ_module":True,
    }
    (args.out_dir/"figure_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
