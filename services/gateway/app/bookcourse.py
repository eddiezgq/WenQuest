"""体验课（第 117 轮）：每本教材在课程包页上自动多一个课程包“《书名》· 体验课”，和现有课程包走同一套发布。

不在构建时写清单，而是网关按服务器上已部署的教材（<textbook_dir>/<书>/web/index.json 与 slides/）当场生成：
互动课件是另一步构建的，这样不漏；教材更新部署后，清单自动跟着变。

第 1 节是课程说明，第 i 章在第 i+1 节（与现有课程包相同）。每章一节：本章导读（各节标题，未写完的标“编写中”）、网页版教材链接、互动课件链接（有才放）、虚拟实验链接（有才放，
指到所在小节）。不设作业、测验、考试，不计成绩（D-4）。整章还没写的先当“建设中”大纲发布，写好后再按“发布”会换成完整的一节。
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode

from .textbook_api import chdir

SUFFIX = ("体验课", "Trial course")


def _link(app_url: str, **q: str) -> str:
    return f"{app_url.rstrip('/')}/pages/textbook/textbook?{urlencode(q)}"


def _short(t: str, n: int) -> str:
    """The first clause of a long title, at most n characters."""
    t = re.split(r"[：:；;，,。.（(—]", t.strip(), maxsplit=1)[0].strip() or t.strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def _p(s: str) -> str:
    return html.escape(s, quote=False)


def make(root: Path, book: str, app_url: str) -> dict | None:
    """The course pack manifest of one built textbook, or None when there is no built index."""
    f = root / book / "web" / "index.json"
    if not f.is_file():
        return None
    idx = json.loads(f.read_text(encoding="utf-8"))
    title, title_en = idx.get("title") or book, idx.get("title_en") or idx.get("title") or book
    chapters = [c for c in idx.get("chapters") or [] if c.get("sections")]
    res = idx.get("resources") or {}
    lessons = []
    for i, c in enumerate(chapters, start=1):
        no = str(c["no"])
        ct, cte = c.get("title") or "", c.get("title_en") or c.get("title") or ""
        ct, cte = _short(ct, 40) if len(ct) > 40 else ct, _short(cte, 80) if len(cte) > 80 else cte
        label = (f"第 {no} 章 {ct}", f"Chapter {no} {cte}") if no.isdigit() else (f"{no} {ct}", f"{no} {cte}")
        secs = c["sections"]
        written = [s for s in secs if s.get("written")]
        li_zh = "".join(f"<li>{_p(s['id'])} {_p(s['title'])}{'' if s.get('written') else '（编写中）'}</li>" for s in secs)
        li_en = "".join(f"<li>{_p(s['id'])} {_p(s.get('title_en') or s['title'])}{'' if s.get('written') else ' (being written)'}</li>"
                        for s in secs)
        acts: list[dict] = [{
            "type": "page", "name": ["本章导读", "Chapter guide"], "visible": 1,
            "content": [f"<p>本章 {len(secs)} 节，已写好 {len(written)} 节。点下面的链接读网页版教材；互动课件、虚拟实验在本节里也有链接。</p><ol>{li_zh}</ol>",
                        (f"<p>{len(secs)} sections, {len(written)} written. Open the web textbook below; the interactive slides and "
                         f"virtual labs are linked in this section too.</p><ol>{li_en}</ol>")]}]
        first = (written or secs)[0]["id"]
        acts.append({"type": "url", "name": [f"网页版教材 · {label[0]}", f"Web textbook · {label[1]}"],
                     "url": _link(app_url, book=book, s=first), "visible": 1})
        if (root / book / "slides" / f"{chdir(no)}.html").is_file():
            acts.append({"type": "url", "name": [f"互动课件 · {label[0]}", f"Interactive slides · {label[1]}"],
                         "url": _link(app_url, book=book, slides=no), "visible": 1})
        for r in res.get(no) or []:
            if r.get("kind") != "lab":
                continue
            # 名字要短：中英两种合起来进 Moodle 的活动名（255 字以内），实验标题常是一整句，只取第一个分句
            acts.append({"type": "url", "name": [f"虚拟实验 {r['num']}：{_short(r.get('title', ''), 40)}",
                                                 f"Virtual lab {r['num']}: {_short(r.get('title_en') or r.get('title', ''), 80)}"],
                         "url": _link(app_url, book=book, s=r.get("sec") or first), "visible": 1})
        lessons.append({"no": i, "section": i + 1, "name": list(label), "placeholder": not written,
                        "summary": [f"<p>{_p(ct)}</p>", f"<p>{_p(cte)}</p>"], "activities": acts})
    if not lessons:
        return None
    toc_zh = "".join(f"<li>{_p(x['name'][0])}</li>" for x in lessons)
    toc_en = "".join(f"<li>{_p(x['name'][1])}</li>" for x in lessons)
    info = [(f"<p>本课程用问渠教材《{_p(title)}》建成，供老师和企业体验：每章一节，节里有网页版教材、互动课件和虚拟实验的链接。"
             "<strong>供体验，不设作业和考试，不计成绩</strong>；内容随教材持续更新，标“编写中”的小节写好后会补上。</p>"
             f"<h4>章目</h4><ol>{toc_zh}</ol>"),
            (f"<p>This course is built from the WenQuest textbook <em>{_p(title_en)}</em> for teachers and companies to try: one "
             "section per chapter, with links to the web textbook, interactive slides and virtual labs. <strong>It is for trying out "
             "only: no assignments, no exams, no grades</strong>; it follows the textbook as it grows.</p>"
             f"<h4>Chapters</h4><ol>{toc_en}</ol>")]
    stamp = str(int(f.stat().st_mtime))
    return {"format": 1, "book": book, "version": stamp, "generated": "bookcourse",
            "course": {"fullname": [f"《{title}》· {SUFFIX[0]}", f"{title_en} · {SUFFIX[1]}"],
                       "shortname": f"WQT-{book.upper()}"[:100],
                       "summary": [f"<p>问渠教材《{_p(title)}》体验课：{len(lessons)} 章，网页版教材、互动课件、虚拟实验。供体验，不计成绩。</p>",
                                   (f"<p>Trial course on the WenQuest textbook <em>{_p(title_en)}</em>: {len(lessons)} chapters, "
                                    "web textbook, interactive slides, virtual labs. For trying out; not graded.</p>")],
                       "blurb": f"免费体验课：问渠教材《{title}》，{len(lessons)} 章，网页版教材、互动课件、虚拟实验。",
                       "info": {"name": ["课程说明", "About this course"],
                                "activities": [{"type": "page", "name": ["课程说明", "About this course"], "content": info,
                                                "visible": 1}]}},
            "batches": [{"no": 1, "name": ["全部章节", "All chapters"], "lessons": [x["no"] for x in lessons], "exams": []}],
            "exam_section": {"section": len(lessons) + 2, "name": ["考试", "Exams"]},
            "lessons": lessons, "exams": []}
