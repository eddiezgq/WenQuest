"""第 8 课 片段 A：压脚簧——XZ 平面上画线径 1.8 的圆（离轴 7），“螺旋”：节距 4、高 60。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps
from steps import sp


def widgets(tag):
    log(tag, [(w.objectName(), w.currentText() if isinstance(w, QtWidgets.QComboBox) else (w.isChecked() if isinstance(w, QtWidgets.QCheckBox) else w.text()))
              for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.objectName()
              and isinstance(w, (QtWidgets.QComboBox, QtWidgets.QAbstractSpinBox, QtWidgets.QCheckBox))])


def script(d):
    yield d.say("弹簧是螺旋：一个圆（钢丝的截面）绕着轴边转边往上走。压脚簧：外径 15.8、钢丝直径 1.8")
    yield from steps.new_body_sketch(d, plane="XZ", say=False, zoom=(20, 300))
    yield d.say("XZ 平面上画钢丝截面：圆心放在横轴上、离原点 7（弹簧中径的一半），直径 1.8")
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(sp(d, 7, 0), 900)
    d.click(); yield 500
    yield d.move(sp(d, 7.6, 0.5), 600)
    d.keys("1.8", enter=True); yield 1000
    d.key(Qt.Key_Escape); yield 600
    steps.dump("circle")
    yield d.say("圆心的位置用“水平距离”锁住：7")
    Gui.Selection.clearSelection()
    c = steps.sketch().Geometry[0].Center
    p = sp(d, c.x, c.y)
    yield d.move(p, 800)
    d.ring(p)                        # 圆心压在横轴上，点下去会选中横轴：直接选圆心那个点（和点中它一样）
    sk = steps.sketch()
    Gui.Selection.addSelection(App.ActiveDocument.Name, sk.Name, "Vertex1")
    log("sel", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield 600
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistanceX")
    yield from steps.datum(d, 7)
    App.ActiveDocument.recompute(); yield 600
    steps.dump("placed")
    log("dof", steps.dof_text(d))
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    yield d.say("点“螺旋”：轴选“垂直草绘轴”，节距 4、高度 60")
    yield d.tool("PartDesign_AdditiveHelix")
    yield from d.until(lambda: steps.named(QtWidgets.QComboBox, "axis") is not None, 8000)
    yield 1500
    widgets("helix0")
    yield from steps.combo_pick(d, steps.named(QtWidgets.QComboBox, "axis"), L("垂直草绘轴", "Vertical sketch axis"))
    yield 800
    widgets("helix-axis")
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "pitch"), "4 mm")
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "height"), "60 mm")
    widgets("helix1")
    yield 800
    h = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::AdditiveHelix"][-1]
    log("helix before ok", h.Pitch.Value, h.Height.Value, h.ReferenceAxis[1])
    yield from steps.task_ok(d)
    h = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::AdditiveHelix"][-1]
    log("helix", h.Mode, h.Pitch.Value, h.Height.Value, h.Turns, h.ReferenceAxis[1], round(h.Shape.Volume, 2), h.Shape.isValid())
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("15 圈的弹簧。改节距、圈数、高度，弹簧跟着变；左旋弹簧勾“左旋”")
    yield 2500
    App.ActiveDocument.saveAs(model_file("压脚簧.FCStd", "PresserSpring.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
