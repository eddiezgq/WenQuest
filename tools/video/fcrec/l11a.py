"""第 11 课 片段 A：送布偏心轮——Part 工作台：两个圆柱（R13 偏 3、R8 在轴上），剪切；再“偏移”看 1 mm 的外包络。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps


def cyl(d, label, r, x):
    yield d.tool("Part_Cylinder"); yield 1500
    o = [x_ for x_ in App.ActiveDocument.Objects if x_.TypeId == "Part::Cylinder"][-1]
    p = d.tree_item(o.Label)
    yield d.move(p, 700)
    d.click(p); yield 800
    yield from steps.prop_set(d, str(r), "Cylinder", "Radius")
    yield from steps.prop_set(d, "8", "Cylinder", "Height")
    if x:
        yield from steps.prop_set(d, str(x), ("基本", "Base"), "Placement", ("位置", "Position"), "x")
    App.ActiveDocument.recompute()
    log("cyl", o.Label, o.Radius.Value, o.Height.Value, o.Placement.Base)
    return o


def script(d):
    App.newDocument(L("偏心轮", "Eccentric"))
    yield from steps.pick_workbench(d, "Part", "Part")
    Gui.runCommand("Std_ViewIsometric")
    yield 800
    yield d.say("送布偏心轮：一个直径 26 的圆盘，套在直径 16 的轴上，圆盘中心偏出 3。这种“几个基本体拼起来”的零件，用 Part 工作台最快")
    yield d.say("点“圆柱体”，在属性里改：半径 13、高 8、位置 x = 3")
    big = yield from cyl(d, "big", 13, 3)
    Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("再一个圆柱：半径 8、高 8，留在原点——这是轴孔")
    small = yield from cyl(d, "small", 8, 0)
    Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("先点大圆柱，按住 Ctrl 再点小圆柱，点“剪切”：大的减去小的")
    p = d.tree_item(big.Label)
    yield d.move(p, 800)
    d.click(p); yield 500
    p = d.tree_item(small.Label)
    yield d.move(p, 700)
    d.click(p, mods=Qt.ControlModifier); yield 700
    yield d.tool("Part_CompBoolean" if not d.action_widget("Part_Cut") else "Part_Cut", None if d.action_widget("Part_Cut") else "Part_Cut")
    yield 1800
    cut = [o for o in App.ActiveDocument.Objects if o.TypeId == "Part::Cut"][-1]
    log("cut", round(cut.Shape.Volume, 2))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    yield d.say("偏心轮做好了，体积和整机里的真零件一样。轴一转，圆盘中心绕着轴画圈，推着送布叉上下动")
    yield 2500
    yield d.say("“偏移”：选剪切的结果，点“三维偏移”，距离 1——得到一个大 1 mm 的外包络，查间隙时常用")
    p = d.tree_item(cut.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    names = [a.objectName() for tb in d.mw.findChildren(QtWidgets.QToolBar) if tb.isVisible() for a in tb.actions() if "ffset" in a.objectName()]
    log("offset buttons", names)
    yield d.tool(names[0], None if names[0] == "Part_Offset" else "Part_Offset")
    yield from d.until(lambda: any(isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and w.window() is d.mw and "ffset" in w.objectName()
                                   for w in QtWidgets.QApplication.allWidgets()), 8000)
    yield 1000
    log("offset widgets", [(w.objectName(), w.text()) for w in QtWidgets.QApplication.allWidgets() if w.isVisible()
                           and isinstance(w, QtWidgets.QAbstractSpinBox) and w.objectName()])
    w = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and "ffset" in w.objectName()][0]
    yield from steps.type_into(d, w, "1 mm")
    yield 1500
    yield from steps.task_ok(d)
    off = [o for o in App.ActiveDocument.Objects if o.TypeId == "Part::Offset"][-1]
    log("offset", off.Value, round(off.Shape.Volume, 2))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    yield d.say("偏移以后，原来的剪切收在它下面——还是依赖关系：改圆柱，剪切、偏移一路跟着重算")
    yield 2500
    App.ActiveDocument.saveAs(model_file("偏心轮.FCStd", "Eccentric.FCStd"))
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
