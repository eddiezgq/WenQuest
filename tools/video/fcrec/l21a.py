"""第 21 课 片段 A：AI 选零件与校验（AI Parts 工作台“选型”“校验”“BOM”三个窗口）。
一句话需求 → AI 只填表单（每项注明原话依据）→ 代码在真实厂商库（安川、哈默纳科、NSK）里查方案、逐条校验 →
找不到就说找不到；缺数据判“待确认”，不算通过 → 放入布局 → 校验窗口逐条看 → BOM。
一句话解析用 engine 自带的真实模型录制（tests/recordings/requirement，回放、不联网），其余全是真操作。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L
import steps

STATEMENT = "六轴机械臂第 2 关节：输出连续扭矩 25 N·m、峰值 50 N·m，输出转速 30 rpm，220 V 单相供电，EtherCAT 总线"


def run_cmd(d, cmd):
    path = steps.menu_find(d, cmd)
    log("menu", cmd, path)
    yield from __import__("director").menu_path(d, *path)


def click_w(d, w, ms=700):
    steps.show(w)
    yield 200
    p = d.center(w)
    yield d.move(p, ms)
    d.click(p)
    yield 600


def dock(d, name):
    for w in d.mw.findChildren(QtWidgets.QDockWidget):
        if w.objectName() == name:
            return w
    return None


def find(d, sp):
    yield from click_w(d, sp.find_button)
    yield from d.until(lambda: sp.find_button.isEnabled(), 60000)
    yield 1200
    log("find", sp.status.text(), [(r.rank, r.status) for r in sp.rows])


def script(d):
    App.newDocument(L("关节2", "Joint2"))
    yield 1000
    yield d.say("最后一课：问渠的 AI 工作台。三条规矩先说清：AI 只起草，改模型、进企业库都要人点确认；能不能用由代码校验，结果是通过、不通过或待确认——缺数据是待确认，不算通过；每次 AI 运行都留记录")
    yield 9000
    log("H0", d.mw.geometry().height())
    yield from steps.pick_workbench(d, "AI Parts", "AI Parts")
    yield 800
    log("H1", d.mw.geometry().height())
    for w in d.mw.findChildren(QtWidgets.QDockWidget):          # 选型窗口很高：先把左边的模型树收起来，让它占满左栏
        if w.objectName() in ("Combo View", "Model", "Tree view", "Property view") and w.isVisible():
            w.hide()
            log("hid", w.objectName())
    for tb in d.mw.findChildren(QtWidgets.QToolBar):            # 第二、三行工具栏也收起（菜单里都有），腾出高度
        if tb.isVisible() and tb.mapTo(d.mw, QtCore.QPoint(0, 0)).y() > 50:
            tb.hide()
    yield d.say("菜单“AI Parts → 选型”")
    yield from run_cmd(d, "FAP_Selection")
    yield from d.until(lambda: dock(d, "FapSelectionPanel") is not None and dock(d, "FapSelectionPanel").isVisible(), 6000)
    sp = dock(d, "FapSelectionPanel")
    log("H2", d.mw.geometry().height(), [(w.objectName(), w.isVisible(), w.minimumSizeHint().height()) for w in d.mw.findChildren(QtWidgets.QDockWidget)])
    cp0 = dock(d, "FapCheckPanel")                             # 选型会顺带打开“校验”窗口：先收起，后面讲到再开
    if cp0 is not None:
        log("check min", cp0.widget().minimumSizeHint())
        cp0.hide()
    d.mw.showNormal()
    d.mw.showMaximized()
    sp.sentence.setMaximumHeight(50)                         # 窗口里的控件最小高度加起来超过 900 像素的屏幕：压一压
    sp.table.setMinimumHeight(56)
    sp.detail.setMinimumHeight(56)
    for c in (sp.table, sp.detail):
        c.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
    for w in (sp.find_button, sp.table, sp.detail, sp.place_button, sp.status):
        log("geom", type(w).__name__, w.mapToGlobal(QtCore.QPoint(0, 0)), w.height())
    from engine.requirement_parse import RecordedClient, RECORDINGS_DIR
    sp._client_factory = lambda: RecordedClient(RECORDINGS_DIR)        # 真实模型的录制回放（不联网）
    d.mw.resizeDocks([sp], [560], Qt.Horizontal)
    yield 1200
    yield d.say("一句话写需求：机械臂第 2 关节，连续 25 N·m、峰值 50 N·m，30 rpm，220 V 单相，EtherCAT 总线")
    yield from click_w(d, sp.sentence)
    for i in range(0, len(STATEMENT) + 1, 2):
        sp.sentence.setPlainText(STATEMENT[:i])
        yield 70
    sp.sentence.setPlainText(STATEMENT)
    yield 1200
    yield d.say("点“解析”。这一步 AI 的回答是真实模型的录制回放（不联网）")
    yield from click_w(d, sp.parse_button)
    yield from d.until(lambda: not sp.parsing, 30000)
    yield 1500
    log("parse", sp.parse_note.text())
    for w in (sp.find_button, sp.table, sp.detail, sp.place_button, sp.status):
        log("geom2", type(w).__name__, w.mapToGlobal(QtCore.QPoint(0, 0)).y(), w.height())
    d.mw.showMaximized()
    log("mw", d.mw.geometry(), d.mw.frameGeometry(), "dock", sp.geometry(), "min", sp.widget().minimumSizeHint(), [ (type(c).__name__, c.minimumSizeHint().height()) for c in sp.widget().children() if isinstance(c, QtWidgets.QWidget)])
    yield d.say("AI 只做一件事：把原话里的数填进下面的表，每一项都标出原话依据；原话没说的（安全系数）按默认值，也写明了")
    yield 7000
    yield d.say("表是人核对的。核对完，点“查找方案”——查找和校验全是代码做的，不经过 AI")
    yield 2500
    sp.parse_note.hide()                                     # 依据讲完了：收起，给方案表和说明腾地方
    yield 500
    if sp.include_unknown.isChecked():
        yield from click_w(d, sp.include_unknown)
        sp.include_unknown.setChecked(False)
    yield from find(d, sp)
    yield d.say("没有方案。库里是真实厂商的零件（安川电机和驱动器、哈默纳科减速器、NSK 轴承），这几款驱动器的规格书写的是三相输入，单相 220 V 用不了")
    yield 7000
    yield d.say("找不到就说找不到，不凑。假设车间有三相 200 V 电源：改两格再查")
    yield from steps.type_into(d, sp.inputs["voltage_v"], "200")
    yield from steps.type_into(d, sp.inputs["phases"], "3")
    yield from find(d, sp)
    yield d.say("还是没有“确定能用”的。勾上“包含待确认的方案”，再查")
    yield 2500
    yield from click_w(d, sp.include_unknown)
    sp.include_unknown.setChecked(True)
    yield from find(d, sp)
    yield d.say(f"{len(sp.rows)} 个方案，结论都是“待确认”")
    yield 3000
    sb = sp.detail.verticalScrollBar()
    yield d.say("看说明：电机和减速器之间的法兰，库里缺分度圆直径、孔数这些数据，代码判不了能不能装——判“待确认”，不算通过")
    for v in range(0, sb.maximum() // 3, 12):
        sb.setValue(v)
        yield 60
    yield 6000
    sb.setValue(0)
    yield d.say("把方案 1 放进模型：点“放入布局”")
    yield from click_w(d, sp.place_button)
    yield from d.until(lambda: sp.find_button.isEnabled(), 60000)
    yield 1500
    Gui.SendMsgToActiveView("ViewFit")
    yield 1500
    log("placed", sp.status.text())
    yield d.say("电机、减速器、驱动器按端口装好了。菜单“AI Parts → 校验”")
    yield from run_cmd(d, "FAP_Checks")
    yield from d.until(lambda: dock(d, "FapCheckPanel") is not None and dock(d, "FapCheckPanel").isVisible(), 6000)
    cp = dock(d, "FapCheckPanel")
    for e in cp.inputs.values():          # 校验窗口的需求栏只补空格：第一次查找时填的 220 V / 单相会留着（AI 工作台的显示问题，0.3.4 修）
        e.setText("")
    cp._show_requirement()
    d.mw.resizeDocks([cp], [520], Qt.Horizontal)
    yield 1500
    tb = [t for t in cp.findChildren(QtWidgets.QTextBrowser) if t.isVisible()][0]
    log("checks", tb.toPlainText()[:400])
    yield d.say("C1 到 C11 逐条：接口、轴孔配合、扭矩、转速、供电、总线……每条写着用了什么数、和什么比")
    sb = tb.verticalScrollBar()
    for v in range(0, sb.maximum() + 1, 10):
        sb.setValue(v)
        yield 70
    yield 3000
    sb.setValue(0)
    yield d.say("C3 法兰配合是待确认。数据从哪补？“补数据”“导入规格书”：从厂商规格书里抽，抽出来的每个值要人复核，才算数")
    yield 8000
    sp.hide()
    cp.hide()
    yield 800
    yield d.say("菜单“AI Parts → BOM”：物料表，每个零件的厂商、型号、质量、数据来源，可以导出 CSV")
    yield from run_cmd(d, "FAP_Bom")
    yield 6000
    yield d.say("AI 只帮你把话变成表；选什么、能不能用，代码按数据说话，最后由人拍板")
    yield 4000


def main():
    d = Director()
    d.run(script(d))


boot(main)
