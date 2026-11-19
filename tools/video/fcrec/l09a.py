"""第 9 课 片段 A：手轮——毛坯（第 6 课的旋转，录屏前用程序做好）；腹板上挖一个 Ø20 的减重孔，“环形阵列”成 5 个。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui, Part
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps

# 手轮的半截面（轴向 t、半径 r；t=0 是装在主轴上的那一面）：轮毂 Ø22 × 10（盲孔 Ø10 深 4）、腹板厚 3、轮缘 Ø92–Ø104 宽 16——取自整机 handwheel.step
PROFILE = [(0, 5), (4, 5), (4, 0), (10, 0), (10, 11), (7, 11), (7, 46), (16, 46), (16, 52), (0, 52), (0, 46), (4, 46), (4, 11), (0, 11)]


def blank():
    doc = App.newDocument(L("手轮", "Handwheel"))
    b = doc.addObject("PartDesign::Body", "Body")
    xz = [f for f in b.Origin.OriginFeatures if f.Role == "XZ_Plane"][0]
    sk = b.newObject("Sketcher::SketchObject", "Sketch")
    sk.AttachmentSupport = [(xz, "")]
    sk.MapMode = "FlatFace"
    n = len(PROFILE)
    for i in range(n):
        (t0, r0), (t1, r1) = PROFILE[i], PROFILE[(i + 1) % n]
        sk.addGeometry(Part.LineSegment(App.Vector(r0, t0, 0), App.Vector(r1, t1, 0)))
    for i in range(n):
        sk.addConstraint(__import__("Sketcher").Constraint("Coincident", i, 2, (i + 1) % n, 1))
    rev = b.newObject("PartDesign::Revolution", "Revolution")
    rev.Profile = sk
    rev.ReferenceAxis = (sk, ["V_Axis"])
    rev.Angle = 360
    doc.recompute()
    sk.Visibility = False
    Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", b)
    log("blank", round(rev.Shape.Volume, 2))
    return doc


def script(d):
    blank()
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("手轮：轮毂、薄腹板、外缘。毛坯用第 6 课的“旋转”做好了。腹板上要挖 5 个减重孔")
    yield 2500
    yield d.say("画一个就够：XY 平面开草图，圆心点在竖轴上，直径 20；再锁住离中心 30")
    yield from steps.sketch_on(d, "XY", zoom=(20, 110))
    yield from steps.circle_on_axis(d, 0, 30, 20, "Sketcher_ConstrainDistanceY", 30)
    yield d.say("凹槽：类型“通过所有”，勾“反转”——草图在手轮底面上，反转才是往里挖")
    yield from steps.pocket_through(d)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    pk = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Pocket"][-1]
    yield d.say("选中这个凹槽，点“环形阵列”：轴默认是草图的法向（手轮的轴），次数 5，360° 均布")
    yield from steps.polar(d, pk, 5)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("5 个孔一圈均布。改次数，孔数跟着变；改原来那个孔，5 个一起变")
    yield 2500
    App.ActiveDocument.saveAs(model_file("手轮.FCStd", "Handwheel.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
