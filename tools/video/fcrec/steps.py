"""几个课都用的操作段落（真操作）。每个都是生成器，用 yield from 接进剧本。"""
import FreeCAD as App
import FreeCADGui as Gui

from director import QtCore, QtWidgets, log


def new_body_sketch(d, plane="XY", say=True, zoom=(10, 170)):
    """开始页 → 参数实体 → 新建草图 → 选平面 → 确定 → 缩放到合适大小"""
    if say:
        d.say("从开始页新建一个“参数实体”：零件设计工作台，一个实体（Body）")
    lab = d.find(QtWidgets.QLabel, "参数实体")
    p = d.center(lab)
    yield d.move(p, 900)
    d.click(p)
    yield from d.until(lambda: Gui.ActiveDocument is not None and Gui.activeWorkbench().name() == "PartDesignWorkbench")
    yield 800
    if say:
        d.say(f"点“新建草图”，选 {plane} 平面")
    yield from sketch_on(d, plane, zoom)


def sketch_on(d, plane="XY", zoom=(10, 170)):
    yield d.tool("PartDesign_CompSketches", "PartDesign_NewSketch")
    lists = lambda: [x for x in QtWidgets.QApplication.allWidgets() if isinstance(x, QtWidgets.QListWidget) and x.isVisible() and x.count() >= 3]
    yield from d.until(lists)
    yield 600
    L = lists()[0]
    it = [L.item(i) for i in range(L.count()) if L.item(i).text().startswith(plane)][0]
    p = L.viewport().mapToGlobal(L.visualItemRect(it).center())
    yield d.move(p, 700)
    d.click(p)
    yield 600
    ok = d.find(QtWidgets.QPushButton, "确定") or d.find(QtWidgets.QPushButton, "OK")
    yield d.move(d.center(ok), 700)
    d.click(d.center(ok))
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1000
    yield d.move(d.center(d.vp()), 600)
    yield from d.zoom_to(*zoom)
    yield 600


def sketch():
    return [o for o in App.ActiveDocument.Objects if o.TypeId == "Sketcher::SketchObject"][-1]


def dump(tag):
    sk = sketch()
    log(tag, [str(g) for g in sk.Geometry], [(c.Type, c.First, c.FirstPos, c.Second, c.SecondPos, round(c.Value, 3)) for c in sk.Constraints],
        "full", getattr(sk, "FullyConstrained", "?"), "dof?", sk.solve())


def open_and_edit(d, path, sketch_label="Sketch", zoom=(10, 300)):
    """打开文件（同“文件 → 打开”），在模型树里双击草图进入编辑"""
    App.openDocument(path)
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    t = d.tree()
    body = t.findItems("Body", QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
    if body:
        body[0].setExpanded(True)
    yield 400
    p = d.tree_item(sketch_label)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is not None and d.action_widget("Sketcher_CompCreateConic"))
    yield 1200
    yield d.move(d.center(d.vp()), 500)
    yield from d.zoom_to(*zoom)
    yield 500


def dof_text(d):
    """任务面板里“约束不足：n 个自由度 / 完全约束 / 过约束”那一行"""
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, QtWidgets.QLabel) and w.isVisible():
            t = w.text()
            if "自由度" in t or "完全约束" in t or "过约束" in t or "冗余" in t or "空草图" in t:
                return " ".join(t.split())
    return "?"


def pick(d, *pts):
    """依次点选（草图里点一下就加进选择，不用按 Ctrl）。点可以是 (x, y)，或 ("v", 几何号, 1/2/3) = 那个端点的当前位置"""
    for p in pts:
        if p[0] == "v":
            v = sketch().getPoint(p[1], p[2])
            x, y = v.x, v.y
        else:
            x, y = p
        yield d.move(d.model_pt(x, y), 800)
        d.click(); yield 500


def leave_and_pad(d, length):
    """关闭草图 → 凸台 → 长度键入 → 确定 → 轴测看"""
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    yield d.tool("PartDesign_Pad")
    find = lambda: [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and isinstance(w, QtWidgets.QAbstractSpinBox) and w.objectName() == "lengthEdit"]
    yield from d.until(find)
    yield 800
    L = find()[0]
    p = d.center(L)
    yield d.move(p, 700)
    d.click(p)
    yield 300
    L.setFocus()
    L.selectAll()
    d.keys(f"{length} mm", w=L)
    yield 1200
    d.key(QtCore.Qt.Key_Tab, L)
    yield 600
    pad = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Pad"][-1]
    if abs(pad.Length.Value - length) > 1e-6:      # 少数情况下输入框没把值交给特征（打开的旧文件里见过）：用输入框自己的接口再交一次
        L.setProperty("rawValue", float(length))
        L.lineEdit().setText(f"{length} mm")
        L.lineEdit().editingFinished.emit()
        yield 400
        log("pad fallback", pad.Length.Value)
    log("pad typed", L.text(), [(w.objectName(), w.text()) for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and isinstance(w, QtWidgets.QAbstractSpinBox)], [(o.Name, o.Length.Value) for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Pad"])
    ok = d.find(QtWidgets.QPushButton, "确定") or d.find(QtWidgets.QPushButton, "OK")
    yield d.move(d.center(ok), 700)
    d.click(d.center(ok))
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    Gui.runCommand("Std_ViewIsometric")
    Gui.SendMsgToActiveView("ViewFit")
    yield 900
    pad = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Pad"][-1]
    log("pad", pad.Length.Value, round(pad.Shape.Volume, 2))
