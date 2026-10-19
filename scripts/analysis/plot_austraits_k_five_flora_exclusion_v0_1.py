#!/usr/bin/env python3
"""Reproducible manuscript graphics for the 283-pair five-flora exclusion check.

Input is the signed, originally K-blind source-supported 283-pair final
aggregate, not species-level trait values. Graphs are descriptive post-
discovery robust comparisons and display family pair counts/holds.
Output PNG + vector SVG (not a new biological inference).
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STATUS="AUSTRAITS_K_FIVE_FLORA_EXCLUSION_ORGAN_SENSITIVITY_AGGREGATED_V0_1"


def validate(x):
    if x.get("status")!=STATUS or x.get("nonflora_supported_before_K_pairs")!=283:
        raise ValueError("not the finalized 283-pair flora removal K robustness result")
    if x.get("original_nonflora_supported_families")!=29:
        raise ValueError("unexpected source-eligible family cohort")
    if not x.get("not_external_TRY_v7_independent_source_validation"):
        raise ValueError("not original AusTraits-only exploratory study")
    if x.get("original_source_blind_pair_universe")!=760:
        raise ValueError("original K source universe changed")
    for ax in ("S3","prune_only"):
        s=x["axes"][ax]
        if s["n_preK_nonflora_qualified_pairs"]!=283 or (
          s["n_valid_real_tree_K_pairs"]+s["n_nonflora_median_or_phylo_K_holds"]!=283):
            raise ValueError("missing original frozen source-qualifying K pair")
        if s["nonflora_source_same_tips"] is None or s["full_sources_same_tips"] is None:
            raise ValueError("insufficient native K axis support to plot")
    return x


def draw_families(x,outdir):
    # Each point is one FAMILY, never a pseudo-independent pair replicate.
    A=x["axes"]["S3"]["individual_families"]
    B=x["axes"]["prune_only"]["individual_families"]
    names=sorted(set(A)|set(B),key=lambda f:(
         -(A.get(f,{"n_reproductive_win_nonflora":0,
                  "n_valid_pairs":0})["n_reproductive_win_nonflora"]/
           max(A.get(f,{"n_valid_pairs":0})["n_valid_pairs"],1)),f))
    if len(names)<20 or len(names)>29:raise ValueError("unexpected family status")
    fig,ax=plt.subplots(figsize=(9.7,max(9,0.34*len(names)+1.5)))
    h=np.arange(len(names))
    for axis,data,offset,label in (
        ("S3",A,-.12,"S3"),
        ("prune",B,+.12,"Prune-only")):
        rows=[data.get(f) for f in names]
        xx=np.array([r["n_reproductive_win_nonflora"]/r["n_valid_pairs"]
                     if r and r["n_valid_pairs"] else np.nan for r in rows])
        size=np.array([30+9*np.sqrt(r["n_valid_pairs"])
                    if r and r["n_valid_pairs"] else 0 for r in rows])
        idx=np.isfinite(xx)
        ax.scatter(xx[idx],(h+offset)[idx],s=size[idx],alpha=.82,label=label)
    ax.axvline(.5,ls="--",lw=1,color="0.4")
    ax.set_xlim(-.02,1.02)
    ax.set_yticks(h,labels=names)
    ax.invert_yaxis()
    ax.set_xlabel("Fraction of family trait-pairs with reproductive K > vegetative K")
    ax.set_title("After removing five electronic flora source archives\n"
                 "Exact same-species and same-tree phylogenetic K")
    ax.legend(title="Phylogenetic tree treatment",frameon=False)
    ax.grid(axis="x",alpha=.15)
    fig.tight_layout()
    fig.savefig(outdir/"figure_family_organ_K_without_floras.png",dpi=230)
    fig.savefig(outdir/"figure_family_organ_K_without_floras.svg")
    plt.close(fig)


def draw_pooled(x,outdir):
    fig,ax=plt.subplots(figsize=(8,5))
    entries=[]
    for axis in ("S3","prune_only"):
        for cond,key in (("All original sources, on nonflora tips","full_sources_same_tips"),
                         ("Five electronic flora archives excluded","nonflora_source_same_tips")):
            z=x["axes"][axis][key]
            entries.append((axis,cond,z["equal_family_mean_rate"],
                        z["family_bootstrap_equal_family_rate_CI95"],
                        z["n_valid_individual_family_pairs"],z["n_distinct_plant_families"]))
    for i,(axis,label,rate,ci,n,nf) in enumerate(entries):
        ax.errorbar(rate,3-i,xerr=np.asarray([[rate-ci[0]],[ci[1]-rate]]),
                    fmt="o",capsize=4,markersize=6,
                    label=axis if i%2==0 else None)
        ax.text(min(1,ci[1]+.02),3-i,f"{n} pairs, {nf} families",va="center",fontsize=8)
    ax.axvline(.5,color="0.4",linestyle="--")
    ax.set_xlim(0,1.12)
    ax.set_yticks([3,2,1,0],
        [f"{a}: {b}" for a,b,*_ in entries])
    ax.set_xlabel("Equal-family mean fraction reproductive K higher (bootstrap 95% CI)")
    ax.set_title("Does a K organ contrast survive removing major electronic floras?")
    ax.grid(axis="x",alpha=.15)
    fig.tight_layout()
    fig.savefig(outdir/"figure_organ_K_five_flora_exclusion_summary.png",dpi=230)
    fig.savefig(outdir/"figure_organ_K_five_flora_exclusion_summary.svg")
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    x=validate(json.loads(a.input.read_text()))
    a.out_dir.mkdir(parents=True,exist_ok=True)
    draw_families(x,a.out_dir)
    draw_pooled(x,a.out_dir)
    for path in a.out_dir.iterdir():
        if path.stat().st_size<200:
            raise ValueError("invalid plot artifact created: "+path.name)
    print("PASS: original K family-level and family-bootstrap source-exclusion figures",
         len(list(a.out_dir.iterdir())))

if __name__=="__main__":main()
