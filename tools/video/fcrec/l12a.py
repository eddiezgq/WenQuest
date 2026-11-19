"""第 12 课 片段 A：机头侧面轮廓——导入机头网格（head.stl）当底图，XZ 平面草图上沿网格描：多段线 + 一段“插值 B 样条”（前上角）。真操作。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file, menu_path
import steps
from steps import sp

# 侧面轮廓（XZ），取自机头网格的外形（只做 z ≥ 120 的上部箱体）
POLY = [(-55, 227.6), (-55, 120), (75, 120), (75, 248), (-28.49, 243.36)]
CORNER = [(-28.49, 243.36), (-34.3, 242.2), (-40.81, 239.71), (-44.98, 237.3), (-50.41, 232.94), (-55, 227.6)]


def new_sketch(d, plane_zh, plane_en):
    """草图工作台：新建草图，方向选 plane，确定"""
    yield d.tool("Sketcher_NewSketch")
    yield from d.until(lambda: QtWidgets.QApplication.activeModalWidget() is not None, 6000)
    m = QtWidgets.QApplication.activeModalWidget()
    yield 900
    log("sketch dlg", m.windowTitle() if m else None,
        [(w.objectName(), w.text()) for w in m.findChildren(QtWidgets.QAbstractButton) if w.isVisible()] if m else None)
    rb = [w for w in m.findChildren(QtWidgets.QRadioButton) if w.isVisible() and w.text().replace("&", "").startswith((plane_zh, plane_en))]
    if rb:
        p = d.center(rb[0])
        yield d.move(p, 700)
        d.ring(p)
        rb[0].setChecked(True)
        yield 600
    ok = [b for b in m.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text().replace("&", "") in ("确定", "OK")][0]
    p = d.center(ok)
    yield d.move(p, 600)
    d.ring(p)
    ok.click()
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1000


def script(d):
    yield d.say("曲线：先照着真机头描轮廓。整机里的机头只有三角网格（STL）——新建文件，“文件 → 导入”机头的网格")
    yield d.tool("Std_New"); yield 1200
    yield from menu_path(d, L("文件", "File"), L("导入", "Import"))
    yield from steps.file_dialog(d, L("机头", "head") + ".stl")
    yield from d.until(lambda: App.ActiveDocument and [o for o in App.ActiveDocument.Objects if o.TypeId == "Mesh::Feature"], 15000)
    yield 1200
    mesh = [o for o in App.ActiveDocument.Objects if o.TypeId == "Mesh::Feature"][0]
    log("mesh", mesh.Label, mesh.Mesh.CountFacets)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("机头的铸件：四面开着检修窗。我们只要它的外形——上半部的箱体。先把网格设成半透明，好在后面描图")
    mesh.ViewObject.Transparency = 70
    yield 1500
    yield from steps.pick_workbench(d, "草图", "Sketcher")
    yield d.say("新建草图，方向选 XZ 平面（从正面看机头的侧面）")
    yield from new_sketch(d, "XZ", "XZ")
    Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("多段线：沿网格的外沿点——左下、右下、右上，到顶上前角开始弯的地方")
    yield d.tool("Sketcher_CompLine", "Sketcher_CreatePolyline") if d.action_widget("Sketcher_CompLine") else d.tool("Sketcher_CreatePolyline")
    yield 400
    for k, (x, z) in enumerate(POLY):
        yield d.move(sp(d, x, z), 800 if k else 1000)
        d.click(); yield 400
    d.click(button=Qt.RightButton, ring=False); yield 500
    d.key(Qt.Key_Escape); yield 700
    steps.dump("poly")
    yield d.say("前上角是一段光滑的曲面：用“插值 B 样条”——曲线穿过你点的每一个点。从顶边的端点起，沿网格点 6 个点到左边的端点")
    yield d.tool("Sketcher_CompCreateBSpline", "Sketcher_CreateBSplineByInterpolation") if d.action_widget("Sketcher_CompCreateBSpline") else d.tool("Sketcher_CreateBSplineByInterpolation")
    yield 400
    v = Gui.ActiveDocument.ActiveView
    yield d.move(sp(d, -40, 238), 700)
    yield from steps.zoom_sk(d, 10, 60, at=sp(d, -40, 238))
    for k, (x, z) in enumerate(CORNER):
        yield d.move(sp(d, x, z), 700)
        d.click(); yield 400
    d.click(button=Qt.RightButton, ring=False); yield 600
    d.key(Qt.Key_Escape); yield 700
    steps.dump("bspline")
    sk = steps.sketch()
    App.ActiveDocument.recompute()
    try:
        log("wires", len(sk.Shape.Wires), [w.isClosed() for w in sk.Shape.Wires], [c.Type for c in sk.Constraints if c.Type == "Coincident"].__len__())
    except Exception as e:  # noqa: BLE001
        log("wires?", e)
    Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("一圈侧面轮廓闭合了：五段直线 + 一段 B 样条。逆向描出来的轮廓不必完全约束，和网格贴得够近就行")
    yield 2500
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 600
    App.ActiveDocument.saveAs(model_file("机头曲面.FCStd", "HeadSurface.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
