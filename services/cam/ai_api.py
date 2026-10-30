"""AI drafting in the cam service (round 39, step 6; plan section 十一). The model is called through the learning
platform's gateway (/api/v1/cam/ai/*: sign-in, daily limit, the record of every run, Claude in the US and DeepSeek
in China); here plain code checks what comes back (camkit.ai_check) and runs the cam's checks on a draft. Nothing is
written into the project: the browser shows the draft and the user adopts it or not.
"""

from __future__ import annotations

import copy
import json

import httpx
from fastapi import HTTPException, Request

import cae_bridge as B
from camkit import ai_check as AC
from camkit.analyze import analyse as analyse_cam
from camkit.laws import LAWS

GW_ERRORS = {
    401: ("sign in to use AI drafting", "请先登录（问渠账号），再用 AI 起草"),
    429: ("today's AI drafts are used up", "今天的 AI 起草次数用完了，明天再来"),
    503: ("no AI model is set up on this server", "这台服务器还没有配置 AI 模型"),
}


def _headers(request: Request) -> dict:
    h = {}
    for k in ("cookie", "authorization"):
        if request.headers.get(k):
            h[k] = request.headers[k]
    return h


def gateway(request: Request, path: str, body: dict) -> dict:
    h = _headers(request)
    if not h:
        en, zh = GW_ERRORS[401]
        raise HTTPException(401, {"en": en, "zh": zh})
    try:
        r = B._client().post(B.GATEWAY + "/api/v1/cam/ai" + path, json=body, headers=h, timeout=200)
    except httpx.HTTPError as exc:
        raise HTTPException(503, {"en": "the AI service cannot be reached", "zh": "暂时连不上 AI 服务"}) from exc
    if r.status_code in GW_ERRORS:
        en, zh = GW_ERRORS[r.status_code]
        raise HTTPException(r.status_code, {"en": en, "zh": zh})
    if r.status_code >= 400:
        raise HTTPException(502, {"en": "the AI service returned an error", "zh": "AI 服务这次出错了，请再试一次"})
    return r.json()


def _verdict(request: Request, run, passed: bool, note: str) -> None:
    if not run:
        return
    try:
        B._client().post(B.GATEWAY + f"/api/v1/cam/ai/runs/{int(run)}", json={"passed": passed, "note": note[:300]},
                         headers=_headers(request), timeout=20)
    except httpx.HTTPError:
        pass  # the record misses one verdict; the user's answer does not depend on it


# ------------------------------------------------------------------------------------------------ the cam(s)


def _target(p: dict, cam_id: str):
    """(follower kind, function that puts a program into a copy of the project, function that runs the checks)."""
    if p.get("kind") == "system" or "cams" in p:
        from camkit import system as S
        c = next((c for c in p.get("cams") or [] if c.get("id") == cam_id), None)
        if c is None:
            raise HTTPException(400, {"en": "no such cam in the system", "zh": "系统里没有这个凸轮"})
        if c.get("type") == "globoidal":
            follower = "indexing"
        else:
            follower = (c.get("cylindrical" if c.get("type") == "cylindrical" else "mechanism") or {}).get(
                "follower") or "translating"

        def put(prog):
            q = copy.deepcopy(p)
            next(x for x in q["cams"] if x.get("id") == cam_id)["program"] = prog
            return q
        return follower, put, lambda q: S.analyse(q, quick=True)
    follower = (p.get("cylindrical" if p.get("type") == "cylindrical" else "mechanism") or {}).get(
        "follower") or "translating"

    def put1(prog):
        q = copy.deepcopy(p)
        q["program"] = prog
        return q
    return follower, put1, analyse_cam


def _checks(res: dict, lang: str) -> list[dict]:
    """The checks as the model sees them: id, name, status, value, limit, unit, note (system and each cam)."""
    out = []

    def add(group, cs):
        for c in cs or []:
            name = c.get("zh") if lang == "zh" else c.get("en")
            note = c.get("note_zh") if lang == "zh" and c.get("note_zh") else c.get("note")
            v, lim = c.get("value"), c.get("limit")
            out.append({"group": group, "id": c.get("id"), "name": name, "status": c.get("status"),
                        "value": round(v, 4) if isinstance(v, float) else v,
                        "limit": round(lim, 4) if isinstance(lim, float) else lim, "unit": c.get("unit"),
                        "note": note})
    add("", res.get("checks"))
    for c in res.get("cams") or []:
        add(c.get("id"), (c.get("result") or {}).get("checks") or c.get("checks"))
    return out


def _numbers(x) -> list[float]:
    if isinstance(x, bool):
        return []
    if isinstance(x, (int, float)):
        return [float(x)]
    if isinstance(x, dict):
        return [v for y in x.values() for v in _numbers(y)]
    if isinstance(x, list):
        return [v for y in x for v in _numbers(y)]
    return []


def _summary(p: dict) -> dict:
    keep = ("program", "mechanism", "loads", "globoidal", "cylindrical", "camshaft", "output", "drive")
    if p.get("kind") == "system" or "cams" in p:
        return {"camshaft": p.get("camshaft"), "drive": p.get("drive"),
                "cams": [{k: c.get(k) for k in ("id", "type", *keep) if c.get(k) is not None} for c in p["cams"]]}
    if p.get("type") == "cylindrical":  # round 39 step 8: the disk fields the page also keeps are not this cam's
        keep = tuple(k for k in keep if k != "mechanism")
    return {k: p.get(k) for k in (("type",) + keep) if p.get(k) is not None}


# ------------------------------------------------------------------------------------------------ endpoints


def draft(request: Request, body: dict) -> dict:
    p, sentence = body.get("project") or {}, str(body.get("sentence") or "").strip()
    lang = "en" if body.get("lang") == "en" else "zh"
    if len(sentence) < 2:
        raise HTTPException(400, {"en": "write the requirement in a sentence", "zh": "请用一句话写出要求"})
    follower, put, run = _target(p, str(body.get("cam") or ""))
    g = gateway(request, "/draft", {"sentence": sentence[:600], "follower": follower, "laws": list(LAWS),
                                    "lang": lang})
    d = g.get("draft") or {}
    chk = AC.program_from_draft(d, follower, sentence)
    res = None
    if chk["usable"]:
        try:
            res = run(put(chk["program"]))
        except ValueError as e:  # the cam cannot be built with this program and the current mechanism
            chk["error"], chk["usable"] = str(e), False
    note = chk["error"] or ("missing " + json.dumps(chk["missing"]) if chk["missing"] else "")
    _verdict(request, g.get("run"), chk["usable"], note + (" cleared " + json.dumps(chk["cleared"]) if chk["cleared"]
                                                           else ""))
    return {"follower": follower, "check": chk, "assumptions": d.get("assumptions") or [],
            "questions": d.get("questions") or [], "checks": _checks(res, lang) if res else None,
            "left_today": g.get("left_today"), "model": g.get("model")}


def text(request: Request, body: dict, kind: str) -> dict:
    p = body.get("project") or {}
    lang = "en" if body.get("lang") == "en" else "zh"
    if p.get("kind") == "system" or "cams" in p:
        from camkit import system as S
        res = S.analyse(p)
    else:
        res = analyse_cam(p)
    checks = _checks(res, lang)
    summ = _summary(p)
    title = ((p.get("title") or {}).get(lang) or (p.get("title") or {}).get("en") or "")[:200]
    g = gateway(request, "/" + kind, {"title": title, "summary": summ, "checks": checks, "lang": lang})
    kept, dropped = AC.keep_supported([str(s) for s in g.get("sentences") or []],
                                      AC.result_numbers(checks, _numbers(summ)))
    _verdict(request, g.get("run"), not dropped, f"dropped {len(dropped)} sentence(s)" if dropped else "")
    return {"sentences": kept, "dropped": len(dropped), "left_today": g.get("left_today"), "model": g.get("model")}


def register(app, run, max_body):
    async def body_of(request: Request) -> dict:
        raw = await request.body()
        if len(raw) > max_body:
            raise HTTPException(413, {"en": "the project is too large", "zh": "项目太大"})
        try:
            d = json.loads(raw or b"{}")
        except ValueError as exc:
            raise HTTPException(400, {"en": "not JSON", "zh": "不是 JSON"}) from exc
        if not isinstance(d, dict):
            raise HTTPException(400, {"en": "not an object", "zh": "格式不对"})
        return d

    @app.post("/api/ai/draft")
    async def draft_ep(request: Request):
        body = await body_of(request)
        return run(lambda: draft(request, body))

    @app.post("/api/ai/explain")
    async def explain_ep(request: Request):
        body = await body_of(request)
        return run(lambda: text(request, body, "explain"))

    @app.post("/api/ai/describe")
    async def describe_ep(request: Request):
        body = await body_of(request)
        return run(lambda: text(request, body, "describe"))
