"""图 18.5.1：左：F(x) = x² sin(1/x) 的导数 2x sin(1/x) − cos(1/x)：有界，在 0 附近剧烈振荡，0 处不连续，但可积；
右：G(x) = x² sin(1/x²) 的导数在 0 附近无界：G 处处可导，G′ 却不是黎曼可积的。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
x = np.linspace(1e-4, 0.5, 20000)
a1.plot(x, 2 * x * np.sin(1 / x) - np.cos(1 / x), color=BLUE, lw=0.6)
a1.set_ylim(-1.6, 1.6)
a1.set_xlabel("x")
a1.set_title(T("F′(x) = 2x sin(1/x) − cos(1/x)：有界，可积", "F′(x) = 2x sin(1/x) − cos(1/x): bounded, integrable"), fontsize=10)
clean(a1)
x = np.linspace(0.02, 0.5, 40000)
a2.plot(x, 2 * x * np.sin(1 / x ** 2) - 2 / x * np.cos(1 / x ** 2), color=RED, lw=0.5)
a2.set_ylim(-100, 100)
a2.set_xlabel("x")
a2.set_title(T("G′(x) = 2x sin(1/x²) − (2/x) cos(1/x²)：无界，不可积", "G′(x) = 2x sin(1/x²) − (2/x) cos(1/x²): unbounded, not integrable"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig18_5_1")
