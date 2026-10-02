# -*- coding: utf-8 -*-
"""仿真与分析（第 11 轮）：枢纽这边核对身份、取零件 STEP，转交给 cae 计算服务。

所有工厂共用一个 cae 服务，任务上带工厂编号（历史库名，如 wq_factory / wq_demo / wq_c_pilot）和提交人。
学生看自己的任务；老师（厂长角色、班级任课老师）看本厂全部任务。
"""
import os
import urllib.parse

import httpx
from fastapi import Body, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

CAE_URL = os.environ.get("WQ_CAE_URL", "http://cae:8200")
FACTORY_ID = os.environ.get("WQ_FACTORY_ID") or urllib.parse.urlparse(
    os.environ.get("WQ_DB", "postgresql://x@h/wq_factory")).path.strip("/") or "wq_factory"
CLIENT = None                 # 测试时换成计算服务的 TestClient
import logging  # noqa: E402
logging.getLogger("httpx").setLevel(logging.WARNING)


def client():
    global CLIENT
    if CLIENT is None:
        CLIENT = httpx.Client(base_url=CAE_URL, timeout=120)
    return CLIENT


def call(method, path, **kw):
    try:
        r = client().request(method, path, **kw)
    except httpx.HTTPError:
        raise HTTPException(503, "计算服务暂时连不上，请稍后再试") from None
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail")
        except Exception:  # noqa: BLE001
            detail = r.text[:200]
        raise HTTPException(r.status_code, detail)
    return r


def mount(app, H, user_of, who, uid_of, is_teacher):
    from hub import plm

    def mine(u, j):
        if j.get("factory") != FACTORY_ID:
            raise HTTPException(404, "没有这个任务")
        if is_teacher(u) or str(j.get("owner")) == uid_of(u):
            return j
        raise HTTPException(403, "这是别人的计算任务")

    @app.get("/api/cae/health")
    def cae_health():
        """计算服务是否在线（上线检查用，不需要登录）"""
        return call("GET", "/health").json()

    @app.get("/api/cae/materials")
    def cae_materials(u=Depends(user_of)):
        return call("GET", "/materials").json()

    @app.get("/api/cae/parts")
    def cae_parts(u=Depends(user_of)):
        """可以直接分析的零件：有现行 STEP 的物料（SH-301 总有）；另外可以上传 STEP"""
        return {"items": [dict(plm.item_info(i) or {"item": i}, item=i) for i in plm.items_with_step(H.db, u["mode"])]}

    def _geo(step, item=None, name=None):
        g = call("POST", "/geometry", content=step, headers={"content-type": "application/step"}).json()
        g["item"], g["name"] = item, name
        g["model_url"] = "/api/cae/geometry/{}/model.glb".format(g["sha"])
        return g

    @app.post("/api/cae/geometry/item/{item}")
    def cae_geometry_item(item: str, u=Depends(user_of)):
        step = plm.current_step(H.db, u["mode"], item)
        if not step:
            raise HTTPException(404, "{} 还没有发布过三维模型（STEP）".format(item))
        return _geo(step, item=item, name=item)

    @app.post("/api/cae/geometry/upload")
    async def cae_geometry_upload(step: UploadFile = File(...), u=Depends(user_of)):
        data = await step.read()
        if len(data) > 30 * 1024 * 1024:
            raise HTTPException(413, "STEP 文件超过 30 MB，教学版不支持")
        return _geo(data, name=step.filename)

    @app.get("/api/cae/geometry/{sha}/model.glb")
    def cae_geometry_glb(sha: str):
        r = call("GET", "/geometry/{}/model.glb".format(sha))
        return Response(r.content, media_type="model/gltf-binary", headers={"Cache-Control": "max-age=86400"})

    @app.post("/api/cae/jobs")
    def cae_submit(body: dict = Body(...), u=Depends(user_of)):
        return call("POST", "/jobs", json={
            "step_sha": body.get("step_sha"), "setup": body.get("setup") or {}, "title": (body.get("title") or "")[:80],
            "item": body.get("item"), "owner": uid_of(u), "owner_name": who(u), "factory": FACTORY_ID}).json()

    @app.get("/api/cae/jobs")
    def cae_jobs(u=Depends(user_of)):
        params = {"factory": FACTORY_ID, "limit": 100}
        if not is_teacher(u):
            params["owner"] = uid_of(u)
        return call("GET", "/jobs", params=params).json()

    @app.get("/api/cae/jobs/{jid}")
    def cae_job(jid: str, u=Depends(user_of)):
        return mine(u, call("GET", "/jobs/" + urllib.parse.quote(jid)).json())

    @app.post("/api/cae/jobs/{jid}/report")
    def cae_report(jid: str, body: dict = Body(default={}), u=Depends(user_of)):
        mine(u, call("GET", "/jobs/" + urllib.parse.quote(jid)).json())
        r = call("POST", "/jobs/{}/report".format(urllib.parse.quote(jid)), json=body)
        return Response(r.content, media_type=r.headers.get("content-type"),
                        headers={"Content-Disposition": r.headers.get("content-disposition", "attachment")})

    @app.get("/api/cae/jobs/{jid}/surface.bin")
    def cae_surface(jid: str, u=Depends(user_of)):
        mine(u, call("GET", "/jobs/" + urllib.parse.quote(jid)).json())
        r = call("GET", "/jobs/{}/surface.bin".format(urllib.parse.quote(jid)))
        return Response(r.content, media_type="application/octet-stream", headers={"Cache-Control": "max-age=86400"})
