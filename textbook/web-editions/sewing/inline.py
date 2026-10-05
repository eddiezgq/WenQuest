"""Inline the shared libraries into a lab page (round 20).

Lab pages are single self-contained HTML files (the course pack attaches each one to Moodle as one file), but the
sewing labs share the lockstitch mechanism library src/lib/lockstitch-kit.js. In the source a lab writes

    <script src="../../lib/lockstitch-kit.js" data-inline></script>

and every build (build.py for the web edition, course/tools/build_course.py for the course pack) replaces that tag
with the library's text. Opening the source page directly in a browser still works, through the relative path.
"""
import re
from pathlib import Path

LIB = Path(__file__).resolve().parent / "src" / "lib"
TAG = re.compile(r'<script src="(?:\.\./)+lib/([A-Za-z0-9_.-]+)" data-inline></script>')


def inline(html: str) -> str:
    def rep(m: re.Match) -> str:
        p = LIB / m.group(1)
        if not p.is_file():
            raise SystemExit(f"inline: no library {p}")
        return "<script>/* " + m.group(1) + " */\n" + p.read_text(encoding="utf-8").replace("</script", "<\\/script") + "\n</script>"
    return TAG.sub(rep, html)
