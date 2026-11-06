# -*- coding: utf-8 -*-
# 凸轮 FreeCAD 帮助录屏（第 90 轮）：由 _帮助生成/rec/fcvrec.py 执行（say/do/wait/cut/until 和 action、typecmd 等都来自那里）。
import os

EX = os.path.join(App.getUserAppDataDir(), "Mod", "WenQuest", "examples")


def open_cam(name):
    """点“凸轮”：文件对话框这里直接给示例路径（录屏里不弹系统的文件窗口）。"""
    Gui.activateWorkbench("WenQuestWorkbench")
    QtGui.QFileDialog.getOpenFileName = staticmethod(lambda *a, **k: (os.path.join(EX, name + ".wqcam.json"), ""))
    action("凸轮")


def tree_select(label):
    doc = App.ActiveDocument
    o = [x for x in doc.Objects if x.Label == label][0]
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(o)
    STATE["drv"] = o


def turn():
    """转角每 80 ms 加 6°，转一整圈。"""
    o = STATE["drv"]
    STATE["a"] = 0.0

    def step():
        STATE["a"] += 6.0
        o.Angle = STATE["a"]
        Gui.updateGui()
        if STATE["a"] < 360:
            QtCore.QTimer.singleShot(80, step)
    step()


def fc01():
    return [
        do(console, 800),
        say("安装只做一次。在 FreeCAD 的 Python 控制台输入这一行，查到用户数据文件夹。"),
        do(lambda: typecmd("App.getUserAppDataDir()"), 2500),
        say("把压缩包里的 WenQuest 文件夹放进这个文件夹里的 Mod，没有 Mod 就新建一个，然后重启 FreeCAD。"),
        do(wb_popup, 1500),
        say("重启后，在工作台列表里选问渠，工具栏上点凸轮，选网页版存的项目。这里用挑线槽凸轮示例。"),
        do(wb_close, 300),
        cut(True), do(lambda: open_cam("sewing-takeup-groove"), 1500), cut(False),
        say("软件用和网页版同一个计算内核重算校核，建出槽凸轮和滚子的实体。"),
        do(close_dialogs, 300), do(report, 300), do(fit, 1500),
        say("校核摘要在报告视图里，和网页版逐项相同。缺许用值的项目同样写未知。"),
        do(lambda: tree_select("转角"), 800), do(turn, 3000),
        say("改属性 Angle，凸轮转动，滚子跟着走。"),
        wait(2500),
    ]


def fc02():
    return [
        say("凸轮系统：打开加工中心换刀机构的示例。弧面分度凸轮按加工方法建精确实体，大约一分钟。"),
        cut(True), do(lambda: open_cam("atc-globoidal"), 1500), cut(False),
        do(close_dialogs, 300), do(fit, 2000),
        say("建好了：弧面分度凸轮、转塔与滚子、槽凸轮和换刀臂，按网页版三维里的位置装配。"),
        do(lambda: tree_select("凸轮系统"), 800), do(turn, 1000),
        say("在模型树里选凸轮系统，改属性 Angle，转塔和换刀臂按时序转动、上下拔插。"),
        wait(3000),
        say("导出时每个零件给出 STEP、加工程序和一张 A3 工作图，技术要求留给工程师填。"),
        wait(1500),
    ]


CLIPS = {"fc-01-cam": fc01, "fc-02-cam-system": fc02}
