"""44.2 节的计算：

算例 44.2.1  德布罗意波长 0.5 nm 的自由电子：由 E = ħ²k²/(2m) 求动能（eV）。
算例 44.2.2  数值解薛定谔方程：有限差分求宽 1 nm 无限深势阱的能级，与解析值比较，看误差随格点数怎样减小
             （图 44.2.2）。全章和网页实验都用这个解法。
图 44.2.1    两个定态的叠加：概率密度来回晃动，周期 τ = h/(E₂ − E₁)。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import h, e, m_e
import _draw as d
import _qm

# ---- 算例 44.2.1
lam = 0.5                                     # nm
k = 2 * math.pi / lam
E_free = _qm.C * k ** 2                        # eV
assert abs(E_free - h ** 2 / (2 * m_e * (lam * 1e-9) ** 2) / e) < 1e-9

# ---- 算例 44.2.2：数值解与解析解
L = 1.0
E_exact = [_qm.C * (n * math.pi / L) ** 2 for n in (1, 2, 3)]
rows = []
for N in (10, 20, 50, 100, 200, 500, 1000):
    dx = L / (N + 1)
    E, _ = _qm.levels(np.zeros(N), dx, 3)
    rows.append((N, E))
E100 = rows[3][1]
err100 = abs(E100[0] - E_exact[0]) / E_exact[0]
E1000 = rows[-1][1]
err1000 = abs(E1000[0] - E_exact[0]) / E_exact[0]
assert 80 < err100 / err1000 < 120               # 误差与 dx² 成正比：格点加密约 10 倍，误差约降 100 倍

# ---- 两个定态的叠加
dE = E_exact[1] - E_exact[0]
period_fs = h / (dE * e) * 1e15

out(lam=lam, k=k, E_free=E_free, E1=E_exact[0], E2=E_exact[1], E3=E_exact[2],
    E1_100=E100[0], err100_pct=100 * err100, err1000_pct=100 * err1000, dE=dE, period_fs=period_fs)

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.0))
Ns = np.array([r[0] for r in rows])
for n in range(3):
    errs = [abs(r[1][n] - E_exact[n]) / E_exact[n] for r in rows]
    ax.loglog(Ns, errs, "o-", lw=1.5, label=f"$E_{n + 1}$")
ax.loglog(Ns, 0.8 * (Ns / 10.0) ** -2, "--", color=d.MUTED, lw=1, label=T("斜率 −2", "slope −2"))
ax.set_xlabel(T("格点数 $N$", "grid points $N$")); ax.set_ylabel(T("相对误差", "relative error"))
ax.legend(frameon=False, fontsize=9); d.spines(ax)
figure(fig, "fig44_2_2")

fig, axs = plt.subplots(1, 4, figsize=(7.6, 2.1), sharey=True)
x = np.linspace(0, L, 300)
p1, p2 = np.sqrt(2 / L) * np.sin(np.pi * x / L), np.sqrt(2 / L) * np.sin(2 * np.pi * x / L)
for ax, frac in zip(axs, (0, 0.25, 0.5, 0.75)):
    ph = 2 * math.pi * frac                       # 相对相位 (E₂ − E₁) t/ħ
    dens = 0.5 * (p1 ** 2 + p2 ** 2 + 2 * p1 * p2 * math.cos(ph))
    ax.fill_between(x, dens, color=d.PROB, alpha=0.35); ax.plot(x, dens, color=d.PROB, lw=1.6)
    ax.set_title(("$t = 0$", "$t = \\tau/4$", "$t = \\tau/2$", "$t = 3\\tau/4$")[int(frac * 4)], fontsize=10)
    ax.set_xticks([0, 0.5, 1]); ax.set_xlabel(T("$x$ / nm", "$x$ / nm")); d.spines(ax)
axs[0].set_ylabel(T("$|\\Psi|^2$ / nm$^{-1}$", "$|\\Psi|^2$ / nm$^{-1}$"))
fig.tight_layout()
figure(fig, "fig44_2_1")
