# FreeCAD 帮助录屏的驱动（第 49 轮）：在 FreeCAD 图形界面里按时间表一步步操作，记下字幕时间。
# 用法：freecad drive.py（环境变量 WQ_CLIP 选哪一段，WQ_CUES 写字幕时间的文件）
import json, os, sys, time
import FreeCAD as App, FreeCADGui as Gui
try:
    from PySide import QtCore, QtGui
    QtW = QtGui
except Exception:
    from PySide2 import QtCore, QtGui, QtWidgets as QtW
from PySide2 import QtTest
CLIP = os.environ.get("WQ_CLIP", "fc-02-design")
CUES = []
mw = Gui.getMainWindow()

def cue(text):
    CUES.append({"t": time.time(), "text": text})

def action(text):
    for a in mw.findChildren(QtW.QAction):
        if a.text().replace("&", "") == text:
            a.trigger(); return True
    raise RuntimeError("no action " + text)

def console():
    for n in ("Python console",):
        d = mw.findChild(QtW.QDockWidget, n)
        if d: d.show(); d.raise_()
    return mw.findChild(QtW.QPlainTextEdit, "Python console")

def typecmd(cmd):
    """往控制台里一个字一个字写（不用模拟按键：虚拟显示器的键盘布局会把 ; = 这类符号打错），再回车"""
    c = console(); c.setFocus()
    for ch in cmd:
        c.insertPlainText(ch); QtW.QApplication.processEvents(); time.sleep(0.03)
    QtTest.QTest.keyClick(c, QtCore.Qt.Key_Return)

def design():
    import wqsew_gui
    return wqsew_gui.design(True)

def fit():
    try:
        Gui.activeDocument().activeView().viewIsometric(); Gui.SendMsgToActiveView("ViewFit")
    except Exception: pass

def select(obj):
    Gui.Selection.clearSelection(); Gui.Selection.addSelection(obj)

def top_dialog():
    for w in QtW.QApplication.topLevelWidgets():
        if isinstance(w, QtW.QDialog) and w.isVisible():
            return w

def close_dialogs():
    for w in QtW.QApplication.topLevelWidgets():
        if isinstance(w, QtW.QDialog) and w.isVisible():
            w.reject() if hasattr(w, "reject") else w.close()

STATE = {}

def keyset():
    import wqsew_net as N
    N.save_settings('http://localhost:8090', open(os.environ['WQ_KEYFILE']).read().strip())

def S_install():
    return [
        (1500, lambda: (Gui.activateWorkbench("StartWorkbench") if "StartWorkbench" in Gui.listWorkbenches() else None, cue("安装只做一次。先在 Python 控制台问 FreeCAD：用户数据文件夹在哪？"), console())),
        (2500, lambda: typecmd("App.getUserAppDataDir()")),
        (3500, lambda: cue("在这个文件夹里的 Mod 文件夹中，放进压缩包里的 WenQuestSewing 文件夹，然后重启 FreeCAD")),
        (5000, lambda: (cue("重启后，在工作台下拉列表里选“问渠缝纫机”"), wb_combo_popup())),
        (3000, lambda: (wb_combo_close(), Gui.activateWorkbench("WenQuestSewingWorkbench"))),
        (1500, lambda: cue("工具栏出现 16 个中文按钮：新建五种机型、重算、校核、时序、转动、导出导入、提交、AI、零件库、帮助")),
        (6000, None),
    ]

def wb_combo_popup():
    for cb in mw.findChildren(QtW.QComboBox):
        if cb.count() > 5 and any("FEM" in cb.itemText(i) or "Part" in cb.itemText(i) for i in range(cb.count())):
            STATE["cb"] = cb; cb.showPopup(); return
def wb_combo_close():
    cb = STATE.get("cb")
    if cb: cb.hidePopup()

def S_design():
    return [
        (1200, lambda: (Gui.activateWorkbench("WenQuestSewingWorkbench"), cue("点“新建平缝机设计”：按教材算例生成 16 个机构零件和 21 项校核"))),
        (1500, lambda: (action("新建平缝机设计"), fit())),
        (3000, lambda: (select(design()), cue("模型树里选中“平缝机设计”，属性面板里就是全部设计参数（P_ 开头）"), show_props())),
        (4500, lambda: cue("把转速 P_n 改成 6000，按 Ctrl+R 重算")),
        (1500, lambda: (setattr(design(), "P_n", 6000.0), App.ActiveDocument.recompute(), select(design()))),
        (2500, lambda: (cue("Status 变成“不合格 2 项”。点“校核结果”看红绿灯——和网页版一字不差"), action("校核结果"))),
        (6000, lambda: (close_dialogs(), cue("针杆组件减到 0.10 kg、机壳一阶固有频率提到 240 Hz，再重算"))),
        (1500, lambda: (setattr(design(), "P_mr", 0.10), setattr(design(), "P_fn", 240.0), App.ActiveDocument.recompute(), select(design()))),
        (3000, lambda: (cue("又全部合格。点“转动机构”让主轴转起来看运动"), action("转动机构"))),
        (7000, lambda: action("转动机构")),
        (1000, None),
    ]

def show_props():
    for n in ("Property view", "Combo View", "Model"):
        d = mw.findChild(QtW.QDockWidget, n)
        if d: d.show()
    for tw in mw.findChildren(QtW.QTabWidget):          # 组合视图切到“Model”页（模型树 + 属性）
        for i in range(tw.count()):
            if tw.tabText(i) in ("Model", "模型"):
                tw.setCurrentIndex(i)

def S_checks():
    p = os.environ.get("WQ_PARAMS", "")
    return [
        (1200, lambda: (Gui.activateWorkbench("WenQuestSewingWorkbench"), action("新建平缝机设计"), fit(), show_props(), cue("“时序图”：针杆、钩线窗口、送布、挑线的时序"))),
        (2500, lambda: action("时序图")),
        (5000, lambda: (close_dialogs(), cue("“导入参数”：读网页版导出的参数文件（这一份是网页版存的 6000 r/min 方案）"))),
        (2500, lambda: (select(design()), __import__("wqsew_feature").import_params(design(), p), select(design()))),
        (2000, lambda: (cue("导入后重算：校核结论和数值与网页版完全相同"), action("校核结果"))),
        (6000, lambda: close_dialogs()),
        (800, None),
    ]

def S_ai():
    import wqsew_gui as G
    keyset()
    def open_ai():
        STATE["d"] = G.AiDialog(design()); STATE["d"].show(); STATE["d"].move(300, 80)
    def say(t):                                     # 中文不能用 keyClicks：一个字一个字插进去，看着像在打字
        ed = STATE["d"].ed; ed.setPlainText(""); ed.setFocus()
        for i, ch in enumerate(t):
            QtCore.QTimer.singleShot(70 * i, lambda ch=ch: ed.insertPlainText(ch))
    return [
        (1200, lambda: (Gui.activateWorkbench("WenQuestSewingWorkbench"), action("新建平缝机设计"), fit(), show_props(), cue("“AI 助手”：在 FreeCAD 里一句话改设计（要联网和钥匙；本录像用规则版）"))),
        (2500, open_ai),
        (1500, lambda: say("转速 6000，针杆组件质量 0.10，机壳一阶固有频率 240")),
        (2600, lambda: (cue("点“起草改法”：问渠服务器上的计算核心重算把关，给出对照表"), STATE["d"].run("draft"))),
        (6000, lambda: (cue("通过了，点“采用”：直接改设计对象的属性并重算"), STATE["d"].apply())),
        (4000, lambda: (cue("“写设计说明”：每个数都由程序核对过"), STATE["d"].run("describe"))),
        (5000, lambda: (STATE["d"].close(), select(design()), show_props(), cue("属性已经改好：转速 6000、针杆 0.10 kg、机壳 240 Hz，全部合格"))),
        (5000, None),
    ]

def S_parts():
    import wqsew_gui as G
    keyset()
    def open_p():
        STATE["d"] = G.PartsDialog(); STATE["d"].show(); STATE["d"].move(280, 80)
    def search():
        STATE["d"].q.setText(""); QtTest.QTest.keyClicks(STATE["d"].q, "NC", delay=120); STATE["d"].load()
    def pick():
        for i, p in enumerate(STATE["d"].items):
            if p["code"] == "NC-150":
                STATE["d"].lst.setCurrentRow(i)
    return [
        (1200, lambda: (Gui.activateWorkbench("WenQuestSewingWorkbench"), action("新建平缝机设计"), fit(), show_props(), cue("“插入本单位零件”：查本单位零件库（要联网和钥匙）"))),
        (2500, open_p),
        (2500, lambda: (cue("按编号查找：NC 开头的针杆曲柄系列"), search())),
        (2500, lambda: (pick(), cue("选 NC-150：能用到当前设计的“刺布曲柄”（曲柄半径 15）"))),
        (3500, lambda: (cue("“插入三维”：STEP 插进当前文档，带本单位编号和 ERP 物料号"), STATE["d"].insert())),
        (3500, lambda: (cue("“用到当前设计”：把孔距写进曲柄半径并重算"), use())),
        (4000, lambda: (STATE["d"].close(), fit())),
        (3000, None),
    ]

def use():
    d = STATE["d"]; uses = getattr(d, "_uses", [])
    u = next((x for x in uses if x["label"] == "刺布曲柄"), uses[0] if uses else None)
    if u:
        import wqsew_feature as F
        done = F.apply_params(design(), u["params"]); d.info.setText("已用到设计（{}）：{}".format(u["label"], done))

def S_fem():
    return [
        (1200, lambda: (Gui.activateWorkbench("WenQuestSewingWorkbench"), action("新建平缝机设计"), fit(), show_props(), cue("FreeCAD 本机有限元：用 FreeCAD 自带的 Gmsh 和 CalculiX"))),
        (2500, lambda: (cue("在 Python 控制台输入一行：零件、约束、载荷和网页版完全一样"), console())),
        (1500, lambda: (cue("建好的是一套普通的 FreeCAD 有限元分析：网格、轴孔固定、销孔加力，CalculiX 求解"), typecmd("import wqsew_fem; r = wqsew_fem.run(); print(r)"))),
        (3000, "wait_fem"),
        (500, lambda: (fit(), cue("应力云图：最大等效应力在销孔边上；控制台里打印了最大应力和安全系数"))),
        (7000, lambda: cue("模型树里切到 FEM 工作台，可以自己改约束、载荷、网格再算")),
        (5000, None),
    ]

def S_case_ls():   # 第 52 轮 案例一（FreeCAD）
    os.makedirs("/home/claude/fc/out", exist_ok=True)
    def setp(**kw):
        d = design()
        for k, v in kw.items():
            setattr(d, "P_" + k, float(v))
        App.ActiveDocument.recompute(); select(d)
    return [
        (1200, lambda: (Gui.activateWorkbench("WenQuestSewingWorkbench"), cue("案例一（FreeCAD）：点“新建平缝机设计”，生成 16 个机构零件和 21 项校核"))),
        (1500, lambda: (action("新建平缝机设计"), fit())),
        (4000, lambda: (select(design()), show_props(), cue("选中“平缝机设计”，属性里把转速 P_n 改成 6000，Ctrl+R 重算"))),
        (2500, lambda: setp(n=6000)),
        (1500, lambda: (cue("不合格 2 项：针杆惯性力、机壳共振。和网页版一样"), action("校核结果"))),
        (5500, lambda: (close_dialogs(), cue("P_mr 改成 0.10（针杆组件减重），P_fn 改成 240（机壳加筋），再重算"))),
        (2500, lambda: setp(mr=0.10, fn=240)),
        (1500, lambda: (cue("全部合格"), action("校核结果"))),
        (4500, lambda: (close_dialogs(), cue("本机有限元：控制台一行，FreeCAD 自带的 Gmsh + CalculiX，受力按 6000 r/min 自动加"), console())),
        (1500, lambda: typecmd("import wqsew_gui, wqsew_feature as F, wqsew_fem; d = wqsew_gui.design(True); r = wqsew_fem.run(d); print(r)")),
        (3000, "wait_fem"),
        (500, lambda: (fit(), cue("针杆曲柄的应力云图；控制台打印了最大应力和安全系数"))),
        (6500, lambda: cue("导出 STEP：16 个零件，交给结构设计或任何 CAD")),
        (1500, lambda: typecmd('F.export_step(d, "/home/claude/fc/out/ls-6000.step")')),
        (4000, lambda: cue("服务器上的 CAE（模态、动力学、减重、数控、电机选型）在网页版做；参数文件两边互通")),
        (5000, None),
    ]

SCRIPTS = {"fc-07-case-ls": S_case_ls, "fc-01-install": S_install, "fc-02-design": S_design, "fc-03-checks": S_checks, "fc-04-ai": S_ai, "fc-05-parts": S_parts, "fc-06-fem": S_fem}

def run():
    mw.setGeometry(0, 0, 1280, 720); mw.showMaximized()
    for b in mw.findChildren(QtW.QPushButton):          # 第一次启动的欢迎页：点“Done”
        if b.text() in ("Done", "完成") and b.isVisible():
            b.click()
    steps = SCRIPTS[CLIP]()
    def nxt(i):
        if i >= len(steps):
            json.dump(CUES, open(os.environ["WQ_CUES"], "w"), ensure_ascii=False)
            QtCore.QTimer.singleShot(300, lambda: os._exit(0)); return
        delay, fn = steps[i]
        if fn == "wait_fem":                             # 等本机有限元算完（CalculiX 求解时界面会卡住）
            def poll():
                d = App.listDocuments().get("FEM_NeedleCrank")
                done = d and any(o.isDerivedFrom("Fem::FemResultObject") and len(getattr(o, "vonMises", []) or []) for o in d.Objects)
                if done:
                    cue("__cut_end__"); QtCore.QTimer.singleShot(1500, lambda: nxt(i + 1))
                else:
                    QtCore.QTimer.singleShot(500, poll)
            QtCore.QTimer.singleShot(delay, lambda: (cue("__cut_start__"), poll()))   # 从真正开始等的时候剪（上一步打字时不剪）
            return
        def go():
            nxt(i + 1)                      # 先排好下一步：这一步可能打开模态对话框（exec_ 会卡住）
            try:
                if fn: fn()
            except Exception as e:
                print("STEP ERROR", i, e, file=sys.stderr)
        QtCore.QTimer.singleShot(delay, go)
    nxt(0)

QtCore.QTimer.singleShot(4000, run)
