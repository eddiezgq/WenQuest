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
from camkit import measure as ME
from camkit import mfg as MF
from camkit import step as ST
from camkit.disk import GeometryError
from camkit.laws import LAWS, coefficients
from camkit.program import ProgramError

HERE = Path(__file__).parent
EXAMPLES = HERE / "examples"
WEB = Path(os.environ.get("CAM_WEB_DIR", HERE / "web"))
MAX_BODY = 4 * 1024 * 1024  # a measured point cloud can be a few MB

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
    # manufacturing and measurement (step 3)
    (r"^the process is grinding, milling or wire EDM$", "加工方式是磨削、铣削或慢走丝"),
    (r"^the chord tolerance is between", "弦高公差在 0.00001 到 0.1 mm 之间"),
    (r"^give the tool radius", "请填刀具半径（砂轮或铣刀）"),
    (r"^the tool is wider than the groove", "刀具比槽宽：刀具半径不能大于滚子半径"),
    (r"^give the milling depth", "请填铣削深度（或接触宽度）"),
    (r"^the depth per pass is more than 0$", "每层切深要大于 0"),
    (r"^the program has no cutting moves$", "程序里没有切削段"),
    (r"^the cam outline has a point that does not move", "凸轮廓线有尖点，不能加工"),
    (r"^the table step divides 360°$", "点表步距要能整除 360°"),
    (r"^give the thickness", "请填厚度（接触宽度）才能出三维模型"),
    (r"^give the blank radius and plate thickness", "槽凸轮出三维模型要填毛坯半径和盘厚"),
    (r"^the plate must be thicker than the groove depth$", "盘厚要大于槽深"),
    (r"^the blank radius must be larger", "毛坯半径要大于槽外侧壁"),
    (r"^the measurement needs at least 36 rows", "测量数据至少要 36 行，每行两个数"),
    (r"^cam angles in degrees, within one turn$", "转角用度，在一圈之内"),
    (r"^the measurement must cover the whole turn$", "测量数据要覆盖整圈"),
    (r"^the measurement is a lift table or profile points$", "测量数据是升程表或廓线 XY 点"),
    (r"^the low orders end between", "低阶的上限要在 2 和最高阶数之间"),
    (r"^profile points need a cam outline", "用 XY 点时，凸轮廓线要能被从中心出发的每条射线只穿过一次"),
    (r"^choose orders between 1 and the highest order$", "补偿阶次要在 1 和最高阶数之间"),
    (r"^give the actual wheel radius$", "请填修整后的实际砂轮半径"),
    (r"^a disk cam brings its follower back", "盘形凸轮每转一圈从动件都回到原位：净分度的运动程序要用弧面分度凸轮"),
    (r"^the net movement over a cycle differs from the index advance by (.*)$", r"一个循环的净转角与分度角相差 \1"),
    (r"^the tool centre path is not star-shaped", "刀心轨迹对凸轮中心不是星形，X–C 磨削走不了，请改用铣削或小砂轮"),
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
        if f.name.endswith(".cae.json"):
            continue  # an example's precomputed CAE results (round 39, step 4)
        d = json.loads(f.read_text(encoding="utf-8"))
        out.append({"id": f.stem, "title": d.get("title", {"zh": f.stem, "en": f.stem}), "kind": d.get("kind", "cam")})
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


# --------------------------------------------------------------------------------------- step 3: manufacturing


def _mfg_of(p: dict) -> dict:
    return dict(p.get("mfg") or {})


def _thin(a, n):
    a = np.asarray(a)
    step = max(1, a.shape[-1] // n)
    return a[..., ::step]


def _scale(unit: str) -> float:
    return 1e3 if unit == "mm" else 1e6  # µm or µrad for the error curves


def manufacture_view(p: dict) -> dict:
    out = MF.manufacture(p, _mfg_of(p))
    return _mfg_json(out)


def _mfg_json(out: dict) -> dict:
    sim = out.get("sim")
    paths = []
    for ph in out["paths"]:
        d = {"name": ph["name"], "points": ph["points"], "tool": _thin(ph["Q"], 1440).round(4).tolist()}
        if "xc" in ph:
            X, C = ph["xc"]
            d["xc"] = [np.round(X, 5).tolist(), np.round(C, 5).tolist()]
        paths.append(d)
    res = {
        "checks": out["checks"],
        "program": out["program"],
        "process": out["settings"]["process"],
        "tool_r": out["settings"]["tool_r"],
        "surfaces": [{"name": sf.name, "zh": sf.zh, "xy": _thin(sf.P, 1440).round(4).tolist()}
                     for sf in out["surfaces"]],
        "paths": paths,
    }
    if sim is not None:
        res["sim"] = {
            "deg": _thin(sim["deg"], 720).round(2).tolist(),
            "flanks": [{"name": f["name"], "dev_um": (_thin(f["dev"], 720) * 1e3).round(4).tolist()}
                       for f in sim["flanks"]],
            "over": out["over"],
            "under": out["under"],
        }
    return res


def export_file(p: dict, kind: str) -> dict:
    title = (p.get("title") or {}).get("en") or "cam"
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", title).strip("_")[:40] or "cam"
    st = _mfg_of(p)
    if kind == "nc":
        out = MF.manufacture(p, st)
        if not out["program"]:
            raise ValueError(next((c["note"] for c in out["checks"] if c["status"] == "fail"), "no program"))
        return {"name": f"{base}.nc", "mime": "text/plain", "text": out["program"]}
    if kind == "dxf":
        _, _, sfs, _ = MF.design(p)
        return {"name": f"{base}.dxf", "mime": "application/dxf",
                "text": MF.dxf(sfs, float(st.get("chord_tol") or MF.DEFAULTS["chord_tol"]))}
    if kind == "csv":
        text = MF.point_table(p, float(st.get("table_step") or 0.5))
        return {"name": f"{base}-points.csv", "mime": "text/csv", "text": text}
    if kind == "step":
        m, _, sfs, _ = MF.design(p)
        blank = st.get("blank") or {}
        num = lambda v: None if v in (None, "") else float(v)  # noqa: E731
        text, rep = ST.solid(base, sfs[0].P, m.width, sfs[1].P if m.groove else None, num(blank.get("radius")),
                             num(blank.get("plate")))
        return {"name": f"{base}.step", "mime": "application/step", "text": text, "report": rep}
    raise HTTPException(404, {"en": "no such export", "zh": "没有这种导出"})


def measure_view(p: dict) -> dict:
    r = ME.measure(p, p.get("measure") or {})
    return _meas_json(r)


def _meas_json(r: dict) -> dict:
    k = _scale(r["unit"])
    h = r["harm"]
    return {
        "unit": r["unit"],
        "err_unit": "µm" if r["unit"] == "mm" else "µrad",
        "shift_deg": r["shift_deg"],
        "offset": r["offset"] * k,
        "deg": _thin(r["deg"], 720).round(2).tolist(),
        "e": (_thin(r["e"], 720) * k).round(4).tolist(),
        "acc": None if r["acc"] is None else _thin(r["acc"], 720).round(5).tolist(),
        "acc_unit": "m/s²" if r["unit"] == "mm" else "rad/s²",
        "harm": {"k": h["k"].tolist(), "A": (h["A"] * k).round(5).tolist(),
                 "phase_deg": np.degrees(h["phase"]).round(2).tolist()},
        "groups": {g: v * k for g, v in r["groups"].items()},
        "low_hi": r["low_hi"],
        "allow_k": None if r["allow_k"] is None else (np.asarray(r["allow_k"]) * k).round(5).tolist(),
        "rpm": r["rpm"],
        "checks": r["checks"],
    }


def compensate_view(p: dict) -> dict:
    meas = p.get("measure") or {}
    comp = meas.get("comp") or {}
    lo, hi = int(comp.get("lo") or 1), int(comp.get("hi") or 6)
    c = ME.compensate(p, meas, _mfg_of(p), lo, hi)
    k = _scale(c["measure"]["unit"])
    return {
        "measure": _meas_json(c["measure"]),
        "mfg": _mfg_json(c["mfg"]),
        "remaining": (_thin(c["remaining"], 720) * k).round(4).tolist(),
        "selected": (_thin(c["e_sel"], 720) * k).round(4).tolist(),
        "after_A": (c["harm_after"]["A"] * k).round(5).tolist(),
        "lo": lo,
        "hi": hi,
        "rms_before": float(np.sqrt(np.mean(c["measure"]["e"] ** 2)) * k),
        "rms_after": float(np.sqrt(np.mean(c["remaining"] ** 2)) * k),
    }


def wheel_view(p: dict) -> dict:
    st = _mfg_of(p)
    r = ME.wheel_error(p, st, MF._num(st.get("r_actual")))
    k = _scale("mm")
    return {"deg": np.round(r["deg"], 2).tolist(), "dn_um": (r["dn"] * k).round(4).tolist(),
            "lift": (r["lift"] * (_scale("rad") if r["mfg"]["mechanism"].follower == "oscillating" else k)).round(4)
            .tolist(), "max_dn_um": r["max_dn"] * k}


@app.post("/api/manufacture")
async def manufacture_ep(request: Request):
    p = await project_of(request)
    return run(lambda: manufacture_view(p))


@app.post("/api/export/{kind}")
async def export_ep(kind: str, request: Request):
    p = await project_of(request)
    return run(lambda: export_file(p, kind))


@app.post("/api/measure")
async def measure_ep(request: Request):
    p = await project_of(request)
    return run(lambda: measure_view(p))


@app.post("/api/compensate")
async def compensate_ep(request: Request):
    p = await project_of(request)
    return run(lambda: compensate_view(p))


@app.post("/api/wheel-error")
async def wheel_ep(request: Request):
    p = await project_of(request)
    return run(lambda: wheel_view(p))


@app.post("/api/synthetic")
async def synthetic_ep(request: Request):
    p = await project_of(request)
    return run(lambda: {"text": ME.synthetic(p)})


# --------------------------------------------------------------------------------------- step 5: FreeCAD

FREECAD = HERE / "freecad"
def workbench_dirs(here: Path) -> list[Path]:
    """Where the workbench files are: in the image /srv/freecad/workbench (copied there by the Dockerfile); in the
    repository factory/digital/freecad/Mod/WenQuest. The image's /srv has no grandparent, so look it up safely."""
    out = [here / "freecad" / "workbench"]
    if len(here.parents) >= 2:
        out.append(here.parents[1] / "factory" / "digital" / "freecad" / "Mod" / "WenQuest")
    return out


WORKBENCH = workbench_dirs(HERE)
FREECAD_README = """问渠凸轮 · FreeCAD 工作台（第 39 轮第 5 步）

1. 安装 FreeCAD 1.1（https://www.freecad.org/downloads.php）。
2. 把本压缩包里的 Mod\\WenQuest 文件夹复制到 FreeCAD 的用户 Mod 目录，重启 FreeCAD：
   Windows：%APPDATA%\\FreeCAD\\Mod；macOS：~/Library/Application Support/FreeCAD/Mod；Linux：~/.local/share/FreeCAD/Mod
   （已装过问渠数字工厂的宏包也没关系：解压到同一个 WenQuest 文件夹，两边的按钮都在。）
3. 工作台列表里选“问渠”，点“凸轮”，选网页版存的项目文件（.wqcam.json；文件夹 examples 里有示例）。
4. 软件重算校核（与网页版同一个计算内核，结果逐项相同），建出零件：盘形 / 槽凸轮、弧面分度凸轮的精确实体、换刀臂；
   凸轮系统按时序装配：在模型树里选“凸轮系统”，改“转角”，转塔、换刀臂按时序动。
5. 导出：零件 STEP、加工程序、每个零件一张 A3 工作图（SVG，技术要求留给工程师填）。
   不开界面也行：在 FreeCAD 的 Python 控制台里
   import wq_cam; wq_cam.run_headless("项目.wqcam.json", "输出文件夹")

需要 Python 包 numpy、scipy、shapely：FreeCAD 自带 numpy；缺的时候点“凸轮”会提示安装命令。
弧面凸轮建模约一分钟。计算全在本机，不连网。
"""


def freecad_pack() -> bytes:
    import io
    import zipfile

    wb = next((d for d in WORKBENCH if (d / "wq_workbench.py").is_file()), None)
    if wb is None:
        raise HTTPException(404, {"en": "the FreeCAD workbench is not in this build",
                                  "zh": "这个版本里没有 FreeCAD 工作台"})
    buf = io.BytesIO()
    root = "wenquest-cam-freecad/Mod/WenQuest/"
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ("InitGui.py", "wq_workbench.py"):
            z.write(wb / f, root + f)
        for f in sorted(FREECAD.glob("*.py")):
            z.write(f, root + f.name)
        for f in sorted((HERE / "camkit").glob("*.py")):
            z.write(f, root + "camkit/" + f.name)
        for f in sorted(EXAMPLES.glob("*.json")):
            if not f.name.endswith(".cae.json"):
                z.write(f, root + "examples/" + f.stem + ".wqcam.json")
        z.writestr("wenquest-cam-freecad/使用说明.txt", FREECAD_README)
    return buf.getvalue()


@app.get("/api/freecad.zip")
def freecad_zip():
    from fastapi.responses import Response

    return Response(freecad_pack(), media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=wenquest-cam-freecad.zip"})


import system_api  # noqa: E402  (cam systems, round 39 step 4)

system_api.register(app, run, project_of)

import ai_api  # noqa: E402  (AI drafting, round 39 step 6)

ai_api.register(app, run, MAX_BODY)

import projects_api  # noqa: E402  (cloud projects, round 39 step 7)

projects_api.register(app, MAX_BODY)

if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
