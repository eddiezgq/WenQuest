"""9.5 压杆稳定：欧拉公式与经验公式。

算例 9.5.1  桁架机器人推送轴的直线模组：滚珠丝杠 SFU1605（零件库：公称直径 16、导程 5、钢球 Ø3.175），伺服电机 400 W
            （额定 1.27 N·m、最大 3.82 N·m，本书设定的常见规格），丝杠传动效率 0.9（第 7 章）。电机最大转矩时的推力
            F = 2πTη/P_h。丝杠受压时，按四种支承方式（长度系数 μ = 2、1、0.7、0.5）求临界载荷随无支承长度的变化，
            柔度小于分界值时改用约翰逊抛物线；求安全系数 2 时的最大无支承长度；
算例 9.5.2  同样“固定–铰支”时，SFU1605、2005、2505 的最大无支承长度；
图 9.5.1。丝杠的小径按“公称直径 − 钢球直径”近似（本书取值），材料按 45 钢调质（E、σs 取材料库）。
"""
import math

import numpy as np

import _ch9 as H
from bookout import T, figure, out, style

ST = H.mat("45-QT")
E, SY = ST["E"], ST["sy"]
SFU = H.lib_rows("A-BSC-SFU")
T_RATED, T_MAX, ETA = 1.27, 3.82, 0.9
S_REQ = 2.0
SUP = [(2.0, T("固定–自由", "fixed–free")), (1.0, T("两端铰支", "pinned–pinned")),
       (0.7, T("固定–铰支", "fixed–pinned")), (0.5, T("固定–固定", "fixed–fixed"))]
COL = ["#d62728", "#ff7f0e", "#1f77b4", "#2ca02c"]


def screw(size):
    r = SFU[size]
    d0, Ph, Dw = float(r["d0_mm"]), float(r["Ph_mm"]), float(r["Dw_mm"])
    dr = d0 - Dw
    return {"d0": d0, "Ph": Ph, "Dw": Dw, "dr": dr, "A": math.pi * dr ** 2 / 4, "I": math.pi * dr ** 4 / 64, "Ca": float(r["Ca_N"])}


s16 = screw("16x5")
F_max = 2 * math.pi * T_MAX * 1e3 * ETA / s16["Ph"]
F_rated = 2 * math.pi * T_RATED * 1e3 * ETA / s16["Ph"]


def L_allow(sc, mu, F, S=S_REQ):
    """临界载荷 = S·F 时的无支承长度（二分法，含约翰逊段）"""
    lo, hi = 10.0, 20000.0
    for _ in range(80):
        mid = (lo + hi) / 2
        P = H.column_cr(E, SY, sc["A"], sc["I"], mid, mu)[0]
        lo, hi = (mid, hi) if P > S * F else (lo, mid)
    return lo


Ls = np.linspace(100, 2000, 400)
lam_c = math.pi * math.sqrt(2 * E / SY)
i16 = math.sqrt(s16["I"] / s16["A"])
L_allow16 = {mu: L_allow(s16, mu, F_max) for mu, _ in SUP}
L_sizes = {sz: L_allow(screw(sz), 0.7, F_max) for sz in ("16x5", "20x5", "25x5")}
# 短杆：固定–铰支、L = 200 时欧拉公式高估多少
P_e200 = H.euler(E, s16["I"], 200, 0.7)
P_j200, lam200, _, kind200 = H.column_cr(E, SY, s16["A"], s16["I"], 200, 0.7)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.3, 1.0]})
for (mu, nm), c in zip(SUP, COL):
    P = [H.column_cr(E, SY, s16["A"], s16["I"], L, mu)[0] / 1e3 for L in Ls]
    Pe = [H.euler(E, s16["I"], L, mu) / 1e3 for L in Ls]
    a0.plot(Ls, P, color=c, lw=1.4, label=nm + T(f"（μ = {mu:g}）", f" (μ = {mu:g})"))
    a0.plot(Ls, Pe, color=c, lw=0.7, ls=":")
a0.axhline(S_REQ * F_max / 1e3, color=H.INK, lw=0.8, ls="--")
a0.text(1990, S_REQ * F_max / 1e3 + 1.2, T(f"2 × 最大推力 = {S_REQ * F_max / 1e3:.1f} kN", f"2 × max thrust = {S_REQ * F_max / 1e3:.1f} kN"),
        fontsize=6.2, ha="right")
a0.set_yscale("log")
a0.set_ylim(1, 300)
a0.set_xlabel(T("无支承长度 L / mm", "Unsupported length L / mm"), fontsize=7.2)
a0.set_ylabel(T("临界载荷 / kN", "Critical load / kN"), fontsize=7.2)
a0.legend(fontsize=5.9, frameon=False, loc="upper right")
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) SFU1605 的临界载荷（点线：只用欧拉公式）", "(a) SFU1605 critical load (dotted: Euler only)"), fontsize=7.3)
names = list(L_sizes)
a1.bar(range(3), [L_sizes[s] for s in names], color="#1f77b4", width=0.55)
for i, s in enumerate(names):
    a1.text(i, L_sizes[s] + 15, f"{L_sizes[s]:.0f} mm", ha="center", fontsize=6.4)
a1.set_xticks(range(3))
a1.set_xticklabels(["SFU" + s.replace("x", "0") for s in names], fontsize=6.6)
a1.set_ylim(0, max(L_sizes.values()) * 1.2)
a1.set_ylabel(T("最大无支承长度 / mm", "Max unsupported length / mm"), fontsize=7.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 固定–铰支、安全系数 2", "(b) Fixed–pinned, safety factor 2"), fontsize=7.3)
fig.tight_layout()
figure(fig, "fig9_5_1")

out(d0=s16["d0"], Ph=s16["Ph"], Dw=s16["Dw"], dr=s16["dr"], i16=i16, T_rated=T_RATED, T_max=T_MAX, eta=ETA,
    F_max=F_max, F_rated=F_rated, E=E / 1e3, sy=SY, lam_c=lam_c, S=S_REQ,
    L_ff=L_allow16[2.0], L_pp=L_allow16[1.0], L_fp=L_allow16[0.7], L_fx=L_allow16[0.5],
    L20=L_sizes["20x5"], L25=L_sizes["25x5"], r_fx_ff=L_allow16[0.5] / L_allow16[2.0],
    lam200=lam200, P_e200=P_e200 / 1e3, P_j200=P_j200 / 1e3, over200=(P_e200 / P_j200 - 1) * 100, Ca=s16["Ca"])
