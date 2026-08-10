#!/usr/bin/env python3
"""
Fetch a course source document and print its text.

Handles the three shapes course sites actually use:
  1. Google Docs   https://docs.google.com/document/d/<ID>/preview  -> export?format=txt
  2. Google Drive  https://drive.google.com/open?id=<ID>            -> uc?export=download
  3. Any direct PDF URL, or a local .pdf path

WebFetch cannot read Google Docs (it returns an empty shell) and cannot read PDFs
at all. This script is the workaround for both.

Usage:
    fetch_course_doc.py <url-or-id> [--pages 1-6] [--save out.pdf] [--outline]

    --pages 1-6   Only extract these PDF pages (1-indexed, inclusive). Course
                  overview pages are usually 2-5; the rest is worked problems.
    --save PATH   Keep the downloaded PDF (for archiving alongside the note).
    --outline     Print only the first 12 lines of each page (fast page survey).
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DOC_RE = re.compile(r"docs\.google\.com/document/d/([A-Za-z0-9_-]+)")
DRIVE_RE = re.compile(r"drive\.google\.com/.*?[?&/](?:id=|d/)([A-Za-z0-9_-]+)")
BARE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{20,}$")


def curl(url: str, dest: Path | None = None) -> bytes:
    cmd = ["curl", "-sL", "--max-time", "120", url]
    if dest:
        cmd += ["-o", str(dest)]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        sys.exit(f"curl failed for {url}: {res.stderr.decode()[:200]}")
    return res.stdout


def parse_pages(spec: str, total: int) -> list[int]:
    if "-" in spec:
        lo, hi = spec.split("-", 1)
        return list(range(int(lo) - 1, min(int(hi), total)))
    return [int(spec) - 1]


def pdf_text(path: Path, pages: str | None, outline: bool) -> str:
    try:
        import pypdf
    except ImportError:
        sys.exit("pypdf not installed. Run: pip3 install --user pypdf\n"
                 "(macOS has no pdftotext by default; pypdf is the portable fallback.)")
    reader = pypdf.PdfReader(str(path))
    idxs = parse_pages(pages, len(reader.pages)) if pages else range(len(reader.pages))
    out = []
    for i in idxs:
        text = reader.pages[i].extract_text() or ""
        if outline:
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()][:12]
            text = "\n".join(lines)
        out.append(f"=== PAGE {i + 1} ===\n{text}")
    return "\n\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="Google Doc/Drive URL, direct PDF URL, bare file ID, or local path")
    ap.add_argument("--pages", help="PDF page range, e.g. 1-6")
    ap.add_argument("--save", help="Keep the downloaded PDF at this path")
    ap.add_argument("--outline", action="store_true", help="First 12 lines per page only")
    args = ap.parse_args()

    target = args.target

    # Local file
    local = Path(target).expanduser()
    if local.exists():
        print(pdf_text(local, args.pages, args.outline))
        return

    # Google Doc -> plain text export (WebFetch returns nothing useful here)
    m = DOC_RE.search(target)
    if m:
        print(curl(f"https://docs.google.com/document/d/{m.group(1)}/export?format=txt").decode("utf-8", "replace"))
        return

    # Google Drive file -> direct download
    m = DRIVE_RE.search(target) or (BARE_ID_RE.match(target) and re.match(r"(.*)", target))
    file_id = m.group(1) if m else None
    url = f"https://drive.google.com/uc?export=download&id={file_id}" if file_id else target

    dest = Path(args.save).expanduser() if args.save else Path(tempfile.mkdtemp()) / "source.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    curl(url, dest)

    head = dest.read_bytes()[:5]
    if head != b"%PDF-":
        sys.exit(f"Not a PDF (got {head!r}). The file may require sign-in, or the ID is wrong.")

    if args.save:
        print(f"[saved {dest}]", file=sys.stderr)
    print(pdf_text(dest, args.pages, args.outline))


if __name__ == "__main__":
    main()
