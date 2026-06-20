#!/usr/bin/env bash
# convert-ebook.sh — convert an EPUB (or other Calibre-supported input) to a
# Kindle format (azw3 by default, or mobi) using Calibre's ebook-convert.
#
# Handles the two things that trip up a bare `ebook-convert` call on macOS:
#   1. The CLI ships INSIDE the .app bundle, not on $PATH.
#   2. Calibre may not be installed, and `brew install` can fail when
#      /opt/homebrew is not owned by the current user.
#
# Usage:
#   convert-ebook.sh <input.epub> [azw3|mobi] [output-path]
#
# Exit codes:
#   0  success
#   2  bad usage
#   3  input not found
#   4  Homebrew not writable — needs a manual `sudo chown` (message printed)
#   5  conversion failed

set -euo pipefail

INPUT="${1:-}"
FORMAT="${2:-azw3}"
OUTPUT="${3:-}"

if [ -z "$INPUT" ]; then
  echo "usage: convert-ebook.sh <input.epub> [azw3|mobi] [output-path]" >&2
  exit 2
fi
if [ ! -f "$INPUT" ]; then
  echo "error: input file not found: $INPUT" >&2
  exit 3
fi
case "$FORMAT" in
  azw3|mobi) ;;
  *) echo "error: format must be azw3 or mobi (got: $FORMAT)" >&2; exit 2 ;;
esac

# Default output: same dir/name as input with the new extension.
if [ -z "$OUTPUT" ]; then
  OUTPUT="${INPUT%.*}.${FORMAT}"
fi

# --- locate ebook-convert -----------------------------------------------------
find_ebook_convert() {
  if command -v ebook-convert >/dev/null 2>&1; then
    command -v ebook-convert
    return 0
  fi
  local bundled="/Applications/calibre.app/Contents/MacOS/ebook-convert"
  if [ -x "$bundled" ]; then
    echo "$bundled"
    return 0
  fi
  return 1
}

# --- install Calibre if missing ----------------------------------------------
if ! EBOOK_CONVERT="$(find_ebook_convert)"; then
  echo "Calibre not found — attempting install via Homebrew..." >&2

  if ! command -v brew >/dev/null 2>&1; then
    echo "error: Homebrew not installed. Install from https://brew.sh or" >&2
    echo "       download Calibre from https://calibre-ebook.com/download_osx" >&2
    exit 4
  fi

  # The classic failure mode: /opt/homebrew owned by root. brew then dies with
  # 'undefined method to_sym' or 'not writable'. This needs an interactive sudo
  # the agent cannot perform — surface the exact command for the user to run.
  BREW_PREFIX="$(brew --prefix)"
  if [ ! -w "$BREW_PREFIX" ]; then
    echo "error: $BREW_PREFIX is not writable, so Homebrew cannot install." >&2
    echo "Run this in a REAL terminal (sudo needs a password prompt):" >&2
    echo "    sudo chown -R \$(whoami) $BREW_PREFIX" >&2
    echo "Then re-run this script." >&2
    exit 4
  fi

  # Stale cask API cache can also trigger the to_sym crash; clearing is harmless.
  rm -rf "$HOME/Library/Caches/Homebrew/api" 2>/dev/null || true
  brew install --cask calibre

  if ! EBOOK_CONVERT="$(find_ebook_convert)"; then
    echo "error: Calibre installed but ebook-convert still not found." >&2
    exit 5
  fi
fi

echo "Using: $EBOOK_CONVERT" >&2
"$EBOOK_CONVERT" --version >&2 || true

# --- convert ------------------------------------------------------------------
echo "Converting -> $OUTPUT" >&2
"$EBOOK_CONVERT" "$INPUT" "$OUTPUT"

if [ -f "$OUTPUT" ]; then
  SIZE="$(ls -la "$OUTPUT" | awk '{print $5}')"
  echo "OK: $OUTPUT ($SIZE bytes)"
else
  echo "error: conversion reported success but output missing" >&2
  exit 5
fi
