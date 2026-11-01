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
    (
        r"^the bearing type is deep_groove, angular, cylindrical or tapered$",
        "轴承类型是深沟球、角接触球、圆柱滚子或圆锥滚子轴承",
    ),
    # tapered roller bearings (step 4 part 2)
    (r"^give the cup angle and the cone angle", "请填圆锥滚子轴承的外圈（杯）角和内圈（锥）角"),
    (r"^the cone angle is above 0 and below the cup angle", "内圈（锥）角要大于 0、小于外圈（杯）角，杯角小于 45°"),
    (r"^the rib cannot hold the roller", "按这些角度，挡边托不住滚子：请检查杯角、锥角和挡边方向"),
    (
        r"^a single tapered roller bearing needs an axial force",
        "单列圆锥滚子轴承受径向力时要有轴向力（只有径向力会把内圈推出）：请填轴向力，或配对使用（第 4 步之三）",
    ),
    (
        r"^the load distribution did not converge \(the radial load may be too large",
        "载荷分布算不出来：对这个轴向力，单列轴承的径向力可能太大",
    ),
    # cylindrical roller bearings (step 4)
    (r"^give the roller diameter Dw, its length", "请填滚子直径 Dw、滚子长度 Lw、有效接触长度 Lwe 和滚子数 Z"),
    (r"^the effective contact length is not longer", "有效接触长度不能大于滚子长度"),
    (r"^give the roller diameter and length", "请填滚子直径和长度、滚子数（至少 3 个），节圆直径要大于滚子直径"),
    (r"^the clearance of a cylindrical roller bearing", "圆柱滚子轴承的游隙要 ≥ 0"),
    (r"^the rollers do not fit round the pitch circle", "节圆上放不下这么多滚子（Z·Dw ≥ π·dm）"),
    (r"^the roller profile is", "滚子素线是直线、圆弧、直线加圆弧或点表"),
    (r"^give the crown radius", "请填凸度圆弧半径（要大于滚子长度的一半）"),
    (r"^the flat middle is shorter", "中间直线段要短于滚子"),
    (r"^give at least two points of the crown profile", "凸度点表至少要两个点"),
    (r"^give a radial force \(cylindrical", "圆柱滚子轴承承受径向载荷：请填径向力"),
    (
        r"^the load distribution did not converge",
        "载荷分布算不出来：载荷可能超出这个游隙下轴承的承载，或力矩没有轴向支承",
    ),
    (r"^the shoulder height is above zero and below the groove radius$", "挡肩高度要大于 0、小于沟道半径"),
    (r"^the bodies do not form a contact", "几何不成立：接触曲率和不大于 0"),
    # application scenarios (step 3)
    (r"^scenario: give (\w+)$", r"应用场景：请填 \1"),
    (r"^scenario: the bearing span L is more than 0$", "应用场景：两轴承跨距 L 要大于 0"),
    (r"^scenario: give at least one operating case$", "应用场景：至少要有一个工况"),
    (r"^scenario: the time shares add up to more than 0$", "应用场景：各工况时间占比之和要大于 0"),
    (r"^scenario: each case has a power", "应用场景：每个工况的功率 ≥ 0、转速 > 0"),
    (r"^scenario: gear module", "应用场景：齿轮模数、齿数、压力角（0–45°）、螺旋角（0–45°）"),
    (r"^scenario: rotor mass", "应用场景：转子质量 ≥ 0、不平衡量 ≥ 0、转速 > 0"),
    (r"^scenario: at least 4 lines", "应用场景：力表至少 4 行，每行：转角, Fx, Fy（可加 Fz）"),
    (r"^scenario: each line of the table", "应用场景：力表每行是 转角, Fx, Fy（可加 Fz）"),
    (r"^scenario: unknown kind (.*)$", r"应用场景：没有这种场景（\1）"),
    (r"^scenario: this bearing is A or B$", "应用场景：本轴承是 A 或 B"),
    (r"^scenario: the row is outboard or inboard$", "应用场景：轴承排是外排或内排"),
    (r"^scenario: the joint axis is horizontal or vertical$", "应用场景：关节轴线是水平或竖直"),
]


SCN_ZH = {  # scenario field names in the Chinese messages
    "mn": "法向模数 mn",
    "z": "齿数 z",
    "alpha_n_deg": "法向压力角 αn",
    "x": "载荷位置 x",
    "L": "两轴承跨距 L",
    "P": "功率 P",
    "n": "转速 n",
    "m": "转子质量 m",
    "a": "悬伸 a",
    "Fr": "径向力",
    "W": "载荷 W",
    "ay": "侧向加速度 ay",
    "R": "车轮滚动半径 R",
    "r": "力臂 r",
}


def zh(msg: str) -> str:
    m = re.fullmatch(r"scenario: give (\w+)", msg)
    if m:
        return "应用场景：请填" + SCN_ZH.get(m.group(1), m.group(1))
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
