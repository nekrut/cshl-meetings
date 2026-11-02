#!/usr/bin/env python3
"""Render the 44x44 in Galaxy Workflow Foundry CSHL poster to poster.pdf and poster-preview.png."""

from __future__ import annotations

import html
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
PAGE_IN = 44
PAGE_PX = PAGE_IN * 96  # 4224 CSS px at 96 dpi

SHORT_LABELS = {
    "summarize-paper": ["summarize"],
    "summarize-nextflow": ["summarize"],
    "freeform-summary-to-workflow-brief": ["write a brief"],
    "nextflow-summary-to-workflow-brief": ["write a brief"],
    "workflow-brief-to-galaxy-interface": ["interface"],
    "workflow-brief-to-galaxy-data-flow": ["data flow"],
    "compare-against-iwc-exemplar": ["compare", "to IWC"],
    "workflow-brief-to-galaxy-template": ["template"],
    "advance-galaxy-draft-step": ["draft loop"],
    "test-data-resolution": ["find", "test data"],
    "workflow-brief-to-galaxy-test-plan": ["test plan"],
    "implement-galaxy-workflow-test": ["write", "the test"],
    "validate-galaxy-workflow": ["validate"],
    "run-workflow-test": ["run", "the test"],
    "debug-galaxy-workflow-output": ["debug"],
}


def zig_svg(n: int = 28) -> str:
    w = 1000.0
    step = w / n
    pts = ["0,0"]
    for i in range(n):
        pts.append(f"{(i + 0.5) * step:.1f},24")
        pts.append(f"{(i + 1) * step:.1f},0")
    return (
        f'<svg class="zig" viewBox="0 0 1000 24" preserveAspectRatio="none">'
        f'<polygon points="{" ".join(pts)}" fill="#ffffff"/></svg>'
    )


def r_row(left: str, right: str, bold_left: bool = False) -> str:
    l_html = f"<b>{left}</b>" if bold_left else left
    return f'<div class="r-row"><span>{l_html}</span><span class="dots"></span><span class="rv">{right}</span></div>'


def render_receipt(
    num: int,
    word: str,
    when: str,
    sub: str,
    body_html: str,
    signed: str,
    fig_title: str,
    caption_html: str,
    stamp_text: str | None = None,
) -> str:
    stamp_html = f'<div class="stamp"><span>{html.escape(stamp_text)}</span></div>' if stamp_text else ""
    return f"""<div class="receipt-fig">
  <div class="slip-wrap">
    <div class="slip">
      <div class="r-head">
        <span class="r-word">{html.escape(word)}</span>
        <span class="r-meta"><span class="sym">№</span>{num} &nbsp;{html.escape(when)}</span>
      </div>
      <div class="r-sub">{html.escape(sub)}</div>
      <hr class="r-rule">
      {body_html}
      <hr class="r-rule">
      <div class="r-signed"><span class="sl">SIGNED</span><span class="sv"><mark>{html.escape(signed)}</mark></span></div>
      {stamp_html}
    </div>
    {zig_svg()}
  </div>
  <div class="fig-cap"><b>Figure {num} · {html.escape(fig_title)}.</b> {caption_html}</div>
</div>"""


def step_key(phase: dict) -> str:
    return phase.get("mold") or phase.get("branch") or ""


def lane_str(lane: list[dict]) -> str:
    arrow = ' <tspan font-family="IBM Plex Sans" font-weight="400">→</tspan> '
    return arrow.join(html.escape(" ".join(SHORT_LABELS[step_key(p)])) for p in lane)


def build_route_svg(route: dict) -> str:
    spine = route["spine"]
    rr = route["run"]
    assert len(spine) == 11, f"expected 11 spine phases, got {len(spine)}"
    gates = {
        rr["loop_phase"]: ("gxwf draft-validate", "Fig. 1, 2"),
        rr["validate_phase"]: ("gxwf validate", "Fig. 3"),
        rr["test_phase"]: ("planemo test", "Fig. 4"),
    }

    paper_txt = lane_str(route["lanes"]["paper"])
    nf_txt = lane_str(route["lanes"]["nextflow"])

    parts = [
        '<svg viewBox="0 0 2960 660" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Foundry 11-phase route diagram">',
        "<style>",
        '  .rt-disp { font-family: "Atkinson Hyperlegible Next", sans-serif; font-weight: 800; fill: #2c3143; }',
        '  .rt-sans { font-family: "Atkinson Hyperlegible Next", "IBM Plex Sans", sans-serif; font-weight: 600; fill: #18243a; }',
        '  .rt-muted { font-family: "Atkinson Hyperlegible Next", sans-serif; font-weight: 400; fill: #4f5b70; }',
        '  .rt-mono { font-family: "Atkinson Hyperlegible Mono", monospace; font-weight: 700; fill: #18243a; }',
        '  .rt-hand { font-family: "Kalam", sans-serif; font-weight: 700; fill: #0b7a75; }',
        "</style>",
        "<defs>",
        '  <marker id="arrNavy" viewBox="0 0 12 10" refX="9" refY="5" markerWidth="11" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto">',
        '    <path d="M0,0 L12,5 L0,10 Z" fill="#2c3143"/>',
        "  </marker>",
        '  <marker id="arrTeal" viewBox="0 0 12 10" refX="9" refY="5" markerWidth="12" markerHeight="10" markerUnits="userSpaceOnUse" orient="auto">',
        '    <path d="M0,0 L12,5 L0,10 Z" fill="#0b7a75"/>',
        "  </marker>",
        "</defs>",
        # Planning lanes: PAPER and NEXTFLOW
        '<rect x="12" y="38" width="585" height="142" rx="14" fill="#e0f2f0" stroke="#0b7a75" stroke-width="3.5"/>',
        '<text x="38" y="92" class="rt-disp" font-size="38" letter-spacing="0.03em">PAPER</text>',
        f'<text x="38" y="144" class="rt-sans" font-size="26">{paper_txt}</text>',
        '<rect x="12" y="212" width="585" height="142" rx="14" fill="#e0f2f0" stroke="#0b7a75" stroke-width="3.5"/>',
        '<text x="38" y="266" class="rt-disp" font-size="38" letter-spacing="0.03em">NEXTFLOW</text>',
        f'<text x="38" y="318" class="rt-sans" font-size="26">{nf_txt}</text>',
        # Curved arrows into WORKFLOW BRIEF
        '<path d="M 597 109 Q 652 109 695 162" fill="none" stroke="#2c3143" stroke-width="5" stroke-linecap="round" marker-end="url(#arrNavy)"/>',
        '<path d="M 597 283 Q 652 283 695 230" fill="none" stroke="#2c3143" stroke-width="5" stroke-linecap="round" marker-end="url(#arrNavy)"/>',
        # WORKFLOW BRIEF box
        '<rect x="706" y="88" width="420" height="216" rx="16" fill="#ffd700" stroke="#d97706" stroke-width="3.5"/>',
        '<text x="734" y="145" class="rt-disp" font-size="36">WORKFLOW</text>',
        '<text x="734" y="185" class="rt-disp" font-size="36">BRIEF</text>',
        '<text x="734" y="232" class="rt-sans" font-size="24">a person reviews it</text>',
        '<text x="734" y="264" class="rt-sans" font-size="24">before any build</text>',
        # Row A spine line (from brief to loop station)
        '<line x1="1126" y1="196" x2="2315" y2="196" stroke="#2c3143" stroke-width="5"/>',
    ]

    # Stations 1..4 on Row A
    row_a_y = 196
    xs_a = [1255, 1545, 1835, 2125]
    for idx, x in enumerate(xs_a):
        n = idx + 1
        lines = SHORT_LABELS[step_key(spine[idx])]
        parts.append(f'<circle cx="{x}" cy="{row_a_y}" r="38" fill="#ffffff" stroke="#0b7a75" stroke-width="4.5"/>')
        parts.append(f'<text x="{x}" y="{row_a_y + 11}" class="rt-disp" font-size="31" fill="#0b7a75" text-anchor="middle">{n}</text>')
        for li, ln in enumerate(lines):
            parts.append(
                f'<text x="{x}" y="{row_a_y + 72 + li * 30}" class="rt-sans" font-size="26" text-anchor="middle">{html.escape(ln)}</text>'
            )

    # Loop station 5 (x=2315..2925, y=74..318)
    parts.extend(
        [
            '<ellipse cx="2620" cy="196" rx="332" ry="154" transform="rotate(-4.5 2620 196)" fill="none" stroke="#ea580c" stroke-width="3.5" stroke-dasharray="12 7"/>',
            '<rect x="2315" y="76" width="610" height="240" rx="22" fill="#ffffff" stroke="#2c3143" stroke-width="4.5"/>',
            # Repeat arc over loop box
            '<path d="M 2810 70 Q 2620 12 2435 70" fill="none" stroke="#0b7a75" stroke-width="5.5" stroke-linecap="round" marker-end="url(#arrTeal)"/>',
            '<text x="2620" y="34" class="rt-hand" font-size="33" text-anchor="middle">repeat</text>',
            # Inside loop box
            '<circle cx="2368" cy="128" r="29" fill="#2c3143" stroke="#ffd700" stroke-width="5"/>',
            f'<text x="2368" y="138" class="rt-disp" font-size="26" fill="#ffffff" text-anchor="middle">{rr["loop_phase"]}</text>',
            '<text x="2412" y="139" class="rt-disp" font-size="33" fill="#0b7a75">draft loop</text>',
            '<text x="2348" y="184" class="rt-muted" font-size="25">one step per pass until</text>',
            '<text x="2348" y="216" class="rt-muted" font-size="25">no step is a draft</text>',
            '<rect x="2344" y="242" width="356" height="44" rx="7" fill="#fff38a"/>',
            '<text x="2356" y="273" class="rt-mono" font-size="25">gxwf draft-validate</text>',
            '<text x="2815" y="276" class="rt-hand" font-size="31" text-anchor="middle">Figs. 1, 2</text>',
        ]
    )

    # Return elbow from loop foot (x=2560, y=316) down to y=378, left to x=135, down to station 6 (y=502)
    row_b_y = 548
    parts.extend(
        [
            '<path d="M 2560 316 L 2560 356 Q 2560 380 2536 380 L 159 380 Q 135 380 135 404 L 135 496" '
            'fill="none" stroke="#2c3143" stroke-width="4.5" stroke-linecap="round" marker-end="url(#arrNavy)"/>',
            f'<line x1="135" y1="{row_b_y}" x2="2536" y2="{row_b_y}" stroke="#2c3143" stroke-width="5" marker-end="url(#arrNavy)"/>',
        ]
    )

    # Stations 6..11 on Row B
    xs_b = [135, 575, 1015, 1455, 1895, 2335]
    for j, x in enumerate(xs_b):
        idx = 5 + j
        n = idx + 1
        lines = SHORT_LABELS[step_key(spine[idx])]
        gate = gates.get(n)
        if gate:
            prog, fig = gate
            parts.append(f'<circle cx="{x}" cy="{row_b_y}" r="39" fill="#2c3143" stroke="#ffd700" stroke-width="6"/>')
            parts.append(f'<text x="{x}" y="{row_b_y + 11}" class="rt-disp" font-size="30" fill="#ffffff" text-anchor="middle">{n}</text>')
            # Callout above gate
            prog_w = max(220, len(prog) * 16 + 28)
            parts.append(f'<text x="{x}" y="{row_b_y - 98}" class="rt-hand" font-size="31" text-anchor="middle">{html.escape(fig)}</text>')
            parts.append(f'<rect x="{x - prog_w / 2:.0f}" y="{row_b_y - 84}" width="{prog_w}" height="38" rx="7" fill="#fff38a"/>')
            parts.append(f'<text x="{x}" y="{row_b_y - 57}" class="rt-mono" font-size="24" text-anchor="middle">{html.escape(prog)}</text>')
        else:
            parts.append(f'<circle cx="{x}" cy="{row_b_y}" r="38" fill="#ffffff" stroke="#0b7a75" stroke-width="4.5"/>')
            parts.append(f'<text x="{x}" y="{row_b_y + 11}" class="rt-disp" font-size="30" fill="#0b7a75" text-anchor="middle">{n}</text>')
        for li, ln in enumerate(lines):
            parts.append(
                f'<text x="{x}" y="{row_b_y + 72 + li * 29}" class="rt-sans" font-size="26" text-anchor="middle">{html.escape(ln)}</text>'
            )

    # Final output box: GALAXY WORKFLOW with its tests
    parts.extend(
        [
            f'<rect x="2552" y="{row_b_y - 84}" width="390" height="168" rx="16" fill="#e0f2f0" stroke="#0b7a75" stroke-width="3.5"/>',
            f'<text x="2582" y="{row_b_y - 26}" class="rt-disp" font-size="34">GALAXY</text>',
            f'<text x="2582" y="{row_b_y + 14}" class="rt-disp" font-size="34">WORKFLOW</text>',
            f'<text x="2582" y="{row_b_y + 56}" class="rt-sans" font-size="25" fill="#0b7a75">with its tests</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts)


def main() -> None:
    d = json.loads((HERE / "receipts.json").read_text())
    route = json.loads((HERE / "route.json").read_text())
    rr = route["run"]

    # 1. CAST receipt
    c = d["cast"]
    cast_body = "\n".join(
        [
            r_row("SKILL.md", html.escape(c["skill"]), bold_left=True),
            r_row(f"MOLD rev {c['revision']}", html.escape(c["hash"])),
            r_row(f"{c['refs']} refs", f"{c['upfront']} upfront · {c['refs'] - c['upfront']} on demand"),
        ]
    )
    rec_cast = render_receipt(
        1,
        "CAST",
        c["cast_at"][5:],
        f"skill build · foundry @ {c['foundry']}",
        cast_body,
        c["signed"],
        "CAST",
        f"The Tool Shed search skill the DengueSeq run used in its draft loop: Mold revision {c['revision']}, {c['refs']} references, <mark>no model in the build</mark>.",
    )

    # 2. PINNED receipt
    pn = d["pinned"]
    pin_rows = []
    for p in pn["pins"]:
        pin_rows.append(
            f'<div class="pin-item">'
            f'<div class="pin-top"><span class="own">{html.escape(p["owner"])}/</span><b>{html.escape(p["tool"])}</b></div>'
            f'<div class="pin-bot">{html.escape(p["version"])} <span class="at">@</span>{html.escape(p["changeset"])}</div>'
            f"</div>"
        )
    rec_pinned = render_receipt(
        2,
        "PINNED",
        f"10-20 {pn['from']}–{pn['to']}",
        f"Tool Shed changesets · phase {rr['loop_phase']}",
        "\n".join(pin_rows),
        pn["signed"],
        "PINNED",
        "The seven tools the run pinned, as <code>gxwf tool-revisions</code> reported them. Planemo later installed exactly these.",
    )

    # 3. VALIDATED receipt
    vd = d["validated"]
    val_body = "\n".join(
        [
            '<div class="r-cmd"><div>$ gxwf validate</div><div class="ind">galaxy-workflow.gxwf.yml</div><div class="ind">--connections --strict --json</div></div>',
            r_row("Tool state", f"{vd['tool_state']['ok']} ok · {vd['tool_state']['fail']} fail · {vd['tool_state']['skip']} skip"),
            r_row("Connections", f"{vd['connections']['ok']} ok · {vd['connections']['invalid']} invalid"),
            r_row("map-over", f"all {vd['map_over_list']} steps over list"),
            r_row("wall time", "&lt; 1 s"),
        ]
    )
    rec_validated = render_receipt(
        3,
        "VALIDATED",
        f"10-21 {vd['at']}",
        f"replayed · gxwf {vd['cli']} · {vd['replayed']}",
        val_body,
        vd["signed"],
        "VALIDATED",
        f"Phase {rr['validate_phase']}’s check, replayed.",
    )

    # 4. TESTED receipt
    ts = d["tested"]
    test_body = "\n".join(
        [
            r_row("planemo test", html.escape(ts["status"])),
            r_row(
                "tests",
                f"{ts['summary']['num_tests']} · failures {ts['summary']['num_failures']} · errors {ts['summary']['num_errors']}",
            ),
            r_row("Tool Shed repos, at the pins", str(ts["installed"])),
            r_row("containers", str(ts["containers"])),
            r_row("wall time", f"{ts['minutes']} min"),
            '<hr class="r-rule">',
            f'<div class="r-jobs"><span>JOBS RUN</span><span class="dots"></span><span>{ts["jobs"]} <small>ok · {ts["jobs"] - ts["jobs_ok"]} failed</small></span></div>',
        ]
    )
    rec_tested = render_receipt(
        4,
        "TESTED",
        f"10-21 {ts['at']}",
        f"planemo {ts['planemo']} · its JSON report",
        test_body,
        ts["signed"],
        "TESTED",
        "Planemo’s report of that run. One larger test case (about 178 MB of reads) was not run.",
        stamp_text="PASS",
    )

    tpl = (HERE / "template.html").read_text()
    replacements = {
        "{{RECEIPT_CAST}}": rec_cast,
        "{{RECEIPT_PINNED}}": rec_pinned,
        "{{RECEIPT_VALIDATED}}": rec_validated,
        "{{RECEIPT_TESTED}}": rec_tested,
        "{{ROUTE_DIAGRAM}}": build_route_svg(route),
        "{{RUN_ID}}": html.escape(d["run"]),
        "{{SPINE_LEN}}": str(len(route["spine"])),
        "{{LOOP_PHASE}}": str(rr["loop_phase"]),
        "{{LOOP_ITERATIONS}}": str(rr["loop_iterations"]),
        "{{VALIDATE_PHASE}}": str(rr["validate_phase"]),
        "{{LEDGER_ENTRIES}}": str(route["ledger"]["entries"]),
        "{{LEDGER_RESOLVED}}": str(route["ledger"]["resolved"]),
        "{{LEDGER_OPEN}}": str(route["ledger"]["open"]),
    }
    for k, v in replacements.items():
        tpl = tpl.replace(k, v)

    out_html = HERE / "poster.html"
    out_html.write_text(tpl)

    pdf_path = HERE / "poster.pdf"
    png_path = HERE / "poster-preview.png"

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": PAGE_PX, "height": PAGE_PX}, device_scale_factor=0.5)
        page.goto(out_html.as_uri(), wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        overflow = page.evaluate(
            """() => {
              const out = [];
              for (const el of document.querySelectorAll('body, main, header, footer, section, .slip')) {
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
