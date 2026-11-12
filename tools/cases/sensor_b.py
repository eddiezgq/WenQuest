"""第 161e 轮：传感器厂案例 B——关节扭矩传感器 WQ-TS 的弹性体：轮辐 + 剪切腹板，手算 → 有限元 → 改版 → 交外协加工。

    python3 tools/cases/sensor_b.py

有限元用数字工厂“仿真与分析”同一个求解器（cae/solve.py，Gmsh + CalculiX），几何与电桥在 tools/cases/tslib.py；
制造用传感器厂仿真车间（扭矩传感器线）。输出到 factory/cases/sensor/B/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-sensor.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import tslib as T  # noqa: E402

TOOLS = {
    "cae": ("仿真与分析（结构有限元）", "Simulation & analysis (FEA)", "/cae"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "supply": ("采购与供应商", "Purchasing & suppliers", "/supply"),
    "inst": ("虚拟仪器（扭矩传感器）", "Virtual instruments (torque sensor)", "/instruments"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("sensor", "B", "中等", "扭矩传感器弹性体：轮辐与剪切腹板", "Torque-sensor flexure: spokes with shear webs", "WQ-TS 弹性体 BODY-TS",
              "给关节扭矩传感器设计弹性体：比较三种结构，手算剪切腹板的应变，再用有限元复核——手算高估了近一倍，改版加宽、减薄腹板；"
              "复核过载、刚度、侧向力串扰，定外协加工要求，传感器厂按它做 20 台。",
              "Designing the flexure of a joint torque sensor: three structures compared, shear-web strain by hand, then FEA — the hand calculation overestimates by nearly 2×, "
              "so the web is widened and thinned; overload, stiffness and cross-talk checked, machining requirements set, 20 sensors built.",
              "tools/cases/sensor_b.py")

CSF = L.lib_part("D-RDC-HD-CSF", "25-100")
K3 = float(CSF["row"]["K3_1e4_Nm_rad"]) * 1e4
T_REP, T_MOM = float(CSF["row"]["T_repeat_Nm"]), float(CSF["row"]["T_momentary_Nm"])
K_MIN = 4 * K3                      # 串联后整个关节刚度下降不超过 20 %：k_s ≥ 4·K3
MV_MIN = 1.0                        # 额定输出 ≥ 1.0 mV/V（信号调理板按 1.0–1.6 mV/V 设计，案例 A）
XT_MAX = 0.5                        # 串扰 ≤ 0.5 %FS
FX_TEST, MX_TEST = 1000.0, 20.0     # 串扰工况：径向力 1 kN、倾覆力矩 20 N·m（关节交叉滚子轴承漏过来的量级，示例）

# ================================================================ 1 任务书
brief = f"""# 设计任务书：关节扭矩传感器的弹性体

**用在哪**　传感器厂的 WQ-TS（应变片全桥，量程 ±{T.T_FS:g} N·m）。目标客户是协作机器人厂的中关节（和问渠 WQJ-M 同级：谐波减速器 25 号、减速比 100），
传感器装在减速器输出和关节输出法兰之间，直接测关节力矩，用于力控、碰撞检测。

| 项目 | 要求 | 出处 |
|---|---|---|
| 量程 | ±{T.T_FS:g} N·m（覆盖减速器重复峰值 {T_REP:g} N·m） | 零件库 `D-RDC-HD-CSF/25-100`（厂商目录） |
| 过载 | {T.T_OVL:g} N·m（150 %FS，覆盖瞬时最大 {T_MOM:g} N·m）不屈服，安全系数 ≥ 2 | 同上 |
| 额定输出 | ≥ {MV_MIN} mV/V（全桥，灵敏系数 {T.GF}） | 案例 A 信号调理板的设计输入 |
| 扭转刚度 | ≥ 4 × K3 = {K_MIN:.3g} N·m/rad（与减速器串联后关节刚度下降 ≤ 20 %） | 零件库 K3 = {K3:.3g} N·m/rad |
| 串扰 | 径向力 {FX_TEST:g} N、倾覆力矩 {MX_TEST:g} N·m 引起的输出 ≤ {XT_MAX} %FS | 本案例设定 |
| 外形 | 外径 ≤ 90 mm（减速器外径 {CSF['row']['OD_mm']} mm）、中空 ≥ Ø20（走线） | 关节结构 |
| 材料 | 17-4PH 不锈钢（清单 BODY-TS） | 传感器厂清单 |

**要定的**：弹性体结构、轮辐和腹板尺寸、应变片位置、安装螺钉；外协加工要求。
"""
case.step("brief", f"±{T.T_FS:g} N·m、过载 {T.T_OVL:g} N·m；额定输出 ≥ {MV_MIN} mV/V、刚度 ≥ {K_MIN:.3g} N·m/rad、串扰 ≤ {XT_MAX} %FS；外径 ≤ 90。",
          f"±{T.T_FS:g} N·m, overload {T.T_OVL:g} N·m; rated output ≥ {MV_MIN} mV/V, stiffness ≥ {K_MIN:.3g} N·m/rad, cross-talk ≤ {XT_MAX} %FS; OD ≤ 90.",
          md=case.text("1_任务书.md", brief), tools=tools("engineer") + L.lib_tools([CSF]),
          facts=[("量程", "Range", T.T_FS, "N·m"), ("过载", "Overload", T.T_OVL, "N·m"), ("刚度下限", "Min. stiffness", round(K_MIN), "N·m/rad")])

# ================================================================ 2 方案
concept = f"""# 方案：弹性体结构

应变片只能测表面应变。额定力矩下要有足够大的应变（输出大、信噪比高），但整个零件又要硬（关节刚度）、强（过载）、对别的力不敏感（串扰）——
这几条互相矛盾，结构形式决定了能调和到什么程度。

| 结构 | 测什么 | 输出 | 刚度 | 串扰 | 结论 |
|---|---|---|---|---|---|
| 薄壁圆管 | 表面剪应变（应变片 ±45°） | 管壁薄才够大 | 薄壁管扭转刚度低 | 弯矩、轴向力对剪应变影响小 | 长度方向占地方，关节里放不下 |
| 十字梁（4 根梁弯曲） | 梁侧面弯曲应变 | 大 | 低（梁要细长） | 倾覆力矩直接弯梁，串扰大 | 刚度、串扰都不够 |
| **轮辐 + 剪切腹板** | 腹板中心的剪应变 | 腹板越薄越大 | 两侧厚壁抗弯，刚度高 | 相对轮辐串联抵消 | **选定** |

**轮辐 + 剪切腹板**：外圈、内毂、4 根轮辐。每根轮辐中段从两面各铣一个凹槽，只留中间一层薄腹板，截面成“工”字——
两侧厚壁承担弯曲（刚度），薄腹板集中承担剪力（应变大），应变片贴在腹板中心（弯曲应变为零的中性轴、反弯点上，只剩剪应变）。

**组桥**：每根轮辐一片剪切型双栅（±45° 两个栅），共 4 片 8 个栅；每个桥臂由相对两根轮辐上同方向的两个栅串联（700 Ω）——
力矩让 4 根轮辐的剪应变同号，相加；径向力让相对两根轮辐的剪应变反号，在串联里抵消；温度让所有栅一起变，在电桥里抵消。
"""
case.step("concept", "三种结构比较，选轮辐 + 剪切腹板：厚壁抗弯给刚度，薄腹板集中剪应变；相对轮辐的栅串联抵消串扰。",
          "Three structures compared; spokes with shear webs chosen: thick walls give stiffness, thin webs concentrate shear strain; grids on opposite spokes in series cancel cross-talk.",
          md=case.text("2_方案.md", concept), tools=tools("engineer"))

# ================================================================ 3 计算：第一版手算
g1, g2 = T.GEOM_V1, T.GEOM
hc1, hc2 = T.handcalc(g1), T.handcalc(g2)
calcmd = f"""# 计算：第一版尺寸（手算）

**几何**（mm）：外圈 R{g1['R_o']:g}/R{g1['R_ri']:g}，内毂 R{g1['R_ho']:g}，中孔 Ø{2 * g1['R_b']:g}，厚 {g1['H']:g}；轮辐宽 {g1['B']:g}、长 {g1['R_ri'] - g1['R_ho']:g}；
凹槽 {g1['PL']:g}（径向）× {g1['PW']:g}（切向），腹板厚 t_w = {g1['TW']:g}。

**轮辐的剪力**：把轮辐看成两端固定、可以相对平移的短梁（内毂转、外圈不动），反弯点在中点。对内毂取矩：

  T = 4·(V·R_ho + V·L/2) = 4·V·R_mid　→　V = T / (4·R_mid) = {T.T_FS:g}×10³ / (4 × {T.r_mid(g1):g}) = **{hc1['V_N']:.0f} N**

**腹板中心的剪应力**（工字截面，绕轴线方向弯曲）：

  I = {hc1['I_mm4']:.0f} mm⁴，中性轴以外面积矩 Q = {hc1['Q_mm3']:.0f} mm³
  τ = V·Q / (I·t_w) = {hc1['V_N']:.0f} × {hc1['Q_mm3']:.0f} / ({hc1['I_mm4']:.0f} × {g1['TW']:g}) = **{hc1['tau_mpa']:.0f} MPa**
  γ = τ / G = {hc1['tau_mpa']:.0f} / {T.G_MPA:.0f} = **{hc1['gamma'] * 1e6:.0f} μ**（G = E / 2(1+ν)，17-4PH：E {T.MAT['E_mpa'] / 1000:g} GPa、ν {T.MAT['nu']}）

**电桥输出**：±45° 栅的应变 = ±γ/2，四个臂 → Vout/Vex = GF·γ/2 = {T.GF} × {hc1['gamma'] * 1e6:.0f}×10⁻⁶ / 2 = **{hc1['mv_v']:.2f} mV/V**

**轮辐根部弯曲**：M = V·L/2 = {hc1['M_root_nmm'] / 1000:.1f} N·m，σ = M·(B/2)/I = {hc1['sig_root_mpa']:.0f} MPa——厚壁让弯曲应力很小。

手算第一版满足 ≥ {MV_MIN} mV/V，看起来还有富余。下一步用有限元复核。
"""
case.step("calc", f"第一版（腹板 {g1['TW']:g} mm、凹槽 {g1['PL']:g}×{g1['PW']:g}）：轮辐剪力 {hc1['V_N']:.0f} N，腹板剪应力 {hc1['tau_mpa']:.0f} MPa，手算输出 {hc1['mv_v']:.2f} mV/V。",
          f"Version 1 (web {g1['TW']:g} mm, pocket {g1['PL']:g}×{g1['PW']:g}): spoke shear {hc1['V_N']:.0f} N, web shear stress {hc1['tau_mpa']:.0f} MPa, hand-calculated output {hc1['mv_v']:.2f} mV/V.",
          md=case.text("3_计算书.md", calcmd), tools=tools("cae"),
          facts=[("轮辐剪力", "Spoke shear force", round(hc1["V_N"]), "N"), ("手算输出", "Hand-calc output", round(hc1["mv_v"], 2), "mV/V")])

# ================================================================ 4 仿真：有限元
print("有限元：第一版、定稿、过载、串扰、网格、腹板公差……")
f1 = T.fea(g1, "torque", T.T_FS)
f2 = T.fea(g2, "torque", T.T_FS)
f2b = T.fea(g2, "torque", T.T_FS, h=1.6)
ffx = T.fea(g2, "fx", FX_TEST)
fmx = T.fea(g2, "mx", MX_TEST)
fthin = T.fea(dict(g2, TW=g2["TW"] - 0.05), "torque", T.T_FS)
fthick = T.fea(dict(g2, TW=g2["TW"] + 0.05), "torque", T.T_FS)
mv1, mv2 = abs(f1["mv_v"]), abs(f2["mv_v"])
k1, k2 = T.T_FS / f1["theta_rad"], T.T_FS / f2["theta_rad"]
vm_ovl = f2["stats"]["vm_max_mpa"] * T.T_OVL / T.T_FS
sf_ovl = T.MAT["yield_mpa"] / vm_ovl
xt_fx = abs(ffx["mv_v"]) / mv2 * 100
xt_mx = abs(fmx["mv_v"]) / mv2 * 100
xt_fx_single = abs(ffx["gauges"][1][2]) / abs(f2["gauges"][1][2]) * 100     # 只用一根轮辐（不串联）时的串扰
mesh_diff = abs(abs(f2b["mv_v"]) / mv2 - 1) * 100
dS_dt = (abs(fthin["mv_v"]) - abs(fthick["mv_v"])) / 0.10 / mv2 * 100     # 每 0.01 mm 腹板厚度变化，输出变化 %……按 0.1 mm 差分
dS_001 = dS_dt / 10

# 图 1：正面应力云图（第一版、定稿）
fig, axs = plt.subplots(1, 2, figsize=(9.2, 4.4))
for ax, fr, gg, ttl in ((axs[0], f1, g1, "第一版"), (axs[1], f2, g2, "定稿")):
    sf = fr["surf"]
    pos, tri, vm = sf["positions"], sf["triangles"], sf["vm"]
    zc = pos[tri][:, :, 2].mean(1)
    sel = zc > gg["TW"] / 2 - 1e-3           # 朝 +z 的面（正面、凹槽底）
    tp = plt.matplotlib.tri.Triangulation(pos[:, 0], pos[:, 1], tri[sel])
    cs = ax.tripcolor(tp, vm, shading="gouraud", cmap="viridis", vmin=0, vmax=200)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(f"{ttl}：腹板 {gg['TW']:g} mm，凹槽 {gg['PL']:g}×{gg['PW']:g}", fontsize=9.5)
    for k in range(4):
        a = math.radians(90 * k)
        cx, cy = T.r_mid(gg) * math.cos(a), T.r_mid(gg) * math.sin(a)
        ax.add_patch(plt.Rectangle((cx - T.GAUGE / 2, cy - T.GAUGE / 2), T.GAUGE, T.GAUGE, fill=False, ec="w", lw=0.8))
fig.colorbar(cs, ax=axs, shrink=0.7, label=f"冯·米塞斯应力 / MPa（{T.T_FS:g} N·m）")
case.fig(fig, "4_应力云图.png")

# 图 2：每根轮辐的剪应变（扭矩、径向力），说明串联抵消
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.0))
x = np.arange(4)
axs[0].bar(x, [-v[2] * 1e6 for v in f2["gauges"]], color=L.ACCENT)
axs[0].set_xticks(x, [f"轮辐 {i + 1}" for i in x])
axs[0].set_ylabel("腹板剪应变 / μ")
axs[0].set_title(f"力矩 {T.T_FS:g} N·m：四根同号", fontsize=9.5)
axs[1].bar(x, [-v[2] * 1e6 for v in ffx["gauges"]], color="#8aa4bd")
axs[1].set_xticks(x, [f"轮辐 {i + 1}" for i in x])
axs[1].set_title(f"径向力 {FX_TEST:g} N：轮辐 2、4 反号，串联抵消", fontsize=9.5)
axs[1].axhline(0, color=L.MUTED, lw=0.6)
case.fig(fig, "4_剪应变与串扰.png")

simmd = f"""# 仿真：有限元复核（数字工厂“仿真与分析”同一个求解器）

外圈外圆固定，内孔加 {T.T_FS:g} N·m 扭矩；Gmsh 二阶四面体、网格 2 mm，CalculiX 线性静力。应变取正面凹槽底腹板中心 {T.GAUGE:g}×{T.GAUGE:g} mm（应变片敏感栅）的平均。

## 第一版不行：手算高估了近一倍

| | 手算 | 有限元 |
|---|---|---|
| 腹板剪应变 | {hc1['gamma'] * 1e6:.0f} μ | {abs(np.mean([v[2] for v in f1['gauges']])) * 1e6:.0f} μ |
| 电桥输出 | {hc1['mv_v']:.2f} mV/V | **{mv1:.2f} mV/V**（< {MV_MIN}） |

**为什么**：轮辐只有 {g1['R_ri'] - g1['R_ho']:g} mm 长、{g1['B']:g} mm 宽，根本不是细长梁；凹槽只占中间 {g1['PL']:g} mm，两头是实心段，
剪力在腹板和侧壁之间重新分配，“工”字截面公式的前提（剪力全由截面按 Q/I 分配）不成立——侧壁比公式认为的多扛了一大块。短而粗的零件，手算只能定方向，数要靠有限元。

## 改版：凹槽加长、加宽，腹板减薄

把凹槽改成 {g2['PL']:g}×{g2['PW']:g}（侧壁 {(g2['B'] - g2['PW']) / 2:g} mm）、腹板 {g2['TW']:g} mm：

{L.md_table(["量", "第一版", "定稿", "要求"], [
    ["电桥输出 mV/V", f"{mv1:.3f}", f"**{mv2:.3f}**", f"≥ {MV_MIN}"],
    ["扭转刚度 N·m/rad", f"{k1:.3g}", f"{k2:.3g}", f"≥ {K_MIN:.3g}"],
    [f"最大应力 MPa（{T.T_FS:g} N·m）", f"{f1['stats']['vm_max_mpa']:.0f}", f"{f2['stats']['vm_max_mpa']:.0f}", "—"],
    [f"过载 {T.T_OVL:g} N·m 最大应力 / 安全系数", "—", f"{vm_ovl:.0f} MPa / {sf_ovl:.1f}", "≥ 2（屈服 1000 MPa）"],
])}

（定稿手算 {hc2['mv_v']:.2f} mV/V，有限元 {mv2:.2f}——手算仍然偏高，但已经知道偏多少。）

## 串扰：相对轮辐串联抵消

{L.md_table(["工况", "电桥输出", "占满量程"], [
    [f"径向力 {FX_TEST:g} N", f"{ffx['mv_v']:.5f} mV/V", f"{xt_fx:.3f} %FS"],
    [f"倾覆力矩 {MX_TEST:g} N·m", f"{fmx['mv_v']:.5f} mV/V", f"{xt_mx:.3f} %FS"],
    [f"（对照）只用一根轮辐的栅，径向力 {FX_TEST:g} N", "—", f"{xt_fx_single:.1f} %FS"],
])}

径向力让轮辐 2、4 的剪应变一正一负（图），单看一根轮辐串扰有 {xt_fx_single:.1f} %FS；相对两根串联后几乎为零。前提是四片应变片贴得对称——贴偏了抵消就不完全（案例 C 的标定会测出来）。

## 网格与腹板公差

- 网格 2 mm 与 1.6 mm 的输出相差 **{mesh_diff:.2f} %**，网格够细。
- 腹板厚度 ±0.05 mm：输出 {abs(fthick['mv_v']):.3f}–{abs(fthin['mv_v']):.3f} mV/V，**每 0.01 mm 变化约 {dS_001:.1f} %**——腹板是这个零件最关键的尺寸（第 6 步定公差）。
"""
case.step("sim", f"有限元：第一版只有 {mv1:.2f} mV/V（手算 {hc1['mv_v']:.2f}），改版后 {mv2:.2f} mV/V；刚度 {k2:.3g} N·m/rad，过载安全系数 {sf_ovl:.1f}，串扰 ≤ {max(xt_fx, xt_mx):.2f} %FS。",
          f"FEA: version 1 gives only {mv1:.2f} mV/V (hand calc {hc1['mv_v']:.2f}); revised {mv2:.2f} mV/V; stiffness {k2:.3g} N·m/rad, overload safety factor {sf_ovl:.1f}, cross-talk ≤ {max(xt_fx, xt_mx):.2f} %FS.",
          md=case.text("4_有限元复核.md", simmd),
          figs=[("4_应力云图.png", "正面应力云图：第一版与定稿（白框 = 应变片）", "Front-face stress: version 1 and final (white squares = gauges)"),
                ("4_剪应变与串扰.png", "每根轮辐腹板的剪应变：力矩与径向力", "Web shear strain per spoke: torque vs radial force")],
          tools=tools("cae"),
          facts=[("第一版输出", "Version-1 output", round(mv1, 3), "mV/V"), ("定稿输出", "Final output", round(mv2, 3), "mV/V"),
                 ("扭转刚度", "Torsional stiffness", round(k2), "N·m/rad"), ("过载安全系数", "Overload safety factor", round(sf_ovl, 2), "")])
case.check("sim", "第一版有限元输出（不满足，改版）", "Version-1 FEA output (fails, revised)", round(mv1, 3), "<", MV_MIN, "mV/V", "有限元：说明为什么改版")
case.check("sim", "定稿额定输出", "Final rated output", round(mv2, 3), ">=", MV_MIN, "mV/V", "任务书")
case.check("sim", "扭转刚度", "Torsional stiffness", round(k2), ">=", round(K_MIN), "N·m/rad", "4 × K3（零件库）")
case.check("sim", "过载 300 N·m 对屈服的安全系数", "Yield safety factor at 300 N·m", round(sf_ovl, 2), ">=", 2.0, "", "任务书")
case.check("sim", "径向力 1 kN 串扰", "Cross-talk, 1 kN radial force", round(xt_fx, 3), "<=", XT_MAX, "%FS", "任务书")
case.check("sim", "倾覆力矩 20 N·m 串扰", "Cross-talk, 20 N·m tilting moment", round(xt_mx, 3), "<=", XT_MAX, "%FS", "任务书")
case.check("sim", "网格 2 mm 与 1.6 mm 输出相差", "Output difference, 2 mm vs 1.6 mm mesh", round(mesh_diff, 2), "<=", 2.0, "%", "网格收敛")

# ================================================================ 5 三维与图纸、安装螺钉
import build123d as bd  # noqa: E402

body = T.solid(g2, holes=True)
bd.export_step(body, str(case.path("BODY-TS.step")))
L.render_solid(body, case.path("5_弹性体三维.png"), elev=38, azim=-58, size=(6.4, 5.0), swap=False)

# 安装螺钉：零件库内六角圆柱头螺钉（12.9 级）；预紧力 F = 0.7·Rp0.2·As（ISO 898-1：12.9 级 Rp0.2 ≥ 1100 MPa；应力截面 M5 14.2、M6 20.1 mm²）
AS = {"M5": 14.2, "M6": 20.1}
MU = 0.15                     # 钢对钢、干的结合面摩擦系数（示例，常用设计取值）
SLIP_SF = 1.2
TAU_PIN = 100.0               # 圆锥销（GB/T 117 / ISO 2339，不淬火）许用剪应力 MPa（示例取值）
T_run = T_REP * SLIP_SF       # 正常工作（减速器重复峰值）不打滑
F_V = {k: 0.7 * 1100 * a for k, a in AS.items()}
SCR_RIM = L.lib_part("A-SCR-SHC", "M5x20")
T_rim = 8 * F_V["M5"] * MU * T.HOLE_R_RIM / 1000
hub_opts = []
for scr, pin, sz, psz in (("M5", 5.0, "M5x25", "5x24"), ("M6", 6.0, "M6x25", "6x30")):
    t_f = 6 * F_V[scr] * MU * T.HOLE_R_HUB / 1000
    f_p = max(0.0, (T.T_OVL - t_f) * 1000 / T.HOLE_R_HUB / 2)
    tau = f_p / (math.pi * pin ** 2 / 4)
    hub_opts.append(dict(scr=scr, pin=pin, sz=sz, psz=psz, t_f=t_f, f_p=f_p, tau=tau, ok=t_f >= T_run and tau <= TAU_PIN))
HUB = next(o for o in hub_opts if o["ok"])
SCR_HUB = L.lib_part("A-SCR-SHC", HUB["sz"])
PIN = L.lib_part("A-PIN-TAPER", HUB["psz"])
T_hub, tau_pin = HUB["t_f"], HUB["tau"]

# 图纸（俯视 + 剖面，主要尺寸）
fig, axs = plt.subplots(1, 2, figsize=(10, 5.0), gridspec_kw={"width_ratios": [1.15, 1]})
ax = axs[0]
th = np.linspace(0, 2 * np.pi, 361)
for r, ls in ((g2["R_o"], "-"), (g2["R_ri"], "-"), (g2["R_ho"], "-"), (g2["R_b"], "-"), (T.HOLE_R_RIM, "-."), (T.HOLE_R_HUB, "-.")):
    ax.plot(r * np.cos(th), r * np.sin(th), ls, color=L.INK if ls == "-" else L.MUTED, lw=0.9 if ls == "-" else 0.5)
for k in range(4):
    a = math.radians(90 * k)
    c, s_ = math.cos(a), math.sin(a)
    for sgn in (1, -1):        # 轮辐两侧边
        x0, x1 = g2["R_ho"], g2["R_ri"]
        yy = sgn * g2["B"] / 2
        ax.plot([x0 * c - yy * s_, x1 * c - yy * s_], [x0 * s_ + yy * c, x1 * s_ + yy * c], color=L.INK, lw=0.9)
    rm = T.r_mid(g2)
    px = np.array([-1, 1, 1, -1, -1]) * g2["PL"] / 2 + rm
    py = np.array([-1, -1, 1, 1, -1]) * g2["PW"] / 2
    ax.plot(px * c - py * s_, px * s_ + py * c, color=L.ACCENT, lw=0.9)
    ax.add_patch(plt.Rectangle((rm * c - 1.5, rm * s_ - 1.5), 3, 3, fc=L.ACCENT, alpha=0.35, ec="none"))
for k in range(8):
    a = math.radians(22.5 + 45 * k)
    ax.add_patch(plt.Circle((T.HOLE_R_RIM * math.cos(a), T.HOLE_R_RIM * math.sin(a)), 2.75, fill=False, ec=L.INK, lw=0.7))
for k in range(8):
    a = math.radians(45 * k)
    ax.add_patch(plt.Circle((T.HOLE_R_HUB * math.cos(a), T.HOLE_R_HUB * math.sin(a)), 2.5 if k % 4 else 3.0, fill=False, ec=L.INK if k % 4 else L.BAD, lw=0.7))
ax.annotate(f"Ø{2 * g2['R_o']:g}", (0, -g2["R_o"]), (0, -g2["R_o"] - 7), ha="center", fontsize=8.5)
ax.text(0, 0, f"Ø{2 * g2['R_b']:g}", ha="center", va="center", fontsize=8)
ax.text(T.r_mid(g2) + 1, -g2["PW"] / 2 - 4.5, f"凹槽 {g2['PL']:g}×{g2['PW']:g}", fontsize=7.5, color=L.ACCENT, ha="center")
fig.text(0.02, 0.07, f"外圈 8×M5 通孔 Ø5.5（分布圆 Ø{2 * T.HOLE_R_RIM:g}）\n内毂 6×{HUB['scr']} 螺纹孔 + 2×Ø{HUB['pin']:g} 锥销孔（红，分布圆 Ø{2 * T.HOLE_R_HUB:g}）",
        fontsize=7.5, va="bottom")
ax.set_aspect("equal")
ax.set_axis_off()
ax.set_title("俯视（蓝框 = 凹槽，蓝块 = 应变片位置）", fontsize=9)
ax = axs[1]                      # 沿轮辐的剖面：外圈—轮辐（凹槽、腹板）—内毂
H, TW = g2["H"], g2["TW"]
pts_top = [(g2["R_b"], H / 2), (g2["R_o"], H / 2)]
ax.add_patch(plt.Rectangle((g2["R_b"], -H / 2), g2["R_o"] - g2["R_b"], H, fc="#dfe6ee", ec=L.INK, lw=0.9))
rm = T.r_mid(g2)
for z in (1, -1):
    ax.add_patch(plt.Rectangle((rm - g2["PL"] / 2, (TW / 2 if z > 0 else -H / 2)), g2["PL"], (H - TW) / 2, fc="white", ec=L.ACCENT, lw=0.9))
ax.annotate("", (rm - g2["PL"] / 2, H / 2 + 3), (rm + g2["PL"] / 2, H / 2 + 3), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(rm, H / 2 + 3.6, f"{g2['PL']:g}", ha="center", fontsize=8)
ax.annotate("", (rm + g2["PL"] / 2 + 2.5, -TW / 2), (rm + g2["PL"] / 2 + 2.5, TW / 2), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(rm + g2["PL"] / 2 + 3.2, 0, f"腹板 {TW:.2f}±0.01", va="center", fontsize=8, color=L.BAD)
ax.annotate("", (g2["R_b"] - 1.2, -H / 2), (g2["R_b"] - 1.2, H / 2), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(g2["R_b"] - 1.8, 0, f"{H:g}", va="center", ha="right", fontsize=8)
for xr, lab in ((g2["R_ho"], f"R{g2['R_ho']:g}"), (g2["R_ri"], f"R{g2['R_ri']:g}")):
    ax.axvline(xr, color=L.MUTED, lw=0.5, ls=":")
    ax.text(xr, -H / 2 - 2.5, lab, ha="center", fontsize=7.5)
ax.text(rm, TW / 2 + 0.6, "应变片", ha="center", fontsize=7, color=L.ACCENT)
ax.set_xlim(g2["R_b"] - 5, g2["R_o"] + 2)
ax.set_ylim(-H / 2 - 6, H / 2 + 7)
ax.set_aspect("equal")
ax.set_axis_off()
ax.set_title("沿轮辐剖面（右半）", fontsize=9)
fig.text(0.02, 0.01, "材料 17-4PH（ASTM A564 Type 630），H1025 时效；应变片区 Ra ≤ 0.4 μm；未注倒角 C0.3、凹槽圆角 R0.5；示例设计", fontsize=7.5, color=L.MUTED)
case.fig(fig, "5_弹性体图纸.png")

cadmd = f"""# 三维、图纸与安装螺钉

定稿：外径 Ø{2 * g2['R_o']:g}、厚 {g2['H']:g}、中孔 Ø{2 * g2['R_b']:g}；4 根轮辐宽 {g2['B']:g}；凹槽 {g2['PL']:g}×{g2['PW']:g}，腹板 **{g2['TW']:.2f} mm**。三维 `BODY-TS.step`（带安装孔）。

## 安装螺钉、销（零件库）

结合面打滑会让零点跳、滞后变大。两条要求：**正常工作**（减速器重复峰值 {T_REP:g} N·m × 防滑系数 {SLIP_SF} = {T_run:.0f} N·m）只靠螺钉摩擦、不打滑；
**过载 {T.T_OVL:g} N·m** 时允许摩擦面微动，由圆锥销剪切兜底，销子剪应力 ≤ {TAU_PIN:g} MPa（不淬火锥销，示例许用值）。
单个 12.9 级螺钉预紧力 F = 0.7·Rp0.2·As（ISO 898-1）：M5 {F_V['M5'] / 1000:.1f} kN、M6 {F_V['M6'] / 1000:.1f} kN；摩擦系数 {MU}（钢对钢、干，示例）。

**外圈**（8 × M5，分布圆 Ø{2 * T.HOLE_R_RIM:g}）：摩擦能传 {T_rim:.0f} N·m，连过载 × {SLIP_SF} 都不打滑 ✓。

**内毂**（分布圆只有 Ø{2 * T.HOLE_R_HUB:g}，6 个螺钉 + 2 个锥销）：

{L.md_table(["方案", "摩擦能传 N·m", f"正常 ≥ {T_run:.0f}", f"过载时每个销受力 N", f"销剪应力 MPa（≤ {TAU_PIN:g}）", "结论"],
            [[f"6×{o['scr']} + 2×Ø{o['pin']:g} 销", f"{o['t_f']:.0f}", "✓" if o["t_f"] >= T_run else "✗", f"{o['f_p']:.0f}", f"{o['tau']:.0f}", "**选定**" if o is HUB else "不够"] for o in hub_opts])}

内毂直径小、摩擦半径小——第一次按 M5 算不够，改成 M6 螺钉、Ø6 锥销。

{L.lib_md([SCR_RIM, SCR_HUB, PIN], {SCR_RIM['ref']: "外圈 ×8（穿过外圈 14 mm，拧进输出法兰 6 mm）", SCR_HUB['ref']: "内毂 ×6（从减速器侧拧进内毂）", PIN['ref']: "内毂 ×2（与减速器配铰）"})}
"""
case.step("cad", f"定稿三维与图纸：Ø{2 * g2['R_o']:g}×{g2['H']:g}，腹板 {g2['TW']:.2f}；外圈 8×M5；内毂 M5 摩擦不够，改 6×{HUB['scr']} + 2×Ø{HUB['pin']:g} 锥销。",
          f"Final 3D model and drawing: Ø{2 * g2['R_o']:g}×{g2['H']:g}, web {g2['TW']:.2f}; 8×M5 on the rim; M5 on the hub is not enough, changed to 6×{HUB['scr']} + 2×Ø{HUB['pin']:g} taper pins.",
          md=case.text("5_三维与图纸.md", cadmd),
          figs=[("5_弹性体三维.png", "弹性体 BODY-TS 三维（定稿）", "Flexure BODY-TS (final)"), ("5_弹性体图纸.png", "弹性体图纸（主要尺寸）", "Flexure drawing (main dimensions)")],
          files=[("BODY-TS.step", "弹性体 STEP", "Flexure (STEP)")], tools=tools("cae") + L.lib_tools([SCR_RIM, SCR_HUB, PIN]),
          facts=[("腹板厚", "Web thickness", g2["TW"], "mm"), ("外圈摩擦能传", "Rim friction capacity", round(T_rim), "N·m"), ("内毂摩擦能传", "Hub friction capacity", round(T_hub), "N·m")])
case.check("cad", "外圈螺钉摩擦能传的力矩", "Rim bolt friction torque", round(T_rim), ">=", round(T.T_OVL * SLIP_SF), "N·m", "过载 × 1.2")
case.check("cad", "内毂螺钉摩擦能传的力矩", "Hub bolt friction torque", round(T_hub), ">=", round(T_run), "N·m", "重复峰值 × 1.2（零件库）")
case.check("cad", "过载时内毂锥销剪应力", "Hub taper-pin shear stress at overload", round(tau_pin), "<=", TAU_PIN, "MPa", "不淬火锥销许用值（示例取值）")

# ================================================================ 6 工艺：外协加工要求
tol_pct = dS_001 * 1      # ±0.01 mm → ±tol_pct %
procmd = f"""# 工艺：弹性体外协加工要求（BODY-TS 是外购件，传感器厂只做来料检验）

| 序 | 工序 | 要点 |
|---|---|---|
| 1 | 下料 | 17-4PH 棒料，固溶状态（Condition A） |
| 2 | 粗车、粗铣 | 留余量 0.5 mm |
| 3 | 时效 H1025 | 552 ℃ 保温 4 h 空冷（ASTM A564）；时效后屈服 ≥ 1000 MPa，尺寸会略缩，所以放在精加工前 |
| 4 | 精车 | 两端面平行度 0.01、内孔与外圆同轴度 Ø0.02（装上关节不别劲） |
| 5 | 精铣凹槽 | 两面对铣，**腹板 {g2['TW']:.2f} ± 0.01 mm**；槽底 Ra ≤ 0.4 μm；槽角 R0.5 |
| 6 | 钻孔、攻丝、铰销孔 | 销孔与减速器配铰 |
| 7 | 去应力 | 低温回火去加工应力（不去，粘片后会慢慢“走零点”） |
| 8 | 检验 | 腹板厚度逐件测（每件 4 个腹板）、硬度抽检、槽底粗糙度 |

**腹板公差怎么定**：有限元算出腹板每变 0.01 mm、输出变约 {dS_001:.1f} %。四个腹板一起偏——输出整体偏，标定能修；
四个腹板不一样厚——四根轮辐分到的力矩不均，相对轮辐串联抵消串扰的前提被破坏。所以要求逐件测四个腹板、相互差 ≤ 0.01 mm。

传感器厂来料检验（工序 1，5 分钟/件）核对外协的检验记录，抽测腹板厚度。
"""
case.step("process", f"外协 8 道工序；时效 H1025 在精加工前；腹板 {g2['TW']:.2f}±0.01（每 0.01 mm 影响输出约 {dS_001:.1f} %），四个腹板相互差 ≤ 0.01。",
          f"Eight outsourced operations; H1025 ageing before finishing; web {g2['TW']:.2f}±0.01 (≈{dS_001:.1f} % output per 0.01 mm), the four webs within 0.01 of each other.",
          md=case.text("6_外协加工要求.md", procmd), tools=tools("supply", "engineer"),
          facts=[("腹板公差", "Web tolerance", "±0.01", "mm"), ("每 0.01 mm 影响输出", "Output change per 0.01 mm", round(dS_001, 1), "%")])

# ================================================================ 7 制造：传感器厂做 20 台
sh = L.run_shop("WQ-TS", 20, "WO-CASE-SN-B", seed=1612)
rows_q, cpk_min, fails, st = L.shop_table(sh["measurements"])
makemd = f"""# 制造：传感器厂做 20 台

外协弹性体到货、来料检验后，传感器厂仿真车间按扭矩传感器线（粘片 → 固化 → 组桥 → 温度补偿 → 砝码标定 → 终检）做 20 台，
总时长约 {sh['hours']:.0f} 小时（胶固化、温度补偿在炉里整批走）。终检五项：

{L.md_table(["特性（%FS）", "公差", "台数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}** 项，最低 Cpk {cpk_min:.2f}。和弹性体直接相关的是**非线性、滞后**：材料（17-4PH 时效后弹性好、滞后小）、
结构（腹板处于纯剪、应力只有屈服的五分之一左右）、安装面不打滑（第 5 步的销子）。粘片和固化的影响见案例 C。
"""
case.step("make", f"20 台终检五项，不合格 {fails} 项，最低 Cpk {cpk_min:.2f}；非线性、滞后均值 {st['ts_nonlin']['mean']:.2f}、{st['ts_hyst']['mean']:.2f} %FS。",
          f"20 sensors, five final-test items: {fails} out of tolerance, lowest Cpk {cpk_min:.2f}; mean non-linearity {st['ts_nonlin']['mean']:.2f} and hysteresis {st['ts_hyst']['mean']:.2f} %FS.",
          md=case.text("7_制造与终检.md", makemd), tools=tools("planner", "operator", "quality"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), "")])
case.check("make", "终检不合格项", "Final-test failures", fails, "==", 0, "", "扭矩终检台")
case.check("make", "终检最低 Cpk", "Lowest final-test Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

（第一项“第一版输出 < {MV_MIN}”是记录第一版不行、需要改版，不是要求。）

1. **短而粗的零件，手算定方向，有限元定数**：工字截面剪应力公式高估了 {hc1['mv_v'] / mv1:.1f} 倍。
2. **一个零件里的矛盾**：输出要大（腹板薄）、刚度要高（侧壁厚）、过载要扛（应力低）——轮辐 + 剪切腹板把三者分给不同的部位。
3. **抵消靠对称**：径向力在单根轮辐上有 {xt_fx_single:.1f} %FS 的串扰，相对轮辐串联后 {xt_fx:.3f} %FS；对称要靠加工（四个腹板一样厚）和粘片（贴在正中）保证。
4. **小直径的结合面要算摩擦**：内毂 M5 不够，改 M6 加锥销。

## 留给学生的问题

1. 在“仿真与分析”里把腹板改成 0.8 mm，输出、刚度、过载安全系数怎么变？有没有上限？
2. 把四根轮辐改成三根：串联抵消还成立吗？
3. 倾覆力矩让正、反两面的腹板应变反号——只在正面贴片，为什么有限元算出的串扰仍然很小？

相关：传感器厂帮助“产品与物料”；实验（虚拟仪器）扭矩传感器标定；案例 A（信号调理）、案例 C（整机、补偿、标定）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过（含记录第一版不行的一项）；定稿 {mv2:.2f} mV/V、{k2:.3g} N·m/rad。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass (including the record that version 1 failed); final {mv2:.2f} mV/V, {k2:.3g} N·m/rad.",
          md=case.text("8_总结.md", review), tools=tools("inst"))
case.write()
print("ok", mv1, mv2, k2, sf_ovl, xt_fx, xt_mx, mesh_diff, dS_001, T_rim, hub_opts)
