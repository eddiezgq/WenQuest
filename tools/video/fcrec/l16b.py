"""第 16 课 片段 B：问渠多体动力学——同一个曲柄滑块，给零件指定材料（45 钢），上轴 5000 r/min 匀速，
运动学反算：曲柄驱动力矩、曲柄销受力；看可信度核查。真操作（AI 工作台“装配体多体动力学”面板，不调用 AI）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_dir, menu_path
import steps

PARTS = [L("机架", "Frame"), L("上轴曲柄", "ShaftCrank"), L("连杆", "Rod"), L("针杆组件", "NeedleBarAssy")]
MAT_PATH = ["System", "Standard", "Metal", "Steel", "Steel-1C45"]


def panel():
    ws = [w for w in QtWidgets.QApplication.allWidgets() if w.objectName() == "FapMbdAssemblyPanel"]
    return ws[0] if ws else None


def click_w(d, w, ms=800):
    steps.show(w)
    yield 200
    p = d.center(w)
    yield d.move(p, ms)
    d.click(p)
    yield 700


def set_material(d, doc, link):
    """模型树里选中零件 → 菜单“编辑 → 设置材料…” → 材料树里点 Steel-1C45 → 确定"""
    p = d.tree_item(link.Label)
    yield d.move(p, 700)
    d.click(p)
    yield 500
    path = steps.menu_find(d, "Std_SetMaterial")
    log("setmat path", path)
    if path:
        yield from menu_path(d, *path)
    else:                                   # 不在菜单栏里：右键菜单
        QtCore.QTimer.singleShot(0, lambda: d.click(p, button=Qt.RightButton))
        yield 1200
        menus = [m for m in QtWidgets.QApplication.topLevelWidgets() if isinstance(m, QtWidgets.QMenu) and m.isVisible()]
        acts = [a for m in menus for a in m.actions() if a.objectName() == "Std_SetMaterial" or a.data() == "Std_SetMaterial"]
        log("ctx", [[a.text() for a in m.actions()] for m in menus][:1])
        if acts:
            a = acts[0]
            m = [m for m in menus if a in m.actions()][0]
            q = m.mapToGlobal(m.actionGeometry(a).center())
            yield d.move(q, 700)
            d.ring(q)
            QtCore.QTimer.singleShot(0, a.trigger)
            m.close()
    yield from d.until(lambda: dlg() is not None, 6000)
    yield 800
    dl = dlg()
    btn = [b for b in dl.findChildren(QtWidgets.QPushButton) if b.isVisible()][0]      # 材质框右边的下拉按钮
    yield from click_w(d, btn, 600)
    yield 600
    t = dl.findChildren(QtWidgets.QTreeView)[0]
    m = t.model()
    ix = QtCore.QModelIndex()
    for name in MAT_PATH:
        hit = [m.index(r, 0, ix) for r in range(m.rowCount(ix)) if m.data(m.index(r, 0, ix)) == name]
        if not hit:
            log("material path miss", name)
            break
        ix = hit[0]
        if name != MAT_PATH[-1]:
            t.expand(ix)
            yield 300
    t.scrollTo(ix)
    yield 500
    q = t.viewport().mapToGlobal(t.visualRect(ix).center())
    yield d.move(q, 700)
    d.click(q)
    yield 900
    lo = link.LinkedObject
    if getattr(getattr(lo, "ShapeMaterial", None), "Name", "") != MAT_PATH[-1]:     # 点空了：选中那一项（同样的效果）
        log("material click fallback", link.Label, t.isVisible())
        t.setCurrentIndex(ix)
        t.clicked.emit(ix)
        yield 600
    cl = [b for b in QtWidgets.QApplication.allWidgets() if isinstance(b, QtWidgets.QPushButton) and b.isVisible()
          and b.text().replace("&", "") in ("Close", "关闭")]
    if cl:                                   # 选中即生效；任务面板点“关闭”
        yield from click_w(d, cl[0], 600)
    yield 600
    lo = link.LinkedObject
    log("material", link.Label, getattr(getattr(lo, "ShapeMaterial", None), "Name", None))


def dlg():
    ws = [w for w in QtWidgets.QApplication.allWidgets() if w.isVisible() and w.objectName() == "MatGui__DlgMaterial"]
    return ws[0] if ws else None


def script(d):
    doc = App.openDocument(os.path.join(model_dir(), "slider", L("曲柄滑块", "SliderCrank") + ".FCStd"))
    for name in PARTS:
        App.openDocument(os.path.join(model_dir(), "slider", name + ".FCStd"))
    App.setActiveDocument(doc.Name)
    links = {o.Label: o for o in doc.Objects if o.TypeId == "App::Link"}
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("上一段看的是“怎么动”。要知道“要多大力”，用问渠多体动力学：AI Parts 工作台，菜单“AI Parts → 装配体多体动力学”")
    yield from steps.pick_workbench(d, "AI Parts", "AI Parts")
    yield 2000
    later = [b for b in QtWidgets.QApplication.allWidgets() if isinstance(b, QtWidgets.QPushButton) and b.isVisible()
             and b.text().replace("&", "") in ("以后再说", "Later", "Not now")]
    if later:                               # 第一次进 AI 工作台会问 AI 密钥：本课不用 AI
        yield d.say("第一次进 AI 工作台会问 AI 密钥；这一课不用 AI，点“以后再说”")
        yield from click_w(d, later[0])
    App.setActiveDocument(doc.Name)
    yield from menu_path(d, "AI Parts", L("装配体多体动力学", "装配体多体动力学"))
    yield from d.until(lambda: panel() is not None, 8000)
    yield 2000
    p = panel()
    dock = p if isinstance(p, QtWidgets.QDockWidget) else [w for w in QtWidgets.QApplication.allWidgets()
                                                          if isinstance(w, QtWidgets.QDockWidget) and w.isAncestorOf(p)][0]
    d.mw.resizeDocks([dock], [720], Qt.Horizontal)      # 面板拉宽，曲线看得清（用户拖面板边就行）
    yield 800
    Gui.SendMsgToActiveView("ViewFit")
    yield 1000
    log("status0", p.status.text())
    yield d.say("先读装配体：它说零件没有材料——算质量、惯量要密度，程序不替你估")
    yield 3500
    yield d.say("给 4 个零件都指定材料：选中零件，菜单“视图 → 材质”，下拉里选 Steel-1C45（45 钢），关闭")
    for name in PARTS:
        yield from set_material(d, doc, links[name])
    yield d.say("再点“用当前文档的装配体”：3 个运动零件、4 个运动副，零件质量按实体和密度算")
    App.setActiveDocument(doc.Name)
    Gui.ActiveDocument = Gui.getDocument(doc.Name)
    yield 300
    yield from click_w(d, p.use_doc)
    yield 2000
    log("status1", p.status.text(), App.ActiveDocument.Label)
    if p.model is None:
        r = p.load_document(doc)
        log("load fallback", r, p.status.text()[:200])
    if p.model:
        log("bodies", [(b["id"], b.get("name"), round(b["mass_kg"], 4)) for b in p.model["bodies"]])
        log("joints", [(j["id"], j["type"], j.get("body_i"), j.get("body_j")) for j in p.model["joints"]])
    drive = [j for j in p.model["joints"] if j["type"] == "revolute" and j.get("body_i") == "ground"][0]["id"]
    yield d.say(L(f"驱动：上轴的转动副（{drive}）选“匀速”，5000 r/min", f"Drive: the upper-shaft revolute joint ({drive}), constant speed, 5000 rpm"))
    row = [i for i in range(p.drives.rowCount()) if p.drives.item(i, 0).text() == drive][0]
    p.drives.scrollToItem(p.drives.item(row, 0), QtWidgets.QAbstractItemView.PositionAtTop)
    yield 300
    yield from steps.combo_pick(d, p.drives.cellWidget(row, 1), 1)
    it = p.drives.item(row, 2)
    p.drives.scrollToItem(it, QtWidgets.QAbstractItemView.PositionAtTop)
    yield 400
    p.drives.setCurrentCell(row, 2)
    p.drives.scrollToItem(it, QtWidgets.QAbstractItemView.PositionAtTop)
    QtWidgets.QApplication.processEvents()
    q = p.drives.viewport().mapToGlobal(p.drives.visualItemRect(it).center())
    yield d.move(q, 700)
    d.ring(q)
    p.drives.editItem(it)                    # 双击单元格进入编辑（表很矮，直接让这一格进编辑，免得点到别的行）
    yield 700
    ed = QtWidgets.QApplication.focusWidget()
    if isinstance(ed, QtWidgets.QLineEdit) and p.drives.isAncestorOf(ed):
        ed.selectAll()
        d.keys("5000", w=ed)
        yield 500
        d.key(Qt.Key_Return, ed)
        yield 600
    for i in range(p.drives.rowCount()):     # 核对：只有上轴这一行有驱动
        if i != row and p.drives.item(i, 2).text():
            log("drive stray", p.drives.item(i, 0).text(), p.drives.item(i, 2).text())
            p.drives.item(i, 2).setText("")
    if p.drives.item(row, 2).text() != "5000" or p.drives.cellWidget(row, 1).currentData() != "speed":
        log("drive fallback", p.drives.item(row, 2).text(), p.drives.cellWidget(row, 1).currentData())
        p.set_drive(drive, "speed", 5000)
    yield 800
    yield d.say("分析选“运动学”：运动给定，反算每一时刻要多大驱动力矩、各运动副受多大力。一圈 0.012 秒，分 120 步")
    yield from steps.combo_pick(d, p.kind, [i for i in range(p.kind.count()) if p.kind.itemData(i) == "kinematic"][0])
    for w, v in ((p.end, "0.012"), (p.steps, "120")):
        yield from click_w(d, w, 600)
        w.selectAll()
        d.keys(v, w=w)
        yield 500
        if w.text() != v:
            log("field fallback", w.text(), v)
            w.setText(v)
    yield d.say("点“计算”")
    yield from click_w(d, p.run_btn)
    yield from d.until(lambda: p.data is not None or "没有算出" in p.status.text(), 120000)
    yield 1500
    log("status2", p.status.text())
    log("verdict", p.verdict.text())
    yield d.say("先看核查：约束残差、自由度都通过——结果才有意义")
    steps.show(p.verdict)
    yield 4000
    from freecad_addon.core import mbd_study as ST
    cv = ST.curves(p.data)
    want = [k for k in cv if k.startswith("驱动")]
    pin = [j for j in p.model["joints"] if j["type"] == "revolute" and j.get("body_i") not in ("ground", None)
           and drive and (j.get("body_i") == [x for x in p.model["joints"] if x["id"] == drive][0].get("body_j"))]
    pin_id = pin[0]["id"] if pin else None
    tq = max(abs(x) for x in cv[want[0]][1])
    log("drive peak", round(tq, 2), "pin", pin_id)
    yield d.say(L(f"曲线：上轴驱动力矩，峰值约 {tq:.2f} N·m（设计计算书 G2 的刺布机构是 4.70 N·m）",
                  f"Curve: drive torque on the upper shaft, peak about {tq:.2f} N·m (design calculation G2, needle mechanism: 4.70 N·m)"))
    yield from steps.combo_pick(d, p.curve, list(cv).index(want[0]))      # 下拉框里的顺序同 curves()（英文界面文字是译过的）
    yield 5000
    if pin_id:
        key = f"运动副 {pin_id} 反力大小（N）"
        fp = max(cv[key][1])
        log("pin peak", round(fp, 1))
        yield d.say(L(f"曲柄销（{pin_id}）受力，峰值约 {fp:.0f} N——第 19 课用它算曲柄的应力",
                      f"Crank-pin force ({pin_id}), peak about {fp:.0f} N — lesson 19 uses it for the crank stress"))
        yield from steps.combo_pick(d, p.curve, list(cv).index(key))
        yield 5000
    yield d.say("点“播放”，机构按算出的运动动一圈")
    yield from click_w(d, p.play)
    yield 5000
    yield d.say("要留档就点“写计算报告…”：Word 报告，有结论、模型、核查和曲线")
    steps.show(p.report_btn)
    p2 = d.center(p.report_btn)
    yield d.move(p2, 800)
    d.ring(p2)
    yield 3000


def main():
    d = Director()
    d.run(script(d))


boot(main)
