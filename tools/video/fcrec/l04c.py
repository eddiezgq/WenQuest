"""第 4 课 片段 C：尺寸约束——半径、宽度、到原点的距离，直到“完全约束”变绿；再凸台 8 mm 成针夹。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets
import steps

M = os.path.join(os.environ.get("WQ_REC", "."), "model")


def datum(d, value):
    """尺寸约束弹出的输入框：键入数值，回车"""
    yield from d.until(lambda: isinstance(QtWidgets.QApplication.focusWidget(), QtWidgets.QAbstractSpinBox), 6000)
    w = QtWidgets.QApplication.focusWidget()
    log("datum focus", w, w.objectName() if w else None, QtWidgets.QApplication.activeModalWidget())
    yield 500
    d.key(Qt.Key_A, w, Qt.ControlModifier)
    d.keys(value, w=w); yield 700
    d.key(Qt.Key_Return, w); yield 1200


def script(d):
    yield from steps.open_and_edit(d, os.path.join(M, "针夹草图.FCStd"))
    d.say("还剩 3 个自由度：圆弧多大、耳朵多宽、耳朵伸多长。用尺寸约束定")
    yield 2500
    d.say("选圆弧，点“半径”，键入 5.5")
    yield from steps.pick(d, (-2.49, 4.99))
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainRadius")
    yield from datum(d, "5.5")
    log("dof", steps.dof_text(d))
    d.say("选下边线，点“水平距离”，键入 7（耳朵宽 7）")
    sk = steps.sketch(); a, b = sk.getPoint(1, 1), sk.getPoint(1, 2)
    yield from steps.pick(d, ((a.x + b.x) / 2 + 1.0, a.y))
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistanceX")
    yield from datum(d, "7")
    log("dof", steps.dof_text(d))
    d.say("选原点和下边线，点“距离”，键入 7（下边离中心 7）")
    sk = steps.sketch(); a = sk.getPoint(1, 1)
    yield from steps.pick(d, (0, 0), (1.5, a.y))
    log("selC", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistance")
    yield from datum(d, "7")
    log("dof", steps.dof_text(d))
    steps.dump("C")
    d.say("“完全约束”，整个草图变绿：每条线在哪、多大都定了")
    lab = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QLabel) and w.isVisible() and "完全约束" in w.text()]
    if lab:
        p = d.center(lab[0]); yield d.move(p, 900); d.ring(p)
    yield 3200
    d.say("关闭草图，凸台 8 mm：针夹就出来了（尺寸和 WQ-LS 设计里的针夹一样）")
    yield from steps.leave_and_pad(d, 8)
    yield 3500
    App.ActiveDocument.save()


def main():
    d = Director()
    d.run(script(d))


boot(main)
