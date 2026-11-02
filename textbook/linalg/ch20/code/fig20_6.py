"""图 20.6.1：(a) 希尔伯特矩阵的条件数（50 位精度计算）与双精度下解 Hₙx = Hₙ1 的相对误差；
(b) 威尔金森多项式 (x − 1)…(x − 20) 的 x¹⁹ 系数减去 2⁻²³ 后的 20 个根：后 10 个变成 5 对共轭复根。"""
import mpmath as mp
import numpy as np
import scipy.linalg as sla

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

mp.mp.dps = 50
ns = np.arange(2, 16)
kap, fe = [], []
for n in ns:
    H = mp.matrix(n, n)
    for i in range(n):
        for j in range(n):
            H[i, j] = mp.mpf(1) / (i + j + 1)
    s = mp.svd_r(H, compute_uv=False)
    kap.append(float(max(s) / min(s)))
    Hd = sla.hilbert(n)
    xh = np.linalg.solve(Hd, Hd @ np.ones(n))
    fe.append(np.linalg.norm(xh - 1) / np.sqrt(n))
eps = np.finfo(float).eps
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.5))
a1.semilogy(ns, kap, "o-", color=RED, label=T("条件数 κ₂(Hₙ)", "condition number κ₂(Hₙ)"))
a1.semilogy(ns, fe, "s-", color=BLUE, label=T("双精度解的相对误差", "relative error of the double-precision solution"))
a1.semilogy(ns, np.array(kap) * eps, color=MUTED, lw=1, ls="--", label="κ·ε")
a1.axhline(1 / eps, color=INK, lw=0.6, ls=":")
a1.text(13.0, 1 / eps * 2.5, "1/ε", fontsize=9)
a1.set_xlabel("n")
a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.set_title(T("(a) 希尔伯特矩阵：每加一阶，条件数约乘 30", "(a) Hilbert matrices: κ grows about 30× per order"), fontsize=11)
coeffs = [mp.mpf(1)]
for r in range(1, 21):
    coeffs = [a - r * b for a, b in zip(coeffs + [0], [0] + coeffs)]
pert = list(coeffs)
pert[1] -= mp.mpf(2) ** -23
roots = mp.polyroots(pert, maxsteps=200, extraprec=200)
a2.plot(range(1, 21), [0] * 20, "o", mfc="none", mec=MUTED, ms=8, label=T("原来的根 1, 2, …, 20", "original roots 1, 2, …, 20"))
a2.plot([float(mp.re(z)) for z in roots], [float(mp.im(z)) for z in roots], "o", color=RED, ms=5, label=T("系数改动 2⁻²³ 之后", "after changing a coefficient by 2⁻²³"))
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("实部", "real part"))
a2.set_ylabel(T("虚部", "imaginary part"))
a2.legend(frameon=False, fontsize=8.5, loc="upper left")
a2.set_ylim(-3.6, 4.2)
a2.set_title(T("(b) 威尔金森多项式的根", "(b) Roots of Wilkinson's polynomial"), fontsize=11)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig20_6_1")
