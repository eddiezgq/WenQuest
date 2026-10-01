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
from .production import spec as sp
from .ai import ModelGateway
from .moodle import EngineError
from .lectures import LectureMixin
from .lead import LeadMixin, chapter_confirmed

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
        """Write the project. The conversation, proposals and answered questions are merged with what is on disk:
        the course lead replies while a job holds an older copy of the project (round 5), and neither may lose the
        other's messages."""
        proj["updated"] = now()
        p = self.path(proj["id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            try:
                disk = json.loads(p.read_text())
            except ValueError:
                disk = {}
            merge_side(proj, disk)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(proj, ensure_ascii=False))
        tmp.replace(p)

    def remove(self, pid: str) -> None:
        """Delete a project with all its materials and lesson files."""
        import shutil
        shutil.rmtree(self.path(pid).parent, ignore_errors=True)

    def all(self) -> list[dict]:
        out = []
        for d in self.root.iterdir():
            try:
                out.append(json.loads((d / "project.json").read_text()))
            except (OSError, ValueError):
                continue
        return out


def merge_side(proj: dict, disk: dict) -> None:
    seen = {m["id"] for m in proj.get("messages") or []}
    extra = [m for m in disk.get("messages") or [] if m["id"] not in seen]
    if extra:
        proj["messages"] = sorted((proj.get("messages") or []) + extra, key=lambda m: m.get("ts") or 0)
    rank = {"open": 0, "superseded": 1, "cancelled": 2, "done": 3}
    mine = {x["id"]: x for x in proj.get("proposals") or []}
    for x in disk.get("proposals") or []:
        if x["id"] not in mine or rank.get(x["status"], 0) > rank.get(mine[x["id"]]["status"], 0):
            mine[x["id"]] = x
    if mine:
        proj["proposals"] = sorted(mine.values(), key=lambda x: x.get("created") or 0)[-60:]
    qs = {q["id"]: q for q in disk.get("questions") or []}
    for q in proj.get("questions") or []:
        d = qs.get(q["id"])
        if d and q["status"] == "open" and d["status"] != "open":
            q.update(status=d["status"], answer=d.get("answer", ""))


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

class Studio(LeadMixin, LectureMixin):
    def __init__(self, projects: Projects, store: mt.Store, ai: ModelGateway, clean: Callable[[str], str]):
        self.projects = projects
        self.store = store
        self.ai = ai
        self.clean = clean
        self.tasks: dict[str, asyncio.Task] = {}
        self.locks: dict[str, asyncio.Lock] = {}
        self.animator_url = ""      # the animation renderer; empty = no videos
        self.animator_timeout = 600.0
        self.labcheck_url = ""      # the lab checker (headless browser); empty = no virtual labs
        self.labcheck_timeout = 150.0
        self.voice_url = ""         # the voice service (speech synthesis / recognition); empty = no lecture videos
        # 相似度检查 is off only for the offline stand-in model (its answers are fixed examples by design)
        self.copy_check = getattr(ai, "provider", "") != "fake"

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
        await self.read_scanned(proj)
        items = self.items(proj)
        textbook_note = ""
        files = [{"id": m.id, "path": m.path, "ext": m.ext, "size": m.size, "pages": m.pages,
                  "error": m.error, "excerpt": m.excerpt} for m in items]
        if files:
            data = await self.ai.json(system=team.LIBRARIAN, prompt=team.librarian_prompt(files, proj["requirements"].get("notes", "")),
                                      schema=team.librarian_schema(), max_tokens=8000,
                                      fake=lambda: fake_librarian(items))
            self.apply_librarian(proj, items, data)
            textbook_note = self.apply_teacher_textbook(proj, items)
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
        proj["questions"] = [x for x in proj["questions"] if x["status"] != "open" or x.get("kind") == "textbook"]
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
        message = str(q.get("message") or "资料看完了，请核对右边的资料清单。")
        if files and textbook_note:
            message = textbook_note + "\n\n" + message
        self.say(proj, message, "lead", "report")
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

    async def classify_new(self, proj: dict) -> None:
        """Files added after the materials were settled: the librarian sorts just those, then the lead says
        what they change — lessons not written yet use them; written ones are named for a possible rewrite."""
        await self.read_scanned(proj)
        items = self.items(proj)
        known = proj["materials"]["files"]
        new = [m for m in items if m.id not in known]
        if not new:
            return
        files = [{"id": m.id, "path": m.path, "ext": m.ext, "size": m.size, "pages": m.pages,
                  "error": m.error, "excerpt": m.excerpt} for m in new]
        data = await self.ai.json(system=team.LIBRARIAN, prompt=team.librarian_prompt(files, proj["requirements"].get("notes", "")),
                                  schema=team.librarian_schema(), max_tokens=6000, fake=lambda: fake_librarian(new))
        data = data if isinstance(data, dict) else {}
        ids = {m.id for m in new}
        got = {f["id"]: f for f in data.get("files") or [] if isinstance(f, dict) and f.get("id") in ids}
        for m in new:
            f = got.get(m.id)
            if f:
                role = f.get("role") if f.get("role") in team.ROLES else "other"
                known[m.id] = {"role": role, "chapters": [c for c in (f.get("chapters") or []) if isinstance(c, int) and 0 < c < 100],
                               "title": str(f.get("title") or "")[:200], "language": f.get("language") or "",
                               "confidence": f.get("confidence") or "high", "note": str(f.get("note") or "")[:300], "by": "librarian"}
            else:
                known[m.id] = {"role": ROLE_OF_CATEGORY.get(m.category, "other"), "chapters": [m.chapter] if m.chapter else [],
                               "title": "", "language": "", "confidence": "low", "note": "", "by": "rules"}
        if not proj["materials"]["textbook"]:
            tb = next((fid for fid in ids if known[fid]["role"] == "main_textbook"), "")
            if tb:
                proj["materials"]["textbook"] = tb
        note = self.apply_teacher_textbook(proj, items)
        if note and proj["materials"]["textbook"] and not proj["materials"].get("toc"):
            await self.read_contents(proj)
        self.say(proj, ((note + "\n\n") if note else "") + self.new_files_report(proj, new), "lead", "report")

    def new_files_report(self, proj: dict, new: list) -> str:
        known = proj["materials"]["files"]
        lines = [f"新加了 {len(new)} 份资料，我已经看过并分好类（可以在资料清单里改）："]
        for m in new[:12]:
            f = known[m.id]
            ch = "、".join(f"第{c}章" for c in f["chapters"]) or "全书通用"
            lines.append(f"· {m.name} → {team.ROLES.get(f['role'], f['role'])}，{ch}")
        if len(new) > 12:
            lines.append(f"……共 {len(new)} 份")
        chapters = (proj.get("outline") or {}).get("chapters") or []
        if chapters:
            touched = {c for m in new for c in known[m.id]["chapters"]}
            general = any(not known[m.id]["chapters"] for m in new)
            in_outline = {c["no"] for c in chapters}
            def nos(status: str) -> list[str]:
                return [f"{c['no']}.{i + 1}" for c in chapters if general or c["no"] in touched
                        for i, les in enumerate(c["lessons"]) if les["status"] == status]
            short = lambda xs: "、".join(xs[:10]) + (" 等" if len(xs) > 10 else "")  # noqa: E731
            lines.append("还没写的课会自动用上这些资料。")
            if nos("awaiting"):
                lines.append(f"写好还没发布的 {short(nos('awaiting'))} 可以参考新资料重写：需要的话在“课时进度”里点那一课的“重写”。")
            if nos("published"):
                lines.append(f"已经发布的 {short(nos('published'))} 不会自动改。")
            extra = sorted(c for c in touched if c not in in_outline)
            if extra:
                lines.append("资料里有" + "、".join(f"第{c}章" for c in extra) + "的内容，大纲里还没有这一章；需要的话告诉我“加上第"
                             + str(extra[0]) + "章”。")
        return "\n".join(lines)

    # scanned books: text recognition (OCR) ----------------------------------------------------
    async def ocr_file(self, proj: dict, fid: str, pages: list[int]) -> int:
        """Recognise the given pages of a scanned PDF (those not read yet). Returns how many were read now."""
        cache = self.store.ocr_cache(proj["import_id"], fid)
        todo = sorted({n for n in pages if n not in cache})
        if not todo or not mt.ocr_available():
            return 0
        data = self.store.data(proj["import_id"], fid)
        got = await asyncio.to_thread(mt.ocr_pages, data, todo)
        cache.update(got)
        self.store.save_ocr(proj["import_id"], proj["owner"], fid, cache)
        return len(got)

    def is_scanned(self, m: mt.Material) -> bool:
        return m.ext == ".pdf" and (m.error == "scanned" or m.ocr > 0)

    async def read_scanned(self, proj: dict) -> None:
        """Scanned PDFs (pictures of pages) are read by text recognition: the front pages first (title, contents,
        the first chapter), the rest of a textbook later, chapter by chapter, when a lesson needs it."""
        for m in self.items(proj):
            if m.ext == ".pdf" and m.error == "scanned" and not m.ocr:
                if not mt.ocr_available():
                    return
                n = min(m.pages or 40, 40 if m.pages >= 60 else 12)
                proj["busy"] = {"label": f"正在识别扫描版资料的文字：{m.name}（前 {n} 页，约 {max(1, n // 20)} 分钟）", "since": now()}
                self.projects.save(proj)
                await self.ocr_file(proj, m.id, list(range(1, n + 1)))

    async def ocr_lesson_pages(self, proj: dict, chapter: dict, les: dict) -> None:
        """Before a lesson is written from a scanned textbook: recognise its sections' pages."""
        tb = proj["materials"]["textbook"]
        m = next((x for x in self.items(proj) if x.id == tb), None)
        if not m or not self.is_scanned(m) or not proj["materials"].get("toc"):
            return
        wanted = set(les.get("sections") or [])
        pages: list[int] = []
        for c in proj["materials"]["toc"]:
            for x in c["sections"]:
                if x["no"] in wanted and x.get("start"):
                    pages += list(range(x["start"], min(x.get("end") or x["start"] + 6, x["start"] + 14) + 1))
            if not wanted and c["no"] == chapter["no"] and c.get("start"):
                pages += list(range(c["start"], min(c.get("end") or c["start"] + 8, c["start"] + 14) + 1))
        pages = sorted(set(pages))[:24]
        if pages:
            proj["busy"] = {"label": f"正在识别教材第 {pages[0]}–{pages[-1]} 页的文字", "since": now()}
            self.projects.save(proj)
            await self.ocr_file(proj, tb, pages)

    # the teacher's textbook is an instruction ---------------------------------------------------
    def teacher_texts(self, proj: dict) -> list[str]:
        out = [proj["requirements"].get("notes", "")]
        out += [m["text"] for m in proj["messages"] if m["role"] == "teacher"]
        out += [f"{q['text']} {q['answer']}" for q in proj["questions"] if q["status"] == "answered"]
        return [t for t in out if t]

    def apply_teacher_textbook(self, proj: dict, items: list[mt.Material]) -> str:
        """When the teacher named the textbook, that book is the main textbook — found by title, author or file
        name. If it is not among the files, say so and ask (with the likeliest files as options); never guess."""
        names = named_textbooks(self.teacher_texts(proj))
        if not names:
            return ""
        files = proj["materials"]["files"]
        cur = proj["materials"]["textbook"]
        if cur and files.get(cur, {}).get("by") == "teacher" and files[cur].get("role") == "main_textbook":
            return ""  # the teacher already chose it in the materials list
        best, score = match_textbook(names, items, {fid: f.get("title", "") for fid, f in files.items()},
                                     lambda fid: self.text(proj, fid)[:3000])
        proj["requirements"]["textbook"] = "、".join(f"《{n}》" for n in names)[:300]
        if best and score >= 0.6:
            for fid, f in files.items():
                if f.get("role") == "main_textbook" and fid != best:
                    f.update(role="aux_textbook")
            files.setdefault(best, {"chapters": [], "title": "", "language": "", "note": ""})
            files[best].update(role="main_textbook", by="teacher", confidence="high", note=f"老师指定的教材《{names[0]}》")
            if cur != best:
                proj["materials"]["textbook"], proj["materials"]["toc"] = best, []
            name = next((m.name for m in items if m.id == best), "")
            return f"按你的要求，主教材定为《{names[0]}》（文件：{name}）。"
        # Not found: ask, with the files most likely to be a textbook as the options.
        cands = sorted(items, key=lambda m: (-(m.ext == ".pdf"), -m.pages, -m.size))[:4]
        text = f"没有在资料里找到你指定的教材《{names[0]}》。它是下面哪一份？"
        if not any(q.get("kind") == "textbook" and q["status"] == "open" for q in proj["questions"]):
            proj["questions"].insert(0, {"id": new_id(), "text": text, "kind": "textbook",
                                         "options": [m.name for m in cands] + ["资料里没有这本书，先不用教材"],
                                         "status": "open", "answer": "", "stage": proj["stage"]})
        return text + "（请在“待回答的问题”里选，或把这本书上传到资料清单。）"

    async def reread_contents(self, proj: dict) -> None:
        """重新读目录: scanned files not recognised yet are read first, then the main textbook's contents again."""
        await self.read_scanned(proj)
        proj["materials"]["toc"] = []
        await self.read_contents(proj)
        toc = proj["materials"].get("toc") or []
        if toc:
            text = f"主教材的目录重新读好了：{len(toc)} 章。"
        elif not pages_of(self.text(proj, proj["materials"]["textbook"])):
            text = ("这个主教材文件没有页码（例如 Word 文件），没法按页读目录；写课时会按章节标题去找内容。"
                    "如果有这本书的 PDF 版，上传后点 ☆ 设为主教材效果更好。")
        else:
            text = "主教材还是没读出目录（可能目录页不清楚或不在前 40 页）。可以换一个版本的文件，或在对话里告诉我各章的起始页。"
        self.say(proj, text, "lead")

    async def design_book_now(self, proj: dict) -> None:
        """生成课程设计书 for a project planned before the design book existed."""
        await self.make_design_book(proj)
        self.say(proj, "《课程设计书》写好了，在“大纲与日历”里，请看一下、需要就改；之后写的课都照它来。", "lead")

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
        m = next((x for x in self.items(proj) if x.id == fid), None)
        if m and self.is_scanned(m) and chapters and not any(c.get("start") for c in chapters):
            await self.find_offset_scanned(proj, fid, chapters, max(toc_pages) if toc_pages else 0)
        proj["materials"]["toc"] = chapters
        proj["materials"]["book_title"] = str((data or {}).get("book_title") or "")[:200]

    async def find_offset_scanned(self, proj: dict, fid: str, chapters: list[dict], after: int) -> None:
        """Printed page numbers differ from PDF pages by the front matter. Read the pages where the second
        chapter could start and use the one whose text carries its title; then every start follows."""
        target = next((c for c in chapters[1:] if c.get("page")), None) or next((c for c in chapters if c.get("page")), None)
        if not target:
            return
        for off in range(0, 41, 4):
            n = target["page"] + off
            await self.ocr_file(proj, fid, [n, n + 1, n + 2, n + 3])
            pages = pages_of(self.text(proj, fid))
            key = norm(target["title"])
            hit = next((k for k in range(n, n + 4) if key and key in norm(pages.get(k, ""))), None)
            if hit:
                off = hit - target["page"]
                for c in chapters:
                    for x in [c, *c["sections"]]:
                        if x.get("page"):
                            x["start"] = x["page"] + off
                flat = sorted((x for c in chapters for x in [c, *c["sections"]] if x.get("start")), key=lambda x: x["start"])
                for a, b in zip(flat, flat[1:] + [None]):
                    a["end"] = max(a["start"], (b["start"] - 1) if b else a["start"] + 10)
                return

    # stage 2: outline --------------------------------------------------------------------------
    async def apply_answers(self, proj: dict, items: list[mt.Material]) -> str:
        """Before designing: let the librarian bring the materials list in line with the teacher's answers."""
        answered = [q for q in proj["questions"] if q["status"] == "answered"]
        tb = proj["materials"]["textbook"]
        if tb and not proj["materials"].get("toc"):  # e.g. the teacher picked the textbook in a question
            await self.read_contents(proj)
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
        # Courseware is Chinese–English by standard (课件中英对照) unless the teacher chose one language.
        keys = lang_keys(proj["requirements"].get("language", "both"))
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
        await self.make_design_book(proj)
        problems = check_outline(outline)
        n = sum(len(c["lessons"]) for c in outline["chapters"])
        last_week = max([les["week"] or 0 for c in outline["chapters"] for les in c["lessons"]] or [0])
        cal = f"教学日历排到第 {last_week} 周" if last_week else "还没排周次（可以在右边给每次课填上周次）"
        msg = (f"大纲草稿出来了：{len(outline['chapters'])} 章、{n} 次课，{cal}。请在右边“大纲与日历”里看，"
               "可以直接改名、调顺序、删课或加课。下面还有一份《课程设计书》：这门课用哪台机器人贯穿全课、每章的动画和实验"
               "怎么做、符号约定——每一课都照它写，请一起看，可以直接改。没问题就点“大纲定稿”。")
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
                lessons.append({"id": new_id(), "title": T(les.get("title")), "goal": T(les.get("goal")), "problem": T(les.get("problem")),
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
        """The next lesson to write — only in a chapter the teacher confirmed (E2); an unconfirmed chapter waits."""
        for c in (proj.get("outline") or {}).get("chapters", []):
            todo = [les for les in c["lessons"] if les["status"] in ("planned", "failed")]
            if todo:
                return (c, todo[0]) if chapter_confirmed(c) else None
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
        book = team.design_book_text(proj.get("design_book"))
        return (f"Course: {disp(proj['outline']['title'])}\nChapter {chapter['no']}: {disp(chapter['title'])}\n"
                f"Lesson: {disp(les['title'])}\nGoal: {disp(les['goal'])}\nTextbook sections: {', '.join(les.get('sections') or []) or '-'}\n"
                f"Students: {r.get('audience') or 'university students'}; level: {r.get('level') or '-'}\n"
                f"Write in: {team.LANG_NAME.get(lang, 'Simplified Chinese')}\n"
                f"Animations and labs available for this chapter: {', '.join(media) or 'none'}\n"
                f"\nThe teacher's requirements (binding):\n{self.requirements_text(proj)}\n"
                + (f"\nThe course design book (follow it):\n{book}\n" if book else ""))

    # 问渠零件与机器人库 ---------------------------------------------------------------------------------
    async def library_catalog(self, proj: dict, extra: str = "") -> str:
        lib = getattr(self, "library", None)
        if not lib:
            return ""
        words = " ".join([disp((proj.get("outline") or {}).get("title")), proj["requirements"].get("notes", "")[:300], extra])
        try:
            return await lib.catalog_text(words)
        except Exception:
            return ""

    async def library_ids(self) -> set[str]:
        lib = getattr(self, "library", None)
        try:
            return set(await lib.entries()) if lib else set()
        except Exception:
            return set()

    def assets_dir(self, proj: dict) -> Path:
        return self.projects.root / proj["id"] / "library"

    async def use_assets(self, proj: dict, ids: list[str], by: str = "ai") -> list[dict]:
        """Copy library entries into the course (once); returns their records (for the sources list)."""
        lib = getattr(self, "library", None)
        out = []
        if not lib:
            return out
        known = await self.library_ids()
        assets = proj.setdefault("assets", {})
        version = ""
        try:
            version = (await lib.index())["version"]
        except Exception:
            pass
        for eid in dict.fromkeys(ids):
            if eid not in known:
                continue
            stale = eid in assets and version and assets[eid].get("version") != version   # rewriting takes the newer version
            if eid not in assets or stale or not (self.assets_dir(proj) / eid / "entry.json").exists():
                try:
                    assets[eid] = {**await lib.copy_into(self.assets_dir(proj), eid), "by": by}
                except Exception as e:  # noqa: BLE001 - a missing entry must not stop the lesson
                    log.warning("library copy %s: %s", eid, e)
                    continue
            out.append(assets[eid])
        return out

    async def lesson_assets(self, proj: dict, les: dict, spec: dict) -> list[dict]:
        """The library entries this lesson shows: what the lecturer listed, else the course's platform."""
        ids = [a["id"] for a in spec.get("assets") or []]
        if not ids:
            ids = [x["id"] for x in (proj.get("design_book") or {}).get("library", [])[:1]]
        recs = await self.use_assets(proj, ids)
        les["assets"] = [r["id"] for r in recs]
        return [{"id": r["id"], "version": r["version"], "name": r["name"], "license": r["license"],
                 "attribution": r["attribution"]} for r in recs]

    def course_brief(self, proj: dict) -> str:
        """What the animator and the lab engineer must know about THIS course (subject, platform, design book)."""
        book = team.design_book_text(proj.get("design_book"))
        return (f"Course: {disp(proj['outline']['title'])}\nThe teacher's requirements (binding):\n{self.requirements_text(proj)}"
                + (f"\n\nThe course design book (follow it):\n{book}" if book else ""))

    @staticmethod
    def fake_animation(spec: dict, no: str) -> str:
        from .production import anim
        return anim.storyboard_code(spec, no)

    def requirements_text(self, proj: dict) -> str:
        r = proj["requirements"]
        lines = [f"- {REQ_LABEL.get(k, k)}: {v}" for k, v in r.items() if v and k not in ("notes",)]
        lines += [f"- 老师说：{t[:600]}" for t in self.teacher_texts(proj)[:8]]
        return "\n".join(lines) or "(none)"

    def previous_spec(self, proj: dict, les: dict) -> str:
        """The latest written lesson of this course before `les` (its spec), for continuity."""
        prev = ""
        for c in proj["outline"]["chapters"]:
            for x in c["lessons"]:
                if x is les or x["id"] == les["id"]:
                    return prev
                f = self.lesson_dir(proj, x) / "spec.json"
                if x["status"] in ("awaiting", "published") and f.exists():
                    try:
                        prev = json.dumps(json.loads(f.read_text())["lesson"], ensure_ascii=False)[:7000]
                    except (ValueError, KeyError):
                        pass
        return prev

    async def make_design_book(self, proj: dict) -> None:
        """课程设计书: the course's own subject, robot platform, notation and per-chapter means — written once the
        outline exists, followed by every lesson. The teacher can read and change it."""
        o = proj.get("outline") or {}
        if not o.get("chapters"):
            return
        if (proj.get("design_book") or {}).get("by") == "teacher":  # the teacher's own version is kept
            proj["design_book"] = normalize_design_book(proj["design_book"], o)
            return
        items = self.items(proj)
        outline = "\n".join(f"Chapter {c['no']} {disp(c['title'])}: " + "; ".join(disp(x["title"]) for x in c["lessons"])
                            for c in o["chapters"])
        proj["busy"] = {"label": "课程设计师正在写《课程设计书》…", "since": now()}
        self.projects.save(proj)
        catalog = await self.library_catalog(proj)
        data = await self.ai.json(system=team.DESIGN_BOOK,
                                  prompt=team.design_book_prompt(summary(proj, items, False), outline, self.requirements_text(proj), catalog),
                                  schema=team.design_book_schema(), max_tokens=5000, fake=lambda: fake_design_book(proj))
        book = normalize_design_book(data, o)
        known = await self.library_ids()
        book["library"] = [x for x in book.get("library", []) if x["id"] in known]
        fs = await self.factory_summary()
        if fs:
            book["factory"] = {"case": fs["case"], "name": fs["case_name"], "products": fs["products"]}
        proj["design_book"] = book

    async def factory_summary(self) -> dict | None:
        """The digital factory's teaching case for the AI team, or None when it is not connected or does not answer."""
        fac = getattr(self, "factory", None)
        if not fac or not fac.available:
            return None
        try:
            return await fac.summary()
        except Exception as e:  # noqa: BLE001 - the factory being down must not stop a lesson
            log.warning("factory: %s", e)
            return None

    def lesson_no(self, proj: dict, chapter: dict, les: dict) -> str:
        return f"{chapter['no']}.{chapter['lessons'].index(les) + 1}"

    def lesson_dir(self, proj: dict, les: dict) -> Path:
        return self.projects.root / proj["id"] / "lessons" / les["id"]

    async def write_lesson(self, proj: dict, lid: str, teacher_note: str = "") -> None:
        """One lesson to the benchmark (D31): lecturer writes the lesson spec, the designer the lab guide and
        lesson plan, assessment the practice set; the reviewer checks; then every deliverable is rendered."""
        chapter, les = self.find_lesson(proj, lid)
        items = self.items(proj)
        keys = lang_keys(proj["outline"]["languages"])
        no = self.lesson_no(proj, chapter, les)
        await self.ocr_lesson_pages(proj, chapter, les)
        src = self.sources(proj, chapter, les, items)
        if not proj.get("design_book"):  # courses planned before the design book existed get one now
            await self.make_design_book(proj)
        catalog = await self.library_catalog(proj, disp(les["title"]))
        ctx = (self.lesson_context(proj, chapter, les, items) + f"\nLesson number: {no}"
               + (f"\n\n问渠零件与机器人库 — entries you may show (id | name | category | tags | principle); list the ones this "
                  f"lesson uses in `assets`, ids exactly as written:\n{catalog}" if catalog else ""))
        fs = await self.factory_summary() if (proj.get("design_book") or {}).get("factory") else None
        if fs:
            ctx += ("\n\n问渠数字工厂 — this course's factory case. Real facts you may use for the robot problem, examples and figures "
                    "(say the data comes from 问渠数字工厂; never invent factory numbers; the workshop has no robot arms):\n" + fs["text"])
        previous = self.previous_spec(proj, les)
        les["status"], les["error"] = "writing", ""
        les["attention"], les["checks"] = [], {}
        if teacher_note:
            les["notes"] = teacher_note
        proj["busy"] = {"label": f"主讲教授正在写：{no} {disp(les['title'])}", "since": now()}
        self.projects.save(proj)
        notes, review, spec, gp = teacher_note, None, None, None
        for attempt in range(2):
            data = await self.ai.json(system=team.AUTHOR, prompt=team.lesson_prompt(ctx, src, notes, sp.STRUCTURE_GUIDE, previous),
                                      schema=sp.lesson_schema(), max_tokens=16000, fake=lambda: fake_spec(les, no))
            spec = sp.normalize_lesson(data)
            missing = sp.check_lesson(spec)
            if not spec["title"][0] or len(missing) > 6:
                raise EngineError("ai_bad_output", "the lesson spec is empty", 502)
            proj["busy"] = {"label": f"课程设计师正在写实验指导书和教案：{no}", "since": now()}
            self.projects.save(proj)
            g = await self.ai.json(system=team.GUIDE_PLAN, prompt=f"{ctx}\n\nLesson spec:\n{json.dumps(spec, ensure_ascii=False)[:20000]}",
                                   schema=sp.guide_plan_schema(), max_tokens=8000, fake=lambda: fake_guide_plan())
            gp = sp.normalize_guide_plan(g)
            proj["busy"] = {"label": f"习题与测评正在出题：{no}", "since": now()}
            self.projects.save(proj)
            ex = await self.ai.json(system=team.ASSESSOR,
                                    prompt=f"{ctx}\n\nLesson spec:\n{json.dumps(spec, ensure_ascii=False)[:14000]}",
                                    schema=team.exercises_schema(keys), max_tokens=6000, fake=lambda: fake_exercises(keys))
            les["exercises"] = {k: self.clean(v) for k, v in cb.norm_text((ex or {}).get("questions"), keys).items()}
            les["answers"] = {k: self.clean(v) for k, v in cb.norm_text((ex or {}).get("answers"), keys).items()}
            les["status"] = "reviewing"
            proj["busy"] = {"label": f"审稿人正在核对：{no}", "since": now()}
            self.projects.save(proj)
            rv = await self.ai.json(system=team.REVIEWER,
                                    prompt=team.review_prompt(ctx, json.dumps(spec, ensure_ascii=False)[:24000],
                                                              disp(les["exercises"])[:4000] + "\n" + disp(les["answers"])[:4000], src[:16000], missing),
                                    schema=team.review_schema(), max_tokens=3000,
                                    fake=lambda: {"verdict": "pass", "issues": [], "summary": "五步齐全，数值与已知条件一致。",
                                                  "checks": {k: {"ok": True, "note": ""} for k in ("textbook", "problem", "numbers", "bilingual")}})
            rv = rv if isinstance(rv, dict) else {}
            ai_checks = rv.get("checks") if isinstance(rv.get("checks"), dict) else {}
            review = {"verdict": rv.get("verdict") if rv.get("verdict") in ("pass", "revise") else "pass",
                      "issues": [i for i in rv.get("issues") or [] if isinstance(i, dict) and i.get("text")][:10],
                      "summary": str(rv.get("summary") or "")[:800], "round": attempt + 1}
            for m in missing:  # what the benchmark requires is never optional
                review["issues"].append({"severity": "high", "text": m})
                review["verdict"] = "revise"
            if review["verdict"] == "pass":
                break
            notes = (teacher_note + "\n" if teacher_note else "") + "审稿人意见：\n" + "\n".join(f"- {i['text']}" for i in review["issues"])
            les["status"] = "writing"
            proj["busy"] = {"label": f"主讲教授按审稿意见重写：{no}", "since": now()}
            self.projects.save(proj)
        spec["sources"] = await self.lesson_assets(proj, les, spec)
        les.pop("factory_used", None)
        spec["figures_made"] = await self.make_figures(proj, les, spec, no)
        video = await self.make_video(proj, les, spec, no, review)
        lab = await self.make_lab(proj, chapter, les, spec, no, review)
        if les.get("factory_used") and fs:
            from .factory import source_record
            spec["sources"] = (spec.get("sources") or []) + [source_record(fs)]
        spec.pop("factory_live", None)
        if fs:
            spec["factory_live"] = f"{self.factory.url}/embed/workshop?view=overview&mode=live"
        proj["busy"] = {"label": f"正在排版课件、指导书、报告模板和教案：{no}", "since": now()}
        self.projects.save(proj)
        await asyncio.to_thread(self.render, proj, chapter, les, spec, gp, no, video, lab)
        await self.make_lecture(proj, chapter, les, spec, no)
        les["review"] = review
        les["status"] = "awaiting"
        les["written"] = now()
        les["ai_checks"] = ai_checks
        les["sources_found"] = bool(src) and not src.startswith("(no source pages")
        les["checklist"] = self.checklist(proj, les, video, lab)
        self.say(proj, self.done_message(les, no, review, video, lab), "lead", "lesson")

    def done_message(self, les: dict, no: str, review: dict | None, video, lab) -> str:
        """Honest: '做好了（审稿通过）' only when nothing needs the teacher; otherwise say what is missing."""
        made = f"讲义、{'动画、' if video else ''}{'虚拟实验、' if lab else ''}课件、练习与答案、实验指导书、实验报告模板、教案"
        todo = les.get("attention") or []
        failed = [c["label"] for c in les.get("checklist") or [] if c["ok"] is False]
        if todo:
            return (f"《{no} {disp(les['title'])}》初稿有了（{made}），但需要你处理：" + "；".join(x["text"] for x in todo)
                    + " 详见右边“课时进度”里这一课的清单。")
        verdict = ("审稿通过" if review and review["verdict"] == "pass" and not failed
                   else "清单里这几项没打勾：" + "、".join(failed) if failed else "审稿人仍有意见，请重点看审稿意见")
        return (f"《{no} {disp(les['title'])}》做好了（{verdict}）：{made}。"
                "请在右边“课时进度”里审阅：通过就发布给学生，或者告诉我怎么改。")

    def checklist(self, proj: dict, les: dict, video, lab) -> list[dict]:
        """每课一张清单: each item ticked or crossed, and who checked it (自动检查 / AI 自查)."""
        ai_checks = les.get("ai_checks") or {}

        def ai(key):
            c = ai_checks.get(key) if isinstance(ai_checks.get(key), dict) else {}
            return (c.get("ok") is True) if c else None, str(c.get("note") or "")[:200]
        found = bool(les.get("sources_found"))
        tb_ai, tb_note = ai("textbook")
        items = [{"key": "textbook", "label": "教材对应章节已参照", "by": "auto+ai",
                  "ok": (found and tb_ai is not False) if proj["materials"].get("textbook") else False,
                  "note": (("参照：" + "、".join(les["sections"]) if les.get("sections") else "已找到这一课对应的教材内容") if found
                           else "没有找到这一课对应的教材页")
                          + (f"；{tb_note}" if tb_note else "")}]
        ok, note = ai("problem")
        items.append({"key": "problem", "label": "机器人问题是本课的", "by": "ai", "ok": ok, "note": note})
        checks = les.get("checks") or {}
        c = checks.get("figures") or {"ok": False, "note": "没有插图"}
        items.append({"key": "figures", "label": "插图切题、标注正确", "by": "auto+ai", "ok": bool(c.get("ok")),
                      "note": c.get("note", ""), "image": c.get("image", "")})
        if self.animator_url:
            c = checks.get("animation") or {"ok": False, "note": "没有动画"}
            c3 = checks.get("animation3d") or {}
            items.append({"key": "animation", "label": "动画切题", "by": c.get("by", "auto+ai"), "ok": bool(c.get("ok")) and bool(video),
                          "note": "；".join(x for x in (c.get("note", ""), c3.get("note", "")) if x),
                          "image": video["poster"].name if video and video.get("poster") else ""})
        if self.labcheck_url:
            c = checks.get("lab") or {"ok": False, "note": "没有虚拟实验"}
            items.append({"key": "lab", "label": "实验切题、能完成", "by": c.get("by", "auto+ai"), "ok": bool(c.get("ok")) and bool(lab),
                          "note": c.get("note", ""), "image": lab["image"].name if lab and lab.get("image") else ""})
        if self.voice_url:
            c = self.lecture_check(les)
            items.append({"key": "lecture", "label": "讲解视频", "by": "auto", "ok": bool(c.get("ok")), "note": c.get("note", "")})
        for key, label in (("numbers", "数值和单位已核对"), ("bilingual", "中英一致")):
            ok, note = ai(key)
            items.append({"key": key, "label": label, "by": "ai", "ok": ok, "note": note})
        return items

    async def make_video(self, proj: dict, les: dict, spec: dict, no: str, review: dict | None) -> dict | None:
        """The lesson video: a 3D opener with the course's real robots (when the library copies allow) followed by
        the formula animation (Manim). Either part alone is fine; both are checked for relevance."""
        video = await self.animate(proj, les, spec, no, review)
        clip = await self.animate3d(proj, les, spec, no)
        if not clip:
            return video
        return await asyncio.to_thread(self.join_clips, proj, les, spec, no, clip, video)

    def models_text(self, models: dict) -> str:
        lines = []
        for eid, m in models.items():
            e = m["entry"]
            js = ", ".join(f"{j['name']}[{j['lower']:.2f}..{j['upper']:.2f}] rest {float((e.get('rest') or {}).get(j['name'], 0)):.2f}"
                           for j in e.get("joints") or [] if j["type"] != "continuous")
            lines.append(f"{eid} | {e['name'].get('zh', '')} / {e['name'].get('en', '')} | {e.get('kind', '')} | {js or '-'} | "
                         f"{(e.get('tool') or {}).get('link', '-')}")
        return "\n".join(lines)

    async def animate3d(self, proj: dict, les: dict, spec: dict, no: str) -> dict | None:
        """三维动画师: a template filled with this lesson's content, rendered by the browser service, checked on its
        key frames. With a digital-factory case the workshop itself can be replayed from the factory's data, followed by
        one robot shot (marked as an illustration). Not made when the service is off or there is nothing to show."""
        from .production import scene3d as S
        les.setdefault("checks", {}).pop("animation3d", None)
        if not self.labcheck_url:
            return None
        ids = list(dict.fromkeys((les.get("assets") or []) + [x["id"] for x in (proj.get("design_book") or {}).get("library", [])]))
        await self.use_assets(proj, ids)
        models = await asyncio.to_thread(S.load_models, self.assets_dir(proj), ids)
        fdata, fsum = await self.workshop_data(proj)
        if not models and not fdata:
            return None
        d = self.lesson_dir(proj, les)
        lang = {"zh": "zh", "en": "en"}.get(proj["outline"].get("languages"), "both")
        spec_json = json.dumps({k: spec[k] for k in ("title", "goal", "problem", "concept", "animation", "summary")},
                               ensure_ascii=False)[:9000]
        title = spec["animation"]["title"] if spec["animation"]["title"][0] else spec["title"]
        source = ""
        if fsum:
            source = "数据来自问渠数字工厂，截至 " + (fsum.get("as_of") or "").replace("T", " ").replace("Z", " UTC")
        problem = ""
        for attempt in range(2):
            proj["busy"] = {"label": f"三维动画师正在{'安排' if attempt == 0 else '重新安排'}三维动画：{no}", "since": now()}
            self.projects.save(proj)
            plan = await self.ai.json(system=team.ANIMATOR_3D,
                                      prompt=team.plan3d_prompt(no, spec_json, self.models_text(models), self.course_brief(proj), problem,
                                                                fsum["text"] if fsum and fdata else ""),
                                      schema=team.plan3d_schema(), max_tokens=3500, fake=lambda: fake_plan3d(models, bool(fdata)))
            plan = normalize_plan3d(plan if isinstance(plan, dict) else {}, models, bool(fdata))
            plans = [plan] + ([plan["also"]] if plan.get("also") else [])
            try:
                scripts = []
                for k, pl in enumerate(plans):
                    illustration = k > 0 and plans[0]["template"] == "workshop"
                    t = (["上下料示意（非工厂数据）", "Loading — an illustration, not factory data"] if illustration else title)
                    scripts.append(S.build(pl, models, title=t, no=no, lang=lang, factory_data=fdata,
                                           source=source if pl["template"] == "workshop" else ""))
            except S.Render3DError as e:
                problem = str(e)
                continue
            proj["busy"] = {"label": f"正在渲染三维动画：{no}（约 1–3 分钟）", "since": now()}
            self.projects.save(proj)
            clips, frames_all, err = [], [], ""
            for k, script in enumerate(scripts):
                try:
                    video, poster, secs, frames = await S.render(self.labcheck_url, S.page(script, models), S.seconds(script),
                                                                 timeout=self.labcheck_timeout * 6)
                except S.Render3DError as e:
                    if e.stage == "service":
                        les["checks"]["animation3d"] = {"ok": None, "note": f"三维渲染服务暂时不可用（{e}）"}
                        return None
                    err = str(e)
                    break
                (d / f"anim3d-{k}.mp4").write_bytes(video)
                if k == 0 and poster:
                    (d / "anim3d.jpg").write_bytes(poster)
                clips.append((d / f"anim3d-{k}.mp4", secs))
                frames_all += frames[:2]
            if err:
                problem = err
                continue
            words = [c[2][0] for sc in scripts for c in sc.get("captions") or []] + [str(x.get("id")) for sc in scripts for x in sc.get("actors") or []]
            rel = await self.relevance(proj, les, spec, "3D animation", words, [("image/jpeg", f) for f in frames_all[:4]])
            if not rel["on_topic"]:
                problem = f"{rel['reason']} {rel['fix']}"
                continue
            out = d / "anim3d.mp4"
            if len(clips) == 1:
                clips[0][0].replace(out)
            else:
                await asyncio.to_thread(self._concat_clips, [c[0] for c in clips], out)
                for c in clips:
                    c[0].unlink(missing_ok=True)
            secs = sum(c[1] for c in clips)
            if any(p["template"] == "workshop" for p in plans):
                les["factory_used"] = True
            note = "＋".join(p["template"] for p in plans)
            les["checks"]["animation3d"] = {"ok": True, "note": f"三维动画 {secs:.0f} 秒（{note}），切题"}
            return {"video": out, "poster": d / "anim3d.jpg" if (d / "anim3d.jpg").exists() else None, "seconds": secs}
        les["checks"]["animation3d"] = {"ok": False, "note": f"三维动画没做成：{problem[:200]}"}
        return None

    @staticmethod
    def _concat_clips(parts: list, out) -> None:
        import subprocess
        norm = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p"
        args = ["ffmpeg", "-y", "-loglevel", "error"]
        for p in parts:
            args += ["-i", str(p)]
        fc = ";".join(f"[{i}:v]{norm}[v{i}]" for i in range(len(parts))) + ";" + "".join(f"[v{i}]" for i in range(len(parts))) \
            + f"concat=n={len(parts)}:v=1:a=0[v]"
        subprocess.run(args + ["-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-crf", "21", "-preset", "veryfast",
                               "-movflags", "+faststart", str(out)], check=True, capture_output=True, timeout=600)

    async def workshop_data(self, proj: dict) -> tuple[dict | None, dict | None]:
        """The busiest recent hour of the factory's workshop (layout, AGV moves, machine states) for a workshop clip."""
        if not (proj.get("design_book") or {}).get("factory"):
            return None, None
        fac = getattr(self, "factory", None)
        fsum = await self.factory_summary()
        if not fsum:
            return None, None
        try:
            frm, to, agv = await fac.busy_window(1.0)
            if not agv:
                return None, fsum
            events = (await fac.data("event")).get("rows") or []
            return {"layout": await fac.layout(), "agv": agv, "event": events, "from": frm, "to": to}, fsum
        except Exception as e:  # noqa: BLE001
            log.warning("factory workshop data: %s", e)
            return None, fsum

    def join_clips(self, proj: dict, les: dict, spec: dict, no: str, clip: dict, video: dict | None) -> dict:
        """3D opener + formula animation → one MP4 (re-encoded to 1280×720, 30 fps). Without ffmpeg, the formula
        animation stays as it is and the 3D clip is kept as its own file."""
        import shutil
        import subprocess
        d = self.lesson_dir(proj, les)
        name = re.sub(r'[\\/:*?"<>|]', "-", f"{no} 动画 {spec['animation']['title'][0] or spec['title'][0]}")[:80]
        target = d / f"{name}.mp4"
        if not video:
            for old in d.glob("*.mp4"):
                if old != clip["video"]:
                    old.unlink()
            shutil.copyfile(clip["video"], target)
            poster = None
            if clip.get("poster"):
                poster = target.with_suffix(".png")
                from PIL import Image
                Image.open(clip["poster"]).save(poster)
            return {"video": target, "poster": poster, "seconds": clip["seconds"], "by": "3d"}
        if not shutil.which("ffmpeg"):
            return video
        out = d / "joined.mp4"
        norm = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip["video"]), "-i", str(video["video"]),
                            "-filter_complex", f"[0:v]{norm}[a];[1:v]{norm}[b];[a][b]concat=n=2:v=1:a=0[v]",
                            "-map", "[v]", "-c:v", "libx264", "-crf", "21", "-preset", "veryfast", "-movflags", "+faststart", str(out)],
                           capture_output=True, timeout=600)
        if r.returncode != 0 or not out.exists():
            log.warning("joining the 3D clip failed: %s", r.stderr[-300:])
            return video
        out.replace(video["video"])
        return {**video, "seconds": round(float(video.get("seconds") or 0) + float(clip["seconds"]), 1), "with3d": True}

    async def animate(self, proj: dict, les: dict, spec: dict, no: str, review: dict | None) -> dict | None:
        """动画师: the storyboard becomes a Manim scene rendered on the server (A2). Before rendering, the code must
        not be a copy of an example or of another lesson (相似度检查); after rendering, the reviewer checks the key
        frames and captions are about THIS lesson (切题检查). Problems go back to the animator twice; then the plain
        storyboard animation (this lesson's own words and formulas) is used and the lesson is marked 需要你处理."""
        from .production import anim, demo_anim, similar
        if not self.animator_url:
            return None
        d = self.lesson_dir(proj, les)
        spec_json = json.dumps({k: spec[k] for k in ("title", "goal", "problem", "concept", "animation", "model", "summary")},
                               ensure_ascii=False)
        code, error, used, why = "", "", "ai", ""
        course = self.course_brief(proj)
        check = {"ok": None, "by": "auto+ai", "note": ""}
        for attempt in range(3):
            proj["busy"] = {"label": f"动画师正在{'写' if attempt == 0 else '修改'}动画：{no}", "since": now()}
            self.projects.save(proj)
            data = await self.ai.json(system=team.ANIMATOR,
                                      prompt=team.animation_prompt(no, spec_json, demo_anim.TECHNIQUE, error, code, course),
                                      schema=team.animation_schema(), max_tokens=12000, fake=lambda: {"code": self.fake_animation(spec, no)})
            code = str((data or {}).get("code") or "")
            code = re.sub(r"^```(?:python)?\s*|```\s*$", "", code.strip())
            if not code:
                error = why = "empty code"
                continue
            if self.copy_check:
                error = similar.problem(code, self.anim_refs(proj, les))
                if error:
                    why = "动画程序和范例或别的课大段雷同"
                    continue
            proj["busy"] = {"label": f"正在渲染动画：{no}（约 2–5 分钟）", "since": now()}
            self.projects.save(proj)
            try:
                res = await anim.render(self.animator_url, code, self.animator_timeout)
            except anim.RenderError as e:
                if e.stage == "service":
                    self.needs_you(les, "animation", f"动画渲染服务暂时不可用（{e}），这一课还没有动画。稍后点“重做动画”。")
                    return self._no_video(review, f"动画渲染服务暂时不可用（{e}），这一课先没有动画")
                error, why = str(e), "动画程序渲染出错"
                continue
            video, poster, secs = res[:3]
            frames = list(res[3]) if len(res) > 3 else []
            proj["busy"] = {"label": f"审稿人正在核对动画是否切题：{no}", "since": now()}
            self.projects.save(proj)
            images = [("image/jpeg", f) for f in frames] or ([("image/png", poster)] if poster else [])
            rel = await self.relevance(proj, les, spec, "animation", anim_texts(code), images)
            check = {"ok": rel["on_topic"], "by": "auto+ai", "note": rel["reason"]}
            if rel["on_topic"]:
                break
            error = f"The reviewer found the animation off topic: {rel['reason']} What to change: {rel['fix']}"
            why = f"审稿人认为动画不切题：{rel['reason']}"
        else:
            used = "storyboard"
            try:
                video, poster, secs = (await anim.render(self.animator_url, anim.storyboard_code(spec, no), self.animator_timeout))[:3]
            except anim.RenderError as e:
                self.needs_you(les, "animation", f"动画没有做成（{why or str(e)[:120]}），这一课还没有动画。可以点“重做动画”，或告诉我怎么改。")
                return self._no_video(review, f"动画没有做成（{str(e)[:200]}）")
            check = {"ok": False, "by": "auto+ai", "note": f"动画师三次都没做成（{why}），先用了只有本课文字和公式的简版动画"}
            self.needs_you(les, "animation", f"动画师三次都没做成合格的动画（{why}），现在是只有本课文字和公式的简版。"
                                             "可以点“重做动画”，或告诉我想要什么画面。")
        les.setdefault("checks", {})["animation"] = check
        name = re.sub(r'[\\/:*?"<>|]', "-", f"{no} 动画 {spec['animation']['title'][0] or spec['title'][0]}")[:80]
        for old in d.glob("*.mp4"):
            old.unlink()
        v, pp = await asyncio.to_thread(anim.save, d, name, video, poster)
        (d / "animation.py").write_text(code if used == "ai" else anim.storyboard_code(spec, no))
        (d / "animation_by.txt").write_text(used)
        return {"video": v, "poster": pp, "seconds": secs, "by": used}

    async def make_figures(self, proj: dict, les: dict, spec: dict, no: str) -> list[dict]:
        """插图师: each figure the lecturer asked for is drawn by a program (scene / graph / chart / drawing), must render
        to a real picture and pass the relevance check (the reviewer sees it); problems go back to the illustrator
        once. A figure that still fails is left out and the checklist says so."""
        from .production import figures as F
        d = self.lesson_dir(proj, les)
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("fig-*"):
            old.unlink()
        lang = {"zh": "zh", "en": "en"}.get(proj["outline"].get("languages"), "both")
        course = self.course_brief(proj)
        spec_json = json.dumps({k: spec[k] for k in ("title", "goal", "problem", "concept", "example", "model", "summary")},
                               ensure_ascii=False)[:12000]
        chapter, _ = self.find_lesson(proj, les["id"])
        ch_no = chapter["no"]
        # figures are numbered through the chapter, like a textbook: after the earlier lessons' figures
        before = 0
        for x in chapter["lessons"]:
            if x["id"] == les["id"]:
                break
            before += len(x.get("figures") or [])
        made, failed = [], []
        for i, fig in enumerate(spec.get("figures") or [], 1):
            dest = d / f"fig-{i}"
            proj["busy"] = {"label": f"插图师正在画图 {ch_no}.{i}：{fig['title'][0]}", "since": now()}
            self.projects.save(proj)
            error, previous, ok, out = "", "", False, None
            for attempt in range(2):
                try:
                    if fig["kind"] == "drawing":
                        aid = fig["asset"] or next(iter(les.get("assets") or []), "")
                        rec = (proj.get("assets") or {}).get(aid)
                        if not rec:
                            recs = await self.use_assets(proj, [aid]) if aid else []
                            rec = recs[0] if recs else None
                        svg = next((f for f in (rec or {}).get("files", []) if f.endswith(".svg")), "")
                        png = next((f for f in (rec or {}).get("files", []) if f.endswith(".png")), "")
                        if svg:
                            out = await asyncio.to_thread(F.render_drawing, self.assets_dir(proj) / rec["id"] / svg, dest)
                        elif png:    # the published library's first phase has rendered pictures, no drawings yet
                            out = await asyncio.to_thread(F.render_picture, self.assets_dir(proj) / rec["id"] / png, dest)
                        else:
                            raise F.FigureError(f"no library drawing for {aid or '(none)'}")
                    elif fig["kind"] == "factory":
                        from .production import factory_figs
                        fac = getattr(self, "factory", None)
                        if not fac or not fac.available or not (proj.get("design_book") or {}).get("factory"):
                            raise F.FigureError("the digital factory is not set up for this course")
                        try:
                            out = await factory_figs.make(fac, fig["asset"] or "layout", dest, lang,
                                                          [x.strip() for x in re.split(r"[,，\s]+", fig.get("data") or "") if x.strip()])
                        except Exception as e:  # noqa: BLE001 - FactoryError, bad data
                            if isinstance(e, F.FigureError):
                                raise
                            raise F.FigureError(f"digital factory: {e} (not set up)") from e
                        les["factory_used"] = True
                    else:
                        data = await self.ai.json(system=team.ILLUSTRATOR,
                                                  prompt=team.figure_prompt(no, fig, spec_json, lang, course, error, previous),
                                                  schema=team.figure_schema(fig["kind"]), max_tokens=8000,
                                                  fake=lambda: fake_figure(fig, spec))
                        data = data if isinstance(data, dict) else {}
                        if fig["kind"] == "graph":
                            previous = json.dumps(data.get("graph") or {}, ensure_ascii=False)[:4000]
                            out = await asyncio.to_thread(F.render_graph, data.get("graph") or {}, lang, dest)
                        elif fig["kind"] == "chart":
                            previous = json.dumps(data.get("chart") or {}, ensure_ascii=False)[:4000]
                            out = await asyncio.to_thread(F.render_chart, data.get("chart") or {}, lang, dest)
                        else:
                            if not self.animator_url:
                                raise F.FigureError("the figure renderer (animator service) is not set up")
                            code = re.sub(r"^```(?:python)?\s*|```\s*$", "", str(data.get("code") or "").strip())
                            previous = code
                            out = await F.render_scene(self.animator_url, code, dest)
                    png = d / out["png"]
                    if not F.png_ok(png):
                        raise F.FigureError("the picture is blank")
                    rel = await self.relevance(proj, les, spec, f"figure “{fig['title'][0]}” (must show: {fig['purpose'][0]})",
                                               [fig["title"][0], fig["title"][1], fig["purpose"][0]], [("image/png", png.read_bytes())])
                    if not rel["on_topic"]:
                        raise F.FigureError(f"the reviewer found it does not show what was asked: {rel['reason']} {rel['fix']}")
                    ok = True
                    break
                except F.FigureError as e:
                    error = str(e)
                    if "not set up" in error or "not installed" in error or "no library drawing" in error:
                        break
            if ok and out:
                made.append({"no": f"{ch_no}.{before + len(made) + 1}", "kind": fig["kind"], "place": fig["place"], "title": fig["title"],
                             "png": out["png"], "svg": out.get("svg", "")})
            else:
                failed.append(f"{fig['title'][0]}（{error[:120]}）")
                for f in d.glob(f"fig-{i}.*"):
                    f.unlink()
        # numbered in the order they appear in the notes
        order = ["problem", "concept", "notes", "example", "model", "summary"]
        made.sort(key=lambda f: order.index(f["place"]))
        for k, f in enumerate(made, 1):
            f["no"] = f"{ch_no}.{before + k}"
        les["figures"] = made
        asked = len(spec.get("figures") or [])
        les.setdefault("checks", {})["figures"] = {
            "ok": bool(made) and not failed, "by": "auto+ai",
            "note": (f"{len(made)}/{asked} 张插图通过切题检查" if asked else "主讲教授没有安排插图")
                    + (f"；没画成：{'；'.join(failed)[:300]}" if failed else ""),
            "image": made[0]["png"] if made else ""}
        return made

    def anim_refs(self, proj: dict, les: dict) -> dict[str, str]:
        """What an animation must not copy: the examples and this course's other lessons' animations."""
        from .production import demo_anim
        refs = {"the technique example": demo_anim.TECHNIQUE, "the physics sample lesson 2.1": demo_anim.AGV_2_1}
        refs.update(self._other_lessons(proj, les, "animation.py", "animation_by.txt"))
        return refs

    def lab_refs(self, proj: dict, les: dict) -> dict[str, str]:
        from .production import labs
        refs = {"the technique example": labs.example_code(), "the 3D technique example": labs.example_code3d(),
                "the physics sample lab 2.1": labs.physics_example()}
        refs.update(self._other_lessons(proj, les, "lab.js"))
        return refs

    def _other_lessons(self, proj: dict, les: dict, name: str, by: str = "") -> dict[str, str]:
        out = {}
        for c in (proj.get("outline") or {}).get("chapters", []):
            for x in c["lessons"]:
                f = self.lesson_dir(proj, x) / name
                if x["id"] == les["id"] or not f.exists():
                    continue
                if by and (self.lesson_dir(proj, x) / by).exists() and (self.lesson_dir(proj, x) / by).read_text() != "ai":
                    continue  # the plain storyboard version is a template, not someone's design
                out[f"lesson {self.lesson_no(proj, c, x)}"] = f.read_text(encoding="utf-8")
        return out

    async def relevance(self, proj: dict, les: dict, spec: dict, what: str, texts: list[str],
                        images: list[tuple[str, bytes]]) -> dict:
        """切题检查: the reviewer looks at the pictures and texts the student will see."""
        lesson = json.dumps({"title": spec["title"], "concept": spec["concept"].get("title"), "points": spec["concept"].get("points"),
                             "robot problem": spec["problem"].get("title"), "problem text": spec["problem"].get("text")},
                            ensure_ascii=False)
        data = await self.ai.json(system=team.RELEVANCE, prompt=team.relevance_prompt(what, self.course_brief(proj), lesson, texts),
                                  schema=team.relevance_schema(), max_tokens=800, images=images[:4],
                                  fake=lambda: {"on_topic": True, "reason": "画面和字幕讲的是本课的概念和机器人问题", "fix": ""})
        data = data if isinstance(data, dict) else {}
        return {"on_topic": data.get("on_topic") is not False, "reason": str(data.get("reason") or "")[:300],
                "fix": str(data.get("fix") or "")[:500]}

    @staticmethod
    def needs_you(les: dict, kind: str, text: str) -> None:
        """需要你处理: something the team could not finish honestly; shown prominently with a button to redo it."""
        items = [x for x in les.get("attention") or [] if x["kind"] != kind]
        items.append({"kind": kind, "text": text})
        les["attention"] = items

    @staticmethod
    def clear_attention(les: dict, kind: str) -> None:
        les["attention"] = [x for x in les.get("attention") or [] if x["kind"] != kind]

    def pairs_for(self, proj: dict, chapter: dict) -> tuple[list[str], list[str], str]:
        o = proj["outline"]
        pair_of = lambda t: [t.get("zh") or t.get("en") or "", t.get("en") or t.get("zh") or ""]  # noqa: E731
        return pair_of(o["title"]), pair_of(chapter["title"]), ("en" if o.get("languages") == "en" else "zh")

    async def make_lab(self, proj: dict, chapter: dict, les: dict, spec: dict, no: str, review: dict | None) -> dict | None:
        """实验师 (A3): one lab in the lab kit, checked for safety, then tried in a headless browser — every scene
        draws, every slider moves, every task's demo ticks it. Problems go back to the lab engineer twice;
        a lab that still fails is not used (the lesson is finished without it and the review says so)."""
        from .production import labs, similar
        d = self.lesson_dir(proj, les)
        d.mkdir(parents=True, exist_ok=True)
        for name in ("lab.js", "lab.png", "lab_check.json"):
            (d / name).unlink(missing_ok=True)
        les.pop("lab_problems", None)
        if not self.labcheck_url:
            return None
        course, chap, lang = self.pairs_for(proj, chapter)
        spec_json = json.dumps({k: spec[k] for k in ("title", "goal", "problem", "concept", "lab", "model", "everyday")},
                               ensure_ascii=False)
        lab_id = no.replace(".", "-")
        from .production import scene3d as S3
        mids = list(dict.fromkeys((les.get("assets") or []) + [x["id"] for x in (proj.get("design_book") or {}).get("library", [])]))
        await self.use_assets(proj, mids)
        models = await asyncio.to_thread(S3.load_models, self.assets_dir(proj), mids)
        models_text = self.models_text(models) if models else ""
        code, problems, result = "", [], None
        check = {"ok": None, "by": "auto+ai", "note": ""}
        for attempt in range(3):
            proj["busy"] = {"label": f"实验师正在{'写' if attempt == 0 else '修改'}虚拟实验：{no}", "since": now()}
            self.projects.save(proj)
            data = await self.ai.json(system=team.LAB_ENGINEER,
                                      prompt=team.lab_prompt(no, spec_json, labs.example_code(), problems, code, self.course_brief(proj),
                                                             models_text, labs.example_code3d() if models else ""),
                                      schema=team.lab_schema(), max_tokens=14000, fake=lambda: {"code": labs.example_code()})
            code = re.sub(r"^```(?:js|javascript)?\s*|```\s*$", "", str((data or {}).get("code") or "").strip())
            problems = labs.static_problems(code)
            if not problems and self.copy_check:
                copy = similar.problem(code, self.lab_refs(proj, les))
                problems = [copy] if copy else []
            if problems:
                continue
            proj["busy"] = {"label": f"正在试运行虚拟实验：{no}（约 30 秒）", "since": now()}
            self.projects.save(proj)
            page_html = labs.page([(no, code)], course=course, chapter=chap, lang=lang, models=models)
            try:
                result = await labs.trial_run(self.labcheck_url, page_html, lab_id, self.labcheck_timeout)
            except labs.CheckError as e:
                self.needs_you(les, "lab", f"实验检查服务暂时不可用（{e}），这一课还没有虚拟实验。稍后点“重做实验”。")
                return self._no_video(review, f"实验检查服务暂时不可用（{e}），这一课先没有虚拟实验，可以点“重做实验”")
            if not result["ok"]:
                problems = result["problems"]
                continue
            proj["busy"] = {"label": f"审稿人正在核对实验是否切题：{no}", "since": now()}
            self.projects.save(proj)
            shot = [("image/png", result["screenshot"])] if result.get("screenshot") else []
            rel = await self.relevance(proj, les, spec, "virtual lab", lab_texts(code), shot)
            done = sum(1 for v in (result.get("tasks") or {}).values() if v)
            check = {"ok": rel["on_topic"], "by": "auto+ai",
                     "note": f"试运行通过，{done} 个任务都能完成；{rel['reason']}" if rel["on_topic"] else rel["reason"]}
            if rel["on_topic"]:
                break
            problems = [f"the reviewer found the lab off topic: {rel['reason']} What to change: {rel['fix']}"]
            result = None
        else:
            les["lab_problems"] = problems[:10]
            les.setdefault("checks", {})["lab"] = {"ok": False, "by": "auto+ai", "note": "；".join(problems[:2])[:300]}
            self.needs_you(les, "lab", "虚拟实验三次都没有通过检查，这一课先不带实验。问题：" + "；".join(problems[:2])[:300]
                           + "。可以点“重做实验”，或告诉我想要什么实验。")
            if review is not None:
                review["issues"].append({"severity": "medium", "text": "虚拟实验三次都没有通过试运行，这一课先不带实验，可以点“重做实验”。"
                                                                       "问题：" + "；".join(problems[:3])})
            return None
        les.setdefault("checks", {})["lab"] = check
        (d / "lab.js").write_text(code, encoding="utf-8")
        les["lab_models"] = labs.models_used(code, models)
        image = None
        if result and result["screenshot"]:
            image = d / "lab.png"
            image.write_bytes(result["screenshot"])
        (d / "lab_check.json").write_text(json.dumps({"tasks": result["tasks"] if result else {}, "seconds": result["seconds"] if result else 0,
                                                      "checked": now()}, ensure_ascii=False))
        return {"code": d / "lab.js", "image": image}

    def lab_page(self, proj: dict, chapter: dict, lessons: list[dict]) -> str | None:
        """The chapter's lab page: the labs of the given lessons, in lesson order."""
        from .production import labs
        items = []
        for les in chapter["lessons"]:
            if les in lessons:
                js = self.lesson_dir(proj, les) / "lab.js"
                if js.exists():
                    items.append((self.lesson_no(proj, chapter, les), js.read_text(encoding="utf-8")))
        if not items:
            return None
        course, chap, lang = self.pairs_for(proj, chapter)
        from .production import scene3d as S3
        mids = sorted({m for les in lessons for m in les.get("lab_models") or []})
        models = S3.load_models(self.assets_dir(proj), mids) if mids else {}
        return labs.page(items, course=course, chapter=chap, lang=lang, key=f"wq-lab-{proj['id'][:8]}-{chapter['id'][:8]}",
                         models=models)

    async def redo_lab(self, proj: dict, lid: str) -> None:
        await self.redo_media(proj, lid, "lab")

    async def redo_media(self, proj: dict, lid: str, kind: str) -> None:
        """重做动画 / 重做实验: only that part of a written lesson, then the slides again (new video or picture)."""
        chapter, les = self.find_lesson(proj, lid)
        d = self.lesson_dir(proj, les)
        data = json.loads((d / "spec.json").read_text())
        spec, gp = data["lesson"], data["guide_plan"]
        no = self.lesson_no(proj, chapter, les)
        review = les.get("review")
        word = "实验" if kind == "lab" else "动画"
        if review:
            review["issues"] = [i for i in review.get("issues", []) if word not in i.get("text", "")]
        self.clear_attention(les, kind)
        mp4 = next(iter(sorted(d.glob("*.mp4"))), None)
        video = None
        if kind == "animation":
            video = await self.make_video(proj, les, spec, no, review)
        elif mp4:
            png = mp4.with_suffix(".png")
            secs = next((f.get("seconds", 0) for f in les.get("files") or [] if f["kind"] == "animation"), 0)
            video = {"video": mp4, "poster": png if png.exists() else None, "seconds": secs}
        if kind == "lab":
            lab = await self.make_lab(proj, chapter, les, spec, no, review)
        else:
            js, shot = d / "lab.js", d / "lab.png"
            lab = {"code": js, "image": shot if shot.exists() else None} if js.exists() else None
        proj["busy"] = {"label": f"正在重新排版课件：{no}", "since": now()}
        self.projects.save(proj)
        await asyncio.to_thread(self.render, proj, chapter, les, spec, gp, no, video, lab)
        await self.make_lecture(proj, chapter, les, spec, no)
        les["review"] = review
        les["checklist"] = self.checklist(proj, les, video, lab)
        todo = next((x["text"] for x in les.get("attention") or [] if x["kind"] == kind), "")
        if kind == "lab":
            text = "重做好了，已通过试运行和切题检查，课件里的实验页也换成了新截图" if lab and not todo else f"还是没做成：{todo or '请看清单'}"
        else:
            text = "重做好了，已通过切题检查，课件里的动画也换了" if video and not todo else f"还是没做成：{todo or '请看清单'}"
        self.say(proj, f"《{no}》的{'虚拟实验' if kind == 'lab' else '动画'}{text}。", "lead", "lesson")

    @staticmethod
    def _no_video(review: dict | None, text: str) -> None:
        if review is not None:
            review["issues"].append({"severity": "low", "text": text})
        return None

    def render(self, proj: dict, chapter: dict, les: dict, spec: dict, gp: dict, no: str, video: dict | None = None,
               lab: dict | None = None) -> None:
        """Every deliverable of one lesson, in the benchmark layout."""
        from .production import deck, docs, page
        o = proj["outline"]
        pair_of = lambda t: [t.get("zh") or t.get("en") or "", t.get("en") or t.get("zh") or ""]  # noqa: E731
        course, chap = pair_of(o["title"]), pair_of(chapter["title"])
        d = self.lesson_dir(proj, les)
        d.mkdir(parents=True, exist_ok=True)
        for old in d.iterdir():
            if old.stem == "lab" or old.stem.startswith("fig-"):
                continue  # lab.* belong to make_lab, fig-* to make_figures
            if old.suffix in (".pptx", ".docx", ".json", ".html") or (not video and old.suffix in (".mp4", ".png")):
                old.unlink()
        # The lesson number is added by the layout; drop one the author may have put in the title.
        spec["title"] = [re.sub(r"^\s*\d+(\.\d+)*\s*", "", x) or x for x in spec["title"]]
        (d / "spec.json").write_text(json.dumps({"lesson": spec, "guide_plan": gp}, ensure_ascii=False))
        files = []
        name = re.sub(r'[\\/:*?"<>|]', "-", f"{no} {spec['title'][0]}")[:80]
        if video:
            files.append({"name": video["video"].name, "kind": "animation", "teacher_only": False, "seconds": video["seconds"]})
        lab_image = lab["image"] if lab and lab.get("image") else None
        deck.build(spec, d / f"{name} 课件.pptx", no=no, course=course, chapter=chap,
                   video=video["video"] if video else None, poster=video["poster"] if video else None, lab_image=lab_image)
        if lab:
            from .production import labs
            lab_name = f"实验{no} 虚拟实验.html"
            from .production import scene3d as S3
            lab_models = S3.load_models(self.assets_dir(proj), les.get("lab_models") or []) if les.get("lab_models") else {}
            (d / lab_name).write_text(labs.page([(no, (d / "lab.js").read_text(encoding="utf-8"))], course=course, chapter=chap,
                                                lang="en" if o.get("languages") == "en" else "zh", models=lab_models), encoding="utf-8")
            files.append({"name": lab_name, "kind": "lab", "teacher_only": False})
        files.append({"name": f"{name} 课件.pptx", "kind": "slides", "teacher_only": False})
        docs.guide(spec, gp, d / f"实验{no} 实验指导书.docx", no)
        files.append({"name": f"实验{no} 实验指导书.docx", "kind": "guide", "teacher_only": False})
        docs.report(spec, gp, d / f"实验{no} 实验报告模板.docx", no)
        files.append({"name": f"实验{no} 实验报告模板.docx", "kind": "report", "teacher_only": False})
        docs.plan(spec, gp, d / f"{no} 教案.docx", no, course[0], chap[0], proj.get("owner_name", ""))
        files.append({"name": f"{no} 教案.docx", "kind": "plan", "teacher_only": True})
        for f in spec.get("figures_made") or []:
            if (d / f["png"]).exists():
                files.append({"name": f["png"], "kind": "figure", "teacher_only": False, "title": f["title"], "no": f["no"]})
        les["files"] = files
        self.set_lecture_file(proj, les, no)
        les["spec_title"] = spec["title"]
        keys = lang_keys(o["languages"])
        les["content"] = {k: self.clean(page.build(spec, k)) for k in keys}

    # talking with the teacher: see lead.py (round 5) -----------------------------------------

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


def anim_texts(code: str) -> list[str]:
    """The words a student sees in an animation: its string literals with letters in them (titles, captions)."""
    out = []
    for q in re.findall(r"""r?(["'])((?:\\.|(?!\1).){2,300})\1""", code or ""):
        t = q[1].strip()
        if re.search(r"[\u4e00-\u9fff]|[A-Za-z]{3,}", t) and not re.fullmatch(r"[\w.]+|#[0-9a-fA-F]{3,8}", t) and t not in out:
            out.append(t)
    return out[:40]


def lab_texts(code: str) -> list[str]:
    """The words a student sees in a lab: its [中文, English] pairs (titles, scenes, tasks)."""
    return anim_texts(code)


def normalize_design_book(d, outline: dict) -> dict:
    d = d if isinstance(d, dict) else {}
    s = lambda k, n=800: str(d.get(k) or "")[:n].strip()  # noqa: E731
    chapters = []
    by_no = {c.get("no"): c for c in d.get("chapters") or [] if isinstance(c, dict)}
    for c in outline.get("chapters") or []:
        x = by_no.get(c["no"]) or {}
        chapters.append({"no": c["no"], "animation": str(x.get("animation") or "")[:500], "lab": str(x.get("lab") or "")[:500],
                         "problems": str(x.get("problems") or "")[:400]})
    return {"subject": s("subject", 200), "audience": s("audience", 200), "textbook": s("textbook", 300),
            "platform": s("platform"), "notation": s("notation"), "visual_style": s("visual_style", 500),
            "chapters": chapters, "avoid": [str(a)[:200] for a in d.get("avoid") or [] if a][:8],
            "library": [{"id": str(x.get("id") or "").strip(), "role": str(x.get("role") or "")[:120]}
                        for x in d.get("library") or [] if isinstance(x, dict) and x.get("id")][:12],
            **({"factory": d["factory"]} if isinstance(d.get("factory"), dict) and d["factory"].get("case") else {}),
            **({"by": "teacher"} if d.get("by") == "teacher" else {})}


def fake_design_book(proj: dict) -> dict:
    o = proj.get("outline") or {}
    return {"subject": disp(o.get("title")) or "课程", "audience": proj["requirements"].get("audience", "本科生"),
            "textbook": proj["requirements"].get("textbook", ""), "platform": "六轴机械臂 + 差速移动机器人（离线示范）",
            "notation": "与主教材一致", "visual_style": "深色背景，坐标系与机构示意，中英字幕",
            "chapters": [{"no": c["no"], "animation": "本章机构与坐标系的动态示意", "lab": "调节本章参数，观察机器人响应",
                          "problems": "本章概念在机器人上的应用"} for c in o.get("chapters") or []],
            "avoid": ["不用其他学科、其他课程的例子"],
            # the built-in sample and the published library; ids the library does not have are dropped afterwards
            "library": [{"id": "B-ARM-6R-S", "role": "贯穿全课的机械臂"}, {"id": "B-MOB-DIFF-S", "role": "移动机器人章节"},
                        {"id": "B-ARM-UR5E", "role": "贯穿全课的机械臂"}, {"id": "B-LEG-GO2", "role": "足式机器人章节"}]}


def named_textbooks(texts: list[str]) -> list[str]:
    """Book titles the teacher named: 《...》, or after 教材 / 课本 / textbook."""
    out: list[str] = []
    for t in texts:
        for name in re.findall(r"《([^《》]{2,60})》", t):
            if name not in out and not re.search(r"大纲|计划|说明|日历", name):
                out.append(name)
        for name in re.findall(r"(?:教材|课本|主教材|textbook)\s*(?:是|为|用|采用|选用|:|：|is)\s*[“\"']?([^\s，。,；;“”\"'《》]{2,40})", t, re.I):
            if name not in out:
                out.append(name)
    return out[:3]


def match_textbook(names: list[str], items: list, titles: dict[str, str], text_of) -> tuple[str, float]:
    """The file that is the named book: the name in its file name, own title or first pages (score 1.0),
    else the best character overlap (0..1)."""
    best, score = "", 0.0
    for m in items:
        hay = norm(m.name) + "|" + norm(titles.get(m.id, "")) + "|" + norm(text_of(m.id))
        for n in names:
            k = norm(n)
            if not k:
                continue
            if k in hay:
                s = 1.0
            else:
                pool = norm(m.name) + norm(titles.get(m.id, ""))
                s = sum(1 for ch in set(k) if ch in pool) / max(1, len(set(k)))
            if s > score or (s == score and best and m.pages > 0):
                best, score = m.id, s
    return best, score


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
    if not chapters:  # no materials at all: build from what the teacher asked for (AI first)
        want = proj["requirements"].get("notes") or proj.get("description") or ""
        for n, (no, name) in enumerate(re.findall(r"第\s*(\d{1,2})\s*章\s*([^\s，,。；;（(]+)", want) or [("1", "")]):
            no = int(no)
            name = name or "课程导论"
            topics = [f"{name}（{k}）" for k in ("一", "二", "三")]
            chapters.append({"no": no, "title": T(f"第{no}章 {name}"), "summary": T(""),
                             "lessons": [{"title": T(f"{no}.{i + 1} {x}"), "goal": T(f"掌握{x}"), "week": week + i, "sections": []}
                                         for i, x in enumerate(topics)]})
            week += len(topics)
        m = re.match(r"\s*([^\s，,。（(第]+)", want)
        title = title or (m.group(1) if m else "")
    return {"title": T(title or mt.course_title(items, text_of)), "summary": T(""), "chapters": chapters}


def fake_spec(les: dict, no: str) -> dict:
    """Offline lecturer: the benchmark-level demo lesson, renamed to this lesson."""
    import copy
    from .production.demo import LESSON_2_1
    s = copy.deepcopy(LESSON_2_1)
    s["title"] = [disp(les["title"], "zh") or s["title"][0], disp(les["title"], "en") or s["title"][1]]
    s.setdefault("figures", [
        {"kind": "graph", "place": "concept", "title": ["本课概念图", "Concept map"], "purpose": ["概念与要点的关系", "How the ideas connect"],
         "asset": "", "data": ""},
        {"kind": "drawing", "place": "problem", "title": ["本课的机器人", "The robot in this lesson"],
         "purpose": ["机构简图与关节编号", "Kinematic sketch with joint numbers"], "asset": "", "data": ""}])
    return s


def fake_figure(fig: dict, spec: dict) -> dict:
    """Offline illustrator: a small, correct figure of the asked kind."""
    t = spec["concept"]["title"]
    pts = spec["concept"]["points"][:4] or [["要点", "Point"]]
    if fig["kind"] == "graph":
        nodes = [{"id": "c", "label": t or ["概念", "Concept"], "emphasis": True}] + \
                [{"id": f"p{i}", "label": p} for i, p in enumerate(pts)]
        return {"graph": {"direction": "TB", "nodes": nodes, "edges": [{"from": "c", "to": f"p{i}"} for i in range(len(pts))]}}
    if fig["kind"] == "chart":
        xs = [i / 10 for i in range(0, 31)]
        return {"chart": {"type": "line", "x_label": ["时间 t（s）", "time t (s)"], "y_label": ["角度 θ（rad）", "angle θ (rad)"],
                          "series": [{"name": ["θ(t)", "θ(t)"], "x": xs, "y": [round(0.5 * x * x, 4) for x in xs]}]}}
    return {"code": "from wq_anim import *\n\n\nclass Lesson(Base):\n    def construct(self):\n"
                    "        self.add(frame2([-3, -1, 0], 0, 1.4, name=r\"\\{A\\}\"), frame2([2, 0, 0], 30, 1.4, name=r\"\\{B\\}\"))\n"}


def fake_plan3d(models: dict, factory: bool = False) -> dict:
    """Offline 3D animator: the factory workshop (then a robot) when the course has a factory case; otherwise a
    showcase when there are several robots, else the first model's typical motion."""
    if factory:
        out = {"template": "workshop", "follow": "agv-01", "highlight": ["cnc-l01-a"],
               "captions": [{"from": 1, "to": 9, "text": ["AGV 把工件送到下一道工序", "AGVs carry parts to the next operation"]}]}
        if models:
            out["also"] = fake_plan3d(models)
        return out
    robots = [k for k, m in models.items() if m["entry"].get("kind") == "robot"]
    if len(robots) >= 2:
        return {"template": "showcase", "items": [{"id": k, "name": list(models[k]["entry"]["name"].values()),
                                                   "line": [((models[k]["entry"].get("teaching") or {}).get("principle") or models[k]["entry"]["name"].get("zh", "")), ""]}
                                                  for k in robots[:4]]}
    k = (robots or list(models))[0]
    e = models[k]["entry"]
    if e.get("kind") == "mechanism":
        return {"template": "mechanism", "item": k}
    demo = e.get("demo") or {}
    return {"template": "joints", "item": k,
            "poses": [{"values": [{"joint": j, "value": v[1]} for j, v in demo.items()]},
                      {"values": [{"joint": j, "value": v[0]} for j, v in demo.items()]}],
            "captions": [{"from": 0, "to": 4, "text": [e["name"].get("zh", ""), e["name"].get("en", "")]}]}


def normalize_plan3d(p: dict, models: dict, factory: bool = False, nested: bool = False) -> dict:
    """Keep only known ids and joints, clamp joint values to their limits, captions to [from, to, [zh, en]];
    `also` = one more clip (not a workshop again)."""
    allowed = ("showcase", "joints", "mechanism", "explode") + (("workshop",) if factory and not nested else ())
    tpl = p.get("template") if p.get("template") in allowed else ("joints" if models else "workshop" if factory else "joints")
    items = [{"id": str(i.get("id")), "name": i.get("name") or ["", ""], "line": i.get("line") or ["", ""]}
             for i in p.get("items") or [] if isinstance(i, dict) and i.get("id") in models][:8]
    item = p.get("item") if p.get("item") in models else next(iter(models), "")
    limits = {j["name"]: (j["lower"], j["upper"]) for j in (models.get(item) or {}).get("entry", {}).get("joints", [])}
    poses = []
    for pose in p.get("poses") or []:
        vals = {}
        for v in (pose or {}).get("values") or []:
            if isinstance(v, dict) and v.get("joint") in limits:
                lo, hi = limits[v["joint"]]
                try:
                    vals[v["joint"]] = min(max(float(v.get("value") or 0), lo), hi)
                except (TypeError, ValueError):
                    continue
        if vals:
            poses.append(vals)
    caps = []
    for c in p.get("captions") or []:
        if isinstance(c, dict) and c.get("text"):
            try:
                caps.append([float(c.get("from") or 0), float(c.get("to") or 0), c["text"]])
            except (TypeError, ValueError):
                continue
    out = {"template": tpl, "items": items, "item": item, "poses": poses[:6], "captions": caps[:6]}
    if tpl == "workshop":
        out["follow"] = str(p.get("follow") or "")[:40]
        out["highlight"] = [str(x)[:40] for x in p.get("highlight") or []][:6]
    if not nested and isinstance(p.get("also"), dict) and p["also"].get("template") and models:
        out["also"] = normalize_plan3d(p["also"], models, factory, True)
    return out


def fake_guide_plan() -> dict:
    from .production.demo import GUIDE_PLAN_2_1
    return GUIDE_PLAN_2_1


def fake_lesson(les: dict, src: str, keys: list[str]) -> dict:
    m = re.search(r"<<< (.+?)\n(.{0,400})", src, re.S)
    cite = f"<p>{html.escape(' '.join(m.group(2).split()))}（参考：{html.escape(m.group(1))}）</p>" if m else ""
    body = (f"<h3>实际问题</h3><p>机器人问题（示例）。</p><h3>概念</h3>{cite}<h3>动画</h3><p>动画说明。</p>"
            f"<h3>虚拟实验</h3><p>实验说明。</p><h3>建模求解</h3><p>求解（示例）。</p>")
    return {"content": {k: body for k in keys}, "summary": disp(les["title"])}


def fake_exercises(keys: list[str]) -> dict:
    return {"questions": {k: "<ol><li>练习一</li><li>练习二</li></ol>" for k in keys},
            "answers": {k: "<ol><li>答案一</li><li>答案二</li></ol>" for k in keys}}
