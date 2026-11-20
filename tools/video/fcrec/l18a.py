"""第 18 课 片段 A：针杆零件图加公差和技术要求——⌀8 加公差带 h5；插入“技术要求”文字；导出 PDF。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builtins
builtins._WQ_IMPORT_ONLY = True
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file, menu_path
import steps
from l17a import page_view, page_pt, place
from l17b import field


def script(d):
    doc = App.openDocument(model_file("针杆零件.FCStd", "NeedleBarPart.FCStd"))
    page = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawPage"][0]
    dims = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewDimension"]
    dia = [o for o in dims if o.FormatSpec.startswith("⌀")][0]
    yield from steps.pick_workbench(d, "TechDraw", "TechDraw")
    p = d.tree_item(page.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: page_view() is not None, 6000)
    yield 1500
    yield d.say("公差：双击 ⌀8 的尺寸，打开尺寸设置")
    p = d.tree_item(dia.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield 2500
    yield d.say("格式改成 ⌀%.0f h5；勾“任意公差”，上偏差 0、下偏差 −0.006（查 GB/T 1800：⌀8 h5）")
    yield from text_into(d, steps.named(QtWidgets.QLineEdit, "leFormatSpecifier"), "⌀%.0f h5")
    yield from check(d, "cbEqualTolerance", False)
    yield from check(d, "cbArbitraryTolerances", True)
    yield from text_into(d, steps.named(QtWidgets.QLineEdit, "leFormatSpecifierOverTolerance"), "0")
    yield from text_into(d, steps.named(QtWidgets.QLineEdit, "leFormatSpecifierUnderTolerance"), "-0.006")
    yield 1000
    yield from steps.task_ok(d, gone="leFormatSpecifier")
    if abs(dia.UnderTolerance.Value + 0.006) > 1e-6:
        log("tol fallback", dia.EqualTolerance, dia.UnderTolerance)
        dia.EqualTolerance = False
        dia.OverTolerance = 0.0
        dia.UnderTolerance = -0.006
    dia.ArbitraryTolerances = True
    dia.FormatSpecOverTolerance = "0"
    dia.FormatSpecUnderTolerance = "-0.006"
    doc.recompute()
    log("dia", dia.FormatSpec, dia.UnderTolerance, dia.OverTolerance)
    yield 1500
    yield d.say("技术要求：点“插入注释”，在属性“文本”里一行一行写")
    Gui.Selection.clearSelection()
    yield d.tool("TechDraw_Annotation") if d.action_widget("TechDraw_Annotation") else d.tool("TechDraw_CompAnnotation", "TechDraw_Annotation")
    yield 2000
    an = [o for o in doc.Objects if o.TypeId == "TechDraw::DrawViewAnnotation"]
    log("annot", [(o.Name, o.Text) for o in an])
    a = an[-1]
    p = d.tree_item(a.Label)
    yield d.move(p, 800)
    d.click(p); yield 700
    pe, q = steps.prop_pt(d, ("注释", "Annotation"), ("文本", "Text"))
    yield d.move(q, 800)
    d.click(q); yield 800
    lines = NOTES
    if list(a.Text) != lines:
        a.Text = lines
    a.TextSize = 4.0
    a.X, a.Y = L(100, 112), 84
    doc.recompute()
    yield 1500
    yield d.say("导出：菜单“文件 → 导出 PDF”，文件名 LS-201")
    if L(0, 1):        # 英文图框自带“General tolerances: ISO 2768-m”，改成和技术要求一致
        yield from field(d, 192, 210 - 161.2 + 1.2, "ISO 2768-f")
    old = os.path.join(os.environ.get("WQ_REC", "."), "LS-201.pdf")
    if os.path.exists(old):
        os.remove(old)      # 免得弹“已存在，替换吗”
    yield from menu_path(d, L("文件", "File"), L("导出 PDF", "Export PDF"))
    yield from steps.file_dialog(d, "LS-201.pdf")
    yield 2000
    pdf = os.path.join(os.environ.get("WQ_REC", "."), "LS-201.pdf")
    log("pdf", os.path.exists(pdf), os.path.getsize(pdf) if os.path.exists(pdf) else 0)
    yield d.say("PDF 发给车间、外协；要给别的 CAD 用，点工具栏的 DXF 按钮导出 DXF")
    yield 3000
    doc.save()


NOTES = L(["技术要求", "1. 淬火、回火 58–62 HRC；外圆镀硬铬 5–8 µm 后抛光。", "2. 外圆 Ra 0.2；直线度 0.005/100。",
           "3. 两端倒角 0.5×45°；未注尺寸公差 GB/T 1804-f。"],
          ["Technical notes", "1. Harden and temper 58–62 HRC; hard-chrome plate 5–8 µm and polish.", "2. Outside diameter Ra 0.2 µm; straightness 0.005/100.",
           "3. Chamfer both ends 0.5 × 45°; general tolerances ISO 2768-f."])     # 照整机的 LS-201（tools/wqls/g7_drawings.py）


def check(d, name, on):
    w = steps.named(QtWidgets.QCheckBox, name)
    steps.show(w)
    yield 300
    if w.isChecked() != on:
        p = d.center(w)
        yield d.move(p, 700)
        d.click(p)
        yield 700


def text_into(d, w, text):
    steps.show(w)
    yield 300
    p = d.center(w)
    yield d.move(p, 700)
    d.click(p); yield 300
    w.setFocus(); w.selectAll()
    d.keys(text, w=w)
    yield 700
    d.key(Qt.Key_Tab, w)
    yield 500

def main():
    d = Director()
    d.run(script(d))


boot(main)
