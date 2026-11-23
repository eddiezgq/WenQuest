"""第 20 课 片段 A：圆角半径太大。同一个文件、同样的操作，WQ_STOCK=1 录官方 FreeCAD 1.1.4，否则录问渠 CAD；
两段由 cat_rec.py 接成一个片段。20 mm 方块，所有边倒圆角，半径 11（超过边长的一半，做不出来）：
官方版显示成功、实体其实无效（“检查几何”报错，体积是负的几百亿）；问渠 CAD 当场报错、说清原因，改成 5 就好。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file, menu_path
import steps

STOCK = os.environ.get("WQ_STOCK") == "1"


def tw(cls, name=None, text=None):
    for w in QtWidgets.QApplication.allWidgets():
        try:
            if isinstance(w, cls) and w.isVisible() and (name is None or w.objectName() == name) \
                    and (text is None or w.text().replace("&", "") in text):
                return w
        except RuntimeError:
            continue
    return None


def click_w(d, get, ms=700):
    yield 300
    w = get() if callable(get) else get
    steps.show(w)
    yield 200
    p = d.center(w)
    yield d.move(p, ms)
    d.click(p)
    yield 600


def run_cmd(d, cmd):
    path = steps.menu_find(d, cmd)
    log("menu", cmd, path)
    yield from menu_path(d, *path)


def dump_task(tag):
    out = []
    for w in QtWidgets.QApplication.allWidgets():
        try:
            if w.isVisible() and w.metaObject().className() in ("QCheckBox", "QPushButton", "Gui::QuantitySpinBox", "QLabel", "QTreeWidget", "QTextEdit", "QPlainTextEdit", "QListWidget"):
                t = w.text() if hasattr(w, "text") and callable(w.text) else ""
                out.append((w.metaObject().className(), w.objectName(), str(t)[:40]))
        except RuntimeError:
            pass
    log(tag, out[:80])


def script(d):
    doc = App.openDocument(model_file("圆角练习.FCStd", "FilletTest.FCStd"))
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    who = L("官方 FreeCAD 1.1.4", "Official FreeCAD 1.1.4") if STOCK else L("问渠 CAD", "WenQuest CAD")
    if STOCK:
        yield d.say(L("先看官方 FreeCAD 1.1.4（窗口标题写着 FreeCAD）：一个 20 mm 的方块，所有边倒圆角，半径 11",
                      "First the official FreeCAD 1.1.4 (the title bar says FreeCAD): a 20 mm cube, fillet all edges, radius 11"))
        yield 3500
        yield d.say("半径超过边长的一半，这个圆角本来就做不出来——看软件怎么说")
    else:
        yield d.say(L("同样的文件、同样的操作，换成问渠 CAD", "Same file, same steps, now in WenQuest CAD"))
    yield 3000
    yield from steps.pick_workbench(d, "Part Design", "Part Design")
    yield 800
    box = doc.getObject("Box")
    p = d.tree_item(box.Label)
    yield d.move(p, 700)
    d.click(p)
    yield 600
    yield from run_cmd(d, "PartDesign_Fillet")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None, 6000)
    yield 1500
    dump_task("fillet task")
    allb = tw(QtWidgets.QCheckBox, "checkBoxUseAllEdges") or tw(QtWidgets.QCheckBox, text=("使用全部边", "Use all edges", "所有边"))
    if allb is not None and not allb.isChecked():
        yield from click_w(d, allb)
    rad = tw(QtWidgets.QWidget, "filletRadius")
    if rad is not None:
        yield from click_w(d, rad)
        le = rad.findChild(QtWidgets.QLineEdit)
        le.selectAll()
        d.keys("11", w=le)
        yield 600
        d.key(Qt.Key_Tab, le)
    yield 1500
    fl = [o for o in doc.Objects if o.TypeId == "PartDesign::Fillet"][0]
    log("fillet props", fl.Radius, fl.UseAllEdges if hasattr(fl, "UseAllEdges") else None, fl.Base)
    if abs(fl.Radius.Value - 11) > 1e-6:
        fl.Radius = 11
    if hasattr(fl, "UseAllEdges") and not fl.UseAllEdges:
        fl.UseAllEdges = True
    doc.recompute()
    yield 1000
    yield d.say(L("勾“使用所有边”，半径 11，确定", "Tick “Use all edges”, radius 11, OK"))
    yield 2000
    yield from steps.task_ok(d)
    yield 1500
    m = QtWidgets.QApplication.activeModalWidget()
    log("after ok modal", m.windowTitle() if m else None, m.text() if isinstance(m, QtWidgets.QMessageBox) else None)
    log("fillet state", list(fl.State), fl.Shape.isNull(), None if fl.Shape.isNull() else fl.Shape.isValid())
    dump_task("after ok")
    yield 2500
    if isinstance(m, QtWidgets.QMessageBox):
        yield d.say(L(f"{who}：报错——" + m.text().splitlines()[0][:60], f"{who}: error — " + m.text().splitlines()[0][:80]))
        yield 5000
        yield from steps.answer_modal(d)
    log("end state", list(fl.State))
    if not fl.Shape.isNull() and "Invalid" not in fl.State:
        yield d.say(L(f"{who}：没报错，模型树上一切正常，看起来“成功”了", f"{who}: no error, the tree looks fine — it seems to have “worked”"))
        yield 4000
        p = d.tree_item(fl.Label)
        yield d.move(p, 700)
        d.click(p)
        yield 600
        yield d.say(L("用“检查几何”看看这个实体", "Check it with Check geometry"))
        yield from run_cmd(d, "Part_CheckGeometry")
        yield 2500
        run = tw(QtWidgets.QPushButton, text=("运行检查", "Run check"))
        if run is not None:
            yield from click_w(d, run)
            yield 6000
        dump_task("check geometry")
        for w in QtWidgets.QApplication.allWidgets():
            try:
                if w.isVisible() and w.metaObject().className() in ("QTreeView", "QTreeWidget", "QTextEdit", "QPlainTextEdit", "QTextBrowser"):
                    if hasattr(w, "toPlainText"):
                        log("text", w.metaObject().className(), w.toPlainText()[:1500])
                    else:
                        m = w.model()
                        if m is None:
                            continue
                        rows = []
                        def walk(ix, dep=0):
                            for r in range(m.rowCount(ix)):
                                c = m.index(r, 0, ix)
                                rows.append("  " * dep + " | ".join(str(m.data(m.index(r, k, ix))) for k in range(m.columnCount(ix))))
                                walk(c, dep + 1)
                        walk(QtCore.QModelIndex())
                        log("tree", w.objectName(), rows[:40])
            except RuntimeError:
                pass
        yield d.say(L("检查几何：实体“无效”——壳没连上、面不封闭、边上的曲线不对；三维视图里也显示不出来。这个“成功”的圆角其实是坏的，后面再建什么都建在坏实体上",
                      "Check geometry: the solid is “invalid” — shell not closed, faces open, bad curves on edges; the 3D view cannot even show it. This “successful” fillet is broken, and everything built on it inherits that"))
        yield 7000



def main():
    d = Director()
    d.run(script(d))


boot(main)
