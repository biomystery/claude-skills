#!/usr/bin/env bash
# link-skills.sh — idempotent: link this repo's skills into ~/.claude/skills.
# Real directories already there are backed up as .bak-<ts>-<name> before being replaced.
# Usage: scripts/link-skills.sh [--dry-run]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/skills"; TS=$(date +%Y%m%d-%H%M%S); DRY=${1:-}
run(){ if [ "$DRY" = "--dry-run" ]; then echo "DRY: $*"; else "$@"; fi; }
[ "$DRY" = "--dry-run" ] || mkdir -p "$DEST"
for d in "$REPO"/*/; do
  name=$(basename "$d"); [ -f "$d/SKILL.md" ] || continue
  tgt="$DEST/$name"
  if [ -L "$tgt" ]; then run ln -sfn "$REPO/$name" "$tgt"
  elif [ -e "$tgt" ]; then run mv "$tgt" "$DEST/.bak-$TS-$name"; run ln -s "$REPO/$name" "$tgt"
  else run ln -s "$REPO/$name" "$tgt"; fi
done
echo "done${DRY:+ ($DRY)} (backups, if any: $DEST/.bak-$TS-*)"
