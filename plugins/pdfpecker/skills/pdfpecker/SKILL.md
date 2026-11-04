---
name: pdfpecker
description: Make PDF documents from HTML or Markdown and check how they look, read existing PDFs as text or page images, and merge PDFs, with the pdfpecker Python package (no browser, about a millisecond per page). Use when the user wants a PDF, such as an invoice, report, letter, certificate, ticket, label, CV or a Markdown document as PDF, or wants to preview, read, count pages of or merge PDFs.
license: MIT
compatibility: Python 3.9 or later on Linux, macOS or Windows, and pip install pdfpecker (one ~9 MB wheel, no other dependencies).
metadata:
  homepage: https://pdfpecker.net/
  source: https://github.com/Moonwalker1307/PdfPecker.Skills
---

# Making and reading PDFs with pdfpecker

pdfpecker turns HTML and CSS (or Markdown) into a PDF without a browser, and renders PDF pages back to images so you
can look at what you made. Work in this order: **write HTML, convert, look at the pages, fix, convert again.**

## Setup

```bash
python3 -c "import pdfpecker" 2>/dev/null || python3 -m pip install --quiet pdfpecker
```

The helper script is `scripts/pdf.py` in this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}/scripts/pdf.py`).
It wraps the package so you need no Python of your own for the usual jobs:

```bash
python3 scripts/pdf.py html invoice.html invoice.pdf          # images and CSS resolve next to the HTML file
python3 scripts/pdf.py md notes.md notes.pdf --page-size Letter
python3 scripts/pdf.py preview invoice.pdf --dpi 80           # writes invoice-page-1.png, ... and prints the paths
python3 scripts/pdf.py text report.pdf --pages 1-2
python3 scripts/pdf.py markdown report.pdf report.md          # any PDF as Markdown, tables and lists kept
python3 scripts/pdf.py info report.pdf                        # page count
python3 scripts/pdf.py merge all.pdf cover.pdf report.pdf
```

Run `python3 scripts/pdf.py <command> --help` for every option. From Python, the same calls are
`pdfpecker.html_to_pdf(html, base_dir=...)`, `html_file_to_pdf(path, out)`, `markdown_to_pdf(text)`,
`pdf_to_images(pdf, dpi=80)`, `pdf_to_text(pdf)`, `pdf_to_markdown(pdf)`, `pdf_page_count(pdf)`, `merge_pdfs([...])`
and `pdf_to_pdfa(pdf, "out.pdf")` (an existing PDF to PDF/A for archiving).

## Writing the HTML

Start from a template when one fits: `templates/invoice.html` (one-page invoice with a line-item table) and
`templates/report.html` (multi-page report with a cover, page numbers, a table that repeats its header, and a
chart in SVG). Copy it next to your output and edit it.

Put page layout in CSS, not in options:

```css
@page {
  size: A4;                      /* or Letter, A5, "A4 landscape", 210mm 99mm */
  margin: 18mm 16mm 20mm;
  @bottom-center { content: "Page " counter(page) " of " counter(pages); font: 9pt sans-serif; color: #666; }
}
@page :first { @bottom-center { content: none; } }
h2 { break-after: avoid; }        /* keep a heading with what follows */
tr, figure, .card { break-inside: avoid; }
.new-page { break-before: page; }
thead { display: table-header-group; }   /* repeated on every page (the default for <thead>) */
```

What to know (details in [reference.md](reference.md)):

- **No JavaScript.** Scripts do not run. Draw charts as inline SVG or CSS (bars as sized `<div>`s), and fill in
  data before converting.
- **No network.** Images, stylesheets and fonts load from the HTML file's folder (`base_dir`) or `data:` URIs,
  never from http(s) URLs. Download what you need first, or embed it.
- **Fonts.** Without fonts of your own, text uses Helvetica (`sans-serif`, Arial), Times (`serif`) and Courier
  (`monospace`), with bundled fallbacks, which cover Latin, Greek and Cyrillic. Chinese, Japanese, Korean, Arabic,
  Hebrew, Hindi, Thai and other scripts come out as `?` unless you pass a font that has them:
  `--font NotoSansSC-Regular.otf` (or `--system-fonts` to use the fonts installed on the machine). Use
  `@font-face` with a relative `src` for a specific typeface.
- **Modern CSS works**: flexbox, grid, tables, floats, multi-column, positioning, transforms, gradients, shadows,
  rounded corners, `object-fit`, SVG, web fonts, counters and CSS variables. Lay out as you would for Chrome's print
  preview; PdfPecker follows Chrome's layout.
- **Units.** Use `mm`, `pt` or `px` (96 px per inch). A4 content width with 16 mm margins is 178 mm (about 673 px).

## Checking the result

Always look at the pages before handing a PDF over: run `preview` and view the PNGs. Check for text cut off or
running off the page, a table or heading split badly across pages, a lone last line on a new page, empty pages,
`?` in place of letters (a missing font) and images that did not load (a wrong path). `text` confirms the wording
and order. Fix the HTML or CSS, convert again, and look again.

## Errors

The script exits with status 1 and prints the reason. From Python, every error is a `pdfpecker.PdfPeckerError`:
`PdfPeckerArgumentError` for a bad option, `PdfReadError` for a file that is not a readable PDF,
`PdfPasswordError`, `PdfLimitError` (too many pages), `PdfTimeoutError`, and `PdfFileError` for a font or file
that cannot be read.
