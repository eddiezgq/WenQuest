"""问渠电子 WenQuest Electronics（第 105 轮 P3）：起草台的服务。网址 <主域名>/eda/。

  GET  /api/health
  GET  /api/catalog              起草目录（规格字段、单元参数、范围、模板默认）
  POST /api/draft                {requirement, lang} → AI 起草（经网关）→ 代码校验 → 展开 → 计算器与仿真 → 结果
  POST /api/evaluate             {requirement, report, values} → 人改过的数 → 校验 → 展开 → 计算 → 结果（不调 AI）

模型只经网关调用（登录、限次、记录都在网关）；校验、展开、判定都由 wqeda 的确定性代码做。草稿不保存到服务器：
人确认后在浏览器里下载设计描述（YAML）。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("EDA_REPO", HERE.parent.parent))
sys.path.insert(0, str(REPO / "eda"))

from wqeda import parts  # noqa: E402
from wqeda.ai import catalog as cat  # noqa: E402
from wqeda.ai import draft as D  # noqa: E402

GATEWAY = os.environ.get("WQ_GATEWAY_URL", "http://gateway:8000").rstrip("/")
TEMPLATE_PATH = Path(os.environ.get("EDA_TEMPLATE", REPO / "factory" / "designs" / "drv-joint" / "design.yaml"))
WEB = Path(os.environ.get("EDA_WEB_DIR", HERE / "web"))
SIM = os.environ.get("EDA_SIM", "1") != "0"
MAX_BODY = 200_000

TEMPLATE = cat.load_template(TEMPLATE_PATH)
CATALOG = cat.build(TEMPLATE)
DEVICES = parts.Devices.load()

GW_ERRORS = {
    401: ("sign in to use AI drafting", "请先登录问渠账号，再用 AI 起草"),
    429: ("today's AI drafts are used up", "今天的 AI 起草次数用完了，明天再来"),
    503: ("no AI model is set up on this server", "这台服务器还没有配置 AI 模型"),
}

app = FastAPI(title="WenQuest Electronics", docs_url=None, redoc_url=None, openapi_url=None)


def _headers(request: Request) -> dict:
    return {k: request.headers[k] for k in ("cookie", "authorization") if request.headers.get(k)}


def _client() -> httpx.Client:
    return httpx.Client(timeout=200)


def gateway_model(request: Request):
    h = _headers(request)
    if not h:
        en, zh = GW_ERRORS[401]
        raise HTTPException(401, {"en": en, "zh": zh})

    def model(requirement, catalog, lang, feedback):
        body = {"requirement": requirement, "catalog": catalog, "lang": lang}
        if feedback:
            body["feedback"] = feedback
        try:
            with _client() as c:
                r = c.post(GATEWAY + "/api/v1/eda/ai/draft", json=body, headers=h)
        except httpx.HTTPError as e:
            raise HTTPException(502, {"en": "the AI service did not answer", "zh": "AI 服务没有响应"}) from e
        if r.status_code in GW_ERRORS:
            en, zh = GW_ERRORS[r.status_code]
            raise HTTPException(r.status_code, {"en": en, "zh": zh})
        if r.status_code != 200:
            raise HTTPException(502, {"en": "the AI service failed", "zh": "AI 服务出错"})
        j = r.json()
        return j.get("draft"), j.get("run")

    def verdict(run_id, passed, note):
        try:
            with _client() as c:
                c.post(GATEWAY + f"/api/v1/eda/ai/runs/{int(run_id)}", json={"passed": passed, "note": note[:300]},
                       headers=h)
        except httpx.HTTPError:
            pass

    return model, verdict


async def body_of(request: Request) -> dict:
    raw = await request.body()
    if len(raw) > MAX_BODY:
        raise HTTPException(413, {"en": "request too large", "zh": "请求太大"})
    try:
        j = json.loads(raw or b"{}")
    except ValueError as e:
        raise HTTPException(400, {"en": "not JSON", "zh": "不是 JSON"}) from e
    if not isinstance(j, dict):
        raise HTTPException(400, {"en": "not a JSON object", "zh": "不是 JSON 对象"})
    return j


def _requirement(j: dict) -> str:
    req = str(j.get("requirement") or "").strip()
    if not 4 <= len(req) <= 3000:
        raise HTTPException(400, {"en": "write the requirement in 4 to 3000 characters",
                                  "zh": "需求写 4 到 3000 个字"})
    return req


def _round(r: dict) -> dict:
    res = r["result"]
    return {"run": r["run"], "report": r["report"], "passed": r["passed"],
            "count": res["count"] if res else None, "fails": res["fails"] if res else None}


@app.get("/api/health")
def health():
    return {"ok": True, "template": TEMPLATE["name"], "units": len(CATALOG["units"]), "devices": len(DEVICES.entries)}


@app.get("/api/catalog")
def catalog():
    return CATALOG


@app.post("/api/draft")
async def draft(request: Request):
    j = await body_of(request)
    req = _requirement(j)
    lang = "en" if j.get("lang") == "en" else "zh"
    model, verdict = gateway_model(request)
    out = D.run(req, model, TEMPLATE, lang=lang, devices=DEVICES, sim=SIM)
    for r in out["rounds"]:
        if r["run"] is not None:
            rep = r["report"]
            note = "退回 {} 处；缺 {}；不通过 {}".format(len(rep["rejected"]), "、".join(rep["missing"]) or "无",
                                               len(r["result"]["fails"]) if r["result"] else "—")
            verdict(r["run"], r["passed"], note)
    f = out["final"]
    return {"rounds": [_round(r) for r in out["rounds"]], "report": f["report"], "result": f["result"],
            "requirement": req}


@app.post("/api/evaluate")
async def evaluate(request: Request):
    j = await body_of(request)
    req = str(j.get("requirement") or "")[:3000]
    rep, probs = D.merge_edits(j.get("report") or {}, j.get("values") or {}, CATALOG)
    prev = j.get("report") or {}
    rep["questions"] = [str(x)[:300] for x in prev.get("questions") or []][:20]
    rep["unsupported"] = [str(x)[:300] for x in prev.get("unsupported") or []][:20]
    rep["rejected"] = []
    if probs:
        raise HTTPException(400, {"en": "; ".join(probs), "zh": "；".join(probs)})
    doc = D.apply(TEMPLATE, rep, req, j.get("runs") or [])
    if doc is None:
        return {"report": rep, "result": None}
    return {"report": rep, "result": D.evaluate(doc, DEVICES, SIM)}


if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
