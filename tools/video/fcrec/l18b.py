"""第 18 课 片段 B：曲柄滑块装配图——装配里做“材料清单”（明细表）；A3 图框，插入装配的侧视图，插入明细表，零件序号，标题栏，导出 PDF。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builtins
builtins._WQ_IMPORT_ONLY = True
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_dir, menu_path
import steps
from l17a import page_view, page_pt
from l17b import field

PARTS = [L("机架", "Frame"), L("上轴曲柄", "ShaftCrank"), L("连杆", "Rod"), L("针杆组件", "NeedleBarAssy")]


# 每个零件的序号指到哪：(第几个实体, 取哪一头)；圆圈放在哪（相对视图中心，毫米）
AIM = [(2, "+x", (55, -60)),      # 1 机架：下导套右边
       (1, "+x", (65, 75)),       # 2 上轴曲柄：平衡块最右
       (0, "-x", (-60, 45)),      # 3 连杆：最左
       (0, "-y", (-45, -90))]     # 4 针杆组件：针杆下端


def part_pts(v, links):
    """零件上的点投到视图里，换成视图里的坐标（视图以投影后的外框中心为原点）"""
    samp = {}
    for name, link in links.items():
        samp[name] = []
        for so in link.Shape.Solids:
            pts = []
            for e in so.Edges:
                pts += [e.valueAt(e.FirstParameter + (e.LastParameter - e.FirstParameter) * t / 8) for t in range(9)]
            samp[name].append([(q.x, q.y) for q in (v.projectPoint(p) for p in pts)])
    allp = [q for ss in samp.values() for qs in ss for q in qs]
    vis = [x.Point for e in v.getVisibleEdges() for x in e.Vertexes]
    cx = (min(q[0] for q in allp) + max(q[0] for q in allp)) / 2 - (min(p.x for p in vis) + max(p.x for p in vis)) / 2
    cy = (min(q[1] for q in allp) + max(q[1] for q in allp)) / 2 - (min(p.y for p in vis) + max(p.y for p in vis)) / 2
    out = {}
    for (name, ss), (i, how, _) in zip(samp.items(), AIM):
        qs = ss[min(i, len(ss) - 1)]
        k = {"+x": lambda q: q[0], "-x": lambda q: -q[0], "-y": lambda q: -q[1]}[how]
        q = max(qs, key=k)
        out[name] = (q[0] - cx, q[1] - cy)
    return out


def menu_find(d, cmd):
    """菜单栏里找命令所在的路径（菜单文字）"""
    norm = lambda t: t.replace("&", "").replace("…", "").replace("...", "").strip()

    def walk(m, path):
        for a in m.actions():
            if a.objectName() == cmd or a.data() == cmd:
                return path + [norm(a.text())]
            if a.menu():
                r = walk(a.menu(), path + [norm(a.text())])
                if r:
                    return r
    for a in d.mw.menuBar().actions():
        if a.menu():
            r = walk(a.menu(), [norm(a.text()).split("(")[0]])
            if r:
                return r


def script(d):
    doc = App.openDocument(os.path.join(model_dir(), "slider", L("曲柄滑块", "SliderCrank") + ".FCStd"))
    for name in PARTS:
        App.openDocument(os.path.join(model_dir(), "slider", name + ".FCStd"))
    App.setActiveDocument(doc.Name)
    asm = [o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject"][0]
    links = {o.Label: o for o in doc.Objects if o.TypeId == "App::Link"}
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield from steps.pick_workbench(d, "装配", "Assembly")
    p = d.tree_item(asm.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield 1500
    yield d.say("装配图 = 视图 + 明细表 + 零件序号。明细表先在装配里做：点“材料清单”")
    yield d.tool("Assembly_CreateBom")
    yield from d.until(lambda: steps.named(QtWidgets.QListWidget, "columnList") is not None, 8000)
    yield 1200
    cl = steps.named(QtWidgets.QListWidget, "columnList")
    log("columns", [cl.item(i).text() for i in range(cl.count())])
    yield d.say("列：序号、名称、数量够用。“说明”“文件名”两列选中按 Delete 删掉")
    for key in ("File", "Description"):
        its = [cl.item(i) for i in range(cl.count()) if cl.item(i).text().startswith(L({"File": "文件", "Description": "说明"}[key], key))
               or cl.item(i).text().startswith(key)]
        if not its:
            log("no column", key); continue
        r = cl.visualItemRect(its[0])
        p = cl.viewport().mapToGlobal(r.center())
        yield d.move(p, 800)
        d.click(p); yield 600
        d.key(Qt.Key_Delete, cl); yield 800
    log("columns", [cl.item(i).text() for i in range(cl.count())])
    yield from steps.task_ok(d, gone="columnList")
    doc.recompute()
    yield 1000
    bom = [o for o in doc.Objects if o.TypeId == "Assembly::BomObject"][0]
    log("bom", bom.Label, [[bom.getContents(f"{c}{r}") for c in "ABC"] for r in range(1, 6)])
    yield d.say("明细表是一张表格，双击能打开看：序号 1–4、名称、数量；零件变了，重算后跟着变")
    p = d.tree_item(bom.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield 3500

    Gui.getDocument(doc.Name).resetEdit()                # 退出装配编辑，别的工作台的命令才可用
    for tb in d.mw.findChildren(QtWidgets.QTabBar):      # 切回三维窗口
        if tb.isVisible():
            ks = [i for i in range(tb.count()) if tb.tabText(i).startswith(doc.Label)]
            if ks:
                p = tb.mapToGlobal(tb.tabRect(ks[0]).center())
                yield d.move(p, 800)
                d.click(p); yield 1000
                break
    yield from d.until(lambda: steps.named(QtWidgets.QListWidget, "columnList") is not None, 2500)
    if steps.named(QtWidgets.QListWidget, "columnList") is not None:     # 双击也打开了清单设置，确定关掉
        yield from steps.task_ok(d, gone="columnList")
    yield from steps.pick_workbench(d, "TechDraw", "TechDraw")
    yield d.say("出图：A3 横图框（机构有 190 高，1:1 放得下）")
    App.setActiveDocument(doc.Name)
    yield d.tool("TechDraw_PageTemplate") if d.action_widget("TechDraw_PageTemplate") else d.tool("TechDraw_PageDefault", "TechDraw_PageTemplate")
    yield from steps.file_dialog(d, L("A3_Landscape_CN_CLIP.svg", "A3_Landscape_ISO5457_minimal.svg"))
    yield from d.until(lambda: page_view() is not None, 8000)
    yield 1500
    page = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawPage"][0]
    yield d.say("选中整个装配，插入视图；点“向右旋转”，从侧面看，曲柄、连杆、针杆都在这个平面里，确定")
    p = d.tree_item(asm.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("TechDraw_View")
    yield from d.until(lambda: steps.named(QtWidgets.QPushButton, "butCWRotate") is not None, 8000)
    yield 1000
    log("view task", [(w.objectName(), w.toolTip()[:30]) for w in QtWidgets.QApplication.allWidgets()
                      if w.isVisible() and isinstance(w, (QtWidgets.QPushButton, QtWidgets.QComboBox)) and w.objectName().startswith(("but", "cmb"))])
    b = steps.named(QtWidgets.QPushButton, "butRightRotate")
    q = d.center(b)
    yield d.move(q, 800)
    d.click(q); yield 1500
    v = [o for o in doc.Objects if o.TypeId in ("TechDraw::DrawProjGroupItem", "TechDraw::DrawViewPart")][0]
    log("dir", v.Direction, v.XDirection, v.Scale, v.ScaleType)
    yield from steps.task_ok(d, gone="butCWRotate")
    doc.recompute()
    yield from d.until(lambda: page_view() is not None and len(v.getVisibleEdges()) > 0, 20000)
    yield 1200
    v = [o for o in doc.Objects if o.TypeId in ("TechDraw::DrawProjGroupItem", "TechDraw::DrawViewPart")][0]
    pts = [x.Point for e in v.getVisibleEdges() for x in e.Vertexes]
    log("vbox", v.Direction, v.Scale, min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts))
    yield d.say("比例 1:1，位置 X = 130、Y = 160")
    p = d.tree_item(v.Label)
    yield d.move(p, 800)
    d.click(p); yield 700
    if abs(v.Scale - 1) > 1e-6:
        yield from steps.prop_set(d, "1", ("基本", "Base"), L("比例", "Scale"))
    yield from steps.prop_set(d, "130 mm", ("基本", "Base"), "X")
    yield from steps.prop_set(d, "160 mm", ("基本", "Base"), "Y")
    if abs(v.Scale - 1) > 1e-6:
        log("scale fallback", v.ScaleType, v.Scale); v.ScaleType = "Custom"; v.Scale = 1.0
    doc.recompute(); yield 1500

    yield d.say("明细表：选中材料清单，菜单“工程图 → 来自其他工作台的视图 → 电子表格视图”，放到标题栏上面")
    Gui.Selection.clearSelection()
    p = d.tree_item(bom.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    path = menu_find(d, "TechDraw_SpreadsheetView")
    log("menu", path)
    yield from menu_path(d, *path)
    yield 2500
    sv = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewSpreadsheet"]
    log("sheet", [(o.Label, o.CellStart, o.CellEnd, o.X, o.Y) for o in sv])
    sv = sv[-1]
    sv.CellEnd = "C5"
    sv.Scale = 1.5
    p = d.tree_item(sv.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield from steps.prop_set(d, "335 mm", ("基本", "Base"), "X")
    yield from steps.prop_set(d, "95 mm", ("基本", "Base"), "Y")
    doc.recompute(); yield 1500

    yield d.say("零件序号：选中视图，点“气球”，在零件上点一下，序号的圆圈拉到旁边；按明细表的顺序 1–4")
    PP = part_pts(v, {n: links[n] for n in PARTS})
    log("pp", {n: (round(x, 1), round(y, 1)) for n, (x, y) in PP.items()})
    for k, name in enumerate(PARTS, 1):
        x, y = v.X.Value + PP[name][0], v.Y.Value + PP[name][1]
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, v.Name)
        yield d.tool("TechDraw_Balloon") if d.action_widget("TechDraw_Balloon") else d.tool("TechDraw_CompAnnotation", "TechDraw_Balloon")
        yield 800
        q = page_pt(x, y)
        yield d.move(q, 900)
        d.click(q)
        yield 1500
        bl = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewBalloon"]
        log("balloon", k, name, (round(x, 1), round(y, 1)), [(o.Name, o.Text, o.OriginX, o.OriginY, o.X, o.Y) for o in bl][-1:] if bl else None)
        if bl:
            b = bl[-1]
            if str(b.Text) != str(k):
                b.Text = str(k)
            b.OriginX, b.OriginY = PP[name]      # 点击位置有吸附偏差：引线起点放准
            b.X, b.Y = AIM[k - 1][2]
            log("bubble at", k, (round(b.X.Value, 1), round(b.Y.Value, 1)))
            doc.recompute()
        yield 1000

    yield d.say(L("标题栏：名称“曲柄滑块机构”、图号“LS-200”（练习用）、比例 1:1、材料“见明细表”",
                  "Title block: “Slider-crank mechanism”, drawing LS-200 (practice), scale 1:1"))
    F = ((("PARTNAME", 358.5, 265.5, "曲柄滑块机构"), ("PART_CODE_NAME", 390, 279, "LS-200"), ("scale", 352, 280, "1:1"),
          ("MATERIALMARK", 338, 255, "见明细表"))
         if not L(0, 1) else
         (("title", 231, 260.2, "Slider-crank mechanism"), ("document_type", 231, 272.2, "Assembly Drawing"), ("drawing_number", 231, 284.2, "LS-200"),
          ("scale", 360, 248.2, "1:1"), ("part_material", 231, 248.2, "see BOM"), ("creator", 316, 260.2, "WenQuest"), ("approval_person", 316, 272.2, "-")))
    for key, x, y, text in F:              # 图框 SVG 里可编辑字段的位置（毫米，左上角为原点）
        yield from field(d, x, 297 - y + 1.2, text)
        log("field", key, page.Template.EditableTexts.get(key))
    doc.recompute()
    yield 1500
    old = os.path.join(os.environ.get("WQ_REC", "."), "LS-200.pdf")
    if os.path.exists(old):
        os.remove(old)
    yield d.say("导出 PDF：文件 → 导出 PDF，LS-200")
    yield from menu_path(d, L("文件", "File"), L("导出 PDF", "Export PDF"))
    yield from steps.file_dialog(d, "LS-200.pdf")
    yield 2500
    log("pdf", os.path.exists(old), os.path.getsize(old) if os.path.exists(old) else 0)
    yield d.say("一张装配图：看得出零件怎么装在一起、各是什么、有几个。零件改了，视图和明细表重算后跟着变")
    yield 3000
    doc.save()


def main():
    d = Director()
    d.run(script(d))


boot(main)
