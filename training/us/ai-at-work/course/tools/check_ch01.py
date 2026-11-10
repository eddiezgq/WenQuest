#!/usr/bin/env python3
"""The toy logits and the bar numbers in the lab pages must match course/calc/ch01.py."""
import json
import re
import subprocess
import sys
from pathlib import Path

C = Path(__file__).resolve().parents[1]
B = C.parent
sys.path.insert(0, str(C / "calc"))
import ch01  # noqa: E402

lab = (B / "src/en/labs/nexttoken.html").read_text(encoding="utf-8")
m = re.search(r"var LOGITS=(\{[^}]*\})", lab)
assert m and json.loads(m.group(1)) == ch01.LOGITS, "nexttoken.html LOGITS differ from calc/ch01.py"
out = json.loads(subprocess.run([sys.executable, str(C / "calc/ch01.py")], capture_output=True, text=True, check=True).stdout)
ver = (B / "src/en/labs/verify.html").read_text(encoding="utf-8")
for v in (out["area"], out["f_yield"], out["f_uts"]):
    assert f"{v:,}" in ver, f"verify.html does not show {v:,}"
print("ch01 labs consistent with calc")
