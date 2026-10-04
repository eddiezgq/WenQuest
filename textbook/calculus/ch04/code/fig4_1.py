"""图 4.1.1：(x² − 1)/(x − 1)、sin x / x、sin(1/x)。"""
import numpy as np

from _fig import ACC, BLUE, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13, 3.8))
x = np.linspace(-1, 3, 400)
a1.plot(x, x + 1, color=BLUE, lw=2)
a1.plot([1], [2], "o", mfc="white", mec=BLUE, ms=7, zorder=5)
a1.text(1.15, 1.6, T("x = 1 处无定义\n极限为 2", "undefined at x = 1\nlimit 2"), fontsize=9)
a1.set_title("$(x^2-1)/(x-1)$", fontsize=11)
clean(a1)
x = np.linspace(-12, 12, 2000)
x = x[np.abs(x) > 1e-9]
a2.plot(x, np.sin(x) / x, color=RED, lw=2)
a2.plot([0], [1], "o", mfc="white", mec=RED, ms=7, zorder=5)
a2.set_title(r"$\sin x / x$", fontsize=11)
clean(a2)
x = 1 / np.linspace(1 / 0.6, 250, 40000)          # 按 1/x 等距采样，每个周期的点数相同
for s in (1, -1):
    a3.plot(s * x, np.sin(1 / (s * x)), color=ACC, lw=0.8)
a3.set_ylim(-1.3, 1.3)
a3.set_title(r"$\sin(1/x)$", fontsize=11)
clean(a3)
fig.tight_layout()
figure(fig, "fig4_1_1")
