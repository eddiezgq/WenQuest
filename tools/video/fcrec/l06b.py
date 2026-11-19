"""第 6 课 片段 B：曲柄销——圆凸台 25 mm；端面上用“孔”工具打 M3 螺纹孔，深 7.5、平底。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps
from steps import sp


def widgets(tag):
    out = []
    for w in QtWidgets.QApplication.allWidgets():
        if w.isVisible() and w.objectName() and isinstance(w, (QtWidgets.QComboBox, QtWidgets.QAbstractSpinBox, QtWidgets.QCheckBox)):
            v = w.currentText() if isinstance(w, QtWidgets.QComboBox) else (w.isChecked() if isinstance(w, QtWidgets.QCheckBox) else w.text())
            out.append((w.objectName(), v))
    log(tag, out)


def script(d):
    yield d.say("曲柄销：直径 10、长 25 的圆柱，一头有 M3 螺纹孔，装在曲柄上")
    yield from steps.new_body_sketch(d, say=False, zoom=(20, 230))
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(d.model_pt(0, 0), 900)
    d.click(); yield 500
    yield d.move(d.model_pt(4, 3), 700)
    d.keys("10", enter=True); yield 1000
    d.key(Qt.Key_Escape); yield 600
    log("dof", steps.dof_text(d))
    yield d.say("圆心在原点、直径 10，完全约束。凸台 25 mm")
    yield from steps.leave_and_pad(d, 25)
    yield 800
    yield d.say("孔要有定位：点选上端面，新建草图，在原点放一个点")
    Gui.Selection.clearSelection()
    p = d.model_pt(0, 0, 25)
    yield d.move(p, 900)
    d.click(p); yield 800
    log("sel face", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.tool("PartDesign_CompSketches", "PartDesign_NewSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1000
    yield d.move(d.center(d.vp()), 500)
    yield from d.zoom_to(20, 230)
    yield d.tool("Sketcher_CreatePoint"); yield 400
    yield d.move(sp(d, 0, 0), 900)
    d.click(); yield 700
    d.key(Qt.Key_Escape); yield 600
    steps.dump("point")
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    sk = steps.sketch()
    yield d.say("选中这个草图，点“孔”")
    p = d.tree_item(sk.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("PartDesign_Hole")
    yield from d.until(lambda: steps.named(QtWidgets.QComboBox, "ThreadType") is not None)
    yield 1200
    widgets("hole0")
    yield d.say("螺纹类型选“ISO 米制普通螺纹”，规格 M3x0.5")
    yield from steps.combo_pick(d, steps.named(QtWidgets.QComboBox, "ThreadType"), L("ISO 米制普通", "ISO metric regular"))
    yield 600
    widgets("hole1")
    yield from steps.combo_pick(d, steps.named(QtWidgets.QComboBox, "ThreadSize"), "M3x0.5")
    yield 600
    widgets("hole2")
    ht = steps.named(QtWidgets.QComboBox, "HoleType")
    log("hole types", [ht.itemText(k) for k in range(ht.count())])
    yield d.say("孔的类型选第二项“攻丝钻”：先钻底孔、以后攻丝，不画螺纹线")
    yield from steps.combo_pick(d, ht, 1)
    yield d.say("深度 7.5；去掉“钻孔角度”，孔底是平的")
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "Depth"), "7.5 mm")
    cb = steps.named(QtWidgets.QCheckBox, "DrillPointAngled")
    if cb is not None and cb.isChecked():
        p = d.center(cb)
        yield d.move(p, 700)
        d.click(p); yield 300
        if cb.isChecked():
            cb.click()
        yield 800
    widgets("hole3")
    yield from steps.task_ok(d)
    h = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Hole"][-1]
    log("hole", h.ThreadType, h.ThreadSize, h.Threaded, h.Diameter.Value, h.Depth.Value, h.DrillPoint, round(h.Shape.Volume, 2))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    yield d.say("孔是螺纹孔，但默认不画螺纹线：按底孔直径 2.5 挖，属性里记着“M3”——出工程图时自动标螺纹")
    yield 1500
    yield d.say("凸台加材料，凹槽去材料；孔是专门的“凹槽”：螺纹、沉头、钻尖都能直接选")
    yield 2500
    App.ActiveDocument.saveAs(model_file("曲柄销.FCStd", "CrankPin.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
