"""问渠 CAD 录屏导演（真操作）：剧本是一个生成器，每步 yield 要等的毫秒数。

鼠标是真的：系统光标平滑移动（录像里看得见），同时把鼠标事件真发给鼠标下面的控件（三维视图、按钮、模型树……），
FreeCAD 当真执行——画草图、点按钮、拖动视图都是软件自己做的，不是用 Python 直接改模型。
点击处记到 clicks.txt（rings.py 事后叠黄圈）；字幕记到 subs.txt（时间 文字），make_vtt 转成字幕。
"""
import os
import time
import traceback

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui

try:
    from PySide import QtWidgets
except ImportError:  # pragma: no cover
    QtWidgets = QtGui
from PySide6.QtTest import QTest

REC = os.environ.get("WQ_REC", ".")
LANG = os.environ.get("WQ_LANG", "zh")        # zh：中文界面、中文字幕；en：英文界面、英文字幕（译文在 subs_en.json）
EN = LANG == "en"
_SUBS_EN = None


def L(zh, en):
    """按录屏语言取界面上的文字（找按钮、菜单、标签用）"""
    return en if EN else zh


def model_dir():
    """整机、针夹草图等文件：中文版在 model/，英文版在 model_en/（部件组名、文件名是英文）"""
    return os.path.join(REC, "model_en" if EN else "model")


def model_file(zh_name, en_name):
    return os.path.join(model_dir(), en_name if EN else zh_name)


def subtitle(text):
    global _SUBS_EN
    if not EN:
        return text
    if _SUBS_EN is None:
        import json
        _SUBS_EN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "subs_en.json"), encoding="utf-8"))
    if text not in _SUBS_EN:
        raise KeyError("subs_en.json 缺译文：" + text)
    return _SUBS_EN[text]
_LOG = open(os.path.join(REC, "director.log"), "w")


def log(*a):
    _LOG.write(" ".join(map(str, a)) + "\n")
    _LOG.flush()


Qt = QtCore.Qt


class Director:
    def __init__(self):
        self.mw = Gui.getMainWindow()
        self.pos = QtCore.QPoint(800, 450)
        QtGui.QCursor.setPos(self.pos)
        for f in ("clicks.txt", "subs.txt"):
            p = os.path.join(REC, f)
            if os.path.exists(p):
                os.remove(p)

    # ------------------------------------------------------------ 找控件、算位置
    def vp(self):
        ws = [w for w in self.mw.findChildren(QtWidgets.QWidget) if "GL" in w.metaObject().className() and w.isVisible()]
        return max(ws, key=lambda w: w.width() * w.height())

    def model_pt(self, x, y, z=0.0):
        """模型坐标 → 屏幕坐标（全局）"""
        v = Gui.ActiveDocument.ActiveView
        w = self.vp()
        px, py = v.getPointOnViewport(App.Vector(x, y, z))
        return w.mapToGlobal(QtCore.QPoint(int(round(px)), int(round(w.height() - py))))

    def center(self, w, rect=None):
        return w.mapToGlobal((rect if rect is not None else w.rect()).center())

    def action_widget(self, cmd):
        for tb in self.mw.findChildren(QtWidgets.QToolBar):
            if not tb.isVisible():
                continue
            for a in tb.actions():
                if a.objectName() == cmd or a.data() == cmd:
                    w = tb.widgetForAction(a)
                    if w and w.isVisible():
                        return w
        return None

    def tool(self, button, cmd=None, ms=800):
        """移到工具栏按钮 button，点它：普通按钮真点；下拉组按钮（Comp…）圈出按钮、运行组里的命令 cmd（和点按钮一样）"""
        w = self.action_widget(button)
        if w is None:                         # 按钮名对不上：找下拉组里含这个命令的那个按钮
            want = cmd or button
            w = self.action_widget(want)
            if w is not None:
                cmd = None                    # 命令自己就是一个按钮：直接点
            for tb in ([] if w is not None else  self.mw.findChildren(QtWidgets.QToolBar)):
                if not tb.isVisible():
                    continue
                for a in tb.actions():
                    m = a.menu()
                    if m and any(x.objectName() == want or x.data() == want for x in m.actions()):
                        w, cmd = tb.widgetForAction(a), want
                        break
                if w is not None:
                    break
            log("tool fallback", button, cmd, w is not None)
        p = self.center(w)
        t = self.move(p, ms)

        def go():
            if cmd:
                self.ring(p)
                Gui.runCommand(cmd)
            else:
                self.click(p)
        QtCore.QTimer.singleShot(t, go)
        return t + 500

    def wb_combo(self):
        for c in self.mw.findChildren(QtWidgets.QComboBox):
            if c.isVisible() and c.count() > 10 and c.mapTo(self.mw, QtCore.QPoint(0, 0)).y() < 80:
                return c

    def tree(self):
        for t in self.mw.findChildren(QtWidgets.QTreeWidget):
            if t.isVisible() and t.topLevelItemCount() and t.mapTo(self.mw, QtCore.QPoint(0, 0)).x() < 300:
                return t

    def tree_item(self, label):
        t = self.tree()
        it = t.findItems(label, Qt.MatchExactly | Qt.MatchRecursive)[0]
        pars = []
        par = it.parent()
        while par is not None:                # 收着的父项先展开（比如凸台下面的草图），不然取到的位置是空的
            pars.append(par)
            par = par.parent()
        if any(not x.isExpanded() for x in pars):
            for x in reversed(pars):
                x.setExpanded(True)
            QtWidgets.QApplication.processEvents()
            it = t.findItems(label, Qt.MatchExactly | Qt.MatchRecursive)[0]   # 展开会重建子项：重新找
        t.scrollToItem(it)
        return t.viewport().mapToGlobal(t.visualItemRect(it).center())

    def find(self, cls, text, exact=True):
        for w in QtWidgets.QApplication.allWidgets():
            if isinstance(w, cls) and w.isVisible():
                t = w.text() if hasattr(w, "text") else ""
                t = t.replace("&", "")
                if (t == text) if exact else (text in t):
                    return w
        return None

    def tab(self, text):
        for tb in QtWidgets.QApplication.allWidgets():
            if isinstance(tb, QtWidgets.QTabBar) and tb.isVisible():
                for i in range(tb.count()):
                    if tb.tabText(i).replace("&", "") == text:
                        return tb, i
        return None, None

    # ------------------------------------------------------------ 真鼠标、真键盘
    def _send(self, kind, gpt, button=Qt.NoButton, buttons=Qt.NoButton, mods=Qt.NoModifier):
        w = QtWidgets.QApplication.widgetAt(gpt)
        if w is None:
            return None
        lp = w.mapFromGlobal(gpt)
        ev = QtGui.QMouseEvent(kind, QtCore.QPointF(lp), QtCore.QPointF(gpt), button, buttons, mods)
        QtWidgets.QApplication.sendEvent(w, ev)
        return w

    def move(self, gpt, ms=700, buttons=Qt.NoButton, mods=Qt.NoModifier):
        """平滑移到 gpt；一路发鼠标移动事件（三维视图、草图预览跟着动）。返回用时。"""
        a, b = QtCore.QPoint(self.pos), QtCore.QPoint(gpt)
        self.pos = QtCore.QPoint(gpt)
        n = max(1, int(ms / 25))
        k = [0]
        t = QtCore.QTimer(self.mw)
        if getattr(self, "_mt", None):
            self._mt.stop()
        self._mt = t

        def step():
            k[0] += 1
            s = k[0] / n
            e = s * s * (3 - 2 * s)
            p = QtCore.QPoint(int(a.x() + (b.x() - a.x()) * e), int(a.y() + (b.y() - a.y()) * e))
            QtGui.QCursor.setPos(p)
            self._send(QtCore.QEvent.MouseMove, p, Qt.NoButton, buttons, mods)
            if k[0] >= n:
                t.stop()
        t.timeout.connect(step)
        t.start(25)
        return ms + 60

    def ring(self, gpt):
        with open(os.path.join(REC, "clicks.txt"), "a") as f:
            f.write(f"{time.time():.3f} {gpt.x()} {gpt.y()}\n")

    def click(self, gpt=None, button=Qt.LeftButton, mods=Qt.NoModifier, ring=True, double=False):
        gpt = gpt or self.pos
        if getattr(self, "_mt", None):      # 还在移动（画面忙时定时器会慢）：直接到位再点
            self._mt.stop()
        QtGui.QCursor.setPos(gpt)
        self._send(QtCore.QEvent.MouseMove, gpt)
        if ring:
            self.ring(gpt)
        self._send(QtCore.QEvent.MouseButtonPress, gpt, button, button, mods)
        self._send(QtCore.QEvent.MouseButtonRelease, gpt, button, Qt.NoButton, mods)
        if double:
            self._send(QtCore.QEvent.MouseButtonDblClick, gpt, button, button, mods)
            self._send(QtCore.QEvent.MouseButtonRelease, gpt, button, Qt.NoButton, mods)

    def press(self, button=Qt.LeftButton, mods=Qt.NoModifier):
        self._send(QtCore.QEvent.MouseButtonPress, self.pos, button, button, mods)

    def release(self, button=Qt.LeftButton, mods=Qt.NoModifier):
        self._send(QtCore.QEvent.MouseButtonRelease, self.pos, button, Qt.NoButton, mods)

    def wheel(self, steps, gpt=None):
        gpt = gpt or self.pos
        w = self.vp()
        if w.rect().contains(w.mapFromGlobal(gpt)):
            w = w.parentWidget()          # 三维视图的滚轮由外层 View3DInventorViewer 处理
        else:
            w = QtWidgets.QApplication.widgetAt(gpt)
        lp = w.mapFromGlobal(gpt)
        ev = QtGui.QWheelEvent(QtCore.QPointF(lp), QtCore.QPointF(gpt), QtCore.QPoint(0, 0), QtCore.QPoint(0, 120 * steps),
                               Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
        QtWidgets.QApplication.sendEvent(w, ev)

    def keys(self, text, enter=False, w=None):
        w = w or QtWidgets.QApplication.focusWidget() or self.vp()
        if text.isascii():
            QTest.keyClicks(w, text, Qt.NoModifier, 60)
        else:      # QTest 只认 ASCII（中文会让 Qt 断言退出）：中文字符用带文字的按键事件发
            for ch in text:
                for kind in (QtCore.QEvent.KeyPress, QtCore.QEvent.KeyRelease):
                    QtWidgets.QApplication.sendEvent(w, QtGui.QKeyEvent(kind, 0, Qt.NoModifier, ch))
        if enter:
            QTest.keyClick(w, Qt.Key_Return)

    def key(self, k, w=None, mods=Qt.NoModifier):
        w = w or QtWidgets.QApplication.focusWidget() or self.vp()
        QTest.keyClick(w, k, mods)

    def until(self, cond, timeout=15000, step=100):
        """yield from d.until(...)：等到 cond() 为真（最多 timeout 毫秒）"""
        t = 0
        while t < timeout:
            try:
                if cond():
                    return
            except Exception:
                pass
            yield step
            t += step
        log("until timeout", cond)

    def zoom_to(self, mm, px, at=None):
        """滚轮真缩放，直到 mm 毫米在屏幕上约 px 像素（草图里用）"""
        for _ in range(40):
            a, b = self.model_pt(0, 0), self.model_pt(mm, 0)
            cur = abs(b.x() - a.x())
            if 0.85 * px <= cur <= 1.18 * px:
                return
            self.wheel(1 if cur < px else -1, at or self.center(self.vp()))
            yield 120
        log("zoom gave up")

    # ------------------------------------------------------------ 字幕
    def say(self, text):
        """出字幕。用法 yield d.say("…")：上一条还没显示够读完的时间，就先等一等再出这一条（中文按每秒 4.5 字，至少 2.5 秒）。"""
        text = subtitle(text)
        now = time.time()
        wait = max(0.0, getattr(self, "_say_until", 0.0) - now)
        self._say_until = now + wait + max(2.5, len(text) / (15.0 if EN else 4.5))
        self._say_text = text

        def put():
            with open(os.path.join(REC, "subs.txt"), "a", encoding="utf-8") as f:
                f.write(f"{time.time():.3f}\t{text}\n")
        if wait > 0:
            QtCore.QTimer.singleShot(int(wait * 1000) - 30, put)
        else:
            put()
        return int(wait * 1000)

    def read_out(self):
        """剧本结尾：yield d.read_out()，等最后一条字幕显示够"""
        return int(max(0.0, getattr(self, "_say_until", 0.0) - time.time()) * 1000) + 300

    # ------------------------------------------------------------ 运行剧本
    def run(self, gen, end_flag=True):
        def nxt():
            try:
                ms = next(gen)
            except StopIteration:
                if end_flag:          # 最后一条字幕显示够了再停录
                    QtCore.QTimer.singleShot(self.read_out(), lambda: open(os.path.join(REC, "end.flag"), "w").close())
                return
            except Exception:
                log("EXC", traceback.format_exc())
                open(os.path.join(REC, "end.flag"), "w").close()
                return
            QtCore.QTimer.singleShot(int(ms or 0), nxt)
        nxt()


def boot(script_main, delay=7000):
    """FreeCAD 启动后：最大化、关开始页上的“首次启动”、告诉录像脚本可以开录"""
    log("boot scheduled")

    def go():
        log("boot go")
        Gui.getMainWindow().showMaximized()
        QtCore.QTimer.singleShot(1200, lambda: (open(os.path.join(REC, "ready.flag"), "w").close(),
                                                QtCore.QTimer.singleShot(800, script_main)))
    QtCore.QTimer.singleShot(delay, go)


def menu_path(d, *names):
    """真点菜单：菜单栏上的“编辑”→ 弹出菜单里的“首选项…”（名字按开头匹配，忽略 & 和 …）"""
    norm = lambda t: t.replace("&", "").replace("…", "").replace("...", "").strip()
    mb = d.mw.menuBar()
    act = [a for a in mb.actions() if norm(a.text()).startswith(names[0])][0]
    p = mb.mapToGlobal(mb.actionGeometry(act).center())
    yield d.move(p, 800)
    d.click(p)
    yield 700
    for name in names[1:]:
        menus = [m for m in QtWidgets.QApplication.topLevelWidgets() if isinstance(m, QtWidgets.QMenu) and m.isVisible()]
        m = menus[-1]
        a = [a for a in m.actions() if norm(a.text()).startswith(name)][0]
        p = m.mapToGlobal(m.actionGeometry(a).center())
        yield d.move(p, 600)
        if name == names[-1]:
            d.ring(p)
            yield 250
            m.close()
            QtCore.QTimer.singleShot(0, a.trigger)     # 触发菜单项（模态对话框在下一轮事件里打开，剧本照常往下走）
        else:
            d.click(p)
        yield 700
