#!/usr/bin/env python3
"""Prepare the poster's logo assets.

Records where each institution mark came from and normalises them so the top
strip can size them all by one height and have them look optically equal:

  * trim transparent / background padding, which varies a lot between sources
    (the Penn State PNG is 45% empty vertically, so at a shared CSS height its
    mark printed half the size of the others)
  * key the disassembler logo's white JPEG ground to the poster's paper colour
    so it sits on the page instead of in a white box

Sources, all fetched 2026-11-01:
  Penn State    pennstate_logo.png, already in this folder
  Institut Pasteur  commons.wikimedia.org/wiki/File:Logo_Institut_Pasteur.svg
                    (public domain: below the threshold of originality)
  Temple        commons.wikimedia.org/wiki/File:Temple_University_logo.svg
                (public domain: below the threshold of originality)
  NBIS          nbis.se/nbislogo-green-orange.svg

The two Commons files and the NBIS file are cached next to this script under
logos_src/; re-run with --fetch to pull them again. Trademarks belong to their
institutions and are used here to credit co-author affiliations.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "logos_src"
OUT = HERE.parent

PAPER = (246, 241, 232)

REMOTE = {
    "pasteur.svg": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Logo_Institut_Pasteur.svg",
    "temple.svg": "https://upload.wikimedia.org/wikipedia/commons/3/39/Temple_University_logo.svg",
    "nbis.svg": "https://nbis.se/nbislogo-green-orange.svg",
}
UA = "disassembler-poster/1.0 (acs6613@psu.edu)"

# Rasterised wide enough that a 30mm-tall mark on the poster still clears
# 600 dpi.
RASTER_WIDTH = 2400


def fetch() -> None:
    SRC.mkdir(parents=True, exist_ok=True)
    for name, url in REMOTE.items():
        dest = SRC / name
        subprocess.run(["curl", "-sSL", "-A", UA, "-o", str(dest), url], check=True)
        print(f"[get] {name}")


def trim(im: Image.Image) -> Image.Image:
    """Crop to the mark itself, whatever the file's own padding."""
    bbox = im.split()[3].getbbox()
    return im.crop(bbox) if bbox else im


def rasterise(name: str, out_name: str) -> None:
    import cairosvg

    tmp = SRC / (out_name + ".raw.png")
    cairosvg.svg2png(url=str(SRC / name), write_to=str(tmp),
                     output_width=RASTER_WIDTH)
    im = trim(Image.open(tmp).convert("RGBA"))
    im.save(OUT / out_name)
    tmp.unlink()
    print(f"[save] {out_name}  {im.size}")


def key_white(path: pathlib.Path, out_name: str) -> None:
    """Swap a white photographic ground for the poster's paper colour.

    Graded rather than thresholded: pixels at or above FULL are paper, those
    below SOFT are left alone, and the band between is blended, so the
    antialiased fringe around the artwork does not turn into a white halo.
    """
    FULL, SOFT = 246, 225
    im = Image.open(path).convert("RGB")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            m = min(r, g, b)
            if m >= FULL:
                px[x, y] = PAPER
            elif m > SOFT:
                t = (m - SOFT) / (FULL - SOFT)
                px[x, y] = tuple(round(c + (p - c) * t)
                                 for c, p in zip((r, g, b), PAPER))
    im.save(OUT / out_name)
    print(f"[save] {out_name}  {im.size}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true",
                    help="re-download the source files")
    args = ap.parse_args()
    if args.fetch or not SRC.exists():
        fetch()

    rasterise("pasteur.svg", "logo_pasteur.png")
    rasterise("temple.svg", "logo_temple.png")
    rasterise("nbis.svg", "logo_nbis.png")

    ps = trim(Image.open(OUT / "pennstate_logo.png").convert("RGBA"))
    ps.save(OUT / "logo_pennstate.png")
    print(f"[save] logo_pennstate.png  {ps.size}")

    key_white(OUT / "disassembler_logo.jpg", "logo_disassembler.png")


if __name__ == "__main__":
    sys.exit(main())
