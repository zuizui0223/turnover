#!/usr/bin/env python3
"""Publication figures for the fixed 142 joint nonflora/shared-source K result.

These are figures of ALREADY completed, verified and explicitly POST-OUTCOME
AusTraits source/tip sensitivity analyses, not independent measurement tests.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

EXPECTED_TRANSITION="AUSTRAITS_K_NONFLORA_COHORT_TRANSITION_EXPLORATORY_VERIFIED"
EXPECTED_STRICT="AUSTRAITS_K_JOINT_NONFLORA_SHARED_DATASET_SENSITIVITY_AGGREGATED_V0_1"
STAGES=["broad_nonflora_tips","same_dataset_eligible_tips_all_nonflora",
        "same_dataset_eligible_tips_identical_dataset_medians"]
LABELS=[
  "Same pair IDs\nall available nonflora species",
  "Only same-dataset-covered species\nall nonflora observations",
  "Same exact species and tree\nidentical-dataset observations"]

def validate(transition,joint):
    if transition.get("status")!=EXPECTED_TRANSITION or joint.get("status")!=EXPECTED_STRICT:
        raise ValueError("not frozen native-tree actual K source artifacts")
    for axis,n,fams in (("S3",142,24),("prune_only",101,18)):
        j=joint["axes"][axis]
        t=transition["axes"][axis]
        if (t["n_pair_identities"],t["n_plant_families"])!=(n,fams):
            raise ValueError("posterior taxon graph changed")
        if (j["n_valid_real_tree_K_pairs"],j["n_families_valid"])!=(n,fams):
            raise ValueError("strict same-source K result and transition graph disagree")
        if int(t["stage_rates"][STAGES[-1]]["n_reproductive_K_higher"])!=int(
             j["identical_nonflora_dataset_same_tips"]["positive_comparisons"]):
            raise ValueError("strict source and transition repro K wins mismatch")
        if len(j["individual_families"])!=fams:
            raise ValueError("missing complete family context")
    return True

def chart_stages(z,outdir):
    fig,ax=plt.subplots(figsize=(12,6.9))
    x=np.arange(3,dtype=float)
    for axis,shift,mark,lab in [
        ("S3",-0.085,"o","S3, 142 comparisons in 24 families"),
        ("prune_only",0.085,"s","Prune, 101 comparisons in 18 families")]:
        metrics=z["axes"][axis]["stage_rates"]
        y=np.array([metrics[k]["pair_weighted_fraction"] for k in STAGES])*100
        lower=np.array([metrics[k]["family_bootstrap_pair_weighted_CI95"][0] for k in STAGES])*100
        upper=np.array([metrics[k]["family_bootstrap_pair_weighted_CI95"][1] for k in STAGES])*100
        ax.errorbar(x+shift,y,yerr=np.vstack([y-lower,upper-y]),linestyle="-",
                    linewidth=1.8,elinewidth=1.7,capsize=5,marker=mark,
                    markersize=8,label=lab)
        for xx,yy in zip(x+shift,y):
            ax.annotate(f"{yy:.1f}%",(xx,yy),xytext=(0,10 if axis=="S3" else -17),
                        textcoords="offset points",ha="center",fontsize=10)
    ax.axhline(50,linestyle="--",linewidth=1,alpha=.6)
    ax.set_xticks(x,LABELS,fontsize=10.2)
    ax.set_xlim(-.36,2.36)
    ax.set_ylim(35,104)
    ax.set_ylabel("Family×trait comparisons with reproductive K higher (%)",fontsize=11)
    ax.set_title("Reproductive-organ phylogenetic K advantage under stricter source support",fontsize=14,pad=20)
    ax.grid(axis="y",alpha=.16)
    ax.spines[["top","right"]].set_visible(False)
    ax.legend(loc="lower right",frameon=False,fontsize=9)
    fig.text(.12,.025,
       "Whiskers: 95% whole-family bootstrap intervals. Stage 1→2 changes species/phylogenetic support;\n"
       "Stage 2→3 changes measured source values on IDENTICAL species/trees. Post-discovery AusTraits sensitivity.",
       fontsize=9.2,ha="left")
    fig.subplots_adjust(bottom=.25,top=.86,left=.1,right=.96)
    for ext in ("png","svg"):
        fig.savefig(outdir/f"figure_nonflora_organK_three_stage.{ext}",dpi=220)
    plt.close(fig)

def chart_families(j,outdir):
    axname="S3"
    a=j["axes"][axname]["individual_families"]
    order=sorted(a,key=lambda fam:(a[fam]["n_reproductive_win_identical_nonflora_dataset"]/a[fam]["n_valid_pairs"],fam))
    n=len(order)
    ys=np.arange(n,dtype=float)
    fig,ax=plt.subplots(figsize=(11.2,12.7))
    rates=np.array([a[k]["n_reproductive_win_identical_nonflora_dataset"]/a[k]["n_valid_pairs"] for k in order])
    ax.scatter(rates*100,ys,s=48,zorder=3,label="Identical nonflora DatasetID median")
    ax.axvline(50,linestyle="--",linewidth=1,alpha=.6)
    ax.set_xlim(-4,109)
    ax.set_yticks(ys,order,fontsize=9.3)
    ax.set_xlabel("Reproductive morphology K higher (% of within-family source-qualified pairs)",fontsize=10)
    ax.grid(axis="x",alpha=.16)
    ax.spines[["top","right"]].set_visible(False)
    ax.set_title("Lineage-specific variation after excluding five electronic Floras",fontsize=13,pad=17)
    for i,fam in enumerate(order):
        ax.text(102,ys[i],f"n={a[fam]['n_valid_pairs']}",fontsize=8.6,ha="left",va="center")
    ax.set_ylim(-.85,n-.15)
    fig.text(.1,.035,
       "S3 axis only: 142 family×trait comparisons in 24 families. Counts within each family are\n"
       "dependent trait pairs, not independent evolutionary origins; no family-specific selection is inferred.",
       fontsize=9,ha="left")
    fig.subplots_adjust(left=.24,right=.85,top=.9,bottom=.1)
    for ext in ("png","svg"):
        fig.savefig(outdir/f"figure_nonflora_organK_family_context.{ext}",dpi=220)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    for key in ("transition","joint","out-dir"):
        p.add_argument("--"+key,required=True,type=Path)
    args=vars(p.parse_args())
    trans=json.loads(args["transition"].read_text())
    joint=json.loads(args["joint"].read_text())
    validate(trans,joint)
    out=args["out_dir"];out.mkdir(parents=True,exist_ok=True)
    chart_stages(trans,out)
    chart_families(joint,out)
    files=list(out.iterdir())
    if len(files)!=4 or any(x.stat().st_size<3000 for x in files):
        raise ValueError("manuscript figures incomplete or empty")
    print(json.dumps({"status":"AUSTRAITS_K_NONFLORA_SOURCE_MANUSCRIPT_FIGURES_PASS",
                       "files":[x.name for x in sorted(files)],
                       "strict_K_stages":[
                         int(trans["axes"]["S3"]["stage_rates"][k]["n_reproductive_K_higher"]) for k in STAGES]},indent=2))
if __name__=="__main__":main()
