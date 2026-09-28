"""AI professor team course building (round 3, D30): course projects and the team's workflow.

A course project lives in <data>/projects/<id>/project.json; its files sit in a materials import
session that never expires. The workflow has four stages, each approved by the teacher:

  intake     the teacher describes the course and drops the materials
  materials  the librarian says what every file is; the lead asks at most five questions
  outline    the designer proposes chapters, lessons and a teaching calendar (quality-checked)
  lessons    one lesson at a time: author -> assessor -> reviewer (one rewrite) -> teacher -> published

Lessons are written when the teacher clicks "write the next lesson", or every day at a set hour
(pace "daily") as long as the previous lesson has been reviewed. Work can be stopped at any time.
Everything the teacher sees comes from the saved project, so leaving the page loses nothing.
"""
from __future__ import annotations

import asyncio
import html
import json
import logging
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from . import course_builder as cb
from . import materials as mt
from . import team
from .ai import ModelGateway
from .moodle import EngineError

log = logging.getLogger("wenquest.studio")

STAGES = ["intake", "materials", "outline", "lessons"]
TEXTBOOK_BUDGET = 28000   # characters of textbook pages per lesson
EXTRA_BUDGET = 8000       # chapter notes, lesson plan and slides per lesson
PAGE_MARK = re.compile(r"\[第(\d+)页\]\n")


def now() -> float:
    return time.time()


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def lang_keys(language: str) -> list[str]:
    return ["zh", "en"] if language == "both" else [language if language in ("zh", "en") else "zh"]


def disp(t: Any, lang: str = "zh") -> str:
    if isinstance(t, dict):
        return str(t.get(lang) or t.get("zh") or t.get("en") or "")
    return str(t or "")


def pages_of(text: str) -> dict[int, str]:
    """Split extracted PDF text back into pages ({page number: text})."""
    parts = PAGE_MARK.split(text or "")
    out: dict[int, str] = {}
    for i in range(1, len(parts) - 1, 2):
        out[int(parts[i])] = parts[i + 1].strip()
    return out


def similar(a: str, b: str) -> bool:
    """Two questions asking the same thing (character overlap)."""
    x, y = set(norm(a)), set(norm(b))
    return bool(x and y) and len(x & y) / min(len(x), len(y)) > 0.7


def norm(s: str) -> str:
    return re.sub(r"[^0-9a-z㐀-鿿]", "", (s or "").lower())


# --- storage ---------------------------------------------------------------------------------

class Projects:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, pid: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{12}", pid or ""):
            raise KeyError("bad project id")
        return self.root / pid / "project.json"

    def load(self, pid: str) -> dict:
        p = self.path(pid)
        if not p.exists():
            raise KeyError("no project")
        return json.loads(p.read_text())

    def save(self, proj: dict) -> None:
        proj["updated"] = now()
        p = self.path(proj["id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(proj, ensure_ascii=False))
        tmp.replace(p)

    def all(self) -> list[dict]:
        out = []
        for d in self.root.iterdir():
            try:
                out.append(json.loads((d / "project.json").read_text()))
            except (OSError, ValueError):
                continue
        return out


def new_project(owner: int, owner_name: str, import_id: str, description: str) -> dict:
    return {
        "id": new_id(), "owner": owner, "owner_name": owner_name, "created": now(), "updated": now(),
        "stage": "intake", "import_id": import_id,
        "requirements": {"notes": description.strip()[:4000]} if description.strip() else {},
        "materials": {"files": {}, "textbook": "", "toc": [], "book_title": "", "summary": ""},
        "questions": [], "messages": [], "outline": None,
        "course": {"id": 0, "shortname": "", "sections": {}, "attached": []},
        "pace": {"mode": "manual", "hour": 8, "tz": "Asia/Shanghai", "last_auto": ""},
        "busy": None,
    }


# --- summaries the agents read ----------------------------------------------------------------------

REQ_LABEL = {"course_title": "课程名称", "audience": "学生", "level": "程度", "language": "授课语言", "weeks": "周数",
             "sessions_per_week": "每周课次", "minutes_per_session": "每次分钟", "scope": "范围", "notes": "老师的说明"}


def summary(proj: dict, items: list[mt.Material] | None = None, with_outline: bool = True) -> str:
    r = proj["requirements"]
    lines = ["## Project state", f"Stage: {proj['stage']}"]
    lines.append("Requirements: " + ("; ".join(f"{k}={v}" for k, v in r.items() if v) or "(none yet)"))
    qs = [q for q in proj["questions"] if q["status"] == "open"]
    done = [q for q in proj["questions"] if q["status"] == "answered"]
    if done:
        lines.append("Answered questions: " + "; ".join(f"{q['text']} → {q['answer']}" for q in done))
    if qs:
        lines.append("Open questions: " + "; ".join(f"[{q['id']}] {q['text']}" for q in qs))
    files = proj["materials"]["files"]
    if files:
        by_id = {m.id: m for m in items or []}
        lines.append("Materials (id | file | role | chapters):")
        for fid, f in files.items():
            name = by_id[fid].path if fid in by_id else f.get("title", fid)
            lines.append(f"- {fid} | {name} | {team.ROLES.get(f['role'], f['role'])} | {f.get('chapters') or '-'}")
        if proj["materials"]["textbook"]:
            lines.append(f"Main textbook: {proj['materials']['textbook']} ({proj['materials'].get('book_title', '')})")
    o = proj.get("outline")
    if with_outline and o:
        lines.append(f"Outline: {disp(o['title'])}")
        for c in o["chapters"]:
            lines.append(f"- Chapter {c['no']} {disp(c['title'])}: " + "; ".join(
                f"[{l['id']}] {disp(l['title'])} ({l['status']})" for l in c["lessons"]))
    return "\n".join(lines)


# --- the orchestrator ---------------------------------------------------------------------------

class Studio:
    def __init__(self, projects: Projects, store: mt.Store, ai: ModelGateway, clean: Callable[[str], str]):
        self.projects = projects
        self.store = store
        self.ai = ai
        self.clean = clean
        self.tasks: dict[str, asyncio.Task] = {}
        self.locks: dict[str, asyncio.Lock] = {}

    # helpers ---------------------------------------------------------------------------------
    def items(self, proj: dict) -> list[mt.Material]:
        return self.store.materials(proj["import_id"], proj["owner"])

    def text(self, proj: dict, fid: str) -> str:
        return self.store.text(proj["import_id"], fid)

    def say(self, proj: dict, text: str, role: str = "lead", kind: str = "") -> None:
        proj["messages"].append({"id": new_id(), "role": role, "text": text, "ts": now(), "kind": kind})

    def is_busy(self, pid: str) -> bool:
        t = self.tasks.get(pid)
        return bool(t and not t.done())

    def run(self, proj: dict, label: str, coro_fn: Callable[[dict], Any]) -> None:
        """Run one piece of team work in the background; the project shows who is working on what."""
        pid = proj["id"]
        if self.is_busy(pid):
            raise EngineError("team_busy", "the team is already working on this course", 409)
        proj["busy"] = {"label": label, "since": now()}
        self.projects.save(proj)

        async def job():
            try:
                p = self.projects.load(pid)
                await coro_fn(p)
                p["busy"] = None
                self.projects.save(p)
            except asyncio.CancelledError:
                p = self.projects.load(pid)
                for c in (p.get("outline") or {}).get("chapters", []):
                    for les in c["lessons"]:
                        if les["status"] in ("writing", "reviewing"):
                            les["status"] = "planned" if not disp(les.get("content")) else "awaiting"
                p["busy"] = None
                self.say(p, "已停止。已经写好的内容都保留着。", "system")
                self.projects.save(p)
                raise
            except EngineError as exc:
                p = self.projects.load(pid)
                p["busy"] = None
                self.say(p, f"这一步没有完成（{exc.code}）。可以稍后再试，或者告诉我换一种做法。", "system", "error")
                self.projects.save(p)
            except Exception:
                log.exception("studio job failed for %s", pid)
                p = self.projects.load(pid)
                p["busy"] = None
                self.say(p, "这一步出错了（server_error），已记录。可以再试一次。", "system", "error")
                self.projects.save(p)

        self.tasks[pid] = asyncio.create_task(job())

    def stop(self, pid: str) -> bool:
        t = self.tasks.get(pid)
        if t and not t.done():
            t.cancel()
            return True
        return False

    def reconcile(self, proj: dict) -> dict:
        """After a restart, a project may still say 'busy' without anyone working on it."""
        if proj.get("busy") and not self.is_busy(proj["id"]):
            proj["busy"] = None
            for c in (proj.get("outline") or {}).get("chapters", []):
                for les in c["lessons"]:
                    if les["status"] in ("writing", "reviewing"):
                        les["status"] = "planned" if not disp(les.get("content")) else "awaiting"
            self.projects.save(proj)
        return proj

    # stage 1: materials ---------------------------------------------------------------------------
    async def study_materials(self, proj: dict) -> None:
        items = self.items(proj)
        files = [{"id": m.id, "path": m.path, "ext": m.ext, "size": m.size, "pages": m.pages,
                  "error": m.error, "excerpt": m.excerpt} for m in items]
        if files:
            data = await self.ai.json(system=team.LIBRARIAN, prompt=team.librarian_prompt(files, proj["requirements"].get("notes", "")),
                                      schema=team.librarian_schema(), max_tokens=8000,
                                      fake=lambda: fake_librarian(items))
            self.apply_librarian(proj, items, data)
            if proj["materials"]["textbook"]:
                await self.read_contents(proj)
        lib_q = (data.get("questions") if files and isinstance(data, dict) else None) or []
        q = await self.ai.json(system=team.LEAD, prompt=team.questions_prompt(summary(proj, items), lib_q[:3]),
                               schema=team.questions_schema(), max_tokens=3000,
                               fake=lambda: fake_questions(proj))
        q = q if isinstance(q, dict) else {}
        for k, v in (q.get("known") or {}).items():
            if v and k in REQ_LABEL and not proj["requirements"].get(k):
                proj["requirements"][k] = v
        proj["questions"] = [x for x in proj["questions"] if x["status"] != "open"]
        # The librarian's own questions (e.g. "two courses: which one?") always reach the teacher, first.
        asked = [x for x in lib_q[:3] if isinstance(x, dict) and x.get("text")]
        for x in q.get("questions") or []:
            if isinstance(x, dict) and x.get("text") and not any(similar(x["text"], y["text"]) for y in asked):
                asked.append(x)
        for x in asked[:5]:
            if isinstance(x, dict) and x.get("text"):
                proj["questions"].append({"id": new_id(), "text": str(x["text"])[:400],
                                          "options": [str(o)[:120] for o in (x.get("options") or [])][:6],
                                          "status": "open", "answer": "", "stage": "materials"})
        self.say(proj, str(q.get("message") or "资料看完了，请核对右边的资料清单。"), "lead", "report")
        proj["stage"] = "materials"

    def apply_librarian(self, proj: dict, items: list[mt.Material], data: dict) -> None:
        ids = {m.id for m in items}
        files = {}
        for f in (data.get("files") or []) if isinstance(data, dict) else []:
            if not isinstance(f, dict) or f.get("id") not in ids:
                continue
            role = f.get("role") if f.get("role") in team.ROLES else "other"
            files[f["id"]] = {"role": role, "chapters": [c for c in (f.get("chapters") or []) if isinstance(c, int) and 0 < c < 100],
                              "title": str(f.get("title") or "")[:200], "language": f.get("language") or "",
                              "confidence": f.get("confidence") or "high", "note": str(f.get("note") or "")[:300],
                              "by": "librarian"}
        for m in items:  # anything the model skipped keeps the rule-based guess
            files.setdefault(m.id, {"role": ROLE_OF_CATEGORY.get(m.category, "other"),
                                    "chapters": [m.chapter] if m.chapter else [], "title": "", "language": "",
                                    "confidence": "low", "note": "", "by": "rules"})
        # The teacher's own corrections always win.
        for fid, old in proj["materials"]["files"].items():
            if old.get("by") == "teacher" and fid in files:
                files[fid] = old
        proj["materials"]["files"] = files
        tb = data.get("main_textbook") if isinstance(data, dict) else ""
        if tb not in files or files.get(tb, {}).get("role") != "main_textbook":
            tb = next((fid for fid, f in files.items() if f["role"] == "main_textbook"), "")
        proj["materials"]["textbook"] = tb
        proj["materials"]["summary"] = str((data or {}).get("summary") or "")[:1500]
        course = (data or {}).get("course") or {}
        if course.get("title") and not proj["requirements"].get("course_title"):
            proj["requirements"]["course_title"] = str(course["title"])[:200]

    async def read_contents(self, proj: dict) -> None:
        """Read the main textbook's table of contents and find where each section starts."""
        fid = proj["materials"]["textbook"]
        pages = pages_of(self.text(proj, fid))
        if not pages:
            return
        toc_pages = find_toc_pages(pages)
        toc_text = "\n\n".join(f"[page {n}]\n{pages[n]}" for n in toc_pages)[:30000]
        data = await self.ai.json(system=team.TOC, prompt="Contents pages:\n" + toc_text, schema=team.toc_schema(),
                                  max_tokens=8000, fake=lambda: fake_toc(pages, toc_pages))
        chapters = []
        for c in (data.get("chapters") or []) if isinstance(data, dict) else []:
            if not isinstance(c, dict) or not isinstance(c.get("no"), int):
                continue
            secs = [{"no": str(s.get("no", "")).strip(), "title": str(s.get("title", "")).strip(),
                     "page": s.get("page") if isinstance(s.get("page"), int) else None}
                    for s in c.get("sections") or [] if isinstance(s, dict) and s.get("title")]
            chapters.append({"no": c["no"], "title": str(c.get("title", "")).strip(), "page": c.get("page"), "sections": secs})
        locate(chapters, pages, max(toc_pages) if toc_pages else 0)
        proj["materials"]["toc"] = chapters
        proj["materials"]["book_title"] = str((data or {}).get("book_title") or "")[:200]

    # stage 2: outline --------------------------------------------------------------------------
    async def apply_answers(self, proj: dict, items: list[mt.Material]) -> str:
        """Before designing: let the librarian bring the materials list in line with the teacher's answers."""
        answered = [q for q in proj["questions"] if q["status"] == "answered"]
        key = ";".join(q["id"] + q["answer"] for q in answered)
        if not answered or proj["materials"].get("answers_applied") == key or not proj["materials"]["files"]:
            return ""
        qa = "\n".join(f"- {q['text']} → {q['answer']}" for q in answered)
        data = await self.ai.json(system=team.LIBRARIAN_UPDATE, prompt=f"Answers:\n{qa}\n\n{summary(proj, items, False)}",
                                  schema=team.update_schema(), max_tokens=4000, fake=lambda: {"files": [], "note": ""})
        files = proj["materials"]["files"]
        changed = 0
        for f in (data.get("files") or []) if isinstance(data, dict) else []:
            cur = files.get(f.get("id") if isinstance(f, dict) else None)
            if not cur or cur.get("by") == "teacher" or f.get("role") not in team.ROLES:
                continue
            chapters = [c for c in f.get("chapters") or [] if isinstance(c, int) and 0 < c < 100]
            if (cur["role"], cur.get("chapters")) != (f["role"], chapters):
                cur.update(role=f["role"], chapters=chapters, by="librarian", note=str(f.get("why") or cur.get("note", ""))[:300])
                changed += 1
        tb = next((fid for fid, f in files.items() if f["role"] == "main_textbook"), "")
        if tb != proj["materials"]["textbook"]:
            proj["materials"]["textbook"], proj["materials"]["toc"] = tb, []
            if tb:
                await self.read_contents(proj)
        proj["materials"]["answers_applied"] = key
        return f"资料馆员按你的回答调整了 {changed} 份资料的身份。" if changed else ""

    async def design(self, proj: dict) -> None:
        items = self.items(proj)
        note = await self.apply_answers(proj, items)
        if note:
            self.say(proj, note, "system")
        keys = lang_keys(proj["requirements"].get("language", "zh"))
        toc = proj["materials"]["toc"]
        toc_text = "\n".join(f"Chapter {c['no']} {c['title']}\n" + "\n".join(f"  {s['no']} {s['title']}" for s in c["sections"])
                             for c in toc)
        extra = self.designer_extra(proj, items)
        feedback, outline = "", None
        for _ in range(2):  # one retry after the quality check (R17)
            data = await self.ai.json(system=team.DESIGNER, prompt=team.outline_prompt(summary(proj, items, False), toc_text, extra, feedback),
                                      schema=team.outline_schema(keys), max_tokens=12000,
                                      fake=lambda: fake_outline(proj, items, keys, lambda f: self.text(proj, f)))
            outline = self.build_outline(proj, data, keys)
            problems = check_outline(outline)
            if not problems:
                break
            feedback = "\n".join(problems)
        proj["outline"] = outline
        problems = check_outline(outline)
        n = sum(len(c["lessons"]) for c in outline["chapters"])
        last_week = max([les["week"] or 0 for c in outline["chapters"] for les in c["lessons"]] or [0])
        cal = f"教学日历排到第 {last_week} 周" if last_week else "还没排周次（可以在右边给每次课填上周次）"
        msg = (f"大纲草稿出来了：{len(outline['chapters'])} 章、{n} 次课，{cal}。请在右边“大纲与日历”里看，"
               "可以直接改名、调顺序、删课或加课。没问题就点“大纲定稿”。")
        if problems:
            msg += "\n\n质量检查还有几处拿不准，请特别看一下：\n" + "\n".join(f"· {p}" for p in problems[:6])
        self.say(proj, msg, "lead", "report")
        proj["stage"] = "outline"

    def designer_extra(self, proj: dict, items: list[mt.Material]) -> str:
        files = proj["materials"]["files"]
        parts = []
        for m in items:
            f = files.get(m.id, {})
            if f.get("role") in ("syllabus", "calendar"):
                parts.append(f"## {team.ROLES[f['role']]}: {m.path}\n{self.text(proj, m.id)[:5000]}")
        if not proj["materials"]["toc"]:
            chapters = sorted({c for f in files.values() for c in f.get("chapters") or []})
            for ch in chapters:
                parts.append(f"## Chapter {ch} materials")
                for m in items:
                    f = files.get(m.id, {})
                    if ch in (f.get("chapters") or []) and f.get("role") in ("notes", "slides", "lesson_plan", "aux_textbook"):
                        text = self.text(proj, m.id)
                        heads = "; ".join(mt.headings(text, ch))
                        outline = " | ".join(mt.slide_outline(text))
                        parts.append(f"- {team.ROLES[f['role']]} {m.path}"
                                     + (f"\n  Section headings: {heads}" if heads else "")
                                     + (f"\n  Slide titles in order (▶ marks a new lesson in the deck): {outline}" if outline else "")
                                     + (f"\n  Beginning: {' '.join(text[:1200].split())}" if not (heads or outline) else ""))
        return "\n".join(parts)

    def build_outline(self, proj: dict, data: dict, keys: list[str]) -> dict:
        T = lambda v: {k: str((v or {}).get(k) or "").strip() if isinstance(v, dict) else str(v or "").strip() for k in keys}  # noqa: E731
        data = data if isinstance(data, dict) else {}
        chapters = []
        for c in data.get("chapters") or []:
            if not isinstance(c, dict):
                continue
            no = mt.as_int(c.get("no")) or len(chapters) + 1
            lessons = []
            for les in c.get("lessons") or []:
                if not isinstance(les, dict):
                    continue
                lessons.append({"id": new_id(), "title": T(les.get("title")), "goal": T(les.get("goal")),
                                "week": mt.as_int(les.get("week")) or 0,
                                "sections": [str(s)[:10] for s in les.get("sections") or []][:6],
                                "status": "planned", "content": {}, "exercises": {}, "answers": {},
                                "review": None, "notes": "", "cmids": [], "error": ""})
            chapters.append({"id": new_id(), "no": no, "title": T(c.get("title")), "summary": T(c.get("summary")),
                             "lessons": lessons})
        return {"title": T(data.get("title")), "summary": T(data.get("summary")), "languages": "both" if len(keys) == 2 else keys[0],
                "chapters": chapters, "calendar_note": str(data.get("calendar_note") or "")[:1000]}

    # stage 3: lessons ---------------------------------------------------------------------------
    def next_lesson(self, proj: dict) -> tuple[dict, dict] | None:
        for c in (proj.get("outline") or {}).get("chapters", []):
            for les in c["lessons"]:
                if les["status"] in ("planned", "failed"):
                    return c, les
        return None

    def awaiting(self, proj: dict) -> int:
        return sum(1 for c in (proj.get("outline") or {}).get("chapters", []) for les in c["lessons"] if les["status"] == "awaiting")

    def find_lesson(self, proj: dict, lid: str) -> tuple[dict, dict]:
        for c in (proj.get("outline") or {}).get("chapters", []):
            for les in c["lessons"]:
                if les["id"] == lid:
                    return c, les
        raise EngineError("not_found", "no such lesson", 404)

    def sources(self, proj: dict, chapter: dict, les: dict, items: list[mt.Material]) -> str:
        """The textbook pages of the lesson's sections, then the chapter's own notes, plan and slides."""
        out, budget = [], TEXTBOOK_BUDGET
        tb = proj["materials"]["textbook"]
        by_id = {m.id: m for m in items}
        if tb and proj["materials"]["toc"]:
            pages = pages_of(self.text(proj, tb))
            name = proj["materials"].get("book_title") or (by_id[tb].name if tb in by_id else "textbook")
            wanted = set(les.get("sections") or [])
            ranges = []
            for c in proj["materials"]["toc"]:
                for s in c["sections"]:
                    if s["no"] in wanted and s.get("start"):
                        ranges.append((s["start"], s.get("end") or s["start"] + 6))
                if not wanted and c["no"] == chapter["no"] and c.get("start"):
                    ranges.append((c["start"], c.get("end") or c["start"] + 8))
            for a, b in ranges:
                for n in range(a, min(b, a + 14) + 1):
                    t = pages.get(n, "")
                    if not t or budget <= 0:
                        continue
                    t = t[:budget]
                    out.append(f"<<< {name}，第{n}页\n{t}\n>>>")
                    budget -= len(t)
        # Without textbook pages, the chapter's own slides and notes are the main source: give them more room.
        budget = EXTRA_BUDGET if out else TEXTBOOK_BUDGET
        files = proj["materials"]["files"]
        for role in ("notes", "lesson_plan", "slides", "aux_textbook"):
            for fid, f in files.items():
                if f["role"] == role and chapter["no"] in (f.get("chapters") or []) and budget > 0 and fid in by_id:
                    t = self.text(proj, fid)[:budget]
                    if t:
                        out.append(f"<<< {by_id[fid].name}（{team.ROLES[role]}）\n{t}\n>>>")
                        budget -= len(t)
        return "\n".join(out) or "(no source pages were found for this lesson; say so and teach from the goal carefully)"

    def lesson_context(self, proj: dict, chapter: dict, les: dict, items: list[mt.Material]) -> str:
        lang = proj["outline"]["languages"]
        files = proj["materials"]["files"]
        media = [m.name for m in items if files.get(m.id, {}).get("role") in ("media", "lab")
                 and chapter["no"] in (files[m.id].get("chapters") or [])]
        r = proj["requirements"]
        return (f"Course: {disp(proj['outline']['title'])}\nChapter {chapter['no']}: {disp(chapter['title'])}\n"
                f"Lesson: {disp(les['title'])}\nGoal: {disp(les['goal'])}\nTextbook sections: {', '.join(les.get('sections') or []) or '-'}\n"
                f"Students: {r.get('audience') or 'university students'}; level: {r.get('level') or '-'}\n"
                f"Write in: {team.LANG_NAME.get(lang, 'Simplified Chinese')}\n"
                f"Animations and labs available for this chapter: {', '.join(media) or 'none'}")

    async def write_lesson(self, proj: dict, lid: str, teacher_note: str = "") -> None:
        chapter, les = self.find_lesson(proj, lid)
        items = self.items(proj)
        keys = lang_keys(proj["outline"]["languages"])
        ctx = self.lesson_context(proj, chapter, les, items)
        src = self.sources(proj, chapter, les, items)
        les["status"], les["error"] = "writing", ""
        if teacher_note:
            les["notes"] = teacher_note
        proj["busy"] = {"label": f"主讲教授正在写：{disp(les['title'])}", "since": now()}
        self.projects.save(proj)
        notes = teacher_note
        review = None
        for attempt in range(2):
            data = await self.ai.json(system=team.AUTHOR, prompt=team.lesson_prompt(ctx, src, notes),
                                      schema=team.lesson_schema(keys), max_tokens=16000 if len(keys) == 2 else 9000,
                                      fake=lambda: fake_lesson(les, src, keys))
            content = cb.norm_text((data or {}).get("content") if isinstance(data, dict) else None, keys)
            les["content"] = {k: self.clean(v) for k, v in content.items()}
            if not any(les["content"].values()):
                raise EngineError("ai_bad_output", "empty lesson", 502)
            proj["busy"] = {"label": f"习题与测评正在出题：{disp(les['title'])}", "since": now()}
            self.projects.save(proj)
            ex = await self.ai.json(system=team.ASSESSOR, prompt=f"{ctx}\n\nLesson:\n{disp(les['content'])[:12000]}\n\nSources:\n{src[:12000]}",
                                    schema=team.exercises_schema(keys), max_tokens=6000, fake=lambda: fake_exercises(keys))
            les["exercises"] = {k: self.clean(v) for k, v in cb.norm_text((ex or {}).get("questions"), keys).items()}
            les["answers"] = {k: self.clean(v) for k, v in cb.norm_text((ex or {}).get("answers"), keys).items()}
            les["status"] = "reviewing"
            proj["busy"] = {"label": f"审稿人正在核对：{disp(les['title'])}", "since": now()}
            self.projects.save(proj)
            rv = await self.ai.json(system=team.REVIEWER,
                                    prompt=team.review_prompt(ctx, disp(les["content"])[:20000],
                                                              disp(les["exercises"])[:4000] + "\n" + disp(les["answers"])[:4000], src),
                                    schema=team.review_schema(), max_tokens=3000,
                                    fake=lambda: {"verdict": "pass", "issues": [], "summary": "与原文一致。"})
            review = {"verdict": rv.get("verdict") if rv.get("verdict") in ("pass", "revise") else "pass",
                      "issues": [i for i in rv.get("issues") or [] if isinstance(i, dict) and i.get("text")][:10],
                      "summary": str(rv.get("summary") or "")[:800], "round": attempt + 1}
            if review["verdict"] == "pass":
                break
            notes = (teacher_note + "\n" if teacher_note else "") + "审稿人意见：\n" + "\n".join(f"- {i['text']}" for i in review["issues"])
            les["status"] = "writing"
            proj["busy"] = {"label": f"主讲教授按审稿意见重写：{disp(les['title'])}", "since": now()}
            self.projects.save(proj)
        les["review"] = review
        les["status"] = "awaiting"
        les["written"] = now()
        verdict = "审稿通过" if review and review["verdict"] == "pass" else "审稿人仍有意见，请重点看审稿意见"
        self.say(proj, f"《{disp(les['title'])}》写好了（{verdict}），请在右边“课时进度”里审阅：通过就发布给学生，或者告诉我怎么改。", "lead", "lesson")

    # talking with the teacher ------------------------------------------------------------------
    async def chat(self, proj: dict, text: str) -> None:
        items = self.items(proj)
        history = [m for m in proj["messages"] if m["role"] in ("teacher", "lead")]
        data = await self.ai.json(system=team.LEAD, prompt=team.chat_prompt(summary(proj, items), history[:-1], text),
                                  schema=team.chat_schema(), max_tokens=3000,
                                  fake=lambda: {"reply": "好的，记下了。", "actions": []})
        data = data if isinstance(data, dict) else {}
        follow_up = self.apply_actions(proj, data.get("actions") or [])
        self.say(proj, str(data.get("reply") or "好的。"), "lead")
        self.projects.save(proj)
        if follow_up:
            await follow_up(proj)

    def apply_actions(self, proj: dict, actions: list[dict]):
        """Record what the teacher decided. Returns follow-up work (at most one) to run now."""
        follow_up = None
        files = proj["materials"]["files"]
        for a in actions[:10]:
            if not isinstance(a, dict):
                continue
            kind = a.get("type")
            if kind == "answer_question":
                q = next((q for q in proj["questions"] if q["id"] == a.get("id")), None)
                if q and a.get("answer"):
                    q["answer"], q["status"] = str(a["answer"])[:500], "answered"
            elif kind == "set_requirement" and a.get("key") in REQ_LABEL and a.get("value") not in (None, ""):
                val = str(a["value"])[:1000]
                if a["key"] == "language":
                    val = {"中文": "zh", "英文": "en", "中英双语": "both", "双语": "both"}.get(val, val)
                    val = val if val in ("zh", "en", "both") else "zh"
                proj["requirements"][a["key"]] = val
            elif kind == "set_role" and a.get("file_id") in files and a.get("role") in team.ROLES:
                files[a["file_id"]].update(role=a["role"], by="teacher", confidence="high")
            elif kind == "set_textbook" and a.get("file_id") in files:
                for f in files.values():
                    if f["role"] == "main_textbook":
                        f["role"] = "aux_textbook"
                files[a["file_id"]].update(role="main_textbook", by="teacher", confidence="high")
                proj["materials"]["textbook"] = a["file_id"]
                proj["materials"]["toc"] = []
                follow_up = follow_up or self.read_contents
            elif kind == "set_pace" and a.get("mode") in ("manual", "daily"):
                proj["pace"]["mode"] = a["mode"]
                if isinstance(a.get("hour"), int) and 0 <= a["hour"] <= 23:
                    proj["pace"]["hour"] = a["hour"]
            elif kind == "revise_lesson" and proj.get("outline") and not follow_up:
                try:
                    _, les = self.find_lesson(proj, str(a.get("lesson_id")))
                    note = str(a.get("note") or "")[:2000]
                    follow_up = lambda p, lid=les["id"], n=note: self.write_lesson(p, lid, n)  # noqa: E731
                except EngineError:
                    pass
            elif kind == "write_next" and proj["stage"] == "lessons" and not follow_up:
                nxt = self.next_lesson(proj)
                if nxt:
                    follow_up = lambda p, lid=nxt[1]["id"]: self.write_lesson(p, lid)  # noqa: E731
            elif kind == "proceed" and proj["stage"] == "materials" and not follow_up:
                follow_up = self.design
        return follow_up

    # the daily pace --------------------------------------------------------------------------
    async def tick(self) -> None:
        for proj in self.projects.all():
            try:
                pace = proj.get("pace") or {}
                if proj.get("stage") != "lessons" or pace.get("mode") != "daily" or self.is_busy(proj["id"]):
                    continue
                local = datetime.now(ZoneInfo(pace.get("tz") or "Asia/Shanghai"))
                today = local.strftime("%Y-%m-%d")
                if pace.get("last_auto") == today or local.hour < int(pace.get("hour", 8)):
                    continue
                if self.awaiting(proj) or not self.next_lesson(proj):
                    continue  # the previous lesson waits for the teacher: do not pile up
                _, les = self.next_lesson(proj)
                proj["pace"]["last_auto"] = today
                self.run(proj, f"每日自动：写《{disp(les['title'])}》", lambda p, lid=les["id"]: self.write_lesson(p, lid))
            except Exception:
                log.exception("daily pace failed for %s", proj.get("id"))

    async def scheduler(self) -> None:
        while True:
            await asyncio.sleep(300)
            await self.tick()


ROLE_OF_CATEGORY = {"syllabus": "syllabus", "calendar": "calendar", "lesson_plan": "lesson_plan", "notes": "notes",
                    "slides": "slides", "homework": "homework", "quiz": "exam", "answer_key": "answer_key", "lab": "lab",
                    "rubric": "rubric", "media": "media", "other": "other"}


# --- reading a textbook's contents ------------------------------------------------------------

def find_toc_pages(pages: dict[int, str]) -> list[int]:
    """Pages near the front that hold the table of contents."""
    first = sorted(pages)[:40]
    start = next((n for n in first if re.search(r"\b(contents|table of contents)\b|目\s*录", pages[n][:400], re.I)), None)
    if start is None:
        # No heading: the densest run of lines ending in page numbers.
        scored = [(sum(1 for ln in pages[n].splitlines() if re.search(r"\s\d{1,4}\s*$", ln)), n) for n in first]
        best = max(scored, default=(0, 0))
        if best[0] < 8:
            return []
        start = best[1]
    out = [start]
    for n in range(start + 1, start + 12):
        lines = pages.get(n, "").splitlines()
        if lines and sum(1 for ln in lines if re.search(r"\s\d{1,4}\s*$", ln)) >= max(4, len(lines) // 4):
            out.append(n)
        else:
            break
    return out


def locate(chapters: list[dict], pages: dict[int, str], after: int) -> None:
    """Find the PDF page where each chapter and section starts (searching the titles after the contents)."""
    order = [n for n in sorted(pages) if n > after]
    normed = {n: norm(pages[n]) for n in order}
    pos = 0
    marks: list[tuple[dict, int]] = []
    offsets = []

    def find(title: str, number: str = "") -> int | None:
        nonlocal pos
        key = norm(title)
        if len(key) < 4:
            return None
        for i in range(pos, len(order)):
            n = order[i]
            if key in normed[n] and (not number or norm(number) in normed[n]):
                pos = i
                return n
        return None

    for c in chapters:
        c["start"] = find(c["title"]) or None
        if c["start"]:
            marks.append((c, c["start"]))
            if c.get("page"):
                offsets.append(c["start"] - c["page"])
        for s in c["sections"]:
            s["start"] = find(s["title"], s["no"]) or find(s["title"])
            if s["start"]:
                marks.append((s, s["start"]))
                if s.get("page"):
                    offsets.append(s["start"] - s["page"])
    # Printed page + typical offset for anything the search missed.
    off = sorted(offsets)[len(offsets) // 2] if offsets else None
    for c in chapters:
        for x in [c, *c["sections"]]:
            if not x.get("start") and off is not None and x.get("page"):
                x["start"] = x["page"] + off
    flat = [x for c in chapters for x in [c, *c["sections"]] if x.get("start")]
    flat.sort(key=lambda x: x["start"])
    for a, b in zip(flat, flat[1:] + [None]):
        a["end"] = max(a["start"], (b["start"] - 1) if b else a["start"] + 10)
    for c in chapters:
        if c["sections"] and c.get("start"):
            last = max((s.get("end") or 0) for s in c["sections"])
            c["end"] = max(c.get("end") or c["start"], last)


# --- quality check (R17) --------------------------------------------------------------------------

def check_outline(o: dict) -> list[str]:
    problems = []
    if not o["chapters"]:
        return ["没有任何章节"]
    if mt.generic_title(disp(o["title"])):
        problems.append(f"课程名称“{disp(o['title'])}”没有说出课程内容")
    for c in o["chapters"]:
        t = disp(c["title"])
        if mt.generic_title(t):
            problems.append(f"第 {c['no']} 章的名称“{t}”只有编号，没有内容")
        if not 1 <= len(c["lessons"]) <= 6:
            problems.append(f"第 {c['no']} 章有 {len(c['lessons'])} 次课（应为 1–6 次）")
        for les in c["lessons"]:
            lt = disp(les["title"])
            core = re.sub(r"^\s*\d+(\.\d+)*\s*", "", lt)
            if not core or mt.generic_title(lt) or not mt._heading_title(core):
                problems.append(f"课时名称“{lt}”像算式、答案或空名字")
    return problems


# --- offline (fake model) behaviour: rules instead of a model, for tests and local demos -----------

def fake_librarian(items: list[mt.Material]) -> dict:
    files, textbook = [], ""
    for m in items:
        role = ROLE_OF_CATEGORY.get(m.category, "other")
        if m.ext == ".pdf" and m.pages >= 80 and re.search(r"contents|目\s*录", m.excerpt[:3000], re.I):
            role, textbook = "main_textbook", textbook or m.id
        files.append({"id": m.id, "role": role, "chapters": [m.chapter] if m.chapter else [], "title": Path(m.name).stem,
                      "language": "zh" if re.search(r"[㐀-鿿]", m.excerpt) else "en", "confidence": "high"})
    return {"course": {"title": "", "subject": "", "language": ""}, "main_textbook": textbook, "files": files,
            "summary": "", "questions": []}


def fake_questions(proj: dict) -> dict:
    tb = proj["materials"]["textbook"]
    n = len(proj["materials"]["files"])
    return {"message": f"资料看完了：共 {n} 份" + ("，已找到主教材" if tb else "，没有找到单独的主教材，按各章讲义来建") + "。有几件事想先确认：",
            "questions": [{"text": "这门课一学期上几周、每周几次课？", "options": ["16 周，每周 2 次", "16 周，每周 1 次", "8 周，每周 2 次"]},
                          {"text": "授课语言？", "options": ["中文", "英文", "中英双语"]}],
            "known": {}}


def fake_toc(pages: dict[int, str], toc_pages: list[int]) -> dict:
    chapters = []
    text = "\n".join(pages[n] for n in toc_pages)
    for line in text.splitlines():
        m = re.match(r"^\s*(?:Chapter\s+(\d+)|第\s*(\d+)\s*章)\s*[:：.]?\s*(\S.*?)\s*(\d+)?\s*$", line, re.I)
        if m:
            chapters.append({"no": int(m.group(1) or m.group(2)), "title": m.group(3), "page": int(m.group(4)) if m.group(4) else None, "sections": []})
            continue
        h = mt.HEADING.match(line)
        if h and chapters and int(h.group(1)) == chapters[-1]["no"]:
            pg = re.search(r"(\d+)\s*$", line)
            chapters[-1]["sections"].append({"no": f"{h.group(1)}.{h.group(2)}", "title": h.group(3).strip(),
                                             "page": int(pg.group(1)) if pg else None})
    return {"book_title": "", "chapters": chapters}


def fake_outline(proj: dict, items: list[mt.Material], keys: list[str], text_of: Callable[[str], str]) -> dict:
    """Offline designer: textbook contents if there is one, otherwise each chapter's own materials
    (numbered headings, or the slide deck's titles), using the roles in the materials list."""
    T = lambda s: {k: s for k in keys}  # noqa: E731
    chapters, week = [], 1
    toc = proj["materials"]["toc"]
    title = proj["requirements"].get("course_title") or proj["materials"].get("book_title") or ""
    if toc:
        for c in toc:
            lessons = []
            for sec in c["sections"][:6]:
                lessons.append({"title": T(f"{sec['no']} {sec['title']}"), "goal": T(f"掌握 {sec['title']}"), "week": week, "sections": [sec["no"]]})
                week += 1
            chapters.append({"no": c["no"], "title": T(c["title"]), "summary": T(""), "lessons": lessons})
        return {"title": T(title or "课程"), "summary": T(""), "chapters": chapters}
    files = proj["materials"]["files"]
    by_id = {m.id: m for m in items}
    use = ("notes", "slides", "lesson_plan", "aux_textbook")
    numbers = sorted({c for fid, f in files.items() if f["role"] in use for c in f.get("chapters") or []})
    for ch in numbers:
        mine = [fid for fid, f in files.items() if f["role"] in use and ch in (f.get("chapters") or []) and fid in by_id]
        mine.sort(key=lambda fid: use.index(files[fid]["role"]))
        text = text_of(mine[0]) if mine else ""
        name = mt.section_title_for(ch, [by_id[f] for f in mine], text_of)
        first = [ln.strip() for ln in re.sub(r"\[(幻灯片|第)\d+页?\]", "\n", text[:400]).splitlines() if ln.strip()]
        if first and re.match(rf"^(chapter|unit)\s*0*{ch}\b", first[0], re.I):
            # The title slide may wrap the chapter name over several lines; stop at the course line.
            name = first[0]
            for ln in first[1:4]:
                if re.search(r"\d{3,}|https?:|download|image|credit|slides?|standard|physics for", ln, re.I):
                    break
                name += " " + ln
        heads = mt.headings(text, ch)
        outline = mt.slide_outline(text)
        if heads:
            topics = heads
        elif any(t.startswith("▶") for t in outline):
            topics = [re.sub(r"^▶\s*in this lesson you will…?\s*", "", t, flags=re.I).replace("•", "").strip(" ;") for t in outline if t.startswith("▶")]
        else:
            topics = [t for t in outline[1:] if not re.match(rf"^(chapter|unit)\s*0*{ch}\b", t, re.I)]
        topics = [t for t in topics if t][:12]
        size = max(1, -(-len(topics) // 6))  # at most 6 lessons: group neighbouring topics
        groups = [topics[i:i + size] for i in range(0, len(topics), size)] or [[name]]
        lessons = []
        for g in groups:
            lessons.append({"title": T(" · ".join(g)[:80]), "goal": T(""), "week": week, "sections": []})
            week += 1
        chapters.append({"no": ch, "title": T(name), "summary": T(""), "lessons": lessons})
    if not chapters:  # nothing chapter-shaped: fall back to the old rule plan
        plan = mt.rule_plan([m for m in items if m.category != "other"], text_of)
        chapters = [{"no": c["chapter"], "title": T(c["title"]), "summary": T(""),
                     "lessons": [{"title": T(x["title"]), "goal": T(""), "week": 0, "sections": []} for x in c["lessons"]]}
                    for c in plan["sections"]]
        title = title or plan["title"]
    return {"title": T(title or mt.course_title(items, text_of)), "summary": T(""), "chapters": chapters}


def fake_lesson(les: dict, src: str, keys: list[str]) -> dict:
    m = re.search(r"<<< (.+?)\n(.{0,400})", src, re.S)
    cite = f"<p>{html.escape(' '.join(m.group(2).split()))}（参考：{html.escape(m.group(1))}）</p>" if m else ""
    body = (f"<h3>实际问题</h3><p>机器人问题（示例）。</p><h3>概念</h3>{cite}<h3>动画</h3><p>动画说明。</p>"
            f"<h3>虚拟实验</h3><p>实验说明。</p><h3>建模求解</h3><p>求解（示例）。</p>")
    return {"content": {k: body for k in keys}, "summary": disp(les["title"])}


def fake_exercises(keys: list[str]) -> dict:
    return {"questions": {k: "<ol><li>练习一</li><li>练习二</li></ol>" for k in keys},
            "answers": {k: "<ol><li>答案一</li><li>答案二</li></ol>" for k in keys}}
