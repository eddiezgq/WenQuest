"""三维仿真视频的接口（第 38 轮）。谁能用：能建课的老师、管理员、管理员开通的企业账号；学生不能用。
收费 11 月做，现在只记账（管理员看用机记录）。"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import video3d as v3
from .moodle import EngineError
from .session import Session

log = logging.getLogger("wenquest.video3d")

MEDIA = {".png": "image/png", ".mp4": "video/mp4", ".webm": "video/webm"}


class NewIn(BaseModel):
    prompt: str = Field(default="", max_length=2000)
    sample: str = Field(default="", max_length=80)


class SayIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class SceneIn(BaseModel):
    scene: str = Field(min_length=1, max_length=v3.MAX_SCENE)


class RenderIn(BaseModel):
    quality: str = Field(pattern="^(draft|hd)$")


class GrantIn(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    note: str = Field(default="", max_length=200)


def provider_of(m):
    st = m.state.settings
    over = getattr(m.state, "video3d_provider", None)
    if over is not None:
        return over or None
    mode = (st.video3d_provider or "auto").lower()
    key = st.video3d_lambda_key or st.gpu_lambda_key
    if mode == "mock":
        return v3.Mock()
    if mode in ("auto", "lambda") and key:
        return v3.Lambda(httpx.AsyncClient(timeout=60), key, st.gpu_lambda_url, st.video3d_lambda_types)
    return None


def service(m) -> v3.Service:
    st = m.state.settings
    root = str(Path(st.data_dir) / "video3d")
    s = getattr(m.state, "video3d", None)
    if s is None or str(s.store.root) != root or s.ai is not m.state.ai:
        blender = v3.Blender(st.video3d_blender_url, getattr(m.state, "video3d_transport", None))
        s = m.state.video3d = v3.Service(Path(root), m.state.ai, blender, provider_of(m), max_machines=st.video3d_max_machines,
                                         max_hours=st.video3d_max_hours, wait_minutes=st.video3d_wait_minutes)
    return s


async def loop(m) -> None:
    await asyncio.sleep(20)
    while True:
        try:
            await service(m).tick()
        except Exception:  # noqa: BLE001
            log.exception("video3d tick")
        await asyncio.sleep(15)


def register(app, m) -> None:
    current = m.current

    async def access(sess: Session) -> dict:
        teacher = await m.can_create(sess.moodle_token)
        admin = await m.accounts_is_admin(sess)
        granted = service(m).store.granted(sess.user_id)
        return {"allowed": bool(teacher or admin or granted), "admin": bool(admin), "teacher": bool(teacher),
                "granted": bool(granted)}

    async def need(sess: Session) -> dict:
        a = await access(sess)
        if not a["allowed"]:
            raise EngineError("forbidden", "3D video is for teachers and enabled accounts", 403)
        return a

    async def need_admin(sess: Session) -> None:
        if not await m.accounts_is_admin(sess):
            raise EngineError("forbidden", "administrators only", 403)

    def load(vid: str, sess: Session, a: dict) -> dict:
        try:
            V = service(m).store.load(vid)
        except KeyError:
            raise EngineError("not_found", "no such video", 404)
        if V["owner"] != sess.user_id and not a["admin"]:
            raise EngineError("forbidden", "not your video", 403)
        return V

    def sign(d: dict) -> str:
        return m.state.codec.fernet.encrypt(json.dumps(d).encode()).decode()

    def link(vid: str, f: str) -> str:
        return f"{m.state.settings.public_url.rstrip('/')}/api/v1/video3d/file/{sign({'v': vid, 'f': f})}"

    def summary(V: dict) -> dict:
        R = V.get("renders") or {}
        S = V.get("stills") or {}
        poster = link(V["id"], "stills/0.png") if S.get("state") == "done" and S.get("n") else ""
        return {"id": V["id"], "title": V.get("title"), "updated": V.get("updated"), "busy": V.get("busy"), "poster": poster,
                "renders": {q: {"state": r.get("state"), "done": r.get("done"), "total": r.get("total")} for q, r in R.items()},
                "owner": V.get("owner")}

    def detail(V: dict) -> dict:
        svc = service(m)
        S = dict(V.get("stills") or {})
        if S.get("state") == "done":
            S["urls"] = [link(V["id"], f"stills/{i}.png") for i in range(int(S.get("n") or 0))]
        S["stale"] = bool(S) and S.get("version") != V.get("version")
        R = {}
        for q, r in (V.get("renders") or {}).items():
            r = dict(r)
            r["urls"] = {f.rsplit(".", 1)[1]: link(V["id"], "out/" + f) for f in r.get("files") or []}
            r["stale"] = r.get("version") != V.get("version")
            R[q] = r
        scene = svc.store.scene(V["id"])
        try:
            spec = v3.yaml.safe_load(scene) or {}
            labels = [{"t": lb.get("t"), "zh": lb.get("zh"), "en": lb.get("en"), "bottom": lb.get("where") == "bottom"}
                      for lb in spec.get("labels") or [] if isinstance(lb, dict)]
            timeline = {"duration": spec.get("duration"), "labels": labels[:80], "shots": len(spec.get("camera") or []),
                        "style": spec.get("style") or "engineering"}
        except Exception:  # noqa: BLE001
            timeline = {"duration": None, "labels": [], "shots": 0, "style": ""}
        return {**summary(V), "prompt": V.get("prompt"), "timeline": timeline, "chat": V.get("chat"), "ai_error": V.get("ai_error"),
                "version": V.get("version"), "scene": scene, "stills": S, "renders": R,
                "render_on": svc.render_on, "stills_on": svc.blender.on}

    @app.get("/api/v1/video3d/access")
    async def get_access(sess: Annotated[Session, Depends(current)]):
        return await access(sess)

    @app.get("/api/v1/video3d")
    async def index(sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        svc = service(m)
        samples = [{"id": s["id"], "title": s.get("title"), "duration": s.get("duration")} for s in await svc.blender.samples()]
        return {"samples": samples, "videos": [summary(V) for V in svc.store.list(sess.user_id)],
                "render_on": svc.render_on, "stills_on": svc.blender.on, "admin": a["admin"]}

    @app.post("/api/v1/video3d")
    async def create(body: NewIn, sess: Annotated[Session, Depends(current)]):
        await need(sess)
        if not body.prompt.strip() and not body.sample:
            raise EngineError("bad_request", "write what you want, or start from a sample", 400)
        if body.prompt.strip() and not m.state.ai.available:
            raise EngineError("ai_unavailable", "no AI model is configured", 503)
        try:
            V = await service(m).create(sess.user_id, "", body.prompt.strip(), body.sample)
        except KeyError:
            raise EngineError("not_found", "no such sample", 404)
        return detail(V)

    @app.get("/api/v1/video3d/{vid}")
    async def get(vid: str, sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        return detail(load(vid, sess, a))

    @app.delete("/api/v1/video3d/{vid}")
    async def delete(vid: str, sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        V = load(vid, sess, a)
        svc = service(m)
        for q in list((V.get("renders") or {})):
            svc.cancel(V, q)
        svc.store.delete(vid)
        return {"ok": True}

    def not_busy(V: dict) -> None:
        if V.get("busy") or (V.get("stills") or {}).get("state") == "running":
            raise EngineError("busy", "this video is being worked on; try again when it is done", 409)

    @app.post("/api/v1/video3d/{vid}/say")
    async def say(vid: str, body: SayIn, sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        V = load(vid, sess, a)
        not_busy(V)
        if not m.state.ai.available:
            raise EngineError("ai_unavailable", "no AI model is configured", 503)
        return detail(await service(m).say(V, body.text.strip()))

    @app.put("/api/v1/video3d/{vid}/scene")
    async def put_scene(vid: str, body: SceneIn, sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        V = load(vid, sess, a)
        not_busy(V)
        errs = service(m).set_scene(V, body.scene)
        if errs:
            raise EngineError("bad_scene", "；".join(errs[:6]), 422)
        return detail(service(m).store.load(vid))

    @app.post("/api/v1/video3d/{vid}/stills")
    async def stills(vid: str, sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        V = load(vid, sess, a)
        not_busy(V)
        svc = service(m)
        if not svc.blender.on:
            raise EngineError("unavailable", "the stills renderer is not set up", 503)
        if not svc.store.scene(vid):
            raise EngineError("bad_request", "no scene yet", 400)
        V["stills"] = {"state": "running", "version": V.get("version")}
        svc.store.save(V)
        svc.spawn(svc.stills(vid))
        return detail(svc.store.load(vid))

    @app.post("/api/v1/video3d/{vid}/render")
    async def render(vid: str, body: RenderIn, sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        V = load(vid, sess, a)
        not_busy(V)
        svc = service(m)
        if not svc.render_on:
            raise EngineError("unavailable", "video rendering machines are not set up", 503)
        if not svc.store.scene(vid):
            raise EngineError("bad_request", "no scene yet", 400)
        r = (V.get("renders") or {}).get(body.quality) or {}
        if r.get("state") in v3.LIVE:
            raise EngineError("busy", "already rendering", 409)
        svc.request_render(V, body.quality, sess.user_id)
        return detail(svc.store.load(vid))

    @app.post("/api/v1/video3d/{vid}/render/{quality}/cancel")
    async def cancel(vid: str, quality: str, sess: Annotated[Session, Depends(current)]):
        a = await need(sess)
        V = load(vid, sess, a)
        service(m).cancel(V, quality)
        return detail(service(m).store.load(vid))

    @app.get("/api/v1/video3d/file/{signed}")
    async def file(signed: str):
        try:
            d = json.loads(m.state.codec.fernet.decrypt(signed.encode(), ttl=m.FILE_TTL))
        except Exception:
            raise EngineError("link_expired", "link expired", 410)
        f = str(d.get("f") or "")
        if not (f.startswith("stills/") or f.startswith("out/")) or ".." in f:
            raise EngineError("not_found", "no such file", 404)
        try:
            p = service(m).store.vdir(d.get("v", "")) / f
        except KeyError:
            raise EngineError("not_found", "no such file", 404)
        if not p.is_file():
            raise EngineError("not_found", "no such file", 404)
        return FileResponse(p, media_type=MEDIA.get(p.suffix, "application/octet-stream"),
                            headers={"Cache-Control": "private, max-age=3600"})

    # ---- 管理：开通企业账号、看用机记录
    @app.get("/api/v1/video3d/admin/overview")
    async def admin_overview(sess: Annotated[Session, Depends(current)]):
        await need_admin(sess)
        svc = service(m)
        runs = svc.store.runs()
        return {"grants": svc.store.grants(), "runs": runs, "render_on": svc.render_on, "stills_on": svc.blender.on,
                "cost": round(sum(r.get("cost") or 0 for r in runs), 2),
                "hours": round(sum(r.get("seconds") or 0 for r in runs) / 3600, 2)}

    @app.post("/api/v1/video3d/admin/grants")
    async def admin_grant(body: GrantIn, sess: Annotated[Session, Depends(current)]):
        await need_admin(sess)
        name = body.username.strip()
        field = "email" if "@" in name else "username"
        try:
            users = await m.state.moodle.call(sess.moodle_token, "core_user_get_users_by_field", field=field, **{"values[0]": name})
        except EngineError:
            users = []
        if not users:
            raise EngineError("not_found", "no such account", 404)
        u = users[0]
        service(m).store.grant(int(u["id"]), u.get("username") or name, body.note, sess.user_id)
        return {"ok": True, "user_id": int(u["id"]), "username": u.get("username"), "fullname": u.get("fullname")}

    @app.delete("/api/v1/video3d/admin/grants/{uid}")
    async def admin_revoke(uid: int, sess: Annotated[Session, Depends(current)]):
        await need_admin(sess)
        service(m).store.revoke(uid)
        return {"ok": True}

    # 白板课“插入”里能选自己的三维视频
    def wb_list(owner: int) -> list[dict]:
        out = []
        for V in service(m).store.list(owner):
            for q in ("hd", "draft"):
                r = (V.get("renders") or {}).get(q) or {}
                if r.get("state") == "done" and r.get("files"):
                    out.append({"src": f"video3d:{V['id']}/{q}", "title": (V.get("title") or {}).get("zh") or "三维视频",
                                "kind": "三维视频" + ("" if q == "hd" else "（小样）")})
                    break
        return out

    def wb_file(owner: int, ref: str) -> Path | None:
        vid, _, q = ref.partition("/")
        try:
            V = service(m).store.load(vid)
        except KeyError:
            return None
        if V.get("owner") != owner or q not in ("hd", "draft"):
            return None
        p = service(m).store.vdir(vid) / "out" / ("hd.mp4" if q == "hd" else "draft.mp4")
        return p if p.exists() else None

    m.video3d_wb_list, m.video3d_wb_file = wb_list, wb_file
