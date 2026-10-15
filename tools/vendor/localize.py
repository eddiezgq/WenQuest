"""Point pages at /vendor/ (our own server) instead of Google Fonts and cdnjs (第 34 轮).

    python3 tools/vendor/localize.py <file or folder> ...      # rewrite in place, prints what changed

- <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=A&family=B…"> becomes one
  <link rel="stylesheet" href="/vendor/fonts/<a>.css"> per family; preconnect links to Google are removed.
- three.js r128 and KaTeX 0.16.9 load from /vendor/; if that fails (a page saved and opened from disk), the old
  CDN address is tried, so a downloaded lab still works where the CDN is reachable.
Fonts need no fallback: without them the page uses the system fonts.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import FONTS, slug  # noqa: E402

GOOGLE_CSS = re.compile(r'<link\s+rel="stylesheet"\s+href="https://fonts\.googleapis\.com/css2\?([^"]+)"\s*/?>')
PRECONNECT = re.compile(r'<link\s+rel="preconnect"\s+href="https://fonts\.(?:googleapis|gstatic)\.com"(?:\s+crossorigin)?\s*/?>\n?[ \t]*')
CDN = {
    "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js": ("/vendor/three/r128/three.min.js", "THREE"),
    "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js": ("/vendor/katex/0.16.9/katex.min.js", "katex"),
}


def font_links(query: str) -> str:
    query = query.replace("&amp;", "&")
    links = []
    for part in query.split("&"):
        if not part.startswith("family="):
            continue
        family = unquote(part[len("family="):].split(":")[0].replace("+", " "))
        if family not in FONTS:
            raise SystemExit(f"font {family!r} is not in tools/vendor/build.py FONTS: add it there first")
        links.append(f'<link rel="stylesheet" href="/vendor/fonts/{slug(family)}.css">')
    return "".join(links)


def script_tag(url: str) -> str:
    local, glob = CDN[url]
    # split "script" so the tag also survives inside Python strings and inline scripts
    return (f'<script src="{local}"></script><script>window.{glob}||document.write('
            f"'<scr'+'ipt src=\"{url}\"></scr'+'ipt>')</script>")


def localize(text: str, scripts: bool = True) -> str:
    text = PRECONNECT.sub("", text)
    text = GOOGLE_CSS.sub(lambda m: font_links(m.group(1)), text)
    for url in CDN if scripts else ():
        text = text.replace(f'<script src="{url}"></script>', script_tag(url))
    return text


def main(paths: list[str]) -> None:
    changed = 0
    for arg in paths:
        p = Path(arg)
        for f in ([p] if p.is_file() else sorted(x for x in p.rglob("*") if x.suffix in (".html", ".py", ".js"))):
            old = f.read_text(encoding="utf-8")
            new = localize(old, scripts=f.suffix != ".py")  # script tags inside Python strings: by hand
            if new != old:
                f.write_text(new, encoding="utf-8")
                changed += 1
                print("localized", f)
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    main(sys.argv[1:])
