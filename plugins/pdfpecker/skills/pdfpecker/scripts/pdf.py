#!/usr/bin/env python3
"""Command-line helper for the pdfpecker skill: HTML or Markdown to PDF, PDF to page images, text and merging.

    python3 pdf.py html  in.html out.pdf [--page-size A4] [--landscape] [--font F ...] [--system-fonts] [...]
    python3 pdf.py md    in.md   out.pdf [same options]
    python3 pdf.py preview in.pdf [--dpi 80] [--pages 1-3] [--format png] [--out-dir DIR]
    python3 pdf.py text  in.pdf [--pages 1-2]
    python3 pdf.py markdown in.pdf [out.md] [--pages 1-2] [--page-comments]
    python3 pdf.py info  in.pdf
    python3 pdf.py merge out.pdf a.pdf b.pdf ...

Exit status 0 on success, 1 when the work failed (the reason is printed), 2 for a wrong command line.
"""
import argparse
import os
import sys

try:
    import pdfpecker
except ImportError:
    sys.stderr.write("The pdfpecker package is not installed. Run: python3 -m pip install pdfpecker\n")
    sys.exit(1)


def add_pdf_options(p):
    p.add_argument("input", help="the HTML or Markdown file")
    p.add_argument("output", help="the PDF to write")
    p.add_argument("--page-size", help="A3, A4, A5, Letter, Legal or WIDTHxHEIGHT in mm (e.g. 100x150); @page size wins")
    p.add_argument("--landscape", action="store_true", help="turn the page size sideways")
    p.add_argument("--margin", type=float, help="page margins in points (72 per inch); @page margin wins")
    p.add_argument("--title", help="the document title (default: the HTML <title>)")
    p.add_argument("--author")
    p.add_argument("--language", help="the document language, such as en-GB")
    p.add_argument("--footer", help='text at the bottom of every page; {page} and {pages} are replaced')
    p.add_argument("--header", help="text at the top of every page")
    p.add_argument("--css", help="a CSS file applied after the document's own styles")
    p.add_argument("--font", action="append", default=[], help="a .ttf/.otf/.woff2 file or a folder of fonts (repeatable)")
    p.add_argument("--system-fonts", action="store_true", help="also use the fonts installed on this machine")
    p.add_argument("--allow-file-access", action="store_true",
                   help="let the document load files outside its own folder (only for HTML you trust)")
    p.add_argument("--pdfa", choices=["PDF/A-2b", "PDF/A-3b", "PDF/A-2u", "PDF/A-3u", "PDF/A-4", "PDF/A-4f"],
                   help="write an archival PDF/A file")
    p.add_argument("--tagged", action="store_true", help="write a tagged (accessible) PDF")
    p.add_argument("--fixed-date", action="store_true", help="fixed creation date, so the same input gives the same bytes")
    p.add_argument("--timeout", type=float, default=120, help="seconds before giving up (default 120)")


def pdf_options(a):
    options = {"timeout": a.timeout}
    if a.page_size:
        if "x" in a.page_size.lower():
            w, h = a.page_size.lower().split("x", 1)
            options["page_size"] = (float(w), float(h))
        else:
            options["page_size"] = a.page_size
    if a.landscape:
        options["landscape"] = True
    for key in ("margin", "title", "author", "language"):
        if getattr(a, key) is not None:
            options[key] = getattr(a, key)
    if a.footer:
        options["footer_text"] = a.footer
    if a.header:
        options["header_text"] = a.header
    if a.css:
        with open(a.css, encoding="utf-8") as f:
            options["user_style_sheet"] = f.read()
    if a.font:
        options["fonts"] = a.font
    if a.system_fonts:
        options["use_system_fonts"] = True
    if a.allow_file_access:
        options["allow_file_access"] = True
    if a.pdfa:
        options["conformance"] = a.pdfa
    if a.tagged:
        options["accessibility"] = "tagged"
    if a.fixed_date:
        options["creation_date"] = 0
    return options


def cmd_convert(a, markdown):
    convert = pdfpecker.markdown_file_to_pdf if markdown else pdfpecker.html_file_to_pdf
    pdf = convert(a.input, a.output, **pdf_options(a))
    print(f"{a.output}: {pdfpecker.pdf_page_count(pdf)} page(s), {len(pdf):,} bytes")


def cmd_preview(a):
    images = pdfpecker.pdf_to_images(a.input, dpi=a.dpi, format=a.format, pages=a.pages, timeout=a.timeout)
    out_dir = a.out_dir or os.path.dirname(os.path.abspath(a.input))
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(a.input))[0]
    numbers = _page_numbers(a.pages, len(images), a.input)
    for number, image in zip(numbers, images):
        path = os.path.join(out_dir, f"{stem}-page-{number}.{'jpg' if a.format == 'jpeg' else a.format}")
        with open(path, "wb") as f:
            f.write(image)
        print(path)


def _page_numbers(pages, count, pdf):
    # Name the files after the real page numbers when the selection is a simple list or range.
    if pages is None:
        return range(1, count + 1)
    total = pdfpecker.pdf_page_count(pdf)
    numbers = []
    for part in pages.replace(" ", "").split(","):
        part = part.replace("last", str(total))
        if "-" in part:
            start, end = part.split("-", 1)
            start, end = int(start or 1), int(end or total)
            step = 1 if end >= start else -1
            numbers.extend(range(start, end + step, step))
        elif part:
            numbers.append(int(part))
    return numbers if len(numbers) == count else range(1, count + 1)


def cmd_text(a):
    print(pdfpecker.pdf_to_text(a.input, pages=a.pages, timeout=a.timeout))


def cmd_markdown(a):
    markdown = pdfpecker.pdf_to_markdown(a.input, pages=a.pages, page_comments=a.page_comments, timeout=a.timeout)
    if a.output:
        with open(a.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(markdown)
        print(f"{a.output}: {len(markdown):,} characters")
    else:
        sys.stdout.write(markdown)


def cmd_info(a):
    with open(a.input, "rb") as f:
        data = f.read()
    print(f"{a.input}: {pdfpecker.pdf_page_count(data)} page(s), {len(data):,} bytes")


def cmd_merge(a):
    pdf = pdfpecker.merge_pdfs(a.inputs, timeout=a.timeout)
    with open(a.output, "wb") as f:
        f.write(pdf)
    print(f"{a.output}: {pdfpecker.pdf_page_count(pdf)} page(s), {len(pdf):,} bytes")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pdf.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    add_pdf_options(sub.add_parser("html", help="HTML file to PDF"))
    add_pdf_options(sub.add_parser("md", help="Markdown file to PDF"))
    p = sub.add_parser("preview", help="render PDF pages to images, to look at them")
    p.add_argument("input")
    p.add_argument("--dpi", type=float, default=80, help="resolution (default 80; 150 for detail)")
    p.add_argument("--pages", help='pages such as "1", "1-3,5" or "last" (default: all)')
    p.add_argument("--format", choices=["png", "jpeg", "webp"], default="png")
    p.add_argument("--out-dir", help="folder for the images (default: next to the PDF)")
    p.add_argument("--timeout", type=float, default=120)
    p = sub.add_parser("text", help="print the text of a PDF, pages separated by form feeds")
    p.add_argument("input")
    p.add_argument("--pages")
    p.add_argument("--timeout", type=float, default=120)
    p = sub.add_parser("markdown", help="convert any PDF to Markdown: headings, lists and tables in reading order")
    p.add_argument("input")
    p.add_argument("output", nargs="?", help="the .md file to write (default: print it)")
    p.add_argument("--pages")
    p.add_argument("--page-comments", action="store_true", help="start each page with <!-- page N -->")
    p.add_argument("--timeout", type=float, default=120)
    p = sub.add_parser("info", help="print the page count")
    p.add_argument("input")
    p = sub.add_parser("merge", help="merge PDFs into one")
    p.add_argument("output")
    p.add_argument("inputs", nargs="+")
    p.add_argument("--timeout", type=float, default=120)
    a = parser.parse_args(argv)
    try:
        if a.command in ("html", "md"):
            cmd_convert(a, a.command == "md")
        else:
            {"preview": cmd_preview, "text": cmd_text, "markdown": cmd_markdown, "info": cmd_info,
             "merge": cmd_merge}[a.command](a)
    except (pdfpecker.PdfPeckerError, OSError, ValueError) as e:
        sys.stderr.write(f"error: {e}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
