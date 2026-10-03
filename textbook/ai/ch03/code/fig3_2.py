"""3.2 节的示意图。

图 3.2.1：（a）阿姆达尔定律：串行比例 f 一定时，加速比随处理器数 p 的变化，上限 1/f；
（b）古斯塔夫森定律：问题规模随 p 扩大时的加速比。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
p = np.logspace(0, 5, 300)
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.2))
ax = axs[0]
for f, col in ((0.05, C["x"]), (0.01, C["accent"]), (0.001, C["z"])):
    S = 1 / (f + (1 - f) / p)
    ax.loglog(p, S, color=col, lw=1.8, label=f"f = {f:g}")
    ax.axhline(1 / f, color=col, lw=0.8, ls=":")
ax.loglog(p, p, color=C["muted"], lw=0.9, ls="--", label=T("理想 S = p", "ideal S = p"))
ax.axvline(16896, color=C["muted"], lw=0.8)
ax.text(16896 * 1.15, 1.4, T("H100 的\nFP32 核心数", "H100 FP32\ncores"), fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("处理器数 p", "processors p"))
ax.set_ylabel(T("加速比 S", "speedup S"))
ax.set_ylim(1, 3e3)
ax.legend(fontsize=9, frameon=False, loc="upper left")
ax.set_title(T("（a）阿姆达尔：问题规模固定", "(a) Amdahl: fixed problem size"), fontsize=11)
ax = axs[1]
q = np.arange(1, 65)
for f, col in ((0.05, C["x"]), (0.2, C["accent"]), (0.5, C["z"])):
    ax.plot(q, f + (1 - f) * q, color=col, lw=1.8, label=f"f = {f:g}")
    ax.plot(q, 1 / (f + (1 - f) / q), color=col, lw=1.0, ls="--")
ax.plot(q, q, color=C["muted"], lw=0.9, ls=":")
ax.text(40, 10.5, T("虚线：同样的 f 按阿姆达尔定律", "dashed: Amdahl with the same f"), fontsize=8.6, color=C["muted"])
ax.set_xlabel(T("处理器数 p", "processors p"))
ax.set_ylabel(T("规模扩大的加速比 S′", "scaled speedup S′"))
ax.legend(fontsize=9, frameon=False, loc="upper left")
ax.set_title(T("（b）古斯塔夫森：问题随 p 扩大", "(b) Gustafson: problem grows with p"), fontsize=11)
for a in axs:
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig3_2_1")
plt.close(fig)
