"""Cam systems in the web service (round 39, step 4): analysis, the globoidal cam's 3D model and 4-axis program, the
tool-changer arm, and the digital factory's CAE (through cae_bridge). Registered on the app by app.py."""

from __future__ import annotations

import base64
import json
import math
import re
from pathlib import Path

import numpy as np
from fastapi import HTTPException, Request

import cae_bridge as B
from camkit import atc_arm as AR
from camkit import cae_setup as CS
from camkit import globoid_mfg as GM
from camkit import globoidal as G
from camkit import system as S
from camkit import system_opt as OPT
from camkit.program import Program

HERE = Path(__file__).parent


def _thin(a, n):
    a = np.asarray(a)
    return a[..., :: max(1, a.shape[-1] // n)]


def system_view(p: dict) -> dict:
    r = S.analyse(p)
    deg = r["deg"]
    idx = np.arange(0, len(deg), max(1, len(deg) // 720))
    cams = []
    for c, src in zip(r["cams"], p.get("cams") or [], strict=True):
        prog = c["program"]
        k = 180 / math.pi if prog.unit == "rad" else 1.0
        d = {"id": c["id"], "name": c["name"], "type": c["type"], "unit": "deg" if prog.unit == "rad" else "mm",
             "s": (c["s"][idx] * k).round(5).tolist(), "v": (c["s1"][idx] * k).round(5).tolist(),
             "acc_out": c["acc"][idx].round(5).tolist(), "moving": S.intervals(c["moving"], deg),
             "checks": c["checks"], "vib": c["vib"], "fn": None if not c["wn"] else c["wn"] / (2 * math.pi),
             "lift": prog.lift() * k, "advance": prog.advance * k}
        sub = c["sub"]
        if c["type"] == "globoidal":
            d["geometry"] = sub.get("geometry")
            d["alpha_deg"] = sub["curves"].get("alpha_deg")
            d["globoidal"] = src.get("globoidal")
        else:
            d["shapes"] = sub.get("shapes")
            d["phi_deg"] = sub["curves"].get("phi_deg")
        cams.append(d)
    return {"status": r["status"], "checks": r["checks"], "cams": cams, "deg": deg[idx].round(3).tolist(),
            "t": r["t"][idx].round(5).tolist(), "speed_rpm": (r["thd"][idx] * 60 / (2 * math.pi)).round(3).tolist(),
            "T_cs": r["T_cs"][idx].round(4).tolist(), "T_motor": r["T_motor"][idx].round(4).tolist(),
            "Je": r["Je"][idx].round(6).tolist(), "cycle": r["cycle"], "ratio": r["ratio"]}


def _cam(p: dict, cid: str) -> dict:
    c = next((c for c in p.get("cams") or [] if c.get("id") == cid), None)
    if c is None:
        raise ValueError("no such cam in the system")
    return c


def globoid_mesh(p: dict, cid: str, fine: bool = False):
    c = _cam(p, cid)
    if c.get("type") != "globoidal":
        raise ValueError("this cam is not a globoidal cam")
    g = G.globoid(c.get("globoidal"))
    prog = Program.from_dict(c.get("program") or {})
    tc, zs, top = GM.height_field(g, prog, d_theta=0.25 if fine else 1.0, dz=0.5 if fine else 1.0,
                                  steps=1440 if fine else 720)
    return g, prog, GM.mesh(tc, zs, top)


def mesh_view(p: dict, cid: str) -> dict:
    g, prog, (V, F) = globoid_mesh(p, cid)
    th = np.radians(np.arange(0, 360, 1.0))
    phi = prog.position(th)
    return {"vertices": base64.b64encode(np.asarray(V, "<f4").tobytes()).decode(),
            "faces": base64.b64encode(np.asarray(F, "<u4").tobytes()).decode(),
            "turret_deg": np.degrees(phi).round(4).tolist(), "globoidal": c_geom(g)}


def c_geom(g: G.Globoid) -> dict:
    return {"C": g.C, "n": g.n, "Rp": g.Rp, "rr": g.rr, "b": g.b, "L": g.L, "rho1": g.rho1, "rho2": g.rho2,
            "phase_deg": math.degrees(g.phase), "hand": g.hand, "clearance": g.clearance}


def system_export(p: dict, kind: str, cid: str = "") -> dict:
    title = (p.get("title") or {}).get("en") or "cam-system"
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", title).strip("_")[:40] or "cam-system"
    if kind == "stl":
        _, _, (V, F) = globoid_mesh(p, cid, fine=True)
        return {"name": f"{base}-{cid}.stl", "mime": "model/stl", "b64": base64.b64encode(GM.stl(V, F, cid)).decode()}
    if kind == "nc4":
        c = _cam(p, cid)
        g = G.globoid(c.get("globoidal"))
        prog = Program.from_dict(c.get("program") or {})
        st = (p.get("mfg") or {}).get(cid) or {}
        text = GM.program(g, prog, st, title)
        sim = GM.simulate(g, prog, text)
        return {"name": f"{base}-{cid}-4axis.nc", "mime": "text/plain", "text": text,
                "sim": {k: sim[k] for k in ("max_over", "max_under", "unreached", "points")}}
    if kind == "arm-step":
        text, rep = AR.step(p.get("arm") or {}, f"{base}-arm")
        return {"name": f"{base}-arm.step", "mime": "application/step", "text": text, "report": rep,
                "mass": AR.mass_properties(p.get("arm") or {})}
    raise HTTPException(404, {"en": "no such export", "zh": "没有这种导出"})


# ------------------------------------------------------------------------------------------------- CAE


def example_cae(eid: str) -> dict:
    if not re.fullmatch(r"[a-z0-9-]{1,60}", eid):
        raise HTTPException(404, {"en": "no such example", "zh": "没有这个示例"})
    f = HERE / "examples" / f"{eid}.cae.json"
    if not f.is_file():
        raise HTTPException(404, {"en": "no CAE results for this example", "zh": "这个示例没有预先算好的 CAE 结果"})
    return json.loads(f.read_text(encoding="utf-8"))


def cae_me(request: Request) -> dict:
    me = B.identity(request) if B.configured() else {"login": False, "licensed": False}
    return {"configured": B.configured(), **{k: me.get(k) for k in ("login", "licensed", "org", "name")}}


def _who(me):
    return {"app": "cam", "org": me["org"], "user": str(me.get("user_id") or ""), "user_name": me.get("name") or ""}


def cae_mbd(request: Request, p: dict) -> dict:
    me = B.need_company(request)
    xml, setup, notes = CS.mbd_model(p)
    model = B.hub("POST", "/mbd/model", params={"app": "cam", "org": me["org"], "name": "cam-system.xml"},
                  content=xml.encode())
    job = B.hub("POST", "/mbd", json=dict(_who(me), model=model["ref"], setup=setup, title=_title(p, "动力学")))
    return {"job": job, "notes": notes}


def cae_arm(request: Request, p: dict) -> dict:
    me = B.need_company(request)
    arm, cae = p.get("arm") or {}, p.get("cae") or {}
    text, _ = AR.step(arm)
    geo = B.hub("POST", "/geometry", params={"app": "cam", "org": me["org"]}, content=text.encode())
    loads = CS.arm_loads(p, cae.get("arm_cam") or "index", float(cae.get("tool_mass") or 0), float(arm["R_tip"]))
    setup = CS.arm_fea_setup(geo["faces"], AR.sizes(arm), loads, float(cae.get("tool_mass") or 0),
                             cae.get("material_id") or "45-QT")
    job = B.hub("POST", "/fea", json=dict(_who(me), sha=geo["sha"], setup=setup, title=_title(p, "换刀臂强度")))
    return {"job": job, "loads": {k: loads[k] for k in ("Ft_max", "Fc_max", "F_max", "deg", "cycle_s")}}


def cae_job(request: Request, jid: str) -> dict:
    me = B.need_company(request)
    return B.hub("GET", f"/jobs/{_jid(jid)}", params={"org": me["org"]})


def cae_followup(request: Request, jid: str, what: str, p: dict) -> dict:
    me = B.need_company(request)
    org = {"org": me["org"]}
    jid = _jid(jid)
    if what == "modal":
        return B.hub("POST", f"/jobs/{jid}/modal", params=org)
    if what == "fatigue":
        arm, cae = p.get("arm") or {}, p.get("cae") or {}
        loads = CS.arm_loads(p, cae.get("arm_cam") or "index", float(cae.get("tool_mass") or 0), float(arm["R_tip"]))
        return B.hub("POST", f"/jobs/{jid}/fatigue", params=org,
                     json=CS.fatigue_body(loads, float(cae.get("changes_per_day") or 0)))
    if what == "compare":
        ser = B.hub("GET", f"/jobs/{jid}/joint-series", params=dict(org, joint="camshaft"))
        cmp = CS.compare_torque(p, ser["values"], ser["duration_s"])
        try:
            motors = B.hub("GET", f"/jobs/{jid}/motors", params=org)
        except HTTPException:
            motors = None
        return {"compare": _thin_cmp(cmp), "motors": motors}
    raise HTTPException(404, {"en": "no such step", "zh": "没有这一步"})


def _thin_cmp(cmp):
    out = dict(cmp)
    for k in ("t", "mbd", "camkit"):
        out[k] = [round(float(x), 5) for x in _thin(np.asarray(cmp[k]), 600)]
    return out


def _jid(jid):
    return re.sub(r"[^0-9A-Za-z_-]", "", jid)


def _title(p, what):
    t = (p.get("title") or {}).get("zh") or "凸轮系统"
    return f"{t} · {what}"[:120]


def register(app, run, project_of):
    @app.post("/api/system")
    async def system_ep(request: Request):
        p = await project_of(request)
        return run(lambda: system_view(p))

    @app.post("/api/system/mesh/{cid}")
    async def mesh_ep(cid: str, request: Request):
        p = await project_of(request)
        return run(lambda: mesh_view(p, cid))

    @app.post("/api/system/export/{kind}")
    async def sys_export_ep(kind: str, request: Request, cam: str = ""):
        p = await project_of(request)
        return run(lambda: system_export(p, kind, cam))

    @app.post("/api/system/optimize")
    async def opt_ep(request: Request):
        p = await project_of(request)
        return run(lambda: OPT.optimise(p))

    @app.get("/api/examples/{eid}/cae")
    def example_cae_ep(eid: str):
        return example_cae(eid)

    @app.get("/api/cae/me")
    def cae_me_ep(request: Request):
        return cae_me(request)

    @app.post("/api/cae/mbd")
    async def cae_mbd_ep(request: Request):
        p = await project_of(request)
        return run(lambda: cae_mbd(request, p))

    @app.post("/api/cae/arm")
    async def cae_arm_ep(request: Request):
        p = await project_of(request)
        return run(lambda: cae_arm(request, p))

    @app.get("/api/cae/jobs/{jid}")
    def cae_job_ep(jid: str, request: Request):
        return run(lambda: cae_job(request, jid))

    @app.post("/api/cae/jobs/{jid}/{what}")
    async def cae_follow_ep(jid: str, what: str, request: Request):
        p = await project_of(request)
        return run(lambda: cae_followup(request, jid, what, p))
