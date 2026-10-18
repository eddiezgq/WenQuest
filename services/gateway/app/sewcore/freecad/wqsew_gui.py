# -*- coding: utf-8 -*-
"""问渠缝纫机工作台：命令与面板（校核结果、时序图、转动机构、导入导出、提交到问渠工厂）。"""
import os
import sys

import FreeCAD as App
import FreeCADGui as Gui

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import wqsew_feature as F  # noqa: E402

try:
    from PySide import QtCore, QtGui
    QtW = QtGui
except Exception:  # noqa: BLE001
    from PySide2 import QtCore, QtGui, QtWidgets as QtW  # type: ignore

ICON = os.path.join(HERE, "wqsew.svg")
COLOR = {"ok": "#2e9e6a", "warn": "#e8913a", "bad": "#c0392b"}
WORD = {"ok": "合格", "warn": "注意", "bad": "不合格"}


def design(silent=False):
    sel = [o for o in Gui.Selection.getSelection() if getattr(o, "Proxy", None).__class__.__name__ == "SewDesign"]
    if sel:
        return sel[0]
    doc = App.ActiveDocument
    if doc:
        for o in doc.Objects:
            if getattr(o, "Proxy", None).__class__.__name__ == "SewDesign":
                return o
    if not silent:
        QtW.QMessageBox.information(None, "问渠缝纫机", "先点“新建平缝机设计”。")
    return None


# ---------- 面板 ----------
def show_checks(obj=None):
    obj = obj or design()
    if not obj:
        return
    R = F.result(obj)
    dlg = QtW.QDialog(Gui.getMainWindow())
    dlg.setWindowTitle("校核结果 · " + obj.Label)
    dlg.resize(820, 640)
    lay = QtW.QVBoxLayout(dlg)
    k = R.get("key", {})
    tr = R.get("trial", {}).get("counts", {})
    head = QtW.QLabel("<b>{}</b>　λ = {:.3f}　针杆惯性力 {:.0f} N　钩线角 {:.1f}°　整机惯性力 {:.0f} N　共振转速 {:.0f} r/min<br>"
                      "虚拟试缝 30 针：成缝 {}，跳针 {}，碰针 {}，划线 {}，断线 {}".format(
                          obj.Status, k.get("lam", 0), k.get("F_bdc", 0), k.get("fc", 0), k.get("fmax", 0), k.get("n_res", 0),
                          tr.get("ok", 0), tr.get("skip", 0), tr.get("hit", 0), tr.get("cut", 0), tr.get("break", 0)))
    head.setWordWrap(True)
    lay.addWidget(head)
    t = QtW.QTableWidget(len(R.get("checks", [])), 5)
    t.setHorizontalHeaderLabels(["结论", "校核项", "数值", "判据", "建议"])
    for i, c in enumerate(R.get("checks", [])):
        cells = [WORD[c["state"]], "第{}讲 {}".format(c["lecture"], c["name"]["zh"]), c["value"]["zh"], c["limit"]["zh"], c["advice"]["zh"]]
        for j, v in enumerate(cells):
            it = QtW.QTableWidgetItem(str(v))
            if j == 0:
                it.setForeground(QtGui.QBrush(QtGui.QColor(COLOR[c["state"]])))
                f = it.font()
                f.setBold(True)
                it.setFont(f)
            t.setItem(i, j, it)
    t.resizeColumnsToContents()
    t.horizontalHeader().setStretchLastSection(True)
    lay.addWidget(t)
    btn = QtW.QPushButton("关闭")
    btn.clicked.connect(dlg.accept)
    lay.addWidget(btn)
    dlg.show()
    dlg.exec_() if hasattr(dlg, "exec_") else dlg.exec()


class TimingView(QtW.QWidget):
    def __init__(self, R):
        super().__init__()
        self.R = R
        self.setMinimumSize(760, 260)

    def paintEvent(self, ev):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        W, H = self.width(), self.height()
        L, Rr, top = 190, 20, 20
        rows = self.R.get("timing", [])
        rh = (H - top - 40) / max(1, len(rows))
        x = lambda a: L + (W - L - Rr) * a / 360.0  # noqa: E731
        p.setPen(QtGui.QColor("#c8d0d8"))
        for a in range(0, 361, 30):
            p.drawLine(int(x(a)), top, int(x(a)), int(H - 30))
            p.drawText(int(x(a)) - 10, int(H - 12), str(a))
        cols = ["#2d6fb3", "#7d5ba6", "#c0392b", "#2e9e6a", "#e8913a"]
        for i, t in enumerate(rows):
            y = top + i * rh
            p.setPen(QtGui.QColor("#1f2a33"))
            p.drawText(8, int(y + rh * 0.65), t["zh"])
            a, b = t["a"], t["b"]
            segs = [(a, b)] if b >= a else [(a, 360), (0, b)]
            if a == b:
                segs = [(a - 1, a + 1)]
            for s0, s1 in segs:
                p.fillRect(QtCore.QRectF(x(s0), y + rh * 0.2, x(s1) - x(s0), rh * 0.6), QtGui.QColor(cols[i % 5]))
            if "mark" in t:
                p.setPen(QtGui.QPen(QtGui.QColor("#000"), 2))
                p.drawLine(int(x(t["mark"])), int(y + rh * 0.1), int(x(t["mark"])), int(y + rh * 0.9))
        p.end()


def show_timing():
    obj = design()
    if not obj:
        return
    dlg = QtW.QDialog(Gui.getMainWindow())
    dlg.setWindowTitle("全机运动时序 · " + obj.Label)
    lay = QtW.QVBoxLayout(dlg)
    lay.addWidget(TimingView(F.result(obj)))
    lay.addWidget(QtW.QLabel("横轴：主轴转角（°），0° = 针杆上止点。黑线：实际钩线角。"))
    dlg.show()
    dlg.exec_() if hasattr(dlg, "exec_") else dlg.exec()


# ---------- 转动 ----------
_TIMER = {"t": None}


def toggle_spin():
    obj = design()
    if not obj:
        return
    if _TIMER["t"]:
        _TIMER["t"].stop()
        _TIMER["t"] = None
        return
    t = QtCore.QTimer()

    def tick():
        try:
            phi = (obj.Phi.Value + 6) % 360
            obj.Proxy.update_parts(obj, obj.Proxy.params(obj), phi)
            obj.Phi = phi
            obj.purgeTouched()
            Gui.updateGui()
        except Exception:  # noqa: BLE001
            t.stop()
            _TIMER["t"] = None
    t.timeout.connect(tick)
    t.start(40)
    _TIMER["t"] = t


# ---------- 命令 ----------
class Cmd:
    def __init__(self, text, tip, fn, needs=True):
        self.text, self.tip, self.fn, self.needs = text, tip, fn, needs

    def GetResources(self):
        return {"MenuText": self.text, "ToolTip": self.tip}      # 不给图标：工具栏直接显示中文按钮名，一看就懂

    def Activated(self):
        try:
            self.fn()
        except Exception as e:  # noqa: BLE001
            QtW.QMessageBox.warning(None, "问渠缝纫机", str(e))

    def IsActive(self):
        return App.ActiveDocument is not None or not self.needs


def new_design():
    obj = F.add_design()
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(obj)
    try:
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewIsometric()
    except Exception:  # noqa: BLE001
        pass


def recompute():
    if App.ActiveDocument:
        obj = design(True)
        if obj:
            obj.touch()
        App.ActiveDocument.recompute()


def _file(save, title, filt):
    if save:
        r = QtW.QFileDialog.getSaveFileName(Gui.getMainWindow(), title, "", filt)
    else:
        r = QtW.QFileDialog.getOpenFileName(Gui.getMainWindow(), title, "", filt)
    return r[0] if isinstance(r, tuple) else r


def export_step():
    obj = design()
    if obj:
        path = _file(True, "导出 STEP", "STEP (*.step *.stp)")
        if path:
            F.export_step(obj, path)


def export_params():
    obj = design()
    if obj:
        path = _file(True, "导出参数", "问渠缝纫机参数 (*.wqsew.json *.json)")
        if path:
            F.export_params(obj, path)


def import_params():
    obj = design()
    if obj:
        path = _file(False, "导入参数（问渠网页版导出的参数文件）", "问渠缝纫机参数 (*.wqsew.json *.json)")
        if path:
            F.import_params(obj, path)


def submit():
    """提交到问渠工厂：用已装的“问渠”工作台（数字工厂企业版宏包）的提交对话框"""
    obj = design()
    if not obj:
        return
    found = None
    for base in (App.getUserAppDataDir(), getattr(App, "getUserModDir", lambda: "")()):
        for p in (os.path.join(base, "Mod", "WenQuest"), os.path.join(base, "WenQuest")):
            if os.path.exists(os.path.join(p, "wq_submit.py")):
                found = p
    if not found:
        QtW.QMessageBox.information(None, "问渠缝纫机", "没找到“问渠”工作台。请在问渠数字工厂“设计与工艺”页下载宏包并安装后再提交；"
                                    "也可以先“导出 STEP”再在数字工厂网页上传。")
        return
    doc = obj.Document
    comp = doc.getObject("SewAssembly") or doc.addObject("Part::Compound", "SewAssembly")
    comp.Label = obj.Label + "（机构零件）"
    comp.Links = list(obj.Parts)
    doc.recompute()
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(comp)
    if found not in sys.path:
        sys.path.insert(0, found)
    import importlib
    importlib.import_module("wq_submit").run_dialog()


def register():
    cmds = [("WQS_New", Cmd("新建平缝机设计", "按默认（教材算例）参数生成平缝机机构零件和校核", new_design)),
            ("WQS_Recompute", Cmd("重新计算", "改了参数后重算零件与校核（Ctrl+R 也可以）", recompute)),
            ("WQS_Checks", Cmd("校核结果", "红绿灯列表：惯性力、钩线、挑线、送布、张力、共振、尺寸链", show_checks)),
            ("WQS_Timing", Cmd("时序图", "针杆、钩线窗口、送布、挑线的时序", show_timing)),
            ("WQS_Spin", Cmd("转动机构", "让主轴转起来看运动（再点一次停止）", toggle_spin)),
            ("WQS_Step", Cmd("导出 STEP", "整套机构零件导出 STEP", export_step)),
            ("WQS_Import", Cmd("导入参数", "读入问渠网页版导出的参数文件（.wqsew.json）", import_params)),
            ("WQS_Export", Cmd("导出参数", "存成参数文件，可在问渠网页版打开", export_params)),
            ("WQS_Submit", Cmd("提交到问渠工厂", "用“问渠”工作台把整套零件提交到数字工厂审批", submit))]
    for name, c in cmds:
        Gui.addCommand(name, c)
    return [n for n, _ in cmds]
