"""第 9 课 片段 B：手轮外缘的 48 道防滑槽——画一道（Ø2.4 的圆、圆心离轴 52.6，比外圆 R52 多出一截），挖穿，“环形阵列”48 个。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, model_file
import steps


def script(d):
    App.openDocument(model_file("手轮.FCStd", "Handwheel.FCStd"))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("手轮外缘一圈防滑槽：48 道。还是只画一道：XY 平面上一个直径 2.4 的圆，圆心在横轴上、离中心 52.6")
    yield from steps.sketch_on(d, "XY", zoom=(20, 110))
    yield d.move(d.model_pt(52.6, 0), 800)
    yield from d.zoom_to(10, 220, at=d.model_pt(52.6, 0))
    yield from steps.circle_on_axis(d, 52.6, 0, 2.4, "Sketcher_ConstrainDistanceX", 52.6)
    yield d.say("圆有一半在外圆以外：挖穿以后，外缘上就是一道半圆槽")
    yield 1500
    yield from steps.pocket_through(d)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    pk = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Pocket"][-1]
    yield d.say("环形阵列：次数 48")
    yield from steps.polar(d, pk, 48)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    yield d.move(d.model_pt(40, -40, 16), 900)
    yield from d.zoom_to(10, 60, at=d.model_pt(40, -40, 16))
    yield d.say("一道槽变 48 道，每道 7.5°。两次阵列，手轮就和整机里的一样了")
    yield 2500
    App.ActiveDocument.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
