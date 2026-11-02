#!/usr/bin/env python3
"""Render the 44x44 in VGP diploid curation CSHL poster to poster.pdf and poster-preview.png."""

from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
PAGE_IN = 44
PAGE_PX = PAGE_IN * 96  # 4224 CSS px at 96 dpi


def main() -> None:
    html_path = HERE / "template.html"
    pdf_path = HERE / "poster.pdf"
    png_path = HERE / "poster-preview.png"

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": PAGE_PX, "height": PAGE_PX}, device_scale_factor=0.5)
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        overflow = page.evaluate(
            """() => {
              const out = [];
              for (const el of document.querySelectorAll('body, main, header, footer, section')) {
                if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) {
                  out.push({tag: el.tagName, cls: el.className, sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight});
                }
              }
              return out;
            }"""
        )
        print("overflow:", overflow or "none")
        page.screenshot(path=str(png_path), full_page=False)
        page.pdf(path=str(pdf_path), width=f"{PAGE_IN}in", height=f"{PAGE_IN}in", print_background=True)
        browser.close()
    print("wrote", pdf_path, png_path)


if __name__ == "__main__":
    main()
