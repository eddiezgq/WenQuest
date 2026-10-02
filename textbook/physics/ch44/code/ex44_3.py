"""44.3 节的计算：

估一估      1 g 的小球在 1 cm 的盒子里以 1 cm/s 往返，对应的量子数 n 有多大。

算例 44.3.1  宽 1 nm 的无限深势阱中的电子：最低三个能级；由 n = 2 跃迁到 n = 1 放出的光子波长。
算例 44.3.2  FinFET 的硅鳍宽 6 nm：侧壁为 (110) 面时，最低一组能谷在限制方向的有效质量约 0.315 mₑ，把鳍看成无限深势阱，求最低两个能级，
             与室温热能 k_B T 比较；能级随鳍宽的变化（图 44.3.2）。数值解（_qm.levels）核对解析式。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import h, c, e, hbar, k as kB
import _draw as d
import _qm


def En(n, L, mr=1.0):
    return _qm.C / mr * (n * math.pi / L) ** 2


# ---- 算例 44.3.1
L1 = 1.0
E = [En(n, L1) for n in (1, 2, 3)]
dE21 = E[1] - E[0]
lam21 = h * c / (dE21 * e) * 1e9                 # nm
N = 800
Enum, psi = _qm.levels(np.zeros(N), L1 / (N + 1), 3)
assert np.allclose(Enum, E, rtol=1e-4)       # 有限差分误差约 (n π dx)²/12

# ---- 算例 44.3.2
W, mr = 6.0, 0.315
F1, F2 = En(1, W, mr), En(2, W, mr)
kT = kB * 300 / e
ratio = (F2 - F1) / kT
boltz = math.exp(-ratio)                          # 第二能级与第一能级上电子数之比（玻尔兹曼因子，不计简并度）
Enum2, _ = _qm.levels(np.zeros(600), W / 601, 2, mr)
assert np.allclose(Enum2, [F1, F2], rtol=1e-4)

# ---- 估一估：1 g 的小球在 1 cm 的盒子里以 1 cm/s 运动，对应的量子数
mb, Lb, vb = 1e-3, 0.01, 0.01
n_ball = Lb * mb * vb / (math.pi * hbar)          # E = n²π²ħ²/(2mL²) = mv²/2 ⇒ n = L m v/(πħ)

out(n_ball=n_ball, L1=L1, E1=E[0], E2=E[1], E3=E[2], dE21=dE21, lam21=lam21,
    W=W, mr=mr, boltz_pct=100 * boltz, F1_meV=F1 * 1000, F2_meV=F2 * 1000, kT_meV=kT * 1000, ratio=ratio)

plt = style()
# ---- 图 44.3.1：能级、波函数与概率密度
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.6), sharey=True)
x = np.linspace(0, L1, 300)
for ax, kind in ((a1, "psi"), (a2, "prob")):
    ax.plot([0, 0], [0, 7], color=d.POT, lw=3); ax.plot([L1, L1], [0, 7], color=d.POT, lw=3)
    ax.plot([0, L1], [0, 0], color=d.POT, lw=1.5)
    for n in (1, 2, 3, 4):
        En_ = En(n, L1)
        ax.plot([0, L1], [En_, En_], color=d.LEVEL, lw=1, ls="--")
        f = np.sqrt(2 / L1) * np.sin(n * math.pi * x / L1)
        y = 0.38 * f if kind == "psi" else 0.27 * f ** 2
        ax.plot(x, En_ + y, color=d.PSI if kind == "psi" else d.PROB, lw=1.8)
        if kind == "psi":
            ax.text(L1 + 0.04, En_, f"$n={n}$", va="center", fontsize=9, color=d.INK)
    ax.set_xlim(-0.08, L1 + 0.2); ax.set_xlabel(T("$x$ / nm", "$x$ / nm")); d.spines(ax)
    ax.set_title(T("波函数 $\\psi_n$" if kind == "psi" else "概率密度 $|\\psi_n|^2$",
                   "wave functions $\\psi_n$" if kind == "psi" else "probability densities $|\\psi_n|^2$"), fontsize=10)
a1.set_ylabel(T("能量 $E$ / eV", "energy $E$ / eV")); a1.set_ylim(-0.3, 7)
figure(fig, "fig44_3_1")

# ---- 图 44.3.2：硅鳍中最低两个能级随鳍宽的变化
fig, ax = plt.subplots(figsize=(5.0, 3.0))
Ws = np.linspace(3, 20, 200)
ax.plot(Ws, 1000 * En(1, Ws, mr), color=d.LEVEL, lw=2, label="$E_1$")
ax.plot(Ws, 1000 * En(2, Ws, mr), color=d.PSI, lw=2, label="$E_2$")
ax.axhline(1000 * kT, color=d.CLASS, ls="--", lw=1.2, label=T("室温 $k_\\mathrm{B}T$", "room-temperature $k_\\mathrm{B}T$"))
ax.plot([W], [1000 * F1], "o", color=d.INK)
ax.annotate(T("鳍宽 6 nm", "6 nm fin"), (W, 1000 * F1), xytext=(9, 120), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=d.MUTED))
ax.set_xlabel(T("鳍宽 $W$ / nm", "fin width $W$ / nm")); ax.set_ylabel(T("能量 / meV", "energy / meV"))
ax.set_ylim(0, 400); ax.legend(frameon=False, fontsize=9); d.spines(ax)
figure(fig, "fig44_3_2")
