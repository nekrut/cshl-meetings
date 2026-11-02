# disassembler: planetary-scale sequence extraction from Logan

Andrew C Seacord, Rayan Chikhi, Danielle Callan, Steven Weaver, Patrik Smeds, Sergei L. Kosakovsky Pond, Anton Nekrutenko. CSHL Biological Data Science, November 4–7, 2026.

Imported from [`as042/disassembler-dump`](https://github.com/as042/disassembler-dump/tree/e1acb6673b6f13294bba494d821e9097c6347a9a/cshl-bds2026) (`cshl-bds2026/` at commit `e1acb66`, `main` `9cdfd1b`).

## Files

| Path | What it is |
| - | - |
| `poster.html` | Unified Galaxy Style 1 poster layout and text (HTML/CSS, `@page { size: 44in 44in; }`) |
| `build.py` | Playwright/Chromium renderer producing `poster.pdf` (`3168 × 3168 pt`) and `poster-preview.png` |
| `poster.pdf` | Pre-rendered 44 × 44 in print PDF (≥300 PPI figures + embedded TrueType fonts) |
| `figures/` | Pre-rendered case-study, metadata, and HyphAeon selection PNGs |
| `qr-*.svg` | Vector QR codes (`disassembler`, Zenodo archive, `HyphAeon`) |
| `logo_*.png`, `hyphaeon_logo.jpeg`, `disassembler_logo.jpg`, `pennstate_logo.png` | Trimmed/keyed logos and sources |
| `scripts/` | Figure plotting scripts (`plot_*.py`, reading data from `as042/disassembler-dump`) and `prepare_logos.py` + `logos_src/` |
| `poster_rough_sketch.jpg` | Layout sketch from upstream |

## Rebuild the PDF

```bash
python build.py
```
