# Build better skills. Build better workflows. Keep the receipts.

John Chilton, Marius van den Beek, Dannon Baker, Danielle Callan, Scott Cain, Anton Nekrutenko. CSHL Biological Data Science, November 4–7, 2026.

The Galaxy Workflow Foundry: a wiki of typed notes compiled into agent skills, with programs (gxwf, Planemo), not the model, checking each step. The receipts on the poster come from one Foundry run that turned the DengueSeq paper into a tested Galaxy workflow.

`template.html` + `build.py` render the unified 44 × 44 in Galaxy Classic Masthead poster (`poster.pdf`); the original Typst source (`poster.typ`, 44 × 44 in) is also preserved.

## Files

| Path | What it is |
| - | - |
| `template.html`, `build.py` | Unified Galaxy Style 1 layout and Playwright/Chromium builder (`44 × 44 in`) |
| `poster.typ`, `render.py`, `build.sh` | Original Typst layout and build scripts |
| `receipts.json` | Receipt contents (CAST, PINNED, VALIDATED, TESTED), extracted from the run |
| `route.json` | The route diagram's phases |
| `assets/` | White Galaxy logo, QR codes (`qr-foundry.svg`, `qr-preprint.svg`, `qr-repo.svg`, `qr.json`) |
| `fonts/` | Atkinson Hyperlegible Next and Mono, Kalam, IBM Plex Sans and Mono; all SIL OFL 1.1, licences alongside |
| `poster.pdf` | Print-ready 44 × 44 in PDF |

## Rebuild

```bash
python build.py
```

(Or `./build.sh` for the original Typst layout via `uvx --from typst==0.15.0 python render.py`.)

## QR codes

- The Foundry: https://galaxyproject.github.io/foundry/
- Preprint [1]: https://doi.org/10.64898/2026.10.26.761864
- GitHub: https://github.com/galaxyproject/foundry
