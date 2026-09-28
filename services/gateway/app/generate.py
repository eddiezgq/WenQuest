"""One-click course generation (round 3, D28).

The teacher drops materials (or describes the course) and clicks once. The gateway then runs
the whole chain in the background:

    classify the files -> plan the outline -> write every lesson (three at a time)

Progress is kept in memory while the job runs and saved to the import session after every
step (job.json), so the teacher can leave the page and come back. A lesson that fails is
marked on its own and can be retried without touching the others. If the gateway restarts
mid-job, the saved job reads as "interrupted" and resumes from where it stopped.

Publishing stays with the teacher: the finished outline goes to the preview, and the page
publishes it with the teacher's own Moodle token.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable

from . import course_builder as cb
from . import materials as mt
from .ai import ModelGateway
from .moodle import EngineError

log = logging.getLogger("wenquest.generate")

WORKERS = 3          # lessons written at the same time: fast, and gentle on rate limits
SOURCE_BUDGET = 16000  # characters of the teacher's files given to the model per lesson


# --- the lesson writer, shared by the job and the single-lesson endpoint ---------------------

async def write_lesson(ai: ModelGateway, store: mt.Store, req: cb.LessonRequest,
                       items: dict[str, mt.Material], clean: Callable[[str], str]) -> dict:
    """Write one lesson, from the teacher's files when the request names sources."""
    src_text, first = "", None
    if req.import_id and req.sources:
        budget = SOURCE_BUDGET
        for fid in req.sources:
            m = items.get(fid)
            if not m:
                continue
            t = store.text(req.import_id, fid)[:budget]
            if not t:
                continue
            first = first or (m.name, t)
            src_text += f"\n<<< 文件：{m.name}（{mt.CATEGORIES[m.category]}）\n{t}\n>>>"
            budget -= len(t)
            if budget <= 0:
                break
    data = await ai.json(system=cb.SYSTEM, prompt=cb.lesson_prompt(req, src_text),
                         schema=cb.lesson_schema(req.languages),
                         max_tokens=12000 if req.languages == "both" else 6000,
                         fake=lambda: cb.fake_lesson(req, first))
    text = cb.norm_text(data.get("content") if isinstance(data, dict) else None, cb.lang_keys(req.languages))
    out = {k: clean(v) for k, v in text.items()}
    if not any(out.values()):
        raise EngineError("ai_bad_output", "the model returned an empty lesson", 502)
    return out


async def plan_from_materials(ai: ModelGateway, items: list[mt.Material], text_of, lang: str, iid: str) -> dict:
    """Outline from classified materials: the rule plan, improved by the model when there is one."""
    items = [m for m in items if m.category != "other"]
    if not mt.chapters(items):
        raise EngineError("no_chapters", "no chapter could be found in the materials", 422)
    plan = mt.rule_plan(items, text_of)
    if ai.provider not in ("fake", "none"):
        ai_plan = await ai.json(system=cb.SYSTEM, prompt=mt.plan_prompt(items, text_of, lang),
                                schema=mt.plan_schema(), max_tokens=6000)
        if isinstance(ai_plan, dict) and isinstance(ai_plan.get("sections"), list) and ai_plan["sections"]:
            plan = mt.merge_plan(ai_plan, plan)
    return mt.outline_from_plan(plan, items, lang, text_of, iid)


async def plan_from_brief(ai: ModelGateway, brief: cb.Brief) -> dict:
    data = await ai.json(system=cb.SYSTEM, prompt=cb.outline_prompt(brief),
                         schema=cb.outline_schema(brief.languages, brief.assignments),
                         max_tokens=8000, fake=lambda: cb.fake_outline(brief))
    outline = cb.norm_outline(data if isinstance(data, dict) else {}, brief)
    if not outline["sections"]:
        raise EngineError("ai_bad_output", "the model returned no sections", 502)
    return outline


# --- jobs ----------------------------------------------------------------------------------

def _key(si: int, li: int) -> str:
    return f"{si}-{li}"


def _disp(t: Any) -> str:
    if isinstance(t, dict):
        return str(t.get("zh") or t.get("en") or "")
    return str(t or "")


class Generator:
    def __init__(self, store: mt.Store, ai: ModelGateway, clean: Callable[[str], str]):
        self.store = store
        self.ai = ai
        self.clean = clean
        self.jobs: dict[str, dict] = {}            # live jobs, the source of truth while running
        self.tasks: dict[str, asyncio.Task] = {}   # held so tasks are not garbage-collected
        self.retries: set[asyncio.Task] = set()

    # persistence -------------------------------------------------------------------------
    def _path(self, sid: str) -> Path:
        return self.store.root / sid / "job.json"

    def _save(self, sid: str) -> None:
        job = self.jobs.get(sid)
        if job is not None:
            job["updated"] = time.time()
            self._path(sid).write_text(json.dumps(job, ensure_ascii=False))

    def _load(self, sid: str, user_id: int) -> dict | None:
        self.store.load(sid, user_id)  # ownership check; raises for other users
        if sid in self.jobs:
            return self.jobs[sid]
        p = self._path(sid)
        if not p.exists():
            return None
        job = json.loads(p.read_text())
        if job.get("state") == "running":  # the gateway restarted mid-job
            job["state"] = "interrupted"
        return job

    # public API --------------------------------------------------------------------------
    def status(self, sid: str, user_id: int) -> dict | None:
        job = self._load(sid, user_id)
        return self.public(job) if job else None

    def start(self, sid: str, user_id: int, languages: str, brief: cb.Brief | None = None,
              outline: dict | None = None) -> dict:
        """Start (or resume) generation. An outline from the teacher skips planning."""
        running = self.tasks.get(sid)
        if running and not running.done():
            return self.public(self.jobs[sid])
        old = self._load(sid, user_id)
        if outline is None and old and old.get("outline") and old.get("state") in ("interrupted", "error", "done"):
            job = old  # resume: keep the outline and every lesson already written
            job["state"], job["error"] = "running", ""
        else:
            items = self.store.materials(sid, user_id)
            job = {
                "state": "running", "phase": "classify", "error": "",
                "languages": languages, "brief": brief.model_dump() if brief else None,
                "files": {"total": len(items), "readable": sum(1 for m in items if m.chars),
                          "unreadable": sum(1 for m in items if m.error)},
                "outline": outline, "lessons": {}, "errors": {}, "started": time.time(),
            }
            if outline:
                job["phase"] = "write"
        job["user"] = user_id
        self.jobs[sid] = job
        self._save(sid)
        self.tasks[sid] = asyncio.create_task(self._run(sid))
        return self.public(job)

    def retry(self, sid: str, user_id: int, si: int, li: int) -> dict:
        job = self._load(sid, user_id)
        if not job or not job.get("outline"):
            raise EngineError("not_found", "nothing has been generated yet", 404)
        secs = job["outline"]["sections"]
        if not (0 <= si < len(secs) and 0 <= li < len(secs[si]["lessons"])):
            raise EngineError("not_found", "no such lesson", 404)
        self.jobs[sid] = job
        if job["lessons"].get(_key(si, li)) != "busy":
            job["lessons"][_key(si, li)] = "busy"
            self._save(sid)
            t = asyncio.create_task(self._write(sid, si, li))
            self.retries.add(t)
            t.add_done_callback(self.retries.discard)
        return self.public(job)

    def public(self, job: dict) -> dict:
        out = {k: v for k, v in job.items() if k != "user"}
        o = job.get("outline")
        total = sum(len(s.get("lessons") or []) for s in o["sections"]) if o else 0
        done = sum(1 for v in job.get("lessons", {}).values() if v == "done")
        failed = sum(1 for v in job.get("lessons", {}).values() if v == "fail")
        out["progress"] = {"lessons_total": total, "lessons_done": done, "lessons_failed": failed}
        return out

    # the job -----------------------------------------------------------------------------
    async def _run(self, sid: str) -> None:
        job = self.jobs[sid]
        uid = job["user"]
        try:
            if not job.get("outline"):
                brief = cb.Brief(**job["brief"]) if job.get("brief") else None
                items = self.store.materials(sid, uid)
                if items:
                    job["phase"] = "classify"
                    self._save(sid)
                    meta = self.store.load(sid, uid)
                    if self.ai.provider not in ("fake", "none") and not meta.get("classified"):
                        data = await self.ai.json(system=cb.SYSTEM, prompt=mt.classify_prompt(items),
                                                  schema=mt.classify_schema(), max_tokens=4000)
                        items = self.store.materials(sid, uid)  # the teacher may have edited meanwhile
                        mt.apply_ai(items, data)
                        self.store.put_materials(sid, uid, items)
                        self.store.mark_classified(sid, uid)
                    job["phase"] = "plan"
                    self._save(sid)
                    lang = "en" if job["languages"] == "en" else "zh"
                    job["outline"] = await plan_from_materials(self.ai, items, lambda f: self.store.text(sid, f), lang, sid)
                elif brief:
                    job["phase"] = "plan"
                    self._save(sid)
                    job["outline"] = await plan_from_brief(self.ai, brief)
                    job["outline"]["import_id"] = sid
                else:
                    raise EngineError("nothing_to_build", "no materials and no description", 422)
            job["phase"] = "write"
            todo = [(si, li) for si, s in enumerate(job["outline"]["sections"]) for li in range(len(s["lessons"]))
                    if job["lessons"].get(_key(si, li)) != "done"]
            for si, li in todo:
                job["lessons"][_key(si, li)] = "wait"
            self._save(sid)

            async def worker():
                while todo:
                    si, li = todo.pop(0)
                    await self._write(sid, si, li)

            await asyncio.gather(*(worker() for _ in range(WORKERS)))
            job["phase"] = "done"
            job["state"] = "done"
        except EngineError as exc:
            job["state"], job["error"] = "error", exc.code
        except Exception:  # never leave a job "running" forever
            log.exception("generation failed for %s", sid)
            job["state"], job["error"] = "error", "server_error"
        finally:
            self._save(sid)

    async def _write(self, sid: str, si: int, li: int) -> None:
        job = self.jobs[sid]
        o = job["outline"]
        sec = o["sections"][si]
        les = sec["lessons"][li]
        k = _key(si, li)
        job["lessons"][k] = "busy"
        job["errors"].pop(k, None)
        self._save(sid)
        brief = job.get("brief") or {}
        req = cb.LessonRequest(
            import_id=sid if les.get("sources") else "", sources=(les.get("sources") or [])[:8],
            course_title=_disp(o.get("title"))[:300], section_title=_disp(sec.get("title"))[:300],
            lesson_title=_disp(les.get("title"))[:300] or "—", goal=_disp(les.get("goal"))[:1000],
            audience=brief.get("audience", ""), level=brief.get("level", ""),
            languages=o.get("languages") or "zh", notes=brief.get("notes", ""),
        )
        try:
            items = {m.id: m for m in self.store.materials(sid, job["user"])}
            les["content"] = await write_lesson(self.ai, self.store, req, items, self.clean)
            job["lessons"][k] = "done"
        except EngineError as exc:
            job["lessons"][k], job["errors"][k] = "fail", exc.code
        except Exception:
            log.exception("lesson %s failed for %s", k, sid)
            job["lessons"][k], job["errors"][k] = "fail", "server_error"
        finally:
            self._save(sid)
