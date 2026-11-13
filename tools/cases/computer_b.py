"""第 166b 轮：计算机厂案例 B——2U 双路服务器 WQ-SV2U 的 CPU 散热：散热器（铜底 + 铝鳍片）与风扇组。
手算鳍片效率、平行板通道对流（Teertstra 复合模型）、风道压降、风扇—风道工作点、坏一只风扇；有限元（数字工厂 CAE，CalculiX）算底板扩散热阻，对照 Song–Lee–Au 公式；
问渠整机老化曲线模型（sim/burnin.py）用设计出的热阻跑 12 小时老化；到计算机厂整机线 20 台、老化后量 CPU 满载温度。

    python3 tools/cases/computer_b.py

外购件（CPU、风扇、散热器）写通用名称和示例参数；螺钉从问渠零件库选。输出到 factory/cases/computer/B/。
"""
from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-computer.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
from sim import burnin as BI  # noqa: E402

TOOLS = {
    "cae": ("仿真与分析：热分析", "Simulation: thermal", "/cae"),
    "burnin": ("整机老化曲线", "System burn-in curves", "/burn-in"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间执行", "Shop floor", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "3d": ("3D 车间", "3D shop", "/3d"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("computer", "B", "中等", "2U 服务器的 CPU 散热", "CPU cooling in the 2U server", "WQ-SV2U 散热器与风扇组",
              "两颗 270 W CPU 装在 2U 机箱里、进风 35 ℃、坏一只风扇也不能过 85 ℃：铜底 + 铝鳍片散热器、六只风扇；手算对流、鳍片效率、风道压降和风扇工作点，"
              "扫鳍片数选最少够用的；有限元算底板扩散热阻对照公式；老化曲线模型跑 12 小时；整机线做 20 台，老化后量 CPU 满载温度。",
              "Two 270 W CPUs in a 2U chassis, 35 °C inlet, must stay below 85 °C even with one fan failed: copper-base aluminium-fin heatsinks and six fans; "
              "convection, fin efficiency, duct pressure drop and fan operating point by hand, fin count swept for the fewest that work; FEA of base spreading vs formula; "
              "12-hour burn-in on the curve model; 20 servers built and burned in.",
              "tools/cases/computer_b.py")

SCR = L.lib_part("A-SCR-SHC", "M3x16")
LIBP = [SCR]

# ---------------------------------------------------------------- 任务与条件（示例值）
P_CPU = 270.0               # 每颗 CPU 满载功耗（与老化曲线模型 sv 一致）
T_IN = 35.0                 # 进风温度上限（数据中心 A2 级常用上限）
DT_PRE = 2.0                # 前面硬盘、内存把空气预热
T_LIM = 85.0                # CPU 温度上限（计算机厂整机测试 pc_tmax 上限）
R_JC = 0.023                # CPU 芯片到顶盖的热阻（CPU 规格，示例）
TIM_T, TIM_K = 60e-6, 8.0   # 导热硅脂厚度、导热系数（示例）
A_IHS = 77.5e-3 * 56.5e-3   # CPU 顶盖接触面积
R_TIM2 = TIM_T / (TIM_K * A_IHS)
R_CASE = R_JC + R_TIM2      # 芯片到散热器底面
R_BUDGET = (T_LIM - T_IN - DT_PRE) / P_CPU - R_CASE
MARGIN = 0.97               # 留 3 % 给制造散布
# 空气（约 40 ℃）
RHO, CP, KA, NU, PR = 1.13, 1007.0, 0.0271, 1.70e-5, 0.71
# 散热器：2U 机箱里能放的外形
W, LF, HF, TF, TB, TP = 108e-3, 100e-3, 62e-3, 0.5e-3, 6e-3, 0.5e-3
K_AL, K_CU = 167.0, 391.0   # 鳍片 6061（数字工厂材料库）、底板 C1100 紫铜（ASM Handbook Vol.2 典型值）
# 风扇（60 × 56 mm 双转子，示例曲线 ΔP = P0·(1 − (Q/Qmax)²)）与风道
P0, QMAX, NFAN = 450.0, 0.022, 6
K_SYS = 100.0 / 0.08 ** 2   # 机箱其余部分的阻力：0.08 m³/s 时 100 Pa（示例）
PHI = 0.20                  # 导风罩让每颗 CPU 的散热器分到总风量的 20 %（示例）
CFM = 2118.88


def hs(n, q):
    """n 片鳍片、通过风量 q（m³/s）：间距、风速、对流系数、鳍片效率、鳍片热阻、空气温升热阻、压降"""
    s = (W - n * TF) / (n - 1)
    v = q / ((n - 1) * s * HF)
    re_s = v * s / NU
    res = re_s * s / LF
    nu_b = ((res * PR / 2) ** -3 + (0.664 * math.sqrt(res) * PR ** (1 / 3) * math.sqrt(1 + 3.65 / math.sqrt(res))) ** -3) ** (-1 / 3)
    h = nu_b * KA / s
    m = math.sqrt(2 * h / (K_AL * TF))
    eta = math.tanh(m * HF) / (m * HF)
    area = n * 2 * HF * LF * eta + (n - 1) * s * LF
    r_f = 1 / (h * area)
    r_cal = 1 / (2 * RHO * CP * q)
    dh = 2 * s
    re_d = v * dh / NU
    lp = LF / (dh * re_d)
    f_re = math.sqrt((3.44 / math.sqrt(lp)) ** 2 + 24 ** 2)
    dp = (4 * f_re / re_d * LF / dh + 1.0) * RHO * v ** 2 / 2
    return dict(n=n, s=s, v=v, re=re_s, h=h, m=m, eta=eta, area=area, r_f=r_f, r_cal=r_cal, dp=dp)


A_S, A_P = A_IHS, W * LF


def spread(h_eff, k=K_CU, t=TB):
    """Song–Lee–Au（1994）扩散热阻（平均温度）+ 一维导热；圆形等效"""
    a, b = math.sqrt(A_S / math.pi), math.sqrt(A_P / math.pi)
    e, tau, bi = a / b, t / b, h_eff * b / k
    lc = math.pi + 1 / (math.sqrt(math.pi) * e)
    phi = (math.tanh(lc * tau) + lc / bi) / (1 + lc / bi * math.tanh(lc * tau))
    r_sp = 0.5 * (1 - e) ** 1.5 * phi / (k * a * math.sqrt(math.pi))
    return r_sp, t / (k * A_P) + TP / (k * A_S)


def fan_dp(q, nf):
    return P0 * (1 - (q / nf / QMAX) ** 2)


def operating(n, nf):
    lo, hi = 0.0, nf * QMAX
    for _ in range(80):
        q = (lo + hi) / 2
        lo, hi = (q, hi) if fan_dp(q, nf) > K_SYS * q ** 2 + hs(n, PHI * q)["dp"] else (lo, q)
    return q


def design(n, nf):
    q = operating(n, nf)
    r = hs(n, PHI * q)
    rc = r["r_f"] + r["r_cal"]
    h_eff = 1 / (rc * A_P)
    r_sp, r_1d = spread(h_eff)
    return dict(r, q=q, rc=rc, h_eff=h_eff, r_sp=r_sp, r_1d=r_1d, r_hs=rc + r_sp + r_1d, dp_sys=K_SYS * q ** 2 + r["dp"])


# ================================================================ 1 任务书
brief = f"""# 设计任务书：2U 服务器 CPU 散热

**用在哪**　计算机厂的 2U 双路服务器 WQ-SV2U，16 台装一个整机柜（案例 C）卖给算力中心。两颗 CPU 并排，各 {P_CPU:.0f} W；
2U 机箱高 88.9 mm，散热器只能 {(HF + TB + TP) * 1000:.0f} mm 高；机房按 A2 级进风，最高 {T_IN:.0f} ℃。

| 项目 | 要求 | 出处 |
|---|---|---|
| CPU 功耗 | {P_CPU:.0f} W × 2（满载） | CPU 规格（示例），和老化曲线模型一致 |
| 进风温度 | ≤ {T_IN:.0f} ℃（前面硬盘、内存再预热约 {DT_PRE:g} ℃） | 数据中心 A2 级 |
| CPU 温度 | ≤ {T_LIM:.0f} ℃ | 计算机厂整机测试 pc_tmax 上限 |
| 风扇冗余 | 坏一只风扇（6 → 5）仍满足 | 服务器常规（N+1） |
| 散热器外形 | {W * 1000:.0f} × {LF * 1000:.0f} mm、高 {(HF + TB + TP) * 1000:.0f} mm | 2U 机箱、内存插槽之间 |
| 风扇 | 6 只 60 mm 高速风扇，机箱前部一排 | 机箱设计 |

CPU、风扇、散热器外购（通用名称、示例参数）；固定螺钉从问渠零件库选。
"""
case.step("brief", f"两颗 {P_CPU:.0f} W CPU、进风 {T_IN:.0f} ℃、坏一只风扇仍 ≤ {T_LIM:.0f} ℃；散热器 {W * 1000:.0f} × {LF * 1000:.0f} × {(HF + TB + TP) * 1000:.0f} mm。",
          f"Two {P_CPU:.0f} W CPUs, {T_IN:.0f} °C inlet, ≤ {T_LIM:.0f} °C even with one fan failed; heatsink {W * 1000:.0f} × {LF * 1000:.0f} × {(HF + TB + TP) * 1000:.0f} mm.",
          md=case.text("1_任务书.md", brief),
          facts=[("CPU 功耗", "CPU power", P_CPU, "W"), ("进风", "Inlet", T_IN, "℃"), ("温度上限", "Limit", T_LIM, "℃")])

# ================================================================ 2 方案
al = design(44, 5)
r_sp_al, r_1d_al = spread(al["h_eff"], k=K_AL)
r_al = al["rc"] + r_sp_al + r_1d_al
concept = f"""# 方案：散热器底板、鳍片、风扇

## 热量的路：芯片 → 顶盖 → 硅脂 → 散热器底板 → 鳍片 → 空气

总热阻预算：({T_LIM:.0f} − {T_IN:.0f} − {DT_PRE:g}) / {P_CPU:.0f} = {(T_LIM - T_IN - DT_PRE) / P_CPU:.4f} K/W；
减去芯片到顶盖 {R_JC:g} K/W（CPU 规格）和硅脂层 {R_TIM2:.4f} K/W，**散热器（底面到进风）≤ {R_BUDGET:.4f} K/W**，坏一只风扇时也要满足。

## 方案比较（44 片鳍片、5 只风扇时）

| 方案 | 散热器热阻 | 说明 | |
|---|---|---|---|
| 全铝挤压（底板 6061） | {r_al:.4f} K/W | 底板导热差，热量从 CPU 中间散不开（扩散热阻 {r_sp_al:.4f}） | ✗ |
| **紫铜底板 + 铝鳍片（钎焊）** | {al['r_hs']:.4f} K/W | 铜导热是铝的 2.3 倍，扩散热阻 {al['r_sp']:.4f} | ✓ |
| 均温板 + 热管 | 更低 | 贵一倍多；350 W 以上的 CPU 再用 | 留给下一代 |

鳍片做薄（{TF * 1000:g} mm）、做高（{HF * 1000:.0f} mm，2U 能放的最高），片数下一步算。风扇六只一排，导风罩把每颗 CPU 的风道隔开（分到总风量的 {PHI * 100:.0f} %）。
"""
case.step("concept", f"散热器热阻预算 ≤ {R_BUDGET:.4f} K/W；选紫铜底板 + 铝鳍片（全铝 {r_al:.3f}，铜底 {al['r_hs']:.3f} K/W）。",
          f"Heatsink budget ≤ {R_BUDGET:.4f} K/W; copper base + aluminium fins chosen (all-aluminium {r_al:.3f}, copper base {al['r_hs']:.3f} K/W).",
          md=case.text("2_方案.md", concept), facts=[("热阻预算", "Budget", round(R_BUDGET, 4), "K/W")])

# ================================================================ 3 计算
NS = list(range(30, 80, 2))
sweep = {n: (design(n, 6), design(n, 5)) for n in NS}
n_sel = min(n for n in NS if sweep[n][1]["r_hs"] <= R_BUDGET * MARGIN)
d6, d5 = sweep[n_sel]
n_best = min(NS, key=lambda n: sweep[n][1]["r_hs"])
T6 = T_IN + DT_PRE + P_CPU * (R_CASE + d6["r_hs"])
T5 = T_IN + DT_PRE + P_CPU * (R_CASE + d5["r_hs"])
p_srv = 2 * P_CPU + 105 + 60       # 两颗 CPU + 其余部件 + 风扇（满转，与老化曲线模型 sv 一致）
dT_srv = p_srv / (RHO * CP * d6["q"])
calc = f"""# 计算书 Calculation

## 1 鳍片通道对流 Channel convection（{n_sel} 片，6 只风扇）

| 量 Quantity | 公式 Formula | 结果 Result |
|---|---|---|
| 鳍片间距 s | (W − n·t)/(n − 1) | {d6['s'] * 1000:.2f} mm |
| 通道风速 V | Q_hs / ((n − 1)·s·H) | {d6['v']:.2f} m/s |
| 雷诺数 Re_s | V·s/ν | {d6['re']:.0f}（层流） |
| 对流系数 h | Teertstra 复合模型：Nu_b = [(Re*·Pr/2)⁻³ + (0.664·√Re*·Pr^⅓·√(1 + 3.65/√Re*))⁻³]^(−⅓)，Re* = Re_s·s/L | {d6['h']:.1f} W/(m²·K) |
| 鳍片效率 η | tanh(mH)/(mH)，m = √(2h/(k·t)) | {d6['eta']:.2f} |
| 鳍片热阻 | 1/(h·(2n·H·L·η + 底面露出面积)) | {d6['r_f']:.4f} K/W |
| 空气温升热阻 | 1/(2·ρ·c_p·Q_hs) | {d6['r_cal']:.4f} K/W |
| 底板扩散热阻 | Song–Lee–Au（顶盖 {A_S * 1e6:.0f} mm² → 底板 {A_P * 1e6:.0f} mm²） | {d6['r_sp']:.4f} K/W |
| 底板一维导热 | t/(k·A) | {d6['r_1d']:.4f} K/W |
| **散热器热阻** | 合计 | **{d6['r_hs']:.4f} K/W** |

## 2 风扇与风道的工作点 Fan operating point

风扇曲线 ΔP = {P0:.0f}·(1 − (Q/{QMAX}·n_f)²) Pa；风道 = 机箱其余 {K_SYS:.0f}·Q² + 散热器压降（发展段层流 f·Re，Muzychka–Yovanovich，加进出口 K = 1）。

| | 总风量 | 每颗 CPU 散热器 | 风道压降 | 散热器热阻 | CPU 温度（进风 {T_IN:.0f} ℃） |
|---|---|---|---|---|---|
| 6 只风扇 | {d6['q'] * CFM:.0f} CFM | {PHI * d6['q'] * CFM:.0f} CFM | {d6['dp_sys']:.0f} Pa | {d6['r_hs']:.4f} K/W | **{T6:.1f} ℃** |
| 坏一只（5 只） | {d5['q'] * CFM:.0f} CFM | {PHI * d5['q'] * CFM:.0f} CFM | {d5['dp_sys']:.0f} Pa | {d5['r_hs']:.4f} K/W | **{T5:.1f} ℃** |

## 3 鳍片数怎么定

片数多：面积大，但间距小、风阻大、风量下降，空气温升变大——有一个最优（5 只风扇时约 {n_best} 片、{sweep[n_best][1]['r_hs']:.4f} K/W）。
**取满足“坏一只风扇 ≤ 预算 × {MARGIN:g}”的最少片数：{n_sel} 片**（间距 {d6['s'] * 1000:.2f} mm，不容易积灰，成本低）。

## 4 整机 Server

满载整机约 {p_srv:.0f} W，全部风量 {d6['q'] * CFM:.0f} CFM，出风比进风高 {dT_srv:.1f} ℃（ΔT = P/(ρ·c_p·Q)）；案例 C 的机柜换热按这个算。
"""
case.step("calc", f"{n_sel} 片鳍片：散热器 {d6['r_hs']:.4f} K/W；进风 {T_IN:.0f} ℃ 时 CPU {T6:.1f} ℃，坏一只风扇 {T5:.1f} ℃。",
          f"{n_sel} fins: heatsink {d6['r_hs']:.4f} K/W; CPU {T6:.1f} °C at {T_IN:.0f} °C inlet, {T5:.1f} °C with one fan failed.",
          md=case.text("3_计算书.md", calc),
          facts=[("鳍片", "Fins", n_sel, ""), ("散热器热阻", "Heatsink R", round(d6["r_hs"], 4), "K/W"), ("CPU（坏一只风扇）", "CPU (one fan out)", round(T5, 1), "℃"),
                 ("总风量", "Airflow", round(d6["q"] * CFM), "CFM")])
case.check("calc", "CPU 温度（6 只风扇、进风 35 ℃）", "CPU temperature (6 fans, 35 °C inlet)", round(T6, 1), "<=", T_LIM, "℃", "任务书")
case.check("calc", "CPU 温度（坏一只风扇）", "CPU temperature (one fan failed)", round(T5, 1), "<=", T_LIM, "℃", "任务书 N+1")

fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.4))
axs[0].plot(NS, [sweep[n][0]["r_hs"] for n in NS], "o-", ms=3, color=L.ACCENT, label="6 只风扇")
axs[0].plot(NS, [sweep[n][1]["r_hs"] for n in NS], "s-", ms=3, color=L.MUTED, label="5 只（坏一只）")
axs[0].axhline(R_BUDGET, color=L.BAD, ls="--", lw=0.8)
axs[0].text(NS[0], R_BUDGET + 0.002, f"预算 {R_BUDGET:.4f}", fontsize=8, color=L.BAD)
axs[0].axvline(n_sel, color=L.OK, ls=":", lw=1)
axs[0].set_xlabel("鳍片数")
axs[0].set_ylabel("散热器热阻 / K/W")
axs[0].set_title(f"选 {n_sel} 片：满足要求里最少的", fontsize=9.5)
axs[0].legend(fontsize=8, frameon=False)
q = np.linspace(0, NFAN * QMAX, 200)
for nf, st_ in ((6, "-"), (5, "--")):
    axs[1].plot(q * CFM, [fan_dp(x, nf) for x in q], st_, color=L.ACCENT, lw=1.2, label=f"{nf} 只风扇")
axs[1].plot(q * CFM, [K_SYS * x ** 2 + hs(n_sel, PHI * x)["dp"] if x > 0.002 else K_SYS * x ** 2 for x in q], color=L.INK, lw=1.2, label="风道阻力")
for dd in (d6, d5):
    axs[1].plot(dd["q"] * CFM, dd["dp_sys"], "o", color=L.BAD, ms=5)
axs[1].set_ylim(0, P0 * 1.05)
axs[1].set_xlabel("总风量 / CFM")
axs[1].set_ylabel("压力 / Pa")
axs[1].set_title("风扇—风道工作点", fontsize=9.5)
axs[1].legend(fontsize=8, frameon=False)
case.fig(fig, "3_鳍片数与工作点.png")
case.steps["calc"]["figs"].append(dict(file="3_鳍片数与工作点.png", caption="鳍片数扫描、风扇—风道工作点", caption_en="Fin-count sweep and fan operating point"))

# ================================================================ 4 仿真：有限元扩散 + 老化曲线
import build123d as bd  # noqa: E402
from cae import geometry as GE, materials as MA, thermal as TH  # noqa: E402

A0 = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
base_fea = bd.Box(77.5, 56.5, TP * 1000, align=A0) + bd.Pos(0, 0, TP * 1000) * bd.Box(W * 1000, LF * 1000, TB * 1000, align=A0)
bd.export_step(base_fea, str(case.path("_base.step")))
step_bytes = case.path("_base.step").read_bytes()
os.remove(case.path("_base.step"))
faces, _, _ = GE.faces(step_bytes)
f_src = [f["id"] for f in faces if f["kind"] == "plane" and abs(f["center"][2]) < 1e-6]
f_top = [f["id"] for f in faces if f["kind"] == "plane" and abs(f["center"][2] - (TP + TB) * 1000) < 1e-6]
T_AIR = T_IN + DT_PRE
cu = dict(MA.get("6061-T6"), id="C1100", name="C1100 紫铜", k_w_mk=K_CU, c_j_kgk=385.0, density_t_mm3=8.94e-9)


def fea(mat, k):
    setup = {"analysis": "thermal", "material": mat,
             "thermal": [{"type": "heat_flux", "faces": f_src, "power_w": P_CPU}, {"type": "convection", "faces": f_top, "h_w_m2k": d6["h_eff"], "t_inf_c": T_AIR}],
             "mesh": {"size_mm": 3.0}}
    st, surf, _ = TH.solve(step_bytes, setup)
    pos, tri, fo, tt = (np.asarray(surf[x]) for x in ("positions", "triangles", "face_of_triangle", "temp"))
    sel = np.isin(fo, f_src)
    a = np.linalg.norm(np.cross(pos[tri[sel, 1]] - pos[tri[sel, 0]], pos[tri[sel, 2]] - pos[tri[sel, 0]]), axis=1) / 2
    t_src = float((tt[tri[sel]].mean(axis=1) * a).sum() / a.sum())
    r_sp, r_1d = spread(d6["h_eff"], k=k)
    t_hand = T_AIR + P_CPU * (d6["rc"] + r_sp + r_1d)
    return dict(st=st, t_src=t_src, t_hand=t_hand, r_fea=(t_src - T_AIR) / P_CPU - d6["rc"], r_hand=r_sp + r_1d, surf=surf)


fe_cu = fea(cu, K_CU)
fe_al = fea(MA.get("6061-T6"), K_AL)
d_fea = abs(fe_cu["t_src"] - fe_cu["t_hand"])

# 老化曲线模型：用设计出的散热器热阻跑 12 小时
R_PLANT = BI.KINDS["sv"]["r_hs"]


def burn(amb, r_hs):
    p = BI.params(random.Random(1662), "CASE-B", "sv")
    p.update(amb=amb, tim=[round(R_CASE, 5)] * 2, hs=[round(r_hs, 5)] * 2, pl=[P_CPU] * 2)
    return BI.generate(p)


g35 = burn(T_AIR, d6["r_hs"])
g25 = burn(25.0, d6["r_hs"])
fig, axs = plt.subplots(1, 3, figsize=(11.6, 3.2), gridspec_kw={"width_ratios": [1.1, 1.3, 1.3]})
surf = fe_cu["surf"]
pos, tri, tt = (np.asarray(surf[x]) for x in ("positions", "triangles", "temp"))
bot = np.isin(np.asarray(surf["face_of_triangle"]), f_top)
tc = axs[0].tripcolor(pos[:, 0], pos[:, 1], tri[bot], tt, cmap="inferno", shading="gouraud")
axs[0].add_patch(plt.Rectangle((-38.75, -28.25), 77.5, 56.5, fill=False, ec="w", ls="--", lw=0.8))
axs[0].set_aspect("equal")
axs[0].set_title("铜底板顶面温度（虚线：CPU 顶盖位置）", fontsize=9)
axs[0].set_xlabel("mm")
fig.colorbar(tc, ax=axs[0], shrink=0.8, label="℃")
mins = np.arange(g35["minutes"])
axs[1].plot(mins / 60, g35["temp"][0], color=L.BAD, lw=0.8, label=f"进风 {T_AIR:.0f} ℃")
axs[1].plot(mins / 60, g25["temp"][0], color=L.ACCENT, lw=0.8, label="进风 25 ℃")
axs[1].axhline(T_LIM, color=L.BAD, ls="--", lw=0.8)
axs[1].set_xlabel("老化时间 / h")
axs[1].set_ylabel("CPU 温度 / ℃")
axs[1].set_title("老化曲线模型（满载 50 分钟、空闲 10 分钟）", fontsize=9)
axs[1].legend(fontsize=8, frameon=False, loc="lower center", ncol=2)
axs[2].plot(mins / 60, np.array(g35["fan"]), color=L.BAD, lw=0.8, label=f"进风 {T_AIR:.0f} ℃")
axs[2].plot(mins / 60, np.array(g25["fan"]), color=L.ACCENT, lw=0.8, label="进风 25 ℃")
axs[2].set_xlabel("老化时间 / h")
axs[2].set_ylabel("风扇转速 / r/min")
axs[2].set_title("风扇按温度调速", fontsize=9)
fig.subplots_adjust(wspace=0.42)
case.fig(fig, "4_有限元与老化.png")
simmd = f"""# 仿真：有限元扩散热阻 + 老化曲线

## 1 底板扩散（数字工厂“仿真与分析”热分析，CalculiX）

紫铜底板 {W * 1000:.0f} × {LF * 1000:.0f} × {TB * 1000:g} mm + {TP * 1000:g} mm 凸台；{P_CPU:.0f} W 从凸台底面（CPU 顶盖大小）进，
顶面按鳍片的等效对流 h = {d6['h_eff']:.0f} W/(m²·K)（第 3 步 1/(R_鳍片 + R_空气)·A）向 {T_AIR:.0f} ℃ 散热。

| | 有限元 | 公式（Song–Lee–Au + 一维） | 相差 |
|---|---|---|---|
| 紫铜：CPU 接触面平均温度 | {fe_cu['t_src']:.1f} ℃ | {fe_cu['t_hand']:.1f} ℃ | {abs(fe_cu['t_src'] - fe_cu['t_hand']):.1f} K |
| 紫铜：扩散 + 导热热阻 | {fe_cu['r_fea']:.4f} K/W | {fe_cu['r_hand']:.4f} K/W | |
| 6061 铝：CPU 接触面平均温度 | {fe_al['t_src']:.1f} ℃ | {fe_al['t_hand']:.1f} ℃ | {abs(fe_al['t_src'] - fe_al['t_hand']):.1f} K |

铝底板比铜底板热 {fe_al['t_src'] - fe_cu['t_src']:.1f} ℃——方案里选铜底板的理由由有限元确认。
（等效对流把鳍片“抹平”在顶面上，鳍片根部的温度不均没算；网格 {fe_cu['st']['elements']} 个单元。）

## 2 老化曲线（`sim/burnin.py`，和计算机厂老化房同一个模型）

把设计出的热阻（芯片到底面 {R_CASE:.4f}、散热器 {d6['r_hs']:.4f} K/W）放进 2U 服务器的老化曲线模型，满载 50 分钟、空闲 10 分钟跑 12 小时，风扇按温度调速：

| 进风 | CPU 满载最高 | 平均功耗 |
|---|---|---|
| {T_AIR:.0f} ℃（任务书最坏） | **{g35['tmax']:.1f} ℃** | {g35['pavg']:.0f} W |
| 25 ℃（工厂老化房） | {g25['tmax']:.1f} ℃ | {g25['pavg']:.0f} W |

工厂老化曲线模型里服务器散热器热阻取 {R_PLANT:g} K/W，设计结果 {d6['r_hs']:.4f}，相差 {abs(d6['r_hs'] / R_PLANT - 1) * 100:.1f} %（模型略保守，不改）。
"""
case.step("sim", f"有限元与公式：CPU 接触面温度相差 {d_fea:.1f} K；铝底板比铜热 {fe_al['t_src'] - fe_cu['t_src']:.1f} ℃。老化曲线：进风 {T_AIR:.0f} ℃ 满载最高 {g35['tmax']:.1f} ℃。",
          f"FEA vs formula: {d_fea:.1f} K at the CPU contact; aluminium base {fe_al['t_src'] - fe_cu['t_src']:.1f} °C hotter than copper. Burn-in model: {g35['tmax']:.1f} °C peak at {T_AIR:.0f} °C inlet.",
          md=case.text("4_有限元与老化.md", simmd), figs=[("4_有限元与老化.png", "铜底板温度场、老化曲线、风扇转速", "Copper base temperature, burn-in curves, fan speed")],
          tools=tools("cae", "burnin"),
          facts=[("有限元与公式相差", "FEA vs formula", round(d_fea, 1), "K"), ("老化最高温度", "Burn-in peak", round(g35["tmax"], 1), "℃")])
case.check("sim", "有限元与公式：CPU 接触面温度相差", "FEA vs formula at the CPU contact", round(d_fea, 1), "<=", 2.0, "K", "核对公式")
case.check("sim", f"老化曲线：进风 {T_AIR:.0f} ℃ 满载最高温度", f"Burn-in model peak at {T_AIR:.0f} °C inlet", round(g35["tmax"], 1), "<=", T_LIM, "℃", "任务书")
case.check("sim", "设计热阻与工厂老化模型相差", "Design R vs plant burn-in model", round(abs(d6["r_hs"] / R_PLANT - 1) * 100, 1), "<=", 5.0, "%", "细则规则 2")

# ================================================================ 5 三维与图纸
n = n_sel
pitch = (W * 1000 - TF * 1000) / (n - 1)
sink = bd.Box(77.5, 56.5, TP * 1000, align=A0) + bd.Pos(0, 0, TP * 1000) * bd.Box(W * 1000, LF * 1000, TB * 1000, align=A0)
for i in range(n):
    x = -W * 500 + TF * 500 + i * pitch
    sink = sink + bd.Pos(x, 0, (TP + TB) * 1000) * bd.Box(TF * 1000, LF * 1000, HF * 1000, align=A0)
for sx in (-1, 1):
    for sy in (-1, 1):
        sink = sink - bd.Pos(sx * 45.0, sy * 41.0, 0) * bd.Cylinder(1.7, (TP + TB) * 1000 + 1, align=A0)
bd.export_step(sink, str(case.path("5_散热器.step")))
L.render_solid(sink, case.path("5_散热器三维.png"), elev=28, azim=-55, color=(0.80, 0.70, 0.55), size=(7, 5), swap=False)

fig, ax = plt.subplots(figsize=(8.2, 5.0))
ax.add_patch(plt.Rectangle((0, 0), 440, 680, fc="#f4f6f8", ec=L.INK, lw=1))
for i in range(6):
    ax.add_patch(plt.Rectangle((20 + i * 68, 560), 60, 56, fc="#c9d6e4", ec=L.INK, lw=0.6))
    ax.text(50 + i * 68, 588, f"风扇{i + 1}", ha="center", va="center", fontsize=7)
for i in range(12):
    ax.add_patch(plt.Rectangle((15 + i * 35, 630), 30, 45, fc="#e2e2e2", ec=L.MUTED, lw=0.5))
ax.text(220, 676, "前部：12 盘位（用 4 块）", ha="center", va="bottom", fontsize=7.5)
for cx in (120, 320):
    ax.add_patch(plt.Rectangle((cx - 54, 330), 108, 100, fc="#e8c9a0", ec=L.INK, lw=0.8))
    ax.text(cx, 380, f"CPU\n散热器\n{n_sel} 片", ha="center", va="center", fontsize=8)
    for j in range(4):
        for side in (-1, 1):
            ax.add_patch(plt.Rectangle((cx + side * 62 + (0 if side > 0 else -8) + side * j * 10, 300), 6, 160, fc="#9fb3c8", ec="none"))
ax.add_patch(plt.Rectangle((10, 20), 120, 200, fc="#d9e4d9", ec=L.INK, lw=0.6))
ax.text(70, 120, "主板 I/O\n扩展卡", ha="center", va="center", fontsize=7.5)
for i in range(2):
    ax.add_patch(plt.Rectangle((340, 20 + i * 90), 90, 80, fc="#e9d4d4", ec=L.INK, lw=0.6))
    ax.text(385, 60 + i * 90, f"电源{i + 1}", ha="center", va="center", fontsize=7.5)
for x in (60, 220, 380):
    ax.annotate("", xy=(x, 250), xytext=(x, 550), arrowprops=dict(arrowstyle="->", color=L.ACCENT, lw=1.2))
ax.text(222, 500, "风向", color=L.ACCENT, fontsize=8)
ax.text(220, 290, "内存 16 条（每颗 CPU 两边各 4 条）", ha="center", fontsize=7.5, color=L.MUTED)
ax.set_xlim(-10, 450)
ax.set_ylim(0, 700)
ax.set_aspect("equal")
ax.set_xlabel("mm（示意）")
ax.set_title("WQ-SV2U 俯视布置（前 → 后）", fontsize=10)
case.fig(fig, "5_服务器布置.png")
cadmd = f"""# 三维与图纸

![散热器](5_散热器三维.png)

**散热器 HS-SV**：紫铜底板 {W * 1000:.0f} × {LF * 1000:.0f} × {TB * 1000:g} mm + {TP * 1000:g} mm 凸台；6061 铝鳍片 {n_sel} 片 × {TF * 1000:g} mm、高 {HF * 1000:.0f} mm、
间距 {pitch:.2f} mm（钎焊在底板上）；四角 Ø3.4 孔，弹簧螺钉固定。三维模型 `5_散热器.step`。

![布置](5_服务器布置.png)

整机布置：前面硬盘 → 一排 6 只风扇 → 两颗 CPU 并排（导风罩隔开，每颗 {PHI * 100:.0f} % 风量）、两边内存 → 后面电源、I/O。两颗 CPU **并排**而不是一前一后，后面那颗就不吃前面那颗的热风。

## 用到的问渠零件库零件

{L.lib_md(LIBP, {SCR['ref']: "散热器弹簧螺钉的螺钉（每颗 CPU 4 只，对角顺序拧紧）"})}

外购件（示例参数，型号待确认）：散热器 HS-SV ×2（按上面图纸外协钎焊）、60 mm 高速风扇 FAN-SV ×6、导热硅脂。
"""
case.step("cad", f"散热器：铜底 + {n_sel} 片铝鳍片、间距 {pitch:.2f} mm；整机：风扇一排在前，两颗 CPU 并排、导风罩隔开。",
          f"Heatsink: copper base + {n_sel} aluminium fins at {pitch:.2f} mm pitch; server: fans in one row, two CPUs side by side with ducting.",
          md=case.text("5_三维与图纸.md", cadmd), figs=[("5_散热器三维.png", "散热器三维", "Heatsink 3D"), ("5_服务器布置.png", "服务器俯视布置", "Server top-view layout")],
          files=[("5_散热器.step", "散热器三维模型（STEP）", "Heatsink 3D model (STEP)")], tools=L.lib_tools(LIBP) + tools("cae"))

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WQ-SV2U"][0]]
tim_g = A_IHS * TIM_T * 1e6 * 2.6
procmd = f"""# 工艺：计算机厂整机线

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

和散热有关的：

- **涂导热硅脂**（点胶机）：每颗 CPU 硅脂层 {TIM_T * 1e6:.0f} μm × {A_IHS * 1e6:.0f} mm² ≈ {tim_g:.2f} g，按五点 + 中间一点的图形点 {tim_g * 1.5:.1f} g（压开后多的挤到边上）；
  每班开工称重一次——点胶量少，硅脂层热阻就大（计算机厂“点胶机针头半堵”问题就是这个）；
- **服务器装配**：散热器四只弹簧螺钉**对角顺序**分两遍拧到底，保证压力均匀；风扇插头、导风罩装好再合盖；
- **老化**：12 小时满载，老化曲线算出 CPU 满载温度（上限 {T_LIM:.0f} ℃）——就是第 4 步那个模型；
- **整机功能测试**：读老化结果、风扇转速、坏一只风扇报警功能。
"""
case.step("process", f"整机线 {len(rt)} 道：每颗 CPU 点硅脂约 {tim_g * 1.5:.1f} g、每班称重；散热器螺钉对角两遍；12 小时老化。",
          f"{len(rt)} operations: about {tim_g * 1.5:.1f} g paste per CPU, weighed every shift; heatsink screws diagonally in two passes; 12-hour burn-in.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer", "burnin"), facts=[("工序", "Operations", len(rt), ""), ("硅脂", "Paste", round(tim_g * 1.5, 1), "g")])

# ================================================================ 7 制造
sh = L.run_shop("WQ-SV2U", 20, "WO-CASE-PC-B", seed=1662)
meas = sh["measurements"]
rows_q, cpk_min, fails, st = L.shop_table(meas)
tst = st["pc_tmax"]
makemd = f"""# 制造：20 台服务器

计算机厂仿真车间整机线做 20 台 WQ-SV2U（{sh['hours']:.1f} 小时，老化房一次放多台），整机功能测试记：

{L.md_table(["特性", "公差", "台数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}**，最低 Cpk {cpk_min:.2f}。CPU 满载温度平均 {tst['mean']:.1f} ℃（老化房进风约 25 ℃），第 4 步模型算 {g25['tmax']:.1f} ℃；
到进风 {T_AIR:.0f} ℃ 的机房还有 {T_LIM - g35['tmax']:.1f} ℃ 余量。
"""
case.step("make", f"20 台：CPU 满载温度平均 {tst['mean']:.1f} ℃，不合格 {fails}，最低 Cpk {cpk_min:.2f}。",
          f"20 servers: average full-load CPU temperature {tst['mean']:.1f} °C; {fails} failures, lowest Cpk {cpk_min:.2f}.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "burnin"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), "")])
case.check("make", "不合格项", "Failures", fails, "==", 0, "", "整机功能测试")
case.check("make", "最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **散热是一串热阻**：芯片、硅脂、底板扩散、鳍片、空气温升，每一段都要算；最容易忽略的是**扩散**（铝底板多 {fe_al['t_src'] - fe_cu['t_src']:.0f} ℃）。
2. **鳍片不是越多越好**：风扇和风道一起决定风量，片数有最优；按“坏一只风扇也够”取最少片数，间距大、不积灰。
3. **设计和工厂用同一个模型**：老化曲线模型里的热阻就是这个散热器的设计值；老化房里 CPU 偏热，先查硅脂（点胶量），不是先加风扇。

## 留给学生的问题

1. CPU 换成 350 W：这个散热器还够不够？要改什么（提示：均温板、风扇曲线）？
2. 进风 35 ℃ 改成 40 ℃（A3 级）：坏一只风扇还行吗？
3. 两颗 CPU 一前一后摆放，后面那颗多热几度？用第 3 步的整机温升公式估一下。

相关：计算机厂帮助“整机老化与老化曲线”；案例 A（主板供电）、案例 C（算力中心的机柜换热按第 3 步的整机温升）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；{n_sel} 片鳍片、{d6['r_hs']:.3f} K/W、坏一只风扇 {T5:.1f} ℃。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; {n_sel} fins, {d6['r_hs']:.3f} K/W, {T5:.1f} °C with one fan failed.",
          md=case.text("8_总结.md", review), tools=tools("burnin", "quality"))
case.write()
print("ok", n_sel, round(d6["r_hs"], 4), round(d5["r_hs"], 4), round(T6, 1), round(T5, 1), fe_cu["t_src"], fe_cu["t_hand"], fe_al["t_src"], g35["tmax"], g25["tmax"], cpk_min)
