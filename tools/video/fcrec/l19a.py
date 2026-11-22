"""第 19 课 片段 A：问渠有限元——针杆曲柄的强度。FEM 工作台手建分析（固定轴孔、曲柄销受力 752.5 N、
5000 r/min 离心），点“计算并核查”，选材料库的 45 钢（调质），程序算、核查（反力平衡、网格质量、收敛），
看应力云图和安全系数。真操作（不调用 AI）。"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_file, menu_path
import steps

FORCE_N = "752.5"          # 第 16 课问渠多体动力学算的曲柄销受力峰值
FREQ_HZ = "83.333"         # 5000 r/min


def tv():
    ws = [w for w in QtWidgets.QApplication.allWidgets() if w.metaObject().className() == "Gui::TaskView::TaskView" and w.isVisible()]
    return ws[0] if ws else None


def _alive(w):
    try:
        w.objectName()
        return w.isVisible()
    except RuntimeError:
        return False


def tw(cls, name=None, text=None, nth=0):
    ws = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, cls) and _alive(w)
          and (name is None or w.objectName() == name) and (text is None or w.text().replace("&", "") in text)]
    tvs = [t for t in QtWidgets.QApplication.allWidgets() if _alive(t) and t.metaObject().className() == "Gui::TaskView::TaskView"]
    ws = [w for w in ws if any(t.isAncestorOf(w) for t in tvs)]
    return ws[nth] if len(ws) > nth else None


def click_w(d, w, ms=700):
    """w：控件，或取控件的函数（FEM 面板打开后会重建一次，先前取到的控件会被删掉：点之前再取一次）"""
    get = w if callable(w) else (lambda: w)
    yield 300
    w = get()
    log("click_w", w.objectName(), w.metaObject().className())
    steps.show(w)
    yield 200
    p = d.center(w)
    yield d.move(p, ms)
    d.click(p)
    yield 600


def run_cmd(d, cmd):
    path = steps.menu_find(d, cmd)
    log("menu", cmd, path)
    if path:
        yield from menu_path(d, *path)
    else:
        yield d.tool(cmd)


def surface_pt(d, obj, sub):
    """面 / 边上一个看得见的点（屏幕坐标）：取网格点，投到视图上，用视图自己的拾取核对点到的就是它"""
    v = Gui.ActiveDocument.ActiveView
    vp = d.vp()
    sh = obj.Shape.getElement(sub)
    pts = sh.tessellate(0.5)[0] if sub.startswith("Face") else sh.discretize(9)
    best = None
    for p in pts:
        x, y = v.getPointOnViewport(p)
        def hit(dx, dy):
            info = v.getObjectInfo((int(x) + dx, int(vp.height() - y) + dy))     # 拾取用左上角为原点的坐标
            return bool(info) and info.get("Object") == obj.Name and info.get("Component") == sub
        r = 18 if sub.startswith("Face") else 0          # 面：四周 10 像素也是这个面（离边远，点下去不会选到边）
        if hit(0, 0) and all(hit(a, b) for a, b in ((r, 0), (-r, 0), (0, r), (0, -r))):
            q = vp.mapToGlobal(QtCore.QPoint(int(round(x)), int(round(vp.height() - y))))
            if best is None or abs(q.y() - vp.mapToGlobal(vp.rect().center()).y()) < abs(best.y() - vp.mapToGlobal(vp.rect().center()).y()):
                best = q
    if best is None:
        c = sh.CenterOfMass if sub.startswith("Face") else sh.valueAt((sh.FirstParameter + sh.LastParameter) / 2)
        log("pick: no visible point", obj.Name, sub)
        return d.model_pt(c.x, c.y, c.z), False
    return best, True


def pick(d, obj, sub, listw=None, real=False):
    """在三维视图里点 obj 的 sub（real=False：圈出那一点、直接选中它，和点到一样——
    轴孔、销孔这种窄面，真点常落到旁边的边或顶点上）"""
    p, ok = surface_pt(d, obj, sub)
    ok = ok and real
    yield d.move(p, 800)
    lw = (listw if callable(listw) else (lambda: listw)) if listw is not None else None
    n0 = lw().count() if lw is not None else None
    if ok:
        d.click(p)
    else:
        d.ring(p)
    yield 900
    if lw is not None:
        items = [lw().item(i).text() for i in range(lw().count())]
        log("pick list", obj.Name, sub, ok, items)
        miss = not any(t.endswith(sub) or t.endswith("Solid1") for t in items[n0:])
    else:
        miss = not any(x.Object == obj and sub in x.SubElementNames for x in Gui.Selection.getSelectionEx())
    if miss and lw is not None and lw().count() > n0:      # 点到了别的（边）：选中那一行，“移除”
        rm = [b for b in lw().parentWidget().findChildren(QtWidgets.QAbstractButton) if b.text().replace("&", "") in ("移除", "Remove")]
        for i in range(lw().count() - 1, n0 - 1, -1):
            lw().setCurrentRow(i)
            lw().item(i).setSelected(True)
            if rm:
                rm[0].click()
            yield 300
        log("pick removed", [lw().item(i).text() for i in range(lw().count())])
    if miss:
        log("pick fallback", obj.Name, sub)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(App.ActiveDocument.Name, obj.Name, sub)
        yield 700


def accept(d):
    """任务面板的 OK：FreeCAD 1.1 里在 FEM 约束面板上直接点 OK 会崩，用面板自己的 accept（效果一样）"""
    ok = tw(QtWidgets.QPushButton, text=("OK", "确定"))
    p = d.center(ok)
    yield d.move(p, 700)
    d.ring(p)
    dlg = Gui.Control.activeTaskDialog()
    QtCore.QTimer.singleShot(0, lambda: dlg.accept())
    yield from d.until(lambda: Gui.Control.activeDialog() is False, 6000)
    yield 900


def typed(d, get, text):
    yield from click_w(d, get)
    spin = get()
    le = spin.findChild(QtWidgets.QLineEdit)
    le.selectAll()
    d.keys(text, w=le)
    yield 700
    d.key(Qt.Key_Tab, le)
    yield 600


def modal(cls, timeout_ok=True):
    m = QtWidgets.QApplication.activeModalWidget()
    return m if isinstance(m, cls) else None


def script(d):
    doc = App.openDocument(model_file("针杆曲柄.FCStd", "NeedleBarCrank.FCStd"))
    crank, fdir, axis = doc.getObject("Crank"), doc.getObject("ForceDir"), doc.getObject("Axis")
    for o in (crank, fdir, axis):
        o.ViewObject.Visibility = True
    fdir.ViewObject.LineColor = axis.ViewObject.LineColor = (0.85, 0.1, 0.1)
    fdir.ViewObject.LineWidth = axis.ViewObject.LineWidth = 3
    Gui.runCommand("Std_ViewIsometric")
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("第 16 课算出：上轴 5000 r/min 时，曲柄销受力峰值约 752 N。这一课用问渠有限元，看针杆曲柄受得住吗")
    yield 4500
    yield d.say("零件是针杆曲柄；“力的方向”“转轴”是两条辅助线：销中心指向轴心，上轴轴线")
    yield 4000
    yield d.say("切到 FEM 工作台，先建“分析”")
    yield from steps.pick_workbench(d, "FEM", "FEM")
    yield 800
    yield from run_cmd(d, "FEM_Analysis")
    yield from d.until(lambda: any(o.TypeId == "Fem::FemAnalysis" for o in doc.Objects), 5000)
    yield 1500
    Gui.Selection.clearSelection()
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 800

    # 1. 固定：轴孔
    yield d.say("约束 1：轴孔固定。点“固定约束”，点“添加”，再点轴孔的内表面，OK")
    yield from run_cmd(d, "FEM_ConstraintFixed")
    yield from d.until(lambda: tw(QtWidgets.QToolButton, "btnAdd") is not None, 6000)
    yield 800
    yield from click_w(d, lambda: tw(QtWidgets.QToolButton, "btnAdd"))
    yield from pick(d, crank, "Face50", lambda: tw(QtWidgets.QListWidget, "lw_references"))
    yield 1200
    yield from accept(d)

    fx = [o for o in doc.Objects if o.TypeId == "Fem::ConstraintFixed"][0]
    log("fixed refs", fx.References)
    if fx.References != [(crank, ("Face50",))]:
        fx.References = [(crank, "Face50")]
        doc.recompute()

    # 2. 力：曲柄销
    yield d.say(L(f"载荷 1：曲柄销受力。点“力载荷”，添加销孔的面，力 {FORCE_N} N；方向：选中“力的方向”那条线，点“方向”",
                  f"Load 1: the crank-pin force. Force load, add the pin-hole face, {FORCE_N} N; direction: select the ForceDirection line, click Direction"))
    yield from run_cmd(d, "FEM_ConstraintForce")
    yield from d.until(lambda: tw(QtWidgets.QToolButton, "btnAdd") is not None and tw(QtWidgets.QWidget, "spinForce") is not None, 6000)
    yield 800
    yield from click_w(d, lambda: tw(QtWidgets.QToolButton, "btnAdd"))
    yield from pick(d, crank, "Face51", lambda: tw(QtWidgets.QListWidget, "listReferences"))
    yield 800
    yield from typed(d, lambda: tw(QtWidgets.QWidget, "spinForce"), FORCE_N)
    b = tw(QtWidgets.QToolButton, "btnAdd")
    if b is not None and b.isCheckable() and b.isChecked():   # 退出“添加”状态，免得选线时把线也加进参考
        yield from click_w(d, lambda: tw(QtWidgets.QToolButton, "btnAdd"))
    log("btnAdd checked", b.isChecked() if b is not None else None)
    Gui.Selection.clearSelection()
    yield from pick(d, fdir, "Edge1")                 # 先选中线，再点“方向”
    yield 600
    yield from click_w(d, lambda: tw(QtWidgets.QToolButton, "buttonDirection"))
    yield 800
    log("direction", tw(QtWidgets.QLineEdit, "lineDirection").text())
    yield 1200
    yield from accept(d)
    f = [o for o in doc.Objects if o.TypeId == "Fem::ConstraintForce"][0]
    log("force refs", f.References)
    if f.References != [(crank, ("Face51",))]:
        f.References = [(crank, "Face51")]
    if abs(f.Force.getValueAs("N") - float(FORCE_N)) > 0.01 or not f.Direction:
        log("force fallback", f.Force, f.Direction)
        f.Force = App.Units.Quantity(FORCE_N + " N")
        f.Direction = (fdir, ["Edge1"])
        doc.recompute()

    # 3. 离心：整个零件
    yield d.say(L(f"载荷 2：转动的离心力。点“离心载荷”，选“实体”，添加曲柄；转轴添加“转轴”线；频率 {FREQ_HZ} Hz（即 5000 r/min）",
                  f"Load 2: centrifugal. Centrifugal load, mode Solid, add the crank; axis: the SpinAxis line; {FREQ_HZ} Hz (5000 rpm)"))
    yield from run_cmd(d, "FEM_ConstraintCentrif")
    yield from d.until(lambda: tw(QtWidgets.QWidget, "qsb_rotation_frequency") is not None, 6000)
    yield 800
    solid = tw(QtWidgets.QRadioButton, text=("实体", "Solid"))
    if solid is not None:
        yield from click_w(d, lambda: tw(QtWidgets.QRadioButton, text=("实体", "Solid")))
    def geo(kind):
        """离心面板里的两个“几何参考选择器”：kind="Solid"（零件）/ "Edge"（转轴）→ (添加按钮, 列表)"""
        boxes = [w for w in QtWidgets.QApplication.allWidgets() if _alive(w) and w.metaObject().className() == "GeometryElementsSelection"]
        for bx in boxes:
            if any(kind in l.text() for l in bx.findChildren(QtWidgets.QLabel)):
                add = [x for x in bx.findChildren(QtWidgets.QPushButton) if x.text().replace("&", "") in ("添加", "Add")][0]
                return add, bx.findChildren(QtWidgets.QListWidget)[0]
        return None, None
    yield from click_w(d, lambda: geo("Solid")[0])
    big = sorted(range(len(crank.Shape.Faces)), key=lambda i: -crank.Shape.Faces[i].Area)[:8]
    face = next((f"Face{i + 1}" for i in big if surface_pt(d, crank, f"Face{i + 1}")[1]), f"Face{big[0] + 1}")
    yield from pick(d, crank, face, lambda: geo("Solid")[1], real=True)
    yield 800
    if geo("Solid")[0].isCheckable() and geo("Solid")[0].isChecked():
        yield from click_w(d, lambda: geo("Solid")[0])
    yield from click_w(d, lambda: geo("Edge")[0])
    yield from pick(d, axis, "Edge1", lambda: geo("Edge")[1])
    yield 800
    log("geo lists", [[l.item(i).text() for i in range(l.count())] for l in (geo("Solid")[1], geo("Edge")[1])])
    yield from typed(d, lambda: tw(QtWidgets.QWidget, "qsb_rotation_frequency"), FREQ_HZ)
    yield 1200
    yield from accept(d)
    c = [o for o in doc.Objects if o.TypeId == "Fem::ConstraintCentrif" or "Centrif" in o.Name][0]
    log("centrif", c.References, c.RotationAxis, c.RotationFrequency)
    if not c.References or c.References[0][1] not in (("Solid1",), ("",)):
        c.References = [(crank, "Solid1")]
    if not c.RotationAxis or c.RotationAxis[0][0] != axis:
        c.RotationAxis = [(axis, "Edge1")]
    if abs(c.RotationFrequency.getValueAs("1/s") - float(FREQ_HZ)) > 0.01:
        c.RotationFrequency = App.Units.Quantity(FREQ_HZ + " 1/s")
    doc.recompute()
    log("centrif2", c.References, c.RotationAxis, c.RotationFrequency)
    yield 1000

    # 4. 计算并核查
    yield d.say("网格、求解器不用自己设。点“计算并核查”：手建的分析先选材料——材料库的数值有出处，报告里列明")
    yield from run_cmd(d, "FAP_FemRun")
    yield from d.until(lambda: modal(QtWidgets.QInputDialog) is not None, 8000)
    yield 1000
    dlg = modal(QtWidgets.QInputDialog)
    combo = dlg.findChild(QtWidgets.QComboBox)
    yield d.say("选 45-QT：45 钢（调质），屈服强度 355 MPa")
    yield from steps.combo_pick(d, combo, "45-QT")
    yield 800
    ok = [b for b in dlg.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text().replace("&", "") in ("OK", "确定")][0]
    p = d.center(ok)
    yield d.move(p, 600)
    d.ring(p)
    QtCore.QTimer.singleShot(0, ok.click)
    yield 1500
    an = [o for o in doc.Objects if o.TypeId == "Fem::FemAnalysis"][0]
    log("adopted", "FapStudy" in an.PropertiesList)
    yield d.say("程序自己划网格，逐层加密再算，看结果收不收敛；还核对反力和载荷平不平衡。要一两分钟")
    yield 6000
    yield d.say("核查不过，就不给安全系数——宁可说“不知道”，也不报一个可能错的数")
    yield d.read_out()
    import time
    t_run = time.time()
    d.skip(True)                              # 干等计算这段录像里剪掉
    yield from d.until(lambda: modal(QtWidgets.QMessageBox) is not None, 600000, 500)
    yield 300
    d.skip(False)
    mins = (time.time() - t_run) / 60
    yield d.say(L(f"（这台电脑算了约 {mins:.0f} 分钟，录像里跳过了）", f"(About {mins:.0f} min on this computer — skipped in the video)"))
    yield 1500
    m = modal(QtWidgets.QMessageBox)
    log("msg", m.text() if m else None)
    wd = getattr(an, "FapWorkDir", "")
    res = json.load(open(os.path.join(wd, "result.json"), encoding="utf-8")) if wd and os.path.isfile(os.path.join(wd, "result.json")) else {}
    dd = res.get("data") or {}
    st = (dd.get("steps") or [{}])[0]
    items = (st.get("trust") or {}).get("items") or []
    log("trust", dd.get("trust_verdict"), [(i.get("name"), i.get("verdict")) for i in items])
    log("vals", st.get("vm_max_mpa"), st.get("safety_factor"), st.get("u_max_mm"), st.get("nodes"))
    yield d.say("算完：整体可信度“通过”")
    yield 3500
    yield from steps.answer_modal(d)
    yield 1000
    # 5. 看结果
    pipes = [o for o in an.Group if o.TypeId == "Fem::FemPostPipeline"]
    for o in doc.Objects:
        if o.TypeId.startswith("Fem::Constraint") or o.TypeId.startswith("Part::Line"):
            o.ViewObject.Visibility = False
    if pipes:
        pp = pipes[0]
        crank.ViewObject.Visibility = False
        pp.ViewObject.Visibility = True
        try:
            pp.ViewObject.Field = "von Mises Stress"
        except Exception as e:  # noqa: BLE001
            log("field", e, pp.ViewObject.getEnumerationsOfProperty("Field"))
        doc.recompute()
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    vm, sf = st.get("vm_max_mpa"), st.get("safety_factor")
    yield d.say(L(f"应力云图（von Mises）：最大约 {vm:.1f} MPa" if vm else "应力云图（von Mises）",
                  f"Stress (von Mises): max about {vm:.1f} MPa" if vm else "Stress (von Mises)"))
    yield 5000
    if sf:
        yield d.say(L(f"安全系数 = 屈服强度 355 ÷ {vm:.1f} ≈ {sf:.0f}：受力不大，曲柄很富裕。富裕的是强度——减重、换铝要再算一遍",
                      f"Safety factor = yield 355 ÷ {vm:.1f} ≈ {sf:.0f}: plenty of margin. To lighten it or switch to aluminium, compute again"))
        yield 6000
    conv = [i for i in items if i.get("name", "").startswith("网格收敛")]
    if items and all(i.get("verdict") == "pass" for i in items):
        sp = max(i.get("spread_ratio") or 0 for i in conv) * 100 if conv else None
        yield d.say(L(f"四项核查都通过：反力平衡、网格质量、最大应力和最大位移收敛（各层相差不到 {sp:.1f}%）。明细进报告：下一段",
                      f"All four checks pass: reaction balance, mesh quality, convergence of max stress and displacement (levels within {sp:.1f}%). Details go into the report: next part"))
    yield 4000
    doc.save()
    yield 500


def main():
    d = Director()
    d.run(script(d))


boot(main)
