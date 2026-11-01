"""9.3 超静定问题。

算例 9.3.1  一根 Ø40 钢轴支承在三个轴承上（两跨等长），每跨中点受 2 kN（本书设定）。先用变形协调求三个支反力（与梁单元对照），
            再看中间轴承座比两端低 δ（加工、装配误差，第 4 章的同轴度）时支反力怎样变化；比较两种跨距：
            输送机的长传动轴（每跨 600 mm）和紧凑的减速器轴（每跨 100 mm）——跨距短、轴刚的，对不同轴更敏感；
算例 9.3.2  两端固定和两端简支的梁受均布载荷：最大挠度之比（龙门横梁、导轨梁）；
图 9.3.1。
"""
import math

import numpy as np

import _ch9 as H
from bookout import T, figure, out, style

ST = H.mat("45-QT")
d, P = 40.0, 2000.0
EI = ST["E"] * math.pi * d ** 4 / 64


def three(Ls, delta):
    """两跨各长 Ls，跨中各受 P，中间支座下沉 delta（mm，向下为正）。返回 (R_A, R_B, R_C)"""
    zz, y, th, R = H.beam_fe([0, Ls / 2, Ls, 1.5 * Ls, 2 * Ls], lambda z: EI, {0.0: 0.0, Ls: delta, 2 * Ls: 0.0},
                             {Ls / 2: P, 1.5 * Ls: P}, h=Ls / 100)
    return R[0.0], R[Ls], R[2 * Ls]


# 变形协调（手算）：去掉中间支座，长 2L 的简支梁在两个四分点受 P，中点挠度 y_P；中间支座的力 R_B 使中点上升 R_B (2L)³/(48EI)
def hand(Ls, delta):
    Lt = 2 * Ls
    a_ = Lt / 4
    y_P = 2 * P * a_ * (3 * Lt ** 2 - 4 * a_ ** 2) / (48 * EI)      # 两个对称力在中点产生的挠度
    k_mid = 48 * EI / Lt ** 3
    RB = (y_P - delta) * k_mid
    RA = (2 * P - RB) / 2
    return RA, RB, RA


rows = {}
deltas = np.linspace(0, 0.05, 51)
for Ls in (600.0, 100.0):
    RA0, RB0, _ = three(Ls, 0.0)
    hA, hB, _ = hand(Ls, 0.0)
    curve = np.array([three(Ls, dd) for dd in deltas])
    k_mid = 48 * EI / (2 * Ls) ** 3
    d_unload = hand(Ls, 0.0)[1] / k_mid            # 中间支座下沉多少，它就完全不受力
    rows[Ls] = dict(RA0=RA0, RB0=RB0, hB=hB, err=abs(hB / RB0 - 1) * 100, curve=curve, k_mid=k_mid, d_unload=d_unload,
                    RB_01=three(Ls, 0.01)[1], RB_05=three(Ls, 0.05)[1])

# 算例 9.3.2：均布载荷的梁，两端固定与两端简支
ratio_ff = 5 / 1.0                                  # 简支 5wL⁴/384EI，固支 wL⁴/384EI

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
for Ls, col in ((600.0, "#1f77b4"), (100.0, "#d62728")):
    c = rows[Ls]["curve"]
    a0.plot(deltas * 1e3, c[:, 1], color=col, lw=1.5, label=T(f"中间支座，跨距 {Ls:.0f} mm", f"middle support, span {Ls:.0f} mm"))
    a0.plot(deltas * 1e3, c[:, 0], color=col, lw=1.0, ls="--", label=T(f"两端支座，跨距 {Ls:.0f} mm", f"end supports, span {Ls:.0f} mm"))
a0.axhline(0, color=H.MUTED, lw=0.5)
a0.set_xlabel(T("中间轴承座下沉 δ / µm", "Middle seat drop δ / µm"), fontsize=7.2)
a0.set_ylabel(T("支反力 / N", "Support reaction / N"), fontsize=7.2)
a0.legend(fontsize=5.9, frameon=False, loc="lower left")
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 三支点轴：支座不同心时的支反力", "(a) Three-bearing shaft: reactions vs misalignment"), fontsize=7.4)
x = np.linspace(0, 1, 200)
y_ss = 16 / 5 * (x - 2 * x ** 3 + x ** 4)            # 以简支梁最大挠度归一（5/384 → 1）
y_ff = 16 / 5 * (x ** 2 * (1 - x) ** 2)
a1.plot(x, y_ss, color="#1f77b4", lw=1.5, label=T("两端简支", "simply supported"))
a1.plot(x, y_ff, color="#d62728", lw=1.5, label=T("两端固定", "both ends fixed"))
a1.invert_yaxis()
a1.set_xlabel(T("位置 x / L", "Position x / L"), fontsize=7.2)
a1.set_ylabel(T("挠度（以简支梁最大值为 1）", "Deflection (simply supported max = 1)"), fontsize=7.2)
a1.legend(fontsize=6.2, frameon=False, loc="lower right")
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 均布载荷的梁：两端固定刚 5 倍", "(b) Uniform load: fixed ends are 5× stiffer"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig9_3_1")

L6, L1 = rows[600.0], rows[100.0]
out(d=d, P=P / 1e3, EI=EI / 1e9,
    RA_600=L6["RA0"], RB_600=L6["RB0"], err_600=L6["err"], k_600=L6["k_mid"], RB01_600=L6["RB_01"], RB05_600=L6["RB_05"],
    dU_600=L6["d_unload"],
    RA_100=L1["RA0"], RB_100=L1["RB0"], k_100=L1["k_mid"] / 1e3, RB01_100=L1["RB_01"], RB05_100=L1["RB_05"],
    dU_100=L1["d_unload"] * 1e3, RA05_100=three(100.0, 0.05)[0],
    r_unload=P / L1["RA0"], r_50=three(100.0, 0.05)[0] / L1["RA0"],
    pct01_100=(1 - L1["RB_01"] / L1["RB0"]) * 100, pct05_600=(1 - L6["RB_05"] / L6["RB0"]) * 100,
    ratio_k=L1["k_mid"] / L6["k_mid"], ratio_ff=ratio_ff)
