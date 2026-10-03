#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def read_effects(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 201:
        raise RuntimeError(f"expected 201 effects, found {len(rows)}")
    keys = {(r["family"], r["trait_name"]) for r in rows}
    if len(keys) != 201:
        raise RuntimeError("family x trait keys are not unique")
    for r in rows:
        r["S3_rho"] = float(r["S3_rho"])
        r["prune_only_rho"] = float(r["prune_only_rho"])
    return rows


def render_matrix(rows, out_png: Path, out_pdf: Path):
    families = sorted({r["family"] for r in rows})
    traits = sorted({r["trait_name"] for r in rows})
    fi = {x: i for i, x in enumerate(families)}
    ti = {x: i for i, x in enumerate(traits)}

    fig, ax = plt.subplots(figsize=(10.5, 13.5))
    x = [ti[r["trait_name"]] for r in rows]
    y = [fi[r["family"]] for r in rows]
    z = [r["S3_rho"] for r in rows]

    lim = max(abs(min(z)), abs(max(z)))
    sc = ax.scatter(x, y, c=z, vmin=-lim, vmax=lim, cmap="RdBu_r", s=38, linewidths=0.25)
    ax.set_xticks(range(len(traits)))
    ax.set_xticklabels(traits, rotation=55, ha="right", fontsize=8)
    ax.set_yticks(range(len(families)))
    ax.set_yticklabels(families, fontsize=7)
    ax.set_xlabel("Trait")
    ax.set_ylabel("Plant family")
    ax.set_title("Phylogenetic trait-memory gradient across the fixed 201 systems")
    ax.invert_yaxis()
    cb = fig.colorbar(sc, ax=ax, pad=0.015)
    cb.set_label("S3 memory-loss rho")
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)


def render_backbone(rows, synthesis_path: Path, out_png: Path, out_pdf: Path):
    synthesis = json.loads(synthesis_path.read_text())
    expected = synthesis["descriptive_memory_distribution"]["S3_prune_only_correspondence"]["spearman"]

    x = np.array([r["S3_rho"] for r in rows], dtype=float)
    y = np.array([r["prune_only_rho"] for r in rows], dtype=float)
    lo = min(float(x.min()), float(y.min()))
    hi = max(float(x.max()), float(y.max()))
    pad = 0.04 * (hi - lo)
    lo -= pad
    hi += pad

    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    ax.scatter(x, y, s=24, alpha=0.72)
    ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("S3 memory-loss rho")
    ax.set_ylabel("Prune-only memory-loss rho")
    ax.set_title(f"Backbone sensitivity across 201 systems\nSpearman correspondence = {expected:.3f}")
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--effects", type=Path, required=True)
    ap.add_argument("--synthesis", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = read_effects(args.effects)

    render_matrix(
        rows,
        args.out_dir / "figure2_memory_matrix.png",
        args.out_dir / "figure2_memory_matrix.pdf",
    )
    render_backbone(
        rows,
        args.synthesis,
        args.out_dir / "figure4_backbone_sensitivity.png",
        args.out_dir / "figure4_backbone_sensitivity.pdf",
    )

    print(json.dumps({
        "status": "TRAIT_MEMORY_CONTEXT_FIGURES_RENDERED",
        "n_systems": len(rows),
        "n_families": len({r["family"] for r in rows}),
        "n_traits": len({r["trait_name"] for r in rows}),
        "outputs": [
            "figure2_memory_matrix.png",
            "figure2_memory_matrix.pdf",
            "figure4_backbone_sensitivity.png",
            "figure4_backbone_sensitivity.pdf",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
