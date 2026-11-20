"""第 17 课 片段 A：针杆零件图——TechDraw：国标 A4 横图框，插入视图（转成横放），标总长 180、直径 ⌀8，局部放大油槽。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file
import steps


def page_view():
    ws = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QGraphicsView) and w.isVisible()
          and w.metaObject().className() == "TechDrawGui::QGVPage"]
    return ws[0] if ws else None


def page_pt(x, y):
    """图纸上的点（毫米，左下角为原点）→ 屏幕点"""
    gv = page_view()
    return gv.viewport().mapToGlobal(gv.mapFromScene(QtCore.QPointF(x * 10, -y * 10)))


def view_edges(v):
    """视图里看得见的边：(序号, 中点在图纸上的位置, 边)"""
    out = []
    for i, e in enumerate(v.getVisibleEdges()):
        m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        out.append((i, (v.X.Value + m.x, v.Y.Value + m.y), e))
    return out


def pick_edge(d, v, i, ctrl=False):
    x, y = [p for k, p, e in view_edges(v) if k == i][0]
    p = page_pt(x, y)
    yield d.move(p, 800)
    d.click(p, mods=Qt.ControlModifier if ctrl else Qt.NoModifier)
    yield 600


def place(d, dim, x, y):
    """尺寸挪开：属性里 X、Y（相对视图中心，毫米）"""
    Gui.Selection.clearSelection()
    p = d.tree_item(dim.Label)
    yield d.move(p, 700)
    d.click(p); yield 600
    yield from steps.prop_set(d, f"{x} mm", ("基本", "Base"), "X")
    yield from steps.prop_set(d, f"{y} mm", ("基本", "Base"), "Y")
    if abs(dim.X.Value - x) > 0.01 or abs(dim.Y.Value - y) > 0.01:    # 属性框没接住：直接改（和键入一样）
        log("place fallback", dim.Label, dim.X, dim.Y)
        dim.X, dim.Y = x, y
    App.ActiveDocument.recompute()
    yield 600


def script(d):
    doc = App.openDocument(model_file("针杆零件.FCStd", "NeedleBarPart.FCStd"))
    bar = doc.Objects[0]
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield from steps.pick_workbench(d, "TechDraw", "TechDraw")
    yield d.say("工程图：TechDraw 工作台。先插一张图纸：点“插入模板页”，选国标 A4 横的图框")
    yield d.tool("TechDraw_PageTemplate") if d.action_widget("TechDraw_PageTemplate") else d.tool("TechDraw_PageDefault", "TechDraw_PageTemplate")
    yield from steps.file_dialog(d, L("A4_Landscape_CN_CLIP.svg", "A4_Landscape_ISO5457_minimal.svg"))   # 中文版国标图框，英文版 ISO 5457
    yield from d.until(lambda: page_view() is not None, 8000)
    yield 1500
    page = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawPage"][0]
    log("page", page.Template.Template if page.Template else None)
    yield d.say("回到三维，选中针杆，点“插入视图”。默认是主视图（从前往后看），针杆竖着；点“顺时针转”让它横过来，确定")
    p = d.tree_item(bar.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("TechDraw_View")
    yield from d.until(lambda: steps.named(QtWidgets.QPushButton, "butCWRotate") is not None, 8000)
    yield 1000
    b = steps.named(QtWidgets.QPushButton, "butCWRotate")
    q = d.center(b)
    yield d.move(q, 800)
    d.click(q); yield 1200
    v = [o for o in doc.Objects if o.TypeId in ("TechDraw::DrawProjGroupItem", "TechDraw::DrawViewPart")][0]
    log("dir", v.Direction, v.XDirection)
    yield from steps.task_ok(d, gone="butCWRotate")
    doc.recompute()
    yield from d.until(lambda: page_view() is not None, 5000)
    yield 1200
    v = [o for o in doc.Objects if o.TypeId in ("TechDraw::DrawProjGroupItem", "TechDraw::DrawViewPart")][0]
    yield d.say("视图往左上挪一点，右边留地方放局部放大图：属性里 X = 125、Y = 140")
    p = d.tree_item(v.Label)
    yield d.move(p, 800)
    d.click(p); yield 700
    yield from steps.prop_set(d, "125 mm", ("基本", "Base"), "X")
    yield from steps.prop_set(d, "140 mm", ("基本", "Base"), "Y")
    doc.recompute(); yield 1200
    E = view_edges(v)
    log("view", v.Direction, v.XDirection, v.X, v.Y, v.Scale, [(k, e.Curve.TypeId.split("::")[-1], round(e.Length, 2), tuple(round(c, 1) for c in p)) for k, p, e in E])
    Gui.Selection.clearSelection()
    yield d.say("标总长：点左端那条短线，按住 Ctrl 点右端那条，点“水平尺寸”——180；属性里 Y 挪到上面")
    yield from pick_edge(d, v, 3)
    yield from pick_edge(d, v, 14, ctrl=True)
    log("sel", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    yield d.tool("TechDraw_CompDimensionTools", "TechDraw_HorizontalDimension")
    yield 2000
    dims = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewDimension"]
    log("dims", [(o.Label, o.Type, round(o.getRawValue(), 3) if hasattr(o, "getRawValue") else None) for o in dims])
    yield from place(d, dims[-1], 0, 14)
    Gui.Selection.clearSelection()
    yield d.say("标直径：点上面一条轮廓线，Ctrl 点下面一条，点“竖直尺寸”——8；再加“⌀”前缀")
    yield from pick_edge(d, v, 11)
    yield from pick_edge(d, v, 20, ctrl=True)
    yield d.tool("TechDraw_CompDimensionTools", "TechDraw_VerticalDimension")
    yield 2000
    dims = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewDimension"]
    log("dims", [(o.Name, o.Label, o.Type, o.FormatSpec) for o in dims])
    dv = dims[-1]
    Gui.Selection.clearSelection()
    p = d.tree_item(dv.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    names = [str(a.objectName() or a.data()) for tb in d.mw.findChildren(QtWidgets.QToolBar) if tb.isVisible() for a in tb.actions()
             if "Diameter" in str(a.objectName() or a.data()) or "Prefix" in str(a.objectName() or a.data())]
    log("prefix buttons", names)
    yield d.tool(names[0], "TechDraw_ExtensionInsertDiameter" if names[0] != "TechDraw_ExtensionInsertDiameter" else None)
    yield 1500
    log("fmt", dv.FormatSpec)
    yield from place(d, dv, 100, 0)
    yield d.say("局部放大：选中视图，点“局部视图”，圆心放在第一道油槽上，半径 4，比例 5:1")
    p = d.tree_item(v.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("TechDraw_DetailView") if d.action_widget("TechDraw_DetailView") else d.tool("TechDraw_CompViews", "TechDraw_DetailView")
    yield 2500
    log("detail widgets", [(w.objectName(), w.text() if hasattr(w, "text") else "") for w in QtWidgets.QApplication.allWidgets()
                           if w.isVisible() and w.objectName() and isinstance(w, (QtWidgets.QAbstractSpinBox, QtWidgets.QLineEdit, QtWidgets.QComboBox)) and d.center(w).x() > 1000])
    for name, val in (("qsbX", "-49.5 mm"), ("qsbY", "3.5 mm"), ("qsbRadius", "4 mm")):
        yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, name), val)
    cb = steps.named(QtWidgets.QComboBox, "cbScaleType")
    log("scale types", [cb.itemText(i) for i in range(cb.count())])
    yield from steps.combo_pick(d, cb, cb.count() - 1)
    yield from steps.type_into(d, steps.named(QtWidgets.QAbstractSpinBox, "qsbScale"), "5")
    yield 1200
    yield from steps.task_ok(d, gone="qsbRadius")
    doc.recompute()
    dt = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewDetail"]
    p = d.tree_item(dt[-1].Label)
    yield d.move(p, 800)
    d.click(p); yield 700
    yield from steps.prop_set(d, "235 mm", ("基本", "Base"), "X")
    yield from steps.prop_set(d, "92 mm", ("基本", "Base"), "Y")
    doc.recompute(); yield 1000
    log("detail", [(o.Label, o.AnchorPoint, o.Radius, o.Scale, o.X, o.Y) for o in dt])
    yield 1500
    yield d.say("一张零件图的骨架有了：主视图横放、总长、直径，油槽单独放大。下一段在放大图上标油槽的尺寸，填标题栏，导出 PDF")
    yield 3000
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


import builtins  # noqa: E402
if not getattr(builtins, "_WQ_IMPORT_ONLY", False):     # l17b 只借用这里的函数，不要再起一遍剧本
    boot(main)
