"""课程负责人 · 专家版 (round 5 step 2): the course lead is Claude itself — a senior professor who has read the
textbook, thinks before answering, looks things up with tools, and proposes concrete plans. The programme keeps only
three rules: changes and work need the teacher's confirmation (proposals), "stop" stops at once, published lessons
stay as they are.

  expert_reply(pid, text, stopped)   one turn of the conversation (Claude, extended thinking, tools)
  study_textbook(proj)               教材研读笔记: chapter by chapter, with page numbers (or from the model's own
                                     knowledge of the book, marked 未见原书, when the book was not uploaded)
Mixed into studio.Studio (after LeadMixin).
"""
from __future__ import annotations

import html as htmlmod
import json
import logging
import re

from . import team
from .lead import BACKGROUND, STEP_DOC, _id, _int, _now, chapter_confirmed

log = logging.getLogger("wenquest.expert")

EXPERT = (
    "You are 课程负责人, the course lead of WenQuest's AI professor team: a senior professor of this course's subject "
    "and an experienced curriculum designer, working with the teacher who owns the course. You have authority and use "
    "it: read the textbook and materials before you advise (use the tools — never guess what a book says; if your "
    "textbook notes do not cover what is asked, read the pages and save notes first), think the problem through, "
    "then answer like a professor: what you found, your judgement, and a concrete plan (lessons, goals, textbook "
    "sections and pages, the robot problem for each lesson). If the current course is built on a wrong basis (wrong "
    "textbook, wrong level, a muddled chapter), say so and propose to redo it — even to start over. Disagree with the "
    "teacher when you have reasons, say them, and offer the better option; the teacher decides.\n\n"
    "Rules you must keep:\n"
    "1. Nothing in the course changes until the teacher confirms: to change the course or start work, call the "
    "`propose` tool with the exact steps; your reply then explains the proposal. Never claim something is done.\n"
    "2. If you were told the teacher asked to stop, the work has already been stopped: say so in one sentence, then "
    "discuss.\n"
    "3. Published lessons are never changed.\n"
    "4. Never invent page numbers, facts about a book or data; say when you have not seen the book itself.\n"
    "Write to the teacher in their language (Chinese unless they write English), plainly, without flattery or filler. "
    "Long answers are fine when the question needs them; use short paragraphs or a numbered plan.\n\n" + STEP_DOC + "\n"
    "- start_over {note}: re-read the textbook (new notes), redo the course design book and the whole outline following "
    "the note; published lessons stay, written-but-unpublished lessons go back to 'to be written'\n"
    "- study_textbook {}: (re)write the textbook notes for every chapter"
)

TOOLS = [
    {"name": "list_materials", "description": "The teacher's uploaded files: id, name, role, chapters, pages.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "textbook_contents", "description": "The main textbook's table of contents with start pages (if it was read).",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "read_pages", "description": "Read pages of an uploaded file (PDFs have page numbers; other files: use part=1,2,... "
                                          "for successive 12000-character parts). At most 15 pages per call.",
     "input_schema": {"type": "object", "properties": {"file_id": {"type": "string"}, "from_page": {"type": "integer"},
                                                       "to_page": {"type": "integer"}, "part": {"type": "integer"}},
                      "required": ["file_id"]}},
    {"name": "search_materials", "description": "Find a word or phrase in the uploaded files; returns snippets with page numbers.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "file_id": {"type": "string"}},
                      "required": ["query"]}},
    {"name": "get_notes", "description": "Your textbook notes (教材研读笔记), all chapters or one.",
     "input_schema": {"type": "object", "properties": {"chapter": {"type": "integer"}}}},
    {"name": "save_notes", "description": "Save or replace your notes on one textbook chapter (what it teaches, key concepts and "
                                          "formulas with page numbers, notation, worked examples, prerequisites, robot problems "
                                          "that fit, suggested lessons). The teacher can read them.",
     "input_schema": {"type": "object", "properties": {"chapter": {"type": "integer"}, "title": {"type": "string"},
                                                       "notes": {"type": "string"}, "seen_book": {"type": "boolean"}},
                      "required": ["chapter", "title", "notes"]}},
    {"name": "get_outline", "description": "The course outline: chapters (confirmed or not), lessons with id, title, goal, "
                                           "textbook sections, week and status.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_design_book", "description": "The course design book (subject, audience, textbook, robot platform, notation, "
                                               "per-chapter animations and labs).",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_lesson", "description": "A written lesson: notes text, exercises, the reviewer's verdict and checklist.",
     "input_schema": {"type": "object", "properties": {"lesson_id": {"type": "string"}}, "required": ["lesson_id"]}},
    {"name": "propose", "description": "Propose changes or work; the teacher sees a card and must confirm. `steps` as listed "
                                       "in the system prompt. Returns the proposal id, or which steps are not possible now.",
     "input_schema": {"type": "object", "properties": {"summary": {"type": "string"},
                                                       "steps": {"type": "array", "items": {"type": "object"}}},
                      "required": ["summary", "steps"]}},
]

TOOL_LABEL = {"list_materials": "正在看资料清单", "textbook_contents": "正在看教材目录", "read_pages": "正在查阅资料",
              "search_materials": "正在资料里查找", "get_notes": "正在看教材研读笔记", "save_notes": "正在写教材研读笔记",
              "get_outline": "正在看大纲", "get_design_book": "正在看课程设计书", "get_lesson": "正在看已写的课",
              "propose": "正在整理方案"}

NOTES_SCHEMA = {"type": "object", "properties": {
    "chapters": {"type": "array", "items": {"type": "object", "properties": {
        "chapter": {"type": "integer"}, "title": {"type": "string"}, "notes": {"type": "string"}},
        "required": ["chapter", "title", "notes"]}}}, "required": ["chapters"]}

STUDY = (
    "You are the course lead, a senior professor, reading the course's main textbook before planning the course. "
    "For the chapter given, write study notes in Chinese (keep technical terms and symbols as in the book): 1) what the "
    "chapter teaches and why it matters in this course; 2) key concepts, definitions and formulas, each with its page; "
    "3) the book's notation; 4) worked examples and exercises worth using (pages); 5) prerequisites and what later "
    "chapters build on it; 6) robotics problems that fit (concrete, with numbers); 7) suggested lessons (titles, goals, "
    "sections and pages). Only what the pages say — no invented page numbers."
)


def strip_html(h: str) -> str:
    return htmlmod.unescape(re.sub(r"<[^>]+>", " ", h or "")).replace("\xa0", " ")


class ExpertMixin:
    def lead_v2_on(self, proj: dict) -> bool:
        return bool(proj.get("lead_v2")) and getattr(self.ai, "agentic", False)

    @property
    def lead_model(self) -> str:
        return getattr(self, "_lead_model", "") or ""

    def set_lead_status(self, pid: str, label: str) -> None:
        self.__dict__.setdefault("lead_status", {})[pid] = label

    # --- one turn ------------------------------------------------------------------------------------------------
    async def expert_reply(self, pid: str, text: str, stopped: str) -> None:
        proj = self.projects.load(pid)
        made: list[str] = []
        self.set_lead_status(pid, "正在思考")

        async def run_tool(name: str, inp: dict) -> str:
            nonlocal proj
            proj = self.projects.load(pid)
            out = await self.expert_tool(proj, name, inp, made)
            if name in ("save_notes", "propose"):
                self.projects.save(proj)
            return out

        async def on_step(name: str, inp: dict) -> None:
            label = TOOL_LABEL.get(name, "正在思考")
            if name == "read_pages" and inp.get("from_page"):
                label += f"（第 {inp.get('from_page')}–{inp.get('to_page') or inp.get('from_page')} 页）"
            self.set_lead_status(pid, label)

        msgs = self.expert_messages(proj, text, stopped)
        try:
            reply = await self.ai.agent(system=EXPERT + "\n\nProject at a glance:\n" + self.expert_glance(proj), messages=msgs,
                                        tools=TOOLS, run_tool=run_tool, on_step=on_step, model=self.lead_model)
        except Exception as e:  # noqa: BLE001 - say so instead of going quiet
            log.warning("expert lead failed: %s", e)
            proj = self.projects.load(pid)
            self.say(proj, ("已经停下了。" if stopped else "") + f"我这次没能处理你的话（{getattr(e, 'code', type(e).__name__)}），请再发一次。",
                     "lead", "error")
            self.projects.save(proj)
            return
        finally:
            self.set_lead_status(pid, "")
        proj = self.projects.load(pid)
        if stopped and "停" not in reply[:40]:
            reply = f"已经停下（{stopped}）。\n" + reply
        if made:
            self.say_proposal(proj, reply or "我的方案见下面的提议。", made[0])
            for extra in made[1:]:
                p = next(x for x in proj["proposals"] if x["id"] == extra)
                self.say_proposal(proj, p["summary"] or "另一项提议", extra)
        else:
            self.say(proj, reply or "我还需要你说得具体一点：你想改哪一部分？", "lead")
        self.projects.save(proj)

    def expert_glance(self, proj: dict) -> str:
        m = proj["materials"]
        o = proj.get("outline") or {}
        lines = [f"Stage: {proj['stage']}", f"Requirements: {json.dumps(proj['requirements'], ensure_ascii=False)[:1500]}",
                 f"Main textbook: file {m.get('textbook') or '(none)'}; title {m.get('book_title') or proj['requirements'].get('textbook') or '(unknown)'}",
                 f"Textbook notes written for chapters: {sorted((proj.get('textbook_notes') or {}).keys()) or 'none yet'}"]
        if o:
            lines.append(f"Outline: {strip_html(json.dumps(o.get('title'), ensure_ascii=False))}, {len(o.get('chapters') or [])} chapters")
        if proj.get("busy"):
            lines.append(f"The team is working now: {proj['busy']['label']}")
        opens = [p for p in proj.get("proposals") or [] if p["status"] == "open"]
        for p in opens[-4:]:
            lines.append("Your proposal waiting for confirmation: " + "; ".join(p.get("lines") or [p["summary"]]))
        qs = [q for q in proj["questions"] if q["status"] == "open"]
        if qs:
            lines.append("Open questions shown to the teacher: " + "; ".join(q["text"] for q in qs[:5]))
        return "\n".join(lines)

    def expert_messages(self, proj: dict, text: str, stopped: str) -> list[dict]:
        """The whole conversation as Claude sees it: teacher = user, lead = assistant; system notes folded in."""
        out: list[dict] = []
        for x in proj["messages"][-60:]:
            if x["role"] == "teacher":
                role, t = "user", x["text"]
            elif x["role"] == "lead":
                role, t = "assistant", x["text"]
            else:
                role, t = "user", f"[系统消息] {x['text']}"
            if out and out[-1]["role"] == role:
                out[-1]["content"] += "\n\n" + t
            else:
                out.append({"role": role, "content": t})
        while out and out[0]["role"] != "user":
            out.pop(0)
        last = (f"[已按老师的要求停下了：{stopped}]\n" if stopped else "") + text
        if out and out[-1]["role"] == "user":
            if out[-1]["content"].endswith(text):
                out[-1]["content"] = out[-1]["content"][: -len(text)] + last
            else:
                out[-1]["content"] += "\n\n" + last
        else:
            out.append({"role": "user", "content": last})
        return out

    # --- tools ---------------------------------------------------------------------------------------------------------
    async def expert_tool(self, proj: dict, name: str, inp: dict, made: list[str]) -> str:
        from .studio import pages_of
        items = {x.id: x for x in self.items(proj)}
        files = proj["materials"]["files"]
        if name == "list_materials":
            return "\n".join(f"{fid} | {items[fid].path if fid in items else f.get('title', '')} | {team.ROLES.get(f['role'], f['role'])} | "
                             f"chapters {f.get('chapters') or '-'} | pages {getattr(items.get(fid), 'pages', 0)}"
                             for fid, f in files.items()) or "(no files)"
        if name == "textbook_contents":
            toc = proj["materials"].get("toc") or []
            if not toc:
                return "(the main textbook's contents have not been read; there may be no uploaded textbook)"
            return "\n".join(f"Chapter {c['no']} {c['title']} (p.{c.get('start')})\n" + "\n".join(
                f"  {s['no']} {s['title']} (p.{s.get('start')})" for s in c["sections"]) for c in toc)
        if name == "read_pages":
            fid = str(inp.get("file_id") or "")
            if fid not in items:
                return "ERROR: no such file id; call list_materials"
            text = self.text(proj, fid)
            pages = pages_of(text)
            if pages and inp.get("from_page"):
                a = int(inp["from_page"])
                b = min(int(inp.get("to_page") or a), a + 14)
                return "\n\n".join(f"=== 第 {n} 页 ===\n{pages.get(n, '(empty)')}" for n in range(a, b + 1))
            part = max(1, int(inp.get("part") or 1))
            chunk = text[(part - 1) * 12000: part * 12000]
            more = len(text) > part * 12000
            return (chunk or "(nothing more)") + (f"\n\n[part {part}; more: part={part + 1}]" if more else "\n\n[end]")
        if name == "search_materials":
            q = str(inp.get("query") or "").strip()
            if not q:
                return "ERROR: empty query"
            hits = []
            for fid in ([inp["file_id"]] if inp.get("file_id") in items else list(items)):
                text = self.text(proj, fid)
                pages = pages_of(text) or {0: text}
                for n, t in pages.items():
                    for mm in re.finditer(re.escape(q), t, re.I):
                        s = max(0, mm.start() - 160)
                        hits.append(f"{fid} {items[fid].name} p.{n}: …{' '.join(t[s:mm.end() + 220].split())}…")
                        break
                    if len(hits) >= 15:
                        break
            return "\n".join(hits) or "(not found)"
        if name == "get_notes":
            notes = proj.get("textbook_notes") or {}
            ch = inp.get("chapter")
            sel = {k: v for k, v in notes.items() if ch is None or str(ch) == k}
            return "\n\n".join(f"## 第 {k} 章 {v['title']}{'' if v.get('seen_book', True) else '（未见原书）'}\n{v['notes']}"
                               for k, v in sorted(sel.items(), key=lambda kv: int(kv[0]))) or "(no notes yet)"
        if name == "save_notes":
            ch = _int(inp.get("chapter"))
            if not ch:
                return "ERROR: chapter must be a number"
            proj.setdefault("textbook_notes", {})[str(ch)] = {"title": str(inp.get("title") or "")[:200], "notes": str(inp.get("notes") or "")[:20000],
                                                             "seen_book": bool(inp.get("seen_book", True)), "at": _now()}
            return f"saved notes for chapter {ch}"
        if name == "get_outline":
            o = proj.get("outline") or {}
            if not o:
                return "(no outline yet)"
            return "\n".join(f"Chapter {c['no']} {c['title']} — {'confirmed' if chapter_confirmed(c) else 'NOT confirmed'}\n" + "\n".join(
                f"  [{les['id']}] {les['title']} | goal {les.get('goal')} | sections {les.get('sections')} | week {les.get('week')} | {les['status']}"
                for les in c["lessons"]) for c in o.get("chapters") or [])
        if name == "get_design_book":
            return team.design_book_text(proj.get("design_book")) or "(no design book yet)"
        if name == "get_lesson":
            try:
                _, les = self.find_lesson(proj, str(inp.get("lesson_id")))
            except Exception:  # noqa: BLE001
                return "ERROR: no such lesson id; call get_outline"
            body = strip_html((les.get("content") or {}).get("zh") or (les.get("content") or {}).get("en") or "")
            return (f"{les['title']} — {les['status']}\nReview: {json.dumps(les.get('review'), ensure_ascii=False)[:1500]}\n"
                    f"Checklist: {json.dumps([{k: c.get(k) for k in ('label', 'ok', 'note')} for c in les.get('checklist') or []], ensure_ascii=False)[:1500]}\n"
                    f"Notes text:\n{' '.join(body.split())[:12000]}")
        if name == "propose":
            steps = [s for s in inp.get("steps") or [] if isinstance(s, dict)]
            ok = [s for s in steps if self.step_ok(proj, s) or s.get("type") in ("start_over", "study_textbook")]
            bad = [s for s in steps if s not in ok]
            if not ok:
                return "ERROR: none of these steps is possible now: " + json.dumps(bad, ensure_ascii=False)[:1500]
            prop = {"id": _id(), "summary": str(inp.get("summary") or "")[:600], "steps": ok[:16],
                    "lines": [self.describe_step(proj, s) for s in ok[:16]], "status": "open", "created": _now(), "result": []}
            proj.setdefault("proposals", []).append(prop)
            made.append(prop["id"])
            return f"proposal {prop['id']} shown to the teacher" + (f"; not possible now: {json.dumps(bad, ensure_ascii=False)[:800]}" if bad else "")
        return f"ERROR: unknown tool {name}"

    def describe_step(self, proj: dict, s: dict) -> str:
        if s.get("type") == "start_over":
            return f"推倒重来：重读教材、重做课程设计书和整份大纲（已发布的课保留，待审的课改为待重写）：{str(s.get('note') or '')[:300]}"
        if s.get("type") == "study_textbook":
            return "重新研读主教材，逐章写教材研读笔记"
        return self.describe(proj, s)

    # --- 教材研读 -------------------------------------------------------------------------------------------------------
    async def study_textbook(self, proj: dict) -> None:
        """Notes on every chapter of the main textbook, from its pages (or from the model's knowledge of the book)."""
        from .studio import pages_of
        title = proj["materials"].get("book_title") or proj["requirements"].get("textbook") or ""
        tb = proj["materials"].get("textbook")
        toc = proj["materials"].get("toc") or []
        notes = proj.setdefault("textbook_notes", {})
        if tb and toc:
            pages = pages_of(self.text(proj, tb))
            for c in toc:
                proj["busy"] = {"label": f"课程负责人正在研读教材第 {c['no']} 章：{c['title']}", "since": _now()}
                self.projects.save(proj)
                a, b = c.get("start") or 0, c.get("end") or (c.get("start") or 0) + 30
                text = "\n".join(f"=== 第 {n} 页 ===\n{pages.get(n, '')}" for n in range(a, min(b, a + 60) + 1) if pages.get(n))[:90000]
                if not text:
                    continue
                prompt = (f"Course: {json.dumps(proj['requirements'], ensure_ascii=False)[:800]}\nTextbook: {title}\n"
                          f"Chapter {c['no']} {c['title']} — sections: " + "; ".join(f"{s['no']} {s['title']} (p.{s.get('start')})" for s in c["sections"])
                          + f"\n\nThe chapter's pages:\n{text}\n\nReturn {{\"chapters\": [{{\"chapter\": {c['no']}, \"title\": ..., \"notes\": ...}}]}}.")
                data = await self.ai.think_json(system=STUDY, prompt=prompt, schema=NOTES_SCHEMA, model=self.lead_model,
                                                fake=lambda c=c: {"chapters": [{"chapter": c["no"], "title": c["title"], "notes": f"第 {c['no']} 章要点（离线示例）"}]})
                for x in (data or {}).get("chapters") or []:
                    if isinstance(x, dict) and x.get("notes"):
                        notes[str(c["no"])] = {"title": str(x.get("title") or c["title"])[:200], "notes": str(x["notes"])[:20000],
                                               "seen_book": True, "at": _now()}
                self.projects.save(proj)
        else:
            proj["busy"] = {"label": f"课程负责人正在整理《{title or '主教材'}》的研读笔记（未见原书）", "since": _now()}
            self.projects.save(proj)
            prompt = (f"Course: {json.dumps(proj['requirements'], ensure_ascii=False)[:800]}\nTextbook: {title or '(none named)'}\n"
                      "The book itself was NOT uploaded. From your own knowledge of this book (only if you know it well; otherwise "
                      "write general notes for the course's subject and say so), write notes for each chapter. Give page numbers "
                      "only if you are sure; otherwise section numbers.")
            data = await self.ai.think_json(system=STUDY, prompt=prompt, schema=NOTES_SCHEMA, model=self.lead_model,
                                            fake=lambda: {"chapters": [{"chapter": 1, "title": "导论", "notes": "（离线示例：未见原书）"}]})
            for x in (data or {}).get("chapters") or []:
                if isinstance(x, dict) and x.get("notes") and _int(x.get("chapter")):
                    notes[str(_int(x["chapter"]))] = {"title": str(x.get("title") or "")[:200], "notes": str(x["notes"])[:20000],
                                                      "seen_book": False, "at": _now()}
        n = len(notes)
        self.say(proj, f"教材研读笔记写好了（{n} 章{'' if tb and toc else '，未见原书，按我对这本书的了解写的，建议上传原书'}），"
                       "在“资料清单”里能看。接下来大纲、设计书和每一课都以它为依据。", "lead", "report")

    async def start_over(self, proj: dict, note: str) -> None:
        for c in (proj.get("outline") or {}).get("chapters", []):
            for les in c["lessons"]:
                if les["status"] in ("awaiting", "failed"):
                    les["status"] = "planned"
                    les["notes"] = ("需按新大纲重写。" + (les.get("notes") or ""))[:2000]
        if proj["materials"].get("textbook") and not proj["materials"].get("toc"):
            await self.reread_contents(proj)
        await self.study_textbook(proj)
        await self.redesign(proj, [], note or "推倒重来：以教材研读笔记为依据重新设计")
        if proj.get("design_book"):
            proj["design_book"].pop("by", None)
        await self.make_design_book(proj)
        self.say(proj, "推倒重来完成：教材研读笔记、课程设计书和大纲都重做了，请在右边看，每章确认后再开写。", "lead", "report")


BACKGROUND.update({"start_over", "study_textbook"})
