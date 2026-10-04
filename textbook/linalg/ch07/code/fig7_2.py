"""图 7.2.1：函数和离散信号也是“向量”。左：cos t、sin t 与它们的组合 3cos t − 2sin t（都是 y'' + y = 0 的解）；
右：一路 8 点采样信号与噪声相加。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

t = np.linspace(0, 2 * np.pi, 400)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 3.8))
a1.plot(t, np.cos(t), color=BLUE, lw=1.6, label="cos t")
a1.plot(t, np.sin(t), color=GREEN, lw=1.6, label="sin t")
a1.plot(t, 3 * np.cos(t) - 2 * np.sin(t), color=RED, lw=2.4, label="3cos t − 2sin t")
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xlabel("t")
a1.legend(frameon=False, fontsize=9)
a1.set_title(T("函数空间中的线性组合", "linear combinations in a function space"), fontsize=11)
k = np.arange(8)
x = np.array([0, 1, 2, 3, 2, 1, 0, -1.0])
nz = np.array([0.1, -0.1, 0.2, 0.0, -0.2, 0.1, 0.0, 0.1])
a2.stem(k - 0.15, x, linefmt=BLUE, markerfmt="o", basefmt=" ", label=T("信号 x", "signal x"))
a2.stem(k + 0.15, x + nz, linefmt=RED, markerfmt="s", basefmt=" ", label=T("x + 噪声", "x + noise"))
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("采样序号 k", "sample k"))
a2.legend(frameon=False, fontsize=9)
a2.set_title(T("离散信号：ℝ⁸ 中的向量", "a discrete signal: a vector in ℝ⁸"), fontsize=11)
for ax in (a1, a2):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig7_2_1")
