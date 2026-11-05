# -*- coding: utf-8 -*-
"""问渠轴承 · FreeCAD 里的参数表单（第 64 轮第 6 步，细则第十四节 F2）。

表单按 bearingkit/fields.py 生成：与网页版同一套字段、同一种项目文件（.wqbearing.json）、同样的“什么时候显示”，
文字取自网页版的中英文表（labels.json）。可以从头设计，也可以打开网页版存的文件；存回去网页版也能打开。
右边是校核结果（与网页版同一个内核）；下面的按钮建模、出图、出工序简图。
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:  # FreeCAD's PySide shim
    from PySide import QtCore, QtWidgets
except ImportError:  # plain Python with PySide6 (tests)
    from PySide6 import QtCore, QtWidgets

from bearingkit import fields as FL  # noqa: E402

# the columns of the load-spectrum table, per scenario (Scenario.vue)
CASE_COLS = {
    "gearbox": [("label", "caseName"), ("P", None), ("n", None), ("share", "share")],
    "spindle": [("label", "caseName"), ("Fr", None), ("Fa", None), ("n", None), ("share", "share")],
}
CASE_HEAD = {"P": "P kW", "Fr": "Fr N", "Fa": "Fa N", "n": "n r/min"}
REBUILD = ("type", "scenario.kind", "pair.arrangement", "profile.kind", "scenario.axis")
STATUS = {"pass": "合格", "fail": "不合格", "unknown": "未知", "na": "不适用", "info": "计算值"}


def _num(text, integer=False):
    text = (text or "").strip().replace("，", ".")
    if not text:
        return None
    v = float(text)
    return int(round(v)) if integer else v


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer() and abs(v) < 1e15:
        return str(int(v))
    return repr(v) if isinstance(v, float) else str(v)


def _case_label(c):
    lab = c.get("label")
    return (lab.get("zh") or lab.get("en") or "") if isinstance(lab, dict) else (lab or "")


ONLINE_HELP = "https://wenquestrobotics.com/bearing/help/freecad/"


def help_url() -> str:
    """The offline help that comes with the workbench (bearing-help/), or the online copy."""
    from pathlib import Path

    local = Path(__file__).resolve().parent / "bearing-help" / "index.html"
    return local.as_uri() if local.is_file() else ONLINE_HELP


class Form(QtWidgets.QWidget):
    """参数表单 + 校核结果。self.project 始终是网页版同样格式的项目。"""

    changed = QtCore.Signal()

    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = FL.normalise(project or FL.blank())
        self.path = None
        self.widgets = {}
        self.setWindowTitle("问渠轴承")
        outer = QtWidgets.QVBoxLayout(self)
        bar = QtWidgets.QHBoxLayout()
        self.buttons = {}
        for key, text in (
            ("new", "新建"),
            ("open", "打开项目"),
            ("catalog", "产品库"),
            ("save", "保存项目"),
            ("calc", "计算"),
            ("model", "建模"),
            ("draw", "出图与 STEP"),
            ("sketch", "工序简图"),
            ("help", "帮助"),
        ):
            b = QtWidgets.QPushButton(text)
            bar.addWidget(b)
            self.buttons[key] = b
        bar.addStretch(1)
        outer.addLayout(bar)
        self.title = QtWidgets.QLineEdit()
        self.title.setPlaceholderText(FL.label("untitled"))
        self.title.editingFinished.connect(self._title_changed)
        outer.addWidget(self.title)
        split = QtWidgets.QSplitter()
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        split.addWidget(self.scroll)
        right = QtWidgets.QWidget()
        rl = QtWidgets.QVBoxLayout(right)
        self.verdict = QtWidgets.QLabel("")
        rl.addWidget(self.verdict)
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["校核", "结论", "数值", "限值"])
        self.table.horizontalHeader().setStretchLastSection(True)
        rl.addWidget(self.table)
        self.note = QtWidgets.QLabel("")
        self.note.setWordWrap(True)
        rl.addWidget(self.note)
        split.addWidget(right)
        outer.addWidget(split, 1)
        self.buttons["new"].clicked.connect(self.new)
        self.buttons["open"].clicked.connect(self.open_dialog)
        self.buttons["catalog"].clicked.connect(self.catalog_dialog)
        self.buttons["save"].clicked.connect(self.save_dialog)
        self.buttons["calc"].clicked.connect(self.calculate)
        self.buttons["model"].clicked.connect(self.model)
        self.buttons["draw"].clicked.connect(self.draw)
        self.buttons["sketch"].clicked.connect(self.sketch)
        self.buttons["help"].clicked.connect(self.help)
        self.rebuild()

    # ------------------------------------------------------------------ the form
    def help(self):
        """The FreeCAD help (round 90): the offline copy beside this module, else the online one."""
        import webbrowser

        webbrowser.open(help_url())

    def rebuild(self):
        self.title.setText(FL.normalise(self.project)["title"].get("zh") or "")
        box = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(box)
        self.widgets = {}
        for gkey, flds in FL.visible(self.project):
            if gkey == "type":
                grp = QtWidgets.QGroupBox(FL.label("type"))
            else:
                grp = QtWidgets.QGroupBox(FL.label(gkey))
            form = QtWidgets.QFormLayout(grp)
            if gkey == "gLimits":
                hint = QtWidgets.QLabel(FL.label("limitsHint"))
                hint.setWordWrap(True)
                form.addRow(hint)
            if gkey == "gScene":
                hint = QtWidgets.QLabel(
                    FL.label("skHint_" + ((self.project.get("scenario") or {}).get("kind") or "generic"))
                )
                hint.setWordWrap(True)
            for f in flds:
                w = self._widget(f)
                lab = FL.label(f["key"]) + (" ({})".format(f["unit"]) if f["unit"] else "")
                if f["hint"]:
                    w.setToolTip(FL.label(f["hint"]))
                form.addRow(lab, w)
                if gkey == "gScene" and f["path"] == "scenario.kind":
                    form.addRow(hint)
            lay.addWidget(grp)
        lay.addStretch(1)
        self.scroll.setWidget(box)

    def _widget(self, f):
        path, kind = f["path"], f["kind"]
        val = FL.get(self.project, path)
        if kind == "select":
            w = QtWidgets.QComboBox()
            for v, key in f["options"]:
                w.addItem(FL.label(key) if key else v, v)
            i = w.findData(val if val is not None else f["options"][0][0])
            w.setCurrentIndex(max(i, 0))
            w.currentIndexChanged.connect(lambda _i, w=w, f=f: self.set(f["path"], w.currentData()))
        elif kind in ("text", "points"):
            w = QtWidgets.QPlainTextEdit(FL.points_text(val) if kind == "points" else (val or ""))
            w.setMinimumHeight(90)
            w.textChanged.connect(
                lambda w=w, f=f: self.set(
                    f["path"],
                    FL.parse_points(w.toPlainText()) if f["kind"] == "points" else w.toPlainText(),
                    rebuild=False,
                )
            )
        elif kind == "cases":
            w = self._cases()
        else:
            w = QtWidgets.QLineEdit(_fmt(val))
            w.editingFinished.connect(lambda w=w, f=f: self._edited(w, f))
        self.widgets[(path, f["key"])] = w
        return w

    def _cases(self):
        s = self.project["scenario"]
        cols = CASE_COLS[s["kind"]]
        box = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        t = QtWidgets.QTableWidget(len(s.get("cases") or []), len(cols))
        t.setHorizontalHeaderLabels([FL.label(k) if k else CASE_HEAD[c] for c, k in cols])
        for i, c in enumerate(s.get("cases") or []):
            for j, (col, _k) in enumerate(cols):
                t.setItem(i, j, QtWidgets.QTableWidgetItem(_case_label(c) if col == "label" else _fmt(c.get(col))))
        t.itemChanged.connect(lambda item: self._case_edited(item, cols))
        lay.addWidget(t)
        row = QtWidgets.QHBoxLayout()
        add = QtWidgets.QPushButton(FL.label("addCase"))
        rem = QtWidgets.QPushButton(FL.label("removeCase"))
        add.clicked.connect(self._add_case)
        rem.clicked.connect(lambda: self._remove_case(t.currentRow()))
        row.addWidget(add)
        row.addWidget(rem)
        lay.addLayout(row)
        self.cases_table = t
        return box

    def _case_edited(self, item, cols):
        c = self.project["scenario"]["cases"][item.row()]
        col = cols[item.column()][0]
        if col == "label":
            c["label"] = item.text()
        else:
            try:
                c[col] = _num(item.text())
            except ValueError:
                item.setText(_fmt(c.get(col)))
                return
        self.changed.emit()

    def _add_case(self):
        s = self.project["scenario"]
        s["cases"].append(
            {"label": "", "P": None, "n": None, "share": None}
            if s["kind"] == "gearbox"
            else {"label": "", "Fr": None, "Fa": None, "n": None, "share": None}
        )
        self.rebuild()

    def _remove_case(self, i):
        s = self.project["scenario"]
        if len(s["cases"]) > 1 and 0 <= i < len(s["cases"]):
            s["cases"].pop(i)
            self.rebuild()

    def _edited(self, w, f):
        try:
            v = _num(w.text(), f["kind"] == "int")
        except ValueError:
            w.setText(_fmt(FL.get(self.project, f["path"])))
            return
        self.set(f["path"], v, rebuild=False)

    def _title_changed(self):
        self.project["title"] = {**(self.project.get("title") or {}), "zh": self.title.text()}
        self.changed.emit()

    def set(self, path, value, rebuild=None):
        """改一个字段（与网页版同样：换应用场景时换成该场景的空白结构）。"""
        if path == "scenario.kind":
            FL.set_scene(self.project, value)
        else:
            FL.put(self.project, path, value)
        if rebuild if rebuild is not None else path in REBUILD:
            QtCore.QTimer.singleShot(0, self.rebuild)
        self.changed.emit()

    # ------------------------------------------------------------------ files
    def new(self):
        self.project, self.path = FL.blank(), None
        self.rebuild()
        self.table.setRowCount(0)
        self.verdict.setText("")

    def open_file(self, path):
        self.project, self.path = FL.load(path), path
        self.rebuild()
        self.calculate()

    def save_file(self, path):
        FL.save(self.project, path)
        self.path = path

    def open_dialog(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "打开问渠轴承项目", os.path.expanduser("~"), "问渠轴承项目 (*.wqbearing.json *.json)"
        )
        if path:
            self.open_file(path)

    def save_dialog(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存问渠轴承项目", self.path or os.path.expanduser("~"), "问渠轴承项目 (*.wqbearing.json)"
        )
        if path:
            if not path.endswith(".json"):
                path += ".wqbearing.json"
            self.save_file(path)

    def use_catalog(self, cat, row):
        """设成产品库里的一个型号（与网页版“产品库”相同：外形尺寸填好，内部尺寸清空待填，应用场景和载荷保留）。"""
        self.project, self.path = FL.from_catalog(self.project, cat, row), None
        self.rebuild()
        self.calculate()

    def catalog_dialog(self):
        """本厂产品库：网页版“产品库”里“下载给 FreeCAD 用”的文件（.wqcatalog.json）。"""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "打开产品库文件", os.path.expanduser("~"), "问渠轴承产品库 (*.wqcatalog.json)"
        )
        if not path:
            return
        with open(path, encoding="utf-8") as f:
            cat = json.load(f)
        rows = FL.catalog_rows(cat)
        if not rows:
            QtWidgets.QMessageBox.information(self, "产品库", "这个文件里没有能计算的型号。")
            return
        names = [f"{FL.catalog_name(r)}   d {r.get('d')}  D {r.get('D')}  T {r.get('T') or r.get('B')}" for r in rows]
        item, ok = QtWidgets.QInputDialog.getItem(
            self, "产品库", "选型号（外形尺寸填好，内部尺寸请自己填）", names, 0, False
        )
        if ok and item:
            self.use_catalog(cat, rows[names.index(item)])

    # ------------------------------------------------------------------ actions
    def calculate(self):
        import wq_bearing

        try:
            res = wq_bearing.analyse(copy.deepcopy(self.project))
        except (ValueError, TypeError) as e:
            self.verdict.setText("算不出来：{}".format(e))
            self.table.setRowCount(0)
            self.note.setText(FL.catalog_note(self.project))
            return None
        self.verdict.setText("总结论：" + STATUS.get(res.get("status"), res.get("status")))
        checks = res.get("checks") or []
        self.table.setRowCount(len(checks))
        for i, c in enumerate(checks):
            v, lim = c.get("value"), c.get("limit")
            unit = c.get("unit") or ""
            vals = [
                c.get("zh"),
                STATUS.get(c.get("status"), c.get("status")),
                "" if v is None else ("{:.4g} {}".format(v, unit) if isinstance(v, (int, float)) else str(v)),
                ""
                if lim is None or c.get("status") == "info"
                else "{:.4g}".format(lim)
                if isinstance(lim, (int, float))
                else str(lim),
            ]
            for j, x in enumerate(vals):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(x).strip()))
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, min(self.table.columnWidth(0), 220))
        self.note.setText(
            "\n".join(
                x
                for x in (
                    FL.catalog_note(self.project),
                    "计算由确定性程序完成，未经 AI；许用值由用户填写，缺数据判为“未知”。",
                )
                if x
            )
        )
        return res

    def model(self):
        import FreeCAD
        import FreeCADGui
        import wq_bearing

        doc = FreeCAD.newDocument("WenQuestBearing")
        try:
            self.objs, notes, _ = wq_bearing.build(doc, copy.deepcopy(self.project))
        except (ValueError, TypeError) as e:
            QtWidgets.QMessageBox.warning(self, "问渠轴承", "建不了模：{}".format(e))
            return
        FreeCADGui.SendMsgToActiveView("ViewFit")
        self.note.setText("\n".join(notes))

    def draw(self):
        import wq_bearing

        if not getattr(self, "objs", None):
            self.model()
        out = QtWidgets.QFileDialog.getExistingDirectory(self, "导出到哪个文件夹", os.path.expanduser("~"))
        if out:
            files = wq_bearing.export(self.objs, self.project, out)
            QtWidgets.QMessageBox.information(self, "问渠轴承", "已导出 {} 个文件到\n{}".format(len(files), out))

    def sketch(self):
        import wq_bearing
        from bearingkit.analyze import geometry_of

        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "打开网页版存的工艺模板", os.path.expanduser("~"), "问渠轴承工艺模板 (*.wqprocess.json *.json)"
        )
        if not path:
            return
        out = QtWidgets.QFileDialog.getExistingDirectory(self, "工序简图存到哪个文件夹", os.path.dirname(path))
        if not out:
            return
        with open(path, encoding="utf-8") as f:
            process = json.load(f)
        files = wq_bearing.process_sheets(geometry_of(self.project), self.project, process, out)
        QtWidgets.QMessageBox.information(
            self, "问渠轴承", "已出 {} 张工序简图到\n{}".format(len([f for f in files if f.endswith(".svg")]), out)
        )


_panel = []


def show():
    """在 FreeCAD 里打开表单（停靠在右边）。"""
    import FreeCADGui

    mw = FreeCADGui.getMainWindow()
    dock = QtWidgets.QDockWidget("问渠轴承", mw)
    form = Form()
    dock.setWidget(form)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    _panel[:] = [dock, form]
    return form
