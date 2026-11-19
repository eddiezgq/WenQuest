"""第 2 课 片段 C：把一个零件导出成 STEP 给别人，再导入看看。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, QtCore, L, model_dir, menu_path
import steps


def script(d):
    App.openDocument(os.path.join(model_dir(), "WQ-LS.FCStd"))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 2000
    yield d.say("别人要你的零件，又不用 FreeCAD：导出成 STEP，几乎所有 CAD 都能打开。先在模型树里选针杆")
    t = d.tree()
    grp = t.findItems(L("主轴与挑线", "Upper shaft & take-up"), Qt.MatchExactly | Qt.MatchRecursive)[0]
    grp.setExpanded(True)
    yield 600
    p = d.tree_item("needle_bar")
    yield d.move(p, 900)
    d.click(p); yield 1000
    log("sel", [s.ObjectName for s in Gui.Selection.getSelectionEx()])
    yield d.say("菜单“文件 → 导出”，文件类型选 STEP，起名“针杆”，保存")
    yield from menu_path(d, L("文件", "File"), L("导出", "Export"))
    yield from steps.file_dialog(d, L("针杆", "needle_bar") + ".step", "STEP")
    for _ in range(20):
        w = QtWidgets.QApplication.activeModalWidget()
        if w is not None and not isinstance(w, QtWidgets.QFileDialog):
            log("extra dialog", w.windowTitle())
            ok = [b for b in w.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text().replace("&", "") in ("确定", "OK")]
            if ok:
                p = d.center(ok[0]); yield d.move(p, 600); d.click(p)
                yield 500
                try:
                    if ok[0].isVisible():          # 鼠标事件没落到按钮上：按按钮自己的点击
                        log("ok fallback")
                        ok[0].click()
                except RuntimeError:               # 对话框已经关了
                    pass
            break
        yield 150
    f = os.path.join(os.environ["WQ_REC"], L("针杆", "needle_bar") + ".step")
    for k in range(40):
        if os.path.exists(f) and os.path.getsize(f) > 1000:
            break
        if k % 5 == 0:
            m = QtWidgets.QApplication.activeModalWidget()
            log("wait", k, m.metaObject().className() if m else None, m.windowTitle() if m else "")
        yield 500
    yield 800
    log("exported", f, os.path.exists(f) and os.path.getsize(f))
    yield d.say("导出好了。检查一下：新建空文档，“文件 → 导入”刚才的 STEP")
    yield d.tool("Std_New"); yield 1200
    yield from menu_path(d, L("文件", "File"), L("导入", "Import"))
    yield from steps.file_dialog(d, L("针杆", "needle_bar") + ".step")
    for _ in range(30):
        m = QtWidgets.QApplication.activeModalWidget()
        if m is not None:
            log("import modal", m.metaObject().className(), m.windowTitle())
            ok = [b for b in m.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text().replace("&", "") in ("确定", "OK")]
            if ok:
                p = d.center(ok[0]); yield d.move(p, 600); d.click(p)
            break
        if [o for o in App.ActiveDocument.Objects if hasattr(o, "Shape")]:
            break
        yield 200
    yield 2000
    log("docs", {n: [o.Name for o in dd.Objects] for n, dd in App.listDocuments().items()}, App.ActiveDocument.Name)
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    shapes = [o for o in App.ActiveDocument.Objects if hasattr(o, "Shape") and not o.Shape.isNull()]
    log("imported", [(o.Name, round(o.Shape.Volume, 2)) for o in shapes], "orig", round(App.getDocument("WQ_LS").needle_bar.Shape.Volume, 2) if "WQ_LS" in App.listDocuments() else "?")
    yield d.say("针杆完整回来了，体积和原来一样。STL（三维打印用）、DXF（二维图）也在“导出”里，用法一样")
    yield 2500


def main():
    d = Director()
    d.run(script(d))


boot(main)
