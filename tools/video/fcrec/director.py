import os
"""问渠 CAD 录屏导演：在 FreeCAD 里按时间表做操作，鼠标平滑移动，点击处画黄圈。由录屏脚本 import。"""
import math
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore, QtGui
try:
    from PySide import QtWidgets
except ImportError:
    QtWidgets = QtGui

R_LOG = os.path.join(os.environ.get('WQ_REC', '.'), 'clicks.txt')

class Ring(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(None, QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool | QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground); self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.resize(90, 90); self.r = 0.0; self.hide()
    def paintEvent(self, e):
        p = QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing)
        a = max(0.0, 1.0 - self.r)
        p.setPen(QtGui.QPen(QtGui.QColor(242, 183, 5, int(255 * a)), 5)); p.setBrush(QtGui.QColor(242, 183, 5, int(50 * a)))
        rad = 14 + 26 * self.r; p.drawEllipse(QtCore.QPointF(45, 45), rad, rad)
    def flash(self, pt, done=None):
        self.move(pt.x() - 45, pt.y() - 45); self.r = 0.0; self.show(); self.raise_()
        t = QtCore.QTimer(self); n = [0]
        def step():
            n[0] += 1; self.r = n[0] / 18.0; self.update()
            if n[0] >= 18:
                t.stop(); self.hide(); done and done()
        t.timeout.connect(step); t.start(40)

class Director:
    def __init__(self):
        self.mw = Gui.getMainWindow(); self.ring = Ring(); self.q = []; self.pos = QtCore.QPoint(800, 450)
    # ---- 位置
    def center(self, w, rect=None):
        r = rect if rect is not None else w.rect()
        return w.mapToGlobal(r.center())
    def action_pt(self, cmd):
        for tb in self.mw.findChildren(QtWidgets.QToolBar):
            for a in tb.actions():
                if a.objectName() == cmd or a.data() == cmd:
                    w = tb.widgetForAction(a)
                    if w and w.isVisible():
                        return self.center(w)
        return None
    def wb_combo(self):
        for c in self.mw.findChildren(QtWidgets.QComboBox):
            if c.isVisible() and c.count() > 10 and c.mapTo(self.mw, QtCore.QPoint(0, 0)).y() < 60:
                return c
    def tree(self):
        for t in self.mw.findChildren(QtWidgets.QTreeWidget):
            if t.isVisible() and t.topLevelItemCount() and t.mapTo(self.mw, QtCore.QPoint(0, 0)).x() < 300:
                return t
    def tree_pt(self, label):
        t = self.tree()
        it = t.findItems(label, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)[0]
        t.scrollToItem(it)
        return t.viewport().mapToGlobal(t.visualItemRect(it).center()), it
    # ---- 时间表
    def at(self, ms, fn):
        self.q.append((ms, fn)); return self
    def run(self):
        for ms, fn in self.q:
            QtCore.QTimer.singleShot(int(ms), self._safe(fn))
    def _safe(self, fn):
        def f():
            try:
                fn()
            except Exception:
                import traceback; traceback.print_exc()
        return f
    # ---- 动作
    def move(self, pt, ms=700):
        a, b = QtCore.QPoint(self.pos), QtCore.QPoint(pt); self.pos = QtCore.QPoint(pt)
        n = max(1, int(ms / 20)); t = QtCore.QTimer(self.mw); k = [0]
        def step():
            k[0] += 1; s = k[0] / n; e = s * s * (3 - 2 * s)
            QtGui.QCursor.setPos(int(a.x() + (b.x() - a.x()) * e), int(a.y() + (b.y() - a.y()) * e))
            if k[0] >= n: t.stop()
        t.timeout.connect(step); t.start(20)
    def click(self, pt, then=None):
        import time
        with open(R_LOG, 'a') as f: f.write(f'{time.time():.3f} {pt.x()} {pt.y()}\n')
        then and QtCore.QTimer.singleShot(250, self._safe(then))
    def orbit(self, ms=6000, vel=1.0, axis=(0, 0, 1)):
        v = Gui.ActiveDocument.ActiveView
        v.startAnimating(axis[0], axis[1], axis[2], vel)
        QtCore.QTimer.singleShot(int(ms), v.stopAnimating)
