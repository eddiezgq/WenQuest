"""第 2 课 片段 A：新建、加对象、撤销 / 重做、保存。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps


def script(d):
    yield d.say("开始页点“空文件”：新建一个空文档")
    lab = d.find(QtWidgets.QLabel, L("空文件", "Empty File"))
    p = d.center(lab)
    yield d.move(p, 900)
    d.click(p)
    yield from d.until(lambda: App.ActiveDocument is not None)
    yield 1000
    yield d.say("工作台换成“零件”（Part）：它有现成的立方体、圆柱这些基本体")
    yield from steps.pick_workbench(d, "零件", "Part")
    yield d.say("点“立方体”：10 × 10 × 10 的方块出现在原点；模型树里多了一项")
    yield d.tool("Part_Box"); yield 1200
    Gui.SendMsgToActiveView("ViewFit"); yield 600
    yield d.say("再点“圆柱”：半径 2、高 10")
    yield d.tool("Part_Cylinder"); yield 1400
    log("objs", [o.Name for o in App.ActiveDocument.Objects])
    yield d.say("撤销（Ctrl+Z 或工具栏的弯箭头）：圆柱没了")
    yield d.tool("Std_Undo"); yield 1600
    log("after undo", [o.Name for o in App.ActiveDocument.Objects])
    yield d.say("重做（Ctrl+Y）：圆柱又回来了。撤销可以一步步往回退很多步")
    yield d.tool("Std_Redo"); yield 1600
    log("after redo", [o.Name for o in App.ActiveDocument.Objects])
    yield d.say("保存（Ctrl+S）：第一次保存要起名字，文件扩展名是 .FCStd")
    yield d.tool("Std_Save")
    yield from steps.file_dialog(d, L("练习", "practice"))
    yield 800
    log("saved", App.ActiveDocument.FileName)
    yield d.say("窗口下面的标签页显示了文件名。以后再按 Ctrl+S 就直接存，不再问")
    yield 2500


def main():
    d = Director()
    d.run(script(d))


boot(main)
