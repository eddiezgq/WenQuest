"""第 15 课 片段 A：曲柄滑块（针杆机构）装配——新建装配，插入 4 个零件（机架、上轴曲柄、连杆、针杆组件），第一个自动固定。真操作。"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_dir
import steps

PARTS = [L("机架", "Frame"), L("上轴曲柄", "ShaftCrank"), L("连杆", "Rod"), L("针杆组件", "NeedleBarAssy")]


def part_list():
    ws = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QTreeWidget) and w.objectName() == "partList" and w.isVisible()]
    return ws[0] if ws else None


def script(d):
    folder = os.path.join(model_dir(), "slider")
    for name in PARTS:
        App.openDocument(os.path.join(folder, name + ".FCStd"))
    doc = App.newDocument(L("曲柄滑块", "SliderCrank"))
    doc.saveAs(os.path.join(folder, L("曲柄滑块", "SliderCrank") + ".FCStd"))   # 插入别的文件里的零件前，装配文件要先存盘
    Gui.runCommand("Std_ViewIsometric")
    yield 1200
    yield d.say("装配：针杆机构是一个曲柄滑块——上轴带着曲柄转，连杆推着针杆上下走。四个零件的文件已经打开，装配文件也存好了")
    yield from steps.pick_workbench(d, "装配", "Assembly")
    yield d.say("点“创建装配”，再点“插入组件”")
    yield d.tool("Assembly_CreateAssembly"); yield 1500
    yield d.tool("Assembly_Insert", "Assembly_InsertLink") if not d.action_widget("Assembly_InsertLink") else d.tool("Assembly_InsertLink")
    yield from d.until(lambda: part_list() is not None, 8000)
    yield 1200
    yield d.say("在列表里点零件，就插进来了。第一个点机架——它会问要不要固定：选“是”，机架就是不动的基准")
    t = part_list()
    for k, name in enumerate(PARTS):
        t = part_list()
        it = [t.topLevelItem(i).child(0) for i in range(t.topLevelItemCount())
              if t.topLevelItem(i).childCount() and t.topLevelItem(i).child(0).text(0) == name][0]
        t.scrollToItem(it)
        p = t.viewport().mapToGlobal(t.visualItemRect(it).center())
        yield d.move(p, 900)
        QtCore.QTimer.singleShot(0, lambda p=p: d.click(p))    # 第一次插入会弹“要不要固定”（模态框）：放到下一轮事件里点，剧本接着走
        yield 1200
        if k == 0:
            yield from steps.answer_modal(d, texts=("Yes", "是"), wait=4000)
            yield 800
        log("inserted", name, [(o.Label, str(o.Placement.Base)) for o in doc.Objects if o.TypeId == "App::Link"])
    yield d.say("后插的零件会错开一点放，免得叠在一起；位置不用管，下一段加“关节”时它们会自己就位")
    yield from steps.task_ok(d, gone="partList")
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    asm = [o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject"][0]
    links = [o for o in doc.Objects if o.TypeId == "App::Link"]
    log("links", [(o.Name, o.Label) for o in links], "grounded", [o.Label for o in doc.Objects if "Ground" in o.TypeId or "Ground" in o.Name])
    yield d.say("模型树里：机架下面多了一个“固定”。其余三个零件各有 6 个自由度——3 个移动、3 个转动")
    yield 3000
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
