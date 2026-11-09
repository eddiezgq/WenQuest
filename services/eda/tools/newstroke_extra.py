"""Build view/vendor/newstroke-extra.js: the KiCad stroke-font glyphs KiCanvas leaves out.

KiCanvas ships glyphs only up to U+4E1F, so Chinese text in schematics showed as "?".
This takes the rest (U+4E20 onward, CJK included) from KiCad's own common/newstroke_font.cpp
and appends them to KiCanvas's glyph table (kicanvas.js reads globalThis.WQ_NEWSTROKE_EXTRA).

Usage: python services/eda/tools/newstroke_extra.py path/to/newstroke_font.cpp
(newstroke_font.cpp from the KiCad 9.0.9 source, common/newstroke_font.cpp).
"""

import json
import re
import sys
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "web" / "view" / "vendor"


def read_glyphs(cpp: str) -> list[str]:
    body = cpp.split("newstroke_font[] =", 1)[1].split("\n};", 1)[0]
    glyphs = []
    for line in body.splitlines():
        m = re.match(r'\s*"((?:[^"\\]|\\.)*)"\s*,', line)
        if m:
            glyphs.append(json.loads('"' + m.group(1) + '"'))
    return glyphs


def kicanvas_count(js: str) -> int:
    i = js.index("K3=[")
    j = js.index("];", i)
    return len(json.loads(js[i + 3 : j + 1]))


def main(cpp_path: str) -> None:
    glyphs = read_glyphs(Path(cpp_path).read_text(encoding="utf-8"))
    have = kicanvas_count((VENDOR / "kicanvas.js").read_text(encoding="utf-8"))
    extra = glyphs[have:]
    out = VENDOR / "newstroke-extra.js"
    out.write_text(
        "// KiCad newstroke glyphs from U+%04X on (KiCad 9.0.9 common/newstroke_font.cpp); "
        "licence: NEWSTROKE-LICENSE.txt. Built by services/eda/tools/newstroke_extra.py\n"
        "globalThis.WQ_NEWSTROKE_EXTRA=%s;\n"
        % (32 + have, json.dumps(extra, ensure_ascii=False, separators=(",", ":"))),
        encoding="utf-8",
    )
    print(f"{len(extra)} glyphs (U+{32 + have:04X}–U+{32 + len(glyphs) - 1:04X}) -> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
