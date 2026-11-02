#!/usr/bin/env python3
"""Poster version: obelisk alpha MSA heatmap with a thin reference strip
on top that tints Oblin-1 and Oblin-2 regions, and nucleotide position ticks
underneath. No other text, no legend.
"""
from __future__ import annotations

import pathlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
FASTA = REPO / "obelisk" / "msa" / "alpha_all_msa.fasta"
OUT = HERE.parent / "figures" / "obelisk_alpha_poster.png"

BASE_TO_CODE = {"A": 1, "C": 2, "G": 3, "T": 4}
GAP_CODE = 5
OTHER_CODE = 6
PALETTE = ["#f3ecdc", "#2e8b57", "#2f6a7a", "#c08a2b",
           "#8b1a2b", "#121212", "#9c9c9c"]
MAX_EDITS = 200  # drop obvious walker chimeras

# alpha-specific feature spans (from the original figure script).
OBLIN1_SPAN = (50, 659)
OBLIN2_SPAN = (695, 875)
OBLIN1_TINT = "#ddd0b3"  # tan
OBLIN2_TINT = "#a0b4c7"  # cool blue-gray
STRIP_BG = "#f3ecdc"

# The poster card behind these figures. The canvas was invisible until the
# ruler band appeared below the map; left white it reads as a seam.
PAPER = "#f6f1e8"

# Nucleotide positions (1-based) to tick along the bottom. The reference row is
# ungapped, so an alignment column is the reference coordinate. Spacing is set
# so no two labels crowd each other at print width; the last one carries the
# unit so the axis needs no separate label.
TICKS = [1, 200, 400, 600, 800, 1168]
# 16x9 figure. The spike figure is 12x12, so it scales these by 12/9 to land on
# the same printed size once all three are stretched into equal poster boxes.
TICK_FS = 25
TICK_LEN = 8
TICK_PAD = 6


def load_msa(path):
    ref = None
    seqs = []
    header = None
    buf = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header is not None:
                    seq = "".join(buf).upper()
                    if ref is None:
                        ref = seq
                    elif len(seq) == len(ref):
                        seqs.append(np.frombuffer(seq.encode("ascii"), dtype=np.uint8))
                header = line[1:]
                buf = []
            else:
                buf.append(line)
        if header is not None:
            seq = "".join(buf).upper()
            if ref is None:
                ref = seq
            elif len(seq) == len(ref):
                seqs.append(np.frombuffer(seq.encode("ascii"), dtype=np.uint8))
    arr = np.array(seqs, dtype=np.uint8) if seqs else np.zeros((0, len(ref)), dtype=np.uint8)
    return ref, arr


def encode(ref, raw):
    ref_arr = np.frombuffer(ref.encode("ascii"), dtype=np.uint8)
    codes = np.zeros(raw.shape, dtype=np.uint8)
    match = raw == ref_arr
    for b, c in BASE_TO_CODE.items():
        codes[(raw == ord(b)) & ~match] = c
    codes[raw == ord("-")] = GAP_CODE
    codes[~match & (codes == 0)] = OTHER_CODE
    return codes


def draw_nt_ticks(ax, ticks, fs, length, pad):
    """Nucleotide ruler under a heatmap axes.

    The labels are drawn below the figure canvas; savefig's tight bbox grows
    the image to take them in, so the heatmap itself keeps its full height and
    the ruler is added underneath rather than carved out of the map.

    End labels are edge-aligned instead of centred: a centred "1" at column 0
    would hang off the left of the canvas, and tight bbox would answer with a
    gutter on both sides that narrows the map.
    """
    ax.set_xticks([p - 1 for p in ticks])
    ax.set_xticklabels([f"{p:,}" for p in ticks[:-1]] + [f"{ticks[-1]:,} nt"],
                       fontsize=fs, color="#1a1a1a")
    labels = ax.get_xticklabels()
    labels[0].set_horizontalalignment("left")
    labels[-1].set_horizontalalignment("right")
    ax.tick_params(axis="x", length=length, width=fs / 12.0, pad=pad,
                   color="#1a1a1a")


def main():
    ref, raw = load_msa(FASTA)
    codes = encode(ref, raw)
    n_muts = (codes != 0).sum(axis=1)
    keep = n_muts <= MAX_EDITS
    codes = codes[keep]
    n_muts = n_muts[keep]
    order = np.argsort(n_muts)
    codes = codes[order]
    N, L = codes.shape

    fig = plt.figure(figsize=(16, 9), dpi=200)
    gs = fig.add_gridspec(nrows=2, ncols=1,
                          height_ratios=[0.07, 1.0], hspace=0.012,
                          left=0, right=1, top=1, bottom=0)

    # Reference strip
    ax_ref = fig.add_subplot(gs[0, 0])
    ax_ref.add_patch(patches.Rectangle((-0.5, 0), L, 1,
                                       facecolor=STRIP_BG, edgecolor="none"))
    # Oblin-1 and Oblin-2 regions as colored blocks on the strip
    for span, color in [(OBLIN1_SPAN, OBLIN1_TINT), (OBLIN2_SPAN, OBLIN2_TINT)]:
        s, e = span
        ax_ref.add_patch(patches.Rectangle((s - 0.5, 0), e - s, 1,
                                           facecolor=color, edgecolor="none"))
    ax_ref.set_xlim(-0.5, L - 0.5)
    ax_ref.set_ylim(0, 1)
    ax_ref.set_xticks([])
    ax_ref.set_yticks([])
    for spine in ("top", "right", "bottom", "left"):
        ax_ref.spines[spine].set_visible(False)

    # Main heatmap
    ax = fig.add_subplot(gs[1, 0])
    cmap = ListedColormap(PALETTE)
    norm = BoundaryNorm(np.arange(len(PALETTE) + 1) - 0.5, len(PALETTE))
    ax.imshow(codes, cmap=cmap, norm=norm, aspect="auto",
              interpolation="nearest", origin="upper", rasterized=True)
    ax.set_yticks([])
    for spine in ("top", "right", "bottom", "left"):
        ax.spines[spine].set_visible(False)
    draw_nt_ticks(ax, TICKS, TICK_FS, TICK_LEN, TICK_PAD)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"[save] {OUT}  ({N} rows x {L} cols)")
    fig.savefig(OUT, dpi=300, bbox_inches="tight", pad_inches=0,
                facecolor=PAPER)
    plt.close(fig)


if __name__ == "__main__":
    main()
