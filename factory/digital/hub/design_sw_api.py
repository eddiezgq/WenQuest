# -*- coding: utf-8 -*-
"""设计软件接口（学习平台第 41 轮，第 39 轮第 4 步共用）：问渠缝纫机设计软件（学习平台网关）和问渠凸轮（凸轮服务）
把计算任务交给数字工厂的 cae 计算服务。

- 只认服务器对服务器的钥匙 WQ_FACTORY_CAE_KEY（Authorization: Bearer），不对外开放；
- 任务按软件登记在单独的工厂编号下（app=sewing → wq_sewing_saas，默认；app=cam → wq_cam_saas），
  提交人记成“单位::用户”，单位之间互相看不到；
- 每个单位每天的任务数有上限（有限元 / 模态 / 动力学 / 拓扑优化 WQ_DESIGN_SW_DAILY，默认 20；数控编程 WQ_DESIGN_SW_CAM_DAILY，默认 100；
  要用有限元的优化 WQ_DESIGN_SW_OPT_DAILY，默认 5）；
- 只提交计算、读结果，不改零件库，不改生产数据（《数字工厂资源接口约定》第七节）。
"""
import hmac
import os
import time

from fastapi import Body, Depends, Header, HTTPException, Request
from fastapi.responses import Response

from hub import cae_api

FACTORY = "wq_sewing_saas"
APPS = {"sewing": "wq_sewing_saas", "cam": "wq_cam_saas"}
KINDS = ("fea", "mbd")


def factory_of(app):
    if app in (None, ""):
        return FACTORY
    if app not in APPS:
        raise HTTPException(400, "不认识的设计软件")
    return APPS[app]


def _key():
    return os.environ.get("WQ_FACTORY_CAE_KEY", "")


def require_key(authorization: str = Header(default="")):
    k = _key()
    got = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
    if not k or not got or not hmac.compare_digest(got.encode(), k.encode()):
        raise HTTPException(401, "需要设计软件钥匙（Authorization: Bearer …）")
    return True


def daily_limit(kind):
    if kind == "opt":
        return int(os.environ.get("WQ_DESIGN_SW_OPT_DAILY", "5"))
    if kind == "cam":                      # 数控编程几秒、不排队，单独计数
        return int(os.environ.get("WQ_DESIGN_SW_CAM_DAILY", "100"))
    return int(os.environ.get("WQ_DESIGN_SW_DAILY", "20"))


def _used(js, kind):
    """今天（滚动 24 小时）用了几个：数控编程单独算，其余（有限元、模态、动力学、拓扑优化）合在一起算"""
    today = time.time() - 86400
    return sum(1 for j in js if (j.get("created") or 0) > today and ((j.get("kind") == "cam") == (kind == "cam")))


def _org(org):
    org = (org or "").strip()
    if not org or "::" in org or len(org) > 80:
        raise HTTPException(400, "单位名称不对")
    return org


def _jobs(org, kind="", factory=FACTORY):
    params = {"factory": factory, "limit": 500}
    if kind:
        params["kind"] = kind
    js = cae_api.call("GET", "/jobs", params=params).json()["jobs"]
    return [j for j in js if str(j.get("owner") or "").startswith(org + "::")]


def _mine(jid, org):
    j = cae_api.call("GET", "/jobs/{}".format(jid.replace("/", ""))).json()
    if j.get("factory") not in APPS.values() or not str(j.get("owner") or "").startswith(_org(org) + "::"):
        raise HTTPException(404, "没有这个任务")
    return j


def mount(app):
    dep = [Depends(require_key)]

    @app.get("/api/design-sw/health", dependencies=dep)
    def ds_health():
        return cae_api.call("GET", "/health").json()

    @app.get("/api/design-sw/materials", dependencies=dep)
    def ds_materials():
        return cae_api.call("GET", "/materials").json()

    @app.get("/api/design-sw/motors", dependencies=dep)
    def ds_motors():
        """主轴伺服选型用的电机表（与动力学的电机选型助手同一张）"""
        from cae import motors as MT
        return {"motors": [{"name": m[0], "power_w": m[1], "rated_nm": m[2], "peak_nm": m[3], "max_rpm": m[4], "inertia_kgm2": m[5]}
                           for m in MT.MOTORS], "source": MT.SOURCE}

    @app.post("/api/design-sw/geometry", dependencies=dep)
    async def ds_geometry(request: Request):
        data = await request.body()
        return cae_api.call("POST", "/geometry", content=data).json()

    @app.post("/api/design-sw/mbd/model", dependencies=dep)
    async def ds_mbd_model(request: Request, name: str = "model.xml"):
        """上传设计软件自己生成的 MJCF（问渠凸轮的整机模型），返回可直接放进任务 model 的引用"""
        data = await request.body()
        return cae_api.call("POST", "/mbd/models/upload", params={"name": name[:60]}, content=data).json()

    @app.post("/api/design-sw/jobs", dependencies=dep)
    def ds_submit(body: dict = Body(...)):
        org = _org(body.get("org"))
        factory = factory_of(body.get("app"))
        kind = body.get("kind") or "fea"
        if kind not in KINDS:
            raise HTTPException(400, "不认识的计算类型")
        used = _used(_jobs(org, factory=factory), kind)
        if used >= daily_limit(kind):
            raise HTTPException(429, "本单位今天的计算次数已用完（每天 {} 个），明天再来或联系问渠调整".format(daily_limit(kind)))
        owner = "{}::{}".format(org, str(body.get("user") or "")[:40])
        common = {"owner": owner, "owner_name": str(body.get("user_name") or "")[:60], "factory": factory,
                  "title": str(body.get("title") or "")[:80], "item": str(body.get("item") or "")[:40] or None}
        if kind == "fea":
            return cae_api.call("POST", "/jobs", json=dict(common, step_sha=body.get("step_sha"), setup=body.get("setup") or {})).json()
        return cae_api.call("POST", "/mbd/jobs", json=dict(common, model=body.get("model") or {}, setup=body.get("setup") or {})).json()

    # ---------- 拓扑优化（两孔平板）、数控编程（学习平台第 41 轮第二批） ----------
    def _quota(org, factory, kind="fea"):
        if _used(_jobs(org, factory=factory), kind) >= daily_limit(kind):
            raise HTTPException(429, "本单位今天的{}次数已用完（每天 {} 个），明天再来或联系问渠调整".format(
                "数控编程" if kind == "cam" else "计算", daily_limit(kind)))

    def _common(body, factory):
        return {"owner": "{}::{}".format(_org(body.get("org")), str(body.get("user") or "")[:40]), "owner_name": str(body.get("user_name") or "")[:60],
                "factory": factory, "title": str(body.get("title") or "")[:80]}

    @app.post("/api/design-sw/topo", dependencies=dep)
    def ds_topo(body: dict = Body(...)):
        """body：org、user、title、spec（preset = plate，plate = 平板说明，volfrac）"""
        org = _org(body.get("org"))
        factory = factory_of(body.get("app"))
        _quota(org, factory)
        spec = dict(body.get("spec") or {}, preset="plate")
        return cae_api.call("POST", "/topo/jobs", json=dict(_common(body, factory), spec=spec)).json()

    @app.get("/api/design-sw/topo/{jid}/result", dependencies=dep)
    def ds_topo_result(jid: str, org: str):
        j = _mine(jid, org)
        return cae_api.call("GET", "/topo/jobs/{}/result".format(j["id"])).json()

    @app.post("/api/design-sw/topo/{jid}/to-step", dependencies=dep)
    def ds_topo_step(jid: str, org: str):
        j = _mine(jid, org)
        return cae_api.call("POST", "/topo/jobs/{}/to-step".format(j["id"])).json()

    @app.get("/api/design-sw/geometry/{sha}/step", dependencies=dep)
    def ds_step(sha: str):
        r = cae_api.call("GET", "/geometry/{}/step".format(sha.replace("/", "")))
        return Response(r.content, media_type="application/step")

    @app.post("/api/design-sw/cam", dependencies=dep)
    def ds_cam(body: dict = Body(...)):
        """平板零件的铣削程序：body：org、user、title、sha（已登记的 STEP）、name、material、stock_margin。
        识别外轮廓、型腔、孔 → 编程单（立式加工中心）→ 生成程序并试切检查（同步，几秒）"""
        from cae import cam_job as J
        org = _org(body.get("org"))
        factory = factory_of(body.get("app"))
        _quota(org, factory, "cam")
        r = cae_api.call("POST", "/cam/recognize", json={"sha": body.get("sha")}).json()
        if r["mill"].get("error"):
            raise HTTPException(422, "认不出铣削特征：" + r["mill"]["error"])
        try:
            spec = J.plan_mill(r["mill"], "VMC-01", str(body.get("material") or "45"), float(body.get("stock_margin", 2.0)),
                               str(body.get("name") or "零件")[:40])
        except ValueError as e:
            raise HTTPException(400, str(e)) from None
        j = cae_api.call("POST", "/cam/jobs", json=dict(_common(body, factory), spec=spec)).json()
        j["features"] = {k: r["mill"].get(k) for k in ("top", "bottom", "bbox")}
        j["features"].update(pockets=len(r["mill"].get("pockets") or []), holes=len(r["mill"].get("holes") or []),
                             narrow=r["mill"].get("narrow_openings") or 0)
        return j

    @app.get("/api/design-sw/cam/{jid}/{k}.nc", dependencies=dep)
    def ds_cam_nc(jid: str, k: int, org: str):
        j = _mine(jid, org)
        r = cae_api.call("GET", "/cam/jobs/{}/{}.nc".format(j["id"], int(k)))
        return Response(r.content, media_type="text/plain; charset=utf-8")

    @app.get("/api/design-sw/jobs", dependencies=dep)
    def ds_jobs(org: str, app: str = ""):
        org = _org(org)
        js = _jobs(org, factory=factory_of(app))
        return {"jobs": js, "used_today": _used(js, "fea"), "daily_limit": daily_limit("fea"),
                "cam_used_today": _used(js, "cam"), "cam_daily_limit": daily_limit("cam")}

    @app.get("/api/design-sw/jobs/{jid}", dependencies=dep)
    def ds_job(jid: str, org: str):
        return _mine(jid, org)

    @app.post("/api/design-sw/jobs/{jid}/fatigue", dependencies=dep)
    def ds_fatigue(jid: str, org: str, body: dict = Body(...)):
        j = _mine(jid, org)
        return cae_api.call("POST", "/jobs/{}/fatigue".format(j["id"]), json=body).json()

    @app.post("/api/design-sw/jobs/{jid}/modal", dependencies=dep)
    def ds_modal(jid: str, org: str):
        j = _mine(jid, org)
        return cae_api.call("POST", "/jobs/{}/modal".format(j["id"])).json()

    @app.post("/api/design-sw/jobs/{jid}/report", dependencies=dep)
    def ds_report(jid: str, org: str, body: dict = Body(default={})):
        j = _mine(jid, org)
        r = cae_api.call("POST", "/jobs/{}/report".format(j["id"]), json=body)
        return Response(r.content, media_type=r.headers.get("content-type", "application/octet-stream"),
                        headers={"Content-Disposition": r.headers.get("content-disposition", "attachment")})

    @app.get("/api/design-sw/jobs/{jid}/surface.bin", dependencies=dep)
    def ds_surface(jid: str, org: str):
        j = _mine(jid, org)
        return Response(cae_api.call("GET", "/jobs/{}/surface.bin".format(j["id"])).content, media_type="application/octet-stream")

    @app.get("/api/design-sw/jobs/{jid}/series.bin", dependencies=dep)
    def ds_series(jid: str, org: str):
        """动力学的全部曲线（单精度，不取整；低速仿真后要按转速平方换算，取整会丢精度）"""
        j = _mine(jid, org)
        return Response(cae_api.call("GET", "/jobs/{}/series.bin".format(j["id"])).content, media_type="application/octet-stream")

    @app.get("/api/design-sw/mbd/jobs/{jid}/joint-series", dependencies=dep)
    def ds_joint_series(jid: str, org: str, joint: str):
        j = _mine(jid, org)
        return cae_api.call("GET", "/mbd/jobs/{}/joint-series".format(j["id"]), params={"joint": joint}).json()

    @app.get("/api/design-sw/mbd/jobs/{jid}/member-series", dependencies=dep)
    def ds_member_series(jid: str, org: str, member: str):
        j = _mine(jid, org)
        return cae_api.call("GET", "/mbd/jobs/{}/member-series".format(j["id"]), params={"member": member}).json()

    @app.get("/api/design-sw/mbd/jobs/{jid}/motors", dependencies=dep)
    def ds_mbd_motors(jid: str, org: str):
        j = _mine(jid, org)
        return cae_api.call("GET", "/mbd/jobs/{}/motors".format(j["id"])).json()
