# -*- coding: utf-8 -*-
# 缝纫机 FreeCAD 帮助录屏（第 95 轮，带配音）：由 docs/帮助/_帮助生成/rec/fcvrec.py 执行（say/do/wait/cut/until 和 action、hide_dock 等都来自那里）。
#   fc-08-proto：六种机型都有三维零件、能转；花样机改坏 → 部件涂红 → 校核结果双击红灯 → 停到出问题的那一针，慢转
#   fc-09-video：出三维讲解片（选语言、配旁白）→ 服务器出好 → 在浏览器里打开（浏览器那一段另用网页录屏接上，见 README）
# 环境：WQ_SEWING_SERVER（问渠网址）、WQ_KEYFILE（FreeCAD 钥匙）；“在浏览器里打开”的网址写到 WQ_URLFILE。
import os


def start():
    Gui.activateWorkbench("WenQuestSewingWorkbench")
    hide_dock("Python console")
    hide_dock("Report view")
    for d in mw.findChildren(QtW.QDockWidget):          # 左边模型树 + 属性放宽，看得清“进度”和参数
        if d.objectName() in ("Combo View", "Model", "Property view") or d.windowTitle() in ("Combo View", "Model"):
            d.setMinimumWidth(330)
    key = open(os.environ["WQ_KEYFILE"]).read().strip() if os.environ.get("WQ_KEYFILE") else ""
    import wqsew_net as N
    N.save_settings(os.environ.get("WQ_SEWING_SERVER", "http://localhost:8088"), key)

    def keep(url):                                   # 录屏机上没有浏览器：记下要打开的网址，浏览器那一段另录
        with open(os.environ.get("WQ_URLFILE", "/tmp/wq_url.txt"), "w") as f:
            f.write(url.toString())
        return True
    QtGui.QDesktopServices.openUrl = staticmethod(keep)


def fitall():
    try:
        v = Gui.activeDocument().activeView()
        v.viewIsometric()
        v.fitAll()
    except Exception:
        pass


def design():
    import wqsew_gui
    return wqsew_gui.design(True)


def select_design():
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(design())
    for tw in mw.findChildren(QtW.QTabWidget):          # 组合视图切到“模型”页（模型树 + 属性）
        for i in range(tw.count()):
            if tw.tabText(i) in ("Model", "模型"):
                tw.setCurrentIndex(i)


def setp(**kw):
    d = design()
    for k, v in kw.items():
        setattr(d, "P_" + k, float(v))
    select_design()


def new(cmd):
    action(cmd)
    fitall()
    Gui.Selection.clearSelection()


def spin():
    action("转动机构")


def checks_table():
    for w in QtW.QApplication.topLevelWidgets():
        if isinstance(w, QtW.QDialog) and w.isVisible() and w.windowTitle().startswith("校核结果"):
            return w.findChild(QtW.QTableWidget)


def pick_red():
    """校核表里选中第一行红灯，停一下再双击（和用户双击一样走 cellDoubleClicked）"""
    t = checks_table()
    for r in range(t.rowCount()):
        if t.item(r, 0).text() in ("不合格", "✕ 不合格") or "不合格" in t.item(r, 0).text():
            t.setCurrentCell(r, 1)
            t.selectRow(r)
            t.setFocus()
            STATE["row"] = r
            return


def dbl_red():
    checks_table().cellDoubleClicked.emit(STATE.get("row", 0), 0)


def video_dlg():
    for w in QtW.QApplication.topLevelWidgets():
        if isinstance(w, QtW.QDialog) and w.isVisible() and w.windowTitle().startswith("出三维讲解片"):
            return w


def fc08():
    return [
        do(start, 1500),
        do(lambda: new("新建绷缝机设计"), 2500),
        say("FreeCAD 版也有六种机型的三维零件。新建一台绷缝机设计：引针、弯针、撑线器、送布都生成零件，和网页版样机是同一套。"),
        do(spin, 300),
        say("点“转动机构”，主轴转起来，零件跟着动。"),
        do(spin, 600),
        do(lambda: App.closeDocument(App.ActiveDocument.Name), 600),
        do(lambda: new("新建花样机设计"), 2500),
        do(select_design, 600), do(spin, 300),
        say("花样机、刺绣机按针走，横机按趟走：工作台按这台设计的花样一针一针走，属性里的“进度”写着第几针。"),
        do(spin, 600), do(select_design, 600),
        say("在属性里把设计转速改成 3000，点“重新计算”。"),
        do(lambda: setp(n=3000), 900), do(lambda: action("重新计算"), 600), do(lambda: Gui.Selection.clearSelection(), 1500),
        say("红灯项对应的部件涂红：机针、模板压框和机头；黄灯涂橙。全部合格就是原来的颜色。"),
        do(lambda: action("校核结果"), 2000),
        say("打开“校核结果”，双击红灯那一行。"),
        do(pick_red, 1200), do(dbl_red, 1500),
        say("三维停到出问题的那一针：第 40 针，出问题的部件选中，状态栏写着停在哪里。"),
        do(spin, 300),
        say("再点“转动机构”，从这里每格 1 度慢转，一格一格看出问题的过程。"),
        wait(2500), do(spin, 600),
        say("改坏别的机型也一样：平缝机停在出问题的主轴转角，横机停在出问题的那一趟。"),
        wait(800),
    ]


def fc09():
    return [
        do(start, 1500),
        do(lambda: new("新建花样机设计"), 2000),
        do(lambda: setp(n=2000), 600), do(lambda: action("重新计算"), 1500),
        say("FreeCAD 里也能出三维讲解片。这台花样机设计转速 2000，有红灯。点工具栏上的“出三维讲解片”。"),
        do(lambda: action("出三维讲解片"), 2000),
        say("选字幕语言；“配旁白”默认勾上。要联网和钥匙，钥匙在网页版零件库里生成。"),
        cut(True), do(lambda: video_dlg().go.click(), 500),
        until(lambda: video_dlg().web.isEnabled(), 120), cut(False), wait(800),
        say("服务器写好了场景，正在配旁白、出关键画面，和网页版一模一样；写着这段片子慢放哪几项。"),
        say("出好就在浏览器里打开这段视频的页面，网页版“三维视频”里也找得到。"),
        do(lambda: video_dlg().accept(), 800),
    ]


CLIPS = {"fc-08-proto": fc08, "fc-09-video": fc09}
