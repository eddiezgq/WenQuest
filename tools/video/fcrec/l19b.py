"""第 19 课 片段 B：出报告。接 19a 算完的分析：菜单“求解 → 出报告（零件库）”，语言、编号、版次、原因，
不让 AI 写解释；出 Word（本机有 LibreOffice 时同时出 PDF）。最后翻看报告各节。真操作（不调用 AI）。"""
import os
import subprocess
import sys
import tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtGui, QtWidgets, L, model_file, menu_path, EN
import steps

NUMBER = "WQ-FEA-019"


def run_cmd(d, cmd):
    path = steps.menu_find(d, cmd)
    log("menu", cmd, path)
    yield from menu_path(d, *path)


def modal(cls):
    m = QtWidgets.QApplication.activeModalWidget()
    if not isinstance(m, cls):
        return None
    try:
        m.objectName()
        if not m.isVisible():
            return None
    except RuntimeError:
        return None
    return m


def _alive(w):
    try:
        w.objectName()
        return w.isVisible()
    except RuntimeError:
        return False


def ok_of(dlg, texts=("OK", "确定")):
    """对话框里的按钮。PySide 偶尔把已删掉的旧对话框的包装对象给回来：按全部顶层窗口里活着的找"""
    bs = [b for b in QtWidgets.QApplication.allWidgets() if isinstance(b, QtWidgets.QPushButton) and _alive(b)
          and b.text().replace("&", "") in texts and isinstance(b.window(), (QtWidgets.QInputDialog, QtWidgets.QMessageBox))]
    return bs[0]


def press(d, b):
    p = d.center(b)
    yield d.move(p, 600)
    d.ring(p)
    QtCore.QTimer.singleShot(0, b.click)
    yield 900


def wait_dialog(d, cls=QtWidgets.QInputDialog):
    """等下一个对话框（不是刚点过的那个：点过的会打上记号）"""
    yield from d.until(lambda: modal(cls) is not None and not modal(cls).property("wq_seen"), 10000)
    modal(cls).setProperty("wq_seen", True)
    yield 900


def script(d):
    doc = App.openDocument(model_file("针杆曲柄.FCStd", "NeedleBarCrank.FCStd"))
    yield from steps.pick_workbench(d, "FEM", "FEM")
    an = [o for o in doc.Objects if o.TypeId == "Fem::FemAnalysis"][0]
    pipes = [o for o in an.Group if o.TypeId == "Fem::FemPostPipeline"]
    for o in doc.Objects:
        if hasattr(o, "ViewObject") and o.ViewObject is not None and o not in pipes:
            o.ViewObject.Visibility = False
    for pp in pipes:
        pp.ViewObject.Visibility = True
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("上一段算完、核查通过。要留档、给别人审，就出报告")
    p = d.tree_item(an.Label)
    yield d.move(p, 700)
    d.click(p)
    yield 800
    yield d.say("选中“分析”，菜单“求解 → 出报告（零件库）”")
    yield from run_cmd(d, "FAP_FemReport")
    # 1. 语言
    yield from wait_dialog(d)
    dlg = modal(QtWidgets.QInputDialog)
    yield d.say("报告语言：中文、英文都能出（数字一样，文字不同）")
    combo = dlg.findChild(QtWidgets.QComboBox)
    yield from steps.combo_pick(d, combo, 1 if EN else 0)
    yield from press(d, ok_of(dlg))
    # 2. 编号
    yield from wait_dialog(d)
    dlg = modal(QtWidgets.QInputDialog)
    yield d.say("报告编号由质量体系分配，可以空着；这里填一个")
    le = dlg.findChild(QtWidgets.QLineEdit)
    yield d.move(d.center(le), 600)
    d.click(d.center(le))
    yield 300
    le.selectAll()
    d.keys(NUMBER, w=le)
    yield 800
    yield from press(d, ok_of(dlg))
    # 3. 版次、4. 原因：用默认
    yield from wait_dialog(d)
    yield d.say("版次 A、改版原因“首次出稿”：用默认，确定")
    yield 1500
    yield from press(d, ok_of(modal(QtWidgets.QInputDialog)))
    yield from wait_dialog(d)
    yield from press(d, ok_of(modal(QtWidgets.QInputDialog)))
    # 5. AI 解释：不要
    yield from wait_dialog(d, QtWidgets.QMessageBox)
    m = modal(QtWidgets.QMessageBox)
    log("question", m.text())
    yield d.say("问要不要让 AI 写“解释与建议”：数字都由程序填，AI 不判定合不合格。这一课不用 AI，点“否”")
    yield 2500
    yield from press(d, ok_of(m, ("否", "No", "&No")))
    yield from d.until(lambda: modal(QtWidgets.QMessageBox) is not None, 300000, 300)
    yield 1200
    m = modal(QtWidgets.QMessageBox)
    text = m.text() if m else ""
    log("result", text)
    docx = pdf = None
    for line in text.splitlines():
        for k in ("报告：", "Report:", "Report: "):
            if line.startswith(k):
                docx = line[len(k):].strip()
        for k in ("PDF：", "PDF:"):
            if line.startswith(k):
                pdf = line[len(k):].strip()
    yield d.say("报告出来了：Word 一份；本机装了 LibreOffice，同时转出 PDF")
    yield 3000
    yield from steps.answer_modal(d)
    yield 800
    # 6. 翻看报告（PDF 每页转成图）
    if not pdf and docx and os.path.isfile(docx):
        env = {k: v for k, v in os.environ.items() if k not in ("LD_LIBRARY_PATH", "PYTHONHOME", "PYTHONPATH", "QT_PLUGIN_PATH")}
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(docx), docx], env=env, capture_output=True, timeout=300)
        pdf = os.path.splitext(docx)[0] + ".pdf"
    log("files", docx, pdf, pdf and os.path.isfile(pdf))
    if not pdf or not os.path.isfile(pdf):
        return
    tmp = tempfile.mkdtemp(prefix="wq19b-")
    env = {k: v for k, v in os.environ.items() if k not in ("LD_LIBRARY_PATH", "PYTHONHOME", "PYTHONPATH")}
    subprocess.run(["pdftoppm", "-r", "80", "-png", pdf, os.path.join(tmp, "p")], env=env, check=True, timeout=120)
    pages = sorted(os.path.join(tmp, f) for f in os.listdir(tmp) if f.endswith(".png"))
    log("pages", len(pages))
    w = QtWidgets.QDialog(d.mw)
    w.setWindowTitle(os.path.basename(pdf))
    w.resize(760, 860)
    lay = QtWidgets.QVBoxLayout(w)
    sa = QtWidgets.QScrollArea(w)
    lab = QtWidgets.QLabel()
    sa.setWidget(lab)
    sa.setWidgetResizable(True)
    lay.addWidget(sa)
    w.move(d.mw.geometry().center() - QtCore.QPoint(380, 430))

    def show(i):
        pm = QtGui.QPixmap(pages[i]).scaledToWidth(720, Qt.SmoothTransformation)
        lab.setPixmap(pm)
        sa.verticalScrollBar().setValue(0)
    show(0)
    w.show()
    yield 1000
    yield d.say("打开看看。第一页：结论摘要——最大应力、安全系数、可信度；下面是零件和材料（带出处）")
    yield 6000
    talk = [L("约束和载荷、分析步；再是网格与可信度核查：三层网格的最大应力、位移，每项的判定",
              "Constraints, loads, steps; then mesh and trust checks: max stress and displacement on three mesh levels, a verdict for each"),
            L("结果：应力、位移云图", "Results: stress and displacement plots"),
            L("没让 AI 写解释，这一节空着；然后是局限、审核清单——签字前逐项核对",
              "No AI explanation, so that section is empty; then limitations and a review checklist — check item by item before signing"),
            L("最后是可追溯信息：程序版本、文件指纹、改版记录", "Finally traceability: program versions, file fingerprints, revision history")]
    for i in range(1, min(len(pages), 5)):
        show(i)
        if i - 1 < len(talk):
            yield d.say(talk[i - 1])
        yield 4500
    w.close()
    yield d.say("报告是专业版功能；免费版能算、能看结果和核查")
    yield 3000


def main():
    d = Director()
    d.run(script(d))


boot(main)
