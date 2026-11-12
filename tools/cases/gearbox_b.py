"""第 161b 轮：减速器厂案例 B——WQR-105 低速级齿轮副 GR-203 / GR-302，从任务书到车间加工 20 对。

    python3 tools/cases/gearbox_b.py

齿轮强度用数字工厂 cae/gears.py（GB/T 3480 简化，与平缝机送布齿轮同一个函数）；轮齿有限元用 Gmsh + CalculiX（cae/solve.py）；
齿形用齿条刀具展成（tools/cases/gearlib.py）；工艺用工厂现行工艺路线 + AI 工艺评审员（hub/process.review）+ 数控编程（cam_job）；
制造用数字工厂仿真车间；标准成本用 hub/mrp.py。输出到 factory/cases/gearbox/B/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory"), str(ROOT / "textbook" / "mechdesign" / "ch33" / "code"),
                str(ROOT / "textbook" / "mechdesign" / "conventions")]
os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import gearlib as GL  # noqa: E402
from cae import gears as G  # noqa: E402
from factory import data as F  # noqa: E402

TOOLS = {
    "engineer": ("在线设计", "Online design", "/work/engineer"),
    "library": ("零件库", "Parts library", "/library"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
    "design": ("设计发布与审批", "Design release", "/design"),
    "process": ("工艺规程与 AI 评审", "Process plans & AI review", "/process"),
    "cam": ("数控编程", "CNC programming", "/cam"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "finance": ("经营与成本", "Business & cost", "/finance"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

# ---------------------------------------------------------------- 已知条件
T2 = 350.0                          # 输出轴额定转矩 N·m（已含工况系数 K_A，与案例 A 同）
ETA = 0.97 * 0.99                   # 一级齿轮 × 一对轴承
I2 = F.GEARS["GR-302"]["z"] / F.GEARS["GR-203"]["z"]
T1 = T2 / (I2 * ETA)                # GR-203（中间轴）转矩
N_IN = 1450.0
N1 = N_IN / (F.GEARS["GR-202"]["z"] / F.GEARS["SH-101"]["z"])
LIFE_H = 10000.0
M, Z1, Z2 = 3.0, F.GEARS["GR-203"]["z"], F.GEARS["GR-302"]["z"]
A_FIX = M * (Z1 + Z2) / 2           # 箱体合镗的中心距
B2, B1 = 45.0, 50.0                 # 大齿轮齿宽（案例 A 的 GR-302 轮缘宽）、小齿轮宽 5 mm
MAT1, MAT2 = "20CrMnTi-carburized", "40Cr-QT"
KA = 1.0                            # T2 已含 K_A，不再重复乘
series_K = None

case = L.Case("gearbox", "B", "中等", "低速级齿轮副 GR-203 / GR-302", "Low-speed gear pair GR-203 / GR-302", "GR-203、GR-302",
              "WQR-105 第二级的一对齿轮：直齿和斜齿方案比较、齿面接触与齿根弯曲强度、轮齿有限元、展成齿形与三维、零件图、工艺与 AI 评审、车间加工 20 对。",
              "The second-stage gear pair of the WQR-105: spur versus helical, contact and root-bending strength, tooth FEA, generated tooth form and 3D, drawings, process review, and 20 pairs made in the simulated shop.",
              "tools/cases/gearbox_b.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：WQR-105 低速级齿轮副

**用途**　二级圆柱齿轮减速器 WQR-105 的第二级：小齿轮 GR-203 装在中间轴 SH-201 上，大齿轮 GR-302 装在输出轴 SH-301 上（案例 A）。

| 项目 | 要求 | 出处 |
|---|---|---|
| 大齿轮转矩 | {T2:.0f} N·m（已含工况系数 K_A） | 参数配置器 T_RATED；案例 A |
| 小齿轮转矩 | {T1:.1f} N·m（= T₂ /（i₂ η），η = 0.97 × 0.99） | 《机器人学》32.1 节的效率取值 |
| 小齿轮转速 | {N1:.1f} r/min（输入 {N_IN:.0f} ÷ 第一级 72/24） | 工厂设计 |
| 传动比 | i₂ = {I2:g}（总传动比 10.5 不变） | 产品规格 |
| 中心距 | a = {A_FIX:g} mm（箱体已合镗，不改） | 箱体 HSG-001/002 |
| 要求寿命 | {LIFE_H:,.0f} h | 与案例 A 同 |
| 材料 | 小齿轮 20CrMnTi 渗碳淬火 58–62 HRC（棒料 RM-20CR-D70）；大齿轮 40Cr 调质（锻坯 RM-40CR-F225） | 工厂物料 |
| 孔 | GR-203 Ø35 H7、键 10 × 8；GR-302 Ø40 H7、键 12 × 8，轮毂 Ø64 × 55 | 工厂尺寸链；案例 A |
| 强度 | 齿面接触 S_H ≥ 1.0，齿根弯曲 S_F ≥ 1.25 | GB/T 3480 一般可靠度 |

**要定的**　齿形（直齿还是斜齿）、齿宽、精度等级；**交付物**：计算书、轮齿有限元、三维模型、两张零件图、工艺路线与评审意见、首批 20 对的加工记录与成本。
"""
case.step("brief", f"小齿轮 {T1:.1f} N·m、{N1:.0f} r/min，i₂ = {I2:g}，中心距 {A_FIX:g} mm 固定；寿命 {LIFE_H:,.0f} h。",
          f"Pinion {T1:.1f} N·m at {N1:.0f} rpm, i₂ = {I2:g}, centre distance fixed at {A_FIX:g} mm; {LIFE_H:,.0f} h life.",
          md=case.text("1_任务书.md", brief), tools=tools("library"),
          facts=[("小齿轮转矩", "Pinion torque", T1, "N·m"), ("小齿轮转速", "Pinion speed", N1, "r/min"), ("中心距", "Centre distance", A_FIX, "mm")])

# ================================================================ 2 方案
def option(name, mn, z1, z2, beta, b):
    g = G.geometry(mn, z1, z2, beta, b=b)
    T1o = T2 / ((z2 / z1) * ETA)
    r = G.check(T1o, N1, g, MAT1, MAT2, KA=KA, hours=LIFE_H)
    Fa = r["Ft"] * math.tan(math.radians(beta))
    return dict(name=name, g=g, r=r, Fa=Fa, i=z2 / z1)


beta_h = math.degrees(math.acos(2.5 * (23 + 81) / (2 * A_FIX)))
opts = [option("直齿 m3、20/70、b = 40", 3, 20, 70, 0, 40), option("直齿 m3、20/70、b = 45", 3, 20, 70, 0, 45),
        option("直齿 m3、20/70、b = 50", 3, 20, 70, 0, 50), option(f"斜齿 mn2.5、23/81、β = {beta_h:.1f}°、b = 45", 2.5, 23, 81, beta_h, 45)]
CH = opts[1]
rows = [[o["name"], f"{o['i']:.3f}", f"{o['g']['eps_a'] + o['g']['eps_b']:.2f}", f"{o['r']['SH']:.2f}", f"{o['r']['SF']:.2f}", f"{o['Fa']:.0f} N",
         "✓ 选定" if o is CH else ("✗ 接触不够" if o["r"]["SH"] < 1.0 else "")] for o in opts]
concept = f"""# 方案比较

中心距 {A_FIX:g} mm（箱体已合镗）和传动比 3.5（总传动比 10.5）不能变。比较四个方案（齿面接触最小安全系数 S_H、齿根弯曲最小安全系数 S_F 用第 3 步同一个函数算）：

{L.md_table(["方案", "传动比", "总重合度", "S_H", "S_F", "轴向力", ""], rows)}

- **接触强度是这对齿轮的关键**：弯曲安全系数都在 4 以上，接触只略大于 1——大齿轮 40Cr 调质的齿面硬度低，许用接触应力只有小齿轮的一半左右。
- **斜齿**接触强度高约 15%、更平稳；但齿数只能取 23/81，传动比变成 3.522，总传动比偏离 10.5；还要多出约 {opts[3]['Fa']:.0f} N 轴向力，两根轴的深沟球轴承、箱体都要重新校核；滚刀也要换成 m2.5。输出端只有 {N1 / I2:.0f} r/min，节线速度 {CH['r']['v']:.1f} m/s，噪声不是问题。
- **直齿 b = 40** 接触不够；**b = 50** 余量更大，但 GR-302 的轮缘宽是 45（案例 A 的结构），加宽要改锻坯和轴的长度。

**选定：直齿 m3、20/70，大齿轮宽 45、小齿轮宽 50**（现行齿数和中心距不变）。接触余量不大（S_H = {CH['r']['SH']:.2f}），第 7 步要盯住齿面质量。
"""
case.step("concept", f"四个方案比接触与弯曲强度；斜齿接触高约 15% 但改传动比、多轴向力；选直齿 b = 45，S_H = {CH['r']['SH']:.2f}。",
          f"Four concepts compared on contact and bending; helical gains about 15% in contact but changes the ratio and adds axial load; spur with b = 45 chosen, S_H = {CH['r']['SH']:.2f}.",
          md=case.text("2_方案.md", concept), tools=tools("design"),
          facts=[("选定方案 S_H", "S_H, chosen", CH["r"]["SH"], ""), ("斜齿方案 S_H", "S_H, helical", opts[3]["r"]["SH"], "")])
case.check("concept", "选定方案齿面接触安全系数", "Contact safety factor of the chosen design", CH["r"]["SH"], ">=", 1.0, "", "GB/T 3480")

# ================================================================ 3 计算
g, r = CH["g"], CH["r"]
k1, W1 = F.base_tangent_length(M, Z1)
k2, W2 = F.base_tangent_length(M, Z2)
_, w1lo, w1hi = F.gear_w("GR-203", -0.05, -0.12)
_, w2lo, w2hi = F.gear_w("GR-302", -0.06, -0.14)
geo_rows = [["分度圆直径 d", f"{g['d1']:.2f}", f"{g['d2']:.2f}", "d = m z"], ["齿顶圆直径 dₐ", f"{g['da1']:.2f}", f"{g['da2']:.2f}", "dₐ = d + 2m"],
            ["齿根圆直径 d_f", f"{g['df1']:.2f}", f"{g['df2']:.2f}", "d_f = d − 2.5m"], ["基圆直径 d_b", f"{g['db1']:.3f}", f"{g['db2']:.3f}", "d_b = d cos α"],
            ["齿宽 b", f"{B1:g}", f"{B2:g}", "方案选定"], ["跨齿数 k、公法线长度 W_k", f"{k1}，{W1:.3f}", f"{k2}，{W2:.3f}", "W = m cos α [π(k − 0.5) + z inv α]"],
            ["公法线检验范围", f"{w1hi:.3f} – {w1lo:.3f}", f"{w2hi:.3f} – {w2lo:.3f}", "工厂检验模板（含侧隙减薄）"]]
calcmd = f"""# 计算书：低速级齿轮副（GB/T 3480 简化方法）

## 几何（标准齿轮，α = 20°，hₐ* = 1，c* = 0.25，不变位）

中心距 a = {g['a']:.1f} mm，端面重合度 ε_α = {g['eps_a']:.3f}。

{L.md_table(["量", "GR-203（z = 20）", "GR-302（z = 70）", "公式 / 出处"], geo_rows)}

## 载荷

| 量 | 值 | 公式 / 出处 |
|---|---|---|
| 圆周力 F_t | {r['Ft']:.0f} N | F_t = 2T₁/d₁ |
| 径向力 F_r | {r['Ft'] * math.tan(math.radians(20)):.0f} N | F_r = F_t tan α |
| 节线速度 v | {r['v']:.2f} m/s | v = π d₁ n₁ / 60 000 |
| 载荷系数 K = K_A K_v K_α K_β | {r['K']:.3f}（K_A = {KA:g}，转矩已含；K_v = K_α = K_β = 1.1） | cae/gears.py 默认值 |

这里的 F_t 与案例 A 输出轴上的齿轮力（{2 * T2 * 1e3 / g['d2']:.0f} N）相同——同一对齿啮合。

## 齿面接触

| 量 | 值 |
|---|---|
| Z_E（弹性系数） | {r['ZE']:.1f} √MPa |
| Z_H（节点区域系数） | {r['ZH']:.3f} |
| Z_ε（重合度系数） | {r['Zeps']:.3f} |
| σ_H = Z_H Z_E Z_ε √(2KT₁(u+1)/(b d₁² u)) | **{r['sigma_H']:.0f} MPa** |
| 应力循环次数 N₁ / N₂ | {r['N1']:.3g} / {r['N2']:.3g} |
| 寿命系数 Z_N1 / Z_N2 | {r['ZN1']:.3f} / {r['ZN2']:.3f} |
| 许用 σ_Hlim·Z_N：小齿轮 / 大齿轮 | {G.MATERIALS[MAT1]['sHlim'] * r['ZN1']:.0f} / {G.MATERIALS[MAT2]['sHlim'] * r['ZN2']:.0f} MPa |
| 安全系数 S_H1 / S_H2 | {r['SH1']:.2f} / **{r['SH2']:.2f}** |

## 齿根弯曲

| 量 | GR-203 | GR-302 |
|---|---|---|
| Y_Fa / Y_Sa | {r['YFa1']:.2f} / {r['YSa1']:.2f} | {r['YFa2']:.2f} / {r['YSa2']:.2f} |
| σ_F = 2KT₁ Y_Fa Y_Sa Y_ε / (b mₙ d₁) | {r['sigma_F1']:.0f} MPa | {r['sigma_F2']:.0f} MPa |
| 许用 σ_Flim·Y_ST·Y_N | {G.MATERIALS[MAT1]['sFlim'] * 2 * r['YN1']:.0f} MPa | {G.MATERIALS[MAT2]['sFlim'] * 2 * r['YN2']:.0f} MPa |
| 安全系数 S_F | {r['SF1']:.2f} | {r['SF2']:.2f} |

材料极限应力：{G.MATERIALS[MAT1]['hard']}：σ_Hlim = {G.MATERIALS[MAT1]['sHlim']:g}、σ_Flim = {G.MATERIALS[MAT1]['sFlim']:g} MPa；
{G.MATERIALS[MAT2]['hard']}：σ_Hlim = {G.MATERIALS[MAT2]['sHlim']:g}、σ_Flim = {G.MATERIALS[MAT2]['sFlim']:g} MPa（ISO 6336-5 MQ 级的量级）。

**结论**：接触 S_H = {r['SH']:.2f} ≥ 1.0，弯曲 S_F = {r['SF']:.2f} ≥ 1.25，满足。起动冲击（案例 A 的跑合台记录，峰值 1.66 倍）在齿面上的累积损伤，
可以照案例 A 第 4 步的载荷谱方法算，留作习题。
"""
case.step("calc", f"F_t = {r['Ft']:.0f} N；σ_H = {r['sigma_H']:.0f} MPa，S_H = {r['SH']:.2f}（大齿轮）；S_F = {r['SF']:.2f}；公法线 W₃ = {W1:.3f}、W₈ = {W2:.3f}。",
          f"F_t = {r['Ft']:.0f} N; σ_H = {r['sigma_H']:.0f} MPa, S_H = {r['SH']:.2f} (wheel); S_F = {r['SF']:.2f}; span measurements {W1:.3f} / {W2:.3f} mm.",
          md=case.text("3_计算书.md", calcmd), tools=tools("cae"),
          facts=[("接触应力", "Contact stress", r["sigma_H"], "MPa"), ("S_H", "S_H", r["SH"], ""), ("S_F", "S_F", r["SF"], "")])
case.check("calc", "齿面接触安全系数 S_H", "Contact safety factor S_H", r["SH"], ">=", 1.0, "", "GB/T 3480")
case.check("calc", "齿根弯曲安全系数 S_F", "Bending safety factor S_F", r["SF"], ">=", 1.25, "", "GB/T 3480")
case.check("calc", "端面重合度", "Transverse contact ratio", g["eps_a"], ">=", 1.2, "", "教材常用下限")

# ================================================================ 4 仿真：轮齿有限元 + 啮合线上的接触应力
fe = {}
for code, z, b in (("GR-203", Z1, B1), ("GR-302", Z2, B2)):
    Ftmm = r["Ft"] / b
    res = GL.tooth_fea(M, z, Ftmm, h=0.6)
    YFa, YSa = G.y_fa_sa(z)
    s0 = r["Ft"] / (b * M) * YFa * YSa
    fe[code] = dict(res=res, s0=s0, YFa=YFa, YSa=YSa, b=b)
# 用有限元齿根应力重算弯曲安全系数（K、Y_ε 照第 3 步）
for code, i in (("GR-203", 1), ("GR-302", 2)):
    x = fe[code]
    mat = G.MATERIALS[MAT1 if i == 1 else MAT2]
    sF_fe = x["res"]["sigma1"] * r["K"] * r["Yeps"]
    x["SF_fe"] = mat["sFlim"] * 2 * r[f"YN{i}"] / sF_fe
# 云图：中间齿 z = 0 面上的最大主应力
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.8))
for ax, code in zip(axs, ("GR-203", "GR-302")):
    res = fe[code]["res"]
    xyz = res["xyz"]
    sel = np.abs(xyz[:, 2]) < 1e-6
    ids = res["ntags"][sel]
    pts = xyz[sel]
    vals = []
    for n in ids:
        st = res["stress"].get(int(n))
        if st is None:
            vals.append(np.nan)
            continue
        sxx, syy, szz, sxy, syz, szx = st[:6]
        vals.append(np.linalg.eigvalsh(np.array([[sxx, sxy, szx], [sxy, syy, syz], [szx, syz, szz]]))[2])
    vals = np.array(vals)
    ok = np.isfinite(vals)
    import matplotlib.tri as mtri
    from shapely import prepared
    from shapely.geometry import Point
    z_ = Z1 if code == "GR-203" else Z2
    shp, _, _, _ = GL.tooth_shapes(M, z_, 3, rim=res["rim"])
    inside = prepared.prep(shp.buffer(1e-3))
    tri = mtri.Triangulation(pts[ok, 0], pts[ok, 1])
    cxy = pts[ok][tri.triangles].mean(axis=1)
    tri.set_mask([not inside.contains(Point(x, y)) for x, y in cxy[:, :2]])   # 齿槽里的三角形不画（三角化会跨过齿槽）
    tc = ax.tricontourf(tri, np.clip(vals[ok], -50, None), levels=24, cmap="viridis")
    mid = res["mid"]
    rr = res["info"]["ra"]
    ax.set_xlim(rr * math.cos(mid) - 2.4 * M, rr * math.cos(mid) + 2.4 * M)
    ax.set_ylim(rr * math.sin(mid) - 4.2 * M, rr * math.sin(mid) + 0.4 * M)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(f"{code}：最大主应力 / MPa（峰值 {res['sigma1']:.0f}）", fontsize=9.5)
    fig.colorbar(tc, ax=ax, shrink=0.7)
case.fig(fig, "4_轮齿有限元.png")
# 啮合线上的接触应力（Hertz 线接触；双齿区每对齿按一半载荷）
rb1, rb2, ra1, ra2 = g["db1"] / 2, g["db2"] / 2, g["da1"] / 2, g["da2"] / 2
al = math.radians(20)
N12 = g["a"] * math.sin(al)
rA = N12 - math.sqrt(ra2 ** 2 - rb2 ** 2)
rE = math.sqrt(ra1 ** 2 - rb1 ** 2)
pb = math.pi * M * math.cos(al)
rB, rD, rC = rE - pb, rA + pb, g["d1"] / 2 * math.sin(al)       # B、D：单齿啮合区的两端
Fn = T1 * 1e3 / rb1 * r["K"]
ZE = r["ZE"]
s = np.linspace(rA, rE, 400)
share = np.where((s >= rB) & (s <= rD), 1.0, 0.5)               # B（= E − p_b）到 D（= A + p_b）单齿啮合
sigH = ZE * np.sqrt(share * Fn / B2 * (1 / s + 1 / (N12 - s)))
sig_at = lambda x, sh: ZE * math.sqrt(sh * Fn / B2 * (1 / x + 1 / (N12 - x)))  # noqa: E731
sB, sC, sD = sig_at(rB, 1.0), sig_at(rC, 1.0), sig_at(rD, 1.0)
fig, ax = plt.subplots(figsize=(8.2, 3.2))
ax.plot(s, sigH, color=L.ACCENT, lw=1.6)
for x, lab in ((rA, "A"), (rB, "B"), (rC, "C"), (rD, "D"), (rE, "E")):
    ax.axvline(x, color=L.MUTED, lw=0.6, ls="--")
    ax.text(x, max(sigH.max(), G.MATERIALS[MAT2]["sHlim"]) * 1.05, lab, ha="center", fontsize=9)
ax.axhline(G.MATERIALS[MAT2]["sHlim"] * r["ZN2"], color=L.BAD, lw=0.9, ls=":")
ax.text(rA, G.MATERIALS[MAT2]["sHlim"] * r["ZN2"] + 8, "大齿轮许用 σ_Hlim·Z_N", fontsize=8.5, color=L.BAD)
ax.set_xlabel("沿啮合线，小齿轮齿面曲率半径 ρ₁ / mm（A 进入啮合 → E 退出）")
ax.set_ylabel("σ_H / MPa")
ax.set_ylim(0, max(sigH.max(), G.MATERIALS[MAT2]["sHlim"]) * 1.12)
case.fig(fig, "4_啮合线接触应力.png")
sim_rows = [[c, f"{fe[c]['res']['n_el']:,}", f"{fe[c]['res']['sigma1']:.0f} MPa", f"{fe[c]['s0']:.0f} MPa（Y_Fa {fe[c]['YFa']:.2f} × Y_Sa {fe[c]['YSa']:.2f}）",
             f"{fe[c]['res']['sigma1'] / fe[c]['s0']:.2f}", f"{fe[c]['SF_fe']:.2f}"] for c in fe]
simmd = f"""# 仿真：轮齿有限元与啮合线上的接触应力

## 轮齿有限元

**齿形**：用标准齿条刀具（α 20°，切入 1.25m，刀顶圆角 0.38m）展成——把齿坯减去刀具在 900 个滚动位置的并集，渐开线齿面和齿根过渡曲线一起得到，不是画出来的。
**模型**：三个齿、厚 1 mm 的薄片（平面应力），Gmsh 二阶四面体、CalculiX 求解（与数字工厂“仿真与分析”同一套代码）；齿根以下 3m 的内圆和两侧剖切面固定；
中间齿受力侧齿顶加法向力（沿啮合线，大小 F_t/(b cos α) × 1 mm）。齿根圆角处加密到 0.19 mm。

{L.md_table(["齿轮", "单元", "齿根最大主应力（有限元）", "ISO 齿顶加载名义值 F_t/(bm)·Y_Fa·Y_Sa", "有限元 / ISO", "按有限元应力的 S_F"], sim_rows)}

有限元比 ISO 的系数法高十几个百分点：ISO 的 Y_Fa、Y_Sa 是查表插值的、按 30° 切线法定危险截面，有限元直接算出整个过渡曲线上的最大值。
即使按有限元的应力算，弯曲安全系数仍远大于 1.25——这对齿轮不会断齿，关键在齿面。

## 啮合线上的接触应力

一对齿从 A 进入啮合到 E 退出：A–B、D–E 两对齿同时啮合（每对约一半载荷，不计轮齿刚度的差别），B–D 只有一对齿（全部载荷）。用赫兹线接触公式沿啮合线算：

- 节点 C：σ_H = {sC:.0f} MPa（第 3 步的 Z_H 就是在节点算的，那里乘了重合度系数 Z_ε = {r['Zeps']:.3f}）；
- B 点（小齿轮单齿啮合下界点，接触在小齿轮齿根、大齿轮齿顶）：σ_H = {sB:.0f} MPa，比节点高 {(sB / sC - 1) * 100:.0f}%——管小齿轮（ISO 6336 的 Z_B），渗碳淬火许用 {G.MATERIALS[MAT1]['sHlim'] * r['ZN1']:.0f} MPa，没问题；
- D 点（大齿轮单齿啮合下界点，接触在大齿轮齿根）：σ_H = **{sD:.0f} MPa**——管大齿轮（ISO 6336 的 Z_D），40Cr 调质许用 {G.MATERIALS[MAT2]['sHlim'] * r['ZN2']:.0f} MPa，**只剩 {(G.MATERIALS[MAT2]['sHlim'] * r['ZN2'] / sD - 1) * 100:.0f}% 余量**。

第 3 步按节点算出的 S_H = {r['SH']:.2f} 看起来还有 {(r['SH'] - 1) * 100:.0f}% 余量，沿啮合线一算，大齿轮齿根附近的单齿区只剩 {(G.MATERIALS[MAT2]['sHlim'] * r['ZN2'] / sD - 1) * 100:.0f}%。
A 点附近曲线翘得很高：那里小齿轮刚过基圆、曲率半径很小；实际上大齿轮齿顶有倒角或修缘，进入啮合时轮齿刚度也是逐渐增加的，分到的载荷远不到一半，所以 ISO 6336 只在 B、C、D 三点校核。

这对齿轮能用，但大齿轮齿面是全减速器最弱的地方：点蚀会最先出现在大齿轮齿根附近。要多留余量，最直接的是大齿轮齿面淬火（见第 8 步）。
"""
case.step("sim", f"展成齿形 + 三齿薄片有限元：齿根应力比 ISO 系数法高 {(fe['GR-203']['res']['sigma1'] / fe['GR-203']['s0'] - 1) * 100:.0f}%，按它算 S_F 仍有 {min(x['SF_fe'] for x in fe.values()):.1f}；沿啮合线算，大齿轮 D 点接触应力 {sD:.0f} MPa，余量只有 {(G.MATERIALS[MAT2]['sHlim'] * r['ZN2'] / sD - 1) * 100:.0f}%。",
          f"Generated tooth form and a three-tooth FEA slice: root stress {(fe['GR-203']['res']['sigma1'] / fe['GR-203']['s0'] - 1) * 100:.0f}% above the ISO factor method, still S_F ≥ {min(x['SF_fe'] for x in fe.values()):.1f}; along the line of action the wheel's contact stress at D is {sD:.0f} MPa, only {(G.MATERIALS[MAT2]['sHlim'] * r['ZN2'] / sD - 1) * 100:.0f}% margin.",
          md=case.text("4_有限元与接触应力.md", simmd),
          figs=[("4_轮齿有限元.png", "三齿薄片有限元：最大主应力（中间齿受力）", "Three-tooth slice FEA: maximum principal stress (middle tooth loaded)"),
                ("4_啮合线接触应力.png", "沿啮合线的接触应力（双齿区一半载荷）", "Contact stress along the line of action (half load in double-tooth zones)")],
          tools=tools("cae"),
          facts=[("齿根应力（有限元）", "Root stress (FEA)", fe["GR-203"]["res"]["sigma1"], "MPa"), ("D 点接触应力", "Contact stress at D", sD, "MPa")])
case.check("sim", "按有限元齿根应力的弯曲安全系数", "Bending safety factor from FEA root stress", min(x["SF_fe"] for x in fe.values()), ">=", 1.25, "", "GB/T 3480")
case.check("sim", "B 点接触应力（小齿轮）不超过许用值", "Contact stress at B within the pinion's allowable", sB, "<=",
           G.MATERIALS[MAT1]["sHlim"] * r["ZN1"], "MPa", "ISO 6336（Z_B）")
case.check("sim", "D 点接触应力（大齿轮）不超过许用值", "Contact stress at D within the wheel's allowable", sD, "<=",
           G.MATERIALS[MAT2]["sHlim"] * r["ZN2"], "MPa", "ISO 6336（Z_D）")

# ================================================================ 5 三维与图纸
import build123d as bd  # noqa: E402

KEY1, KEY2 = (10.0, 38.3 - 35 / 2), (12.0, 43.3 - 40 / 2)          # 键槽：槽底离孔心（孔径 + t₂ − 孔半径）
pin, _ = GL.gear_solid(M, Z1, B1, 35.0, key=KEY1)
wheel, _ = GL.gear_solid(M, Z2, B2, 40.0, key=KEY2, hub=(64.0, 55.0), web=(15.0, g["df2"] - 2 * 2.5 * M))
bd.export_step(pin, str(case.path("GR-203.step")))
bd.export_step(wheel, str(case.path("GR-302.step")))
pair = bd.Compound([pin, bd.Pos(A_FIX, 0, 0) * bd.Rot(0, 0, 180 + 180 / Z2) * wheel])
L.render_solid(pair, case.path("5_三维.png"), elev=35, azim=-60, size=(8, 4.6))
m1 = pin.volume * 7.85e-6
m2 = wheel.volume * 7.85e-6
params1 = [("模数 m", "3"), ("齿数 z", "20"), ("压力角 α", "20°"), ("齿顶高系数 hₐ*", "1"), ("变位系数 x", "0"),
           ("精度等级", "8（GB/T 10095.1）"), ("配对齿轮", "GR-302（z = 70）"), ("中心距", f"{A_FIX:g} ± 0.03"),
           ("跨齿数 k", str(k1)), ("公法线长度 W_k", f"{W1:.3f}（{-0.05:+.2f} / {-0.12:+.2f}）")]
params2 = [("模数 m", "3"), ("齿数 z", "70"), ("压力角 α", "20°"), ("齿顶高系数 hₐ*", "1"), ("变位系数 x", "0"),
           ("精度等级", "8（GB/T 10095.1）"), ("配对齿轮", "GR-203（z = 20）"), ("中心距", f"{A_FIX:g} ± 0.03"),
           ("跨齿数 k", str(k2)), ("公法线长度 W_k", f"{W2:.3f}（{-0.06:+.2f} / {-0.14:+.2f}）")]
case.text("5_GR-203零件图.svg", GL.gear_drawing(item="GR-203", title="小齿轮 Pinion", material="20CrMnTi 渗碳淬火", rev="B", m=M, z=Z1, b=B1,
                                               da=g["da1"], d=g["d1"], df=g["df1"], bore=35.0, bore_tol="H7", key_w=10, key_depth_total=KEY1[1],
                                               params=params1, tech=["渗碳淬火，有效硬化层 0.6–0.9，齿面 58–62 HRC", "孔与两端面淬火后磨削",
                                                                     "未注倒角 C1，齿顶倒角 0.5 × 45°", "示例设计，未经实物试制"]))
case.text("5_GR-302零件图.svg", GL.gear_drawing(item="GR-302", title="大齿轮 Gear", material="40Cr 调质 241–286 HBW", rev="B", m=M, z=Z2, b=B2,
                                               da=g["da2"], d=g["d2"], df=g["df2"], bore=40.0, bore_tol="H7", key_w=12, key_depth_total=KEY2[1],
                                               hub=(64.0, 55.0), web=(15.0, g["df2"] - 2 * 2.5 * M), params=params2,
                                               tech=["锻件，调质 241–286 HBW", "轮毂两端面对孔轴线的端面圆跳动 0.02", "未注倒角 C1.5",
                                                     "示例设计，未经实物试制"]))
cadmd = f"""# 三维模型与零件图

- **齿形**：三维里的齿形就是第 4 步展成出来的那一条外廓（渐开线 + 齿根过渡曲线），拉伸成齿轮，不是用近似圆弧画的。
- **GR-203**：齿宽 {B1:g}、孔 Ø35 H7、键槽 10 JS9；质量约 {m1:.2f} kg。
- **GR-302**：齿宽（轮缘）{B2:g}、辐板厚 15、轮毂 Ø64 × 55（案例 A 的 B 版带毂锻件）、孔 Ø40 H7、键槽 12 JS9；质量约 {m2:.1f} kg。
- **零件图**：轴向全剖视、啮合参数表（模数、齿数、精度等级、跨齿数和公法线长度及偏差——车间用公法线千分尺检验）、技术要求。
- 三维效果图把两只齿轮按中心距 {A_FIX:g} 放在啮合位置。
"""
LIBP = [L.lib_part("A-KEY-FLAT", "10x8x40"), L.lib_part("A-KEY-FLAT", "12x8x45")]
cadmd += f"""
## 用到的零件库零件

{L.lib_md(LIBP, {"A-KEY-FLAT/10x8x40": "GR-203 与中间轴（轮毂宽 50）", "A-KEY-FLAT/12x8x45": "GR-302 与输出轴（轮毂宽 55，案例 A）"})}

键槽宽、毂槽深 t₂ 取零件库（GB/T 1095）：GR-203 孔径 + t₂ = 35 + {LIBP[0]['row']['t2_mm']}，GR-302 = 40 + {LIBP[1]['row']['t2_mm']}，和两张零件图一致。
"""
key_ok = abs(35 + float(LIBP[0]["row"]["t2_mm"]) - 38.3) < 1e-6 and abs(40 + float(LIBP[1]["row"]["t2_mm"]) - 43.3) < 1e-6
case.check("cad", "毂槽深与零件库（GB/T 1095）一致", "Hub keyway depth matches the parts library", 1 if key_ok else 0, "==", 1, "", "零件库 A-KEY-FLAT")
case.step("cad", f"展成齿形直接拉伸成三维；GR-203 约 {m1:.2f} kg，GR-302 约 {m2:.1f} kg；两张零件图带啮合参数表和公法线检验尺寸。",
          f"The generated tooth outline is extruded into 3D; GR-203 about {m1:.2f} kg, GR-302 about {m2:.1f} kg; two drawings with gear data tables and span measurements.",
          md=case.text("5_三维与图纸.md", cadmd),
          figs=[("5_三维.png", "齿轮副三维（中心距 135 啮合位置）", "3D gear pair at 135 mm centre distance"),
                ("5_GR-203零件图.svg", "GR-203 零件图（生成）", "GR-203 drawing (generated)"), ("5_GR-302零件图.svg", "GR-302 零件图（生成）", "GR-302 drawing (generated)")],
          files=[("GR-203.step", "GR-203 三维 STEP", "GR-203 3D model (STEP)"), ("GR-302.step", "GR-302 三维 STEP", "GR-302 3D model (STEP)")],
          tools=tools("design") + L.lib_tools(LIBP), facts=[("GR-203 质量", "GR-203 mass", m1, "kg"), ("GR-302 质量", "GR-302 mass", m2, "kg")])

# ================================================================ 6 工艺
from hub import process as PR  # noqa: E402
from cae import cam, cam_job as J  # noqa: E402

proc_rows, review_rows, progs = [], [], []
for code, prof_segs in (("GR-203", [(g["da1"], B1)]), ("GR-302", [(64.0, (55 - B2) / 2), (g["da2"], B2), (64.0, (55 - B2) / 2)])):
    plan = PR.factory_plan(code)
    for o in plan["operations"]:
        proc_rows.append([code, o["seq"], o["operation"], o["workstation"], o["minutes"]])
    for x in PR.review(plan):
        if x["level"] in ("error", "warning"):
            review_rows.append([code, x["level"], x["rule"], x.get("seq") or "", x["text"][:90]])
    prof = cam.design_profile(prof_segs, 1.0)
    tp = J.generic_turn_plan(prof, code, stock_d=math.ceil(max(d for d, _ in prof_segs) + 4))
    tp["material"] = "20CrMnTi" if code == "GR-203" else "40Cr"
    for op in tp["operations"]:
        for p in J.generate(J.plan_turn(tp, op["seq"], prof, "B"), number=2000 + 100 * (code == "GR-302") + op["seq"]):
            progs.append((code, op["operation"], p))
nc_files, nc_rows = [], []
for code, opn, p in progs:
    fn = f"6_{code}_O{p['number']}.nc"
    case.text(fn, p["gcode"])
    nc_files.append((fn, f"{code} O{p['number']} {opn} {p['title']}", f"{code} O{p['number']} CNC program"))
    errs = [c for c in p.get("checks", []) if c.get("level") == "error"]
    nc_rows.append([code, f"O{p['number']}", opn, p["title"], f"{p['time']['total_s'] / 60:.1f} min", "无" if not errs else "；".join(c["text"] for c in errs)])
cam_err = sum(1 for _, _, p in progs for c in p.get("checks", []) if c.get("level") == "error")
n_err_review = sum(1 for x in review_rows if x[1] == "error")
procmd = f"""# 工艺路线、AI 工艺评审与数控程序

## 现行工艺路线（工厂数据）

{L.md_table(["零件", "工序", "名称", "设备", "工时 / min"], proc_rows)}

两条路线的骨架都对：小齿轮“车 → 铣键槽 → 滚齿 → 渗碳淬火”，大齿轮“锻坯粗车 → 调质 → 精车 → 铣键槽 → 滚齿”。

## AI 工艺评审员的意见

把这两条路线交给数字工厂的 AI 工艺评审员（“工艺规程与 AI 评审”页同一个函数，规则检查，不调大模型）：

{L.md_table(["零件", "级别", "规则", "工序", "意见"], review_rows) if review_rows else "没有错误和警告。"}

工厂数据里的现行工序只有工序名和工时，没有毛坯、基准、切削参数，评审员按“工艺规程不完整”提意见是对的；正式投产前要在“工艺规程”页把它们补成完整的工艺规程。
另外两点要在工艺上落实：小齿轮渗碳淬火后**孔要磨**（以齿面定位磨孔），否则孔变形、键槽对不上（《制造技术》53.5 节的尺寸链就是这一道）；
大齿轮 40Cr 调质后滚齿，精度 8 级，不用磨齿。

## 齿坯车削的数控程序

由“数控编程”按齿坯外形生成（粗车 + 精车，两次装夹），仿真检查：

{L.md_table(["零件", "程序", "工序", "装夹", "时间", "检查出的错误"], nc_rows)}

孔、键槽、齿形的加工（镗孔、插键槽、滚齿）不在车削程序里：滚齿机和插床按工艺卡调整。
"""
case.step("process", f"两条现行路线 {len(proc_rows)} 道工序；AI 评审 {len(review_rows)} 条意见（{n_err_review} 条错误，都是“工艺规程没写全”）；齿坯车削程序 {len(progs)} 个，仿真无错。",
          f"{len(proc_rows)} operations on the two current routings; the AI reviewer raises {len(review_rows)} points ({n_err_review} errors, all about incomplete process plans); {len(progs)} blank-turning programs, no errors in simulation.",
          md=case.text("6_工艺与评审.md", procmd), files=nc_files, tools=tools("process", "cam"),
          facts=[("工序", "Operations", len(proc_rows), ""), ("评审意见", "Review points", len(review_rows), ""), ("数控程序", "CNC programs", len(progs), "")])
case.check("process", "齿坯数控程序仿真错误", "Errors in blank-turning CNC simulation", cam_err, "==", 0, "", "数控编程仿真")

# ================================================================ 7 制造
from hub import mrp  # noqa: E402

shops = {code: L.run_shop(code, 20, f"WO-CASE-GB-B-{code}", seed=161) for code in ("GR-203", "GR-302")}
mk_rows, cost_rows, good = [], [], 0
for code, sh in shops.items():
    done = [e for e in sh["events"] if e["event"] == "op_complete"]
    last = [e for e in done if e.get("last_op")]
    good += sum(e["qty_good"] for e in last)
    for e in done:
        mk_rows.append([code, e["operation"], e["qty_good"], f"{e['time_s'] / 3600:.1f} h"])
    mc, oc = mrp.std_unit_cost(code)
    cost_rows.append([code, f"${mc:.2f}", f"${oc:.2f}", f"**${mc + oc:.2f}**"])
hob = {code: next(m for o, m in sh["routing"] if "滚齿" in o) for code, sh in shops.items()}
makemd = f"""# 在减速器厂的仿真车间加工 20 对

两张工单（GR-203、GR-302 各 20 件）同时下达，按现行工艺路线从下料走到检验站：

- GR-203 用了 **{shops['GR-203']['hours']:.1f} 小时**，GR-302 用了 **{shops['GR-302']['hours']:.1f} 小时**（含排队、热处理一炉）；
- 每道工序完成的件数和这道工序的累计时间：

{L.md_table(["零件", "工序", "合格件", "这道工序累计"], mk_rows)}

**瓶颈是滚齿**：大齿轮每件 {hob['GR-302']} 分钟、小齿轮 {hob['GR-203']} 分钟，两种齿轮共用一台滚齿机，一对齿轮在滚齿机上占 {hob['GR-302'] + hob['GR-203']} 分钟，比其他任何一道都长。
接大批量订单时先看滚齿机的负荷（“订单与计划”的算料会提示）。

**检验**：检验站按检验模板量公法线长度（GR-203 跨 {k1} 齿 {w1hi:.3f}–{w1lo:.3f}，GR-302 跨 {k2} 齿 {w2hi:.3f}–{w2lo:.3f}）、孔径、齿面硬度。
仿真车间目前只给输出轴 SH-301 出测量值，齿轮的检验结果在“车间终端”录入后才进质量记录——这是仿真车间要补的一块。

**标准成本**（数字工厂成本核算）：

{L.md_table(["零件", "材料", "加工", "合计 / 件"], cost_rows)}
"""
case.step("make", f"20 对齿轮全部完工；GR-302 用 {shops['GR-302']['hours']:.1f} h；瓶颈是滚齿（一对 {hob['GR-302'] + hob['GR-203']} 分钟）。",
          f"All 20 pairs completed; GR-302 took {shops['GR-302']['hours']:.1f} h; gear hobbing is the bottleneck ({hob['GR-302'] + hob['GR-203']} min per pair).",
          md=case.text("7_制造.md", makemd), tools=tools("planner", "operator", "quality", "finance"),
          facts=[("GR-302 加工时间", "GR-302 shop time", shops["GR-302"]["hours"], "h"), ("滚齿每对", "Hobbing per pair", hob["GR-302"] + hob["GR-203"], "min")])
case.check("make", "两张工单完工合格件", "Good parts from both work orders", good, "==", 40, "", "检验站")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

## 校核一览

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

## 这对齿轮定了什么

1. **齿形**：直齿，m3、20/70、不变位——中心距和总传动比不变；斜齿接触强度更高，但要改传动比、多出轴向力。
2. **齿宽**：大齿轮 45（与输出轴的轮毂结构一致）、小齿轮 50；b = 40 接触不够。
3. **关键在齿面**：按节点算接触余量 {(r['SH'] - 1) * 100:.0f}%，沿啮合线到大齿轮单齿区 D 点只剩 {(G.MATERIALS[MAT2]['sHlim'] * r['ZN2'] / sD - 1) * 100:.0f}%；弯曲余量很大。想多留余量，最省事的是大齿轮改**齿面淬火**或改 42CrMo（第 2 步的表里加一行算算）。
4. **工艺**：现行路线要补成完整的工艺规程；小齿轮淬火后磨孔；滚齿是瓶颈。

## 留给学生的问题

1. 在第 2 步的表里加一个方案：大齿轮改 42CrMo 调质 + 齿面感应淬火，S_H 能到多少？代价是什么？
2. 用案例 A 的跑合台转矩记录，按迈因纳法则算大齿轮齿面的累积损伤。
3. 第 4 步的有限元为什么比 ISO 系数法高？把薄片改成 5 个齿、把内圆再往下挪，结果变不变？
4. 滚齿是瓶颈。一对齿轮滚齿 {hob['GR-302'] + hob['GR-203']} 分钟，一个月（22 天、两班）最多能做多少台 WQR-105？

相关：《机械设计》齿轮传动各章，《制造技术》53.5 节（GR-203 孔键槽的尺寸链）、56 章（工艺路线），《机器人学》32.1 节（WQR-105 的传动比与背隙）；案例 A（输出轴）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；直齿 m3 20/70、b = 45/50；关键在大齿轮齿面。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; spur m3 20/70, b = 45/50; the wheel's flank is the critical point.",
          md=case.text("8_总结.md", review), tools=tools("design"))
case.write()
