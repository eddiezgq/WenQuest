"""第 20 课 片段 B：改尺寸与重算。WQ_STOCK=1 录官方 FreeCAD 1.1.4，否则录问渠 CAD；cat_rec.py 接成一段。
① 草图里有一个多余的尺寸（左右两条竖边各标了 20），把宽度 30 改成 40：官方版退回、报“无效”；问渠 CAD 改成 40，另外提示多余约束。
② 方块 → 圆角 2 → 挖孔；把方块改成 3 mm（圆角做不出来）、重算：官方版后面的“挖孔”显示正常，其实还是旧形状；
   问渠 CAD 把它标成“要重算”。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file, menu_path
import steps

STOCK = os.environ.get("WQ_STOCK") == "1"


def alive(w):
    try:
        return w.isVisible()
    except RuntimeError:
        return False


def find(cls, name=None, text=None):
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, cls) and alive(w) and (name is None or w.objectName() == name) \
                and (text is None or w.text().replace("&", "") in text):
            return w
    return None


def run_cmd(d, cmd):
    path = steps.menu_find(d, cmd)
    log("menu", cmd, path)
    yield from menu_path(d, *path)


def modal_text():
    m = QtWidgets.QApplication.activeModalWidget()
    if isinstance(m, QtWidgets.QMessageBox):
        return m.text()
    return None


def script(d):
    who = L("官方 FreeCAD 1.1.4", "Official FreeCAD 1.1.4") if STOCK else L("问渠 CAD", "WenQuest CAD")
    # ① 草图
    doc = App.openDocument(model_file("草图冗余.FCStd", "SketchRedundant.FCStd"))
    sk = doc.getObject("Sketch")
    yield 1000
    yield d.say(L(f"{who}：一张草图，矩形 30 × 20；左右两条竖边各标了 20——多了一个，是多余的约束",
                  f"{who}: a sketch, a 30 × 20 rectangle; both vertical sides are dimensioned 20 — one of them is redundant"))
    p = d.tree_item(sk.Label)
    yield d.move(p, 700)
    d.click(p, double=True)
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None, 6000)
    yield 1500
    Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    lw = find(QtWidgets.QListWidget, "listWidgetConstraints")
    log("constraints list", lw is not None)
    item = None
    if lw is not None:
        for i in range(lw.count()):
            t = lw.item(i).text()
            if "30" in t:
                item = lw.item(i)
                break
        log("items", [lw.item(i).text() for i in range(lw.count())])
    yield d.say(L("把宽度 30 改成 40：双击这个尺寸，输入 40，确定", "Change the width 30 to 40: double-click the dimension, type 40, OK"))
    yield 2000
    if item is not None:
        lw.scrollToItem(item)
        yield 300
        q = lw.viewport().mapToGlobal(lw.visualItemRect(item).center())
        yield d.move(q, 700)
        QtCore.QTimer.singleShot(0, lambda: d.click(q, double=True))     # 双击会弹出模态对话框：放到下一轮事件里，剧本照常往下走
    else:
        Gui.runCommand("Sketcher_EditConstraint")
    yield 1800
    dlg = QtWidgets.QApplication.activeModalWidget()
    log("datum dlg", dlg.windowTitle() if dlg else None)
    if dlg is not None:
        log("dlg children", [(w.metaObject().className(), w.objectName()) for w in dlg.findChildren(QtWidgets.QWidget)][:30],
            QtWidgets.QApplication.focusWidget().metaObject().className() if QtWidgets.QApplication.focusWidget() else None)
        le = QtWidgets.QApplication.focusWidget()
        if not isinstance(le, QtWidgets.QLineEdit) or not dlg.isAncestorOf(le):
            les = [w for w in dlg.findChildren(QtWidgets.QLineEdit) if w.objectName() == "qt_spinbox_lineedit" and alive(w)]
            le = les[0] if les else None
        if le is not None:
            le.setFocus()
            le.selectAll()
            d.keys("40", w=le)
            yield 800
            log("typed", le.text())
            if not le.text().startswith("40"):
                le.setText("40 mm")
                yield 500
        ok = [b for b in dlg.findChildren(QtWidgets.QPushButton) if alive(b) and b.text().replace("&", "") in ("OK", "确定")]
        if ok:
            pp = d.center(ok[0])
            yield d.move(pp, 600)
            d.ring(pp)
            QtCore.QTimer.singleShot(0, ok[0].click)
    yield 2000
    t = modal_text()
    dx = [c for c in sk.Constraints if c.Type == "DistanceX"][0]
    log("after datum", t, dx.Value, list(sk.RedundantConstraints))
    if t:
        yield d.say(L(f"{who}：" + t.replace("\n", " ")[:70], f"{who}: " + t.replace("\n", " ")[:90]))
        yield 5000
        yield from steps.answer_modal(d)
        yield 1000
    log("dx final", dx.Value)
    if abs(dx.Value - 40) < 1e-6:
        yield d.say(L("宽度改成了 40；多余的那个尺寸照样标出来提醒你删掉，但不妨碍改别的尺寸",
                      "The width is now 40; the redundant dimension is still reported so you can delete it, but it does not block other changes"))
    else:
        yield d.say(L(f"没有任何提示，宽度又变回 {dx.Value:.0f}（只在报告视图里留了一行英文：Datum 40 mm … is invalid）——多余的是另一个尺寸，宽度却改不了",
                      f"No message at all; the width snaps back to {dx.Value:.0f} (only one line in the report view: Datum 40 mm … is invalid) — another dimension is redundant, yet the width cannot be changed"))
    yield 5000
    Gui.ActiveDocument.resetEdit()
    yield 800
    App.closeDocument(doc.Name)
    yield 800

    # ② 前面失败，后面的特征
    doc = App.openDocument(model_file("失败重算.FCStd", "RecomputeAfterFail.FCStd"))
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield d.say(L("第二个：方块 20 mm，倒圆角 2，再挖一个孔（Part 工作台，模型树：方块 → 圆角 → 挖孔）",
                  "Second: a 20 mm box, fillet 2, then a hole cut (Part workbench; tree: Box → Fillet → Cut)"))
    yield 4500
    box = doc.getObject("Box")
    p = d.tree_item(box.Label)
    tr = d.tree()
    if tr is not None:
        tr.expandAll()
    yield d.move(p, 700)
    d.click(p)
    yield 700
    yield d.say(L("把方块改成 4 mm：圆角 2 正好是边长的一半，做不出来", "Make the box 4 mm: a fillet of 2 is half the edge, impossible"))
    for prop in ("Length", "Width", "Height"):
        yield from steps.prop_set(d, "4 mm", ("Box", "Box"), prop)
        if abs(getattr(box, prop).Value - 4) > 1e-6:
            setattr(box, prop, 4)
    yield 600
    yield from run_cmd(d, "Std_Refresh")
    yield 2500
    if doc.getObject("Cut").isValid() and "Touched" in doc.getObject("Box").State:
        doc.recompute()
        yield 1500
    fl, cut = doc.getObject("Fillet"), doc.getObject("Cut")
    log("states", list(box.State), list(fl.State), list(cut.State), round(cut.Shape.Volume, 1))
    if tr is not None:
        tr.expandAll()
    yield 800
    yield d.say(L("重算：圆角失败，模型树上打了红叉", "Recompute: the fillet fails and gets a red mark in the tree"))
    yield 4000
    if "Touched" in cut.State:
        yield d.say(L(f"{who}：后面的“挖孔”标成“要重算”（蓝色标记）——它还是旧形状，提醒你不能用",
                      f"{who}: the Cut after it is marked “needs recompute” (blue mark) — it still holds the old shape, and you are told so"))
    else:
        yield d.say(L(f"{who}：后面的“挖孔”看起来一切正常，三维视图里还是 20 mm 的旧形状——其实它根本没重算",
                      f"{who}: the Cut after it looks fine, and the 3D view still shows the old 20 mm shape — it was never recomputed"))
    yield 6500


def main():
    d = Director()
    d.run(script(d))


boot(main)
