#!/usr/bin/env python3
"""Extract Mermaid blocks from a markdown file, render each to PNG, write a temp md file.

Usage: render_mermaid.py <src_md>
Prints TMP_MD=<path> and PNG_COUNT=<n> to stdout.
If no Mermaid blocks found, prints TMP_MD=<src_md> and PNG_COUNT=0 and exits 0.
"""
import re, subprocess, os, sys

src = sys.argv[1]
src_dir = os.path.dirname(os.path.abspath(src))

with open(src) as f:
    content = f.read()

mermaid_pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
matches = list(mermaid_pattern.finditer(content))

if not matches:
    print(f"TMP_MD={src}")
    print("PNG_COUNT=0")
    sys.exit(0)

png_paths = []
for i, match in enumerate(matches):
    mmd_path = os.path.join(src_dir, f"_mermaid_{i}.mmd")
    png_path = os.path.join(src_dir, f"_mermaid_{i}.png")
    with open(mmd_path, 'w') as f:
        f.write(match.group(1))
    result = subprocess.run(
        ["npx", "@mermaid-js/mermaid-cli", "-i", mmd_path, "-o", png_path, "--scale", "3"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Warning: mermaid render failed for block {i}: {result.stderr}", file=sys.stderr)
        png_paths.append(None)
    else:
        png_paths.append(png_path)
    os.remove(mmd_path)

offset = 0
new_content = content
for i, match in enumerate(matches):
    png = png_paths[i]
    replacement = f"![Diagram]({png_paths[i]})" if png else match.group(0)
    new_content = (new_content[:match.start() + offset]
                   + replacement
                   + new_content[match.end() + offset:])
    offset += len(replacement) - (match.end() - match.start())

tmp_md = os.path.join(src_dir, "_tmp_pandoc_input.md")
with open(tmp_md, 'w') as f:
    f.write(new_content)

print(f"TMP_MD={tmp_md}")
print(f"PNG_COUNT={len([p for p in png_paths if p])}")
