"""Render the Cannabis sativa 217-way alignment poster: template.html -> cannabis-poster.pdf and a PNG preview.

Usage: python build.py [preview-scale]   (needs playwright with Chrome or Chromium installed)
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGE_PX = 4224  # 44 in at 96 px/in


def launch_browser(p):
    try:
        return p.chromium.launch(channel="chrome", headless=True)
    except Exception:
        return p.chromium.launch(headless=True)


def main() -> None:
    out_html = HERE / "template.html"
    pdf, png = HERE / "cannabis-poster.pdf", HERE / "poster-preview.png"
    scale = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    with sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_page(
            viewport={"width": PAGE_PX, "height": PAGE_PX},
            device_scale_factor=scale,
        )
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
