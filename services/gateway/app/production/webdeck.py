"""网页互动课件 for AI-built lessons (round 32, 附二): the same engine and layouts as 《缝纫机设计与制造》
(textbook/tools/webcourse/wc_slides.py, copied here as wc_slides.py — a test keeps the two identical).

  design(ai, spec, ...)  the 课件设计师 lays the lesson out as pages (layout + bilingual text + speaker notes)
  fallback(spec, ...)    the same lesson laid out by rule, used when the designer's pages do not hold up
  build(out, ...)        one self-contained HTML deck: pages flip like PPT, the lesson's own animation loops and its
                         virtual lab runs inside the page (full-screen with one click), S opens the presenter window

The engine reads a "book" folder (course.yaml with the course name, img/*.webp figures, src/zh/labs/<page>.html live
pages); for a lesson we lay out such a folder in a temporary directory and load a fresh copy of the engine on it.
"""
from __future__ import annotations

import base64
import html as H
import importlib.util
import io
import json
import logging
import os
import re
import tempfile
import threading
from pathlib import Path
from typing import Any

log = logging.getLogger("wenquest.webdeck")
HERE = Path(__file__).resolve().parent
_LOCK = threading.Lock()

LAYOUT_GUIDE = """\
Layouts (one per page; every text field is ["中文", "English"]; at most 3 points per page, each point ≤ 22 Chinese characters
and one English line — split into more pages rather than crowding):
- cover: video (a clip name), kicker, title, sub — the first page
- question: tag, title, facts (exactly 3 short facts with the numbers) — the robot problem
- section: num ("01", "02", …), title — opens a part of the lesson
- points: title, points (≤3), optional tag, optional foot — key ideas
- split: title, points (≤3), visual — points left, picture/clip right
- figure: title, visual, optional caption — one big picture or live clip
- duo: title, left, right — each {visual fields (video|fig|svg), label, note} — a comparison
- lab: title, shot: {page: "lab"}, tasks (≤3) — the virtual lab inside the page (only if a lab exists)
- bignum: title, nums: [{n: "60 s", n_en: "", label}] (≤3), optional foot — key numbers
- chain: title, steps (3–7 short pairs), hot (indexes to highlight), foot — a process
- timeline: title, events: [{year: 1965, who, what}] (3–6) — history
- answer: optional tag, title, rows: [["已知/Given…", "value"], …] (≤5), optional side: {big: "60 s", text}, foot — the solved robot problem
- summary: title, points (3), after — what to do after class
visual is one of: {"video": "<clip name>"} (live: the lesson's animation or lab), {"fig": "<figure name>"},
{"svg": "<svg viewBox='0 0 900 600'>…</svg>"} (a new simple diagram: light lines #f3f6fa on dark, accents #f2b705 #2ec4b6
#ff7a45 #4c8dff, text ≥ 22 px).
Every page has "notes": ["中文讲稿 60–150 字", "English script"] for the presenter window.
Structure (22–30 pages): cover → question (robot problem) → 3–5 parts (section → concept pages → a live page → worked
modelling) → robot link and one everyday example → answer → summary. At least 3 live pages (animation, lab)."""

DESIGNER = (
    "You are the 课件设计师 of the 问渠 team. Lay out ONE lesson as a web interactive slide deck in the house standard "
    "(it replaces PowerPoint): pages that flip like PPT, one idea per page, Chinese large on top and English below, "
    "live animation and virtual-lab pages inside. Use ONLY the lesson's own content and numbers (never invent facts or "
    "numbers), the clips and figures listed as available, and the layouts below.\n\n" + LAYOUT_GUIDE)

SCHEMA = {"type": "object", "properties": {"slides": {"type": "array", "items": {"type": "object"}}}, "required": ["slides"]}


def _pair(v: Any) -> list[str]:
    if isinstance(v, (list, tuple)) and v:
        a = str(v[0] or "").strip()
        b = str(v[1] if len(v) > 1 else v[0] or "").strip()
        return [a or b, b or a]
    if isinstance(v, dict):
        a, b = str(v.get("zh") or "").strip(), str(v.get("en") or "").strip()
        return [a or b, b or a]
    s = str(v or "").strip()
    return [s, s]


def _text(h: str) -> str:
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", h or "")).split())


def _short(p: list[str], n_zh: int = 40, n_en: int = 110) -> list[str]:
    zh, en = p
    if len(zh) > n_zh:
        zh = zh[: n_zh - 1].rstrip("，、；,; ") + "…"
    if len(en) > n_en:
        en = en[: n_en - 1].rsplit(" ", 1)[0] + "…"
    return [zh, en]


def _sentences(zh: str, en: str, k: int) -> list[list[str]]:
    zs = [s for s in re.split(r"(?<=[。；！？])", _text(zh)) if s.strip()]
    es = [s for s in re.split(r"(?<=[.;!?])\s+", _text(en)) if s.strip()]
    out = []
    for i in range(min(k, max(len(zs), len(es)))):
        out.append(_short([zs[i] if i < len(zs) else "", es[i] if i < len(es) else ""]))
    return [p for p in out if p[0] or p[1]]


# --- the deck laid out by rule ----------------------------------------------------------------------------------
def fallback(spec: dict, no: str, assets: dict) -> list[dict]:
    """A complete deck from the lesson spec alone (no model call)."""
    live = "anim" if assets.get("anim") else "title"     # a lab page is white and busy: never the cover
    S = []
    notes = lambda *ps: [" ".join(_pair(p)[0] for p in ps)[:300], " ".join(_pair(p)[1] for p in ps)[:600]]  # noqa: E731
    pr, co, an, lab, mo, ev = (spec.get(k) or {} for k in ("problem", "concept", "animation", "lab", "model", "everyday"))
    S.append({"layout": "cover", "video": live, "kicker": [f"第 {no} 讲", f"Lesson {no}"], "title": _pair(spec.get("title")),
              "sub": _short(_pair(spec.get("goal")), 36, 90), "notes": notes(spec.get("title"), spec.get("goal"))})
    facts = [_short(_pair(g), 26, 70) for g in (pr.get("given") or [])][:3] or _sentences(*_pair(pr.get("text")), 3)
    if facts:
        while len(facts) < 3:
            facts.append(["", ""])
        S.append({"layout": "question", "tag": ["机器人问题", "Robot problem"], "title": _short(_pair(pr.get("title")), 30, 80),
                  "facts": facts, "notes": notes(pr.get("text"))})
    S.append({"layout": "section", "num": "01", "title": _pair(co.get("title")) if _pair(co.get("title"))[0] else ["概念", "Concepts"]})
    pts = [_short(_pair(p)) for p in co.get("points") or []]
    for i in range(0, len(pts), 3):
        S.append({"layout": "points", "title": _pair(co.get("title")), "points": pts[i:i + 3],
                  "foot": _short(_pair(co.get("formula")), 60, 90) if i == 0 and _pair(co.get("formula"))[0] else None,
                  "notes": notes(*pts[i:i + 3])})
    if assets.get("anim"):
        S.append({"layout": "figure", "title": _pair(an.get("title")) if _pair(an.get("title"))[0] else ["动画", "Animation"],
                  "visual": {"video": "anim"}, "caption": _short(_pair(an.get("question")), 50, 120), "notes": notes(an.get("question"))})
    for f in assets.get("figures") or []:
        S.append({"layout": "figure", "title": _short(f["title"], 30, 80), "visual": {"fig": f["name"]}, "notes": notes(f["title"])})
    sec = 2
    for n in spec.get("notes") or []:
        pts = _sentences(n.get("zh", ""), n.get("en", ""), 3)
        if pts:
            S.append({"layout": "points", "title": _short(_pair(n.get("heading")), 30, 80), "points": pts, "notes": notes(*pts)})
    ex = spec.get("example") or {}
    steps = [_short(_pair(s)) for s in ex.get("steps") or []]
    if steps:
        S.append({"layout": "section", "num": f"0{sec}", "title": ["例题", "Worked example"]})
        sec += 1
        S.append({"layout": "points", "title": _short(_pair(ex.get("question")), 34, 90), "points": steps[:3], "notes": notes(ex.get("question"))})
        for i in range(3, len(steps), 3):
            S.append({"layout": "points", "title": ["例题（续）", "Example (continued)"], "points": steps[i:i + 3]})
    if assets.get("lab"):
        S.append({"layout": "section", "num": f"0{sec}", "title": _pair(lab.get("title")) if _pair(lab.get("title"))[0] else ["虚拟实验", "Virtual lab"]})
        sec += 1
        S.append({"layout": "lab", "title": _pair(lab.get("title")), "shot": {"page": "lab"},
                  "tasks": [_short(_pair(t)) for t in (lab.get("tasks") or [])][:3], "notes": notes(lab.get("robot_scene"))})
    steps5 = [(["建模", "Model"], mo.get("assume")), (["求解", "Solve"], mo.get("solve")), (["检验", "Check"], mo.get("check")),
              (["修正", "Improve"], mo.get("improve"))]
    have = [(t, _pair(v)) for t, v in steps5 if _pair(v)[0]]
    if have:
        S.append({"layout": "chain", "title": ["建模求解", "Modelling"], "steps": [t for t, _ in have], "hot": [1] if len(have) > 1 else [],
                  "mark": ["本讲的模型", "this lesson's model"], "foot": _short(have[0][1], 60, 120)})
        for i in range(0, len(have), 3):
            S.append({"layout": "points", "title": ["建模求解", "Modelling"], "points": [_short(v) for _, v in have[i:i + 3]],
                      "notes": notes(*[v for _, v in have[i:i + 3]])})
    if _pair(ev.get("text"))[0]:
        S.append({"layout": "points", "tag": ["生活中的例子", "Everyday example"], "title": ["生活中的例子", "In everyday life"],
                  "points": _sentences(*_pair(ev.get("text")), 3) or [_short(_pair(ev.get("text")))], "notes": notes(ev.get("text"), ev.get("answer"))})
    if _pair(pr.get("answer"))[0]:
        pts = [_short(_pair(pr.get("answer")), 44, 120)] + [_short(_pair(mo.get(k)), 44, 120) for k in ("solve", "check") if _pair(mo.get(k))[0]]
        S.append({"layout": "points", "tag": ["回到问题", "Back to the problem"], "title": _short(_pair(pr.get("title")), 30, 80),
                  "points": pts[:3], "notes": notes(pr.get("answer"))})
    summ = [_short(_pair(s)) for s in spec.get("summary") or []][:3] or [["本讲小结", "Summary"]]
    S.append({"layout": "summary", "title": ["小结", "Summary"], "points": summ,
              "after": ["课后：在平台上完成练习、测验和实验报告", "After class: exercises, the quiz and the lab report on the platform"],
              "notes": notes(*summ)})
    return [s for s in S if s]


# --- checking a page so the engine can draw it -------------------------------------------------------------------
PAIRS = {"title", "kicker", "sub", "tag", "caption", "foot", "after", "label", "note", "mark"}


def clean_slide(s: Any, assets: dict) -> dict | None:
    if not isinstance(s, dict) or s.get("layout") not in LAYOUT_NAMES:
        return None
    s = dict(s)
    for k in list(s):
        if k in PAIRS and s[k] is not None:
            s[k] = _pair(s[k])
    for k in ("points", "facts", "tasks", "steps"):
        if k in s:
            s[k] = [_pair(x) for x in (s[k] or []) if x][: 3 if k in ("points", "facts", "tasks") else 9]
    if "notes" in s:
        s["notes"] = _pair(s["notes"])
    lay = s["layout"]
    clips = {"anim"} if assets.get("anim") else set()
    if assets.get("lab"):
        clips.add("lab")
    figs = {f["name"] for f in assets.get("figures") or []}

    def vis_ok(v: Any) -> bool:
        if not isinstance(v, dict):
            return False
        if "video" in v:
            return v["video"] in clips
        if "fig" in v:
            return v["fig"] in figs
        if "svg" in v:
            v["svg"] = safe_svg(str(v["svg"]))
            return v["svg"].startswith("<svg")
        return False
    if lay == "cover":
        if s.get("video") not in clips or s.get("video") == "lab":
            s["video"] = "anim" if "anim" in clips else "title"
        s.setdefault("kicker", ["", ""])
        s.setdefault("sub", ["", ""])
    if lay in ("split", "figure") and not vis_ok(s.get("visual")):
        if lay == "figure":
            return None
        s["layout"] = "points"
        s.pop("visual", None)
    if lay == "duo":
        for side in ("left", "right"):
            c = s.get(side)
            if not vis_ok(c):
                return None
            c["label"], c["note"] = _pair(c.get("label")), _pair(c.get("note"))
    if lay == "lab":
        if not assets.get("lab"):
            return None
        s["shot"] = {"page": "lab"}
    if lay == "question":
        while len(s.get("facts") or []) < 3:
            s.setdefault("facts", []).append(["", ""])
        s.setdefault("tag", ["问题", "Problem"])
    if lay in ("chain", "answer"):
        s.setdefault("foot", ["", ""])
        if s["foot"] is None:
            s["foot"] = ["", ""]
    if lay == "chain":
        s["hot"] = [int(i) for i in s.get("hot") or [] if str(i).isdigit() and int(i) < len(s.get("steps") or [])]
    if lay == "answer":
        rows = []
        for r in s.get("rows") or []:
            if isinstance(r, (list, tuple)) and len(r) == 2:
                rows.append([_pair(r[0]) if isinstance(r[0], (list, dict)) else str(r[0]), _pair(r[1])[0] if isinstance(r[1], (list, dict)) else str(r[1])])
        s["rows"] = rows[:5]
        if s.get("side") and isinstance(s["side"], dict):
            s["side"] = {"big": str(s["side"].get("big") or ""), "text": _pair(s["side"].get("text"))}
        else:
            s.pop("side", None)
    if lay == "bignum":
        s["nums"] = [{"n": str(n.get("n") or ""), "n_en": str(n.get("n_en") or ""), "label": _pair(n.get("label"))}
                     for n in s.get("nums") or [] if isinstance(n, dict) and n.get("n")][:3]
        if not s["nums"]:
            return None
    if lay == "timeline":
        ev = [{"year": int(v["year"]), "who": _pair(v.get("who")), "what": _pair(v.get("what"))}
              for v in s.get("events") or [] if isinstance(v, dict) and str(v.get("year", "")).lstrip("-").isdigit()][:6]
        if len(ev) < 2 or len({v["year"] for v in ev}) < len(ev):
            return None
        s["events"] = ev
    if lay == "summary":
        s.setdefault("after", ["", ""])
    if lay in ("points", "split", "summary") and not s.get("points"):
        return None
    if lay == "section":
        s["num"] = str(s.get("num") or "")
    if "title" not in s and lay not in ("cover",):
        s["title"] = ["", ""]
    if s.get("foot") is None:
        s.pop("foot", None)
    return s


def safe_svg(svg: str) -> str:
    """A diagram the designer drew: drawing only — no scripts, event handlers, links or embedded documents."""
    s = svg.strip()
    s = re.sub(r"(?is)<\s*(script|foreignObject|iframe|object|embed|style)\b.*?(</\s*\1\s*>|/>)", "", s)
    s = re.sub(r"(?is)<\s*/?\s*(script|foreignObject|iframe|object|embed|a)\b[^>]*>", "", s)
    s = re.sub(r"""(?is)\s+on[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", "", s)
    s = re.sub(r"""(?is)\s+(xlink:)?href\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", "", s)
    s = re.sub(r"(?i)javascript:", "", s)
    return s if s.lower().startswith("<svg") and s.lower().rstrip().endswith("</svg>") else ""


LAYOUT_NAMES = {"cover", "question", "section", "points", "split", "figure", "duo", "lab", "bignum", "chain", "timeline",
                "answer", "summary"}


async def design(ai, spec: dict, no: str, course: list[str], assets: dict, note: str = "") -> list[dict]:
    """The 课件设计师 lays the lesson out; pages that do not hold up are dropped, and the rule-made deck is used when too
    few remain."""
    avail = {"clips": (["anim (the lesson's animation, loops)"] if assets.get("anim") else [])
             + (["lab (the lesson's virtual lab — use it in a `lab` page)"] if assets.get("lab") else []),
             "figures": [{"name": f["name"], "title": f["title"]} for f in assets.get("figures") or []]}
    keep = {k: v for k, v in spec.items() if k not in ("figures_made", "sources", "factory_live", "assets")}
    prompt = (f"Course: {course[0]} / {course[1]}\nLesson {no}\n\nAvailable: {json.dumps(avail, ensure_ascii=False)}\n\n"
              f"The lesson (all text and numbers come from here):\n{json.dumps(keep, ensure_ascii=False)[:24000]}"
              + (f"\n\nThe teacher / course lead asked: {note}" if note else ""))
    try:
        data = await ai.json(system=DESIGNER, prompt=prompt, schema=SCHEMA, max_tokens=16000, fake=lambda: {"slides": []})
    except Exception as e:  # noqa: BLE001 - the rule-made deck still gives the lesson its courseware
        log.warning("deck design failed for %s: %s", no, e)
        data = {}
    pages = [p for p in (clean_slide(s, assets) for s in (data or {}).get("slides") or []) if p]
    if len(pages) < 8 or pages[0]["layout"] != "cover":
        if pages:
            log.info("deck design for %s too thin (%d usable pages): laid out by rule", no, len(pages))
        return fallback(spec, no, assets)
    if assets.get("lab") and not any(p["layout"] == "lab" for p in pages):
        lab = next(p for p in fallback(spec, no, assets) if p["layout"] == "lab")
        pages.insert(max(1, len(pages) - 2), lab)
    return pages


# --- building the file --------------------------------------------------------------------------------------------
TITLE_PAGE = ("<!doctype html><html><head><meta charset='utf-8'><style>html,body{margin:0;height:100%;background:#0b1424;overflow:hidden}"
              "svg{width:100%;height:100%}.r{transform-origin:800px 450px;animation:s 18s linear infinite}@keyframes s{to{transform:rotate(360deg)}}"
              "</style></head><body><svg viewBox='0 0 1600 900'><g class='r' fill='none' stroke-width='3'>"
              "<circle cx='800' cy='450' r='300' stroke='#2ec4b6' stroke-dasharray='14 18'/><circle cx='800' cy='450' r='200' stroke='#f2b705' "
              "stroke-dasharray='4 14'/><path d='M500 450 H1100 M800 150 V750' stroke='#4c8dff' opacity='.5'/></g></svg></body></html>")


def _anim_page(mp4: Path) -> str:
    b = base64.b64encode(mp4.read_bytes()).decode("ascii")
    return ("<!doctype html><html><head><meta charset='utf-8'><style>html,body{margin:0;height:100%;background:#000;overflow:hidden}"
            "video{width:100%;height:100%;object-fit:contain}</style></head><body>"
            f"<video autoplay loop muted playsinline src='data:video/mp4;base64,{b}'></video></body></html>")


def _engine(course_dir: Path):
    """A fresh copy of the engine, configured for this lesson's book folder."""
    with _LOCK:
        old = os.environ.get("WQ_COURSE_DIR")
        os.environ["WQ_COURSE_DIR"] = str(course_dir)
        try:
            name = f"wq_wc_slides_{abs(hash(str(course_dir)))}"
            sp = importlib.util.spec_from_file_location(name, HERE / "wc_slides.py")
            mod = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(mod)
            return mod
        finally:
            if old is None:
                os.environ.pop("WQ_COURSE_DIR", None)
            else:
                os.environ["WQ_COURSE_DIR"] = old


def build(out: Path, slides: list[dict], *, no: str, title: list[str], course: list[str], deck_id: str,
          anim: Path | None = None, lab_html: str | None = None, figures: list[dict] | None = None) -> Path:
    """Write the deck. figures: [{name, png: Path, title}]."""
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "a" / "b" / "c" / "book"
        course_dir = book / "course"
        (book / "img").mkdir(parents=True)
        labs = book / "src" / "zh" / "labs"
        labs.mkdir(parents=True)
        course_dir.mkdir(parents=True)
        import yaml
        (course_dir / "course.yaml").write_text(yaml.safe_dump({"name": list(course), "summary": list(course), "info": list(course),
                                                                "book": deck_id, "lessons": []}, allow_unicode=True),
                                                encoding="utf-8")
        for f in figures or []:
            try:
                Image.open(f["png"]).save(book / "img" / f"{f['name']}.webp", "WEBP", quality=88)
            except OSError:
                log.warning("figure %s could not be read", f["png"])
        (labs / "title.html").write_text(TITLE_PAGE, encoding="utf-8")
        if anim:
            (labs / "anim.html").write_text(_anim_page(anim), encoding="utf-8")
        if lab_html:
            (labs / "lab.html").write_text(lab_html if "</body>" in lab_html else lab_html + "</body>", encoding="utf-8")
        try:
            wc = _engine(course_dir)
        except SystemExit as e:      # the engine stops its command line this way; here it is an ordinary error
            raise RuntimeError(f"web deck engine: {e}") from None
        clips = {"title": {"page": "title"}}
        if anim:
            clips["anim"] = {"page": "anim"}
        if lab_html:
            clips["lab"] = {"page": "lab", "vw": 1400, "vh": 830}
        pages, used = [], []
        total = len(slides)
        for s in slides:
            s = dict(s)
            try:
                ctx = {"foot": wc.foot(no, len(used) + 1, total), "v": {}, "lang": "zh"}
                pages.append(wc.mark_frags(wc.LAYOUTS[s["layout"]](s, ctx), s["layout"]))
                used.append(s)
            except Exception as e:  # noqa: BLE001 - one bad page must not cost the whole deck
                log.warning("deck %s: page %s (%s) dropped: %s", no, len(used) + 1, s.get("layout"), e)
        out.parent.mkdir(parents=True, exist_ok=True)
        live = {m for p in pages for m in re.findall(r'data-live="([^"]+)"', p)}
        spec = {"lesson": no, "clips": {k: v for k, v in clips.items() if k in live}, "slides": used}
        return wc.build_deck(spec, {"title": list(title)}, pages, out, "zh")
