"""白板课接口（第 35 轮第 3 步）：老师菜单“白板课”、编辑器、AI 建课里的“白板讲解”。只有本人能看、能改。

    GET    /api/v1/whiteboards                       我的白板课
    POST   /api/v1/whiteboards                       新建：题目（全自动）或录音（等上传）
    GET    /api/v1/whiteboards/{id}                  一节课（讲稿、画板、链接、进度）
    PUT    /api/v1/whiteboards/{id}                  保存（标题、讲稿文字、画板）
    DELETE /api/v1/whiteboards/{id}
    POST   /api/v1/whiteboards/{id}/compile          预览用的播放数据
    POST   /api/v1/whiteboards/{id}/revoice          改过讲稿后重新配音（只配改过的段）
    POST   /api/v1/whiteboards/{id}/redo             请 AI 重排（整节或一张画板）
    POST   /api/v1/whiteboards/{id}/upload           上传录音或视频（分片）
    POST   /api/v1/whiteboards/{id}/mp4              出视频
    GET    /api/v1/whiteboards/{id}/media            可插入的实验、动画、视频
    POST   /api/v1/studio/projects/{pid}/lessons/{lid}/whiteboard   AI 建课里一讲的“白板讲解”
    GET    /api/v1/whiteboards/play/{signed}         网页版（有时效的链接）
    GET    /api/v1/whiteboards/file/{signed}         配音、MP4、框里的视频和实验页
    GET    /api/v1/whiteboards/assets/{player.js|rough.js}  编辑器预览用的播放器
"""

import json
import re
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

from .moodle import EngineError
from .production.whiteboard import core
from .session import Session
from .whiteboards import AUDIO_EXT, VIDEO_EXT, Whiteboards, summary

CHUNK_MAX = 64 * 1024 ** 2
UPLOAD_MAX = {"recording": 300 * 1024 ** 2, "video": 200 * 1024 ** 2}
SANDBOX = "sandbox allow-scripts allow-popups allow-forms allow-modals; frame-ancestors 'self'"
VOICE_IDS = re.compile(r"^[a-z]{1,3}_[a-z0-9_]{1,30}$")


class NewIn(BaseModel):
    source: str = Field(default="topic", pattern=r"^(topic|recording)$")
    topic: str = Field(default="", max_length=200)
    note: str = Field(default="", max_length=30000)
    minutes: float = Field(default=6, ge=1, le=20)
    voice: str = Field(default="zm_yunjian", max_length=40)
    course_pid: str = Field(default="", max_length=40)
    book: str = Field(default="", max_length=40)


class SegIn(BaseModel):
    zh: str = Field(max_length=400)
    en: str = Field(default="", max_length=800)


class SaveIn(BaseModel):
    title: str | None = Field(default=None, max_length=60)
    segments: list[SegIn] | None = None
    scene: dict | None = None


class CompileIn(BaseModel):
    segments: list[SegIn] | None = None
    scene: dict | None = None


class RedoIn(BaseModel):
    note: str = Field(default="", max_length=2000)
    frame: str = Field(default="", max_length=80)


class LessonWbIn(BaseModel):
    voice: str = Field(default="", max_length=40)
    note: str = Field(default="", max_length=4000)


def register(app, m) -> None:
    current = m.current

    def env() -> dict:
        from .textbook_api import media_dir
        st = m._studio()
        return {"ai": m.state.ai, "voice_url": st.voice_url, "labcheck_url": st.labcheck_url, "studio": st,
                "textbook_dir": m.state.settings.textbook_dir, "textbook_media": lambda book: media_dir(m, book)}

    def wbs() -> Whiteboards:
        root = getattr(m.state, "whiteboards_dir", None) or str(Path(m.state.settings.data_dir) / "whiteboards")
        w = getattr(m.state, "whiteboards", None)
        if w is None or str(w.root) != str(root):
            w = m.state.whiteboards = Whiteboards(root, env)
        return w

    def load(wid: str, sess: Session) -> dict:
        try:
            L = wbs().load(wid)
        except KeyError:
            raise EngineError("not_found", "no such whiteboard lesson", 404)
        if L["owner"] != sess.user_id:
            raise EngineError("forbidden", "not your whiteboard lesson", 403)
        return L

    def not_busy(L: dict) -> None:
        if wbs().busy(L["id"]):
            raise EngineError("busy", "this lesson is being worked on; try again when it is done", 409)

    def sign(d: dict) -> str:
        return m.state.codec.fernet.encrypt(json.dumps(d).encode()).decode()

    def base() -> str:
        return m.state.settings.public_url.rstrip("/")

    def file_link(wid: str, what: str, src: str = "") -> str:
        return f"{base()}/api/v1/whiteboards/file/{sign({'w': wid, 'f': what, **({'m': src} if src else {})})}"

    def resolver_links(L: dict):
        """Signed links for the media frames (the web page and the editor's preview)."""
        def resolve_link(src: str):
            f = wbs().media_file(L, src)
            if not f:
                return None
            kind, _, h = f
            return {"kind": kind, "url": file_link(L["id"], "media", src) + (f"#{h}" if h else ""), **({"zoom": 1.0} if kind == "page" else {})}
        return resolve_link

    def compiled(L: dict, scene: dict | None = None, segments: list[dict] | None = None) -> dict:
        return core.compile_scene(scene or L["scene"], segments or L["segments"], L.get("duration", 0),
                                  L.get("moves") or [], resolver_links(L))

    def detail(L: dict) -> dict:
        busy = wbs().busy(L["id"])
        out = summary(L, busy)
        out.update(segments=L.get("segments") or [], scene=L.get("scene"), moves=len(L.get("moves") or []),
                   notes=L.get("notes") or [], voice=L.get("voice"), audio_kind=L.get("audio_kind", ""),
                   voice_stale=bool(L.get("voice_stale")), topic=L.get("topic", ""), book=L.get("book", ""),
                   audio=file_link(L["id"], "audio") if L.get("audio") else "",
                   play=f"{base()}/api/v1/whiteboards/play/{sign({'w': L['id']})}" if L.get("scene") else "",
                   video=file_link(L["id"], "mp4") if (L.get("mp4") or {}).get("state") == "done" else "",
                   mp4_state=(L.get("mp4") or {}).get("state", ""))
        return out

    def ready(L: dict) -> None:
        if not L.get("scene") or not L.get("segments"):
            raise EngineError("not_ready", "the lesson is not made yet", 409)

    # ------------------------------------------------------------------ list, create
    @app.get("/api/v1/whiteboards")
    async def lessons(sess: Annotated[Session, Depends(current)]):
        st = m._studio()
        return {"lessons": [summary(L, wbs().busy(L["id"])) for L in wbs().all(sess.user_id)],
                "voice_on": bool(st.voice_url), "mp4_on": bool(st.labcheck_url)}

    @app.post("/api/v1/whiteboards")
    async def create(body: NewIn, sess: Annotated[Session, Depends(current)]):
        await m.require_creator(sess)
        if body.source == "topic" and not body.topic.strip():
            raise EngineError("bad_request", "a topic please", 400)
        if body.voice and not VOICE_IDS.match(body.voice):
            raise EngineError("bad_voice", "no such voice", 400)
        course = None
        if body.course_pid:
            proj = studio_project(body.course_pid, sess)
            from .studio import disp
            course = {"pid": proj["id"], "title": disp((proj.get("outline") or {}).get("title")) or ""}
        L = wbs().new(sess.user_id, source=body.source, topic=body.topic.strip(), note=body.note, minutes=body.minutes,
                      voice=body.voice or "zm_yunjian", course=course, book=re.sub(r"[^a-z0-9_\-]", "", body.book))
        if body.source == "topic":
            wbs().run(L, "AI 正在写讲稿", wbs().make_from_topic)
        else:
            L["state"] = "waiting"          # the recording comes next (upload?kind=recording)
            wbs().save(L)
        return detail(wbs().load(L["id"]))

    def studio_project(pid: str, sess: Session) -> dict:
        try:
            proj = m._studio().projects.load(pid)
        except KeyError:
            raise EngineError("not_found", "no such course project", 404)
        if proj["owner"] != sess.user_id:
            raise EngineError("forbidden", "not your course project", 403)
        return proj

    @app.get("/api/v1/whiteboards/{wid}")
    async def get(wid: str, sess: Annotated[Session, Depends(current)]):
        return detail(load(wid, sess))

    @app.delete("/api/v1/whiteboards/{wid}")
    async def delete(wid: str, sess: Annotated[Session, Depends(current)]):
        load(wid, sess)
        wbs().remove(wid)
        return {"ok": True}

    # ------------------------------------------------------------------ edit
    @app.put("/api/v1/whiteboards/{wid}")
    async def save(wid: str, body: SaveIn, sess: Annotated[Session, Depends(current)]):
        await m.require_creator(sess)
        L = load(wid, sess)
        not_busy(L)
        if body.title is not None and body.title.strip():
            L["title"] = {**(L.get("title") or {}), "zh": body.title.strip()}
        if body.segments is not None:
            segs = L.get("segments") or []
            if len(body.segments) != len(segs):
                raise EngineError("bad_request", "the number of segments cannot change here", 400)
            for s, new in zip(segs, body.segments):
                if s["zh"] != new.zh.strip() and new.zh.strip():
                    s["zh"] = new.zh.strip()
                    if L.get("audio_kind") in ("ai", "silent"):
                        L["voice_stale"] = True
                if new.en:
                    s["en"] = new.en.strip()
        if body.scene is not None:
            check_scene(body.scene)
            L["scene"] = body.scene
        wbs().save(L)
        return detail(L)

    def check_scene(scene: dict) -> None:
        els = scene.get("elements")
        if not isinstance(els, list) or len(els) > 20000:
            raise EngineError("bad_request", "a drawing please (at most 20000 elements)", 400)
        if len(json.dumps(scene)) > 30 * 1024 ** 2:
            raise EngineError("too_large", "the drawing is too large", 413)
        for e in els:
            if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not isinstance(e.get("type"), str):
                raise EngineError("bad_request", "a drawing element without id or type", 400)

    @app.post("/api/v1/whiteboards/{wid}/compile")
    async def compile_(wid: str, body: CompileIn, sess: Annotated[Session, Depends(current)]):
        L = load(wid, sess)
        ready(L)
        segs = L["segments"]
        if body.segments is not None and len(body.segments) == len(segs):
            segs = [dict(s, zh=n.zh or s["zh"]) for s, n in zip(segs, body.segments)]
        if body.scene is not None:
            check_scene(body.scene)
        try:
            return compiled(L, body.scene, segs)
        except (KeyError, TypeError, ValueError) as e:
            raise EngineError("bad_request", f"the drawing could not be read: {str(e)[:200]}", 400)

    @app.post("/api/v1/whiteboards/{wid}/revoice")
    async def revoice(wid: str, sess: Annotated[Session, Depends(current)]):
        await m.require_creator(sess)
        L = load(wid, sess)
        not_busy(L)
        ready(L)
        if L.get("audio_kind") == "teacher":
            raise EngineError("teacher_recording", "this lesson uses your recording; upload a new recording instead", 409)

        async def job(cur: dict) -> None:
            await wbs().voice(cur)
            cur["voice_stale"] = False
            cur["mp4"] = None
        wbs().run(L, "正在重新配音", job)
        return detail(wbs().load(wid))

    @app.post("/api/v1/whiteboards/{wid}/redo")
    async def redo(wid: str, body: RedoIn, sess: Annotated[Session, Depends(current)]):
        await m.require_creator(sess)
        L = load(wid, sess)
        not_busy(L)
        ready(L)
        note, frame = body.note.strip(), body.frame

        async def job(cur: dict) -> None:
            if frame:
                await wbs().redo_board(cur, frame, note)
            else:
                await wbs().lay_out(cur, note)
        wbs().run(L, "AI 正在重排画板", job)
        return detail(wbs().load(wid))

    @app.get("/api/v1/whiteboards/{wid}/media")
    async def media(wid: str, sess: Annotated[Session, Depends(current)]):
        import asyncio
        L = load(wid, sess)
        return {"media": [{k: x.get(k, "") for k in ("src", "title", "kind", "from")} for x in await asyncio.to_thread(wbs().catalog, L)]}

    @app.post("/api/v1/whiteboards/{wid}/upload")
    async def upload(wid: str, request: Request, sess: Annotated[Session, Depends(current)],
                     kind: str = "recording", upload: str = "", index: int = 0, total: int = 1, name: str = ""):
        """The teacher's recording (the lesson is recognised again) or a video for a frame, in pieces of ≤ 64 MB."""
        await m.require_creator(sess)
        L = load(wid, sess)
        if kind not in UPLOAD_MAX:
            raise EngineError("bad_request", "kind is recording or video", 400)
        ext = Path(name).suffix.lower()
        if ext not in (AUDIO_EXT if kind == "recording" else VIDEO_EXT):
            raise EngineError("bad_file", "an audio file (mp3 m4a wav) or a video (mp4 webm mov) please", 400)
        if not re.fullmatch(r"[a-z0-9]{8,32}", upload) or not (0 <= index < total <= UPLOAD_MAX[kind] // CHUNK_MAX + 1):
            raise EngineError("bad_request", "bad upload piece", 400)
        if index == 0 and kind == "recording":
            not_busy(L)
        folder = wbs().dir(wid) / "_parts"
        folder.mkdir(parents=True, exist_ok=True)
        part = folder / f"{upload}.part"
        if index == 0:
            part.unlink(missing_ok=True)
        elif not part.exists():
            raise EngineError("bad_request", "upload the pieces in order", 400)
        size, got = part.stat().st_size if part.exists() else 0, 0
        with part.open("ab") as fh:
            async for chunk in request.stream():
                got += len(chunk)
                if got > CHUNK_MAX or size + got > UPLOAD_MAX[kind]:
                    fh.close()
                    part.unlink(missing_ok=True)
                    raise EngineError("too_large", "the file is too large", 413)
                fh.write(chunk)
        if index < total - 1:
            return {"ok": True, "received": index + 1}
        if kind == "video":
            d = wbs().dir(wid) / "uploads"
            d.mkdir(exist_ok=True)
            stem = re.sub(r"[^\w\-一-鿿]+", "_", Path(name).stem)[:40] or "video"
            dst = d / f"{stem}{ext}"
            k = 1
            while dst.exists():
                k += 1
                dst = d / f"{stem}_{k}{ext}"
            part.rename(dst)
            return {"ok": True, "src": f"upload:{dst.name}", "title": dst.stem}
        src = folder / f"{upload}{ext}"
        part.rename(src)
        if L.get("scene"):
            async def job(cur: dict) -> None:
                await wbs().take_recording(cur, src)
                cur["mp4"], cur["voice_stale"] = None, False
            wbs().run(L, "正在识别新录音", job)
        else:
            L["state"] = "making"
            wbs().save(L)
            wbs().run(L, "正在识别录音", lambda cur: wbs().make_from_recording(cur, src))
        return detail(wbs().load(wid))

    @app.post("/api/v1/whiteboards/{wid}/mp4")
    async def mp4(wid: str, sess: Annotated[Session, Depends(current)]):
        await m.require_creator(sess)
        L = load(wid, sess)
        not_busy(L)
        ready(L)
        if not m._studio().labcheck_url:
            raise EngineError("mp4_unavailable", "the video recorder is not set up", 503)
        wbs().run(L, "排队出视频", wbs().render_mp4)
        return detail(wbs().load(wid))

    # ------------------------------------------------------------------ AI 建课：一讲的白板讲解
    @app.post("/api/v1/studio/projects/{pid}/lessons/{lid}/whiteboard")
    async def lesson_whiteboard(pid: str, lid: str, body: LessonWbIn, sess: Annotated[Session, Depends(current)]):
        await m.require_creator(sess)
        from .studio import disp
        proj = studio_project(pid, sess)
        st = m._studio()
        try:
            _, les = st.find_lesson(proj, lid)
        except KeyError:
            raise EngineError("not_found", "no such lesson", 404)
        if les["status"] not in ("awaiting", "published"):
            raise EngineError("wrong_stage", "write the lesson first", 409)
        old = les.get("whiteboard")
        if old:
            try:
                if wbs().busy(old):
                    raise EngineError("busy", "the whiteboard lecture is being made", 409)
            except KeyError:
                pass
        text = " ".join(re.sub(r"<[^>]+>", " ", v) for v in (les.get("content") or {}).values() if isinstance(v, str))
        text = re.sub(r"\s+", " ", text)[:20000]
        voice = body.voice or (st.voices_of(proj).get("zh") if hasattr(st, "voices_of") else "") or "zm_yunjian"
        title = disp(les.get("title"))
        L = wbs().new(sess.user_id, source="lesson", topic=title, note=(body.note + "\n" + text).strip(), minutes=6,
                      voice=voice if VOICE_IDS.match(voice) else "zm_yunjian",
                      course={"pid": pid, "lid": lid, "title": disp((proj.get("outline") or {}).get("title")) or ""})
        les["whiteboard"] = L["id"]
        st.projects.save(proj)
        wbs().run(L, "AI 正在写讲稿", wbs().make_from_topic)
        return detail(wbs().load(L["id"]))

    # ------------------------------------------------------------------ links: the page, its files
    def unsign(signed: str) -> dict:
        try:
            return json.loads(m.state.codec.fernet.decrypt(signed.encode(), ttl=m.FILE_TTL))
        except Exception:
            raise EngineError("link_expired", "link expired", 410)

    @app.get("/api/v1/whiteboards/play/{signed}")
    async def play(signed: str):
        d = unsign(signed)
        try:
            L = wbs().load(d["w"])
        except KeyError:
            raise EngineError("not_found", "no such whiteboard lesson", 404)
        ready(L)
        data = compiled(L)
        html_ = core.page(data, (L.get("title") or {}).get("zh", "白板课"), audio_url=file_link(L["id"], "audio"))
        return HTMLResponse(html_, headers={"Cache-Control": "private, max-age=60", "Content-Security-Policy": SANDBOX,
                                            "X-Content-Type-Options": "nosniff"})

    @app.get("/api/v1/whiteboards/file/{signed}")
    async def file(signed: str):
        import asyncio
        d = unsign(signed)
        try:
            L = wbs().load(d["w"])
        except KeyError:
            raise EngineError("not_found", "no such file", 404)
        what = d.get("f")
        if what == "audio":
            p = await asyncio.to_thread(wbs().web_audio, L)
            if not p:
                raise EngineError("not_found", "no narration yet", 404)
            return FileResponse(p, media_type="audio/mpeg", headers={"Cache-Control": "private, max-age=60"})
        if what == "mp4":
            p = wbs().dir(L["id"]) / "白板课.mp4"
            if not p.exists():
                raise EngineError("not_found", "no video yet", 404)
            t = re.sub(r'[\\/:*?<>|"]', "-", (L.get("title") or {}).get("zh") or "白板课")[:60]
            return FileResponse(p, media_type="video/mp4", filename=f"{t}.mp4")
        if what == "media":
            f = wbs().media_file(L, d.get("m", ""))
            if not f:
                raise EngineError("not_found", "no such media", 404)
            kind, path, _ = f
            if kind == "page":
                return Response(path.read_bytes(), media_type="text/html; charset=utf-8", headers={
                    "Cache-Control": "private, max-age=600", "X-Content-Type-Options": "nosniff",
                    # framed by the lesson page, which is itself sandboxed (no origin), so no frame-ancestors 'self' here
                    "Content-Security-Policy": "sandbox allow-scripts allow-popups allow-forms allow-modals"})
            return FileResponse(path, media_type="video/mp4", headers={"Cache-Control": "private, max-age=3600"})
        raise EngineError("not_found", "no such file", 404)

    @app.get("/api/v1/whiteboards/assets/{name}")
    async def asset(name: str):
        if name == "pen.svg":       # the hand (or the drawn marker) for the editor's preview, as the web page has it
            return Response(core.pen_svg(), media_type="text/plain; charset=utf-8", headers={"Cache-Control": "public, max-age=300"})
        if name not in ("player.js", "rough.js"):
            raise EngineError("not_found", "no such file", 404)
        return FileResponse(Path(core.__file__).parent / name, media_type="text/javascript; charset=utf-8",
                            headers={"Cache-Control": "public, max-age=300"})
