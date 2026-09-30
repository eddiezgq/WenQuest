"""WenQuest API gateway: the single entry point for the WenQuest frontend."""
from __future__ import annotations

import asyncio
import json
import sys
import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from typing import Annotated, Any

import httpx
from cryptography.fernet import InvalidToken
from fastapi import Depends, FastAPI, File, Form, Header, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field

from . import accounts
from . import catalog_api
from . import content
from . import course_api
from . import edit_api
from . import learn_api
from . import course_builder as cb
from . import generate as gen
from . import materials as mt
from . import slides as sl
from . import studio as st
from . import studio_api
from .ai import ModelGateway
from .mailer import Mailer
from .config import Settings, get_settings
from .moodle import EngineError, MoodleClient
from .multilang import plain, resolve
from .session import Session, SessionCodec

VERSION = "0.15.1"
FILE_TTL = 86400  # signed file links live one day


class State:
    settings: Settings
    http: httpx.AsyncClient
    moodle: MoodleClient
    codec: SessionCodec
    ai: ModelGateway
    store: mt.Store
    slides: sl.SlideStore
    studio: st.Studio
    slide_settings: sl.Settings


state = State()


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    state.settings = s
    state.http = httpx.AsyncClient(timeout=s.http_timeout, follow_redirects=False)
    state.moodle = MoodleClient(s.moodle_url, s.moodle_service, state.http, s.moodle_connect_url)
    state.codec = SessionCodec(s.secret_key, s.session_days)
    state.ai = ModelGateway(s.ai_provider, state.http, anthropic_key=s.anthropic_api_key,
                            claude_model=s.claude_model, deepseek_key=s.deepseek_api_key,
                            deepseek_model=s.deepseek_model, timeout=s.ai_timeout,
                            fake_delay=s.ai_fake_delay)
    state.store = mt.Store(s.import_dir)
    state.slides = sl.SlideStore(str(Path(s.data_dir) / "slides"))
    state.slide_settings = sl.Settings(str(Path(s.data_dir) / "settings.json"))
    state.projects_dir = str(Path(s.data_dir) / "projects")
    state.accounts = accounts.Store(str(Path(s.data_dir) / "accounts"))
    state.mailer = Mailer(s.smtp_host, s.smtp_port, s.smtp_secure, s.smtp_user, s.smtp_password,
                          s.mail_from, s.mail_from_name)
    pace = asyncio.create_task(_pace_loop())
    sweep = asyncio.create_task(_accounts_loop())
    yield
    pace.cancel()
    sweep.cancel()
    await state.http.aclose()

log = logging.getLogger("wenquest.gateway")


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="WenQuest Gateway", version=VERSION, lifespan=lifespan,
                  docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_list, allow_credentials=False,
                       allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Authorization", "Content-Type"])

    @app.exception_handler(EngineError)
    async def _engine_error(_: Request, exc: EngineError):
        return JSONResponse({"error": exc.code, "detail": exc.message}, status_code=exc.status)

    @app.exception_handler(Exception)
    async def _unexpected(req: Request, exc: Exception):
        # Log the real cause for the administrator; give the page a code it can show instead of a bare 500.
        log.exception("unhandled error on %s %s", req.method, req.url.path)
        return JSONResponse({"error": "server_error", "detail": type(exc).__name__}, status_code=500)

    register(app)
    accounts.register(app, sys.modules[__name__])
    catalog_api.register(app, sys.modules[__name__])
    studio_api.register(app, sys.modules[__name__])
    course_api.register(app, sys.modules[__name__])
    learn_api.register(app, sys.modules[__name__])
    edit_api.register(app, sys.modules[__name__])
    return app


# --- helpers ------------------------------------------------------------

def lang_of(req_lang: str | None, sess: Session | None = None) -> str:
    lang = (req_lang or (sess.lang if sess else None) or state.settings.default_lang).lower()
    return "zh" if lang.startswith("zh") else "en"


async def current(authorization: Annotated[str | None, Header()] = None) -> Session:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise EngineError("not_logged_in", "missing bearer token", 401)
    sess = state.codec.read(authorization.split(" ", 1)[1].strip())
    if not sess:
        raise EngineError("session_expired", "invalid or expired session", 401)
    return sess


def sign_file(moodle_token: str):
    def _sign(url: str) -> str:
        body = json.dumps({"u": url, "t": moodle_token}).encode()
        tok = state.codec.fernet.encrypt(body).decode()
        return f"{state.settings.public_url.rstrip('/')}/api/v1/files/{tok}"
    return _sign


def proxied(url: str | None, moodle_token: str) -> str | None:
    """Route a Moodle file URL through the file proxy; leave other URLs alone."""
    if not url or url.startswith("data:"):
        return None
    base = state.settings.moodle_url.rstrip("/")
    if url.startswith(base + "/pluginfile.php/"):
        url = url.replace("/pluginfile.php/", "/webservice/pluginfile.php/", 1)
    if url.startswith(base + "/webservice/pluginfile.php/"):
        return sign_file(moodle_token)(url)
    return url


# --- schemas ------------------------------------------------------------

class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)
    lang: str | None = None


class UserOut(BaseModel):
    id: int
    fullname: str
    username: str
    avatar: str | None = None
    lang: str
    can_create_courses: bool = False
    classic_url: str = ""  # Moodle's address, for pages the new UI links out to (calendar, messages)


class GenLesson(BaseModel):
    title: cb.Text
    goal: cb.Text = cb.Text()
    content: cb.Text = cb.Text()
    sources: list[str] = Field(default_factory=list, max_length=8)


class GenSection(cb.DraftSection):
    lessons: list[GenLesson] = Field(default_factory=list, max_length=12)


class GenOutline(cb.Draft):
    sections: list[GenSection] = Field(min_length=1, max_length=20)
    files: dict[str, Any] = Field(default_factory=dict)


class SlideSettingsIn(BaseModel):
    allow_download: bool


class GenerateIn(BaseModel):
    languages: cb.Languages = "zh"
    brief: cb.Brief | None = None        # describe mode: "one sentence" course building
    outline: GenOutline | None = None    # the teacher looked at the outline first ("先看大纲")


class LoginOut(BaseModel):
    token: str
    user: UserOut


class FileEdit(BaseModel):
    id: str
    category: str
    chapter: int | None = None


class PlanIn(BaseModel):
    languages: cb.Languages = "zh"


# --- routes -------------------------------------------------------------

def register(app: FastAPI) -> None:
    @app.get("/api/health")
    async def health():
        # Which model is configured (never the key), so an administrator can check without logging in.
        animator: Any = False
        if state.settings.animator_url:
            try:
                async with httpx.AsyncClient(timeout=2.0, trust_env=False) as c:
                    r = await c.get(state.settings.animator_url.rstrip("/") + "/health")
                animator = r.json() if r.status_code == 200 else "down"
            except (httpx.HTTPError, ValueError):
                animator = "down"
        labcheck: Any = False
        if state.settings.labcheck_url:
            try:
                async with httpx.AsyncClient(timeout=2.0, trust_env=False) as c:
                    r = await c.get(state.settings.labcheck_url.rstrip("/") + "/health")
                labcheck = r.json() if r.status_code == 200 else "down"
            except (httpx.HTTPError, ValueError):
                labcheck = "down"
        return {"ok": True, "version": VERSION, "ai": state.ai.provider, "slides": state.slides.available,
                "slide_queue": state.slides.overview(), "animator": animator, "labcheck": labcheck}

    @app.post("/api/v1/auth/login", response_model=LoginOut)
    async def login(body: LoginIn, response: Response):
        # User name or email (Moodle's authloginviaemail is on).
        mtoken = await state.moodle.login(body.username.strip(), body.password)
        info = await state.moodle.site_info(mtoken)
        lang = lang_of(body.lang or info.get("lang"))
        token = state.codec.issue(Session(moodle_token=mtoken, user_id=int(info["userid"]), lang=lang))
        set_sso_cookie(response, token)  # signed in on the academy website and every platform too
        return LoginOut(token=token, user=_user(info, lang, await can_create(mtoken)))

    @app.get("/api/v1/me", response_model=UserOut)
    async def me(sess: Annotated[Session, Depends(current)], lang: str | None = None):
        info = await state.moodle.site_info(sess.moodle_token)
        return _user(info, lang_of(lang, sess), await can_create(sess.moodle_token))

    @app.get("/api/v1/courses")
    async def courses(sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = lang_of(lang, sess)
        rows = await state.moodle.user_courses(sess.moodle_token, sess.user_id, lg)
        out = []
        for c in rows:
            if not c.get("visible", 1):
                continue
            # Only a picture the teacher uploaded; Moodle's generated pattern is replaced by our own art.
            image = proxied(_course_image(c), sess.moodle_token)
            out.append({
                "id": c["id"],
                "shortname": c.get("shortname", ""),
                "name": plain(c.get("fullname"), lg),
                "summary": plain(c.get("summary"), lg),
                "image": image,
                "progress": c.get("progress"),
                "lastaccess": c.get("lastaccess"),
            })
        out.sort(key=lambda c: -(c["lastaccess"] or 0))
        return {"courses": out}

    @app.get("/api/v1/courses/{courseid}")
    async def course_info(courseid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = lang_of(lang, sess)
        tok = sess.moodle_token
        c = await state.moodle.course(tok, courseid, lg)
        if not c:
            raise EngineError("not_found", "course", 404)
        try:
            teacher = await state.moodle.can_edit_course(tok, courseid)
        except EngineError:
            teacher = False
        return {
            "id": courseid,
            "shortname": c.get("shortname", ""),
            "name": plain(c.get("fullname"), lg),
            "summary": content.clean(resolve(c.get("summary"), lg), state.settings.moodle_url, sign_file(tok)),
            "image": proxied(_course_image(c), tok),
            "teachers": [plain(t.get("fullname"), lg) for t in c.get("contacts") or []],
            "start": c.get("startdate") or None,
            "end": c.get("enddate") or None,
            "role": "teacher" if teacher else "student",
            "classic_url": f"{state.settings.moodle_url.rstrip('/')}/course/view.php?id={courseid}",
        }

    @app.get("/api/v1/courses/{courseid}/outline")
    async def outline(courseid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = lang_of(lang, sess)
        sections = await state.moodle.course_contents(sess.moodle_token, courseid, lg)
        out = []
        for sec in sections:
            if not sec.get("uservisible", True) and not sec.get("modules"):
                continue
            mods = []
            for m in sec.get("modules", []):
                if m.get("modname") == "label":
                    mods.append({"id": m["id"], "type": "label",
                                 "html": content.clean(resolve(m.get("description"), lg),
                                                       state.settings.moodle_url, sign_file(sess.moodle_token))})
                    continue
                item = {
                    "id": m["id"],
                    "type": m.get("modname"),
                    "name": plain(m.get("name"), lg),
                    "locked": not m.get("uservisible", True),
                    # Hidden from students; only teachers receive these modules at all.
                    "hidden": not m.get("visible", 1),
                    "completed": (m.get("completiondata") or {}).get("state") in (1, 2),
                    "has_completion": bool(m.get("completion")),
                }
                if m.get("modname") == "resource":
                    f = next((x for x in m.get("contents") or [] if x.get("type") == "file"), None)
                    if f:
                        item["file"] = {"name": f.get("filename"), "size": f.get("filesize"),
                                        "mimetype": f.get("mimetype"),
                                        "kind": content.file_kind(f.get("filename"), f.get("mimetype"))}
                        if item["file"]["kind"] == "slides" and f.get("fileurl"):
                            # Convert decks ahead of time, so opening the slides never waits.
                            _prepare_deck(f, sess.moodle_token)
                mods.append(item)
            name = plain(sec.get("name"), lg)
            if sec.get("section") == 0 and not mods:
                continue
            out.append({
                "id": sec["id"],
                "number": sec.get("section"),
                "name": name,
                "summary": plain(sec.get("summary"), lg),
                "visible": bool(sec.get("visible", 1)),
                "modules": mods,
            })
        return {"course_id": courseid, "sections": out}

    @app.get("/api/v1/activities/{cmid}")
    async def activity(cmid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = lang_of(lang, sess)
        tok = sess.moodle_token
        cm = await state.moodle.course_module(tok, cmid, lg)
        kind, courseid, inst = cm["modname"], int(cm["course"]), int(cm["instance"])
        sign = sign_file(tok)
        base: dict[str, Any] = {"id": cmid, "type": kind, "course_id": courseid,
                                "name": plain(cm.get("name"), lg)}
        if kind == "page":
            page = next((p for p in await state.moodle.pages(tok, courseid, lg) if p["id"] == inst), None)
            if not page:
                raise EngineError("not_found", "page", 404)
            base["html"] = content.clean(resolve(page.get("content"), lg), state.settings.moodle_url, sign)
            base["intro"] = plain(page.get("intro"), lg)
            try:
                await state.moodle.view_page(tok, inst)
            except EngineError:
                pass  # logging a view must never block reading
        elif kind == "url":
            u = next((x for x in await state.moodle.urls(tok, courseid, lg) if x["id"] == inst), None)
            if not u:
                raise EngineError("not_found", "url", 404)
            base["url"] = u.get("externalurl")
            base["intro"] = content.clean(resolve(u.get("intro"), lg), state.settings.moodle_url, sign)
        elif kind == "assign":
            a = next((x for x in await state.moodle.assignments(tok, courseid, lg) if x["cmid"] == cmid), None)
            if not a:
                raise EngineError("not_found", "assign", 404)
            base["intro"] = content.clean(resolve(a.get("intro"), lg), state.settings.moodle_url, sign)
            base["due"] = a.get("duedate") or None
            base["cutoff"] = a.get("cutoffdate") or None
        elif kind == "resource":
            sections = await state.moodle.course_contents(tok, courseid, lg)
            mod = next((m for s in sections for m in s.get("modules", []) if m["id"] == cmid), None)
            files = []
            for f in (mod or {}).get("contents", []):
                if f.get("type") == "file" and f.get("fileurl"):
                    kind = content.file_kind(f.get("filename"), f.get("mimetype"))
                    item = {"name": f.get("filename"), "size": f.get("filesize"),
                            "mimetype": f.get("mimetype"), "kind": kind, "url": sign(f["fileurl"])}
                    if kind == "lab":
                        item["lab_url"] = item["url"].replace("/api/v1/files/", "/api/v1/labs/", 1)
                    files.append(item)
            base["files"] = files
            base["kind"] = files[0]["kind"] if files else "file"
            base["hidden"] = not (mod or {}).get("visible", 1)
        # Anything the new UI does not render yet opens in Moodle's classic view.
        base["classic_url"] = f"{state.settings.moodle_url.rstrip('/')}/mod/{kind}/view.php?id={cmid}"
        return base

    # --- AI course workshop -------------------------------------------------

    @app.post("/api/v1/ai/outline")
    async def ai_outline(body: cb.Brief, sess: Annotated[Session, Depends(current)]):
        await require_creator(sess)
        data = await state.ai.json(system=cb.SYSTEM, prompt=cb.outline_prompt(body),
                                   schema=cb.outline_schema(body.languages, body.assignments),
                                   max_tokens=8000, fake=lambda: cb.fake_outline(body))
        outline = cb.norm_outline(data, body)
        if not outline["sections"]:
            raise EngineError("ai_bad_output", "the model returned no sections", 502)
        return outline

    @app.post("/api/v1/ai/lesson")
    async def ai_lesson(body: cb.LessonRequest, sess: Annotated[Session, Depends(current)]):
        await require_creator(sess)
        items = {m.id: m for m in _materials(body.import_id, sess)} if body.import_id and body.sources else {}
        clean = await gen.write_lesson(state.ai, state.store, body, items, _clean)
        return {"content": clean}

    @app.post("/api/v1/courses")
    async def publish_course(draft: cb.Draft, sess: Annotated[Session, Depends(current)]):
        if not await can_create(sess.moodle_token):
            raise EngineError("forbidden", "you may not create courses", 403)
        payload = cb.to_moodle(draft, lambda h: content.clean(h, state.settings.moodle_url, lambda u: u))
        if draft.import_id:
            items = {m.id: m for m in _materials(draft.import_id, sess)}
            for sec, out in zip(draft.sections, payload["sections"]):
                for fid in sec.files:
                    m = items.get(fid)
                    if not m:
                        continue
                    item = await state.moodle.upload(sess.moodle_token, m.name, state.store.data(draft.import_id, fid))
                    out["activities"].append({
                        "type": "resource", "name": Path(m.name).stem, "draftitemid": item,
                        "visible": 0 if m.category in mt.TEACHER_ONLY else 1,
                    })
        result = await state.moodle.call(sess.moodle_token, "local_wenquest_create_course", None, **payload)
        return {"course_id": result["courseid"], "shortname": result["shortname"], "activities": result["activities"]}

    # --- importing course materials ------------------------------------------

    @app.post("/api/v1/imports")
    async def import_start(sess: Annotated[Session, Depends(current)]):
        if not await can_create(sess.moodle_token):
            raise EngineError("forbidden", "you may not create courses", 403)
        return {"import_id": state.store.new_session(sess.user_id)}

    @app.post("/api/v1/imports/{iid}/files")
    async def import_file(iid: str, sess: Annotated[Session, Depends(current)],
                          file: UploadFile = File(...), path: str = Form("")):
        return await ingest(iid, sess, file, path)

    @app.get("/api/v1/imports/{iid}")
    async def import_list(iid: str, sess: Annotated[Session, Depends(current)]):
        return {"files": [m.public() for m in _materials(iid, sess)], "categories": mt.CATEGORIES}

    @app.post("/api/v1/imports/{iid}/classify")
    async def import_classify(iid: str, sess: Annotated[Session, Depends(current)]):
        items = _materials(iid, sess)
        if state.ai.available and state.ai.provider != "fake" and items:
            data = await state.ai.json(system=cb.SYSTEM, prompt=mt.classify_prompt(items),
                                       schema=mt.classify_schema(), max_tokens=4000)
            mt.apply_ai(items, data)
            state.store.put_materials(iid, sess.user_id, items)
            state.store.mark_classified(iid, sess.user_id)
        return {"files": [m.public() for m in items], "categories": mt.CATEGORIES}

    @app.put("/api/v1/imports/{iid}/files")
    async def import_edit(iid: str, edits: list[FileEdit], sess: Annotated[Session, Depends(current)]):
        items = {m.id: m for m in _materials(iid, sess)}
        for e in edits:
            m = items.get(e.id)
            if m and e.category in mt.CATEGORIES:
                if (m.category, m.chapter) != (e.category, e.chapter):
                    m.confidence = "teacher"
                m.category, m.chapter = e.category, (e.chapter if e.chapter and e.chapter > 0 else None)
        state.store.put_materials(iid, sess.user_id, list(items.values()))
        return {"files": [m.public() for m in items.values()]}

    @app.post("/api/v1/imports/{iid}/outline")
    async def import_outline(iid: str, body: PlanIn, sess: Annotated[Session, Depends(current)]):
        await require_creator(sess)
        lang = "en" if body.languages == "en" else "zh"
        return await gen.plan_from_materials(state.ai, _materials(iid, sess), lambda f: state.store.text(iid, f), lang, iid)

    # --- one-click generation (D28) ------------------------------------------------

    @app.post("/api/v1/imports/{iid}/generate")
    async def import_generate(iid: str, body: GenerateIn, sess: Annotated[Session, Depends(current)]):
        await require_creator(sess)
        _materials(iid, sess)  # ownership check
        outline = body.outline.model_dump() if body.outline else None
        if outline:
            outline["import_id"] = iid
            for s in outline["sections"]:
                for les in s["lessons"]:
                    les.setdefault("goal", {})
        return _gen().start(iid, sess.user_id, body.languages, body.brief, outline)

    @app.get("/api/v1/imports/{iid}/job")
    async def import_job(iid: str, sess: Annotated[Session, Depends(current)]):
        _materials(iid, sess)
        job = _gen().status(iid, sess.user_id)
        if not job:
            raise EngineError("not_found", "nothing is being generated", 404)
        return job

    @app.post("/api/v1/imports/{iid}/job/lessons/{si}/{li}")
    async def import_job_retry(iid: str, si: int, li: int, sess: Annotated[Session, Depends(current)]):
        await require_creator(sess)
        _materials(iid, sess)
        return _gen().retry(iid, sess.user_id, si, li)

    @app.get("/api/v1/ai/status")
    async def ai_status(sess: Annotated[Session, Depends(current)]):
        return {"available": state.ai.available, "provider": state.ai.provider,
                "can_create_courses": await can_create(sess.moodle_token)}

    # --- slides presented in the browser (R12) -------------------------------------

    @app.get("/api/v1/slides/{cmid}")
    async def slides(cmid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = lang_of(lang, sess)
        tok = sess.moodle_token
        cm = await state.moodle.course_module(tok, cmid, lg)
        if cm.get("modname") != "resource":
            raise EngineError("not_slides", "not a slide deck", 415)
        courseid = int(cm["course"])
        sections = await state.moodle.course_contents(tok, courseid, lg)
        mod = next((m for s in sections for m in s.get("modules", []) if m["id"] == cmid), None)
        f = next((x for x in (mod or {}).get("contents", []) if x.get("type") == "file"
                  and content.file_kind(x.get("filename"), x.get("mimetype")) == "slides"), None)
        if not f or not f.get("fileurl"):
            raise EngineError("not_slides", "not a slide deck", 415)
        teacher = await state.moodle.can_edit_course(tok, courseid)
        allow = bool(state.slide_settings.get(cmid).get("allow_download"))
        out: dict[str, Any] = {
            "id": cmid, "course_id": courseid, "name": plain(cm.get("name"), lg), "teacher": teacher,
            "allow_download": allow, "file_name": f.get("filename"),
            "download_url": sign_file(tok)(f["fileurl"]) if teacher or allow else None,
        }
        if not state.slides.available:
            return {**out, "status": "unavailable"}
        src = _prepare_deck(f, tok, priority=0)  # someone is looking at this deck: it goes first
        status, key = state.slides.status(src)
        out["status"] = status
        if status == "converting":
            out.update(state.slides.progress(src))
        if status == "ready" and key:
            m = state.slides.manifest(key) or {}
            base = f"{state.settings.public_url.rstrip('/')}/api/v1/slides/files/{key}/"
            out.update(pages=m.get("pages", 0), width=m.get("width"), height=m.get("height"), slides=[{
                "image": base + s["image"], "thumb": base + s["thumb"], "labs": s.get("labs", []),
                "videos": [{**v, "src": base + v["src"]} for v in s.get("videos", [])],
                "links": s.get("links", []),
                **({"notes": s.get("notes", "")} if teacher else {}),
            } for s in m.get("slides", [])])
        return out

    @app.post("/api/v1/slides/{cmid}/retry")
    async def slides_retry(cmid: int, sess: Annotated[Session, Depends(current)]):
        state.slides.failed.clear()
        return await slides(cmid, sess)  # queues it again, at the front

    @app.put("/api/v1/slides/{cmid}/settings")
    async def slides_settings(cmid: int, body: SlideSettingsIn, sess: Annotated[Session, Depends(current)]):
        cm = await state.moodle.course_module(sess.moodle_token, cmid)
        if not await state.moodle.can_edit_course(sess.moodle_token, int(cm["course"])):
            raise EngineError("forbidden", "only teachers change this", 403)
        return state.slide_settings.set(cmid, allow_download=body.allow_download)

    @app.get("/api/v1/slides/files/{key}/{name}")
    async def slide_file(key: str, name: str):
        """Slide images and embedded videos. The content hash in the path is the capability:
        it is only handed to people who may open the deck, and the files never change."""
        p = state.slides.file(key, name)
        if not p:
            raise EngineError("not_found", "no such slide file", 404)
        return FileResponse(p, headers={"Cache-Control": "private, max-age=31536000, immutable",
                                        "X-Content-Type-Options": "nosniff"})

    @app.get("/api/v1/labs/{signed}")
    async def labs(signed: str):
        """Run a teacher's HTML lab. The page gets its own opaque origin (CSP sandbox without
        allow-same-origin), so its scripts can run but cannot reach WenQuest cookies, storage or APIs."""
        r = await state.moodle.fetch_file(*_unsign(signed))
        if not r.headers.get("content-type", "").lower().startswith("text/html"):
            raise EngineError("not_a_lab", "not an HTML file", 415)
        return Response(r.content, media_type="text/html; charset=utf-8", headers={
            "Cache-Control": "private, max-age=3600",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "sandbox allow-scripts allow-popups allow-forms allow-modals allow-downloads; "
                                       "frame-ancestors 'self'",
        })

    @app.get("/api/v1/files/{signed}")
    async def files(signed: str, range: Annotated[str | None, Header()] = None):
        mtoken, url = _unsign(signed)
        r = await state.moodle.fetch_file(mtoken, url)
        ctype = r.headers.get("content-type", "application/octet-stream")
        headers = {
            "Cache-Control": "private, max-age=3600",
            "X-Content-Type-Options": "nosniff",
            # Files are served from the app's own domain: never let one run script there.
            "Content-Security-Policy": "default-src 'none'; img-src 'self' data:; media-src 'self'; "
                                       "style-src 'unsafe-inline'; sandbox",
        }
        base_type = ctype.split(";")[0].strip().lower()
        inline = base_type.startswith(("image/", "video/", "audio/")) or base_type in ("application/pdf", "text/plain")
        headers["Content-Disposition"] = _disposition("inline" if inline else "attachment", _file_name(url))
        headers["Accept-Ranges"] = "bytes"
        body, total = r.content, len(r.content)
        if range and (span := _byte_range(range, total)):
            start, end = span
            headers["Content-Range"] = f"bytes {start}-{end}/{total}"
            return Response(body[start:end + 1], status_code=206, media_type=ctype, headers=headers)
        return Response(body, media_type=ctype, headers=headers)


def _unsign(signed: str) -> tuple[str, str]:
    """(moodle token, file url) from a signed file link."""
    try:
        raw = state.codec.fernet.decrypt(signed.encode(), ttl=FILE_TTL)
    except (InvalidToken, ValueError):
        raise EngineError("link_expired", "file link expired", 410)
    d = json.loads(raw)
    return d["t"], d["u"]


def _course_image(c: dict) -> str | None:
    uploaded = next((f.get("fileurl") for f in c.get("overviewfiles") or [] if f.get("fileurl")), None)
    if uploaded:
        return uploaded
    img = c.get("courseimage") or ""
    return img if "/pluginfile.php/" in img and "/course/generated" not in img else None


def _file_name(url: str) -> str:
    """The file name at the end of a Moodle file URL (percent-decoded, query removed)."""
    return unquote(urlsplit(url).path.rsplit("/", 1)[-1]) or "file"


def _disposition(kind: str, name: str) -> str:
    """Content-Disposition that survives non-ASCII names (headers must be Latin-1; RFC 6266 filename*)."""
    stem, dot, ext = name.rpartition(".")
    ascii_name = name if name.isascii() else (f"file.{ext}" if dot and ext.isascii() else "file")
    ascii_name = ascii_name.replace('"', "").replace("\\", "")
    return f"{kind}; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(name, safe='')}"


def _byte_range(header: str, total: int) -> tuple[int, int] | None:
    """Parse a single 'bytes=a-b' range (what browsers send when seeking in a video)."""
    if not header.startswith("bytes=") or "," in header or total == 0:
        return None
    a, _, b = header[6:].strip().partition("-")
    try:
        if a == "":
            n = int(b)
            return (max(0, total - n), total - 1) if n > 0 else None
        start = int(a)
        end = min(int(b), total - 1) if b else total - 1
    except ValueError:
        return None
    return (start, end) if 0 <= start <= end else None


def _user(info: dict, lang: str, creator: bool = False) -> UserOut:
    pic = info.get("userpictureurl")
    return UserOut(id=int(info["userid"]), fullname=info.get("fullname", ""),
                   username=info.get("username", ""), avatar=pic, lang=lang, can_create_courses=creator,
                   classic_url=state.settings.moodle_url.rstrip("/"))


async def can_create(moodle_token: str) -> bool:
    """Whether this user may create courses (needs the local_wenquest plugin in Moodle)."""
    try:
        perms = await state.moodle.call(moodle_token, "local_wenquest_get_permissions")
        return bool(perms.get("cancreatecourses"))
    except EngineError:
        return False


def _materials(iid: str, sess: Session) -> list[mt.Material]:
    try:
        return state.store.materials(iid, sess.user_id)
    except PermissionError:
        raise EngineError("forbidden", "not your import", 403)
    except (KeyError, OSError):
        raise EngineError("not_found", "import not found or expired", 404)


async def ingest(iid: str, sess: Session, file: UploadFile, path: str) -> dict:
    """Store one uploaded file in an import session: repair its name, read its text, guess what it is."""
    _materials(iid, sess)  # ownership check
    data = await file.read(mt.MAX_FILE + 1)
    if len(data) > mt.MAX_FILE:
        raise EngineError("file_too_large", "files are limited to 190 MB", 413)
    name = mt.fix_name(Path((file.filename or "file").replace("\\", "/")).name)
    rel = mt.fix_name((path or name).replace("\\", "/").lstrip("/"))[:300]
    m = mt.Material(id=uuid.uuid4().hex, name=name, path=rel, size=len(data), ext=Path(name).suffix.lower())
    text = ""
    try:
        # Reading a whole textbook takes seconds: do it off the event loop.
        text, m.pages = await asyncio.to_thread(mt.extract, name, data)
    except mt.ScannedPDF:
        m.error = "scanned"
    except ValueError:
        m.error = "unsupported"
    except Exception:  # corrupt or encrypted files must not break the whole import
        m.error = "unreadable"
    text = mt.clean(text)[:mt.MAX_TEXT]
    m.chars, m.excerpt = len(text), text[:1500]
    mt.classify_rule(m)
    m.headings = mt.headings(text, m.chapter)
    state.store.add(iid, sess.user_id, m, data, text)
    return m.public()


def _prepare_deck(f: dict, moodle_token: str, priority: int = 1) -> str:
    """Start converting a deck in the background if needed; return its source key."""
    src = sl.SlideStore.source_key(f["fileurl"], f.get("timemodified"), f.get("filesize"))

    async def fetch() -> bytes:
        return (await state.moodle.fetch_file(moodle_token, f["fileurl"])).content

    state.slides.start(src, fetch, Path(f.get("filename") or "deck.pptx").suffix.lower(), priority)
    return src


def _clean(h: str) -> str:
    return content.clean(h, state.settings.moodle_url, lambda u: u)


def _studio() -> st.Studio:
    """The AI professor team, rebuilt if the store or model gateway was replaced (tests)."""
    s = getattr(state, "studio", None)
    if s is None or s.store is not state.store or s.ai is not state.ai:
        s = state.studio = st.Studio(st.Projects(getattr(state, "projects_dir", "/tmp/wq-data/projects")),
                                     state.store, state.ai, _clean)
    s.animator_url = state.settings.animator_url
    s.animator_timeout = state.settings.animator_timeout
    s.labcheck_url = state.settings.labcheck_url
    s.labcheck_timeout = state.settings.labcheck_timeout
    return s


async def _pace_loop() -> None:
    """Daily pace: every five minutes, write the next lesson for courses that asked for one a day."""
    while True:
        await asyncio.sleep(300)
        try:
            await _studio().tick()
        except Exception:
            log.exception("daily pace check failed")


def _gen() -> gen.Generator:
    """The background generator, rebuilt if the store or model gateway was replaced (tests)."""
    g = getattr(state, "gen", None)
    if g is None or g.store is not state.store or g.ai is not state.ai:
        g = state.gen = gen.Generator(state.store, state.ai, _clean)
    return g


async def _accounts_loop() -> None:
    """Review forgotten teacher applications and send the administrator's summary email."""
    while True:
        await asyncio.sleep(300)
        try:
            await accounts_sweep()
        except Exception:  # noqa: BLE001 - keep the loop alive
            log.exception("accounts sweep failed")


async def require_creator(sess: Session) -> None:
    if not await can_create(sess.moodle_token):
        raise EngineError("forbidden", "you may not create courses", 403)
    if not state.ai.available:
        raise EngineError("ai_unavailable", "no AI model is configured", 503)


app = create_app()
