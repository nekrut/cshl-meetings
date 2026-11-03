#!/usr/bin/env python3
"""Poster version: H. pylori oipA strict-panel MSA heatmap.

No reference strip. The obelisk and spike figures tint real annotated
sub-features on theirs (Oblin-1/Oblin-2, RBD); oipA has no sub-feature
coordinates anywhere in this repo -- the query FASTA header carries only the
CDS's genomic location -- so the strip here was an empty cream bar carrying
no information. Dropped rather than filled with invented spans.

Nucleotide position ticks run underneath the map.
"""
from __future__ import annotations

import pathlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
REF = REPO / "h-pylori" / "queries" / "markers" / "h_pylori_oipa.fasta"
MSA = REPO / "h-pylori" / "baseline" / "oipa_strict" / "oipa.clean.accessions.fasta"
OUT = HERE.parent / "figures" / "oipa_poster.png"

BASE_TO_CODE = {"A": 1, "C": 2, "G": 3, "T": 4}
GAP_CODE = 5
OTHER_CODE = 6
PALETTE = ["#f3ecdc", "#2e8b57", "#2f6a7a", "#c08a2b",
           "#8b1a2b", "#121212", "#9c9c9c"]

# The poster card behind these figures. The canvas was invisible until the
# ruler band appeared below the map; left white it reads as a seam.
PAPER = "#f6f1e8"

# Nucleotide positions (1-based) to tick along the bottom. The reference CDS is
# ungapped in this panel, so an alignment column is the reference coordinate.
# The last label carries the unit so the axis needs no separate label.
TICKS = [1, 200, 400, 600, 800, 918]
# 16x9 figure, same as the obelisk one; the spike figure is 12x12 and scales
# these by 12/9 to land on the same printed size.
TICK_FS = 25
TICK_LEN = 8
TICK_PAD = 6


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


def read_fasta(path):
    out = {}
    header = None
    buf = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header is not None:
                    out[header] = "".join(buf).upper()
                header = line[1:].split()[0]
                buf = []
            else:
                buf.append(line)
        if header is not None:
            out[header] = "".join(buf).upper()
    return out


def main():
    ref_recs = read_fasta(REF)
    ref = next(iter(ref_recs.values()))
    L = len(ref)
    ref_arr = np.frombuffer(ref.encode("ascii"), dtype=np.uint8)

    recs = read_fasta(MSA)
    rows = []
    muts = []
    for seq in recs.values():
        if len(seq) != L:
            continue
        row = np.frombuffer(seq.encode("ascii"), dtype=np.uint8)
        codes = np.zeros(L, dtype=np.uint8)
        match = row == ref_arr
        for b, c in BASE_TO_CODE.items():
            codes[(row == ord(b)) & ~match] = c
        codes[row == ord("-")] = GAP_CODE
        codes[~match & (codes == 0)] = OTHER_CODE
        rows.append(codes)
        muts.append(int((codes != 0).sum()))
    codes = np.array(rows, dtype=np.uint8)
    order = np.argsort(muts)
    codes = codes[order]
    N, L = codes.shape

    fig = plt.figure(figsize=(16, 9), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
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
