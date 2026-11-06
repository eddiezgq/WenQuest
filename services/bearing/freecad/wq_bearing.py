# -*- coding: utf-8 -*-
"""问渠轴承 · FreeCAD 页（第 64 轮第 6 步，细则第十四节）。

在 FreeCAD 里设计和校核轴承：完整参数表单（与网页版同一套字段、同一种项目文件 .wqbearing.json），
用与网页版同一个计算内核 bearingkit 重算校核；内圈、外圈、滚动体按同一剖面回转成精确实体，整套按节圆排好，
检查滚动体与套圈是否干涉；出零件工作图，读网页版存的工艺模板（.wqprocess.json）出每道磨削 / 超精的工序简图；
导出 STEP 和 SVG。bearingkit 放在本文件旁边（工作台文件夹里），离线可用，不连网，不调 AI。

用法：
  - 工作台“问渠”→“轴承”：打开表单，从头填或打开项目文件；“计算”“建模”“出图”“工序简图”。
  - 命令行（不开界面）：设环境变量 WQ_BEARING_PROJECT=项目.wqbearing.json、WQ_BEARING_OUT=输出文件夹，
    可加 WQ_BEARING_PROCESS=工艺模板.wqprocess.json，再运行 FreeCADCmd wq_bearing.py
需要 numpy、scipy（1.9 以上）。FreeCAD 自带 numpy；缺 scipy 时会提示安装命令。
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

NEEDS = ("numpy", "scipy")
STATUS_ZH = {"pass": "合格", "fail": "不合格", "unknown": "未知", "na": "不适用", "info": "计算值"}


def missing():
    """Python 包里还缺的，或 scipy 太旧（合套要 1.9 以上的整数规划）。"""
    out = []
    for m in NEEDS:
        try:
            mod = __import__(m)
        except ImportError:
            out.append(m)
            continue
        if m == "scipy":
            try:
                major, minor = (int(x) for x in mod.__version__.split(".")[:2])
            except ValueError:
                continue
            if (major, minor) < (1, 9):
                out.append("scipy>=1.9")
    return out


def install_hint(pkgs):
    return ("在 FreeCAD 的 Python 控制台里粘贴下面一行，回车，装完重启 FreeCAD：\n"
            "from freecad.utils import get_python_exe as py; import subprocess as sp; "
            "sp.run([py(), '-m', 'ensurepip', '--user']); "
            "sp.run([py(), '-m', 'pip', 'install', '--user', {}])\n"
            "（先补上 pip，已经有 pip 时这一步什么也不做；再装缺的包）"
            ).format(", ".join(repr(p) for p in pkgs))


def load(path):
    from bearingkit import fields as FL

    return FL.load(path)


def title(p, lang="zh"):
    t = p.get("title") or {}
    return t.get(lang) or t.get("en") or t.get("zh") or "bearing"


# ---------------------------------------------------------------------------------- 计算（与网页版同一套）


def analyse(p):
    """校核结果：与网页版接口 /api/analyse 同一个内核、同一组参数。"""
    from bearingkit.analyze import analyse as A

    return A(p)


def check_rows(res):
    """校核项展平成 (编号, 结论, 数值)，用于网页版与 FreeCAD 逐项对比和摘要。"""
    rows = []
    for c in res.get("checks") or []:
        v = c.get("value")
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            v = None if v is None else str(v)
        rows.append((c.get("id"), c.get("status"), v))
    return rows


def summary_text(p, res):
    lines = [
        "问渠轴承 · 校核摘要（FreeCAD）",
        title(p),
        "总结论：" + STATUS_ZH.get(res.get("status"), res.get("status")),
        "",
    ]
    for c in res.get("checks") or []:
        v = c.get("value")
        val = (
            ""
            if v is None
            else (
                " = {:.6g} {}".format(v, c.get("unit") or "").rstrip()
                if isinstance(v, (int, float)) and not isinstance(v, bool)
                else " = " + str(v)
            )
        )
        lines.append("[{}] {}{}".format(STATUS_ZH.get(c.get("status"), c.get("status")), c.get("zh"), val))
    lines += ["", "计算由确定性程序完成，未经 AI；许用值由用户填写，缺数据判为“未知”。"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------------- 实体


def _edge(Part, Vector, s):
    """剖面上的一段（r, z）→ XZ 平面里的一条边（x = r，z = 轴向）。"""
    a = Vector(s["a"][0], 0, s["a"][1])
    b = Vector(s["b"][0], 0, s["b"][1])
    if not s.get("arc"):
        return Part.LineSegment(a, b).toShape()
    rc, zc = s["arc"]["c"]
    rho = s["arc"]["rho"]
    a0 = math.atan2(s["a"][1] - zc, s["a"][0] - rc)
    a1 = math.atan2(s["b"][1] - zc, s["b"][0] - rc)
    if s["arc"]["ccw"] and a1 <= a0:
        a1 += 2 * math.pi
    if not s["arc"]["ccw"] and a1 >= a0:
        a1 -= 2 * math.pi
    am = (a0 + a1) / 2
    m = Vector(rc + rho * math.cos(am), 0, zc + rho * math.sin(am))
    return Part.Arc(a, m, b).toShape()


def revolve(Part, Vector, segs):
    """剖面（逆时针、首尾相接）绕 Z 轴转一整圈成实体。贴着轴线的那条边转出来退化，不影响实体。"""
    edges = [_edge(Part, Vector, s) for s in segs]
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    solid = face.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)
    if solid.ShapeType != "Solid":
        solids = solid.Solids
        solid = solids[0] if len(solids) == 1 else Part.makeSolid(solid)
    return solid


def element_placements(g, pr, FreeCAD):
    """滚动体在整套里的位置（与网页版 STEP 同一组坐标系）。"""
    from bearingkit import parts as PT

    out = []
    for f in PT._elements(g, pr):
        if pr["element_kind"] == "ball":
            out.append(FreeCAD.Placement(FreeCAD.Vector(*[float(v) for v in f]), FreeCAD.Rotation()))
            continue
        z = [float(v) for v in f.z]
        x = [float(v) for v in f.x]
        y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
        m = FreeCAD.Matrix(x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0)
        out.append(FreeCAD.Placement(FreeCAD.Vector(*[float(v) for v in f.o]), FreeCAD.Rotation(m)))
    return out


def shapes(p, FreeCAD, Part):
    """{'inner', 'outer', 'element'}（零件自己的坐标系）、滚动体的位置和网页版的解析体积。"""
    from bearingkit import parts as PT
    from bearingkit import step3d as S
    from bearingkit.analyze import geometry_of

    g = geometry_of(p)
    pr = PT.parts(g)
    V = FreeCAD.Vector
    out = {"inner": revolve(Part, V, pr["inner"]), "outer": revolve(Part, V, pr["outer"])}
    if pr["element_kind"] == "ball":
        out["element"] = Part.makeSphere(g["Dw"] / 2)
        vol_e = math.pi * g["Dw"] ** 3 / 6
    else:
        out["element"] = revolve(Part, V, pr["element"])
        vol_e = S.volume(pr["element"])
    vols = {"inner": S.volume(pr["inner"]), "outer": S.volume(pr["outer"]), "element": vol_e}
    return out, element_placements(g, pr, FreeCAD), vols, g


def interference(sh, places):
    """前两个滚动体（按对称，其余与它们之一相同；交叉滚子正反交替，所以看两个）与内、外圈求交的最大体积，mm³。"""
    out = {"inner": 0.0, "outer": 0.0}
    for pl in places[:2]:
        e = sh["element"].copy()
        e.Placement = pl
        out["inner"] = max(out["inner"], e.common(sh["inner"]).Volume)
        out["outer"] = max(out["outer"], e.common(sh["outer"]).Volume)
    return out


def build(doc, p, log=print):
    """在文档里建内圈、外圈、全部滚动体（按节圆排好），返回对象和说明。"""
    import FreeCAD
    import Part

    sh, places, vols, g = shapes(p, FreeCAD, Part)
    objs = {}
    for key, label in (("inner", "内圈"), ("outer", "外圈")):
        o = doc.addObject("Part::Feature", "Inner" if key == "inner" else "Outer")
        o.Label = label
        o.Shape = sh[key]
        objs[key] = o
    kind = "钢球" if g["type"] in ("deep_groove", "angular", "four_point") else "滚子"
    elems = []
    for j, pl in enumerate(places):
        o = doc.addObject("Part::Feature", "Element{:03d}".format(j + 1))
        o.Label = "{} {}".format(kind, j + 1)
        s = sh["element"].copy()
        s.Placement = pl
        o.Shape = s
        elems.append(o)
    grp = doc.addObject("App::DocumentObjectGroup", "Elements")
    grp.Label = "滚动体"
    for o in elems:
        grp.addObject(o)
    objs["elements"] = elems
    doc.recompute()
    notes = []
    for key in ("inner", "outer", "element"):
        got = sh[key].Volume
        notes.append(
            "{}：体积 {:.3f} mm³（解析 {:.3f}，相差 {:.2e}）".format(
                {"inner": "内圈", "outer": "外圈", "element": "单个滚动体"}[key],
                got,
                vols[key],
                abs(got - vols[key]) / vols[key],
            )
        )
    ov = interference(sh, places)
    notes.append("干涉检查：滚动体与内圈重叠 {:.4f} mm³，与外圈 {:.4f} mm³".format(ov["inner"], ov["outer"]))
    if g["type"] == "tapered" and max(ov.values()) > 0:
        notes.append("（圆锥滚子与滚道线接触相切，求交会留下极小的残差，不是干涉）")
    if p.get("type") == "flex":
        objs["mounted"] = build_mounted(doc, p, g)
        notes.append(
            "装配变形：真实尺寸，放在旁边（x 向偏移 1.5D）；套圈画成沟底壁厚的环（不含沟道和挡边），是形状示意"
        )
    return objs, notes, {"shapes": sh, "volumes": vols, "overlap": ov, "geometry": g}


def build_mounted(doc, p, g):
    """谐波柔性轴承装在凸轮上的形状（细则第十八节）：内圈随凸轮、外圈按计算的变形、钢球在最重的保持架位置。"""
    import FreeCAD
    import Part

    from bearingkit import flex_check as FC

    m = FC.deformed(p)
    V = FreeCAD.Vector
    off = 1.5 * g["D"]
    B = m["B"]

    def closed(pts):
        c = Part.BSplineCurve()
        c.interpolate([V(x + off, y, -B / 2) for x, y in pts], PeriodicFlag=True)
        return Part.Wire(c.toShape())

    grp = doc.addObject("App::DocumentObjectGroup", "Mounted")
    grp.Label = "装配变形（真实尺寸）"
    out = []
    for key, label in (("inner", "内圈（装在凸轮上）"), ("outer", "外圈（变形后）")):
        a, b = closed(m[key][0]), closed(m[key][1])
        face = Part.Face(b).cut(Part.Face(a))
        o = doc.addObject("Part::Feature", "Mounted" + key.capitalize())
        o.Label = label
        o.Shape = face.extrude(V(0, 0, B))
        grp.addObject(o)
        out.append(o)
    for j, (x, y) in enumerate(m["balls"]):
        o = doc.addObject("Part::Feature", "MountedBall{:03d}".format(j + 1))
        o.Label = "钢球 {}（装配变形）".format(j + 1)
        o.Shape = Part.makeSphere(m["Dw"] / 2, V(x + off, y, 0))
        grp.addObject(o)
        out.append(o)
    doc.recompute()
    return out


# ---------------------------------------------------------------------------------- 导出


def export(objs, p, outdir, process=None, log=print):
    """各零件 STEP（零件坐标系）、整套 STEP、零件工作图；给了工艺模板再出工序简图和工序尺寸表。"""
    import Part
    from bearingkit import drawing as D
    from bearingkit.analyze import geometry_of

    os.makedirs(outdir, exist_ok=True)
    files = []
    g = geometry_of(p)
    for key in ("inner", "outer"):
        path = os.path.join(outdir, "bearing-{}.step".format(key))
        objs[key].Shape.exportStep(path)
        files.append(path)
    if objs["elements"]:
        e = objs["elements"][0].Shape.copy()
        e.Placement = type(e.Placement)()
        path = os.path.join(outdir, "bearing-element.step")
        e.exportStep(path)
        files.append(path)
    comp = Part.makeCompound([objs["inner"].Shape, objs["outer"].Shape] + [o.Shape for o in objs["elements"]])
    path = os.path.join(outdir, "bearing.step")
    comp.exportStep(path)
    files.append(path)
    for which in ("inner", "outer", "element"):
        path = os.path.join(outdir, "{}-drawing.svg".format(which))
        with open(path, "w", encoding="utf-8") as f:
            f.write(D.part_sheet(g, which, title(p)))
        files.append(path)
    if process:
        files += process_sheets(g, p, process, outdir)
    return files


def process_sheets(g, p, process, outdir):
    """读工艺模板：与网页版“工艺”同一个内核倒推工序尺寸；每道磨削 / 超精一张工序简图。"""
    from bearingkit import drawing as D
    from bearingkit import process as PR

    res = PR.run(g, process)
    files = []
    for name, svg in D.sketches(g, res, title(p)):
        path = os.path.join(outdir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        files.append(path)
    path = os.path.join(outdir, "process.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=float)
    files.append(path)
    return files


# ---------------------------------------------------------------------------------- 命令行与界面


def run_headless(path, outdir, process_path=None):
    import FreeCAD

    miss = missing()
    if miss:
        raise SystemExit("缺少 Python 包：{}\n{}".format(", ".join(miss), install_hint(miss)))
    p = load(path)
    res = analyse(p)
    doc = FreeCAD.newDocument("WenQuestBearing")
    objs, notes, info = build(doc, p)
    process = None
    if process_path:
        with open(process_path, encoding="utf-8") as f:
            process = json.load(f)
    files = export(objs, p, outdir, process)
    doc.saveAs(os.path.join(outdir, "bearing.FCStd"))
    with open(os.path.join(outdir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary_text(p, res) + "\n\n" + "\n".join(notes) + "\n")
    with open(os.path.join(outdir, "checks.json"), "w", encoding="utf-8") as f:
        json.dump(check_rows(res), f, ensure_ascii=False)
    sh = info["shapes"]
    return {
        "status": res.get("status"),
        "notes": notes,
        "files": files,
        "valid": {k: bool(sh[k].isValid()) for k in ("inner", "outer", "element")},
        "volumes": {k: sh[k].Volume for k in ("inner", "outer", "element")},
        "analytic": info["volumes"],
        "overlap": info["overlap"],
        "elements": len(objs["elements"]),
    }


def run_dialog():
    from PySide import QtWidgets

    miss = missing()
    if miss:
        QtWidgets.QMessageBox.warning(
            None, "问渠轴承", "缺少 Python 包：{}\n\n{}".format(", ".join(miss), install_hint(miss))
        )
        return
    import wq_bearing_form

    wq_bearing_form.show()


if __name__ == "__main__" and os.environ.get("WQ_BEARING_PROJECT"):
    print(
        json.dumps(
            run_headless(
                os.environ["WQ_BEARING_PROJECT"],
                os.environ.get("WQ_BEARING_OUT") or "wq-bearing-out",
                os.environ.get("WQ_BEARING_PROCESS"),
            ),
            ensure_ascii=False,
            indent=1,
            default=float,
        )
    )
