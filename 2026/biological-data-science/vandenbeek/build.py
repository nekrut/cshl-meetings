"""Render the UDT poster: template.html + shots/ -> poster.html -> udt-poster.pdf (44x44 in) and a PNG preview.

Usage: python build.py [preview-scale]   (needs playwright with Chrome or Chromium installed)
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGE_PX = 4224  # 44 in at 96 px/in

# Line numbers as shown in Galaxy's tool editor (it stores lists in block style) -> callout number.
EDITOR_MARKERS = {6: 1, 7: 2, 13: 3, 17: 4, 19: 5, 36: 6}


def launch_browser(p):
    try:
        return p.chromium.launch(channel="chrome", headless=True)
    except Exception:
        return p.chromium.launch(headless=True)


def editor_block() -> str:
    """Tool-editor screenshot with numbered callouts and a vector pointer at the hovered expression."""
    geo = json.loads((HERE / "shots" / "editor-c.json").read_text())
    height = geo["clip"]["height"]
    marks = []
    for line, n in EDITOR_MARKERS.items():
        top = (geo["firstLineTop"] + (line - 0.5) * geo["lineHeight"]) / height * 100
        marks.append(f'<span class="m" style="top:{top:.3f}%">{n}</span>')
    px, py = geo["pointer"]
    pointer = (
        f'<svg class="pointer" style="left:{px / geo["clip"]["width"] * 100:.3f}%;top:{py / height * 100:.3f}%" viewBox="0 0 18 26">'
        '<path d="M2.2 2.2 L2.2 20.2 L6.7 15.7 L9.7 23.2 L12.7 22.0 L9.8 14.8 L15.7 14.8 Z" fill="rgba(0,0,0,0.28)"/>'
        '<path d="M1 1 L1 19 L5.5 14.5 L8.5 22 L11.5 20.8 L8.6 13.6 L14.5 13.6 Z" fill="#111" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/></svg>'
    )
    return (
        '<div class="editor"><img src="shots/editor-c.png" alt="The Foldseek UDT in Galaxy\'s tool editor, with the type hint for inputs.evalue">'
        + pointer
        + "".join(marks)
        + "</div>"
    )


def main() -> None:
    page_html = (HERE / "template.html").read_text().replace("{{EDITOR}}", editor_block())
    out_html = HERE / "poster.html"
    out_html.write_text(page_html)
    pdf, png = HERE / "udt-poster.pdf", HERE / "poster-preview.png"
    scale = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    with sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_page(viewport={"width": PAGE_PX, "height": PAGE_PX}, device_scale_factor=scale)
        page.goto(out_html.as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        overflow = page.evaluate(
            f"""() => [...document.querySelectorAll('section, .col, header, footer, main')]
                .filter(e => e.scrollHeight > e.clientHeight + 2 || e.getBoundingClientRect().bottom > {PAGE_PX} + 1)
                .map(e => (e.querySelector('h2')?.innerText || e.className || e.tagName) + ' ' + e.scrollHeight + '/' + e.clientHeight)"""
        )
        print("overflow:", overflow or "none")
        assert not overflow, f"Overflow detected: {overflow}"
        page.screenshot(path=str(png))
        page.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
        browser.close()
    print("wrote", pdf, png)


if __name__ == "__main__":
    main()
