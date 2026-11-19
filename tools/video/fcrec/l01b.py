"""第 1 课 片段 B：鼠标导航（CAD 方式）与视图：中键拖 = 平移，中键 + 左键拖 = 旋转，滚轮 = 缩放；导航立方体、标准视图、适应全部；点选零件看属性。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtWidgets, QtCore, QtGui, L, model_dir
import steps

M = os.path.join(os.environ.get("WQ_REC", "."), "model")


def scale(d):
    a, b = d.model_pt(0, 0, 0), d.model_pt(100, 0, 0)
    return round(((b.x() - a.x()) ** 2 + (b.y() - a.y()) ** 2) ** 0.5, 1)


def script(d):
    App.openDocument(os.path.join(model_dir(), "WQ-LS.FCStd"))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 2500
    vp = d.vp()
    c = d.center(vp)
    yield d.say("状态栏右下角写着“CAD”：现在是 CAD 导航方式（问渠 CAD 默认）")
    sb = d.mw.statusBar()
    p = sb.mapToGlobal(QtCore.QPoint(sb.width() - 220, sb.height() // 2))
    yield d.move(p, 900); d.ring(p); yield 2600
    yield d.say("CAD 导航方式：按住中键拖动 = 平移")
    yield d.move(c, 700)
    d.press(Qt.MiddleButton); yield 150
    yield d.move(c + QtCore.QPoint(220, 60), 1500, buttons=Qt.MiddleButton)
    d.release(Qt.MiddleButton); yield 800
    log("after pan", scale(d))
    yield d.say("按住中键再按左键拖动 = 旋转")
    p = d.pos
    d.press(Qt.MiddleButton); d._send(QtCore.QEvent.MouseButtonPress, p, Qt.LeftButton, Qt.MiddleButton | Qt.LeftButton); yield 150
    yield d.move(p + QtCore.QPoint(-260, 40), 1800, buttons=Qt.MiddleButton | Qt.LeftButton)
    d._send(QtCore.QEvent.MouseButtonRelease, d.pos, Qt.LeftButton, Qt.MiddleButton); d.release(Qt.MiddleButton); yield 900
    yield d.say("滚轮 = 缩放：往前滚放大，往后滚缩小（以鼠标所在点为中心）")
    q = d.model_pt(0, 0, 150)
    yield d.move(c, 700)
    for k in range(5):
        d.wheel(1); yield 260
    yield 600
    for k in range(5):
        d.wheel(-1); yield 260
    yield 800
    yield d.say("转乱了不要紧：点“适应全部”，整机回到画面中间")
    yield d.tool("Std_ViewFitAll"); yield 1400
    yield d.say("导航立方体：点“前视图”那一面，就从前面看；点角上，看轴测")
    cube = QtCore.QPoint(vp.width() - 80, 75)
    p = vp.mapToGlobal(cube)
    yield d.move(p, 900)
    d.click(p); yield 1800
    log("after cube", Gui.ActiveDocument.ActiveView.getViewDirection())
    yield d.say("键盘也行：0 轴测、1 前、2 上、3 右")
    for k, key in ((Qt.Key_2, "2"), (Qt.Key_3, "3"), (Qt.Key_0, "0")):
        d.key(key, d.vp()); yield 1500
        log("key", key, Gui.ActiveDocument.ActiveView.getViewDirection())
    Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("左键点一个零件：它变绿，左下的属性里显示它的数据；点空白处取消")
    obj = App.ActiveDocument.getObject("handwheel")
    bb = obj.Shape.BoundBox
    p = d.model_pt(bb.Center.x, bb.YMin, bb.Center.z)
    yield d.move(p, 900)
    d.click(p); yield 1500
    log("sel", [s.ObjectName for s in Gui.Selection.getSelectionEx()])
    yield 2000
    p = vp.mapToGlobal(QtCore.QPoint(140, vp.height() - 110))
    yield d.move(p, 800)
    d.click(p); yield 1500
    log("sel2", [s.ObjectName for s in Gui.Selection.getSelectionEx()])


def main():
    d = Director()
    d.run(script(d))


boot(main)
