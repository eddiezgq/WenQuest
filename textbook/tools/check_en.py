"""Quick check of one English section while translating (the full build checks the same and more).

    python3 textbook/tools/check_en.py robotics/ch04/04-2.en.md

Checks parity with the Chinese section, English glossary terms, the English copies of the programs it lists, and
runs the chapter's figure programs with English labels (figures go to a temporary folder).
"""
import csv
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import english

TOOLS = Path(__file__).resolve().parent


def main(path: str) -> int:
    en = Path(path) if Path(path).is_absolute() else TOOLS.parent / path
    zh = en.with_name(en.name[:-6] + ".md")
    problems = []
    a, b = zh.read_text(encoding="utf-8"), en.read_text(encoding="utf-8")
    problems += english.parity(a, b)
    book_dir = next(p for p in en.resolve().parents if p.parent == TOOLS.parent)      # textbook/<book>/
    with (book_dir / "conventions" / "术语表.csv").open(encoding="utf-8") as f:
        gl = {r["中文"].strip(): (r.get("English") or "").strip() for r in csv.DictReader(f)}
    problems += english.check_terms(a, b, gl)
    for src in re.findall(r"^src:\s*(code/\S+\.py)", b, re.M):
        p = en.parent / src
        why = english.same_code(p, p.parent / "en" / p.name)
        if why:
            problems.append(why)
    if re.search(r"[一-鿿]", re.sub(r"^```.*?^```", "", b, flags=re.S | re.M)):
        problems.append("英文版正文里还有中文：" + ", ".join(sorted(set(re.findall(r"[一-鿿]+", b)))[:8]))
    code = en.parent / "code"
    with tempfile.TemporaryDirectory() as tmp:
        for prog in sorted(code.glob("*.py")):
            if prog.name.startswith("_"):
                continue
            env = {**os.environ, "WQ_LANG": "en", "WQ_BOOK_FIGDIR": tmp, "WQ_BOOK_OUT": os.path.join(tmp, "out.json"),
                   "PYTHONPATH": str(TOOLS), "MPLBACKEND": "Agg"}
            r = subprocess.run([sys.executable, prog.name], cwd=code, env=env, capture_output=True, text=True, timeout=300)
            if r.returncode:
                problems.append(f"{prog.name}（英文运行）：" + (r.stderr.strip().splitlines() or ["?"])[-1])
    for p in problems:
        print("✗", p)
    print("通过" if not problems else f"{len(problems)} 个问题")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
