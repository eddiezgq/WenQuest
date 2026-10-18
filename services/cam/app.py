"""问渠凸轮 web service (第 39 轮): the kernel behind a small JSON API, and the built web app (apps/cam) as static
files. Served at /cam/ on the academy domain (Caddy strips the prefix). No sign-in yet: the demo is open and projects
stay in the browser (step 7 adds accounts). No AI, no network: it only computes.
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

from camkit import analyse, min_base_radius
from camkit.disk import GeometryError
from camkit.laws import LAWS, coefficients
from camkit.program import ProgramError

HERE = Path(__file__).parent
EXAMPLES = HERE / "examples"
WEB = Path(os.environ.get("CAM_WEB_DIR", HERE / "web"))
MAX_BODY = 512 * 1024

ERR_ZH = [  # kernel messages in Chinese (patterns over the English text)
    (r"^segment (\d+): a (\w+) has a lift more than 0$", r"第 \1 段：升程或回程的行程要大于 0"),
    (r"^segment (\d+): its cam angle is more than 0°$", r"第 \1 段：凸轮转角要大于 0°"),
    (r"^segment (\d+): rise, dwell or return$", r"第 \1 段：类型是升、停或回"),
    (r"^segment (\d+): the follower would go below its lowest position$", r"第 \1 段：从动件会低于最低位置"),
    (r"^segment (\d+): unknown motion law (.*)$", r"第 \1 段：没有这种运动规律（\2）"),
    (r"^the segments add up to (.*)°, not 360°$", r"各段转角加起来是 \1°，不是 360°"),
    (
        r"^the follower does not come back to where it started: rises and returns differ by (.*)$",
        r"从动件转一圈回不到起点：升程与回程相差 \1",
    ),
    (r"^a program has at least one segment$", "运动程序至少要有一段"),
    (r"^a table needs at least 8 points", "点表至少要 8 个点，每个点有转角和位移"),
    (r"^table angles rise strictly", "点表的转角要在 0° 到 360° 之间逐个增大"),
    (r"^a groove cam drives a roller$", "槽凸轮只能配滚子"),
    (r"^an oscillating follower needs the centre distance$", "摆动从动件要填中心距"),
    (r"^an oscillating follower's program is in angle", "摆动从动件的运动程序用角度，直动的用毫米"),
    (r"^an oscillating roller or knife follower needs the arm length$", "摆动滚子或尖顶从动件要填摆杆长度"),
    (r"^give the allowed pressure angle or minimum radius", "求最小基圆前，先填许用压力角或最小曲率半径"),
    (r"^give the roller radius$", "请填滚子半径"),
    (r"^no base circle up to a very large radius meets the limits$", "基圆再大也满足不了这些限值，请改运动规律或限值"),
    (r"^the arm would swing past the line of centres$", "摆杆会摆过中心连线：摆角太大或中心距、摆杆长度不合适"),
    (r"^the base circle radius is more than 0$", "基圆半径要大于 0"),
    (r"^the flat face cannot touch the base circle", "平底够不到基圆：中心距太短"),
    (r"^the offset is larger than the base circle", "偏距比基圆（加滚子）还大"),
    (
        r"^with this centre distance and arm the roller cannot touch the base circle$",
        "这个中心距和摆杆长度下，滚子碰不到基圆",
    ),
    (r"^the face lines have no envelope here$", "平底包络在这里不存在：几何不成立"),
    (r"^the pitch curve has a point that does not move", "理论廓线退化：请检查参数"),
    (r"^unknown mechanism field: (.*)$", r"不认识的机构参数：\1"),
    (r"^numbers must be finite$", "数值必须是有限数"),
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


app = FastAPI(title="WenQuest Cam", docs_url=None, redoc_url=None, openapi_url=None)


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
    return d.get("project", d)


def run(fn):
    try:
        return JSONResponse(clean(fn()))
    except (ProgramError, GeometryError, ValueError, TypeError) as exc:
        msg = str(exc)
        raise HTTPException(422, {"en": msg, "zh": zh(msg)}) from exc


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/laws")
def laws():
    return [{"key": k, "zh": v.zh, "en": v.en, **coefficients(k)} for k, v in LAWS.items()]


@app.get("/api/examples")
def examples():
    out = []
    for f in sorted(EXAMPLES.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        out.append({"id": f.stem, "title": d.get("title", {"zh": f.stem, "en": f.stem})})
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


@app.post("/api/min-base-radius")
async def min_rb(request: Request):
    p = await project_of(request)
    return run(lambda: min_base_radius(p))


if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
