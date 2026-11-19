"""第 3 课 片段 A：新建零件、在 XY 平面上画套环截面（两个圆、键入尺寸）、凸台 3 mm——真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore
from director import Director, boot, log, Qt, QtWidgets
import steps


def script(d):
    yield from steps.new_body_sketch(d)
    yield d.say("圆工具：先点圆心（原点），再键入直径 16，回车")
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(d.model_pt(0, 0), 900)
    d.click(); yield 500
    yield d.move(d.model_pt(9, 5), 800)
    d.keys("16", enter=True); yield 1400
    yield d.say("工具还开着，接着画内孔：圆心还是原点，直径 8")
    yield d.move(d.model_pt(0, 0), 900)
    d.click(); yield 500
    yield d.move(d.model_pt(3, 2), 700)
    d.keys("8", enter=True); yield 1200
    d.key(Qt.Key_Escape); yield 800
    sk = [o for o in App.ActiveDocument.Objects if o.TypeId == "Sketcher::SketchObject"][0]
    log("geo", [str(g) for g in sk.Geometry], [(c.Type, c.First, c.FirstPos, c.Second, c.SecondPos) for c in sk.Constraints], "full", getattr(sk, "FullyConstrained", "?"))
    yield d.say("右边显示“完全约束”（绿色）：两个圆的位置、大小都定了")
    yield 2600
    yield d.say("关闭草图，选中草图点“凸台”，长度键入 3 mm")
    yield from steps.leave_and_pad(d, 3)
    yield d.say("压脚杆套环：外径 16、内孔 8、厚 3——和 WQ-LS 设计里的一样")
    yield 3500


def main():
    d = Director()
    d.run(script(d))


boot(main)
