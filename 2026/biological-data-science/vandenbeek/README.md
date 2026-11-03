# From research code to reproducible infrastructure with Galaxy user-defined tools

Marius van den Beek, John Chilton, Dannon Baker. CSHL Biological Data Science, November 4–7, 2026.

`udt-poster.pdf` is the print file: 44 × 44 in, fonts embedded, screenshots at 327 ppi or more.

## Files

| Path | What it is |
| - | - |
| `template.html` | Poster layout and text (HTML/CSS, `@page` 44 × 44 in) |
| `build.py` | Renders `template.html` to `udt-poster.pdf` with headless Chromium |
| `foldseek.yml` | The Foldseek UDT shown in panel C |
| `pvivax-foldseek.gxwf.yml` | The example workflow shown in panel B |
| `shots/` | Screenshots from a local Galaxy; `editor-c.json` positions the callouts |
| `screenshots/` | Scripts and Galaxy config that produce `shots/` |
| `galaxy-logo.svg`, `qr-*.svg` | Logo and QR codes (signup, docs, source) |

## Rebuild the PDF

```bash
uv run --with playwright playwright install chromium-headless-shell
uv run --with playwright python build.py
```

`build.py` reports any panel that overflows the page.

## Retake the screenshots

1. Start a Galaxy (dev, 26.2 or newer, with a built client) on `localhost:8091` using
   `screenshots/galaxy.yml.sample`.
2. From this directory:

   ```bash
   uv run --with requests --with pyyaml python screenshots/setup_galaxy.py .
   uv run --with playwright python screenshots/shoot_form.py .
   uv run --with playwright python screenshots/shoot_editor.py .
   uv run --with playwright python screenshots/shoot_workflow.py .
   ```

The datasets in the screenshots are placeholders; only their names are visible. The workflow is
imported and displayed, not run.
