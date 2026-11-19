"""第 5 课 片段 B：电子表格驱动尺寸——表里写中心距，草图的尺寸用表达式引用它；改表，零件跟着变。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, QtCore, L, model_file
import steps


def sheet_view(d):
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, QtWidgets.QTableView) and w.isVisible() and w.model() and w.model().rowCount() > 50:
            return w


def cell_pt(d, tv, row, col):
    return tv.viewport().mapToGlobal(tv.visualRect(tv.model().index(row, col)).center())


def type_cell(d, tv, row, col, text):
    """点单元格，在表格上方的内容栏里键入，回车（和在格子里直接打字一样）"""
    p = cell_pt(d, tv, row, col)
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
    """点主窗口下面的文档标签页"""
    for tb in d.mw.findChildren(QtWidgets.QTabBar):
        if tb.isVisible():
            for i in range(tb.count()):
                if tb.tabText(i).replace("&", "").startswith(text):
                    p = tb.mapToGlobal(tb.tabRect(i).center())
                    yield d.move(p, 700)
                    d.click(p)
                    yield 1000
                    return
    log("no tab", text)


def script(d):
    f = model_file("曲柄草图.FCStd", "CrankSketch.FCStd")
    App.openDocument(f)
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    doc_label = App.ActiveDocument.Label
    yield d.say("上一段的曲柄草图还差中心距。这次不直接写 15.5，而是写进电子表格，让草图去读表——以后改表就行")
    yield from steps.pick_workbench(d, "电子表格", "Spreadsheet")
    yield d.tool("Spreadsheet_CreateSheet"); yield 1200
    yield d.say("模型树里多了 Spreadsheet，双击打开：A1 写名字，B1 写 15.5")
    p = d.tree_item("Spreadsheet")
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: sheet_view(d) is not None)
    yield 900
    tv = sheet_view(d)
    yield from type_cell(d, tv, 0, 0, L("中心距", "centre"))
    yield from type_cell(d, tv, 0, 1, "15.5")
    App.ActiveDocument.recompute()
    log("B1", App.ActiveDocument.Spreadsheet.get("B1"))
    yield d.say("回到模型，双击草图进入编辑")
    yield from mdi_tab(d, doc_label)
    yield from steps.pick_workbench(d, "零件设计", "Part Design")
    t = d.tree()
    for it in t.findItems("Body", Qt.MatchExactly | Qt.MatchRecursive):
        it.setExpanded(True)
    yield 400
    p = d.tree_item("Sketch")
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1000
    yield d.move(d.center(d.vp()), 500)
    yield from d.zoom_to(20, 230)
    yield d.say("选原点和小圆的圆心，点“竖直距离”。弹出的框里先打等号，再写 Spreadsheet.B1，回车")
    c = steps.sketch().Geometry[1].Center
    Gui.Selection.clearSelection()
    yield from steps.pick(d, (0, 0), (c.x, c.y))
    log("sel", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDistanceY")
    yield from d.until(lambda: isinstance(QtWidgets.QApplication.focusWidget(), QtWidgets.QAbstractSpinBox), 6000)
    w = QtWidgets.QApplication.focusWidget()
    yield 600
    d.key(Qt.Key_A, w, Qt.ControlModifier)
    d.keys("=", w=w)
    yield 900
    e = QtWidgets.QApplication.focusWidget()
    log("expr editor", e.metaObject().className() if e else None)
    d.keys("Spreadsheet.B1", w=e)
    yield 1000
    d.key(Qt.Key_Return, e)
    yield 900
    oks = [b for b in QtWidgets.QApplication.allWidgets() if isinstance(b, QtWidgets.QPushButton) and b.isVisible()
           and b.text().replace("&", "") in ("确定", "OK") and b.window() is not d.mw]
    log("datum ok", len(oks))
    if oks:                                   # 尺寸框里点“确定”
        p = d.center(oks[0])
        yield d.move(p, 700)
        d.click(p)
        yield 600
        try:
            if oks[0].isVisible():
                oks[0].click()
        except RuntimeError:
            pass
        yield 700
    App.ActiveDocument.recompute()
    yield 800
    log("dof", steps.dof_text(d))
    log("expr", steps.sketch().ExpressionEngine)
    steps.dump("expr")
    yield d.say("尺寸前面多了个“f(x)”标记：它是算出来的，不是手填的。草图完全约束了")
    yield 2200
    yield d.say("关闭草图，凸台 10 mm，曲柄的板就出来了")
    yield from steps.leave_and_pad(d, 10)
    yield 1500
    yield d.say("现在改表：B1 改成 18，重新计算，曲柄跟着变长")
    yield from mdi_tab(d, "Spreadsheet")
    tv = sheet_view(d)
    yield from type_cell(d, tv, 0, 1, "18")
    yield from mdi_tab(d, doc_label)
    yield d.tool("Std_Refresh"); yield 1500
    App.ActiveDocument.recompute()
    pad = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Pad"][-1]
    c = steps.sketch().Geometry[1].Center
    log("after 18", round(c.y, 3), round(pad.Shape.Volume, 1))
    Gui.SendMsgToActiveView("ViewFit")
    yield 2000
    yield d.say("一张表管住一组尺寸：做系列零件、把计算结果直接带进模型，都靠它")
    yield 2500
    App.ActiveDocument.save()


def main():
    d = Director()
    d.run(script(d))


boot(main)
