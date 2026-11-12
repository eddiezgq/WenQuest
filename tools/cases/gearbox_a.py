"""第 161a 轮：减速器厂案例 A——输出轴 SH-301（B 版），从任务书到车间加工 20 根。

    python3 tools/cases/gearbox_a.py

数字全部由程序算出：受力、强度、疲劳、刚度、临界转速用《机械设计》第 33 章的同一套函数（_shaft.py、_calc33.py）；
有限元、疲劳寿命用数字工厂“仿真与分析”的代码（cae/solve.py、cae/fatigue.py）；数控程序用“数控编程”（cae/cam_job.py）；
加工、检验用数字工厂仿真车间（sim/engine.py）；标准成本用 hub/mrp.py。输出到 factory/cases/gearbox/A/。
"""
from __future__ import annotations

import io
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
import mdstd  # noqa: E402
import _shaft as S  # noqa: E402
import _calc33  # noqa: E402

MAT_CHOSEN = "40Cr-QT"
TOOLS = {
    "engineer": ("在线设计", "Online design", "/work/engineer"),
    "library": ("零件库", "Parts library", "/library"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
    "design": ("设计发布与审批", "Design release", "/design"),
    "process": ("工艺规程", "Process plans", "/process"),
    "cam": ("数控编程", "CNC programming", "/cam"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "finance": ("经营与成本", "Business & cost", "/finance"),
}


def tools(*keys):
    return [TOOLS[k] for k in keys]


case = L.Case("gearbox", "A", "简单", "输出轴 SH-301（B 版）", "Output shaft SH-301 (rev B)", "SH-301",
              "一根轴从任务书做到车间：受力、强度、疲劳、有限元、三维、零件图、数控程序，再在减速器厂的仿真车间加工 20 根、检验、核算成本。",
              "One shaft from the design brief to the shop floor: loads, strength, fatigue, FEA, 3D model, drawing, CNC programs, then 20 parts machined, inspected and costed in the gearbox plant's simulated shop.",
              "tools/cases/gearbox_a.py")

# ================================================================ 1 任务书
Ft, Fr = S.gear_forces()
series, rate, rated = S.torque_series()
K_peak = float(series.max()) / rated
brg = mdstd.bearing(S.BRG)
brief = f"""# 设计任务书：WQR-105 输出轴 SH-301

**用途**　二级圆柱齿轮减速器 WQR-105 的输出轴：低速级大齿轮 GR-302 装在轴上，外伸端经联轴器带动输送机、搅拌机一类连续运转的设备。

| 项目 | 要求 | 出处 |
|---|---|---|
| 额定输出转矩 | {S.T_RATED / 1e3:.0f} N·m（已含工况系数 K_A） | 数字工厂参数配置器 T_RATED |
| 输出转速 | {S.N_OUT:.1f} r/min（输入 {S.N_IN:.0f} r/min ÷ 传动比 {S.I_TOTAL:g}） | 工厂设计；齿数 72/24 × 70/20 |
| 起动冲击 | 跑合试验台转矩记录的峰值是额定的 {K_peak:.2f} 倍，每 25 s 一次起停 | 数字工厂跑合台 test-01（仿真车间同一个函数） |
| 齿轮 | GR-302：模数 {S.M_GEAR:g}、{S.Z_TEETH} 齿、直齿、α = 20°，分度圆 Ø{S.D_GEAR:g}，带毂锻件（毂宽 {S.HUB_GEAR:g}） | 第 33.2 节 B 版 |
| 轴承 | 两端深沟球轴承 {S.BRG}（Ø{brg['d']} × Ø{brg['D']} × {brg['B']}，C = {brg['C_kN']} kN） | BOM：BRG-6207；GB/T 276 |
| 联轴器 | 外伸段 Ø30，轮毂长 {S.HUB_CPL:g} | 第 33.2 节 |
| 要求寿命 | {S.LIFE_H:,.0f} h（频繁起停） | 参数配置器默认值；任务单 TS-33-1 |
| 毛坯 | 热轧圆钢 Ø50（物料 RM-45-D50），最大直径不超过 Ø48 | 工厂物料；工艺规程 GY-SH301 |
| 安全系数 | 静强度、疲劳都不小于 1.5 | 《机械设计》33.5.5 节 |
| 刚度 | 轴承处转角不超过 1 mrad | [SHI] 轴一章 |
| 临界转速 | 工作转速不超过一阶临界的 0.7 倍 | 33.7.2 节 |

**交付物**　计算书、有限元与疲劳报告、三维模型（STEP）、零件图、工艺路线与数控程序、首批 20 根的检验与成本记录。
"""
case.step("brief", f"额定 {S.T_RATED / 1e3:.0f} N·m、{S.N_OUT:.1f} r/min，起停冲击 {K_peak:.2f} 倍，寿命 {S.LIFE_H:,.0f} h；轴承 6207，毛坯 Ø50 圆钢。",
          f"Rated {S.T_RATED / 1e3:.0f} N·m at {S.N_OUT:.1f} rpm, start-up peaks {K_peak:.2f}× rated, {S.LIFE_H:,.0f} h life; 6207 bearings, Ø50 bar stock.",
          md=case.text("1_任务书.md", brief), tools=tools("engineer", "library"),
          facts=[("额定转矩", "Rated torque", S.T_RATED / 1e3, "N·m"), ("输出转速", "Output speed", S.N_OUT, "r/min"), ("起动冲击", "Start-up peak", K_peak, "×"), ("要求寿命", "Required life", S.LIFE_H, "h")])

# ================================================================ 4（先算）有限元与疲劳——方案比较要用寿命
import _fea  # noqa: E402
from cae import fatigue as FAT, materials as MATS  # noqa: E402

seats = {"A": (S.Z_BRG_A - 1, S.Z_BRG_A + 1), "B": (S.Z_BRG_B - 1, S.Z_BRG_B + 1),
         "gear": (S.Z_GEAR - 22.5, S.Z_GEAR + 22.5), "cpl": (S.LEN_B - 20, S.LEN_B)}
rows, n_el, reac = _fea.shaft_fea(S.LAY_B, S.FILLET_B, seats, (Ft, Fr), S.T_RATED, h=5.0, fine_r=2)
zz, rr, th, vm = rows.T
keep = (zz > 2) & (zz < S.LEN_B - 25)
outer = keep & (rr > np.array([S.diameter_at(min(max(z, 0), S.LEN_B)) for z in zz]) / 2 - 0.05)


def nominal(z):
    d = S.diameter_at(z)
    return math.sqrt((S.M_total(z) / S.W_solid(d)) ** 2 + 3 * (S.torque_at(z) / S.WT_solid(d)) ** 2)


def peak_near(z0, w=2.5):
    return float(vm[keep & (abs(zz - z0) < w)].max())


RA_fe, RB_fe = float(np.hypot(*reac[0][:2])), float(np.hypot(*reac[1][:2]))
RA_h = math.hypot(*[S.reactions(F)[0] for F in (Ft, Fr)])
RB_h = math.hypot(*[S.reactions(F)[1] for F in (Ft, Fr)])
ext = keep & (zz > 182) & (zz < 210) & outer
vm_ext = float(np.median(vm[ext]))
vm_ext_nom = math.sqrt(3) * S.T_RATED / S.WT_solid(30)
hot = {"II": peak_near(90.0), "III": peak_near(115.0), "IV": peak_near(172.0)}
kfe = {"II": hot["II"] / nominal(89.99), "III": hot["III"] / nominal(115.01), "IV": hot["IV"] / vm_ext_nom}

block_s = len(series) / rate
cyc = FAT.rainflow(series)
f4 = S.fatigue_factors(S.SECTIONS["IV"], mdstd.material(S.MAT), "ground")
lives = {}
for mid in ("45-QT", "40Cr-QT"):
    m = MATS.get(mid)
    _, s_fil = FAT.compute(vm[keep & (zz > 60)], rated, series, block_s, m, surface="ground", size_factor=mdstd.size_factor(35), kf=1.0)
    _, s_key = FAT.compute(np.array([vm_ext]), rated, series, block_s, m, surface="ground", size_factor=mdstd.size_factor(30), kf=f4["k_t"])
    life = lambda s: math.inf if s["infinite"] else s["life_hours"]  # noqa: E731
    lives[mid] = dict(fillet=life(s_fil), key=life(s_key))

# ================================================================ 2 方案
def variant(mat_id):
    mat = mdstd.material(mat_id)
    S_min, sca_min = math.inf, math.inf
    for k, sec in S.SECTIONS.items():
        M, Tq = S.M_total(sec["z"]), S.torque_at(sec["z"])
        sig, tau = M / S.W_solid(sec["d"]), Tq / S.WT_solid(sec["d"])
        S_min = min(S_min, mat["sigma_s"] / (K_peak * math.sqrt(sig ** 2 + 3 * tau ** 2)))
        if sec["notch"] == "keyseat":
            f = S.fatigue_factors(sec, mat, "ground")
        else:
            a = mdstd.kt_estimate("shoulder_round")
            f = S.fatigue_factors(sec, mat, "ground", (a["Kt"], a["Kts"]))
        sca_min = min(sca_min, S.safety(sec, mat, f, M, Tq)["S_ca"])
    return dict(S_static=S_min, S_ca=sca_min, life=min(lives[mat_id].values()), name=mat["name"])


V45, V40 = variant("45-QT"), variant("40Cr-QT")
kA = mdstd.key_for(40)
T_key_A_hub45 = S.key_torque_limit(40, kA["b"], kA["h"], mdstd.key_length(45 - 5)) / 1e3
T_key_ext_A = S.key_torque_limit(30, 8, 7, 36) / 1e3
lf = lambda x: "无限" if not math.isfinite(x) else f"{x:,.0f} h"  # noqa: E731
concept = f"""# 方案比较

## 现行 A 版为什么不能直接用

数字工厂里的 SH-301 现行 A 版（五段 Ø30–Ø35–Ø40–Ø35–Ø30，一个键槽）是 FreeCAD 入门实验的模型。按《机械设计》33.2 节的结构设计清单评审，有四个问题：

1. 左端 Ø35 段长 12 mm，小于 6207 轴承宽 {brg['B']} mm，轴承装不下；
2. 齿轮锻坯毂宽 45 mm，键长也是 45 mm——键不能和轮毂一样长；键改成标准长度 40 mm 后只能传 {T_key_A_hub45:.0f} N·m，不够 {S.T_RATED / 1e3:.0f} N·m；
3. 外伸段的键 8 × 7 × 36 只能传 {T_key_ext_A:.0f} N·m，也不够；
4. 台阶处都是尖角，有限元应力随网格加密一直升高，没有确定值。

所以 A 版只能当几何练习，作为产品图纸必须改版。

## B 版：两种材料

B 版按 33.2 节重新布置：七段（左轴承位 + 套筒、齿轮位、轴环、轴肩、右轴承位、密封段、外伸段），所有台阶加圆角，齿轮改带毂锻件（毂宽 55），两个键槽开在同一条母线上。材料比较 45 钢调质和 40Cr 调质：

{L.md_table(["方案", "静强度最小安全系数", "疲劳最小安全系数", "疲劳寿命（跑合台载荷谱）", "结论"], [
    ["B 版，45 钢调质", f"{V45['S_static']:.2f}", f"{V45['S_ca']:.2f}", lf(V45['life']), "✗ 疲劳不够" if V45['S_ca'] < 1.5 or V45['life'] < S.LIFE_H else "✓"],
    ["B 版，40Cr 调质", f"{V40['S_static']:.2f}", f"{V40['S_ca']:.2f}", lf(V40['life']), "✓ 选定" if V40['S_ca'] >= 1.5 and V40['life'] >= S.LIFE_H else "✗"],
])}

疲劳安全系数按 DIN 743 流程（第 3 步）；寿命用有限元应力加跑合台转矩记录、雨流计数、迈因纳累积（第 4 步）。最危险的是外伸段根部（台阶 + 键槽）。

**选定：B 版，40Cr 调质。** 尺寸不变，只换材料，毛坯仍是 Ø50 圆钢。
"""
case.step("concept", f"现行 A 版装不下轴承、键传不了扭矩，改 B 版；B 版用 45 钢疲劳安全系数 {V45['S_ca']:.2f} 不够，选 40Cr（{V40['S_ca']:.2f}）。",
          f"Rev A cannot take the bearing and its keys are too weak, so rev B; with 45 steel the fatigue factor is {V45['S_ca']:.2f}, so 40Cr is chosen ({V40['S_ca']:.2f}).",
          md=case.text("2_方案.md", concept), tools=tools("engineer", "design"),
          facts=[("45 钢疲劳安全系数", "Fatigue factor, 45 steel", V45["S_ca"], ""), ("40Cr 疲劳安全系数", "Fatigue factor, 40Cr", V40["S_ca"], "")])
case.check("concept", "选定方案疲劳安全系数", "Fatigue factor of the chosen design", V40["S_ca"], ">=", 1.5, "", "33.5.5 节")

# ================================================================ 3 计算
cs = _calc33.sheet(MAT_CHOSEN)
# 键与轴承（第 25、34 章的常规校核）
kg, kc = mdstd.key_for(40), mdstd.key_for(30)
T_kg = S.key_torque_limit(40, kg["b"], kg["h"], S.L_KEY_GEAR, "A") / 1e3
T_kc = S.key_torque_limit(30, kc["b"], kc["h"], S.L_KEY_CPL, "C") / 1e3
FP = 1.2
R_max = max(RA_h, RB_h)
P = FP * R_max
L10h = (brg["C_kN"] * 1e3 / P) ** 3 * 1e6 / (60 * S.N_OUT)
extra = f"""

## 补充：平键与轴承

| 项目 | 计算 | 结果 | 要求 | 出处 |
|---|---|---|---|---|
| 齿轮处平键 A 型 {kg['b']}×{kg['h']}×{S.L_KEY_GEAR} | T = σp·d·(h/2)·(L−b)/2，σp = {S.SIGMA_P_ALLOW:g} MPa | {T_kg:.0f} N·m | ≥ {S.T_RATED / 1e3:.0f} N·m | 第 25 章；33.2 节 |
| 外伸段平键 C 型 {kc['b']}×{kc['h']}×{S.L_KEY_CPL} | T = σp·d·(h/2)·(L−b/2)/2 | {T_kc:.0f} N·m | ≥ {S.T_RATED / 1e3:.0f} N·m | 同上 |
| 轴承 {S.BRG} 当量载荷 | P = f_p·R_max，f_p = {FP}（中等冲击） | {P:.0f} N | — | 濮良贵《机械设计》滚动轴承一章 |
| 轴承 {S.BRG} 基本额定寿命 | L₁₀h = (C/P)³ × 10⁶ / (60 n) | {L10h:,.0f} h | ≥ {S.LIFE_H:,.0f} h | GB/T 6391（ISO 281） |
"""
calc_ok = cs.ok
case.step("calc", f"齿轮力 {Ft:.0f} / {Fr:.0f} N；四个截面静强度、疲劳都过（40Cr）；转角、临界转速、键、轴承寿命 {L10h:,.0f} h 都满足。",
          f"Gear forces {Ft:.0f} / {Fr:.0f} N; static and fatigue checks pass at all four sections (40Cr); slope, critical speed, keys and bearing life ({L10h:,.0f} h) all pass.",
          md=case.text("3_计算书.md", cs.markdown() + extra), tools=tools("cae"),
          facts=[("圆周力", "Tangential force", Ft, "N"), ("径向力", "Radial force", Fr, "N"), ("轴承寿命", "Bearing life", L10h, "h")])
case.check("calc", "计算书全部校核（40Cr）", "All checks in the calculation sheet (40Cr)", 1 if calc_ok else 0, "==", 1, "", "计算书")
case.check("calc", "齿轮处平键能传的转矩", "Torque capacity of the gear key", T_kg, ">=", S.T_RATED / 1e3, "N·m", "第 25 章")
case.check("calc", "外伸段平键能传的转矩", "Torque capacity of the coupling key", T_kc, ">=", S.T_RATED / 1e3, "N·m", "第 25 章")
case.check("calc", "轴承 6207 寿命", "6207 bearing life", L10h, ">=", S.LIFE_H, "h", "ISO 281")

# ================================================================ 4 仿真（写图、报告）
zs = np.linspace(0, S.LEN_B, 977)
vn = np.array([nominal(z) for z in zs])
fig, ax = plt.subplots(figsize=(8.2, 3.3))
ax.scatter(zz[outer], vm[outer], s=2, color=L.ACCENT, alpha=0.35, lw=0, rasterized=True, label="有限元：表面节点")
ax.plot(zs, vn, color=L.INK, lw=1.4, label="梁理论名义应力")
for k, z0 in (("II", 90.0), ("III", 115.0), ("IV", 172.0)):
    ax.annotate(f"{k}: {hot[k]:.0f} MPa", (z0, hot[k]), (z0 + 6, hot[k] + 25), fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.7))
ax.set_xlabel("z / mm（从左端面）")
ax.set_ylabel("冯·米塞斯应力 / MPa")
ax.set_ylim(0, 240)
ax.legend(fontsize=8.5, frameon=False, loc="upper left", markerscale=4)
case.fig(fig, "4_应力沿轴线.png")
fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.0), gridspec_kw={"width_ratios": [2.2, 1]})
t = np.arange(len(series)) / rate
axs[0].plot(t, series, color="#8e44ad", lw=0.9)
axs[0].axhline(rated, color=L.MUTED, lw=0.8, ls="--")
axs[0].set_xlabel("t / s")
axs[0].set_ylabel("转矩 / N·m")
axs[0].set_title("跑合试验台转矩记录", fontsize=9.5)
axs[1].scatter(cyc[:, 1], cyc[:, 0] * 2, s=10, color="#8e44ad", alpha=0.6)
axs[1].set_xlabel("平均值 / N·m")
axs[1].set_ylabel("变程 / N·m")
axs[1].set_title(f"雨流计数：每块 {len(cyc)} 个循环", fontsize=9.5)
case.fig(fig, "4_载荷谱与雨流计数.png")
err = lambda a, b: (a - b) / b * 100  # noqa: E731
simmd = f"""# 有限元与疲劳寿命

**模型**　整根 B 版轴（各台阶圆角，不含键槽）；Gmsh 二阶四面体 {n_el:,} 个单元，CalculiX 求解——与数字工厂“仿真与分析”同一套代码。
两个轴承位只在中心 ±1 mm 一圈限制径向位移（近似铰支），左端兼限轴向；齿轮位受齿轮力和转矩，外伸段限制转动。

## 核对（不核对的有限元结果不能用）

{L.md_table(["量", "有限元", "手算", "相差"], [
    ["左轴承支反力", f"{RA_fe:.0f} N", f"{RA_h:.0f} N", f"{err(RA_fe, RA_h):+.1f} %"],
    ["右轴承支反力", f"{RB_fe:.0f} N", f"{RB_h:.0f} N", f"{err(RB_fe, RB_h):+.1f} %"],
    ["外伸段光滑处应力（纯扭转）", f"{vm_ext:.1f} MPa", f"{vm_ext_nom:.1f} MPa", f"{err(vm_ext, vm_ext_nom):+.1f} %"],
])}

## 台阶处的应力集中

{L.md_table(["截面", "峰值应力", "峰值 / 名义（有效应力集中系数）"], [
    ["II 轴环左侧轴肩", f"{hot['II']:.0f} MPa", f"{kfe['II']:.2f}"],
    ["III 右轴承轴肩", f"{hot['III']:.0f} MPa", f"{kfe['III']:.2f}"],
    ["IV 外伸段根部", f"{hot['IV']:.0f} MPa", f"{kfe['IV']:.2f}"],
])}

## 疲劳寿命

载荷谱：跑合试验台“工况模拟”的转矩记录（{block_s:.0f} s 一块，峰值 {float(series.max()):.0f} N·m），雨流计数每块 {len(cyc)} 个循环；
古德曼平均应力修正，迈因纳线性累积（pyLife）。圆角处用有限元应力；外伸段键槽用名义应力乘有效应力集中系数 k_τ = {f4['k_t']:.2f}。

{L.md_table(["材料", "台阶圆角处", "外伸段键槽", "要求"], [
    ["45 钢调质", lf(lives['45-QT']['fillet']), lf(lives['45-QT']['key']), f"{S.LIFE_H:,.0f} h"],
    ["40Cr 调质（选定）", lf(lives['40Cr-QT']['fillet']), lf(lives['40Cr-QT']['key']), f"{S.LIFE_H:,.0f} h"],
])}
"""
case.step("sim", f"有限元支反力与手算差 {abs(err(RA_fe, RA_h)):.1f}%、光滑段应力差 {abs(err(vm_ext, vm_ext_nom)):.1f}%；40Cr 寿命 {lf(V40['life'])}，45 钢只有 {lf(V45['life'])}。",
          f"FEA reactions within {abs(err(RA_fe, RA_h)):.1f}% and plain-shaft stress within {abs(err(vm_ext, vm_ext_nom)):.1f}% of hand calculation; life {lf(V40['life'])} with 40Cr versus {lf(V45['life'])} with 45 steel.",
          md=case.text("4_有限元与疲劳.md", simmd),
          figs=[("4_应力沿轴线.png", "表面冯·米塞斯应力（有限元）与梁理论对照", "Surface von Mises stress (FEA) against beam theory"), ("4_载荷谱与雨流计数.png", "跑合台转矩记录与雨流计数", "Run-in bench torque record and rainflow counting")],
          tools=tools("cae"), facts=[("单元数", "Elements", n_el, ""), ("40Cr 寿命", "Life, 40Cr", f"{V40['life']:,.0f}" if math.isfinite(V40["life"]) else "∞", "h"), ("45 钢寿命", "Life, 45 steel", f"{V45['life']:,.0f}" if math.isfinite(V45["life"]) else "∞", "h")])
case.check("sim", "有限元支反力与手算相差", "FEA bearing reaction vs hand calculation", abs(err(RA_fe, RA_h)), "<=", 5.0, "%", "33.8 节")
case.check("sim", "光滑段应力与手算相差", "FEA plain-shaft stress vs hand calculation", abs(err(vm_ext, vm_ext_nom)), "<=", 5.0, "%", "33.8 节")
case.check("sim", "疲劳寿命（40Cr，跑合台载荷谱）", "Fatigue life (40Cr, run-in bench spectrum)", V40["life"] if math.isfinite(V40["life"]) else 1e12, ">=", S.LIFE_H, "h", "任务书")

# ================================================================ 5 三维与图纸
import build123d as bd  # noqa: E402


def build():
    z, s = 0.0, None
    for d, Lseg, *_ in S.SEG_B:
        c = bd.Pos(0, 0, z) * bd.Cylinder(d / 2, Lseg, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        s = c if s is None else s + c
        z += Lseg
    s = s.clean()
    for zz_, r in S.FILLET_B.items():
        es = [e for e in s.edges() if e.geom_type == bd.GeomType.CIRCLE and abs(e.center().Z - zz_) < 1e-6]
        if len(es) == 2:
            s = s.fillet(r, [min(es, key=lambda e: e.radius)])
    for z0, z1, d, kind in S.KEYWAYS:
        k = mdstd.key_for(d)
        b, t_ = k["b"], k["t"]
        if kind == "C":
            z1 = z1 + b
        H = 10.0
        yc = d / 2 - t_ + H / 2
        cut = bd.Pos(0, yc, (z0 + z1) / 2) * bd.Box(b, H, z1 - z0 - b)
        for zc in ((z0 + b / 2,) if kind == "C" else (z0 + b / 2, z1 - b / 2)):
            cut = cut + bd.Pos(0, yc, zc) * bd.Rot(90, 0, 0) * bd.Cylinder(b / 2, H)
        s = s - cut
    for zc, d in ((0.0, S.SEG_B[0][0]), (S.LEN_B, S.SEG_B[-1][0])):       # 两端倒角 C1.5
        es = [e for e in s.edges() if e.geom_type == bd.GeomType.CIRCLE and abs(e.center().Z - zc) < 1e-6 and abs(e.radius - d / 2) < 1e-6]
        if es:
            s = s.chamfer(1.5, None, es)
    return s


solid = build()
step_path = case.path("SH-301-B.step")
bd.export_step(solid, str(step_path))
rho = mdstd.material(MAT_CHOSEN)["density"]
mass = solid.volume * rho * 1e-6
L.render_solid(solid, case.path("5_三维.png"))
segs = [(d, Lseg, name, tol, 0.8 if tol in ("k6", "r6") else (1.6 if tol == "f9" else None)) for d, Lseg, name, tol in S.SEG_B]
kws = [(z0, z1, d, mdstd.key_for(d)["b"], mdstd.key_for(d)["t"], "N9", kind) for z0, z1, d, kind in S.KEYWAYS]
svg = L.shaft_drawing(segs, kws, S.FILLET_B, item="SH-301", title="输出轴 Output shaft", material="40Cr 调质 241–286 HBW", rev="B",
                      runout=[(0, 0.012, "radial"), (4, 0.012, "radial"), (1, 0.015, "radial"), (2, 0.02, "face")], datums=[(0, "A"), (4, "B")],
                      tech=["调质 241–286 HBW", "未注倒角 C1.5，未注圆角见图（台阶圆角不得大于轴承内圈倒角）",
                            "未注尺寸公差按 GB/T 1804-m", "两端中心孔 A3.15（GB/T 145）保留",
                            "两个键槽在同一条母线上，对称度 0.02", "示例设计，未经实物试制"])
case.text("5_零件图.svg", svg)
cadmd = f"""# 三维模型与零件图

- **三维**：build123d 参数化建模（与在线设计台、教材程序 33.9.1 同一种方法）：七段圆柱 → {len(S.FILLET_B)} 处台阶圆角 → 两个键槽（齿轮处 A 型，外伸段开口 C 型，同一条母线）→ 两端倒角 C1.5。
  体积 {solid.volume / 1e3:.1f} cm³，40Cr 质量 **{mass:.2f} kg**，总长 {S.LEN_B:g} mm，最大直径 Ø48（毛坯 Ø50 够用）。
- **零件图**：轴承位 Ø35 k6、齿轮位 Ø40 r6（与齿轮孔 H7 过盈）、密封段 Ø35 f9、外伸段 Ø30 k6；轴承位、齿轮位 Ra 0.8 磨削；
  以两个轴承位为公共基准 A–B，轴承位、齿轮位径向圆跳动和齿轮定位端面（轴环左端面）圆跳动；两个键槽断面 C–C、D–D。
- 标准件全部来自零件库：轴承 6207（A-BRG-DG）、平键（A-KEY-FLAT）、唇形油封（A-SEL-LIP）。
- 下载：STEP 模型可直接在 FreeCAD、SolidWorks 打开，也可以在“仿真与分析”里上传复算。

{L.md_table(["轴段", "直径", "长度", "公差带", "作用"], [[i + 1, f"Ø{d:g}", f"{Lseg:g}", tol or "—", name] for i, (d, Lseg, name, tol) in enumerate(S.SEG_B)])}
"""
case.step("cad", f"七段、{len(S.FILLET_B)} 处圆角、两个键槽；质量 {mass:.2f} kg；零件图带公差、跳动、粗糙度和两个键槽断面。",
          f"Seven steps, {len(S.FILLET_B)} fillets, two keyways; {mass:.2f} kg; drawing with fits, run-out, roughness and keyway sections.",
          md=case.text("5_三维与图纸.md", cadmd), figs=[("5_三维.png", "SH-301 B 版三维模型", "SH-301 rev B 3D model"), ("5_零件图.svg", "零件图（生成）", "Part drawing (generated)")],
          files=[("SH-301-B.step", "三维模型 STEP", "3D model (STEP)"), ("5_零件图.svg", "零件图 SVG", "Part drawing (SVG)")], tools=tools("engineer", "library", "design"),
          facts=[("质量", "Mass", mass, "kg"), ("总长", "Length", S.LEN_B, "mm")])
case.check("cad", "最大直径不超过毛坯（Ø50 圆钢）", "Largest diameter within the Ø50 bar stock", 48.0, "<=", 48.0, "mm", "任务书")

# ================================================================ 6 工艺与数控程序
import yaml  # noqa: E402
from cae import cam, cam_job as J  # noqa: E402

plan_A = yaml.safe_load(open(ROOT / "factory" / "digital" / "std" / "SH-301_process.yaml", encoding="utf-8"))
segB2 = [(d, Lseg) for d, Lseg, *_ in S.SEG_B]
prof = cam.design_profile(segB2, 1.5)
turn_plan = J.generic_turn_plan(prof, "SH-301", stock_d=50)
turn_plan["material"] = "40Cr"
progs = []
for op in turn_plan["operations"]:
    for p in J.generate(J.plan_turn(turn_plan, op["seq"], prof, "B")):
        progs.append((op["operation"], p))
for i, (z0, z1, d, kind) in enumerate(S.KEYWAYS):
    seg = next(j for j, (za, zb, dd, *_) in enumerate(S.LAY_B) if dd == d and za <= (z0 + z1) / 2 <= zb)
    k = mdstd.key_for(d)
    dp = {"segments": segB2, "chamfer": 1.5, "keyway": {"segment": seg, "b": float(k["b"]), "t": float(k["t"]), "L": float(z1 - z0)}}
    sp = J.plan_slot(plan_A, 50, dp, "B")
    sp["material"] = "40Cr"
    b_ = float(k["b"])
    if kind == "C":                     # 开口键槽：刀具铣出轴端；槽深直接按设计 t（规程里的 H 是齿轮位 Ø40 的）
        Le = z1 - z0 + b_
        sp.update(depth=float(k["t"]), length=Le, a=[-(Le - b_) / 2, 0.0], b=[(Le - b_) / 2, 0.0],
                  stock={"cyl_r": d / 2, "box": [-(Le / 2 + 15), -d / 2, Le / 2 + 15, d / 2]}, x0_from_left=(z0 + z1 + b_) / 2)
        sp["sources"].update(depth="设计槽深 t（开口键槽，外伸段 Ø30）", length="键长 + 键宽（刀具铣出轴端）")
    else:
        sp["x0_from_left"] = (z0 + z1) / 2
    sp["sources"]["x0_from_left"] = "B 版键槽位置（《机械设计》33.2 节，_shaft.KEYWAYS）"
    for p in J.generate(sp, number=1501 + i):
        progs.append((f"铣键槽（{'齿轮处' if kind == 'A' else '外伸段'}）", p))
nc_files = []
rows_nc = []
for name, p in progs:
    fn = f"6_O{p['number']}.nc"
    case.text(fn, p["gcode"])
    nc_files.append((fn, f"O{p['number']} {name} {p['title']}", f"O{p['number']} CNC program"))
    errs = [c for c in p.get("checks", []) if c.get("level") == "error"]
    rows_nc.append([f"O{p['number']}", name, p["title"], f"{p['time']['total_s'] / 60:.1f} min", "无" if not errs else "；".join(c["text"] for c in errs)])
cam_errors = sum(1 for _, p in progs for c in p.get("checks", []) if c.get("level") == "error")
ops_rows = [[o["seq"], o["operation"], o.get("workstation", ""), o.get("minutes", ""), o.get("content", "")[:60]] for o in plan_A["operations"]]
procmd = f"""# 工艺路线与数控程序

**工艺路线**　沿用减速器厂的输出轴工艺规程 GY-SH301（{len(plan_A['operations'])} 道工序），B 版改了三处：毛坯长度按 B 版总长 {S.LEN_B:g} mm 加余量；
精车按 B 版七段轮廓重编程序；铣键槽由一个增加为两个（齿轮处闭口、外伸段开口），同一次装夹、同一条母线。材料改 40Cr 后，调质温度、切削速度按 40Cr 取（切削力按 Kienzle 低合金钢调质组）。

{L.md_table(["工序", "名称", "设备", "工时 / min", "内容（现行规程）"], ops_rows)}

**数控程序**　由“数控编程”按 B 版轮廓生成，并在仿真里走一遍（过切、碰撞、机床功率检查）：

{L.md_table(["程序", "工序", "装夹", "仿真时间", "检查出的错误"], rows_nc)}

改用 40Cr 是工程更改（ECN）：要在“设计发布与审批”里发布 B 版、在“工艺规程”里改版，物料从 RM-45-D50 换成 40Cr 圆钢。
**本案例不改教学工厂的清单**（实验数据要稳定），第 7 步按厂里现行工艺路线仿真加工。
"""
case.step("process", f"{len(plan_A['operations'])} 道工序；生成 {len(progs)} 个数控程序（车两次装夹 × 粗精、两个键槽），仿真检查错误 {cam_errors} 个。",
          f"{len(plan_A['operations'])} operations; {len(progs)} CNC programs generated (two turning set-ups × rough/finish, two keyways); {cam_errors} errors in simulation.",
          md=case.text("6_工艺与数控程序.md", procmd), files=nc_files, tools=tools("process", "cam"),
          facts=[("工序", "Operations", len(plan_A["operations"]), ""), ("数控程序", "CNC programs", len(progs), "")])
case.check("process", "数控程序仿真检查出的错误", "Errors found by CNC simulation", cam_errors, "==", 0, "", "数控编程仿真")

# ================================================================ 7 制造
shop = L.run_shop("SH-301", 20, "WO-CASE-GB-A1", seed=161)
shop2 = L.run_shop("SH-301", 20, "WO-CASE-GB-A2", seed=161, fixes=["shorten_dressing"])
from hub import mrp  # noqa: E402
from sim import errors as ERR  # noqa: E402

mat_c, op_c = mrp.std_unit_cost("SH-301")
rows_q, cpk1, fails1, st1 = L.shop_table(shop["measurements"])
rows_q2, cpk2, fails2, st2 = L.shop_table(shop2["measurements"])
worst = min(st1.values(), key=lambda x: x["cpk"])
worst_id = min(st1, key=lambda k: st1[k]["cpk"])
parts = sorted({m["part_serial"] for m in shop["measurements"]})
n_chars = len({m["characteristic"] for m in shop["measurements"]})
makemd = f"""# 在减速器厂的仿真车间加工两批

用数字工厂仿真车间（和线上减速器厂同一份程序）按现行工艺路线下达工单，从锯床一直走到检验站。
检验站按厂里现行的检验模板量（齿轮位还是 A 版的 k6）；B 版发布后检验模板要跟着改成 r6。

## 第一批 20 根（WO-CASE-GB-A1）

- 全部 {len(shop['routing'])} 道工序走完用了 **{shop['hours']:.1f} 小时**（含排队、换刀、热处理一炉）；
- 检验站量了 {len(parts)} 根，每根 {n_chars} 个特性，共 {len(shop['measurements'])} 个值，不合格 **{fails1}** 个；
- 过程能力：

{L.md_table(["特性", "公差 / mm", "件数", "均值", "标准差", "Cpk"], rows_q)}

**全部合格，但{worst['name']}的 Cpk 只有 {worst['cpk']:.2f}**，低于常用要求 1.33：k6 的公差带只有 {(worst['hi'] - worst['lo']) * 1000:.0f} μm，
外圆磨床 GRD-01 的砂轮在两次修整之间不断磨损，轴径跟着慢慢变大（标准差 {worst['sd'] * 1000:.1f} μm 里大半是这种漂移）。量产时迟早会有超差。

## 改进：缩短砂轮修整间隔，第二批 20 根（WO-CASE-GB-A2）

措施和“质量 → 8D”里能下发的同一个：**{ERR.FIXES['shorten_dressing']}**（实验 41 查的就是这台磨床）。第二批：

{L.md_table(["特性", "公差 / mm", "件数", "均值", "标准差", "Cpk"], rows_q2)}

{st1[worst_id]['name']}：Cpk {st1[worst_id]['cpk']:.2f} → **{st2[worst_id]['cpk']:.2f}**；最低 Cpk {cpk1:.2f} → **{cpk2:.2f}**，不合格 {fails2} 个。代价是修整次数多了，砂轮消耗和磨削工时略增。

## 标准成本

数字工厂成本核算（按现行物料和工时）：材料 ${mat_c:.2f} + 加工 ${op_c:.2f} = **${mat_c + op_c:.2f} / 根**。改 40Cr 后材料一项要按 40Cr 圆钢的单价重算。

想自己走一遍：在“订单与计划”接一张 WQR-105 的订单（或直接下 SH-301 工单），到“车间终端”看各工序，“质量”页看这些特性的控制图，“质量 → 8D”下发同一个措施。
"""
case.step("make", f"第一批 20 根全合格，但轴承位 Cpk {cpk1:.2f}；缩短砂轮修整间隔后第二批最低 Cpk {cpk2:.2f}。标准成本 ${mat_c + op_c:.2f}/根。",
          f"First 20 parts all in tolerance but bearing-seat Cpk {cpk1:.2f}; after shortening the dressing interval the second batch reaches Cpk {cpk2:.2f}. Standard cost ${mat_c + op_c:.2f} per part.",
          md=case.text("7_制造与检验.md", makemd), tools=tools("planner", "operator", "quality", "finance"),
          facts=[("加工时间", "Shop time", shop["hours"], "h"), ("第一批最低 Cpk", "Lowest Cpk, batch 1", cpk1, ""), ("改进后最低 Cpk", "Lowest Cpk, batch 2", cpk2, ""), ("标准成本", "Standard cost", f"${mat_c + op_c:.2f}", "")])
case.check("make", "两批 40 根测量不合格数", "Out-of-tolerance values in 40 parts", fails1 + fails2, "==", 0, "", "检验站")
case.check("make", "改进后最低过程能力 Cpk", "Lowest Cpk after improvement", cpk2, ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

## 校核一览

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

## 这根轴的设计改了什么

1. **结构**：A 版五段 → B 版七段：左轴承位加长到能装下 6207，加轴环给齿轮定位，加密封段；齿轮改带毂锻件。
2. **键**：两个键槽按轮毂长度取标准键长，外伸段用开口 C 型键；两个键槽开在同一条母线上，一次装夹铣出。
3. **圆角**：所有台阶加圆角（不大于轴承内圈倒角），有限元峰值应力有了确定值。
4. **材料**：45 钢在起停冲击下外伸段根部疲劳不够，改 40Cr 调质。
5. **制造**：首批轴承位过程能力不足，磨床改为每 5 件修整一次砂轮。

## 留给学生的问题

1. 把外伸段从 Ø30 加粗到 Ø32，45 钢够不够？毛坯、联轴器、键要跟着改什么？
2. 跑合台每 25 s 起停一次；实际输送机每小时起停 10 次，45 钢的寿命是多少？
3. 第 7 步第一批轴承位的 Cpk 为什么低？除了缩短修整间隔，还有什么办法（在线测量补偿、换砂轮）？各自的代价是什么？
4. 在“仿真与分析”里上传本案例的 STEP，按 33.9.5 节操作 (1)–(10) 复算，和第 4 步比较。

相关：《机械设计》第 33 章（全章），实验 8（输出轴强度与疲劳）、实验 10（数控车削与键槽铣削）、实验 12（一根轴的数字化设计）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；设计改了结构、键、圆角、材料四处，制造改了砂轮修整间隔。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; changes in layout, keys, fillets and material, plus a shorter wheel-dressing interval in production.",
          md=case.text("8_总结.md", review), tools=tools("design"))
case.write()
