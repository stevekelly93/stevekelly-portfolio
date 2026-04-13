# Portfolio Quickstart

How to set up the environment, create a new document using the MCP server, and generate a PDF.

---

## Prerequisites

### Ruby + Jekyll

Jekyll is the static site generator. Install Ruby first, then Jekyll.

**Windows:** Download the Ruby+Devkit installer from [rubyinstaller.org](https://rubyinstaller.org/downloads/) — use the `WITH DEVKIT` version. Accept defaults and run `ridk install` at the end.

```bash
gem install bundler
cd stevekelly-portfolio
bundle install
```

This installs Jekyll 4.3, jekyll-feed, webrick, and other gems from `Gemfile`.

### Python

Python 3.11 or later required.

```bash
pip install playwright pypdf mcp
python -m playwright install chromium
```

| Package | Purpose |
|---------|---------|
| `playwright` | Headless Chromium — renders the Jekyll pages and captures PDFs |
| `pypdf` | Merges the two-pass PDFs (cover + content) |
| `mcp` | Runs the MCP server that scaffolds new documents |

---

## Project Structure

```
stevekelly-portfolio/
├── samples/              # Markdown source for each document
├── assets/
│   ├── css/style.css     # All styles (screen + print)
│   └── pdf/              # Generated PDFs (committed to repo, served as downloads)
├── _layouts/page.html    # Page layout with PDF download button
├── generate-pdfs.py      # PDF generation script (Playwright two-pass + pypdf merge)
├── mcp_server.py         # MCP server — document scaffolding tools
├── Gemfile               # Ruby gem dependencies
└── _config.yml           # Jekyll site config
```

---

## Creating a New Document with the MCP Server

The MCP server (`mcp_server.py`) is registered in Claude Code as `portfolio-docs`. It provides three tools:

### `list_doc_types`

Returns the available document templates and their section keys.

**Templates:**

| Key | Type |
|-----|------|
| `migration-overview` | Migration Overview & Application Owner Communication |
| `post-mortem` | Post-Incident Review |
| `technical-resolution` | Technical Resolution Summary |
| `architecture-design` | Architecture Design & Evolution |
| `project-overview` | Project Overview |

### `create_document`

Scaffolds a new `.md` file in `samples/` with correct frontmatter, table of contents, section bodies, and a confidentiality footer.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `doc_type` | Yes | Template key from `list_doc_types` |
| `title` | Yes | Full document title |
| `description` | Yes | One-sentence description for metadata |
| `quarter` | Yes | Publication quarter, e.g. `Q2 2025` |
| `section_content` | Yes | Dict of section key → Markdown content string |
| `filename` | No | Output filename without `.md` (defaults to slug of title) |
| `status` | No | Optional `doc_status` value, e.g. `Draft` |
| `overwrite` | No | Set `true` to replace an existing file (default: `false`) |

**Example — creating a post-mortem:**

Ask Claude Code (with the `portfolio-docs` MCP active):

> Use `create_document` with doc_type `post-mortem`, title "BGP Route Leak — Transit Provider Outage", quarter Q3 2025, and the following section content: [your content]

The tool writes `samples/<slug>.md` and adds the slug to `generate-pdfs.py` automatically.

### `regenerate_pdfs`

Runs `generate-pdfs.py` against a running Jekyll instance.

```
regenerate_pdfs(slugs=["my-new-doc"])   # regenerate one doc
regenerate_pdfs()                        # regenerate all docs
```

Requires Jekyll running at `localhost:4000` before calling this (see below).

---

## Generating PDFs Manually

### 1. Start Jekyll

```bash
bundle exec jekyll serve
```

Jekyll serves the site at `http://localhost:4000/stevekelly-portfolio/`. Leave this running.

### 2. Run the PDF script

In a second terminal:

```bash
python generate-pdfs.py
```

This loops through every slug in `SLUGS`, renders each page twice with Playwright, and merges the results:

- **Pass 1** — full-bleed cover page (no margins, no header, gradient background edge-to-edge)
- **Pass 2** — content pages with running header (document title + page number) and standard margins

Output PDFs are written to `assets/pdf/<slug>.pdf`.

### 3. Commit the PDFs

The PDFs are committed to the repository and served as static file downloads. After generating:

```bash
git add assets/pdf/
git commit -m "Regenerate PDFs"
git push
```

---

## MCP Server Registration

The server is registered for Claude Code in `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "portfolio-docs": {
      "type": "stdio",
      "command": "C:\\Users\\Steven\\python.exe",
      "args": ["C:\\Users\\Steven\\Documents\\stevekelly-portfolio\\mcp_server.py"]
    }
  }
}
```

To use the tools from a different machine, update `command` to the local Python path (`where python` on Windows, `which python3` on Mac/Linux) and update `args` to the full path of `mcp_server.py`.

---

## Troubleshooting

**Jekyll `bundle install` fails on Windows**
Make sure the Ruby+Devkit installer was used (not the slim version) and `ridk install` completed successfully.

**`playwright install chromium` is slow**
This downloads ~150MB of Chromium. Run it once and it caches locally.

**PDFs have no cover page / blank first page**
Jekyll must be fully started before running `generate-pdfs.py`. Wait for the `Server running` message in the Jekyll terminal, then run the script.

**MCP tools not available in Claude Code**
Restart Claude Code after editing `~/.claude/mcp.json`. Tools appear under the `portfolio-docs` namespace.
