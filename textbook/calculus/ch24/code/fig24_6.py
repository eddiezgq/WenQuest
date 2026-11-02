"""图 24.6.1：左：erf x 的交错级数各项绝对值（x = 3、5），最大项远大于结果，相消损失有效数字；
右：y′ = x² + y² 的幂级数部分和与数值解，收敛半径约 2.003（解趋于无穷处）。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
c = 2 / math.sqrt(math.pi)
for x, col in ((1, GREEN), (3, BLUE), (5, RED)):
    n = np.arange(0, 100)
    lt = np.array([(2 * k + 1) * math.log(x) - math.lgamma(k + 1) - math.log(2 * k + 1) for k in n]) + math.log(c)
    a1.semilogy(n, np.exp(lt), color=col, lw=1.8, label=f"x = {x}")
    a1.axhline(math.erf(x), color=col, ls=":", lw=0.8)
a1.axhline(1e-16, color=MUTED, ls="--", lw=1)
a1.set_ylim(1e-18, 1e10)
a1.set_xlabel(T("项的序号 n", "term index n")); a1.set_ylabel(T("第 n 项的绝对值", "|n-th term|"))
a1.set_title(T("erf x 的交错级数：x 大时最大项远大于和", "Alternating series for erf x: huge terms for large x"), fontsize=10)
a1.legend(fontsize=9, frameon=False); clean(a1, zero=False)
K = 400
a = [0.0] * (K + 1)
for k in range(K):
    a[k + 1] = ((1.0 if k == 2 else 0.0) + sum(a[i] * a[k - i] for i in range(k + 1))) / (k + 1)
xs = np.linspace(0, 1.99, 400)
sol = solve_ivp(lambda x, y: [x * x + y[0] ** 2], (0, 1.99), [0.0], t_eval=xs, rtol=1e-11, atol=1e-12)
a2.plot(xs, sol.y[0], color=INK, lw=3, alpha=0.5, label=T("数值解", "numerical solution"))
for m, col in ((4, RED), (12, ACC), (40, GREEN), (400, BLUE)):
    a2.plot(xs, sum(a[k] * xs ** k for k in range(m + 1)), color=col, lw=1.3, label=T(f"级数到 x^{m}", f"series to x^{m}").replace(f"x^{m}", f"$x^{{{m}}}$"))
a2.axvline(2.0031, color=MUTED, ls=":", lw=1)
a2.text(0.95, 12, T("收敛半径 ≈ 2.003", "radius ≈ 2.003"), fontsize=9, color=MUTED)
a2.set_ylim(0, 20); a2.set_xlabel("x"); a2.set_ylabel("y")
a2.set_title(T("y′ = x² + y² 的幂级数解", "Power-series solution of y′ = x² + y²"), fontsize=10)
a2.legend(fontsize=8.5, frameon=False, loc="upper left"); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig24_6_1")
