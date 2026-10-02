"""2.4 节的示意图。

图 2.4.1：（a）一个两层感知机（输入 3、隐藏 4、输出 2）；（b）常用的激活函数。
图 2.4.2：（a）用 N = 4、8 个 ReLU 单元逼近 sin x（点为插值节点）；（b）最大误差随 N 的变化与误差界 h²/8（对数坐标）。
"""
import math

import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
relu = lambda z: np.maximum(z, 0)

# ---------------------------------------------------------------- 图 2.4.1
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.0), gridspec_kw={"width_ratios": [1.15, 1]})
ax = axs[0]
ax.set_xlim(0, 6)
ax.set_ylim(0, 5)
ax.axis("off")
layers = [(1.0, [3.75, 2.5, 1.25], "x", C["z"]), (3.0, [4.25, 3.1, 1.95, 0.8], "h", C["accent"]), (5.0, [3.1, 1.9], "\\hat y", C["x"])]
for (xa, ya, _, _), (xb, yb, _, _) in zip(layers[:-1], layers[1:]):
    for p in ya:
        for q in yb:
            ax.plot([xa + 0.28, xb - 0.28], [p, q], color=C["muted"], lw=0.7, alpha=0.7)
for xx, ys, nm, col in layers:
    for i, yy in enumerate(ys):
        ax.add_patch(Circle((xx, yy), 0.28, fc="white", ec=col, lw=1.6, zorder=3))
        ax.text(xx, yy, f"${nm}_{{{i + 1}}}$", ha="center", va="center", fontsize=10, zorder=4)
ax.text(1.0, 4.55, T("输入层", "input"), ha="center", fontsize=10, color=C["z"])
ax.text(3.0, 4.75, T("隐藏层", "hidden"), ha="center", fontsize=10, color=C["accent"])
ax.text(5.0, 3.7, T("输出层", "output"), ha="center", fontsize=10, color=C["x"])
ax.text(2.0, 0.15, "$W^{(1)}\\in\\mathbb{R}^{4\\times3}$", ha="center", fontsize=10)
ax.text(4.0, 0.15, "$W^{(2)}\\in\\mathbb{R}^{2\\times4}$", ha="center", fontsize=10)
ax.set_title(T("（a）两层感知机", "(a) A two-layer perceptron"), fontsize=11)
ax = axs[1]
z = np.linspace(-4, 4, 400)
gelu = 0.5 * z * (1 + np.vectorize(math.erf)(z / math.sqrt(2)))
ax.plot(z, relu(z), color=C["z"], lw=2, label="ReLU")
ax.plot(z, 1 / (1 + np.exp(-z)), color=C["y"], lw=1.6, label="sigmoid")
ax.plot(z, np.tanh(z), color=C["accent"], lw=1.6, label="tanh")
ax.plot(z, gelu, color=C["x"], lw=1.6, ls="--", label="GELU")
ax.axhline(0, color=C["muted"], lw=0.6)
ax.axvline(0, color=C["muted"], lw=0.6)
ax.set_ylim(-1.3, 3.2)
ax.set_xlabel("$z$")
ax.legend(fontsize=9, frameon=False, loc="upper left")
ax.set_title(T("（b）常用的激活函数", "(b) Common activation functions"), fontsize=11)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_4_1")
plt.close(fig)


# ---------------------------------------------------------------- 图 2.4.2
def interp(N):
    xs = np.linspace(0, 2 * np.pi, N + 1)
    ys = np.sin(xs)
    sl = np.diff(ys) / np.diff(xs)
    return xs, np.r_[sl[0], np.diff(sl)], ys[0]


fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9))
ax = axs[0]
xq = np.linspace(0, 2 * np.pi, 600)
ax.plot(xq, np.sin(xq), color=C["ink"], lw=2.2, label="$\\sin x$")
for N, col in ((4, C["x"]), (8, C["z"])):
    xs, c, y0 = interp(N)
    g = y0 + relu(xq[:, None] - xs[None, :-1]) @ c
    ax.plot(xq, g, color=col, lw=1.4, label=T(f"{N} 个 ReLU 单元", f"{N} ReLU units"))
    ax.plot(xs, np.sin(xs), "o", color=col, ms=4)
ax.set_ylim(-1.25, 1.35)
ax.set_xlabel("$x$")
ax.legend(fontsize=9, frameon=False, loc="upper right")
ax.set_title(T("（a）分段线性逼近", "(a) Piecewise-linear approximation"), fontsize=11)
ax = axs[1]
Ns = np.array([4, 8, 16, 32, 64, 128])
errs = []
for N in Ns:
    xs, c, y0 = interp(N)
    xq2 = np.linspace(0, 2 * np.pi, 20001)
    errs.append(np.max(np.abs(y0 + relu(xq2[:, None] - xs[None, :-1]) @ c - np.sin(xq2))))
ax.loglog(Ns, errs, "o-", color=C["z"], label=T("实际最大误差", "actual max error"))
ax.loglog(Ns, (2 * np.pi / Ns) ** 2 / 8, "--", color=C["accent"], label=T("误差界 $h^2/8$", "bound $h^2/8$"))
ax.set_xlabel(T("隐藏单元数 $N$", "hidden units $N$"))
ax.set_ylabel(T("最大误差", "max error"))
ax.legend(fontsize=9, frameon=False)
ax.set_title(T("（b）$N$ 加倍，误差约缩小到 1/4", "(b) Doubling $N$ quarters the error"), fontsize=11)
for a_ in axs:
    for s in ("top", "right"):
        a_.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_4_2")
plt.close(fig)
