"""第 13 课 片段 B：G0 → G1——侧面轮廓里，B 样条的两头和相邻直线加“相切”；回到实体，左边那道折棱没了。真操作。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui, Part
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps
from steps import sp


def crease(shape, x, z):
    """实体在 (x, *, z) 附近那条沿 Y 的棱两侧的面夹角（度）"""
    best = None
    for e in shape.Edges:
        p = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        if abs(p.x - x) < 2 and abs(p.z - z) < 2 and e.Length > 50:
            fs = shape.ancestorsOfType(e, Part.Face)
            if len(fs) == 2:
                n = [f.normalAt(*f.Surface.parameter(p)) for f in fs]
                best = round(math.degrees(n[0].getAngle(n[1])), 1)
    return best


def bs_pt(sk, k):
    g = [x for x in sk.Geometry if x.TypeId == "Part::GeomBSplineCurve"][0]
    return g.value(g.FirstParameter + k * (g.LastParameter - g.FirstParameter))


def script(d):
    doc = App.openDocument(model_file("机头曲面.FCStd", "HeadSurface.FCStd"))
    com = [o for o in doc.Objects if o.TypeId in ("Part::Common", "Part::MultiCommon")][-1]
    side = [o for o in doc.Objects if o.TypeId == "Sketcher::SketchObject"][0]
    log("crease before", crease(com.Shape, -55, 227.5))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield d.say("左边那道折棱从哪来？侧面轮廓里，B 样条是穿过描的点画的，到了端点和竖线拐了个角——轮廓只有 G0，拉出来的曲面也就折了")
    yield 1500
    yield d.say("双击侧面轮廓的草图，让 B 样条的两头和相邻的直线相切")
    p = d.tree_item(side.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1200
    Gui.SendMsgToActiveView("ViewFit"); yield 600
    yield d.move(sp(d, -45, 235), 800)
    yield from steps.zoom_sk(d, 10, 70, at=sp(d, -45, 235))
    sk = steps.sketch()
    lines = [(i, g) for i, g in enumerate(sk.Geometry) if g.TypeId == "Part::GeomLineSegment"]
    # 竖线（左边）和顶线：按端点找
    left = [g for i, g in lines if abs(g.StartPoint.x - g.EndPoint.x) < 1e-6 and min(g.StartPoint.x, g.EndPoint.x) < -50][0]
    top = [g for i, g in lines if abs(g.StartPoint.y - g.EndPoint.y) > 1 and abs(g.StartPoint.x - g.EndPoint.x) > 50][0]
    yield d.say("先删掉两头的“重合”约束（列表里选中，按 Delete）——“端点相切”本身就包含重合，留着会冗余")
    sk = steps.sketch()
    bi = [i for i, g in enumerate(sk.Geometry) if g.TypeId == "Part::GeomBSplineCurve"][0]
    ends = {}
    for pos in (1, 2):
        q = sk.getPoint(bi, pos)
        for i, g in enumerate(sk.Geometry):
            if g.TypeId == "Part::GeomLineSegment":
                for lp in (1, 2):
                    if (sk.getPoint(i, lp) - q).Length < 1e-3:
                        ends[pos] = (i, lp)
    log("ends", ends)
    for _ in range(2):
        sk = steps.sketch()
        k = [i for i, c in enumerate(sk.Constraints) if c.Type == "Coincident" and
             any((c.First, c.FirstPos) == e or (c.Second, c.SecondPos) == e for e in ends.values())
             and sk.Geometry[c.First].TypeId == "Part::GeomPoint"]
        if not k:
            break
        lw = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QListWidget) and w.isVisible()
              and w.count() == len(sk.Constraints)][0]
        it = lw.item(k[0])
        lw.scrollToItem(it)
        p = lw.viewport().mapToGlobal(lw.visualItemRect(it).center())
        yield d.move(p, 800)
        d.click(p); yield 500
        d.key(Qt.Key_Delete, lw.viewport()); yield 900
        if len(steps.sketch().Constraints) == len(sk.Constraints):     # 没删掉：直接删（和按 Delete 一样）
            steps.sketch().delConstraint(k[0])
            yield 500
        log("deleted", k[0])
    yield d.say("再选 B 样条的端点、按住 Ctrl 选直线的端点，点“相切”——两头各做一次")
    for pos in (2, 1):
        sk = steps.sketch()
        li, lp = ends[pos]
        q = sk.getPoint(bi, pos)
        vb = [v for v in range(300) if sk.getGeoVertexIndex(v) == (bi, pos)][0]
        vl = [v for v in range(300) if sk.getGeoVertexIndex(v) == (li, lp)][0]
        Gui.Selection.clearSelection()
        yield d.move(sp(d, q.x, q.y), 900)
        d.ring(sp(d, q.x, q.y))          # 两个端点叠在一起，点一下只能选中一个：两个都选上（和 Ctrl 点两次一样）
        Gui.Selection.addSelection(App.ActiveDocument.Name, sk.Name, f"Vertex{vb + 1}")
        Gui.Selection.addSelection(App.ActiveDocument.Name, sk.Name, f"Vertex{vl + 1}")
        yield 600
        yield d.tool("Sketcher_ConstrainTangent")
        yield from steps.answer_modal(d)
        yield 900
        App.ActiveDocument.recompute()
        log("tangent", sk.solve(), [c.Type for c in sk.Constraints].count("Tangent"))
    steps.dump("tangent")
    yield d.say("两头都相切了：轮廓到了 G1——方向连续，没有拐角")
    yield 1500
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    doc.recompute()
    log("crease after", crease(com.Shape, -55, 227.5), round(com.Shape.Volume, 1))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    v = d.model_pt(-55, 0, 228)
    yield d.move(v, 900)
    yield from d.zoom_to(30, 200, at=v)
    yield d.say("回到实体：左边的折棱没有了，弯面顺滑地接到侧面上。G0 位置连续、G1 再加方向连续、G2 再加曲率连续——反光最顺")
    yield 3000
    Gui.SendMsgToActiveView("ViewFit"); yield 500
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
