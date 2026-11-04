# PdfPecker Skills

Agent Skills that let AI agents make and check PDFs with [PdfPecker](https://pdfpecker.net/): HTML or Markdown to PDF
in about a millisecond a page, page previews the agent can look at, text extraction and merging. There is no browser
to install and no JavaScript: one `pip install pdfpecker`, about 9 MB.

| Skill | What it does |
|---|---|
| [`pdfpecker`](plugins/pdfpecker/skills/pdfpecker/SKILL.md) | Writes HTML with print CSS (or Markdown), converts it, renders the pages to PNG to check them, and reads, counts and merges PDFs. Comes with an invoice and a multi-page report template. |

## Install

**Claude Code**: add the marketplace and install the plugin:

```
/plugin marketplace add Moonwalker1307/PdfPecker.Skills
/plugin install pdfpecker@pdfpecker-skills
```

**Claude.ai and the Claude apps**: download `pdfpecker.zip` from the
[latest release](https://github.com/Moonwalker1307/PdfPecker.Skills/releases/latest) and upload it in the Skills section
of Settings. Code execution must be on, with network access to PyPI so the skill can install the package.

**Claude API**: upload the same zip with the Skills API (`POST /v1/skills`) and pass its id in the request's
`container.skills`, with the code execution tool.

**Other agents** that read `SKILL.md` folders: copy `plugins/pdfpecker/skills/pdfpecker` into the agent's skills
folder.

Every route needs Python 3.9 or later; the skill installs `pdfpecker` from PyPI the first time it runs.

## What the agent gets

```bash
python3 scripts/pdf.py html invoice.html invoice.pdf          # or: md notes.md notes.pdf
python3 scripts/pdf.py preview invoice.pdf --dpi 80           # invoice-page-1.png, ... to look at
python3 scripts/pdf.py text report.pdf --pages 1-2
python3 scripts/pdf.py merge all.pdf cover.pdf report.pdf
```

The skill teaches the loop that gives good PDFs: write HTML with `@page` rules for size, margins and page numbers,
convert, look at the pages, fix, convert again. Its reference lists the CSS that works, what doesn't (scripts,
network resources, fonts for non-Latin scripts) and a checklist before handing a PDF over.

## Development

```
python -m pip install pdfpecker pytest
python -m pytest -q tests        # frontmatter and manifest checks, and the script run on the templates
python tools/package.py          # dist/pdfpecker.zip for Claude.ai and the API
```

See `AGENTS.md` for the rules. The pdfpecker package itself is built in
[PdfPecker.Python](https://github.com/Moonwalker1307/PdfPecker.Python), and the library in
[PdfPecker](https://github.com/Moonwalker1307/PdfPecker).

## License

MIT.
