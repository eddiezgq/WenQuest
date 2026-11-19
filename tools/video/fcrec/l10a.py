"""第 10 课 片段 A：针杆接头——毛坯（第 6 课的凸台，录屏前做好）；建一个基准面：附着在 YZ 平面、往外偏 6（正好是方块的侧面），在上面画 Ø6 的圆，凸台 17 成侧销。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui, Part, Sketcher
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file
import steps

# 针杆接头（整机 nb_link.step）：方块 12 × 14 × 16，竖孔 Ø8，侧面伸出 Ø6 的销 17 长、在高度一半处
def blank():
    doc = App.newDocument(L("针杆接头", "NeedleBarLink"))
    b = doc.addObject("PartDesign::Body", "Body")
    xy = [f for f in b.Origin.OriginFeatures if f.Role == "XY_Plane"][0]
    sk = b.newObject("Sketcher::SketchObject", "Sketch")
    sk.AttachmentSupport = [(xy, "")]
    sk.MapMode = "FlatFace"
    P = [(-6, -7), (6, -7), (6, 7), (-6, 7)]
    for k in range(4):
        sk.addGeometry(Part.LineSegment(App.Vector(*P[k], 0), App.Vector(*P[(k + 1) % 4], 0)))
    for k in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", k, 2, (k + 1) % 4, 1))
    sk.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 4))
    pad = b.newObject("PartDesign::Pad", "Pad")
    pad.Profile = sk
    pad.Length = 16
    doc.recompute()
    sk.Visibility = False
    Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", b)
    log("blank", round(pad.Shape.Volume, 2))
    return doc, b


def script(d):
    doc, body = blank()
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("针杆接头：方块中间一个竖孔（套针杆），侧面伸出一根 Ø6 的销。方块是第 6 课的凸台，已经做好")
    yield 2000
    yield d.say("销要画在侧面上。这次不直接点面，建一个“基准面”：附着在 YZ 平面上，往外偏 6——正好是侧面")
    Gui.Selection.clearSelection()
    yield d.tool("PartDesign_CompDatums", "PartDesign_Plane") if d.action_widget("PartDesign_CompDatums") else d.tool("Part_Datums", "PartDesign_Plane")
    yield from d.until(lambda: steps.named(QtWidgets.QListWidget, "listOfModes") is not None, 8000)
    yield 1200
    yz = [f for f in body.Origin.OriginFeatures if f.Role == "YZ_Plane"][0]
    t = d.tree()
    for it in t.findItems(body.Origin.Label, Qt.MatchExactly | Qt.MatchRecursive):
        it.setExpanded(True)
    yield 500
    p = d.tree_item(yz.Label)
    yield d.move(p, 900)
    d.click(p); yield 900
    log("ref1", steps.named(QtWidgets.QLineEdit, "lineRef1").text(), steps.named(QtWidgets.QLabel, "message").text())
    yield d.say("参照选 YZ 平面，附着模式“平面”；下面的附着偏移量里，Z 方向（面的法向）填 6")
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "attachmentOffsetZ"), "6 mm")
    yield 800
    yield from steps.task_ok(d, gone="listOfModes")
    dp = [o for o in doc.Objects if o.TypeId == "PartDesign::Plane"][-1]
    log("datum", dp.MapMode, dp.AttachmentSupport, dp.AttachmentOffset, dp.Placement)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    yield d.say("基准面贴在方块的侧面上。选中它，新建草图：草图就画在基准面上")
    p = d.tree_item(dp.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("PartDesign_CompSketches", "PartDesign_NewSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1000
    Gui.runCommand("Sketcher_ViewSketch")      # 进草图时视角没自动转正（基准面上的草图）：和点“视图对齐草图”一样
    yield 600
    Gui.SendMsgToActiveView("ViewFit"); yield 500
    yield d.move(d.center(d.vp()), 500)
    yield from steps.zoom_sk(d, 10, 120)
    yield d.say("Ø6 的圆，圆心在竖轴上、高 8（方块高度的一半）")
    yield from steps.circle_on_axis(d, 0, 8, 6, "Sketcher_ConstrainDistanceY", 8)
    yield d.say("关闭草图，凸台 17：销从侧面伸出来")
    yield from steps.leave_and_pad(d, 17)
    pad = [o for o in doc.Objects if o.TypeId == "PartDesign::Pad"][-1]
    log("pin", round(pad.Shape.Volume, 2))
    yield 1200
    yield d.say("基准面的好处：它不依赖某个面的编号。前面的特征改了，面编号变了，基准面和画在上面的销都不会丢")
    yield 3000
    doc.saveAs(model_file("针杆接头.FCStd", "NeedleBarLink.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
