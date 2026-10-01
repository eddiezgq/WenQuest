"""课程委员会 (round 6): a lesson reaches students only after an AI pre-review and the committee's approval.

  teacher: 提交审核 → AI 预审 (an independent expert reviewer: Claude, thinking first) → 预审意见
           → 按意见修改, or 提交委员会 (with a note)
  committee: the chair approves (→ published at once) or returns it with comments; with `self_review` the teacher
             may approve their own lesson as chair (recorded as 本人审核).

Committee members live in <projects>/../committee.json: {members: [{id, name, email}], chair: id, self_review: true}.
Mixed into studio.Studio.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from . import team
from .expert import strip_html

log = logging.getLogger("wenquest.review")

AREAS = {"academic": "学术正确", "standard": "课程标准", "complete": "完整", "teaching": "教学",
         "bilingual": "中英一致", "sources": "来源与合规"}

REVIEWER = (
    "You are an independent expert reviewer on WenQuest's course committee: a senior professor of this course's "
    "subject who did NOT take part in writing the lesson. Review the finished lesson exactly as students would get it, "
    "against the main textbook (notes and pages given), the course design book and the WenQuest course standard: real "
    "robotics problem → concept → animation → virtual lab → modelling and solving, with one everyday example; complete "
    "deliverables (notes, slides, lecture video, animation, virtual lab that can be completed, lab guide and report "
    "template, practice with answers, lesson plan); bilingual consistency; sources and licences; no personal data. "
    "Check the science and every number yourself. Be specific: where (section, slide, exercise), what is wrong, how to "
    "fix it. Do not praise what is merely present. Write in Chinese."
)


def review_schema() -> dict:
    item = {"type": "object", "properties": {"area": {"type": "string", "enum": list(AREAS)}, "ok": {"type": ["boolean", "null"]},
                                              "note": {"type": "string"}}, "required": ["area", "ok", "note"]}
    issue = {"type": "object", "properties": {"severity": {"type": "string", "enum": ["high", "medium", "low"]},
                                               "where": {"type": "string"}, "text": {"type": "string"}, "fix": {"type": "string"}},
             "required": ["severity", "text"]}
    return {"type": "object", "properties": {
        "verdict": {"type": "string", "enum": ["approve", "revise", "reject"]},
        "summary": {"type": "string"}, "items": {"type": "array", "items": item},
        "issues": {"type": "array", "items": issue}, "highlights": {"type": "array", "items": {"type": "string"}}},
        "required": ["verdict", "summary", "items", "issues"]}


def fake_review(les: dict) -> dict:
    failed = [c for c in les.get("checklist") or [] if c.get("ok") is False]
    return {"verdict": "revise" if failed else "approve",
            "summary": "离线预审：" + ("清单里有未通过的项目，建议修改后再批。" if failed else "五步齐全，未发现明显问题。"),
            "items": [{"area": a, "ok": not failed if a == "complete" else True, "note": ""} for a in AREAS],
            "issues": [{"severity": "medium", "where": c.get("label", ""), "text": c.get("note") or "未通过", "fix": "按清单补齐"} for c in failed],
            "highlights": []}


class Committee:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict:
        try:
            return json.loads(self.path.read_text())
        except (OSError, ValueError):
            return {"members": [], "chair": 0, "self_review": True}

    def save(self, d: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(d, ensure_ascii=False))

    def member(self, uid: int) -> bool:
        return any(m["id"] == uid for m in self.load()["members"])

    def chair(self, uid: int) -> bool:
        d = self.load()
        return bool(uid) and d.get("chair") == uid


class ReviewMixin:
    @property
    def committee(self) -> Committee:
        return Committee(self.projects.root.parent / "committee.json")

    def flow(self, les: dict) -> dict:
        return les.setdefault("review_flow", {"state": "", "history": []})

    def log_flow(self, les: dict, who: str, action: str, comment: str = "") -> None:
        f = self.flow(les)
        f["history"].append({"ts": time.time(), "who": who, "action": action, "comment": comment[:4000]})
        f["history"] = f["history"][-60:]

    async def prereview(self, proj: dict, lid: str) -> None:
        """AI 预审 of one written lesson; the opinion is kept with the lesson and shown to the teacher."""
        chapter, les = self.find_lesson(proj, lid)
        no = self.lesson_no(proj, chapter, les)
        d = self.lesson_dir(proj, les)
        try:
            spec = json.loads((d / "spec.json").read_text())["lesson"]
        except (OSError, ValueError, KeyError):
            spec = {}
        content = les.get("content") or {}
        files = [f"{f['kind']}: {f['name']}" for f in les.get("files") or []]
        lecture = ""
        sc = d / "lecture" / "script.json"
        if sc.exists():
            try:
                x = json.loads(sc.read_text())
                lecture = "\n".join(f"[{i + 1}] {s.get('zh', '')}" for i, s in enumerate(x.get("slides") or x.get("lines") or []))[:6000]
            except ValueError:
                pass
        prompt = (f"Course: {strip_html(json.dumps(proj['outline']['title'], ensure_ascii=False))}\n"
                  f"Lesson {no}: {les['title']}\nGoal: {les.get('goal')}\n\n"
                  f"Course design book:\n{team.design_book_text(proj.get('design_book'))}\n"
                  f"{self.notes_for(proj, chapter['no'])}\n"
                  f"Textbook pages for this lesson:\n{self.sources(proj, chapter, les, self.items(proj))[:30000]}\n\n"
                  f"Lesson spec (problem, concept, animation, lab, model):\n{json.dumps({k: spec.get(k) for k in ('problem', 'concept', 'animation', 'lab', 'model', 'everyday')}, ensure_ascii=False)[:12000]}\n\n"
                  f"Lecture notes (Chinese):\n{' '.join(strip_html(content.get('zh', '')).split())[:20000]}\n\n"
                  f"Lecture notes (English):\n{' '.join(strip_html(content.get('en', '')).split())[:8000]}\n\n"
                  f"Practice:\n{strip_html(json.dumps(les.get('exercises'), ensure_ascii=False))[:5000]}\n"
                  f"Answers:\n{strip_html(json.dumps(les.get('answers'), ensure_ascii=False))[:5000]}\n\n"
                  f"Deliverables: {files}\nThe team's own checklist: {json.dumps([{k: c.get(k) for k in ('label', 'ok', 'note')} for c in les.get('checklist') or []], ensure_ascii=False)[:3000]}\n"
                  f"Lecture video narration:\n{lecture}")
        proj["busy"] = {"label": f"AI 预审正在审《{no}》", "since": time.time()}
        self.projects.save(proj)
        data = await self.ai.think_json(system=REVIEWER, prompt=prompt, schema=review_schema(), model=getattr(self, "lead_model", ""),
                                        thinking=10000, fake=lambda: fake_review(les))
        data = data if isinstance(data, dict) else {}
        verdict = data.get("verdict") if data.get("verdict") in ("approve", "revise", "reject") else "revise"
        op = {"verdict": verdict, "summary": str(data.get("summary") or "")[:3000],
              "items": [{"area": x.get("area"), "label": AREAS.get(x.get("area"), x.get("area")), "ok": x.get("ok"), "note": str(x.get("note") or "")[:800]}
                        for x in data.get("items") or [] if isinstance(x, dict)][:10],
              "issues": [{"severity": x.get("severity") or "medium", "where": str(x.get("where") or "")[:200],
                          "text": str(x.get("text") or "")[:1200], "fix": str(x.get("fix") or "")[:1200]}
                         for x in data.get("issues") or [] if isinstance(x, dict) and x.get("text")][:30],
              "highlights": [str(x)[:300] for x in data.get("highlights") or []][:8], "at": time.time()}
        f = self.flow(les)
        f["state"], f["prereview"] = "prereviewed", op
        self.log_flow(les, "AI 预审", "prereview", op["summary"])
        word = {"approve": "建议批准", "revise": "建议修改后批准", "reject": "建议退回"}[verdict]
        self.say(proj, f"《{no}》AI 预审完成：{word}。{len(op['issues'])} 条意见，详见“课时进度”里这一课。"
                       "你可以按意见修改，也可以带着意见提交课程委员会。", "lead", "report")

    def revise_note(self, les: dict) -> str:
        f = self.flow(les)
        lines = []
        for x in (f.get("prereview") or {}).get("issues") or []:
            lines.append(f"- [{x['severity']}] {x.get('where', '')}：{x['text']}" + (f"（改法：{x['fix']}）" if x.get("fix") else ""))
        for h in f.get("history") or []:
            if h["action"] == "return" and h.get("comment"):
                lines.append(f"- 课程委员会：{h['comment']}")
        return "按审核意见修改：\n" + "\n".join(lines[-30:])
