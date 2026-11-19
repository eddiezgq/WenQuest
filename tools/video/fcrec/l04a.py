"""第 4 课 片段 A：自由度——打开第 3 课画的针夹轮廓，看“约束不足：n 个自由度”，拖一下就变形，撤销。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, QtGui
import steps

M = os.path.join(os.environ.get("WQ_REC", "."), "model")


def script(d):
    yield from steps.open_and_edit(d, os.path.join(M, "针夹草图.FCStd"))
    log("dof0", steps.dof_text(d))
    d.say("右边写着“约束不足”：还有几个自由度——形状能被拖动，尺寸没定")
    lab = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QLabel) and w.isVisible() and "自由度" in w.text()]
    if lab:
        p = d.center(lab[0]); yield d.move(p, 900); d.ring(p); yield 2200
    d.say("拖一下下边线：整条边跟着走，因为它离原点多远还没定")
    a = d.model_pt(1.5, -7.03)
    yield d.move(a, 900)
    d.press(); yield 200
    yield d.move(d.model_pt(1.5, -9.5), 1300, buttons=Qt.LeftButton)
    d.release(); yield 900
    steps.dump("dragged")
    d.say("圆弧也能拖大拖小：半径也没定")
    a = d.model_pt(2.49, 4.99)
    yield d.move(a, 900)
    d.press(); yield 200
    yield d.move(d.model_pt(3.2, 6.4), 1100, buttons=Qt.LeftButton)
    d.release(); yield 900
    steps.dump("dragged2")
    d.say("撤销两次（Ctrl+Z），回到原样")
    d.key(Qt.Key_Z, d.vp(), Qt.ControlModifier); yield 600
    d.key(Qt.Key_Z, d.vp(), Qt.ControlModifier); yield 900
    steps.dump("undone")
    d.say("颜色也告诉你：白色是还能动的，完全约束以后全变绿")
    yield 3500
    log("dof1", steps.dof_text(d))


def main():
    d = Director()
    d.run(script(d))


boot(main)
