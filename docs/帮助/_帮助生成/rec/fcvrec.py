# -*- coding: utf-8 -*-
"""带配音的 FreeCAD 录屏驱动（第 90 轮，从第 49 轮缝纫机的 drive.py 改来）：在 FreeCAD 图形界面里按脚本一步步操作，
每句 say 等配音读完（时长来自 lines.py 写的 durations.json），记下字幕时间和要剪掉的等待段，写 <名字>.json 给 vfinish.py。

由 fcrec.sh 启动：freecad fcvrec.py；环境变量 WQ_SCRIPT（脚本 .py，里面 CLIPS = {名字: 函数}）、WQ_CLIP、WQ_VOICE、WQ_OUT、WQ_T0。
脚本里的步骤：say("…")、do(函数, 之后等的毫秒)、wait(毫秒)、cut(True/False)、until(条件函数, 最长秒数)。
"""
import json
import os
import sys
import time

import FreeCAD as App  # noqa: F401  (scripts use it)
import FreeCADGui as Gui
from PySide import QtCore, QtGui

try:
    from PySide import QtWidgets as QtW
except ImportError:
    QtW = QtGui
try:
    from PySide6 import QtTest
except ImportError:
    from PySide2 import QtTest

DUR = json.load(open(os.path.join(os.environ["WQ_VOICE"], "durations.json"), encoding="utf-8"))
T0 = float(os.environ["WQ_T0"])
mw = Gui.getMainWindow()
CUES, CUTS, STATE = [], [], {}


def now():
    return time.time() - T0


def say(text):
    return ("say", text)


def do(fn, ms=600):
    return ("do", fn, ms)


def wait(ms):
    return ("wait", ms)


def cut(on):
    return ("cut", on)


def until(pred, sec=180):
    return ("until", pred, sec)


# ---- helpers the scripts use
def action(text):
    for a in mw.findChildren(getattr(QtGui, "QAction", None) or QtW.QAction):   # Qt6: QAction 在 QtGui 里
        if a.text().replace("&", "") == text:
            a.trigger()
            return True
    raise RuntimeError("no action " + text)


def console():
    for n in ("Python console",):
        d = mw.findChild(QtW.QDockWidget, n)
        if d:
            d.show()
            d.raise_()
    return mw.findChild(QtW.QPlainTextEdit, "Python console")


def report():
    d = mw.findChild(QtW.QDockWidget, "Report view")
    if d:
        d.show()
        d.raise_()


def hide_dock(name):
    d = mw.findChild(QtW.QDockWidget, name)
    if d:
        d.hide()


def dock_width(title, w):
    """按标题找停靠面板，设宽度（右边的软件表单、左边的模型树）。"""
    for d in mw.findChildren(QtW.QDockWidget):
        if d.windowTitle() == title or d.objectName() == title:
            mw.resizeDocks([d], [w], QtCore.Qt.Horizontal)
            return


def typecmd(cmd):
    """一个字一个字写进控制台（虚拟显示器的键盘布局会打错符号，不用模拟按键），再回车"""
    c = console()
    c.setFocus()
    for ch in cmd:
        c.insertPlainText(ch)
        QtW.QApplication.processEvents()
        time.sleep(0.04)
    QtTest.QTest.keyClick(c, QtCore.Qt.Key_Return)


def fit(iso=True):
    try:
        v = Gui.activeDocument().activeView()
        if iso:
            v.viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass


def close_dialogs():
    for w in QtW.QApplication.topLevelWidgets():
        if isinstance(w, QtW.QDialog) and w.isVisible():
            w.reject() if hasattr(w, "reject") else w.close()


def wb_popup():
    for cb in mw.findChildren(QtW.QComboBox):
        if cb.count() > 5 and any("Part" in cb.itemText(i) for i in range(cb.count())):
            STATE["cb"] = cb
            cb.showPopup()
            return


def wb_close():
    cb = STATE.get("cb")
    if cb:
        cb.hidePopup()


def finish():
    out = os.environ["WQ_OUT"]
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"cues": CUES, "cuts": CUTS, "end": now()}, f, ensure_ascii=False, indent=1)
    QtCore.QTimer.singleShot(300, lambda: os._exit(0))


def run():
    mw.setGeometry(0, 0, 1280, 720)
    mw.showMaximized()
    for b in mw.findChildren(QtW.QPushButton):          # 第一次启动的欢迎页
        if b.text() in ("Done", "完成") and b.isVisible():
            b.click()
    g = dict(globals())
    exec(open(os.environ["WQ_SCRIPT"], encoding="utf-8").read(), g)
    steps = g["CLIPS"][os.environ["WQ_CLIP"]]()
    cut_start = []

    def nxt(i):
        if i >= len(steps):
            QtCore.QTimer.singleShot(1500, finish)
            return
        s = steps[i]
        kind = s[0]
        if kind == "say":
            d = DUR.get(s[1])
            if not d:
                print("NO VOICE", s[1], file=sys.stderr)
                os._exit(2)
            CUES.append({"t": now(), "text": s[1], "dur": d["sec"], "wav": d["wav"]})
            QtCore.QTimer.singleShot(int(d["sec"] * 1000 + 350), lambda: nxt(i + 1))
        elif kind == "wait":
            QtCore.QTimer.singleShot(s[1], lambda: nxt(i + 1))
        elif kind == "cut":
            if s[1]:
                cut_start[:] = [now()]
            elif cut_start:
                CUTS.append([cut_start[0], now()])
                cut_start[:] = []
            QtCore.QTimer.singleShot(0, lambda: nxt(i + 1))
        elif kind == "until":
            t1 = time.time()

            def poll():
                try:
                    ok = s[1]()
                except Exception:
                    ok = False
                if ok or time.time() - t1 > s[2]:
                    QtCore.QTimer.singleShot(800, lambda: nxt(i + 1))
                else:
                    QtCore.QTimer.singleShot(400, poll)
            poll()
        elif kind == "do":
            QtCore.QTimer.singleShot(s[2], lambda: nxt(i + 1))   # 先排好下一步：这一步可能打开模态对话框
            try:
                s[1]()
            except Exception as e:
                import traceback
                print("STEP ERROR", i, e, traceback.format_exc(), file=sys.stderr)
    nxt(0)


QtCore.QTimer.singleShot(4000, run)
