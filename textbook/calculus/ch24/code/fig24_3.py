"""图 24.3.1：左：光滑但不解析的 ψ(x) = e^{−1/x}（x > 0）及用它做的 C^∞ 过渡，与三次、五次多项式过渡比较；
右：ln(1 + x) 在 x = −0.75 的部分和误差，拉格朗日余项的界无用，积分余项的界贴着实际误差。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

psi = lambda x: np.where(x > 0, np.exp(-1 / np.maximum(x, 1e-300)), 0.0)
step = lambda x: psi(x) / (psi(x) + psi(1 - x))
t = np.linspace(-0.25, 1.25, 1201)
tc = np.clip(t, 0, 1)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
a1.plot(t, 3 * tc ** 2 - 2 * tc ** 3, color=ACC, lw=1.6, label=T("三次 3x² − 2x³", "cubic 3x² − 2x³"))
a1.plot(t, 10 * tc ** 3 - 15 * tc ** 4 + 6 * tc ** 5, color=GREEN, lw=1.6, label=T("五次", "quintic"))
a1.plot(t, step(t), color=BLUE, lw=2.2, label=T(r"$C^\infty$ 过渡 σ(x) = ψ(x)/(ψ(x) + ψ(1 − x))", r"$C^\infty$ step σ(x) = ψ(x)/(ψ(x) + ψ(1 − x))"))
a1.plot(t, psi(t), color=RED, lw=1.4, ls="--", label=T(r"ψ(x) = $e^{-1/x}$（x > 0）", r"ψ(x) = $e^{-1/x}$ (x > 0)"))
a1.set_ylim(-0.05, 1.1)
a1.set_xlabel(T("归一化时间 x = t/T", "normalized time x = t/T")); a1.set_ylabel(T("归一化夹爪力", "normalized grip force"))
a1.set_title(T("ψ 在 0 处各阶导数都为 0：泰勒级数恒为 0，却不等于 ψ", "All derivatives of ψ vanish at 0: its Taylor series is 0, not ψ"), fontsize=10)
a1.legend(fontsize=8.5, frameon=False, loc="upper left"); clean(a1)
x = -0.75
ns = np.arange(2, 41)
err = [abs(sum((-1) ** (k + 1) * x ** k / k for k in range(1, n + 1)) - math.log1p(x)) for n in ns]
a2.semilogy(ns, err, "o-", color=BLUE, ms=3, label=T("实际误差", "actual error"))
a2.semilogy(ns, (abs(x) / (1 + x)) ** (ns + 1) / (ns + 1), color=RED, lw=1.6, label=T("拉格朗日余项的界", "Lagrange bound"))
a2.semilogy(ns, abs(x) ** (ns + 1) / ((ns + 1) * (1 - abs(x))), color=GREEN, lw=1.6, ls="--", label=T("积分型余项的界", "integral-remainder bound"))
a2.set_xlabel(T("项数 n", "terms n")); a2.set_ylabel(T("误差", "error"))
a2.set_title(T("ln(1 + x)，x = −0.75", "ln(1 + x), x = −0.75"), fontsize=10)
a2.legend(fontsize=9, frameon=False); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig24_3_1")
