"""第 12 课 片段 C：两条轮廓各自“拉伸”成曲面（不勾“创建实体”），再求两张曲面的“截面”——机头前上角的空间交线。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps


def extrude(d, sk, fwd, rev):
    """选草图，Part“拉伸”：沿草图法向，正向 fwd、反向 rev，不勾“创建实体”"""
    p = d.tree_item(sk.Label)
    yield d.move(p, 800)
    d.click(p); yield 500
    yield d.tool("Part_Extrude")
    yield from d.until(lambda: steps.named(QtWidgets.QAbstractSpinBox, "spinLenFwd") is not None, 8000)
    yield 1000
    log("extrude widgets", [(w.objectName(), w.isChecked() if isinstance(w, QtWidgets.QAbstractButton) else w.text())
                            for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.objectName()
                            and isinstance(w, (QtWidgets.QAbstractSpinBox, QtWidgets.QCheckBox, QtWidgets.QRadioButton))])
    rb = steps.named(QtWidgets.QRadioButton, "rbDirModeNormal")
    if rb is not None and not rb.isChecked():
        p = d.center(rb); yield d.move(p, 600); d.click(p); yield 500
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "spinLenFwd"), f"{fwd} mm")
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "spinLenRev"), f"{rev} mm")
    cb = steps.named(QtWidgets.QCheckBox, "chkSolid")
    if cb is not None and cb.isChecked():
        steps.show(cb)
        yield 300
        p = d.center(cb); yield d.move(p, 600); d.click(p); yield 500
        if cb.isChecked():
            cb.click()
            yield 300
    yield 600
    yield from steps.task_ok(d, gone="spinLenFwd")
    e = [o for o in App.ActiveDocument.Objects if o.TypeId == "Part::Extrusion"][-1]
    App.ActiveDocument.recompute()
    log("extrusion", e.Label, e.DirMode, e.LengthFwd.Value, e.LengthRev.Value, e.Solid, e.Shape.ShapeType, round(e.Shape.Area, 1),
        [round(x, 1) for x in (e.Shape.BoundBox.XMin, e.Shape.BoundBox.XMax, e.Shape.BoundBox.YMin, e.Shape.BoundBox.YMax)])
    return e


def script(d):
    doc = App.openDocument(model_file("机头曲面.FCStd", "HeadSurface.FCStd"))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    mesh = [o for o in doc.Objects if o.TypeId == "Mesh::Feature"][0]
    side, front = [o for o in doc.Objects if o.TypeId == "Sketcher::SketchObject"][:2]
    yield from steps.pick_workbench(d, "Part", "Part")
    yield d.say("两条轮廓变成曲面：选侧面轮廓，点“拉伸”，沿法向往两边拉，盖住机头的宽度；不勾“创建实体”——要的是曲面")
    e1 = yield from extrude(d, side, 48, 70)
    yield d.say("正面轮廓同样拉伸，盖住机头的长度")
    e2 = yield from extrude(d, front, 75, 55)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    yield d.say("两张曲面互相穿插。选这两个拉伸，点“截面”：得到它们的交线")
    p = d.tree_item(e1.Label)
    yield d.move(p, 800)
    d.click(p); yield 500
    p = d.tree_item(e2.Label)
    yield d.move(p, 700)
    d.click(p, mods=Qt.ControlModifier); yield 700
    yield d.tool("Part_CompBoolean", "Part_Section") if not d.action_widget("Part_Section") else d.tool("Part_Section")
    yield 2500
    sec = [o for o in doc.Objects if o.TypeId == "Part::Section"][-1]
    doc.recompute()
    log("section", len(sec.Shape.Edges), round(sum(e.Length for e in sec.Shape.Edges), 1), [e.Curve.TypeId.split("::")[-1] for e in sec.Shape.Edges][:12])
    for o in (e1, e2, mesh):
        o.ViewObject.Visibility = False
    sec.ViewObject.LineWidth = 4
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("只看交线：机头外形的空间棱线，包括前上角那段弯过来的 B 样条——它不在任何一个平面里，是两张曲面交出来的")
    yield 3000
    for o in (e1, e2):
        o.ViewObject.Visibility = True
    Gui.SendMsgToActiveView("ViewFit")
    yield 600
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
