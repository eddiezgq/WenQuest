"""第 21 课 片段 B：零件库与企业库（AI Parts 工作台“零件库”“企业库”）。两次启动接成一段（cat_rec.py）：
WQ_PART=1：零件库里看公共库零件每个值的出处、复核状态 → 菜单“企业库”选文件夹（示范缝纫机企业，虚构）→ 提示重启后生效。
WQ_PART=2：重启后零件库里多了企业库的两个自制件 → 看上轴 LS-101（尺寸由代码从三维模型量出）、缺的数据 → 导出完整度报告 → 放入模型。
企业库文件夹：WQ_ENT（make_all.sh 从 freecad-ai-parts 的 examples/enterprise-lockstitch/library 拷出）。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui
from director import Director, boot, log, Qt, QtCore, QtWidgets, L, menu_path
import steps

PART = os.environ.get("WQ_PART", "1")
ENT = os.environ["WQ_ENT"]


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


def dock(d, name):
    for w in d.mw.findChildren(QtWidgets.QDockWidget):
        if w.objectName() == name:
            return w
    return None


def pick_row(d, br, text):
    for i in range(br.table.rowCount()):
        cells = " ".join(br.table.item(i, j).text() for j in range(br.table.columnCount()) if br.table.item(i, j))
        if text in cells:
            br.table.scrollToItem(br.table.item(i, 0))
            yield 300
            r = br.table.visualItemRect(br.table.item(i, 1 if br.table.columnCount() > 1 else 0))
            p = br.table.viewport().mapToGlobal(r.center())
            yield d.move(p, 700)
            d.click(p)
            br.table.selectRow(i)
            yield 1200
            return
    log("row not found", text)


def scroll(d, tb, frac, ms=4000):
    sb = tb.verticalScrollBar()
    end = int(sb.maximum() * frac)
    n = max(1, ms // 60)
    for k in range(n + 1):
        sb.setValue(sb.value() + (end - sb.value()) // max(1, n - k))
        yield 60


def open_browser(d):
    yield from steps.pick_workbench(d, "AI Parts", "AI Parts")
    yield 800
    yield from run_cmd(d, "FAP_Browser")
    yield from d.until(lambda: dock(d, "FapLibraryBrowser") is not None and dock(d, "FapLibraryBrowser").isVisible(), 6000)
    br = dock(d, "FapLibraryBrowser")
    for w in d.mw.findChildren(QtWidgets.QDockWidget):          # 零件库窗口占满左栏；顺带打开的“校验”窗口这一段用不上
        if w.objectName() in ("Model", "FapCheckPanel") and w.isVisible():
            w.hide()
    d.mw.resizeDocks([br], [760], Qt.Horizontal)
    yield 1500
    cp = dock(d, "FapCheckPanel")
    if cp is not None:
        cp.hide()
        d.mw.resizeDocks([br], [760], Qt.Horizontal)
    return br


def part1(d):
    App.newDocument(L("零件库", "Library"))
    yield 800
    yield d.say("零件从哪来？菜单“AI Parts → 零件库”")
    br = yield from open_browser(d)
    yield d.say("公共库里是真实厂商的零件：安川电机和驱动器、哈默纳科减速器、NSK 轴承、ROBOTIS 智能舵机。参数从厂商公开的规格书里抽出来")
    yield 5000
    yield from steps.combo_pick(d, br.category, br.category.itemText([k for k in range(br.category.count()) if br.category.itemData(k) == "reducer"][0]))
    yield 1000
    yield from pick_row(d, br, "CSF-25-100")
    log("detail", br.detail.toPlainText()[:600])
    yield d.say("选一个减速器：每个值后面写着出自哪份规格书、第几页，有没有人复核过。没有出处的值不进库")
    yield from scroll(d, br.detail, 0.45, 6000)
    yield 4000
    yield d.say("企业自己的零件——自制件、公共库里没有的外购件——放在企业库：一个文件夹，数据只存在企业自己那边")
    yield 4000
    yield d.say("菜单“AI Parts → 企业库”，选文件夹（这里是示范缝纫机企业，虚构的）")
    yield from run_cmd(d, "FAP_Enterprise")
    yield from d.until(lambda: isinstance(QtWidgets.QApplication.activeModalWidget(), QtWidgets.QFileDialog), 6000)
    dlg = QtWidgets.QApplication.activeModalWidget()
    dlg.setDirectory(os.path.dirname(ENT))
    yield 1200
    e = dlg.findChild(QtWidgets.QLineEdit, "fileNameEdit")
    p = d.center(e)
    yield d.move(p, 600)
    d.click(p)
    e.selectAll()
    d.keys(os.path.basename(ENT), w=e)
    yield 1200
    ok = [b for b in dlg.findChildren(QtWidgets.QPushButton) if b.isVisible() and b.isEnabled()
          and b.text().replace("&", "").startswith(("选择", "Choose", "打开", "Open"))]
    log("dir buttons", [b.text() for b in dlg.findChildren(QtWidgets.QPushButton) if b.isVisible()])
    p = d.center(ok[0])
    yield d.move(p, 600)
    d.ring(p)
    QtCore.QTimer.singleShot(0, ok[0].click)
    yield 2000
    m = QtWidgets.QApplication.activeModalWidget()
    log("after dir", m and m.windowTitle(), m and [l.text() for l in m.findChildren(QtWidgets.QLabel)][:3])
    yield d.say("提示：重启 FreeCAD 后生效")
    yield 2500
    yield from steps.answer_modal(d)
    yield 1500


def part2(d):
    App.newDocument(L("上轴", "UpperShaft"))
    yield 800
    yield d.say("重启以后，再打开零件库")
    br = yield from open_browser(d)
    log("header", br.header.text())
    import re
    h = br.header.text()
    n_ent = re.search(r"(\d+) (?:个组件|components)", h).group(1)
    mp = re.search(r"真实厂商组件 (\d+) 个|(\d+) real vendor components", h)
    n_pub = (mp.group(1) or mp.group(2)) if mp else "?"
    yield d.say(L(f"顶上写着：企业库 {n_ent} 个组件，叠加在公共库 {n_pub} 个组件上面",
                  f"The header says: company library, {n_ent} components, layered over the public library's {n_pub}"))
    yield 4500
    yield from click_w(d, br.text)
    d.keys("LS", w=br.text)
    yield 1500
    yield from pick_row(d, br, "LS-101")
    log("detail", br.detail.toPlainText()[:300])
    yield d.say("平缝机上轴 LS-101，自制件。这两个自制件是 AI 帮企业建的：AI 读物料表、提议零件类型，人确认；五段直径、长度由代码从三维模型量出来")
    yield from scroll(d, br.detail, 0.5, 7000)
    yield 3000
    yield d.say("量出来的数“未复核”——要人看过才算复核过")
    yield 3000
    yield d.say("最下面“缺的数据”：这个零件校验要用的数据是齐的；缺了会一条条列出来")
    yield from scroll(d, br.detail, 1.0, 2500)
    yield 4000
    yield d.say("全库一起看：点“完整度报告…”，导出 Excel——每个零件缺什么、缺了哪些校验会“待确认”、先补哪个")
    b = br.report_button
    p = d.center(b)
    yield d.move(p, 700)
    d.ring(p)
    QtCore.QTimer.singleShot(0, b.click)                        # 会弹出保存对话框：不能在剧本里同步点
    yield 800
    yield from steps.file_dialog(d, L("零件库完整度.xlsx", "library-completeness.xlsx"))
    yield 1500
    log("report", br.status.text())
    yield d.say("把上轴放进模型：点“放入布局”")
    yield from click_w(d, br.place_button)
    yield from d.until(lambda: br.place_button.isEnabled(), 30000)
    yield 1500
    Gui.SendMsgToActiveView("ViewFit")
    yield 4000


def main():
    d = Director()
    d.run(part1(d) if PART == "1" else part2(d))


boot(main)
