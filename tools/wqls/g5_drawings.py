"""第 138 轮 G5.1 第 8 步：机壳的工程图（数字工厂 drawings/sheet.py：由三维模型投影，国标图框、尺寸、公差、形位公差、粗糙度、技术要求）。

    python3 tools/wqls/g5_drawings.py <零件 STEP 目录> <毛坯 STEP 目录> <输出目录>

五张 A2：上件零件图、下件零件图、上件毛坯（铸件）图、下件毛坯图、上件卧加夹具 FX-HSG-U-20 总图（带明细栏）。
图上的数值与工艺规程（factory/digital/std/HSG-LS-*_process.yaml 的 characteristics）一致——程序从那里读。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIG = ROOT / "factory" / "digital"
sys.path[:0] = [str(DIG)]
import build123d as bd  # noqa: E402
from drawings.sheet import Sheet  # noqa: E402

DATE = "2026-11-11"
ZU = 200.0


def load(path):
    """STEP → 实体（剖视要求是 Solid，不是 Compound）"""
    so = bd.import_step(str(path)).solids()
    if len(so) == 1:
        return so[0]
    s = so[0]
    for x in so[1:]:
        s = s + x
    return s


def chars(item):
    p = yaml.safe_load((DIG / "std" / f"{item}_process.yaml").read_text(encoding="utf-8"))
    return {c["id"]: c for c in p["characteristics"]}


def spec(c, key):
    return c[key]["spec"].split("，")[0].split("（")[0]


COMMON_REQ = [
    "铸件材料 HT250（GB/T 9439），硬度 190–240 HBW；铸件尺寸公差 DCTG9、几何公差 GCTG7（GB/T 6414）。",
    "未注铸造圆角 R3–R5，拔模斜度 1°；铸件经两次去应力退火（铸后、粗加工后，550 ℃）。",
    "铸件不得有裂纹、冷隔；加工面上不得有气孔、砂眼、缩松；首件 X 光检查（部位见铸造工艺）。",
    "未注尺寸公差 GB/T 1804-m；未注几何公差 GB/T 1184-K。",
]


def save(sh: Sheet, out: Path, name: str):
    svg = out / f"{name}.svg"
    svg.write_text(sh.svg(), encoding="utf-8")
    pdf = out / f"{name}.pdf"
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(pdf), str(svg)], check=True)
    subprocess.run(["rsvg-convert", "-w", "2400", "-o", str(out / f"{name}.png"), str(svg)], check=True)
    return pdf


# ---------------------------------------------------------------- 上件零件图
def upper_part(step: Path) -> Sheet:
    c = chars("HSG-LS-U")
    s = load(step)
    sh = Sheet(size="A2", title="机壳上件", code="WQLS-HSG-U", material="HT250", scale_text="1:2", mass="15.7 kg", qty="1",
               designer="AI（问渠）", checker="", date=DATE, sheet_no="共 1 张 第 1 张")
    ref = (173.0, 0.0, 130.0)
    fv = sh.view([(s, 1)], "front", scale=0.5, ref3=ref, at=(215, 175), hidden=False, section=((0, 0, 0), (0, -1, 0)), name="A–A")
    lv = sh.view([(s, 1)], "left", scale=0.5, ref3=(0, 27, 130), at=(430, 175), hidden=False, name="")
    tv = sh.view([(s, 1)], "top", scale=0.5, ref3=ref, at=(215, 330), hidden=False, name="")
    # 中心线
    sh.centerline(fv, (-62, 0, ZU), (420, 0, ZU))
    sh.centerline(fv, (0, 0, 40), (0, 0, 200))
    sh.centerline(lv, (0, -60, ZU), (0, 70, ZU))
    # 尺寸
    sh.dim(fv, (37.5, 0, ZU), (380.0, 0, ZU), "342.5", offset=78)
    sh.dim(fv, (0.0, 0, 120), (37.5, 0, 120), "37.5", offset=-6)
    sh.dim(fv, (408.0, 0, 0.0), (408.0, 0, ZU), "200", offset=-22, orient="v", dev=(0.03, -0.03))
    sh.dim(fv, (37.5, 0, ZU), (408.0, 0, ZU), "370.5", offset=92)
    # 直径与形位公差（引线标注）
    p6202 = fv.at((37.5, 0, ZU + 17.5))
    sh.leader_note(p6202, (p6202[0] - 30, p6202[1] - 30), spec(c, "C1"))
    sh.gdt(fv.at((44, 0, ZU + 17.5)), (p6202[0] + 6, p6202[1] - 44), "◎", "Ø0.02", "A–B")
    sh.datum(fv.at((31, 0, ZU - 17.5)), "A", direction=(0, 1))
    p6201 = fv.at((380, 0, ZU + 16))
    sh.leader_note(p6201, (p6201[0] - 25, p6201[1] - 36), spec(c, "C2"))
    sh.gdt(fv.at((385, 0, ZU + 16)), (p6201[0] - 70, p6201[1] - 50), "◎", "Ø0.02", "A–B")
    sh.datum(fv.at((376, 0, ZU - 16)), "B", direction=(0, 1))
    pn = fv.at((0, 0, 60))
    sh.leader_note(pn, (pn[0] - 40, pn[1] + 18), spec(c, "C4"))
    sh.gdt(fv.at((6, 0, 52)), (pn[0] + 10, pn[1] + 34), "⌖", "Ø0.05", "A–B")
    sh.gdt(fv.at((6, 0, 70)), (pn[0] + 10, pn[1] + 44), "⊥", "0.02/100", "C")
    pm = fv.at((408, 0, ZU + 26))
    sh.leader_note(pm, (pm[0] + 12, pm[1] - 30), spec(c, "C7"))
    sh.gdt(fv.at((402, 0, ZU + 26)), (pm[0] + 12, pm[1] - 44), "◎", "Ø0.03", "A–B")
    sh.gdt(fv.at((408, 0, ZU - 20)), (pm[0] + 12, pm[1] + 40), "⊥", "0.02", "A–B")
    pc = fv.at((348, 0, 0))
    sh.datum(fv.at((330, 0, -0.5)), "C", direction=(0, 1))
    sh.gdt(fv.at((365, 0, 0)), (pc[0] + 30, pc[1] + 14), "▱", "0.02")
    # 粗糙度
    sh.roughness(fv.at((40, 0, ZU + 17.5)), "Ra 1.6")
    sh.roughness(fv.at((380, 0, ZU + 16)), "Ra 1.6")
    sh.roughness(fv.at((340, 0, -0.5)), "Ra 1.6", ang=180)
    sh.roughness(fv.at((408, 0, ZU + 40)), "Ra 3.2", ang=90)
    sh.roughness(fv.at((-62, 0, ZU + 40)), "Ra 3.2", ang=-90)
    # 俯视图：工艺孔、M10
    for (x, y) in ((315.8, 7.0), (380.2, 47.0)):
        sh.center_mark(tv, (x, y, 0), 4.5)
    pp = tv.at((315.8, 7.0, 0))
    sh.leader_note(pp, (pp[0] - 95, pp[1] + 75), "2 × Ø9 H7 ↧12（装配后配铰 1:50 锥销孔）")
    pb = tv.at((319.8, -42.2, 0))
    sh.leader_note(pb, (pb[0] - 40, pb[1] + 40), "4 × M10-6H ↧18，底孔 ↧22（仰视）")
    sh.dim(tv, (319.8, -42.2, 0), (376.2, -42.2, 0), "56.4", offset=-30)
    sh.dim(tv, (376.2, -42.2, 0), (376.2, 96.2, 0), "138.4", offset=-20, orient="v")
    # 左视图（机头端）：面板口螺孔
    pf = lv.at((-62, -33.5, 143.36))
    sh.leader_note(pf, (pf[0] + 25, pf[1] + 40), "4 × M4-6H ↧7")
    sh.roughness_rest((505, 42), "Ra 12.5")
    sh.requirements(COMMON_REQ + [
        "两轴承孔的公共轴线为基准 A–B；接合面为基准 C。上轴两孔用同轴镗杆一次镗出（工艺规程工序 50）。",
        "上、下件配对加工：两工艺孔 Ø9 H7 在装配找正后与下件配铰 1:50 锥销孔（GB/T 117 10 × 40），上、下件打同一配对编号。",
        "其余螺孔：电机座 4 × M5-6H ↧9（PCD 40），前窗口 6 × M4-6H ↧7，顶盖 4 × M4-6H ↧3。",
        "非加工内表面涂防锈底漆，外表面喷漆；加工后清洗，内腔不得有残砂、切屑。",
    ], (390, 255))
    return sh


# ---------------------------------------------------------------- 下件零件图
def lower_part(step: Path) -> Sheet:
    c = chars("HSG-LS-L")
    s = load(step)
    sh = Sheet(size="A2", title="机壳下件", code="WQLS-HSG-L", material="HT250", scale_text="1:2", mass="8.4 kg", qty="1",
               designer="AI（问渠）", checker="", date=DATE)
    ref = (153.0, 27.0, -31.0)
    fv = sh.view([(s, 1)], "front", scale=0.5, ref3=ref, at=(215, 130), hidden=False, section=((0, 0, 0), (0, -1, 0)), name="A–A")
    tv = sh.view([(s, 1)], "top", scale=0.5, ref3=ref, at=(215, 250), hidden=False)
    lv = sh.view([(s, 1)], "left", scale=0.5, ref3=ref, at=(430, 130), hidden=False)
    sh.dim(fv, (-105, 0, -62), (-105, 0, 0), "62", offset=12, orient="v", dev=(0.05, -0.05))
    sh.dim(fv, (-105, 0, 0), (412, 0, 0), "517", offset=16)
    sh.datum(fv.at((-60, 0, -62)), "A", direction=(0, 1))
    sh.gdt(fv.at((60, 0, 0)), (fv.at((60, 0, 0))[0] + 20, fv.at((60, 0, 0))[1] - 26), "∥", "0.03", "A")
    sh.gdt(fv.at((200, 0, 0)), (fv.at((200, 0, 0))[0] + 20, fv.at((200, 0, 0))[1] - 26), "▱", "0.02")
    sh.gdt(fv.at((200, 0, -62)), (fv.at((200, 0, -62))[0] + 20, fv.at((200, 0, -62))[1] + 20), "▱", "0.05")
    sh.roughness(fv.at((150, 0, 0)), "Ra 1.6")
    sh.roughness(fv.at((150, 0, -62)), "Ra 3.2", ang=180)
    pn = tv.at((0, 0, 0))
    sh.leader_note(pn, (pn[0] - 50, pn[1] - 35), "针板座 64 × 44 深 2.5 ± 0.03")
    ps = tv.at((0, -40, 0))
    sh.leader_note(ps, (ps[0] - 50, ps[1] + 30), "滑板座 46 × 36 深 1.5 ± 0.05")
    pb = tv.at((319.8, -42.2, 0))
    sh.leader_note(pb, (pb[0] - 60, pb[1] + 60), "4 × Ø11 通孔，背面锪平 Ø18 深 1.5")
    pp = tv.at((-94.4, -30.0, 0))
    sh.leader_note(pp, (pp[0] - 10, pp[1] + 50), "2 × Ø10 H7 工艺孔（底边法兰）")
    sh.dim(tv, (-94.4, -30.0, 0), (401.4, -30.0, 0), "495.8", offset=-60)
    sh.dim(tv, (401.4, -30.0, 0), (401.4, 80.0, 0), "110", offset=-15, orient="v")
    for (x, y) in ((-27, -17), (27, -17), (-27, 17), (27, 17)):
        sh.center_mark(tv, (x, y, 0), 1.25)
    sh.roughness_rest((505, 42), "Ra 12.5")
    sh.requirements(COMMON_REQ + [
        "底面 A 为基准；两工艺孔 Ø10 H7 用于加工、检测和装配找正。",
        "机座顶面是接合面，整面精铣；立柱脚处两锥销孔在装配找正后与上件配铰（不在本件单独加工）。",
        "针板螺孔 4 × M3-6H ↧6（针板座底面起）；铰链销孔 2 × Ø8.2 H11。",
        "旋梭、送布机构的孔系在 G4 旋梭组设计后补入本图。",
    ], (390, 255))
    return sh


# ---------------------------------------------------------------- 毛坯图
def blank_sheet(step_blank: Path, step_part: Path, part: str) -> Sheet:
    b = load(step_blank)
    p = load(step_part)
    if part == "upper":
        sh = Sheet(size="A2", title="机壳上件 铸件毛坯", code="WQLS-HSG-U-M", material="HT250", scale_text="1:2", mass="16.4 kg", qty="1",
                   designer="AI（问渠）", date=DATE)
        ref = (173.0, 0.0, 130.0)
        fv = sh.view([(b, 1)], "front", scale=0.5, ref3=ref, at=(215, 175), hidden=False, section=((0, 0, 0), (0, -1, 0)), phantom=[p])
        lv = sh.view([(b, 1)], "left", scale=0.5, ref3=(0, 27, 130), at=(430, 175), hidden=False)
        sh.note((215, 92), "（细双点画线为加工后零件）", 3.5, anchor="middle")
        sh.centerline(lv, (0, -80, 130), (0, 135, 130))
        sh.note(lv.at((0, 110, 265)), "分型面 y = 0（后面 +y 在上型）", 3.5)
        pts = [((340, 0, -3), (0, 1), "接合面余量 3"), ((410.5, 0, ZU + 20), (1, 0), "端面余量 3"), ((37.5, 0, ZU + 15), (0, -1), "孔 Ø30（单边 2.5）"),
               ((380, 0, ZU + 13.5), (0, -1), "孔 Ø27、过孔 Ø16 铸出"), ((-65, 0, ZU + 40), (-1, 0), "面板口端面余量 3")]
        req = ["分型面 y = 0，机壳后面（+y）在上型；机头、机臂、立柱内腔用一个整体树脂砂芯，芯头从面板口、前窗口、顶面两个清砂孔、立柱脚过带孔伸出。",
               "浇注系统：直浇道 Ø30（立柱右侧），横浇道在上型沿机臂顶面，4 个内浇道 21 × 6 进机臂顶面；浇注 1380 ± 10 ℃，7–8 s。",
               "冒口：立柱脚接合面侧暗冒口 1 个（x 305…391），机头、立柱后面出气冒口 Ø30 各 1 个。",
               "冷铁：立柱脚凸台 4 块、电机座端面与止口各 1、6201 孔冷铁芯 1、机头右壁 1、针杆下导套座 1（位置见铸造工艺图）。",
               "Ø20 以下的孔不铸出；加工余量见图（浇注时朝上的面 4 mm，其余 3 mm，孔单边 2.5 mm）。",
               "铸件尺寸公差 DCTG9（GB/T 6414）；未注铸造圆角 R3–R5，拔模斜度 1°。", "铸后去应力退火 550 ℃ × 3 h，清砂、去浇冒口，冒口根部留 2–3 mm。"]
    else:
        sh = Sheet(size="A2", title="机壳下件 铸件毛坯", code="WQLS-HSG-L-M", material="HT250", scale_text="1:2", mass="11.3 kg", qty="1",
                   designer="AI（问渠）", date=DATE)
        ref = (153.0, 27.0, -31.0)
        fv = sh.view([(b, 1)], "front", scale=0.5, ref3=ref, at=(215, 140), hidden=False, section=((0, 0, 0), (0, -1, 0)), phantom=[p])
        lv = sh.view([(b, 1)], "left", scale=0.5, ref3=ref, at=(430, 140), hidden=False)
        sh.note((215, 100), "（细双点画线为加工后零件）", 3.5, anchor="middle")
        pts = [((150, 0, 4), (0, -1), "顶面余量 4（浇注时朝上）"), ((150, 0, -65), (0, 1), "底面余量 3")]
        req = ["分型面在机座顶面，整件在下型、开口朝下，内腔由下型自带砂胎形成，不用芯子。",
               "浇注系统：直浇道 Ø28（右端），横浇道在上型沿机座前侧，4 个内浇道 18 × 6 进前壁顶边；浇注 1380 ± 10 ℃，6–7 s。",
               "冒口：立柱脚 4 个凸台正上方各一个暗冒口 Ø36 × 60（在顶面余量上）。",
               "冷铁：底边法兰两端下面各一条，左铰链耳外侧一块。",
               "Ø20 以下的孔不铸出；加工余量见图。", "铸件尺寸公差 DCTG9（GB/T 6414）；未注铸造圆角 R3–R5，拔模斜度 1°。",
               "铸后去应力退火 550 ℃ × 3 h，清砂、去浇冒口。"]
    for p3, d, txt in pts:
        q = fv.at(p3)
        sh.leader_note(q, (q[0] + d[0] * 25 + 10, q[1] + d[1] * 25), txt)
    sh.requirements(req, (390, 265))
    return sh


# ---------------------------------------------------------------- 上件卧加夹具 FX-HSG-U-20
def fixture_model():
    """零件坐标（整机坐标）里画夹具：托盘顶面 z −200，转台中心 x 209、y 27"""
    B = bd.Box
    parts = []

    def at(shape, x, y, z):
        return shape.moved(bd.Location((x, y, z)))
    base = at(B(500, 500, 40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)), 209, 27, -200)
    parts.append(("1", "FX-U20-01", "底板（托盘过渡板）", 1, "HT300", base))
    riser = at(B(86, 164, 188, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), 348, 27, -200)
    riser = riser - at(bd.Cylinder(30, 200, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), 348, 27, -205)   # 中间通孔：拉杆、油路
    parts.append(("2", "FX-U20-02", "垫块（立柱座）", 1, "HT300", riser))
    pads = None
    for x, y in ((319.8, -42.2), (376.2, -42.2), (319.8, 96.2), (376.2, 96.2)):
        pd = at(bd.Cylinder(12, 12, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), x, y, -12)
        pads = pd if pads is None else pads + pd
    parts.append(("3", "JB/T 8029.2", "支承钉 Ø24（淬硬，与拉杆同轴）", 4, "T8", pads))
    pin1 = at(bd.Cylinder(4.5, 22, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), 315.8, 7.0, -12)
    parts.append(("4", "外购", "液压圆柱涨销 Ø9", 1, "—", pin1))
    pin2 = at(B(9, 4, 22, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), 380.2, 47.0, -12)
    parts.append(("5", "外购", "液压削边涨销 Ø9", 1, "—", pin2))
    rods = None
    for x, y in ((319.8, -42.2), (376.2, -42.2), (319.8, 96.2), (376.2, 96.2)):
        r = at(bd.Cylinder(5, 60, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), x, y, -50)
        cyl = at(bd.Cylinder(25, 45, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), x, y, -110)
        rods = (r + cyl) if rods is None else rods + r + cyl
    parts.append(("6", "外购", "液压拉缸 Ø32（拉杆 M10 拧进工件螺孔）", 4, "—", rods))
    col = at(B(40, 90, 380, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), 465, 0, -200)
    parts.append(("7", "FX-U20-07", "导向套支架（液压翻转，镗孔时翻上）", 1, "Q235", col))
    bush = at(bd.Cylinder(35, 40, rotation=(0, 90, 0), align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)), 440, 0, ZU)
    bush = bush - at(bd.Cylinder(8.5, 50, rotation=(0, 90, 0), align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)), 440, 0, ZU)
    parts.append(("8", "FX-U20-08", "旋转导向套（预紧角接触轴承，内孔 Ø17）", 1, "组件", bush))
    return parts


def fixture_sheet(step_part: Path) -> Sheet:
    p = load(step_part)
    parts = fixture_model()
    sh = Sheet(size="A2", title="上件卧加夹具", code="FX-HSG-U-20", material="", scale_text="1:4", mass="", qty="1", designer="AI（问渠）", date=DATE)
    shapes = [(s, n) for n, _, _, _, _, s in parts]
    fv = sh.view(shapes, "front", scale=0.25, ref3=(209, 0, 0), at=(160, 150), hidden=False, phantom=[p])
    tv = sh.view(shapes, "top", scale=0.25, ref3=(209, 27, 0), at=(160, 300), hidden=False, phantom=[p])
    lv = sh.view(shapes, "left", scale=0.25, ref3=(209, 27, 0), at=(330, 150), hidden=False, phantom=[p])
    sh.balloon_row(fv, [(n, (s.center().X, s.center().Y, s.center().Z)) for n, _, _, _, _, s in parts], along="x", at=60, gap=12)
    sh.dim(fv, (300, 0, -200), (300, 0, 0), "200", offset=60, orient="v")
    sh.dim(fv, (465, 0, -200), (465, 0, ZU), "400", offset=-20, orient="v")
    sh.dim(tv, (315.8, 7.0, 0), (380.2, 47.0, 0), "75.8 ± 0.005", orient="a", offset=8)
    sh.bom([(n, code, name, q, m, "") for n, code, name, q, m, _ in parts])
    sh.requirements([
        "定位：接合面 C 贴 4 个支承钉（限 3 个自由度），两工艺孔 Ø9 H7 套液压圆柱涨销和削边涨销（零间隙，限 3 个）。",
        "夹紧：4 个液压拉缸的拉杆拧进工件立柱脚 4 个 M10 螺孔，拉在支承钉正上方，不产生弯矩；油压 4 MPa 时每个 2.35 kN，合计 9.4 kN"
        "（需要 9.1 kN，安全系数 3.9，计算见 精度分析.json）。精镗前油压降到 40%。",
        "支承钉顶面等高 0.005，对底板底面平行度 0.005；两涨销中心距 75.8 ± 0.005。",
        "导向套支架翻上后，导向套轴线对主轴（B 0°）同轴 0.002（在机用检棒调整）；翻下时让开电机端的加工。",
        "垫块高 200（接合面到托盘顶面），机头下方留出 245 mm 放直角铣头。",
    ], (395, 222))
    return sh


def main():
    src, bsrc, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    done = []
    for name, fn in (("零件图_上件", lambda: upper_part(src / "housing_upper.step")),
                     ("零件图_下件", lambda: lower_part(src / "housing_lower.step")),
                     ("毛坯图_上件", lambda: blank_sheet(bsrc / "blank_upper.step", src / "housing_upper.step", "upper")),
                     ("毛坯图_下件", lambda: blank_sheet(bsrc / "blank_lower.step", src / "housing_lower.step", "lower")),
                     ("夹具总图_FX-HSG-U-20", lambda: fixture_sheet(src / "housing_upper.step"))):
        sh = fn()
        done.append(str(save(sh, out, name)))
        print(name, "ok", flush=True)
    print(done)


if __name__ == "__main__":
    main()
