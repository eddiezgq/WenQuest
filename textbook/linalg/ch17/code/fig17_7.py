"""图 17.7.1：若尔当块对扰动极其敏感。(a) 8 阶若尔当块 J₈(0) 的左下角加 ε = 10⁻¹⁶、10⁻⁸、10⁻⁴：8 个特征值均匀分布在半径 ε^{1/8} 的圆上；
(b) 特征值的模 |λ| 随 ε 的变化（双对数坐标），斜率为 1/n：ε 改变 10⁻¹⁶ 时，n = 8 的特征值移动 10⁻²。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.4))
n = 8
for e, col in ((1e-16, BLUE), (1e-8, GREEN), (1e-4, RED)):
    Jn = np.diag(np.ones(n - 1), 1); Jn[-1, 0] = e
    ev = np.linalg.eigvals(Jn)
    r = e ** (1 / n)
    th = np.linspace(0, 2 * np.pi, 200)
    a1.plot(r * np.cos(th), r * np.sin(th), color=col, lw=0.8, ls=":")
    a1.plot(ev.real, ev.imag, "o", color=col, ms=6, label=f"ε = 1e{int(np.log10(e))}，|λ| = {r:.3g}")
a1.plot(0, 0, "k+", ms=10)
a1.set_aspect("equal"); a1.set_xlim(-0.4, 0.4); a1.set_ylim(-0.4, 0.4)
a1.legend(frameon=False, fontsize=8.5, loc="upper right")
a1.set_title(T("(a) J₈(0) + ε e₈e₁ᵀ 的特征值", "(a) Eigenvalues of J₈(0) + ε e₈e₁ᵀ"), fontsize=11)
eps = np.logspace(-16, 0, 50)
for nn, col in ((2, BLUE), (4, GREEN), (8, RED)):
    a2.loglog(eps, eps ** (1 / nn), color=col, lw=2, label=T(f"n = {nn}：斜率 1/{nn}", f"n = {nn}: slope 1/{nn}"))
a2.loglog(eps, eps, color=MUTED, lw=1, ls="--", label=T("可对角化：斜率 1", "diagonalizable: slope 1"))
a2.set_xlabel(T("扰动 ε", "perturbation ε")); a2.set_ylabel(T("特征值的移动 |λ|", "eigenvalue shift |λ|"))
a2.legend(frameon=False, fontsize=8.5, loc="lower right")
a2.set_title(T("(b) 移动量 ε^{1/n}", "(b) Shift ε^{1/n}").replace("{1/n}", "(1/n)"), fontsize=11)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig17_7_1")
