"""Fail when a page that goes live loads fonts or scripts from Google Fonts or a public CDN (第 34 轮).

In mainland China Google Fonts cannot be reached and public CDNs are slow; a blocked stylesheet in <head> holds the whole
page. Use /vendor/ instead (tools/vendor/build.py, tools/vendor/localize.py).    python3 tools/vendor/check_external.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVED = ["site", "tools/site_home", "tools/site_cases", "textbook/web-editions", "textbook/tools", "labs/micro",
          "services/gateway/app", "apps/web/src", "apps/cam"]
SKIP = [
    "site/vendor/",                      # the local copies themselves
    "labs/micro/spice/",                 # SPICE calibration page, not offered on the platform
    "labs/micro/tools/",                 # browser tests: they block or stub these addresses
    "apps/web/src/static/h5/mathjax/",   # MathJax's built-in default addresses (speech add-on, only on request)
    "apps/cam/dist/",                    # built from apps/cam/src (checked above)
    "/node_modules/", "/__pycache__/",
]
EXT = (".html", ".js", ".mjs", ".css", ".py", ".vue", ".ts")
BAD = re.compile(r"fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|unpkg\.com")
# allowed on a line: the fallback after a local copy (document.write … only when the local file did not load),
# the Verilog lab's engine list (a server can override it; China deployments use the server and /vendor/),
# and the website case builder's preview mode (a local preview, never published)
ALLOWED = re.compile(r"document\.write\(|scr'\+'ipt src=|const BASES = |^CDN_THREE = ")


def problems() -> list[str]:
    out = []
    for top in SERVED:
        for f in sorted((ROOT / top).rglob("*")):
            rel = f.relative_to(ROOT).as_posix()
            if f.suffix not in EXT or not f.is_file() or any(s in "/" + rel for s in SKIP):
                continue
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if BAD.search(line) and not ALLOWED.search(line.strip()):
                    out.append(f"{rel}:{i}: {BAD.search(line).group(0)}")
    return out


if __name__ == "__main__":
    found = problems()
    for p in found:
        print(p)
    if found:
        sys.exit(f"{len(found)} external font/CDN address(es) in pages that go live: use /vendor/ (tools/vendor/localize.py)")
    print("no Google Fonts or public CDN addresses in pages that go live")
