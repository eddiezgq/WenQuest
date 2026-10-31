# -*- coding: utf-8 -*-
"""问渠凸轮 · FreeCAD 页（第 39 轮第 5 步，细则第十节）。

打开网页版存的项目（.wqcam.json，单个凸轮或凸轮系统），用与网页版同一个计算内核 camkit 重算校核，
在 FreeCAD 里建实体（盘形 / 槽凸轮、弧面分度凸轮的精确实体、换刀臂），凸轮系统按时序装配、可拖转角，
导出 STEP、加工程序和校核摘要。camkit 放在本文件旁边（工作台文件夹里），离线可用，不连网。

用法：
  - 工作台“问渠”→“凸轮”：选项目文件，建模、装配；改文档里“凸轮系统”对象的“转角”看各零件按时序动。
  - 命令行（不开界面）：设环境变量 WQ_CAM_PROJECT=项目.wqcam.json、WQ_CAM_OUT=输出文件夹，再运行 FreeCADCmd wq_cam.py
需要 numpy、scipy、shapely（换刀臂外形用）。FreeCAD 自带 numpy；缺 scipy 或 shapely 时会提示安装命令。
"""
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

NEEDS = ("numpy", "scipy", "shapely")


def missing():
    """Python 包里还缺的（FreeCAD 自带 numpy；scipy、shapely 可能要装）。"""
    out = []
    for m in NEEDS:
        try:
            __import__(m)
        except ImportError:
            out.append(m)
    return out


def install_hint(pkgs):
    return ("在 FreeCAD 的 Python 控制台里运行：\n"
            "import subprocess, sys; subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', {}])\n"
            "（Windows 版 FreeCAD 若 sys.executable 不是 python.exe，改用 FreeCAD 安装目录 bin 下的 python.exe）"
            ).format(", ".join(repr(p) for p in pkgs))


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_system(p):
    return p.get("kind") == "system" or "cams" in p


def title(p, lang="zh"):
    t = p.get("title") or {}
    return t.get(lang) or t.get("en") or t.get("zh") or "cam"


# ---------------------------------------------------------------------------------- 计算（与网页版同一套）


def analyse(p):
    """校核结果，与网页版接口 /api/analyse（单个凸轮）或 /api/system（凸轮系统）同一个内核、同一组参数。"""
    if is_system(p):
        from camkit import system as S
        return S.analyse(p)
    from camkit.analyze import analyse as A
    return A(p)


def check_rows(res):
    """校核项展平成 (组, 编号, 结论, 数值)，用于网页版与 FreeCAD 逐项对比和摘要。"""
    rows = []

    def add(group, checks):
        for c in checks or []:
            v = c.get("value")
            val = v if isinstance(v, (int, float)) or v is None else str(v)
            rows.append((group, c.get("id"), c.get("status"), val))

    add("system", res.get("checks"))
    for c in res.get("cams") or []:
        add(c.get("id"), (c.get("result") or {}).get("checks") or c.get("checks"))
    return rows


def summary_text(p, res):
    names = {"pass": "合格", "fail": "不合格", "unknown": "未知", "na": "不适用", "info": "—"}
    lines = ["问渠凸轮 · 校核摘要（FreeCAD）", title(p), ""]
    for group, cid, st, v in check_rows(res):
        val = "" if v is None else (" = {:.6g}".format(v) if isinstance(v, (int, float)) else " = " + v)
        lines.append("[{}] {} {}{}".format(group, cid, names.get(st, st), val))
    lines += ["", "计算由确定性程序完成，未经 AI；许用值由用户填写，缺数据判为“未知”。"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------------- 实体


def _read_step_text(Part, text, name):
    fd, path = tempfile.mkstemp(suffix=".step", prefix=name[:20])
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        return Part.read(path)
    finally:
        os.remove(path)


def disk_shape(Part, sub, name="cam"):
    """盘形 / 槽凸轮：与网页版“STEP”下载同一个实体（精确 B 样条廓线）。槽凸轮要项目里填了毛坯（mfg.blank）。"""
    from camkit import mfg as MF
    from camkit import step as ST
    m, _, sfs, _ = MF.design(sub)
    blank = ((sub.get("mfg") or {}).get("blank")) or {}
    num = lambda v: None if v in (None, "") else float(v)  # noqa: E731
    text, rep = ST.solid(name, sfs[0].P, m.width, sfs[1].P if m.groove else None, num(blank.get("radius")),
                         num(blank.get("plate")))
    return _read_step_text(Part, text, name), rep


def cam_shape(Part, sub, name):
    """盘形 / 槽凸轮实体和说明。槽凸轮没填毛坯（mfg.blank）时按槽外 10 mm、槽底下 10 mm 建一个示意件（不导出）。"""
    if (sub.get("mechanism") or {}).get("groove") and not ((sub.get("mfg") or {}).get("blank")):
        from camkit import mfg as MF
        from camkit import step as ST
        m, _, sfs, _ = MF.design(sub)
        rmax = float(max(math.hypot(x, y) for x, y in zip(*sfs[1].P, strict=True)))
        text, _ = ST.solid(name, sfs[0].P, m.width, sfs[1].P, rmax + 10, m.width + 10)
        note = "{}：项目里没填毛坯，按槽外 10 mm、槽底下 10 mm 示意，不导出".format(name)
        return _read_step_text(Part, text, name), True, note
    shape, rep = disk_shape(Part, sub, name)
    return shape, False, "{}：廓线拟合偏差 {:.1e} mm".format(name, max(rep["fit_dev"].values()))


def globoid_shape(Part, Vector, c, bore=0.0):
    from camkit import globoid_solid as GS
    from camkit import globoidal as G
    from camkit.program import Program
    g = G.globoid(c.get("globoidal"))
    return GS.build_part(g, Program.from_dict(c.get("program") or {}), Part, Vector, bore=bore)


def is_cyl(p):
    return (p or {}).get("type") == "cylindrical"


def cyl_shape(Part, Vector, sub):
    """圆柱凸轮（第 39 轮第 8 步）：按加工方法的精确实体，与 camkit.cyl_solid 的 OpenCASCADE 版同一组曲面。"""
    from camkit import cyl_solid as CS
    c, prog = CS.build(sub)
    shape, info = CS.build_part(c, prog, Part, Vector)
    if not info["valid"]:
        raise RuntimeError("圆柱凸轮实体检查不通过")
    return shape, "圆柱凸轮：槽侧面拟合偏差 {:.2f} µm（{} 个站位）".format(info["fit_err_um"], info["sites"])


def roller_shape(Part, Vector, sub):
    """滚子（真实尺寸，沿 x 轴，从滚子内端到外端；锥形的锥顶在凸轮轴线上）。"""
    from camkit import cyl_solid as CS
    c, _ = CS.build(sub)
    if c.roller == "cone":
        return Part.makeCone(c.k * c.x1, c.k * c.x2, c.b, Vector(c.x1, 0, 0), Vector(1, 0, 0))
    return Part.makeCylinder(c.rr, c.b, Vector(c.x1, 0, 0), Vector(1, 0, 0))


def arm_shape(Part, arm):
    from camkit import atc_arm as AR
    text, rep = AR.step(arm)
    return _read_step_text(Part, text, "atc-arm"), rep


def _sub_project(p, c):
    """系统里的一个盘形 / 槽凸轮，换成单个凸轮项目（与网页版系统计算里一样）。"""
    out = {"title": {"en": c.get("id") or "cam"}, "program": c.get("program"), "mechanism": c.get("mechanism"),
           "material": c.get("material"), "limits": c.get("limits"), "mfg": c.get("mfg") or {}}
    if is_cyl(c):
        out.update(type="cylindrical", cylindrical=c.get("cylindrical"))
    return out


# ---------------------------------------------------------------------------------- 文档、装配与转角


def build(doc, p, Part, Vector, Placement, Rotation, log=print):
    """在 FreeCAD 文档里建出项目的零件；凸轮系统再按网页版三维里的布置装配。返回 {名称: 对象} 和说明。"""
    objs, notes = {}, []
    if not is_system(p) and is_cyl(p):  # 圆柱凸轮：凸轮、滚子；“凸轮系统”对象的转角让凸轮转、滚子跟着走
        shape, note = cyl_shape(Part, Vector, p)
        o = doc.addObject("Part::Feature", "Cam")
        o.Shape = shape
        o.Label = title(p)
        objs["cam"] = o
        r = doc.addObject("Part::Feature", "Roller")
        r.Shape = roller_shape(Part, Vector, p)
        r.Label = "滚子"
        objs["roller"] = r
        notes.append(note)
        drv = doc.addObject("App::FeaturePython", "CamSystem")
        CamDriver(drv)
        drv.Label = "转角"
        drv.Project = json.dumps(p, ensure_ascii=False)
        objs["driver"] = drv
        doc.recompute()
        set_angle(doc, p, 0.0, Placement, Rotation, Vector)
        return objs, notes
    if not is_system(p):
        shape, sketch, note = cam_shape(Part, p, "cam")
        o = doc.addObject("Part::Feature", "Cam")
        o.Shape = shape
        o.Label = title(p) + ("（示意）" if sketch else "")
        objs["cam"] = o
        notes.append(note)
        doc.recompute()
        return objs, notes
    glob = next((c for c in p.get("cams") or [] if c.get("type") == "globoidal"), None)
    if glob:
        shape, info = globoid_shape(Part, Vector, glob)
        if not info["valid"]:
            raise RuntimeError("弧面凸轮实体检查不通过")
        o = doc.addObject("Part::Feature", "GloboidalCam")
        o.Shape = shape
        o.Label = glob.get("name", {}).get("zh") if isinstance(glob.get("name"), dict) else "弧面分度凸轮"
        objs[glob["id"]] = o
        notes.append("弧面凸轮：按 {} 次滚子通过切出槽，工作面拟合偏差 ≤ {:.2f} µm".format(
            len(info["grooves"]), max(gr["fit_err_um"] for gr in info["grooves"])))
        # 转塔与滚子（滚子按真实尺寸；转塔轮毂示意）
        from camkit import globoidal as G
        g = G.globoid(glob.get("globoidal"))
        parts = [Part.makeCylinder(g.rho1 - 4, 2 * g.rr + 12, Vector(0, -(g.rr + 6), 0), Vector(0, 1, 0))]
        for i in range(g.n):
            a = g.phase + 2 * math.pi * i / g.n
            u = Vector(math.cos(a), 0, math.sin(a))
            parts.append(Part.makeCylinder(g.rr, g.b, u * g.rho1, u))
        o = doc.addObject("Part::Feature", "Turret")
        o.Shape = Part.makeCompound(parts)
        o.Label = "转塔与滚子"
        objs["turret"] = o
    for c in p.get("cams") or []:
        if c.get("type") == "globoidal":
            continue
        if is_cyl(c):
            shape, note = cyl_shape(Part, Vector, _sub_project(p, c))
            sketch = False
        else:
            shape, sketch, note = cam_shape(Part, _sub_project(p, c), c.get("id") or "cam")
        notes.append(note)
        o = doc.addObject("Part::Feature", "Cam_" + (c.get("id") or "x"))
        o.Shape = shape
        o.Label = (c.get("name") or {}).get("zh", c.get("id")) + ("（示意）" if sketch else "")
        objs[c["id"]] = o
    if p.get("arm"):
        shape, rep = arm_shape(Part, p["arm"])
        o = doc.addObject("Part::Feature", "Arm")
        o.Shape = shape
        o.Label = "换刀臂"
        objs["arm"] = o
    drv = doc.addObject("App::FeaturePython", "CamSystem")
    CamDriver(drv)
    drv.Label = "凸轮系统"
    drv.Project = json.dumps(p, ensure_ascii=False)
    objs["driver"] = drv
    doc.recompute()
    set_angle(doc, p, 0.0, Placement, Rotation, Vector)
    return objs, notes


def poses(p, theta_deg):
    """凸轮轴转到 theta_deg 时各零件的位置（与网页版三维一致）：凸轮绕凸轮轴转 θ；转塔绕 y 轴转 −h·φ；
    换刀臂随转塔转，并按拔插刀凸轮的摆角上下移动（摆杆半径 × 摆角）。返回 {名称: (平移, 绕轴, 角度°)}。"""
    from camkit import globoidal as G
    from camkit.program import Program
    th = math.radians(theta_deg)
    out = {}
    if not is_system(p) and is_cyl(p):  # 圆柱凸轮：凸轮绕 z 转 σθ；滚子平移到滚子轴线的位置（轴线方向不变，沿 x）
        import numpy as np

        from camkit import cyl_solid as CS
        from camkit import cylindrical as C
        c, prog = CS.build(p)
        ps = C.pose(c, prog, np.array([[th]]))
        out["cam"] = ((0.0, 0.0, 0.0), (0, 0, 1), c.sigma * theta_deg)
        out["roller"] = ((0.0, float(ps["cy"][0, 0]), float(ps["cz"][0, 0])), (0, 0, 1), 0.0)
        return out
    glob = next((c for c in p.get("cams") or [] if c.get("type") == "globoidal"), None)
    turret, C = 0.0, 0.0
    if glob:
        g = G.globoid(glob.get("globoidal"))
        prog = Program.from_dict(glob.get("program") or {})
        phi = float(prog.position(th))
        turret = -g.hand * phi
        C = g.C
        out[glob["id"]] = ((C, 0.0, 0.0), (0, 0, 1), theta_deg)
        out["turret"] = ((0.0, 0.0, 0.0), (0, 1, 0), math.degrees(turret))
        z_next = g.L / 2 + 120
    else:
        z_next = 0.0
    drop = 0.0
    for c in p.get("cams") or []:
        if c.get("type") == "globoidal":
            continue
        out[c["id"]] = ((C, 0.0, z_next), (0, 0, 1), theta_deg)
        prog = Program.from_dict(c.get("program") or {})
        s = float(prog.eval(th)[0])
        R = float((c.get("output") or {}).get("radius") or 0.0)
        if prog.unit == "rad" and R:
            drop = R * s
    if p.get("arm"):
        out["arm"] = ((0.0, -170.0 - drop, 0.0), (0, 1, 0), math.degrees(turret))
    return out


def set_angle(doc, p, theta_deg, Placement, Rotation, Vector):
    ps = poses(p, theta_deg)
    names = {"turret": "Turret", "arm": "Arm", "cam": "Cam", "roller": "Roller"}
    for key, (t, ax, ang) in ps.items():
        o = doc.getObject(names.get(key) or ("GloboidalCam" if key == _glob_id(p) else "Cam_" + key))
        if o is None:
            continue
        rot = Rotation(Vector(*ax), ang)
        if key == "arm":
            # 换刀臂的板面在 xy 平面里：先转到与转塔轴（y）垂直，再随转塔转
            rot = rot.multiply(Rotation(Vector(1, 0, 0), -90))
        o.Placement = Placement(Vector(*t), rot)


def _glob_id(p):
    return next((c["id"] for c in p.get("cams") or [] if c.get("type") == "globoidal"), None)


class CamDriver:
    """文档里的“凸轮系统”对象：改“转角”，各零件按时序摆到位。"""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyAngle", "Angle", "Cam", "凸轮轴转角")
        obj.addProperty("App::PropertyString", "Project", "Cam", "项目（网页版的 .wqcam.json 内容）")

    def onChanged(self, obj, prop):
        if prop == "Angle" and getattr(obj, "Project", ""):
            import FreeCAD
            set_angle(obj.Document, json.loads(obj.Project), float(obj.Angle), FreeCAD.Placement, FreeCAD.Rotation,
                      FreeCAD.Vector)

    def execute(self, obj):
        pass

    def dumps(self):
        return None

    def loads(self, state):
        return None


# ---------------------------------------------------------------------------------- 导出


def export(objs, p, outdir, log=print):
    """各零件的 STEP（零件自己的坐标系，不带装配位置）、加工程序和校核摘要。示意件不导出。"""
    os.makedirs(outdir, exist_ok=True)
    files = []
    for key, o in objs.items():
        if key in ("driver", "turret", "roller") or "示意" in o.Label:
            continue
        sh = o.Shape.copy()
        sh.Placement = type(sh.Placement)()
        path = os.path.join(outdir, "{}.step".format(o.Name))
        sh.exportStep(path)
        files.append(path)
    files += drawings(objs, p, outdir, log)
    glob = next((c for c in p.get("cams") or [] if c.get("type") == "globoidal"), None) if is_system(p) else None
    if glob:
        from camkit import globoid_mfg as GM
        from camkit import globoidal as G
        from camkit.program import Program
        g = G.globoid(glob["globoidal"])
        text = GM.program(g, Program.from_dict(glob["program"]), glob.get("mfg") or {}, title(p, "en"))
        path = os.path.join(outdir, "globoidal-4axis.nc")
        with open(path, "w", encoding="ascii") as f:
            f.write(text)
        files.append(path)
    if not is_system(p) and is_cyl(p):  # 圆柱凸轮的四轴程序（网页版“制造”里的设置；没填用示例值）
        from camkit import cyl_mfg as CM
        from camkit import cyl_solid as CS
        c, prog = CS.build(p)
        text = CM.program(c, prog, (p.get("mfg") or {}).get("four") or {}, title(p, "en"))
        path = os.path.join(outdir, "cylindrical-4axis.nc")
        with open(path, "w", encoding="ascii") as f:
            f.write(text)
        files.append(path)
        return files
    if not is_system(p) and p.get("mfg"):  # 制造设置（刀具、机床）是网页版“制造”里填的；没填就不出程序
        from camkit import mfg as MF
        try:
            out = MF.manufacture(p, dict(p["mfg"]))
        except ValueError as e:
            log("加工程序没有导出：{}".format(e))
            out = {"program": ""}
        if out["program"]:
            path = os.path.join(outdir, "cam.nc")
            with open(path, "w", encoding="ascii") as f:
                f.write(out["program"])
            files.append(path)
    return files


def drawings(objs, p, outdir, log=print):
    """每个导出的零件一张 A3 工作图（SVG）：两个视图、主要参数、运动程序、盘形凸轮的廓线坐标表。"""
    import FreeCAD
    import TechDraw
    import wq_cam_drawing as D
    files = []
    cams = {c.get("id"): c for c in p.get("cams") or []} if is_system(p) else {}
    for key, o in objs.items():
        if key in ("driver", "turret", "roller") or "示意" in o.Label:
            continue
        sh = o.Shape.copy()
        sh.Placement = FreeCAD.Placement()
        c = cams.get(key)
        src = c if c is not None else p
        if is_cyl(src):  # 圆柱凸轮：端视图和侧视图、参数、运动程序、槽中心线展开坐标
            sub = _sub_project(p, c) if c is not None else p
            rows = D.cyl_rows(sub)
            extra = [("运动程序", D.program_rows(src)), ("槽中心线（外圆处，每 20°）", D.cyl_coords(sub, 20.0))]
            svg, k = D.sheet(TechDraw, FreeCAD.Vector, sh, o.Label, rows, extra, ((0, 0, 1), (0, -1, 0)),
                             project_title=title(p))
            path = os.path.join(outdir, "{}-drawing.svg".format(o.Name))
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            files.append(path)
            continue
        if key == "arm":
            rows, extra, dirs = D.arm_rows(p["arm"]), [], ((0, 0, 1), (0, -1, 0))
        elif c is not None and c.get("type") == "globoidal":
            rows, extra, dirs = D.globoid_rows(c), [("运动程序（转塔）", D.program_rows(c))], ((0, 0, 1), (0, -1, 0))
        else:
            sub = _sub_project(p, c) if c is not None else p
            src = c if c is not None else p
            rows = D.disk_rows(sub)
            extra = [("运动程序", D.program_rows(src)), ("廓线坐标（每 20°；全表见 CSV）", D.disk_coords(sub, 20.0))]
            dirs = ((0, 0, 1), (0, -1, 0))
            csv = os.path.join(outdir, "{}-points.csv".format(o.Name))
            from camkit import mfg as MF
            with open(csv, "w", encoding="utf-8") as f:
                f.write(MF.point_table(sub, 0.5))
            files.append(csv)
        svg, k = D.sheet(TechDraw, FreeCAD.Vector, sh, o.Label, rows, extra, dirs, project_title=title(p))
        path = os.path.join(outdir, "{}-drawing.svg".format(o.Name))
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        files.append(path)
    return files


# ---------------------------------------------------------------------------------- 命令行与界面


def run_headless(path, outdir):
    import FreeCAD
    import Part
    miss = missing()
    if miss:
        raise SystemExit("缺少 Python 包：{}\n{}".format(", ".join(miss), install_hint(miss)))
    p = load(path)
    res = analyse(p)
    doc = FreeCAD.newDocument("WenQuestCam")
    objs, notes = build(doc, p, Part, FreeCAD.Vector, FreeCAD.Placement, FreeCAD.Rotation)
    files = export(objs, p, outdir)
    doc.saveAs(os.path.join(outdir, "cam.FCStd"))
    summ = summary_text(p, res)
    with open(os.path.join(outdir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summ + "\n\n" + "\n".join(notes) + "\n")
    with open(os.path.join(outdir, "checks.json"), "w", encoding="utf-8") as f:
        json.dump(check_rows(res), f, ensure_ascii=False)
    return {"objects": {k: o.Label for k, o in objs.items()}, "notes": notes, "files": files,
            "valid": {k: bool(o.Shape.isValid()) for k, o in objs.items() if k != "driver"}}


def run_dialog():
    import FreeCAD
    import FreeCADGui
    import Part
    from PySide import QtGui
    miss = missing()
    if miss:
        QtGui.QMessageBox.warning(None, "问渠凸轮",
                                  "缺少 Python 包：{}\n\n{}".format(", ".join(miss), install_hint(miss)))
        return
    path, _ = QtGui.QFileDialog.getOpenFileName(None, "打开问渠凸轮项目", os.path.expanduser("~"),
                                                "问渠凸轮项目 (*.wqcam.json *.json)")
    if not path:
        return
    p = load(path)
    FreeCAD.Console.PrintMessage("问渠凸轮：正在计算和建模（弧面凸轮约一分钟）…\n")
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtGui.Qt.WaitCursor))
    try:
        res = analyse(p)
        doc = FreeCAD.newDocument("WenQuestCam")
        objs, notes = build(doc, p, Part, FreeCAD.Vector, FreeCAD.Placement, FreeCAD.Rotation)
    finally:
        QtGui.QApplication.restoreOverrideCursor()
    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCAD.Console.PrintMessage(summary_text(p, res) + "\n" + "\n".join(notes) + "\n")
    msg = "已建好 {} 个零件。\n{}\n\n校核摘要在“报告视图”里。".format(len([k for k in objs if k != "driver"]),
                                                          "\n".join(notes))
    if "driver" in objs:
        msg += "\n在模型树里选“凸轮系统”，改属性“转角”，各零件按时序动。"
    QtGui.QMessageBox.information(None, "问渠凸轮", msg)


if __name__ == "__main__" and os.environ.get("WQ_CAM_PROJECT"):
    print(json.dumps(run_headless(os.environ["WQ_CAM_PROJECT"], os.environ.get("WQ_CAM_OUT") or "wq-cam-out"),
                     ensure_ascii=False, indent=1))
