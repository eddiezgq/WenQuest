# -*- coding: utf-8 -*-
"""设计软件接口（第 39 轮第 4 步 / 第 41 轮共用）：学习平台上的行业专用软件（问渠凸轮、缝纫机设计）提交 CAE 计算。

只认服务器对服务器的钥匙 WQ_FACTORY_CAE_KEY（Authorization: Bearer），不对浏览器开放；只能提交计算、取结果，
不改零件库、不改生产数据（《数字工厂资源接口约定》“设计软件提交计算任务”一节）。
调用方在请求里写明软件（app：cam / sewing）、单位（org）和提交人（user、user_name）——身份由调用方（学习平台网关、
凸轮服务）核对过企业开通后才转来。任务记在计算服务的工厂编号 wq_<app>_saas 下，owner 为“单位/提交人”。
用量：每个单位每天有限元 / 模态 / 动力学任务上限 WQ_DESIGN_SW_DAILY（默认 20）。

路径（都在 /api/design-sw/ 下）：
  GET  materials                       材料库（带出处）
  POST geometry?app=&org=              正文是 STEP → 面列表（id、类型、圆柱的轴线与半径、面积、中心）与 sha
  POST fea                             {app, org, user, user_name, sha, setup, title} → 有限元任务
  POST mbd/model?app=&org=&name=       正文是 MJCF（xml）→ 模型信息（关节、构件）
  POST mbd                             {app, org, user, user_name, model, setup, title} → 动力学任务
  GET  jobs/{jid}?org=                 任务状态和结果（只能看本单位的）
  POST jobs/{jid}/modal?org=           固有频率（用这次强度计算的零件、材料和支承）
  POST jobs/{jid}/fatigue?org=         疲劳寿命（正文同计算服务）
  GET  jobs/{jid}/joint-series?org=&joint=   动力学：某个关节的位置、速度、驱动力随时间
  GET  jobs/{jid}/motors?org=          动力学：电机选型（数字工厂电机库）
"""
import datetime as dt
import hmac
import os
import re

from fastapi import Body, Depends, Header, HTTPException, Request

APPS = ("cam", "sewing")


def _key():
    return os.environ.get("WQ_FACTORY_CAE_KEY", "")


def require_key(authorization: str = Header(default="")):
    k = _key()
    got = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
    if not k or not got or not hmac.compare_digest(got.encode(), k.encode()):
        raise HTTPException(401, "需要数字工厂设计软件钥匙（Authorization: Bearer …）")
    return True


def factory_of(app):
    if app not in APPS:
        raise HTTPException(400, "不认识的设计软件")
    return "wq_{}_saas".format(app)


def _org(org):
    org = (org or "").strip()
    if not org or len(org) > 80 or "/" in org:
        raise HTTPException(400, "单位名称不对")
    return org


def daily_limit():
    try:
        return int(os.environ.get("WQ_DESIGN_SW_DAILY", "20"))
    except ValueError:
        return 20


def mount(app, call):
    """call(method, path, **kw)：转交计算服务（hub.cae_api.call；测试时换成假的）。"""

    def used_today(factory, org):
        jobs = call("GET", "/jobs", params={"factory": factory, "limit": 500}).json().get("jobs", [])
        today = dt.date.today()
        n = 0
        for j in jobs:
            if not str(j.get("owner") or "").startswith(org + "/"):
                continue
            created = j.get("created")
            if created and dt.date.fromtimestamp(float(created)) == today:
                n += 1
        return n

    def check_quota(factory, org):
        if used_today(factory, org) >= daily_limit():
            raise HTTPException(429, "本单位今天的计算次数已用完（每天 {} 个），明天再算或联系问渠".format(daily_limit()))

    def owned(jid, org):
        jid = re.sub(r"[^0-9A-Za-z_-]", "", jid)
        j = call("GET", "/jobs/{}".format(jid)).json()
        if not str(j.get("factory") or "").endswith("_saas") or not str(j.get("owner") or "").startswith(_org(org) + "/"):
            raise HTTPException(404, "没有这个任务")
        return j

    @app.get("/api/design-sw/materials")
    def ds_materials(_=Depends(require_key)):
        return call("GET", "/materials").json()

    @app.post("/api/design-sw/geometry")
    async def ds_geometry(request: Request, app: str = "cam", org: str = "", _=Depends(require_key)):
        factory_of(app)
        _org(org)
        data = await request.body()
        return call("POST", "/geometry", content=data).json()

    @app.post("/api/design-sw/fea")
    def ds_fea(body: dict = Body(...), _=Depends(require_key)):
        factory = factory_of(body.get("app"))
        org = _org(body.get("org"))
        check_quota(factory, org)
        payload = {"step_sha": body.get("sha"), "setup": body.get("setup") or {}, "title": body.get("title") or "",
                   "factory": factory, "owner": "{}/{}".format(org, body.get("user") or ""),
                   "owner_name": body.get("user_name") or ""}
        return call("POST", "/jobs", json=payload).json()

    @app.post("/api/design-sw/mbd/model")
    async def ds_mbd_model(request: Request, app: str = "cam", org: str = "", name: str = "model.xml",
                           _=Depends(require_key)):
        factory_of(app)
        _org(org)
        data = await request.body()
        return call("POST", "/mbd/models/upload", params={"name": name}, content=data).json()

    @app.post("/api/design-sw/mbd")
    def ds_mbd(body: dict = Body(...), _=Depends(require_key)):
        factory = factory_of(body.get("app"))
        org = _org(body.get("org"))
        check_quota(factory, org)
        payload = {"model": body.get("model") or {}, "setup": body.get("setup") or {}, "title": body.get("title") or "",
                   "factory": factory, "owner": "{}/{}".format(org, body.get("user") or ""),
                   "owner_name": body.get("user_name") or ""}
        return call("POST", "/mbd/jobs", json=payload).json()

    @app.get("/api/design-sw/jobs/{jid}")
    def ds_job(jid: str, org: str = "", _=Depends(require_key)):
        return owned(jid, org)

    @app.post("/api/design-sw/jobs/{jid}/modal")
    def ds_modal(jid: str, org: str = "", _=Depends(require_key)):
        j = owned(jid, org)
        return call("POST", "/jobs/{}/modal".format(j["id"])).json()

    @app.post("/api/design-sw/jobs/{jid}/fatigue")
    def ds_fatigue(jid: str, org: str = "", body: dict = Body(...), _=Depends(require_key)):
        j = owned(jid, org)
        out = call("POST", "/jobs/{}/fatigue".format(j["id"]), json=body).json()
        out.pop("damage_b64", None)              # 设计软件只要汇总
        return out

    @app.get("/api/design-sw/jobs/{jid}/joint-series")
    def ds_joint_series(jid: str, org: str = "", joint: str = "", _=Depends(require_key)):
        j = owned(jid, org)
        return call("GET", "/mbd/jobs/{}/joint-series".format(j["id"]), params={"joint": joint}).json()

    @app.get("/api/design-sw/jobs/{jid}/motors")
    def ds_motors(jid: str, org: str = "", safety: float = 1.2, _=Depends(require_key)):
        j = owned(jid, org)
        return call("GET", "/mbd/jobs/{}/motors".format(j["id"]), params={"safety": safety}).json()
