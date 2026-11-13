"""第 161b 轮：减速器厂案例 C——整台二级圆柱齿轮减速器 WQR-105，从任务书到装配、跑合、出厂 10 台。

    python3 tools/cases/gearbox_c.py

在案例 A（输出轴）、B（低速级齿轮副）的基础上做整机：传动比分配、两级齿轮、三根轴与六个轴承、轴向布置、箱体热平衡
（数字工厂“仿真与分析”的热分析示例，CalculiX）、三维装配、装配工艺、在仿真车间里合箱镗孔—部件装配—总装—跑合—出厂检验。
输出到 factory/cases/gearbox/C/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "textbook" / "mechdesign" / "conventions"), str(ROOT / "textbook" / "mechdesign" / "ch33" / "code"),
                str(ROOT / "factory" / "digital"), str(ROOT / "factory")]
os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import gearlib as GL  # noqa: E402
import mdstd  # noqa: E402
import _shaft as SA  # noqa: E402
from cae import gears as G  # noqa: E402
from factory import data as F  # noqa: E402

TOOLS = {
    "configurator": ("参数配置器", "Configurator", "/configurator"),
    "library": ("零件库", "Parts library", "/library"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
    "design": ("设计发布与审批", "Design release", "/design"),
    "process": ("工艺规程与 AI 评审", "Process plans & AI review", "/process"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "twin": ("数字孪生", "Digital twin", "/twin"),
    "quality": ("质量", "Quality", "/work/quality"),
    "finance": ("经营与成本", "Business & cost", "/finance"),
    "3d": ("3D 车间", "3D shop", "/3d"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

# ---------------------------------------------------------------- 已知条件（与案例 A、B 同一组数）
T_OUT = 350.0
N_IN = 1450.0
EG, EB = 0.97, 0.99
LIFE_H = 10000.0
Z = {k: v["z"] for k, v in F.GEARS.items()}
MOD = {k: v["m"] for k, v in F.GEARS.items()}
I1, I2 = Z["GR-202"] / Z["SH-101"], Z["GR-302"] / Z["GR-203"]
I = I1 * I2
T_MID = T_OUT / (I2 * EG * EB)
T_IN = T_MID / (I1 * EG * EB)
N_MID, N_OUT = N_IN / I1, N_IN / I
ETA = EG ** 2 * EB ** 3
P_OUT = T_OUT * N_OUT * 2 * math.pi / 60
P_IN = P_OUT / ETA
A1 = MOD["SH-101"] * (Z["SH-101"] + Z["GR-202"]) / 2
A2 = MOD["GR-203"] * (Z["GR-203"] + Z["GR-302"]) / 2
B_SH101, B_GR202 = 30.0, 28.0               # SH-101 齿宽见 std/SH-101_part.yaml；GR-202 本案例定
B_GR203, B_GR302 = 50.0, 45.0               # 案例 B
MAT_P, MAT_W = "20CrMnTi-carburized", "40Cr-QT"
SERIES, RATE, RATED = SA.torque_series()

case = L.Case("gearbox", "C", "完整", "二级圆柱齿轮减速器 WQR-105（整机）", "Two-stage gear reducer WQR-105 (complete)", "WQR-105",
              "整台减速器：传动比分配、两级齿轮、三根轴和六个轴承、轴向布置、箱体热平衡（有限元）、三维装配，再在减速器厂合箱镗孔、装配、跑合、出厂 10 台。",
              "The complete reducer: ratio split, both gear stages, three shafts and six bearings, axial layout, housing heat balance (FEA), 3D assembly, then line-boring, assembly, run-in and dispatch of 10 units in the gearbox plant.",
              "tools/cases/gearbox_c.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：二级圆柱齿轮减速器 WQR-105

**用途**　带式输送机、搅拌机一类连续运转的设备，四极电机直接驱动，输出轴经联轴器接工作机。

| 项目 | 要求 | 出处 |
|---|---|---|
| 输入 | 四极电机 {N_IN:.0f} r/min，额定 4 kW | 工厂设计；《机械设计》习题 33.3.2 |
| 输出 | 额定转矩 {T_OUT:.0f} N·m（含工况系数 K_A = 1.25），{N_OUT:.1f} r/min | 参数配置器 T_RATED |
| 总传动比 | {I:g} | 产品规格 |
| 起停 | 频繁起停，起动峰值约 1.66 倍额定（跑合台记录） | 案例 A |
| 寿命 | {LIFE_H:,.0f} h | 参数配置器默认 |
| 油温 | 连续满载不超过 80 ℃（车间 20 ℃） | 濮良贵《机械设计》减速器热平衡 |
| 已定零部件 | 输出轴 SH-301 B 版（案例 A）、低速级齿轮副 GR-203 / GR-302（案例 B） | — |
| 现有工装 | 箱体合镗工装、m2 和 m3 滚刀、跑合试验台 test-01 | 减速器厂 |

**交付物**　总体方案与传动比分配、整机计算书（两级齿轮、三根轴、六个轴承、热平衡）、三维装配、装配工艺、首批 10 台的装配与跑合记录、成本。
"""
case.step("brief", f"4 kW、{N_IN:.0f} r/min 输入，{T_OUT:.0f} N·m、{N_OUT:.1f} r/min 输出，i = {I:g}；油温 ≤ 80 ℃；输出轴和低速级齿轮用案例 A、B 的结果。",
          f"4 kW at {N_IN:.0f} rpm in, {T_OUT:.0f} N·m at {N_OUT:.1f} rpm out, i = {I:g}; oil ≤ 80 °C; output shaft and low-speed gears from cases A and B.",
          md=case.text("1_任务书.md", brief), tools=tools("configurator"),
          facts=[("输入功率", "Input power", P_IN / 1000, "kW"), ("总传动比", "Overall ratio", I, ""), ("输出转矩", "Output torque", T_OUT, "N·m")])

# ================================================================ 2 方案：传动比分配、浸油
K3 = 1.1 ** 3
ZZ = G.z_e() * G.z_h(0) * 0.88


def a_min(T1, u, mat=MAT_W, phi=0.35, SH=1.1):
    """按接触强度的最小中心距：a = (u+1)·∛(K T₁ (Z_E Z_H Z_ε)² S_H² / (2 φ_a u σ_Hlim²))"""
    return (u + 1) * (K3 * T1 * 1e3 * ZZ ** 2 * SH ** 2 / (2 * phi * u * G.MATERIALS[mat]["sHlim"] ** 2)) ** (1 / 3)


def immersion(d_fast, d_slow, m_fast):
    """高速级大齿轮浸油一个齿高（不少于 10 mm）时，低速级大齿轮浸油多深、占半径几分之几（两轴在同一水平面）"""
    dep_fast = max(2.25 * m_fast, 10.0)
    level = -(d_fast / 2 + m_fast) + dep_fast
    dep_slow = (d_slow / 2 + 3) + level
    return dep_slow, dep_slow / (d_slow / 2)


rows = []
for i1, i2 in ((3.0, 3.5), (3.5, 3.0), (3.83, 2.74), (2.5, 4.2)):
    Tm = T_OUT / (i2 * EG * EB)
    Ti = Tm / (i1 * EG * EB)
    a1, a2 = a_min(Ti, i1), a_min(Tm, i2)
    d_f, d_s = 2 * a1 * i1 / (i1 + 1), 2 * a2 * i2 / (i2 + 1)
    dep, frac = immersion(d_f, d_s, 2.0)
    rows.append([f"{i1:g} × {i2:g}" + ("（现行）" if (i1, i2) == (3.0, 3.5) else "（i₁ ≈ √(1.4 i)）" if i1 == 3.83 else ""),
                 f"{a1:.0f}", f"{a2:.0f}", f"{a1 + a2:.0f}", f"{d_f:.0f} / {d_s:.0f}", f"{dep:.0f} mm（{frac:.2f} r）"])
dep_now, frac_now = immersion(MOD["GR-202"] * Z["GR-202"], MOD["GR-302"] * Z["GR-302"], 2.0)
concept = f"""# 方案：传动比怎么分

两级展开式圆柱齿轮减速器，总传动比 {I:g}。按接触强度估算两级需要的中心距（同一组材料、齿宽系数 φ_a = 0.35、S_H = 1.1），
再看两只大齿轮的浸油：高速级大齿轮浸一个齿高（不少于 10 mm）时，低速级大齿轮浸多深（教材建议不超过分度圆半径的 1/6–1/3）：

{L.md_table(["i₁ × i₂", "a₁ 估算", "a₂ 估算", "合计", "两只大齿轮直径", "低速级大齿轮浸油"], rows)}

- 总中心距几个方案差不到 4%，箱体大小差不多；**差别在浸油**：i₁ 大一些（教材经验 i₁ ≈ (1.3–1.5) i₂），两只大齿轮直径接近，低速级大齿轮浸得浅、搅油损失小。
- 现行 3 × 3.5 是“前小后大”，实际齿轮（GR-202 Ø{MOD['GR-202'] * Z['GR-202']:g}、GR-302 Ø{MOD['GR-302'] * Z['GR-302']:g}）下低速级大齿轮浸油约 {dep_now:.0f} mm（{frac_now:.2f} 倍半径），略超 1/3。
- 但现行方案的箱体合镗工装（中心距 {A1:g}、{A2:g}）、m2 / m3 滚刀、案例 A 的输出轴和案例 B 的齿轮副都已经定了。换成 3.5 × 3 要重做两级齿轮和箱体。

**选定：保持 3 × 3.5**，中心距 {A1:g} + {A2:g}。浸油超出的部分在第 4 步的热平衡里一起算（搅油损失变成热），油位按下限加注（高速级大齿轮刚好浸一个齿高）。
下一代产品（换箱体时）建议改成 i₁ > i₂。
"""
case.step("concept", f"比较四种传动比分配：总中心距差不到 4%，差在浸油；现行 3 × 3.5 低速级大齿轮浸油 {frac_now:.2f} 倍半径略深，但工装和 A、B 已定，保持不变，下一代改 i₁ > i₂。",
          f"Four ratio splits compared: total centre distance within 4%, the difference is oil immersion; the current 3 × 3.5 dips the low-speed wheel {frac_now:.2f} of its radius, slightly deep, but tooling and cases A/B are fixed, so it is kept; next generation should use i₁ > i₂.",
          md=case.text("2_方案.md", concept), tools=tools("configurator"),
          facts=[("中心距", "Centre distances", f"{A1:g} + {A2:g}", "mm"), ("低速级浸油", "Low-speed immersion", frac_now, "r")])

# ================================================================ 3 计算：两级齿轮、轴向布置、三根轴、六个轴承
g1 = G.geometry(MOD["SH-101"], Z["SH-101"], Z["GR-202"], 0, b=B_GR202)
r1 = G.check(T_IN, N_IN, g1, MAT_P, MAT_W, KA=1.0, hours=LIFE_H)
g2 = G.geometry(MOD["GR-203"], Z["GR-203"], Z["GR-302"], 0, b=B_GR302)
r2 = G.check(T_MID, N_MID, g2, MAT_P, MAT_W, KA=1.0, hours=LIFE_H)
gear_rows = [["第一级 SH-101 / GR-202", f"m2、{Z['SH-101']}/{Z['GR-202']}、b {B_SH101:g}/{B_GR202:g}", f"{r1['Ft']:.0f} N", f"{r1['sigma_H']:.0f} MPa", f"{r1['SH']:.2f}", f"{r1['SF']:.2f}"],
             ["第二级 GR-203 / GR-302（案例 B）", f"m3、{Z['GR-203']}/{Z['GR-302']}、b {B_GR203:g}/{B_GR302:g}", f"{r2['Ft']:.0f} N", f"{r2['sigma_H']:.0f} MPa", f"{r2['SH']:.2f}", f"{r2['SF']:.2f}"]]

# 轴向布置：从左轴承中心量起；三根轴的两个轴承都装在箱体的同两面壁上，跨距相同
BRG = {"SH-101": "6205", "SH-201": "6206", "SH-301": "6207"}
Z_STAGE2 = SA.Z_GEAR - SA.Z_BRG_A                      # 案例 A：GR-302 中心离左轴承中心 54
CLEAR = 10.0                                           # 齿轮端面到箱壁（轴承内侧）的间隙
GAP = 10.0                                             # 中间轴上两只齿轮之间
Z_STAGE1 = Z_STAGE2 + B_GR203 / 2 + GAP + B_GR202 / 2
SPAN = math.ceil(Z_STAGE1 + max(B_GR202, B_SH101) / 2 + CLEAR + mdstd.bearing("6206")["B"] / 2)
SPAN_A = SA.Z_BRG_B - SA.Z_BRG_A


def shaft_loads(F_list, span=SPAN):
    """F_list：[(z, Fx, Fy)]（Fx 径向、Fy 切向，N）→ 两个轴承的支反力（合成，N）和沿轴的合成弯矩函数"""
    RB = np.array([sum(f[1] * f[0] for f in F_list), sum(f[2] * f[0] for f in F_list)]) / span
    RA = np.array([sum(f[1] for f in F_list), sum(f[2] for f in F_list)]) - RB

    def M(z):
        mx = RA[0] * z - sum(f[1] * (z - f[0]) for f in F_list if f[0] < z)
        my = RA[1] * z - sum(f[2] * (z - f[0]) for f in F_list if f[0] < z)
        return math.hypot(mx, my) if 0 <= z <= span else 0.0
    return float(np.hypot(*RA)), float(np.hypot(*RB)), M


tan20 = math.tan(math.radians(20))
Ft1, Ft2 = r1["Ft"], r2["Ft"]
# 三根轴在同一水平面上：输入轴在中间轴左边（−x），输出轴在右边（+x）；中间轴上两个圆周力同向、两个径向力反向
loads = {
    "SH-101": [(Z_STAGE1, Ft1 * tan20, Ft1)],
    "SH-201": [(Z_STAGE1, -Ft1 * tan20, -Ft1), (Z_STAGE2, Ft2 * tan20, -Ft2)],
    "SH-301": [(Z_STAGE2, -Ft2 * tan20, Ft2)],
}
speed = {"SH-101": N_IN, "SH-201": N_MID, "SH-301": N_OUT}
torque = {"SH-101": T_IN, "SH-201": T_MID, "SH-301": T_OUT}
FP = 1.1                                   # 载荷系数：转矩已含 K_A = 1.25，按“无冲击或轻微冲击 1.0–1.2”取中间值
brg_rows, brg_min = [], math.inf
moments = {}
for code, fl in loads.items():
    RA, RB, Mf = shaft_loads(fl)
    moments[code] = Mf
    b = mdstd.bearing(BRG[code])
    for side, R in (("左", RA), ("右", RB)):
        L10 = (b["C_kN"] * 1e3 / (FP * R)) ** 3 * 1e6 / (60 * speed[code])
        brg_min = min(brg_min, L10)
        brg_rows.append([code, side, BRG[code], f"{R:.0f} N", f"{b['C_kN']:g} kN", f"{L10:,.0f} h"])

# 轴的疲劳安全系数（与案例 A 同一套函数：_shaft.fatigue_factors、safety，DIN 743 流程）
SECS = {
    "SH-101": [("齿轮左侧轴肩", Z_STAGE1 - B_SH101 / 2, 30, 34, 1.0, "shoulder", "20CrMnTi"), ("齿轮右侧轴肩", Z_STAGE1 + B_SH101 / 2, 30, 34, 1.0, "shoulder", "20CrMnTi")],
    "SH-201": [("GR-203 轴段（键槽）", Z_STAGE2, 35, None, None, "keyseat", "45-QT"), ("GR-202 轴段（键槽）", Z_STAGE1, 35, None, None, "keyseat", "45-QT"),
               ("轴环右侧轴肩", Z_STAGE2 + B_GR203 / 2 + 1, 35, 42, 1.0, "shoulder", "45-QT")],
    "SH-301": [("齿轮中点（键槽）", Z_STAGE2, 40, None, None, "keyseat", "40Cr-QT"), ("轴环左侧轴肩", Z_STAGE2 + 27.5, 40, 48, 1.6, "shoulder", "40Cr-QT")],
}
MATID = {"20CrMnTi": "20CrMnTi-CQ", "45-QT": "45-QT", "40Cr-QT": "40Cr-QT"}
shaft_rows, sca_min = [], math.inf
for code, secs in SECS.items():
    for name, z, d, D, rr, kind, mid in secs:
        mat = mdstd.material(MATID[mid])
        sec = {"z": z, "d": d, "D": D, "r": rr, "notch": "keyseat" if kind == "keyseat" else "shoulder"}
        if kind == "keyseat":
            f = SA.fatigue_factors(sec, mat, "ground")
        else:
            a = mdstd.kt_estimate("shoulder_round")
            f = SA.fatigue_factors(sec, mat, "ground", (a["Kt"], a["Kts"]))
        M_ = moments[code](z)
        c = SA.safety(sec, mat, f, M_, torque[code] * 1e3)
        sca_min = min(sca_min, c["S_ca"])
        shaft_rows.append([code, name, f"Ø{d:g}", mat["name"], f"{M_ / 1e3:.1f} N·m", f"{torque[code]:.1f} N·m", f"{c['S_ca']:.2f}"])
used_mats = sorted({r_[3] for r_ in shaft_rows})

calcmd = f"""# 整机计算书

## 传动参数

| 轴 | 转速 r/min | 转矩 N·m | 功率 kW |
|---|---|---|---|
| 输入轴 SH-101 | {N_IN:.0f} | {T_IN:.2f} | {P_IN / 1000:.2f} |
| 中间轴 SH-201 | {N_MID:.1f} | {T_MID:.1f} | {P_IN * EG * EB / 1000:.2f} |
| 输出轴 SH-301 | {N_OUT:.1f} | {T_OUT:.0f} | {P_OUT / 1000:.2f} |

总效率 η = 0.97² × 0.99³ = {ETA:.4f}，损耗 {P_IN - P_OUT:.0f} W（第 4 步热平衡的热源）。

## 两级齿轮（GB/T 3480 简化，同案例 B 的函数）

{L.md_table(["", "参数", "圆周力", "接触应力", "S_H", "S_F"], gear_rows)}

第一级大齿轮 GR-202 的齿宽本案例定为 {B_GR202:g}：b = 22 时 S_H 刚到 1.0，取 28 和第二级的余量（{r2['SH']:.2f}）相当。

## 轴向布置（从左轴承中心量起）

- 第二级（GR-203 / GR-302）中心在 {Z_STAGE2:g}（案例 A 输出轴的齿轮位置）；
- 中间轴上 GR-203 宽 {B_GR203:g}，与 GR-202 间隔 {GAP:g}，第一级（SH-101 / GR-202）中心在 {Z_STAGE1:g}；
- 齿轮端面到箱壁留 {CLEAR:g} mm，**三根轴的轴承跨距都是 {SPAN:g} mm**（两只轴承装在箱体同两面壁上）。

**这里和案例 A 对不上**：案例 A（教材 33.2 节的 B 版）只看了输出轴，跨距 {SPAN_A:g} mm；放进整机，中间轴要并排装两只齿轮，箱壁要往外移 {SPAN - SPAN_A:g} mm。
输出轴的轴肩段（Ø42）相应加长 {SPAN - SPAN_A:g} mm，第 4 步按新跨距复核了输出轴。这就是整机设计反过来改零件设计。

## 三根轴的疲劳安全系数（DIN 743 流程，同案例 A 的函数）

三根轴在同一水平面上：中间轴上两只齿轮的圆周力**同向**、径向力反向，所以中间轴受力最大。

{L.md_table(["轴", "截面", "直径", "材料", "合成弯矩", "转矩", "S_ca"], shaft_rows)}

## 六个轴承（L₁₀h = (C/P)³·10⁶/(60n)，P = f_p R）

载荷系数 f_p = {FP}：转矩里已经含了工况系数 K_A = 1.25，f_p 再按“无冲击或轻微冲击 1.0–1.2”取中间值（濮良贵《机械设计》滚动轴承一章）。
若按“中等冲击”取 1.2，中间轴轴承只有 {brg_min * (FP / 1.2) ** 3:,.0f} h——**中间轴轴承是全机寿命最短的零件**，两个圆周力同向是原因。

{L.md_table(["轴", "位置", "轴承", "径向载荷", "C", "寿命"], brg_rows)}
"""
case.step("calc", f"两级齿轮 S_H {r1['SH']:.2f} / {r2['SH']:.2f}；轴承跨距要从案例 A 的 {SPAN_A:g} 加到 {SPAN:g} mm；三根轴最小 S_ca {sca_min:.2f}；轴承最短寿命 {brg_min:,.0f} h。",
          f"Gear stages S_H {r1['SH']:.2f} / {r2['SH']:.2f}; bearing span must grow from case A's {SPAN_A:g} to {SPAN:g} mm; lowest shaft S_ca {sca_min:.2f}; shortest bearing life {brg_min:,.0f} h.",
          md=case.text("3_计算书.md", calcmd), tools=tools("cae", "library"),
          facts=[("第一级 S_H", "Stage 1 S_H", r1["SH"], ""), ("第二级 S_H", "Stage 2 S_H", r2["SH"], ""), ("轴承跨距", "Bearing span", SPAN, "mm"),
                 ("轴最小 S_ca", "Lowest shaft S_ca", sca_min, ""), ("轴承最短寿命", "Shortest bearing life", brg_min, "h")])
case.check("calc", "第一级齿面接触安全系数", "Stage 1 contact safety factor", r1["SH"], ">=", 1.0, "", "GB/T 3480")
case.check("calc", "第二级齿面接触安全系数", "Stage 2 contact safety factor", r2["SH"], ">=", 1.0, "", "GB/T 3480")
case.check("calc", "两级齿根弯曲安全系数", "Bending safety factor, both stages", min(r1["SF"], r2["SF"]), ">=", 1.25, "", "GB/T 3480")
case.check("calc", "三根轴疲劳安全系数", "Fatigue safety factor, three shafts", sca_min, ">=", 1.5, "", "《机械设计》33.5.5 节")
case.check("calc", "六个轴承最短寿命", "Shortest life of the six bearings", brg_min, ">=", LIFE_H, "h", "ISO 281")

# ================================================================ 4 仿真：箱体热平衡（有限元）
from cae import geometry as GE, materials as MA, thermal as TH, thermal_parts as TP  # noqa: E402

HOUSE = {"L": round(A1 + A2 + (Z["SH-101"] + 2) * 2 / 2 + (Z["GR-302"] + 2) * 3 / 2 + 2 * 15 + 2 * 10), "W": SPAN + 2 * 10, "H": 300.0}


def heat(fins):
    p = TP.params_of("housing", dict(HOUSE, fins=fins))
    step = TP.build("housing", p)
    faces, _, _ = GE.faces(step)
    ex = TP.example("housing", p, faces)
    mat = MA.get(ex["material_id"])
    stats, surf, _ = TH.solve(step, {"analysis": "thermal", "material": mat, "thermal": ex["thermal"], "mesh": {"size_mm": ex["mesh_mm"]}})
    return p, ex["formula"], stats, surf


th = {n: heat(n) for n in (0, 8)}
fig, ax = plt.subplots(figsize=(7.6, 3.1))
for n, (p, fo, st, surf) in th.items():
    ax.barh(f"{n} 条散热筋 / 侧" if n else "无散热筋", st["t_surface_mean_c"], color=L.ACCENT if n else L.BAD, alpha=0.85)
    ax.text(st["t_surface_mean_c"] + 1, f"{n} 条散热筋 / 侧" if n else "无散热筋", f"有限元 {st['t_surface_mean_c']:.1f} ℃ / 公式 {fo['t_oil_c']:.1f} ℃", va="center", fontsize=9)
ax.axvline(80, color=L.BAD, ls=":", lw=1)
ax.text(80.5, -0.45, "80 ℃", color=L.BAD, fontsize=9)
ax.set_xlim(0, 115)
ax.set_xlabel("箱体外表面平均温度（≈ 油温）/ ℃，车间 20 ℃")
case.fig(fig, "4_热平衡.png")
# 箱体温度分布（加筋方案的外表面三角形，按温度着色）
p8, fo8, st8, surf8 = th[8]
try:
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    P_ = np.asarray(surf8["positions"], float)
    T_ = np.asarray(surf8.get("temp"), float) if surf8.get("temp") is not None else None
    tri = np.asarray(surf8["triangles"], int)
    if T_ is not None and len(T_) == len(P_):
        fig = plt.figure(figsize=(7.5, 4.2))
        ax = fig.add_subplot(111, projection="3d")
        cm = plt.get_cmap("inferno")
        tv = T_[tri].mean(axis=1)
        nrm = (tv - tv.min()) / max(1e-9, tv.max() - tv.min())
        ax.add_collection3d(Poly3DCollection(P_[tri], facecolors=cm(nrm), edgecolors="none"))
        lo, hi = P_.min(0), P_.max(0)
        ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
        ax.set_box_aspect(hi - lo)
        ax.view_init(24, -58)
        ax.set_axis_off()
        sm = plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(tv.min(), tv.max()))
        fig.colorbar(sm, ax=ax, shrink=0.6, label="℃")
        ax.set_title(f"8 条散热筋 / 侧：外表面温度 {tv.min():.0f}–{tv.max():.0f} ℃", fontsize=10)
        case.fig(fig, "4_箱体温度.png")
        has_temp_fig = True
    else:
        has_temp_fig = False
except Exception:  # noqa: BLE001
    has_temp_fig = False
# 输出轴按新跨距复核（案例 A 的函数，支点换成新的右轴承）
mat40 = mdstd.material("40Cr-QT")
zB_new = SA.Z_BRG_A + SPAN
rech = []
for k, sec in SA.SECTIONS.items():
    zz_ = sec["z"] if sec["z"] < 100 else sec["z"] + (SPAN - SPAN_A)
    Ftg, Frg = SA.gear_forces()
    M_ = math.hypot(SA.moment(zz_, Ftg, SA.Z_GEAR, SA.Z_BRG_A, zB_new), SA.moment(zz_, Frg, SA.Z_GEAR, SA.Z_BRG_A, zB_new))
    if sec["notch"] == "keyseat":
        f = SA.fatigue_factors(sec, mat40, "ground")
    else:
        a = mdstd.kt_estimate("shoulder_round")
        f = SA.fatigue_factors(sec, mat40, "ground", (a["Kt"], a["Kts"]))
    Tq = SA.T_RATED if zz_ >= SA.Z_GEAR else 0.0
    M_old = SA.M_total(sec["z"])
    c = SA.safety(sec, mat40, f, M_, Tq)
    c0 = SA.safety(sec, mat40, f, M_old, Tq)
    rech.append((k, sec["what"][0], M_old / 1e3, M_ / 1e3, c0["S_ca"], c["S_ca"]))
rech_min = min(x[5] for x in rech)
simmd = f"""# 仿真：箱体热平衡、输出轴复核

## 箱体热平衡（数字工厂“仿真与分析”的热分析，CalculiX）

箱体按整机尺寸取：长 {HOUSE['L']:g}、宽 {HOUSE['W']:g}、高 {HOUSE['H']:g} mm，壁厚 10，HT200。热源是第 3 步的损耗 {fo8['loss_w']:.0f} W，加在箱内壁上；
外表面按 K_s = {fo8['K_s']} W/(m²·K) 向 20 ℃ 的车间散热（底面装在机座上，不计）。

{L.md_table(["方案", "有限元：外表面平均", "最高", "教材公式油温", "要求"], [
    [("无散热筋" if n else "无散热筋") if n == 0 else f"每侧 {n} 条散热筋（高 {p['fin_h']:g}、厚 {p['fin_t']:g}）", f"{st['t_surface_mean_c']:.1f} ℃", f"{st['t_max_c']:.1f} ℃", f"{fo['t_oil_c']:.1f} ℃", "≤ 80 ℃"]
    for n, (p, fo, st, _) in th.items()])}

**光箱体过热**：连续满载油温约 {th[0][1]['t_oil_c']:.0f} ℃，超过 80 ℃。两条路：加散热筋，或在输入轴上装风扇（实验 14 用流体分析算风扇）。
本案例选**每个长侧面 8 条散热筋**（铸出，不加工），公式算油温约 {fo8['t_oil_c']:.0f} ℃，有限元 {st8['t_surface_mean_c']:.0f} ℃。
光箱体两边几乎一样；加筋后有限元低 {fo8['t_oil_c'] - st8['t_surface_mean_c']:.0f} ℃：有限元把散热筋的全部面积都按同一个散热系数算，教材公式考虑到筋间空气流动差、只算一半面积。
校核取公式的值（偏保守）；筋间的实际散热系数要用流体分析或跑合台实测来定。
第 2 步提到的低速级大齿轮浸油偏深，搅油损失也在这 {fo8['loss_w']:.0f} W 里（效率按概略值），实际油温要在跑合台上实测核对。

## 输出轴按新跨距复核（案例 A 的函数）

{L.md_table(["截面", "位置", "弯矩（跨距 " + f"{SPAN_A:g}" + "）", "弯矩（跨距 " + f"{SPAN:g}" + "）", "S_ca 原", "S_ca 新"],
            [[k, w, f"{a:.0f} N·m", f"{b:.0f} N·m", f"{c:.2f}", f"{d:.2f}"] for k, w, a, b, c, d in rech])}

跨距加大后齿轮处弯矩变大，但最危险的外伸段根部只受扭，不受影响：最小 S_ca = {rech_min:.2f}，案例 A 的结论（40Cr）仍然成立。
"""
figs4 = [("4_热平衡.png", "箱体热平衡：有限元与教材公式", "Housing heat balance: FEA and textbook formula")]
if has_temp_fig:
    figs4.append(("4_箱体温度.png", "加散热筋后箱体外表面温度（有限元）", "Housing surface temperature with fins (FEA)"))
case.step("sim", f"光箱体满载油温约 {th[0][1]['t_oil_c']:.0f} ℃，超 80 ℃；每侧 8 条散热筋后约 {fo8['t_oil_c']:.0f} ℃（有限元 {st8['t_surface_mean_c']:.0f} ℃）；输出轴按新跨距复核 S_ca {rech_min:.2f}。",
          f"Plain housing runs at about {th[0][1]['t_oil_c']:.0f} °C, above 80 °C; with 8 fins per side about {fo8['t_oil_c']:.0f} °C (FEA {st8['t_surface_mean_c']:.0f} °C); output shaft rechecked at the new span, S_ca {rech_min:.2f}.",
          md=case.text("4_热平衡与复核.md", simmd), figs=figs4, tools=tools("cae"),
          facts=[("光箱体油温", "Plain housing oil", th[0][1]["t_oil_c"], "℃"), ("加筋后油温", "With fins", fo8["t_oil_c"], "℃"), ("输出轴 S_ca", "Output shaft S_ca", rech_min, "")])
case.check("sim", "加散热筋后满载油温（教材公式，偏保守）", "Full-load oil temperature with fins (textbook formula, conservative)", fo8["t_oil_c"], "<=", 80.0, "℃", "濮良贵《机械设计》")
case.check("sim", "输出轴按新跨距的疲劳安全系数", "Output shaft fatigue factor at the new span", rech_min, ">=", 1.5, "", "33.5.5 节")

# ================================================================ 5 三维装配与装配示意图
import build123d as bd  # noqa: E402


def shaft(segs):
    z, s = 0.0, None
    for d, Lg in segs:
        c = bd.Pos(0, 0, z) * bd.Cylinder(d / 2, Lg, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        s = c if s is None else s + c
        z += Lg
    return s


def ring(d, D, B):
    return bd.Cylinder(D / 2, B) - bd.Cylinder(d / 2, B + 1)


# 三根轴（从左轴承中心 z = 0 起；轴的左端在轴承左侧）
X = {"SH-101": 0.0, "SH-201": A1, "SH-301": A1 + A2}
parts = []
b5, b6, b7 = (mdstd.bearing(x) for x in ("6205", "6206", "6207"))
segs101 = [(25, b5["B"]), (30, Z_STAGE1 - B_SH101 / 2 - b5["B"] / 2 - 0), (30, 0.01)]
s101 = bd.Pos(0, 0, -b5["B"] / 2) * shaft([(25, b5["B"] / 2 + 10), (30, Z_STAGE1 - B_SH101 / 2 - 10), (30, B_SH101), (30, SPAN - Z_STAGE1 - B_SH101 / 2 - b5["B"] / 2),
                                           (25, b5["B"])])
s101 = s101 + bd.Pos(0, 0, -b5["B"] / 2 - 56) * shaft([(20, 36), (24, 20)])
pin1, _ = GL.gear_solid(MOD["SH-101"], Z["SH-101"], B_SH101, 1.0)
s201 = bd.Pos(0, 0, -b6["B"] / 2) * shaft([(30, b6["B"]), (35, SPAN - b6["B"]), (30, b6["B"])])
g202, _ = GL.gear_solid(MOD["GR-202"], Z["GR-202"], B_GR202, 35.0)
g203, _ = GL.gear_solid(MOD["GR-203"], Z["GR-203"], B_GR203, 35.0)
lay = SA.LAY_B
segsB = [(d, Lg + (SPAN - SPAN_A if i == 3 else 0)) for i, (d, Lg, *_) in enumerate(SA.SEG_B)]
s301 = bd.Pos(0, 0, -SA.Z_BRG_A) * shaft(segsB)
g302, _ = GL.gear_solid(MOD["GR-302"], Z["GR-302"], B_GR302, 40.0, hub=(64.0, 55.0), web=(15.0, g2["df2"] - 15))
asm = [
    bd.Pos(X["SH-101"], 0, 0) * s101, bd.Pos(X["SH-101"], 0, Z_STAGE1) * pin1,
    bd.Pos(X["SH-201"], 0, 0) * s201, bd.Pos(X["SH-201"], 0, Z_STAGE1) * bd.Rot(0, 0, 180 / Z["GR-202"]) * g202,
    bd.Pos(X["SH-201"], 0, Z_STAGE2) * g203,
    bd.Pos(X["SH-301"], 0, 0) * s301, bd.Pos(X["SH-301"], 0, Z_STAGE2) * bd.Rot(0, 0, 180 / Z["GR-302"]) * g302,
]
for code, b in (("SH-101", b5), ("SH-201", b6), ("SH-301", b7)):
    for zc in (0.0, SPAN):
        asm.append(bd.Pos(X[code], 0, zc - b["B"] / 2) * ring(b["d"], b["D"], b["B"]))
inner = bd.Compound(asm)
bd.export_step(inner, str(case.path("WQR-105-内部.step")))
L.render_solid(inner, case.path("5_三维装配.png"), elev=28, azim=-50, size=(9, 5))
# 装配示意图（俯视展开）：横向是中心距方向，竖向是轴线方向
fig, ax = plt.subplots(figsize=(8.6, 4.8))
from matplotlib.patches import Rectangle  # noqa: E402
for code, x0 in X.items():
    ax.add_patch(Rectangle((x0 - 3, -30), 6, SPAN + 60, color="#b8c4ce", zorder=1))
    b = mdstd.bearing(BRG[code])
    for zc in (0.0, SPAN):
        ax.add_patch(Rectangle((x0 - b["D"] / 2, zc - b["B"] / 2), b["D"], b["B"], fc="#7f9cb8", ec="k", lw=0.6, zorder=3))
    ax.text(x0, SPAN + 40, f"{code}\n{BRG[code]}", ha="center", va="bottom", fontsize=9)
for code, z, d, b, lab in (("SH-101", Z_STAGE1, MOD["SH-101"] * Z["SH-101"], B_SH101, "z24"), ("SH-201", Z_STAGE1, MOD["GR-202"] * Z["GR-202"], B_GR202, "GR-202"),
                           ("SH-201", Z_STAGE2, MOD["GR-203"] * Z["GR-203"], B_GR203, "GR-203"), ("SH-301", Z_STAGE2, MOD["GR-302"] * Z["GR-302"], B_GR302, "GR-302")):
    ax.add_patch(Rectangle((X[code] - d / 2, z - b / 2), d, b, fc="#d9a441", ec="k", lw=0.6, alpha=0.75, zorder=2))
    ax.text(X[code] + d / 2 - 3, z, lab, ha="right", va="center", fontsize=8)
for zc in (0.0, SPAN):
    ax.axhline(zc, color=L.MUTED, ls="--", lw=0.7)
ax.annotate("", (-60, 0), (-60, SPAN), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(-64, SPAN / 2, f"跨距 {SPAN:g}\n（案例 A 原为 {SPAN_A:g}）", ha="right", va="center", fontsize=9)
ax.set_xlim(-150, A1 + A2 + 130)
ax.set_ylim(-45, SPAN + 75)
ax.set_aspect("equal")
ax.set_xlabel("中心距方向 / mm（输入轴在 0）")
ax.set_ylabel("沿轴线 / mm")
case.fig(fig, "5_装配示意图.png")
bom_rows = [[it, F.ITEMS[it][0] if it in F.ITEMS else it, q] for it, q in F.BOMS["WQR-105"][1]]
cadmd = f"""# 三维装配与装配示意图

- **三维**：三根轴、四只齿轮（齿形都是第 4 步案例 B 同一种齿条展成）、六只轴承按第 3 步的轴向布置装好；箱体另见第 4 步热分析的模型（加了散热筋）。
  STEP 可在 FreeCAD 里打开、再加箱体。输出轴是案例 A 的 B 版，轴肩段加长了 {SPAN - SPAN_A:g} mm。
- **装配示意图**：俯视展开，第一级在右（靠输入端的另一侧）、第二级在左，两级齿轮在中间轴上并排、间隔 {GAP:g} mm。
- **物料清单**（工厂数据，WQR-105 一层）：

{L.md_table(["物料", "名称", "用量"], bom_rows)}

部件 SA-000（箱体合镗）、SA-100 / 200 / 300（三根轴部件）各有自己的物料清单，见“设计与工艺”页的“本厂物料”。
"""
LIBP = [L.lib_part("A-BRG-DG", b_) for b_ in ("6205", "6206", "6207")] + [
    L.lib_part("A-KEY-FLAT", "6x6x25"), L.lib_part("A-KEY-FLAT", "10x8x28"), L.lib_part("A-KEY-FLAT", "12x8x45"), L.lib_part("A-KEY-FLAT", "8x7x63"),
    L.lib_part("A-SEL-LIP", "20x40x7"), L.lib_part("A-SEL-LIP", "35x52x8"), L.lib_part("A-BLT-HEX", "M12x110"), L.lib_part("A-NUT-HEX", "M12"),
    L.lib_part("A-WSH-PLN", "M12"), L.lib_part("A-PIN-TAPER", "8x35"), L.lib_part("A-PLG-HEX", "M16x1.5"), L.lib_part("A-SCR-SHC", "M8x25")]
lib_bad = [b_ for b_ in ("6205", "6206", "6207") if any(float(L.lib_part("A-BRG-DG", b_)["row"][k + "_mm"]) != mdstd.bearing(b_)[k] for k in ("d", "D", "B"))]
cadmd += f"""
## 用到的零件库零件

物料清单里的标准件逐个在问渠零件库里对上编号：

{L.lib_md(LIBP, {"A-BRG-DG/6205": "输入轴 ×2", "A-BRG-DG/6206": "中间轴 ×2", "A-BRG-DG/6207": "输出轴 ×2", "A-KEY-FLAT/6x6x25": "输入轴伸",
                 "A-KEY-FLAT/10x8x28": "中间轴两只齿轮", "A-KEY-FLAT/12x8x45": "输出轴齿轮", "A-KEY-FLAT/8x7x63": "输出轴伸（案例 A，C 型同截面）",
                 "A-SEL-LIP/20x40x7": "输入端油封", "A-SEL-LIP/35x52x8": "输出端油封", "A-BLT-HEX/M12x110": "箱座箱盖联接 ×6",
                 "A-NUT-HEX/M12": "×6", "A-WSH-PLN/M12": "×6", "A-PIN-TAPER/8x35": "定位销 ×2", "A-PLG-HEX/M16x1.5": "放油螺塞",
                 "A-SCR-SHC/M8x25": "轴承端盖 ×24"})}

- 六只轴承的尺寸与计算用表 {'一致' if not lib_bad else '不一致：' + '、'.join(lib_bad)}；额定动载荷零件库没录，取《机械设计手册》表（教材 `std/gbt276_6200.yaml`）。
- 端盖螺钉：物料清单的 BOLT-M8x25 是内六角螺钉，对应零件库 `A-SCR-SHC/M8x25`（清单 `library` 字段已写明）。
- 透气塞、油标（VENT-M16、GAUGE-M12）零件库还没有，按外购件处理。
"""
case.check("cad", "轴承尺寸与零件库一致", "Bearing dimensions match the parts library", len(lib_bad), "==", 0, "", "零件库 A-BRG-DG")
case.step("cad", f"三根轴、四只齿轮、六只轴承按新布置装成三维；装配示意图标出跨距 {SPAN:g} mm；物料清单 {len(bom_rows)} 行。",
          f"Three shafts, four gears and six bearings assembled in 3D to the new layout; layout sketch with the {SPAN:g} mm span; {len(bom_rows)}-line BOM.",
          md=case.text("5_三维与装配.md", cadmd),
          figs=[("5_三维装配.png", "WQR-105 内部三维（不含箱体）", "WQR-105 internals in 3D (housing hidden)"), ("5_装配示意图.png", "装配示意图（俯视展开）", "Layout sketch (developed plan view)")],
          files=[("WQR-105-内部.step", "内部三维 STEP", "Internals (STEP)")], tools=tools("design", "3d") + L.lib_tools(LIBP[:3]),
          facts=[("跨距", "Span", SPAN, "mm"), ("物料清单", "BOM lines", len(bom_rows), "")])

# ================================================================ 6 装配工艺
from hub import process as PR  # noqa: E402

asm_rows = []
for it in ("SA-000", "SA-100", "SA-200", "SA-300", "WQR-105"):
    plan = PR.factory_plan(it)
    for o in plan["operations"]:
        asm_rows.append([it, o["seq"], o["operation"], o["workstation"], o["minutes"]])
procmd = f"""# 装配工艺

## 工艺路线（工厂数据）

{L.md_table(["部件 / 产品", "工序", "名称", "设备", "工时 / min"], asm_rows)}

## 装配顺序和要点

1. **合箱镗孔（SA-000）**：箱座、箱盖用两个定位销定位、6 个 M12 螺栓合紧后一起镗三对轴承孔——中心距 {A1:g}、{A2:g} 和三孔平行度靠这一道保证（中心距公差 ±0.03，案例 B 的齿轮图上有）。
   **散热筋**是铸出来的，不加工，模型改了要通知铸造厂改模样。
2. **三根轴部件（SA-100 / 200 / 300）**：齿轮按 H7/r6 压装（输出轴）或 H7/k6 加键（中间轴），轴承热装（加热到 80–100 ℃），装套筒、挡圈。
3. **总装**：三根轴部件放进箱座，合箱盖，装轴承端盖（调整垫片定轴向游隙 0.05–0.10）、油封、透气塞、油标；加 CKC220 齿轮油 {dict(F.BOMS['WQR-105'][1]).get('OIL-CKC220', 0):g} L（油位按第 2 步的下限）。
4. **跑合试验**：跑合台 test-01 按“工况模拟”（启动—运行—停机 × 3）记录输出转矩，查异响、温升、渗漏。
5. **出厂检验、清洗包装**。

轴向布置改了（跨距 {SPAN:g}），箱体图、输出轴图、中间轴图都要跟着改版——在“设计发布与审批”里一起发布、一起生效。
"""
case.step("process", f"5 个部件 / 产品、{len(asm_rows)} 道装配工序；合箱镗孔保证中心距；跨距改了，箱体、输出轴、中间轴一起改版。",
          f"Five assemblies, {len(asm_rows)} operations; line-boring holds the centre distances; with the new span the housing, output and intermediate shafts are revised together.",
          md=case.text("6_装配工艺.md", procmd), tools=tools("process", "design"), facts=[("装配工序", "Assembly operations", len(asm_rows), "")])

# ================================================================ 7 制造：合箱、部件、总装、跑合
from hub import mrp  # noqa: E402

shops = {it: L.run_shop(it, 10, f"WO-CASE-GB-C-{it}", seed=161) for it in ("SA-000", "SA-100", "SA-200", "SA-300", "WQR-105")}
mk_rows, good = [], 0
for it, sh in shops.items():
    last = [e for e in sh["events"] if e["event"] == "op_complete" and e.get("last_op")]
    g_ = sum(e["qty_good"] for e in last)
    if it == "WQR-105":
        good = g_
    mk_rows.append([it, " → ".join(o.split(" ")[0] for o, _ in sh["routing"]), g_, f"{sh['hours']:.1f} h"])
runin = []
for i in range(10):
    rec = SA.torque_series(serial=f"WQR-105-C{i + 1:03d}", work_order="WO-CASE-GB-C-WQR-105")[0]
    runin.append((f"WQR-105-C{i + 1:03d}", float(rec.max()), float(np.mean(rec[rec > 0.2 * RATED]))))
pk = [x[1] / RATED for x in runin]
fig, ax = plt.subplots(figsize=(8.2, 2.9))
ax.bar([x[0][-4:] for x in runin], [x[1] for x in runin], color=L.ACCENT, alpha=0.85, label="起动峰值")
ax.bar([x[0][-4:] for x in runin], [x[2] for x in runin], color="#8aa4bd", label="运行平均")
ax.axhline(RATED, color=L.MUTED, ls="--", lw=0.8)
ax.set_ylabel("输出转矩 / N·m")
ax.legend(fontsize=8.5, frameon=False, ncol=2)
case.fig(fig, "7_跑合记录.png")
mc, oc = mrp.std_unit_cost("WQR-105")
makemd = f"""# 在减速器厂装配 10 台

在仿真车间按现行工艺路线下达五张工单（各 10 套 / 台）：

{L.md_table(["工单", "工序", "完工", "用时"], mk_rows)}

## 跑合记录（跑合台 test-01，“工况模拟”启动—运行—停机 × 3）

10 台的起动峰值是额定的 {min(pk):.2f}–{max(pk):.2f} 倍——这就是案例 A 用来算疲劳的载荷谱，每台都留了记录（“数字孪生”页按序列号查得到）。

## 标准成本

数字工厂成本核算，物料按清单逐层汇总：材料 ${mc:.2f} + 加工 ${oc:.2f} = **${mc + oc:.2f} / 台**。
散热筋只改铸造模样，不加工，单件成本基本不变。

想自己走一遍：在“订单与计划”接一张 WQR-105 订单，算料会展开出这五张工单和齿轮、轴的零件工单；“数字孪生”页看每台的跑合记录；“经营与成本”看这张订单的毛利。
"""
case.step("make", f"五张工单各 10 套 / 台完工；跑合起动峰值 {min(pk):.2f}–{max(pk):.2f} 倍额定；标准成本 ${mc + oc:.2f}/台。",
          f"Five work orders of 10 completed; run-in start-up peaks {min(pk):.2f}–{max(pk):.2f}× rated; standard cost ${mc + oc:.2f} per unit.",
          md=case.text("7_装配与跑合.md", makemd), figs=[("7_跑合记录.png", "10 台跑合的起动峰值与运行平均转矩", "Run-in start-up peaks and running mean torque of 10 units")],
          tools=tools("planner", "operator", "twin", "finance"),
          facts=[("总装用时", "Final assembly", shops["WQR-105"]["hours"], "h"), ("标准成本", "Standard cost", f"${mc + oc:.2f}", "")])
case.check("make", "10 台总装、跑合、出厂完工", "Units through assembly, run-in and dispatch", good, "==", 10, "", "检验站")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

## 校核一览

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

## 整机设计改了什么

1. **箱体加宽**：放进中间轴的两只齿轮后，轴承跨距从案例 A 的 {SPAN_A:g} mm 加到 {SPAN:g} mm；输出轴轴肩段加长，复核后仍满足。**零件单独设计、放进整机再改**，这是整机设计最常见的一类改动。
2. **箱体加散热筋**：光箱体满载油温约 {th[0][1]['t_oil_c']:.0f} ℃，每侧 8 条散热筋后约 {fo8['t_oil_c']:.0f} ℃。
3. **第一级大齿轮齿宽定为 {B_GR202:g}**，两级齿面接触余量相当。
4. **传动比分配保持 3 × 3.5**：低速级浸油偏深，下一代产品改 i₁ > i₂。

## 三个案例连起来看

- 案例 A 只看输出轴，定了结构和材料（40Cr）；
- 案例 B 只看低速级齿轮，发现关键在大齿轮齿面（D 点余量很小）；
- 案例 C 把它们放进整机：跨距要改、箱体要加筋、浸油偏深——**单个零件都对，放在一起不一定对**。

## 留给学生的问题

1. 不加散热筋，在输入轴上装风扇：风扇要吹出多大的散热系数，油温才到 80 ℃？（用实验 14 的流体分析）
2. 把传动比改成 3.5 × 3，两级齿轮的齿数、中心距怎么取？箱体长度、浸油深度变多少？
3. 中间轴上两个圆周力同向，所以中间轴受力最大。如果输入轴和输出轴放在中间轴的同一侧（不在一个平面上），会怎样？
4. 第二级大齿轮 D 点接触余量只有 1% 左右（案例 B）。整机寿命 {LIFE_H:,.0f} h 里，最先坏的会是哪个零件？

相关：《机械设计》第 33 章与齿轮传动、减速器各章，《机器人学》32.1 节，实验 7（数字工厂闭环）、实验 11（热平衡与轻量化）、实验 14（风扇冷却）、实验 33（一张非标订单）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；整机反过来改了零件：跨距 {SPAN_A:g} → {SPAN:g}、箱体加筋。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; the whole machine changed its parts: span {SPAN_A:g} → {SPAN:g}, housing fins.",
          md=case.text("8_总结.md", review), tools=tools("design"))
case.write()
