#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

ap=argparse.ArgumentParser()
ap.add_argument("--data-dir",type=Path,required=True)
ap.add_argument("--out-dir",type=Path,required=True)
a=ap.parse_args()
a.out_dir.mkdir(parents=True,exist_ok=True)

BLUE="#315C85"
ORANGE="#C46A2D"
DARK="#2B2B2B"
MID="#7A7A7A"
LIGHT="#E8E8E8"
PALE="#F5F5F5"

plt.rcParams.update({
    "font.family":"DejaVu Sans",
    "font.size":9,
    "axes.titlesize":10,
    "axes.labelsize":9,
    "svg.fonttype":"none"
})

def read_csv(name):
    with (a.data_dir/name).open(newline="") as f:
        return list(csv.DictReader(f))

def save(fig,name):
    fig.savefig(a.out_dir/name,bbox_inches="tight",transparent=False)
    plt.close(fig)

# Figure 1
rec=read_csv("fig1_recovery.csv")
fig=plt.figure(figsize=(7.2,3.6))
gs=fig.add_gridspec(1,2,width_ratios=[1.45,1],wspace=0.32)
ax=fig.add_subplot(gs[0,0]); ax.axis("off")
labels=["Declared\ntarget","Structurally\nrealizable","Generator-\naccessible","Recoverable"]
xs=[0.11,0.37,0.63,0.89]
for i,(x,lbl) in enumerate(zip(xs,labels)):
    fc=PALE if i==0 else "white"
    ax.add_patch(patches.FancyBboxPatch((x-0.080,0.38),0.16,0.24,
        boxstyle="round,pad=0.02,rounding_size=0.02",facecolor=fc,edgecolor=DARK,linewidth=1.2))
    ax.text(x,0.50,lbl,ha="center",va="center",fontsize=8.3)
    if i<3:
        ax.annotate("",xy=(xs[i+1]-0.090,0.50),xytext=(x+0.090,0.50),
                    arrowprops=dict(arrowstyle="->",lw=1.3,color=DARK))
for x,txt in zip(xs[1:],["Gate 1","Gate 2","Gate 3"]):
    ax.text(x,0.68,txt,ha="center",va="bottom",fontsize=8,color=MID)
ax.text(0.50,0.18,"Failure at an earlier gate cannot be interpreted as downstream low power",
        ha="center",va="center",fontsize=7.8,color=DARK)
ax.set_title("A  Known truth must first be assignable",loc="left",fontweight="bold")

ax=fig.add_subplot(gs[0,1])
names=[r["representation"] for r in rec]
rates=[float(r["rate"])*100 for r in rec]
tot=[int(r["total"]) for r in rec]
got=[int(r["recovered"]) for r in rec]
bars=ax.barh([1,0],rates,color=[BLUE,ORANGE],edgecolor=DARK,linewidth=0.8)
ax.set_xlim(0,65); ax.set_xlabel("Known-truth recovery (%)")
ax.set_yticks([1,0],labels=names)
ax.grid(axis="x",color=LIGHT,linewidth=0.7)
ax.set_axisbelow(True)
for bar,rate,n,d in zip(bars,rates,got,tot):
    ax.text(rate+1.2,bar.get_y()+bar.get_height()/2,f"{n}/{d}\n{rate:.1f}%",va="center",fontsize=8.5)
ax.spines[["top","right"]].set_visible(False)
ax.set_title("B  Equal target, unequal recoverability",loc="left",fontweight="bold")
fig.suptitle("Figure 1. Known truth passes three distinct gates before recovery",x=0.02,ha="left",fontsize=11,fontweight="bold")
save(fig,"Fig1_truth_assignability.svg")

# Figure 2
acc=read_csv("fig2_accessibility.csv")
vals={r["quantity"]:float(r["value"]) for r in acc}
fig=plt.figure(figsize=(7.2,3.6))
gs=fig.add_gridspec(1,2,wspace=0.34)
ax=fig.add_subplot(gs[0,0])
x=[0,1]
y=[vals["Median max edge-split rho"],vals["Median max OU-grid rho"]]
ax.bar(x,y,color=[BLUE,ORANGE],edgecolor=DARK,linewidth=0.8,width=0.62)
ax.axhline(vals["Target rho"],color=DARK,linestyle="--",linewidth=1.1)
ax.text(0.05,vals["Target rho"]+0.012,"target ρ = 0.15",ha="left",va="bottom",fontsize=8)
ax.set_xticks(x,["Realizable\none-edge split","Latent-OU\ngrid"])
ax.set_ylabel("Median maximum ρ")
ax.set_ylim(0,0.86)
ax.grid(axis="y",color=LIGHT,linewidth=0.7); ax.set_axisbelow(True)
for xx,yy in zip(x,y):
    if xx==1:
        ax.text(xx,yy*0.52,f"{yy:.3f}",ha="center",va="center",fontsize=8.5,color="white",fontweight="bold")
    else:
        ax.text(xx,yy+0.025,f"{yy:.3f}",ha="center",fontsize=9)
ax.spines[["top","right"]].set_visible(False)
ax.set_title("A  State space contains the target",loc="left",fontweight="bold")

ax=fig.add_subplot(gs[0,1])
effect=int(vals["Effect ceiling"]); collapse=int(vals["Validity collapse"]); total=effect+collapse
ax.barh([0],[effect/total*100],color=ORANGE,edgecolor=DARK,linewidth=0.8,label="Effect ceiling")
ax.barh([0],[collapse/total*100],left=[effect/total*100],color="white",edgecolor=DARK,linewidth=0.8,hatch="////",label="Validity collapse")
ax.set_xlim(0,104); ax.set_yticks([])
ax.set_xlabel("OU no-bracket systems (%)")
ax.text(effect/total*50,0,f"{effect}/220\n88.6%",ha="center",va="center",color="white",fontweight="bold",fontsize=9)
ax.text(effect/total*100+(collapse/total*50),0,f"{collapse}/220\n11.4%",ha="center",va="center",fontsize=8.5)
ax.legend(frameon=False,loc="upper center",bbox_to_anchor=(0.5,-0.18),ncol=1,fontsize=8)
ax.spines[["top","right","left"]].set_visible(False)
ax.set_title("B  Failure lies inside generator accessibility",loc="left",fontweight="bold")
fig.suptitle("Figure 2. Binary state space is not the observed calibration ceiling",x=0.02,ha="left",fontsize=11,fontweight="bold")
save(fig,"Fig2_accessibility_mechanism.svg")

# Figure 3
seq=read_csv("fig3_sequential.csv")
paired=read_csv("fig3_paired.csv")
reco=read_csv("fig3_recovery.csv")
fig=plt.figure(figsize=(7.2,5.9))
gs=fig.add_gridspec(2,2,height_ratios=[1.15,1],hspace=0.68,wspace=0.48)

ax=fig.add_subplot(gs[0,:])
stages=[r["stage"] for r in seq]
mid=np.array([float(r["no_bracket_rate"])*100 for r in seq])
lo=np.array([float(r["lower"])*100 for r in seq])
hi=np.array([float(r["upper"])*100 for r in seq])
xx=np.arange(len(stages))
ax.plot(xx,mid,marker="o",linewidth=1.8,color=BLUE)
ax.errorbar(xx,mid,yerr=np.vstack([mid-lo,hi-mid]),fmt="none",ecolor=DARK,capsize=4,linewidth=1.2)
ax.set_xticks(xx,stages)
ax.set_ylabel("No-bracket systems (%)")
ax.set_ylim(0,90)
ax.grid(axis="y",color=LIGHT,linewidth=0.7); ax.set_axisbelow(True)
for x0,y0,l0,h0 in zip(xx,mid,lo,hi):
    lab=f"{y0:.1f}%" if abs(h0-l0)<1e-9 else f"{l0:.1f}–{h0:.1f}%"
    ax.text(x0,y0+5,lab,ha="center",fontsize=9)
ax.spines[["top","right"]].set_visible(False)
ax.set_title("A  Accessibility improves sequentially, but a large remainder persists",loc="left",fontweight="bold")

ax=fig.add_subplot(gs[1,0])
labels=[r["transition"] for r in paired]
resc=[int(r["rescued"]) for r in paired]
loss=[int(r["new_failure"]) for r in paired]
y=np.arange(len(labels))
ax.barh(y,resc,color=BLUE,edgecolor=DARK,linewidth=0.8,label="Rescued")
ax.barh(y,[-x for x in loss],color="white",edgecolor=DARK,linewidth=0.8,hatch="////",label="New failure")
ax.axvline(0,color=DARK,linewidth=0.9)
ax.set_yticks(y,labels)
ax.set_xlabel("Paired systems")
lim=max(max(resc)+7,10); ax.set_xlim(-lim*0.25,lim)
for yy,n in zip(y,resc): ax.text(n+1,yy,str(n),va="center",fontsize=9)
for yy,n in zip(y,loss):
    if n: ax.text(-n-1,yy,str(n),ha="right",va="center",fontsize=9)
    else: ax.text(-0.8,yy,"0",ha="right",va="center",fontsize=9)
ax.text(0.02,0.98,"← new failures",transform=ax.transAxes,ha="left",va="top",fontsize=7.8,color=MID)\nax.text(0.98,0.98,"rescued →",transform=ax.transAxes,ha="right",va="top",fontsize=7.8,color=BLUE)
ax.spines[["top","right"]].set_visible(False)
ax.set_title("B  Paired rescues exceed new failures",loc="left",fontweight="bold")

ax=fig.add_subplot(gs[1,1])
d={r["outcome"]:int(r["n"]) for r in reco}
total=sum(d.values())
ax.barh([0],[d["PASS"]/total*100],color=BLUE,edgecolor=DARK,linewidth=0.8)
ax.barh([0],[d["Recovery fail"]/total*100],left=[d["PASS"]/total*100],color="white",edgecolor=DARK,linewidth=0.8,hatch="////")
ax.set_xlim(0,100); ax.set_yticks([])
ax.set_xlabel("Mk2-calibrated systems (%)")
ax.text(d["PASS"]/total*50,0,f"PASS\n{d['PASS']}/106",ha="center",va="center",color="white",fontweight="bold")
ax.text(d["PASS"]/total*100+d["Recovery fail"]/total*50,0,f"Recovery fail\n{d['Recovery fail']}/106",ha="center",va="center",fontsize=8.5)
ax.spines[["top","right","left"]].set_visible(False)
ax.set_title("C  Assignment does not ensure recovery",loc="left",fontweight="bold")

fig.suptitle("Figure 3. Generator choice, state balance and recovery are separable bottlenecks",x=0.02,ha="left",fontsize=11,fontweight="bold")
save(fig,"Fig3_sequential_rescue.svg")
