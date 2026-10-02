"""2.9 节的示意图。

图 2.9.1：算例 2.9.1 的注意力权重矩阵：（a）不加掩码；（b）加因果掩码，每个词元只看自己和之前的词元。
图 2.9.2：小型 Transformer 的结构：词元嵌入加位置嵌入，L 个前置层归一化的 Transformer 块（多头注意力 + 前馈网络，各带残差），
最后的层归一化与输出层。
"""
import math

import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from _ch2 import TINY
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS


def softmax(z):
    z = z - z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


Q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0]])
K = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, 0.0]])
S = Q @ K.T / math.sqrt(2)
A = softmax(S)
Ac = softmax(S + np.triu(np.full((4, 4), -np.inf), 1))
fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.9))
for ax, M, title in ((axs[0], A, T("（a）不加掩码", "(a) No mask")), (axs[1], Ac, T("（b）因果掩码", "(b) Causal mask"))):
    ax.imshow(M, cmap="Oranges", vmin=0, vmax=1)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center", fontsize=10, color=C["ink"] if M[i, j] < 0.6 else "white")
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels([T(f"键 {j + 1}", f"key {j + 1}") for j in range(4)], fontsize=9)
    ax.set_yticklabels([T(f"查询 {i + 1}", f"query {i + 1}") for i in range(4)], fontsize=9)
    ax.set_title(title, fontsize=11)
fig.tight_layout()
figure(fig, "fig2_9_1")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.6, 6.4))
ax.set_xlim(0, 8.6)
ax.set_ylim(0, 9.2)
ax.axis("off")


def box(x, y, w, h, text, fc, ec=C["ink"], fs=10):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=C["ink"])


def up(y0, y1, x=3.0):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=C["ink"]))


box(3.0, 0.5, 3.0, 0.55, T("词元编号 $(B, T)$", "token ids $(B, T)$"), "#ffffff")
up(0.78, 1.15)
box(3.0, 1.45, 3.6, 0.6, T("词元嵌入 + 位置嵌入 → $(B, T, d)$", "token + position embedding → $(B, T, d)$"), "#eef3f8")
up(1.75, 2.15)
ax.add_patch(FancyBboxPatch((0.6, 2.2), 4.8, 4.75, boxstyle="round,pad=0.02,rounding_size=0.12", fc="#fafafa", ec=C["accent"], lw=1.5, ls="--"))
ax.text(5.55, 4.6, T(f"× L = {TINY['layers']}", f"× L = {TINY['layers']}"), fontsize=12, color=C["accent"], weight="bold")
box(3.0, 2.75, 2.4, 0.5, T("层归一化", "LayerNorm"), "#ffffff")
up(3.0, 3.35)
box(3.0, 3.7, 3.0, 0.6, T(f"多头注意力（{TINY['heads']} 头，因果）", f"multi-head attention ({TINY['heads']} heads, causal)"), "#fdf3dc")
up(4.0, 4.38)
ax.text(3.0, 4.55, "⊕", fontsize=18, ha="center", va="center")
ax.annotate("", xy=(2.75, 4.55), xytext=(1.1, 2.35), arrowprops=dict(arrowstyle="-|>", color=C["z"], lw=1.2, connectionstyle="angle,angleA=90,angleB=180"))
ax.text(0.75, 3.5, T("残差", "residual"), fontsize=9, color=C["z"], rotation=90)
up(4.75, 5.05)
box(3.0, 5.3, 2.4, 0.5, T("层归一化", "LayerNorm"), "#ffffff")
up(5.55, 5.85)
box(3.0, 6.15, 3.4, 0.55, T(f"前馈网络 $d \\to {TINY['ff']} \\to d$（GELU）", f"feed-forward $d \\to {TINY['ff']} \\to d$ (GELU)"), "#fdf3dc")
up(6.43, 6.62)
ax.text(3.0, 6.78, "⊕", fontsize=18, ha="center", va="center")
ax.annotate("", xy=(2.75, 6.78), xytext=(1.1, 4.75), arrowprops=dict(arrowstyle="-|>", color=C["z"], lw=1.2, connectionstyle="angle,angleA=90,angleB=180"))
up(7.0, 7.4)
box(3.0, 7.65, 2.4, 0.5, T("层归一化", "LayerNorm"), "#ffffff")
up(7.9, 8.2)
box(3.0, 8.5, 3.8, 0.55, T("输出层（与词元嵌入共享）→ $(B, T, V)$", "output layer (tied) → $(B, T, V)$"), "#eef3f8")
ax.text(6.2, 8.1, T(f"$V = {TINY['vocab']}$\n$T_{{\\max}} = {TINY['ctx']}$\n$d = {TINY['d']}$\n$L = {TINY['layers']}$，$h = {TINY['heads']}$\n$d_{{\\rm ff}} = {TINY['ff']}$",
                    f"$V = {TINY['vocab']}$\n$T_{{\\max}} = {TINY['ctx']}$\n$d = {TINY['d']}$\n$L = {TINY['layers']}$, $h = {TINY['heads']}$\n$d_{{\\rm ff}} = {TINY['ff']}$"),
        fontsize=10, va="top", color=C["ink"], linespacing=1.5)
figure(fig, "fig2_9_2")
plt.close(fig)
