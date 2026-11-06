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
    tr = R.get("trial", {}).get("counts")
    res = "　".join("{} {} {}".format(r["zh"], r["value"], r["unit"]) for r in R.get("results", [])[:6])
    txt = "<b>{}</b>　{}".format(obj.Status, res)
    if tr:
        txt += "<br>虚拟试缝 30 针：成缝 {}，跳针 {}，碰针 {}，划线 {}，断线 {}".format(tr["ok"], tr["skip"], tr["hit"], tr["cut"], tr["break"])
    head = QtW.QLabel(txt)
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
    if any(c["state"] != "ok" for c in R.get("checks", [])):      # 第 94 轮：双击红黄灯那一行，三维停到出问题的地方
        tip = QtW.QLabel("双击红 / 黄灯那一行：三维停到出问题的转角（花样机、刺绣机停到那一针，横机停到那一趟），"
                         "出问题的部件选中；再点“转动机构”就从这里慢转。")
        tip.setWordWrap(True)
        lay.addWidget(tip)
    checks = R.get("checks", [])

    def dbl(row, _col=0):
        if 0 <= row < len(checks) and checks[row]["state"] != "ok":
            msg = goto(obj, checks[row]["key"])
            if msg:
                dlg.accept()
            else:                                           # 第 94 轮以前存的文件：还没算过出问题的部件
                QtW.QMessageBox.information(dlg, "问渠缝纫机", "先点“重新计算”（Ctrl+R），再双击。")
    t.setEditTriggers(QtW.QAbstractItemView.NoEditTriggers)    # 双击是“停到出问题的地方”，不是改格子
    t.cellDoubleClicked.connect(dbl)
    t.setMinimumHeight(min(len(checks), 8) * 30 + 40)     # 第 94 轮：下面的表很长时（花样机每针表）校核表不被挤成一行
    lay.addWidget(t, 3)
    if R.get("tables"):
        box = QtW.QWidget()
        bl = QtW.QVBoxLayout(box)
        for tb in R.get("tables", []):
            cell = lambda c: c[0] if isinstance(c, (list, tuple)) else str(c)  # noqa: E731
            html = "<b>{}</b><table cellpadding='4' border='1' cellspacing='0'><tr>{}</tr>{}</table>".format(
                tb["zh"], "".join("<th>{}</th>".format(h[0]) for h in tb["head"]),
                "".join("<tr>{}</tr>".format("".join("<td>{}</td>".format(cell(c)) for c in r)) for r in tb["rows"]))
            lab = QtW.QLabel(html)
            lab.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            bl.addWidget(lab)
        sc = QtW.QScrollArea()
        sc.setWidgetResizable(True)
        sc.setWidget(box)
        lay.addWidget(sc, 2)
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
    R = F.result(obj)
    lay.addWidget(TimingView(R))
    lay.addWidget(QtW.QLabel("横轴：机头走一趟的时间（0–360 表示 0–100%）。" if R.get("timing_x") == "pass"
                             else "横轴：主轴转角（°），0° = 针杆上止点。黑线：实际钩线角。"))
    dlg.show()
    dlg.exec_() if hasattr(dlg, "exec_") else dlg.exec()


# ---------- 转动 ----------
_TIMER = {"t": None, "slow": False}


def toggle_spin():
    obj = design()
    if not obj:
        return
    if _TIMER["t"]:
        _TIMER["t"].stop()
        _TIMER["t"] = None
        _TIMER["slow"] = False
        return
    t = QtCore.QTimer()
    p = obj.Proxy.params(obj)
    whole = F.span(obj, p)               # 主轴机型 360°；花样、刺绣、横机走完全部针 / 趟再从头
    fast = 18.0 if obj.Machine == "flatknit" else 6.0     # 横机一片几百趟：一格走得多一点（每趟 0.8 秒）
    step = fast / 6.0 if _TIMER["slow"] else fast

    def tick():
        try:
            phi = (F.get_phi(obj) + step) % whole
            obj.Proxy.update_parts(obj, p, phi)
            F.set_phi(obj, phi)
            obj.purgeTouched()
            Gui.updateGui()
        except Exception:  # noqa: BLE001
            t.stop()
            _TIMER["t"] = None
    t.timeout.connect(tick)
    t.start(40)
    _TIMER["t"] = t


def goto(obj, key):
    """第 94 轮：停到这一项出问题的地方，选中出问题的部件；返回状态栏上那句话（没有对应的部件时返回空）"""
    h = F.hotspot_of(obj, key)
    if not h:
        return ""
    if _TIMER["t"]:
        _TIMER["t"].stop()
        _TIMER["t"] = None
    p = obj.Proxy.params(obj)
    where = ""
    if h.get("phi") is not None:
        obj.Proxy.update_parts(obj, p, h["phi"])
        F.set_phi(obj, h["phi"])
        obj.purgeTouched()
        where = F.progress_text(obj, p, h["phi"])
    Gui.Selection.clearSelection()
    for o in obj.Parts or []:
        if getattr(o, "SewKey", "") in (h.get("names") or []):
            Gui.Selection.addSelection(o)
    _TIMER["slow"] = True
    name = (h.get("name") or {}).get("zh", key)
    msg = "{}：{}".format(WORD.get(h["state"], ""), name) + ("，停在 {}。再点“转动机构”从这里慢转。".format(where) if where else
                                                          "：整圈都要看，没有停到某个转角；出问题的部件已选中，点“转动机构”慢转一圈看。")
    try:
        Gui.getMainWindow().statusBar().showMessage(msg, 15000)
    except Exception:  # noqa: BLE001
        pass
    Gui.updateGui()
    return msg


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


def new_design(machine="lockstitch"):
    obj = F.add_design(machine=machine)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(obj)
    try:
        v = Gui.activeDocument().activeView()
        v.viewIsometric()
        v.fitAll()                          # FreeCAD 1.0 里 SendMsgToActiveView("ViewFit") 不认了
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
    if obj and not obj.Parts:
        QtW.QMessageBox.information(None, "问渠缝纫机", "还没有零件：先点“重新计算”。")
        return
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



# ---------- 第 49 轮：AI 助手、本单位零件库、帮助 ----------
import html as _html  # noqa: E402
import json as _json  # noqa: E402

import wqsew_net as N  # noqa: E402


def key_dialog(parent=None):
    """填钥匙和服务器地址（只在本机保存）"""
    st = N.settings()
    d = QtW.QDialog(parent or Gui.getMainWindow())
    d.setWindowTitle("问渠缝纫机 · 设置钥匙")
    lay = QtW.QFormLayout(d)
    tip = QtW.QLabel("钥匙在问渠网页版“缝纫机设计 → 零件库 → FreeCAD 钥匙”里生成，每人一把，只显示一次。")
    tip.setWordWrap(True)
    lay.addRow(tip)
    k = QtW.QLineEdit(st["key"])
    k.setEchoMode(QtW.QLineEdit.Password)
    sv = QtW.QLineEdit(st["server"])
    lay.addRow("钥匙", k)
    lay.addRow("服务器", sv)
    bb = QtW.QDialogButtonBox(QtW.QDialogButtonBox.Ok | QtW.QDialogButtonBox.Cancel)
    bb.accepted.connect(d.accept)
    bb.rejected.connect(d.reject)
    lay.addRow(bb)
    if d.exec_():
        N.save_settings(sv.text(), k.text())
        return True
    return False


def _need_key():
    return bool(N.settings()["key"]) or key_dialog()


class AiDialog(QtW.QDialog):
    """一句话改设计、解释红黄灯、写设计说明；判定由问渠服务器上的计算核心做，人点“采用”才改属性"""

    def __init__(self, obj):
        super().__init__(Gui.getMainWindow())
        self.obj, self.adopt = obj, None
        self.setWindowTitle("问渠缝纫机 · AI 助手（" + obj.Label + "）")
        self.resize(720, 560)
        lay = QtW.QVBoxLayout(self)
        self.ed = QtW.QPlainTextEdit()
        self.ed.setPlaceholderText("例：转速提到 6000，其他尽量不动，全部合格")
        self.ed.setMaximumHeight(70)
        lay.addWidget(self.ed)
        row = QtW.QHBoxLayout()
        for text, kind in (("起草改法", "draft"), ("解释红黄灯", "explain"), ("写设计说明", "describe")):
            b = QtW.QPushButton(text)
            b.clicked.connect(lambda _=False, k=kind: self.run(k))
            row.addWidget(b)
        self.ok = QtW.QPushButton("采用")
        self.ok.setEnabled(False)
        self.ok.clicked.connect(self.apply)
        row.addStretch(1)
        row.addWidget(self.ok)
        kb = QtW.QPushButton("设置钥匙")
        kb.clicked.connect(lambda: key_dialog(self))
        row.addWidget(kb)
        lay.addLayout(row)
        self.out = QtW.QTextBrowser()
        lay.addWidget(self.out, 1)

    def run(self, kind):
        if kind == "draft" and len(self.ed.toPlainText().strip()) < 2:
            self.out.setHtml("先写一句你要什么。")
            return
        M = F.SewDesign.machine(self.obj)
        p = self.obj.Proxy.params(self.obj)
        self.out.setHtml("AI 在想…")
        QtW.QApplication.processEvents()
        try:
            r = N.Client().ai(kind, M.MACHINE, p, self.ed.toPlainText())
        except N.NetError as e:
            self.out.setHtml(_html.escape(str(e)))
            return
        self.adopt = None
        e = _html.escape
        h = []
        if kind == "draft":
            b, a = r["before"], r["after"]
            h.append("<p><b style='color:{}'>{}</b>　改前 红 {} 黄 {} → 改后 红 {} 黄 {}</p>".format(
                COLOR["ok" if r["status"] == "ok" else "bad"], "通过计算核心校核" if r["status"] == "ok" else "没通过：改完红灯变多了",
                b["bad"], b["warn"], a["bad"], a["warn"]))
            h.append("<table border=1 cellspacing=0 cellpadding=4><tr><th>参数</th><th>原来</th><th>改成</th><th>为什么</th></tr>")
            for c in r["changes"]:
                h.append("<tr><td>{} {}</td><td>{}</td><td><b>{}</b></td><td>{}{}</td></tr>".format(e(c["name"]), e(c["unit"]), c["old"], c["new"],
                                                                                                e(c["why"]), ("（" + e(c["note"]) + "）") if c["note"] else ""))
            h.append("</table>")
            if r["new_bad"]:
                h.append("<p style='color:#c0392b'>新出现的红灯：" + "、".join(e(x["name"]) for x in r["new_bad"]) + "</p>")
            h += ["<p>· " + e(x) + "</p>" for x in r["assumptions"]] + ["<p>？" + e(x) + "</p>" for x in r["questions"]]
            if r["status"] == "ok" and r["changes"]:
                self.adopt = {c["key"]: c["new"] for c in r["changes"]}
        elif kind == "explain":
            if r.get("all_ok"):
                h.append("<p>现在全部合格，没有要解释的。</p>")
            for it in r["items"]:
                h.append("<p><b style='color:{}'>●</b> <b>{}</b>　{}（判据 {}）<br>{}</p>".format(COLOR[it["state"]], e(it["name"]), e(it["value"]),
                                                                                             e(it["limit"]), e(it["why"])))
                for fx in it["fixes"]:
                    ok = fx["clears"] and fx["params"]
                    h.append("<p style='margin-left:16px'>→ {} {} → <b>{}</b> {}：{}　<span style='color:{}'>{}</span></p>".format(
                        e(fx["name"]), fx["old"], fx["new"], e(fx["unit"]), e(fx["how"]), COLOR["ok" if ok else "bad"],
                        "试算过：能消掉这盏灯" if ok else "试算过：消不掉或会出新红灯"))
                    if ok and self.adopt is None:
                        self.adopt = {fx["key"]: fx["new"]}
            if self.adopt:
                h.append("<p>“采用”用第一条能消灯的改法。</p>")
        else:
            h.append("<p>" + e("".join(r["sentences"])) + "</p>")
            if r["dropped"]:
                h.append("<p style='color:#8a4b00'>有 {} 句里的数在这组设计里找不到出处，已删掉。</p>".format(len(r["dropped"])))
        h.append("<p style='color:#888'>今天还能用 {} 次 · {}</p>".format(r.get("left_today"), "规则版" if r.get("model") == "rules" else r.get("model") or ""))
        self.out.setHtml("".join(h))
        self.ok.setEnabled(bool(self.adopt))

    def apply(self):
        if self.adopt:
            done = F.apply_params(self.obj, self.adopt)
            self.out.append("<p><b>已采用：</b>" + "，".join("{} = {}".format(k, v) for k, v in done.items()) + "</p>")
            self.ok.setEnabled(False)
            self.adopt = None


def ai_dialog():
    obj = design()
    if obj and _need_key():
        AiDialog(obj).exec_()


class PartsDialog(QtW.QDialog):
    """查本单位零件库，插入 STEP；能接进当前设计的，可以直接“用到设计”"""

    def __init__(self):
        super().__init__(Gui.getMainWindow())
        self.setWindowTitle("问渠缝纫机 · 插入本单位零件")
        self.resize(760, 480)
        self.items = []
        lay = QtW.QVBoxLayout(self)
        row = QtW.QHBoxLayout()
        self.q = QtW.QLineEdit()
        self.q.setPlaceholderText("编号、名称或 ERP 物料号")
        self.q.returnPressed.connect(self.load)
        b = QtW.QPushButton("查找")
        b.clicked.connect(self.load)
        kb = QtW.QPushButton("设置钥匙")
        kb.clicked.connect(lambda: key_dialog(self))
        row.addWidget(self.q, 1)
        row.addWidget(b)
        row.addWidget(kb)
        lay.addLayout(row)
        self.lst = QtW.QListWidget()
        lay.addWidget(self.lst, 1)
        self.info = QtW.QLabel("")
        self.info.setWordWrap(True)
        lay.addWidget(self.info)
        row = QtW.QHBoxLayout()
        self.ins = QtW.QPushButton("插入三维")
        self.ins.clicked.connect(self.insert)
        self.use = QtW.QPushButton("用到当前设计")
        self.use.clicked.connect(self.use_in_design)
        row.addStretch(1)
        row.addWidget(self.use)
        row.addWidget(self.ins)
        lay.addLayout(row)
        self.lst.currentRowChanged.connect(self.pick)
        self.load()

    def load(self):
        try:
            r = N.Client().parts(self.q.text())
        except N.NetError as e:
            self.info.setText(str(e))
            return
        self.items = r["parts"]
        self.lst.clear()
        for p in self.items:
            self.lst.addItem("{}　{}　{}{}".format(p["code"], p["name"], "" if p["has_step"] else "（没有三维）", "　ERP " + p["erp"] if p["erp"] else ""))
        self.info.setText("{} 的零件库：可用的 {} 个。".format(r["org"], len(self.items)))

    def cur(self):
        i = self.lst.currentRow()
        return self.items[i] if 0 <= i < len(self.items) else None

    def pick(self, _i):
        p = self.cur()
        if not p:
            return
        obj = design(True)
        uses = []
        if obj:
            try:
                uses = N.Client().part(p["id"], F.SewDesign.machine(obj).MACHINE).get("uses") or []
            except N.NetError:
                uses = []
        self._uses = uses
        f = "，".join("{} {}".format(k, v) for k, v in p["fields"].items())
        self.info.setText("{} {}：{}{}".format(p["code"], p["name"], f, ("\n能用到当前设计：" + "；".join(
            "{}（{}）".format(u["label"], "，".join("{} = {}".format(k, v) for k, v in u["params"].items())) for u in uses)) if uses else ""))
        self.ins.setEnabled(p["has_step"])
        self.use.setEnabled(bool(uses))

    def insert(self):
        p = self.cur()
        if not p:
            return
        try:
            data = N.Client().step(p["id"])
        except N.NetError as e:
            self.info.setText(str(e))
            return
        path = os.path.join(N.cache_dir(), "{}-{}.step".format(p["id"], "".join(ch for ch in p["code"] if ch.isalnum() or ch in "-_") or "part"))
        with open(path, "wb") as fh:
            fh.write(data)
        doc = App.ActiveDocument or App.newDocument("WenQuestSewing")
        before = set(o.Name for o in doc.Objects)
        import Part
        shape = Part.read(path)
        o = doc.addObject("Part::Feature", "OrgPart")
        o.Shape = shape
        o.Label = "{} {}".format(p["code"], p["name"])
        o.addProperty("App::PropertyString", "WQ_OrgPart", "问渠", "本单位零件库编号")
        o.addProperty("App::PropertyString", "WQ_ErpItem", "问渠", "ERP 物料号")
        o.WQ_OrgPart, o.WQ_ErpItem = p["code"], p["erp"] or ""
        doc.recompute()
        self.info.setText("已插入：{}（{}）".format(o.Label, len(set(x.Name for x in doc.Objects) - before)))
        try:
            Gui.activeDocument().activeView().fitAll()
        except Exception:  # noqa: BLE001
            pass

    def use_in_design(self):
        obj = design()
        uses = getattr(self, "_uses", [])
        if not obj or not uses:
            return
        u = uses[0]
        if len(uses) > 1:
            names = [x["label"] for x in uses]
            name, ok = QtW.QInputDialog.getItem(self, "用到当前设计", "用作：", names, 0, False)
            if not ok:
                return
            u = uses[names.index(name)]
        done = F.apply_params(obj, u["params"])
        self.info.setText("已用到设计（{}）：{}".format(u["label"], "，".join("{} = {}".format(k, v) for k, v in done.items())))


def insert_part():
    if _need_key():
        PartsDialog().exec_()


# ---------- 第 62 轮：电控箱（热、电容寿命、开关时间；参数化外壳）----------
EBOX_FIELDS = ["src", "Irun", "Ipk", "Kt", "starts", "duty", "Ta", "tsw", "fsw", "clog", "rbox_src", "L", "W", "H", "wall", "fins", "fin_h", "fin_t",
               "air", "vfan"]


class EboxDialog(QtW.QDialog):
    """电控箱：常改的几项参数（其余用默认，网页版能改全部）→ 计算核心算结温、电容寿命、开关时间窗口和改进方案；在文档里建外壳"""

    def __init__(self, obj):
        from sewcore import ebox as EB
        super().__init__(Gui.getMainWindow())
        self.obj, self.EB = obj, EB
        M = F.SewDesign.machine(obj)
        self.q = EB.defaults_for(M.MACHINE)
        self.setWindowTitle("电控箱 · " + obj.Label)
        self.resize(900, 720)
        lay = QtW.QHBoxLayout(self)
        left = QtW.QFormLayout()
        self.w = {}
        for k in EBOX_FIELDS:
            sp = EB.PARAMS[k]
            if k in EB.CHOICES:
                cb = QtW.QComboBox()
                for c in EB.CHOICES[k]:
                    cb.addItem(c[1], c[0])
                cb.setCurrentIndex([c[0] for c in EB.CHOICES[k]].index(self.q[k]))
                self.w[k] = cb
            else:
                box = QtW.QDoubleSpinBox()
                box.setRange(sp[5], sp[6])
                box.setSingleStep(sp[7])
                box.setDecimals(3 if sp[7] < 0.01 else 2 if sp[7] < 1 else 0)
                box.setValue(float(self.q[k]))
                self.w[k] = box
            left.addRow("{}{}".format(sp[1], " · " + sp[3] if sp[3] else ""), self.w[k])
        lw = QtW.QWidget()
        lw.setLayout(left)
        sc = QtW.QScrollArea()
        sc.setWidget(lw)
        sc.setWidgetResizable(True)
        sc.setMinimumWidth(380)
        lay.addWidget(sc)
        right = QtW.QVBoxLayout()
        self.out = QtW.QTextBrowser()
        right.addWidget(self.out)
        row = QtW.QHBoxLayout()
        for text, fn in (("计算", self.calc), ("在文档里建外壳", self.build), ("关闭", self.accept)):
            b = QtW.QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        right.addLayout(row)
        lay.addLayout(right, 1)
        self.calc()

    def values(self):
        q = dict(self.q)
        for k, wdg in self.w.items():
            q[k] = wdg.currentData() if isinstance(wdg, QtW.QComboBox) else wdg.value()
        return q

    def calc(self):
        R = F.ebox_analyze(self.obj, self.values())
        drv = "".join("<tr><td>{}</td><td>{:.2f} A</td><td>{:.2f} A</td><td>{:.1f} W</td><td>{:.1f} °C</td></tr>".format(
            d["zh"], d["Irun"], d["Ipk"], d["Pavg"], d["Tjpk"]) for d in R["drives"])
        res = "　".join("{} <b>{}</b> {}".format(r["zh"], r["value"], r["unit"].replace("年 / years", "年")) for r in R["results"])
        chk = "".join("<tr><td style='color:{}'><b>{}</b></td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            COLOR[c["state"]], WORD[c["state"]], c["name"]["zh"], c["value"]["zh"], c["limit"]["zh"]) for c in R["checks"])
        v = R["variants"]
        var = "".join("<tr>{}</tr>".format("".join("<td>{}</td>".format(x) for i, x in enumerate(r) if i != 1)) for r in v["rows"])
        self.out.setHtml(
            "<p>教材第 18 章：电流取这台设计（主轴转矩 ÷ K<sub>t</sub>），判据是教材的示意值。外壳尺寸、翅片、风扇只在“箱内空气到车间的热阻”"
            "选“按外壳尺寸算”时起作用；网页版“CAE 分析 → 电控箱”能用数字工厂的流体 + 温度场复核。</p>"
            "<table border='1' cellspacing='0' cellpadding='3'><tr><th>驱动</th><th>运行电流</th><th>峰值电流</th><th>平均损耗</th><th>结温峰值</th></tr>{}</table>"
            "<p>{}</p><table border='1' cellspacing='0' cellpadding='3'><tr><th>结论</th><th>校核项</th><th>数值</th><th>判据</th></tr>{}</table>"
            "<p><b>{}</b></p><table border='1' cellspacing='0' cellpadding='3'><tr>{}</tr>{}</table>".format(
                drv, res, chk, v["zh"], "".join("<th>{}</th>".format(h[0]) for i, h in enumerate(v["cols"]) if i != 1), var))

    def build(self):
        f = F.add_ebox(self.obj, self.values())
        try:
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(f)
            Gui.activeDocument().activeView().fitAll()
        except Exception:  # noqa: BLE001
            pass
        self.out.append("<p>已在文档里建好“{}”，可以用“文件 → 导出”存成 STEP。</p>".format(f.Label))


def ebox_dialog():
    obj = design()
    if obj:
        d = EboxDialog(obj)
        d.exec_() if hasattr(d, "exec_") else d.exec()


HELP_ONLINE = "https://learn.wenquestrobotics.com/static/help/sewing-freecad/index.html"


# ---------- 第 94 轮：出三维讲解片（交给问渠服务器出，浏览器里看、改、下载）----------
class VideoDialog(QtW.QDialog):
    LANGS = [("中文", "zh"), ("英文", "en"), ("中英两行", "both")]

    def __init__(self, obj):
        super().__init__(Gui.getMainWindow())
        self.obj = obj
        self.vid = None
        self.setWindowTitle("出三维讲解片 · " + obj.Label)
        self.resize(520, 300)
        lay = QtW.QVBoxLayout(self)
        intro = QtW.QLabel("把这台设计发给问渠服务器，自动写好讲解片：整机、各机构，再把红黄灯慢放到出问题的地方。"
                           "出好后在浏览器里打开这段视频：看关键画面、提意见修改、出小样和高清、下载 MP4。"
                           "<br>要联网和钥匙；浏览器里要用同一个账号登录。")
        intro.setWordWrap(True)
        lay.addWidget(intro)
        row = QtW.QHBoxLayout()
        row.addWidget(QtW.QLabel("字幕语言"))
        self.lang = QtW.QComboBox()
        for zh, _ in self.LANGS:
            self.lang.addItem(zh)
        row.addWidget(self.lang)
        row.addStretch(1)
        lay.addLayout(row)
        self.voice = QtW.QCheckBox("配旁白（念画面上的标题和字幕；要几分钟，旁白长的段放慢拉长）")
        self.voice.setChecked(True)
        lay.addWidget(self.voice)
        self.out = QtW.QLabel("")
        self.out.setWordWrap(True)
        self.out.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        lay.addWidget(self.out)
        bt = QtW.QHBoxLayout()
        self.go = QtW.QPushButton("出讲解片")
        self.go.clicked.connect(self.run)
        self.web = QtW.QPushButton("在浏览器里打开")
        self.web.setEnabled(False)
        self.web.clicked.connect(self.open_web)
        kb = QtW.QPushButton("设置钥匙")
        kb.clicked.connect(lambda: key_dialog(self))
        close = QtW.QPushButton("关闭")
        close.clicked.connect(self.accept)
        for b in (self.go, self.web, kb, close):
            bt.addWidget(b)
        lay.addLayout(bt)

    def run(self):
        if not _need_key():
            return
        M = F.SewDesign.machine(self.obj)
        p = self.obj.Proxy.params(self.obj)
        lang = self.LANGS[self.lang.currentIndex()][1]
        self.out.setText("正在发给问渠服务器写场景……")
        self.go.setEnabled(False)
        QtW.QApplication.processEvents()
        try:
            c = N.Client()
            r = c.video(M.MACHINE, p, lang, self.voice.isChecked(), self.obj.Label)
        except N.NetError as e:
            self.out.setText(_html.escape(str(e)))
            return
        finally:
            self.go.setEnabled(True)
        self.vid, self.url = r["id"], c.video_url(r["id"])
        probs = []
        for k in (r.get("problems") or [])[:3]:            # 服务器给的是校核项代号，换成名字
            h = F.hotspot_of(self.obj, k)
            probs.append(((h or {}).get("name") or {}).get("zh", k))
        txt = "写好了：约 {:g} 秒{}。".format(r.get("duration", 0), "，慢放 " + "、".join(probs) if probs else "")
        if self.voice.isChecked():
            txt += ("正在配旁白（要几分钟），配好接着出关键画面。" if r.get("voice") else "这台服务器没装语音服务，这次是无声的片子。")
        txt += "<br>已在浏览器里打开；没打开就点“在浏览器里打开”。网页版“三维视频”里也能找到它。"
        self.out.setText(txt)
        self.web.setEnabled(True)
        self.go.setEnabled(True)
        self.open_web()

    def open_web(self):
        if self.vid:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.url))


def video_dialog():
    obj = design()
    if obj:
        d = VideoDialog(obj)
        d.exec_() if hasattr(d, "exec_") else d.exec()


def open_help():
    """本机的帮助（随安装包，断网也能看）；没有就开在线版"""
    p = os.path.join(HERE, "help", "index.html")
    url = QtCore.QUrl.fromLocalFile(p) if os.path.exists(p) else QtCore.QUrl(HELP_ONLINE)
    QtGui.QDesktopServices.openUrl(url)


def register():
    cmds = [("WQS_New", Cmd("新建平缝机设计", "按默认（教材算例）参数生成平缝机机构零件和校核", new_design, needs=False)),
            ("WQS_NewOverlock", Cmd("新建包缝机设计", "按教材第 9 讲算例机生成包缝机机构零件和校核", lambda: new_design("overlock"), needs=False)),
            ("WQS_NewCover", Cmd("新建绷缝机设计", "绷缝机：弯针定时校核与耗线量、线团计划；引针、弯针、撑线器、送布的三维零件", lambda: new_design("cover"), needs=False)),
            ("WQS_NewPattern", Cmd("新建花样机设计", "电子花样机：离布窗口、转速上限、前瞻调速、X/Y 伺服与同步带校核；三维零件按针走", lambda: new_design("pattern"), needs=False)),
            ("WQS_NewEmbroid", Cmd("新建刺绣机设计", "多头刺绣机：绷架加速度、转速上限、断线补绣与全机效率；三维零件按针走", lambda: new_design("embroid"), needs=False)),
            ("WQS_NewFlatknit", Cmd("新建横机设计", "电脑横机：选针时间与提前量、换向余量、摇床、机头电机、一片用时与改进方案；三维零件按趟走", lambda: new_design("flatknit"), needs=False)),
            ("WQS_Recompute", Cmd("重新计算", "改了参数后重算零件与校核（Ctrl+R 也可以）", recompute)),
            ("WQS_Checks", Cmd("校核结果", "红绿灯列表；双击红黄灯那一行，三维停到出问题的地方（出问题的部件涂红 / 橙）", show_checks)),
            ("WQS_Timing", Cmd("时序图", "针杆、钩线窗口、送布、挑线的时序", show_timing)),
            ("WQS_Spin", Cmd("转动机构", "让主轴转起来看运动（花样机、刺绣机一针针走，横机一趟趟走；再点一次停止）", toggle_spin)),
            ("WQS_Video", Cmd("出三维讲解片", "发给问渠服务器自动出讲解片（可配旁白），在浏览器里看、改、下载（要联网和钥匙）", video_dialog)),
            ("WQS_Step", Cmd("导出 STEP", "整套机构零件导出 STEP", export_step)),
            ("WQS_Ebox", Cmd("电控箱", "这台机配的电控箱：结温、电容寿命、开关时间窗口、改进方案；在文档里建参数化外壳（第 18 章）", ebox_dialog)),
            ("WQS_Import", Cmd("导入参数", "读入问渠网页版导出的参数文件（.wqsew.json）", import_params)),
            ("WQS_Export", Cmd("导出参数", "存成参数文件，可在问渠网页版打开", export_params)),
            ("WQS_Submit", Cmd("提交到问渠工厂", "用“问渠”工作台把整套零件提交到数字工厂审批", submit)),
            ("WQS_Ai", Cmd("AI 助手", "一句话改设计、解释红黄灯、写设计说明（要联网和钥匙；判定由计算核心做，点“采用”才改）", ai_dialog)),
            ("WQS_Parts", Cmd("插入本单位零件", "从本单位零件库查找零件，插入三维或把参数用到当前设计（要联网和钥匙）", insert_part, needs=False)),
            ("WQS_Help", Cmd("帮助", "打开帮助：怎么用、内核、零件库、AI、CAE 快速上手（断网也能看）", open_help, needs=False))]
    for name, c in cmds:
        Gui.addCommand(name, c)
    return [n for n, _ in cmds]
