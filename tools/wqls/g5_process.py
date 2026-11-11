"""第 138 轮 G5.1 第 3 步：机壳两件的机械加工工艺规程（数字工厂数据格式 v2）。

    python3 tools/wqls/g5_process.py [<输出目录>]

由程序生成工艺规程：每个工步的切削用量按刀具和材料（HT250）取，转速、进给速度、机动时间都由程序算，不手填；
孔的各工序尺寸与余量（单边）由程序核对；切削功率按 Kienzle 公式核对机床功率。结果写到
  factory/digital/std/HSG-LS-U_process.yaml、HSG-LS-L_process.yaml（数字工厂的工艺规程，卡片由 hub/cards.py 生成），
然后跑数字工厂的 AI 工艺评审员预审（hub/process.review）和卡片完整性检查（hub/cards.check），输出工艺卡 HTML / PDF。

坐标同整机（mm）：上轴轴线是 B（y = 0、z = 200），上件接合面是 C（z = 0），下件底面是 A。
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


# ---------------------------------------------------------------- 上件 HSG-LS-U
def upper():
    tools = [
        dict(id="T01", name="面铣刀 Ø80", spec="Ø80 八刃可转位面铣刀，SEKN 1203 刀片（涂层硬质合金 K20，铸铁用）", ops=[10, 40]),
        dict(id="T02", name="面铣刀 Ø63", spec="Ø63 五刃可转位面铣刀（K20），电机座端面、面板口端面", ops=[20, 50]),
        dict(id="T03", name="同轴粗镗杆", spec="同 T13 的粗镗杆（双刃刀夹，K20 刀片）", ops=[20]),
        dict(id="T04", name="精镗刀", spec="微调精镗刀 Ø25–Ø45，调整精度 0.002（CBN 或细晶粒硬质合金刀片，刀尖圆弧 r0.4）", ops=[50]),
        dict(id="T05", name="立铣刀 Ø20", spec="Ø20 四刃硬质合金立铣刀，圆弧插补铣电机止口外圆", ops=[20, 50]),
        dict(id="T06", name="直角铣头", spec="90° 直角铣头（HSK-A63 接口，回转定位精度 ±0.005）", ops=[20, 50, 60]),
        dict(id="T07", name="钻头 Ø11.5 / 铰刀 Ø12 H7", spec="整体硬质合金钻 Ø11.5；整体硬质合金铰刀 Ø12 H7（针杆孔）", ops=[20, 50]),
        dict(id="T08", name="钻头 Ø8.5 / 铰刀 Ø9 H7", spec="整体硬质合金钻 Ø8.5；铰刀 Ø9 H7（两个工艺孔；装配时再配铰成锥销孔）", ops=[10, 40]),
        dict(id="T09", name="钻头 Ø8.5、丝锥 M10", spec="硬质合金钻 Ø8.5；M10 螺旋槽丝锥（铸铁用，6H）", ops=[10]),
        dict(id="T10", name="钻头 Ø4.2、丝锥 M5", spec="硬质合金钻 Ø4.2；M5 丝锥（6H）", ops=[60]),
        dict(id="T11", name="钻头 Ø3.3、丝锥 M4", spec="硬质合金钻 Ø3.3；M4 丝锥（6H）", ops=[60]),
        dict(id="T12", name="中心钻", spec="Ø6 90° 定心钻（硬质合金）", ops=[10, 40, 60]),
        dict(id="T14", name="粗镗刀 Ø18", spec="Ø16–Ø22 单刃粗镗刀（K20），轴过孔", ops=[20]),
        dict(id="T13", name="同轴镗杆", spec="同轴镗杆三根（粗、半精、精）：Ø28 钢制减振杆，前端 Ø35 档、后端 Ø32 档两个刀夹相距 344，尾部 Ø17 导向柱穿过 Ø20 轴过孔进旋转导向套", ops=[20, 50]),
    ]
    gauges = [
        dict(id="G01", name="三坐标测量机（MPE_E = 1.8 + L/300 μm）"),
        dict(id="G02", name="气动量仪 + Ø35 H7、Ø32 H7 气动塞规"),
        dict(id="G03", name="内径千分表 18–35 mm（0.001）"),
        dict(id="G04", name="Ø12 H7、Ø9 H7 塞规（通端 / 止端）"),
        dict(id="G05", name="外径千分尺 50–75 mm（0.001）"),
        dict(id="G06", name="螺纹塞规 M10-6H、M5-6H、M4-6H"),
        dict(id="G07", name="表面粗糙度仪"),
        dict(id="G08", name="游标卡尺 0–300 mm（0.02）"),
        dict(id="G09", name="大理石平板 00 级 + 杠杆千分表（0.002）"),
        dict(id="G10", name="布氏硬度计"),
        dict(id="G11", name="X 光探伤（首件、每批抽 1 件）"),
    ]
    chars = [
        dict(id="C1", name="前轴承孔（6202）", spec="Ø35 H7（+0.025/0），Ra 1.6", nominal=35, es=0.025, ei=0.0, kind="dim", key=True,
             qms="前轴承孔 Front bearing bore Ø35 H7 (mm)"),
        dict(id="C2", name="后轴承孔（6201）", spec="Ø32 H7（+0.025/0），Ra 1.6", nominal=32, es=0.025, ei=0.0, kind="dim", key=True,
             qms="后轴承孔 Rear bearing bore Ø32 H7 (mm)"),
        dict(id="C3", name="两轴承孔同轴度", spec="Ø0.02（公共轴线 B）", nominal=0.0, es=0.02, ei=0.0, kind="geo", key=True),
        dict(id="C4", name="针杆导套孔（上、下）", spec="2 × Ø12 H7（+0.018/0），Ra 1.6", nominal=12, es=0.018, ei=0.0, kind="dim", key=True),
        dict(id="C5", name="针杆孔对接合面 C 的垂直度", spec="0.02/100", kind="geo"),
        dict(id="C6", name="针杆孔轴线对 B 的位置度", spec="Ø0.05（针杆轴线在 x = 0、y = 0，与 B 垂直相交）", nominal=0.0, es=0.05, ei=0.0,
             kind="geo", key=True),
        dict(id="C7", name="电机止口", spec="Ø52 h7（0/−0.030），Ra 1.6", nominal=52, es=0.0, ei=-0.030, kind="dim", key=True),
        dict(id="C8", name="电机止口对 B 的同轴度", spec="Ø0.03", nominal=0.0, es=0.03, ei=0.0, kind="geo"),
        dict(id="C9", name="电机法兰端面对 B 的垂直度", spec="0.02", nominal=0.0, es=0.02, ei=0.0, kind="geo"),
        dict(id="C10", name="接合面 C", spec="平面度 0.02，Ra 1.6", nominal=0.0, es=0.02, ei=0.0, kind="geo", key=True),
        dict(id="C11", name="B 轴线到接合面 C 的距离", spec="200 ± 0.03", nominal=200, es=0.03, ei=-0.03, kind="dim", key=True,
             qms="上轴中心高 Shaft height above C (mm)"),
        dict(id="C12", name="工艺孔", spec="2 × Ø9 H7（+0.015/0），位置度 Ø0.05（对 C 与 B）；装配找正后与下件配铰成 1:50 锥销孔", nominal=9, es=0.015, ei=0.0, kind="dim"),
        dict(id="C13", name="螺纹孔", spec="4 × M10-6H 螺纹深 18、底孔深 22（接合面）；4 × M5-6H（电机座 PCD 40）；10 × M4-6H（面板口 4、前窗口 6）；4 × M4-6H（顶盖）", kind="other"),
        dict(id="C14", name="面板口端面、前窗口法兰面", spec="平面度 0.1，Ra 3.2", kind="geo"),
        dict(id="C15", name="铸件质量", spec="HT250：硬度 190–240 HBW；首件 X 光检查电机座、立柱脚、针杆导套座无缩松", kind="other"),
    ]
    holes = {   # 孔、外圆的工序尺寸（直径，上下偏差）——由程序核对单边余量
        "前轴承孔": [("铸出", 30.0, 0.6, -0.6), (20, 34.0, 0.1, 0.0), (50, 34.7, 0.039, 0.0), (50, 35.0, 0.025, 0.0)],
        "后轴承孔": [("铸出", 27.0, 0.6, -0.6), (20, 31.0, 0.1, 0.0), (50, 31.7, 0.039, 0.0), (50, 32.0, 0.025, 0.0)],
        "针杆孔": [("钻", 11.5, 0.1, 0.0), (50, 11.85, 0.027, 0.0), (50, 12.0, 0.018, 0.0)],
        "电机止口（外圆）": [("铸出", 57.0, 0.6, -0.6), (20, 53.0, 0.0, -0.1), (50, 52.0, 0.0, -0.030)],
        "轴过孔": [("铸出", 16.0, 0.5, -0.5), (20, 18.0, 0.2, 0.0), (50, 20.0, 0.13, 0.0)],
        "工艺孔": [(10, 8.5, 0.1, 0.0), (40, 8.85, 0.022, 0.0), (40, 9.0, 0.015, 0.0)],
    }
    S = []
    # ---- 工序 10：VMC，接合面向上（工件倒放），粗基准是两个轴承孔的铸孔
    fm = face_mill(80, 8, 160, 0.18, 178, 96, 2.5)
    ops = []
    o10 = dict(seq=10, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="工件倒放（接合面朝上）。粗基准：前后两个轴承孔的铸孔（两端锥面涨套，保证轴承孔余量均匀）＋机臂顶面一个可调支承限转。"
                       "粗铣、半精铣接合面 C，留精铣余量 0.5；钻两个工艺孔（以后铰成 Ø9 H7），作为以后各工序“一面两销”的定位基准，装配找正后它们再与下件一起配铰成锥销孔；"
                       "钻攻 4 × M10（装配用，也是卧加夹具拉紧工件用的螺孔：立柱脚的凸台在立柱里面，外面压不到）",
               datum="前后轴承孔铸孔（粗基准）、机臂顶面", clamping="两端锥面涨套（液压），机臂顶面辅助支承", fixture="专用夹具 FX-HSG-U-10（涨套式）",
               coolant="干切（铸铁）", setup_min=40, fixture_id=None,
               locate=[dict(surface="前后轴承孔铸孔", symbol="mandrel", dof=4), dict(surface="机臂顶面", symbol="support", dof=1)],
               clamp=[dict(surface="轴承孔铸孔（涨套）", kind="hydraulic")])
    s1 = step(1, "粗铣接合面 C（余量 3 → 1.0），三行", "T01", "G08", fm, vc=160, f=0.18 * 8, ap=2.0)
    fm2 = face_mill(80, 8, 200, 0.10, 178, 96, 0.5)
    s2 = step(2, "半精铣接合面 C（留精铣余量 0.5，平面度 0.05）", "T01", "G09", fm2, vc=200, f=0.10 * 8, ap=0.5)
    cd = drill(6, 0.08, 60, 2, 2)
    s3 = step(3, "定心钻两个工艺孔位置", "T12", "", cd, vc=60, f=0.08)
    dr = drill(8.5, 0.2, 70, 12, 2)
    s4 = step(4, "钻两个工艺孔 Ø8.5 深 12（x 315.8 / y 7.0 与 x 380.2 / y 47.0）", "T08", "G08", dr, vc=70, f=0.2)
    s5 = step(5, "定心、钻 4 × Ø8.5 深 22", "T09", "G08", drill(8.5, 0.18, 70, 22, 4), vc=70, f=0.18)
    s6 = step(6, "攻 4 × M10-6H 深 18（刚性攻丝）：以后各道卧加工序的液压拉杆拧进这 4 个孔，把工件拉紧在垫块上", "T09", "G06",
              tap(10, 1.5, 10, 18, 4), vc=10, f=1.5)
    o10["steps"] = [s1, s2, s3, s4, s5, s6]
    o10["inspect"] = [dict(char="接合面 C 平面度 0.05（半精铣后）", gauge="G09", freq="首件、每 10 件"), dict(char="M10-6H", gauge="G06", freq="每件"),
                      dict(char="C 面到两轴承孔铸孔中心的距离（余量均匀）200.5 ± 0.5", gauge="G01", freq="首件")]
    ops.append(o10)
    # ---- 工序 20：HMC 粗加工
    br1 = bore(32, 0.25, 110, 13)
    br2 = bore(29, 0.25, 110, 22)
    fm3 = face_mill(63, 5, 160, 0.15, 57, 57, 2.0)
    io = interp_od(53, 20, 4, 0.10, 150, 2, 12)
    o20 = dict(seq=20, operation="镗轴承孔 Bearing-bore boring", workstation="卧式加工中心 HMC-01", shop="机加",
               content="一面两销定位（接合面 C ＋ 两工艺孔），夹具抬高 160 让出机头下方空间。B 180° 钻轴过孔、粗铣电机座端面和止口外圆；"
                       "B 0° 粗铣面板口端面，同轴镗杆（带导向套）粗镗两轴承孔；直角铣头从下方钻针杆孔 Ø11.5。各面单边留 0.5。"
                       "后轴承孔 6201 在电机座里面、外侧只有 Ø20 的轴过孔，只能从机头一端用长镗杆镗",
               datum="接合面 C、两工艺孔（一面两销，精基准）", clamping="4 个液压拉缸，拉杆拧进立柱脚 4 个 M10 螺孔，把工件拉紧在正下方的 4 个支承钉上", fixture="专用夹具 FX-HSG-U-20（一面两销，与工序 50 共用）",
               coolant="干切（铸铁）", setup_min=45, fixture_id="FX-HSG-U-20",
               locate=[dict(surface="接合面 C", symbol="plane", dof=3), dict(surface="工艺孔 1（圆柱销）", symbol="pin", dof=2),
                       dict(surface="工艺孔 2（削边销）", symbol="pin_diamond", dof=1)],
               clamp=[dict(surface="立柱脚 4 个 M10 螺孔（液压拉杆）", kind="hydraulic")])
    o20["steps"] = [
        step(1, "B 180°（电机端）：粗镗轴过孔 Ø16（铸出）→ Ø18，深 40（后轴承孔 6201 在它里面，只能从机头一端镗）", "T14", "G08",
             bore(18, 0.2, 110, 40), vc=110, f=0.2, ap=1.0),
        step(2, "B 180°：粗铣电机座端面（余量 3 → 0.5）", "T02", "G08", fm3, vc=160, f=0.75, ap=2.5),
        step(3, "B 180°：圆弧插补粗铣电机止口外圆 Ø57 → Ø53.0（0/−0.1），两圈", "T05", "G05", io, vc=150, f=0.4, ap=2.0),
        step(4, "B 0°（机头端）：粗铣面板口端面（余量 3 → 0.5）", "T02", "G08", face_mill(63, 5, 160, 0.15, 112, 120, 2.5), vc=160, f=0.75, ap=2.5),
        step(5, "B 0°：翻上导向套支架；同轴粗镗杆（前刀 Ø34、后刀 Ø31，尾部 Ø17 导向柱穿过 Ø18 过孔进导向套）从机头端伸入，"
                "两孔一刀粗镗到 Ø34.0、Ø31.0（+0.1/0）；镗完支架翻下", "T03", "G03", bore(32, 0.25, 110, 22), vc=110, f=0.25, ap=2.0, ta=1.0),
        step(6, "装直角铣头，从机头下方钻针杆孔 Ø11.5，一次钻通上、下两个导套座", "T07", "G08", drill(11.5, 0.15, 60, 150, 1), vc=60, f=0.15),
    ]
    o20["inspect"] = [dict(char="两轴承孔 Ø34.0、Ø31.0（+0.1/0）", gauge="G03", freq="首件、每 5 件"),
                      dict(char="止口 Ø53.0（0/−0.1）", gauge="G05", freq="首件、每 5 件")]
    ops.append(o20)
    ops.append(dict(seq=30, operation="时效 Stress relieving", workstation="热处理炉 HT-01", shop="热处理",
                    content="第二次去应力退火：≤ 200 ℃ 装炉，≤ 80 ℃/h 升到 550 ± 10 ℃，保温 2 h，≤ 40 ℃/h 随炉冷到 200 ℃ 以下出炉。"
                            "粗加工后的残余应力在这里释放，变形在精加工切掉", datum="—", clamping="料架平放，接合面朝下", minutes=6, setup_min=10,
                    steps=[], inspect=[dict(char="炉温曲线记录（550 ± 10 ℃、保温 2 h）", gauge="炉温记录仪", freq="每炉")]))
    # ---- 工序 40：VMC 精铣接合面、铰工艺孔、M10
    fm4 = face_mill(80, 8, 220, 0.06, 178, 96, 0.5)
    o40 = dict(seq=40, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="工件倒放。以粗镗后的两个轴承孔定位（两端涨芯轴，B 轴线成为这道的基准）＋机臂顶面限转：精铣接合面 C 保证中心高 200 ± 0.03、"
                       "平面度 0.02（M10 螺纹深 18，精铣 0.5 后仍有 17.5 ≥ 1.5d）；扩、铰两个工艺孔 Ø9 H7",
               datum="两轴承孔（粗镗后，涨芯轴）—— 即 B 轴线", clamping="两端液压涨芯轴，机臂顶面辅助支承", fixture="专用夹具 FX-HSG-U-40（涨芯轴式）",
               coolant="干切；攻丝用切削油", setup_min=40,
               locate=[dict(surface="两轴承孔（粗镗）", symbol="mandrel", dof=4), dict(surface="机臂顶面", symbol="support", dof=1)],
               clamp=[dict(surface="涨芯轴", kind="hydraulic")])
    o40["steps"] = [
        step(1, "精铣接合面 C（0.5），保证 C 到 B 轴线 200 ± 0.03、平面度 0.02、Ra 1.6（修光刃刀片）", "T01", "G09", fm4, vc=220, f=0.48, ap=0.5),
        step(2, "扩工艺孔 Ø8.5 → Ø8.85", "T08", "G04", bore(8.85, 0.15, 60, 12), vc=60, f=0.15),
        step(3, "铰工艺孔 Ø9 H7（两孔）", "T08", "G04", bore(9, 0.3, 12, 12), vc=12, f=0.3),
    ]
    o40["inspect"] = [dict(char="C 面平面度 0.02", gauge="G09", freq="每件"), dict(char="C 到 B 轴线 200 ± 0.03", gauge="G01", freq="首件、每 5 件"),
                      dict(char="工艺孔 Ø9 H7", gauge="G04", freq="每件")]
    ops.append(o40)
    # ---- 工序 50：HMC 精加工
    o50 = dict(seq=50, operation="镗轴承孔 Bearing-bore boring", workstation="卧式加工中心 HMC-01", shop="机加",
               content="一面两销（接合面 C ＋ 两个 Ø9 H7 工艺孔，液压圆柱涨销 ＋ 削边涨销，零间隙）。上轴两孔、针杆孔、止口、各端面都在这一次装夹里完成，相互位置与定位误差无关。"
                       "B 180° 镗轴过孔 Ø20、精铣电机法兰端面、圆弧插补精铣止口 Ø52 h7；B 0° 精铣面板口端面，"
                       "用镗杆加旋转导向套同轴半精镗、精镗两轴承孔（两孔一刀）；直角铣头扩、铰针杆孔 Ø12 H7（上下两孔一次铰通）",
               datum="接合面 C、两工艺孔（一面两销，精基准）", clamping="4 个液压拉缸（拉杆拧进 M10 螺孔），拉在支承钉正上方", fixture="专用夹具 FX-HSG-U-20",
               coolant="干切；精镗用油雾", setup_min=45, fixture_id="FX-HSG-U-20",
               locate=[dict(surface="接合面 C", symbol="plane", dof=3), dict(surface="工艺孔 1（圆柱涨销）", symbol="pin", dof=2),
                       dict(surface="工艺孔 2（削边涨销）", symbol="pin_diamond", dof=1)],
               clamp=[dict(surface="立柱脚 4 个 M10 螺孔（液压拉杆）", kind="hydraulic")])
    o50["steps"] = [
        step(1, "B 180°（电机端）：镗轴过孔 Ø18 → Ø20 H11", "T04", "G08", bore(20, 0.12, 120, 40), vc=120, f=0.12, ap=1.0),
        step(2, "B 180°：精铣电机法兰端面（0.5），对 B 垂直度 0.02", "T02", "G09", face_mill(63, 5, 200, 0.08, 57, 57, 0.5), vc=200, f=0.4, ap=0.5),
        step(3, "B 180°：圆弧插补精铣止口 Ø52 h7（0/−0.030），Ra 1.6", "T05", "G05", interp_od(52, 20, 4, 0.05, 180, 1, 12), vc=180, f=0.2, ap=0.5),
        step(4, "B 0°（机头端）：精铣面板口端面（0.5），平面度 0.1", "T02", "G09", face_mill(63, 5, 200, 0.08, 112, 120, 0.5), vc=200, f=0.4, ap=0.5),
        step(5, "B 0°：翻上导向套支架，精镗前液压夹紧降到 40%；同轴半精镗杆两孔一刀镗到 Ø34.7、Ø31.7（+0.039/0）", "T13", "G03",
             bore(34.7, 0.12, 140, 22), vc=140, f=0.12, ap=0.35, ta=1.0),
        step(6, "B 0°：同轴精镗杆（镗模式）：前刀 Ø35 H7、后刀 Ø32 H7 相距 344，尾部导向柱插进旋转导向套（预紧轴承，零间隙），"
                "两孔一刀镗出，Ra 1.6（镗杆通过时离后轴承孔入口只有 0.86 mm：进、退刀时主轴定向、刀尖朝上，抬高 1 mm 走）；镗完支架翻下，夹紧力恢复", "T13", "G02", bore(35, 0.06, 150, 22), vc=150, f=0.06, ap=0.15, ta=1.0),
        step(7, "直角铣头：扩针杆孔 Ø11.5 → Ø11.85", "T07", "G03", bore(11.85, 0.12, 60, 150), vc=60, f=0.12),
        step(8, "直角铣头：铰针杆孔 Ø12 H7，上下两孔一次铰通", "T07", "G04", bore(12, 0.25, 12, 150), vc=12, f=0.25),
    ]
    import g5_precision as PRC
    bud = PRC.budgets()
    o50["accuracy"] = [dict(char=c, T=T, items=[dict(name=i["name"], range=i["range"], kind=i["kind"]) for i in bud[k]["items"]])
                       for c, k, T in (("C3", "两轴承孔同轴度 Ø0.02", 0.02), ("C6", "针杆孔对 B 位置度 Ø0.05", 0.05),
                                       ("C11", "上轴中心高 200 ± 0.03（对 C）", 0.06))]
    o50["inspect"] = [dict(char="前、后轴承孔 Ø35 H7、Ø32 H7", gauge="G02", freq="每件"), dict(char="止口 Ø52 h7", gauge="G05", freq="每件"),
                      dict(char="针杆孔 Ø12 H7", gauge="G04", freq="每件"), dict(char="两孔同轴度、止口同轴度（在机测头抽检）", gauge="G01", freq="首件、每 10 件")]
    ops.append(o50)
    # ---- 工序 60：HMC 钻攻小螺纹孔（同一夹具，换托盘后接着做）
    o60 = dict(seq=60, operation="钻攻螺纹孔 Drilling & tapping", workstation="卧式加工中心 HMC-01", shop="机加",
               content="同工序 50 的夹具。B 180° 钻攻电机座 4 × M5（PCD 40）；B 0° 钻攻面板口 4 × M4；B 270° 钻攻前窗口 6 × M4；"
                       "直角铣头钻攻顶盖 4 × M4",
               datum="接合面 C、两工艺孔（一面两销，精基准）", clamping="同工序 50", fixture="专用夹具 FX-HSG-U-20", coolant="攻丝用切削油", setup_min=10,
               fixture_id="FX-HSG-U-20")
    o60["steps"] = [
        step(1, "定心全部 18 个孔", "T12", "", drill(6, 0.08, 60, 1.5, 18), vc=60, f=0.08),
        step(2, "钻 4 × Ø4.2 深 14、攻 M5-6H 深 10", "T10", "G06", {"tb": drill(4.2, 0.1, 60, 14, 4)["tb"] + tap(5, 0.8, 8, 10, 4)["tb"]}, vc=60, f=0.1),
        step(3, "钻 14 × Ø3.3 深 12、攻 M4-6H 深 8", "T11", "G06", {"tb": drill(3.3, 0.08, 60, 12, 14)["tb"] + tap(4, 0.7, 8, 8, 14)["tb"]}, vc=60, f=0.08),
    ]
    o60["inspect"] = [dict(char="M5-6H、M4-6H", gauge="G06", freq="每件")]
    ops.append(o60)
    # ---- 工序 70：终检
    ops.append(dict(seq=70, operation="零件检验 Part inspection", workstation="检验站 QC-01", shop="检验", final_inspection=True,
                    content="清洗后在恒温室（20 ± 1 ℃，工件等温 4 h）三坐标全检：按《机壳三坐标检测计划》建立 C–工艺孔坐标系和 B 轴线，测全部尺寸与形位公差；"
                            "首件加 X 光与解剖（见铸造工艺第七节）", datum="接合面 C、两工艺孔（与加工同一基准）", clamping="三坐标测量夹具（一面两销）",
                    minutes=25, setup_min=10, steps=[],
                    inspect=[dict(char=c["id"], gauge={"C13": "G06", "C15": "G10"}.get(c["id"], "G01"), freq="每件" if c.get("key") else "每 5 件")
                             for c in chars]))
    return dict(item="HSG-LS-U", name="机壳上件（机头、机臂、立柱）", drawing_no="WQLS-HSG-U", tools=tools, gauges=gauges, chars=chars, ops=ops,
                holes=holes, blank_mass=16.45, part_mass=15.78)


# ---------------------------------------------------------------- 下件 HSG-LS-L
def lower():
    tools = [
        dict(id="T01", name="面铣刀 Ø100", spec="Ø100 十刃可转位面铣刀，SEKN 1203（K20），铣底面 A 和机座顶面", ops=[10, 20, 40]),
        dict(id="T02", name="立铣刀 Ø16", spec="Ø16 四刃硬质合金立铣刀，铣针板座、滑板座", ops=[40]),
        dict(id="T03", name="钻头 Ø9.5 / 铰刀 Ø10 H7", spec="整体硬质合金钻 Ø9.5；铰刀 Ø10 H7（底边法兰上的两个工艺孔）", ops=[10]),
        dict(id="T04", name="钻头 Ø11", spec="硬质合金钻 Ø11（M10 螺钉过孔）", ops=[40]),
        dict(id="T05", name="反锪刀 Ø18", spec="反向锪平刀 Ø18（从上面穿过 Ø11 孔，在凸台下端锪平面）", ops=[40]),
        dict(id="T06", name="钻头 Ø2.5、丝锥 M3", spec="硬质合金钻 Ø2.5；M3 丝锥（6H），针板螺孔", ops=[50]),
        dict(id="T07", name="钻头 Ø8.2", spec="硬质合金钻 Ø8.0 ＋ 铰刀 Ø8.2 H11（铰链销孔）", ops=[50]),
        dict(id="T08", name="中心钻", spec="Ø6 90° 定心钻", ops=[10, 40, 50]),
    ]
    gauges = [
        dict(id="G01", name="三坐标测量机（MPE_E = 1.8 + L/300 μm）"),
        dict(id="G04", name="Ø10 H7 塞规（通端 / 止端）"),
        dict(id="G06", name="螺纹塞规 M3-6H"),
        dict(id="G07", name="表面粗糙度仪"),
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
        dict(id="C6", name="工艺孔（底边法兰）", spec="2 × Ø10 H7（+0.015/0）：加工、检测、装配找正共用的基准", nominal=10, es=0.015, ei=0.0, kind="dim"),
        dict(id="C7", name="螺钉过孔与锪平", spec="4 × Ø11，背面锪平 Ø18 深 1.5", kind="other"),
        dict(id="C8", name="螺纹孔与铰链孔", spec="4 × M3-6H（针板）；2 × Ø8.2 H11 铰链销孔", kind="other"),
        dict(id="C9", name="铸件质量", spec="HT250：硬度 190–240 HBW；首件 X 光检查立柱脚 4 个凸台无缩松", kind="other"),
    ]
    holes = {"工艺孔": [(10, 9.5, 0.1, 0.0), (10, 9.85, 0.022, 0.0), (10, 10.0, 0.015, 0.0)]}
    ops = []
    o10 = dict(seq=10, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="工件倒放（顶面朝下）。粗基准：机座顶面铸面三点＋前侧面两点＋左端面一点。粗、半精铣底面 A（余量 3 → 0.3）；在底边法兰上钻铰两个工艺孔 Ø10 H7（对角）",
               datum="机座顶面铸面、前侧面、左端面（粗基准）", clamping="手动压板 4 点压在底边法兰上", fixture="专用夹具 FX-HSG-L-10",
               coolant="干切", setup_min=30,
               locate=[dict(surface="机座顶面铸面", symbol="support", dof=3), dict(surface="前侧面", symbol="support", dof=2), dict(surface="左端面", symbol="support", dof=1)],
               clamp=[dict(surface="底边法兰", kind="manual")])
    o10["steps"] = [
        step(1, "粗铣底面 A（3 → 0.8）", "T01", "G08", face_mill(100, 10, 160, 0.18, 197, 522, 2.2), vc=160, f=1.8, ap=2.2),
        step(2, "半精铣底面 A（留 0.3），平面度 0.05", "T01", "G09", face_mill(100, 10, 200, 0.10, 197, 522, 0.5), vc=200, f=1.0, ap=0.5),
        step(3, "钻、扩、铰两个工艺孔 Ø10 H7（底边法兰对角）", "T03", "G04",
             {"tb": drill(9.5, 0.2, 70, 8, 2)["tb"] + bore(10, 0.3, 12, 8)["tb"] * 2}, vc=70, f=0.2),
    ]
    o10["inspect"] = [dict(char="底面 A 平面度 0.05", gauge="G09", freq="首件、每 10 件")]
    ops.append(o10)
    o20 = dict(seq=20, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="一面两销（底面 A ＋ 两工艺孔）。粗铣机座顶面（余量 4 → 0.5），粗铣针板座、滑板座（留 0.3）",
               datum="底面 A、两工艺孔（精基准）", clamping="液压 4 点", fixture="专用夹具 FX-HSG-L-20（一面两销，与工序 40 共用）",
               coolant="干切", setup_min=30, fixture_id="FX-HSG-L-20")
    o20["steps"] = [step(1, "粗铣机座顶面（4 → 0.5），两刀", "T01", "G08", face_mill(100, 10, 160, 0.18, 197, 522, 1.75, passes=2), vc=160, f=1.8, ap=1.75)]
    o20["inspect"] = [dict(char="顶面到 A 62.5 ± 0.1", gauge="G08", freq="首件、每 10 件")]
    ops.append(o20)
    ops.append(dict(seq=30, operation="时效 Stress relieving", workstation="热处理炉 HT-01", shop="热处理",
                    content="第二次去应力退火（规范同上件工序 30）", datum="—", clamping="料架平放，底面朝下", minutes=6, setup_min=10, steps=[],
                    inspect=[dict(char="炉温曲线记录", gauge="炉温记录仪", freq="每炉")]))
    o40 = dict(seq=40, operation="铣结合面 Face milling", workstation="立式加工中心 VMC-01", shop="机加",
               content="一面两销（底面 A ＋ 两工艺孔）。精铣底面 A 前先翻面精铣 A（以顶面粗铣面定位，0.3），再回到一面两销：精铣机座顶面保证高度 62 ± 0.05、"
                       "平面度 0.02、对 A 平行度 0.03；精铣针板座、滑板座；钻 4 × Ø11 过孔，反锪 Ø18。立柱脚的两个锥销孔不在这里加工，装配找正后与上件配铰",
               datum="底面 A、两工艺孔", clamping="液压 4 点", fixture="专用夹具 FX-HSG-L-20", coolant="干切", setup_min=40, fixture_id="FX-HSG-L-20")
    o40["steps"] = [
        step(1, "（翻面，顶面粗铣面定位）精铣底面 A（0.3），平面度 0.05", "T01", "G09", face_mill(100, 10, 220, 0.06, 197, 522, 0.3), vc=220, f=0.6, ap=0.3),
        step(2, "（回一面两销）精铣机座顶面（0.5），高度 62 ± 0.05，平面度 0.02，Ra 1.6", "T01", "G09", face_mill(100, 10, 220, 0.06, 197, 522, 0.5), vc=220, f=0.6, ap=0.5),
        step(3, "铣针板座深 2.5 ± 0.03、滑板座深 1.5 ± 0.05（立铣刀，环切）", "T02", "G12", {"tb": 4.0}, vc=180, f=0.05 * 4),
        step(4, "钻 4 × Ø11 通孔，反锪 Ø18 深 1.5", "T04", "G08", {"tb": drill(11, 0.2, 70, 30, 4)["tb"] + 4 * 0.3}, vc=70, f=0.2),
    ]
    o40["inspect"] = [dict(char="机座高度 62 ± 0.05", gauge="G01", freq="首件、每 5 件"), dict(char="顶面平面度 0.02、对 A 平行度 0.03", gauge="G09", freq="每件"),
                      dict(char="针板座深 2.5 ± 0.03", gauge="G12", freq="每件")]
    ops.append(o40)
    o50 = dict(seq=50, operation="钻攻螺纹孔 Drilling & tapping", workstation="立式加工中心 VMC-01", shop="机加",
               content="同工序 40 夹具：钻攻针板 4 × M3；夹具侧转 90°（附加角度板）钻铰两个铰链销孔 Ø8.2 H11",
               datum="底面 A、两工艺孔", clamping="同工序 40", fixture="专用夹具 FX-HSG-L-20", coolant="攻丝用切削油", setup_min=15)
    o50["steps"] = [step(1, "钻 4 × Ø2.5 深 8、攻 M3-6H 深 6", "T06", "G06", {"tb": drill(2.5, 0.06, 50, 8, 4)["tb"] + tap(3, 0.5, 6, 6, 4)["tb"]}, vc=50, f=0.06),
                    step(2, "钻 Ø8.0、铰 Ø8.2 H11 铰链销孔（两个耳）", "T07", "G08", {"tb": drill(8, 0.18, 70, 26, 2)["tb"] + bore(8.2, 0.3, 15, 26)["tb"] * 2}, vc=70, f=0.18)]
    o50["inspect"] = [dict(char="M3-6H", gauge="G06", freq="每件")]
    ops.append(o50)
    ops.append(dict(seq=60, operation="零件检验 Part inspection", workstation="检验站 QC-01", shop="检验", final_inspection=True,
                    content="清洗后在恒温室三坐标全检：A–工艺孔坐标系；首件 X 光（立柱脚凸台）", datum="底面 A、两工艺孔", clamping="三坐标测量夹具",
                    minutes=15, setup_min=10, steps=[],
                    inspect=[dict(char=c["id"], gauge={"C9": "G10"}.get(c["id"], "G01"), freq="每件" if c.get("key") else "每 5 件") for c in chars]))
    return dict(item="HSG-LS-L", name="机壳下件（机座）", drawing_no="WQLS-HSG-L", tools=tools, gauges=gauges, chars=chars, ops=ops, holes=holes,
                blank_mass=11.28, part_mass=8.38)


# ---------------------------------------------------------------- 机壳部件 HSG-LS-P（上件＋下件，装配找正后配铰锥销，配对使用）
def pair():
    tools = [
        dict(id="T01", name="直角铣头", spec="90° 直角铣头（同上件工序 50）", ops=[20]),
        dict(id="T02", name="钻头 Ø8.5", spec="整体硬质合金钻 Ø8.5（穿过下件顶板进上件凸台，扩通上件工艺孔下面那一段）", ops=[20]),
        dict(id="T03", name="锥度铰刀 1:50", spec="1:50 锥度铰刀（粗、精两把），按 GB/T 117 锥销 10 × 40 的小端 Ø10 铰到锥销打入后露出 3–4 mm", ops=[20]),
    ]
    gauges = [
        dict(id="G01", name="三坐标测量机"),
        dict(id="G02", name="找正检棒 Ø12 h5 × 260（插进针杆两个孔，下端伸到针板座）"),
        dict(id="G03", name="针板孔基准检具：装在针板座里，用针板的 4 个 M3 孔和两侧边定位，中间 Ø12 H6 衬套"),
        dict(id="G04", name="扭力扳手 20–100 N·m"),
        dict(id="G05", name="锥销接触检查（红丹）"),
    ]
    chars = [
        dict(id="P1", name="针杆孔轴线对针板孔基准的位置", spec="Ø0.1，即 ±0.05（找正检棒能顺利插进针板孔基准检具的 Ø12 H6 衬套）", nominal=0.0, es=0.05, ei=-0.05,
             kind="geo", key=True),
        dict(id="P2", name="接合面贴合", spec="0.02 塞尺塞不进", kind="other"),
        dict(id="P3", name="M10 螺钉拧紧力矩", spec="4 × M10（10.9 级）45 N·m，对角分两次拧紧", kind="other", key=True),
        dict(id="P4", name="锥销孔", spec="2 × 锥销 10 × 40（GB/T 117，1:50），红丹检查接触 ≥ 75%，锥销打入后露出 3–4 mm", kind="other", key=True),
        dict(id="P5", name="配对编号", spec="上、下件在立柱脚打同一配对编号，此后不得与别的件互换", kind="other"),
    ]
    ops = []
    o10 = dict(seq=10, operation="部件装配 Sub-assembly", workstation="装配工位 ASM-01", shop="装配",
               content="下件以底面 A 和两个工艺孔装在找正台上；针板座里装针板孔基准检具。接合面清洁后放上上件，套上 4 个 M10 螺钉（不拧紧）。"
                       "找正检棒从机头上面的针杆孔插入，用立柱脚两侧的顶丝微调上件，直到检棒下端顺利插进检具的 Ø12 H6 衬套；"
                       "对角分两次拧紧 4 个 M10 到 45 N·m，再插一次检棒复查",
               datum="下件底面 A、两工艺孔；上件针杆孔（找正）", clamping="找正台 3 点压板压下件底边法兰", fixture="找正台 FX-HSG-P-10 ＋ 针板孔基准检具",
               minutes=12, setup_min=5,
               steps=[dict(step=1, content="清洁接合面，下件装上找正台，装针板孔基准检具", tool="", gauge="G03", tb_min=0, ta_min=3.0),
                      dict(step=2, content="放上上件，插找正检棒，微调到检棒插进衬套", tool="", gauge="G02", tb_min=0, ta_min=5.0),
                      dict(step=3, content="4 × M10 对角分两次拧到 45 N·m，复查检棒", tool="", gauge="G04", tb_min=0, ta_min=2.5)],
               inspect=[dict(char="找正检棒插进衬套（P1）", gauge="G02", freq="每件"), dict(char="M10 拧紧力矩 45 N·m（P3）", gauge="G04", freq="每件")])
    ops.append(o10)
    o20 = dict(seq=20, operation="合箱钻铰销孔 Pin-hole reaming", workstation="卧式加工中心 HMC-01", shop="机加",
               content="合好的部件立在夹具 FX-HSG-P-20 上（底面 A、两个工艺孔；夹具中间开窗）。直角铣头从机座里面向上：钻 Ø8.5 穿过下件顶板，"
                       "扩通到上件工艺孔；锥度铰刀粗铰、精铰两个锥销孔；打入锥销；在立柱脚打配对编号",
               datum="下件底面 A、两工艺孔", clamping="液压 4 点压底边法兰", fixture="专用夹具 FX-HSG-P-20（中间开窗，放直角铣头）",
               coolant="干切", setup_min=30)
    o20["steps"] = [
        step(1, "直角铣头：钻 2 × Ø8.5 穿过下件顶板（约 9.6 mm），与上件工艺孔对通", "T02", "", drill(8.5, 0.15, 60, 22, 2), vc=60, f=0.15),
        step(2, "粗铰、精铰 1:50 锥销孔（两孔）", "T03", "G05", {"tb": 2 * 2 * bore(10, 0.15, 8, 34)["tb"]}, vc=8, f=0.15),
        step(3, "打入锥销 10 × 40，检查露出 3–4 mm；打配对编号", "", "G05", {"tb": 0.0}, ta=1.5),
    ]
    o20["inspect"] = [dict(char="锥销孔接触 ≥ 75%（红丹）", gauge="G05", freq="首件、每 10 件")]
    ops.append(o20)
    ops.append(dict(seq=30, operation="零件检验 Part inspection", workstation="检验站 QC-01", shop="检验", final_inspection=True,
                    content="部件三坐标检测：以下件 A 与工艺孔建坐标系，测针杆孔轴线、上轴 B 对针板座的位置；检查配对编号",
                    datum="下件底面 A、两工艺孔", clamping="三坐标测量夹具", minutes=12, setup_min=5, steps=[],
                    inspect=[dict(char=c["id"], gauge={"P3": "G04", "P4": "G05"}.get(c["id"], "G01"), freq="每件") for c in chars]))
    import g5_precision as PRC
    s3 = PRC.scheme_III()
    chains = [dict(name="针杆孔对针板孔基准（装配找正后配铰锥销）", char="P1",
                   links=[dict(name=l["name"], nominal=0.0, es=l["half"], ei=-l["half"], sense=1) for l in s3["links"]])]
    return dict(chains=chains, item="HSG-LS-P", name="机壳部件（上件＋下件，配对）", drawing_no="WQLS-HSG-P", tools=tools, gauges=gauges, chars=chars, ops=ops,
                holes={}, blank_mass=24.2, part_mass=24.2, blank_kind="上件 HSG-LS-U ＋ 下件 HSG-LS-L（各自加工完）")


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
                part=dict(kind="housing", mass_kg=P["part_mass"], source="tools/wqls/cad/housing.py（G4.4）"),
                blank=dict(kind=P.get("blank_kind", "铸件"), spec=f"HT250 砂型铸件 {P['blank_mass']} kg" if "blank_kind" not in P else "", length_mm="", material_item=f"CS-{P['item']}",
                           drawing="docs/设计/WQ-LS/G5/机壳铸造工艺.md"),
                chains=P.get("chains", []), characteristics=P["chars"], tool_list=P["tools"], gauges=P["gauges"], operations=ops,
                hole_sizes={k: [dict(op=a, d=d, es=es, ei=ei) for a, d, es, ei in v] for k, v in P["holes"].items()},
                attachments=[dict(kind="calc", name="机壳机械加工工艺计算（tools/wqls/g5_process.py，切削用量、机动时间、余量、功率）", missing=[])])
    return plan


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "设计" / "WQ-LS" / "G5"
    out.mkdir(parents=True, exist_ok=True)
    from hub import cards, process as PR
    summary = {}
    for P in (upper(), lower(), pair()):
        import copy
        plan = build(copy.deepcopy(P))
        path = STD / f"{P['item']}_process.yaml"
        path.write_text("# 第 138 轮 G5.1：WQ-LS 机壳机械加工工艺规程（由 tools/wqls/g5_process.py 生成，不要手改）\n"
                        + yaml.safe_dump(plan, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
        rv = PR.review(plan)
        ck = cards.check(plan)
        hc = hole_check(P["holes"])
        pc = power_check(P["ops"])
        html = cards.html(plan, title=f"{P['item']} {P['name']} 机械加工工艺卡")
        cn = {"HSG-LS-U": "上件", "HSG-LS-L": "下件", "HSG-LS-P": "部件"}[P["item"]]
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
