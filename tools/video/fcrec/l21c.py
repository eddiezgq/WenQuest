"""第 21 课 片段 C：AI 设计零件（AI Parts 工作台“AI 设计零件…”）。
“载入示例：平缝机上轴”（示意数据）→ 开始设计：AI 列条件、提方案；轴承位、强度、临界转速、轴承寿命由代码校核，
不合格交回 AI 改；合格后交回 AI 减重，采用通过且最轻的一轮 → 三维模型、工程图、BOM，模型回读核对 →
回放的示例不入企业库（真用时由人填图号、确认人后入库）。
AI 的回答是 freecad-ai-parts 自带的真实模型录制（面板标“录制回放”），其余全是真操作。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, menu_path
import steps


def run_cmd(d, cmd):
    path = steps.menu_find(d, cmd)
    log("menu", cmd, path)
    yield from menu_path(d, *path)


def click_w(d, w, ms=700):
    steps.show(w)
    yield 200
    p = d.center(w)
    yield d.move(p, ms)
    d.click(p)
    yield 600


def btn(*texts):
    bs = [b for b in QtWidgets.QApplication.allWidgets()
          if isinstance(b, QtWidgets.QPushButton) and b.isVisible() and b.text().startswith(texts)]
    return bs[0] if bs else None


def scroll(d, tb, frac, ms=4000):
    sb = tb.verticalScrollBar()
    end = int(sb.maximum() * frac)
    n = max(1, ms // 60)
    for k in range(n + 1):
        sb.setValue(sb.value() + (end - sb.value()) // max(1, n - k))
        yield 60


def tab_click(d, tabs, i):
    bar = tabs.tabBar()
    p = bar.mapToGlobal(bar.tabRect(i).center())
    yield d.move(p, 600)
    d.click(p)
    tabs.setCurrentIndex(i)
    yield 1200


def frame_left(d, right_px):
    """等轴测、充满，再把相机往右挪 right_px 像素：模型落在“AI 设计零件”窗口左边看得见的地方（不用 pivy：改相机描述字符串）"""
    import re
    v = Gui.ActiveDocument.ActiveView
    v.viewIsometric()
    v.fitAll()
    cam = v.getCamera()
    m = re.search(r"height\s+([-\d.e+]+)", cam)
    h = float(m.group(1)) if m else 100.0
    vp = v.getSize()
    k = right_px * h / max(1, vp[1])
    r = v.getCameraOrientation().multVec(App.Vector(1, 0, 0))
    mp = re.search(r"position\s+([-\d.e+]+)\s+([-\d.e+]+)\s+([-\d.e+]+)", cam)
    x, y, z = (float(mp.group(i)) for i in (1, 2, 3))
    cam = cam[:mp.start()] + f"position {x + r.x * k} {y + r.y * k} {z + r.z * k}" + cam[mp.end():]
    v.setCamera(cam)


def script(d):
    App.newDocument(L("上轴设计", "UpperShaftDesign"))
    yield 800
    yield d.say("最后一样：AI 设计零件。菜单“AI Parts → AI 设计零件…”")
    yield from steps.pick_workbench(d, "AI Parts", "AI Parts")
    yield 800
    yield from run_cmd(d, "FAP_AiDesign")
    yield from d.until(lambda: btn("载入示例", "Load example") is not None, 8000)
    yield 1500
    ex = btn("载入示例", "Load example")
    form = ex.window()
    log("form", form.windowTitle(), form.geometry())
    yield d.say("先选零件类型（阶梯轴），再写需求原话：转速、电机、机构参数、轴向位置、材料……轴承型号可以不指定")
    yield 5000
    yield d.say("点“载入示例：平缝机上轴”：一段写好的需求（示意数据）")
    yield from click_w(d, ex)
    yield 1500
    text = [w for w in form.findChildren(QtWidgets.QPlainTextEdit) if w.isVisible()][0]
    yield d.say("要求：最高 5000 r/min、要能提到 5500；两个轴承中心在 27 和 252 mm；曲柄、凸轮、偏心轮、带轮、手轮各在哪、多重；45 钢调质，安全系数 1.5，轴承寿命 2 万小时")
    yield from scroll(d, text, 1.0, 8000)
    yield 3000
    yield d.say("点“开始设计”。AI 的回答是真实模型的录制回放，面板上会标明")
    go = btn("开始设计", "Start design")
    yield from click_w(d, go)
    done = lambda: any(("结论" in l.text() or "Result" in l.text()) for l in form.findChildren(QtWidgets.QLabel) if l.isVisible())
    yield from d.until(done, 300000)
    yield 2500
    frame_left(d, 330)
    labels = [l.text() for l in form.findChildren(QtWidgets.QLabel) if l.isVisible() and l.text()]
    log("labels", labels)
    tabs = [t for t in form.findChildren(QtWidgets.QTabWidget) if t.isVisible()][0]
    yield d.say("结论：全部通过，4 轮。怎么来的？分工是：AI 列条件、提方案；能不能用全由代码算")
    yield 5000
    yield from tab_click(d, tabs, 0)
    yield d.say("“条件”：AI 从原话里读出的转速、轴承位置、载荷、质量，每条对着原话核过")
    yield from scroll(d, tabs.currentWidget(), 0.6, 5000)
    yield 2500
    yield from tab_click(d, tabs, 2)
    yield d.say("“AI 的问题”：原话没说清的地方 AI 不瞎猜，列出来问人——比如轴承寿命按 5000 还是 5500 r/min 算")
    yield 6500
    yield from tab_click(d, tabs, 1)
    tb = tabs.currentWidget()
    yield d.say("“每一轮”：第 1 轮通过，但轴粗到 Ø46、3.55 kg")
    yield from scroll(d, tb, 0.08, 2500)
    yield 2500
    yield d.say("每一项都是代码校核的：轴承能不能套进去、轴肩够不够高、每个台阶的安全系数、临界转速、轴承寿命")
    yield from scroll(d, tb, 0.3, 6000)
    yield 2500
    yield d.say("通过以后交回 AI 减重，再校核；第 4 轮 0.28 kg，仍全部通过——采用通过且最轻的一轮")
    yield from scroll(d, tb, 1.0, 6000)
    yield 3000
    yield d.say("然后生成三维模型和工程图，再从模型回读尺寸、和设计逐段核对，一致才出图")
    frame_left(d, 330)
    yield 6000
    yield d.say("最下面“确认入企业库”：真用时由工程师填图号、确认人，点了才入库；录制回放的示例不入库，按钮是灰的")
    ok = btn("确认入企业库", "Confirm")
    if ok is not None:
        p = d.center(ok)
        yield d.move(p, 800)
    yield 6000
    yield d.say("这一课的三样——选零件、零件库、设计零件——都是 AI 起草、代码把关、人拍板。课程到这里结束")
    yield 4000


def main():
    d = Director()
    d.run(script(d))


boot(main)
