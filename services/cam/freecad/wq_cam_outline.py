# -*- coding: utf-8 -*-
"""问渠凸轮 · FreeCAD：用画好的草图当凸轮廓线，反求从动件运动（第 179 轮）。

在 FreeCAD 里选中凸轮廓线的草图（或者任何带封闭轮廓的对象：线框、面、平板零件），点工作台“问渠”→“凸轮”，
回答“是”，填从动件参数，软件就用与网页版同一个内核（camkit/inverse.py）按廓线求出从动件的运动，
存成网页版能打开的项目文件（.wqcam.json），并照常重算校核、建实体。

取廓线：对象里面积最大的那条封闭线（轴孔、键槽这些小的封闭线不算），在草图自己的平面里取点（每 0.02 mm 一个，
按图原样，圆弧和样条都是精确取点）；回转中心默认是草图原点。

命令行（不开界面）：
  import wq_cam_outline as O
  O.run_headless(FreeCAD.ActiveDocument.getObject("Sketch"), {"follower": "translating", "contact": "roller",
                 "rr": 3, "e": 0, "sigma": 1}, "输出文件夹")
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SPACING = 0.02  # mm between points along the outline


def outline_points(obj):
    """The largest closed loop of the object, as [[x, y], ...] in the object's own plane (a sketch: its XY)."""
    import FreeCAD
    import Part

    shape = obj.Shape
    wires = [w for w in shape.Wires if w.isClosed()]
    if not wires:
        raise ValueError("选中的对象里没有封闭的线：凸轮廓线要首尾相接")
    # area of each loop in its own plane
    best, best_area = None, -1.0
    for w in wires:
        try:
            a = abs(Part.Face(w).Area)
        except Exception:  # noqa: BLE001 - a wire that is not flat
            continue
        if a > best_area:
            best, best_area = w, a
    if best is None:
        raise ValueError("封闭的线不在一个平面里")
    n = int(min(60000, max(2000, math.ceil(best.Length / SPACING))))
    pts = best.discretize(Number=n)
    # back to the object's own plane (a sketch's placement puts its XY anywhere in space)
    inv = obj.getGlobalPlacement().inverse() if hasattr(obj, "getGlobalPlacement") else obj.Placement.inverse()
    local = [inv.multVec(p) for p in pts]
    zs = [abs(p.z) for p in local]
    if max(zs) > 1e-6 * max(1.0, best.BoundBox.DiagonalLength):
        # not in the object's XY: use the plane of the loop itself
        plane = Part.Face(best).Surface
        u = plane.Axis
        x = FreeCAD.Vector(1, 0, 0) if abs(u.x) < 0.9 else FreeCAD.Vector(0, 1, 0)
        ex = (x - u * x.dot(u)).normalize()
        ey = u.cross(ex)
        o = plane.Position
        local = [FreeCAD.Vector((p - o).dot(ex), (p - o).dot(ey), 0) for p in pts]
    if local[0].distanceToPoint(local[-1]) < 1e-9:
        local = local[:-1]
    return [[p.x, p.y] for p in local]


def solve(points, mechanism, center=(0.0, 0.0), zero="rise", smooth=1.0):
    """The same call as the web app's “导入廓线”: the point-table program, the base circle and the report."""
    from camkit import inverse as IV

    return IV.import_outline({"mechanism": mechanism, "outline": {
        "format": "points", "data": points, "spline": False, "center": list(center), "zero": zero,
        "smooth": smooth}})


def project_of(points, mechanism, res, title, center=(0.0, 0.0), zero="rise", smooth=1.0):
    """A project the web app opens: the program found, the base circle, and the outline kept as x, y points."""
    text = "x,y\n" + "\n".join("{:.6f},{:.6f}".format(x, y) for x, y in points)
    return {
        "title": {"zh": title, "en": title},
        "program": res["program"],
        "mechanism": res["mechanism"],
        "outline": {"format": "xy", "name": title + ".csv", "data": text, "cx": center[0], "cy": center[1],
                    "zero": zero, "smooth": smooth, "report": res["report"], "used": ""},
    }


def report_text(rep):
    unit = "°" if rep["unit"] == "deg" else "mm"
    ck = rep["check"]
    sh = rep["shift_deg"] - 360 if rep["shift_deg"] > 180 else rep["shift_deg"]
    lines = [
        "基圆半径（由廓线求出）：{:.4f} mm".format(rep["rb"]),
        "行程：{:.4f} {}".format(rep["lift"], unit),
        "零位相对图上转过：{:.2f}°".format(sh) if rep["zero"] == "rise" else "零位：按图上方位",
        "反求校验（重新生成的廓线与导入廓线的最大偏差）：{:.2f} µm {}".format(ck["max_dev"] * 1000,
                                                                    "合格" if ck["ok"] else "不合格"),
        "加速度峰值（对转角）：未平滑 {:.4g}，平滑后 {:.4g}".format(rep["acc"]["raw_peak"], rep["acc"]["smooth_peak"]),
    ]
    if not ck["ok"]:
        lines.append("导入的廓线和所填的从动件对不上（约 {:.1f}° 处）：常见原因是滚子半径、偏距、中心距或回转中心填错，"
                     "或者滚子比廓线凹处还大，那一段碰不到。".format(ck["at_deg"]))
    return "\n".join(lines)


def run_headless(obj, mechanism, outdir, center=(0.0, 0.0), zero="rise", smooth=1.0):
    """Outline from obj → project file, rebuilt and checked by wq_cam like any project."""
    import wq_cam

    pts = outline_points(obj)
    res = solve(pts, mechanism, center, zero, smooth)
    os.makedirs(outdir, exist_ok=True)
    p = project_of(pts, mechanism, res, obj.Label, center, zero, smooth)
    path = os.path.join(outdir, obj.Label + ".wqcam.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    out = wq_cam.run_headless(path, outdir)
    out["project"] = path
    out["report"] = res["report"]
    return out


def selected_outline():
    """The selected object, if it has a closed loop (a sketch, a wire, a face, a plate)."""
    try:
        import FreeCADGui
        sel = FreeCADGui.Selection.getSelection()
    except Exception:  # noqa: BLE001
        return None
    for o in sel:
        sh = getattr(o, "Shape", None)
        if sh is not None and any(w.isClosed() for w in sh.Wires):
            return o
    return None


def run_dialog(obj):
    """Ask for the follower, find the motion, save the project, build the cam (wq_cam)."""
    import FreeCAD
    import FreeCADGui
    import Part
    from PySide import QtGui

    import wq_cam

    d = QtGui.QDialog()
    d.setWindowTitle("问渠凸轮 · 用廓线反求运动")
    form = QtGui.QFormLayout(d)
    fol = QtGui.QComboBox()
    fol.addItems(["直动", "摆动"])
    con = QtGui.QComboBox()
    con.addItems(["滚子", "平底", "尖顶"])

    def num(v, lo=-1e6):
        s = QtGui.QDoubleSpinBox()
        s.setDecimals(4)
        s.setRange(lo, 1e6)
        s.setValue(v)
        return s

    rr, e, a, L = num(5, 0), num(0), num(100, 0), num(80, 0)
    cx, cy = num(0), num(0)
    sig = QtGui.QComboBox()
    sig.addItems(["逆时针", "顺时针"])
    zero = QtGui.QComboBox()
    zero.addItems(["升程开始处为 0°", "按图上方位（从动件在 +y 方向）"])
    sm = QtGui.QComboBox()
    levels = [(1.0, "自动（按廓线精度）"), (0.3, "弱"), (3.0, "强"), (10.0, "更强"), (0.0, "不平滑")]
    sm.addItems([x[1] for x in levels])
    for label, w in (("从动件", fol), ("接触", con), ("滚子半径 mm", rr), ("偏距 mm（直动）", e),
                     ("中心距 mm（摆动）", a), ("摆杆长 mm（摆动滚子、尖顶）", L), ("凸轮转向", sig),
                     ("回转中心 x mm（草图坐标）", cx), ("回转中心 y mm", cy), ("零位", zero), ("平滑程度", sm)):
        form.addRow(label, w)
    btn = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
    btn.accepted.connect(d.accept)
    btn.rejected.connect(d.reject)
    form.addRow(btn)
    if not d.exec_():
        return
    osc = fol.currentIndex() == 1
    contact = ["roller", "flat", "knife"][con.currentIndex()]
    mech = {"follower": "oscillating" if osc else "translating", "contact": contact,
            "sigma": 1 if sig.currentIndex() == 0 else -1}
    if contact == "roller":
        mech["rr"] = rr.value()
    if osc:
        mech["a"] = a.value()
        if contact != "flat":
            mech["L"] = L.value()
    elif contact != "flat":
        mech["e"] = e.value()
    center = (cx.value(), cy.value())
    zr = "rise" if zero.currentIndex() == 0 else "drawing"
    level = levels[sm.currentIndex()][0]
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtGui.Qt.WaitCursor))
    try:
        pts = outline_points(obj)
        res = solve(pts, mech, center, zr, level)
    except Exception as exc:  # noqa: BLE001 - shown to the user in Chinese where the kernel has it
        QtGui.QApplication.restoreOverrideCursor()
        from camkit.inverse import zh
        QtGui.QMessageBox.warning(None, "问渠凸轮", "求不出来：" + zh(str(exc)))
        return
    QtGui.QApplication.restoreOverrideCursor()
    rep = report_text(res["report"])
    FreeCAD.Console.PrintMessage("问渠凸轮 · 廓线反求\n" + rep + "\n")
    path, _ = QtGui.QFileDialog.getSaveFileName(None, "保存项目（网页版也能打开）",
                                                os.path.join(os.path.expanduser("~"), obj.Label + ".wqcam.json"),
                                                "问渠凸轮项目 (*.wqcam.json)")
    p = project_of(pts, mech, res, obj.Label, center, zr, level)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=1)
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtGui.Qt.WaitCursor))
    try:
        chk = wq_cam.analyse(p)
        doc = FreeCAD.newDocument("WenQuestCam")
        objs, notes = wq_cam.build(doc, p, Part, FreeCAD.Vector, FreeCAD.Placement, FreeCAD.Rotation)
    finally:
        QtGui.QApplication.restoreOverrideCursor()
    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCAD.Console.PrintMessage(wq_cam.summary_text(p, chk) + "\n")
    QtGui.QMessageBox.information(None, "问渠凸轮", rep + ("\n\n项目已存：" + path if path else "") +
                                  "\n\n按求出的运动重建了凸轮，校核摘要在“报告视图”里。")
