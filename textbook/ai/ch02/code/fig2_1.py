"""2.1 节的示意图。

图 2.1.1：监督学习的流程：数据集分为训练集、验证集、测试集；模型 f_θ 给出预测，损失比较预测与标签，优化器沿梯度更新参数。
图 2.1.2：梯度下降在 L(w) = ½·4·(w − 3)² 上的迭代：η = 0.1 单调收敛，η = 0.45 振荡收敛，η = 0.55 发散。
"""
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS


def box(ax, x, y, w, h, text, fc, ec=C["ink"], fs=10):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=C["ink"])


def arr(ax, p, q, text="", dy=0.18, color=C["ink"], rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, lw=1.3, color=color, connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, text, ha="center", fontsize=9, color=color)


# ---------------------------------------------------------------- 图 2.1.1
fig, ax = plt.subplots(figsize=(11.0, 3.9))
ax.set_xlim(0, 11)
ax.set_ylim(0, 3.9)
ax.axis("off")
box(ax, 1.1, 2.9, 1.9, 0.75, T("训练集 70%", "training set 70%"), "#eef3f8", C["z"])
box(ax, 1.1, 1.95, 1.9, 0.75, T("验证集 15%", "validation set 15%"), "#f1f6ef", C["y"])
box(ax, 1.1, 1.0, 1.9, 0.75, T("测试集 15%", "test set 15%"), "#fbe9e7", C["x"])
box(ax, 3.9, 2.9, 1.7, 0.8, T("模型 $f_{\\boldsymbol{\\theta}}(\\boldsymbol{x})$", "model $f_{\\boldsymbol{\\theta}}(\\boldsymbol{x})$"), "#fdf3dc")
box(ax, 6.3, 2.9, 1.7, 0.8, T("损失 $\\ell(\\hat y, y)$", "loss $\\ell(\\hat y, y)$"), "#fdf3dc")
box(ax, 5.1, 1.35, 2.2, 0.8, T("优化器：$\\boldsymbol{\\theta} \\leftarrow \\boldsymbol{\\theta} - \\eta\\nabla\\mathcal{L}$",
                               "optimizer: $\\boldsymbol{\\theta} \\leftarrow \\boldsymbol{\\theta} - \\eta\\nabla\\mathcal{L}$"), "#ffffff", fs=9.5)
arr(ax, (2.05, 2.9), (3.05, 2.9), T("$\\boldsymbol{x}_i$", "$\\boldsymbol{x}_i$"))
arr(ax, (4.75, 2.9), (5.45, 2.9), "$\\hat y_i$")
ax.annotate("", xy=(6.3, 3.3), xytext=(1.1, 3.28), arrowprops=dict(arrowstyle="-|>", color=C["muted"], lw=1.0,
                                                                   connectionstyle="arc3,rad=-0.18"))
ax.text(2.45, 3.42, T("标签 $y_i$", "labels $y_i$"), fontsize=9, color=C["muted"])
arr(ax, (6.3, 2.5), (5.6, 1.75), T("梯度", "gradient"), dy=0.0)
arr(ax, (4.4, 1.75), (3.9, 2.5), T("更新参数", "update"), dy=0.0)
ax.text(8.1, 2.95, T("训练集：求梯度、更新参数\n验证集：选超参数、决定何时停\n测试集：最后只用一次，\n估计对新数据的表现",
                     "training: gradients and updates\nvalidation: hyperparameters, stopping\ntest: used once at the end\nto estimate new-data performance"),
        fontsize=9, color=C["ink"], va="center", linespacing=1.5)
figure(fig, "fig2_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.1.2
a, ws, w0 = 4.0, 3.0, 0.0
fig, axs = plt.subplots(1, 2, figsize=(10.0, 3.8))
ax = axs[0]
w = np.linspace(-0.8, 6.8, 300)
ax.plot(w, 0.5 * a * (w - ws) ** 2, color=C["muted"], lw=1.2)
cols = {0.1: C["z"], 0.45: C["accent"], 0.55: C["x"]}
for eta, col in cols.items():
    x = w0
    pts = [x]
    for _ in range(6 if eta < 0.5 else 3):
        x = x - eta * a * (x - ws)
        pts.append(x)
    pts = np.array(pts)
    ax.plot(pts, 0.5 * a * (pts - ws) ** 2, "o-", color=col, ms=4, lw=1.1, label=f"$\\eta = {eta}$")
ax.set_xlim(-0.8, 6.8)
ax.set_ylim(-1, 40)
ax.set_xlabel("$w$")
ax.set_ylabel("$L(w)$")
ax.legend(fontsize=9, frameon=False)
ax.set_title(T("（a）在损失曲线上的前几步", "(a) The first steps on the loss curve"), fontsize=11)
ax = axs[1]
for eta, col in list(cols.items()) + [(0.25, C["y"])]:
    x, pts = w0, [abs(w0 - ws)]
    for _ in range(30):
        x = x - eta * a * (x - ws)
        pts.append(abs(x - ws))
    ax.semilogy(range(31), np.maximum(pts, 1e-16), "-", color=col, lw=1.6, label=f"$\\eta = {eta}$")
ax.set_xlabel(T("迭代次数 $k$", "iteration $k$"))
ax.set_ylabel("$|w_k - w^*|$")
ax.set_ylim(1e-16, 1e4)
ax.legend(fontsize=9, frameon=False, loc="lower left", ncol=2)
ax.set_title(T("（b）误差随迭代的变化（对数坐标）", "(b) Error versus iteration (log scale)"), fontsize=11)
for a_ in axs:
    for s in ("top", "right"):
        a_.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_1_2")
plt.close(fig)
