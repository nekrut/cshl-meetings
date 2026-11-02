#!/usr/bin/env python3
"""Poster version: zoomed-only lexi+walker20k bucket chart, no labels.

Reads the same TSVs as the original figure script (which lives in
sars-cov-2/metadata/scripts/). Writes a single, wide, label-stripped
PNG next to this script, under figures/.
"""
from __future__ import annotations

import csv
import pathlib

import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LEXI_SUMMARY = REPO / "sars-cov-2" / "metadata" / "results" / "per_cohort_summary.tsv"
W20K_SUMMARY = REPO / "sars-cov-2" / "metadata" / "results" / "walker20k" / "bucket_summary_corrected.tsv"
OUT = HERE.parent / "figures" / "metadata_bars_poster.png"

BUCKETS = ["A_labeled_covid", "B_mixed_plausible", "C_mislabeled", "D_no_ena_record"]
BUCKET_COLOR = {
    "A_labeled_covid": "#efefe6",
    "B_mixed_plausible": "#d79b2f",
    "C_mislabeled": "#8b1a2b",
    "D_no_ena_record": "#9c9c9c",
}
ROW_KEYS = [
    "lexi_all_hsp",
    "lexi_perm_cfl",
    "lexi_strict_cfl",
    "walker20k_input",
    "walker20k_success",
    "walker20k_cleanfull",
]
ROW_LABELS = {
    "lexi_all_hsp":        "LexicMap all hits  ·  4.99 M",
    "lexi_perm_cfl":       "LexicMap permissive CFL  ·  1.15 M",
    "lexi_strict_cfl":     "LexicMap strict CFL  ·  76 k",
    "walker20k_input":     "Walker input  ·  20 k",
    "walker20k_success":   "Walker success  ·  9,448",
    "walker20k_cleanfull": "Walker CLEAN_FULL_LENGTH  ·  6,827",
}


def load_rows() -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    with LEXI_SUMMARY.open() as f:
        for r in csv.DictReader(f, delimiter="\t"):
            cohort = r["cohort"]
            if cohort in ("lexi_all_hsp", "lexi_perm_cfl", "lexi_strict_cfl"):
                out[cohort] = {
                    "n": int(r["records_matched"]),
                    **{b: int(r[b]) for b in BUCKETS},
                }
    with W20K_SUMMARY.open() as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out[r["tier"]] = {
                "n": int(r["n"]),
                **{b: int(r[b]) for b in BUCKETS},
            }
    return out


def main() -> None:
    rows = load_rows()
    fracs = {
        b: np.array([rows[k][b] / max(rows[k]["n"], 1) for k in ROW_KEYS])
        for b in BUCKETS
    }

    # ~4.8:1. The figure shares the bottom row with the HyphAeon panel now
    # instead of spanning the poster, so the old 7.9:1 left it only ~61mm
    # tall in a column with ~46mm of unused height beneath it.
    fig, ax = plt.subplots(figsize=(22, 4.58))
    y = np.arange(len(ROW_KEYS))

    left = np.zeros(len(ROW_KEYS))
    for b in BUCKETS:
        ax.barh(y, fracs[b], left=left, color=BUCKET_COLOR[b],
                edgecolor="#444444", linewidth=0.6)
        left += fracs[b]

    for i, k in enumerate(ROW_KEYS):
        ax.text(0.9015, i, ROW_LABELS[k],
                ha="left", va="center",
                fontsize=18, color="#1a1a1a",
                family="DejaVu Sans")

    ax.set_yticks([])
    ax.invert_yaxis()
    ax.set_xlim(0.90, 1.0)
    ax.set_xticks([])
    for spine in ("top", "right", "left", "bottom"):
        ax.spines[spine].set_visible(False)

    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"[save] {OUT}")
    fig.savefig(OUT, dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


if __name__ == "__main__":
    main()
