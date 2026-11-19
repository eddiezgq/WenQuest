"""第 2 课 片段 B：对象之间的依赖——布尔剪切，改圆柱的半径和位置，结果跟着变。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, QtCore, L
import steps


def script(d):
    App.openDocument(os.path.join(os.environ["WQ_REC"], L("练习", "practice") + ".FCStd"))
    Gui.activateWorkbench("PartWorkbench")
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("打开上一段存的“练习”。在模型树里先点立方体，再按住 Ctrl 点圆柱：两个都选上")
    p = d.tree_item(L("立方体", "Cube"))
    yield d.move(p, 800)
    d.click(p); yield 500
    p = d.tree_item(L("圆柱体", "Cylinder"))
    yield d.move(p, 700)
    d.click(p, mods=Qt.ControlModifier); yield 700
    log("sel", [s.ObjectName for s in Gui.Selection.getSelectionEx()])
    yield d.say("点“剪切”：从立方体里挖掉圆柱。模型树里，立方体和圆柱收进了“剪切”下面——剪切依赖它们")
    yield d.tool("Part_CompBoolean" if not d.action_widget("Part_Cut") else "Part_Cut", None if d.action_widget("Part_Cut") else "Part_Cut")
    yield 1800
    log("objs", [(o.Name, o.TypeId) for o in App.ActiveDocument.Objects])
    t = d.tree()
    for it in t.findItems(L("剪切", "Cut"), Qt.MatchExactly | Qt.MatchRecursive):
        p = t.viewport().mapToGlobal(t.visualItemRect(it).topLeft() + QtCore.QPoint(-12, 9))
        yield d.move(p, 700)
        d.ring(p)
        it.setExpanded(True)
        yield 1500
    yield d.say("改圆柱：在模型树里点圆柱，在属性里把半径改成 3")
    p = d.tree_item(L("圆柱体", "Cylinder"))
    yield d.move(p, 700)
    d.click(p); yield 900
    yield from steps.prop_set(d, "3", "Cylinder", "Radius")
    yield d.say("再把位置改到方块中间：x = 5，y = 5")
    yield from steps.prop_set(d, "5", ("基本", "Base"), "Placement", ("位置", "Position"), "x")
    yield from steps.prop_set(d, "5", ("基本", "Base"), "Placement", ("位置", "Position"), "y")
    App.ActiveDocument.recompute()
    yield 800
    Gui.Selection.clearSelection()
    cut = [o for o in App.ActiveDocument.Objects if o.TypeId == "Part::Cut"][0]
    log("cut volume", round(cut.Shape.Volume, 2), App.ActiveDocument.Cylinder.Radius.Value, App.ActiveDocument.Cylinder.Placement.Base)
    yield d.say("剪切的结果跟着变了：一个穿通的孔。这就是参数化——改前面的对象，后面依赖它的全部自动重算")
    yield 2000
    App.ActiveDocument.save()
    yield 600


def main():
    d = Director()
    d.run(script(d))


boot(main)
