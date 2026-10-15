"""改一课的局部、单独重做成品 (round 32, D2 + D3): the course lead works on one part of a written lesson instead of
rewriting the whole lesson, and redoes any one deliverable on its own.

  rework_lesson step   {lesson_id, summary, set: {part: value}, rewrite: [part], note, redo: [deliverable]}
                       set      — the lead's own new content for these parts (lesson-spec shape)
                       rewrite  — the lecturer rewrites just these parts following `note`
                       redo     — deliverables to make again: animation, lab, figures, exercises, guide_plan, lecture
                       Only what the change touches is made again: a changed `animation` part redoes the animation, a
                       changed `lab` part the lab; the slides, notes page, guide, report template and plan are always
                       laid out again (cheap). The lesson's folder is kept first, so the change can be undone.
Mixed into studio.Studio (before LeadAgentMixin, which offers it as a tool).
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
import time
from . import course_builder as cb
from . import team
from .moodle import EngineError
from .production import spec as sp

log = logging.getLogger("wenquest.lesson_edit")

PARTS = ("title", "goal", "problem", "concept", "notes", "example", "animation", "lab", "model", "everyday", "summary",
         "self_check", "figures")
REDO = ("animation", "lab", "figures", "exercises", "guide_plan", "lecture")
REDO_LABEL = {"animation": "动画", "lab": "虚拟实验", "figures": "插图", "exercises": "练习与答案", "guide_plan": "实验指导书和教案",
              "lecture": "讲解视频"}
PART_LABEL = {"title": "课名", "goal": "目标", "problem": "机器人问题", "concept": "概念", "notes": "讲义", "example": "例题",
              "animation": "动画分镜", "lab": "虚拟实验设计", "model": "建模五步", "everyday": "生活中的例子", "summary": "小结",
              "self_check": "自测题", "figures": "插图设计"}
# a changed part of the spec means this deliverable is made again too
FOLLOWS = {"animation": "animation", "lab": "lab", "figures": "figures"}
KEEP_BACKUPS = 3


def rework_ok(les: dict | None, s: dict) -> bool:
    if not les or les["status"] not in ("awaiting", "failed", "published"):   # published: a new version (round 32, D5)
        return False
    st = s.get("set") if isinstance(s.get("set"), dict) else {}
    rw = [p for p in s.get("rewrite") or [] if p in PARTS]
    redo = [r for r in s.get("redo") or [] if r in REDO]
    return bool({k for k in st if k in PARTS} or rw or redo)


def describe_rework(les: dict, s: dict) -> str:
    st = s.get("set") if isinstance(s.get("set"), dict) else {}
    parts = [PART_LABEL[k] for k in st if k in PARTS] + [PART_LABEL[p] for p in s.get("rewrite") or [] if p in PARTS]
    redo = [REDO_LABEL[r] for r in s.get("redo") or [] if r in REDO]
    title = (les.get("title") or {}).get("zh") or (les.get("title") or {}).get("en") or ""
    bits = []
    if parts:
        bits.append("改" + "、".join(dict.fromkeys(parts)))
    if redo:
        bits.append("重做" + "、".join(dict.fromkeys(redo)))
    note = str(s.get("note") or s.get("summary") or "")[:160]
    return f"《{title}》：" + "；".join(bits) + (f"（{note}）" if note else "")


class LessonEditMixin:
    # --- keeping the lesson as it was ---------------------------------------------------------------------------
    def lesson_backup(self, proj: dict, les: dict) -> str:
        """Copy the lesson's folder (without the lecture recordings) and its record; returns the backup's name."""
        d = self.lesson_dir(proj, les)
        root = d.parent.parent / "lesson_backups" / les["id"]
        root.mkdir(parents=True, exist_ok=True)
        name = f"{int(time.time() * 1000)}"
        if d.exists():
            shutil.copytree(d, root / name, ignore=shutil.ignore_patterns("lecture"))
        else:
            (root / name).mkdir()
        rec = {k: v for k, v in les.items() if k not in ("lecture",)}
        (root / name / "_record.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        for old in sorted(p for p in root.iterdir() if p.is_dir())[:-KEEP_BACKUPS * 3]:
            shutil.rmtree(old, ignore_errors=True)
        return name

    def lesson_restore(self, proj: dict, lid: str, name: str) -> bool:
        try:
            _, les = self.find_lesson(proj, lid)
        except Exception:  # noqa: BLE001 - the lesson is gone
            return False
        if les["status"] == "published":
            return False
        d = self.lesson_dir(proj, les)
        src = d.parent.parent / "lesson_backups" / lid / name
        if not src.exists():
            return False
        rec = json.loads((src / "_record.json").read_text(encoding="utf-8"))
        for child in list(d.iterdir()) if d.exists() else []:
            if child.name == "lecture":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
        d.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            if child.name == "_record.json":
                continue
            (shutil.copytree if child.is_dir() else shutil.copy2)(child, d / child.name)
        keep = {k: les[k] for k in ("id", "lecture") if k in les}
        les.clear()
        les.update(rec)
        les.update(keep)
        return True

    # --- the work ----------------------------------------------------------------------------------------------
    async def rework_lesson(self, proj: dict, s: dict) -> None:
        lid = str(s["lesson_id"])
        chapter, les = self.find_lesson(proj, lid)
        d = self.lesson_dir(proj, les)
        if not (d / "spec.json").exists():
            raise EngineError("wrong_stage", "this lesson has not been written yet", 409)
        data = json.loads((d / "spec.json").read_text(encoding="utf-8"))
        spec, gp = data["lesson"], data.get("guide_plan") or {}
        no = self.lesson_no(proj, chapter, les)
        st = {k: v for k, v in (s.get("set") or {}).items() if k in PARTS}
        rewrite = [p for p in s.get("rewrite") or [] if p in PARTS]
        note = str(s.get("note") or "")
        redo = [r for r in s.get("redo") or [] if r in REDO]
        changed = list(st) + rewrite
        prev_status = les["status"]
        les["status"] = "writing"
        proj["busy"] = {"label": f"课程负责人在改：{no} {describe_rework(les, s)[:80]}", "since": time.time()}
        self.projects.save(proj)

        extra_keys = {k: v for k, v in spec.items() if k not in PARTS and k not in ("assets",)}
        raw = dict(spec)
        raw.update(st)
        if rewrite:
            items = self.items(proj)
            ctx = self.lesson_context(proj, chapter, les, items) + f"\nLesson number: {no}"
            src = self.sources(proj, chapter, les, items)
            prompt = (team.lesson_prompt(ctx, src, note, sp.STRUCTURE_GUIDE)
                      + "\n\nThe lesson spec as it is now (keep everything not asked to change — same robot problem, numbers "
                        "and notation unless the change is about them):\n" + json.dumps(raw, ensure_ascii=False)[:16000]
                      + "\n\nRewrite ONLY these parts, complete and in full, following the change asked for: " + ", ".join(rewrite))
            extra = await self.ai.json(system=team.AUTHOR, prompt=prompt, schema=sp.parts_schema(rewrite), max_tokens=12000,
                                       fake=lambda: {p: raw.get(p) for p in rewrite})
            raw = sp.merge_parts(raw, extra, rewrite)
        new = sp.normalize_lesson(raw)
        new.update(extra_keys)
        new["assets"] = spec.get("assets") or []
        for p in changed:   # a part the change emptied keeps what it had
            if p in sp.PART_FILLED and not sp.PART_FILLED[p](new) and sp.PART_FILLED[p](spec):
                new[p] = spec[p]
        spec = new
        redo = list(dict.fromkeys(redo + [FOLLOWS[p] for p in changed if p in FOLLOWS]))
        items = self.items(proj)
        if "figures" in redo:
            proj["busy"] = {"label": f"正在重画插图：{no}", "since": time.time()}
            self.projects.save(proj)
            spec["figures_made"] = await self.make_figures(proj, les, spec, no)
        if "guide_plan" in redo:
            ctx = self.lesson_context(proj, chapter, les, items) + f"\nLesson number: {no}"
            g = await self.ai.json(system=team.GUIDE_PLAN, prompt=f"{ctx}\n\nLesson spec:\n{json.dumps(spec, ensure_ascii=False)[:20000]}",
                                   schema=sp.guide_plan_schema(), max_tokens=8000, fake=lambda: gp)
            gp = sp.normalize_guide_plan(g)
        if "exercises" in redo:
            ctx = self.lesson_context(proj, chapter, les, items) + f"\nLesson number: {no}"
            from .studio import lang_keys
            keys = lang_keys(proj["outline"]["languages"])
            ex = await self.ai.json(system=team.ASSESSOR, prompt=f"{ctx}\n\nLesson spec:\n{json.dumps(spec, ensure_ascii=False)[:14000]}"
                                    + (f"\n\nWhat to change: {note}" if note else ""),
                                    schema=team.exercises_schema(keys), max_tokens=6000,
                                    fake=lambda: {"questions": les.get("exercises"), "answers": les.get("answers")})
            les["exercises"] = {k: self.clean(v) for k, v in cb.norm_text((ex or {}).get("questions"), keys).items()}
            les["answers"] = {k: self.clean(v) for k, v in cb.norm_text((ex or {}).get("answers"), keys).items()}
        review = les.get("review")
        mp4 = next(iter(sorted(d.glob("*.mp4"))), None)
        if "animation" in redo:
            self.clear_attention(les, "animation")
            video = await self.make_video(proj, les, spec, no, review)
        elif mp4:
            png = mp4.with_suffix(".png")
            secs = next((f.get("seconds", 0) for f in les.get("files") or [] if f["kind"] == "animation"), 0)
            video = {"video": mp4, "poster": png if png.exists() else None, "seconds": secs}
        else:
            video = None
        if "lab" in redo:
            self.clear_attention(les, "lab")
            lab = await self.make_lab(proj, chapter, les, spec, no, review)
        else:
            js, shot = d / "lab.js", d / "lab.png"
            lab = {"code": js, "image": shot if shot.exists() else None} if js.exists() else None
        proj["busy"] = {"label": f"正在重新排版课件：{no}", "since": time.time()}
        self.projects.save(proj)
        await asyncio.to_thread(self.render, proj, chapter, les, spec, gp, no, video, lab)
        if "lecture" in redo or changed:
            await self.make_lecture(proj, chapter, les, spec, no)
        les["checklist"] = self.checklist(proj, les, video, lab)
        les["status"] = "awaiting"
        if prev_status == "published":
            # a new version: students keep the published one until the committee approves this one (round 32, D5)
            les["republish"] = {"since": time.time(), "published": les.get("published")}
            flow = les.get("review_flow") or {}
            if flow.get("state") == "approved":
                flow["state"] = ""
        les["error"] = ""
        les.setdefault("edits", []).append({"at": time.time(), "what": describe_rework(les, s)[:300], "by": "lead"})
        del les["edits"][:-20]
        self.say(proj, f"改好了：{describe_rework(les, s)}。请在右边“课时进度”里看。"
                 + ("这是已发布的课的新版本：学生现在看到的仍是旧版，提交审核、委员会批准后才替换上线。" if les.get("republish") else ""),
                 "lead", "lesson")

    def lesson_card(self, proj: dict, les: dict) -> str:
        """The written lesson as the lead sees it to edit it: every part of its spec, its deliverables and review."""
        d = self.lesson_dir(proj, les)
        try:
            data = json.loads((d / "spec.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return ""
        spec = {k: v for k, v in data.get("lesson", {}).items() if k in PARTS}
        files = [f"{f['kind']}: {f['name']}" for f in les.get("files") or []]
        return ("Lesson spec (parts you can change with edit_lesson `set`, same shape):\n" + json.dumps(spec, ensure_ascii=False)[:24000]
                + "\nDeliverables: " + "; ".join(files)
                + f"\nExercises: {json.dumps(les.get('exercises'), ensure_ascii=False)[:2000]}"
                + f"\nEdits so far: {json.dumps(les.get('edits') or [], ensure_ascii=False)[:800]}")
