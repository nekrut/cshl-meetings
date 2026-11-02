#!/usr/bin/env python3
"""Poster version: panel C of the showcase HyphAeon selection landscape.

Lifted from showcase/scripts/05_plot_showcase_figures.py (plot_fig1_hyphaeon,
Panel C) and reduced to a standalone figure so the poster does not have to
crop a 3-panel image. Reads the same authentic result CSV/JSON as the
original; nothing under showcase/ is written to.

Differences from the original panel:
  * standalone figure, so the "C. ..." panel title is dropped (the poster
    section carries its own HTML heading)
  * non-significant site MEME LRT lines are dark purple instead of the pale
    #9ecae1, which disappeared against white at print size
"""
from __future__ import annotations

import json
import pathlib

import matplotlib.pyplot as plt
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
RESULTS = REPO / "showcase" / "results" / "hyphaeon"
OUT = HERE.parent / "figures" / "hyphaeon_selection_poster.png"

# Pale blue -> dark purple. Kept clear of the #1f78b4 plasticity trace so the
# two never read as the same series.
NONSIG_COLOR = "#5c2d91"
SIG_COLOR = "#d95f02"
PHI_COLOR = "#1f78b4"

DOMAINS = [
    ("NTD", 14, 305, "#e0ecf4"),
    ("RBD", 319, 541, "#fee8c8"),
    ("RBM", 437, 508, "#fdd49e"),
    ("Furin/S1-S2", 675, 695, "#fdae6b"),
    ("FP/HR1", 788, 984, "#e5f5e0"),
    ("HR2/TM", 1163, 1237, "#efedf5"),
]

# (dx, dy) from the site's own (codon, LRT) point. The plasticity trace sweeps
# the LRT-equivalent 9-15 band for most of the gene, so every label except
# codon 13 (where Phi is low) is lifted clear of it rather than left on top.
ANNOT_OFFSETS = {
    13: (22, 1.8),
    445: (-110, 6.0),
    484: (25, 0.5),
    681: (-60, 6.5),
    950: (-95, 7.5),
    1118: (-105, 7.0),
}
# These three sit clear of the plasticity trace on their own -- 445 and 484
# over the RBD/RBM tint, 681 in the gap above it -- so they read better
# without a backing box behind them.
NO_BBOX_SITES = {445, 484, 681}
Y_MAX = 21.0
DOMAIN_LABEL_Y = 20.5
ANNOT_Y_CAP = 17.6

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.5,
    "axes.labelsize": 10.5,
    "axes.labelweight": "bold",
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 8.8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def main() -> None:
    with open(RESULTS / "hyphaeon_showcase_summary.json") as f:
        summary = json.load(f)
    spk_rec = {r["name"]: r for r in summary["runs"]}["sarscov2_spike"]

    df_meme = pd.read_csv(RESULTS / "sarscov2_spike_meme.csv")
    df_dms = pd.read_csv(RESULTS / "sarscov2_spike_dms.csv")

    sites = df_meme["site"].values
    lrt = df_meme["hyphaeon_lrt"].values
    pvals = df_meme["p_value"].values

    fig, ax = plt.subplots(figsize=(15.0, 4.6))

    for dname, start, end, dcol in DOMAINS:
        ax.axvspan(start, end, color=dcol, alpha=0.55, zorder=0)
        ax.text((start + end) / 2, DOMAIN_LABEL_Y, dname, ha="center", va="top",
                fontsize=8.6, fontweight="bold", color="#333333")

    sig = pvals <= 0.05
    ax.vlines(sites[~sig], 0, lrt[~sig], color=NONSIG_COLOR, alpha=0.8,
              linewidth=1.1, label="Site MEME LRT (p > 0.05)")
    ax.vlines(sites[sig], 0, lrt[sig], color=SIG_COLOR, alpha=0.95,
              linewidth=1.6,
              label=f"Episodic Diversifying Sites (p ≤ 0.05, n={int(sig.sum())})")
    ax.scatter(sites[sig], lrt[sig], color=SIG_COLOR, s=20, zorder=4)

    ax2 = ax.twinx()
    ax2.spines["top"].set_visible(False)
    phi = (df_dms.set_index("site")["intrinsic_plasticity"]
           .rolling(25, center=True, min_periods=5).mean())
    ax2.plot(phi.index, phi.values, color=PHI_COLOR, linewidth=1.7, alpha=0.85,
             label="Digital DMS Plasticity Φ (25-codon rolling mean)")
    ax2.set_ylabel("Rolling Digital DMS Plasticity (Φ)", color=PHI_COLOR,
                   fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=PHI_COLOR)
    ax2.set_ylim(1.0, 5.2)

    # Drawn on ax2, positioned in ax's data space: twinx stacks ax2 above ax,
    # so an annotation added to ax would sit under the plasticity trace no
    # matter its zorder. The backing box covers whatever still passes behind.
    for top_s in spk_rec["top_meme_sites"][:6]:
        s = int(top_s["codon"])
        val = float(top_s["lrt"])
        mut = top_s["top_mutation"]
        dx, dy = ANNOT_OFFSETS.get(s, (20, 1.5))
        ax2.annotate(
            f"Codon {s} ({mut})\nLRT={val:.1f}",
            xy=(s, val), xytext=(s + dx, min(val + dy, ANNOT_Y_CAP)),
            xycoords=ax.transData, textcoords=ax.transData,
            fontsize=8.6, fontweight="bold", color="#99000d",
            bbox=None if s in NO_BBOX_SITES else dict(
                boxstyle="round,pad=0.22", facecolor="white",
                edgecolor="none", alpha=0.85),
            arrowprops=dict(arrowstyle="->", color="#99000d", lw=1.0),
            zorder=6,
        )

    ax.set_xlim(1, 1274)
    ax.set_ylim(0, Y_MAX)
    ax.set_xlabel("SARS-CoV-2 Spike Codon Position "
                  "(161 Global LexicMap Haplotypes representing >500k SRA Runs)")
    ax.set_ylabel("HyphAeon MEME LRT Statistic")

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    # Below the axes: in the top-right corner it covered the FP/HR1 and
    # HR2/TM domain labels and crowded the plasticity peak near codon 930.
    ax.legend(h1 + h2, l1 + l2, loc="upper center",
              bbox_to_anchor=(0.5, -0.20), ncol=3, frameon=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"[save] {OUT}")


if __name__ == "__main__":
    main()
