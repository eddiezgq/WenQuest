"""第 17 课 片段 B：在局部放大图上标油槽（宽 0.5、间距 2、深 0.2），主视图上标油槽位置 39.25；填标题栏（零件名、材料、比例）。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file
import steps
import builtins  # noqa: E402
builtins._WQ_IMPORT_ONLY = True
from l17a import page_view, page_pt, view_edges, pick_edge, place


def script(d):
    doc = App.openDocument(model_file("针杆零件.FCStd", "NeedleBarPart.FCStd"))
    page = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawPage"][0]
    v = [o for o in doc.Objects if o.TypeId in ("TechDraw::DrawProjGroupItem", "TechDraw::DrawViewPart")][0]
    dt = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewDetail"][0]
    yield from steps.pick_workbench(d, "TechDraw", "TechDraw")
    p = d.tree_item(page.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: page_view() is not None, 5000)
    for o in ():
        log("edges", o.Label, [(k, e.Curve.TypeId.split("::")[-1], round(e.Length, 3), tuple(round(c, 2) for c in p)) for k, p, e in view_edges(o)])
    yield d.say("接着标油槽。局部放大图上：点一道槽底的短线，点“水平尺寸”——槽宽 0.5（放大图上的尺寸按真实大小标）")
    yield from dim(d, doc, dt, [11], "TechDraw_HorizontalDimension", -5, 7, flip=True)
    yield d.say("两道槽之间那段：1.5；槽深：外圆那条线 + 槽底那条线，“竖直尺寸”——0.2")
    yield from dim(d, doc, dt, [12], "TechDraw_HorizontalDimension", 1, 13, flip=True)
    yield from dim(d, doc, dt, [14, 13], "TechDraw_VerticalDimension", 20, -3, flip=True)
    yield d.say("主视图上标槽的位置：左端线 + 第一道槽的左边线——39.25")
    yield from dim(d, doc, v, [3, 2], "TechDraw_HorizontalDimension", -70, -10)
    yield d.say("最后填标题栏：点图框上的字段，输入。零件名称“针杆”、材料“GCr15”、图号“LS-201”、比例“1:1”")
    F = ((("PARTNAME", 239.5, 178.5, "针杆"), ("MATERIALMARK", 219, 168, "GCr15"), ("PART_CODE_NAME", 271, 192, "LS-201"), ("scale", 228, 193, "1:1"))
         if not L(0, 1) else
         (("title", 112, 173.2, "Needle bar"), ("part_material", 112, 161.2, "GCr15 (AISI 52100)"), ("drawing_number", 112, 197.2, "LS-201"),
          ("scale", 237, 161.2, "1:1"), ("creator", 192, 173.2, "WenQuest"), ("approval_person", 192, 185.2, "-")))   # 图框自带的示例人名换掉
    for key, x, y, text in F:                 # 图框 SVG 里可编辑字段的位置（毫米，左上角为原点）
        yield from field(d, x, 210 - y + 1.2, text)
        log("field", key, page.Template.EditableTexts.get(key))
    doc.recompute()
    log("dims", [(o.Label, round(o.getRawValue(), 2), o.X, o.Y, o.Visibility) for o in doc.Objects if o.TypeId == "TechDraw::DrawViewDimension"])
    yield 1500
    yield d.say("一张能看懂的零件图：视图、尺寸、放大图、标题栏。下一课加公差、粗糙度和技术要求，再导出 PDF")
    yield 3000
    doc.save()
    yield 300


def edge_pt(o, i, flip=False):
    e = o.getVisibleEdges()[i]
    m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
    return (o.X.Value + m.x, o.Y.Value - m.y if flip else o.Y.Value + m.y)    # 局部视图的边：y 方向反过来（录屏前量过）


def dim(d, doc, o, edges, cmd, x, y, flip=False):
    Gui.Selection.clearSelection()
    for k, i in enumerate(edges):
        q = page_pt(*edge_pt(o, i, flip))
        yield d.move(q, 800)
        d.click(q, mods=Qt.ControlModifier if k else Qt.NoModifier)
        yield 600
        want = f"Edge{i}"
        got = [n for s_ in Gui.Selection.getSelectionEx() if s_.ObjectName == o.Name for n in s_.SubElementNames]
        if want not in got:                      # 放大图里的线很短，点到了端点：直接选这条边（和点中它一样）
            for n in got:
                if n.startswith("Vertex") or n.startswith("Face"):
                    Gui.Selection.removeSelection(doc.Name, o.Name, n)
            Gui.Selection.addSelection(doc.Name, o.Name, want)
            yield 300
    wanted = {f"Edge{i}" for i in edges}
    for s_ in Gui.Selection.getSelectionEx():
        for n in s_.SubElementNames:
            if s_.ObjectName != o.Name or n not in wanted:     # 挨得很近的线一起被点中了：只留要的
                Gui.Selection.removeSelection(doc.Name, s_.ObjectName, n)
    yield 300
    log("sel", [s.SubElementNames for s in Gui.Selection.getSelectionEx()])
    n0 = len([o2 for o2 in doc.Objects if o2.TypeId == "TechDraw::DrawViewDimension"])
    yield d.tool("TechDraw_CompDimensionTools", cmd)
    yield 1800
    dims = [o2 for o2 in doc.Objects if o2.TypeId == "TechDraw::DrawViewDimension"]
    if len(dims) > n0:
        log("dim", dims[-1].Type, round(dims[-1].getRawValue(), 3))
        yield from place(d, dims[-1], x, y)
    else:
        log("dim failed")


def field(d, x, y, text):
    """点图框里的可编辑字段（模态框），输入，确定"""
    if page_view() is None:          # 图纸窗口被切走了：双击模型树里的页面，切回来
        pg = [o for o in App.ActiveDocument.Objects if o.TypeId == "TechDraw::DrawPage"][0]
        p = d.tree_item(pg.Label)
        yield d.move(p, 700)
        d.click(p, double=True)
        yield from d.until(lambda: page_view() is not None, 5000)
        yield 800
    q = page_pt(x, y)
    yield d.move(q, 900)
    QtCore.QTimer.singleShot(0, lambda: d.click(q))
    yield from d.until(lambda: QtWidgets.QApplication.activeModalWidget() is not None, 4000)
    m = QtWidgets.QApplication.activeModalWidget()
    if m is None:
        log("no field dialog")
        return
    yield 600
    log("field dlg", m.metaObject().className(), [(w.metaObject().className(), w.objectName()) for w in m.findChildren(QtWidgets.QWidget) if w.isVisible()][:12])
    e = [w for w in m.findChildren(QtWidgets.QLineEdit) if w.isVisible()][0]
    e.setFocus(); e.selectAll()
    d.keys(text, w=e)
    yield 700
    ok = [b for b in m.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text().replace("&", "") in ("确定", "OK")][0]
    p = d.center(ok)
    yield d.move(p, 600)
    d.ring(p)
    ok.click()
    yield 900

def main():
    d = Director()
    d.run(script(d))


boot(main)
