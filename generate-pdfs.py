"""
Generate portfolio PDFs using a two-pass approach:

  Pass 1 — zero margins, no header, full CSS
           -> clean full-bleed cover page (page 1 of merged PDF)

  Pass 2 — standard margins, running header, cover div HIDDEN via injected CSS
           -> content-only pages starting at page 1 (become pages 2+ in merged PDF)

Run with: python generate-pdfs.py
Requires Jekyll running at localhost:4000
"""

import asyncio
import io
import os
from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter

BASE_URL = "http://localhost:4000/stevekelly-portfolio/samples"
OUT_DIR  = os.path.join(os.path.dirname(__file__), "assets", "pdf")

SLUGS = [
    "vpn-migration",
    "wan-failover-postmortem",
    "wan-failover-technical",
    "wan-failover-architecture",
    "aws-directconnect-migration",
    "isp-cdn-localization",
]

# Page margins for content pages
MARGIN_TOP    = "2.0cm"   # must exceed header height (~1.3cm) with breathing room
MARGIN_BOTTOM = "1.0cm"
MARGIN_LEFT   = "1.8cm"
MARGIN_RIGHT  = "1.8cm"


def header_template(title: str) -> str:
    """Running header: document title left, bold page number right, rule below."""
    safe = (title
            .replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))
    return f"""
    <div style="
        width: 100%;
        padding: 0.35cm {MARGIN_LEFT} 0.2cm;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        box-sizing: border-box;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
        border-bottom: 0.6pt solid #c8d4e0;
    ">
        <span style="
            font-size: 7.5pt;
            font-weight: 500;
            color: #667;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 78%;
        ">{safe}</span>
        <span style="
            font-size: 16pt;
            font-weight: 700;
            color: #1a2a3a;
            line-height: 1;
        "><span class="pageNumber"></span></span>
    </div>
    """


async def generate():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page    = await browser.new_page()

        for slug in SLUGS:
            url = f"{BASE_URL}/{slug}"
            out = os.path.join(OUT_DIR, f"{slug}.pdf")
            print(f"  {slug}...", end="", flush=True)

            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(2000)   # let Mermaid render

            # Grab document title from the page h1
            try:
                doc_title = await page.inner_text("h1.post-title")
                doc_title = doc_title.strip()
            except Exception:
                doc_title = slug.replace("-", " ").title()

            # ── Pass 1: full-bleed cover ───────────────────────────────
            # Inject @page margin:0 so it overrides the CSS @page rules,
            # giving edge-to-edge gradient with no white border.
            await page.add_style_tag(content="@page { margin: 0 !important; }")
            pass1_bytes = await page.pdf(
                format="Letter",
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                display_header_footer=False,
                print_background=True,
            )

            # Reload so the injected @page override is gone before pass 2
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(1500)

            # ── Pass 2: content only, CSS @page margins control layout ─
            # Hide the cover so pass 2 is content pages only.
            # margin: 0 here defers entirely to the CSS @page rules.
            await page.add_style_tag(content="""
                @media print { .print-cover { display: none !important; } }
            """)
            pass2_bytes = await page.pdf(
                format="Letter",
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                display_header_footer=True,
                header_template=header_template(doc_title),
                footer_template="<span></span>",
                print_background=True,
            )

            # Reload for next slug
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(1000)

            # ── Merge: cover (pass 1 page 1) + content (all of pass 2) ─
            r1 = PdfReader(io.BytesIO(pass1_bytes))
            r2 = PdfReader(io.BytesIO(pass2_bytes))

            writer = PdfWriter()
            writer.add_page(r1.pages[0])          # full-bleed cover
            for p2_page in r2.pages:              # all content pages
                writer.add_page(p2_page)

            with open(out, "wb") as f:
                writer.write(f)

            total = 1 + len(r2.pages)
            size  = os.path.getsize(out)
            print(f" {total}pp {size // 1024}KB -> {out}")

        await browser.close()


print("Generating PDFs...")
asyncio.run(generate())
print("Done.")
