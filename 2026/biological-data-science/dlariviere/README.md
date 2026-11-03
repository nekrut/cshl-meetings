# Resolving both haplotypes of vertebrate genomes through diploid curation with the VGP Galaxy workflows

Delphine Larivière, Kirsty McCaffrey, Erick Duarte, Ying Chen, Bonhwang Koo, Jack A. Medico, Marco Sollitto, Nadolina Brajuka, Jennifer Balacco, Saim Momin, Patrik Smeds, Jo Wood, Dominic Absolon, Joanna Collins, Tom Mathers, Michael Paulini, Sarah Pelan, Camilla Santos, Kerstin Howe, Danny Jackson, Melissa A. Wilson, Ross Lazarus, Nate Coraor, Marius van den Beek, Michael C. Schatz, Erich D. Jarvis, Anton Nekrutenko, Giulio Formenti. CSHL Biological Data Science, November 4–7, 2026.

## Files

| Path | What it is |
| - | - |
| `template.html` | Unified Galaxy Style 1 poster layout and text (HTML/CSS, `@page { size: 44in 44in; }`) |
| `build.py` | Playwright/Chromium renderer producing `poster.pdf` (`3168 × 3168 pt`) and `poster-preview.png` |
| `poster.pdf` | Pre-rendered 44 × 44 in print PDF (high-resolution figures + embedded TrueType fonts) |
| `figures/` | Extracted high-resolution figure panels and consortium/institutional logos from `Poster BDS2026.svg` |
| `qr-*.svg` | Vector QR codes (`galaxyproject.org/projects/vgp`, `iwc.galaxyproject.org`, `genomeark.org`, GTN assembly tutorials) |
| `Poster BDS2026.svg` | Original submitted SVG draft from PR #4 |

## Rebuild the PDF

```bash
python build.py
```
