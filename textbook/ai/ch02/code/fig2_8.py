"""2.8 节的示意图。

图 2.8.1：（a）卷积：3×3 的卷积核在 7×7 的输入上滑动（步长 1），每个位置做一次点积，得到 5×5 的输出；
（b）im2col：把每个窗口展成一行，卷积变成一次矩阵乘法。
图 2.8.2：循环神经网络按时间展开：同一组权重在每个时间步重复使用，后一步要等前一步算完。
"""
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, axs = plt.subplots(1, 2, figsize=(10.8, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
ax = axs[0]
ax.set_xlim(0, 13)
ax.set_ylim(-0.8, 7.6)
ax.axis("off")
for i in range(7):
    for j in range(7):
        hl = 1 <= i <= 3 and 2 <= j <= 4
        ax.add_patch(Rectangle((j * 0.8, 6.0 - i * 0.8), 0.78, 0.78, fc="#fdf3dc" if hl else "#eef3f8", ec=C["ink"], lw=0.6))
ax.add_patch(Rectangle((2 * 0.8, 6.0 - 3 * 0.8), 2.4, 2.4, fill=False, ec=C["accent"], lw=2.2))
ax.text(2.8, 6.95, T("输入 7×7", "input 7×7"), ha="center", fontsize=10)
for i in range(3):
    for j in range(3):
        ax.add_patch(Rectangle((6.3 + j * 0.6, 4.6 - i * 0.6), 0.58, 0.58, fc="#fbe9e7", ec=C["ink"], lw=0.6))
ax.text(7.2, 5.4, T("卷积核 3×3", "kernel 3×3"), ha="center", fontsize=10)
for i in range(5):
    for j in range(5):
        hl = i == 1 and j == 2
        ax.add_patch(Rectangle((9.0 + j * 0.75, 5.0 - i * 0.75), 0.73, 0.73, fc=C["accent"] if hl else "#f1f6ef", ec=C["ink"], lw=0.6))
ax.text(10.9, 5.95, T("输出 5×5", "output 5×5"), ha="center", fontsize=10)
ax.add_patch(FancyArrowPatch((4.1, 4.4), (10.5, 4.0), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=C["accent"],
                             connectionstyle="arc3,rad=-0.35"))
ax.text(6.5, -0.4, T("同一组 9 个权重在所有位置共用；每个输出只看输入中的一小块", "the same 9 weights are shared by every position;\neach output sees only a small patch"),
        ha="center", fontsize=9, color=C["ink"])
ax.set_title(T("（a）卷积：滑动的点积", "(a) Convolution: a sliding dot product"), fontsize=11)
ax = axs[1]
ax.set_xlim(0, 10)
ax.set_ylim(-0.8, 7.6)
ax.axis("off")
ax.add_patch(Rectangle((0.3, 0.8), 3.6, 5.6, fc="#eef3f8", ec=C["ink"], lw=1))
for r in range(1, 8):
    ax.plot([0.3, 3.9], [0.8 + r * 0.7, 0.8 + r * 0.7], color=C["muted"], lw=0.5)
ax.add_patch(Rectangle((0.3, 5.7), 3.6, 0.7, fc="#fdf3dc", ec=C["accent"], lw=1.6))
ax.text(2.1, 6.75, T("窗口展成行", "patches as rows"), ha="center", fontsize=9.5)
ax.text(2.1, 0.35, T("$(H_{\\rm out}W_{\\rm out})\\times(k^2C_{\\rm in})$", "$(H_{\\rm out}W_{\\rm out})\\times(k^2C_{\\rm in})$"), ha="center", fontsize=9.5)
ax.text(4.4, 3.6, "×", fontsize=16, ha="center", va="center")
ax.add_patch(Rectangle((5.0, 1.8), 1.5, 3.6, fc="#fbe9e7", ec=C["ink"], lw=1))
ax.text(5.75, 5.75, T("卷积核", "kernels"), ha="center", fontsize=9.5)
ax.text(5.75, 1.35, "$(k^2C_{\\rm in})\\times C_{\\rm out}$", ha="center", fontsize=9.5)
ax.text(7.0, 3.6, "=", fontsize=16, ha="center", va="center")
ax.add_patch(Rectangle((7.5, 0.8), 1.5, 5.6, fc="#f1f6ef", ec=C["ink"], lw=1))
ax.text(8.25, 6.75, T("输出", "output"), ha="center", fontsize=9.5)
ax.text(8.25, 0.35, "$(H_{\\rm out}W_{\\rm out})\\times C_{\\rm out}$", ha="center", fontsize=9.5)
ax.set_title(T("（b）im2col：卷积变成矩阵乘法", "(b) im2col: convolution as a matrix product"), fontsize=11)
fig.tight_layout()
figure(fig, "fig2_8_1")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10.4, 3.4))
ax.set_xlim(0, 10.4)
ax.set_ylim(0, 3.6)
ax.axis("off")
for t in range(4):
    x0 = 0.9 + 2.4 * t
    lab = ["1", "2", "3", "T"][t]
    ax.add_patch(FancyBboxPatch((x0 - 0.5, 1.45), 1.0, 0.7, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#fdf3dc", ec=C["ink"], lw=1.2))
    ax.text(x0, 1.8, f"$\\boldsymbol{{h}}_{{{lab}}}$", ha="center", va="center", fontsize=12)
    ax.text(x0, 0.35, f"$\\boldsymbol{{x}}_{{{lab}}}$", ha="center", va="center", fontsize=12)
    ax.add_patch(FancyArrowPatch((x0, 0.6), (x0, 1.42), arrowstyle="-|>", mutation_scale=11, lw=1.1, color=C["ink"]))
    ax.text(x0 + 0.1, 0.95, "$W_x$", fontsize=9, color=C["z"])
    ax.text(x0, 3.15, f"$\\hat{{\\boldsymbol{{y}}}}_{{{lab}}}$", ha="center", va="center", fontsize=12)
    ax.add_patch(FancyArrowPatch((x0, 2.18), (x0, 2.9), arrowstyle="-|>", mutation_scale=11, lw=1.1, color=C["ink"]))
    if t < 3:
        if t == 2:
            ax.text(x0 + 1.2, 1.8, "⋯", fontsize=16, ha="center", va="center")
            continue
        ax.add_patch(FancyArrowPatch((x0 + 0.52, 1.8), (x0 + 1.88, 1.8), arrowstyle="-|>", mutation_scale=12, lw=1.4, color=C["x"]))
        ax.text(x0 + 1.2, 1.95, "$W_h$", ha="center", fontsize=10, color=C["x"])
ax.text(0.1, 2.6, "$\\boldsymbol{h}_0$", fontsize=11, color=C["muted"])
ax.add_patch(FancyArrowPatch((0.2, 2.45), (0.38, 1.95), arrowstyle="-|>", mutation_scale=9, lw=1.0, color=C["muted"]))
ax.text(9.6, 1.0, T("同一组 $W_h$、$W_x$\n在每一步重复使用；\n第 $t$ 步要等第 $t-1$ 步", "the same $W_h$, $W_x$\nat every step;\nstep $t$ waits for step $t-1$"),
        fontsize=9, color=C["ink"], ha="center", linespacing=1.4)
figure(fig, "fig2_8_2")
plt.close(fig)
