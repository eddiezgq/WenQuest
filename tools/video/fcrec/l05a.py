"""第 5 课 片段 A：曲柄轮廓——两个圆、一条切线、镜像、修剪。真操作，结果存给片段 B。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, model_file
import steps


def circle(d, x, y, dia):
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(d.model_pt(x, y), 900)
    d.click(); yield 500
    yield d.move(d.model_pt(x + dia * 0.4, y + dia * 0.3), 700)
    d.keys(str(dia), enter=True); yield 1000
    d.key(Qt.Key_Escape); yield 600


def script(d):
    yield from steps.new_body_sketch(d, say=False, zoom=(20, 230))
    yield d.say("曲柄的轮廓：下面是套在主轴上的大圆（直径 33），上面是装曲柄销的小圆（直径 22），中心距 15.5")
    yield from circle(d, 0, 0, 33)
    yield from circle(d, 0, 15.5, 22)
    steps.dump("circles")
    yield d.say("右边画一条线，两头分别点在两个圆上")
    yield d.tool("Sketcher_CreateLine"); yield 300
    yield d.move(d.model_pt(16.45, 1.0), 900)
    d.click(); yield 500
    yield d.move(d.model_pt(10.95, 16.5), 900)
    d.click(); yield 600
    d.key(Qt.Key_Escape); yield 600
    steps.dump("line")
    yield d.say("加“相切”：选线、选大圆，点相切；再选线、选小圆，点相切")
    yield from steps.pick(d, (14.5, 6.0), (0, -16.5))
    yield d.tool("Sketcher_ConstrainTangent")
    yield from steps.answer_modal(d)
    yield 800
    yield from steps.pick(d, ("v", 2, 1), (0, 26.5))
    log("sel tan2", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.tool("Sketcher_ConstrainTangent")
    yield from steps.answer_modal(d)
    yield 1000
    log("dof", steps.dof_text(d))
    steps.dump("tangent")
    yield d.say("左边不用再画：选中这条线，点“对称”工具，再点竖轴（Y 轴）——镜像出左边的线")
    Gui.Selection.clearSelection()
    sk = steps.sketch()
    a, b = sk.getPoint(2, 1), sk.getPoint(2, 2)
    yield from steps.pick(d, ((a.x + b.x) / 2, (a.y + b.y) / 2))
    log("sel sym", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.tool("Sketcher_Symmetry")
    yield 900
    cb = [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and isinstance(w, QtWidgets.QCheckBox) and w.text().startswith(("创建对称约束", "Create symmetric"))][0]
    if not cb.isChecked():
        yield d.say("任务栏里勾上“创建对称约束”：左右两条线就一直对称，改一边另一边跟着变")
        p = d.center(cb)
        yield d.move(p, 800)
        d.ring(p)
        cb.click()
        yield 900
    log("sym checkbox", cb.isChecked())
    yield d.move(d.model_pt(0, -24), 900)
    d.click(); yield 1200
    yield from steps.answer_modal(d, wait=800)
    yield 600
    for w in QtWidgets.QApplication.allWidgets():
        if w.isVisible() and isinstance(w, QtWidgets.QAbstractButton) and w.text().replace("&", "") in ("确定", "OK") and w.window() is not d.mw:
            log("sym task ok?", w.window().windowTitle())
    steps.dump("mirrored")
    yield d.say("修剪：点“修剪”工具，再点圆上不要的那一段——大圆上面一段、小圆下面一段")
    yield d.tool("Sketcher_CompCurveEdition", "Sketcher_Trimming"); yield 500
    yield d.move(d.model_pt(0, 16.5), 900)
    d.click(); yield 900
    yield d.move(d.model_pt(0, 4.5), 900)
    d.click(); yield 900
    d.key(Qt.Key_Escape); yield 800
    steps.dump("trimmed")
    log("dof", steps.dof_text(d))
    yield d.say("轮廓出来了：大圆弧、两条切线、小圆弧连成一圈")
    yield 1500
    App.ActiveDocument.saveAs(model_file("曲柄草图.FCStd", "CrankSketch.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
