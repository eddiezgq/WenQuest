"""几个课都用的操作段落（真操作）。每个都是生成器，用 yield from 接进剧本。"""
import FreeCAD as App
import FreeCADGui as Gui

from director import L, QtCore, QtWidgets, log
from director import L as _L


def new_body_sketch(d, plane="XY", say=True, zoom=(10, 170)):
    """开始页 → 参数实体 → 新建草图 → 选平面 → 确定 → 缩放到合适大小"""
    if say:
        yield d.say("从开始页新建一个“参数实体”：零件设计工作台，一个实体（Body）")
    lab = d.find(QtWidgets.QLabel, L("参数实体", "Parametric Body"))
    p = d.center(lab)
    yield d.move(p, 900)
    d.click(p)
    yield from d.until(lambda: Gui.ActiveDocument is not None and Gui.activeWorkbench().name() == "PartDesignWorkbench")
    yield 800
    if say:
        yield d.say(f"点“新建草图”，选 {plane} 平面")
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
    """正在编辑的草图；没在编辑就是最后一个草图"""
    vp = Gui.ActiveDocument.getInEdit() if Gui.ActiveDocument else None
    if vp is not None and getattr(vp, "Object", None) is not None and vp.Object.TypeId == "Sketcher::SketchObject":
        return vp.Object
    return [o for o in App.ActiveDocument.Objects if o.TypeId == "Sketcher::SketchObject"][-1]


def dump(tag):
    sk = sketch()
    log(tag, [str(g) for g in sk.Geometry], [(c.Type, c.First, c.FirstPos, c.Second, c.SecondPos, round(c.Value, 3)) for c in sk.Constraints],
        "full", getattr(sk, "FullyConstrained", "?"), "dof?", sk.solve())


def open_and_edit(d, path, sketch_label="Sketch", zoom=(10, 300)):
    """打开文件（同“文件 → 打开”），在模型树里双击草图进入编辑"""
    yield d.say("打开上一课存的针夹草图，在模型树里双击草图，进入编辑")
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
            lo = t.lower()
            if any(k in t for k in ("自由度", "完全约束", "过约束", "冗余", "空草图")) or any(k in lo for k in ("degree", "fully constrained", "over-constrained", "redundant", "empty sketch", "conflicting")):
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


def prop_pt(d, *path):
    """属性栏里某一行“值”那一格的位置：prop_pt(d, "Cylinder", "Radius")；路径按每层的名字（中英界面里组名会变，传元组 (中, 英) 也行）"""
    pe = [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.metaObject().className() == "Gui::PropertyEditor::PropertyEditor"][0]
    m = pe.model()
    par = QtCore.QModelIndex()
    ix = None
    for name in path:
        names = name if isinstance(name, tuple) else (name,)
        ix = None
        for r in range(m.rowCount(par)):
            if m.data(m.index(r, 0, par)) in names:
                ix = m.index(r, 0, par)
                break
        assert ix is not None, (path, name)
        pe.expand(ix)
        par = ix
    v = m.index(ix.row(), 1, ix.parent())
    pe.scrollTo(v)
    return pe, pe.viewport().mapToGlobal(pe.visualRect(v).center())


def prop_set(d, value, *path):
    """真操作改属性：双击值那一格，全选，键入，回车"""
    pe, p = prop_pt(d, *path)
    yield d.move(p, 800)
    d.click(p, double=True)
    yield 600
    w = QtWidgets.QApplication.focusWidget()
    log("prop editor", path, w.metaObject().className() if w else None)
    if w is None or w.metaObject().className() in ("Gui::PropertyEditor::PropertyEditor", "Gui::TreeWidget"):
        return                              # 编辑框没打开：不键入（空格会去切换模型树里的显示），由调用的人直接改
    d.key(QtCore.Qt.Key_A, w, QtCore.Qt.ControlModifier)
    d.keys(str(value), w=w)
    yield 500
    d.key(QtCore.Qt.Key_Return, w)
    yield 900


def file_dialog(d, name, type_hint=None):
    """Qt 的保存 / 导出对话框：（可选）选文件类型，键入文件名，点“保存”"""
    yield from d.until(lambda: isinstance(QtWidgets.QApplication.activeModalWidget(), QtWidgets.QFileDialog))
    dlg = QtWidgets.QApplication.activeModalWidget()
    import os
    dlg.setDirectory(os.environ.get("WQ_REC", "."))      # 文件都放录屏工作目录（软件会记上次的目录）
    yield 700
    if type_hint:
        cb = dlg.findChild(QtWidgets.QComboBox, "fileTypeCombo")
        i = [k for k in range(cb.count()) if type_hint in cb.itemText(k)][0]
        p = d.center(cb)
        yield d.move(p, 700)
        d.click(p)
        yield 700
        view = cb.view()
        ip = view.viewport().mapToGlobal(view.visualRect(cb.model().index(i, 0)).center())
        yield d.move(ip, 600)
        d.ring(ip)
        cb.setCurrentIndex(i)
        cb.activated.emit(i)
        cb.hidePopup()
        yield 600
    e = dlg.findChild(QtWidgets.QLineEdit, "fileNameEdit")
    p = d.center(e)
    yield d.move(p, 600)
    d.click(p)
    e.selectAll()
    d.keys(name, w=e)
    yield 700
    ok = [b for b in dlg.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text().replace("&", "").startswith(("保存", "Save", "打开", "Open"))][0]
    p = d.center(ok)
    yield d.move(p, 600)
    d.click(p)
    yield 1200


def pick_workbench(d, zh, en):
    """真点工作台下拉框，在弹出的列表里点名字"""
    from director import L
    c = d.wb_combo()
    p = d.center(c)
    yield d.move(p, 700)
    d.click(p)
    yield 800
    name = en          # 1.1 的工作台下拉框中文界面里也是英文名
    items = [c.itemText(k).replace("&", "") for k in range(c.count())]
    log("wb items", items)
    i = [k for k, t in enumerate(items) if t == name or t.startswith(name + " ")][0]
    view = c.view()
    view.scrollTo(c.model().index(i, 0))
    yield 300
    ip = view.viewport().mapToGlobal(view.visualRect(c.model().index(i, 0)).center())
    yield d.move(ip, 700)
    d.ring(ip)
    c.setCurrentIndex(i)
    c.activated.emit(i)
    c.hidePopup()
    yield 600
    cls = {wb.MenuText: k for k, wb in Gui.listWorkbenches().items()}.get(en)
    if cls and Gui.activeWorkbench().name() != cls:      # 程序里设下拉框当前项不一定触发切换：用它自己的切换命令
        Gui.activateWorkbench(cls)
    yield 1200
    log("workbench", Gui.activeWorkbench().name())


def answer_modal(d, texts=("是", "Yes", "确定", "OK"), wait=2500):
    """有对话框弹出来（比如“草图替代约束”问要不要换成端点相切）：移过去点“是 / 确定”"""
    t = 0
    while t < wait:
        m = QtWidgets.QApplication.activeModalWidget()
        if m is not None:
            log("modal", m.windowTitle())
            bs = [b for b in m.findChildren(QtWidgets.QAbstractButton) if b.isVisible() and b.text().replace("&", "").strip() in texts]
            if bs:
                yield 700
                p = d.center(bs[0])
                yield d.move(p, 600)
                d.ring(p)
                bs[0].click()
                yield 800
            return
        yield 150
        t += 150


# ------------------------------------------------------------ 第 6 课起
def sp(d, u, v):
    """草图坐标 (u, v) → 屏幕点（草图不在 XY 平面时用；按当前草图的放置换算）"""
    p = sketch().Placement.multVec(App.Vector(u, v, 0))
    return d.model_pt(p.x, p.y, p.z)


def combo_pick(d, combo, text):
    """真点下拉框，在弹出的列表里点 text（按开头匹配；给整数就是第几项）"""
    show(combo)
    yield 300
    p = d.center(combo)
    yield d.move(p, 700)
    d.click(p)
    yield 700
    i = text if isinstance(text, int) else [k for k in range(combo.count()) if combo.itemText(k).replace("&", "").startswith(text)][0]
    view = combo.view()
    view.scrollTo(combo.model().index(i, 0))
    yield 300
    ip = view.viewport().mapToGlobal(view.visualRect(combo.model().index(i, 0)).center())
    yield d.move(ip, 600)
    d.ring(ip)
    combo.setCurrentIndex(i)
    combo.activated.emit(i)
    combo.hidePopup()
    yield 800


def named(cls, name):
    ws = [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and isinstance(w, cls) and w.objectName() == name]
    return ws[0] if ws else None


def show(w):
    """任务面板很长时，先把 w 滚到看得见的地方（不然算出来的点会落在面板外面）"""
    p = w.parentWidget()
    while p is not None:
        if isinstance(p, QtWidgets.QScrollArea):
            p.ensureWidgetVisible(w, 10, 40)
            return
        p = p.parentWidget()


def type_into(d, w, text):
    """点输入框，全选，键入，Tab 交给特征"""
    show(w)
    yield 300
    p = d.center(w)
    yield d.move(p, 700)
    d.click(p)
    yield 300
    w.setFocus()
    w.selectAll()
    d.keys(text, w=w)
    yield 900
    d.key(QtCore.Qt.Key_Tab, w)
    yield 600
    le = w.findChild(QtWidgets.QLineEdit)
    if le is not None and le.text() == text:      # 有的输入框（螺旋的节距、高度）Tab 不交值：让它自己解析一次
        le.editingFinished.emit()
        try:
            w.setProperty("rawValue", float(text.split()[0]))
        except ValueError:
            pass
        yield 400
        log("type_into fallback", w.objectName(), w.text())


def task_ok(d, gone=None):
    """任务面板的“确定”（只找任务面板里的，别点到状态栏上的按钮）。gone：等这个名字的控件消失（基准面这类不进“编辑”的对话框）"""
    def in_task(w):
        p = w.parentWidget()
        while p is not None:
            if "Task" in p.metaObject().className():
                return True
            p = p.parentWidget()
        return False
    oks = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QPushButton) and w.isVisible()
           and w.text().replace("&", "") in ("确定", "OK") and in_task(w)]
    ok = oks[0] if oks else (d.find(QtWidgets.QPushButton, "确定") or d.find(QtWidgets.QPushButton, "OK"))
    log("task ok", len(oks), ok.text() if ok else None, d.center(ok) if ok else None)
    yield d.move(d.center(ok), 700)
    d.click(d.center(ok))
    if gone:
        yield from d.until(lambda: not [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.objectName() == gone], 6000)
    else:
        yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900


def datum(d, value):
    """尺寸约束弹出的输入框：全选、键入、回车，再点框里的“确定”（第 5 课见过回车不一定关框）"""
    yield from d.until(lambda: isinstance(QtWidgets.QApplication.focusWidget(), QtWidgets.QAbstractSpinBox), 6000)
    w = QtWidgets.QApplication.focusWidget()
    yield 500
    d.key(QtCore.Qt.Key_A, w, QtCore.Qt.ControlModifier)
    d.keys(str(value), w=w)
    yield 800
    d.key(QtCore.Qt.Key_Return, w)
    yield 800
    oks = [b for b in QtWidgets.QApplication.allWidgets() if isinstance(b, QtWidgets.QPushButton) and b.isVisible()
           and b.text().replace("&", "") in ("确定", "OK") and b.window() is not d.mw]
    if oks:
        p = d.center(oks[0])
        yield d.move(p, 600)
        d.click(p)
        yield 500
        try:
            if oks[0].isVisible():
                oks[0].click()
        except RuntimeError:
            pass
        yield 600


def pick_sp(d, *pts):
    """同 pick，草图坐标按当前草图的放置换算（草图不在 XY 平面时用）"""
    for u, v in pts:
        yield d.move(sp(d, u, v), 800)
        d.click(); yield 500


# ------------------------------------------------------------ 第 9 课起（手轮：圆、挖穿、环形阵列）
def circle_on_axis(d, x, y, dia, axis_tool, value):
    """圆心点在坐标轴上，键入直径；选圆心，加水平 / 竖直距离"""
    yield d.tool("Sketcher_CompCreateConic", "Sketcher_CreateCircle"); yield 300
    yield d.move(sp(d, x, y), 900)
    d.click(); yield 500
    yield d.move(sp(d, x + dia * 0.4, y + dia * 0.3), 700)
    n0 = len(sketch().Geometry)
    d.keys(str(dia), enter=True); yield 1000
    if len(sketch().Geometry) == n0:     # 小圆键入的直径有时接不住：点第二下定大概，后面补直径约束
        yield d.move(sp(d, x + dia * 0.4, y + dia * 0.3), 300)
        d.click(); yield 700
    d.key(QtCore.Qt.Key_Escape); yield 600
    sk = sketch()
    c = sk.Geometry[-1].Center
    p = sp(d, c.x, c.y)
    yield d.move(p, 700)
    d.ring(p)                      # 圆心压在坐标轴上，点下去会选中轴：直接选圆心那个点
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(App.ActiveDocument.Name, sk.Name, "Vertex1")
    yield 500
    yield d.tool("Sketcher_CompDimensionTools", axis_tool)
    yield from datum(d, value)
    App.ActiveDocument.recompute(); yield 500
    sk = sketch()
    if not any(c.Type in ("Diameter", "Radius") for c in sk.Constraints):
        Gui.Selection.clearSelection()
        g = sk.Geometry[-1]
        yield d.move(sp(d, g.Center.x, g.Center.y + g.Radius), 800)
        d.click(); yield 500
        yield d.tool("Sketcher_CompDimensionTools", "Sketcher_ConstrainDiameter")
        yield from datum(d, dia)
        App.ActiveDocument.recompute(); yield 500
    dump("circle")
    log("dof", dof_text(d))


def pocket_through(d):
    """凹槽：通过所有 + 反转（草图在 XY 基准面上 = 手轮的底面，默认往外挖，反转才往里）"""
    yield d.tool("Sketcher_LeaveSketch")
    yield from d.until(lambda: Gui.ActiveDocument.getInEdit() is None)
    yield 900
    yield d.tool("PartDesign_Pocket")
    yield from d.until(lambda: named(QtWidgets.QComboBox, "changeMode") is not None, 8000)
    yield 1000
    yield from combo_pick(d, named(QtWidgets.QComboBox, "changeMode"), _L("通过所有", "Through all"))
    log("pocket boxes", [(w.objectName(), w.text(), w.isChecked()) for w in QtWidgets.QApplication.allWidgets()
                         if w.isVisible() and isinstance(w, QtWidgets.QCheckBox)])
    cb = named(QtWidgets.QCheckBox, "checkBoxReversed")
    if cb is not None and not cb.isChecked():
        p = d.center(cb)
        yield d.move(p, 700)
        d.click(p); yield 300
        if not cb.isChecked():
            cb.click()
        yield 800
    yield from task_ok(d)
    pk = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::Pocket"][-1]
    log("pocket", pk.Type, pk.Reversed, round(pk.Shape.Volume, 2))
    return pk


def polar(d, feat, n):
    """在模型树里选特征，点“环形阵列”，次数 n，确定"""
    p = d.tree_item(feat.Label)
    yield d.move(p, 800)
    d.click(p); yield 600
    yield d.tool("PartDesign_PolarPattern")
    find = lambda: [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and isinstance(w, QtWidgets.QAbstractSpinBox)
                    and "ccurrence" in w.objectName()]
    yield from d.until(find, 8000)
    yield 1200
    log("polar widgets", [(w.objectName(), w.currentText() if isinstance(w, QtWidgets.QComboBox) else w.text()) for w in QtWidgets.QApplication.allWidgets() if w.isVisible()
                          and isinstance(w, (QtWidgets.QAbstractSpinBox, QtWidgets.QComboBox)) and w.objectName()])
    w = find()[0]
    yield from type_into(d, w, str(n))
    yield 1200
    yield from task_ok(d)
    pp = [o for o in App.ActiveDocument.Objects if o.TypeId == "PartDesign::PolarPattern"][-1]
    log("polar", pp.Occurrences, pp.Angle.Value, pp.Axis, round(pp.Shape.Volume, 2))




def zoom_sk(d, mm, px, at=None):
    """同 d.zoom_to，但按当前草图的横轴量（草图不在 XY 平面时用）"""
    for _ in range(90):
        a, b = sp(d, 0, 0), sp(d, mm, 0)
        cur = ((b.x() - a.x()) ** 2 + (b.y() - a.y()) ** 2) ** 0.5
        if 0.85 * px <= cur <= 1.18 * px:
            return
        d.wheel(1 if cur < px else -1, at or d.center(d.vp()))
        yield 120
    log("zoom_sk gave up", cur)


def prop_bool(d, obj, prop, value, *path):
    """属性栏里的是/否：点值那一格，出来的勾选框（或下拉）改成 value；没接住就直接改属性（和点一样）"""
    pe, p = prop_pt(d, *path)
    yield d.move(p, 800)
    d.click(p)
    yield 700
    w = QtWidgets.QApplication.focusWidget()
    log("prop bool editor", path, w.metaObject().className() if w else None)
    if isinstance(w, QtWidgets.QCheckBox):
        if w.isChecked() != value:
            q = d.center(w)
            d.click(q)
            yield 400
            if w.isChecked() != value:
                w.click()
    elif isinstance(w, QtWidgets.QComboBox):
        w.setCurrentIndex(1 if value else 0)
    yield 500
    if bool(getattr(obj, prop)) != value:
        setattr(obj, prop, value)
    d.key(QtCore.Qt.Key_Return, w) if w is not None else None
    yield 600


def menu_find(d, cmd):
    """菜单栏里找命令所在的路径（菜单文字）"""
    norm = lambda t: t.replace("&", "").replace("…", "").replace("...", "").strip()

    def walk(m, path):
        for a in m.actions():
            if a.objectName() == cmd or a.data() == cmd:
                return path + [norm(a.text())]
            if a.menu():
                r = walk(a.menu(), path + [norm(a.text())])
                if r:
                    return r
    for a in d.mw.menuBar().actions():
        if a.menu():
            r = walk(a.menu(), [norm(a.text()).split("(")[0]])
            if r:
                return r
