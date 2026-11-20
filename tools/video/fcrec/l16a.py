"""第 16 课 片段 A：让机构动起来——装配里“创建仿真”，给上轴的旋转关节加运动：角度 = 2π·时间（1 秒一圈），算运动学，播放；拖时间条看针杆的上下止点。真操作。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_dir
import steps

PARTS = [L("机架", "Frame"), L("上轴曲柄", "ShaftCrank"), L("连杆", "Rod"), L("针杆组件", "NeedleBarAssy")]


def named(name):
    ws = [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.objectName() == name]
    return ws[0] if ws else None


def click_w(d, w, ms=800):
    p = d.center(w)
    yield d.move(p, ms)
    d.click(p)
    yield 600


def script(d):
    doc = App.openDocument(os.path.join(model_dir(), "slider", L("曲柄滑块", "SliderCrank") + ".FCStd"))
    for name in PARTS:
        App.openDocument(os.path.join(model_dir(), "slider", name + ".FCStd"))
    App.setActiveDocument(doc.Name)
    asm = [o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject"][0]
    nb = [o for o in doc.Objects if o.TypeId == "App::Link" and o.Label == PARTS[3]][0]
    Gui.runCommand("Std_ViewFront"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield from steps.pick_workbench(d, "装配", "Assembly")
    p = d.tree_item(asm.Label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield 1500
    yield d.say("运动：上一课的曲柄滑块只剩 1 个自由度。给上轴的旋转关节一个“运动”，整个机构就跟着动")
    yield d.say("点“创建仿真”，再点“添加”运动")
    yield d.tool("Assembly_CreateSimulation")
    yield from d.until(lambda: named("AddButton") is not None, 8000)
    yield 1000
    b = named("AddButton")
    p = d.center(b)
    yield d.move(p, 800)
    QtCore.QTimer.singleShot(0, lambda: d.click(p))      # 运动设置框是模态的：放到下一轮事件里点
    yield from d.until(lambda: QtWidgets.QApplication.activePopupWidget() is not None or QtWidgets.QApplication.activeModalWidget() is not None, 6000)
    yield 1000
    dlg = QtWidgets.QApplication.activePopupWidget() or QtWidgets.QApplication.activeModalWidget()
    combo = [w for w in dlg.findChildren(QtWidgets.QComboBox)][0]
    log("joints", [combo.itemText(i) for i in range(combo.count())], combo.currentText())
    yield d.say("关节选上轴的旋转关节，公式写 2*pi*time：角度按弧度，1 秒转一圈")
    ed = dlg.findChildren(QtWidgets.QLineEdit)[0]
    p = d.center(ed)
    yield d.move(p, 700)
    d.click(p); yield 300
    ed.setFocus(); ed.selectAll()
    d.keys("2*pi*time", w=ed)
    yield 1200
    ok = [b for b in dlg.findChildren(QtWidgets.QPushButton) if b.text().replace("&", "") in ("OK", "确定")][0]
    p = d.center(ok)
    yield d.move(p, 700)
    d.ring(p)
    ok.click()
    yield 1500
    sims = [o for o in doc.Objects if "Simulation" in o.Name or (hasattr(o, "Proxy") and o.Proxy.__class__.__name__ == "Simulation")]
    log("motions", [(o.Label, getattr(o, "Formula", None)) for o in doc.Objects if hasattr(o, "Formula")])
    yield d.say("点“运行运动学”算一遍，再点“向前播放”")
    yield from click_w(d, named("RunKinematicsButton"))
    yield from d.until(lambda: named("PlayForwardButton") is not None, 30000)
    yield 1500
    yield from click_w(d, named("PlayForwardButton"))
    yield 5000
    s = named("frameSlider")
    zs = []
    for v in range(s.minimum(), s.maximum() + 1):
        s.setValue(v)
        QtWidgets.QApplication.processEvents()
        zs.append(nb.Placement.Base.z)
    s.setValue(s.minimum())
    log("frames", s.minimum(), s.maximum(), "nb z min/max", round(min(zs), 2), round(max(zs), 2), "stroke", round(max(zs) - min(zs), 2),
        "at", zs.index(max(zs)), zs.index(min(zs)))
    yield d.say("拖时间条：曲柄销在最上面时针杆在上止点，转半圈到下止点——针杆走了一个行程")
    lo, hi = s.minimum(), s.maximum()
    for v in (lo, (lo + hi) // 2):       # 时间条拖到 0 s（上止点）、0.5 s（下止点）
        frac = (v - lo) / (hi - lo)
        q = s.mapToGlobal(QtCore.QPoint(int(8 + (s.width() - 16) * frac), s.height() // 2))
        yield d.move(q, 900)
        d.ring(q)
        s.setValue(v)
        yield 2500
    yield 3000
    yield d.say("针杆行程 31 mm = 曲柄半径 15.5 × 2：滑块正对着曲柄轴心时，行程就是两倍曲柄半径")
    yield 3500
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
