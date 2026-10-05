#!/usr/bin/env python3
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.
from __future__ import annotations
import argparse,csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ap=argparse.ArgumentParser()
ap.add_argument("--data-dir",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
a=ap.parse_args()
a.out_dir.mkdir(parents=True,exist_ok=True)

plt.rcParams.update({
    "font.family":"DejaVu Sans",
    "font.size":9,
    "axes.titlesize":10,
    "axes.labelsize":9,
    "svg.fonttype":"none"
})

def read(name):
    with (a.data_dir/name).open(newline="") as fh:
        return list(csv.DictReader(fh))

def save(fig,name):
    fig.savefig(a.out_dir/name,bbox_inches="tight")
    plt.close(fig)

# ---------- Figure 1 ----------
var=read("figure1_variance_shares.csv")
het=read("figure1_heterogeneity_ci.csv")
fig=plt.figure(figsize=(10.2,4.0))
gs=fig.add_gridspec(1,3,width_ratios=[1.05,1.0,1.05],wspace=0.58)

component_order={
    "naive":["family","trait","residual_unresolved"],
    "measurement_aware":["family","trait","system_heterogeneity","sampling_error"]
}
hatches={
    "family":"",
    "trait":"..",
    "residual_unresolved":"//",
    "system_heterogeneity":"//",
    "sampling_error":"xx"
}

def stacked(ax,axis,title,show_ylabels=True):
    y=[1,0]
    models=["naive","measurement_aware"]
    labels=["Original lmer","Measurement-aware"]
    for yy,model,label in zip(y,models,labels):
        left=0.0
        for comp in component_order[model]:
            r=next(z for z in var if z["axis"]==axis and z["model"]==model and z["component"]==comp)
            v=float(r["estimate"])
            ax.barh([yy],[v*100],left=[left*100],height=.52,
                    hatch=hatches[comp],edgecolor="black",linewidth=.7)
            if v>=.10:
                ax.text((left+v/2)*100,yy,f"{v*100:.0f}%",ha="center",va="center",fontsize=8)
            left+=v
    if show_ylabels:
        ax.set_yticks(y,labels)
    else:
        ax.set_yticks(y,["",""])
    ax.set_xlim(0,100)
    ax.set_xlabel("Variance share (%)")
    ax.set_title(title,loc="left",fontweight="bold")
    ax.spines[["top","right"]].set_visible(False)

ax=fig.add_subplot(gs[0,0])
stacked(ax,"S3","A  S3 point decomposition")

ax=fig.add_subplot(gs[0,1])
names=["family","trait","system"]
points=np.array([float(next(z for z in het if z["component"]==n)["estimate"]) for n in names])
lo=np.array([float(next(z for z in het if z["component"]==n)["lo"]) for n in names])
hi=np.array([float(next(z for z in het if z["component"]==n)["hi"]) for n in names])
x=np.arange(3)
ax.errorbar(x,points,yerr=np.vstack([points-lo,hi-points]),fmt="o",capsize=4,linewidth=1.2)
ax.set_xticks(x,["Family","Trait","System"])
ax.set_ylim(0,0.82)
ax.set_ylabel("Share of between-system heterogeneity")
ax.set_title("B  Heterogeneity uncertainty",loc="left",fontweight="bold")
ax.spines[["top","right"]].set_visible(False)
for xx,p in zip(x,points):
    ax.text(xx,p+.035,f"{p:.2f}",ha="center",fontsize=8)

ax=fig.add_subplot(gs[0,2])
stacked(ax,"prune_only","C  Prune-only decomposition",show_ylabels=False)

fig.suptitle("Figure 1. Sampling error accounts for a substantial part of apparent cell-level variation",
             x=.02,y=.98,ha="left",fontsize=10.5,fontweight="bold")
save(fig,"Fig1_measurement_error_decomposition.svg")

# ---------- Figure 2 ----------
null=read("figure2_correlated_trait_null.csv")
rob=read("figure2_family_robustness.csv")
fig=plt.figure(figsize=(8.6,3.9))
gs=fig.add_gridspec(1,2,wspace=.42)

ax=fig.add_subplot(gs[0,0])
for i,r in enumerate(null):
    med=float(r["null_median"]); lo=float(r["lo"]); hi=float(r["hi"]); obs=float(r["observed"])
    ax.plot([lo,hi],[i,i],linewidth=5,solid_capstyle="butt")
    ax.plot(med,i,"o",markersize=6)
    ax.plot(obs,i,"D",markersize=6)
    ax.text(obs+.008,i,f"obs {obs:.3f}\np={float(r['p']):.3f}",va="center",fontsize=8)
ax.set_yticks(range(len(null)),["S3","Prune-only"])
ax.set_xlim(0,.19)
ax.set_xlabel("Family repeatability")
ax.set_title("A  Observed family component exceeds null",loc="left",fontweight="bold")
ax.spines[["top","right"]].set_visible(False)

ax=fig.add_subplot(gs[0,1])
labels=["Unadjusted","Species count","Geometry","Source","Citation","Five domains"]
vals=[float(r["R_family"]) for r in rob]
xx=np.arange(len(vals))
ax.plot(xx,vals,marker="o",linewidth=1.2)
ax.axhline(vals[0],linestyle="--",linewidth=.8)
ax.set_xticks(xx,labels,rotation=42,ha="right")
ax.set_ylim(.13,.16)
ax.set_ylabel("S3 family repeatability")
ax.set_title("B  Family component is stable to audits",loc="left",fontweight="bold")
ax.spines[["top","right"]].set_visible(False)
for x0,v in zip(xx,vals):
    ax.text(x0,v+.0009,f"{v:.3f}",ha="center",fontsize=7.5)

fig.suptitle("Figure 2. Correlated traits and measured design artifacts do not explain the family component",
             x=.02,y=.98,ha="left",fontsize=10.5,fontweight="bold")
fig.text(.035,.02,"Panel A: thick line = null 95% interval; circle = null median; diamond = observed",fontsize=7.2)
save(fig,"Fig2_family_repeatability_robustness.svg")

# ---------- Figure 3 ----------
port=read("figure3_portability.csv")
tv=read("figure3_training_variance.csv")
fig=plt.figure(figsize=(9.8,4.25))
gs=fig.add_gridspec(1,3,width_ratios=[1.0,1.0,1.35],wspace=.44)

ax=fig.add_subplot(gs[0,0])
axes=["S3","prune_only"]
preds=["unshrunk","BLUP"]
width=.34
for k,pred in enumerate(preds):
    vals=[float(next(r for r in port if r["axis"]==axis and r["predictor"]==pred)["gain"]) for axis in axes]
    ax.bar(np.arange(2)+(k-.5)*width,vals,width=width,edgecolor="black",linewidth=.7,hatch="" if pred=="BLUP" else "//",label=pred)
ax.axhline(0,linewidth=.9)
ax.set_xticks(np.arange(2),["S3","Prune-only"])
ax.set_ylabel("Portability gain")
ax.set_ylim(-.04,.015)
ax.legend(frameon=False,fontsize=8)
ax.set_title("A  Portability gain",loc="left",fontweight="bold")
ax.spines[["top","right"]].set_visible(False)

ax=fig.add_subplot(gs[0,1])
for k,comp in enumerate(["trait","residual"]):
    vals=[float(next(r for r in tv if r["axis"]==axis and r["component"]==comp)["variance"]) for axis in axes]
    ax.bar(np.arange(2)+(k-.5)*width,vals,width=width,edgecolor="black",linewidth=.7,hatch=".." if comp=="trait" else "",label=comp)
ax.set_xticks(np.arange(2),["S3","Prune-only"])
ax.set_ylabel("Training variance")
ax.legend(frameon=False,fontsize=8)
ax.set_title("B  Training variance",loc="left",fontweight="bold")
ax.spines[["top","right"]].set_visible(False)

ax=fig.add_subplot(gs[0,2]); ax.axis("off")
items=[
    ("H1  Trait-intrinsic","Not supported","same trait → unseen family"),
    ("H2  Family-context","Modest support","same family → other traits"),
    ("H3  Deep inheritance","Not supported*","family context → deep phylogeny")
]
positions=[.80,.50,.20]
for (name,result,desc),y in zip(items,positions):
    ax.text(.02,y,name,fontweight="bold",fontsize=8.8,transform=ax.transAxes)
    ax.text(.02,y-.085,result,fontsize=8.5,transform=ax.transAxes)
    ax.text(.02,y-.165,desc,fontsize=7.3,transform=ax.transAxes)
ax.set_title("C  Generalization hierarchy",loc="left",fontweight="bold")

fig.suptitle("Figure 3. Trait identity carries little robust memory information across families",
             x=.02,y=.98,ha="left",fontsize=10.5,fontweight="bold")
fig.text(.705,.02,"* H3 is a post-outcome complementary analysis",fontsize=7.0)
save(fig,"Fig3_portability_and_scale.svg")
