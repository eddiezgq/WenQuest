"""第 4 课 片段 B：几何约束——点在线上、对称。先选，再点约束按钮。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets
import steps

M = os.path.join(os.environ.get("WQ_REC", "."), "model")


def script(d):
    yield from steps.open_and_edit(d, os.path.join(M, "针夹草图.FCStd"))
    d.say("几何约束：先选对象，再点约束按钮。中心线下端还没定——选它的下端点，再选下边线")
    yield from steps.pick(d, ("v", 5, 1), (1.8, -7.03))
    log("sel1", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    d.say("点“重合 / 点在线上”：端点落到线上")
    yield d.tool("Sketcher_ConstrainCoincidentUnified"); yield 1500
    log("dof", steps.dof_text(d))
    d.say("上端点放到圆弧上：同样先选，再点")
    yield from steps.pick(d, ("v", 5, 2), (-2.49, 4.99))
    yield d.tool("Sketcher_ConstrainCoincidentUnified"); yield 1500
    log("dof", steps.dof_text(d))
    d.say("左右对称：选左下角、右下角，再选竖轴（Y 轴），点“对称”")
    Gui.Selection.clearSelection()
    yield from steps.pick(d, ("v", 1, 2), ("v", 1, 1), (0, -10.5))
    log("sel3", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.tool("Sketcher_ConstrainSymmetric"); yield 1800
    log("dof", steps.dof_text(d))
    d.say("红字“冗余约束”：对称已经让左右两点一样高，下边线原来的“水平”就重复了")
    lab = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QLabel) and w.isVisible() and "冗余" in w.text()]
    if lab:
        p = d.center(lab[0]); yield d.move(p, 900); d.ring(p)
    yield 3000
    d.say("撤销对称（Ctrl+Z），在约束列表里选中那个“水平”，按 Delete 删掉")
    d.key(Qt.Key_Z, d.vp(), Qt.ControlModifier); yield 1200
    sk = steps.sketch()
    idx = [i for i, c in enumerate(sk.Constraints) if c.Type == "Horizontal" and c.First == 1][0]
    L = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QListWidget) and w.isVisible() and w.count() >= 8][0]
    it = [L.item(i) for i in range(L.count()) if L.item(i).text().startswith(f"Constraint{idx + 1}")][0]
    p = L.viewport().mapToGlobal(L.visualItemRect(it).center())
    yield d.move(p, 900)
    d.click(p); yield 700
    d.key(Qt.Key_Delete, L); yield 1200
    log("after delete", steps.dof_text(d), [c.Type for c in steps.sketch().Constraints])
    d.say("再加对称：左下角、右下角、Y 轴，点“对称”")
    Gui.Selection.clearSelection()
    yield from steps.pick(d, ("v", 1, 2), ("v", 1, 1), (0, -10.5))
    yield d.tool("Sketcher_ConstrainSymmetric"); yield 1800
    log("dof", steps.dof_text(d))
    steps.dump("B")
    d.say("每加一个约束，自由度就少一点。剩下的要用尺寸定")
    yield 3500
    App.ActiveDocument.save()


def main():
    d = Director()
    d.run(script(d))


boot(main)
