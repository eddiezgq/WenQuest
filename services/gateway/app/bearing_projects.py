"""问渠轴承的云端项目（第 64 轮第 7 步，细则第十五节）：做法与问渠凸轮的云端项目（cam_projects.py）相同，
多一个“类型”：设计项目（design，.wqbearing.json）、工艺模板（process，.wqprocess.json）和产品库（catalog，企业自己的
产品目录表，细则第十七节 K3），列表可按类型筛。

  GET    /api/v1/bearing/projects?kind=design|process|catalog   本单位的项目列表（不含内容）
  POST   /api/v1/bearing/projects                       新建（第 1 版）
  GET    /api/v1/bearing/projects/{id}                  打开：当前版本的内容和历史版本列表；?version=n 打开某一版（只读）
  PUT    /api/v1/bearing/projects/{id}                  保存：带上打开时的版本号 base；别人已存过新版 → 409
  POST   /api/v1/bearing/projects/{id}/restore          把某一版恢复成新的一版（同样带 base）
  DELETE /api/v1/bearing/projects/{id}                  删除（标记删除，留记录）

谁能用：与缝纫机、凸轮同一份企业授权（m.sewing_who_web）；管理员当作“问渠”单位。认人：Bearer 或全站登录 cookie wq_sso
（轴承服务转来）。每家上限 500 个，单个 2 MB 以内；留最近 20 版；建、存、恢复、删都记一条。
数据：<data_dir>/bearing.db（SQLite），与凸轮的 cam.db 分开。项目内容原样存，网关不解读、不改。
凸轮的模块不动：两者各管各的库，以后若合并成一份通用代码再统一。
"""

import contextlib
import json
import sqlite3
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .moodle import EngineError

KEEP = 20                 # 每个项目保留的版本数
PER_ORG = 500
MAX_BYTES = 2_000_000


class NewIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    kind: str = Field(default="design", pattern="^(design|process|catalog)$")
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

    @contextlib.contextmanager
    def db() -> Iterator[sqlite3.Connection]:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "bearing.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists projects(id integer primary key, org text, kind text, name text, version integer,
                     created integer, created_by integer, created_name text, updated integer, updated_by integer, updated_name text,
                     deleted integer default 0)""")
        c.execute("""create table if not exists versions(id integer primary key, project integer, version integer, body text,
                     saved_by integer, saved_name text, ts integer, note text)""")
        c.execute("create index if not exists versions_p on versions(project, version)")
        c.execute("""create table if not exists log(id integer primary key, ts integer, org text, user_id integer, name text,
                     action text, project integer, version integer)""")
        try:
            yield c
        finally:
            c.close()

    async def who(req: Request, authorization: Annotated[str | None, Header()] = None) -> dict:
        """开通记录；没登记名字的（如管理员）用本人 Moodle 资料里的姓名，让历史版本、顶栏显示人名而不是编号。"""
        lic = await m.sewing_who_web(req, authorization)
        if (lic.get("name") or "").strip():
            return lic
        tok = authorization.split(" ", 1)[1].strip() if authorization and authorization.lower().startswith("bearer ") \
            else req.cookies.get("wq_sso", "")
        sess = state.codec.read(tok) if tok else None
        try:
            name = (await state.moodle.site_info(sess.moodle_token)).get("fullname") if sess else ""
        except Exception:  # noqa: BLE001  (名字拿不到不影响保存)
            name = ""
        return {**lic, "name": name or ""}

    def me(lic: dict) -> tuple[str, int, str]:
        """(单位, 用户号, 显示的名字)"""
        return lic["org"], int(lic["user_id"]), (lic.get("name") or "").strip() or f"#{lic['user_id']}"

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

    def note(c, org, uid, name, action, pid, version):
        c.execute("insert into log(ts,org,user_id,name,action,project,version) values(?,?,?,?,?,?,?)",
                  (int(time.time()), org, uid, name, action, pid, version))

    def history(c, pid: int) -> list[dict]:
        return [dict(r) for r in c.execute("select version, saved_by, saved_name, ts, note from versions where project=? "
                                            "order by version desc", (pid,))]

    def meta(r) -> dict:
        return {k: r[k] for k in ("id", "kind", "name", "version", "created", "created_name", "updated", "updated_name")}

    def add_version(c, pid: int, version: int, text: str, uid: int, name: str, why: str = "") -> None:
        now = int(time.time())
        c.execute("insert into versions(project,version,body,saved_by,saved_name,ts,note) values(?,?,?,?,?,?,?)",
                  (pid, version, text, uid, name, now, why))
        c.execute("delete from versions where project=? and version<=?", (pid, version - KEEP))
        c.execute("update projects set version=?, updated=?, updated_by=?, updated_name=? where id=?",
                  (version, now, uid, name, pid))

    def conflict(r) -> JSONResponse:
        return JSONResponse({"error": "conflict", "detail": "someone saved a newer version", "version": r["version"],
                             "updated": r["updated"], "updated_name": r["updated_name"], "updated_by": r["updated_by"]}, status_code=409)

    @app.get("/api/v1/bearing/projects")
    async def list_projects(lic: Annotated[dict, Depends(who)], kind: str | None = None):
        org, _uid, name = me(lic)
        if kind not in (None, "", "design", "process", "catalog"):
            raise EngineError("bad_kind", "the kind is design, process or catalog", 400)
        with db() as c:
            if kind:
                rs = c.execute("select * from projects where org=? and kind=? and deleted=0 order by updated desc", (org, kind))
            else:
                rs = c.execute("select * from projects where org=? and deleted=0 order by updated desc", (org,))
            return {"org": org, "me": name, "projects": [meta(r) for r in rs]}

    @app.post("/api/v1/bearing/projects")
    async def create(body: NewIn, lic: Annotated[dict, Depends(who)]):
        org, uid, name = me(lic)
        text = body_text(body.body)
        now = int(time.time())
        with db() as c:
            if c.execute("select count(*) from projects where org=? and deleted=0", (org,)).fetchone()[0] >= PER_ORG:
                raise EngineError("too_many", "at most 500 projects per company", 400)
            pid = c.execute("insert into projects(org,kind,name,version,created,created_by,created_name,updated,updated_by,"
                            "updated_name) values(?,?,?,?,?,?,?,?,?,?)",
                            (org, body.kind, body.name.strip(), 0, now, uid, name, now, uid, name)).lastrowid
            add_version(c, pid, 1, text, uid, name)
            note(c, org, uid, name, "create", pid, 1)
            return {**meta(own(c, pid, org)), "opened": 1, "history": history(c, pid)}

    @app.get("/api/v1/bearing/projects/{pid}")
    async def open_project(pid: int, lic: Annotated[dict, Depends(who)], version: int | None = None):
        org, _uid, _name = me(lic)
        with db() as c:
            r = own(c, pid, org)
            v = version or r["version"]
            row = c.execute("select body from versions where project=? and version=?", (pid, v)).fetchone()
            if not row:
                raise EngineError("not_found", "that version is no longer kept", 404)
            return {**meta(r), "opened": v, "body": json.loads(row["body"]), "history": history(c, pid)}

    @app.put("/api/v1/bearing/projects/{pid}")
    async def save(pid: int, body: SaveIn, lic: Annotated[dict, Depends(who)]):
        org, uid, name = me(lic)
        text = body_text(body.body)
        with db() as c:
            c.execute("begin immediate")
            try:
                r = own(c, pid, org)
                if body.base != r["version"]:
                    c.execute("rollback")
                    return conflict(r)
                if body.name:
                    c.execute("update projects set name=? where id=?", (body.name.strip(), pid))
                add_version(c, pid, r["version"] + 1, text, uid, name)
                note(c, org, uid, name, "save", pid, r["version"] + 1)
                c.execute("commit")
            except Exception:
                if c.in_transaction:
                    c.execute("rollback")
                raise
            r = own(c, pid, org)
            return {**meta(r), "opened": r["version"], "history": history(c, pid)}

    @app.post("/api/v1/bearing/projects/{pid}/restore")
    async def restore(pid: int, body: RestoreIn, lic: Annotated[dict, Depends(who)]):
        org, uid, name = me(lic)
        with db() as c:
            c.execute("begin immediate")
            try:
                r = own(c, pid, org)
                if body.base != r["version"]:
                    c.execute("rollback")
                    return conflict(r)
                old = c.execute("select body from versions where project=? and version=?", (pid, body.version)).fetchone()
                if not old:
                    raise EngineError("not_found", "that version is no longer kept", 404)
                add_version(c, pid, r["version"] + 1, old["body"], uid, name, f"restored v{body.version}")
                note(c, org, uid, name, f"restore v{body.version}", pid, r["version"] + 1)
                c.execute("commit")
            except Exception:
                if c.in_transaction:
                    c.execute("rollback")
                raise
            r = own(c, pid, org)
            row = c.execute("select body from versions where project=? and version=?", (pid, r["version"])).fetchone()
            return {**meta(r), "opened": r["version"], "body": json.loads(row["body"]), "history": history(c, pid)}

    @app.delete("/api/v1/bearing/projects/{pid}")
    async def remove(pid: int, lic: Annotated[dict, Depends(who)]):
        org, uid, name = me(lic)
        with db() as c:
            r = own(c, pid, org)
            c.execute("update projects set deleted=1 where id=?", (pid,))
            note(c, org, uid, name, "delete", pid, r["version"])
        return {"ok": True}
