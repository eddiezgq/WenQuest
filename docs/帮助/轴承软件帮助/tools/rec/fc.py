# -*- coding: utf-8 -*-
# 轴承 FreeCAD 帮助录屏（第 90 轮）：由 _帮助生成/rec/fcvrec.py 执行（say/do/wait/cut/until 和 action、typecmd 等都来自那里）。
import os

EX = os.path.join(App.getUserAppDataDir(), "Mod", "WenQuest", "examples")


def form():
    import wq_bearing_form as F
    return F._panel[1]


def open_bearing():
    Gui.activateWorkbench("WenQuestWorkbench")
    action("轴承")


def tidy():
    """录屏版面：收起 Python 控制台，表单放宽，模型树收窄，三维视图留在中间。"""
    hide_dock("Python console")
    hide_dock("Tasks")
    dock_width("问渠轴承", 640)
    dock_width("Combo View", 200)


def views():
    """换两个视角（二等角、三等角），看清截面和钢球。"""
    def go(cmd):
        Gui.runCommand(cmd, 0)
        Gui.SendMsgToActiveView("ViewFit")
    QtCore.QTimer.singleShot(0, lambda: go("Std_ViewDimetric"))
    QtCore.QTimer.singleShot(1700, lambda: go("Std_ViewTrimetric"))


def ex(name):
    form().open_file(os.path.join(EX, name + ".wqbearing.json"))


def click(key):
    form().buttons[key].animateClick()


def fc01():
    return [
        do(console, 800),
        say("安装只做一次。在 FreeCAD 的 Python 控制台输入这一行，查到用户数据文件夹。"),
        do(lambda: typecmd("App.getUserAppDataDir()"), 2500),
        say("把压缩包里的 WenQuest 文件夹放进这个文件夹里的 Mod，没有 Mod 就新建一个，然后重启 FreeCAD。"),
        do(wb_popup, 1500),
        say("重启后，在工作台列表里选问渠。"),
        do(wb_close, 300), do(open_bearing, 500), do(tidy, 1500),
        say("工具栏上点轴承，右边出现参数表单，字段和网页版一样。"),
        say("点打开项目，选网页版存的文件。这里打开压缩包里的深沟球轴承示例。"),
        do(lambda: ex("demo-deep-groove"), 1500),
        do(lambda: click("calc"), 2000),
        say("点计算：右边逐项校核，和网页版用同一个计算内核，结果逐项相同。"),
        cut(True), do(lambda: form().model(), 500), cut(False), do(fit, 1500),
        say("点建模：内圈、外圈和全部钢球建成精确实体，按节圆排好，并检查有没有干涉，结果写在表单下面。"),
        say("出图与 STEP 导出每个零件的 STEP 和 A3 工作图。帮助按钮打开随包带的这份帮助，不联网也能看。"),
        wait(1500),
    ]


def fc02():
    return [
        do(open_bearing, 500), do(tidy, 2000),
        say("再看机器人腕关节的四点接触薄壁轴承。打开示例。"),
        do(lambda: ex("demo-thin-x"), 1500), do(lambda: click("calc"), 2500),
        say("计算之后，右边的校核表列出接触角范围、最大接触应力和截面刚度，和网页版相同；每个钢球的载荷图在网页版看。"),
        cut(True), do(lambda: form().model(), 500), cut(False), do(fit, 2000),
        say("建模时，内外圈的沟道按两段圆弧拼成的尖拱形回转成实体，五十六个钢球按节圆排好，再查有没有干涉。"),
        do(views, 3500),
        say("工序简图要选网页版工艺页存的模板，每道磨削和超精出一张简图。"),
        wait(1500),
    ]


CLIPS = {"fc-01-bearing": fc01, "fc-02-bearing-thin": fc02}
