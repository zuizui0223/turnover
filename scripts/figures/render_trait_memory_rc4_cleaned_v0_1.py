#!/usr/bin/env python3
"""RC4 source-linked figures from the recovered, validation-gated 201-system Stage B table.

This script DOES NOT estimate new ecological effects, fit models or search for significance.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"results/trait_memory_positive_only_cleaning_impact_v0_2"

def figure_save(fig,out,stem):
    fig.savefig(out/(stem+".svg"),bbox_inches="tight")
    fig.savefig(out/(stem+".png"),bbox_inches="tight",dpi=220)
    plt.close(fig)

def main(dest):
    d=json.loads((DATA/"result.json").read_text(encoding="utf-8"))
    with (DATA/"effects_positive_only_cleaned_recovered_v0_2.csv").open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    assert d["status"]=="TRAIT_MEMORY_POSITIVE_ONLY_CLEANING_IMPACT_COMPLETE"
    assert len(rows)==201
    assert sum(r["cleaning_status"]=="CLEANED_STAGE_B" for r in rows)==49
    assert sum(r["cleaning_status"]=="CLEAN_UNCHANGED_STAGE_A" for r in rows)==152
    dest.mkdir(parents=True,exist_ok=True)

    # Fig 1: source-correction and source-effect identity (not selection/causal effects).
    fig,axs=plt.subplots(1,2,figsize=(10.0,4.6),sharex=True,sharey=True)
    for ax,axis,name in zip(axs,["S3","prune"],["S3 phylogeny","Prune-only phylogeny"]):
        base=np.asarray([float(r[f"original_{axis}_raw_rho"]) for r in rows])
        new=np.asarray([float(r[f"{axis}_raw_rho"]) for r in rows])
        changed=np.asarray([r["cleaning_status"]=="CLEANED_STAGE_B" for r in rows])
        limits=(min(-.2,float(base.min()),float(new.min()))-.015,max(.8,float(base.max()),float(new.max()))+.015)
        ax.plot(limits,limits,linestyle="--",linewidth=1,label="Identity")
        ax.scatter(base[~changed],new[~changed],s=20,alpha=.50,label="152 unchanged")
        ax.scatter(base[changed],new[changed],s=23,alpha=.80,label="49 corrected")
        ax.set_xlim(*limits);ax.set_ylim(*limits)
        ax.set_aspect("equal",adjustable="box")
        ax.set_title(name)
        ax.set_xlabel("Original uncorrected rho")
        ax.text(.03,.95,"n = 201",transform=ax.transAxes,va="top")
    axs[0].set_ylabel("Corrected positive-only rho")
    axs[0].legend(frameon=False,loc="lower right",fontsize=8)
    fig.suptitle("Figure 1. Data-validity correction preserves most system gradients",fontsize=11)
    figure_save(fig,dest,"Fig1_source_correction_identity")

    # Fig 2: matched study geometry and model estimate, without attaching a 500-bootstrap CI to the wrong estimand.
    fig,ax=plt.subplots(figsize=(9,5.0))
    fig.subplots_adjust(top=.72,bottom=.15)
    series=[]
    for scale in ["cleaned_raw","cleaned_log"]:
        for axis in ["S3_total_point_shares","prune_total_point_shares"]:
            shares=d[scale]["measurement_aware"][axis]
            vals=[shares[k] for k in ["family","trait","system_heterogeneity","sampling_error"]]
            assert math.isclose(sum(vals),1,rel_tol=0,abs_tol=1e-9)
            series.append(vals)
    arr=np.asarray(series)
    labels=["Raw / S3","Raw / prune","Log / S3","Log / prune"]
    xx=np.arange(4);bottom=np.zeros(4)
    names=["Family","Trait","System heterogeneity","Sampling error"]
    hatches=["","..","//","xx"]
    for j,component in enumerate(names):
        ax.bar(xx,arr[:,j]*100,bottom=bottom*100,label=component,
               edgecolor="black",linewidth=.5,hatch=hatches[j])
        bottom+=arr[:,j]
    ax.set_xticks(xx,labels);ax.set_ylabel("Typical total variance (point share, %)")
    ax.set_ylim(0,100)
    ax.legend(loc="lower center",bbox_to_anchor=(.5,1.01),frameon=False,fontsize=8,ncol=4)
    ax.set_title("Figure 2. Family context remains; sampling error is substantial",loc="left",fontsize=11,y=1.27)
    fig.text(.02,.02,"Point estimates only; 500-refit component-share intervals overlap. No dominance test.",fontsize=8)
    figure_save(fig,dest,"Fig2_measurement_aware_point_shares")

    # Fig 3: use the exact same held-out-family BLUP definition on both source-verified scales.
    fig,ax=plt.subplots(figsize=(8,4.6))
    raw=[d["cleaned_raw"]["portability"][axis]["gain_blup"]*100 for axis in ["S3","prune_only"]]
    logs=[d["cleaned_log"]["portability"][axis]["gain_blup"]*100 for axis in ["S3","prune_only"]]
    xx=np.arange(2);w=.32
    a=ax.bar(xx-w/2,raw,width=w,label="Raw states",edgecolor="black",linewidth=.6)
    b=ax.bar(xx+w/2,logs,width=w,label="Log states",edgecolor="black",linewidth=.6,hatch="//")
    ax.axhline(0,linestyle="--",linewidth=.9)
    ax.set_xticks(xx,["S3","Prune-only"]);ax.set_ylabel("Held-out-family BLUP SSE gain (%)")
    ax.set_ylim(min(-.5,min(raw+logs)-.8),max(raw+logs)+1.1)
    for bars in (a,b):
        for bar in bars:
            v=bar.get_height();ax.text(bar.get_x()+bar.get_width()/2,v+(.2 if v>=0 else -.4),
                                     f"{v:+.2f}%",ha="center",fontsize=9)
    ax.legend(frameon=False)
    ax.set_title("Figure 3. Trait portability is scale-dependent",loc="left",fontsize=11)
    fig.text(.02,.02,"Descriptive predictive gains; no new raw-versus-log significance test.",fontsize=8)
    figure_save(fig,dest,"Fig3_raw_vs_log_trait_portability")

    outputs=sorted(p.name for p in dest.iterdir() if p.suffix in (".png",".svg"))
    manifest={
      "status":"RC4_FIGURES_DERIVED_ONLY_FROM_FROZEN_STAGE_B",
      "source_table":"effects_positive_only_cleaned_recovered_v0_2.csv",
      "recovered_systems":201,
      "corrected_systems":49,
      "unchanged_systems":152,
      "source_original_action_runs":[37281031394,37443037590],
      "no_new_inferential_model":True,
      "no_new_significance_tests":True,
      "figure_files":outputs,
      "submission_ready":False
    }
    (dest/"rc4_figures_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,sort_keys=True))

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",type=Path,required=True)
    args=ap.parse_args()
    main(args.out_dir)
