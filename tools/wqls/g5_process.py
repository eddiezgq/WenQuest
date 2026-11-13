"""第 138 轮 G5.1 第 3 步、G5.2：机壳的机械加工工艺规程（数字工厂数据格式 v2）。

G5.2（2026-11-11）：路线改为“上件粗、下件粗、合件精”——两件各自粗加工、时效、精铣接合面（上件同时精铰针杆孔），
合箱后在卧加上一次装夹打锥销、测针杆轴线、精加工两件上的全部孔系。三份规程：HSG-LS-U、HSG-LS-L、HSG-LS-P。

    python3 tools/wqls/g5_process.py [<输出目录>]

由程序生成工艺规程：每个工步的切削用量按刀具和材料（HT250）取，转速、进给速度、机动时间都由程序算，不手填；
孔的各工序尺寸与余量（单边）由程序核对；切削功率按 Kienzle 公式核对机床功率。结果写到
  factory/digital/std/HSG-LS-U_process.yaml、HSG-LS-L_process.yaml（数字工厂的工艺规程，卡片由 hub/cards.py 生成），
然后跑数字工厂的 AI 工艺评审员预审（hub/process.review）和卡片完整性检查（hub/cards.check），输出工艺卡 HTML / PDF。

坐标同整机（mm）：上轴轴线是 B（y = 0、z = 200），上件接合面是 C（z = 0），下件底面是 A（z = −62），下轴两孔公共轴线是 D。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIG = ROOT / "factory" / "digital"
sys.path[:0] = [str(DIG), str(ROOT / "factory"), str(HERE)]
STD = DIG / "std"

# HT250 切削力（Kienzle）：kc1.1 = 1160 N/mm²、mc = 0.26（灰铸铁 GG25 的常用值）
KC11, MC = 1160.0, 0.26
POWER = {"立式加工中心 VMC-01": (15.0, 0.8), "卧式加工中心 HMC-01": (18.5, 0.8)}
TA_TOOL = 0.08          # 换刀（加工中心）每次 min
BLANK_MASS = dict(upper=16.45, lower=11.28)      # 毛坯质量 kg（cad/blank.py 的 blank_*.json；G5.2 模型改后由 main() 读 WQ_BLANK 目录更新）
DATE = "2026-11-11"


# ---------------------------------------------------------------- 切削时间与功率
def n_of(vc, d):
    return 1000 * vc / (math.pi * d)


def face_mill(D, z, vc, fz, width, length, ap, passes=1):
    """端铣：走刀长度 = 长度 + 刀径（切入切出）；行数 = ceil(宽 / 0.75D)"""
    n = n_of(vc, D)
    vf = fz * z * n
    rows = math.ceil(width / (0.75 * D))
    tb = rows * (length + D + 4) / vf * passes
    ae = min(width, 0.75 * D)
    hm = fz * math.sqrt(ae / D)                       # 平均切屑厚度（近似）
    Fc = KC11 * hm ** (-MC) * ap * hm * z * ae / (math.pi * D) if hm > 0 else 0
    P = Fc * vc / 60e3
    return dict(n=round(n), vf=round(vf), tb=tb, rows=rows, P_kw=round(P, 2))


def bore(d, f, vc, L, z=1):
    n = n_of(vc, d)
    tb = (L + 3) / (n * f)
    return dict(n=round(n), vf=round(n * f), tb=tb)


def drill(d, f, vc, depth, holes):
    n = n_of(vc, d)
    tb = (depth + 0.3 * d + 2) / (n * f) * holes
    return dict(n=round(n), vf=round(n * f), tb=tb)


def tap(d, pitch, vc, depth, holes):
    n = n_of(vc, d)
    tb = 2 * (depth + 2 * pitch) / (n * pitch) * holes
    return dict(n=round(n), tb=tb)


def interp_od(D, Dt, z, fz, vc, passes, height):
    """圆弧插补铣外圆：刀心轨迹周长 π(D + Dt)"""
    n = n_of(vc, Dt)
    vf = fz * z * n * (D + Dt) / D                    # 外圆插补：刀心进给要放大，保证切削刃处的每齿进给
    tb = passes * math.ceil(height / 10) * math.pi * (D + Dt) / vf
    return dict(n=round(n), vf=round(vf), tb=tb)


def step(no, content, tool, gauge, calc, vc=None, f=None, ap=None, passes=1, ta=0.3, note=""):
    s = dict(step=no, content=content, tool=tool, gauge=gauge, vc=vc, f=f, ap=ap, passes=passes,
             tb_min=round(calc["tb"], 2), ta_min=ta)
    if note:
        s["note"] = note
    s["_n"] = calc.get("n")
    if calc.get("P_kw"):
        s["_P"] = calc["P_kw"]
    return s


# ---------------------------------------------------------------- 上件 HSG-LS-U（G5.2：上件只做粗加工、精铣接合面 C、精铰针杆孔）
def upper():
    tools = [
        dict(id="T01", name="面铣刀 Ø80", spec="Ø80 八刃可转位面铣刀，SEKN 1203 刀片（涂层硬质合金 K20，铸铁用）；精铣用修光刃刀片", ops=[10, 50]),
        dict(id="T02", name="面铣刀 Ø63", spec="Ø63 五刃可转位面铣刀（K20），电机座端面、面板口端面", ops=[20]),
        dict(id="T03", name="同轴粗镗杆", spec="Ø28 钢制减振杆，前刀 Ø34、后刀 Ø31 两个双刃刀夹相距 344，尾部 Ø17 导向柱", ops=[20]),
        dict(id="T05", name="立铣刀 Ø20", spec="Ø20 四刃硬质合金立铣刀，圆弧插补粗铣电机止口外圆", ops=[20]),
        dict(id="T06", name="直角铣头", spec="90° 直角铣头（HSK-A63 接口，回转定位精度 ±0.005），从机头下方钻针杆孔、锪沉孔 Ø14", ops=[20]),
        dict(id="T07", name="钻头 Ø11.5", spec="整体硬质合金钻 Ø11.5，加长型（有效长 160）", ops=[20]),
        dict(id="T08", name="钻头 Ø8.5 / 扩孔钻 Ø8.85 / 铰刀 Ø9 H7", spec="整体硬质合金钻 Ø8.5、扩孔钻 Ø8.85、铰刀 Ø9 H7（两个工艺孔）", ops=[10]),
        dict(id="T09", name="钻头 Ø8.5、丝锥 M10", spec="硬质合金钻 Ø8.5；M10 螺旋槽丝锥（铸铁用，6H）", ops=[10]),
        dict(id="T12", name="中心钻", spec="Ø6 90° 定心钻（硬质合金）", ops=[10]),
        dict(id="T14", name="粗镗刀 Ø18", spec="Ø16–Ø22 单刃粗镗刀（K20），轴过孔", ops=[20]),
        dict(id="T15", name="扩孔钻 Ø11.85 / 铰刀 Ø12 H7", spec="整体硬质合金扩孔钻 Ø11.85、机用铰刀 Ø12 H7，加长（有效长 200），前端导向", ops=[50]),
    ]
    gauges = [
        dict(id="G01", name="三坐标测量机（MPE_E = 1.8 + L/300 μm）"),
        dict(id="G03", name="内径千分表 18–35 mm（0.001）"),
        dict(id="G04", name="Ø12 H7、Ø9 H7 塞规（通端 / 止端）"),
        dict(id="G05", name="外径千分尺 50–75 mm（0.001）"),
        dict(id="G06", name="螺纹塞规 M10-6H"),
        dict(id="G08", name="游标卡尺 0–300 mm（0.02）"),
        dict(id="G09", name="大理石平板 00 级 + 杠杆千分表（0.002）"),
        dict(id="G10", name="布氏硬度计"),
        dict(id="G11", name="X 光探伤（首件、每批抽 1 件）"),
        dict(id="G13", name="针杆孔垂直度检具：Ø12 h5 × 260 检棒插进两孔，接合面 C 贴在平板上，杠杆千分表测检棒母线"),
    ]
    chars = [
        dict(id="C1", name="接合面 C", spec="平面度 0.02，Ra 1.6", nominal=0.0, es=0.02, ei=0.0, kind="geo", key=True),
        dict(id="C2", name="针杆导套孔（上、下）", spec="2 × Ø12 H7（+0.018/0），Ra 1.6", nominal=12, es=0.018, ei=0.0, kind="dim", key=True),
        dict(id="C3", name="针杆孔对接合面 C 的垂直度", spec="0.02/100", nominal=0.0, es=0.02, ei=0.0, kind="geo", key=True),
        dict(id="C4", name="C 到上轴两孔（粗镗）中心的距离", spec="200 ± 0.1（给合件精镗留均匀余量）", nominal=200, es=0.1, ei=-0.1, kind="dim"),
        dict(id="C5", name="上轴两孔（粗镗）", spec="Ø34.0、Ø31.0（+0.1/0）；合箱后在合件工序 70 精镗到 Ø35 H7、Ø32 H7", kind="other"),
        dict(id="C6", name="工艺孔", spec="2 × Ø9 H7（+0.015/0），粗加工定位用；合箱后在合件工序 70 配铰成 1:50 锥销孔", nominal=9, es=0.015, ei=0.0, kind="dim"),
        dict(id="C7", name="螺纹孔", spec="4 × M10-6H 螺纹深 18、底孔深 22（接合面）", kind="other"),
        dict(id="C8", name="铸件质量", spec="HT250：硬度 190–240 HBW；首件 X 光检查电机座、立柱脚、针杆导套座无缩松", kind="other"),
        dict(id="C9", name="压脚杆导套孔（上、下）", spec="2 × Ø12 H7（+0.018/0），Ra 1.6；轴线 x −16、y 6（G4.7）", nominal=12, es=0.018, ei=0.0, kind="dim", key=True),
        dict(id="C10", name="压脚杆孔对针杆孔的平行度", spec="0.03/100（同一次装夹由机床保证）", nominal=0.0, es=0.03, ei=0.0, kind="geo"),
    ]
    holes = {
        "前轴承孔（粗）": [("铸出", 30.0, 0.6, -0.6), (20, 34.0, 0.1, 0.0)],
        "后轴承孔（粗）": [("铸出", 27.0, 0.6, -0.6), (20, 31.0, 0.1, 0.0)],
        "针杆孔": [(20, 11.5, 0.1, 0.0), (50, 11.85, 0.027, 0.0), (50, 12.0, 0.018, 0.0)],
        "压脚杆孔": [(20, 11.5, 0.1, 0.0), (50, 11.85, 0.027, 0.0), (50, 12.0, 0.018, 0.0)],
        "电机止口（外圆，粗）": [("铸出", 57.0, 0.6, -0.6), (20, 53.0, 0.0, -0.1)],
        "轴过孔（粗）": [("铸出", 16.0, 0.5, -0.5), (20, 18.0, 0.2, 0.0)],
        "工艺孔": [(10, 8.5, 0.1, 0.0), (10, 8.85, 0.022, 0.0), (10, 9.0, 0.015, 0.0)],
    }
    ops = []
    # ---- 工序 10：VMC，接合面向上（工件倒放），粗基准是两个轴承孔的铸孔
    o10 = dict(seq=10, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="工件倒放（接合面朝上）。粗基准：前后两个轴承孔的铸孔（两端锥面涨套，保证轴承孔余量均匀）＋机臂顶面一个可调支承限转。"
                       "粗铣、半精铣接合面 C，留精铣余量 0.5；钻、扩、铰两个工艺孔 Ø9 H7，作为工序 20 粗加工“一面两销”的定位基准（合箱后它们配铰成锥销孔）；"
                       "钻攻 4 × M10（装配用，也是卧加夹具拉紧工件用的螺孔：立柱脚的凸台在立柱里面，外面压不到）",
               datum="前后轴承孔铸孔（粗基准）、机臂顶面", clamping="两端锥面涨套（液压），机臂顶面辅助支承", fixture="专用夹具 FX-HSG-U-10（涨套式）",
               coolant="干切（铸铁）", setup_min=40,
               locate=[dict(surface="前后轴承孔铸孔", symbol="mandrel", dof=4), dict(surface="机臂顶面", symbol="support", dof=1)],
               clamp=[dict(surface="轴承孔铸孔（涨套）", kind="hydraulic")])
    o10["steps"] = [
        step(1, "粗铣接合面 C（余量 3 → 1.0），三行", "T01", "G08", face_mill(80, 8, 160, 0.18, 178, 96, 2.5), vc=160, f=0.18 * 8, ap=2.0),
        step(2, "半精铣接合面 C（留精铣余量 0.5，平面度 0.05）", "T01", "G09", face_mill(80, 8, 200, 0.10, 178, 96, 0.5), vc=200, f=0.10 * 8, ap=0.5),
        step(3, "定心两个工艺孔、4 个 M10 孔", "T12", "", drill(6, 0.08, 60, 2, 6), vc=60, f=0.08),
        step(4, "钻两个工艺孔 Ø8.5 深 12（x 315.8 / y 7.0 与 x 380.2 / y 66.0）", "T08", "G08", drill(8.5, 0.2, 70, 12, 2), vc=70, f=0.2),
        step(5, "扩工艺孔 Ø8.5 → Ø8.85、铰 Ø9 H7", "T08", "G04", {"tb": bore(8.85, 0.15, 60, 12)["tb"] * 2 + bore(9, 0.3, 12, 12)["tb"] * 2}, vc=12, f=0.3),
        step(6, "钻 4 × Ø8.5 深 22", "T09", "G08", drill(8.5, 0.18, 70, 22, 4), vc=70, f=0.18),
        step(7, "攻 4 × M10-6H 深 18（刚性攻丝）：工序 20 卧加夹具的液压拉杆拧进这 4 个孔，合箱时也用它们", "T09", "G06",
             tap(10, 1.5, 10, 18, 4), vc=10, f=1.5),
    ]
    o10["inspect"] = [dict(char="接合面 C 平面度 0.05（半精铣后）", gauge="G09", freq="首件、每 10 件"), dict(char="工艺孔 Ø9 H7（C6）", gauge="G04", freq="每件"),
                      dict(char="M10-6H（C7）", gauge="G06", freq="每件"),
                      dict(char="C 面到两轴承孔铸孔中心的距离（余量均匀）200.5 ± 0.5", gauge="G01", freq="首件")]
    ops.append(o10)
    # ---- 工序 20：HMC 粗加工（G5.1 补充的辅助支承用在这里）
    o20 = dict(seq=20, operation="镗轴承孔 Bearing-bore boring", workstation="卧式加工中心 HMC-01", shop="机加",
               content="一面两销定位（接合面 C ＋ 两工艺孔），夹具抬高 160 让出机头下方空间。B 180° 钻轴过孔、粗铣电机座端面和止口外圆；"
                       "B 0° 粗铣面板口端面，同轴镗杆（带导向套）粗镗两轴承孔；直角铣头从下方钻针杆孔 Ø11.5。各面单边留 0.5，合箱后在合件工序 70 精加工。"
                       "装夹顺序：一面两销定位 → 4 个拉缸拉紧 → 4 个辅助支承伸出（弹簧推力 ≤ 10 N）、液压锁紧，顶面支承的回转臂转到工作位、插定位销；卸件反过来",
               datum="接合面 C、两工艺孔（一面两销）", clamping="4 个液压拉缸，拉杆拧进立柱脚 4 个 M10 螺孔，把工件拉紧在正下方的 4 个支承钉上；机头 4 个液压浮动辅助支承（底面 2、后侧 1、顶面 1）在拉紧后伸出、锁紧，只撑不定位",
               fixture="专用夹具 FX-HSG-U-20（一面两销，带辅助支承）", coolant="干切（铸铁）", setup_min=45, fixture_id="FX-HSG-U-20",
               locate=[dict(surface="接合面 C", symbol="plane", dof=3), dict(surface="工艺孔 1（圆柱销）", symbol="pin", dof=2),
                       dict(surface="工艺孔 2（削边销）", symbol="pin_diamond", dof=1)],
               clamp=[dict(surface="立柱脚 4 个 M10 螺孔（液压拉杆）", kind="hydraulic")],
               support=[dict(surface="机头底面 2 点、后侧面 1 点、顶面 1 点", kind="hydraulic_work_support", note="拉紧后伸出锁紧，只撑不定位")])
    fm3 = face_mill(63, 5, 160, 0.15, 57, 57, 2.0)
    o20["steps"] = [
        step(1, "B 180°（电机端）：粗镗轴过孔 Ø16（铸出）→ Ø18，深 40", "T14", "G08", bore(18, 0.2, 110, 40), vc=110, f=0.2, ap=1.0),
        step(2, "B 180°：粗铣电机座端面（余量 3 → 0.5）", "T02", "G08", fm3, vc=160, f=0.75, ap=2.5),
        step(3, "B 180°：圆弧插补粗铣电机止口外圆 Ø57 → Ø53.0（0/−0.1），两圈", "T05", "G05", interp_od(53, 20, 4, 0.10, 150, 2, 12), vc=150, f=0.4, ap=2.0),
        step(4, "B 0°（机头端）：粗铣面板口端面（余量 3 → 0.5）。走刀方向选得使切削合力把机头压向底面和后侧的支承", "T02", "G08",
             face_mill(63, 5, 160, 0.15, 112, 120, 2.5), vc=160, f=0.75, ap=2.5),
        step(5, "B 0°：翻上导向套支架；同轴粗镗杆从机头端伸入，两孔一刀粗镗到 Ø34.0、Ø31.0（+0.1/0）；镗完支架翻下", "T03", "G03",
             bore(32, 0.25, 110, 22), vc=110, f=0.25, ap=2.0, ta=1.0),
        step(6, "装直角铣头，从机头下方钻针杆孔 Ø11.5，一次钻通上、下两个导套座（往上的轴向力约 0.9 kN 由顶面支承承受）", "T06", "G08",
             drill(11.5, 0.15, 60, 150, 1), vc=60, f=0.15),
        step(7, "直角铣头：锪针杆孔下端沉孔 Ø14 深 4（上止点时针夹进去 0.5）", "T06", "G08", bore(14, 0.08, 60, 4), vc=60, f=0.08),
        step(8, "直角铣头：钻压脚杆孔 Ø11.5（x −16、y 6），一次钻通上、下两个导套座（G4.7）", "T06", "G08", drill(11.5, 0.15, 60, 150, 1), vc=60, f=0.15),
    ]
    o20["inspect"] = [dict(char="两轴承孔 Ø34.0、Ø31.0（+0.1/0）（C5）", gauge="G03", freq="首件、每 5 件"),
                      dict(char="止口 Ø53.0（0/−0.1）", gauge="G05", freq="首件、每 5 件")]
    ops.append(o20)
    ops.append(dict(seq=40, operation="时效 Stress relieving", workstation="热处理炉 HT-01", shop="热处理",
                    content="第二次去应力退火（与下件同炉）：≤ 200 ℃ 装炉，≤ 80 ℃/h 升到 550 ± 10 ℃，保温 2 h，≤ 40 ℃/h 随炉冷到 200 ℃ 以下出炉。"
                            "粗加工后的残余应力在这里释放，变形在精铣接合面、精铰针杆孔和合件精加工时切掉", datum="—", clamping="料架平放，接合面朝下", minutes=6,
                    setup_min=10, steps=[], inspect=[dict(char="炉温曲线记录（550 ± 10 ℃、保温 2 h）", gauge="炉温记录仪", freq="每炉")]))
    # ---- 工序 50：VMC 精铣接合面 C、精铰针杆孔（同一次装夹：C 面和机头底面都朝上）
    o50 = dict(seq=50, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="工件倒放（接合面 C 朝上；机头底面也朝上，比 C 低 46）。以粗镗后的两个轴承孔定位（两端涨芯轴）＋机臂顶面限转："
                       "精铣接合面 C，C 到上轴两孔（粗镗）中心 200 ± 0.1、平面度 0.02；同一次装夹，立式主轴从上面扩、铰针杆两孔 Ø12 H7（一次铰通），"
                       "针杆孔对 C 的垂直度 0.02/100 由机床保证。合箱后进不去刀，所以针杆孔在这里精加工（见细则 G5.2 偏差 1）；"
                       "合件工序 70 先测出针杆孔的实际轴线，再以它为基准精镗旋梭轴孔和上轴两孔",
               datum="两轴承孔（粗镗后，涨芯轴）、机臂顶面", clamping="两端液压涨芯轴，机臂顶面辅助支承", fixture="专用夹具 FX-HSG-U-50（涨芯轴式）",
               coolant="干切；铰孔用切削油", setup_min=40,
               locate=[dict(surface="两轴承孔（粗镗）", symbol="mandrel", dof=4), dict(surface="机臂顶面", symbol="support", dof=1)],
               clamp=[dict(surface="涨芯轴", kind="hydraulic")])
    o50["steps"] = [
        step(1, "精铣接合面 C（0.5），平面度 0.02、Ra 1.6（修光刃刀片）", "T01", "G09", face_mill(80, 8, 220, 0.06, 178, 96, 0.5), vc=220, f=0.48, ap=0.5),
        step(2, "扩针杆孔 Ø11.5 → Ø11.85（两孔一次扩通，深 46 起到 182）", "T15", "G03", bore(11.85, 0.12, 60, 136), vc=60, f=0.12),
        step(3, "铰针杆孔 Ø12 H7，上下两孔一次铰通", "T15", "G04", bore(12, 0.25, 12, 136), vc=12, f=0.25),
        step(4, "扩压脚杆孔 Ø11.5 → Ø11.85（同一把刀，两孔一次扩通）（G4.7）", "T15", "G03", bore(11.85, 0.12, 60, 144), vc=60, f=0.12),
        step(5, "铰压脚杆孔 Ø12 H7，上下两孔一次铰通；和针杆孔同一次装夹，平行度 0.03/100 由机床保证", "T15", "G04", bore(12, 0.25, 12, 144), vc=12, f=0.25),
    ]
    o50["inspect"] = [dict(char="C 面平面度 0.02（C1）", gauge="G09", freq="每件"), dict(char="针杆孔 Ø12 H7（C2）", gauge="G04", freq="每件"),
                      dict(char="针杆孔对 C 垂直度 0.02/100（C3）", gauge="G13", freq="首件、每 5 件"),
                      dict(char="C 到上轴两孔（粗镗）中心 200 ± 0.1（C4）", gauge="G01", freq="首件")]
    ops.append(o50)
    ops.append(dict(seq=60, operation="零件检验 Part inspection", workstation="检验站 QC-01", shop="检验", final_inspection=True,
                    content="上件到合箱之前的检验：接合面 C、针杆孔、工艺孔、M10；首件加 X 光与解剖（见铸造工艺第七节）。成品的孔系在合件（WQLS-HSG-P）上检验",
                    datum="接合面 C、两工艺孔", clamping="三坐标测量夹具（一面两销）", minutes=10, setup_min=5, steps=[],
                    inspect=[dict(char=c["id"], gauge={"C7": "G06", "C8": "G10"}.get(c["id"], "G01"), freq="每件" if c.get("key") else "每 5 件")
                             for c in chars]))
    return dict(item="HSG-LS-U", name="机壳上件（机头、机臂、立柱）", drawing_no="WQLS-HSG-U", tools=tools, gauges=gauges, chars=chars, ops=ops,
                holes=holes, blank_mass=BLANK_MASS["upper"], part_mass=15.85)


# ---------------------------------------------------------------- 下件 HSG-LS-L（G5.2：粗加工，精铣底面 A 和接合面；孔系在合件上精加工）
def lower():
    tools = [
        dict(id="T01", name="面铣刀 Ø100", spec="Ø100 十刃可转位面铣刀，SEKN 1203（K20），铣底面 A 和机座顶面", ops=[10, 20, 50]),
        dict(id="T02", name="立铣刀 Ø16", spec="Ø16 四刃硬质合金立铣刀：针板座、滑板座（工序 50）；左端壁两个 Ø20 孔螺旋插补（工序 30）", ops=[30, 50]),
        dict(id="T03", name="钻头 Ø9.5 / 扩孔钻 Ø9.85 / 铰刀 Ø10 H7", spec="整体硬质合金钻 Ø9.5、扩孔钻 Ø9.85、铰刀 Ø10 H7（底边法兰上的两个工艺孔）", ops=[10]),
        dict(id="T04", name="钻头 Ø11", spec="硬质合金钻 Ø11（M10 螺钉过孔）", ops=[20]),
        dict(id="T05", name="反锪刀 Ø18", spec="反向锪平刀 Ø18（从上面穿过 Ø11 孔，在凸台下端锪平面）", ops=[20]),
        dict(id="T06", name="钻头 Ø2.5、丝锥 M3", spec="硬质合金钻 Ø2.5；M3 丝锥（6H），针板螺孔", ops=[50]),
        dict(id="T07", name="钻头 Ø8.0 / 铰刀 Ø8.2", spec="硬质合金钻 Ø8.0 ＋ 铰刀 Ø8.2 H11（铰链销孔）", ops=[50]),
        dict(id="T08", name="中心钻", spec="Ø6 90° 定心钻", ops=[10, 20, 50]),
        dict(id="T09", name="下轴粗镗杆", spec="Ø26 钢制减振杆，两个 Ø31 双刃刀夹相距 276，尾部 Ø17 导向柱（与合件工序 70 的下轴镗杆同一结构）", ops=[30]),
        dict(id="T10", name="旋梭轴孔阶梯粗镗杆", spec="Ø18 硬质合金杆 ＋ Ø12 颈部（长 46），单刃粗镗刀 Ø13", ops=[30]),
    ]
    gauges = [
        dict(id="G01", name="三坐标测量机（MPE_E = 1.8 + L/300 μm）"),
        dict(id="G03", name="内径千分表 10–35 mm（0.001）"),
        dict(id="G04", name="Ø10 H7 塞规（通端 / 止端）"),
        dict(id="G06", name="螺纹塞规 M3-6H"),
        dict(id="G08", name="游标卡尺 0–600 mm（0.02）"),
        dict(id="G09", name="大理石平板 00 级 + 杠杆千分表（0.002）"),
        dict(id="G10", name="布氏硬度计"),
        dict(id="G12", name="深度千分尺 0–25 mm（0.01）"),
    ]
    chars = [
        dict(id="C1", name="底面 A", spec="平面度 0.05，Ra 3.2", nominal=0.0, es=0.05, ei=0.0, kind="geo", key=True),
        dict(id="C2", name="机座顶面（接合面）", spec="平面度 0.02，对 A 平行度 0.03，Ra 1.6", nominal=0.0, es=0.02, ei=0.0, kind="geo", key=True),
        dict(id="C3", name="机座高度（A 到顶面）", spec="62 ± 0.05", nominal=62, es=0.05, ei=-0.05, kind="dim", key=True, qms="机座高度 Bed height (mm)"),
        dict(id="C4", name="针板座", spec="深 2.5 ± 0.03，平面度 0.03，对 A 平行度 0.03", nominal=2.5, es=0.03, ei=-0.03, kind="dim", key=True),
        dict(id="C5", name="滑板座", spec="深 1.5 ± 0.05", nominal=1.5, es=0.05, ei=-0.05, kind="dim"),
        dict(id="C6", name="工艺孔（底边法兰）", spec="2 × Ø10 H7（+0.015/0），中心距 507.9 ± 0.02：合件精加工（工序 70）和检测的基准", nominal=10, es=0.015, ei=0.0,
             kind="dim", key=True),
        dict(id="C7", name="螺钉过孔与锪平", spec="4 × Ø11，背面锪平 Ø18 深 1.5", kind="other"),
        dict(id="C8", name="螺纹孔与铰链孔", spec="4 × M3-6H（针板）；2 × Ø8.2 H11 铰链销孔", kind="other"),
        dict(id="C9", name="孔系（粗镗）", spec="下轴两孔 Ø31.0、旋梭轴孔 Ø13.0（+0.1/0）；左端壁 2 × Ø20 过孔；合箱后在合件工序 70 精镗", kind="other"),
        dict(id="C10", name="铸件质量", spec="HT250：硬度 190–240 HBW；首件 X 光检查立柱脚凸台、轴承座、旋梭轴座无缩松", kind="other"),
    ]
    holes = {"工艺孔": [(10, 9.5, 0.1, 0.0), (10, 9.85, 0.022, 0.0), (10, 10.0, 0.015, 0.0)],
             "下轴孔（粗）": [("铸出", 27.0, 0.6, -0.6), (30, 31.0, 0.1, 0.0)],
             "旋梭轴孔（粗）": [("铸出", 9.0, 0.6, -0.6), (30, 13.0, 0.1, 0.0)]}
    ops = []
    o10 = dict(seq=10, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="工件倒放（顶面朝下）。粗基准：机座顶面铸面三点＋前侧面两点＋左端面一点。粗、半精铣底面 A（余量 3 → 0.3）；"
                       "在底边法兰上钻、扩、铰两个工艺孔 Ø10 H7（对角）——它们和 A 面是以后各道（直到合件精加工）的统一基准",
               datum="机座顶面铸面、前侧面、左端面（粗基准）", clamping="手动压板 4 点压在底边法兰上", fixture="专用夹具 FX-HSG-L-10",
               coolant="干切", setup_min=30,
               locate=[dict(surface="机座顶面铸面", symbol="support", dof=3), dict(surface="前侧面", symbol="support", dof=2), dict(surface="左端面", symbol="support", dof=1)],
               clamp=[dict(surface="底边法兰", kind="manual")])
    o10["steps"] = [
        step(1, "粗铣底面 A（3 → 0.8）", "T01", "G08", face_mill(100, 10, 160, 0.18, 197, 522, 2.2), vc=160, f=1.8, ap=2.2),
        step(2, "半精铣底面 A（留 0.3），平面度 0.05", "T01", "G09", face_mill(100, 10, 200, 0.10, 197, 522, 0.5), vc=200, f=1.0, ap=0.5),
        step(3, "定心、钻、扩、铰两个工艺孔 Ø10 H7（底边法兰对角，中心距 507.9 ± 0.02）", "T03", "G04",
             {"tb": drill(9.5, 0.2, 70, 8, 2)["tb"] + bore(9.85, 0.15, 60, 8)["tb"] * 2 + bore(10, 0.3, 12, 8)["tb"] * 2}, vc=70, f=0.2),
    ]
    o10["inspect"] = [dict(char="底面 A 平面度 0.05", gauge="G09", freq="首件、每 10 件"), dict(char="工艺孔 Ø10 H7（C6）", gauge="G04", freq="每件")]
    ops.append(o10)
    o20 = dict(seq=20, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="一面两销（底面 A ＋ 两工艺孔）。粗铣机座顶面（余量 4 → 0.5）；钻 4 × Ø11 螺钉过孔，反锪 Ø18",
               datum="底面 A、两工艺孔（精基准）", clamping="液压 4 点", fixture="专用夹具 FX-HSG-L-20（一面两销，与工序 50 共用）",
               coolant="干切", setup_min=30, fixture_id="FX-HSG-L-20")
    o20["steps"] = [step(1, "粗铣机座顶面（4 → 0.5），两刀", "T01", "G08", face_mill(100, 10, 160, 0.18, 197, 522, 1.75, passes=2), vc=160, f=1.8, ap=1.75),
                    step(2, "定心、钻 4 × Ø11 通孔，反锪 Ø18 深 1.5", "T04", "G08", {"tb": drill(11, 0.2, 70, 30, 4)["tb"] + 4 * 0.3}, vc=70, f=0.2)]
    o20["inspect"] = [dict(char="顶面到 A 62.5 ± 0.1", gauge="G08", freq="首件、每 10 件")]
    ops.append(o20)
    o30 = dict(seq=30, operation="镗轴承孔 Bearing-bore boring", workstation="卧式加工中心 HMC-01", shop="机加",
               content="下件单独装在合件夹具 FX-HSG-P-70 上（底面 A ＋ 两工艺孔，与合件精加工同一基准）。B 0°：螺旋插补铣出左端壁两个 Ø20 过孔"
                       "（旋梭轴孔、下轴的镗杆导向柱从这里过；铸件上是实心的）；阶梯镗杆粗镗旋梭轴孔 Ø9（铸出）→ Ø13.0。"
                       "B 180°：下轴粗镗杆从右端壁 Ø34 孔伸进去，经两道横筋的 Ø34 孔，尾部导向柱穿过左端壁 Ø20 孔进左支架的导向套，两孔一刀粗镗 Ø27 → Ø31.0。单边留 0.5",
               datum="底面 A、两工艺孔（一面两销）", clamping="4 个液压回转压板压在机座顶面四角（正对支承钉）",
               fixture="专用夹具 FX-HSG-P-70（合件精加工夹具，这里只装下件）", coolant="干切", setup_min=30, fixture_id="FX-HSG-P-70",
               locate=[dict(surface="底面 A", symbol="plane", dof=3), dict(surface="工艺孔 1（圆柱涨销）", symbol="pin", dof=2),
                       dict(surface="工艺孔 2（削边涨销）", symbol="pin_diamond", dof=1)],
               clamp=[dict(surface="机座顶面四角（液压回转压板）", kind="hydraulic")])
    o30["steps"] = [
        step(1, "B 0°：螺旋插补铣左端壁 2 × Ø20 过孔（壁厚约 6）", "T02", "G08", {"tb": 2 * 0.6}, vc=150, f=0.05 * 4),
        step(2, "B 0°：阶梯粗镗杆粗镗旋梭轴孔 Ø9 → Ø13.0（+0.1/0），长 42", "T10", "G03", bore(13, 0.12, 100, 42), vc=100, f=0.12, ap=2.0),
        step(3, "B 180°：翻上左支架；下轴粗镗杆两孔一刀粗镗 Ø27 → Ø31.0（+0.1/0）（进刀时主轴定向、刀尖朝上，抬高 1 mm 穿过右端壁和横筋孔）", "T09", "G03",
             bore(31, 0.25, 110, 16), vc=110, f=0.25, ap=2.0, ta=1.0),
    ]
    o30["inspect"] = [dict(char="下轴两孔 Ø31.0、旋梭轴孔 Ø13.0（C9）", gauge="G03", freq="首件、每 5 件")]
    ops.append(o30)
    ops.append(dict(seq=40, operation="时效 Stress relieving", workstation="热处理炉 HT-01", shop="热处理",
                    content="第二次去应力退火（与上件同炉，规范同上件工序 40）", datum="—", clamping="料架平放，底面朝下", minutes=6, setup_min=10, steps=[],
                    inspect=[dict(char="炉温曲线记录", gauge="炉温记录仪", freq="每炉")]))
    o50 = dict(seq=50, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="先翻面：以顶面粗铣面定位精铣底面 A（0.3），平面度 0.05；再回到一面两销（A ＋ 两工艺孔）：精铣机座顶面保证高度 62 ± 0.05、"
                       "平面度 0.02、对 A 平行度 0.03；精铣针板座、滑板座；钻攻针板 4 × M3；夹具侧转 90°（附加角度板）钻铰两个铰链销孔 Ø8.2 H11",
               datum="底面 A、两工艺孔", clamping="液压 4 点", fixture="专用夹具 FX-HSG-L-20", coolant="干切；攻丝用切削油", setup_min=40, fixture_id="FX-HSG-L-20")
    o50["steps"] = [
        step(1, "（翻面，顶面粗铣面定位）精铣底面 A（0.3），平面度 0.05", "T01", "G09", face_mill(100, 10, 220, 0.06, 197, 522, 0.3), vc=220, f=0.6, ap=0.3),
        step(2, "（回一面两销）精铣机座顶面（0.5），高度 62 ± 0.05，平面度 0.02，Ra 1.6", "T01", "G09", face_mill(100, 10, 220, 0.06, 197, 522, 0.5), vc=220, f=0.6, ap=0.5),
        step(3, "铣针板座深 2.5 ± 0.03、滑板座深 1.5 ± 0.05（立铣刀，环切）", "T02", "G12", {"tb": 4.0}, vc=180, f=0.05 * 4),
        step(4, "钻 4 × Ø2.5 深 8、攻 M3-6H 深 6", "T06", "G06", {"tb": drill(2.5, 0.06, 50, 8, 4)["tb"] + tap(3, 0.5, 6, 6, 4)["tb"]}, vc=50, f=0.06),
        step(5, "钻 Ø8.0、铰 Ø8.2 H11 铰链销孔（两个耳）", "T07", "G08", {"tb": drill(8, 0.18, 70, 26, 2)["tb"] + bore(8.2, 0.3, 15, 26)["tb"] * 2}, vc=70, f=0.18),
    ]
    o50["inspect"] = [dict(char="机座高度 62 ± 0.05（C3）", gauge="G01", freq="首件、每 5 件"), dict(char="顶面平面度 0.02、对 A 平行度 0.03（C2）", gauge="G09", freq="每件"),
                      dict(char="针板座深 2.5 ± 0.03（C4）", gauge="G12", freq="每件"), dict(char="M3-6H", gauge="G06", freq="每件")]
    ops.append(o50)
    ops.append(dict(seq=60, operation="零件检验 Part inspection", workstation="检验站 QC-01", shop="检验", final_inspection=True,
                    content="下件到合箱之前的检验：A–工艺孔坐标系测底面、顶面、高度、针板座、工艺孔；首件 X 光。孔系在合件（WQLS-HSG-P）上检验",
                    datum="底面 A、两工艺孔", clamping="三坐标测量夹具", minutes=12, setup_min=10, steps=[],
                    inspect=[dict(char=c["id"], gauge={"C10": "G10"}.get(c["id"], "G01"), freq="每件" if c.get("key") else "每 5 件") for c in chars]))
    return dict(item="HSG-LS-L", name="机壳下件（机座）", drawing_no="WQLS-HSG-L", tools=tools, gauges=gauges, chars=chars, ops=ops, holes=holes,
                blank_mass=BLANK_MASS["lower"], part_mass=8.65)


# ---------------------------------------------------------------- 机壳合件 HSG-LS-P（G5.2：合箱、打锥销，一次装夹精加工两件上的全部孔系）
def pair():
    tools = [
        dict(id="T01", name="直角铣头", spec="90° 直角铣头（HSK-A63，回转定位 ±0.005）：机座底下向上钻铰锥销孔（工序 70）；从上面钻攻顶盖螺孔（工序 80）", ops=[70, 80]),
        dict(id="T02", name="钻头 Ø8.5", spec="整体硬质合金钻 Ø8.5，加长（从机座底下穿过下件凸台，进上件工艺孔）", ops=[70]),
        dict(id="T03", name="锥度铰刀 1:50", spec="1:50 锥度铰刀（粗、精两把），按 GB/T 117 锥销 10 × 40 的小端 Ø10 铰到锥销打入后露出 3–4 mm", ops=[70]),
        dict(id="T04", name="测头", spec="主轴测头（单点重复性 1 μm），曲柄测针 Ø3 球、杆长 50；测针偏置每班在标准环上标定", ops=[70]),
        dict(id="T05", name="面铣刀 Ø63", spec="Ø63 五刃可转位面铣刀（K20，修光刃），面板口端面、电机法兰端面", ops=[70]),
        dict(id="T06", name="旋梭轴孔阶梯精镗杆", spec="Ø18 硬质合金杆 ＋ Ø12 颈部，半精镗刀 Ø13.7、微调精镗刀 Ø14（调整精度 0.002）", ops=[70]),
        dict(id="T07", name="上轴同轴镗杆（半精、精）", spec="Ø28 减振杆，前刀 Ø34.7 / Ø35、后刀 Ø31.7 / Ø32 相距 344，尾部 Ø17 导向柱进右支架旋转导向套", ops=[70]),
        dict(id="T08", name="下轴同轴镗杆（半精、精）", spec="Ø26 减振杆，两刀 Ø31.7 / Ø32 相距 276，尾部 Ø17 导向柱穿过左端壁 Ø20 孔进左支架旋转导向套", ops=[70]),
        dict(id="T09", name="精镗刀 Ø20", spec="微调精镗刀 Ø16–Ø22（轴过孔）", ops=[70]),
        dict(id="T10", name="立铣刀 Ø20", spec="Ø20 四刃硬质合金立铣刀，圆弧插补精铣电机止口外圆", ops=[70]),
        dict(id="T11", name="钻头 Ø4.2、丝锥 M5", spec="硬质合金钻 Ø4.2；M5 丝锥（6H）", ops=[80]),
        dict(id="T12", name="钻头 Ø3.3、丝锥 M4", spec="硬质合金钻 Ø3.3；M4 丝锥（6H）", ops=[80]),
        dict(id="T13", name="中心钻", spec="Ø6 90° 定心钻", ops=[80]),
        dict(id="T14", name="摆轴孔镗杆（半精、精）", spec="Ø12 硬质合金减振杆，有效伸出 230；微调镗头 Ø13.7 / Ø14、Ø15.7 / Ø16（调整精度 0.002）", ops=[70]),
        dict(id="T15", name="加长钻头 Ø9.7、加长铰刀 Ø10 H7", spec="硬质合金，有效长 125（从右端壁、右横筋的 Ø14 工艺孔伸进去）", ops=[70]),
        dict(id="T16", name="碗形堵盖压装工具", spec="Ø14、Ø16、Ø18 碗形堵盖（DIN 443，涂厌氧密封胶）的压头", ops=[80]),
        dict(id="T17", name="钻头 Ø4.8 / Ø5.8 / Ø7.8、铰刀 Ø5 / Ø6 / Ø8 H7", spec="硬质合金；G4.7 操纵件的轴孔、销孔（Ø6 加长一套，有效长 80，钻 C1 销孔）", ops=[80]),
        dict(id="T18", name="钻头 Ø16.5、丝锥 M18 × 1.5", spec="直角铣头用，机头顶上的调压螺钉孔", ops=[80]),
        dict(id="T19", name="加长钻头 Ø12", spec="直角铣头用，有效长 100：机座底下向上钻针距拉杆、膝抬推杆过孔（拉杆孔穿过机座顶板和立柱下横隔板）", ops=[80]),
    ]
    gauges = [
        dict(id="G01", name="三坐标测量机（MPE_E = 1.8 + L/300 μm）"),
        dict(id="G02", name="气动量仪 + Ø35 H7、Ø32 H7、Ø14 H7 气动塞规"),
        dict(id="G03", name="内径千分表 10–35 mm（0.001）"),
        dict(id="G04", name="Ø20 H11 塞规"),
        dict(id="G05", name="外径千分尺 50–75 mm（0.001）"),
        dict(id="G06", name="螺纹塞规 M5-6H、M4-6H"),
        dict(id="G07", name="表面粗糙度仪"),
        dict(id="G09", name="大理石平板 00 级 + 杠杆千分表（0.002）"),
        dict(id="G13", name="液压涨紧测量塞规 Ø12 两个（零间隙，测量段 Ø12 h4 × 20，经检定）：工序 70 测针杆轴线用"),
        dict(id="G14", name="合箱找正检棒 Ø12 h5 × 260（插进针杆两孔，下端伸到针板座）＋ 针板孔基准检具（装在针板座里，中间 Ø12 H6 衬套）"),
        dict(id="G15", name="扭力扳手 20–100 N·m"),
        dict(id="G16", name="锥销接触检查（红丹）"),
        dict(id="G17", name="0.02 塞尺"),
    ]
    chars = [
        dict(id="P1", name="针杆孔轴线对旋梭轴孔轴线的位置度", spec="Ø0.05，即 y 向偏离 ±0.025（针杆轴线与旋梭轴线垂直相交）", nominal=0.0, es=0.025, ei=-0.025,
             kind="geo", key=True),
        dict(id="P2", name="针杆孔轴线对上轴孔公共轴线 B 的位置度", spec="Ø0.05（针杆轴线与 B 垂直相交，x = 0）", nominal=0.0, es=0.05, ei=0.0, kind="geo", key=True),
        dict(id="P3", name="前轴承孔（6202）", spec="Ø35 H7（+0.025/0），Ra 1.6", nominal=35, es=0.025, ei=0.0, kind="dim", key=True,
             qms="前轴承孔 Front bearing bore Ø35 H7 (mm)"),
        dict(id="P4", name="后轴承孔（6201）", spec="Ø32 H7（+0.025/0），Ra 1.6", nominal=32, es=0.025, ei=0.0, kind="dim", key=True,
             qms="后轴承孔 Rear bearing bore Ø32 H7 (mm)"),
        dict(id="P5", name="上轴两孔同轴度", spec="Ø0.02（公共轴线 B）", nominal=0.0, es=0.02, ei=0.0, kind="geo", key=True),
        dict(id="P6", name="上轴中心高（B 到底面 A）", spec="262 ± 0.05", nominal=262, es=0.05, ei=-0.05, kind="dim", key=True, qms="上轴中心高 Shaft height above A (mm)"),
        dict(id="P7", name="下轴两孔（6201）", spec="2 × Ø32 H7（+0.025/0），Ra 1.6", nominal=32, es=0.025, ei=0.0, kind="dim", key=True),
        dict(id="P8", name="下轴两孔同轴度", spec="Ø0.02（公共轴线 D）", nominal=0.0, es=0.02, ei=0.0, kind="geo", key=True),
        dict(id="P9", name="旋梭轴孔", spec="Ø14 H7（+0.018/0），Ra 1.6（压两个铜套）", nominal=14, es=0.018, ei=0.0, kind="dim", key=True),
        dict(id="P10", name="旋梭轴孔中心高（到底面 A）", spec="40.5 ± 0.05", nominal=40.5, es=0.05, ei=-0.05, kind="dim"),
        dict(id="P11", name="齿轮中心距（旋梭轴孔—下轴孔）", spec="31.058 ± 0.015", nominal=31.058, es=0.015, ei=-0.015, kind="dim", key=True),
        dict(id="P12", name="旋梭轴孔对下轴公共轴线 D 的平行度", spec="0.012/100（斜齿轮 6 级的轴线平行度）", nominal=0.0, es=0.012, ei=0.0, kind="geo"),
        dict(id="P13", name="上轴 B 对下轴 D 的平行度", spec="0.03/300（同步带两轮对齐）", nominal=0.0, es=0.03, ei=0.0, kind="geo"),
        dict(id="P14", name="电机止口", spec="Ø52 h7（0/−0.030），Ra 1.6", nominal=52, es=0.0, ei=-0.030, kind="dim", key=True),
        dict(id="P15", name="电机止口对 B 的同轴度", spec="Ø0.03", nominal=0.0, es=0.03, ei=0.0, kind="geo"),
        dict(id="P16", name="电机法兰端面对 B 的垂直度", spec="0.02", nominal=0.0, es=0.02, ei=0.0, kind="geo"),
        dict(id="P17", name="针杆轴线对针板座（合箱找正）", spec="Ø0.1：找正检棒插进针板孔基准检具的 Ø12 H6 衬套", nominal=0.0, es=0.1, ei=0.0, kind="geo"),
        dict(id="P18", name="合箱：接合面贴合、螺钉、锥销", spec="0.02 塞尺塞不进；4 × M10（10.9 级）45 N·m 对角两次拧紧；2 × 锥销 10 × 40（GB/T 117，1:50）红丹接触 ≥ 75%、露出 3–4 mm",
             kind="other", key=True),
        dict(id="P19", name="配对编号", spec="上、下件在立柱脚打同一配对编号，此后不得与别的件互换", kind="other"),
        dict(id="P20", name="螺纹孔", spec="电机座 4 × M5-6H ↧9（PCD 40）；面板口 4 × M4-6H、前窗口 6 × M4-6H、顶盖 4 × M4-6H", kind="other"),
        dict(id="P21", name="轴过孔、面板口端面", spec="轴过孔 Ø20 H11；面板口端面平面度 0.1，Ra 3.2", kind="other"),
        # G4.6 送布组的孔（都在下件机座里，合件一次装夹加工）
        dict(id="P22", name="送布摆轴两孔", spec="2 × Ø14 H7（+0.018/0），Ra 1.6，压含油轴套 Ø10 × Ø14", nominal=14, es=0.018, ei=0.0, kind="dim", key=True),
        dict(id="P23", name="送布摆轴两孔同轴度", spec="Ø0.04（公共轴线 F）", nominal=0.0, es=0.04, ei=0.0, kind="geo"),
        dict(id="P24", name="抬牙摆轴孔", spec="前 Ø16 H7（+0.018/0）、后 Ø14 H7（+0.018/0），Ra 1.6", nominal=14, es=0.018, ei=0.0, kind="dim", key=True),
        dict(id="P25", name="抬牙摆轴两孔同轴度", spec="Ø0.03（公共轴线 L）", nominal=0.0, es=0.03, ei=0.0, kind="geo"),
        dict(id="P26", name="调节器轴孔", spec="Ø10 H7（+0.015/0），Ra 1.6", nominal=10, es=0.015, ei=0.0, kind="dim"),
        dict(id="P27", name="送布摆轴、抬牙摆轴、调节器轴的位置", spec="对旋梭轴孔 ± 0.1（y、z）；F、L 对下轴公共轴线 D 的平行度 0.05/100", kind="other"),
        dict(id="P28", name="压脚与操纵件的轴孔、销孔（G4.7）", spec="夹线柱 Ø5 H7；针距旋钮、倒缝扳手、手抬扳手轴孔 Ø8 H7；松线轴、C1、C2、松线拨杆 Ø6 H7；位置 ± 0.1",
             nominal=6, es=0.012, ei=0.0, kind="dim"),
        dict(id="P29", name="调压螺钉孔", spec="M18 × 1.5-6H 螺纹深 15（机头顶，压脚杆轴线上）", kind="other"),
    ]
    holes = {
        "前轴承孔": [(20, 34.0, 0.1, 0.0), (70, 34.7, 0.039, 0.0), (70, 35.0, 0.025, 0.0)],
        "后轴承孔": [(20, 31.0, 0.1, 0.0), (70, 31.7, 0.039, 0.0), (70, 32.0, 0.025, 0.0)],
        "下轴孔": [(30, 31.0, 0.1, 0.0), (70, 31.7, 0.039, 0.0), (70, 32.0, 0.025, 0.0)],
        "旋梭轴孔": [(30, 13.0, 0.1, 0.0), (70, 13.7, 0.027, 0.0), (70, 14.0, 0.018, 0.0)],
        "电机止口（外圆）": [(20, 53.0, 0.0, -0.1), (70, 52.0, 0.0, -0.030)],
        "轴过孔": [(20, 18.0, 0.2, 0.0), (70, 20.0, 0.13, 0.0)],
        "送布摆轴孔": [(70, 13.7, 0.027, 0.0), (70, 14.0, 0.018, 0.0)],
        "抬牙摆轴前孔": [(70, 15.7, 0.027, 0.0), (70, 16.0, 0.018, 0.0)],
        "调节器轴孔": [(70, 9.7, 0.036, 0.0), (70, 10.0, 0.015, 0.0)],
    }
    ops = []
    o60 = dict(seq=60, operation="部件装配 Sub-assembly", workstation="装配工位 ASM-01", shop="装配",
               content="下件以底面 A 和两个工艺孔装在合箱台上，针板座里装针板孔基准检具；两接合面清洁后放上上件，套上 4 个 M10 螺钉（不拧紧）。"
                       "找正检棒从机头上面的针杆孔插入，用立柱脚两侧的顶丝微调上件，直到检棒下端顺利插进检具的 Ø12 H6 衬套；"
                       "对角分两次拧紧 4 个 M10 到 45 N·m，再插一次检棒复查。锥销孔在工序 70 钻铰（只能从机座底下往上钻，见细则 G5.2 偏差 2）",
               datum="下件底面 A、两工艺孔；上件针杆孔（找正）", clamping="合箱台 3 点压板压下件底边法兰", fixture="合箱台 FX-HSG-P-60 ＋ 针板孔基准检具",
               minutes=12, setup_min=5,
               steps=[dict(step=1, content="清洁接合面，下件装上合箱台，装针板孔基准检具", tool="", gauge="G14", tb_min=0, ta_min=3.0),
                      dict(step=2, content="放上上件，插找正检棒，微调到检棒插进衬套", tool="", gauge="G14", tb_min=0, ta_min=5.0),
                      dict(step=3, content="4 × M10 对角分两次拧到 45 N·m，复查检棒；0.02 塞尺查接合面", tool="", gauge="G15", tb_min=0, ta_min=2.5)],
               inspect=[dict(char="找正检棒插进衬套（P17）", gauge="G14", freq="每件"), dict(char="M10 拧紧力矩、接合面贴合（P18）", gauge="G15", freq="每件")])
    ops.append(o60)
    s3 = 3 * math.pi / 180 / 3600
    o70 = dict(seq=70, operation="镗轴承孔 Bearing-bore boring", workstation="卧式加工中心 HMC-01", shop="机加",
               content="合件以下件底面 A ＋ 两个工艺孔 Ø10 H7 定位（液压圆柱涨销 ＋ 削边涨销，零间隙），4 个液压回转压板压在机座顶面四角，正对支承钉。"
                       "① 直角铣头在夹具框里、机座底下，向上钻、铰两个锥销孔，打锥销，打配对编号；"
                       "② 针杆上、下孔各插一个液压涨紧测量塞规，测头在 B 0° 测两个塞规（下塞规在机座和机头之间的空当里，上塞规经面板口），"
                       "算出针杆轴线，写进工件坐标系（旋梭轴孔、上轴两孔的 y 坐标取这条轴线外推到 z −21.5、z 200 处的值），取下塞规；"
                       "③ B 0°：精铣面板口端面，阶梯镗杆半精镗、精镗旋梭轴孔 Ø14 H7，同轴镗杆（右支架导向套）半精镗、精镗上轴两孔；"
                       "④ B 180°：镗轴过孔 Ø20、精铣电机法兰端面、圆弧插补精铣止口 Ø52 h7，同轴镗杆（左支架导向套）半精镗、精镗下轴两孔；"
                       "⑤ 送布组的孔（G4.6）：B 180° 送布摆轴后孔、调节器孔，B 0° 送布摆轴前孔、抬牙摆轴两孔，镗杆都从端壁的工艺孔伸进去。"
                       "精镗前夹紧力降到 40%",
               datum="下件底面 A、两工艺孔（一面两销）",
               clamping="4 个液压回转压板压在机座顶面四角，正对 4 个支承钉；精镗时油压降到 40%", fixture="专用夹具 FX-HSG-P-70（框架式，带左、右两个可翻导向套支架）",
               coolant="干切；精镗用油雾；铰锥销孔用切削油", setup_min=50, fixture_id="FX-HSG-P-70",
               locate=[dict(surface="下件底面 A", symbol="plane", dof=3), dict(surface="工艺孔 1（圆柱涨销）", symbol="pin", dof=2),
                       dict(surface="工艺孔 2（削边涨销）", symbol="pin_diamond", dof=1)],
               clamp=[dict(surface="机座顶面四角（液压回转压板）", kind="hydraulic")])
    o70["steps"] = [
        step(1, "直角铣头（机座底下，向上）：钻 2 × Ø8.5 穿过下件销孔凸台（16），与上件工艺孔 Ø9 对通", "T02", "", drill(8.5, 0.15, 60, 28, 2), vc=60, f=0.15),
        step(2, "粗铰、精铰 1:50 锥销孔（两孔）", "T03", "G16", {"tb": 2 * 2 * bore(10, 0.15, 8, 34)["tb"]}, vc=8, f=0.15),
        step(3, "打入锥销 10 × 40，检查露出 3–4 mm；打配对编号", "", "G16", {"tb": 0.0}, ta=1.5),
        step(4, "插两个测量塞规（上塞规经面板口放进上导套孔）；测头 B 0° 测下塞规（z 30）、上塞规（z 190）各 3 点，算针杆轴线，写入工件坐标系；取下塞规",
             "T04", "G13", {"tb": 0.6}, ta=3.0),
        step(5, "B 0°（机头端）：精铣面板口端面（0.5），平面度 0.1", "T05", "G09", face_mill(63, 5, 200, 0.08, 112, 120, 0.5), vc=200, f=0.4, ap=0.5),
        step(6, "B 0°：阶梯镗杆从左端壁 Ø20 孔伸进去，半精镗旋梭轴孔 Ø13.0 → Ø13.7（+0.027/0）", "T06", "G03", bore(13.7, 0.10, 120, 42), vc=120, f=0.10, ap=0.35),
        step(7, "B 0°：精镗旋梭轴孔 Ø14 H7，Ra 1.6（测孔径后微调到中差）", "T06", "G02", bore(14, 0.05, 140, 42), vc=140, f=0.05, ap=0.15, ta=0.8),
        step(8, "B 0°：翻上右导向套支架，压板油压降到 40%；同轴镗杆两孔一刀半精镗 Ø34.7、Ø31.7（+0.039/0）", "T07", "G03",
             bore(34.7, 0.12, 140, 22), vc=140, f=0.12, ap=0.35, ta=1.0),
        step(9, "B 0°：同轴精镗杆两孔一刀精镗 Ø35 H7、Ø32 H7，Ra 1.6（进、退刀时主轴定向、刀尖朝上，抬高 1 mm）；支架翻下，油压恢复", "T07", "G02",
             bore(35, 0.06, 150, 22), vc=150, f=0.06, ap=0.15, ta=1.0),
        step(10, "B 180°（电机端）：镗轴过孔 Ø18 → Ø20 H11", "T09", "G04", bore(20, 0.12, 120, 40), vc=120, f=0.12, ap=1.0),
        step(11, "B 180°：精铣电机法兰端面（0.5），对 B 垂直度 0.02", "T05", "G09", face_mill(63, 5, 200, 0.08, 57, 57, 0.5), vc=200, f=0.4, ap=0.5),
        step(12, "B 180°：圆弧插补精铣止口 Ø52 h7（0/−0.030），Ra 1.6", "T10", "G05", interp_od(52, 20, 4, 0.05, 180, 1, 12), vc=180, f=0.2, ap=0.5),
        step(13, "B 180°：翻上左导向套支架，油压降到 40%；下轴镗杆从右端壁 Ø34 孔伸进去，两孔一刀半精镗 Ø31.0 → Ø31.7（+0.039/0）", "T08", "G03",
             bore(31.7, 0.12, 140, 16), vc=140, f=0.12, ap=0.35, ta=1.0),
        step(14, "B 180°：精镗下轴两孔 Ø32 H7，Ra 1.6，位置取旋梭轴孔（测出的针杆轴线）＋ 中心距 31.058；支架翻下，油压恢复", "T08", "G02",
             bore(32, 0.06, 150, 16), vc=150, f=0.06, ap=0.15, ta=1.0),
        # G4.6 送布组的孔：都用砂芯铸出（抬牙摆轴前孔 Ø15、调节器孔 Ø6，其余比成品小 3，见 cad/blank.py），这里半精、精两刀
        step(15, "B 180°：摆轴镗杆从右端壁、右横筋的 Ø16 工艺孔伸进去，半精镗、精镗送布摆轴后孔 Ø14 H7（x 296…311）", "T14", "G02",
             {"tb": bore(13.7, 0.10, 120, 15)["tb"] + bore(14, 0.05, 140, 15)["tb"]}, vc=140, f=0.05, ap=0.15, ta=0.8),
        step(16, "B 180°：加长钻、铰调节器轴孔 Ø10 H7（x 296…311，从 Ø14 工艺孔进）", "T15", "G03",
             {"tb": drill(9.7, 0.12, 70, 15, 1)["tb"] + bore(10, 0.2, 12, 15)["tb"]}, vc=12, f=0.2),
        step(17, "B 0°：摆轴镗杆从左端壁 Ø16 工艺孔伸进去，半精镗、精镗送布摆轴前孔 Ø14 H7（x 33…47），与后孔同一轴线 F", "T14", "G02",
             {"tb": bore(13.7, 0.10, 120, 14)["tb"] + bore(14, 0.05, 140, 14)["tb"]}, vc=140, f=0.05, ap=0.15, ta=0.8),
        step(18, "B 0°：从左端壁 Ø18 工艺孔进，镗刀穿过抬牙摆轴前孔（铸出 Ø15）半精镗、精镗后孔 Ø14 H7（x 95…107）", "T14", "G02",
             {"tb": bore(13.7, 0.10, 120, 12)["tb"] + bore(14, 0.05, 140, 12)["tb"]}, vc=140, f=0.05, ap=0.15, ta=0.8),
        step(19, "B 0°：半精镗、精镗抬牙摆轴前孔 Ø16 H7（x 24…38）", "T14", "G02",
             {"tb": bore(15.7, 0.10, 120, 14)["tb"] + bore(16, 0.05, 140, 14)["tb"]}, vc=140, f=0.05, ap=0.15, ta=0.8),
    ]
    import g5_precision as PRC
    bud = PRC.pair_budgets()
    o70["accuracy"] = [dict(char=c, T=T, items=[dict(name=i["name"], range=i["range"], kind=i["kind"]) for i in bud[k]["items"]])
                       for c, k, T in (("P1", "针杆孔对旋梭轴孔 位置度 Ø0.05", 0.05), ("P2", "针杆孔对上轴孔 B 位置度 Ø0.05", 0.05),
                                       ("P5", "上轴两孔同轴度 Ø0.02", 0.02), ("P8", "下轴两孔同轴度 Ø0.02", 0.02),
                                       ("P11", "齿轮中心距 31.058 ± 0.015", 0.03), ("P6", "上轴中心高 262 ± 0.05（对 A）", 0.10),
                                       ("P13", "上轴对下轴平行度 0.03/300", 0.03),
                                       ("P23", "送布摆轴两孔同轴度 Ø0.04", 0.04), ("P25", "抬牙摆轴两孔同轴度 Ø0.03", 0.03))]
    o70["inspect"] = [dict(char="前、后轴承孔 Ø35 H7、Ø32 H7（P3、P4）", gauge="G02", freq="每件"), dict(char="下轴两孔 Ø32 H7（P7）", gauge="G02", freq="每件"),
                      dict(char="旋梭轴孔 Ø14 H7（P9）", gauge="G02", freq="每件"), dict(char="止口 Ø52 h7（P14）", gauge="G05", freq="每件"),
                      dict(char="送布摆轴、抬牙摆轴孔 Ø14 / Ø16 H7（P22、P24）", gauge="G02", freq="每件"), dict(char="调节器轴孔 Ø10 H7（P26）", gauge="G03", freq="每件"),
                      dict(char="锥销孔接触 ≥ 75%（P18）", gauge="G16", freq="首件、每 10 件"),
                      dict(char="针杆轴线测量值（在机，留记录）；两孔同轴度、中心距（在机测头抽检）", gauge="G01", freq="首件、每 10 件")]
    ops.append(o70)
    o80 = dict(seq=80, operation="钻攻螺纹孔 Drilling & tapping", workstation="卧式加工中心 HMC-01", shop="机加",
               content="同工序 70 的夹具。B 180° 钻攻电机座 4 × M5（PCD 40）；B 0° 钻攻面板口 4 × M4；B 270° 钻攻前窗口 6 × M4；直角铣头从上面钻攻顶盖 4 × M4；"
                       "G4.7 压脚与操纵件的轴孔、销孔（B 270°、B 90°、直角铣头从上面、机座底下、机臂下面）",
               datum="下件底面 A、两工艺孔（一面两销）", clamping="同工序 70", fixture="专用夹具 FX-HSG-P-70", coolant="攻丝用切削油", setup_min=10, fixture_id="FX-HSG-P-70")
    o80["steps"] = [
        step(1, "定心全部 18 个孔", "T13", "", drill(6, 0.08, 60, 1.5, 18), vc=60, f=0.08),
        step(2, "钻 4 × Ø4.2 深 14、攻 M5-6H 深 10", "T11", "G06", {"tb": drill(4.2, 0.1, 60, 14, 4)["tb"] + tap(5, 0.8, 8, 10, 4)["tb"]}, vc=60, f=0.1),
        step(3, "钻 14 × Ø3.3 深 12、攻 M4-6H 深 8", "T12", "G06", {"tb": drill(3.3, 0.08, 60, 12, 14)["tb"] + tap(4, 0.7, 8, 8, 14)["tb"]}, vc=60, f=0.08),
        # G4.7 压脚与操纵件的孔（g5_cam.ctrl_holes）
        step(4, "B 270°：钻、铰夹线柱孔 Ø5 H7（机臂前壁）；钻、铰针距旋钮轴孔、倒缝扳手轴孔 2 × Ø8 H7（立柱前壁）", "T17", "G03",
             {"tb": drill(4.8, 0.08, 60, 7, 1)["tb"] + drill(7.8, 0.1, 60, 12, 2)["tb"] + bore(8, 0.25, 12, 12)["tb"] * 2 + bore(5, 0.2, 12, 7)["tb"]}, vc=60, f=0.1),
        step(5, "B 90°：钻、铰手抬扳手轴孔 Ø8 H7、松线轴孔 Ø6 H7、C2 销孔 Ø6 H7（机头后壁）；加长钻、铰 C1 销孔 Ø6 H7 深 71（立柱后壁）", "T17", "G03",
             {"tb": drill(7.8, 0.1, 60, 22, 1)["tb"] + drill(5.8, 0.08, 60, 27, 2)["tb"] + drill(5.8, 0.06, 50, 71, 1)["tb"] + bore(6, 0.2, 12, 27)["tb"] * 4},
             vc=60, f=0.08),
        step(6, "直角铣头从上面：钻机头顶调压螺钉底孔 Ø16.5 深 23、攻 M18 × 1.5 深 15", "T18", "G06",
             {"tb": drill(16.5, 0.15, 70, 23, 1)["tb"] + tap(18, 1.5, 8, 15, 1)["tb"]}, vc=70, f=0.15),
        step(7, "直角铣头在机座底下向上：钻针距拉杆过孔 Ø12（穿机座顶板、立柱下横隔板）、膝抬推杆过孔 Ø12", "T19", "",
             {"tb": drill(12, 0.12, 60, 82, 1)["tb"] + drill(12, 0.12, 60, 18, 1)["tb"]}, vc=60, f=0.12),
        step(8, "直角铣头伸进机臂下面的空档向上：钻、铰松线拨杆座孔 Ø6 H7 深 10", "T17", "G03", {"tb": drill(5.8, 0.08, 60, 10, 1)["tb"] + bore(6, 0.2, 12, 10)["tb"]},
             vc=60, f=0.08),
        step(9, "卸下后清洗，压 4 个碗形堵盖：左端壁 Ø16、Ø18，右端壁 Ø16、Ø14（右横筋上的两个工艺孔在机座里面，不堵）", "T16", "", {"tb": 0.0}, ta=2.5),
    ]
    o80["inspect"] = [dict(char="M5-6H、M4-6H、M18 × 1.5-6H（P20、P29）", gauge="G06", freq="每件"),
                      dict(char="操纵件轴孔、销孔 Ø5 / Ø6 / Ø8 H7（P28）", gauge="G03", freq="首件、每 5 件")]
    ops.append(o80)
    ops.append(dict(seq=90, operation="零件检验 Part inspection", workstation="检验站 QC-01", shop="检验", final_inspection=True,
                    content="清洗后在恒温室（20 ± 1 ℃，工件等温 4 h）三坐标全检：按《机壳三坐标检测计划》以下件 A 与两工艺孔建坐标系，"
                            "测针杆孔、旋梭轴孔、上轴两孔、下轴两孔的位置与相互关系（P1–P16）；检查配对编号",
                    datum="下件底面 A、两工艺孔（与精加工同一基准）", clamping="三坐标测量夹具（一面两销）", minutes=30, setup_min=10, steps=[],
                    inspect=[dict(char=c["id"], gauge={"P18": "G16", "P20": "G06"}.get(c["id"], "G01"), freq="每件" if c.get("key") else "每 5 件")
                             for c in chars]))
    chains = [dict(name="针杆孔对旋梭轴孔（合件：测出针杆轴线后镗旋梭轴孔）", char="P1",
                   links=[dict(name=i["name"], nominal=0.0, es=round(i["range"] / 2, 4), ei=-round(i["range"] / 2, 4), sense=1)
                          for i in bud["针杆孔对旋梭轴孔 位置度 Ø0.05"]["items"]])]
    del s3
    return dict(chains=chains, item="HSG-LS-P", name="机壳合件（上件＋下件，配对）", drawing_no="WQLS-HSG-P", tools=tools, gauges=gauges, chars=chars, ops=ops,
                holes=holes, blank_mass=BLANK_MASS["upper"] + BLANK_MASS["lower"], part_mass=24.2,
                blank_kind="上件 HSG-LS-U ＋ 下件 HSG-LS-L（各自粗加工、时效、精铣接合面后）")


# ---------------------------------------------------------------- 组装、核对
def finish_minutes(o):
    """单件工时 = 机动时间 + 辅助时间（工步辅助、换刀）+ 布置工作地与休息（按 12%），保留 0.5 min"""
    tb = sum(s["tb_min"] for s in o.get("steps") or [])
    ta = sum(s.get("ta_min") or 0 for s in o.get("steps") or []) + TA_TOOL * len({s["tool"] for s in o.get("steps") or []}) + 1.5
    return math.ceil((tb + ta) * 1.12 * 2) / 2, round(tb, 2)


def hole_check(holes):
    """孔：单边余量 z = (本道下限 − 上道上限) / 2；外圆反过来。余量必须 > 0，精镗、精铰的最小余量 ≥ 0.05（单边）"""
    out = []
    for name, seq in holes.items():
        outer = "外圆" in name
        for (a, da, esa, eia), (b, db, esb, eib) in zip(seq, seq[1:]):
            if outer:
                zmin = ((da + eia) - (db + esb)) / 2
                zmax = ((da + esa) - (db + eib)) / 2
            else:
                zmin = ((db + eib) - (da + esa)) / 2
                zmax = ((db + esb) - (da + eia)) / 2
            out.append(dict(feature=name, from_=a, to=b, d_from=da, d_to=db, z_min=round(zmin, 3), z_max=round(zmax, 3),
                            ok=zmin > 0 and (zmin >= 0.05 or db - da < 0.4)))
    return out


def power_check(ops):
    """端铣的切削功率（Kienzle）除以传动效率，不得超过主电机功率"""
    out = []
    for o in ops:
        pw = POWER.get(o["workstation"])
        for s in o.get("steps") or []:
            if pw and s.get("_P"):
                out.append(dict(seq=o["seq"], step=s["step"], P_kw=s["_P"], need_kw=round(s["_P"] / pw[1], 2), motor_kw=pw[0],
                                ok=s["_P"] / pw[1] <= pw[0]))
    return out


def build(P):
    ops = []
    for o in P["ops"]:
        o = dict(o)
        if o.get("steps"):
            for s in o["steps"]:
                s.pop("_n", None)
                s.pop("_P", None)
                if s.get("gauge") == "":
                    s.pop("gauge")
            o["minutes"], tb = finish_minutes(o)
        o.pop("fixture_id", None) if not o.get("fixture_id") else None
        ops.append(o)
    plan = dict(version=2, item=P["item"], material="HT250", batch=200,
                doc=dict(number=f"GY-{P['item']}", revision="A", product_model="WQ-LS", product_name="WQ-LS 工业平缝机", drawing_no=P["drawing_no"],
                         part_name=P["name"], per_unit=1, per_blank=1, batch=200, factory="问渠数字工厂",
                         signatures={k: dict(by=v, date=DATE) for k, v in (("prepared", "工艺员（AI 起草）"), ("checked", "工艺主管"),
                                                                            ("standardized", "标准化员"), ("approved", "技术负责人"))}, changes=[]),
                part=dict(kind="housing", mass_kg=P["part_mass"], source="tools/wqls/cad/housing.py（G5.2）"),
                blank=dict(kind=P.get("blank_kind", "铸件"), spec=f"HT250 砂型铸件 {P['blank_mass']} kg" if "blank_kind" not in P else "", length_mm="", material_item=f"CS-{P['item']}",
                           drawing="docs/设计/WQ-LS/G5/机壳铸造工艺.md"),
                chains=P.get("chains", []), characteristics=P["chars"], tool_list=P["tools"], gauges=P["gauges"], operations=ops,
                hole_sizes={k: [dict(op=a, d=d, es=es, ei=ei) for a, d, es, ei in v] for k, v in P["holes"].items()},
                attachments=[dict(kind="calc", name="机壳机械加工工艺计算（tools/wqls/g5_process.py，切削用量、机动时间、余量、功率）", missing=[])])
    return plan


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "设计" / "WQ-LS" / "G5"
    out.mkdir(parents=True, exist_ok=True)
    import os
    bdir = os.environ.get("WQ_BLANK")
    if bdir:
        for k in ("upper", "lower"):
            BLANK_MASS[k] = round(json.loads((Path(bdir) / f"blank_{k}.json").read_text())["mass_blank_kg"], 2)
    from hub import cards, process as PR
    summary = {}
    for P in (upper(), lower(), pair()):
        import copy
        plan = build(copy.deepcopy(P))
        path = STD / f"{P['item']}_process.yaml"
        path.write_text("# 第 138 轮 G5.1、G5.2：WQ-LS 机壳机械加工工艺规程（由 tools/wqls/g5_process.py 生成，不要手改）\n"
                        + yaml.safe_dump(plan, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
        rv = PR.review(plan)
        ck = cards.check(plan)
        hc = hole_check(P["holes"])
        pc = power_check(P["ops"])
        html = cards.html(plan, title=f"{P['item']} {P['name']} 机械加工工艺卡")
        cn = {"HSG-LS-U": "上件", "HSG-LS-L": "下件", "HSG-LS-P": "合件"}[P["item"]]
        (out / f"工艺卡_{cn}.html").write_text(html, encoding="utf-8")
        pdf = cards.pdf(html, out / f"工艺卡_{cn}.pdf")
        summary[P["item"]] = dict(ops=[(o["seq"], o["operation"].split(" ")[0], o.get("minutes")) for o in plan["operations"]],
                                  total_min=round(sum(o.get("minutes", 0) for o in plan["operations"]), 1),
                                  review=[(r["level"], r["rule"], r["seq"], r["text"]) for r in rv], cards_check=ck,
                                  holes=hc, power=pc, pdf=str(pdf) if pdf else None)
    (out / "工艺规程_核对.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    for k, v in summary.items():
        print(k, "总工时", v["total_min"], "min", v["ops"])
        for r in v["review"]:
            print("  评审", r)
        for c in v["cards_check"]:
            print("  卡片", c)
        for h in v["holes"]:
            if not h["ok"]:
                print("  余量不够", h)


if __name__ == "__main__":
    main()
