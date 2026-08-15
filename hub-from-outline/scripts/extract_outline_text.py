#!/usr/bin/env python3
"""Extract the text layer of an outline PDF, page by page.

Prints each page as a `--- page N (M chars) ---` block so the caller can see at a
glance whether the PDF has a usable text layer.

Exit codes:
  0  text extracted from at least one selected page
  2  the document has no usable text layer anywhere -> render pages and read them,
     or ask the user to paste the outline
  3  bad invocation or unreadable file -> fix the arguments, or ask for another file.
     Includes the case where --pages selected only blank pages but the document
     does carry text elsewhere.
"""

import argparse
import importlib
import site
import subprocess
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_NO_TEXT_LAYER = 2
EXIT_BAD_INPUT = 3

# A text-layer page of an outline carries at least a heading and a few rows. Under
# this, the page is a scan, a divider, or a near-empty cover. Applied per page, and
# a document is only called image-only when *every* page falls below it.
MIN_CHARS_PER_PAGE = 40

INSTALL_HELP = """Could not install pypdf automatically. Install it one of these ways:
  python3 -m pip install --user --break-system-packages pypdf
  pipx install pypdf
  python3 -m venv ~/.venvs/skills && ~/.venvs/skills/bin/pip install pypdf"""


def load_reader():
    """Import pypdf, installing it if absent. Returns the class, or None on failure."""
    try:
        from pypdf import PdfReader

        return PdfReader
    except ImportError:
        pass

    print("pypdf not found; installing...", file=sys.stderr)
    base = [sys.executable, "-m", "pip", "install", "--quiet", "pypdf"]
    if sys.prefix != sys.base_prefix:
        # Inside a venv, --user is rejected outright.
        attempts = [base]
    else:
        # PEP 668 environments (Homebrew python, most distro pythons) refuse the
        # plain --user form and name --break-system-packages as the escape.
        attempts = [base + ["--user"], base + ["--user", "--break-system-packages"]]

    for cmd in attempts:
        if subprocess.run(cmd, capture_output=True).returncode != 0:
            continue
        # A first-ever --user install can land in a directory that did not exist when
        # this interpreter resolved its paths, so it is not yet importable.
        user_site = site.getusersitepackages()
        if isinstance(user_site, str) and user_site not in sys.path:
            sys.path.append(user_site)
        importlib.invalidate_caches()
        try:
            from pypdf import PdfReader

            return PdfReader
        except ImportError:
            break

    print(INSTALL_HELP, file=sys.stderr)
    return None


def parse_pages(spec, total):
    """Turn '1-4' / '2,5' / '' into a sorted list of 1-based page numbers.

    Raises ValueError with an actionable message rather than letting int() throw or
    silently returning an empty selection.
    """
    if not spec:
        return list(range(1, total + 1))

    pages = set()
    for part in [p.strip() for p in spec.split(",") if p.strip()]:
        try:
            if "-" in part:
                start, _, end = part.partition("-")
                lo, hi = int(start), int(end)
                if lo > hi:
                    raise ValueError(f"--pages range '{part}' runs backwards")
                pages.update(range(lo, hi + 1))
            else:
                pages.add(int(part))
        except ValueError as exc:
            if str(exc).startswith("--pages"):
                raise
            raise ValueError(
                f"--pages value '{part}' is not a page number or N-M range"
            ) from None

    selected = sorted(p for p in pages if 1 <= p <= total)
    if not selected:
        raise ValueError(
            f"--pages '{spec}' selects nothing in a {total}-page document "
            f"(valid pages are 1-{total})"
        )
    return selected


def page_text(reader, number):
    """Extract one page's text, treating an extractor failure as an empty page."""
    try:
        return (reader.pages[number - 1].extract_text() or "").strip()
    except Exception as exc:
        print(f"page {number}: extract failed ({exc})", file=sys.stderr)
        return ""


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
        return EXIT_BAD_INPUT

    PdfReader = load_reader()
    if PdfReader is None:
        return EXIT_BAD_INPUT

    try:
        reader = PdfReader(str(args.pdf))
        total = len(reader.pages)
    except Exception as exc:  # encrypted, truncated, or not a PDF
        print(f"Cannot open {args.pdf}: {exc}", file=sys.stderr)
        print("Ask the user to re-export or paste the outline.", file=sys.stderr)
        return EXIT_BAD_INPUT

    try:
        selected = parse_pages(args.pages, total)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_BAD_INPUT

    extracted = 0
    for number in selected:
        text = page_text(reader, number)
        if len(text) >= MIN_CHARS_PER_PAGE:
            extracted += 1
        print(f"\n--- page {number} ({len(text)} chars) ---\n{text}")

    if extracted:
        return EXIT_OK

    # Nothing in the selection. Before declaring the PDF a scan, check whether the
    # pages the caller did not ask for carry text — otherwise a sparse cover page
    # sends the caller off to OCR a perfectly extractable document.
    elsewhere = [
        n
        for n in range(1, total + 1)
        if n not in set(selected) and len(page_text(reader, n)) >= MIN_CHARS_PER_PAGE
    ]
    if elsewhere:
        preview = ", ".join(str(n) for n in elsewhere[:10])
        more = " ..." if len(elsewhere) > 10 else ""
        print(
            f"\nThe selected page(s) are blank, but pages {preview}{more} carry text. "
            f"Rerun with --pages covering those.",
            file=sys.stderr,
        )
        return EXIT_BAD_INPUT

    print(
        f"\nNo usable text layer anywhere in {args.pdf} "
        f"({total} page(s) below {MIN_CHARS_PER_PAGE} chars). This is an image-only "
        "PDF: render the pages and read them, or ask the user to paste the outline.",
        file=sys.stderr,
    )
    return EXIT_NO_TEXT_LAYER


if __name__ == "__main__":
    sys.exit(main())
