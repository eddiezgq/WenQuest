"""第 13 课 片段 C：过渡曲面——前上角两侧，弯面和 R14 圆角面交成尖棱：选这两条棱，Part“圆角”R8，做出相切的过渡面。真操作。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui, Part
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps


def corner_edges(shape):
    """弯面（拉伸出来的 B 样条面）和圆柱面（R14 圆角）之间的棱"""
    out = []
    for i, e in enumerate(shape.Edges):
        fs = shape.ancestorsOfType(e, Part.Face)
        if len(fs) == 2:
            ts = sorted(f.Surface.TypeId.split("::")[-1] for f in fs)
            if ts == ["GeomCylinder", "GeomSurfaceOfExtrusion"] and e.Length < 40:
                out.append(i)
    return out


def script(d):
    doc = App.openDocument(model_file("机头曲面.FCStd", "HeadSurface.FCStd"))
    com = [o for o in doc.Objects if o.TypeId in ("Part::Common", "Part::MultiCommon")][-1]
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield from steps.pick_workbench(d, "Part", "Part")
    ce = corner_edges(com.Shape)
    log("corner edges", ce, [round(com.Shape.Edges[i].Length, 1) for i in ce])
    mids = [com.Shape.Edges[i].valueAt((com.Shape.Edges[i].FirstParameter + com.Shape.Edges[i].LastParameter) / 2) for i in ce]
    pm = min(mids, key=lambda q: q.y)          # 朝着镜头的那一侧
    yield d.move(d.model_pt(pm.x, pm.y, pm.z), 900)
    yield from d.zoom_to(20, 300, at=d.model_pt(pm.x, pm.y, pm.z))
    yield d.say("前上角两侧还有尖棱：前面的弯面和侧面的 R14 圆角面在这里相交。两张面各自光顺，交在一起就是 G0")
    yield 2000
    yield d.say("做一张过渡面：选中这两条棱（另一条在背面），点 Part 的“圆角”，半径 8")
    Gui.Selection.clearSelection()
    for i in ce:
        e = com.Shape.Edges[i]
        q = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        p = d.model_pt(q.x, q.y, q.z)
        yield d.move(p, 800)
        d.ring(p)                      # 背面那条看不见、点不到：两条都直接选上（和点中它们一样）
        Gui.Selection.addSelection(doc.Name, com.Name, f"Edge{i + 1}")
        yield 600
    yield d.tool("Part_Fillet")
    yield from d.until(lambda: any(isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and "adius" in w.objectName()
                                   for w in QtWidgets.QApplication.allWidgets()), 8000)
    yield 1200
    log("fillet widgets", [(w.objectName(), w.text() if hasattr(w, "text") else "") for w in QtWidgets.QApplication.allWidgets()
                           if w.isVisible() and w.objectName() and isinstance(w, (QtWidgets.QAbstractSpinBox, QtWidgets.QComboBox, QtWidgets.QCheckBox))][:20])
    tw = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QTreeView) and w.isVisible() and w.window() is d.mw
          and w.model() and w.model().rowCount() > 10]
    if tw:
        m = tw[0].model()
        log("checked", sum(1 for r in range(m.rowCount()) if m.data(m.index(r, 0), Qt.CheckStateRole) in (2, Qt.Checked)))
    w = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and "adius" in w.objectName()][0]
    yield from steps.type_into(d, w, "8 mm")
    yield from steps.task_ok(d, gone=w.objectName())
    f = [o for o in doc.Objects if o.TypeId == "Part::Fillet"]
    doc.recompute()
    log("fillet", len(f), f and [round(f[-1].Shape.Volume, 1), f[-1].Shape.isValid(), len(f[-1].Edges)])
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.move(d.model_pt(pm.x, pm.y, pm.z), 900)
    yield from d.zoom_to(20, 300, at=d.model_pt(pm.x, pm.y, pm.z))
    yield d.say("尖棱换成了一张圆角过渡面，和两边都相切（G1）。要 G2（曲率也连续，反光更顺），用曲面工作台的“填充”，边界条件选曲率")
    yield 3000
    Gui.SendMsgToActiveView("ViewFit"); yield 500
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
