"""图 6.4.1：柯西准则——相邻两步之差趋于零不等于收敛：x = cos x 的迭代（压缩）与调和级数部分和。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
xs = [1.0]
for _ in range(50):
    xs.append(math.cos(xs[-1]))
xs = np.array(xs)
k = np.arange(1, 51)
step = np.abs(np.diff(xs))
err = np.abs(xs[1:] - 0.7390851332151607)
q = math.sin(1)
a1.semilogy(k, step, color=BLUE, lw=2, label=T("相邻两步之差", "step |xₖ − xₖ₋₁|"))
a1.semilogy(k, q / (1 - q) * step, color=ACC, lw=1.5, ls="--", label=T("误差上界 q/(1−q)·步长", "bound q/(1−q)·step"))
a1.semilogy(k, err, color=RED, lw=1.5, label=T("真实误差", "true error"))
a1.set_xlabel("k")
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("x = cos x：压缩迭代，步长小就说明离极限近", "x = cos x: contraction, small steps mean close"), fontsize=10)
clean(a1, zero=False)
n = np.arange(1, 10 ** 5 + 1)
H = np.cumsum(1 / n)
a2.semilogx(n, H, color=RED, lw=2, label=T("部分和 Hₙ → ∞", "partial sum Hₙ → ∞"))
ax2 = a2.twinx()
ax2.loglog(n, 1 / n, color=BLUE, lw=1.5, ls="--", label=T("步长 1/n → 0", "step 1/n → 0"))
a2.set_xlabel("n")
a2.set_ylabel(T("部分和", "partial sum"), color=RED)
ax2.set_ylabel(T("步长", "step"), color=BLUE)
a2.set_title(T("调和级数：步长趋于零，部分和却发散", "Harmonic series: steps → 0, sums diverge"), fontsize=10)
h1, l1 = a2.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
a2.legend(h1 + h2, l1 + l2, fontsize=9, frameon=False, loc="center left")
fig.tight_layout()
figure(fig, "fig6_4_1")
