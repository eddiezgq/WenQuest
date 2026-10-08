"""Turn the agreed outline (docs/教材/<book>/00_提纲.md) into textbook/<book>/book.yaml: parts, chapters, sections.

The outline stays the one place where the table of contents is decided; book.yaml is generated from it and checked in,
and the build refuses to run when the two disagree (so a section reference like "4.8 节" is always checked against
the agreed outline).

    python3 textbook/tools/outline.py robotics
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {"robotics": ROOT / "docs" / "教材" / "机器人学" / "00_提纲.md"}
TITLES = {"robotics": ("机器人学", "Robotics")}


def meta(book: str) -> tuple[Path, str, str]:
    """(outline, title, title_en). A new book needs no change here: it writes textbook/<book>/meta.yaml with
    outline (path in the repository), title and title_en (第 10 轮)."""
    if book in SOURCES:
        return SOURCES[book], *TITLES[book]
    m = yaml.safe_load((ROOT / "textbook" / book / "meta.yaml").read_text(encoding="utf-8"))
    return ROOT / m["outline"], m["title"], m["title_en"]

PART = re.compile(r"^###\s+(.+?)\s*$")
CHAPTER = re.compile(r"^\*\*第\s*(M?\d+)\s*章\s+(.+?)\*\*\s*(?:【([^】]+)】)?")
SECTION = re.compile(r"^-\s+(M?\d+)\.(\d+)\s+(.+?)\s*$")


def chkey(no) -> int:
    """排序键：数学篇（M1、M2…）排在第 1 章之前（《人工智能》第 26 轮）。"""
    s = str(no)
    return int(s) if s.isdigit() else int(s[1:]) - 1000


def parse(text: str) -> dict:
    body = text.split("## 三、提纲", 1)[1].split("\n## ", 1)[0]
    parts: list[dict] = []
    chapters: list[dict] = []
    part = ""
    ch: dict | None = None
    for line in body.splitlines():
        if m := PART.match(line):
            part = m.group(1)
            if part != "附录":
                parts.append({"title": part})
            ch = None
            continue
        if m := CHAPTER.match(line):
            no = m.group(1)
            ch = {"no": int(no) if no.isdigit() else no, "title": m.group(2).strip(),
                  "level": m.group(3) or "", "part": part, "sections": []}
            chapters.append(ch)
            continue
        if ch and (m := SECTION.match(line)) and m.group(1) == str(ch["no"]):
            ch["sections"].append({"id": f"{m.group(1)}.{m.group(2)}", "title": m.group(3)})
    nos = [c["no"] for c in chapters]
    want = sorted(nos, key=chkey)                       # 数学篇在前，正文各章按号
    math_nos = [n for n in want if not str(n).isdigit()]
    plain = [n for n in want if str(n).isdigit()]
    if nos != want:
        raise ValueError(f"chapters are out of order: {nos}")
    if [chkey(n) for n in math_nos] != list(range(-999, -999 + len(math_nos))):
        raise ValueError(f"数学篇的章号要从 M1 起连续：{math_nos}")
    if plain != list(range(1, len(plain) + 1)):
        raise ValueError(f"chapter numbers are not consecutive: {plain}")
    return {"parts": parts, "chapters": chapters}


def generate(book: str) -> dict:
    src, title, title_en = meta(book)
    data = parse(src.read_text(encoding="utf-8"))
    return {"book": book, "title": title, "title_en": title_en, "source": str(src.relative_to(ROOT)), **data}


def write(book: str) -> Path:
    out = ROOT / "textbook" / book / "book.yaml"
    out.write_text("# 由 textbook/tools/outline.py 从提纲生成，请改提纲后重新生成，不要手改。\n"
                   + yaml.safe_dump(generate(book), allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    return out


if __name__ == "__main__":
    p = write(sys.argv[1] if len(sys.argv) > 1 else "robotics")
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    print(f"{p.relative_to(ROOT)}: {len(d['chapters'])} 章，{sum(len(c['sections']) for c in d['chapters'])} 节")
