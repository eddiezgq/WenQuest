"""3.5 节的示意图。

图 3.5.1：(a) 列维-奇维塔符号的记法：沿 1 → 2 → 3 的轮换方向读为 +1，逆着读为 −1，有重复指标为 0；
          (b) ε_ijk 的 27 个值按 k 分成三层，每层是一个 3×3 反对称矩阵（等于 −[e_k]）。
"""
import math

import numpy as np

from _vec import C, arrow2
from bookout import T, figure, style

plt = style()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2), gridspec_kw={"width_ratios": [1, 1.5]})
for ax in (ax1, ax2):
    ax.set_aspect("equal")
    ax.axis("off")
# (a) 轮换图
pos = {1: (0.0, 1.0), 2: (math.cos(math.radians(-30)), math.sin(math.radians(-30))), 3: (math.cos(math.radians(210)), math.sin(math.radians(210)))}
for k, (x, y) in pos.items():
    ax1.add_patch(plt.Circle((x, y), 0.17, fc="white", ec=C["ink"], lw=1.4, zorder=3))
    ax1.text(x, y, str(k), ha="center", va="center", fontsize=15, zorder=4)
for a_, b_ in ((1, 2), (2, 3), (3, 1)):
    p, q = np.array(pos[a_]), np.array(pos[b_])
    mid = (p + q) / 2
    out = mid / np.linalg.norm(mid) * 0.32
    arrow2(ax1, p + (q - p) * 0.2 + out * 0.4, q - (q - p) * 0.2 + out * 0.4, C["y"], 1.8)
    arrow2(ax1, q - (q - p) * 0.2 - out * 0.4, p + (q - p) * 0.2 - out * 0.4, C["x"], 1.4)
ax1.text(0.0, -0.05, T("顺着读：\n123、231、312\nε = +1", "with the arrows:\n123, 231, 312\nε = +1"), ha="center", va="center", fontsize=10, color=C["y"])
ax1.text(0.0, -1.05, T("逆着读：132、213、321，ε = −1；有重复指标，ε = 0", "against: 132, 213, 321, ε = −1; repeated index, ε = 0"),
         ha="center", fontsize=9.5, color=C["x"])
ax1.text(-1.25, 1.35, T("(a) 轮换次序与符号", "(a) Cyclic order and sign"), fontsize=10)
ax1.set_xlim(-1.3, 1.3)
ax1.set_ylim(-1.2, 1.45)

# (b) 三层
eps = np.zeros((3, 3, 3))
for i in range(3):
    for j in range(3):
        for k in range(3):
            if len({i, j, k}) == 3:
                eps[i, j, k] = np.linalg.det(np.eye(3)[[i, j, k]])
for kk in range(3):
    x0 = kk * 2.0
    ax2.text(x0 + 0.75, 2.55, rf"$k={kk + 1}$", ha="center", fontsize=12)
    ax2.plot([x0 + 0.02, x0, x0, x0 + 0.02], [2.3, 2.3, 0.2, 0.2], color=C["ink"], lw=1.1)
    ax2.plot([x0 + 1.48, x0 + 1.5, x0 + 1.5, x0 + 1.48], [2.3, 2.3, 0.2, 0.2], color=C["ink"], lw=1.1)
    for i in range(3):
        for j in range(3):
            v = int(eps[i, j, kk])
            col = C["y"] if v > 0 else C["x"] if v < 0 else C["muted"]
            ax2.text(x0 + 0.25 + 0.5 * j, 1.95 - 0.7 * i, f"{v:+d}" if v else "0", ha="center", va="center", fontsize=13, color=col)
    ax2.text(x0 + 0.75, -0.15, rf"$\varepsilon_{{ij{kk + 1}}}=-[\hat{{\boldsymbol{{e}}}}_{kk + 1}]_{{ij}}$", ha="center", fontsize=11)
ax2.text(-0.1, 2.95, T("(b) ε_ijk 的 27 个值：按 k 分为三层，第 i 行、第 j 列", "(b) The 27 values of ε_ijk in three layers k; row i, column j"), fontsize=10)
ax2.set_xlim(-0.2, 5.7)
ax2.set_ylim(-0.45, 3.15)
fig.subplots_adjust(wspace=0.08)
figure(fig, "fig3_5_1")
plt.close(fig)
