"""Light check of one English section while translating: parity, glossary terms, English program copies, leftover Chinese.
Unlike check_en.py it does not run the chapter's programs (several translators can use it at once without running out of memory).

    python3 textbook/tools/check_en_light.py mechdesign/ch04/04-2.en.md
"""
import csv
import re
import sys
from pathlib import Path

import english

TOOLS = Path(__file__).resolve().parent


def main(path: str) -> int:
    en = Path(path) if Path(path).is_absolute() else TOOLS.parent / path
    zh = en.with_name(en.name[:-6] + ".md")
    a, b = zh.read_text(encoding="utf-8"), en.read_text(encoding="utf-8")
    problems = list(english.parity(a, b))
    book_dir = next(p for p in en.resolve().parents if p.parent == TOOLS.parent)
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
    for p in problems:
        print("✗", p)
    print("通过" if not problems else f"{len(problems)} 个问题")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
