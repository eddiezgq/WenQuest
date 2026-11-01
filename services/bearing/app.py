"""问渠轴承 web service (第 64 轮第 2 步): the bearingkit kernel behind a small JSON API, and the built web app
(apps/bearing) as static files. Served at /bearing/ on the academy domain (Caddy strips the prefix). No sign-in yet:
projects stay in the browser. No AI, no network: it only computes.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from bearingkit.analyze import analyse

HERE = Path(__file__).parent
EXAMPLES = HERE / "examples"
WEB = Path(os.environ.get("BEARING_WEB_DIR", HERE / "web"))
MAX_BODY = 256 * 1024

ERR_ZH = [  # kernel messages in Chinese (patterns over the English text)
    (r"^a deep groove bearing with preload", "深沟球轴承预紧：请改填接触角"),
    (r"^give the axial force on the side", "轴向力要加在接触角承受的一侧（Fa ≥ 0）"),
    (r"^give the ball diameter Dw and the number of balls Z$", "请填钢球直径 Dw 和球数 Z"),
    (r"^give the ball diameter, the number of balls", "请填钢球直径、球数（至少 3 个），节圆直径要大于球径"),
    (r"^give the bore d, the outside diameter D", "请填内径 d、外径 D（大于 d）和宽度 B"),
    (r"^give the contact angle of the angular contact bearing", "请填角接触球轴承的接触角（0° 到 60° 之间）"),
    (r"^give the groove radius ratios", "请填沟曲率半径系数 f_i 和 f_o（沟道半径 / 钢球直径）"),
    (r"^groove radius ratios f_i, f_o are between 0.5 and 0.6$", "沟曲率半径系数 f_i、f_o 要在 0.5 到 0.6 之间"),
    (r"^numbers must be finite$", "数值必须是有限数"),
    (r"^the balls do not fit round the pitch circle", "节圆上放不下这么多钢球（Z·Dw ≥ π·dm）"),
    (r"^the bearing type is deep_groove or angular", "本版支持深沟球和角接触球轴承（滚子轴承在第 3 步）"),
    (
        r"^the load distribution did not converge",
        "载荷分布算不出来：载荷可能超出这个游隙下轴承的承载，或力矩没有轴向支承",
    ),
    (r"^the shoulder height is above zero and below the groove radius$", "挡肩高度要大于 0、小于沟道半径"),
    (r"^the bodies do not form a contact", "几何不成立：接触曲率和不大于 0"),
]


def zh(msg: str) -> str:
    for pat, rep in ERR_ZH:
        if re.search(pat, msg):
            return re.sub(pat, rep, msg)
    return msg


def clean(x):
    """JSON cannot carry inf / nan: they become null (unknown) or the string "inf"."""
    if isinstance(x, float):
        return "inf" if x == float("inf") else None if x != x else x
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [clean(v) for v in x]
    if isinstance(x, np.generic):
        return clean(x.item())
    return x


app = FastAPI(title="WenQuest Bearing", docs_url=None, redoc_url=None, openapi_url=None)


async def project_of(request: Request) -> dict:
    raw = await request.body()
    if len(raw) > MAX_BODY:
        raise HTTPException(413, {"en": "the project is too large", "zh": "项目太大"})
    try:
        d = json.loads(raw or b"{}")
    except ValueError as exc:
        raise HTTPException(400, {"en": "not JSON", "zh": "不是 JSON"}) from exc
    if not isinstance(d, dict):
        raise HTTPException(400, {"en": "a project is an object", "zh": "项目格式不对"})
    p = d.get("project", d)
    if not isinstance(p, dict):
        raise HTTPException(400, {"en": "a project is an object", "zh": "项目格式不对"})
    return p


def run(fn):
    try:
        return JSONResponse(clean(fn()))
    except (ValueError, TypeError, AttributeError) as exc:
        msg = str(exc)
        raise HTTPException(422, {"en": msg, "zh": zh(msg)}) from exc


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/examples")
def examples():
    out = []
    for f in sorted(EXAMPLES.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        out.append({"id": f.stem, "title": d.get("title", {"zh": f.stem, "en": f.stem}), "type": d.get("type")})
    return out


@app.get("/api/examples/{eid}")
def example(eid: str):
    if not re.fullmatch(r"[a-z0-9-]{1,60}", eid) or not (EXAMPLES / f"{eid}.json").is_file():
        raise HTTPException(404, {"en": "no such example", "zh": "没有这个示例"})
    return json.loads((EXAMPLES / f"{eid}.json").read_text(encoding="utf-8"))


@app.post("/api/analyse")
async def analyse_ep(request: Request):
    p = await project_of(request)
    return run(lambda: analyse(p))


if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
