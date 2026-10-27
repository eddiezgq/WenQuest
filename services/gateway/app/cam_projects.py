"""问渠凸轮的云端项目（第 39 轮第 7 步，细则第十二节）：开通企业授权的单位，成员共享项目；每次保存留一版，留最近 20 版；
两人同时改时，后存的人收到“别人已存过新版”，不会悄悄覆盖。

  GET    /api/v1/cam/projects                 本单位的项目列表（不含内容）
  POST   /api/v1/cam/projects                 新建（第 1 版）
  GET    /api/v1/cam/projects/{id}            打开：当前版本的内容和历史版本列表；?version=n 打开某一版（只读）
  PUT    /api/v1/cam/projects/{id}            保存：带上打开时的版本号 base；别人已存过新版 → 409，附对方是谁、几点存的
  POST   /api/v1/cam/projects/{id}/restore    把某一版恢复成新的一版（同样带 base）
  DELETE /api/v1/cam/projects/{id}            删除（标记删除，留记录）

谁能用：与缝纫机设计软件同一份企业授权（sewing.py 的 licenses）；管理员当作“问渠”单位。认人：Bearer 或全站登录 cookie wq_sso
（凸轮服务转来）。每家上限 500 个项目，单个项目内容 2 MB 以内。谁建、谁存、谁恢复、谁删，都记一条（log 表）。
数据：<data_dir>/cam.db（SQLite）。项目内容原样存（凸轮服务的项目 JSON），网关不解读、不改。
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

KEEP = 20                 # 每个项目保留的版本数
PER_ORG = 500
MAX_BYTES = 2_000_000


class NewIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    kind: str = Field(default="cam", pattern="^(cam|system)$")
    body: dict[str, Any]


class SaveIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    body: dict[str, Any]
    base: int = Field(ge=1)


class RestoreIn(BaseModel):
    version: int = Field(ge=1)
    base: int = Field(ge=1)


def register(app, m) -> None:
    state = m.state

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "cam.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists projects(id integer primary key, org text, kind text, name text, version integer,
                     created integer, created_by integer, created_name text, updated integer, updated_by integer, updated_name text,
                     deleted integer default 0)""")
        c.execute("""create table if not exists versions(id integer primary key, project integer, version integer, body text,
                     saved_by integer, saved_name text, ts integer, note text)""")
        c.execute("create index if not exists versions_p on versions(project, version)")
        c.execute("""create table if not exists log(id integer primary key, ts integer, org text, user_id integer, name text,
                     action text, project integer, version integer)""")
        return c

    async def who(req: Request, authorization: Annotated[str | None, Header()] = None) -> Session:
        sess = None
        if authorization and authorization.lower().startswith("bearer "):
            sess = state.codec.read(authorization.split(" ", 1)[1].strip())
        if not sess:
            tok = req.cookies.get("wq_sso", "")
            sess = state.codec.read(tok) if tok else None
        if not sess:
            raise EngineError("not_logged_in", "sign in to use cloud projects", 401)
        return sess

    async def lic_of(sess: Session) -> dict:
        lic = await m.sewing_need_license(sess)          # 没开通 → 403 not_licensed
        return {"org": lic["org"], "name": lic.get("name") or ""}

    def body_text(body: dict) -> str:
        t = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        if len(t.encode("utf-8")) > MAX_BYTES:
            raise EngineError("too_large", "a project can be at most 2 MB", 413)
        return t

    def own(c, pid: int, org: str):
        r = c.execute("select * from projects where id=? and org=? and deleted=0", (pid, org)).fetchone()
        if not r:
            raise EngineError("not_found", "no such project", 404)
        return r

    def note(c, org, sess, name, action, pid, version):
        c.execute("insert into log(ts,org,user_id,name,action,project,version) values(?,?,?,?,?,?,?)",
                  (int(time.time()), org, sess.user_id, name, action, pid, version))

    def history(c, pid: int) -> list[dict]:
        return [dict(r) for r in c.execute("select version, saved_by, saved_name, ts, note from versions where project=? "
                                            "order by version desc", (pid,))]

    def meta(r) -> dict:
        return {k: r[k] for k in ("id", "kind", "name", "version", "created", "created_name", "updated", "updated_name")}

    def add_version(c, pid: int, version: int, text: str, sess: Session, name: str, why: str = "") -> None:
        now = int(time.time())
        c.execute("insert into versions(project,version,body,saved_by,saved_name,ts,note) values(?,?,?,?,?,?,?)",
                  (pid, version, text, sess.user_id, name, now, why))
        c.execute("delete from versions where project=? and version<=?", (pid, version - KEEP))
        c.execute("update projects set version=?, updated=?, updated_by=?, updated_name=? where id=?", (version, now, sess.user_id, name, pid))

    def conflict(r) -> JSONResponse:
        return JSONResponse({"error": "conflict", "detail": "someone saved a newer version", "version": r["version"],
                             "updated": r["updated"], "updated_name": r["updated_name"], "updated_by": r["updated_by"]}, status_code=409)

    @app.get("/api/v1/cam/projects")
    async def list_projects(sess: Annotated[Session, Depends(who)]):
        lic = await lic_of(sess)
        with db() as c:
            rs = c.execute("select * from projects where org=? and deleted=0 order by updated desc", (lic["org"],))
            return {"org": lic["org"], "projects": [meta(r) for r in rs]}

    @app.post("/api/v1/cam/projects")
    async def create(body: NewIn, sess: Annotated[Session, Depends(who)]):
        lic = await lic_of(sess)
        text = body_text(body.body)
        now = int(time.time())
        with db() as c:
            if c.execute("select count(*) from projects where org=? and deleted=0", (lic["org"],)).fetchone()[0] >= PER_ORG:
                raise EngineError("too_many", "at most 500 projects per company", 400)
            pid = c.execute("insert into projects(org,kind,name,version,created,created_by,created_name,updated,updated_by,updated_name) "
                            "values(?,?,?,?,?,?,?,?,?,?)", (lic["org"], body.kind, body.name.strip(), 0, now, sess.user_id, lic["name"],
                                                         now, sess.user_id, lic["name"])).lastrowid
            add_version(c, pid, 1, text, sess, lic["name"])
            note(c, lic["org"], sess, lic["name"], "create", pid, 1)
            return {**meta(own(c, pid, lic["org"])), "history": history(c, pid)}

    @app.get("/api/v1/cam/projects/{pid}")
    async def open_project(pid: int, sess: Annotated[Session, Depends(who)], version: int | None = None):
        lic = await lic_of(sess)
        with db() as c:
            r = own(c, pid, lic["org"])
            v = version or r["version"]
            row = c.execute("select body from versions where project=? and version=?", (pid, v)).fetchone()
            if not row:
                raise EngineError("not_found", "that version is no longer kept", 404)
            return {**meta(r), "opened": v, "body": json.loads(row["body"]), "history": history(c, pid)}

    @app.put("/api/v1/cam/projects/{pid}")
    async def save(pid: int, body: SaveIn, sess: Annotated[Session, Depends(who)]):
        lic = await lic_of(sess)
        text = body_text(body.body)
        with db() as c:
            c.execute("begin immediate")
            try:
                r = own(c, pid, lic["org"])
                if body.base != r["version"]:
                    c.execute("rollback")
                    return conflict(r)
                if body.name:
                    c.execute("update projects set name=? where id=?", (body.name.strip(), pid))
                add_version(c, pid, r["version"] + 1, text, sess, lic["name"])
                note(c, lic["org"], sess, lic["name"], "save", pid, r["version"] + 1)
                c.execute("commit")
            except Exception:
                if c.in_transaction:
                    c.execute("rollback")
                raise
            return {**meta(own(c, pid, lic["org"])), "history": history(c, pid)}

    @app.post("/api/v1/cam/projects/{pid}/restore")
    async def restore(pid: int, body: RestoreIn, sess: Annotated[Session, Depends(who)]):
        lic = await lic_of(sess)
        with db() as c:
            c.execute("begin immediate")
            try:
                r = own(c, pid, lic["org"])
                if body.base != r["version"]:
                    c.execute("rollback")
                    return conflict(r)
                old = c.execute("select body from versions where project=? and version=?", (pid, body.version)).fetchone()
                if not old:
                    raise EngineError("not_found", "that version is no longer kept", 404)
                add_version(c, pid, r["version"] + 1, old["body"], sess, lic["name"], f"restored v{body.version}")
                note(c, lic["org"], sess, lic["name"], f"restore v{body.version}", pid, r["version"] + 1)
                c.execute("commit")
            except Exception:
                if c.in_transaction:
                    c.execute("rollback")
                raise
            r = own(c, pid, lic["org"])
            row = c.execute("select body from versions where project=? and version=?", (pid, r["version"])).fetchone()
            return {**meta(r), "opened": r["version"], "body": json.loads(row["body"]), "history": history(c, pid)}

    @app.delete("/api/v1/cam/projects/{pid}")
    async def remove(pid: int, sess: Annotated[Session, Depends(who)]):
        lic = await lic_of(sess)
        with db() as c:
            r = own(c, pid, lic["org"])
            c.execute("update projects set deleted=1 where id=?", (pid,))
            note(c, lic["org"], sess, lic["name"], "delete", pid, r["version"])
        return {"ok": True}
