"""课程负责人 (round 5): talking with the teacher — listen first, say what you understood and what you think, propose,
and act only when the teacher confirms. "Stop" always stops at once.

  reply(pid, text)     answers at once, even while the team is working (its own lane, never queued behind a job);
                       records the teacher's answers to open questions; anything that changes the course or starts
                       work becomes a proposal (提议) with [确认] [不对，我再说]
  confirm(pid, prop)   carries the proposal out, then reports what actually changed (not before)
  cancel(pid, prop)    drops it
Mixed into studio.Studio.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
import uuid

from . import team
from .moodle import EngineError

log = logging.getLogger("wenquest.lead")

# "喊停必停": short commands to stop; a sentence that merely mentions stopping (an AGV's emergency stop) does not count.
STOP = re.compile(r"(停下|停一下|先停|暂停|停止|停住|别写了|不要写了|先别写|先别做|别做了|不要做了|等一下|等等|"
                  r"\bstop\b|hold on|\bpause\b)", re.I)


def is_stop(text: str) -> bool:
    t = text.strip().strip("！!。.，, ")
    return t in ("停", "停停", "stop", "Stop", "STOP") or bool(STOP.search(text)) and len(text) <= 120
DESIGN_FIELDS = {"subject": "学科与层次", "audience": "学生", "textbook": "教材", "platform": "贯穿全课的机器人",
                 "notation": "符号约定", "visual_style": "动画风格"}
BACKGROUND = {"redesign", "remake_design_book", "revise_lesson", "write_lesson", "write_next", "proceed", "reread_textbook"}


def _id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> float:
    return time.time()


def _pair(v) -> dict:
    if isinstance(v, dict):
        return {"zh": str(v.get("zh") or v.get("en") or "").strip()[:200], "en": str(v.get("en") or v.get("zh") or "").strip()[:200]}
    if isinstance(v, (list, tuple)) and v:
        return {"zh": str(v[0] or "")[:200], "en": str((v[1] if len(v) > 1 else v[0]) or "")[:200]}
    return {"zh": str(v or "")[:200], "en": str(v or "")[:200]}


def _disp(t) -> str:
    return (t or {}).get("zh") or (t or {}).get("en") or "" if isinstance(t, dict) else str(t or "")


def chapter_confirmed(c: dict) -> bool:
    """本章确认 (E2): the teacher confirmed this chapter's lessons, or lessons of it were already written before round 5."""
    return bool(c.get("confirmed")) or any(les["status"] != "planned" for les in c.get("lessons") or [])


# --- what the course lead may propose ------------------------------------------------------------------------------

STEP_DOC = """Steps a proposal may contain (JSON objects with "type"):
- set_requirement {key, value}: key one of course_title, audience, level, language (zh|en|both), weeks, sessions_per_week, minutes_per_session, scope, notes
- set_role {file_id, role}: what an uploaded file is (roles as listed in the project state)
- set_textbook {file_id}: an uploaded file is the main textbook
- set_textbook_title {title}: the main textbook is a book that is NOT among the uploaded files (record its title; stop asking which file)
- set_course_title {title: {zh, en}}
- set_chapter {no, title: {zh, en}, lessons: [{id (keep an existing lesson's id when it stays), title: {zh, en}, goal: {zh, en}}]}: create or replace a whole chapter of the outline (published lessons are kept anyway)
- remove_chapter {no}
- confirm_chapter {no}: the teacher confirms this chapter's lesson plan (writing may start only after this)
- redesign {chapters: [no, ...] (empty = whole outline), note}: the course designer redoes the outline following the note
- set_design_book {field, value}: field one of subject, audience, textbook, platform, notation, visual_style
- remake_design_book {note}: the designer rewrites the course design book following the note
- reread_textbook {}: read the main textbook's table of contents again
- revise_lesson {lesson_id, note}: rewrite a written (not published) lesson following the note
- write_lesson {lesson_id}: write this planned lesson now
- write_next {}: write the next planned lesson of a confirmed chapter
- proceed {}: materials stage only — the materials are settled, design the outline
- set_pace {mode: manual|daily, hour}"""

LEAD = team.COMMON + (
    " Role: 课程负责人 (course lead) — the only one who talks to the teacher, and a senior colleague who knows the "
    "subject, not a messenger. For every message: (1) understand what the teacher wants and why; (2) judge it with "
    "your expertise and the project state — if it is sound, say how you will do it; if something is wrong or risky "
    "(the textbook does not fit the course aim, a topic is in the wrong chapter, too few hours, it would break what "
    "is published), say so plainly with the reason and give the better option; the teacher decides; (3) when the "
    "message is ambiguous, ask ONE concrete question and propose nothing yet. Never reply with empty phrases such as "
    "'好的，记下了' and never say something is done — nothing changes until the teacher confirms your proposal. "
    "Anything that changes the course or starts work goes into `proposal` (steps from the list); only answers to the "
    "team's own open questions go into `answers` and take effect at once. If the teacher only asks or discusses, "
    "answer and propose nothing. If the teacher asked to stop, the work has ALREADY been stopped: say so in one "
    "sentence, then give your view (was stopping right? what should change?) and what you propose next. "
    "Reply in the teacher's language, short and concrete (at most 6 sentences)."
)


def lead_schema() -> dict:
    step = {"type": "object", "properties": {"type": {"type": "string"}}, "required": ["type"]}
    return team._obj({"understanding": team.STR, "reply": team.STR, "question": team.STR,
                      "answers": {"type": "array", "items": team._obj({"id": team.STR, "answer": team.STR})},
                      "proposal": {"type": ["object", "null"], "properties": {"summary": team.STR, "steps": {"type": "array", "items": step}}}},
                     ["understanding", "reply"])


class LeadMixin:
    # --- state for the lead's prompt -------------------------------------------------------------------------------
    def lead_state(self, proj: dict) -> str:
        from .studio import summary
        lines = [summary(proj, self.items(proj))]
        m = proj["materials"]
        lines.append(f"Main textbook: file {m.get('textbook') or '(none)'}; book title {m.get('book_title') or proj['requirements'].get('textbook') or '(unknown)'}")
        o = proj.get("outline") or {}
        for c in o.get("chapters") or []:
            lines.append(f"Chapter {c['no']} confirmed by teacher: {'yes' if chapter_confirmed(c) else 'NO'}")
        book = team.design_book_text(proj.get("design_book"))
        if book:
            lines.append("Course design book:\n" + book)
        if proj.get("busy"):
            lines.append(f"The team is working now: {proj['busy']['label']}")
        opens = [p for p in proj.get("proposals") or [] if p["status"] == "open"]
        for p in opens[-4:]:
            lines.append("Your proposal still waiting for the teacher's confirmation: " + "; ".join(p.get("lines") or [p["summary"]]))
        return "\n".join(lines)

    # --- talking ---------------------------------------------------------------------------------------------------
    def chat_lock(self, pid: str) -> asyncio.Lock:
        locks = self.__dict__.setdefault("_chat_locks", {})
        return locks.setdefault(pid, asyncio.Lock())

    async def reply(self, pid: str, text: str) -> None:
        async with self.chat_lock(pid):
            stopped = ""
            if is_stop(text):
                proj = self.projects.load(pid)
                if self.is_busy(pid):
                    label = (proj.get("busy") or {}).get("label", "")
                    self.stop(pid)
                    t = self.tasks.get(pid)
                    if t:
                        try:
                            await asyncio.wait_for(asyncio.shield(t), 10)
                        except (asyncio.CancelledError, asyncio.TimeoutError, Exception):  # noqa: BLE001
                            pass
                    stopped = label or "当前工作"
            proj = self.projects.load(pid)
            history = [x for x in proj["messages"] if x["role"] in ("teacher", "lead")][-14:]
            hist = "\n".join(f"{x['role']}: {x['text'][:700]}" for x in history[:-1])
            prompt = (f"{self.lead_state(proj)}\n\n{STEP_DOC}\n\nRecent conversation:\n{hist}\n\n"
                      + (f"(You have just stopped: {stopped}.)\n" if stopped else "") + f"Teacher: {text}")
            try:
                data = await self.ai.json(system=LEAD, prompt=prompt, schema=lead_schema(), max_tokens=3000,
                                          fake=lambda: fake_lead(proj, text, stopped))
            except Exception as e:  # noqa: BLE001 - say so instead of going quiet
                log.warning("lead reply failed: %s", e)
                proj = self.projects.load(pid)
                self.say(proj, ("已经停下了。" if stopped else "") + "我这次没能处理你的话（模型暂时没有回应），请再发一次。", "lead", "error")
                self.projects.save(proj)
                return
            data = data if isinstance(data, dict) else {}
            proj = self.projects.load(pid)
            for a in data.get("answers") or []:
                q = next((q for q in proj["questions"] if isinstance(a, dict) and q["id"] == a.get("id") and q["status"] == "open"), None)
                if q and a.get("answer"):
                    q["answer"], q["status"] = str(a["answer"])[:500], "answered"
            reply = str(data.get("reply") or "").strip()
            if stopped and "停" not in reply[:30]:
                reply = f"已经停下（{stopped}）。" + reply
            question = str(data.get("question") or "").strip()
            steps = [s for s in ((data.get("proposal") or {}).get("steps") or []) if isinstance(s, dict) and self.step_ok(proj, s)]
            if steps:      # earlier open proposals stay open: each request is confirmed or dropped by the teacher
                prop = {"id": _id(), "summary": str((data.get("proposal") or {}).get("summary") or "")[:400],
                        "steps": steps[:12], "lines": [self.describe(proj, s) for s in steps[:12]], "status": "open",
                        "created": _now(), "result": []}
                proj.setdefault("proposals", []).append(prop)
                self.say_proposal(proj, (reply + ("\n" + question if question else "")).strip(), prop["id"])
            else:
                self.say(proj, (reply + ("\n" + question if question else "")).strip() or "我没听明白，能具体说一下要改哪里吗？", "lead")
            self.projects.save(proj)

    def say_proposal(self, proj: dict, text: str, prop_id: str) -> None:
        proj["messages"].append({"id": _id(), "role": "lead", "text": text, "ts": _now(), "kind": "proposal", "proposal": prop_id})

    # --- checking and describing steps ------------------------------------------------------------------------------
    def step_ok(self, proj: dict, s: dict) -> bool:
        t = s.get("type")
        files = proj["materials"]["files"]
        o = proj.get("outline") or {}
        nos = {c["no"] for c in o.get("chapters") or []}
        lessons = {les["id"]: les for c in o.get("chapters") or [] for les in c["lessons"]}
        if t == "set_requirement":
            return s.get("key") in ("course_title", "audience", "level", "language", "weeks", "sessions_per_week",
                                    "minutes_per_session", "scope", "notes") and s.get("value") not in (None, "")
        if t == "set_role":
            return s.get("file_id") in files and s.get("role") in team.ROLES
        if t == "set_textbook":
            return s.get("file_id") in files
        if t == "set_textbook_title":
            return bool(str(s.get("title") or "").strip())
        if t in ("set_course_title",):
            return bool(o) and bool(_disp(_pair(s.get("title"))))
        if t == "set_chapter":
            return bool(o) and bool(_disp(_pair(s.get("title")))) and isinstance(s.get("lessons"), list) and bool(s["lessons"])
        if t in ("remove_chapter", "confirm_chapter"):
            return _int(s.get("no")) in nos
        if t == "redesign":
            return bool(o) or proj["stage"] in ("materials", "outline")
        if t == "set_design_book":
            return s.get("field") in DESIGN_FIELDS and bool(str(s.get("value") or "").strip())
        if t == "remake_design_book":
            return bool(o)
        if t == "reread_textbook":
            return bool(proj["materials"].get("textbook"))
        if t == "revise_lesson":
            les = lessons.get(str(s.get("lesson_id")))
            return bool(les) and les["status"] in ("awaiting", "failed")
        if t == "write_lesson":
            les = lessons.get(str(s.get("lesson_id")))
            return bool(les) and les["status"] in ("planned", "failed")
        if t == "write_next":
            return proj["stage"] == "lessons"
        if t == "proceed":
            return proj["stage"] == "materials"
        if t == "set_pace":
            return s.get("mode") in ("manual", "daily")
        return False

    def describe(self, proj: dict, s: dict) -> str:
        t = s["type"]
        lessons = {les["id"]: les for c in (proj.get("outline") or {}).get("chapters") or [] for les in c["lessons"]}
        files = proj["materials"]["files"]
        fname = lambda fid: (files.get(fid) or {}).get("title") or next((x.path for x in self.items(proj) if x.id == fid), fid)  # noqa: E731
        if t == "set_requirement":
            return f"要求：{s['key']} 改为 {s['value']}"
        if t == "set_role":
            return f"资料《{fname(s['file_id'])}》改为：{team.ROLES.get(s['role'], s['role'])}"
        if t == "set_textbook":
            return f"主教材改为《{fname(s['file_id'])}》"
        if t == "set_textbook_title":
            return f"主教材记为《{str(s['title']).strip('《》')}》（资料里没有这本书，不再追问是哪份文件）"
        if t == "set_course_title":
            return f"课程名改为“{_disp(_pair(s['title']))}”"
        if t == "set_chapter":
            names = "；".join(_disp(_pair(x.get("title"))) for x in s["lessons"] if isinstance(x, dict))
            return f"第 {s.get('no')} 章改为“{_disp(_pair(s['title']))}”：{names}"
        if t == "remove_chapter":
            return f"删除第 {s['no']} 章（已发布的课时保留）"
        if t == "confirm_chapter":
            return f"确认第 {s['no']} 章的课时安排，可以开始写"
        if t == "redesign":
            which = "、".join(f"第 {n} 章" for n in s.get("chapters") or []) or "整份大纲"
            return f"课程设计师按你的要求重做{which}：{str(s.get('note') or '')[:200]}"
        if t == "set_design_book":
            return f"课程设计书“{DESIGN_FIELDS[s['field']]}”改为：{str(s['value'])[:200]}"
        if t == "remake_design_book":
            return f"重写课程设计书：{str(s.get('note') or '')[:200]}"
        if t == "reread_textbook":
            return "重新读主教材的目录"
        if t == "revise_lesson":
            return f"按意见重写《{_disp(lessons[s['lesson_id']]['title'])}》：{str(s.get('note') or '')[:200]}"
        if t == "write_lesson":
            return f"开始写《{_disp(lessons[s['lesson_id']]['title'])}》"
        if t == "write_next":
            return "写下一课"
        if t == "proceed":
            return "资料清单定下来，开始设计大纲"
        if t == "set_pace":
            return "改为每天自动写一课" if s["mode"] == "daily" else "改为手动：你说写才写"
        return t

    # --- confirming ---------------------------------------------------------------------------------------------------
    def proposal(self, proj: dict, prop_id: str) -> dict:
        p = next((x for x in proj.get("proposals") or [] if x["id"] == prop_id), None)
        if not p:
            raise EngineError("not_found", "no such proposal", 404)
        if p["status"] != "open":
            raise EngineError("proposal_closed", "this proposal is no longer open", 409)
        return p

    def cancel_proposal(self, pid: str, prop_id: str) -> dict:
        proj = self.projects.load(pid)
        p = self.proposal(proj, prop_id)
        p["status"] = "cancelled"
        self.say(proj, "好，这个提议不做了。你再说说想怎么改。", "lead")
        self.projects.save(proj)
        return proj

    def confirm_proposal(self, pid: str, prop_id: str) -> dict:
        """Carry the proposal out. Immediate changes first; the one piece of background work (if any) then starts."""
        if self.is_busy(pid):
            raise EngineError("team_busy", "the team is working; stop it first", 409)
        proj = self.projects.load(pid)
        p = self.proposal(proj, prop_id)
        results, job = [], None
        for s in p["steps"]:
            if not self.step_ok(proj, s):
                results.append(f"✗ {self.describe(proj, s) if s.get('type') else s}（现在做不了：条件变了）")
                continue
            if s["type"] in BACKGROUND:
                if job is None:
                    job = s
                    results.append(f"▶ {self.describe(proj, s)}（已开始）")
                else:
                    results.append(f"… {self.describe(proj, s)}（等上一项做完再说）")
                continue
            try:
                note = self.apply_step(proj, s)
                results.append(f"✓ {self.describe(proj, s)}" + (f"（{note}）" if note else ""))
            except EngineError as e:
                results.append(f"✗ {self.describe(proj, s)}（{e}）")
        p["status"], p["result"], p["done"] = "done", results, _now()
        self.say(proj, "已按你确认的做了：\n" + "\n".join(results), "lead", "done")
        self.projects.save(proj)
        if job:
            self.run(proj, self.describe(proj, job), lambda pr, s=job: self.run_step(pr, s))
        return self.projects.load(pid)

    def apply_step(self, proj: dict, s: dict) -> str:
        t = s["type"]
        files = proj["materials"]["files"]
        o = proj.get("outline") or {}
        if t == "set_requirement":
            val = str(s["value"])[:1000]
            if s["key"] == "language":
                val = {"中文": "zh", "英文": "en", "中英双语": "both", "双语": "both"}.get(val, val)
                val = val if val in ("zh", "en", "both") else "both"
            proj["requirements"][s["key"]] = val
            return ""
        if t == "set_role":
            files[s["file_id"]].update(role=s["role"], by="teacher", confidence="high")
            return ""
        if t in ("set_textbook", "set_textbook_title"):
            for f in files.values():
                if f["role"] == "main_textbook":
                    f["role"] = "aux_textbook"
            if t == "set_textbook":
                files[s["file_id"]].update(role="main_textbook", by="teacher", confidence="high")
                proj["materials"]["textbook"] = s["file_id"]
                proj["materials"]["book_title"] = files[s["file_id"]].get("title", "")
            else:
                title = str(s["title"]).strip().strip("《》")[:200]
                proj["materials"]["textbook"] = ""
                proj["materials"]["book_title"] = title
                proj["requirements"]["textbook"] = title
            proj["materials"]["toc"] = []
            for q in proj["questions"]:
                if q["status"] == "open" and "教材" in q["text"]:
                    q["status"] = "dropped"
            if proj.get("design_book"):
                proj["design_book"]["textbook"] = proj["materials"]["book_title"]
            return "大纲和设计书还是按原来的教材做的；要不要按新教材重做，你说一声我再提"
        if t == "set_course_title":
            o["title"] = _pair(s["title"])
            return ""
        if t == "set_chapter":
            self.set_chapter(proj, s)
            return "这一章需要你再点“本章确认”才会开写"
        if t == "remove_chapter":
            no = _int(s["no"])
            ch = next(c for c in o["chapters"] if c["no"] == no)
            if any(les["status"] == "published" for les in ch["lessons"]):
                raise EngineError("published", "这一章有已发布的课时，不能删")
            o["chapters"] = [c for c in o["chapters"] if c["no"] != no]
            for i, c in enumerate(o["chapters"], 1):
                c["no"] = i
            return ""
        if t == "confirm_chapter":
            ch = next(c for c in o["chapters"] if c["no"] == _int(s["no"]))
            ch["confirmed"] = True
            return ""
        if t == "set_design_book":
            book = proj.setdefault("design_book", {})
            book[s["field"]] = str(s["value"])[:800]
            book["by"] = "teacher"
            return ""
        if t == "set_pace":
            proj["pace"]["mode"] = s["mode"]
            if isinstance(s.get("hour"), int) and 0 <= s["hour"] <= 23:
                proj["pace"]["hour"] = s["hour"]
            return ""
        raise EngineError("unknown_step", t)

    def set_chapter(self, proj: dict, s: dict) -> None:
        from .studio import new_id
        o = proj["outline"]
        keys = [k for k in ("zh", "en") if o.get("languages") in (k, "both")] or ["zh"]
        T = lambda v: {k: _pair(v)[k] for k in keys}  # noqa: E731
        no = _int(s.get("no")) or len(o["chapters"]) + 1
        old = next((c for c in o["chapters"] if c["no"] == no), None)
        all_lessons = {les["id"]: les for c in o["chapters"] for les in c["lessons"]}
        kept = [les for les in (old or {}).get("lessons", []) if les["status"] == "published"]
        lessons = list(kept)
        for x in s["lessons"][:12]:
            if not isinstance(x, dict):
                continue
            base = all_lessons.get(str(x.get("id") or ""))
            if base and base["status"] == "published":
                continue
            if base:   # moved here from another chapter or kept
                for c in o["chapters"]:
                    if c is not old:
                        c["lessons"] = [les for les in c["lessons"] if les["id"] != base["id"]]
            else:
                base = {"id": new_id(), "status": "planned", "content": {}, "exercises": {}, "answers": {}, "review": None,
                        "notes": "", "cmids": [], "error": "", "week": 0, "sections": [], "problem": {}}
            base.update(title=T(x.get("title")), goal=T(x.get("goal") or base.get("goal") or ""))
            lessons.append(base)
        chapter = {"id": (old or {}).get("id") or new_id(), "no": no, "title": T(s["title"]),
                   "summary": (old or {}).get("summary") or T(""), "lessons": lessons, "confirmed": False}
        if old:
            o["chapters"][o["chapters"].index(old)] = chapter
        else:
            o["chapters"].append(chapter)
            o["chapters"].sort(key=lambda c: c["no"])

    async def run_step(self, proj: dict, s: dict) -> None:
        t = s["type"]
        if t == "redesign":
            await self.redesign(proj, [n for n in (_int(x) for x in s.get("chapters") or []) if n], str(s.get("note") or ""))
        elif t == "remake_design_book":
            if proj.get("design_book"):
                proj["design_book"].pop("by", None)
            note = str(s.get("note") or "")
            if note:
                proj["requirements"]["notes"] = (proj["requirements"].get("notes", "") + "\n" + note).strip()[:4000]
            await self.make_design_book(proj)
            self.say(proj, "课程设计书按你的要求重写好了，请在右边看。", "lead", "report")
        elif t == "reread_textbook":
            await self.reread_contents(proj)
        elif t == "revise_lesson":
            await self.write_lesson(proj, s["lesson_id"], str(s.get("note") or ""))
        elif t == "write_lesson":
            chapter, _ = self.find_lesson(proj, s["lesson_id"])
            if not chapter_confirmed(chapter):
                self.say(proj, f"第 {chapter['no']} 章的课时安排还没确认，先不写。请先看一下大纲，点“本章确认”。", "lead")
                return
            await self.write_lesson(proj, s["lesson_id"])
        elif t == "write_next":
            nxt = self.next_lesson(proj)
            if not nxt:
                self.say(proj, self.nothing_to_write(proj), "lead")
                return
            await self.write_lesson(proj, nxt[1]["id"])
        elif t == "proceed":
            await self.design(proj)

    def nothing_to_write(self, proj: dict) -> str:
        pending = [c for c in (proj.get("outline") or {}).get("chapters", []) if not chapter_confirmed(c)
                   and any(les["status"] in ("planned", "failed") for les in c["lessons"])]
        if pending:
            return f"第 {pending[0]['no']} 章的课时安排还没确认。请看一下这一章的大纲，没问题就点“本章确认”，我再开始写。"
        return "所有课时都写好了。"

    async def redesign(self, proj: dict, chapters: list[int], note: str) -> None:
        """The designer redoes the outline (or some chapters) following the teacher's note; published lessons stay."""
        from .studio import check_outline, fake_outline, lang_keys, summary
        items = self.items(proj)
        keys = lang_keys(proj["requirements"].get("language", "both"))
        toc = proj["materials"]["toc"]
        toc_text = "\n".join(f"Chapter {c['no']} {c['title']}\n" + "\n".join(f"  {s['no']} {s['title']}" for s in c["sections"]) for c in toc)
        cur = proj.get("outline") or {}
        current = "\n".join(f"Chapter {c['no']} {_disp(c['title'])}: " + "; ".join(_disp(les["title"]) for les in c["lessons"])
                            for c in cur.get("chapters") or [])
        which = ("chapters " + ", ".join(map(str, chapters))) if chapters else "the whole outline"
        feedback = (f"The teacher asked you to redo {which}. The teacher's instructions (binding):\n{note}\n\n"
                    f"Main textbook: {proj['materials'].get('book_title') or proj['requirements'].get('textbook') or '(none)'}\n"
                    f"Current outline:\n{current}")
        data = await self.ai.json(system=team.DESIGNER, prompt=team.outline_prompt(summary(proj, items, False), toc_text,
                                                                                   self.designer_extra(proj, items), feedback),
                                  schema=team.outline_schema(keys), max_tokens=12000,
                                  fake=lambda: fake_outline(proj, items, keys, lambda f: self.text(proj, f)))
        new = self.build_outline(proj, data, keys)
        if not cur.get("chapters"):
            proj["outline"] = new
        else:
            by_no = {c["no"]: c for c in new["chapters"]}
            out = []
            nos = sorted({c["no"] for c in cur["chapters"]} | set(by_no)) if not chapters else [c["no"] for c in cur["chapters"]]
            for no in nos:
                old = next((c for c in cur["chapters"] if c["no"] == no), None)
                if (chapters and no not in chapters) or no not in by_no:
                    if old and (chapters or no in by_no or any(les["status"] == "published" for les in old["lessons"])):
                        out.append(old)
                    continue
                fresh = by_no[no]
                kept = [les for les in (old or {}).get("lessons", []) if les["status"] in ("published", "awaiting")]
                fresh["lessons"] = kept + [les for les in fresh["lessons"]
                                           if _disp(les["title"]) not in {_disp(k["title"]) for k in kept}]
                fresh["id"] = (old or {}).get("id") or fresh["id"]
                fresh["confirmed"] = False
                out.append(fresh)
            cur["chapters"] = out
            if not chapters:
                cur["title"] = new.get("title") or cur.get("title")
            proj["outline"] = cur
        problems = check_outline(proj["outline"])
        msg = f"大纲已按你的要求重做（{'第 ' + '、'.join(map(str, chapters)) + ' 章' if chapters else '整份大纲'}），请在右边“大纲与日历”里看。"
        if proj["stage"] == "lessons":
            msg += " 改过的章需要你点“本章确认”才会开写。"
        if problems:
            msg += "\n还有几处请特别看一下：\n" + "\n".join(f"· {p}" for p in problems[:5])
        self.say(proj, msg, "lead", "report")


def _int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def fake_lead(proj: dict, text: str, stopped: str) -> dict:
    """The offline stand-in: understands a few phrasings used in the tests."""
    if stopped:
        return {"understanding": "老师要停下", "reply": "已经停下了。你觉得哪里不对？我先听你说。", "question": ""}
    m = re.search(r"主教材(?:应该)?是《([^》]+)》", text)
    if m:
        files = proj["materials"]["files"]
        hit = next((fid for fid, f in files.items() if m.group(1) in (f.get("title") or "")), "")
        step = {"type": "set_textbook", "file_id": hit} if hit else {"type": "set_textbook_title", "title": m.group(1)}
        return {"understanding": "换主教材", "reply": f"明白，你要把主教材换成《{m.group(1)}》。换了以后大纲最好按它重排第 1 章。",
                "proposal": {"summary": "换主教材", "steps": [step]}}
    m = re.search(r"第\s*(\d+)\s*章.*?改成[:：]?(.+)", text)
    if m:
        names = [x.strip() for x in re.split(r"[；;，,、]\s*", m.group(2)) if x.strip()]
        return {"understanding": "改一章", "reply": f"好的，第 {m.group(1)} 章按你说的排成 {len(names)} 次课。",
                "proposal": {"summary": "改第一章", "steps": [{"type": "set_chapter", "no": int(m.group(1)), "title": {"zh": "导论", "en": "Introduction"},
                                                            "lessons": [{"title": {"zh": n, "en": n}} for n in names]}]}}
    if re.search(r"确认.*第\s*\d+\s*章|第\s*\d+\s*章.*确认", text):
        no = int(re.search(r"(\d+)", text).group(1))
        return {"understanding": "确认本章", "reply": "好，确认后就可以开写这一章。", "proposal": {"summary": "确认", "steps": [{"type": "confirm_chapter", "no": no}]}}
    if re.search(r"写下一课", text):
        return {"understanding": "写下一课", "reply": "好，确认后开始写。", "proposal": {"summary": "写", "steps": [{"type": "write_next"}]}}
    return {"understanding": "", "reply": "你是想改哪一部分？是大纲、教材，还是某一课？", "question": ""}
