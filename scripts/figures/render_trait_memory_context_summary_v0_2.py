#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_effects(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 201:
        raise RuntimeError(f"expected 201 systems, found {len(rows)}")
    return rows


def figure1(rows, out_dir: Path):
    families = sorted({r["family"] for r in rows})
    traits = sorted({r["trait_name"] for r in rows})
    fi = {v: i for i, v in enumerate(families)}
    ti = {v: i for i, v in enumerate(traits)}
    mat = np.zeros((len(families), len(traits)), dtype=float)
    for r in rows:
        mat[fi[r["family"]], ti[r["trait_name"]]] = 1.0

    fig, ax = plt.subplots(figsize=(10.5, 13.5))
    ax.imshow(mat, aspect="auto", interpolation="nearest")
    ax.set_xticks(range(len(traits)))
    ax.set_xticklabels(traits, rotation=55, ha="right", fontsize=8)
    ax.set_yticks(range(len(families)))
    ax.set_yticklabels(families, fontsize=7)
    ax.set_xlabel("Trait")
    ax.set_ylabel("Plant family")
    ax.set_title("Prospectively qualified crossed family × trait design\n201 systems, 45 families, 12 traits")
    fig.tight_layout()
    fig.savefig(out_dir / "figure1_crossed_design.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "figure1_crossed_design.pdf", bbox_inches="tight")
    plt.close(fig)


def figure3(repeatability, portability, lineage, out_dir: Path):
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3))

    # Panel A: repeatability decomposition.
    ax = axes[0]
    labels = ["Family", "Trait", "Residual /\nsystem-level"]
    est = [
        repeatability["primary_S3"]["R_family"],
        repeatability["primary_S3"]["R_trait"],
        repeatability["primary_S3"]["R_residual"],
    ]
    ci = [
        repeatability["bootstrap"]["ci95"]["R_family"],
        repeatability["bootstrap"]["ci95"]["R_trait"],
        repeatability["bootstrap"]["ci95"]["R_residual"],
    ]
    prune = [
        repeatability["prune_only_sensitivity"]["R_family"],
        repeatability["prune_only_sensitivity"]["R_trait"],
        repeatability["prune_only_sensitivity"]["R_residual"],
    ]
    y = np.arange(3)
    lo = np.array(est) - np.array([x[0] for x in ci])
    hi = np.array([x[1] for x in ci]) - np.array(est)
    ax.errorbar(est, y, xerr=np.vstack([lo, hi]), fmt="o", capsize=3, label="S3")
    ax.scatter(prune, y, marker="x", label="Prune-only")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    ax.set_xlabel("Repeatability / residual share")
    ax.set_title("A  Crossed decomposition")
    ax.legend(frameon=False, fontsize=8)

    # Panel B: portability gain relative to null distribution.
    ax = axes[1]
    labels2 = ["S3", "Prune-only"]
    gains = [portability["S3"]["gain"], portability["prune_only"]["gain"]]
    qlo = [portability["S3"]["null_q025"], portability["prune_only"]["null_q025"]]
    qhi = [portability["S3"]["null_q975"], portability["prune_only"]["null_q975"]]
    y2 = np.arange(2)
    for i in range(2):
        ax.plot([qlo[i], qhi[i]], [y2[i], y2[i]], linewidth=3)
        ax.scatter([gains[i]], [y2[i]], marker="o")
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.set_yticks(y2)
    ax.set_yticklabels(labels2)
    ax.invert_yaxis()
    ax.set_xlabel("Portability gain")
    ax.set_title("B  Held-out-family portability")
    ax.text(gains[0], y2[0] + 0.22, f"p={portability['S3']['p_value']:.3f}", ha="center", fontsize=8)
    ax.text(gains[1], y2[1] + 0.22, f"p={portability['prune_only']['p_value']:.3f}", ha="center", fontsize=8)

    # Panel C: conditional family repeatability.
    ax = axes[2]
    est3 = lineage["primary_S3"]["conditional_family_repeatability"]
    ci3 = lineage["bootstrap"]["ci95_conditional_family_repeatability"]
    prune3 = lineage["prune_only_sensitivity"]["conditional_family_repeatability"]
    ax.errorbar(
        [est3], [0],
        xerr=[[est3 - ci3[0]], [ci3[1] - est3]],
        fmt="o", capsize=3, label="S3"
    )
    ax.scatter([prune3], [0], marker="x", label="Prune-only")
    ax.axvline(lineage["practical_reference"], linestyle="--", linewidth=1)
    ax.set_yticks([0])
    ax.set_yticklabels(["Family context"])
    ax.set_xlim(0, max(0.4, ci3[1] + 0.04))
    ax.set_xlabel("Conditional family repeatability")
    ax.set_title("C  Cross-trait lineage context")
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle("Triangulation of trait portability and family-level context", y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / "figure3_triangulation.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "figure3_triangulation.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--effects", type=Path, required=True)
    ap.add_argument("--repeatability", type=Path, required=True)
    ap.add_argument("--portability", type=Path, required=True)
    ap.add_argument("--lineage", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_effects(a.effects)
    repeatability = json.loads(a.repeatability.read_text())
    portability = json.loads(a.portability.read_text())
    lineage = json.loads(a.lineage.read_text())

    figure1(rows, a.out_dir)
    figure3(repeatability, portability, lineage, a.out_dir)

    print(json.dumps({
        "status": "TRAIT_MEMORY_CONTEXT_SUMMARY_FIGURES_RENDERED",
        "outputs": [
            "figure1_crossed_design.png",
            "figure1_crossed_design.pdf",
            "figure3_triangulation.png",
            "figure3_triangulation.pdf",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
