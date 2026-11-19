"""第 9 课 片段 C：针杆第二圈油槽——不再画草图，“线性阵列”：沿竖轴、长度 2、次数 2。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, QtWidgets, L, model_file
import steps


def script(d):
    App.openDocument(model_file("针杆_L6.FCStd", "NeedleBar_L6.FCStd"))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield d.move(d.model_pt(4, 0, 40), 800)
    yield from d.zoom_to(10, 260, at=d.model_pt(4, 0, 40))
    yield d.say("第 6 课的针杆只挖了一圈油槽。第二圈在上面 2 mm：不用再画草图，用“线性阵列”")
    g = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Groove"][-1]
    p = d.tree_item(g.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("PartDesign_LinearPattern")
    find = lambda: [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and isinstance(w, QtWidgets.QAbstractSpinBox)
                    and "ccurrence" in w.objectName()]
    yield from d.until(find, 8000)
    yield 1200
    named = lambda: {w.objectName(): w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.objectName()
                     and isinstance(w, (QtWidgets.QAbstractSpinBox, QtWidgets.QComboBox))}
    log("linear widgets", [(k, w.currentText() if isinstance(w, QtWidgets.QComboBox) else w.text()) for k, w in named().items()])
    yield d.say("方向选“垂直草图轴”（沿着针杆），长度 2，次数 2")
    yield from steps.combo_pick(d, named()["comboDirection"], L("垂直草", "Vertical sketch"))
    yield from d.until(lambda: steps.named(QtWidgets.QAbstractSpinBox, "spinExtent") is not None, 5000)
    yield 500
    log("after dir", [(k, w.currentText() if isinstance(w, QtWidgets.QComboBox) else w.text()) for k, w in named().items()])
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "spinExtent"), "2 mm")
    yield from d.until(find, 5000)
    yield from steps.type_into(d, find()[0], "2")
    yield 1200
    yield from steps.task_ok(d)
    lp = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::LinearPattern"][-1]
    log("linear", lp.Direction, lp.Length.Value, lp.Occurrences, round(lp.Shape.Volume, 2))
    yield d.move(d.model_pt(4, 0, 40), 600)
    yield d.say("第二圈出来了，体积和第 7 课补的那圈一样。阵列跟着原特征走：改第一圈的槽宽，两圈一起变")
    yield 2500
    App.ActiveDocument.saveAs(model_file("针杆_阵列.FCStd", "NeedleBar_pattern.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
