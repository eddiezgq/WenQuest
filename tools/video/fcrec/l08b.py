"""第 8 课 片段 B：挑线簧——路径（R9.35 圆弧 265° + 切线 14.85）和截面（Ø0.7 的圆）各画一个草图，“添加式管道”（扫掠）。真操作。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps
from steps import sp

R = 9.35


def arc_pt(ang, sk=None):
    g = (sk or steps.sketch()).Geometry[0]
    a = math.radians(ang)
    return (g.Center.x + g.Radius * math.cos(a), g.Center.y + g.Radius * math.sin(a))


def line_mid():
    g = steps.sketch().Geometry[1]
    return ((g.StartPoint.x + g.EndPoint.x) / 2, (g.StartPoint.y + g.EndPoint.y) / 2)


def script(d):
    yield d.say("扫掠：一个截面沿着一条路径走一遍。挑线簧是一根直径 0.7 的钢丝，弯成 R9.35 的圆弧再伸出一段直腿")
    yield from steps.new_body_sketch(d, say=False, zoom=(20, 200))
    yield d.say("先画路径。圆弧：圆心点原点，起点点在横轴上，绕一大圈到右下方")
    yield d.tool("Sketcher_CompCreateArc", "Sketcher_CreateArc"); yield 300
    yield d.move(d.model_pt(0, 0), 800)
    d.click(); yield 400
    yield d.move(d.model_pt(R, 0), 700)
    d.click(); yield 300
    for ang in (30, 70, 110, 150, 190, 230, 255):
        yield d.move(d.model_pt(R * math.cos(math.radians(ang)), R * math.sin(math.radians(ang))), 300)
    yield d.move(d.model_pt(R * math.cos(math.radians(265)), R * math.sin(math.radians(265))), 400)
    d.click(); yield 500
    d.key(Qt.Key_Escape); yield 600
    steps.dump("arc")
    yield d.say("从圆弧的终点画一条直线，大致顺着圆弧的方向")
    sk = steps.sketch()
    e = sk.Geometry[0].EndPoint
    a = math.atan2(e.y, e.x)
    t = (-math.sin(a), math.cos(a))
    yield d.tool("Sketcher_CreateLine"); yield 300
    yield d.move(d.model_pt(e.x, e.y), 800)
    d.click(); yield 400
    yield d.move(d.model_pt(e.x + 14 * t[0] + 0.8, e.y + 14 * t[1] + 0.5), 900)
    d.click(); yield 500
    d.key(Qt.Key_Escape); yield 600
    steps.dump("line")
    yield d.say("加约束：圆弧半径 9.35、圆心角 265°；直线和圆弧相切，长 14.85")
    Gui.Selection.clearSelection()
    yield from steps.pick(d, arc_pt(135))
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainRadius")
    yield from steps.datum(d, 9.35)
    App.ActiveDocument.recompute(); yield 400
    Gui.Selection.clearSelection()
    yield from steps.pick(d, arc_pt(135))
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainAngle")
    yield from steps.datum(d, 265)
    App.ActiveDocument.recompute(); yield 400
    steps.dump("arc dims")
    Gui.Selection.clearSelection()
    yield from steps.pick(d, line_mid(), arc_pt(200))
    yield d.tool("Sketcher_ConstrainTangent")
    yield from steps.answer_modal(d)
    yield 600
    App.ActiveDocument.recompute(); yield 400
    Gui.Selection.clearSelection()
    yield from steps.pick(d, line_mid())
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistance")
    yield from steps.datum(d, 14.85)
    App.ActiveDocument.recompute(); yield 600
    steps.dump("path")
    log("dof", steps.dof_text(d))
    path = steps.sketch()
    yield d.say("路径完全约束了。关闭草图")
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    yield d.say("再画截面：XZ 平面，圆心在圆弧的起点（横轴上、离原点 9.35）；放大，加直径 0.7、水平距离 9.35")
    Gui.Selection.clearSelection()
    path.ViewObject.Visibility = False      # 路径正好压在截面草图的横轴上：先藏起来，免得点圆心时点到它
    yield 300
    yield from steps.sketch_on(d, "XZ", zoom=(20, 200))
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(sp(d, R, 0), 900)
    d.click(); yield 500
    yield d.move(sp(d, R + 0.6, 0.8), 600)  # 圆太小，键入的直径不一定接得住：点第二下定个大概，再加直径约束
    d.click(); yield 700
    d.key(Qt.Key_Escape); yield 600
    sk = steps.sketch()
    log("circle", [str(g) for g in sk.Geometry])
    yield d.move(sp(d, R, 0), 800)
    yield from d.zoom_to(2, 300, at=sp(d, R, 0))      # 放大看清楚这个小圆，再锁位置
    if not any(c.Type == "Diameter" for c in sk.Constraints):
        Gui.Selection.clearSelection()
        g = sk.Geometry[0]
        yield from steps.pick_sp(d, (g.Center.x, g.Center.y + g.Radius))
        yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDiameter")
        yield from steps.datum(d, 0.7)
        App.ActiveDocument.recompute(); yield 400
    sk = steps.sketch()
    c = sk.Geometry[0].Center
    p = sp(d, c.x, c.y)
    yield d.move(p, 700)
    d.ring(p)                        # 圆心压在横轴上：直接选圆心那个点
    Gui.Selection.addSelection(App.ActiveDocument.Name, sk.Name, "Vertex1")
    yield 500
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistanceX")
    yield from steps.datum(d, 9.35)
    App.ActiveDocument.recompute(); yield 600
    steps.dump("profile")
    log("dof", steps.dof_text(d))
    prof = steps.sketch()
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    path.ViewObject.Visibility = True
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 900
    yield d.say("选中截面草图，点“添加式管道”；在面板里点路径旁的“对象”，再到视图里点一下路径")
    p = d.tree_item(prof.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("PartDesign_AdditivePipe")
    yield from d.until(lambda: steps.named(QtWidgets.QToolButton, "buttonSpineBase") is not None, 8000)
    yield 1200
    b = steps.named(QtWidgets.QToolButton, "buttonSpineBase")
    p = d.center(b)
    yield d.move(p, 800)
    d.click(p); yield 900
    x, y = arc_pt(135, path)
    p = d.model_pt(x, y, 0)
    yield d.move(p, 1000)
    d.click(p); yield 1200
    pipe = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::AdditivePipe"][-1]
    log("spine", pipe.Spine, steps.named(QtWidgets.QLineEdit, "spineBaseEdit").text())
    if b.isChecked():
        p = d.center(b)
        yield d.move(p, 700)
        d.click(p); yield 800
    yield from steps.task_ok(d)
    pipe = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::AdditivePipe"][-1]
    log("pipe", pipe.Spine[1] if pipe.Spine else None, round(pipe.Shape.Volume, 2), pipe.Shape.isValid())
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("钢丝沿着路径弯出来了。路径和截面分开画：改路径，弹簧形状跟着变")
    yield 2500
    App.ActiveDocument.saveAs(model_file("挑线簧.FCStd", "CheckSpring.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
