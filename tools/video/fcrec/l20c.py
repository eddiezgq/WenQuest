"""第 20 课 片段 C：计算与导出（在 Python 控制台里，宏、脚本也是这样用的）。WQ_STOCK=1 录官方 FreeCAD 1.1.4，否则录问渠 CAD。
① 半径 3、高 10 的圆柱转成 B 样条，求体积，和 π·r²·h 比：官方版差 0.86%，问渠 CAD 一样。
② 装配里两个方块，带颜色导出 STEP 再导回：官方版变成 4 个零件（重复了），问渠 CAD 是 2 个。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, menu_path
import steps

STOCK = os.environ.get("WQ_STOCK") == "1"
LINES1 = ["import Part, math",
          "c = Part.makeCylinder(3, 10).toNurbs()",
          "c.Volume, math.pi * 3**2 * 10, abs(c.Volume / (math.pi * 90) - 1)"]
LINES2 = ["import Import",
          "doc = App.newDocument('Colors'); asm = doc.addObject('App::Part', 'Assembly')",
          "boxes = [doc.addObject('Part::Box', 'Box%d' % i) for i in range(2)]; boxes[1].Placement.Base.x = 20",
          "for b in boxes: asm.addObject(b)",
          "",
          "doc.recompute(); Import.export([asm] + [(b, [(1.0, 0.0, 0.0, 1.0)] * 6) for b in boxes], '/tmp/colors.step')",
          "back = App.newDocument('Back'); Import.insert('/tmp/colors.step', back.Name)",
          "len([o for o in back.Objects if o.TypeId == 'Part::Feature'])"]


def console():
    for w in QtWidgets.QApplication.allWidgets():
        try:
            if w.metaObject().className() == "Gui::PythonConsole" and w.isVisible():
                return w
        except RuntimeError:
            pass
    return None


def type_lines(d, con, lines):
    for ln in lines:
        con.setFocus()
        d.keys(ln, w=con)
        yield 300 + 25 * len(ln)
        d.key(Qt.Key_Return, con)
        yield 900


def last_output(con, n=1):
    lines = [x for x in con.toPlainText().splitlines() if x.strip() and not x.startswith((">>>", "..."))]
    return lines[-n:]


def script(d):
    who = L("官方 FreeCAD 1.1.4", "Official FreeCAD 1.1.4") if STOCK else L("问渠 CAD", "WenQuest CAD")
    App.newDocument("Unnamed")
    yield 1000
    if console() is None:
        path = steps.menu_find(d, "Std_DlgPythonConsole") or None
        log("console menu", path)
        for dw in d.mw.findChildren(QtWidgets.QDockWidget):
            if dw.objectName() in ("Python console", "Python 控制台"):
                dw.show()
                dw.raise_()
        yield 1000
    con = console()
    log("console", con is not None)
    yield d.say(L(f"{who}：打开 Python 控制台（菜单“视图 → 面板”）。宏、脚本、AI 工作台，都是这样调用 FreeCAD 的",
                  f"{who}: open the Python console (View → Panels). Macros, scripts and the AI workbench all call FreeCAD this way"))
    yield 4000
    p = d.center(con)
    yield d.move(p, 700)
    d.click(p)
    yield 500
    yield d.say(L("① 半径 3、高 10 的圆柱，转成 B 样条（STEP 里常见的表示法），求体积，和 π r² h 比", "① A cylinder r 3, h 10 converted to B-spline (common in STEP files): its volume versus π r² h"))
    yield from type_lines(d, con, LINES1)
    out = last_output(con)
    log("out1", out)
    yield 1500
    try:
        rel = float(out[-1].strip("() ").split(",")[-1])
    except Exception:  # noqa: BLE001
        rel = None
    if rel is not None and rel > 1e-6:
        yield d.say(L(f"{who}：差了 {rel * 100:.2f}%——同一个圆柱，换个表示法体积就不对了，质量、惯量跟着错",
                      f"{who}: off by {rel * 100:.2f}% — the same cylinder, a different representation, a wrong volume; mass and inertia are wrong too"))
    elif rel is not None:
        yield d.say(L(f"{who}：相对误差 {rel:.0e}，和公式一样", f"{who}: relative error {rel:.0e}, the same as the formula"))
    yield 6000
    yield d.say(L("② 装配里放两个方块，带颜色导出 STEP，再导回来，数一数有几个零件", "② Two boxes in an assembly, export to STEP with colours, import back and count the parts"))
    yield from type_lines(d, con, LINES2)
    yield 1500
    out = last_output(con)
    log("out2", out)
    try:
        n = int(out[-1].strip())
    except Exception:  # noqa: BLE001
        n = None
    if n == 2:
        yield d.say(L(f"{who}：2 个，对", f"{who}: 2, correct"))
    elif n is not None:
        yield d.say(L(f"{who}：{n} 个——每个零件导出了两遍，别人收到的文件里零件重复了",
                      f"{who}: {n} — each part was written twice, so the file you send has duplicate parts"))
    yield 5000


def main():
    d = Director()
    d.run(script(d))


boot(main)
