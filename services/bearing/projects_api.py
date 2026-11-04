"""Cloud projects in the bearing service (round 64, step 7; plan section 十五). The projects live in the learning
platform's gateway (/api/v1/bearing/projects: company activation, sharing within the company, 20 versions kept, save
conflicts, two kinds: design projects and process templates); here the browser's sign-in (the site-wide cookie or a
Bearer token) is passed on and the gateway's answers are put into words the page can show. Contents pass through as
they are. The same way as the cam service (services/cam/projects_api.py).

  GET    /api/me                         who is signed in, the company, whether the cloud is open to them
  GET    /api/projects[?kind=design|process]
  POST   /api/projects                   {name, kind, body} → version 1
  GET    /api/projects/{id}[?version=n]
  PUT    /api/projects/{id}              {body, base[, name]} → 409 with who saved a newer version and when
  POST   /api/projects/{id}/restore      {version, base}
  DELETE /api/projects/{id}
"""

from __future__ import annotations

import json
import os

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

GATEWAY = os.environ.get("WQ_GATEWAY_URL", "http://gateway:8000").rstrip("/")
TIMEOUT = 60.0
_CLIENT: list[httpx.Client] = []

ERRORS = {
    401: ("sign in to use cloud projects", "请先登录问渠账号，再用云端项目"),
    403: (
        "cloud projects are for activated company accounts; ask WenQuest to activate yours",
        "云端项目给已开通的企业账号用，请联系问渠开通",
    ),
    404: (
        "this project or version is not there (deleted, or older than the 20 kept)",
        "找不到这个项目或这一版（已删除，或早于保留的 20 版）",
    ),
    413: ("a project can be at most 2 MB", "单个项目不能超过 2 MB"),
    422: ("the name is empty or too long", "名称不能为空，也不能太长"),
}


def client() -> httpx.Client:
    if not _CLIENT:
        _CLIENT.append(httpx.Client(timeout=TIMEOUT))
    return _CLIENT[0]


def _headers(request: Request) -> dict:
    return {k: request.headers[k] for k in ("cookie", "authorization") if request.headers.get(k)}


def identity(request: Request) -> dict:
    """Who is signed in and the company the account is activated for (same activation as the sewing and cam
    software)."""
    h = _headers(request)
    if not h:
        return {"login": False, "licensed": False, "org": "", "user_id": None, "name": ""}
    try:
        r = client().get(GATEWAY + "/api/v1/industry/me", headers=h)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError:
        return {"login": False, "licensed": False, "org": "", "user_id": None, "name": "", "error": "gateway"}


def gateway(request: Request, method: str, path: str, base: str = "/api/v1/bearing/projects", errors=None, **kw):
    errors = errors or ERRORS
    h = _headers(request)
    if not h:
        raise HTTPException(401, {"en": errors[401][0], "zh": errors[401][1]})
    try:
        r = client().request(method, GATEWAY + base + path, headers=h, **kw)
    except httpx.HTTPError as exc:
        raise HTTPException(
            503, {"en": "the cloud cannot be reached just now", "zh": "暂时连不上云端，请稍后再试"}
        ) from exc
    if r.status_code == 409:  # someone saved a newer version: the page needs who and when
        return JSONResponse(r.json(), status_code=409)
    if r.status_code in errors:
        en, zh = errors[r.status_code]
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
        m = identity(request)
        return {k: m.get(k) for k in ("login", "licensed", "org", "name")} | {"reachable": "error" not in m}

    @app.get("/api/projects")
    def list_ep(request: Request, kind: str | None = None):
        if kind not in (None, "", "design", "process"):
            raise HTTPException(400, {"en": "the kind is design or process", "zh": "类型是设计项目或工艺模板"})
        return gateway(request, "GET", "", params={"kind": kind} if kind else None)

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
