"""图 3.3.1：ε–N 定义的几何意义。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, clean, figure, plt

n = np.arange(1, 61)
a = (-1.0) ** n / n
fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
for ax, eps in zip(axs, (0.2, 0.05)):
    N = int(np.ceil(1 / eps))      # n > N 时 1/n < ε
    inside = np.abs(a) < eps
    ax.axhspan(-eps, eps, color=RED, alpha=0.12)
    ax.plot(n[n <= N], a[n <= N], "o", color=MUTED, ms=3.5)
    ax.plot(n[n > N], a[n > N], "o", color=BLUE, ms=3.5)
    ax.axvline(N, color=RED, lw=1, ls="--")
    ax.text(N + 1, 0.75, f"N = {N}", color=RED)
    ax.text(45, eps + 0.03, f"ε = {eps}", color=RED, fontsize=9)
    ax.set_xlabel("n")
    ax.set_title(T(f"ε = {eps}：第 {N} 项以后全在带内", f"ε = {eps}: all terms after n = {N} lie in the band"), fontsize=10)
    clean(ax)
axs[0].set_ylabel("$(-1)^n/n$")
axs[0].set_ylim(-1.1, 1.0)
fig.tight_layout()
figure(fig, "fig3_3_1")
