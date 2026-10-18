"""缝纫机设计与制造软件（第 39 轮）：问渠首页“企业解决方案 → 缝纫机设计与制造”的网页版（SaaS）接口。

  GET  /api/v1/sewing/schema                 参数表（分组、单位、范围、选项）——网页表单照它生成
  POST /api/v1/sewing/analyze                 一组参数 → 尺寸、曲线、时序、校核、试缝（来宾也能用；按网络地址限次）
  GET  /api/v1/sewing/proto                   平缝机三维虚拟样机页（教材实验页，同源嵌入，网页调 __api.setCfg 同步参数）
  GET  /api/v1/sewing/me                      当前账号是否已开通（企业授权）、所在单位、是否管理员
  GET/POST/PUT/DELETE /api/v1/sewing/projects…  机型项目（已开通：同一单位的成员共享）
  POST /api/v1/sewing/export/{kind}           出件：report 计算书 / card 调机卡（Word）、params 参数表（Excel）、
                                              step 三维模型、macro FreeCAD 宏、dxf 平板零件轮廓、json 参数文件（已开通才能导出）
  GET  /api/v1/sewing/freecad.zip             FreeCAD 工作台“问渠缝纫机”安装包（已开通）
  GET/POST/DELETE /api/v1/admin/sewing/licenses  管理员手动开通 / 收回（价格未定，先手动授权）

数据：<data_dir>/sewing.db（SQLite）。计算核心 app/sewcore 与 FreeCAD 工作台共用，两边同一组参数结果一致。
"""

import io
import json
import sqlite3
import time
import zipfile
from collections import deque
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import quote

from fastapi import Depends, Header, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from . import sewcore
from .moodle import EngineError
from .session import Session

HERE = Path(__file__).resolve().parent
PER_MIN = 120                        # 每个网络地址每分钟最多算多少次
KINDS = {"report": ("计算书", "docx"), "card": ("调机卡", "docx"), "params": ("参数表", "xlsx"), "step": ("三维模型", "step"),
         "macro": ("FreeCAD宏", "FCMacro"), "dxf": ("零件轮廓", "dxf"), "json": ("参数", "wqsew.json")}
MIME = {"docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "step": "model/step",
        "FCMacro": "text/x-python; charset=utf-8", "dxf": "image/vnd.dxf", "wqsew.json": "application/json"}


MACHINE_RE = "^(lockstitch|overlock|cover)$"
NO_CAD = {"cover"}                   # 绷缝机第一期没有三维零件（第 40 轮 Q2）


class AnalyzeIn(BaseModel):
    machine: str = Field(default="lockstitch", pattern=MACHINE_RE)
    params: dict[str, Any] = Field(default_factory=dict)


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    note: str = Field(default="", max_length=2000)
    machine: str = Field(default="lockstitch", pattern=MACHINE_RE)
    params: dict[str, Any] = Field(default_factory=dict)


class ExportIn(BaseModel):
    machine: str = Field(default="lockstitch", pattern=MACHINE_RE)
    params: dict[str, Any] = Field(default_factory=dict)
    project: str = Field(default="", max_length=80)
    lang: str = "zh"


class LicenseIn(BaseModel):
    username: str = Field(min_length=1, max_length=120)      # 登录名或邮箱
    org: str = Field(min_length=1, max_length=80)
    note: str = Field(default="", max_length=500)


def register(app, m) -> None:
    state = m.state
    hits: dict[str, deque] = {}

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "sewing.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists licenses(user_id integer primary key, org text, name text, note text,
                     granted_by integer, ts integer)""")
        c.execute("""create table if not exists projects(id integer primary key, org text, owner integer, owner_name text, name text,
                     note text, params text, created integer, updated integer)""")
        if "machine" not in [r[1] for r in c.execute("pragma table_info(projects)")]:      # 第 40 轮加机型
            c.execute("alter table projects add column machine text default 'lockstitch'")
        return c

    def ip(req: Request) -> str:
        fwd = req.headers.get("x-forwarded-for", "")
        return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "?"

    def limit(req: Request) -> None:
        now = time.time()
        q = hits.setdefault(ip(req), deque())
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= PER_MIN:
            raise EngineError("rate_limited", "too many calculations; wait a minute", 429)
        q.append(now)
        if len(hits) > 5000:
            hits.clear()

    async def optional(authorization: Annotated[str | None, Header()] = None) -> Session | None:
        if not authorization or not authorization.lower().startswith("bearer "):
            return None
        return state.codec.read(authorization.split(" ", 1)[1].strip())

    def license_of(uid: int) -> dict | None:
        with db() as c:
            r = c.execute("select * from licenses where user_id=?", (uid,)).fetchone()
        return dict(r) if r else None

    async def need_license(sess: Session) -> dict:
        lic = license_of(sess.user_id)
        if lic:
            return lic
        if await m.accounts_is_admin(sess):          # 管理员当作“问渠”单位的已开通用户（演示与验收用）
            return {"user_id": sess.user_id, "org": "问渠", "name": "", "note": "admin"}
        raise EngineError("not_licensed", "this feature is for activated enterprise accounts", 403)

    # 第 41 轮：CAE 接口（sewing_cae.py）共用开通检查和数据库
    m.sewing_need_license = need_license
    m.sewing_db = db

    # ---------- 来宾也能用 ----------
    @app.get("/api/v1/sewing/schema")
    async def schema(machine: str = "lockstitch"):
        M = sewcore.get(machine)
        return {"version": M.VERSION, "machine": M.MACHINE,
                "machines": [{"key": k, "zh": sewcore.MACHINES[k].NAME[0], "en": sewcore.MACHINES[k].NAME[1]} for k in sewcore.ORDER],
                "groups": [{"key": g, "zh": zh, "en": en,
                            "params": [{"key": k, "zh": pzh, "en": pen, "unit": u, "default": d, "min": lo, "max": hi, "step": st,
                                        "choices": [{"key": c[0], "zh": c[1], "en": c[2]} for c in M.CHOICES.get(k, [])]}
                                       for k, pzh, pen, u, d, lo, hi, st in items]}
                           for g, zh, en, items in M.GROUPS],
                "kinds": {k: v[1] for k, v in KINDS.items() if not (M.MACHINE in NO_CAD and k in ("step", "macro", "dxf"))}}

    @app.post("/api/v1/sewing/analyze")
    async def analyze(body: AnalyzeIn, req: Request):
        limit(req)
        r = sewcore.get(body.machine).analyze(body.params)
        r["proto"] = r["view"]["cfg"]                 # 第 39 轮的字段名，网页旧版本还在用
        return r

    PAGES = {"proto-lockstitch", "model-overlock", "looper"}

    @app.get("/api/v1/sewing/proto")
    async def proto(lang: str = "zh", page: str = "proto-lockstitch"):
        if page not in PAGES:
            raise EngineError("not_found", "no such page", 404)
        base = Path(state.settings.textbook_dir) / "sewing" / "webed"
        p = base / ("en/labs" if lang == "en" else "labs") / f"{page}.html"
        if not p.exists():
            raise EngineError("not_found", "the 3D prototype is not installed on this server", 404)
        return HTMLResponse(p.read_text(encoding="utf-8"), headers={"Cache-Control": "public, max-age=600",
                                                                     "Content-Security-Policy": "frame-ancestors 'self'"})

    @app.get("/api/v1/sewing/me")
    async def me(sess: Annotated[Session | None, Depends(optional)]):
        if not sess:
            return {"login": False, "licensed": False, "admin": False}
        admin = await m.accounts_is_admin(sess)
        lic = license_of(sess.user_id)
        return {"login": True, "licensed": bool(lic) or admin, "admin": admin, "org": (lic or {}).get("org") or ("问渠" if admin else "")}

    # ---------- 机型项目（已开通） ----------
    def row(r) -> dict:
        d = dict(r)
        d["params"] = json.loads(d["params"] or "{}")
        return d

    def own(c, pid: int, lic: dict):
        r = c.execute("select * from projects where id=? and org=?", (pid, lic["org"])).fetchone()
        if not r:
            raise EngineError("not_found", "no such project", 404)
        return r

    @app.get("/api/v1/sewing/projects")
    async def projects(sess: Annotated[Session, Depends(m.current)]):
        lic = await need_license(sess)
        with db() as c:
            rs = c.execute("select id,name,note,owner_name,machine,created,updated from projects where org=? order by updated desc", (lic["org"],))
            return {"org": lic["org"], "projects": [dict(r) for r in rs]}

    @app.post("/api/v1/sewing/projects")
    async def create(body: ProjectIn, sess: Annotated[Session, Depends(m.current)]):
        lic = await need_license(sess)
        now = int(time.time())
        p = sewcore.get(body.machine).clean(body.params)
        with db() as c:
            if c.execute("select count(*) from projects where org=?", (lic["org"],)).fetchone()[0] >= 500:
                raise EngineError("too_many", "at most 500 projects per company", 400)
            cur = c.execute("insert into projects(org,owner,owner_name,name,note,params,machine,created,updated) values(?,?,?,?,?,?,?,?,?)",
                            (lic["org"], sess.user_id, lic.get("name") or "", body.name.strip(), body.note, json.dumps(p), body.machine, now, now))
            return row(c.execute("select * from projects where id=?", (cur.lastrowid,)).fetchone())

    @app.get("/api/v1/sewing/projects/{pid}")
    async def get_project(pid: int, sess: Annotated[Session, Depends(m.current)]):
        lic = await need_license(sess)
        with db() as c:
            return row(own(c, pid, lic))

    @app.put("/api/v1/sewing/projects/{pid}")
    async def save(pid: int, body: ProjectIn, sess: Annotated[Session, Depends(m.current)]):
        lic = await need_license(sess)
        with db() as c:
            own(c, pid, lic)
            c.execute("update projects set name=?, note=?, params=?, machine=?, updated=? where id=?",
                      (body.name.strip(), body.note, json.dumps(sewcore.get(body.machine).clean(body.params)), body.machine, int(time.time()), pid))
            return row(c.execute("select * from projects where id=?", (pid,)).fetchone())

    @app.delete("/api/v1/sewing/projects/{pid}")
    async def remove(pid: int, sess: Annotated[Session, Depends(m.current)]):
        lic = await need_license(sess)
        with db() as c:
            own(c, pid, lic)
            c.execute("delete from projects where id=?", (pid,))
        return {"ok": True}

    # ---------- 出件（已开通） ----------
    @app.post("/api/v1/sewing/export/{kind}")
    async def export(kind: str, body: ExportIn, sess: Annotated[Session, Depends(m.current)]):
        if kind not in KINDS:
            raise EngineError("not_found", "no such export", 404)
        lic = await need_license(sess)
        lang = "en" if body.lang.startswith("en") else "zh"
        M = sewcore.get(body.machine)
        p = M.clean(body.params)
        if M.MACHINE in NO_CAD and kind in ("step", "macro", "dxf"):
            raise EngineError("not_found", "no 3D parts for this machine yet", 404)
        from .sewcore import cad, report
        if kind == "report":
            cae = m.sewing_cae_results(lic["org"], M.MACHINE, p) if hasattr(m, "sewing_cae_results") else []
            data = report.calc_report(p, lang, body.project, lic["org"], machine=M.MACHINE, cae=cae)
        elif kind == "card":
            data = report.card_docx(p, lang, body.project, machine=M.MACHINE)
        elif kind == "params":
            data = report.params_xlsx(p, lang, body.project, machine=M.MACHINE)
        elif kind == "step":
            data = cad.to_step(p, machine=M.MACHINE)
            if data is None:
                raise EngineError("unavailable", "STEP export is not installed on this server; use the FreeCAD macro", 503)
        elif kind == "macro":
            data = cad.freecad_macro(p, machine=M.MACHINE).encode("utf-8")
        elif kind == "dxf":
            data = cad.to_dxf(p, machine=M.MACHINE)
        else:
            data = json.dumps({"format": "wenquest-sewing", "machine": M.MACHINE, "version": M.VERSION,
                               "project": body.project, "params": p}, ensure_ascii=False, indent=1).encode("utf-8")
        label, ext = KINDS[kind]
        stem = (body.project.strip() or M.NAME[0]) if lang == "zh" else (body.project.strip() or M.MACHINE)
        name = f"{stem}-{label if lang == 'zh' else kind}.{ext}"
        return Response(data, media_type=MIME[ext], headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}",
                                                              "Cache-Control": "no-store"})

    @app.get("/api/v1/sewing/freecad.zip")
    async def freecad_zip(sess: Annotated[Session, Depends(m.current)]):
        await need_license(sess)
        return Response(workbench_zip(), media_type="application/zip",
                        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote('问渠缝纫机-FreeCAD工作台.zip')}"})

    # ---------- 授权（管理员） ----------
    @app.get("/api/v1/admin/sewing/licenses")
    async def licenses(sess: Annotated[Session, Depends(m.current)]):
        await m.accounts_require_admin(sess)
        with db() as c:
            return {"licenses": [dict(r) for r in c.execute("select * from licenses order by ts desc")]}

    @app.post("/api/v1/admin/sewing/licenses")
    async def grant(body: LicenseIn, sess: Annotated[Session, Depends(m.current)]):
        await m.accounts_require_admin(sess)
        who = body.username.strip()
        try:
            users = await state.moodle.call(sess.moodle_token, "core_user_get_users_by_field", field="email" if "@" in who else "username",
                                            **{"values[0]": who})
        except EngineError:
            users = []
        if not users:
            raise EngineError("not_found", "no such account", 404)
        u = users[0]
        name = u.get("fullname") or u.get("username") or who
        with db() as c:
            c.execute("insert or replace into licenses(user_id,org,name,note,granted_by,ts) values(?,?,?,?,?,?)",
                      (int(u["id"]), body.org.strip(), name, body.note.strip(), sess.user_id, int(time.time())))
        return {"ok": True, "user_id": int(u["id"]), "name": name}

    @app.delete("/api/v1/admin/sewing/licenses/{uid}")
    async def revoke(uid: int, sess: Annotated[Session, Depends(m.current)]):
        await m.accounts_require_admin(sess)
        with db() as c:
            c.execute("delete from licenses where user_id=?", (uid,))
        return {"ok": True}


def workbench_zip() -> bytes:
    """FreeCAD 工作台安装包：Mod/WenQuestSewing/（界面 + 同一份计算核心），加使用说明"""
    core = HERE / "sewcore"
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        root = "Mod/WenQuestSewing/"
        for f in sorted((core / "freecad").glob("*")):
            if f.is_file() and f.suffix in (".py", ".svg", ".txt") and f.name != "使用说明.txt":
                z.write(f, root + f.name)
        for f in ("__init__.py", "common.py", "kit.py", "design.py", "overlock.py", "cover.py", "machines.py", "cad.py"):
            z.write(core / f, root + "sewcore/" + f)
        z.write(core / "freecad" / "使用说明.txt", "使用说明.txt")
    return b.getvalue()
