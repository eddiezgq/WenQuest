"""图 4.4.1：ε–δ 定义的几何意义（f(x) = x²，a = 2，L = 4）。"""
import math

import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, clean, figure, plt

fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(0.8, 3.2, 400)
for ax, eps in zip(axs, (1.0, 0.3)):
    d = min(2 - math.sqrt(4 - eps), math.sqrt(4 + eps) - 2)
    ax.axhspan(4 - eps, 4 + eps, color=RED, alpha=0.12)
    ax.axvspan(2 - d, 2 + d, color=BLUE, alpha=0.12)
    ax.plot(x, x * x, color=INK, lw=2)
    xx = np.linspace(2 - d, 2 + d, 100)
    ax.plot(xx, xx * xx, color=BLUE, lw=3.5)
    ax.plot([2], [4], "o", color=INK, ms=5, zorder=5)
    dp = min(1, eps / 5)                               # 算例 4.4.2 的证明给出的 δ
    for xv in (2 - dp, 2 + dp):
        ax.axvline(xv, color=BLUE, lw=1, ls="--")
    ax.text(0.85, 4 + eps + 0.15, f"$L+\\varepsilon$", color=RED)
    ax.text(0.85, 4 - eps - 0.55, f"$L-\\varepsilon$", color=RED)
    ax.text(2 + d + 0.03, 0.6, f"$a+\\delta$", color=BLUE)
    ax.set_xlim(0.8, 3.2)
    ax.set_ylim(0, 10)
    ax.set_title(T(f"ε = {eps:g}：最大可用 δ ≈ {d:.3f}，证明取 δ = {dp:g}", f"ε = {eps:g}: largest δ ≈ {d:.3f}, proof uses δ = {dp:g}"), fontsize=10)
    clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig4_4_1")
