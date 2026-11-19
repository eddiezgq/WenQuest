"""第 13 课 片段 A：两张轮廓曲面互相修剪——两个拉伸都勾上“创建实体”，求“交集”：留下机头的外形。看三处折棱。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps


def resolid(d, e):
    """选中拉伸，属性栏里“Solid”改成 是"""
    p = d.tree_item(e.Label)
    yield d.move(p, 800)
    d.click(p); yield 800
    yield from steps.prop_bool(d, e, "Solid", True, ("拉伸", "Extrude"), "Solid")
    App.ActiveDocument.recompute()
    yield 800
    log("solid", e.Label, e.Solid, e.Shape.ShapeType)


def script(d):
    doc = App.openDocument(model_file("机头曲面.FCStd", "HeadSurface.FCStd"))
    sec = [o for o in doc.Objects if o.TypeId == "Part::Section"]
    for o in sec:
        doc.removeObject(o.Name)
    doc.recompute()
    e1, e2 = [o for o in doc.Objects if o.TypeId == "Part::Extrusion"][:2]
    mesh = [o for o in doc.Objects if o.TypeId == "Mesh::Feature"][0]
    mesh.ViewObject.Visibility = False
    for o in (e1, e2):
        o.ViewObject.Visibility = True
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield from steps.pick_workbench(d, "Part", "Part")
    yield d.say("曲面：接着上一课的两张轮廓曲面。要互相修剪，先让它们围成实体：选拉伸，属性里“Solid”改成“是”")
    yield from resolid(d, e1)
    yield from resolid(d, e2)
    Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("选两个拉伸，点“交集”：只留两者都有的部分——两张曲面互相修剪掉多余的")
    p = d.tree_item(e1.Label)
    yield d.move(p, 800)
    d.click(p); yield 500
    p = d.tree_item(e2.Label)
    yield d.move(p, 700)
    d.click(p, mods=Qt.ControlModifier); yield 700
    yield d.tool("Part_CompBoolean", "Part_Common")
    yield 2500
    c = [o for o in doc.Objects if o.TypeId in ("Part::Common", "Part::MultiCommon")][-1]
    doc.recompute()
    log("common", c.Label, round(c.Shape.Volume, 1), len(c.Shape.Faces), c.Shape.isValid())
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    v = d.model_pt(-55, 0, 228)
    yield d.move(v, 900)
    yield from d.zoom_to(30, 200, at=v)
    yield d.say("机头的外形出来了。转着看几条棱：左边那条——前上角的弯面和左侧平面在这里折了一下，有棱")
    yield 2500
    yield d.move(d.model_pt(-40, 66, 240), 900)
    yield d.say("前上角两侧：弯面和 R14 的圆角面交成一道尖棱。这些“折了一下”的地方，就是只有 G0（位置连续）")
    yield 3000
    Gui.SendMsgToActiveView("ViewFit"); yield 600
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
