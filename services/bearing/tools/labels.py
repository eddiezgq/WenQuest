"""Copy the web app's interface words (apps/bearing/src/i18n.js) to bearingkit/labels.json for the FreeCAD form.

python tools/labels.py          # write
python tools/labels.py --check  # exit 1 when labels.json is out of date (a test runs this)
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
I18N = HERE.parents[1] / "apps" / "bearing" / "src" / "i18n.js"
OUT = HERE / "bearingkit" / "labels.json"
ENTRY = re.compile(r"""(\w+):\s*\[\s*(['"])((?:(?!\2)[^\\]|\\.)*)\2\s*,\s*(['"])((?:(?!\4)[^\\]|\\.)*)\4\s*\]""")


def parse(text: str) -> dict:
    return {m.group(1): [m.group(3).replace("\\'", "'"), m.group(5).replace("\\'", "'")] for m in ENTRY.finditer(text)}


def render() -> str:
    return json.dumps(parse(I18N.read_text(encoding="utf-8")), ensure_ascii=False, indent=0, sort_keys=True) + "\n"


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if OUT.read_text(encoding="utf-8") == render() else 1)
    OUT.write_text(render(), encoding="utf-8")
    print(OUT)
