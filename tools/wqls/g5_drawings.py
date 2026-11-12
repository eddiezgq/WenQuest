"""第 138 轮 G5.1 第 8 步、G5.2：机壳的工程图（数字工厂 drawings/sheet.py：由三维模型投影，国标图框、尺寸、公差、形位公差、粗糙度、技术要求）。

    python3 tools/wqls/g5_drawings.py <零件 STEP 目录> <毛坯 STEP 目录> <输出目录>

八张 A2：上件零件图、下件零件图、合件图（G5.2：孔系在合件上精加工，基准 A ＋ 两工艺孔）、上件毛坯图、下件毛坯图、
上件卧加粗加工夹具 FX-HSG-U-20、合箱台 FX-HSG-P-60、合件卧加夹具 FX-HSG-P-70 总图（带明细栏）。
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
    sh.dim(fv, (408.0, 0, 0.0), (408.0, 0, ZU), "(200)", offset=-22, orient="v")
    sh.dim(fv, (37.5, 0, ZU), (408.0, 0, ZU), "370.5", offset=92)
    # G5.2：上件只标本件做到的要素（接合面 C、针杆孔、工艺孔、螺孔）；上轴两孔、止口、端面在合件上精加工，见合件图 WQLS-HSG-P
    p6202 = fv.at((37.5, 0, ZU + 17.5))
    sh.leader_note(p6202, (p6202[0] - 30, p6202[1] - 30), "Ø35 H7（合件上加工，见 WQLS-HSG-P）")
    p6201 = fv.at((380, 0, ZU + 16))
    sh.leader_note(p6201, (p6201[0] - 25, p6201[1] - 36), "Ø32 H7（合件上加工）")
    pn = fv.at((0, 0, 60))
    sh.leader_note(pn, (pn[0] - 40, pn[1] + 18), spec(c, "C2"))
    sh.gdt(fv.at((6, 0, 70)), (pn[0] + 10, pn[1] + 34), "⊥", "0.02/100", "C")
    pc = fv.at((348, 0, 0))
    sh.datum(fv.at((330, 0, -0.5)), "C", direction=(0, 1))
    sh.gdt(fv.at((365, 0, 0)), (pc[0] + 30, pc[1] + 14), "▱", "0.02")
    # 粗糙度
    sh.roughness(fv.at((340, 0, -0.5)), "Ra 1.6", ang=180)
    # 俯视图：工艺孔、M10
    for (x, y) in ((315.8, 7.0), (380.2, 66.0)):
        sh.center_mark(tv, (x, y, 0), 4.5)
    pp = tv.at((315.8, 7.0, 0))
    sh.leader_note(pp, (pp[0] - 95, pp[1] + 75), "2 × Ø9 H7 ↧12（合箱后配铰 1:50 锥销孔）")
    pb = tv.at((319.8, -42.2, 0))
    sh.leader_note(pb, (pb[0] - 40, pb[1] + 40), "4 × M10-6H ↧18，底孔 ↧22（仰视）")
    sh.dim(tv, (319.8, -42.2, 0), (376.2, -42.2, 0), "56.4", offset=-30)
    sh.dim(tv, (376.2, -42.2, 0), (376.2, 96.2, 0), "138.4", offset=-20, orient="v")
    # 左视图（机头端）：面板口螺孔
    pf = lv.at((-62, -33.5, 143.36))
    sh.leader_note(pf, (pf[0] + 25, pf[1] + 40), "4 × M4-6H ↧7")
    sh.roughness_rest((505, 42), "Ra 12.5")
    sh.requirements(COMMON_REQ + [
        "接合面为基准 C。本件只精加工接合面 C 和针杆两孔（同一次装夹，工艺规程工序 50）；上轴两孔、电机止口与端面、面板口端面、"
        "螺孔在合箱后的合件上加工（合件图 WQLS-HSG-P），本件上这些处只粗加工、单边留 0.5。",
        "上、下件配对：两工艺孔 Ø9 H7 在合件工序 70 与下件配铰 1:50 锥销孔（GB/T 117 10 × 40），上、下件打同一配对编号。",
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
    sh.dim(tv, (-94.4, -30.0, 0), (401.4, 80.0, 0), "507.9 ± 0.02", orient="a", offset=-8)
    for (x, y) in ((-27, -17), (27, -17), (-27, 17), (27, 17)):
        sh.center_mark(tv, (x, y, 0), 1.25)
    sh.roughness_rest((505, 42), "Ra 12.5")
    sh.requirements(COMMON_REQ + [
        "底面 A 为基准；两工艺孔 Ø10 H7 是本件、合件精加工和三坐标检测的统一基准。",
        "机座顶面是接合面，整面精铣；立柱脚处两锥销孔在合件工序 70 与上件配铰（不在本件单独加工）。",
        "针板螺孔 4 × M3-6H ↧6（针板座底面起）；铰链销孔 2 × Ø8.2 H11。",
        "旋梭轴孔 Ø14 H7、下轴两孔 Ø32 H7 在本件上只粗镗（Ø13.0、Ø31.0），合箱后在合件上精镗（合件图 WQLS-HSG-P）；"
        "左端壁 2 × Ø20、右端壁和两道横筋 Ø34 为镗杆过孔，装配后橡胶堵堵上。",
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
    pin2 = at(B(9, 4, 22, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), 380.2, 66.0, -12)
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
    # 辅助支承（G5.1 补充）：液压浮动支承，弹簧推出、液压锁紧；只撑不定位
    C = bd.Cylinder
    up = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    sup = None
    for x, y in ((-25, 52), (25, 52)):
        s = at(C(16, 180, align=up), x, y, -200) + at(C(16, 50, align=up), x, y, -20) + at(C(8, 16, align=up), x, y, 30)   # 支柱、支承缸体、柱塞（顶到 z 46）
        sup = s if sup is None else sup + s
    parts.append(("9", "外购", "液压辅助支承（机头底面）", 2, "—", sup))
    side = at(B(40, 40, 520, align=up), -20, 120, -200)                             # 后支架立柱（在机头后面：让开 B 0° 主轴和 B 270° 前窗口加工）
    side = side + at(C(16, 18, rotation=(90, 0, 0), align=up), -20, 104, 190)       # 缸体 y 86..104
    side = side + at(C(8, 16, rotation=(90, 0, 0), align=up), -20, 86, 190)        # 柱塞顶到 y 70
    parts.append(("10", "FX-U20-10", "液压辅助支承（机头后侧，含立柱）", 1, "—", side))
    top = at(B(40, 190, 30, align=up), -20, 47, 290)                               # 回转臂（绕立柱手动转开，定位销定位），y −48..142
    top = top + at(C(16, 16, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)), -20, -28, 290)
    top = top + at(C(8, 16, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)), -20, -28, 274)
    parts.append(("11", "FX-U20-11", "液压辅助支承（机头顶面，含回转臂）", 1, "—", top))
    return parts


def fixture_sheet(step_part: Path) -> Sheet:
    p = load(step_part)
    parts = fixture_model()
    sh = Sheet(size="A2", title="上件卧加粗加工夹具", code="FX-HSG-U-20", material="", scale_text="1:4", mass="", qty="1", designer="AI（问渠）", date=DATE)
    shapes = [(s, n) for n, _, _, _, _, s in parts]
    fv = sh.view(shapes, "front", scale=0.25, ref3=(209, 0, 0), at=(160, 150), hidden=False, phantom=[p])
    tv = sh.view(shapes, "top", scale=0.25, ref3=(209, 27, 0), at=(160, 300), hidden=False, phantom=[p])
    lv = sh.view(shapes, "left", scale=0.25, ref3=(209, 27, 0), at=(330, 150), hidden=False, phantom=[p])
    sh.balloon_row(fv, [(n, (s.center().X, s.center().Y, s.center().Z)) for n, _, _, _, _, s in parts], along="x", at=60, gap=12)
    sh.dim(fv, (300, 0, -200), (300, 0, 0), "200", offset=60, orient="v")
    sh.dim(fv, (465, 0, -200), (465, 0, ZU), "400", offset=-20, orient="v")
    sh.dim(tv, (315.8, 7.0, 0), (380.2, 66.0, 0), "87.3 ± 0.005", orient="a", offset=8)
    sh.bom([(n, code, name, q, m, "") for n, code, name, q, m, _ in parts])
    sh.requirements([
        "G5.2 起只用于上件粗加工（工序 20）；精加工在合件上做（夹具 FX-HSG-P-70）。",
        "定位：接合面 C 贴 4 个支承钉（限 3 个自由度），两工艺孔 Ø9 H7 套液压圆柱涨销和削边涨销（零间隙，限 3 个）。",
        "夹紧：4 个液压拉缸的拉杆拧进工件立柱脚 4 个 M10 螺孔，拉在支承钉正上方，不产生弯矩；油压 4 MPa 时每个 2.35 kN，合计 9.4 kN"
        "（需要 9.1 kN，安全系数 3.9，计算见 精度分析.json）。",
        "支承钉顶面等高 0.005，对底板底面平行度 0.005；两涨销中心距 75.8 ± 0.005。",
        "导向套支架翻上后，导向套轴线对主轴（B 0°）同轴 0.01（粗镗用）；翻下时让开电机端的加工。",
        "垫块高 200（接合面到托盘顶面），机头下方留出 245 mm 放直角铣头。",
        "辅助支承（件 9、10、11，柱塞 Ø16、额定 4 kN）只撑不定位：定位、拉紧之后，弹簧推柱塞贴住工件（≤ 10 N），再液压锁紧；松开时反过来。"
        "件 11 管直角铣头从下往上钻针杆孔的轴向力。",
    ], (395, 150))
    return sh


# ---------------------------------------------------------------- G5.2 合件图 WQLS-HSG-P
YL, ZL, ZH = 27.791774943072237, -35.36485983577417, -21.5


def pair_sheet(step_u: Path, step_l: Path) -> Sheet:
    c = chars("HSG-LS-P")
    u, lo = load(step_u), load(step_l)
    sh = Sheet(size="A2", title="机壳合件", code="WQLS-HSG-P", material="HT250", scale_text="1:2.5", mass="24.2 kg", qty="1",
               designer="AI（问渠）", checker="", date=DATE)
    ref = (153.0, 0.0, 100.0)
    fv = sh.view([(u, 1), (lo, 2)], "front", scale=0.4, ref3=ref, at=(205, 185), hidden=False, section=((0, 0, 0), (0, -1, 0)), name="A–A")
    lv = sh.view([(u, 1), (lo, 2)], "left", scale=0.4, ref3=(0, 27, 100), at=(455, 185), hidden=False, name="")
    for v_ in (fv,):
        sh.centerline(v_, (-75, 0, ZU), (420, 0, ZU))
        sh.centerline(v_, (-115, 0, ZH), (75, 0, ZH))
        sh.centerline(v_, (0, 0, -30), (0, 0, 200))
    for p_ in ((0, 0, ZU), (0, 0, ZH), (0, YL, ZL)):
        sh.center_mark(lv, p_, 8)
    # 基准 A（底面）与中心高
    sh.datum(fv.at((-60, 0, -62)), "A", direction=(0, 1))
    sh.dim(fv, (-105, 0, -62), (-105, 0, ZU), "262 ± 0.05", offset=24, orient="v")
    sh.dim(fv, (-105, 0, -62), (-105, 0, ZH), "40.5 ± 0.05", offset=10, orient="v")
    sh.dim(lv, (0, 0, ZH), (0, YL, ZL), "31.058 ± 0.015", orient="a", offset=10)
    # 孔与形位公差
    p6202 = fv.at((37.5, 0, ZU + 17.5))
    sh.leader_note(p6202, (p6202[0] - 30, p6202[1] - 26), spec(c, "P3"))
    sh.gdt(fv.at((44, 0, ZU + 17.5)), (p6202[0] + 6, p6202[1] - 38), "◎", "Ø0.02", "B")
    p6201 = fv.at((380, 0, ZU + 16))
    sh.leader_note(p6201, (p6201[0] - 30, p6201[1] - 26), spec(c, "P4"))
    sh.datum(fv.at((376, 0, ZU - 16)), "B", direction=(0, 1))
    ph = fv.at((45, 0, ZH + 7))
    sh.leader_note(ph, (ph[0] - 10, ph[1] - 40), spec(c, "P9"))
    sh.gdt(fv.at((60, 0, ZH + 7)), (ph[0] + 20, ph[1] - 52), "∥", "0.012/100", "D")
    sh.datum(fv.at((30, 0, ZH - 7)), "E", direction=(0, -1))
    pn = fv.at((0, 0, 120))
    sh.leader_note(pn, (pn[0] - 50, pn[1] - 20), "针杆孔 2 × Ø12 H7（上件已加工）")
    sh.gdt(fv.at((6, 0, 110)), (pn[0] - 50, pn[1] - 8), "⌖", "Ø0.05", "E")
    sh.gdt(fv.at((6, 0, 140)), (pn[0] - 50, pn[1] + 4), "⌖", "Ø0.05", "B")
    pm = fv.at((408, 0, ZU + 26))
    sh.leader_note(pm, (pm[0] + 10, pm[1] - 26), spec(c, "P14"))
    sh.gdt(fv.at((402, 0, ZU + 26)), (pm[0] + 10, pm[1] - 38), "◎", "Ø0.03", "B")
    sh.gdt(fv.at((408, 0, ZU - 20)), (pm[0] + 10, pm[1] + 30), "⊥", "0.02", "B")
    pd = lv.at((0, YL, ZL - 16))
    sh.leader_note(pd, (pd[0] - 95, pd[1] + 26), "下轴两孔 2 × Ø32 H7，公共轴线 D，◎ Ø0.02 D；D ∥ B 0.03/300")
    # G4.6 送布组的孔：送布摆轴 F、抬牙摆轴 L、调节器轴（在左视图上标轴线位置）
    import json as _json
    _g = _json.loads((Path(__file__).resolve().parents[2] / "docs" / "设计" / "WQ-LS" / "G4" / "送布机构.json").read_text(encoding="utf-8"))["geo"]
    for key, txt, dx, dy in (("Fr", f"{spec(c, 'P22')}；公共轴线 F，◎ Ø0.04 F", 20, 30), ("Lr", f"{spec(c, 'P24')}；公共轴线 L，◎ Ø0.03 L", -110, 34),
                             ("G", spec(c, "P26"), -100, 50)):
        y_, z_ = _g[key]
        sh.center_mark(lv, (0, y_, z_), 6)
        pf = lv.at((0, y_, z_))
        sh.leader_note(pf, (pf[0] + dx, pf[1] + dy), txt)
    sh.roughness(fv.at((40, 0, ZU + 17.5)), "Ra 1.6")
    sh.roughness(fv.at((45, 0, ZH + 7)), "Ra 1.6")
    sh.roughness_rest((505, 42), "Ra 12.5")
    sh.requirements([
        "本图为上件 WQLS-HSG-U 与下件 WQLS-HSG-L 合箱后的配对件：两件立柱脚打同一配对编号，不得与别的件互换；更换须整对更换。",
        "合箱：接合面 0.02 塞尺塞不进；4 × M10（10.9 级）45 N·m 对角两次拧紧；2 × 锥销 10 × 40（GB/T 117，1:50）合箱后配铰，红丹接触 ≥ 75%。",
        "基准 A：下件底面；两工艺孔 Ø10 H7（下件底边法兰）与 A 组成加工、检测的统一基准体系。B：上轴两孔公共轴线；D：下轴两孔公共轴线；E：旋梭轴孔轴线。",
        "本图标注的孔系在合件上一次装夹加工（工艺规程 HSG-LS-P 工序 70）。旋梭轴孔、上轴两孔的 y 向位置以合箱后实测的针杆轴线为准"
        "（针杆孔在上件工序 50 精铰），使针杆轴线与旋梭轴线、B 垂直相交，位置度 Ø0.05。",
        "螺孔：电机座 4 × M5-6H ↧9（PCD 40），面板口 4 × M4-6H ↧7，前窗口 6 × M4-6H ↧7，顶盖 4 × M4-6H ↧3。",
        "左端壁 2 × Ø20、右端壁与两道横筋 Ø34 为镗杆过孔，装配后用橡胶堵堵上。",
        "送布组（G4.6）：F、L、调节器轴孔对旋梭轴孔 E 的位置 ± 0.1，F、L ∥ D 0.05/100；左端壁 Ø16、Ø18，右端壁 Ø16、Ø14 为镗杆工艺孔，"
        "加工后压碗形堵盖（DIN 443，涂厌氧密封胶）。",
    ], (390, 285))
    return sh


# ---------------------------------------------------------------- G5.2 合箱台 FX-HSG-P-60 与合件卧加夹具 FX-HSG-P-70
LOWER_PINS = ((-94.4, -30.0), (401.4, 80.0))
PADS = ((-90.0, -57.0), (-90.0, 111.0), (402.0, -57.0), (402.0, 111.0))     # 支承钉：下件底边法兰四角，正上方压板


def fixture_p70_model():
    """合件卧加夹具（工序 70、80；工序 L30 只装下件也用）：托盘过渡板 ＋ 框架（前、后、左、右四根梁，中间空着放直角铣头），
    梁顶 4 个支承钉托住底面 A，两个液压涨销进下件工艺孔，4 个液压回转压板从机座顶面四角往下压（正对支承钉），
    左、右两个液压翻转支架上装旋转导向套（左：下轴镗杆；右：上轴镗杆）。零件坐标：A 在 z −62，托盘顶面 z −222。"""
    B, C = bd.Box, bd.Cylinder
    up = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)

    def at(shape, x, y, z):
        return shape.moved(bd.Location((x, y, z)))
    parts = []
    parts.append(("1", "FX-P70-01", "托盘过渡板", 1, "HT300", at(B(640, 360, 40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)), 153, 27, -222)))
    frame = at(B(560, 40, 140, align=up), 153, -57, -222) + at(B(560, 40, 140, align=up), 153, 111, -222)
    frame = frame + at(B(40, 128, 140, align=up), -90, 27, -222) + at(B(40, 128, 140, align=up), 402, 27, -222)
    parts.append(("2", "FX-P70-02", "框架（中间空，放直角铣头）", 1, "Q235", frame))
    pads = None
    for x, y in PADS:
        pd = at(C(12, 20, align=up), x, y, -82)
        pads = pd if pads is None else pads + pd
    parts.append(("3", "JB/T 8029.2", "支承钉 Ø24", 4, "T8", pads))
    parts.append(("4", "外购", "液压圆柱涨销 Ø10", 1, "—", at(C(5, 24, align=up), *LOWER_PINS[0], -82)))
    parts.append(("5", "外购", "液压削边涨销 Ø10", 1, "—", at(B(10, 4, 24, align=up), *LOWER_PINS[1], -82)))
    cl = None
    for x, y in PADS:
        yo = y - 38 if y < 0 else y + 38                   # 缸体在机座外面
        k = at(C(20, 222 + 18, align=up), x, yo, -222) + at(B(24, abs(yo - y) + 14, 12, align=up), x, (y + yo) / 2, 2)
        cl = k if cl is None else cl + k
    parts.append(("6", "外购", "液压回转压板 缸径 25", 4, "—", cl))
    lb = at(B(40, 70, 222 - 36 + 20, align=up), -150, YL, -222) + at(C(35, 40, rotation=(0, 90, 0), align=(bd.Align.CENTER,) * 3), -135, YL, ZL)
    lb = lb - at(C(8.5, 50, rotation=(0, 90, 0), align=(bd.Align.CENTER,) * 3), -135, YL, ZL)
    parts.append(("7", "FX-P70-07", "左支架＋旋转导向套（下轴）", 1, "组件", lb))
    rb = at(B(40, 90, 380 + 62 - 160 + 160, align=up), 465, 0, -222) + at(C(35, 40, rotation=(0, 90, 0), align=(bd.Align.CENTER,) * 3), 440, 0, ZU)
    rb = rb - at(C(8.5, 50, rotation=(0, 90, 0), align=(bd.Align.CENTER,) * 3), 440, 0, ZU)
    parts.append(("8", "FX-P70-08", "右支架＋旋转导向套（上轴）", 1, "组件", rb))
    return parts


def fixture_p70_sheet(step_u: Path, step_l: Path) -> Sheet:
    u, lo = load(step_u), load(step_l)
    parts = fixture_p70_model()
    sh = Sheet(size="A2", title="合件卧加夹具", code="FX-HSG-P-70", material="", scale_text="1:5", mass="", qty="1", designer="AI（问渠）", date=DATE)
    shapes = [(s_, n) for n, _, _, _, _, s_ in parts]
    fv = sh.view(shapes, "front", scale=0.2, ref3=(153, 0, 20), at=(150, 140), hidden=False, phantom=[u, lo])
    tv = sh.view(shapes, "top", scale=0.2, ref3=(153, 27, 0), at=(150, 290), hidden=False, phantom=[lo])
    sh.view(shapes, "left", scale=0.2, ref3=(153, 27, 20), at=(320, 140), hidden=False, phantom=[u, lo])
    sh.balloon_row(fv, [(n, (s_.center().X, s_.center().Y, s_.center().Z)) for n, _, _, _, _, s_ in parts], along="x", at=48, gap=12)
    sh.dim(fv, (-130, 0, -222), (-130, 0, -62), "160", offset=20, orient="v")
    sh.dim(tv, (LOWER_PINS[0][0], LOWER_PINS[0][1], 0), (LOWER_PINS[1][0], LOWER_PINS[1][1], 0), "507.9 ± 0.005", orient="a", offset=10)
    sh.bom([(n, code, name, q, m, "") for n, code, name, q, m, _ in parts])
    sh.requirements([
        "定位：下件底面 A 放在 4 个支承钉上（限 3 个自由度），两工艺孔 Ø10 H7 套液压圆柱涨销和削边涨销（零间隙，限 3 个）。",
        "夹紧：4 个液压回转压板压在机座顶面四角，正对下面的支承钉，不产生弯矩。最大的外力是工序 70 第 1 步从下往上钻锥销孔，"
        "约 650 N，取安全系数 2.07、减去合件重 238 N，需要 1.1 kN；4 MPa 时每个 1.4 kN（计算见 精度分析.json fixture_pair）。精镗前油压降到 40%。",
        "支承钉顶面等高 0.005，对过渡板底面平行度 0.005；两涨销中心距 507.9 ± 0.005。",
        "框架高 160，中间空着：直角铣头放在机座底下，向上钻铰锥销孔。工序 L30（下件单独粗镗）也用本夹具。",
        "两个旋转导向套（预紧角接触轴承，内孔 Ø17）翻上后，轴线对主轴同轴 0.002（在机用检棒调整）：右支架给上轴镗杆（B 0°），"
        "左支架给下轴镗杆（B 180°）；不用时翻下，让开另一端的加工。",
        "机头不加辅助支承：精加工最大的横向力是精铣面板口端面约 96 N，机头让刀约 10 μm，只影响这个端面（平面度 0.1）。",
    ], (395, 150))
    return sh


def fixture_p60_model():
    """合箱台（钳工工位）：底板上 4 个支承钉、两个定位销托住下件；立柱脚两侧 4 个顶丝座微调上件；针板孔基准检具装在针板座里。"""
    B, C = bd.Box, bd.Cylinder
    up = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)

    def at(shape, x, y, z):
        return shape.moved(bd.Location((x, y, z)))
    parts = [("1", "FX-P60-01", "底板", 1, "HT300", at(B(620, 300, 40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)), 153, 27, -82))]
    pads = None
    for x, y in PADS:
        pd = at(C(12, 20, align=up), x, y, -82)
        pads = pd if pads is None else pads + pd
    parts.append(("2", "JB/T 8029.2", "支承钉 Ø24", 4, "T8", pads))
    parts.append(("3", "JB/T 8014.1", "圆柱定位销 Ø10 g6", 1, "T8", at(C(5, 24, align=up), *LOWER_PINS[0], -82)))
    parts.append(("4", "JB/T 8014.2", "削边定位销 Ø10 g6", 1, "T8", at(B(10, 4, 24, align=up), *LOWER_PINS[1], -82)))
    js = None
    for x, y, dy in ((330, -75, 1), (366, -75, 1), (330, 129, -1), (366, 129, -1)):
        j = at(B(30, 20, 120, align=up), x, y, -82) + at(C(5, 30, rotation=(90, 0, 0), align=up), x, y + dy * 10, 20)
        js = j if js is None else js + j
    parts.append(("5", "FX-P60-05", "顶丝座＋M10 细牙顶丝", 4, "45", js))
    gauge = at(B(64, 44, 2.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)), 0, 0, 0) - at(C(6, 5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)), 0, 0, 0.5)
    parts.append(("6", "FX-P60-06", "针板孔基准检具", 1, "GCr15", gauge))
    parts.append(("7", "FX-P60-07", "找正检棒 Ø12 h5 × 260", 1, "GCr15", at(C(6, 260, align=up), 0, 0, -2.5)))
    return parts


def fixture_p60_sheet(step_u: Path, step_l: Path) -> Sheet:
    u, lo = load(step_u), load(step_l)
    parts = fixture_p60_model()
    sh = Sheet(size="A2", title="合箱台", code="FX-HSG-P-60", material="", scale_text="1:5", mass="", qty="1", designer="AI（问渠）", date=DATE)
    shapes = [(s_, n) for n, _, _, _, _, s_ in parts]
    fv = sh.view(shapes, "front", scale=0.2, ref3=(153, 0, 80), at=(150, 150), hidden=False, phantom=[u, lo])
    sh.view(shapes, "top", scale=0.2, ref3=(153, 27, 0), at=(150, 290), hidden=False, phantom=[lo])
    sh.balloon_row(fv, [(n, (s_.center().X, s_.center().Y, s_.center().Z)) for n, _, _, _, _, s_ in parts], along="x", at=58, gap=12)
    sh.bom([(n, code, name, q, m, "") for n, code, name, q, m, _ in parts])
    sh.requirements([
        "合件工艺规程工序 60（钳工）：下件以底面 A 和两工艺孔放在合箱台上，针板座里装针板孔基准检具（件 6）。",
        "放上上件，找正检棒（件 7）从机头上面插进针杆两孔，用顶丝（件 5）微调上件，直到检棒下端顺利插进件 6 的 Ø12 H6 衬套（针杆轴线对针板座 Ø0.1）。",
        "4 × M10 对角分两次拧到 45 N·m，再插一次检棒复查；0.02 塞尺查接合面。锥销孔在卧加工序 70 配铰。",
        "这一步只要保证针板孔对得上针杆、精镗余量够；针杆与旋梭、上轴的精确关系在工序 70 由机床保证。",
    ], (395, 150))
    return sh


def main():
    src, bsrc, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    done = []
    only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    for name, fn in (("零件图_上件", lambda: upper_part(src / "housing_upper.step")),
                     ("零件图_下件", lambda: lower_part(src / "housing_lower.step")),
                     ("毛坯图_上件", lambda: blank_sheet(bsrc / "blank_upper.step", src / "housing_upper.step", "upper")),
                     ("毛坯图_下件", lambda: blank_sheet(bsrc / "blank_lower.step", src / "housing_lower.step", "lower")),
                     ("夹具总图_FX-HSG-U-20", lambda: fixture_sheet(src / "housing_upper.step")),
                     ("合件图", lambda: pair_sheet(src / "housing_upper.step", src / "housing_lower.step")),
                     ("夹具总图_FX-HSG-P-60", lambda: fixture_p60_sheet(src / "housing_upper.step", src / "housing_lower.step")),
                     ("夹具总图_FX-HSG-P-70", lambda: fixture_p70_sheet(src / "housing_upper.step", src / "housing_lower.step"))):
        if only and name not in only:
            continue
        sh = fn()
        done.append(str(save(sh, out, name)))
        print(name, "ok", flush=True)
    print(done)


if __name__ == "__main__":
    main()
