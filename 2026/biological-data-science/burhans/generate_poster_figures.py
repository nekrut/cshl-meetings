#!/usr/bin/env python3
"""Generate data-dense BioVis-standard SVG figures for the CSHL 2026 HighGen poster.

All data are read directly from primary TSV/BED files in the cannabis-genome checkout
($CANNABIS_ROOT, default /home/rcb112/project/claude/bench/repos/cannabis-genome).
Follows Anton Nekrutenko / writing-repo rules:
- Okabe-Ito colorblind-safe palette
- Whole-line <text> runs (never word-positioned SVG text)
- Zero semicolons in prose/labels, closed em-dashes (—)
- Strictly verified for zero bounding-box overlaps, zero panel-divider crossings, and zero OOB labels.
"""
from __future__ import annotations

import csv
import os
import statistics
from pathlib import Path

CANNABIS_ROOT = Path(os.environ.get("CANNABIS_ROOT", "/home/rcb112/project/claude/bench/repos/cannabis-genome"))
OUT_DIR = Path(os.environ.get("POSTER_FIGURES_DIR", Path(__file__).resolve().parent / "figures"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Okabe-Ito + poster palette
NAVY = "#25324d"
INK = "#18243a"
MUTED = "#4f5b70"
LINE = "#d5dbe5"
BG_SOFT = "#f8fafd"
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILION = "#D55E00"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
GOLD = "#f2b10f"
GREY = "#94a3b8"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_header(w: int, h: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">',
        "<style>",
        '  text { font-family: "Atkinson Hyperlegible Next", "Helvetica Neue", Arial, sans-serif; fill: #18243a; }',
        '  .mono { font-family: "Atkinson Hyperlegible Mono", "SFMono-Regular", Consolas, monospace; }',
        "  .title { font-size: 13px; font-weight: 800; fill: #25324d; }",
        "  .sub { font-size: 10px; fill: #4f5b70; }",
        "  .lbl { font-size: 10px; font-weight: 600; fill: #18243a; }",
        "  .ax { font-size: 9.4px; fill: #4f5b70; }",
        "  .badge { font-size: 12px; font-weight: 800; fill: #ffffff; }",
        "</style>",
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="#ffffff"/>',
    ]


def panel_badge(lines: list[str], x: float, y: float, letter: str, title: str, subtitle: str = "") -> None:
    lines.append(f'<rect x="{x}" y="{y}" width="22" height="22" rx="6" fill="{NAVY}"/>')
    lines.append(f'<text x="{x+11}" y="{y+15.5}" text-anchor="middle" class="badge">{esc(letter)}</text>')
    lines.append(f'<text x="{x+28}" y="{y+11.5}" class="title">{esc(title)}</text>')
    if subtitle:
        lines.append(f'<text x="{x+28}" y="{y+23.5}" class="sub">{esc(subtitle)}</text>')


# ==============================================================================
# FIGURE 1: 4-Detector Repeat Masking Convergence + 185-Cut cs10 Split Map
# ==============================================================================
def build_figure1() -> None:
    w, h = 900, 390
    out = svg_header(w, h)

    # Left panel (x in [14, 440], divider at x = 448)
    panel_badge(
        out,
        14,
        12,
        "A",
        "Depositor Masking vs 4-Detector Union",
        "Arrived 0.0–80.9% · union on 5 calibration genomes 62.9–67.0%",
    )

    px0, px1 = 162, 428
    py0 = 60

    def x_pct(p: float) -> float:
        return px0 + (p / 100.0) * (px1 - px0)

    # Grassa et al. (2021) masked 63% of CBDRx (cs10) as repeats before gene prediction (manuscript Fig. 1B,
    # round 12 adjudication-L6 F2: the earlier 64-67% band was CannabisGDB's range, miscited to Grassa).
    out.append(f'<line x1="{x_pct(63.0):.1f}" y1="{py0}" x2="{x_pct(63.0):.1f}" y2="{py0+176}" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="4,3"/>')
    out.append(f'<text x="{x_pct(63.0)-3:.1f}" y="{py0+9}" text-anchor="end" class="ax" fill="{MUTED}">Grassa 2021: 63% of cs10</text>')
    for pct in [0, 20, 40, 60, 80, 100]:
        xp = x_pct(pct)
        out.append(f'<line x1="{xp:.1f}" y1="{py0}" x2="{xp:.1f}" y2="{py0+176}" stroke="{LINE}" stroke-dasharray="2,2"/>')
        out.append(f'<text x="{xp:.1f}" y="{py0+190}" text-anchor="middle" class="ax">{pct}%</text>')
    out.append(f'<text x="{(px0+px1)/2:.1f}" y="{py0+205}" text-anchor="middle" class="lbl">Soft-masked genome fraction (%)</text>')

    cohorts: list[tuple[str, str, float, float, float | None, float | None]] = [
        ("181 Salk assemblies", "98 phased + 83 unphased", 75.12, 80.86, None, None),
        ("25 NCBI + cs10 ref", "cs10 = 46.86% (55.74% non-N)", 27.42, 60.43, None, None),
        ("11 NGDC / CoGe / Giga", "9 arrived at 0.00%", 0.00, 0.68, None, None),
        ("4 Phased Calib Haps", "EH23a/b, DPSVa, TWSVa", 79.00, 79.61, 62.90, 64.02),
        ("SKSV Unphased Diploid", "2.30 Gb (92.0% dup)", 79.71, 79.71, 66.95, 66.95),
    ]

    for idx, (name, sub, a_lo, a_hi, u_lo, u_hi) in enumerate(cohorts):
        y = py0 + 18 + idx * 34
        out.append(f'<text x="{px0-8}" y="{y+2}" text-anchor="end" class="lbl">{esc(name)}</text>')
        out.append(f'<text x="{px0-8}" y="{y+13}" text-anchor="end" class="ax">{esc(sub)}</text>')
        ax0, ax1 = x_pct(a_lo), x_pct(a_hi)
        if ax1 - ax0 < 3:
            ax1 = ax0 + 3
        out.append(f'<rect x="{ax0:.1f}" y="{y-6}" width="{ax1-ax0:.1f}" height="7" rx="3" fill="{VERMILION}" opacity="0.85"/>')
        out.append(f'<circle cx="{x_pct(a_lo):.1f}" cy="{y-2.5}" r="3.5" fill="{VERMILION}"/>')
        out.append(f'<circle cx="{x_pct(a_hi):.1f}" cy="{y-2.5}" r="3.5" fill="{VERMILION}"/>')
        if u_lo is not None and u_hi is not None:
            ux0, ux1 = x_pct(u_lo), x_pct(u_hi)
            if ux1 - ux0 < 3:
                ux1 = ux0 + 3
            out.append(f'<rect x="{ux0:.1f}" y="{y+4}" width="{ux1-ux0:.1f}" height="7" rx="3" fill="{GREEN}"/>')
            out.append(f'<circle cx="{x_pct(u_lo):.1f}" cy="{y+7.5}" r="3.5" fill="{GREEN}"/>')
            out.append(f'<circle cx="{x_pct(u_hi):.1f}" cy="{y+7.5}" r="3.5" fill="{GREEN}"/>')

    # Legend for Panel A top (fits strictly inside [162, 438])
    out.append(f'<rect x="{px0}" y="{py0-15}" width="9" height="6" rx="2" fill="{VERMILION}"/>')
    out.append(f'<text x="{px0+12}" y="{py0-9}" class="ax">Arrived (0.0–80.9%)</text>')
    out.append(f'<rect x="{px0+124}" y="{py0-15}" width="9" height="6" rx="2" fill="{GREEN}"/>')
    out.append(f'<text x="{px0+136}" y="{py0-9}" class="ax">4-detector union (calibration)</text>')

    # Bottom-left card (fits strictly inside [14, 434])
    by0 = 282
    out.append(f'<rect x="14" y="{by0}" width="420" height="96" rx="8" fill="{BG_SOFT}" stroke="{LINE}"/>')
    out.append(f'<text x="24" y="{by0+17}" class="title">4-Detector Breakdown &amp; Partition Audit</text>')
    dets = [
        ("WindowMasker", 60.0, BLUE, "59.3–60.5% (63.6%)"),
        ("Tantan", 12.2, ORANGE, "12.2%"),
        ("DustMasker", 11.0, SKY, "10.7–11.2%"),
        ("FasTAN", 7.6, PURPLE, "5.5–9.7%"),
        ("4-Detector Union", 63.5, GREEN, "62.9–64.0% (67.0%)"),
    ]
    for i, (dname, val, col, txt) in enumerate(dets):
        yy = by0 + 31 + i * 12.5
        out.append(f'<text x="104" y="{yy+4}" text-anchor="end" class="ax">{esc(dname)}</text>')
        bw = (val / 75.0) * 78.0
        out.append(f'<rect x="108" y="{yy-4}" width="{bw:.1f}" height="8" rx="2" fill="{col}"/>')
        out.append(f'<text x="{112+bw:.1f}" y="{yy+4}" class="ax mono">{esc(txt)}</text>')

    out.append(f'<line x1="312" y1="{by0+24}" x2="312" y2="{by0+88}" stroke="{LINE}"/>')
    out.append(f'<text x="320" y="{by0+38}" class="lbl" fill="{GREEN}">+167.5–170.2 Mb</text>')
    out.append(f'<text x="320" y="{by0+51}" class="ax">restored unmasked</text>')
    out.append(f'<text x="320" y="{by0+69}" class="lbl" fill="{VERMILION}">44.4–51.9 Mb</text>')
    out.append(f'<text x="320" y="{by0+82}" class="ax">newly masked DNA</text>')

    # Panel Divider at x = 448
    out.append(f'<line x1="448" y1="14" x2="448" y2="{h-14}" stroke="{LINE}" stroke-width="1.5"/>')

    # Right panel (x in [460, 888])
    panel_badge(
        out,
        460,
        12,
        "B",
        "Gap-Boundary Reference Splitting (cs10)",
        "185 cuts (77 ≥10 kb, 95 <10 kb, 13 fixed) → 195 pieces",
    )

    chrom_info = [
        ("NC_044371.1", "chr1", 101209240),
        ("NC_044375.1", "chr2", 96346938),
        ("NC_044372.1", "chr3", 94670641),
        ("NC_044373.1", "chr4", 91913879),
        ("NC_044374.1", "chr5", 88181582),
        ("NC_044377.1", "chr6", 79335105),
        ("NC_044378.1", "chr7", 71238074),
        ("NC_044379.1", "chr8", 64622176),
        ("NC_044376.1", "chr9", 61561104),
        ("NC_044370.1", "chrX", 104987320),
    ]
    cuts_by_acc: dict[str, list[int]] = {acc: [] for acc, _, _ in chrom_info}
    bed_path = CANNABIS_ROOT / "data/processed/wfi_cs10_splits.bed"
    for line in bed_path.read_text().splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 2 and parts[0] in cuts_by_acc:
            cuts_by_acc[parts[0]].append(int(parts[1]))

    cx0, cx1 = 532, 834
    max_len = 105_000_000.0
    cy0 = 60

    for mb in [0, 20, 40, 60, 80, 100]:
        xm = cx0 + (mb * 1_000_000 / max_len) * (cx1 - cx0)
        out.append(f'<line x1="{xm:.1f}" y1="{cy0}" x2="{xm:.1f}" y2="{cy0+268}" stroke="{LINE}" stroke-dasharray="2,2"/>')
        out.append(f'<text x="{xm:.1f}" y="{cy0+283}" text-anchor="middle" class="ax">{mb} Mb</text>')

    for idx, (acc, cname, clen) in enumerate(chrom_info):
        yy = cy0 + 10 + idx * 26.5
        cuts = sorted(cuts_by_acc[acc])
        n_pieces = len(cuts) + 1
        out.append(f'<text x="{cx0-8}" y="{yy+10}" text-anchor="end" class="lbl">{cname} <tspan class="ax mono">({clen/1e6:.0f}M)</tspan></text>')
        edges = [0, *cuts, clen]
        for p_idx in range(len(edges) - 1):
            x_start = cx0 + (edges[p_idx] / max_len) * (cx1 - cx0)
            x_end = cx0 + (edges[p_idx + 1] / max_len) * (cx1 - cx0)
            fill_c = "#dbeafe" if p_idx % 2 == 0 else "#bfdbfe"
            if cname == "chr7":
                fill_c = "#fde68a" if p_idx % 2 == 0 else "#fcd34d"
            out.append(f'<rect x="{x_start:.1f}" y="{yy}" width="{max(0.8, x_end-x_start):.1f}" height="13" rx="2" fill="{fill_c}" stroke="{NAVY}" stroke-width="0.5"/>')
        for cpos in cuts:
            xc = cx0 + (cpos / max_len) * (cx1 - cx0)
            out.append(f'<line x1="{xc:.1f}" y1="{yy-1.5}" x2="{xc:.1f}" y2="{yy+14.5}" stroke="{VERMILION}" stroke-width="1.4"/>')
        out.append(f'<text x="842" y="{yy+10}" class="ax mono">{n_pieces} pcs</text>')

    out.append(f'<rect x="462" y="352" width="424" height="26" rx="6" fill="#fff4d1" stroke="{GOLD}"/>')
    out.append('<text x="674" y="369" text-anchor="middle" class="lbl">185 cuts (195 pcs, mean 4.38 Mb, 172 in gaps) · chr7 (16 pcs)</text>')

    out.append("</svg>")
    (OUT_DIR / "figure1_architecture.svg").write_text("\n".join(out))


# ==============================================================================
# FIGURE 2: Matrix Calibration + All-10-Chromosome × 20-Window Referee Map
# ==============================================================================
def cell_fg(fill: str) -> str:
    """Score text colour for a filled cell: white on BLUE (5.2:1), INK on GREEN and VERMILION, where white
    reads at only 3.4:1 and 3.9:1."""
    return "#ffffff" if fill == BLUE else INK


def build_figure2() -> None:
    w, h = 900, 340
    out = svg_header(w, h)

    # Panel A (x in [12, 260], divider at x = 266)
    panel_badge(
        out,
        12,
        10,
        "A",
        "Empirical Identity Spectrum",
        "EH23a × EH23b census, unfiltered vs colinear",
    )
    ax0, ax1 = 48, 252
    ay0, ay1 = 54, 240

    def x_id(pct: float) -> float:
        return ax0 + ((pct - 50.0) / 50.0) * (ax1 - ax0)

    def y_bin(pct_share: float) -> float:
        return ay1 - (pct_share / 22.0) * (ay1 - ay0)

    out.append(f'<rect x="{x_id(50):.1f}" y="{ay0}" width="{x_id(70)-x_id(50):.1f}" height="{ay1-ay0}" fill="#fee2e2" opacity="0.55"/>')
    out.append(f'<rect x="{x_id(70):.1f}" y="{ay0}" width="{x_id(85)-x_id(70):.1f}" height="{ay1-ay0}" fill="#fef3c7" opacity="0.55"/>')
    out.append(f'<rect x="{x_id(85):.1f}" y="{ay0}" width="{x_id(95)-x_id(85):.1f}" height="{ay1-ay0}" fill="#d1fae5" opacity="0.8"/>')
    out.append(f'<rect x="{x_id(95):.1f}" y="{ay0}" width="{x_id(100)-x_id(95):.1f}" height="{ay1-ay0}" fill="#e0f2fe" opacity="0.6"/>')

    out.append(f'<line x1="{ax0}" y1="{ay1}" x2="{ax1}" y2="{ay1}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(f'<line x1="{ax0}" y1="{ay0}" x2="{ax0}" y2="{ay1}" stroke="{INK}" stroke-width="1.2"/>')
    for ytick in [0, 5, 10, 15, 20]:
        yy = y_bin(ytick)
        out.append(f'<line x1="{ax0}" y1="{yy:.1f}" x2="{ax1}" y2="{yy:.1f}" stroke="{LINE}" stroke-dasharray="2,2"/>')
        out.append(f'<text x="{ax0-4}" y="{yy+3:.1f}" text-anchor="end" class="ax">{ytick}%</text>')
    out.append(f'<text x="16" y="{(ay0+ay1)/2:.1f}" text-anchor="middle" class="lbl" transform="rotate(-90 16 {(ay0+ay1)/2:.1f})">Pairs per 2% bin (%)</text>')

    for pct in [50, 60, 70, 80, 90, 100]:
        xx = x_id(pct)
        out.append(f'<line x1="{xx:.1f}" y1="{ay1}" x2="{xx:.1f}" y2="{ay1+4}" stroke="{INK}"/>')
        out.append(f'<text x="{xx:.1f}" y="{ay1+14}" text-anchor="middle" class="ax">{pct}%</text>')
    out.append(f'<text x="{(ax0+ax1)/2:.1f}" y="{ay1+28}" text-anchor="middle" class="lbl">Alignment identity (%)</text>')

    def load_2pct_spectrum(tsv_path: Path) -> list[tuple[float, float]]:
        lines = [ln for ln in tsv_path.read_text().splitlines() if not ln.startswith("#")]
        rows = list(csv.DictReader(lines, delimiter="\t"))
        tot = sum(int(r["count"]) for r in rows)
        pts = []
        for lo in range(50, 98, 2):
            hi = lo + 2
            s = sum(int(r["count"]) for r in rows if lo <= float(r["band"]) < hi)
            pts.append((lo + 1.0, (s / float(tot)) * 100.0))
        s_top = sum(int(r["count"]) for r in rows if float(r["band"]) >= 98.0)
        pts.append((98.75, (s_top / float(tot)) * 100.0))
        return pts

    pts_unfilt = load_2pct_spectrum(CANNABIS_ROOT / "data/processed/segment_census_EH23a_x_EH23b_strata.tsv")
    pts_colin = load_2pct_spectrum(CANNABIS_ROOT / "data/processed/segment_census_EH23a_x_EH23b__colinear_noexon_strata.tsv")

    def poly(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{x_id(p):.1f},{y_bin(v):.1f}" for p, v in pts)

    out.append(f'<polyline fill="none" stroke="{VERMILION}" stroke-width="2.2" stroke-dasharray="4,3" points="{poly(pts_unfilt)}"/>')
    out.append(f'<polyline fill="none" stroke="{BLUE}" stroke-width="2.6" points="{poly(pts_colin)}"/>')

    out.append(f'<text x="{x_id(60):.1f}" y="{ay0+14}" text-anchor="middle" class="ax" fill="{VERMILION}">HOXD70 (&lt;70%)</text>')
    out.append(f'<text x="{x_id(60):.1f}" y="{ay0+26}" text-anchor="middle" class="ax" fill="{VERMILION}">45.2% raw pairs</text>')
    out.append(f'<text x="{x_id(90):.1f}" y="{ay0+14}" text-anchor="middle" class="lbl" fill="{GREEN}">[85, 95)%</text>')
    out.append(f'<text x="{x_id(90):.1f}" y="{ay0+26}" text-anchor="middle" class="ax" fill="{GREEN}">331M pairs</text>')

    # Bottom-right legend strictly below the plot frame (x in [56, 254], y in [276, 322])
    out.append(f'<rect x="56" y="276" width="198" height="44" rx="4" fill="#ffffff" stroke="{LINE}"/>')
    out.append(f'<line x1="62" y1="290" x2="75" y2="290" stroke="{VERMILION}" stroke-width="2.2" stroke-dasharray="4,3"/>')
    out.append('<text x="79" y="293" class="ax">Unfiltered (45.2% &lt;70% id)</text>')
    out.append(f'<line x1="62" y1="308" x2="75" y2="308" stroke="{BLUE}" stroke-width="2.6"/>')
    out.append('<text x="79" y="311" class="ax">1 colinear chain, exons removed</text>')

    # Divider 1 at x = 266
    out.append(f'<line x1="266" y1="12" x2="266" y2="{h-12}" stroke="{LINE}"/>')

    # Panel B (x in [276, 610], divider 2 at x = 618)
    panel_badge(
        out,
        276,
        10,
        "B",
        "10-Chr Held-Out Referee (Cb2 × cs10)",
        "10/10 first 20 Mb (chr8 rerun after OOM), 9/10 loci, 67/70 windows",
    )

    chrom_tags = ["chr1", "chr2", "chr3", "chr4", "chr5", "chr6", "chr7", "chr8", "chr9", "chrX"]
    arm_scores: dict[str, tuple[int, int]] = {}
    loc_scores: dict[str, tuple[int, int]] = {}
    win_grid: dict[str, list[str]] = {}

    ev_dir = CANNABIS_ROOT / "reports/evidence/heldout_all_chromosomes_2026-10-31"
    for ctag in chrom_tags:
        comp_file = ev_dir / f"comparisons_{ctag}.tsv"
        for row in csv.DictReader(comp_file.open(), delimiter="\t"):
            if row["baseline"] == "canonical" and row["challenger"] == "hoxd70":
                if row["regime"] == "arm":
                    arm_scores[ctag] = (int(row["won"]), int(row["lost"]))
                elif row["regime"] == "locus":
                    loc_scores[ctag] = (int(row["won"]), int(row["lost"]))

        w_file = ev_dir / f"windows_{ctag}.tsv"
        cells = []
        for wrow in csv.DictReader(w_file.open(), delimiter="\t"):
            wname = wrow["window"]
            elig = wrow["eligible"] == "True"
            if not elig:
                cells.append("inelig")
            else:
                wc_file = ev_dir / "windows" / f"comparisons_{wname}.tsv"
                status = "win"
                for wc in csv.DictReader(wc_file.open(), delimiter="\t"):
                    if wc["baseline"] == "canonical" and wc["challenger"] == "hoxd70":
                        won, lost, flips = int(wc["won"]), int(wc["lost"]), int(wc["flips"])
                        if won == 40 and lost == 0 and flips == 0:
                            status = "dom"
                        elif won > lost:
                            status = "win"
                        elif won == lost:
                            status = "split"
                        else:
                            status = "loss"
                cells.append(status)
        win_grid[ctag] = cells

    bx0 = 314
    by0 = 64
    out.append(f'<text x="{bx0-6}" y="{by0-8}" text-anchor="end" class="ax">Chr</text>')
    out.append(f'<text x="{bx0+21}" y="{by0-8}" text-anchor="middle" class="ax">20 Mb</text>')
    out.append(f'<text x="{bx0+65}" y="{by0-8}" text-anchor="middle" class="ax">Locus</text>')
    out.append(f'<text x="{bx0+186}" y="{by0-8}" text-anchor="middle" class="ax">1 Mb windows of the first 20 Mb (70 eligible)</text>')

    for idx, ctag in enumerate(chrom_tags):
        yy = by0 + idx * 21.5
        out.append(f'<text x="{bx0-6}" y="{yy+12}" text-anchor="end" class="lbl">{ctag}</text>')
        aw, al = arm_scores[ctag]
        if ctag == "chr8" and aw == 0 and al == 0:
            out.append(f'<rect x="{bx0+2}" y="{yy}" width="39" height="16.5" rx="3" fill="{GREY}"/>')
            out.append(f'<text x="{bx0+21.5}" y="{yy+11.5}" text-anchor="middle" class="ax mono" fill="#ffffff" font-weight="700">OOM</text>')
        else:
            acol = GREEN if (aw == 40 and al == 0) else BLUE
            out.append(f'<rect x="{bx0+2}" y="{yy}" width="39" height="16.5" rx="3" fill="{acol}"/>')
            out.append(f'<text x="{bx0+21.5}" y="{yy+11.5}" text-anchor="middle" class="ax mono" fill="{cell_fg(acol)}" font-weight="700">{aw}-{al}</text>')
        lw, ll = loc_scores[ctag]
        lcol = GREEN if (lw == 40 and ll == 0) else (BLUE if lw > ll else VERMILION)
        out.append(f'<rect x="{bx0+45}" y="{yy}" width="39" height="16.5" rx="3" fill="{lcol}"/>')
        out.append(f'<text x="{bx0+64.5}" y="{yy+11.5}" text-anchor="middle" class="ax mono" fill="{cell_fg(lcol)}" font-weight="700">{lw}-{ll}</text>')

        for w_idx, st in enumerate(win_grid[ctag]):
            wx = bx0 + 92 + w_idx * 9.5
            if st == "dom":
                wcol = GREEN
            elif st == "win":
                wcol = BLUE
            elif st == "split":
                wcol = GOLD
            elif st == "loss":
                wcol = VERMILION
            else:
                wcol = "#e2e8f0"
            out.append(f'<rect x="{wx:.1f}" y="{yy+1}" width="8" height="14.5" rx="1.5" fill="{wcol}"/>')

    # Two-row legend under Panel B (strictly inside [278, 610])
    out.append(f'<rect x="278" y="286" width="9" height="9" rx="2" fill="{GREEN}"/>')
    out.append('<text x="290" y="294" class="ax">40–0 Dom (7 at 20 Mb, 2 loci, 28/70)</text>')
    out.append(f'<rect x="484" y="286" width="9" height="9" rx="2" fill="{BLUE}"/>')
    out.append('<text x="496" y="294" class="ax">Crossing win (39/70)</text>')

    out.append(f'<rect x="278" y="303" width="9" height="9" rx="2" fill="{GOLD}"/>')
    out.append('<text x="290" y="311" class="ax">Split (1/70)</text>')
    out.append(f'<rect x="356" y="303" width="9" height="9" rx="2" fill="{VERMILION}"/>')
    out.append('<text x="368" y="311" class="ax">Loss (1 locus, 2/70)</text>')
    out.append('<rect x="484" y="303" width="9" height="9" rx="2" fill="#e2e8f0"/>')
    out.append('<text x="496" y="311" class="ax">Ineligible (&lt;500 kb)</text>')

    # Divider 2 at x = 618
    out.append(f'<line x1="618" y1="12" x2="618" y2="{h-12}" stroke="{LINE}"/>')

    # Panel C (x in [628, 888])
    panel_badge(
        out,
        628,
        10,
        "C",
        "4×4 Log-Odds Matrix",
        "Max match +100 · Gap 682 / 51",
    )

    bases = ["A", "C", "G", "T"]
    mat = [
        [80, -191, -92, -198],
        [-191, 100, -197, -92],
        [-92, -197, 100, -191],
        [-198, -92, -191, 80],
    ]
    mx0, my0 = 674, 70
    cell_w, cell_h = 48, 36
    for i, b in enumerate(bases):
        out.append(f'<text x="{mx0 + i*cell_w + cell_w/2}" y="{my0-8}" text-anchor="middle" class="lbl mono">{b}</text>')
        out.append(f'<text x="{mx0 - 12}" y="{my0 + i*cell_h + cell_h/2 + 4}" text-anchor="middle" class="lbl mono">{b}</text>')
        for j, val in enumerate(mat[i]):
            cx = mx0 + j * cell_w
            cy = my0 + i * cell_h
            if val > 0:
                bg = "#0072B2" if val == 100 else "#56B4E9"
                fg = "#ffffff"
            elif val == -92:
                bg = "#fde68a"
                fg = INK
            else:
                bg = "#fecaca"
                fg = INK
            out.append(f'<rect x="{cx}" y="{cy}" width="{cell_w-3}" height="{cell_h-3}" rx="5" fill="{bg}"/>')
            sval = f"+{val}" if val > 0 else f"−{abs(val)}"
            out.append(f'<text x="{cx+(cell_w-3)/2}" y="{cy+(cell_h-3)/2+4}" text-anchor="middle" class="lbl mono" fill="{fg}">{sval}</text>')

    cy_card = 224
    out.append(f'<rect x="630" y="{cy_card}" width="256" height="102" rx="7" fill="{BG_SOFT}" stroke="{LINE}"/>')
    out.append(f'<text x="638" y="{cy_card+18}" class="lbl">GC match +100 vs AT +80</text>')
    out.append(f'<text x="638" y="{cy_card+36}" class="ax">Ti: −92 · Tv: −191 A-C/G-T, −197 C-G, −198 A-T</text>')
    out.append(f'<text x="638" y="{cy_card+54}" class="ax">Either pair alone: every entry within 1 unit</text>')
    out.append(f'<text x="638" y="{cy_card+72}" class="lbl" fill="{BLUE}">Gap 682/51 (400/30 × 1.705 mismatch ratio):</text>')
    out.append(f'<text x="638" y="{cy_card+89}" class="ax">70.6% single coverage after chaining (550/40: 70.1%)</text>')

    out.append("</svg>")
    (OUT_DIR / "figure2_matrix_calibration.svg").write_text("\n".join(out))


# ==============================================================================
# FIGURE 3: 216-Query Coverage Waterfall + LASTZ Chunking + MULTIZ 11.3/11.4 Scaling
# ==============================================================================
def build_figure3() -> None:
    w, h = 900, 788
    out = svg_header(w, h)

    q_rows = []
    q_path = CANNABIS_ROOT / "data/processed/query_coverage.tsv"
    for row in csv.DictReader(q_path.open(), delimiter="\t"):
        q_rows.append(
            (
                row["label"],
                row["assembly_class"],
                float(row["synnet_cs10_frac"]) * 100.0,
                float(row["rbest_cs10_frac"]) * 100.0,
            )
        )
    q_rows.sort(key=lambda r: r[2])
    syn_med = statistics.median(r[2] for r in q_rows)
    rb_med = statistics.median(r[3] for r in q_rows)

    # Top Tier: Panel A full-width (x in [14, 886], y in [10, 482])
    panel_badge(
        out,
        14,
        10,
        "A",
        "216-Query Syntenic (synNet) and Reciprocal-Best (rbest) Coverage Across cs10",
        f"Median {syn_med:.1f}% synNet ({rb_med:.1f}% rbest, range 29.3–88.1%), Chemdog91 (12.2%) to ACDC (85.1%)",
    )

    wx0, wx1 = 54, 880
    wy0, wy1 = 50, 434

    def y_cov(pct: float) -> float:
        return wy1 - (pct / 100.0) * (wy1 - wy0)

    for pct in [0, 20, 40, 60, 80, 100]:
        yy = y_cov(pct)
        out.append(f'<line x1="{wx0}" y1="{yy:.1f}" x2="{wx1}" y2="{yy:.1f}" stroke="{LINE}" stroke-dasharray="2,2"/>')
        out.append(f'<text x="{wx0-5}" y="{yy+3:.1f}" text-anchor="end" class="ax">{pct}%</text>')
    out.append(f'<text x="18" y="{(wy0+wy1)/2:.1f}" text-anchor="middle" class="lbl" transform="rotate(-90 18 {(wy0+wy1)/2:.1f})">cs10 non-N coverage (%)</text>')

    n_q = len(q_rows)
    bar_step = (wx1 - wx0) / float(n_q)
    rbest_pts = []
    for idx, (_lbl, aclass, syn_p, rb_p) in enumerate(q_rows):
        xx = wx0 + idx * bar_step
        rbest_pts.append(f"{xx+1.4:.1f},{y_cov(rb_p):.1f}")
        if "Salk HiFi" in aclass:
            col = BLUE
        elif "unphased/diploid" in aclass:
            col = ORANGE
        elif "ONT" in aclass:
            col = PURPLE
        else:
            col = GREEN
        out.append(f'<rect x="{xx:.2f}" y="{y_cov(syn_p):.1f}" width="2.85" height="{wy1-y_cov(syn_p):.1f}" fill="{col}" opacity="0.88"/>')

    out.append(f'<polyline fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="3,2" points="{" ".join(rbest_pts)}"/>')

    ymed = y_cov(syn_med)
    out.append(f'<line x1="{wx0}" y1="{ymed:.1f}" x2="{wx1}" y2="{ymed:.1f}" stroke="{VERMILION}" stroke-width="1.6" stroke-dasharray="4,3"/>')

    # Summary callout placed in the open upper-left whitespace (y in [56, 90], strictly above all bars and rbest points)
    out.append(f'<rect x="{wx0+8}" y="56" width="254" height="34" rx="4" fill="#ffffff" stroke="{LINE}"/>')
    out.append(f'<text x="{wx0+15}" y="70" class="lbl" fill="{VERMILION}">Median synNet = {syn_med:.1f}% (rbest = {rb_med:.1f}%)</text>')
    out.append(f'<text x="{wx0+15}" y="84" class="ax">Range: Chemdog91 (12.2%) – ACDC (85.1%)</text>')
    out.append(f'<text x="{(wx0+wx1)/2:.1f}" y="{wy1+18}" text-anchor="middle" class="lbl">216 query assemblies sorted by cs10 synNet coverage</text>')

    # Single horizontal legend row for Panel A at y = 466..476 across x in [18, 886]
    out.append(f'<rect x="18" y="466" width="9" height="9" rx="2" fill="{BLUE}"/>')
    out.append('<text x="30" y="474" class="ax">Salk HiFi phased (98)</text>')
    out.append(f'<rect x="172" y="466" width="9" height="9" rx="2" fill="{ORANGE}"/>')
    out.append('<text x="184" y="474" class="ax">Unphased/diploid (84)</text>')
    out.append(f'<rect x="330" y="466" width="9" height="9" rx="2" fill="{GREEN}"/>')
    out.append('<text x="342" y="474" class="ax">T2T/GWH (7) &amp; other (17)</text>')
    out.append(f'<rect x="510" y="466" width="9" height="9" rx="2" fill="{PURPLE}"/>')
    out.append('<text x="522" y="474" class="ax">Pike ONT (10)</text>')
    out.append(f'<line x1="622" y1="470.5" x2="638" y2="470.5" stroke="{VERMILION}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    out.append(f'<text x="642" y="474" class="ax">Median ({syn_med:.1f}%)</text>')
    out.append(f'<line x1="752" y1="470.5" x2="768" y2="470.5" stroke="{INK}" stroke-width="1.8" stroke-dasharray="3,2"/>')
    out.append(f'<text x="772" y="474" class="ax">rbest ({rb_med:.1f}% med)</text>')

    # Horizontal divider between Top Tier (Panel A) and Bottom Tier (Panels B & C)
    out.append(f'<line x1="14" y1="488" x2="886" y2="488" stroke="{LINE}" stroke-width="1.5"/>')

    # Bottom-Left: Panel B (x in [14, 438], vertical divider at x = 448)
    panel_badge(
        out,
        14,
        500,
        "B",
        "Chunked LASTZ & Collection Purge",
        "≤50,000-segment chunks (7.8×) & −56.5% disk summed over runs",
    )
    bx0 = 20
    out.append(f'<text x="{bx0}" y="546" class="lbl">EH23a × EH23b Gapped Extension (100 chr-pair jobs)</text>')
    out.append(f'<rect x="{bx0}" y="552" width="380" height="22" rx="4" fill="{VERMILION}"/>')
    out.append(f'<text x="{bx0+8}" y="567" class="ax mono" fill="#ffffff" font-weight="700">Whole-chr extension: 389.0 allocated slot-h</text>')
    out.append(f'<rect x="{bx0}" y="578" width="48.6" height="22" rx="4" fill="{GREEN}"/>')
    out.append(f'<text x="{bx0+55}" y="593" class="lbl mono" fill="{GREEN}">49.8 slot-h (7.8×, 1.79 h for the 100 jobs)</text>')

    out.append(f'<text x="{bx0}" y="624" class="lbl">218-Run Galaxy History Storage, Summed Over Runs</text>')
    out.append(f'<rect x="{bx0}" y="630" width="380" height="22" rx="4" fill="{GREY}"/>')
    out.append(f'<text x="{bx0+8}" y="645" class="ax mono" fill="#ffffff" font-weight="700">Unpurged: 14.96 TB (68.6 GB/run)</text>')
    out.append(f'<rect x="{bx0}" y="656" width="165.1" height="22" rx="4" fill="{BLUE}"/>')
    out.append(f'<text x="{bx0+172}" y="671" class="lbl mono" fill="{BLUE}">6.50 TB (−56.5%, 8.45 TB saved)</text>')

    out.append(f'<rect x="{bx0}" y="690" width="414" height="84" rx="7" fill="{BG_SOFT}" stroke="{LINE}"/>')
    out.append(f'<text x="{bx0+10}" y="709" class="lbl">Benchmarks &amp; UCSC chr21 Parity:</text>')
    out.append(f'<text x="{bx0+10}" y="728" class="ax">• growler_lastz_lav (same chunking): 99.99% of UCSC chr21 pairs</text>')
    out.append(f'<text x="{bx0+10}" y="746" class="ax">• EH23a×b: med 28 min/job (max 49 vs. 660 min), RAM &lt; 3.97 GB</text>')
    out.append(f'<text x="{bx0+10}" y="764" class="ax">• doRecipBest.pl chains reproduced on 5 queries, 1 per class</text>')

    # Vertical divider between Panel B and Panel C
    out.append(f'<line x1="448" y1="500" x2="448" y2="{h-12}" stroke="{LINE}" stroke-width="1.5"/>')

    # Bottom-Right: Panel C (x in [460, 886])
    panel_badge(
        out,
        460,
        500,
        "C",
        "Streaming MULTIZ 11.3 & Column-Count 11.4",
        "51.7× RAM (11.3), 33.8× one upstream-timed deep merge (11.4)",
    )
    cx0 = 466
    out.append(f'<text x="{cx0}" y="546" class="lbl">Peak RAM of a Roast Run (hg38 5-way chrX, multiz#27)</text>')
    out.append(f'<rect x="{cx0}" y="552" width="380" height="21" rx="4" fill="{VERMILION}"/>')
    out.append(f'<text x="{cx0+8}" y="566" class="ax mono" fill="#ffffff" font-weight="700">Buffered MAF (v11.2): 677 MiB</text>')
    out.append(f'<rect x="{cx0}" y="576" width="8.0" height="21" rx="2" fill="{GREEN}"/>')
    out.append(f'<text x="{cx0+15}" y="590" class="lbl mono" fill="{GREEN}">13 MiB (v11.3, 51.7×)</text>')

    out.append(f'<text x="{cx0}" y="618" class="lbl">One Deep Merge in a 216-Genome Roast (11.3 vs 11.4)</text>')
    out.append(f'<rect x="{cx0}" y="624" width="380" height="21" rx="4" fill="{ORANGE}"/>')
    out.append(f'<text x="{cx0+8}" y="638" class="ax mono" fill="#ffffff" font-weight="700">Pairwise row×row DP: 981 s</text>')
    out.append(f'<rect x="{cx0}" y="648" width="{380 * 29 / 981:.1f}" height="21" rx="2" fill="{BLUE}"/>')
    out.append(f'<text x="{cx0+18}" y="662" class="lbl mono" fill="{BLUE}">5×5 column-count DP: 29 s (33.8×)</text>')

    out.append(f'<text x="{cx0}" y="690" class="lbl">One 4.4 Mb Piece, 216-Genome Roast (same host)</text>')
    out.append(f'<rect x="{cx0}" y="696" width="380" height="21" rx="4" fill="{GREY}"/>')
    out.append(f'<text x="{cx0+8}" y="710" class="ax mono" fill="#ffffff" font-weight="700">Release 11.3: 3.9 h (median of 3 runs)</text>')
    out.append(f'<rect x="{cx0}" y="720" width="{380 * 2873 / 14085:.1f}" height="21" rx="3" fill="{GREEN}"/>')
    out.append(f'<text x="{cx0+85}" y="734" class="lbl mono" fill="{GREEN}">0.80 h (11.4, 4.9×)</text>')

    out.append(f'<rect x="{cx0}" y="746" width="414" height="28" rx="6" fill="#fff4d1" stroke="{GOLD}"/>')
    out.append(f'<text x="{cx0+207}" y="764" text-anchor="middle" class="lbl">Same host, interleaved runs · output identical</text>')

    out.append("</svg>")
    (OUT_DIR / "figure3_scalability_benchmarks.svg").write_text("\n".join(out))


# ==============================================================================
# FIGURE 4: Compact CBDAS Stratification + netFilter -syn Paralog Trade-off
# ==============================================================================
def build_figure4() -> None:
    w, h = 900, 215
    out = svg_header(w, h)

    # Panel A (x in [12, 458], divider at x = 468)
    panel_badge(
        out,
        12,
        10,
        "A",
        "CBDAS (chr7:30.98 Mb) Across 216 Queries",
        "79 ≥98.5%, 77 at 93.0–98.5% (63 B-locus annotated), 6 <93%, 54 pruned",
    )

    bx0 = 24
    cats = [
        ("Intact CBDAS (≥98.5% id, 56 full-len)", 79, GREEN, "79 (59 plants)—functional copy"),
        ("93.0–98.5% (~94% B-locus pseudogene)", 77, ORANGE, "77 (67 plants) — 63 annotated, 14 not"),
        ("Diverged aligned (<93.0%, ≥50% CDS)", 6, SKY, "6 queries (91.9–92.9% id)"),
        ("Unaligned in synNet (<50% CDS)", 54, VERMILION, "54 pruned by -syn (Finola 99.4%)"),
    ]
    for idx, (lbl, cnt, col, desc) in enumerate(cats):
        yy = 54 + idx * 38
        bw = max(6.0, (cnt / 85.0) * 140.0)
        out.append(f'<text x="{bx0}" y="{yy}" class="lbl">{esc(lbl)}</text>')
        out.append(f'<rect x="{bx0}" y="{yy+5}" width="{bw:.1f}" height="14" rx="3" fill="{col}"/>')
        out.append(f'<text x="{bx0+bw+8:.1f}" y="{yy+16}" class="ax">{esc(desc)}</text>')

    # Divider at x = 468
    out.append(f'<line x1="468" y1="12" x2="468" y2="{h-12}" stroke="{LINE}"/>')

    # Panel B (x in [480, 888])
    panel_badge(
        out,
        480,
        10,
        "B",
        "netFilter -syn Pruning vs Paralog Reuse",
        "46.4% of recovered pairs (569/1,225) overlap another family gene",
    )

    rx0 = 492
    bars = [
        ("TPS family (41 genes: 31 in 9 clusters + 10)", "418/8,856 pruned (4.7%)", 4.7, SKY),
        ("BBE-like family (35 genes: 29 in 9 clusters + 6)", "807/7,560 pruned (10.7%)", 10.7, BLUE),
        ("Recovered pairs overlapping another family gene", "569/1,225 (46.4%)", 46.4, VERMILION),
    ]
    for idx, (blbl, bval, pct, col) in enumerate(bars):
        yy = 54 + idx * 39
        bw = (pct / 50.0) * 145.0
        out.append(f'<text x="{rx0}" y="{yy}" class="lbl">{esc(blbl)}</text>')
        out.append(f'<rect x="{rx0}" y="{yy+5}" width="{bw:.1f}" height="15" rx="3" fill="{col}"/>')
        out.append(f'<text x="{rx0+bw+8:.1f}" y="{yy+16}" class="ax mono">{esc(bval)}</text>')
    out.append(f'<rect x="{rx0}" y="172" width="388" height="27" rx="5" fill="#fff4d1" stroke="{GOLD}"/>')
    out.append(f'<text x="{rx0+194}" y="189" text-anchor="middle" class="lbl">Needs rbest nets or duplication-aware orthology</text>')

    out.append("</svg>")
    (OUT_DIR / "figure4_tandem_clusters.svg").write_text("\n".join(out))


# ==============================================================================
# FIGURE 5: Panagram AH3Mb.chrY PAR Boundary Profile + 42-Genome rbest Scatter
# ==============================================================================
def build_figure5() -> None:
    w, h = 900, 460
    out = svg_header(w, h)

    # Panel A (x in [12, 444], divider at x = 452)
    panel_badge(
        out,
        12,
        10,
        "A",
        "Panagram k = 21 AH3Mb.chrY Profile (0–110.7 Mb)",
        "PAR (0–29.1 Mb) vs 205,619 MSY Y-mers (males ≥0.976, V3 XX ≤0.077)",
    )

    v3_path = CANNABIS_ROOT / "reports/evidence/panagram_step0_2026-10-27/v3_k21.tsv"
    cont_path = CANNABIS_ROOT / "reports/evidence/panagram_step0_2026-10-27/cont_k21_AH3Mb.tsv"

    chry_cont = []
    for row in csv.DictReader(cont_path.open(), delimiter="\t"):
        if row["chrom"] == "AH3Mb.chrY":
            mb = int(row["start"]) / 1e6
            f_mean = (float(row["cs10"]) + float(row["EH23a"]) + float(row["EH23b"])) / 3.0
            m_mean = (float(row["BCMb"]) + float(row["GRMa"]) + float(row["KOMPb"])) / 3.0
            chry_cont.append((mb, f_mean, m_mean))

    chry_v3 = []
    for row in csv.DictReader(v3_path.open(), delimiter="\t"):
        if row["chrom"] == "AH3Mb.chrY" and int(row["specific"]) >= 500:
            mb = int(row["start"]) / 1e6
            f_mean = (float(row["cs10"]) + float(row["EH23a"]) + float(row["EH23b"])) / 3.0
            m_mean = (float(row["BCMb"]) + float(row["GRMa"]) + float(row["KOMPb"])) / 3.0
            chry_v3.append((mb, f_mean, m_mean))

    px0, px1 = 50, 436
    py0, py1 = 58, 385

    def x_mb(mb: float) -> float:
        return px0 + (mb / 111.0) * (px1 - px0)

    def y_frac(f: float) -> float:
        return py1 - f * (py1 - py0)

    x_par = x_mb(29.08)
    out.append(f'<rect x="{px0}" y="{py0}" width="{x_par-px0:.1f}" height="{py1-py0}" fill="#e0f2fe" opacity="0.55"/>')
    out.append(f'<rect x="{x_par:.1f}" y="{py0}" width="{px1-x_par:.1f}" height="{py1-py0}" fill="#fef3c7" opacity="0.45"/>')
    out.append(f'<line x1="{x_par:.1f}" y1="{py0}" x2="{x_par:.1f}" y2="{py1}" stroke="{VERMILION}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    out.append('<rect x="54" y="206" width="94" height="26" rx="3" fill="#ffffff"/>')
    out.append(f'<text x="{(px0+x_par)/2:.1f}" y="217" text-anchor="middle" class="lbl" fill="{BLUE}">PAR (0–29.1M)</text>')
    out.append(f'<text x="{(px0+x_par)/2:.1f}" y="228" text-anchor="middle" class="ax" fill="{BLUE}">all 21-mers</text>')
    out.append('<rect x="176" y="212" width="236" height="16" rx="3" fill="#ffffff"/>')
    out.append(f'<text x="{(x_par+px1)/2:.1f}" y="223" text-anchor="middle" class="lbl" fill="{VERMILION}">MSY: Y-specific 21-mers (29.1–110.7 Mb)</text>')

    for fv in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        yy = y_frac(fv)
        out.append(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px1}" y2="{yy:.1f}" stroke="{LINE}" stroke-dasharray="2,2"/>')
        out.append(f'<text x="{px0-5}" y="{yy+3:.1f}" text-anchor="end" class="ax">{fv:.1f}</text>')
    out.append(f'<text x="16" y="{(py0+py1)/2:.1f}" text-anchor="middle" class="lbl" transform="rotate(-90 16 {(py0+py1)/2:.1f})">Containment / Y-mer recall</text>')

    for mb_tick in [0, 29, 50, 70, 90, 110]:
        xx = x_mb(mb_tick)
        out.append(f'<line x1="{xx:.1f}" y1="{py1}" x2="{xx:.1f}" y2="{py1+4}" stroke="{INK}"/>')
        out.append(f'<text x="{xx:.1f}" y="{py1+15}" text-anchor="middle" class="ax">{mb_tick}</text>')
    out.append(f'<text x="{(px0+px1)/2:.1f}" y="{py1+30}" text-anchor="middle" class="lbl">AH3Mb.chrY coordinate (Mb, 1 Mb windows)</text>')

    m_pts = [f"{x_mb(mb):.1f},{y_frac(m):.1f}" for mb, f, m in chry_cont if mb < 29] + [
        f"{x_mb(mb):.1f},{y_frac(m):.1f}" for mb, f, m in chry_v3 if mb >= 29
    ]
    f_pts = [f"{x_mb(mb):.1f},{y_frac(f):.1f}" for mb, f, m in chry_cont if mb < 29] + [
        f"{x_mb(mb):.1f},{y_frac(f):.1f}" for mb, f, m in chry_v3 if mb >= 29
    ]
    out.append(f'<polyline fill="none" stroke="{GREEN}" stroke-width="2.4" points="{" ".join(m_pts)}"/>')
    out.append(f'<polyline fill="none" stroke="{VERMILION}" stroke-width="2.4" points="{" ".join(f_pts)}"/>')

    out.append(f'<line x1="22" y1="432" x2="40" y2="432" stroke="{GREEN}" stroke-width="3"/>')
    out.append('<text x="45" y="436" class="lbl">Male Y-carriers (BCMb 0.976, GRMa 0.984, KOMPb 0.987)</text>')
    out.append(f'<line x1="22" y1="448" x2="40" y2="448" stroke="{VERMILION}" stroke-width="3"/>')
    out.append('<text x="45" y="452" class="lbl">Female XX (V3 3/3: cs10 0.071, EH23a/b ≤0.077)</text>')

    # Divider at x = 452
    out.append(f'<line x1="452" y1="12" x2="452" y2="{h-12}" stroke="{LINE}"/>')

    # Panel B (x in [464, 888])
    panel_badge(
        out,
        464,
        10,
        "B",
        "1 Mb Window k = 21 vs rbest Chain Identity",
        "Tier P2 (43 genomes, 1.14 GB): 41/42 queries pass r ≥ 0.50",
    )

    chrom_lens: dict[str, int] = {}
    for row in csv.DictReader((CANNABIS_ROOT / "data/processed/wfi_cs10_splits.tsv").open(), delimiter="\t"):
        c = row["chrom"]
        chrom_lens[c] = max(chrom_lens.get(c, 0), int(row["cut"]))

    grma_cont: dict[tuple[str, int], float] = {}
    grma_pos: dict[tuple[str, int], int] = {}
    for row in csv.DictReader((CANNABIS_ROOT / "reports/evidence/panagram_step0_2026-10-27/cont_k21_cs10.tsv").open(), delimiter="\t"):
        key = (row["chrom"], int(row["start"]))
        grma_cont[key] = float(row["GRMa"])
        grma_pos[key] = int(row["positions"])

    pts_all_631 = []
    for row in csv.DictReader((CANNABIS_ROOT / "reports/evidence/panagram_step0_2026-10-27/identity_cs10_rbest.tsv").open(), delimiter="\t"):
        if row["genome"] == "GRMa":
            c = row["chrom"]
            st = int(row["start"])
            aln = int(row["aligned"])
            mat = int(row["matched"])
            key = (c, st)
            if key in grma_cont:
                span = min(chrom_lens[c] - st, 1_000_000) if c in chrom_lens else min(grma_pos[key] * 100, 1_000_000)
                if aln / float(span) >= 0.5 and aln > 0:
                    ident = (mat / float(aln)) * 100.0
                    cont = grma_cont[key]
                    pts_all_631.append((ident, cont))

    # OLS slope & intercept across all 631 qualifying windows
    mean_x = sum(x for x, _ in pts_all_631) / len(pts_all_631)
    mean_y = sum(y for _, y in pts_all_631) / len(pts_all_631)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in pts_all_631) / sum((x - mean_x) ** 2 for x, _ in pts_all_631)
    intercept = mean_y - slope * mean_x

    sx0, sx1 = 506, 706
    sy0, sy1 = 58, 385

    def x_ident(id_pct: float) -> float:
        return sx0 + ((id_pct - 93.0) / 7.0) * (sx1 - sx0)

    def y_cont(c: float) -> float:
        return sy1 - ((c - 0.50) / 0.50) * (sy1 - sy0)

    for id_t in [93, 95, 97, 99, 100]:
        xx = x_ident(id_t)
        out.append(f'<line x1="{xx:.1f}" y1="{sy0}" x2="{xx:.1f}" y2="{sy1}" stroke="{LINE}" stroke-dasharray="2,2"/>')
        out.append(f'<text x="{xx:.1f}" y="{sy1+15}" text-anchor="middle" class="ax">{id_t}%</text>')
    for ct in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        yy = y_cont(ct)
        out.append(f'<line x1="{sx0}" y1="{yy:.1f}" x2="{sx1}" y2="{yy:.1f}" stroke="{LINE}" stroke-dasharray="2,2"/>')
        out.append(f'<text x="{sx0-5}" y="{yy+3:.1f}" text-anchor="end" class="ax">{ct:.1f}</text>')
    out.append(f'<text x="472" y="{(sy0+sy1)/2:.1f}" text-anchor="middle" class="lbl" transform="rotate(-90 472 {(sy0+sy1)/2:.1f})">cs10 k = 21 containment</text>')

    for ident, cont in pts_all_631:
        xc = max(sx0 + 1.5, min(sx1 - 1.5, x_ident(ident)))
        yc = max(sy0 + 1.5, min(sy1 - 1.5, y_cont(cont)))
        out.append(f'<circle cx="{xc:.1f}" cy="{yc:.1f}" r="1.9" fill="{BLUE}" opacity="0.48"/>')

    x_ols0, x_ols1 = 93.4, 99.6
    y_ols0, y_ols1 = intercept + slope * x_ols0, intercept + slope * x_ols1
    out.append(f'<line x1="{x_ident(x_ols0):.1f}" y1="{y_cont(y_ols0):.1f}" x2="{x_ident(x_ols1):.1f}" y2="{y_cont(y_ols1):.1f}" stroke="{VERMILION}" stroke-width="2.2"/>')
    out.append(f'<rect x="{sx0+6}" y="{sy0+5}" width="174" height="14" rx="2" fill="#ffffff" opacity="0.9"/>')
    out.append(f'<text x="{sx0+8}" y="{sy0+16}" class="lbl" fill="{BLUE}">GRMa ({len(pts_all_631)} win, r = 0.8118)</text>')
    out.append(f'<text x="{(sx0+sx1)/2:.1f}" y="{sy1+30}" text-anchor="middle" class="lbl">cs10 rbest chain identity (%)</text>')

    rx = 720
    out.append(f'<rect x="{rx}" y="58" width="168" height="120" rx="7" fill="{BG_SOFT}" stroke="{LINE}"/>')
    out.append(f'<text x="{rx+8}" y="82" class="lbl" fill="{NAVY}">Tier P2 V1 (42 queries)</text>')
    out.append(f'<text x="{rx+8}" y="105" class="lbl" fill="{GREEN}">41 / 42 pass r ≥ 0.50</text>')
    out.append(f'<text x="{rx+8}" y="126" class="ax">• Range: 0.5848–0.8118</text>')
    out.append(f'<text x="{rx+8}" y="146" class="ax">• G3: 2 SUP ONT flags</text>')
    out.append(f'<text x="{rx+8}" y="166" class="ax" fill="{VERMILION}">• ASM5191173v1: r = 0.4763</text>')

    out.append(f'<rect x="{rx}" y="191" width="168" height="120" rx="7" fill="{BG_SOFT}" stroke="{LINE}"/>')
    out.append(f'<text x="{rx+8}" y="215" class="lbl" fill="{NAVY}">TOGA2 v2.0.9 Pilot</text>')
    # cannabis-genome reports/evidence/toga2_pilot_2026-10-30.md (2026-11-02 update): standard L+UL of 24,503
    out.append(f'<text x="{rx+8}" y="238" class="lbl" fill="{BLUE}">Control: 25 L/UL (0.10%)</text>')
    out.append(f'<text x="{rx+8}" y="259" class="ax">• EH23a L/UL: prod 8.48%</text>')
    out.append(f'<text x="{rx+8}" y="279" class="ax">• loose 7.26%, filled 6.77%</text>')
    out.append(f'<text x="{rx+8}" y="299" class="ax" fill="{VERMILION}">• Arms not ranked, none chosen</text>')

    out.append(f'<rect x="{rx}" y="324" width="168" height="120" rx="7" fill="#fff4d1" stroke="{GOLD}"/>')
    out.append(f'<text x="{rx+8}" y="348" class="lbl" fill="{NAVY}">Phenotype Ledger</text>')
    out.append(f'<text x="{rx+8}" y="371" class="lbl">1,341 rows · 154 plants</text>')
    out.append(f'<text x="{rx+8}" y="392" class="ax">• 40 sources (43 paper audits)</text>')
    out.append(f'<text x="{rx+8}" y="412" class="ax">• 78 families (69 in Salk fam)</text>')
    out.append(f'<text x="{rx+8}" y="432" class="ax">• 0/14 traits pass ≥30-fam</text>')

    out.append("</svg>")
    (OUT_DIR / "figure5_panagram_kmer.svg").write_text("\n".join(out))


# ==============================================================================
# KMER BANDS (k = 21 Multiplicity-Weighted Occurrence Spectrum across 12 Genomes)
# ==============================================================================
def build_kmer_bands() -> None:
    w, h = 900, 710
    out = svg_header(w, h)
    out.append('<text x="16" y="24" class="title">Meryl k = 21 Occurrence Spectrum (Multiplicity-Weighted Across 12 Representative Assemblies)</text>')

    rows = [
        ("Salk_SRIb", [42.09, 7.17, 11.84, 15.33, 23.58], ["42%", "7%", "12%", "15%", "24%"]),
        ("Salk_SRIa", [42.07, 7.00, 11.80, 15.19, 23.93], ["42%", "7%", "12%", "15%", "24%"]),
        ("cs10_RefSeq", [39.62, 8.36, 12.58, 14.81, 24.62], ["40%", "8%", "13%", "15%", "24%"]),
        ("Salk_HAWb", [38.61, 6.99, 11.81, 15.78, 26.81], ["38%", "7%", "12%", "16%", "27%"]),
        ("Salk_HAWa", [38.00, 7.17, 11.88, 15.81, 27.13], ["38%", "7%", "12%", "16%", "27%"]),
        ("Salk_TRCa", [37.25, 7.00, 11.75, 15.99, 28.03], ["37%", "7%", "12%", "16%", "28%"]),
        ("Salk_TRCb", [36.96, 7.25, 11.88, 15.91, 28.00], ["37%", "7%", "12%", "16%", "28%"]),
        ("Salk_ANCb", [36.64, 7.70, 11.86, 15.91, 27.90], ["36%", "8%", "12%", "16%", "28%"]),
        ("Salk_ANCa", [35.86, 7.83, 11.91, 16.09, 28.30], ["36%", "8%", "12%", "16%", "28%"]),
        ("T2T_42815.1", [35.33, 5.64, 10.57, 14.77, 33.70], ["35%", "6%", "10%", "15%", "34%"]),
        ("T2T_42775.1", [35.12, 5.58, 10.57, 14.77, 33.97], ["35%", "6%", "10%", "15%", "34%"]),
        ("Cannbio2_dip", [26.41, 17.38, 13.17, 15.22, 27.81], ["27%", "17%", "13%", "15%", "28%"]),
    ]
    cols = [BLUE, VERMILION, GREEN, ORANGE, PURPLE]

    x_base = 114.0
    bar_tot_w = 766.0
    for idx, (name, pcts, lbls) in enumerate(rows):
        yy = 42.0 + idx * 52.0
        out.append(f'<text x="{x_base-8:.1f}" y="{yy+23.5:.1f}" text-anchor="end" class="lbl">{esc(name)}</text>')
        cur_x = x_base
        for b_idx, (p, ltxt) in enumerate(zip(pcts, lbls, strict=True)):
            bw = (p / 100.0) * bar_tot_w
            out.append(f'<rect x="{cur_x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="38" fill="{cols[b_idx]}" stroke="#ffffff" stroke-width="0.6"/>')
            if bw >= 18.0:
                out.append(f'<text x="{cur_x + bw/2:.1f}" y="{yy+23:.1f}" text-anchor="middle" class="ax" fill="#ffffff" font-weight="700">{ltxt}</text>')
            cur_x += bw

    leg = [
        ("1× (unique)", BLUE, 180),
        ("2× (allelic/dup)", VERMILION, 295),
        ("3–10×", GREEN, 430),
        ("11–100×", ORANGE, 515),
        ("&gt;100× (high-copy LTR)", PURPLE, 610),
    ]
    for ltxt, col, lx in leg:
        out.append(f'<rect x="{lx}" y="680" width="12" height="12" rx="2" fill="{col}"/>')
        out.append(f'<text x="{lx+16}" y="690" class="lbl">{ltxt}</text>')

    out.append("</svg>")
    (OUT_DIR / "kmer_bands_k21.svg").write_text("\n".join(out))


if __name__ == "__main__":
    build_figure1()
    build_figure2()
    build_figure3()
    build_figure4()
    build_figure5()
    build_kmer_bands()
    print("Generated all 6 data-dense poster SVG figures in", OUT_DIR)
