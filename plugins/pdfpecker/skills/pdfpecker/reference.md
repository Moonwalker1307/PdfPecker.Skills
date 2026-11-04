# pdfpecker reference

More detail for the pdfpecker skill. The full manual is at https://pdfpecker.net/docs/.

## Python API

```python
import pdfpecker

pdf: bytes = pdfpecker.html_to_pdf(html, base_dir="assets", page_size="A4", title="Report")
pdfpecker.html_file_to_pdf("in.html", "out.pdf")            # base_dir is the file's folder
pdfpecker.markdown_to_pdf(markdown_text)                     # CommonMark + GitHub tables, task lists, footnotes
pdfpecker.markdown_file_to_pdf("in.md", "out.pdf")
images: list[bytes] = pdfpecker.pdf_to_images(pdf, dpi=80, pages="1-3", format="png")   # or "jpeg", "webp"
text: str = pdfpecker.pdf_to_text(pdf)                       # pages separated by "\f"
pages: list[str] = pdfpecker.pdf_to_text_pages(pdf)
count: int = pdfpecker.pdf_page_count(pdf)
merged: bytes = pdfpecker.merge_pdfs([pdf, "other.pdf"])
```

PDF arguments take bytes or a path. Options of the HTML and Markdown calls, all keyword-only:

| Option | Meaning |
|---|---|
| `base_dir` | Folder for relative image, CSS and font paths. Without it, a string loads no local files. |
| `allow_file_access` | Also load files outside `base_dir` (trusted HTML only). |
| `page_size`, `landscape` | `"A3"`, `"A4"`, `"A5"`, `"Letter"`, `"Legal"` or `(width_mm, height_mm)`. `@page { size }` wins. |
| `margin` | Points, one number or `(top, right, bottom, left)`; default 36. `@page { margin }` wins. |
| `header_text`, `footer_text` | One line per page; `{page}` and `{pages}` are replaced. |
| `fonts`, `use_system_fonts` | Font files or folders that `font-family` can name; or installed fonts. |
| `title`, `author`, `subject`, `keywords`, `language` | Document properties. |
| `user_style_sheet` | Extra CSS applied last. |
| `creation_date` | Fixed date (datetime or Unix seconds) for byte-identical output. |
| `conformance` | `"PDF/A-2b"`, `"PDF/A-3b"`, `"PDF/A-2u"`, `"PDF/A-3u"`, `"PDF/A-4"`, `"PDF/A-4f"`. |
| `accessibility` | `"tagged"`, `"PDF/UA-1"`, `"PDF/UA-2"`. |
| `max_pages`, `timeout` | Stop with an error beyond this many pages or seconds. |

## Paged-media CSS that works

```css
@page { size: A4 landscape; margin: 15mm; }
@page :first { margin-top: 30mm; }                 /* also :left, :right, :blank */
@page wide { size: A4 landscape; }  .wide { page: wide; }   /* named pages: one section in landscape */

@page {                                           /* margin boxes: running headers and footers */
  @top-left     { content: string(chapter); }     /* h2 { string-set: chapter content(); } */
  @top-right    { content: "Company name"; }
  @bottom-center{ content: "Page " counter(page) " of " counter(pages); }
}
a.toc::after { content: target-counter(attr(href), page); }   /* page numbers in a table of contents */

h1, h2, h3 { break-after: avoid; }
table, figure, .keep { break-inside: avoid; }
.chapter { break-before: page; }
p { orphans: 2; widows: 2; }
thead { display: table-header-group; }            /* header row on every page (default for <thead>) */
tfoot { display: table-footer-group; }
```

Footnotes: `.note { float: footnote; }` moves the element to the foot of its page. Bookmarks come from headings
automatically.

## Layout CSS that works

Flexbox, grid (also `subgrid`, `repeat()`, `minmax()`, areas), tables (`border-collapse`, `colspan`, `rowspan`),
floats, multi-column (`columns: 2`), `position: relative/absolute/fixed` (fixed repeats on every page), transforms,
`calc()`, CSS variables, `clamp()`, linear, radial and conic gradients, `box-shadow`, `border-radius`, `opacity`,
filters, `object-fit`, `aspect-ratio`, `::before` and `::after` content, counters, `text-overflow: ellipsis`,
`line-clamp`, hyphenation (`hyphens: auto` with `lang` set), `@font-face` (TTF, OTF, WOFF, WOFF2), inline SVG and
`<img>` in PNG, JPEG, GIF, WebP, BMP, TIFF and SVG, media queries (`@media print` applies), and
`-pdfpecker-scale-to-fit: shrink` to fit text of any length into a fixed box (labels, badges, certificates).

## What does not work

- JavaScript (charting libraries, frameworks that render in the browser). Render data to HTML or SVG first.
- Loading from the network: `<img src="https://...">`, Google Fonts links and CDN stylesheets are skipped. Save the
  files next to the HTML and link them relatively, or use `data:` URIs.
- `<canvas>`, video, audio and iframes.
- Scripts other than Latin, Greek and Cyrillic without a font that has them: pass `fonts=[...]` or
  `use_system_fonts=True` (for example Noto Sans CJK, Noto Sans Arabic, Noto Sans Devanagari).

## Sizes

| Paper | mm | points | px at 96 dpi |
|---|---|---|---|
| A4 | 210 × 297 | 595 × 842 | 794 × 1123 |
| Letter | 215.9 × 279.4 | 612 × 792 | 816 × 1056 |
| A5 | 148 × 210 | 420 × 595 | 559 × 794 |

## Checklist before handing over a PDF

1. `preview` every page (or the first, a middle and the last of a long one) and look at them.
2. Nothing cut off at the right edge or bottom; no page that is empty or holds a single line.
3. Headings are not alone at the bottom of a page; table headers repeat; rows are not split.
4. No `?` instead of letters, and every image showed up.
5. `text` reads in the right order, and totals and dates are right.
