"""第 15 课 片段 B：加关节——旋转（上轴在轴承里）、旋转（连杆大头套曲柄销）、旋转（连杆小头套接头销）、滑动（针杆在针杆套里）。零件自己就位，最后剩 1 个自由度。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_dir
import steps

PARTS = [L("机架", "Frame"), L("上轴曲柄", "ShaftCrank"), L("连杆", "Rod"), L("针杆组件", "NeedleBarAssy")]
F, C, R, N = PARTS
# 每个关节：命令、两边（零件，边，边圆心——零件文件里的坐标），字幕
JOINTS = [
    ("Assembly_CreateJointRevolute", (F, "Edge4", (51, 0, 200)), (C, "Edge2", (51, 0, 200)),
     L("旋转关节：选机架上轴承孔的圆边，再选上轴上同一处的圆边——上轴只能绕轴线转", "Revolute: the bearing bore edge on the frame, then the matching edge on the shaft—the shaft can only turn about its axis")),
    ("Assembly_CreateJointRevolute", (C, "Edge180", (6, 0, 215.5)), (R, "Edge15", (6, 0, 215.5)),
     L("旋转关节：曲柄销端头的圆边，连杆大头孔的圆边——连杆套在曲柄销上", "Revolute: the end edge of the crank pin, the big-end bore edge of the rod—the rod rides on the crank pin")),
    ("Assembly_CreateJointRevolute", (R, "Edge20", (6, 0, 160.5)), (N, "Edge36", (6, 0, 160.5)),
     L("旋转关节：连杆小头孔，针杆接头上的销", "Revolute: the rod's small-end bore and the pin on the needle-bar link")),
    ("Assembly_CreateJointSlider", (F, "Edge16", (0, 0, 182)), (N, "Edge31", (0, 0, 168.5)),
     L("滑动关节：针杆套的孔边，针杆的圆边——针杆只能沿轴线上下走", "Slider: the bush bore edge and a needle-bar edge—the bar can only slide along its axis")),
]


def pick(d, doc, asm, part, edge, c):
    link = [o for o in doc.Objects if o.TypeId == "App::Link" and o.Label == part][0]
    g = link.Placement.multVec(App.Vector(*c))
    p = d.model_pt(g.x, g.y, g.z)
    yield d.move(p, 900)
    d.ring(p)       # 圆边常被别的零件挡住、很细：直接选中这条边（和点中它一样），位置就是点的位置
    Gui.Selection.addSelection(doc.Name, asm.Name, f"{link.Name}.{edge}", g.x, g.y, g.z)
    yield 900


def script(d):
    doc = App.openDocument(os.path.join(model_dir(), "slider", L("曲柄滑块", "SliderCrank") + ".FCStd"))
    for name in PARTS:
        App.openDocument(os.path.join(model_dir(), "slider", name + ".FCStd"))
    App.setActiveDocument(doc.Name)
    asm = [o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject"][0]
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield from steps.pick_workbench(d, "装配", "Assembly")
    yield d.say("重新打开文件后，先双击模型树里的“Assembly”，把装配激活——关节按钮才能用")
    p = d.tree_item(asm.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield 1500
    log("active", Gui.ActiveDocument.ActiveView.getActiveObject("part"))
    yield d.say("关节告诉软件零件之间怎么连。一个关节：点关节按钮，在两个零件上各选一个几何元素（圆边、面），确定")
    for k, (cmd, a, b, say) in enumerate(JOINTS):
        Gui.Selection.clearSelection()
        yield d.say(say)
        yield d.tool(cmd)
        yield from d.until(lambda: any(w.isVisible() and w.objectName() == "jointType" for w in QtWidgets.QApplication.allWidgets()), 8000)
        yield 1000
        yield from pick(d, doc, asm, *a)
        yield from pick(d, doc, asm, *b)
        yield 1200
        yield from steps.task_ok(d, gone="jointType")
        doc.recompute()
        js = [o for o in doc.Objects if hasattr(o, "JointType")]
        log("joint", k, [(j.Label, j.JointType) for j in js][-1:] if js else None,
            [(o.Label, [round(x, 1) for x in (o.Placement.Base.x, o.Placement.Base.y, o.Placement.Base.z)]) for o in doc.Objects if o.TypeId == "App::Link"])
        Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("四个关节加完，零件都到了自己的位置。数一数：曲柄能转（1 个自由度），连杆、针杆跟着它走——整个机构只剩 1 个自由度")
    yield 3500
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
