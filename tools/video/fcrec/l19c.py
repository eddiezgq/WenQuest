"""第 19 课 片段 C：一句话起草（AI）。问渠有限元入门例子 02——机器人肩关节空心轴 RJ-201：
选中零件 → 求解 → 一句话起草（AI）→ 写一句话 → 起草：AI 起草约束和载荷、程序逐项核对、列出追问 →
工程师看追问、勾“已处理”、写确认人 → 确认算例 → 计算并核查 → 看结论。
AI 的回复是真实模型的录制回放（FAP_LLM_REPLAY=问渠有限元的 tests/recordings/fea_draft；画面上标明“回放”），
其余全是真操作。录制：FAP_LLM_REPLAY、FAP_AI_PROVIDER=claude 由 make_all.sh 设。"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
import Part
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, model_dir, menu_path, EN
import steps

STATEMENT = "肩关节空心轴 RJ-201，45 钢调质。Ø70 法兰那一端的端面固定，在 Ø42.75 花键段上加峰值扭矩 92.5 N·m。"
STEP = os.path.join(os.environ.get("WQ_REC", "."), "rj201", "RJ-201.step")


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


def modal(cls):
    m = QtWidgets.QApplication.activeModalWidget()
    return m if isinstance(m, cls) else None


def script(d):
    # 零件：问渠有限元入门例子 02 的 STEP（录制时用的就是这个文件，回放才对得上）
    doc = App.newDocument(L("空心轴RJ201", "HollowShaftRJ201"))
    doc.saveAs(os.path.join(model_dir(), L("空心轴RJ-201", "HollowShaftRJ-201") + ".FCStd"))
    s = Part.Shape()
    s.read(STEP)
    part = doc.addObject("Part::Feature", "RJ201")
    part.Shape = s
    part.Label = L("RJ-201 肩关节空心轴", "RJ-201 shoulder hollow shaft")
    part.addProperty("App::PropertyString", "FapStepPath", "Fap", "")
    part.FapStepPath = STEP
    doc.recompute()
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    yield d.say("最后看 AI 怎么帮忙：一句话说清材料、支承、载荷，AI 起草算例。换一个零件——问渠有限元入门例子里的机器人肩关节空心轴")
    yield 3000
    yield from steps.pick_workbench(d, "FEM", "FEM")
    yield 800
    p = d.tree_item(part.Label)
    yield d.move(p, 700)
    d.click(p)
    yield 700
    yield d.say("选中零件，菜单“求解 → 一句话起草（AI）”")
    yield from run_cmd(d, "FAP_FemDraft")
    from freecad_addon.gui import fem_commands
    yield from d.until(lambda: fem_commands._LAST_PANEL is not None and fem_commands._LAST_PANEL.form.isVisible(), 6000)
    yield 800
    pn = fem_commands._LAST_PANEL
    yield d.say(L("写一句话：零件、材料、怎么固定、受什么载荷", "Write one sentence: part, material, how it is held, what load (in Chinese here — the recorded AI reply is for this sentence)"))
    yield from click_w(d, pn.text)
    for i in range(0, len(STATEMENT) + 1, 2):                 # 逐字打出来（输入法打汉字，录屏里用逐段写入代替）
        pn.text.setPlainText(STATEMENT[:i])
        yield 70
    pn.text.setPlainText(STATEMENT)
    yield 1200
    yield d.say("点“起草”。这一段 AI 的回复是真实模型的录制回放，面板上会标明“回放”")
    yield from click_w(d, pn.go)
    yield from d.until(lambda: pn.analysis is not None or pn.info.toPlainText().startswith(("没有起草", "No draft")), 120000)
    yield 1200
    info = pn.info.toPlainText()
    log("info", info)
    an = pn.analysis
    if an is None:
        return
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 800
    kinds = [o.TypeId for o in an.Group]
    log("group", kinds)
    yield d.say("AI 起草、程序逐项核对：端面固定、花键段加扭矩、材料 45 钢调质，都放进了模型树的“分析”，三维视图里能看到")
    yield 6000
    nq = sum(1 for x in info.splitlines() if x.startswith(("追问", "Question")))
    yield d.say(L(f"AI 拿不准的列成追问（这次 {nq} 条）：工程师逐条看，在 FEM 里改好，或者判断不需要",
                  f"What the AI is unsure of is listed as questions ({nq} this time): the engineer reads each, fixes it in FEM or decides it is not needed"))
    pn.info.verticalScrollBar().setValue(pn.info.verticalScrollBar().maximum())
    yield 6500
    yield d.say("扭矩的转向对线弹性应力的大小没有影响，可以。勾“追问都已处理”，写确认人，点“确认算例”")
    yield from click_w(d, pn.handled)
    if not pn.handled.isChecked():
        pn.handled.setChecked(True)
    yield from click_w(d, pn.by)
    d.keys(L("张工", "J. Smith"), w=pn.by)
    yield 700
    yield from click_w(d, pn.ok)
    yield 1500
    if pn.ok.isEnabled():                         # 没点上（确认成功后按钮会变灰）：再按一次
        log("confirm fallback", pn.by.text(), pn.handled.isChecked())
        if not pn.by.text().strip():
            pn.by.setText(L("张工", "J. Smith"))
        pn.ok.click()
        yield 1200
    log("confirmed", pn.info.toPlainText().splitlines()[-1])
    yield d.say("确认人和时间记进算例；没确认的 AI 草稿不能算——程序不替人签字")
    yield 4500
    close = [b for b in QtWidgets.QApplication.allWidgets() if isinstance(b, QtWidgets.QPushButton) and b.isVisible()
             and b.text().replace("&", "") in ("关闭", "Close")]
    if close:
        yield from click_w(d, close[0])
    else:
        Gui.Control.closeDialog()
    yield 800
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(an)
    yield d.say("接着和前面一样：计算并核查")
    yield from run_cmd(d, "FAP_FemRun")
    yield d.read_out()
    import time
    t_run = time.time()
    d.skip(True)
    yield from d.until(lambda: modal(QtWidgets.QMessageBox) is not None, 600000, 500)
    yield 300
    d.skip(False)
    yield d.say(L(f"（这台电脑算了约 {(time.time() - t_run) / 60:.0f} 分钟，录像里跳过了）", f"(About {(time.time() - t_run) / 60:.0f} min on this computer — skipped in the video)"))
    yield 1500
    m = modal(QtWidgets.QMessageBox)
    log("msg", m.text() if m else None)
    wd = getattr(an, "FapWorkDir", "")
    rp = os.path.join(wd, "result.json") if wd else ""
    res = json.load(open(rp, encoding="utf-8")) if rp and os.path.isfile(rp) else {}
    dd = res.get("data") or {}
    st = (dd.get("steps") or [{}])[0]
    items = (st.get("trust") or {}).get("items") or []
    verdict = dd.get("trust_verdict")
    log("trust", verdict, [(i.get("name"), i.get("verdict"), i.get("text")) for i in items])
    log("vals", st.get("vm_max_mpa"), st.get("safety_factor"))
    yield 2500
    yield from steps.answer_modal(d)
    yield 800
    for o in doc.Objects:
        if o.TypeId == "Part::Feature" or o.TypeId.startswith("Fem::Constraint") or "Torque" in o.Name:
            if getattr(o, "ViewObject", None) is not None:
                o.ViewObject.Visibility = False
    pipes = [o for o in an.Group if o.TypeId == "Fem::FemPostPipeline"]
    if pipes:
        pipes[0].ViewObject.Visibility = True
        try:
            pipes[0].ViewObject.Field = "von Mises Stress"
        except Exception as e:  # noqa: BLE001
            log("field", e)
        doc.recompute()
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    bad = [i for i in items if i.get("verdict") != "pass"]
    if verdict == "pass":
        yield d.say(L(f"四项核查都通过：最大应力约 {st.get('vm_max_mpa'):.0f} MPa，安全系数约 {st.get('safety_factor'):.1f}",
                      f"All checks pass: max stress about {st.get('vm_max_mpa'):.0f} MPa, safety factor about {st.get('safety_factor'):.1f}"))
    else:
        names = "、".join(i.get("name", "") for i in bad)
        log("bad", names)
        yield d.say(L(f"这次整体可信度“{ {'fail': '不通过', 'unknown': '未知'}.get(verdict, '未知') }”：{names}没过，安全系数就不给",
                      "This time the overall trust is not “pass”: a check did not pass, so no safety factor is given"))
        yield 5000
        why = "；".join(i.get("text", "") for i in bad)
        yield d.say(L(f"程序说的原因：{why}。云图照样能看——台阶的尖角处加圆角，或者看离开尖角处的应力，再算",
                      "The program's reason: max stress keeps rising as the mesh is refined — a suspected singularity (sharp corner), so that value is not a design basis. The plot is still there: add a fillet at the step, or read the stress away from the corner, and compute again"))
    yield 5000
    yield d.say("这就是问渠有限元的分工：AI 只起草，程序核对、计算、核查，人确认、签字")
    yield 4000


def main():
    d = Director()
    d.run(script(d))


boot(main)
