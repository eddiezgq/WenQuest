"""Cloud projects in the cam service (round 39, step 7; plan section 十二). The projects live in the learning platform's
gateway (/api/v1/cam/projects: the company activation, sharing within the company, 20 versions kept, save conflicts);
here the browser's sign-in (the site-wide cookie, or a Bearer token) is passed on and the gateway's answers are put
into words the page can show. The project's content is passed through as it is.

  GET    /api/me                         who is signed in, the company, whether the cloud is open to them
  GET    /api/projects                   the company's projects
  POST   /api/projects                   {name, kind, body} → version 1
  GET    /api/projects/{id}[?version=n]  open (the current version, or an older one to look at)
  PUT    /api/projects/{id}              {body, base[, name]} → 409 with who saved a newer version and when
  POST   /api/projects/{id}/restore      {version, base}
  DELETE /api/projects/{id}
"""

from __future__ import annotations

import json

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

import cae_bridge as B

ERRORS = {
    401: ("sign in to use cloud projects", "请先登录问渠账号，再用云端项目"),
    403: ("cloud projects are for activated company accounts; ask WenQuest to activate yours",
          "云端项目给已开通的企业账号用，请联系问渠开通"),
    404: ("this project or version is not there (deleted, or older than the 20 kept)",
          "找不到这个项目或这一版（已删除，或早于保留的 20 版）"),
    413: ("a project can be at most 2 MB", "单个项目不能超过 2 MB"),
    422: ("the name is empty or too long", "名称不能为空，也不能太长"),
}


def _headers(request: Request) -> dict:
    return {k: request.headers[k] for k in ("cookie", "authorization") if request.headers.get(k)}


def gateway(request: Request, method: str, path: str, **kw):
    h = _headers(request)
    if not h:
        raise HTTPException(401, {"en": ERRORS[401][0], "zh": ERRORS[401][1]})
    try:
        r = B._client().request(method, B.GATEWAY + "/api/v1/cam/projects" + path, headers=h, timeout=60, **kw)
    except httpx.HTTPError as exc:
        raise HTTPException(503, {"en": "the cloud cannot be reached just now",
                                  "zh": "暂时连不上云端，请稍后再试"}) from exc
    if r.status_code == 409:                       # someone saved a newer version: the page needs who and when
        return JSONResponse(r.json(), status_code=409)
    if r.status_code in ERRORS:
        en, zh = ERRORS[r.status_code]
        raise HTTPException(r.status_code, {"en": en, "zh": zh})
    if r.status_code == 400:
        raise HTTPException(400, {"en": "at most 500 projects per company", "zh": "每家单位最多 500 个云端项目"})
    if r.status_code >= 400:
        raise HTTPException(502, {"en": "the cloud returned an error", "zh": "云端这次出错了，请再试一次"})
    return r.json()


def register(app, max_body: int) -> None:
    async def body_of(request: Request) -> dict:
        raw = await request.body()
        if len(raw) > max_body:
            raise HTTPException(413, {"en": ERRORS[413][0], "zh": ERRORS[413][1]})
        try:
            d = json.loads(raw or b"{}")
        except ValueError as exc:
            raise HTTPException(400, {"en": "not JSON", "zh": "不是 JSON"}) from exc
        if not isinstance(d, dict):
            raise HTTPException(400, {"en": "not an object", "zh": "格式不对"})
        return d

    @app.get("/api/me")
    def me(request: Request):
        m = B.identity(request)
        return {k: m.get(k) for k in ("login", "licensed", "org", "name")} | {"reachable": "error" not in m}

    @app.get("/api/projects")
    def list_ep(request: Request):
        return gateway(request, "GET", "")

    @app.post("/api/projects")
    async def create_ep(request: Request):
        return gateway(request, "POST", "", json=await body_of(request))

    @app.get("/api/projects/{pid}")
    def open_ep(pid: int, request: Request, version: int | None = None):
        return gateway(request, "GET", f"/{pid}", params={"version": version} if version else None)

    @app.put("/api/projects/{pid}")
    async def save_ep(pid: int, request: Request):
        return gateway(request, "PUT", f"/{pid}", json=await body_of(request))

    @app.post("/api/projects/{pid}/restore")
    async def restore_ep(pid: int, request: Request):
        return gateway(request, "POST", f"/{pid}/restore", json=await body_of(request))

    @app.delete("/api/projects/{pid}")
    def delete_ep(pid: int, request: Request):
        return gateway(request, "DELETE", f"/{pid}")
