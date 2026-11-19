"""第 10 课 片段 B：参数化——电子表格写方块高 16；凸台长度 = 表格，侧销的高度 = 表格 / 2。把高改成 22，方块变高、销还在正中。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file
import steps


def sheet_view():
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, QtWidgets.QTableView) and w.isVisible() and w.model() and w.model().rowCount() > 50:
            return w


def type_cell(d, tv, row, col, text):
    p = tv.viewport().mapToGlobal(tv.visualRect(tv.model().index(row, col)).center())
    yield d.move(p, 700)
    d.click(p)
    tv.setCurrentIndex(tv.model().index(row, col))
    yield 500
    e = [x for x in QtWidgets.QApplication.allWidgets() if isinstance(x, QtWidgets.QLineEdit) and x.isVisible() and x.objectName() == "cellContent"][0]
    q = d.center(e)
    yield d.move(q, 600)
    d.click(q)
    e.setFocus()
    e.selectAll()
    d.keys(text, w=e)
    yield 500
    d.key(Qt.Key_Return, e)
    yield 800


def mdi_tab(d, text):
    for tb in d.mw.findChildren(QtWidgets.QTabBar):
        if tb.isVisible():
            for i in range(tb.count()):
                if tb.tabText(i).replace("&", "").startswith(text):
                    p = tb.mapToGlobal(tb.tabRect(i).center())
                    yield d.move(p, 700)
                    d.click(p)
                    yield 1000
                    return


def expr_into(d, w, expr):
    """输入框里先打 =，弹出表达式框，键入表达式，回车"""
    steps.show(w)
    yield 300
    p = d.center(w)
    yield d.move(p, 700)
    d.click(p)
    yield 300
    w.setFocus()
    d.key(Qt.Key_A, w, Qt.ControlModifier)
    d.keys("=", w=w)
    yield 900
    e = QtWidgets.QApplication.focusWidget()
    log("expr editor", e.metaObject().className() if e else None)
    d.keys(expr, w=e)
    yield 1000
    d.key(Qt.Key_Return, e)
    yield 900


def script(d):
    doc = App.openDocument(model_file("针杆接头.FCStd", "NeedleBarLink.FCStd"))
    label = doc.Label
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("参数化：让尺寸之间有关系。方块的高写进电子表格；侧销永远在高度正中")
    yield from steps.pick_workbench(d, "电子表格", "Spreadsheet")
    yield d.tool("Spreadsheet_CreateSheet"); yield 1200
    p = d.tree_item("Spreadsheet")
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: sheet_view() is not None)
    yield 900
    tv = sheet_view()
    yield from type_cell(d, tv, 0, 0, L("高", "height"))
    yield from type_cell(d, tv, 0, 1, "16")
    doc.recompute()
    yield from mdi_tab(d, label)
    yield from steps.pick_workbench(d, "零件设计", "Part Design")
    yield d.say("双击凸台：长度框里先打等号，写 Spreadsheet.B1")
    pad = doc.getObject("Pad")
    p = d.tree_item(pad.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: steps.named(QtWidgets.QAbstractSpinBox, "lengthEdit") is not None, 8000)
    yield 900
    yield from expr_into(d, steps.named(QtWidgets.QAbstractSpinBox, "lengthEdit"), "Spreadsheet.B1")
    yield from steps.task_ok(d)
    log("pad expr", pad.ExpressionEngine)
    yield d.say("再双击侧销的草图，双击“竖直距离 8”那条约束，改成 =Spreadsheet.B1 / 2")
    sk = doc.getObject("Sketch001")
    p = d.tree_item(sk.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1000
    k = [i for i, c in enumerate(sk.Constraints) if c.Type == "DistanceY"][0]
    lw = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QListWidget) and w.isVisible()
          and w.count() == len(sk.Constraints)][0]
    it = lw.item(k)
    lw.scrollToItem(it)
    p = lw.viewport().mapToGlobal(lw.visualItemRect(it).center())
    yield d.move(p, 800)
    QtCore.QTimer.singleShot(0, lambda: d.click(p, double=True))   # 尺寸框是模态的（exec）：放到下一轮事件里点，剧本才能接着走
    yield from d.until(lambda: isinstance(QtWidgets.QApplication.focusWidget(), QtWidgets.QAbstractSpinBox), 6000)
    yield 600
    w = QtWidgets.QApplication.focusWidget()
    yield from expr_into(d, w, "Spreadsheet.B1 / 2")
    oks = [b for b in QtWidgets.QApplication.allWidgets() if isinstance(b, QtWidgets.QPushButton) and b.isVisible()
           and b.text().replace("&", "") in ("确定", "OK") and b.window() is not d.mw]
    if oks:
        p = d.center(oks[0])
        yield d.move(p, 600)
        d.click(p)
        yield 600
        try:
            if oks[0].isVisible():
                oks[0].click()
        except RuntimeError:
            pass
        yield 600
    doc.recompute()
    log("sk expr", sk.ExpressionEngine, steps.dof_text(d))
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 900
    yield d.say("现在改表：高 16 改成 22，重新计算")
    yield from mdi_tab(d, "Spreadsheet")
    tv = sheet_view()
    yield from type_cell(d, tv, 0, 1, "22")
    yield from mdi_tab(d, label)
    yield d.tool("Std_Refresh"); yield 1500
    doc.recompute()
    pin = doc.getObject("Pad001")
    log("after 22", pad.Length.Value, sk.Constraints[k].Value, round(pin.Shape.Volume, 2))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("方块高了 6，销自己跟到了新的正中。这就是参数化：设计意图写进模型，改一个数，相关的都跟着变")
    yield 3000
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
