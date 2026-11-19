"""第 7 课 片段 B：梭壳——Ø22.4 凸台 14，点开口那一面，“抽壳”壁厚 0.6。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, model_file
import steps


def script(d):
    yield d.say("梭壳（装梭芯的小杯子）：外径 22.4、深 14、壁厚 0.6。杯子、盒子、外壳这类零件用“抽壳”")
    yield from steps.new_body_sketch(d, say=False, zoom=(20, 230))
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(d.model_pt(0, 0), 900)
    d.click(); yield 500
    yield d.move(d.model_pt(8, 6), 700)
    d.keys("22.4", enter=True); yield 1000
    d.key(Qt.Key_Escape); yield 600
    yield d.say("先做实心的：圆 22.4，凸台 14")
    yield from steps.leave_and_pad(d, 14)
    yield 800
    yield d.say("点选上端面——开口就开在这一面")
    Gui.Selection.clearSelection()
    p = d.model_pt(0, 0, 14)
    yield d.move(p, 900)
    d.click(p); yield 800
    log("sel face", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.say("点“抽壳”，厚度 0.6，确定：选中的面被挖开，其余的面都留 0.6 的壁")
    yield d.tool("PartDesign_Thickness")
    sb = lambda: [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible()
                  and w.window() is d.mw and w.objectName() not in ("",)]
    yield from d.until(lambda: steps.named(QtWidgets.QAbstractSpinBox, "Value") is not None, 8000)
    yield 1200
    log("thick widgets", [(w.objectName(), w.text()) for w in sb()],
        [(w.objectName(), w.isChecked()) for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QCheckBox) and w.isVisible()])
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "Value"), "0.6 mm")
    yield from steps.task_ok(d)
    t = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Thickness"][-1]
    log("thickness", t.Value.Value, t.Reversed, t.Mode, t.Join, round(t.Shape.Volume, 2))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("杯子出来了，体积约 787 mm³。真梭壳的底厚 1.5：抽壳只能处处一样厚，底要更厚，就改用凹槽挖内腔（本课“自己做”）")
    yield 3000
    App.ActiveDocument.saveAs(model_file("梭壳.FCStd", "BobbinCase.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
