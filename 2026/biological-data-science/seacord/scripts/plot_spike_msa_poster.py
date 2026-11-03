#!/usr/bin/env python3
"""Poster version: SARS-CoV-2 spike comparison figure.

One shared reference strip at the top (RBD tinted), then the kmindex->walker
20k heatmap stacked above the lexicmap-permissive-sieved heatmap. Both share
the same spike CDS coordinate frame so a column lines up across both panels.
No text, no ticks, no legend.
"""
from __future__ import annotations

import pathlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LEXI_FASTA = REPO / "sars-cov-2" / "lexicmap" / "sieved_permissive" / "Wuhan_Hu1_ref.clean.sieved.msa.fasta"
KMI_FASTA = REPO / "sars-cov-2" / "kmindex" / "msa_20k" / "sarscov2_spike_11strains_codon_msa.fasta"
OUT = HERE.parent / "figures" / "spike_poster.png"

BASE_TO_CODE = {"A": 1, "C": 2, "G": 3, "T": 4}
GAP_CODE = 5
OTHER_CODE = 6
PALETTE = ["#f3ecdc", "#2e8b57", "#2f6a7a", "#c08a2b",
           "#8b1a2b", "#121212", "#9c9c9c"]

RBD_NT_START = 954
RBD_NT_END = 1623
RBD_TINT = "#ddd0b3"
STRIP_BG = "#f3ecdc"

# The poster card behind these figures. The canvas was invisible until the
# ruler band appeared below the map; left white it reads as a seam.
PAPER = "#f6f1e8"

# Nucleotide positions (1-based) to tick under the lower panel. Both panels
# share this frame, and the Wuhan Hu-1 reference row is ungapped, so an
# alignment column is the spike CDS coordinate. The last label carries the
# unit so the axis needs no separate label.
TICKS = [1, 500, 1000, 1500, 2000, 2500, 3000, 3822]
TICK_FS = 25
TICK_LEN = 8
TICK_PAD = 6


def draw_nt_ticks(ax, ticks, fs, length, pad):
    """Nucleotide ruler under a heatmap axes.

    The labels are drawn below the figure canvas; savefig's tight bbox grows
    the image to take them in, so the heatmaps themselves keep their full
    height and the ruler is added underneath rather than carved out of them.

    End labels are edge-aligned instead of centred: a centred "1" at column 0
    would hang off the left of the canvas, and tight bbox would answer with a
    gutter on both sides that narrows the maps.
    """
    ax.set_xticks([p - 1 for p in ticks])
    ax.set_xticklabels([f"{p:,}" for p in ticks[:-1]] + [f"{ticks[-1]:,} nt"],
                       fontsize=fs, color="#1a1a1a")
    labels = ax.get_xticklabels()
    labels[0].set_horizontalalignment("left")
    labels[-1].set_horizontalalignment("right")
    ax.tick_params(axis="x", length=length, width=fs / 12.0, pad=pad,
                   color="#1a1a1a")


def iter_records(path):
    header = None
    buf = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(buf).upper()
                header = line[1:]
                buf = []
            else:
                buf.append(line)
        if header is not None:
            yield header, "".join(buf).upper()


def encode_all(path, ref_len):
    """Stream records, return (codes, muts) matched to ref_len."""
    it = iter_records(path)
    _, ref = next(it)
    assert len(ref) == ref_len, f"ref len mismatch in {path}"
    ref_arr = np.frombuffer(ref.encode("ascii"), dtype=np.uint8)
    code_rows = []
    mut_counts = []
    for _, seq in it:
        if len(seq) != ref_len:
            continue
        row = np.frombuffer(seq.encode("ascii"), dtype=np.uint8)
        codes = np.zeros(ref_len, dtype=np.uint8)
        match = row == ref_arr
        for b, c in BASE_TO_CODE.items():
            codes[(row == ord(b)) & ~match] = c
        codes[row == ord("-")] = GAP_CODE
        codes[~match & (codes == 0)] = OTHER_CODE
        code_rows.append(codes)
        mut_counts.append(int((codes != 0).sum()))
    codes = np.array(code_rows, dtype=np.uint8)
    muts = np.array(mut_counts, dtype=np.int64)
    order = np.argsort(muts)
    return codes[order]


def main():
    # Determine L from the lexicmap ref (Wuhan Hu-1 spike, 3822 nt).
    with open(LEXI_FASTA) as f:
        _ = f.readline()
        buf = []
        for line in f:
            if line.startswith(">"):
                break
            buf.append(line.rstrip("\n"))
        ref = "".join(buf).upper()
    L = len(ref)
    print(f"[info] L = {L}")

    print(f"[load] kmindex 20k: {KMI_FASTA}")
    kmi = encode_all(KMI_FASTA, L)
    print(f"[info]   {kmi.shape[0]} rows")

    print(f"[load] lexicmap:    {LEXI_FASTA}")
    lexi = encode_all(LEXI_FASTA, L)
    print(f"[info]   {lexi.shape[0]} rows")

    # 16x9 like the obelisk and oipA figures. The poster stretches all three
    # into boxes of the same size with object-fit: fill, so a figure of a
    # different aspect gets a different horizontal scale from its vertical one
    # -- harmless for a heatmap, but it printed the ruler's digits 1.8x too
    # wide and ran them into each other. The panel proportions below are all
    # ratios, so they are unchanged by the new canvas.
    fig = plt.figure(figsize=(16, 9), dpi=300)
    # 0.14 against two stacked panels puts the strip at ~6.5% of figure
    # height, matching the single-panel obelisk and oipA figures (0.07 of
    # 1.0). All three are stretched into the same box on the poster, so it
    # is this fraction, not the absolute size, that has to agree.
    gs = fig.add_gridspec(nrows=3, ncols=1,
                          height_ratios=[0.14, 1.0, 1.0], hspace=0.01,
                          left=0, right=1, top=1, bottom=0)

    # Shared reference strip
    ax_ref = fig.add_subplot(gs[0, 0])
    ax_ref.add_patch(patches.Rectangle((-0.5, 0), L, 1,
                                       facecolor=STRIP_BG, edgecolor="none"))
    ax_ref.add_patch(patches.Rectangle((RBD_NT_START - 0.5, 0),
                                       RBD_NT_END - RBD_NT_START, 1,
                                       facecolor=RBD_TINT, edgecolor="none"))
    ax_ref.set_xlim(-0.5, L - 0.5)
    ax_ref.set_ylim(0, 1)
    ax_ref.set_xticks([])
    ax_ref.set_yticks([])
    for spine in ("top", "right", "bottom", "left"):
        ax_ref.spines[spine].set_visible(False)

    cmap = ListedColormap(PALETTE)
    norm = BoundaryNorm(np.arange(len(PALETTE) + 1) - 0.5, len(PALETTE))

    for i, data in enumerate([kmi, lexi], start=1):
        ax = fig.add_subplot(gs[i, 0])
        ax.imshow(data, cmap=cmap, norm=norm, aspect="auto",
                  interpolation="nearest", origin="upper", rasterized=True)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ("top", "right", "bottom", "left"):
            ax.spines[spine].set_visible(False)
        # Only the lower panel gets the ruler; the two share a coordinate frame.
        if i == 2:
            draw_nt_ticks(ax, TICKS, TICK_FS, TICK_LEN, TICK_PAD)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"[save] {OUT}")
    fig.savefig(OUT, dpi=300, bbox_inches="tight", pad_inches=0,
                facecolor=PAPER)
    plt.close(fig)


if __name__ == "__main__":
    main()
