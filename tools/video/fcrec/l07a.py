"""第 7 课 片段 A：针杆两头倒角 0.5——选两条端面圆边，倒角。做完和整机里的真针杆体积一样。真操作。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, model_file
import steps


def second_groove(doc):
    """上一课“跟着做”第 3 步：第二圈油槽（竖直距离 41.25）。录屏前补上，不在画面里做"""
    b = doc.getObject("Body")
    s1 = doc.getObject("Sketch001")
    s2 = b.newObject("Sketcher::SketchObject", "Sketch002")
    s2.AttachmentSupport = s1.AttachmentSupport
    s2.MapMode = s1.MapMode
    for g in s1.Geometry:
        s2.addGeometry(g)
    for c in s1.Constraints:
        s2.addConstraint(c)
    k = [i for i, c in enumerate(s2.Constraints) if c.Type == "DistanceY"][0]
    s2.setDatum(k, App.Units.Quantity("41.25 mm"))
    g = b.newObject("PartDesign::Groove", "Groove001")
    g.Profile = s2
    g.ReferenceAxis = (s2, ["V_Axis"])
    g.Angle = 360
    doc.recompute()
    s2.Visibility = False
    log("groove2", round(g.Shape.Volume, 2))


def end_edge_pt(d, z):
    """端面圆边上朝着镜头的那一点"""
    v = Gui.ActiveDocument.ActiveView.getViewDirection()
    n = math.hypot(v.x, v.y) or 1
    return d.model_pt(-4 * v.x / n, -4 * v.y / n, z)


def script(d):
    doc = App.openDocument(model_file("针杆.FCStd", "NeedleBar.FCStd"))
    second_groove(doc)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("接着上一课的针杆，两圈油槽都做好了。真针杆两头还各有 0.5 的倒角：装进轴套不刮、不伤手")
    yield d.move(d.center(d.vp()), 600)
    yield from d.zoom_to(10, 70)
    Gui.SendMsgToActiveView("ViewFit"); yield 600
    yield d.say("点选下端的圆边，按住 Ctrl 再点上端的圆边")
    Gui.Selection.clearSelection()
    p = end_edge_pt(d, 0)
    yield d.move(p, 900)
    d.click(p); yield 700
    p = end_edge_pt(d, 180)
    yield d.move(p, 1100)
    d.click(p, mods=Qt.ControlModifier); yield 700
    log("sel", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.say("点“倒角”，大小 0.5，确定")
    yield d.tool("PartDesign_Chamfer")
    yield from d.until(lambda: any(isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and "ize" in w.objectName()
                                   for w in QtWidgets.QApplication.allWidgets()))
    yield 1200
    sp_ = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and "ize" in w.objectName()]
    log("chamfer widgets", [(w.objectName(), w.text()) for w in sp_])
    yield from steps.type_into(d, sp_[0], "0.5 mm")
    yield from steps.task_ok(d)
    ch = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Chamfer"][-1]
    log("chamfer", ch.Size.Value, [s for s in ch.Base[1]], round(ch.Shape.Volume, 2))
    yield d.move(end_edge_pt(d, 180), 800)
    yield from d.zoom_to(10, 230, at=end_edge_pt(d, 180))
    yield d.say("体积 9036.86 mm³：和整机 STEP 里的真针杆一样——尺寸、油槽、倒角一处不差")
    yield 2500
    Gui.SendMsgToActiveView("ViewFit")
    yield d.say("圆角也是这样：选边，点“圆角”，填半径。倒角、圆角都是“修饰特征”，加在零件做好以后")
    yield 2500
    App.ActiveDocument.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
