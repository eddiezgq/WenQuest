import os
import sys, os
R = os.environ.get("WQ_REC", ".") + "/"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore, QtGui
from director import Director, QtWidgets
os.environ.get("REC_GO") and open(R + "go.flag", "w").close()

def main():
    d = Director(); mw = d.mw
    def find_text(cls, txt):
        for w in mw.findChildren(cls):
            if w.isVisible() and txt in (w.text() if hasattr(w, "text") else ""):
                return w
    T = 1500                                         # 录像开始后先停 1.5 秒
    # 1 开始页：点“打开文件”
    def open_card():
        lab = None
        for w in mw.findChildren(QtWidgets.QLabel):
            if w.isVisible() and w.text().strip() == "打开文件":
                lab = w; break
        p = d.center(lab) if lab else QtCore.QPoint(640, 300)
        d.move(p, 900); QtCore.QTimer.singleShot(1000, lambda: d.click(p, lambda: (App.openDocument(R + "model/WQ-LS.FCStd"), Gui.activeDocument().activeView().viewIsometric(), Gui.SendMsgToActiveView("ViewFit"))))
    d.at(T, open_card)
    # 2 转一圈
    d.at(T + 4500, lambda: (d.move(QtCore.QPoint(1380, 760), 600), d.orbit(7000, 0.9)))
    # 3 模型树：展开“主轴与挑线”，选曲柄
    def tree1():
        p, it = d.tree_pt("主轴与挑线"); d.move(p, 800)
        QtCore.QTimer.singleShot(900, lambda: d.click(p, lambda: it.setExpanded(True)))
    d.at(T + 12500, tree1)
    def tree2():
        p, it = d.tree_pt("crank"); d.move(p, 700)
        def sel():
            Gui.Selection.clearSelection(); Gui.Selection.addSelection(App.ActiveDocument.crank)
        QtCore.QTimer.singleShot(800, lambda: d.click(p, sel))
    d.at(T + 15000, tree2)
    # 4 属性：看“数据”页
    def props():
        tab = None
        for tb in mw.findChildren(QtWidgets.QTabBar):
            for i in range(tb.count()):
                if tb.isVisible() and tb.tabText(i) == "数据":
                    tab = (tb, i)
        if tab:
            p = tab[0].mapToGlobal(tab[0].tabRect(tab[1]).center()); d.move(p, 700)
            QtCore.QTimer.singleShot(800, lambda: d.click(p, lambda: tab[0].setCurrentIndex(tab[1])))
    d.at(T + 17500, props)
    # 5 标准视图：前、俯、右、轴测
    for k, cmd in enumerate(["Std_ViewFront", "Std_ViewTop", "Std_ViewRight", "Std_ViewIsometric"]):
        def v(cmd=cmd):
            p = d.action_pt(cmd) or QtCore.QPoint(580, 42)
            d.move(p, 500); QtCore.QTimer.singleShot(600, lambda: d.click(p, lambda: (Gui.runCommand(cmd), Gui.SendMsgToActiveView("ViewFit"))))
        d.at(T + 21000 + k * 2000, v)
    # 6 放大看机针：选中针杆，“适合选中”
    def zoom():
        Gui.Selection.clearSelection(); Gui.Selection.addSelection(App.ActiveDocument.needle_bar)
        Gui.SendMsgToActiveView("ViewSelection")
    d.at(T + 29500, zoom)
    d.at(T + 32500, lambda: (Gui.Selection.clearSelection(), Gui.SendMsgToActiveView("ViewFit")))
    # 7 工作台：零件设计 → 草图 → AI Parts
    for k, wb in enumerate(["SketcherWorkbench", "AiPartsWorkbench"]):
        def w(wb=wb):
            c = d.wb_combo(); p = d.center(c); d.move(p, 600)
            QtCore.QTimer.singleShot(700, lambda: d.click(p, lambda: Gui.activateWorkbench(wb)))
        d.at(T + 34500 + k * 3000, w)
    d.at(T + 43500, lambda: open(R + "end.flag", "w").close())
    d.run()

def boot():
    Gui.getMainWindow().showMaximized()
    open(R + "ready.flag", "w").close()
    QtCore.QTimer.singleShot(1000, main)
QtCore.QTimer.singleShot(7000, boot)
