#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TRAIT_ORDER = [
    "diameter at breast height (1.3 m)",
    "leaf area",
    "leaf area per leaf dry mass",
    "leaf dry mass",
    "leaf dry mass per leaf fresh mass",
    "leaf nitrogen content per leaf area",
    "leaf nitrogen content per leaf dry mass",
    "leaf phosphorus content per leaf dry mass",
    "maximum whole plant height",
    "seed mass",
    "stem wood density",
    "whole plant height",
]


def load_json(path: Path):
    return json.loads(path.read_text())


def save(fig, outdir: Path, stem: str):
    fig.savefig(outdir / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(outdir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(outdir / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig1_qualification(outdir: Path):
    labels = [
        "Temporal support",
        "Semantic validity",
        "Phylogeny crosswalk",
        "Pre-informativeness core",
        "Informativeness PASS",
        "Final crossed core",
    ]
    systems = [1455, 1219, 802, 722, 255, 201]
    families = [240, 219, 160, 120, 70, 45]
    traits = [49, 47, 47, 25, 22, 12]

    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.barh(y, systems)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Family × trait systems")
    ax.set_title("Outcome-blind qualification of the temporal trait-memory core")
    for i, (s, f, t) in enumerate(zip(systems, families, traits)):
        ax.text(s + max(systems) * 0.015, i, f"{s:,} systems | {f} families | {t} traits",
                va="center", fontsize=9)
    ax.set_xlim(0, max(systems) * 1.42)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, outdir, "fig1_qualification")


def fig2_heatmap(df: pd.DataFrame, outdir: Path):
    families = sorted(df["family"].unique())
    present_traits = [t for t in TRAIT_ORDER if t in set(df["trait_name"])]
    mat = df.pivot(index="family", columns="trait_name", values="S3_rho").reindex(
        index=families, columns=present_traits
    )

    masked = np.ma.masked_invalid(mat.to_numpy(dtype=float))
    fig, ax = plt.subplots(figsize=(11.0, 12.0))
    im = ax.imshow(masked, aspect="auto", interpolation="nearest", cmap="coolwarm",
                   vmin=-0.35, vmax=0.75)
    ax.set_yticks(np.arange(len(families)), families, fontsize=7)
    ax.set_xticks(np.arange(len(present_traits)), present_traits, rotation=55, ha="right", fontsize=8)
    ax.set_title("Phylogenetic memory-loss strength across the fixed 201-system core")
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("S3 memory-loss Spearman ρ")
    ax.set_xlabel("Trait")
    ax.set_ylabel("Plant family (alphabetical)")
    fig.tight_layout()
    save(fig, outdir, "fig2_memory_heatmap")


def fig3_backbone(df: pd.DataFrame, outdir: Path, synthesis: dict):
    x = df["S3_rho"].to_numpy(float)
    y = df["prune_only_rho"].to_numpy(float)
    lo = min(x.min(), y.min()) - 0.03
    hi = max(x.max(), y.max()) + 0.03

    fig, ax = plt.subplots(figsize=(6.0, 5.6))
    ax.scatter(x, y, s=22, alpha=0.75)
    ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("S3 memory-loss ρ")
    ax.set_ylabel("Prune-only memory-loss ρ")
    ax.set_title("Memory estimates are concordant across phylogenetic treatments")
    corr = synthesis["descriptive_memory_distribution"]["S3_prune_only_correspondence"]
    ax.text(0.04, 0.95,
            f"Pearson r = {corr['pearson']:.3f}\nSpearman ρ = {corr['spearman']:.3f}\nn = {len(df)}",
            transform=ax.transAxes, va="top")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, outdir, "fig3_backbone_concordance")


def fig4_triangulation(outdir: Path, repeat: dict, portability: dict, lineage: dict):
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))

    # Panel A: repeatability shares.
    ax = axes[0]
    names = ["Family", "Trait", "Residual"]
    vals = [
        repeat["primary_S3"]["R_family"],
        repeat["primary_S3"]["R_trait"],
        repeat["primary_S3"]["R_residual"],
    ]
    cis = [
        repeat["bootstrap"]["ci95"]["R_family"],
        repeat["bootstrap"]["ci95"]["R_trait"],
        repeat["bootstrap"]["ci95"]["R_residual"],
    ]
    y = np.arange(3)
    xerr = np.array([[v - ci[0] for v, ci in zip(vals, cis)],
                     [ci[1] - v for v, ci in zip(vals, cis)]])
    ax.errorbar(vals, y, xerr=xerr, fmt="o", capsize=3)
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("Repeatability share")
    ax.set_title("A  Crossed repeatability")
    ax.spines[["top", "right"]].set_visible(False)

    # Panel B: held-out-family portability.
    ax = axes[1]
    axes_names = ["S3", "Prune-only"]
    vals = [portability["S3"]["gain"], portability["prune_only"]["gain"]]
    qlo = [portability["S3"]["null_q025"], portability["prune_only"]["null_q025"]]
    qhi = [portability["S3"]["null_q975"], portability["prune_only"]["null_q975"]]
    y = np.arange(2)
    ax.errorbar(vals, y,
                xerr=np.array([[v-lo for v,lo in zip(vals,qlo)],
                               [hi-v for v,hi in zip(vals,qhi)]]),
                fmt="o", capsize=3)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.set_yticks(y, axes_names)
    ax.invert_yaxis()
    ax.set_xlabel("Portability gain")
    ax.set_title("B  Held-out-family prediction")
    ax.text(0.04, 0.06,
            f"S3 p = {portability['S3']['p_value']:.3f}\n"
            f"Prune p = {portability['prune_only']['p_value']:.3f}",
            transform=ax.transAxes, va="bottom")
    ax.spines[["top", "right"]].set_visible(False)

    # Panel C: conditional family repeatability.
    ax = axes[2]
    est = lineage["primary_S3"]["conditional_family_repeatability"]
    ci = lineage["bootstrap"]["ci95_conditional_family_repeatability"]
    ax.errorbar([est], [0], xerr=[[est-ci[0]], [ci[1]-est]], fmt="o", capsize=3)
    ax.axvline(lineage["practical_reference"], linestyle="--", linewidth=1)
    ax.set_yticks([0], ["Family | trait means"])
    ax.set_xlim(0, max(0.4, ci[1] + 0.04))
    ax.set_xlabel("Conditional family repeatability")
    ax.set_title("C  Recurring family context")
    ax.text(0.04, 0.06,
            f"Prune-only = {lineage['prune_only_sensitivity']['conditional_family_repeatability']:.3f}\n"
            "Dashed line = predeclared 0.10 reference",
            transform=ax.transAxes, va="bottom")
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    save(fig, outdir, "fig4_triangulation")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--effects", type=Path, required=True)
    p.add_argument("--repeatability", type=Path, required=True)
    p.add_argument("--portability", type=Path, required=True)
    p.add_argument("--lineage", type=Path, required=True)
    p.add_argument("--synthesis", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    a = p.parse_args()

    a.outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(a.effects)
    assert len(df) == 201
    assert df["family"].nunique() == 45
    assert df["trait_name"].nunique() == 12
    assert set(df["trait_name"]) == set(TRAIT_ORDER)

    repeat = load_json(a.repeatability)
    portability = load_json(a.portability)
    lineage = load_json(a.lineage)
    synthesis = load_json(a.synthesis)

    fig1_qualification(a.outdir)
    fig2_heatmap(df, a.outdir)
    fig3_backbone(df, a.outdir, synthesis)
    fig4_triangulation(a.outdir, repeat, portability, lineage)


if __name__ == "__main__":
    main()
