"""WenQuest API gateway: the single entry point for the WenQuest frontend."""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Annotated, Any

import httpx
from cryptography.fernet import InvalidToken
from fastapi import Depends, FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from . import content
from .config import Settings, get_settings
from .moodle import EngineError, MoodleClient
from .multilang import plain, resolve
from .session import Session, SessionCodec

VERSION = "0.2.0"
FILE_TTL = 86400  # signed file links live one day


class State:
    settings: Settings
    http: httpx.AsyncClient
    moodle: MoodleClient
    codec: SessionCodec


state = State()


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    state.settings = s
    state.http = httpx.AsyncClient(timeout=s.http_timeout, follow_redirects=False)
    state.moodle = MoodleClient(s.moodle_url, s.moodle_service, state.http, s.moodle_connect_url)
    state.codec = SessionCodec(s.secret_key, s.session_days)
    yield
    await state.http.aclose()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="WenQuest Gateway", version=VERSION, lifespan=lifespan,
                  docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_list, allow_credentials=False,
                       allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Authorization", "Content-Type"])

    @app.exception_handler(EngineError)
    async def _engine_error(_: Request, exc: EngineError):
        return JSONResponse({"error": exc.code, "detail": exc.message}, status_code=exc.status)

    register(app)
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


class LoginOut(BaseModel):
    token: str
    user: UserOut


# --- routes -------------------------------------------------------------

def register(app: FastAPI) -> None:
    @app.get("/api/health")
    async def health():
        return {"ok": True, "version": VERSION}

    @app.post("/api/v1/auth/login", response_model=LoginOut)
    async def login(body: LoginIn):
        mtoken = await state.moodle.login(body.username.strip(), body.password)
        info = await state.moodle.site_info(mtoken)
        lang = lang_of(body.lang or info.get("lang"))
        token = state.codec.issue(Session(moodle_token=mtoken, user_id=int(info["userid"]), lang=lang))
        return LoginOut(token=token, user=_user(info, lang))

    @app.get("/api/v1/me", response_model=UserOut)
    async def me(sess: Annotated[Session, Depends(current)], lang: str | None = None):
        info = await state.moodle.site_info(sess.moodle_token)
        return _user(info, lang_of(lang, sess))

    @app.get("/api/v1/courses")
    async def courses(sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = lang_of(lang, sess)
        rows = await state.moodle.user_courses(sess.moodle_token, sess.user_id, lg)
        out = []
        for c in rows:
            if not c.get("visible", 1):
                continue
            image = c.get("courseimage") or next(
                (f.get("fileurl") for f in c.get("overviewfiles") or [] if f.get("fileurl")), None)
            image = proxied(image, sess.moodle_token)  # data: placeholders -> None; frontend draws its own
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
                mods.append({
                    "id": m["id"],
                    "type": m.get("modname"),
                    "name": plain(m.get("name"), lg),
                    "locked": not m.get("uservisible", True),
                    "completed": (m.get("completiondata") or {}).get("state") in (1, 2),
                    "has_completion": bool(m.get("completion")),
                })
            name = plain(sec.get("name"), lg)
            if sec.get("section") == 0 and not mods:
                continue
            out.append({
                "id": sec["id"],
                "number": sec.get("section"),
                "name": name,
                "summary": plain(sec.get("summary"), lg),
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
                    files.append({"name": f.get("filename"), "size": f.get("filesize"),
                                  "mimetype": f.get("mimetype"), "url": sign(f["fileurl"])})
            base["files"] = files
        # Anything the new UI does not render yet opens in Moodle's classic view.
        base["classic_url"] = f"{state.settings.moodle_url.rstrip('/')}/mod/{kind}/view.php?id={cmid}"
        return base

    @app.get("/api/v1/files/{signed}")
    async def files(signed: str):
        try:
            raw = state.codec.fernet.decrypt(signed.encode(), ttl=FILE_TTL)
        except (InvalidToken, ValueError):
            raise EngineError("link_expired", "file link expired", 410)
        d = json.loads(raw)
        r = await state.moodle.fetch_file(d["t"], d["u"])
        headers = {"Cache-Control": "private, max-age=3600"}
        if cd := r.headers.get("content-disposition"):
            headers["Content-Disposition"] = cd
        return Response(r.content, media_type=r.headers.get("content-type", "application/octet-stream"),
                        headers=headers)


def _user(info: dict, lang: str) -> UserOut:
    pic = info.get("userpictureurl")
    return UserOut(id=int(info["userid"]), fullname=info.get("fullname", ""),
                   username=info.get("username", ""), avatar=pic, lang=lang)


app = create_app()
