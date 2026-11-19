"""第 1 课 片段 C：首选项——单位、导航方式、语言在哪里改。真操作（看完按“取消”，不改设置）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, QtCore, menu_path, L


def page(d, text):
    """首选项左边的分类列表里点一项"""
    for w in QtWidgets.QApplication.allWidgets():
        if w.isVisible() and isinstance(w, (QtWidgets.QListView, QtWidgets.QTreeView)) and w.window().objectName().startswith("Gui__Dialog__DlgPreferences"):
            m = w.model()
            stack = [QtCore.QModelIndex()]
            while stack:
                par = stack.pop()
                for r in range(m.rowCount(par)):
                    ix = m.index(r, 0, par)
                    if m.data(ix) == text:
                        if isinstance(w, QtWidgets.QTreeView):
                            w.expand(par)
                            w.scrollTo(ix)
                        return w.viewport().mapToGlobal(w.visualRect(ix).center())
                    stack.append(ix)
    return None


def script(d):
    yield d.say("菜单“编辑 → 首选项”：软件的各种设置都在这里")
    yield from menu_path(d, L("编辑", "Edit"), L("首选项", "Preferences"))
    yield from d.until(lambda: QtWidgets.QApplication.activeModalWidget() is not None)
    dlg = QtWidgets.QApplication.activeModalWidget()
    log("dlg", dlg.objectName(), dlg.windowTitle())
    yield 1200
    names = []
    for w in dlg.findChildren(QtWidgets.QAbstractItemView):
        if w.isVisible():
            m = w.model(); names.append([m.data(m.index(r, 0)) for r in range(m.rowCount())])
    log("pages", names)
    yield d.say("“常规”页的“语言和数字格式”：界面语言、默认单位系统（标准 mm / kg / s，或英制）、小数位数")
    p = page(d, L("常规", "General"))
    if p:
        yield d.move(p, 800); d.click(p); yield 1200
    log("groups", [w.title() for w in dlg.findChildren(QtWidgets.QGroupBox) if w.isVisible()])
    for txt in (L("语言", "Language"),):
        g = [w for w in dlg.findChildren(QtWidgets.QGroupBox) if w.isVisible() and txt in w.title()]
        log("group", txt, [x.title() for x in g])
        if g:
            p = d.center(g[0]); yield d.move(p, 800); d.ring(p); yield 1500
            cb = [c for c in g[0].findChildren(QtWidgets.QComboBox) if "mm" in c.currentText()]
            if cb:
                p = d.center(cb[0]); yield d.move(p, 700); d.ring(p); yield 2600
    yield d.say("“显示 → 导航栏”：导航方式（CAD、Blender、触摸板……）也可以在这里换")
    p = page(d, L("显示", "Display"))
    if p:
        yield d.move(p, 800); d.click(p); yield 900
    pg = None
    for w in dlg.findChildren(QtWidgets.QAbstractItemView):
        if w.isVisible() and isinstance(w, QtWidgets.QTreeView):
            m = w.model()
            def walk(par, out):
                for r in range(m.rowCount(par)):
                    ix = m.index(r, 0, par); out.append(m.data(ix)); walk(ix, out)
            allp = []; walk(QtCore.QModelIndex(), allp); log("allpages", allp)
    p = page(d, L("导航栏", "Navigation"))
    if p:
        yield d.move(p, 800); d.click(p); yield 1200
    tabs = [w for w in dlg.findChildren(QtWidgets.QTabBar) if w.isVisible()]
    for tb in tabs:
        for i in range(tb.count()):
            if L("导航", "Navigation") in tb.tabText(i):
                p = tb.mapToGlobal(tb.tabRect(i).center()); yield d.move(p, 700); d.click(p); yield 1500
    log("tabs", [[tb.tabText(i) for i in range(tb.count())] for tb in tabs], "combos", [c.currentText() for c in dlg.findChildren(QtWidgets.QComboBox) if c.isVisible()])
    combo = [w for w in dlg.findChildren(QtWidgets.QComboBox) if w.isVisible() and "CAD" in w.currentText()]
    log("combo", [c.currentText() for c in combo])
    if combo:
        p = d.center(combo[0]); yield d.move(p, 800); d.ring(p); yield 2400
    yield d.say("看完按“取消”，什么都不改")
    b = [w for w in dlg.findChildren(QtWidgets.QPushButton) if w.isVisible() and w.text().replace("&", "") in ("取消", "Cancel")]
    if b:
        p = d.center(b[0]); yield d.move(p, 800); d.click(p); yield 1500
    yield 1000


def main():
    d = Director()
    d.run(script(d))


boot(main)
