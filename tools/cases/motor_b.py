"""第 161d 轮：电机厂案例 B——WQ-SM200 的电磁设计：磁钢厚度、匝数、二维静磁场有限元（气隙磁密、反电势、转矩常数），到终检台测 20 台。

    python3 tools/cases/motor_b.py

有限元：Gmsh 二维网格 + scikit-fem（tools/cases/motorlib.py，线性铁心）；制造用电机厂仿真车间的终检台。输出到 factory/cases/motor/B/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-motor.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import motorlib as ML  # noqa: E402
import sm200 as S  # noqa: E402

TOOLS = {
    "wave": ("电机终检波形", "Motor test waveforms", "/motor-wave"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731
G = dict(S.GEOM)
COILS = ML.tooth_winding(G["Q"], G["p"])
P = G["p"]

case = L.Case("motor", "B", "中等", "WQ-SM200 电磁设计与有限元", "WQ-SM200 electromagnetic design and FEA", "WQ-SM200",
              "12 槽 10 极伺服电机的电磁设计：磁钢厚度比较、按 48 V 母线定匝数，二维静磁场有限元算气隙磁密、反电势和转矩常数并与手算对照，再在终检台测 20 台。",
              "Electromagnetic design of the 12-slot 10-pole servo motor: magnet thickness, turns from the 48 V bus, 2D magnetostatic FEA for air-gap flux density, back-EMF and torque constant checked against hand calculation, then 20 motors tested.",
              "tools/cases/motor_b.py")


def flux_per_turn(g, steps=37):
    xy, tris, reg = ML.build_mesh(g, h_gap=0.12, h=1.0)
    angs = np.radians(np.linspace(0, 72, steps))
    lam = []
    for a in angs:
        A = ML.solve(xy, tris, reg, a, g, mu_r_iron=S.MU_IRON, Br=S.BR)
        sf, _, _, _ = ML.slot_side_flux(xy, tris, reg, A, g, S.L_STK)
        lam.append(ML.phase_flux(sf, COILS, 1))
    return xy, tris, reg, angs, lam


# ================================================================ 1 任务书
brief = f"""# 设计任务书：WQ-SM200 电磁设计

| 项目 | 要求 | 出处 |
|---|---|---|
| 额定 | {S.T_RATED} N·m、{S.N_RATED:.0f} r/min（200 W），最高 {S.N_MAX:.0f} r/min | 电机选型助手（伺服 200 W） |
| 母线 | {S.V_DC:g} V；最高转速时线反电势峰值不超过母线的 80 %（留调节余量） | 关节驱动板 DRV-JOINT-B |
| 外形 | 60 机座（方形法兰 60 mm） | 电机厂物料 LAM-60、HSG-60 |
| 槽极配合 | 12 槽 10 极集中绕组 | 案例 A |
| 磁钢 | 钕铁硼 N35 级，Br = {S.BR} T，表贴 10 块（MAG-60） | GB/T 13560 |
| 铁心 | 不饱和：齿、轭磁密 ≤ 1.6 T | 硅钢片常用设计值 |

**要定的**：磁钢多厚、每个线圈几匝；**要算的**：气隙磁密、反电势常数、转矩常数、额定电流。
"""
case.step("brief", f"{S.T_RATED} N·m、{S.N_RATED:.0f}/{S.N_MAX:.0f} r/min、{S.V_DC:g} V；60 机座；N35 磁钢。",
          f"{S.T_RATED} N·m, {S.N_RATED:.0f}/{S.N_MAX:.0f} rpm, {S.V_DC:g} V; frame 60; N35 magnets.",
          md=case.text("1_任务书.md", brief), tools=tools("engineer"),
          facts=[("额定转矩", "Rated torque", S.T_RATED, "N·m"), ("母线", "DC bus", S.V_DC, "V"), ("机座", "Frame", 60, "mm")])

# ================================================================ 2 方案：第一版 → 有限元发现问题 → 定稿
def quick(g, Lk):
    """一版设计的关键数：每匝磁链、按 48 V 定的匝数、额定电流、额定电流时齿部磁密（99 % 分位）、电流密度"""
    xy_, tr_, rg_ = ML.build_mesh(g, h_gap=0.15, h=1.0)
    an = np.radians(np.linspace(0, 72, 13))
    la_ = []
    for a in an:
        A_ = ML.solve(xy_, tr_, rg_, a, g, mu_r_iron=S.MU_IRON, Br=S.BR)
        sf_, _, _, _ = ML.slot_side_flux(xy_, tr_, rg_, A_, g, Lk)
        la_.append(ML.phase_flux(sf_, COILS, 1)["A"])
    la_ = np.array(la_)
    l1 = (la_.max() - la_.min()) / 2
    t0 = an[int(np.argmax(la_))]
    wm = S.N_MAX * 2 * math.pi / 60 * P
    nc = int(math.floor(0.8 * S.V_DC / (math.sqrt(3) * wm * l1)))
    I_ = S.T_RATED / (1.5 * P * l1 * nc)
    ia_ = {ph: I_ * math.cos(P * (0 - t0) + math.pi / 2 - k * 2 * math.pi / 3) for k, ph in enumerate("ABC")}
    A_ = ML.solve(xy_, tr_, rg_, 0.0, g, mu_r_iron=S.MU_IRON, Br=S.BR, J=ML.current_density(xy_, tr_, rg_, g, COILS, nc, ia_))
    Bt_ = float(np.percentile(ML.element_B(xy_, tr_, A_)[rg_ == "iron_s"], 99))
    Ah_ = float(np.mean([h[1] for k in ML.slot_halves(xy_, tr_, rg_, g) for h in k]))
    return dict(nc=nc, I=I_, B=Bt_, J=I_ / math.sqrt(2) / (S.FILL * Ah_ / nc) / 1e6)


v1, v2 = quick(dict(S.GEOM_V1), S.L_V1), quick(dict(G), S.L_STK)
vrows = [["第一版", f"Ø{2 * S.GEOM_V1['R_so']:g} × {S.L_V1 * 1000:.0f}", f"{S.GEOM_V1['bt']} / {S.GEOM_V1['h_yoke']}", v1["nc"], f"{v1['I'] / math.sqrt(2):.1f} A", f"**{v1['B']:.2f} T**", f"**{v1['J']:.1f}**"],
         ["定稿", f"Ø{2 * G['R_so']:g} × {S.L_STK * 1000:.0f}", f"{G['bt']} / {G['h_yoke']}", v2["nc"], f"{v2['I'] / math.sqrt(2):.1f} A", f"{v2['B']:.2f} T", f"{v2['J']:.1f}"]]
concept = f"""# 方案：第一版不行，改了一次

先按“60 机座、定子外径 50、叠厚 40”做第一版，用第 4 步同一套有限元算额定电流时的情况：

{L.md_table(["", "定子外径 × 叠厚 mm", "齿宽 / 轭厚 mm", "每线圈匝数", "额定相电流（有效值）", "齿部磁密（99 % 分位）", "电流密度 A/mm²"], vrows)}

第一版两处不行：**齿部磁密 {v1['B']:.2f} T，已经饱和**（硅钢片过了 1.6 T 磁导率掉得很快，线性模型也不再可信）；**电流密度 {v1['J']:.1f} A/mm²**，自然冷却的小电机吃不消。

为什么不能靠多绕几匝降电流？匝数被 48 V 母线卡死：最高转速时反电势不能超过母线——**转矩常数基本由母线电压和最高转速决定**，额定电流也就定了。
能做的只有：齿和轭加宽（降磁密）、定子外径加大（槽面积够用）、叠厚加长（每匝磁链大，匝数少一点）。

**定稿**：定子外径 56（60 机座四周还留 2 mm 壁）、齿宽 5.2、轭厚 4.2、叠厚 45。
"""
case.step("concept", f"第一版（Ø50 × 40）齿部 {v1['B']:.2f} T 饱和、电流密度 {v1['J']:.1f} A/mm²；匝数被 48 V 卡死，只能改铁心：定稿 Ø56 × 45，{v2['B']:.2f} T、{v2['J']:.1f} A/mm²。",
          f"First try (Ø50 × 40): teeth saturate at {v1['B']:.2f} T, {v1['J']:.1f} A/mm²; turns are fixed by the 48 V bus, so the core changes: final Ø56 × 45, {v2['B']:.2f} T, {v2['J']:.1f} A/mm².",
          md=case.text("2_方案.md", concept), tools=tools("engineer"),
          facts=[("第一版齿部磁密", "First-try tooth flux", v1["B"], "T"), ("定稿齿部磁密", "Final tooth flux", v2["B"], "T")])

# ================================================================ 4（先算）有限元：空载磁链 → 匝数、反电势；带电流 → 转矩
xy, tris, reg, angs, lam = flux_per_turn(G)
la = np.array([x["A"] for x in lam])
lb = np.array([x["B"] for x in lam])
lam1 = (la.max() - la.min()) / 2
th0 = float(angs[int(np.argmax(la))])
w_max = S.N_MAX * 2 * math.pi / 60 * P
NC = int(math.floor(0.8 * S.V_DC / (math.sqrt(3) * w_max * lam1)))
w_r = S.N_RATED * 2 * math.pi / 60
e_ph = np.gradient(la * NC, angs) * w_r                       # 3000 r/min 时的相反电势 V
e_line = (la - lb) * NC
eL = np.gradient(e_line, angs) * w_r
harm = np.abs(np.fft.rfft(eL[:-1]))
thd = math.sqrt(np.sum(harm[2:] ** 2)) / harm[1] * 100
Ke_line = (eL.max() - eL.min()) / 2 / (S.N_RATED / 1000)       # V（线，峰值）/ krpm
A0 = ML.solve(xy, tris, reg, 0.0, G, mu_r_iron=S.MU_IRON, Br=S.BR)
th, Br_, _ = ML.gap_field(xy, tris, reg, A0, (G["R_si"] - G["gap"] / 2) / 1000)
B1 = 2 * abs(np.mean(Br_ * np.exp(-1j * P * th)))
# 带电流：q 轴电流 I（峰值），在几个转子位置算转矩（阿尔基奥法）
Kt_hand = 1.5 * P * lam1 * NC                                    # N·m / A（峰值）
I_rated = S.T_RATED / Kt_hand
tq_pos, Bmax_iron = [], 0.0
pos = np.radians(np.linspace(0, 12, 7))                          # 一个齿距的 2/5（齿槽转矩每 6° 一个周期）
for a in pos:
    thE = P * (a - th0)
    ia = {ph: I_rated * math.cos(thE + math.pi / 2 - k * 2 * math.pi / 3) for k, ph in enumerate("ABC")}
    J = ML.current_density(xy, tris, reg, G, COILS, NC, ia)
    A = ML.solve(xy, tris, reg, a, G, mu_r_iron=S.MU_IRON, Br=S.BR, J=J)
    tq_pos.append(ML.arkkio_torque(xy, tris, reg, A, G, S.L_STK))
    Bmax_iron = max(Bmax_iron, float(np.percentile(ML.element_B(xy, tris, A)[np.isin(reg, ["iron_s"])], 99)))
tq_pos = np.array(tq_pos)
T_fe = float(tq_pos.mean())
ripple = (tq_pos.max() - tq_pos.min()) / T_fe * 100
# 铜：每半槽面积 → 线径、电流密度、相电阻
halves = ML.slot_halves(xy, tris, reg, G)
A_half = float(np.mean([h[1] for k in halves for h in k]))         # m²
a_wire = S.FILL * A_half / NC
d_wire = math.sqrt(4 * a_wire / math.pi)
I_rms = I_rated / math.sqrt(2)
Jcu = I_rms / a_wire / 1e6
l_turn = 2 * S.L_STK + 2 * (G["bt"] / 1000 + 2 * math.sqrt(A_half) * 0.6)    # 平均匝长：两条边 + 两个端部（绕齿，近似）
R_ph = S.RHO_CU * l_turn * NC * 4 / a_wire
P_cu = 3 * I_rms ** 2 * R_ph
B_iron_ok = Bmax_iron <= 1.6

# ================================================================ 3 计算书
carter_g = G["gap"] + G["t_m"] / 1.05
B_hand = S.BR * G["t_m"] / 1.05 / carter_g
calcmd = f"""# 计算书：WQ-SM200 电磁设计

## 气隙磁密（磁路法）

磁钢厚 h_m = {G['t_m']} mm、气隙 g = {G['gap']} mm、回复磁导率 μ_r ≈ 1.05：B_g ≈ B_r·(h_m/μ_r)/(g + h_m/μ_r) = **{B_hand:.3f} T**（磁钢下的平顶值）；
有限元（第 4 步）气隙磁密基波幅值 {B1:.3f} T（平顶波的基波约为平顶值 × 4/π × sin(极弧 π/2) 量级）。

## 匝数：由母线电压定

有限元得每相每匝磁链幅值 λ₁ = {lam1 * 1e3:.4f} mWb（4 个线圈串联、叠厚 {S.L_STK * 1000:.0f} mm）。
{S.N_MAX:.0f} r/min 时电角速度 ω_e = {w_max:.0f} rad/s，每匝线反电势峰值 √3·ω_e·λ₁ = {math.sqrt(3) * w_max * lam1:.2f} V。
线反电势峰值 ≤ 0.8 × {S.V_DC:g} V ⇒ 每个线圈匝数 N_c ≤ {0.8 * S.V_DC / (math.sqrt(3) * w_max * lam1):.2f}，**取 N_c = {NC}**。

## 转矩常数、额定电流

K_t = 1.5·p·λ₁·N_c = 1.5 × {P} × {lam1 * 1e3:.4f}e-3 × {NC} = **{Kt_hand:.4f} N·m/A**（相电流峰值）；
额定 {S.T_RATED} N·m 要相电流峰值 I = {I_rated:.2f} A（有效值 {I_rms:.2f} A）。

## 绕组铜

每半槽面积 {A_half * 1e6:.1f} mm²，槽满率 {S.FILL}：每匝导线截面 {a_wire * 1e6:.3f} mm²（线径约 Ø{d_wire * 1000:.2f}，可用多股并绕）；
额定电流密度 **{Jcu:.1f} A/mm²**；平均匝长约 {l_turn * 1000:.0f} mm，相电阻（100 ℃）{R_ph * 1000:.1f} mΩ，额定铜耗 **{P_cu:.1f} W**（案例 C 的热计算用）。
"""
case.step("calc", f"磁路法气隙磁密 {B_hand:.2f} T；按 48 V 定每线圈 {NC} 匝；K_t = {Kt_hand:.4f} N·m/A，额定相电流 {I_rms:.1f} A 有效值；电流密度 {Jcu:.1f} A/mm²、铜耗 {P_cu:.1f} W。",
          f"Magnetic-circuit air-gap flux density {B_hand:.2f} T; {NC} turns per coil from the 48 V bus; K_t = {Kt_hand:.4f} N·m/A, rated phase current {I_rms:.1f} A rms; {Jcu:.1f} A/mm², copper loss {P_cu:.1f} W.",
          md=case.text("3_计算书.md", calcmd), tools=tools("engineer"),
          facts=[("每线圈匝数", "Turns per coil", NC, ""), ("转矩常数", "Torque constant", Kt_hand, "N·m/A"), ("电流密度", "Current density", Jcu, "A/mm²"), ("铜耗", "Copper loss", P_cu, "W")])
case.check("calc", "最高转速线反电势峰值 / 母线", "Peak line back-EMF at max speed / bus", math.sqrt(3) * w_max * lam1 * NC / S.V_DC, "<=", 0.8, "", "任务书")
case.check("calc", "额定电流密度", "Rated current density", Jcu, "<=", 8.0, "A/mm²", "自然冷却小电机常用上限")

# ================================================================ 4 仿真（图）
fig, axs = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axs[0]
Bel = ML.element_B(xy, tris, A0)
tp = ax.tripcolor(xy[:, 0] * 1000, xy[:, 1] * 1000, tris, facecolors=np.clip(Bel, 0, 2.0), cmap="viridis", shading="flat")
ax.tricontour(xy[:, 0] * 1000, xy[:, 1] * 1000, tris, A0, levels=24, colors="w", linewidths=0.4)
ax.set_aspect("equal")
ax.set_axis_off()
ax.set_title("空载磁场：|B| / T（白线：磁力线）", fontsize=9.5)
fig.colorbar(tp, ax=ax, shrink=0.75)
axs[1].plot(np.degrees(angs), eL, color=L.ACCENT, lw=1.4, label="线反电势 u_AB（有限元）")
axs[1].plot(np.degrees(angs), e_ph, color="#8aa4bd", lw=1, label="相反电势 e_A")
axs[1].set_xlabel("转子机械角 / °（一个电周期 72°）")
axs[1].set_ylabel(f"V（{S.N_RATED:.0f} r/min）")
axs[1].legend(fontsize=8.5, frameon=False)
case.fig(fig, "4_磁场与反电势.png")
fig, ax = plt.subplots(figsize=(8, 2.6))
ax.plot(np.degrees(th), Br_, color=L.ACCENT, lw=1)
ax.set_xlabel("圆周角 / °")
ax.set_ylabel("气隙径向磁密 / T")
ax.set_xlim(0, 144)
case.fig(fig, "4_气隙磁密.png")
simmd = f"""# 仿真：二维静磁场有限元

**模型**：定子（12 齿、齿靴、轭）、气隙、10 块表贴磁钢、转子铁心，Gmsh 二维三角形网格 {len(tris):,} 个（气隙里加密到 0.12 mm），scikit-fem 解矢量磁位 A。
铁心按线性材料（μ_r = {S.MU_IRON:g}），磁钢 μ_r ≈ 1、B_r = {S.BR} T。转子转动 = 磁钢的磁化跟着转，一个电周期算 {len(angs)} 个位置。

| 量 | 有限元 | 手算 | 相差 |
|---|---|---|---|
| 气隙磁密（磁钢下平顶 / 基波） | 基波 {B1:.3f} T | 平顶 {B_hand:.3f} T | 波形不同，量级一致 |
| 转矩（额定电流 {I_rated:.2f} A，q 轴） | {T_fe:.4f} N·m | {S.T_RATED} N·m（K_t × I） | {(T_fe / S.T_RATED - 1) * 100:+.1f} % |
| 转矩脉动（一个齿距内 7 个位置） | {ripple:.1f} % | — | — |
| 线反电势谐波畸变 THD | {thd:.2f} % | — | 终检公差 ≤ 5 % |
| 线反电势常数 | {Ke_line:.2f} V/krpm（峰值） | — | — |
| 额定电流时定子铁心磁密（99 % 分位） | {Bmax_iron:.2f} T | — | ≤ 1.6 T，线性假设{'成立' if B_iron_ok else '不成立，要做非线性'} |

有限元的转矩与“K_t × I”相差 {abs(T_fe / S.T_RATED - 1) * 100:.1f} %：K_t 由空载磁链算出，有限元里还有电流本身的磁场和齿槽效应。
**齿槽转矩**比额定转矩小两个数量级，这套线性、固定网格的二维模型分辨不出来（磁钢边缘在网格里跳格造成的数值噪声和它同一个量级）；
齿槽转矩以终检台实测为准（案例 A 第 4 步、电机厂“电机终检波形”页）。
"""
case.step("sim", f"有限元：额定电流转矩 {T_fe:.3f} N·m（与手算差 {(T_fe / S.T_RATED - 1) * 100:+.1f} %）、线反电势 THD {thd:.2f} %、铁心磁密 {Bmax_iron:.2f} T。",
          f"FEA: torque at rated current {T_fe:.3f} N·m ({(T_fe / S.T_RATED - 1) * 100:+.1f} % vs hand), line back-EMF THD {thd:.2f} %, iron flux density {Bmax_iron:.2f} T.",
          md=case.text("4_有限元.md", simmd),
          figs=[("4_磁场与反电势.png", "空载磁场与反电势（有限元）", "No-load field and back-EMF (FEA)"), ("4_气隙磁密.png", "气隙径向磁密（两个极距）", "Air-gap radial flux density (two pole pitches)")],
          tools=tools("wave"), facts=[("转矩（有限元）", "Torque (FEA)", T_fe, "N·m"), ("THD", "THD", thd, "%"), ("铁心磁密", "Iron flux density", Bmax_iron, "T")])
case.check("sim", "有限元转矩与手算相差", "FEA torque vs hand calculation", abs(T_fe / S.T_RATED - 1) * 100, "<=", 5.0, "%", "核对有限元")
case.check("sim", "线反电势 THD（有限元）", "Line back-EMF THD (FEA)", thd, "<=", 5.0, "%", "终检公差")
case.check("sim", "额定电流时定子铁心磁密", "Stator iron flux density at rated current", Bmax_iron, "<=", 1.6, "T", "线性铁心的前提")

# ================================================================ 5 冲片图与三维
import build123d as bd  # noqa: E402

polys = G["_polys"]
lam_face = bd.Face(bd.Wire.make_circle(G["R_so"])) - bd.Face(bd.Wire.make_circle(G["R_si"]))
for pl in polys:
    lam_face = lam_face - bd.Face(bd.Wire.make_polygon([bd.Vector(float(x), float(y), 0) for x, y in pl], close=True))
stack = bd.extrude(lam_face, amount=S.L_STK * 1000)
bd.export_step(stack, str(case.path("LAM-60-定子铁心.step")))
L.render_solid(stack, case.path("5_定子铁心.png"), elev=35, azim=-60, size=(5.5, 5), swap=False)
fig, ax = plt.subplots(figsize=(5.6, 5.6))
for nm, colr in (("iron_s", "#9aa5b1"), ("slot", "#d9a441"), ("mag", "#c0392b"), ("iron_r", "#7f9cb8")):
    sel = reg == nm
    ax.tripcolor(xy[:, 0] * 1000, xy[:, 1] * 1000, tris[sel], facecolors=np.ones(sel.sum()), cmap=plt.matplotlib.colors.ListedColormap([colr]), shading="flat")
ax.set_aspect("equal")
ax.set_title("截面：定子（灰）、绕组（黄）、磁钢（红）、转子（蓝）", fontsize=9.5)
ax.set_xlabel("mm")
case.fig(fig, "5_截面.png")
cadmd = f"""# 冲片与截面

{L.md_table(["尺寸", "值 mm"], [["定子外径 / 内径", f"{2 * G['R_so']:g} / {2 * G['R_si']:g}"], ["齿宽 / 轭厚", f"{G['bt']} / {G['h_yoke']}"],
    ["槽口宽 / 齿靴高", f"{G['b0']} / {G['h0']}"], ["气隙", f"{G['gap']}"], ["磁钢厚 / 极弧系数", f"{G['t_m']} / {G['arc']}"], ["叠厚", f"{S.L_STK * 1000:.0f}"]])}

定子铁心 STEP 由有限元同一组槽形多边形生成（冲片 LAM-60 的外形图以它为准）。
"""
case.step("cad", f"冲片 Ø{2 * G['R_so']:g}/Ø{2 * G['R_si']:g}、12 槽，叠厚 {S.L_STK * 1000:.0f}；STEP 与有限元同一套槽形。",
          f"Lamination Ø{2 * G['R_so']:g}/Ø{2 * G['R_si']:g}, 12 slots, {S.L_STK * 1000:.0f} mm stack; STEP from the same slot shapes as the FEA.",
          md=case.text("5_冲片.md", cadmd), figs=[("5_截面.png", "电机截面（有限元网格的区域）", "Motor cross-section (FEA regions)"), ("5_定子铁心.png", "定子铁心三维", "Stator core 3D")],
          files=[("LAM-60-定子铁心.step", "定子铁心 STEP", "Stator core (STEP)")], tools=tools("engineer"), facts=[("叠厚", "Stack", S.L_STK * 1000, "mm")])

# ================================================================ 6 工艺（转子：磁钢粘贴、充磁、动平衡）
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WQ-SM200"][0]]
procmd = f"""# 工艺：转子与充磁

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt) if any(x in op for x in ("磁钢", "充磁", "动平衡", "叠压"))])}

- 磁钢先粘贴后充磁（未充磁的磁钢不互相吸，好装）；充磁电压不够，反电势常数就偏低（实验 35 的“充磁电压”问题）。
- 磁钢定位工装决定 10 块磁钢的角度位置——位置误差直接变成齿槽转矩（案例 A 第 4 步）。
"""
case.step("process", "叠压、磁钢粘贴、充磁、动平衡；充磁电压决定反电势常数，定位工装决定齿槽转矩。",
          "Stacking, magnet bonding, magnetising, balancing; magnetising voltage sets K_e, the fixture sets cogging.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("相关工序", "Operations", 4, "")])

# ================================================================ 7 制造：终检
sh = L.run_shop("WQ-SM200", 20, "WO-CASE-MT-B", seed=262)
final = [m for m in sh["measurements"] if any(k in m["name"] for k in ("反电势", "齿槽", "空载电流"))]
rows_q, cpk_min, fails, st = L.shop_table(final)
makemd = f"""# 终检台测 20 台

{L.md_table(["特性", "公差", "件数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}** 个，最低 Cpk {cpk_min:.2f}。终检的反电势常数是“相对额定 %”——额定就是第 3 步按 {NC} 匝算出的值；反电势 THD 实测（约 2 %）和有限元（{thd:.1f} %）同一量级。
"""
case.step("make", f"20 台终检，不合格 {fails} 个，最低 Cpk {cpk_min:.2f}。", f"20 motors final-tested, {fails} out of tolerance, lowest Cpk {cpk_min:.2f}.",
          md=case.text("7_终检.md", makemd), tools=tools("planner", "operator", "wave", "quality"), facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", cpk_min, "")])
case.check("make", "终检不合格数", "Final-test failures", fails, "==", 0, "", "终检台")
case.check("make", "终检最低 Cpk", "Lowest final-test Cpk", cpk_min, ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. 磁钢 2.5 mm；每线圈 {NC} 匝（由 48 V 母线和最高转速定）；K_t = {Kt_hand:.4f} N·m/A，额定相电流 {I_rms:.1f} A 有效值。
2. 有限元与手算对得上（转矩差 {abs(T_fe / S.T_RATED - 1) * 100:.1f} %），铁心不饱和，线性假设成立。
3. 齿槽转矩太小，这套模型算不准，以终检实测为准——知道模型能算什么、不能算什么，和算出数一样重要。

## 留给学生的问题

1. 母线改成 24 V，匝数、额定电流、铜耗各怎么变？驱动板要换吗？
2. 叠厚从 40 加到 50 mm，转矩常数变多少？机座长度呢？
3. 把铁心的 μ_r 从 2000 改成 500（相当于饱和了一些），转矩常数降多少？

相关：案例 A（绕组）、案例 C（整机热与结构）；电机厂帮助；实验 35、42。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；2.5 mm 磁钢、{NC} 匝、K_t {Kt_hand:.4f}。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; 2.5 mm magnets, {NC} turns, K_t {Kt_hand:.4f}.", md=case.text("8_总结.md", review), tools=tools("wave"))
case.write()
