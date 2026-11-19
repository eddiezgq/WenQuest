"""第 3 课 片段 B：多段线、圆弧、圆、构造线——画针夹的轮廓（先不管尺寸准不准，第 4 课加约束）。真操作，结果存成文件给第 4 课用。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, model_file, Qt, QtWidgets
import steps




def script(d):
    yield from steps.new_body_sketch(d, say=False, zoom=(10, 300))
    yield d.say("针夹的轮廓：上面一段圆弧，下面一个方耳朵。先用“多段线”画三条直边")
    yield d.tool("Sketcher_CreatePolyline"); yield 300
    pts = [(3.5, -4.3), (3.5, -7), (-3.5, -7), (-3.5, -4.3)]
    yield d.move(d.model_pt(*pts[0]), 900)
    d.click(); yield 400
    for x, y in pts[1:]:
        yield d.move(d.model_pt(x, y), 800)
        d.click(); yield 400
    yield d.say("右键结束多段线（工具还开着就按 Esc 退出）")
    d.click(button=Qt.RightButton, ring=False); yield 500
    d.key(Qt.Key_Escape); yield 700
    steps.dump("poly")
    yield d.say("圆弧工具：先点圆心（原点），再点起点，绕过上面，到终点")
    yield d.tool("Sketcher_CompCreateArc", "Sketcher_CreateArc"); yield 300
    yield d.move(d.model_pt(0, 0), 800)
    d.click(); yield 400
    yield d.move(d.model_pt(3.5, -4.3), 700)
    d.click(); yield 300
    for x, y in ((5.4, -1), (4.2, 3.5), (0, 5.5), (-4.2, 3.5), (-5.4, -1)):
        yield d.move(d.model_pt(x, y), 350)
    yield d.move(d.model_pt(-3.5, -4.3), 350)
    d.click(); yield 500
    d.key(Qt.Key_Escape); yield 600
    steps.dump("arc")
    yield d.say("中间的孔：圆工具，圆心在原点，直径 8")
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(d.model_pt(0, 0), 800)
    d.click(); yield 400
    yield d.move(d.model_pt(2.5, 2), 600)
    d.keys("8", enter=True); yield 900
    d.key(Qt.Key_Escape); yield 600
    yield d.say("再画一条竖的中心线，切换成“构造线”（蓝色虚线：只帮忙定位，不成形）")
    yield d.tool("Sketcher_CreateLine"); yield 300
    yield d.move(d.model_pt(0, -8.5), 800)
    d.click(); yield 400
    yield d.move(d.model_pt(0, 7.5), 900)
    d.click(); yield 500
    d.key(Qt.Key_Escape); yield 500
    sk = steps.sketch()
    Gui.Selection.clearSelection(); Gui.Selection.addSelection(sk, f"Edge{len(sk.Geometry)}")
    yield d.tool("Sketcher_ToggleConstruction"); yield 1200
    Gui.Selection.clearSelection()
    steps.dump("final")
    yield d.say("轮廓画好了，但尺寸是点出来的，不准——右边写着还有几个自由度。第 4 课用约束把它定死")
    yield 4500
    App.ActiveDocument.saveAs(model_file("针夹草图.FCStd", "NeedleClampSketch.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
