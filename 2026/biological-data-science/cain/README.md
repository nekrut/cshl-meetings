# Orbit and Galaxy User-Defined Tools for Reproducible, Auditable Computational Biology

Dannon Baker, Scott Cain, Marius van den Beek, John Chilton, Danielle Callan, Steven Weaver, Nate Coraor, Kelsey Beavers, Michael C. Schatz, Björn Grüning, Sergei L. Kosakovsky Pond, and Anton Nekrutenko. CSHL Biological Data Science, November 4–7, 2026.

## Files

| Path | What it is |
| - | - |
| `orbit_poster_draft.pptx`, `orbit_poster_draft.pdf` | Original PowerPoint draft (`34 × 44 in`) and PDF export |
| `template.html` | Unified Galaxy Style 1 layout (`44 × 44 in`, `@page { size: 44in 44in; margin: 0; }`) |
| `build.py` | Playwright/Chromium renderer producing `orbit-poster.pdf` (`3168 × 3168 pt`) and `poster-preview.png` |
| `orbit-poster.pdf` | Print-ready 44 × 44 in PDF (≥300 PPI figures + embedded TrueType fonts) |
| `figures/` | High-resolution screenshots and reanalysis figures extracted from `orbit_poster_draft.pptx` |
| `qr-*.svg` | Vector QR codes (`galaxyproject.org/agents/orbit`, `udt-signup.galaxyproject.org`, preprint) |

## Rebuild

```bash
python build.py
```
