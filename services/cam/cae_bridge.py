"""问渠凸轮 → digital factory CAE (round 39, step 4d). The browser never talks to the factory: the cam service checks
who is signed in (the site-wide sign-in, through the learning platform's gateway: /api/v1/industry/me), and for an
account activated for a company it passes the job to the factory hub's design-software interface with the server key.

Environment: WQ_GATEWAY_URL (default http://gateway:8000), WQ_FACTORY_URL (https://factory.<domain>),
WQ_FACTORY_CAE_KEY (copied from the factory's .env at deploy). Without the factory settings CAE is "not set up here".
"""

from __future__ import annotations

import os

import httpx
from fastapi import HTTPException, Request

GATEWAY = os.environ.get("WQ_GATEWAY_URL", "http://gateway:8000").rstrip("/")
TIMEOUT = 180  # reading a STEP and meshing it for the viewer can take a minute
CLIENT: httpx.Client | None = None  # tests swap in their own


def _client() -> httpx.Client:
    global CLIENT
    if CLIENT is None:
        CLIENT = httpx.Client(timeout=TIMEOUT)
    return CLIENT


def factory_url() -> str:
    return os.environ.get("WQ_FACTORY_URL", "").rstrip("/")


def configured() -> bool:
    return bool(factory_url() and os.environ.get("WQ_FACTORY_CAE_KEY"))


def identity(request: Request) -> dict:
    """Who is signed in, and the company the account is activated for (same activation as the sewing software)."""
    headers = {}
    if request.headers.get("cookie"):
        headers["cookie"] = request.headers["cookie"]
    if request.headers.get("authorization"):
        headers["authorization"] = request.headers["authorization"]
    if not headers:
        return {"login": False, "licensed": False, "org": "", "user_id": None, "name": ""}
    try:
        r = _client().get(GATEWAY + "/api/v1/industry/me", headers=headers)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError:
        return {"login": False, "licensed": False, "org": "", "user_id": None, "name": "", "error": "gateway"}


def need_company(request: Request) -> dict:
    if not configured():
        raise HTTPException(503, {"en": "CAE is not set up on this server", "zh": "这台服务器还没有接上问渠 CAE"})
    me = identity(request)
    if not me.get("login"):
        raise HTTPException(401, {"en": "sign in first", "zh": "请先登录"})
    if not me.get("licensed"):
        raise HTTPException(403, {"en": "CAE is for activated company accounts",
                                  "zh": "CAE 计算给已开通的企业账号用，请联系问渠开通"})
    return me


def hub(method: str, path: str, **kw):
    headers = {"authorization": "Bearer " + os.environ.get("WQ_FACTORY_CAE_KEY", "")}
    try:
        r = _client().request(method, factory_url() + "/api/design-sw" + path, headers=headers, **kw)
    except httpx.HTTPError as exc:
        raise HTTPException(503, {"en": "the digital factory cannot be reached",
                                  "zh": "数字工厂暂时连不上，请稍后再试"}) from exc
    if r.status_code >= 400:
        try:
            d = r.json().get("detail")
        except ValueError:
            d = r.text[:200]
        raise HTTPException(r.status_code if r.status_code < 500 else 502, {"en": str(d), "zh": str(d)})
    return r.json()
