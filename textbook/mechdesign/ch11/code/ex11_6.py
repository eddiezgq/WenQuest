"""11.7 应变–寿命法与低周疲劳：回形针；WQR-105 输出轴键槽在矿山现场每天的最大转矩下。

材料常数用曼森的通用斜率法（Manson 1965），只要抗拉强度 R_m、弹性模量 E 和断面收缩率 ψ：
  Δε/2 = 1.75 (R_m/E) N^−0.12 + 0.5 D^0.6 N^−0.6，D = ln(1/(1 − ψ))（N 为循环次数），
  对应 σa = 1.75 R_m N^−0.12、εp,a = 0.5 D^0.6 N^−0.6；循环应力应变曲线 εa = σa/E + (σa/K′)^(1/n′)，n′ = 0.12/0.6 = 0.2。
算例 11.7.1  回形针：低碳钢丝 Ø1.0 mm（R_m ≈ 600 MPa、ψ ≈ 50%，本书取值），用手来回弯折，弯曲处中心线的半径 ρ 约 3 mm
            （本书取值）：表面应变幅 εa = (d/2)/ρ，求断前能弯几个来回；ρ 从 2 mm 到 10 mm 时怎样变；
算例 11.7.2  WQR-105 的输出轴外伸段（Ø30，A 版 45 钢调质，R_m 取材料库，ψ = 40% 为 GB/T 699 规定的最小值），端铣键槽：
            扭转的理论应力集中系数 Kts ≈ 3.0（[SHI] 表 7-1 的初估值，r/d = 0.02）。矿山现场一年 365 天（数字孪生的现场模拟器，
            第 7 章；第 10 章 10.7 节用过同一组数），每天起停一次的最大转矩形成 0 → T_day → 0 的循环。名义当量应力 √3·16T/(πd³)，
            键槽根部的局部应力：诺伊伯法则 σ·ε = (Kt·σ_nom)²/E 与循环应力应变曲线（滞回线取 2 倍）求交；
            寿命按 SWT 参数（R = 0 的循环有平均应力）σmax·εa = (σ′f²/E)·N^(2b) + σ′f ε′f·N^(b+c)；迈因纳累加一年的损伤；
            B 版（40Cr 调质，ψ 取 45%）同样算；
图 11.7.1。
"""
import math

import numpy as np
from scipy.optimize import brentq

import _ch11 as H
import _ch7 as C7
from bookout import T, figure, out, style

B_, C_ = -0.12, -0.6


def params(Rm, psi, E):
    Dd = math.log(1 / (1 - psi))
    sf, ef = 1.75 * Rm, 0.5 * Dd ** 0.6
    n_ = B_ / C_
    return {"E": E, "sf": sf, "ef": ef, "n": n_, "K": sf / ef ** n_, "D": Dd}


def life_strain(ea, P):
    """应变幅 → 寿命（循环数）"""
    f = lambda lg: P["sf"] / P["E"] * (10 ** lg) ** B_ + P["ef"] * (10 ** lg) ** C_ - ea   # noqa: E731
    return 10 ** brentq(f, -2, 12)


def life_swt(swt, P):
    f = lambda lg: P["sf"] ** 2 / P["E"] * (10 ** lg) ** (2 * B_) + P["sf"] * P["ef"] * (10 ** lg) ** (B_ + C_) - swt   # noqa: E731
    if f(12) > 0:
        return math.inf
    return 10 ** brentq(f, -2, 12)


def neuber(s_el, P, factor=1.0):
    """诺伊伯：σ·ε = s_el²/E 与 ε = σ/E + factor·(σ/(factor·K′))^(1/n′) 的交点（factor = 2 为滞回线）"""
    g = lambda s: s * (s / P["E"] + factor * (s / (factor * P["K"])) ** (1 / P["n"])) - s_el ** 2 / P["E"]   # noqa: E731
    s = brentq(g, 1e-6, s_el)
    return s, s_el ** 2 / P["E"] / s


# ---------------------------------------------------------------- 算例 11.7.1 回形针
CLIP = params(600.0, 0.50, 207000.0)
d_w, RHO = 1.0, 3.0
ea_clip = d_w / 2 / RHO
N_clip = life_strain(ea_clip, CLIP)
rhos = [2.0, 3.0, 5.0, 10.0]
N_rhos = [life_strain(d_w / 2 / r, CLIP) for r in rhos]
ep_share = CLIP["ef"] * N_clip ** C_ / ea_clip * 100       # 塑性应变占的比例
N_trans = brentq(lambda lg: CLIP["sf"] / CLIP["E"] * (10 ** lg) ** B_ - CLIP["ef"] * (10 ** lg) ** C_, -2, 12)
N_trans = 10 ** N_trans                                      # 弹性、塑性两部分相等的“过渡寿命”

# ---------------------------------------------------------------- 算例 11.7.2 输出轴键槽
DIA, KTS = 30.0, 3.0
Tday = np.array([dd["torque_max_nm"] for dd in C7.site_year("mine")])
c = math.sqrt(3) * 16 / (math.pi * DIA ** 3) * 1e3           # MPa / (N·m)
s_nom = Tday * c


def year(mid, psi):
    m = H.mat(mid)
    P = params(m["ultimate_mpa"], psi, m["E_mpa"])
    D, worst = 0.0, None
    for sn in s_nom:
        s_el = KTS * sn
        smax, emax = neuber(s_el, P)                         # 第一次加载：循环应力应变曲线
        ds, de = neuber(s_el, P, factor=2.0)                 # 卸载：滞回线（应变、应力的变程）
        swt = smax * de / 2
        N = life_swt(swt, P)
        D += 0 if not math.isfinite(N) else 1 / N
        if worst is None or s_el > worst[0]:
            worst = (s_el, smax, emax, ds, de, N)
    return m, P, D, worst


mA, PA, DA, wA = year("45-QT", 0.40)
mB, PB, DB, wB = year("40Cr-QT", 0.45)
n_yield_A = int(np.sum(KTS * s_nom > mA["yield_mpa"]))

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
Ns = np.logspace(0, 7, 300)
for P, col, lab in ((CLIP, "#1f77b4", T("回形针钢丝", "paper-clip wire")), (PA, "#d62728", T("45 钢调质", "1045 Q&T"))):
    a0.loglog(Ns, P["sf"] / P["E"] * Ns ** B_ + P["ef"] * Ns ** C_, color=col, lw=1.3, label=lab)
a0.loglog(Ns, CLIP["sf"] / CLIP["E"] * Ns ** B_, color="#1f77b4", lw=0.7, ls="--")
a0.loglog(Ns, CLIP["ef"] * Ns ** C_, color="#1f77b4", lw=0.7, ls=":")
for r, N in zip(rhos, N_rhos):
    a0.plot([N], [d_w / 2 / r], "o", color="#1f77b4", ms=3.5)
    a0.annotate("ρ = {:.0f}".format(r), (N, d_w / 2 / r), textcoords="offset points", xytext=(5, 2), fontsize=6.0)
a0.set_xlabel(T("循环次数 N", "Cycles N"), fontsize=7.0)
a0.set_ylabel(T("应变幅 εa", "Strain amplitude εa"), fontsize=7.0)
a0.set_ylim(1e-4, 1)
a0.legend(fontsize=6.0, frameon=False, loc="upper right")
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 应变–寿命曲线（虚线弹性、点线塑性部分）", "(a) Strain–life (dashed: elastic, dotted: plastic)"), fontsize=7.0)
s_el, smax, emax = wA[0], wA[1], wA[2]
ss = np.linspace(1, s_el * 1.05, 300)
a1.plot(ss / PA["E"] + (ss / PA["K"]) ** (1 / PA["n"]), ss, color="#d62728", lw=1.3, label=T("循环应力应变曲线", "cyclic stress–strain curve"))
ee = np.linspace(s_el ** 2 / PA["E"] / (s_el * 1.05), 0.012, 300)
a1.plot(ee, s_el ** 2 / PA["E"] / ee, color=H.INK, lw=1.0, ls="--", label=T("诺伊伯双曲线 σε = (Ktσnom)²/E", "Neuber hyperbola σε = (Ktσnom)²/E"))
a1.plot([0, s_el / PA["E"]], [0, s_el], color=H.MUTED, lw=0.8, ls=":", label=T("线弹性（有限元、手册 Kt）", "linear elastic (FE, handbook Kt)"))
a1.plot([emax], [smax], "o", color="#d62728", ms=4)
a1.plot([s_el / PA["E"]], [s_el], "o", color=H.MUTED, ms=4)
a1.set_xlim(0, 0.012)
a1.set_ylim(0, s_el * 1.1)
a1.set_xlabel(T("局部应变 ε", "Local strain ε"), fontsize=7.0)
a1.set_ylabel(T("局部应力 σ / MPa", "Local stress σ / MPa"), fontsize=7.0)
a1.legend(fontsize=5.8, frameon=False, loc="lower right")
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 键槽根部：一年里最大的一天（A 版 45 钢）", "(b) Keyseat root on the year's worst day (A, 1045)"), fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_7_1")

out(d_w=d_w, rho=RHO, ea_clip=ea_clip, N_clip=N_clip, ep_share=ep_share, N_trans_clip=N_trans,
    **{f"N_rho{int(r)}": N for r, N in zip(rhos, N_rhos)},
    clip_K=CLIP["K"], clip_ef=CLIP["ef"], clip_sf=CLIP["sf"],
    dia=DIA, kts=KTS, s_nom_max=float(s_nom.max()), s_nom_mean=float(s_nom.mean()), s_el_max=wA[0],
    syA=mA["yield_mpa"], RmA=mA["ultimate_mpa"], n_yield=n_yield_A,
    smax_A=wA[1], emax_A=wA[2], de_A=wA[4], ds_A=wA[3], N_worst_A=wA[5], D_A=DA, yrs_A=1 / DA if DA > 0 else math.inf,
    KA=PA["K"], sfA=PA["sf"], efA=PA["ef"],
    smax_B=wB[1], N_worst_B=wB[5], D_B=DB, yrs_B=1 / DB if DB > 0 else math.inf)
