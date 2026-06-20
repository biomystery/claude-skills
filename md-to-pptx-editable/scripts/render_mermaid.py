#!/usr/bin/env python3
"""Extract Mermaid blocks from a Marp markdown file, render each to PNG, write a temp md.

Usage: render_mermaid.py <src_md> [--config <mermaid_config.json>]

Replaces each ```mermaid ... ``` fence with an image reference to the rendered PNG,
so the diagram appears as a picture in the slide (Marp does not render Mermaid natively).
Uses the system Chrome via PUPPETEER_EXECUTABLE_PATH when available to avoid a
puppeteer Chromium download.

Prints to stdout:
  TMP_MD=<path>      temp markdown to feed to marp (equals src if no blocks)
  PNG_COUNT=<n>      number of diagrams rendered
  PNGS=<p1,p2,...>   rendered PNG paths (for cleanup by the caller)
"""
import re, subprocess, os, sys

src = sys.argv[1]
config = None
if "--config" in sys.argv:
    config = sys.argv[sys.argv.index("--config") + 1]

src_dir = os.path.dirname(os.path.abspath(src))
with open(src) as f:
    content = f.read()

matches = list(re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL).finditer(content))
if not matches:
    print(f"TMP_MD={src}")
    print("PNG_COUNT=0")
    print("PNGS=")
    sys.exit(0)

# Reuse the system Chrome if marp/this host has one, so npx mermaid-cli skips the
# ~150MB puppeteer Chromium download.
env = dict(os.environ)
for cand in (
    os.environ.get("CHROME_PATH", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
):
    if cand and os.path.exists(cand):
        env.setdefault("PUPPETEER_EXECUTABLE_PATH", cand)
        break

png_paths = []
for i, m in enumerate(matches):
    mmd = os.path.join(src_dir, f"_mermaid_{i}.mmd")
    png = os.path.join(src_dir, f"_mermaid_{i}.png")
    with open(mmd, "w") as f:
        f.write(m.group(1))
    cmd = ["npx", "-y", "@mermaid-js/mermaid-cli", "-i", mmd, "-o", png,
           "-b", "transparent", "--scale", "3", "--width", "1600"]
    if config:
        cmd += ["-c", config]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"Warning: mermaid render failed for block {i}: {r.stderr}", file=sys.stderr)
        png_paths.append(None)
    else:
        png_paths.append(png)
    os.remove(mmd)

# Splice image refs in for each fence (back-to-front to keep offsets valid).
new_content = content
for i in range(len(matches) - 1, -1, -1):
    m = matches[i]
    png = png_paths[i]
    repl = f"![Diagram]({os.path.basename(png)})" if png else m.group(0)
    new_content = new_content[:m.start()] + repl + new_content[m.end():]

tmp_md = os.path.join(src_dir, "_tmp_marp_input.md")
with open(tmp_md, "w") as f:
    f.write(new_content)

ok = [p for p in png_paths if p]
print(f"TMP_MD={tmp_md}")
print(f"PNG_COUNT={len(ok)}")
print("PNGS=" + ",".join(ok))
