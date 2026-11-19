"""第 1 课 片段 A：认识界面——打开 WQ-LS 整机，逐块看：菜单、工具栏、工作台、模型树、属性、三维视图、导航立方体、报告视图、状态栏。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, QtCore
import steps

M = os.path.join(os.environ.get("WQ_REC", "."), "model")


def show(d, w, text, ms=2600, rect=None):
    d.say(text)
    p = d.center(w, rect)
    yield d.move(p, 800)
    d.ring(p)
    yield ms


def script(d):
    d.say("开始页：新建、打开文件、示例。点“打开文件”，打开 WQ-LS 平缝机整机")
    lab = d.find(QtWidgets.QLabel, "打开文件")
    p = d.center(lab)
    yield d.move(p, 900)
    d.ring(p)
    App.openDocument(os.path.join(M, "WQ-LS.FCStd"))       # 同点“打开文件”后在对话框里选文件
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 2500
    mw = d.mw
    yield from show(d, mw.menuBar(), "最上面是菜单：文件、编辑、视图、工具……所有命令都在这里", rect=QtCore.QRect(0, 0, 500, 22))
    tb = d.action_widget("Std_New")
    yield from show(d, tb, "下面是工具栏：常用命令的按钮。鼠标停在按钮上会显示它是什么")
    yield from show(d, d.wb_combo(), "工作台下拉框：零件设计、草图、装配、工程图、有限元……换工作台，工具栏跟着换")
    t = d.tree()
    yield from show(d, t, "左上是模型树：文件里的每个对象。WQ-LS 按部件分了八组")
    pv = [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.metaObject().className() == "Gui::PropertyEditor::PropertyEditor"]
    if pv:
        yield from show(d, pv[0], "左下是属性：选中一个对象，它的位置、颜色、尺寸都在这里")
    yield from show(d, d.vp(), "中间最大的是三维视图，零件在这里看、在这里点选")
    vp = d.vp()
    yield from show(d, vp, "右上角是导航立方体：点它的面，就转到那个方向看", rect=QtCore.QRect(vp.width() - 170, 0, 170, 170))
    d.say("报告视图：软件的提示、警告、出错都写在这里（视图 → 面板 → 报告视图）")
    docks = {w.objectName(): w for w in d.mw.findChildren(QtWidgets.QDockWidget)}
    log("docks", list(docks))
    rep = docks.get("Report view")
    rep and rep.setVisible(True)
    yield 1200
    if rep:
        p = d.center(rep); yield d.move(p, 800); d.ring(p)
    yield 2800
    sb = mw.statusBar()
    yield from show(d, sb, "最下面是状态栏：鼠标指着什么、当前的导航方式、单位", rect=QtCore.QRect(sb.width() - 420, 0, 420, sb.height()))
    rep and rep.setVisible(False)
    yield 600
    d.say("这就是 FreeCAD 的界面。问渠 CAD 是在它上面改的，界面一样")
    yield 3000


def main():
    d = Director()
    d.run(script(d))


boot(main)
