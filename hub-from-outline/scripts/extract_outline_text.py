#!/usr/bin/env python3
"""Extract the text layer of an outline PDF, page by page.

Prints each page as a `--- page N (M chars) ---` block so the caller can see at a
glance whether the PDF actually has a usable text layer. Exits 2 with an explicit
message when it does not, so the caller falls through to the OCR / paste strategy
instead of parsing an empty extract.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# A text-layer page of an outline/syllabus carries at least a heading and a few
# rows. Under this, the page is a scan wrapped in a PDF, not extractable text.
MIN_CHARS_PER_PAGE = 40


def load_reader():
    """Import pypdf, installing it into the user site-packages if absent."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("pypdf not found; installing into user site-packages...", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--user", "--quiet", "pypdf"]
        )
        from pypdf import PdfReader
    return PdfReader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="path to the outline PDF")
    parser.add_argument(
        "--pages",
        default="",
        help="1-based page selection, e.g. '1-4' or '2,5,9' (default: all pages)",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"No such file: {args.pdf}", file=sys.stderr)
        return 2

    PdfReader = load_reader()
    try:
        reader = PdfReader(str(args.pdf))
    except Exception as exc:  # encrypted, truncated, or not a PDF
        print(f"Cannot open {args.pdf}: {exc}", file=sys.stderr)
        print("Ask the user to re-export or paste the outline.", file=sys.stderr)
        return 2

    total = len(reader.pages)
    wanted = parse_pages(args.pages, total)

    extracted = 0
    for i in wanted:
        try:
            text = reader.pages[i - 1].extract_text() or ""
        except Exception as exc:
            text = ""
            print(f"page {i}: extract failed ({exc})", file=sys.stderr)
        if len(text.strip()) >= MIN_CHARS_PER_PAGE:
            extracted += 1
        print(f"\n--- page {i} ({len(text.strip())} chars) ---\n{text}")

    if extracted == 0:
        print(
            f"\nNo usable text layer in {args.pdf} "
            f"({len(wanted)} page(s) below {MIN_CHARS_PER_PAGE} chars). "
            "This is an image-only PDF: render the pages and read them, or ask "
            "the user to paste the outline.",
            file=sys.stderr,
        )
        return 2
    return 0


def parse_pages(spec, total):
    """Turn '1-4' / '2,5' / '' into a sorted list of 1-based page numbers."""
    if not spec:
        return list(range(1, total + 1))
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, _, end = part.partition("-")
            pages.update(range(int(start), int(end) + 1))
        elif part:
            pages.add(int(part))
    return sorted(p for p in pages if 1 <= p <= total)


if __name__ == "__main__":
    sys.exit(main())
