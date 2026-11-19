"""第 12 课 片段 B：机头正面轮廓——YZ 平面草图：矩形（宽 118、高 128）沿网格放好，上面两个角“圆角”，半径 14。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file
import steps
from steps import sp


def script(d):
    App.openDocument(model_file("机头曲面.FCStd", "HeadSurface.FCStd"))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield from steps.pick_workbench(d, "草图", "Sketcher")
    yield d.say("再描正面轮廓：新建草图，方向选 YZ 平面")
    Gui.Selection.clearSelection()
    yield d.tool("Sketcher_NewSketch")
    yield from d.until(lambda: QtWidgets.QApplication.activeModalWidget() is not None, 6000)
    m = QtWidgets.QApplication.activeModalWidget()
    yield 900
    rb = [w for w in m.findChildren(QtWidgets.QRadioButton) if w.objectName() == "YZ_radioButton"][0]
    p = d.center(rb)
    yield d.move(p, 700)
    d.ring(p)
    rb.setChecked(True)
    yield 600
    ok = [b for b in m.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text().replace("&", "") in ("确定", "OK")][0]
    p = d.center(ok)
    yield d.move(p, 600)
    d.ring(p)
    ok.click()
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1000
    Gui.SendMsgToActiveView("ViewFit"); yield 800
    ie = Gui.ActiveDocument.getInEdit()
    log("edit", ie, getattr(ie, "Object", None) and ie.Object.Name, steps.sketch().Name, steps.sketch().Placement, sp(d, -48, 120), sp(d, 70, 248))
    yield d.say("多段线沿网格的外沿点四个角：左下、右下、右上、左上，再点回左下闭合（y 从 −48 到 70，z 从 120 到 248）")
    yield d.tool("Sketcher_CompLine", "Sketcher_CreatePolyline") if d.action_widget("Sketcher_CompLine") else d.tool("Sketcher_CreatePolyline")
    yield 400
    for k, (y, z) in enumerate([(-48, 120), (70, 120), (70, 248), (-48, 248), (-48, 120)]):
        yield d.move(sp(d, y, z), 1000 if not k else 800)
        d.click(); yield 400
    d.click(button=Qt.RightButton, ring=False); yield 500
    log("in edit after poly", Gui.ActiveDocument.getInEdit() is not None)
    if Gui.ActiveDocument.getInEdit() is not None and steps.sketch().Name != "Sketch":
        pass
    steps.dump("rect")
    yield d.say("描出来的线没有约束，加半径时会整体跑掉。选左下角点，点“锁定”；右上角点也锁定：位置钉死")
    sk = steps.sketch()
    for vx, (y, z) in (("Vertex1", (-48, 120)), ("Vertex4", (70, 248))):
        Gui.Selection.clearSelection()
        p = sp(d, y, z)
        yield d.move(p, 800)
        d.ring(p)
        Gui.Selection.addSelection(App.ActiveDocument.Name, sk.Name, vx)
        yield 500
        yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainLock")
        yield 900
    yield 1200
    App.ActiveDocument.recompute()
    log("dof", steps.dof_text(d))
    yield d.say("上面两个角是铸件的圆角：点“圆角”工具，点左上角的角点，再点右上角的角点")
    sk = steps.sketch()
    names = [str(a.objectName() or a.data()) for tb in d.mw.findChildren(QtWidgets.QToolBar) if tb.isVisible() for a in tb.actions()
             if "illet" in str(a.objectName() or a.data())]
    log("fillet buttons", names)
    log("all acts", [(tb.objectName(), [(a.objectName(), a.data(), a.text()) for a in tb.actions()]) for tb in d.mw.findChildren(QtWidgets.QToolBar) if tb.isVisible() and "ketch" in tb.objectName()])
    yield d.tool(names[0], None if names[0] == "Sketcher_CreateFillet" else "Sketcher_CreateFillet")
    yield 500
    for y in (-48, 70):
        yield d.move(sp(d, y, 248), 900)
        d.click(); yield 900
        yield from steps.answer_modal(d, wait=600)
    d.key(Qt.Key_Escape); yield 700
    sk = steps.sketch()
    arcs = [i for i, g in enumerate(sk.Geometry) if g.TypeId == "Part::GeomArcOfCircle"]
    log("arcs", arcs, [round(sk.Geometry[i].Radius, 2) for i in arcs])
    yield d.say("两个圆弧的半径都约成 14：选圆弧，点“半径”，键入 14")
    for i in arcs:
        g = steps.sketch().Geometry[i]
        import math
        a = (g.FirstParameter + g.LastParameter) / 2
        Gui.Selection.clearSelection()
        yield d.move(sp(d, g.Center.x + g.Radius * math.cos(a), g.Center.y + g.Radius * math.sin(a)), 800)
        d.click(); yield 500
        yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainRadius")
        yield from steps.datum(d, 14)
        App.ActiveDocument.recompute(); yield 500
    steps.dump("front")
    yield d.say("正面轮廓也描好了：一个上角倒圆的矩形")
    yield 2000
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 600
    App.ActiveDocument.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
