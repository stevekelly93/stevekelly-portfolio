"""
Portfolio Document MCP Server

Tools:
  list_doc_types      — list available document type templates
  create_document     — scaffold a new portfolio sample document
  regenerate_pdfs     — run generate-pdfs.py (requires Jekyll running)
"""

import os
import re
import subprocess
import textwrap
from typing import Optional

from mcp.server.fastmcp import FastMCP

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

# ---------------------------------------------------------------------------
# Document type templates
# ---------------------------------------------------------------------------

DOC_TYPES = {
    "migration-overview": {
        "label": "Migration Overview & Application Owner Communication",
        "audience": "Application Owners & Cross-functional Stakeholders",
        "description": "Communicates a planned migration to non-technical stakeholders. Explains why, what changes, what stays the same, and how rollout is phased.",
        "sections": [
            ("Why We're Making This Change", "why"),
            ("What This Means for Application Owners", "impact"),
            ("How the Migration Works", "how"),
            ("Migration Schedule and Coordination", "schedule"),
            ("Questions", "questions"),
        ],
    },
    "post-mortem": {
        "label": "Post-Incident Review",
        "audience": "Customer IT Leadership & Business Stakeholders",
        "description": "Documents a production incident: impact, timeline, root cause, resolution, and prevention actions.",
        "sections": [
            ("Summary", "summary"),
            ("Impact", "impact"),
            ("Timeline", "timeline"),
            ("Root Cause", "root-cause"),
            ("Resolution", "resolution"),
            ("What We Are Doing to Prevent Recurrence", "prevention"),
            ("Lessons Learned", "lessons"),
        ],
    },
    "technical-resolution": {
        "label": "Technical Resolution Summary",
        "audience": "Network Engineering & IT Operations",
        "description": "Documents an implemented technical fix: the problem, the solution, how it behaves, validation steps, and known limitations.",
        "sections": [
            ("Background", "background"),
            ("The Problem", "problem"),
            ("The Solution", "solution"),
            ("How It Now Behaves", "behavior"),
            ("Validation", "validation"),
            ("Known Limitations", "limitations"),
            ("Key Takeaway", "takeaway"),
        ],
    },
    "architecture-design": {
        "label": "Architecture Design & Evolution",
        "audience": "Network Engineering & IT Operations",
        "description": "Describes a target-state architecture, the rationale for the design evolution, configuration intent, and implementation sequence.",
        "sections": [
            ("Purpose", "purpose"),
            ("Problem Statement", "problem"),
            ("Evolution of the Design", "evolution"),
            ("Configuration Intent", "config"),
            ("Risks and Considerations", "risks"),
            ("Implementation Sequence", "sequence"),
            ("Summary", "summary"),
        ],
    },
    "project-overview": {
        "label": "Project Overview",
        "audience": "IT Leadership & Cross-functional Stakeholders",
        "description": "Communicates a technology project to leadership and cross-functional partners: rationale, what changes, timeline, risks, and stakeholder responsibilities.",
        "sections": [
            ("Why We're Making This Change", "why"),
            ("What Changes — and What Stays the Same", "changes"),
            ("Timeline and Phases", "timeline"),
            ("Risks and How We're Addressing Them", "risks"),
            ("What We Need From Stakeholders", "stakeholders"),
            ("Questions and Resources", "questions"),
        ],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_emdash(text: str) -> str:
    """Replace em dashes with a plain hyphen. Portfolio content must not contain em dashes."""
    return text.replace("\u2014", "-")


def _slugify(title: str) -> str:
    """Produce a filesystem-safe slug from a title."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:60]


def _anchor(heading: str) -> str:
    """Produce a Kramdown/Jekyll anchor ID from a heading string.

    Rules that match Jekyll/Kramdown behaviour:
      1. Lowercase everything
      2. Remove characters that are not alphanumeric, space, or hyphen
      3. Replace spaces (and any resulting consecutive hyphens) with single hyphens
    """
    anchor = heading.lower()
    anchor = re.sub(r"[^a-z0-9\s-]", "", anchor)
    anchor = re.sub(r"[\s-]+", "-", anchor.strip())
    return anchor


def _toc_block(sections: list[tuple[str, str]]) -> str:
    """Build a TOC div from a list of (heading, _unused_key) pairs."""
    items = "\n".join(
        f"- [{heading}](#{_anchor(heading)})" for heading, _ in sections
    )
    return f"""<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

{items}

</div>"""


def _section_block(heading: str, content: str) -> str:
    body = textwrap.dedent(content).strip() if content.strip() else "_Content to be added._"
    return f"## {heading}\n\n{body}"


def _frontmatter(
    title: str,
    description: str,
    doc_type_key: str,
    quarter: str,
    status: Optional[str],
) -> str:
    tmpl = DOC_TYPES[doc_type_key]
    doc_type_label = tmpl["label"]
    audience = tmpl["audience"]

    lines = [
        "---",
        "layout: page",
        f'title: "{title}"',
        f"description: {description}",
        f"doc_type: {doc_type_label}",
        f"audience: {audience}",
        f"doc_date: {quarter}",
    ]
    if status:
        lines.append(f"doc_status: {status}")
    lines += ["show_pdf: true", "---"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

mcp = FastMCP("portfolio-docs")


@mcp.tool()
def list_doc_types() -> str:
    """List the available document type templates and their sections."""
    lines = ["Available document types:\n"]
    for key, tmpl in DOC_TYPES.items():
        section_names = ", ".join(h for h, _ in tmpl["sections"])
        lines.append(f"**{key}**")
        lines.append(f"  Label    : {tmpl['label']}")
        lines.append(f"  Audience : {tmpl['audience']}")
        lines.append(f"  Sections : {section_names}")
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def create_document(
    doc_type: str,
    title: str,
    description: str,
    quarter: str,
    section_content: dict,
    filename: Optional[str] = None,
    status: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    """Scaffold a new portfolio sample document.

    Args:
        doc_type: One of the keys returned by list_doc_types
                  (e.g. "migration-overview", "post-mortem").
        title: Full document title (used in frontmatter and cover page).
        description: One-sentence description for the frontmatter.
        quarter: Publication quarter, e.g. "Q2 2025".
        section_content: Dict mapping section keys to markdown content strings.
                         Keys are the short identifiers shown in list_doc_types
                         (e.g. {"why": "...", "impact": "...", "how": "..."}).
                         Omitted sections get a placeholder.
        filename: Optional output filename (without .md). Defaults to a slug
                  derived from the title.
        status: Optional doc_status frontmatter value (e.g. "Draft").
        overwrite: If False (default), refuse to overwrite an existing file.

    Returns:
        Path to the created file, or an error message.
    """
    if doc_type not in DOC_TYPES:
        available = ", ".join(DOC_TYPES.keys())
        return f"Unknown doc_type '{doc_type}'. Available: {available}"

    slug = filename if filename else _slugify(title)
    if not slug:
        return "Could not derive a filename from the title. Pass an explicit filename."

    out_path = os.path.join(SAMPLES_DIR, f"{slug}.md")
    if os.path.exists(out_path) and not overwrite:
        return (
            f"File already exists: {out_path}\n"
            "Pass overwrite=True to replace it."
        )

    tmpl = DOC_TYPES[doc_type]
    sections = tmpl["sections"]

    # Build section blocks
    section_blocks = []
    for heading, key in sections:
        content = section_content.get(key, "")
        section_blocks.append(_section_block(heading, content))

    fm = _frontmatter(title, description, doc_type, quarter, status)
    toc = _toc_block(sections)
    body = "\n\n---\n\n".join(section_blocks)

    doc = _strip_emdash(
        fm
        + "\n\n"
        + toc
        + "\n\n"
        + body
        + "\n\n---\n\n"
        + "*Organization and infrastructure details have been generalized to protect confidentiality.*\n"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)

    # Also append slug to generate-pdfs.py SLUGS list if not already present
    genpdf_path = os.path.join(os.path.dirname(__file__), "generate-pdfs.py")
    if os.path.exists(genpdf_path):
        with open(genpdf_path, "r", encoding="utf-8") as f:
            genpdf = f.read()
        if f'"{slug}"' not in genpdf:
            updated = genpdf.replace(
                "]",
                f'    "{slug}",\n]',
                1,  # only first ] that closes the SLUGS list
            )
            # Be more precise: replace inside the SLUGS list
            updated = re.sub(
                r'(SLUGS\s*=\s*\[.*?)(^\])',
                lambda m: m.group(0).rstrip("]") + f'    "{slug}",\n]',
                genpdf,
                flags=re.DOTALL | re.MULTILINE,
            )
            if updated != genpdf:
                with open(genpdf_path, "w", encoding="utf-8") as f:
                    f.write(updated)

    return f"Created: {out_path}"


@mcp.tool()
def regenerate_pdfs(slugs: Optional[list[str]] = None) -> str:
    """Run the PDF generation script (requires Jekyll at localhost:4000).

    Args:
        slugs: Optional list of document slugs to regenerate. If omitted,
               all documents in generate-pdfs.py are regenerated.

    Returns:
        stdout/stderr from the script, or an error message.
    """
    script = os.path.join(os.path.dirname(__file__), "generate-pdfs.py")
    if not os.path.exists(script):
        return f"generate-pdfs.py not found at {script}"

    env = os.environ.copy()

    if slugs:
        # Pass slug list via environment variable; script checks for it
        env["PDF_SLUGS"] = ",".join(slugs)

    try:
        result = subprocess.run(
            ["python", script],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
            cwd=os.path.dirname(__file__),
        )
        output = result.stdout + result.stderr
        if result.returncode != 0:
            return f"Script exited with code {result.returncode}:\n{output}"
        return output or "PDF generation complete."
    except subprocess.TimeoutExpired:
        return "Timed out after 120 seconds. Is Jekyll running at localhost:4000?"
    except Exception as exc:
        return f"Error running script: {exc}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
