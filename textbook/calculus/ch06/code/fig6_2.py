"""图 6.2.1：上确界——q(t) = 1 − e^(−t/τ) 的上确界 1 取不到，ε 刻画；sin n 的上确界 1。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
tau = 0.15
t = np.linspace(0, 1.2, 600)
a1.plot(t, 1 - np.exp(-t / tau), color=BLUE, lw=2)
a1.axhline(1, color=RED, lw=1.2, ls="--")
eps = 0.1
a1.axhspan(1 - eps, 1, color=RED, alpha=0.12)
te = tau * math.log(1 / eps)
a1.plot([te], [1 - eps], "o", color=RED, ms=5)
a1.text(te + 0.02, 1 - eps - 0.08, T("t > τ ln(1/ε) 时 q > 1 − ε", "q > 1 − ε for t > τ ln(1/ε)"), fontsize=9)
a1.text(0.8, 1.03, T("上确界 1（取不到）", "sup = 1 (not attained)"), color=RED, fontsize=9)
a1.set_ylim(0, 1.12)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel("q(t)")
clean(a1, zero=False)
n = np.arange(1, 401)
a2.plot(n, np.sin(n), ".", color=BLUE, ms=3)
a2.axhline(1, color=RED, lw=1.2, ls="--")
a2.axhline(-1, color=RED, lw=1.2, ls="--")
best = [k for k in n if np.sin(k) == max(np.sin(n[:k]))]
a2.plot(best, np.sin(best), "o", mfc="none", mec=ACC, ms=7, label=T("刷新最大值的项", "new records"))
a2.legend(fontsize=9, frameon=True, loc="center right")
a2.set_xlabel("n")
a2.set_ylabel("sin n")
a2.set_title(T("{sin n} 的上确界 1、下确界 −1，都取不到", "sup{sin n} = 1, inf = −1, neither attained"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig6_2_1")
