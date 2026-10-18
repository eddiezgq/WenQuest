"""缝纫机设计软件接入问渠 CAE（第 41 轮）。

网关把任务交给数字工厂枢纽的“设计软件接口”（/api/design-sw/*，服务钥匙 WQ_FACTORY_CAE_KEY），枢纽再交给 cae 计算服务排队。

  GET  /api/v1/sewing/cae/options                 这个机型能做哪些分析、零件、优化目标，数字工厂连没连上，本单位今天用了几次
  POST /api/v1/sewing/cae/fea                     关键零件强度 + 疲劳（零件、约束、载荷、载荷谱全自动）
  POST /api/v1/sewing/cae/frame                   上传机壳 STEP → 固有频率（模态）
  POST /api/v1/sewing/cae/mbd                     刺布 / 引针机构动力学（数字工厂 MuJoCo），与本软件公式对照
  POST /api/v1/sewing/cae/motor                   主轴伺服选型（本软件算转矩曲线 + 数字工厂电机表）
  GET  /api/v1/sewing/cae/jobs[/{jid}]            任务列表、结果（算完后自动补疲劳寿命 / 固有频率，并给出判定）
  GET  /api/v1/sewing/cae/jobs/{jid}/image.png    应力云图（服务器画）
  GET  /api/v1/sewing/cae/jobs/{jid}/report.docx  数字工厂的分析报告（附云图）
  POST /api/v1/sewing/optimize                    设计优化（本软件公式，网关里直接算）

来宾不能用；企业开通后才能用（第 41 轮 Q4）。任务记在 <data_dir>/sewing.db 的 cae_jobs 表里，结果算完后缓存。
"""

import asyncio
import base64
import hashlib
import io
import json
import math
import struct
import time
from typing import Annotated, Any

from fastapi import Depends, File, Form, Response, UploadFile
from pydantic import BaseModel, Field

from . import sewcore
from .moodle import EngineError
from .session import Session
from .sewcore import cae_setup as CS
from .sewcore import optimize as OPT

MACHINE_RE = "^(lockstitch|overlock|cover)$"
SF_MIN = 2.0
LIFE_MIN_Y = 5.0


class DesignIn(BaseModel):
    machine: str = Field(default="lockstitch", pattern=MACHINE_RE)
    params: dict[str, Any] = Field(default_factory=dict)
    part: str = Field(default="", max_length=40)
    goal: str = Field(default="", max_length=20)
    project: str = Field(default="", max_length=80)
    volfrac: float = Field(default=0.5, ge=0.3, le=0.8)
    topo: str = Field(default="", max_length=40)        # 数控编程：用这个拓扑优化任务减重后的零件


def phash(machine: str, p: dict) -> str:
    """同一组参数的指纹；数字统一成小数（整理参数时 3 和 3.0 可能互换）"""
    q = {k: (round(float(v), 6) if isinstance(v, (int, float)) and not isinstance(v, bool) else v) for k, v in p.items()}
    return hashlib.sha1((machine + json.dumps(q, sort_keys=True)).encode()).hexdigest()[:12]


def read_surface(raw: bytes) -> dict:
    import numpy as np
    _, nv, nt = struct.unpack_from("<4sII", raw)
    o, out = 12, {}
    for name, n, dt in (("positions", nv * 3, "<f4"), ("vm", nv, "<f4"), ("u", nv * 3, "<f4"), ("triangles", nt * 3, "<u4")):
        out[name] = np.frombuffer(raw, dt, n, o)
        o += 4 * n
    out["positions"] = out["positions"].reshape(-1, 3)
    out["triangles"] = out["triangles"].reshape(-1, 3)
    return out


def read_series(raw: bytes) -> dict:
    import numpy as np
    _, hl = struct.unpack_from("<4sI", raw)
    head = json.loads(raw[8:8 + hl])
    arr = np.frombuffer(raw, "<f4", offset=8 + hl).reshape(head["n"], len(head["names"]))
    return {n: arr[:, i] for i, n in enumerate(head["names"])}


def contour_png(raw: bytes, title: str) -> bytes:
    """表面应力云图（等轴测视角），服务器端用 matplotlib 画"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from .sewcore.report import _mpl_cjk
    plt.rcParams["font.family"] = [_mpl_cjk(), "DejaVu Sans"]
    s = read_surface(raw)
    P, T, V = s["positions"], s["triangles"], s["vm"]
    fv = V[T].mean(axis=1)
    vmax = float(np.percentile(V, 99.5)) or 1.0
    cmap = plt.get_cmap("jet")
    fig = plt.figure(figsize=(7, 5.2))
    ax = fig.add_subplot(111, projection="3d")
    pc = Poly3DCollection(P[T], facecolors=cmap(np.clip(fv / vmax, 0, 1)), edgecolor="none")
    ax.add_collection3d(pc)
    c = (P.max(0) + P.min(0)) / 2
    r = float((P.max(0) - P.min(0)).max()) / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.view_init(25, -55)
    ax.set_axis_off()
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, vmax))
    fig.colorbar(sm, ax=ax, shrink=0.7, label="von Mises MPa")
    ax.set_title(title, fontsize=11)
    b = io.BytesIO()
    fig.savefig(b, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return b.getvalue()


def topo_png(res: dict, ctx: dict, title: str) -> bytes:
    """减重结果：原外形（虚线）、减重后的零件（实心）、孔、受力方向"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon
    from .sewcore.report import _mpl_cjk
    plt.rcParams["font.family"] = [_mpl_cjk(), "DejaVu Sans"]
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    dom = ctx["domain"]
    ax.add_patch(Polygon(dom, closed=True, fill=False, ls="--", lw=1.0, ec="#8a9aa8"))
    ax.add_patch(Polygon(res["outline"], closed=True, fc="#2d6fb3", ec="#1d4e75", lw=1.0))
    for ring in res["inner"]:
        ax.add_patch(Polygon(ring, closed=True, fc="white", ec="#1d4e75", lw=0.8))
    for x, y, r in ctx["holes"]:
        ax.add_patch(Circle((x, y), r, fc="white", ec="#1d4e75", lw=0.8))
    sx, sy = ctx["support"]["center"][:2]
    lx, ly = ctx["load"]["center"][:2]
    fx, fy = ctx["vector_n"][:2]
    L = max(abs(fx), abs(fy)) or 1
    xs = [p[0] for p in dom]
    ys = [p[1] for p in dom]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    ax.annotate("", xy=(lx + fx / L * span * 0.25, ly + fy / L * span * 0.25), xytext=(lx, ly),
                arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2))
    ax.plot([sx], [sy], marker="^", ms=12, color="#2e9e6a")
    ratio = res.get("mass_ratio")
    ax.set_title(f"{title}\n质量 {ratio:.0%}（虚线为原外形；绿 = 支承孔，红箭头 = 受力）" if ratio else title, fontsize=10)
    m = span * 0.32
    ax.set_xlim(min(xs) - m, max(xs) + m)
    ax.set_ylim(min(ys) - m, max(ys) + m)
    ax.set_aspect("equal")
    ax.set_xlabel("mm")
    b = io.BytesIO()
    fig.savefig(b, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return b.getvalue()


def register(app, m) -> None:
    state = m.state

    def db():
        c = m.sewing_db()
        c.execute("""create table if not exists cae_jobs(jid text primary key, org text, user_id integer, machine text, kind text, part text,
                     title text, phash text, params text, ctx text, result text, created integer)""")
        return c

    def connected() -> bool:
        return bool(state.settings.factory_url and state.settings.factory_cae_key)

    async def factory(method: str, path: str, *, raw: bool = False, **kw: Any) -> Any:
        if not connected():
            raise EngineError("factory_unavailable", "the digital factory CAE is not connected", 503)
        url = state.settings.factory_url.rstrip("/") + "/api/design-sw" + path
        try:
            r = await state.http.request(method, url, headers={"Authorization": f"Bearer {state.settings.factory_cae_key}"}, timeout=120, **kw)
        except Exception as e:  # noqa: BLE001
            raise EngineError("factory_unavailable", f"digital factory unreachable: {type(e).__name__}", 503) from e
        if r.status_code >= 400:
            try:
                detail = r.json().get("detail")
            except ValueError:
                detail = r.text[:200]
            if r.status_code == 429:
                raise EngineError("rate_limited", str(detail), 429)
            raise EngineError("factory_error", str(detail), 502 if r.status_code >= 500 else 400)
        return r if raw else r.json()

    def save(jid: str, lic: dict, sess: Session, machine: str, kind: str, part: str, title: str, p: dict, ctx: dict) -> None:
        with db() as c:
            c.execute("insert or replace into cae_jobs(jid,org,user_id,machine,kind,part,title,phash,params,ctx,result,created) values(?,?,?,?,?,?,?,?,?,?,?,?)",
                      (jid, lic["org"], sess.user_id, machine, kind, part, title, phash(machine, p), json.dumps(p), json.dumps(ctx), None, int(time.time())))

    def row(jid: str, org: str) -> dict:
        with db() as c:
            r = c.execute("select * from cae_jobs where jid=? and org=?", (jid, org)).fetchone()
        if not r:
            raise EngineError("not_found", "no such analysis", 404)
        d = dict(r)
        d["params"] = json.loads(d["params"])
        d["ctx"] = json.loads(d["ctx"] or "{}")
        d["result"] = json.loads(d["result"]) if d["result"] else None
        return d

    def submit_body(lic: dict, sess: Session, kind: str, title: str, item: str, **kw: Any) -> dict:
        return dict(org=lic["org"], user=str(sess.user_id), user_name=lic.get("name") or "", kind=kind, title=title[:80], item=item[:40], **kw)

    # ---------- 选项 ----------
    @app.get("/api/v1/sewing/cae/options")
    async def options(sess: Annotated[Session, Depends(m.current)], machine: str = "lockstitch"):
        lic = await m.sewing_need_license(sess)
        q = None
        if connected():
            try:
                j = await factory("GET", "/jobs", params={"org": lic["org"]})
                q = {"used": j["used_today"], "limit": j["daily_limit"]}
            except EngineError:
                q = None
        return {"connected": connected(), "parts": CS.parts(machine), "cam_parts": CS.cam_parts(machine), "goals": OPT.goals(machine), "quota": q,
                "kinds": {"fea": bool(CS.parts(machine)), "frame": True, "mbd": machine in ("lockstitch", "overlock"),
                          "motor": machine in ("lockstitch", "overlock"), "topo": bool(CS.parts(machine)), "cam": bool(CS.cam_parts(machine))}}

    # ---------- 强度 + 疲劳 ----------
    @app.post("/api/v1/sewing/cae/fea")
    async def fea(body: DesignIn, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        M = sewcore.get(body.machine)
        p = M.clean(body.params)
        case = CS.fea_case(body.machine, p, body.part)
        if not case:
            raise EngineError("not_found", "this part cannot be analysed for this machine", 404)
        step = await asyncio.to_thread(CS.part_step, case["descriptor"])
        if not step:
            raise EngineError("unavailable", "3D part generation is not installed on this server", 503)
        g = await factory("POST", "/geometry", content=step)
        try:
            setup = CS.fea_setup(case, g["faces"], p.get("mat", "45-QT"))
        except ValueError as e:
            raise EngineError("factory_error", str(e), 400) from e
        name = next((x["zh"] for x in CS.parts(body.machine) if x["key"] == body.part), body.part)
        j = await factory("POST", "/jobs", json=submit_body(lic, sess, "fea", f"{M.NAME[0]} · {name}", body.part,
                                                             step_sha=g["sha"], setup=setup))
        ctx = {k: case[k] for k in ("phi", "vector_n", "ref_load", "series", "block_seconds", "n", "analytic")}
        ctx["material"] = setup["material_id"]
        save(j["id"], lic, sess, body.machine, "fea", body.part, f"{M.NAME[0]} · {name}", p, ctx)
        return {"id": j["id"], "status": j["status"]}

    # ---------- 机壳模态 ----------
    @app.post("/api/v1/sewing/cae/frame")
    async def frame(sess: Annotated[Session, Depends(m.current)], file: UploadFile = File(...), machine: str = Form("lockstitch"),
                    params: str = Form("{}"), material: str = Form("HT200")):
        lic = await m.sewing_need_license(sess)
        M = sewcore.get(machine)
        try:
            p = M.clean(json.loads(params or "{}"))
        except ValueError:
            p = M.clean({})
        data = await file.read()
        if not data or len(data) > 30 * 1024 * 1024:
            raise EngineError("bad_file", "the STEP file is empty or larger than 30 MB", 400)
        g = await factory("POST", "/geometry", content=data)
        try:
            fs = CS.frame_setup(g["faces"])
        except ValueError as e:
            raise EngineError("factory_error", str(e), 400) from e
        mat = material if material in ("HT200", "QT500-7", "Q235", "6061-T6", "45-QT") else "HT200"
        setup = dict(fs, material_id=mat)
        j = await factory("POST", "/jobs", json=submit_body(lic, sess, "fea", f"{M.NAME[0]} · 机壳固有频率", "frame",
                                                             step_sha=g["sha"], setup=setup))
        save(j["id"], lic, sess, machine, "frame", "frame", f"{M.NAME[0]} · 机壳固有频率", p,
             {"file": (file.filename or "")[:80], "material": mat, "n": p["n"]})
        return {"id": j["id"], "status": j["status"]}

    # ---------- 动力学 ----------
    @app.post("/api/v1/sewing/cae/mbd")
    async def mbd(body: DesignIn, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        M = sewcore.get(body.machine)
        p = M.clean(body.params)
        spec = CS.mbd_spec(body.machine, p)
        if not spec:
            raise EngineError("not_found", "no dynamics model for this machine yet", 404)
        title = f"{M.NAME[0]} · {'刺布机构' if body.machine == 'lockstitch' else '引针机构'}动力学"
        j = await factory("POST", "/jobs", json=submit_body(lic, sess, "mbd", title, "needle", model=spec["model"], setup=spec["setup"]))
        save(j["id"], lic, sess, body.machine, "mbd", "needle", title, p, {"analytic_torque_peak": spec["analytic_torque_peak"], "n": p["n"],
                                                                          "scale": spec["scale"], "n_sim": spec["n_sim"]})
        return {"id": j["id"], "status": j["status"]}

    # ---------- 主轴电机 ----------
    @app.post("/api/v1/sewing/cae/motor")
    async def motor(body: DesignIn, sess: Annotated[Session, Depends(m.current)]):
        await m.sewing_need_license(sess)
        M = sewcore.get(body.machine)
        p = M.clean(body.params)
        T = CS.spindle_torque(body.machine, p)
        if T is None:
            raise EngineError("not_found", "no spindle model for this machine yet", 404)
        tab = await factory("GET", "/motors")
        sel = CS.select_motor(T, p["n"], tab["motors"])
        sel["torque"] = [round(x, 4) for x in T[::2]]
        sel["source"] = "通用典型值 / typical catalogue values"      # 工厂表里的来源写了品牌名，平台内容不点名
        return sel

    # ---------- 拓扑优化（两孔平板减重，第 41 轮第二批） ----------
    @app.post("/api/v1/sewing/cae/topo")
    async def topo(body: DesignIn, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        M = sewcore.get(body.machine)
        p = M.clean(body.params)
        tc = CS.topo_case(body.machine, p, body.part, body.volfrac)
        if not tc:
            raise EngineError("not_found", "this part cannot be optimised for this machine", 404)
        name = next((x["zh"] for x in CS.parts(body.machine) if x["key"] == body.part), body.part)
        title = f"{M.NAME[0]} · {name} · 减重（留 {body.volfrac:.0%}）"
        spec = dict(tc["spec"], material_id=p.get("mat", "45-QT"))
        j = await factory("POST", "/topo", json=dict(org=lic["org"], user=str(sess.user_id), user_name=lic.get("name") or "", title=title, spec=spec))
        c = tc["case"]
        ctx = {k: c[k] for k in ("phi", "vector_n", "ref_load", "series", "block_seconds", "n", "analytic", "support", "load")}
        ctx.update(material=p.get("mat", "45-QT"), area0=tc["area0"], t=float(c["descriptor"]["t"]), holes=tc["spec"]["plate"]["holes"],
                   domain=tc["spec"]["plate"]["domain"], part_zh=name, volfrac=body.volfrac)
        save(j["id"], lic, sess, body.machine, "topo", body.part, title, p, ctx)
        return {"id": j["id"], "status": j["status"]}

    @app.post("/api/v1/sewing/cae/topo/{jid}/verify")
    async def topo_verify(jid: str, sess: Annotated[Session, Depends(m.current)]):
        """减重后的零件送有限元复核（同一组受力、同一材料，强度与疲劳判据不变）"""
        lic = await m.sewing_need_license(sess)
        d = row(jid, lic["org"])
        if d["kind"] != "topo" or not d["result"]:
            raise EngineError("not_found", "the optimisation has not finished", 404)
        ctx = d["ctx"]
        geo = d["result"]["geometry"]
        try:
            setup = CS.fea_setup(dict(support=ctx["support"], load=ctx["load"], vector_n=ctx["vector_n"], descriptor={"t": ctx["t"]}),
                                 geo["faces"], ctx["material"])
        except ValueError as e:
            raise EngineError("factory_error", str(e), 400) from e
        title = d["title"].replace("减重", "减重后复核")
        j = await factory("POST", "/jobs", json=submit_body(lic, sess, "fea", title, d["part"], step_sha=geo["sha"], setup=setup))
        fctx = {k: ctx[k] for k in ("phi", "vector_n", "ref_load", "series", "block_seconds", "n", "analytic")}
        fctx.update(material=ctx["material"], from_topo=jid)
        save(j["id"], lic, sess, d["machine"], "fea", d["part"], title, d["params"], fctx)
        return {"id": j["id"], "status": j["status"]}

    # ---------- 数控编程（平板零件铣削，第 41 轮第二批） ----------
    @app.post("/api/v1/sewing/cae/cam")
    async def cam(body: DesignIn, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        M = sewcore.get(body.machine)
        p = M.clean(body.params)
        if body.topo:
            t = row(body.topo, lic["org"])
            if t["kind"] != "topo" or not t["result"]:
                raise EngineError("not_found", "the optimisation has not finished", 404)
            sha, part, name = t["result"]["geometry"]["sha"], t["part"], t["ctx"].get("part_zh", t["part"]) + "（减重后）"
            p = t["params"]
        else:
            dsc = CS.cam_desc(body.machine, p, body.part)
            if not dsc:
                raise EngineError("not_found", "no flat part with this name", 404)
            step = await asyncio.to_thread(CS.part_step, dsc)
            if not step:
                raise EngineError("unavailable", "3D part generation is not installed on this server", 503)
            sha = (await factory("POST", "/geometry", content=step))["sha"]
            part, name = body.part, dsc["zh"]
        mat = str(p.get("mat", "45-QT"))
        title = f"{M.NAME[0]} · {name} · 铣削程序"
        j = await factory("POST", "/cam", json=dict(org=lic["org"], user=str(sess.user_id), user_name=lic.get("name") or "", title=title,
                                                    sha=sha, name=name[:40], material=("7075" if mat.startswith("7075") else "6061" if mat.startswith("6061") else "45")))
        res = cam_result(j)
        save(j["id"], lic, sess, body.machine, "cam", part, title, p, {"sha": sha, "topo": body.topo or None})
        with db() as c:
            c.execute("update cae_jobs set result=? where jid=?", (json.dumps(res), j["id"]))
        return {"id": j["id"], "status": "done" if j.get("status") == "done" else j.get("status")}

    def cam_result(j: dict) -> dict:
        progs = j.get("programs") or []
        bad = [c for pg in progs for c in pg.get("checks") or [] if c.get("level") in ("error", "bad")]
        warn = [c for pg in progs for c in pg.get("checks") or [] if c.get("level") in ("warn", "warning")]
        total = sum((pg.get("time") or {}).get("total_s", 0) for pg in progs)
        path = []
        for pg in progs[:1]:
            rows = pg.get("path") or []
            step = max(1, len(rows) // 1500)
            path = [[r[0], round(r[1], 2), round(r[2], 2), round(r[3], 2)] for r in rows[::step]]
        txt = lambda c: str(c.get("text") or c.get("msg") or c.get("message") or c.get("kind") or "")  # noqa: E731
        res = {"status": j.get("status"), "error": j.get("error"), "programs": len(progs), "time_s": round(total, 1),
               "tools": [dict(n=k, **v) for pg in progs for k, v in (pg.get("tools") or {}).items()],
               "features": j.get("features"), "path": path, "issues": [txt(c) for c in bad + warn][:10]}
        res["checks"] = [dict(key="cam_sim", zh="试切检查（撞刀、过切、超程、转速、功率）", en="Trial-cut checks (collision, gouge, overtravel, speed, power)",
                              value=f"{len(bad)} / {len(warn)}", limit="0 错误 / errors", state="bad" if bad or j.get("status") != "done" else ("warn" if warn else "ok"))]
        return res

    @app.get("/api/v1/sewing/cae/jobs/{jid}/program.nc")
    async def program(jid: str, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        d = row(jid, lic["org"])
        if d["kind"] != "cam":
            raise EngineError("not_found", "no program for this analysis", 404)
        r = await factory("GET", f"/cam/{jid}/0.nc", params={"org": lic["org"]}, raw=True)
        from urllib.parse import quote
        return Response(r.content, media_type="text/plain; charset=utf-8",
                        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(d['title'] + '.nc')}"})

    @app.get("/api/v1/sewing/cae/jobs/{jid}/part.{ext}")
    async def topo_part(jid: str, ext: str, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        d = row(jid, lic["org"])
        if d["kind"] != "topo" or not d["result"] or ext not in ("dxf", "step"):
            raise EngineError("not_found", "no optimised part", 404)
        from urllib.parse import quote
        name = quote(d["title"] + "." + ext)
        if ext == "dxf":
            data = CS.outline_dxf(d["result"]["outline"], d["result"]["inner"], d["ctx"]["holes"], d["part"], d["ctx"]["t"])
            return Response(data, media_type="application/dxf", headers={"Content-Disposition": f"attachment; filename*=UTF-8''{name}"})
        r = await factory("GET", f"/geometry/{d['result']['geometry']['sha']}/step", raw=True)
        return Response(r.content, media_type="application/step", headers={"Content-Disposition": f"attachment; filename*=UTF-8''{name}"})

    # ---------- 结果 ----------
    async def finish(d: dict, j: dict) -> dict | None:
        """任务算完后补算（疲劳、模态、对照）并给出判定；结果缓存"""
        if d["result"] is not None:
            return d["result"]
        if j.get("status") != "done":
            return None
        ctx, res = d["ctx"], {}
        st = j.get("stats") or {}
        if d["kind"] == "fea":
            sf = st.get("safety_factor")
            fat = await factory("POST", f"/jobs/{d['jid']}/fatigue", params={"org": d["org"]},
                                json={"ref_load": ctx["ref_load"], "series": ctx["series"], "block_seconds": ctx["block_seconds"],
                                      "surface": "fine_turned", "label": "一转（每针）", "ref_unit": "N"})
            summ = fat.get("summary") or {}
            life = CS.life_years(summ)
            res = {"vm_max_mpa": st.get("vm_max_mpa"), "safety_factor": sf, "u_max_mm": st.get("u_max_mm"),
                   "elements": st.get("elements"), "life_years": None if life is None else (None if math.isinf(life) else round(life, 2)),
                   "infinite": bool(summ.get("infinite")), "fatigue": summ, "analytic": ctx.get("analytic"),
                   "applied_force_n": st.get("applied_force_n"), "phi": ctx.get("phi"), "material": ctx.get("material")}
            res["checks"] = [
                dict(key="sf", zh="强度安全系数（有限元）", en="Strength safety factor (FEA)", value=f"{sf:.2f}" if sf else "—", limit=f"≥ {SF_MIN:g}",
                     state="ok" if sf and sf >= SF_MIN else "bad"),
                dict(key="life", zh="疲劳寿命（每天 16 小时、每年 300 天）", en="Fatigue life (16 h/day, 300 days/yr)",
                     value="∞" if res["infinite"] else ("—" if life is None else ("> 1000 年 / years" if life > 1000 else f"{life:.1f} 年 / years")),
                     limit=f"≥ {LIFE_MIN_Y:g} 年 / years",
                     state="ok" if res["infinite"] or (life is not None and life >= LIFE_MIN_Y) else "bad")]
        elif d["kind"] == "topo":
            r = await factory("GET", f"/topo/{d['jid']}/result", params={"org": d["org"]})
            st2 = await factory("POST", f"/topo/{d['jid']}/to-step", params={"org": d["org"]})
            a0 = ctx.get("area0") or 0
            ratio = st2["area_mm2"] / a0 if a0 else None
            res = {"iterations": r.get("iterations"), "converged": r.get("converged"), "mass_ratio": ratio, "area0": a0, "area": st2["area_mm2"],
                   "outline": st2["outline"], "inner": st2["inner"], "geometry": {"sha": st2["geometry"]["sha"], "faces": st2["geometry"]["faces"]},
                   "density": r.get("density"), "cell_mm": (r.get("plate") or {}).get("cell_mm"), "origin": (r.get("plate") or {}).get("origin")}
            res["checks"] = [dict(key="topo_mass", zh="减重后质量 / 原质量", en="Mass after / before",
                                  value=f"{ratio:.0%}" if ratio else "—", limit="送有限元复核 / verify with FEA", state="ok" if ratio else "warn")]
        elif d["kind"] == "frame":
            mo = await factory("POST", f"/jobs/{d['jid']}/modal", params={"org": d["org"]})
            fr = [x["hz"] for x in mo.get("freqs") or []]
            f1 = fr[0] if fr else None
            n = ctx.get("n") or d["params"].get("n", 5000)
            r2 = (2 * n / 60 / f1) if f1 else None
            res = {"freqs_hz": fr, "f1": f1, "r2": r2,
                   "apply": {"fn": round(f1)} if (f1 and d["machine"] == "lockstitch" and 120 <= f1 <= 320) else None}
            res["checks"] = [dict(key="frame_res", zh="二阶激振频率 / 机壳一阶固有频率（实算）", en="2nd-order excitation / frame 1st mode (computed)",
                                  value=f"{r2:.3f}" if r2 else "—", limit="≤ 0.90", state="ok" if r2 and r2 <= 0.9 else "bad")]
        elif d["kind"] == "mbd":
            raw = await factory("GET", f"/jobs/{d['jid']}/series.bin", params={"org": d["org"]}, raw=True)
            ser = read_series(raw.content)
            k = ctx.get("scale", 1.0)                            # 低速仿真 → 设计转速：乘转速比的平方
            vals = [float(x) * k for x in ser["drive.crank"]]
            n = len(vals)
            tail = vals[n // 3:]                                  # 去掉起步的第一转
            peak = max(abs(x) for x in tail)
            ana = ctx["analytic_torque_peak"]
            diff = abs(peak - ana) / ana if ana else None
            res = {"torque_peak_mbd": round(peak, 4), "torque_peak_formula": round(ana, 4), "diff": diff,
                   "series": [round(x, 4) for x in tail[:: max(1, len(tail) // 180)]]}
            res["checks"] = [dict(key="mbd_vs_formula", zh="刺布机构主轴转矩峰值：动力学与公式对照", en="Needle-drive torque peak: dynamics vs. formula",
                                  value=f"{peak:.3f} / {ana:.3f} N·m", limit="相差 ≤ 5% / within 5%", state="ok" if diff is not None and diff <= 0.05 else "warn")]
        with db() as c:
            c.execute("update cae_jobs set result=? where jid=?", (json.dumps(res), d["jid"]))
        return res

    @app.get("/api/v1/sewing/cae/jobs")
    async def jobs(sess: Annotated[Session, Depends(m.current)], machine: str = ""):
        lic = await m.sewing_need_license(sess)
        with db() as c:
            rs = [dict(r) for r in c.execute("select jid,machine,kind,part,title,phash,created,result from cae_jobs where org=? order by created desc limit 100",
                                             (lic["org"],)) if not machine or r["machine"] == machine]
        remote = {}
        if connected() and rs:
            try:
                remote = {j["id"]: j for j in (await factory("GET", "/jobs", params={"org": lic["org"]}))["jobs"]}
            except EngineError:
                remote = {}
        for r in rs:
            j = remote.get(r["jid"]) or {}
            r["status"] = "done" if r["result"] else j.get("status", "unknown")
            r["position"] = j.get("position")
            r["has_result"] = bool(r.pop("result"))
        return {"jobs": rs}

    @app.get("/api/v1/sewing/cae/jobs/{jid}")
    async def job(jid: str, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        d = row(jid, lic["org"])
        if d["result"] is not None:
            return {"id": jid, "status": "done", "kind": d["kind"], "title": d["title"], "machine": d["machine"], "result": d["result"]}
        j = await factory("GET", f"/jobs/{jid}", params={"org": lic["org"]})
        out = {"id": jid, "status": j.get("status"), "kind": d["kind"], "title": d["title"], "machine": d["machine"],
               "position": j.get("position"), "error": j.get("error")}
        if j.get("status") == "done":
            out["result"] = await finish(d, j)
        return out

    @app.get("/api/v1/sewing/cae/jobs/{jid}/image.png")
    async def image(jid: str, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        d = row(jid, lic["org"])
        if d["kind"] == "topo" and d["result"]:
            png = await asyncio.to_thread(topo_png, d["result"], d["ctx"], d["title"])
            return Response(png, media_type="image/png", headers={"Cache-Control": "private, max-age=3600"})
        if d["kind"] not in ("fea", "frame"):
            raise EngineError("not_found", "no contour for this analysis", 404)
        r = await factory("GET", f"/jobs/{jid}/surface.bin", params={"org": lic["org"]}, raw=True)
        png = await asyncio.to_thread(contour_png, r.content, d["title"])
        return Response(png, media_type="image/png", headers={"Cache-Control": "private, max-age=3600"})

    @app.get("/api/v1/sewing/cae/jobs/{jid}/report.docx")
    async def report(jid: str, sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        d = row(jid, lic["org"])
        if d["kind"] in ("topo", "cam"):
            raise EngineError("not_found", "no report for this analysis", 404)
        imgs = []
        if d["kind"] in ("fea", "frame"):
            r = await factory("GET", f"/jobs/{jid}/surface.bin", params={"org": lic["org"]}, raw=True)
            png = await asyncio.to_thread(contour_png, r.content, d["title"])
            imgs = [{"data": "data:image/png;base64," + base64.b64encode(png).decode(), "caption": "应力云图 / stress contour"}]
        r = await factory("POST", f"/jobs/{jid}/report", params={"org": lic["org"]}, json={"images": imgs}, raw=True)
        from urllib.parse import quote
        return Response(r.content, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(d['title'] + '-CAE报告.docx')}"})

    # ---------- 设计优化（本软件公式） ----------
    @app.post("/api/v1/sewing/optimize")
    async def optimize(body: DesignIn, sess: Annotated[Session, Depends(m.current)]):
        await m.sewing_need_license(sess)
        if body.goal not in [g["key"] for g in OPT.goals(body.machine)]:
            raise EngineError("not_found", "no such goal", 404)
        return await asyncio.to_thread(OPT.run, body.machine, body.params, body.goal)

    # 计算书用：本单位、这个机型、这组参数已经算完的 CAE 结果
    def results_for(org: str, machine: str, params: dict) -> list:
        h = phash(machine, sewcore.get(machine).clean(params))
        with db() as c:
            rs = [dict(r) for r in c.execute("select title,kind,result,created from cae_jobs where org=? and machine=? and phash=? and result is not null "
                                             "order by created", (org, machine, h))]
        return [dict(title=r["title"], kind=r["kind"], result=json.loads(r["result"])) for r in rs]
    m.sewing_cae_results = results_for
