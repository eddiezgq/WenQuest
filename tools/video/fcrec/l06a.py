"""第 6 课 片段 A：针杆——XZ 平面画半个截面（4 × 180 的矩形），绕竖轴“旋转”成圆杆；再画一个 0.2 × 0.5 的小矩形，“挖槽旋转”出一圈油槽。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, model_file
import steps
from steps import sp


def rect(d, u, v, w, h, aim):
    """矩形工具：点第一个角，鼠标往 aim 方向带一下，键入宽、Tab、高、回车"""
    yield d.tool("Sketcher_CompCreateRectangles", "Sketcher_CreateRectangle"); yield 400
    yield d.move(sp(d, u, v), 900)
    d.click(); yield 600
    yield d.move(sp(d, *aim), 700)
    d.keys(str(w)); yield 500
    d.key(Qt.Key_Tab); yield 400
    d.keys(str(h), enter=True); yield 1000
    d.key(Qt.Key_Escape); yield 700


def script(d):
    yield d.say("针杆是一根细长的圆杆：直径 8、长 180。回转体不用一层层拉伸，画半个截面，绕轴转一圈")
    yield from steps.new_body_sketch(d, plane="XZ", say=False, zoom=(10, 120))
    yield d.say("XZ 平面上画半截面：从原点起一个矩形，宽 4（半径）、高 180")
    yield from rect(d, 0, 0, 4, 180, (3, 6))
    Gui.SendMsgToActiveView("ViewFit"); yield 1200
    steps.dump("rect")
    log("dof", steps.dof_text(d))
    yield d.say("矩形左边贴着竖轴——待会儿就绕这根轴转")
    yield 1500
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    yield d.say("点“旋转”：轴默认是“垂直草绘轴”，角度 360°，确定")
    yield d.tool("PartDesign_Revolution")
    yield from d.until(lambda: steps.named(steps.QtWidgets.QComboBox, "axis") is not None)
    yield 1500
    log("axis", steps.named(steps.QtWidgets.QComboBox, "axis").currentText())
    yield from steps.task_ok(d)
    rev = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Revolution"][-1]
    log("rev", rev.ReferenceAxis[1], rev.Angle.Value, round(rev.Shape.Volume, 2))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("一根直径 8 的光杆。下面挖油槽：离下端 39.25 mm，宽 0.5、深 0.2")
    yield from steps.sketch_on(d, "XZ", zoom=(10, 120))
    Gui.SendMsgToActiveView("ViewFit"); yield 900
    yield d.move(sp(d, 4, 39.5), 900)
    yield from d.zoom_to(2, 320, at=sp(d, 4, 39.5))
    yield 600
    yield d.say("放大到杆的右边缘，画一个小矩形：宽 0.2、高 0.5")
    yield from rect(d, 3.8, 39.25, 0.2, 0.5, (3.95, 39.6))
    steps.dump("groove rect")
    yield d.say("矩形的位置用尺寸锁住：选左下角，“水平距离”3.8；再选它，“竖直距离”39.25")
    sk = steps.sketch()
    gi = len(sk.Geometry) - 4
    corner = min(range(4), key=lambda k: (lambda p: p.x + p.y)(sk.getPoint(gi + k, 1)))
    Gui.Selection.clearSelection()
    yield d.move(sp(d, *(lambda p: (p.x, p.y))(sk.getPoint(gi + corner, 1))), 800)
    d.click(); yield 600
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistanceX")
    yield from steps.datum(d, 3.8)
    App.ActiveDocument.recompute(); yield 500
    sk = steps.sketch()
    Gui.Selection.clearSelection()
    yield d.move(sp(d, *(lambda p: (p.x, p.y))(sk.getPoint(gi + corner, 1))), 800)
    d.click(); yield 600
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistanceY")
    yield from steps.datum(d, 39.25)
    App.ActiveDocument.recompute(); yield 600
    steps.dump("groove placed")
    log("dof", steps.dof_text(d))
    yield d.say("完全约束了。关闭草图，点“挖槽旋转”：同样绕竖轴 360°")
    yield 1200
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    yield d.tool("PartDesign_Groove")
    yield from d.until(lambda: steps.named(steps.QtWidgets.QComboBox, "axis") is not None)
    yield 1500
    yield from steps.task_ok(d)
    g = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Groove"][-1]
    log("groove", g.ReferenceAxis[1], round(g.Shape.Volume, 2))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.move(d.model_pt(4, 0, 39.5), 900)
    yield from d.zoom_to(6, 300, at=d.model_pt(4, 0, 39.5))
    yield d.say("一圈油槽出来了。旋转、挖槽旋转是“凸台、凹槽”的回转版：一个加材料，一个去材料")
    yield 2500
    App.ActiveDocument.saveAs(model_file("针杆.FCStd", "NeedleBar.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
