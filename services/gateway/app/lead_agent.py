"""课程负责人由 AI 内核担任 (round 31): the course lead is the model itself, guided by a principles document
(principles/course_lead.md) instead of a fixed pipeline. This module adds what the agent needs on top of the expert
lane (expert.py): editing the course draft directly, starting work, autonomy levels, a change history with undo.

  autonomy           proj["autonomy"]: "ask" (every change is a proposal), "small" (default: edits at once, batch work
                     and deletions are proposals), "free" (edits and batch work at once; deletions and start-over ask)
  snapshot / undo    every change to the draft (by the lead or the teacher) keeps the state before it; undo restores
                     the outline, design book and requirements without losing lesson content written since
Mixed into studio.Studio (before ExpertMixin, which uses these).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .lead import BACKGROUND, OUTLINE_OPS, _id, _now
from .moodle import EngineError

PRINCIPLES = Path(__file__).with_name("principles") / "course_lead.md"
AUTONOMY = ("ask", "small", "free")
AUTONOMY_LABEL = {"ask": "每步都问", "small": "小改直接做", "free": "放手做"}
# edits that are always proposals, whatever the autonomy
ALWAYS_ASK_EDIT = {"remove_chapter"}
ALWAYS_ASK_WORK = {"start_over"}
LIGHT_WORK = {"rework_lesson", "write_lesson", "revise_lesson", "write_next", "reread_textbook", "study_textbook", "remake_design_book"}

AGENT_TOOLS = [
    {"name": "edit_course", "description": (
        "Change the course draft: requirements, main textbook, outline (chapters, lessons, weeks, goals, textbook sections, "
        "calendar note) and the course design book. `ops` are steps from the list in the system prompt (immediate ones: "
        "set_requirement, set_role, set_textbook, set_textbook_title, set_course_title, set_chapter, rename_chapter, "
        "move_chapter, remove_chapter, confirm_chapter, set_lesson, add_lesson, move_lesson, remove_lesson, "
        "set_calendar_note, set_design_book, set_pace, approve_outline). Depending on the autonomy level they are applied at once (the "
        "teacher can undo) or become a proposal. Returns what happened."),
     "input_schema": {"type": "object", "properties": {"summary": {"type": "string"},
                                                       "ops": {"type": "array", "items": {"type": "object"}}},
                      "required": ["summary", "ops"]}},
    {"name": "start_work", "description": (
        "Start background work by the team: write_lesson, write_lessons {lesson_ids}, revise_lesson, write_next, redesign, "
        "remake_design_book, reread_textbook, study_textbook, start_over. One piece of work runs at a time; steps given "
        "together run one after another. Depending on the autonomy level it starts at once or becomes a proposal."),
     "input_schema": {"type": "object", "properties": {"summary": {"type": "string"},
                                                       "steps": {"type": "array", "items": {"type": "object"}}},
                      "required": ["summary", "steps"]}},
    {"name": "edit_lesson", "description": (
        "Work on ONE written lesson (waiting for review, or published — that makes a new version the committee approves "
        "before students see it) without rewriting all of it: change some parts and/or make some "
        "deliverables again. Call get_lesson first to see its parts. `set`: your own new content for parts (same shape "
        "as get_lesson shows: problem, notes, example, lab, model, …); `rewrite` + `note`: the lecturer rewrites those "
        "parts following the note; `redo`: deliverables to make again (courseware = the web interactive deck, animation, lab, figures, "
        "exercises, guide_plan, lecture), with `note` for what to change. Slides and documents are laid out again; a changed animation/lab/figures part redoes it too. Runs as "
        "background work (one lesson at a time); the teacher can undo it."),
     "input_schema": {"type": "object", "properties": {
         "lesson_id": {"type": "string"}, "summary": {"type": "string"}, "set": {"type": "object"},
         "rewrite": {"type": "array", "items": {"type": "string"}}, "note": {"type": "string"},
         "redo": {"type": "array", "items": {"type": "string"}}}, "required": ["lesson_id", "summary"]}},
    {"name": "confirm_proposal", "description": (
        "Carry out an open proposal (yours, waiting for the teacher) because the teacher has just agreed to it in the "
        "chat (e.g. '好', '可以', '写吧', '就这样'). Only when the teacher's latest message agrees; never re-propose the "
        "same thing instead. Immediate changes apply at once; background work starts and runs one step after another."),
     "input_schema": {"type": "object", "properties": {"proposal_id": {"type": "string"}}, "required": ["proposal_id"]}},
    {"name": "undo", "description": "Undo the last change to the course draft (outline, design book, requirements).",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "history", "description": "The recent changes to the course draft, newest last.",
     "input_schema": {"type": "object", "properties": {}}},
]
AGENT_LABEL = {"edit_lesson": "正在安排改这一课", "edit_course": "正在改课程草稿", "start_work": "正在安排工作", "confirm_proposal": "正在照你确认的做", "undo": "正在撤销", "history": "正在看改动记录"}


def principles() -> str:
    """Read at every turn, so editing the file changes the lead's behaviour from the next message."""
    try:
        return PRINCIPLES.read_text(encoding="utf-8")
    except OSError:
        return ""


class LeadAgentMixin:
    # --- autonomy ------------------------------------------------------------------------------------------------
    def autonomy(self, proj: dict) -> str:
        a = proj.get("autonomy") or "small"
        return a if a in AUTONOMY else "small"

    # --- history and undo ------------------------------------------------------------------------------------------
    def snapshot(self, proj: dict, label: str, by: str) -> None:
        """Keep the draft as it is now, before a change (label says what the change is)."""
        hist = proj.setdefault("history", [])
        hist.append({"id": _id(), "at": _now(), "label": label[:300], "by": by,
                     "outline": copy.deepcopy(proj.get("outline")), "design_book": copy.deepcopy(proj.get("design_book")),
                     "requirements": copy.deepcopy(proj.get("requirements") or {}), "stage": proj.get("stage"),
                     "materials": {k: copy.deepcopy(proj["materials"].get(k)) for k in ("textbook", "book_title")}})
        del hist[:-30]

    def history_view(self, proj: dict) -> list[dict]:
        return [{"id": h["id"], "at": h["at"], "label": h["label"], "by": h["by"]} for h in proj.get("history") or []]

    def undo(self, proj: dict) -> str:
        hist = proj.get("history") or []
        if not hist:
            raise EngineError("nothing_to_undo", "nothing to undo", 409)
        snap = hist.pop()
        cur = {les["id"]: (c, les) for c in (proj.get("outline") or {}).get("chapters", []) for les in c["lessons"]}
        o = copy.deepcopy(snap["outline"])
        if o:
            seen = set()
            for c in o["chapters"]:
                for i, les in enumerate(c["lessons"]):
                    now = cur.get(les["id"])
                    if now:   # the plan comes back; what was written since stays
                        _, nl = now
                        c["lessons"][i] = {**nl, **{k: les.get(k) for k in ("title", "goal", "week", "sections") if k in les}}
                        if nl["status"] == "published":
                            c["lessons"][i] = nl
                    seen.add(les["id"])
            # lessons that were written or published after the snapshot are never thrown away
            for lid, (cc, les) in cur.items():
                if lid in seen or les["status"] == "planned":
                    continue
                dst = next((c for c in o["chapters"] if c.get("id") == cc.get("id")), None) or (o["chapters"][-1] if o["chapters"] else None)
                if dst is None:
                    o["chapters"].append({**{k: v for k, v in cc.items() if k != "lessons"}, "lessons": [les]})
                else:
                    dst["lessons"].append(les)
        proj["outline"] = o
        # back to the outline stage only while nothing has been written (an approve_outline undone)
        if snap.get("stage") == "outline" and proj.get("stage") == "lessons" and not any(
                les["status"] != "planned" for c in (o or {}).get("chapters", []) for les in c["lessons"]):
            proj["stage"] = "outline"
        proj["design_book"] = snap["design_book"]
        b = snap.get("lesson_backup")
        if b:   # a lesson worked on by rework_lesson: its folder and record come back as they were
            self.lesson_restore(proj, b["lesson_id"], b["name"])
        proj["requirements"] = snap["requirements"]
        for k, v in (snap.get("materials") or {}).items():
            proj["materials"][k] = v
        proj["last_change"] = {"at": _now(), "lessons": [], "label": "撤销：" + snap["label"]}
        return snap["label"]

    # --- the two acting tools ----------------------------------------------------------------------------------------
    def agent_edit(self, proj: dict, inp: dict, made: list[str]) -> str:
        ops = [s for s in inp.get("ops") or [] if isinstance(s, dict) and s.get("type")]
        summary = str(inp.get("summary") or "")[:600]
        if not ops:
            return "ERROR: no ops"
        bad = [s for s in ops if s.get("type") in BACKGROUND or not self.step_ok(proj, s)]
        ok = [s for s in ops if s not in bad]
        if not ok:
            return "ERROR: none of these ops is possible now (check ids with get_outline): " + json.dumps(bad, ensure_ascii=False)[:1500]
        # a lesson that is already written is only removed with the teacher's confirmation
        must_ask = self.autonomy(proj) == "ask" or any(
            s["type"] in ALWAYS_ASK_EDIT or (s["type"] == "set_chapter" and self._drops_written(proj, s)) for s in ok)
        note_bad = f"; not possible now: {json.dumps(bad, ensure_ascii=False)[:800]}" if bad else ""
        if must_ask:
            pid = self.make_proposal(proj, summary, ok, made)
            return f"became proposal {pid}: waiting for the teacher to confirm" + note_bad
        self.snapshot(proj, summary or "；".join(self.describe(proj, s) for s in ok)[:300], "lead")
        done, changed = [], []
        for s in ok:
            line = self.describe(proj, s)
            try:
                res = self.apply_step(proj, s)
                done.append("✓ " + line)
                if s["type"] == "add_lesson" and res:
                    changed.append(res)
                for k in ("lesson_id",):
                    if s.get(k):
                        changed.append(str(s[k]))
                if s["type"] == "set_chapter":
                    no = s.get("no")
                    changed += [les["id"] for c in proj["outline"]["chapters"] if c["no"] == no for les in c["lessons"]]
            except EngineError as e:
                done.append(f"✗ {line}（{e}）")
        proj["last_change"] = {"at": _now(), "lessons": changed, "label": summary}
        proj["messages"].append({"id": _id(), "role": "lead", "kind": "change", "ts": _now(),
                                 "text": "已改：" + (summary or "课程草稿"), "lines": done})
        return "applied (the teacher can undo):\n" + "\n".join(done) + note_bad

    def _drops_written(self, proj: dict, s: dict) -> bool:
        o = proj.get("outline") or {}
        old = next((c for c in o.get("chapters") or [] if c["no"] == s.get("no")), None)
        if not old:
            return False
        keep = {str(x.get("id")) for x in s.get("lessons") or [] if isinstance(x, dict)}
        return any(les["status"] not in ("planned",) and les["id"] not in keep for les in old["lessons"])

    def agent_work(self, proj: dict, inp: dict, made: list[str]) -> str:
        steps = [s for s in inp.get("steps") or [] if isinstance(s, dict) and s.get("type") in BACKGROUND]
        summary = str(inp.get("summary") or "")[:600]
        ok = [s for s in steps if self.step_ok(proj, s)]
        bad = [s for s in (inp.get("steps") or []) if s not in ok]
        if not ok:
            return "ERROR: none of these steps is possible now: " + json.dumps(bad, ensure_ascii=False)[:1500]
        note_bad = f"; not possible now: {json.dumps(bad, ensure_ascii=False)[:800]}" if bad else ""
        level = self.autonomy(proj)
        light = all(s["type"] in LIGHT_WORK for s in ok) and len(ok) == 1
        batch_ok = level == "free" and not any(s["type"] in ALWAYS_ASK_WORK for s in ok)
        if level == "ask" or not (light or batch_ok) or (level == "small" and not light):
            pid = self.make_proposal(proj, summary, ok, made)
            return f"became proposal {pid}: waiting for the teacher to confirm" + note_bad
        if self.is_busy(proj["id"]):
            return f"NOT started: the team is busy ({(proj.get('busy') or {}).get('label', '')}). Tell the teacher; it can start when that is done."
        label = "；".join(self.describe(proj, s) for s in ok)[:200]

        async def chain(p: dict, steps=ok) -> None:
            for s in steps:
                self.refresh(p)
                await self.run_step(p, s)
        self.run(proj, label, chain)
        return "started: " + label + note_bad

    def agent_confirm(self, proj: dict, inp: dict) -> str:
        """The teacher agreed in the chat: do what the open proposal says (same rules as the 确认 button)."""
        p = next((x for x in proj.get("proposals") or [] if x["id"] == str(inp.get("proposal_id")) and x["status"] == "open"), None)
        if not p:
            opened = [x["id"] for x in proj.get("proposals") or [] if x["status"] == "open"]
            return f"ERROR: no open proposal with that id (open: {opened or 'none'})"
        work = [s for s in p["steps"] if s.get("type") in BACKGROUND and self.step_ok(proj, s)]
        if work and self.is_busy(proj["id"]):
            return f"NOT done: the team is busy ({(proj.get('busy') or {}).get('label', '')}). Tell the teacher; confirm again when it is done."
        edits = [s for s in p["steps"] if s.get("type") not in BACKGROUND]
        results = []
        if edits:
            self.snapshot(proj, p.get("summary") or "按确认的提议修改", "lead")
        for s in edits:
            if not self.step_ok(proj, s):
                results.append(f"✗ {self.describe(proj, s) if s.get('type') else s}（现在做不了：条件变了）")
                continue
            try:
                note = self.apply_step(proj, s)
                results.append(f"✓ {self.describe(proj, s)}" + (f"（{note}）" if note else ""))
            except EngineError as e:
                results.append(f"✗ {self.describe(proj, s)}（{e}）")
        results += [f"▶ {self.describe(proj, s)}" for s in work]
        p["status"], p["result"], p["done"] = "done", results, _now()
        proj["messages"].append({"id": _id(), "role": "lead", "kind": "change", "ts": _now(),
                                 "text": "已按你的同意执行：" + (p.get("summary") or ""), "lines": results})
        if work:
            label = "；".join(self.describe(proj, s) for s in work)[:200]

            async def chain(pr: dict, steps=work) -> None:
                for st in steps:
                    self.refresh(pr)
                    await self.run_step(pr, st)
            self.run(proj, label, chain)
        return "done:\n" + "\n".join(results)

    def make_proposal(self, proj: dict, summary: str, steps: list[dict], made: list[str]) -> str:
        prop = {"id": _id(), "summary": summary, "steps": steps[:16], "lines": [self.describe_step(proj, s) for s in steps[:16]],
                "status": "open", "created": _now(), "result": []}
        proj.setdefault("proposals", []).append(prop)
        made.append(prop["id"])
        return prop["id"]

    async def agent_tool(self, proj: dict, name: str, inp: dict, made: list[str]) -> str | None:
        """The round-31 tools; None when the name is not one of them."""
        if name == "edit_course":
            return self.agent_edit(proj, inp, made)
        if name == "start_work":
            return self.agent_work(proj, inp, made)
        if name == "edit_lesson":
            step = {"type": "rework_lesson", **{k: inp[k] for k in ("lesson_id", "summary", "set", "rewrite", "note", "redo") if k in inp}}
            return self.agent_work(proj, {"summary": inp.get("summary") or "", "steps": [step]}, made)
        if name == "confirm_proposal":
            return self.agent_confirm(proj, inp)
        if name == "undo":
            try:
                label = self.undo(proj)
            except EngineError:
                return "nothing to undo"
            proj["messages"].append({"id": _id(), "role": "lead", "kind": "change", "ts": _now(), "text": f"已撤销：{label}", "lines": []})
            return f"undone: {label}"
        if name == "history":
            return "\n".join(f"{i + 1}. [{h['by']}] {h['label']}" for i, h in enumerate(self.history_view(proj))) or "(no changes yet)"
        return None

    def agent_glance(self, proj: dict) -> str:
        a = self.autonomy(proj)
        return (f"Autonomy: {a} ({AUTONOMY_LABEL[a]}): "
                + {"ask": "every edit and every piece of work becomes a proposal",
                   "small": "edits apply at once (undoable); one lesson or one light job starts at once; batch work, "
                            "start-over and deleting written lessons become proposals",
                   "free": "edits and work apply at once; start-over and deleting written lessons become proposals"}[a]
                + f"\nChanges in the undo history: {len(proj.get('history') or [])}")
