"""AI drafting in the bearing service (round 64, step 7; plan section 十五). The model is called through the learning
platform's gateway (/api/v1/bearing/ai/*: activated companies only, daily limit, the record of every run, Claude in
the US and DeepSeek in China); here plain code checks what comes back (bearingkit.ai_check) and runs the bearing's
checks on a draft. Nothing is written into the project: the browser shows the draft and the user adopts it or not.
The same way as the cam software (services/cam/ai_api.py).
"""

from __future__ import annotations

import json

import httpx
from fastapi import HTTPException, Request

import projects_api as P
from bearingkit import ai_check as AC
from bearingkit.analyze import analyse

GW_ERRORS = {
    401: ("sign in to use AI drafting", "请先登录问渠账号，再用 AI 起草"),
    403: (
        "AI drafting is for activated company accounts; ask WenQuest to activate yours",
        "AI 起草给已开通的企业账号用，请联系问渠开通",
    ),
    429: ("today's AI drafts are used up", "今天的 AI 起草次数用完了，明天再来"),
    503: ("no AI model is set up on this server", "这台服务器还没有配置 AI 模型"),
}


def gateway(request: Request, path: str, body: dict) -> dict:
    h = P._headers(request)
    if not h:
        en, zh = GW_ERRORS[401]
        raise HTTPException(401, {"en": en, "zh": zh})
    try:
        r = P.client().post(P.GATEWAY + "/api/v1/bearing/ai" + path, json=body, headers=h, timeout=200)
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
        P.client().post(
            P.GATEWAY + f"/api/v1/bearing/ai/runs/{int(run)}",
            json={"passed": passed, "note": note[:300]},
            headers=P._headers(request),
            timeout=20,
        )
    except httpx.HTTPError:
        pass  # the record misses one verdict; the user's answer does not depend on it


def _checks(res: dict, lang: str) -> list[dict]:
    """The checks as the model sees them: id, name, status, value, limit, unit, note."""
    out = []
    for c in res.get("checks") or []:
        v, lim = c.get("value"), c.get("limit")
        out.append(
            {
                "id": c.get("id"),
                "name": c.get("zh") if lang == "zh" else c.get("en"),
                "status": c.get("status"),
                "value": round(v, 4) if isinstance(v, float) else v,
                "limit": round(lim, 4) if isinstance(lim, float) else lim,
                "unit": c.get("unit"),
                "note": (c.get("note_zh") if lang == "zh" else c.get("note")) or "",
            }
        )
    return out


def _summary(p: dict) -> dict:
    keep = (
        "type",
        "size",
        "inner",
        "pair",
        "profile",
        "alignment",
        "material",
        "scenario",
        "loads",
        "fits",
        "lube",
        "limits",
    )
    return {k: p.get(k) for k in keep if p.get(k) not in (None, {}, "")}


def draft(request: Request, body: dict, zh) -> dict:
    p, sentence = body.get("project") or {}, str(body.get("sentence") or "").strip()
    lang = "en" if body.get("lang") == "en" else "zh"
    if len(sentence) < 2:
        raise HTTPException(
            400, {"en": "write where the bearing is used in a sentence", "zh": "请用一句话写出轴承用在哪、受什么力"}
        )
    g = gateway(
        request,
        "/draft",
        {
            "sentence": sentence[:600],
            "kinds": AC.kind_fields(lang),
            "bearing": str(p.get("type") or "deep_groove"),
            "lang": lang,
        },
    )
    d = g.get("draft") or {}
    chk = AC.apply_draft(d, sentence, p, lang)
    res, err = None, chk["error"]
    if chk["usable"] and not chk["missing"]:
        try:
            res = analyse(chk["project"])
        except (ValueError, TypeError) as e:
            err = str(e)
    note = (err or "") + (" missing " + json.dumps([m["path"] for m in chk["missing"]]) if chk["missing"] else "")
    note += " cleared " + json.dumps(chk["cleared"], ensure_ascii=False) if chk["cleared"] else ""
    _verdict(request, g.get("run"), chk["usable"] and not chk["cleared"], note)
    return {
        "kind": chk["kind"],
        "scenario": (chk["project"] or {}).get("scenario"),
        "loads": (chk["project"] or {}).get("loads"),
        "values": chk["values"],
        "cleared": chk["cleared"],
        "dropped": chk["dropped"],
        "missing": chk["missing"],
        "usable": chk["usable"],
        "error": None if not err else {"en": err, "zh": zh(err)},
        "status": res.get("status") if res else None,
        "checks": _checks(res, lang) if res else None,
        "assumptions": d.get("assumptions") or [],
        "questions": d.get("questions") or [],
        "left_today": g.get("left_today"),
        "model": g.get("model"),
    }


def text(request: Request, body: dict, kind: str) -> dict:
    p = body.get("project") or {}
    lang = "en" if body.get("lang") == "en" else "zh"
    res = analyse(p)
    checks = _checks(res, lang)
    summ = _summary(p)
    title = ((p.get("title") or {}).get(lang) or (p.get("title") or {}).get("en") or "")[:200]
    g = gateway(request, "/" + kind, {"title": title, "summary": summ, "checks": checks, "lang": lang})
    vals = AC.numbers_in(checks) + AC.numbers_in(summ)
    kept, dropped = AC.keep_supported([str(s) for s in g.get("sentences") or []], vals)
    _verdict(request, g.get("run"), not dropped, f"dropped {len(dropped)} sentence(s)" if dropped else "")
    return {"sentences": kept, "dropped": len(dropped), "left_today": g.get("left_today"), "model": g.get("model")}


def register(app, run, project_of, zh) -> None:
    @app.post("/api/ai/draft")
    async def draft_ep(request: Request):
        body = await project_of(request)
        return run(lambda: draft(request, body, zh))

    @app.post("/api/ai/explain")
    async def explain_ep(request: Request):
        body = await project_of(request)
        return run(lambda: text(request, body, "explain"))

    @app.post("/api/ai/describe")
    async def describe_ep(request: Request):
        body = await project_of(request)
        return run(lambda: text(request, body, "describe"))
