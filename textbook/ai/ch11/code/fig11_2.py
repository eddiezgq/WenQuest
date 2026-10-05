"""11.2 节的示意图（数值同程序 11.2.1）。

图 11.2.1：（a）梯度在 64 层网络中逐层反传时范数的变化（对数坐标）：朴素堆叠每层乘一个随机矩阵，
梯度指数衰减；加上残差连接与归一化后，梯度每层只被轻微缩放，传到第一层仍是同一量级。
（b）残差块的结构：主路算 F(h)，旁路把 h 原样加过来，反向时梯度有一条不经过 F 的直路。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
from _ch11 import grad_profile                      # 与程序 11.2.1 调同一个函数，保证图与算例一致

D, L = 64, 64
prof_plain, prof_res = grad_profile(D, L)

fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.2), gridspec_kw={"width_ratios": [1.35, 1]})
x = np.arange(1, L + 1)
a.semilogy(x, prof_plain, color=C["x"], lw=1.8, label=T("朴素堆叠", "plain stacking"))
a.semilogy(x, prof_res, color=C["z"], lw=1.8, label=T("残差 + 归一化", "residual + normalization"))
a.axhline(prof_res[0], ls=":", lw=0.9, color=C["muted"])
a.set_xlabel(T("反传经过的层数", "layers traversed backward"))
a.set_ylabel(T("梯度范数（对数）", "gradient norm (log)"))
a.set_title(T("(a) 梯度反传时的范数", "(a) Gradient norm during backprop"), fontsize=10)
a.legend(fontsize=9, framealpha=0.9)
a.grid(alpha=0.25, lw=0.5)

# (b) 残差块
def box(x0, y0, w, h, text, col, alpha=0.5):
    b.add_patch(plt.Rectangle((x0, y0), w, h, fc=col, alpha=alpha, ec=col, lw=0.9))
    b.text(x0 + w / 2, y0 + h / 2, text, ha="center", va="center", fontsize=9, color=C["ink"])


b.text(0.5, 3.55, T("h", "h"), ha="center", fontsize=11, color=C["ink"])
box(0.0, 2.2, 1.0, 0.55, T("卷积", "conv"), C["z"])
box(0.0, 1.3, 1.0, 0.55, T("归一化 + 激活", "norm + act"), C["y"])
box(0.0, 0.4, 1.0, 0.55, T("卷积", "conv"), C["z"])
b.annotate("", (0.5, 2.2), (0.5, 3.4), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C["muted"]))
b.annotate("", (0.5, 1.85), (0.5, 2.2), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C["muted"]))
b.annotate("", (0.5, 0.95), (0.5, 1.3), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C["muted"]))
b.annotate("", (0.5, -0.15), (0.5, 0.4), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C["muted"]))
b.plot([1.6, 1.6], [3.4, -0.35], lw=1.6, color=C["x"])            # 旁路
b.annotate("", (0.75, -0.35), (1.6, -0.35), arrowprops=dict(arrowstyle="-|>", lw=1.6, color=C["x"]))
b.plot([0.5, 1.6], [3.4, 3.4], lw=1.6, color=C["x"])
b.add_patch(plt.Circle((0.5, -0.35), 0.16, fc="white", ec=C["ink"], lw=0.9))
b.text(0.5, -0.35, "+", ha="center", va="center", fontsize=11)
b.text(1.75, 1.6, T("旁路：h 原样加过来\n反向时梯度走这里不衰减", "identity path:\ngradients flow unchanged"),
       fontsize=8.5, color=C["x"], va="center")
b.text(0.5, -1.0, T("h + F(h)", "h + F(h)"), ha="center", fontsize=11, color=C["ink"])
b.set_xlim(-0.6, 4.4)
b.set_ylim(-1.4, 4.0)
b.axis("off")
b.set_title(T("(b) 残差块", "(b) A residual block"), fontsize=10)
fig.tight_layout()
figure(fig, "fig11_2_1")
