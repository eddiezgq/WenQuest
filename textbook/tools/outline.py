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
CHAPTER = re.compile(r"^\*\*第\s*(\d+)\s*章\s+(.+?)\*\*\s*(?:【([^】]+)】)?")
SECTION = re.compile(r"^-\s+(\d+)\.(\d+)\s+(.+?)\s*$")


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
            ch = {"no": int(m.group(1)), "title": m.group(2).strip(), "level": m.group(3) or "", "part": part, "sections": []}
            chapters.append(ch)
            continue
        if ch and (m := SECTION.match(line)) and int(m.group(1)) == ch["no"]:
            ch["sections"].append({"id": f"{m.group(1)}.{m.group(2)}", "title": m.group(3)})
    nos = [c["no"] for c in chapters]
    if nos != list(range(1, len(nos) + 1)):
        raise ValueError(f"chapter numbers are not consecutive: {nos}")
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
