"""HTTP endpoints of the AI professor team (round 3, D30). Registered by main.create_app().

The team works in the background; the page polls GET /projects/{id} while `busy` is set.
Creating the course and publishing a lesson happen only on the teacher's click, with the
teacher's own Moodle token.
"""

import json
import re
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, File, Form, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from . import course_builder as cb
from . import materials as mt
from . import team
from .moodle import EngineError
from .session import Session
from .studio import disp, lang_keys, new_id, new_project


class NewProject(BaseModel):
    description: str = Field(default="", max_length=4000)


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class AnswerIn(BaseModel):
    answer: str = Field(min_length=1, max_length=1000)


class FileRoleIn(BaseModel):
    id: str
    role: str
    chapters: list[int] = Field(default_factory=list, max_length=40)


class MaterialsIn(BaseModel):
    files: list[FileRoleIn] = Field(default_factory=list, max_length=400)
    textbook: str | None = None


class LessonIn(BaseModel):
    id: str = ""
    title: dict[str, str]
    goal: dict[str, str] = Field(default_factory=dict)
    week: int = 0
    sections: list[str] = Field(default_factory=list, max_length=10)


class ChapterIn(BaseModel):
    id: str = ""
    no: int = 0
    title: dict[str, str]
    summary: dict[str, str] = Field(default_factory=dict)
    lessons: list[LessonIn] = Field(default_factory=list, max_length=20)


class OutlineIn(BaseModel):
    title: dict[str, str]
    summary: dict[str, str] = Field(default_factory=dict)
    chapters: list[ChapterIn] = Field(min_length=1, max_length=40)


class NoteIn(BaseModel):
    note: str = Field(default="", max_length=4000)


class PaceIn(BaseModel):
    mode: str = Field(pattern="^(manual|daily)$")
    hour: int = Field(default=8, ge=0, le=23)
    tz: str = Field(default="Asia/Shanghai", max_length=60)


def register(app, m) -> None:  # m: the main module (state, current, helpers)
    global STUDIO_ITEMS
    STUDIO_ITEMS = lambda proj: m._studio().items(proj)  # noqa: E731
    current = m.current

    def studio():
        return m._studio()

    def load(pid: str, sess: Session) -> dict:
        try:
            proj = studio().projects.load(pid)
        except KeyError:
            raise EngineError("not_found", "no such course project", 404)
        if proj["owner"] != sess.user_id:
            raise EngineError("forbidden", "not your course project", 403)
        return studio().reconcile(proj)

    def view(proj: dict) -> dict:
        items = {x.id: x for x in studio().items(proj)}
        files = []
        for fid, x in items.items():
            f = proj["materials"]["files"].get(fid, {})
            files.append({"id": fid, "name": x.name, "path": x.path, "size": x.size, "pages": x.pages, "error": x.error,
                          "url": sign_material(proj["id"], fid), "ocr": x.ocr,
                          "role": f.get("role", ""), "role_label": team.ROLES.get(f.get("role", ""), ""),
                          "chapters": f.get("chapters", []), "title": f.get("title", ""),
                          "confidence": f.get("confidence", ""), "note": f.get("note", ""), "by": f.get("by", "")})
        files.sort(key=lambda f: f["path"])
        lessons = [les for c in (proj.get("outline") or {}).get("chapters", []) for les in c["lessons"]]
        out = {k: v for k, v in proj.items() if k not in ("owner",)}
        out["files"] = files
        out["roles"] = team.ROLES
        out["progress"] = {s: sum(1 for les in lessons if les["status"] == s)
                           for s in ("planned", "writing", "reviewing", "awaiting", "published", "failed")}
        out["progress"]["total"] = len(lessons)
        out["busy"] = proj.get("busy") if studio().is_busy(proj["id"]) else None
        out["labs_on"] = bool(studio().labcheck_url)   # virtual labs can be made (the lab checker is set up)
        out["zip_url"] = sign_material(proj["id"], "*") if files else ""
        out["toc"] = [{"no": c["no"], "title": c["title"], "start": c.get("start"),
                       "sections": [{"no": s["no"], "title": s["title"], "start": s.get("start")} for s in c["sections"]]}
                      for c in proj["materials"].get("toc", [])]
        out["materials"] = {k: v for k, v in proj["materials"].items() if k not in ("files", "toc")}
        for c in (out.get("outline") or {}).get("chapters", []):
            for les in c["lessons"]:
                les["files"] = [{**f, "url": sign_lesson_file(proj["id"], les["id"], f["name"])} for f in les.get("files") or []]
        return out

    def sign_material(pid: str, fid: str) -> str:
        """A one-day link to one of the teacher's own materials ("*" = all of them as a zip)."""
        tok = m.state.codec.fernet.encrypt(json.dumps({"p": pid, "f": fid}).encode()).decode()
        return f"{m.state.settings.public_url.rstrip('/')}/api/v1/studio/materials/{tok}"

    def sign_lesson_file(pid: str, lid: str, name: str) -> str:
        tok = m.state.codec.fernet.encrypt(json.dumps({"p": pid, "l": lid, "n": name}).encode()).decode()
        return f"{m.state.settings.public_url.rstrip('/')}/api/v1/studio/files/{tok}"

    async def need_creator(sess: Session) -> None:
        await m.require_creator(sess)

    # --- projects ------------------------------------------------------------------------------
    @app.get("/api/v1/studio/projects")
    async def projects(sess: Annotated[Session, Depends(current)]):
        out = []
        for p in studio().projects.all():
            if p["owner"] != sess.user_id:
                continue
            o = p.get("outline") or {}
            lessons = [les for c in o.get("chapters", []) for les in c["lessons"]]
            out.append({"id": p["id"], "title": disp(o.get("title")) or p["requirements"].get("course_title") or "",
                        "stage": p["stage"], "updated": p["updated"], "course_id": p["course"]["id"],
                        "lessons": len(lessons), "published": sum(1 for x in lessons if x["status"] == "published"),
                        "awaiting": sum(1 for x in lessons if x["status"] == "awaiting"),
                        "busy": bool(p.get("busy")) and studio().is_busy(p["id"]),
                        "open_questions": sum(1 for q in p["questions"] if q["status"] == "open")})
        out.sort(key=lambda x: -x["updated"])
        return {"projects": out}

    @app.post("/api/v1/studio/projects")
    async def create(body: NewProject, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        iid = m.state.store.new_session(sess.user_id, keep=True)
        info = await m.state.moodle.site_info(sess.moodle_token)
        proj = new_project(sess.user_id, info.get("fullname", ""), iid, body.description)
        studio().say(proj, "你好，我是这门课的课程负责人。请把课程资料（整个文件夹）拖进来，也可以先用几句话说说这门课：给谁上、上多久、用什么教材。"
                           "资料放好后点“交给教授团队”，资料馆员会逐个看一遍，然后我把需要确认的事一次问清楚。", "lead")
        studio().projects.save(proj)
        return view(proj)

    @app.get("/api/v1/studio/projects/{pid}")
    async def get(pid: str, sess: Annotated[Session, Depends(current)]):
        return view(load(pid, sess))

    @app.post("/api/v1/studio/projects/{pid}/files")
    async def upload(pid: str, sess: Annotated[Session, Depends(current)],
                     file: UploadFile = File(...), path: str = Form("")):
        proj = load(pid, sess)
        return await m.ingest(proj["import_id"], sess, file, path)

    @app.post("/api/v1/studio/projects/{pid}/files/done")
    async def files_done(pid: str, sess: Annotated[Session, Depends(current)]):
        """The teacher finished adding files. Once the materials were read, the librarian sorts the new ones
        at once and the lead says what they change (before that, 'start' reads everything)."""
        proj = load(pid, sess)
        known = proj["materials"]["files"]
        if proj["stage"] != "intake" and any(x.id not in known for x in studio().items(proj)):
            studio().run(proj, "资料馆员正在阅读新加的资料…", studio().classify_new)
        return view(studio().projects.load(pid))

    @app.delete("/api/v1/studio/projects/{pid}/files/{fid}")
    async def delete_file(pid: str, fid: str, sess: Annotated[Session, Depends(current)]):
        """Remove a material. Lessons already written keep what they are; later lessons no longer use it."""
        proj = load(pid, sess)
        if studio().is_busy(pid):
            raise EngineError("team_busy", "wait until the team has finished", 409)
        if not m.state.store.remove(proj["import_id"], sess.user_id, fid):
            raise EngineError("not_found", "no such file", 404)
        proj["materials"]["files"].pop(fid, None)
        if proj["materials"].get("textbook") == fid:
            proj["materials"]["textbook"] = ""
            proj["materials"]["toc"] = []
        studio().projects.save(proj)
        return view(proj)

    @app.get("/api/v1/studio/materials/{signed}")
    async def material_file(signed: str):
        """Download one of the teacher's materials, or all of them as a zip in their folders."""
        try:
            d = json.loads(m.state.codec.fernet.decrypt(signed.encode(), ttl=m.FILE_TTL))
            proj = studio().projects.load(d["p"])
        except KeyError:
            raise EngineError("not_found", "no such file", 404)
        except Exception:
            raise EngineError("link_expired", "file link expired", 410)
        items = studio().items(proj)
        if d["f"] == "*":
            import io
            import zipfile
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                used: set[str] = set()
                for x in items:
                    name = re.sub(r"^/+|\.\.", "", x.path or x.name) or x.id
                    while name in used:
                        name = "_" + name
                    used.add(name)
                    try:
                        z.writestr(name, m.state.store.data(proj["import_id"], x.id))
                    except KeyError:
                        continue
            title = re.sub(r'[\\/:*?"<>|]', "-", disp(proj["outline"]["title"]) if proj.get("outline") else "") or "资料"
            return Response(buf.getvalue(), media_type="application/zip", headers={
                "Content-Disposition": m._disposition("attachment", f"{title} 资料.zip"), "Cache-Control": "private, max-age=600"})
        x = next((i for i in items if i.id == d["f"]), None)
        if not x:
            raise EngineError("not_found", "no such file", 404)
        return Response(m.state.store.data(proj["import_id"], x.id), media_type="application/octet-stream", headers={
            "Content-Disposition": m._disposition("attachment", x.name), "Cache-Control": "private, max-age=600",
            "X-Content-Type-Options": "nosniff"})

    @app.post("/api/v1/studio/projects/{pid}/start")
    async def start(pid: str, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        proj = load(pid, sess)
        if proj["stage"] not in ("intake", "materials"):
            raise EngineError("wrong_stage", "materials are already settled", 409)
        if not studio().items(proj) and not proj["requirements"].get("notes"):
            raise EngineError("nothing_to_build", "add materials or a description first", 422)
        studio().run(proj, "资料馆员正在逐个阅读资料…", studio().study_materials)
        return view(studio().projects.load(pid))

    @app.post("/api/v1/studio/projects/{pid}/messages")
    async def message(pid: str, body: MessageIn, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        proj = load(pid, sess)
        if proj["stage"] == "intake" and not studio().is_busy(pid):
            # Before the team starts, what the teacher writes is the course description.
            proj["requirements"]["notes"] = (proj["requirements"].get("notes", "") + "\n" + body.text).strip()[:4000]
        studio().say(proj, body.text, "teacher")
        studio().projects.save(proj)
        text = body.text
        studio().run(proj, "课程负责人正在回复…", lambda p: studio().chat(p, text))
        return view(studio().projects.load(pid))

    @app.post("/api/v1/studio/projects/{pid}/questions/{qid}")
    async def answer(pid: str, qid: str, body: AnswerIn, sess: Annotated[Session, Depends(current)]):
        proj = load(pid, sess)
        q = next((q for q in proj["questions"] if q["id"] == qid), None)
        if not q:
            raise EngineError("not_found", "no such question", 404)
        q["answer"], q["status"] = body.answer, "answered"
        _learn_from_answer(proj, q)
        studio().projects.save(proj)
        return view(proj)

    @app.put("/api/v1/studio/projects/{pid}/materials")
    async def materials(pid: str, body: MaterialsIn, sess: Annotated[Session, Depends(current)]):
        proj = load(pid, sess)
        files = proj["materials"]["files"]
        for f in body.files:
            if f.id in files and f.role in team.ROLES:
                cur = files[f.id]
                chapters = [c for c in f.chapters if 0 < c < 100]
                if (cur["role"], cur.get("chapters")) != (f.role, chapters):
                    cur.update(role=f.role, chapters=chapters, by="teacher", confidence="high")
        if body.textbook is not None:
            tb = body.textbook if body.textbook in files else ""
            for fid, f in files.items():
                if f["role"] == "main_textbook" and fid != tb:
                    f.update(role="aux_textbook", by="teacher")
            if tb:
                files[tb].update(role="main_textbook", by="teacher", confidence="high")
            if tb != proj["materials"]["textbook"]:
                proj["materials"]["textbook"], proj["materials"]["toc"] = tb, []
                studio().projects.save(proj)
                if tb:
                    studio().run(proj, "资料馆员正在读主教材的目录…", studio().read_contents)
                    return view(studio().projects.load(pid))
        studio().projects.save(proj)
        return view(proj)

    @app.post("/api/v1/studio/projects/{pid}/approve-materials")
    async def approve_materials(pid: str, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        proj = load(pid, sess)
        if proj["stage"] not in ("materials", "outline"):
            raise EngineError("wrong_stage", "not at this stage", 409)
        studio().say(proj, "资料清单确认了，课程设计师开始设计大纲和教学日历。", "system")
        studio().run(proj, "课程设计师正在设计大纲和教学日历…", studio().design)
        return view(studio().projects.load(pid))

    @app.put("/api/v1/studio/projects/{pid}/outline")
    async def edit_outline(pid: str, body: OutlineIn, sess: Annotated[Session, Depends(current)]):
        proj = load(pid, sess)
        o = proj.get("outline")
        if not o:
            raise EngineError("wrong_stage", "no outline yet", 409)
        keys = lang_keys(o["languages"])
        T = lambda d: {k: str(d.get(k, "")).strip()[:300] for k in keys}  # noqa: E731
        old = {les["id"]: les for c in o["chapters"] for les in c["lessons"]}
        old_ch = {c["id"]: c for c in o["chapters"]}
        chapters = []
        for i, c in enumerate(body.chapters):
            prev = old_ch.get(c.id, {})
            lessons = []
            for les in c.lessons:
                base = old.get(les.id) or {"id": new_id(), "status": "planned", "content": {}, "exercises": {},
                                           "answers": {}, "review": None, "notes": "", "cmids": [], "error": ""}
                if base["status"] == "published":
                    lessons.append(base)  # already in the course: keep as it is
                    continue
                base.update(title=T(les.title), goal=T(les.goal), week=les.week, sections=les.sections)
                lessons.append(base)
            chapters.append({"id": prev.get("id") or new_id(), "no": c.no or i + 1, "title": T(c.title),
                             "summary": T(c.summary), "lessons": lessons})
        o.update(title=T(body.title), summary=T(body.summary), chapters=chapters)
        studio().projects.save(proj)
        return view(proj)

    @app.put("/api/v1/studio/projects/{pid}/design-book")
    async def edit_design_book(pid: str, body: dict, sess: Annotated[Session, Depends(current)]):
        """The teacher corrects the course design book; every later lesson, animation and lab follows it."""
        from .studio import normalize_design_book
        proj = load(pid, sess)
        if not proj.get("outline"):
            raise EngineError("wrong_stage", "no outline yet", 409)
        book = normalize_design_book({**(proj.get("design_book") or {}), **body}, proj["outline"])
        book["by"] = "teacher"
        proj["design_book"] = book
        studio().say(proj, "课程设计书按你的修改更新了，之后写的课时、动画和实验都照它来；已经写好的课时如需跟着改，可以点“重写”。", "lead")
        studio().projects.save(proj)
        return view(proj)

    @app.post("/api/v1/studio/projects/{pid}/approve-outline")
    async def approve_outline(pid: str, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        proj = load(pid, sess)
        if proj["stage"] != "outline" or not proj.get("outline"):
            raise EngineError("wrong_stage", "not at this stage", 409)
        if not proj["outline"]["chapters"] or not any(c["lessons"] for c in proj["outline"]["chapters"]):
            raise EngineError("empty_outline", "the outline has no lessons yet", 409)
        if not proj["course"]["id"]:
            await create_course(proj, sess)
        proj["stage"] = "lessons"
        studio().say(proj, "大纲定稿，课程已经在平台上建好了（目前只有章节，学生还看不到课时）。"
                           "接下来一课一课地写：点“写下一课”，或者在“节奏”里设成每天自动写一课。每一课都要你审过、点“通过并发布”，学生才看得到。", "lead")
        studio().projects.save(proj)
        return view(proj)

    # --- lessons ---------------------------------------------------------------------------
    @app.post("/api/v1/studio/projects/{pid}/lessons/next")
    async def write_next(pid: str, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        proj = load(pid, sess)
        if proj["stage"] != "lessons":
            raise EngineError("wrong_stage", "settle the outline first", 409)
        nxt = studio().next_lesson(proj)
        if not nxt:
            raise EngineError("all_written", "every lesson is written", 409)
        lid = nxt[1]["id"]
        studio().run(proj, f"主讲教授正在写：{disp(nxt[1]['title'])}", lambda p: studio().write_lesson(p, lid))
        return view(studio().projects.load(pid))

    @app.post("/api/v1/studio/projects/{pid}/lessons/{lid}/write")
    async def rewrite(pid: str, lid: str, body: NoteIn, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        proj = load(pid, sess)
        _, les = studio().find_lesson(proj, lid)
        if les["status"] == "published":
            raise EngineError("published", "this lesson is already in the course", 409)
        if body.note:
            studio().say(proj, f"请修改《{disp(les['title'])}》：{body.note}", "teacher")
        note = body.note
        studio().run(proj, f"主讲教授正在修改：{disp(les['title'])}", lambda p: studio().write_lesson(p, lid, note))
        return view(studio().projects.load(pid))

    @app.post("/api/v1/studio/projects/{pid}/lessons/{lid}/lab")
    async def redo_lab(pid: str, lid: str, sess: Annotated[Session, Depends(current)]):
        """重做实验: write and try the lesson's virtual lab again; a published lesson's chapter lab page is updated too."""
        await need_creator(sess)
        proj = load(pid, sess)
        chapter, les = studio().find_lesson(proj, lid)
        if les["status"] not in ("awaiting", "published") or not (studio().lesson_dir(proj, les) / "spec.json").exists():
            raise EngineError("wrong_stage", "write the lesson first", 409)
        if not studio().labcheck_url:
            raise EngineError("labs_unavailable", "the lab checker is not set up", 503)

        async def job(p: dict) -> None:
            await studio().redo_lab(p, lid)
            ch, ls = studio().find_lesson(p, lid)
            if ls["status"] == "published":
                await update_chapter_lab(p, ch, ls, sess)

        studio().run(proj, f"实验师正在重做虚拟实验：{disp(les['title'])}", job)
        return view(studio().projects.load(pid))

    @app.post("/api/v1/studio/projects/{pid}/lessons/{lid}/approve")
    async def publish(pid: str, lid: str, sess: Annotated[Session, Depends(current)]):
        await need_creator(sess)
        proj = load(pid, sess)
        chapter, les = studio().find_lesson(proj, lid)
        if les["status"] != "awaiting":
            raise EngineError("wrong_stage", "only a written lesson can be published", 409)
        if not proj["course"]["id"]:
            await create_course(proj, sess)
        await publish_lesson(proj, chapter, les, sess)
        studio().say(proj, f"《{disp(les['title'])}》已发布，学生现在能看到了。", "system")
        studio().projects.save(proj)
        return view(proj)

    @app.get("/api/v1/studio/files/{signed}")
    async def lesson_file(signed: str):
        """A deliverable of a lesson (slides, lab guide, report template, lesson plan) for the teacher to check."""
        try:
            d = json.loads(m.state.codec.fernet.decrypt(signed.encode(), ttl=m.FILE_TTL))
        except Exception:
            raise EngineError("link_expired", "file link expired", 410)
        try:
            proj = studio().projects.load(d["p"])
            _, les = studio().find_lesson(proj, d["l"])
        except KeyError:
            raise EngineError("not_found", "no such file", 404)
        f = next((x for x in les.get("files") or [] if x["name"] == d["n"]), None)
        path = studio().lesson_dir(proj, les) / d["n"]
        if not f or not path.exists():
            raise EngineError("not_found", "no such file", 404)
        if f["kind"] == "lab":
            # A virtual lab runs sandboxed (its own opaque origin), exactly as students get it.
            return Response(path.read_bytes(), media_type="text/html; charset=utf-8", headers={
                "Cache-Control": "private, max-age=600", "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": "sandbox allow-scripts allow-popups allow-forms allow-modals; frame-ancestors 'self'"})
        return FileResponse(path, filename=d["n"], headers={"Cache-Control": "private, max-age=600"})

    @app.get("/api/v1/studio/projects/{pid}/lessons/{lid}/deck")
    async def lesson_deck(pid: str, lid: str, sess: Annotated[Session, Depends(current)]):
        """Preview the lesson's slides while reviewing it (converted like any course deck)."""
        proj = load(pid, sess)
        _, les = studio().find_lesson(proj, lid)
        f = next((x for x in les.get("files") or [] if x["kind"] == "slides"), None)
        path = studio().lesson_dir(proj, les) / f["name"] if f else None
        if not path or not path.exists():
            raise EngineError("not_found", "no slides yet", 404)
        slides = m.state.slides
        if not slides.available:
            return {"status": "unavailable"}
        src = f"studio:{pid}:{lid}:{path.stat().st_mtime_ns}"

        async def fetch() -> bytes:
            return path.read_bytes()

        slides.start(src, fetch, ".pptx", priority=0)
        status, key = slides.status(src)
        if status != "ready" or not key:
            return {"status": status, **slides.progress(src)}
        man = slides.manifest(key) or {}
        base = f"{m.state.settings.public_url.rstrip('/')}/api/v1/slides/files/{key}/"
        return {"status": "ready", "slides": [{"image": base + x["image"], "thumb": base + x["thumb"]} for x in man.get("slides", [])]}

    @app.post("/api/v1/studio/projects/{pid}/stop")
    async def stop(pid: str, sess: Annotated[Session, Depends(current)]):
        load(pid, sess)
        studio().stop(pid)
        return {"stopped": True}

    @app.put("/api/v1/studio/projects/{pid}/pace")
    async def pace(pid: str, body: PaceIn, sess: Annotated[Session, Depends(current)]):
        proj = load(pid, sess)
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(body.tz)
            tz = body.tz
        except Exception:
            tz = "Asia/Shanghai"
        proj["pace"].update(mode=body.mode, hour=body.hour, tz=tz)
        studio().projects.save(proj)
        return view(proj)

    # --- publishing into Moodle -------------------------------------------------------------------
    def ml(t: dict, languages: str, is_html: bool = False) -> str:
        return cb.ml(cb.Text(zh=t.get("zh", ""), en=t.get("en", "")), languages, is_html)

    async def upload_files(proj: dict, fids: list[str], sess: Session) -> list[dict]:
        items = {x.id: x for x in studio().items(proj)}
        acts = []
        for fid in fids:
            x = items.get(fid)
            if not x:
                continue
            info = proj["materials"]["files"].get(fid, {})
            role = info.get("role", "other")
            draft = await m.state.moodle.upload(sess.moodle_token, x.name, m.state.store.data(proj["import_id"], fid))
            # A readable name: the document's own title, else the file name without download numbers.
            name = (info.get("title") or "").strip() or readable_name(x.name)
            acts.append({"type": "resource", "name": name[:250], "draftitemid": draft,
                         "visible": 0 if role in team.TEACHER_ONLY_ROLES else 1})
        return acts

    async def create_course(proj: dict, sess: Session) -> None:
        o = proj["outline"]
        lg = o["languages"]
        files = proj["materials"]["files"]
        info_files = [fid for fid, f in files.items() if f["role"] in team.INFO_ROLES]
        info_name = {"zh": "课程说明", "en": "Course information"}
        forum = {"type": "forum", "name": ml({"zh": "课程讨论区", "en": "Course discussion"}, lg),
                 "intro": ml({"zh": "<p>课程问题、学习心得都可以在这里讨论。</p>",
                              "en": "<p>Ask questions and share what you learn here.</p>"}, lg, True)}
        sections = [{"name": ml(info_name, lg), "summary": "",
                     "activities": [forum] + await upload_files(proj, info_files, sess)}]
        for c in o["chapters"]:
            sections.append({"name": ml(c["title"], lg) or f"{c['no']}",
                             "summary": ml({k: cb.paragraphs(v) for k, v in c.get("summary", {}).items()}, lg, True),
                             "activities": []})
        draft = cb.Draft(title=cb.Text(**{k: v for k, v in o["title"].items() if k in ("zh", "en")}), languages=lg,
                         sections=[cb.DraftSection(title=cb.Text(zh="x"))])
        payload = {"fullname": ml(o["title"], lg) or "Course", "shortname": cb.shortname_for(draft),
                   "summary": ml({k: cb.paragraphs(v) for k, v in o.get("summary", {}).items()}, lg, True),
                   "sections": sections}
        res = await m.state.moodle.call(sess.moodle_token, "local_wenquest_create_course", None, **payload)
        proj["course"] = {"id": res["courseid"], "shortname": res["shortname"],
                          "sections": {c["id"]: i + 2 for i, c in enumerate(o["chapters"])}, "attached": []}

    async def _lab_upload(proj: dict, chapter: dict, les: dict, sess: Session) -> tuple[str, int] | None:
        """The chapter's lab page with every published lab plus this lesson's, uploaded as a draft: (name, draft id)."""
        lessons = [x for x in chapter["lessons"] if x["status"] == "published" or x is les]
        page_html = studio().lab_page(proj, chapter, lessons)
        if not page_html:
            return None
        lg = proj["outline"]["languages"]
        no = chapter["no"]
        name = ml({"zh": f"第{no}章 虚拟实验", "en": f"Chapter {no} virtual lab"}, lg) or f"第{no}章 虚拟实验"
        fname = f"第{no}章虚拟实验（中英）.html" if lg != "en" else f"Chapter{no}-virtual-lab.html"
        draft = await m.state.moodle.upload(sess.moodle_token, fname, page_html.encode("utf-8"))
        return name, draft


    async def chapter_lab(proj: dict, chapter: dict, les: dict, sess: Session) -> dict | None:
        """Publishing a lesson: replace the chapter's lab page in the course, or return the activity that adds it
        (one lab file per chapter, never one per lesson)."""
        up = await _lab_upload(proj, chapter, les, sess)
        if not up:
            return None
        name, draft = up
        cmid = (proj["course"].get("labs") or {}).get(chapter["id"])
        if cmid:
            try:
                await m.state.moodle.call(sess.moodle_token, "local_wenquest_edit_course", None, courseid=proj["course"]["id"],
                                          action="replacefile", cmid=cmid, draftitemid=draft)
                return None
            except EngineError as exc:
                if exc.code not in ("not_found", "invalid_input"):
                    raise
                proj["course"]["labs"].pop(chapter["id"], None)  # the teacher deleted it: add a new one
                up = await _lab_upload(proj, chapter, les, sess)
                name, draft = up if up else (name, draft)
        return {"type": "resource", "name": name, "draftitemid": draft, "visible": 1}


    async def update_chapter_lab(proj: dict, chapter: dict, les: dict, sess: Session) -> None:
        """After redoing a published lesson's lab: put the new chapter page into the course."""
        act = await chapter_lab(proj, chapter, les, sess)
        if act:
            number = proj["course"]["sections"].get(chapter["id"])
            res = await m.state.moodle.call(sess.moodle_token, "local_wenquest_add_activities", None, courseid=proj["course"]["id"],
                                            section=number, activities=[act])
            if res.get("cmids"):
                proj["course"].setdefault("labs", {})[chapter["id"]] = res["cmids"][0]

    async def publish_lesson(proj: dict, chapter: dict, les: dict, sess: Session) -> None:
        lg = proj["outline"]["languages"]
        course = proj["course"]
        number = course["sections"].get(chapter["id"])
        if not number:  # a chapter added after the course was created
            number = max(list(course["sections"].values()) + [1]) + 1
            course["sections"][chapter["id"]] = number
        clean = lambda h: m._clean(h)  # noqa: E731
        html_of = lambda t: ml({k: clean(v) for k, v in t.items()}, lg, True)  # noqa: E731
        title = ml(les["title"], lg)
        ex_name = {"zh": "练习：", "en": "Practice: "}
        ans_name = {"zh": "练习参考答案：", "en": "Answer key: "}
        d = studio().lesson_dir(proj, les)

        async def produced(kind: str) -> list[dict[str, Any]]:
            out = []
            for f in les.get("files") or []:
                path = d / f["name"]
                if f["kind"] == kind and path.exists():
                    draft = await m.state.moodle.upload(sess.moodle_token, f["name"], path.read_bytes())
                    out.append({"type": "resource", "name": Path(f["name"]).stem, "draftitemid": draft,
                                "visible": 0 if f.get("teacher_only") else 1})
            return out

        # The benchmark order: lecture notes, slides, practice, lab guide, report template; then teacher-only items.
        acts: list[dict[str, Any]] = [{"type": "page", "name": title, "content": html_of(les["content"])}]
        acts += await produced("animation")
        acts += await produced("slides")
        if any(les.get("exercises", {}).values()):
            acts.append({"type": "page", "name": ml({k: ex_name[k] + v for k, v in les["title"].items() if k in ex_name}, lg),
                         "content": html_of(les["exercises"])})
        acts += await produced("guide")
        acts += await produced("report")
        lab_act = await chapter_lab(proj, chapter, les, sess)
        lab_index = -1
        if lab_act:
            lab_index = len(acts)
            acts.append(lab_act)
        if any(les.get("answers", {}).values()):
            acts.append({"type": "page", "name": ml({k: ans_name[k] + v for k, v in les["title"].items() if k in ans_name}, lg),
                         "content": html_of(les["answers"]), "visible": 0})
        acts += await produced("plan")
        if chapter["id"] not in course["attached"]:
            fids = [fid for fid, f in proj["materials"]["files"].items()
                    if f["role"] in team.ATTACH_ROLES and chapter["no"] in (f.get("chapters") or [])]
            acts += await upload_files(proj, fids, sess)
        res = await m.state.moodle.call(sess.moodle_token, "local_wenquest_add_activities", None,
                                        courseid=course["id"], section=number, sectionname=ml(chapter["title"], lg),
                                        activities=acts)
        if chapter["id"] not in course["attached"]:
            course["attached"].append(chapter["id"])
        les["cmids"] = res.get("cmids", [])
        if lab_index >= 0 and lab_index < len(les["cmids"]):
            course.setdefault("labs", {})[chapter["id"]] = les["cmids"][lab_index]
        les["status"] = "published"
        les["published"] = time.time()


def readable_name(filename: str) -> str:
    """'1790630614206_Chapter_01_S3q00QP_1.pptx' -> 'Chapter 01': drop download numbers in front and
    random codes at the end (letters mixed with digits or odd capitals), keep real words ('Circuits')."""
    stem = re.sub(r"^\d{6,}[_-]", "", Path(filename).stem)
    m = re.search(r"[_-]([A-Za-z0-9]{6,8})(?:_\d)?$", stem)
    if m:
        code = m.group(1)
        random_like = bool(re.search(r"\d", code)) or bool(re.search(r"[a-z][A-Z]|[A-Z]{2}[a-z]", code))
        if random_like:
            stem = stem[:m.start()]
    return stem.replace("_", " ").strip() or Path(filename).stem


STUDIO_ITEMS = None  # set by register(): the files of a project (for answers that name one)


def studio_items(proj: dict) -> list:
    return STUDIO_ITEMS(proj) if STUDIO_ITEMS else []


def _learn_from_answer(proj: dict, q: dict) -> None:
    """Answers to the standard questions also fill the requirements the team works from."""
    text, ans = q["text"], q["answer"]
    req = proj["requirements"]
    if q.get("kind") == "textbook":
        files = proj["materials"]["files"]
        fid = next((x.id for x in studio_items(proj) if x.name == ans.strip()), "")
        for k, f in files.items():
            if f.get("role") == "main_textbook" and k != fid:
                f.update(role="aux_textbook")
        if fid:
            files.setdefault(fid, {"chapters": [], "title": "", "language": "", "note": ""})
            files[fid].update(role="main_textbook", by="teacher", confidence="high")
        proj["materials"]["textbook"], proj["materials"]["toc"] = fid, []
        return
    if "语言" in text or "language" in text.lower():
        req["language"] = "both" if ("双语" in ans or "bilingual" in ans.lower()) else "en" if ("英" in ans or ans.lower().startswith("en")) else "zh"
    elif "周" in text or "week" in text.lower():
        req.setdefault("schedule", ans)
        req["schedule"] = ans
    elif "学生" in text or "对象" in text or "student" in text.lower():
        req["audience"] = ans
    elif "课程名" in text or "title" in text.lower():
        req["course_title"] = ans
    else:
        req["notes"] = (req.get("notes", "") + f"\n{text} → {ans}").strip()[:4000]
