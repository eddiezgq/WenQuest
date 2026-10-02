"""5.2 节的示意图。

图 5.2.1：读齐次变换矩阵：前三列是 {b} 的三根轴在 {a} 中的分量（末位补 0），第四列是 {b} 的原点（末位补 1）。
图 5.2.2：同一个位移作用在点和自由矢量上：点 (p, 1) 既转又移；方向 (v, 0) 只转不移。
"""
import math

import numpy as np

from _fig5 import AX, C, arrow, frame2, plane
from _frames import DEG
from bookout import T as TT, figure, style

plt = style()

# ---------------------------------------------------------------- 图 5.2.1
fig = plt.figure(figsize=(8.2, 3.6))
ax = fig.add_axes([0.0, 0.0, 0.46, 1.0])
ang = 30 * DEG
Ob = np.array([1.9, 1.0])
frame2(ax, (0, 0), 0, 1.0, "{a}", sub="a", name_off=(-0.15, -0.2))
frame2(ax, Ob, ang, 0.9, "{b}", sub="b", name_off=(0.12, -0.3))
arrow(ax, (0, 0), Ob, C["accent"], 1.6, ls="--")
ax.text(0.85, 0.25, r"$p_{ab}$", color=C["accent"], fontsize=13)
ax.text(Ob[0] + 0.62, Ob[1] + 0.12, TT("第 1 列", "column 1"), color=AX[0], fontsize=10)
ax.text(Ob[0] - 1.05, Ob[1] + 0.4, TT("第 2 列", "column 2"), color=AX[1], fontsize=10)
plane(ax, (-0.45, 3.1), (-0.5, 2.1))

ax2 = fig.add_axes([0.48, 0.05, 0.52, 0.9])
ax2.axis("off")
ax2.set_xlim(0, 5.2)
ax2.set_ylim(0, 4.6)
cols = [AX[0], AX[1], AX[2], C["accent"]]
ents = [[r"$r_{11}$", r"$r_{12}$", r"$r_{13}$", r"$p_1$"], [r"$r_{21}$", r"$r_{22}$", r"$r_{23}$", r"$p_2$"],
        [r"$r_{31}$", r"$r_{32}$", r"$r_{33}$", r"$p_3$"], ["0", "0", "0", "1"]]
x0, y0, w, h = 0.7, 0.8, 0.9, 0.75
for j in range(4):
    from matplotlib.patches import FancyBboxPatch
    ax2.add_patch(FancyBboxPatch((x0 + j * w + 0.06, y0 + 0.06), w - 0.12, 4 * h - 0.12, boxstyle="round,pad=0.02",
                                 facecolor=cols[j], alpha=0.12, edgecolor=cols[j], lw=1.0))
    for i in range(4):
        ax2.text(x0 + (j + 0.5) * w, y0 + (3.5 - i) * h, ents[i][j], ha="center", va="center", fontsize=13,
                 color=C["muted"] if i == 3 else C["ink"])
ax2.plot([x0 - 0.05, x0 - 0.15, x0 - 0.15, x0 - 0.05], [y0 + 4 * h, y0 + 4 * h, y0, y0], color=C["ink"], lw=1.2)
ax2.plot([x0 + 4 * w + 0.05, x0 + 4 * w + 0.15, x0 + 4 * w + 0.15, x0 + 4 * w + 0.05], [y0 + 4 * h, y0 + 4 * h, y0, y0],
         color=C["ink"], lw=1.2)
ax2.text(0.05, y0 + 2 * h, r"$T_{ab}=$", fontsize=14, va="center")
labs = [TT("$x_b$ 轴", "axis $x_b$"), TT("$y_b$ 轴", "axis $y_b$"), TT("$z_b$ 轴", "axis $z_b$"), TT("原点 $O_b$", "origin $O_b$")]
for j in range(4):
    ax2.text(x0 + (j + 0.5) * w, y0 + 4 * h + 0.25, labs[j], ha="center", fontsize=10, color=cols[j])
ax2.text(x0 + 1.5 * w, 0.3, TT("方向：末位补 0", "directions: last entry 0"), ha="center", fontsize=9.5, color=C["muted"])
ax2.text(x0 + 3.5 * w, 0.3, TT("点：末位补 1", "a point: last entry 1"), ha="center", fontsize=9.5, color=C["muted"])
figure(fig, "fig5_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 5.2.2
fig, ax = plt.subplots(figsize=(6.4, 4.0))
th, d = 60 * DEG, np.array([2.4, 0.6])
R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
body = np.array([[0.2, 0.2], [1.4, 0.2], [1.4, 0.9], [0.2, 0.9], [0.2, 0.2]])
P = np.array([1.4, 0.9])
v = np.array([0.7, 0.0])
frame2(ax, (0, 0), 0, 0.8, "{a}", sub="a", name_off=(-0.15, -0.25), alpha=0.9)
ax.fill(*body.T, color="#d9dee2", alpha=0.6)
ax.plot(*body.T, color=C["muted"], lw=0.9, ls="--")
b2 = (R @ body.T).T + d
ax.fill(*b2.T, color="#f3e2b3", alpha=0.7)
ax.plot(*b2.T, color=C["accent"], lw=1.1)
P2 = R @ P + d
ax.plot(*P, "o", color=C["ink"], ms=5)
ax.plot(*P2, "o", color=C["ink"], ms=5)
ax.text(P[0] + 0.07, P[1] + 0.05, "P", fontsize=12)
ax.text(P2[0] + 0.08, P2[1] + 0.02, "P′", fontsize=12)
arrow(ax, P, P2, C["ink"], 1.0, ls=":")
# 自由矢量：画在物体上；位移后只转不移
arrow(ax, (0.4, 0.55), (0.4, 0.55) + v, "#1f77b4", 2.0)
q = R @ np.array([0.4, 0.55]) + d
arrow(ax, q, q + R @ v, "#1f77b4", 2.0)
ax.text(0.42, 0.62, r"$v$", color="#1f77b4", fontsize=13)
ax.text(*(q + R @ v * 0.45 + np.array([-0.32, 0.0])), r"$v'$", color="#1f77b4", fontsize=13)
ax.text(-0.3, -0.75, TT(r"点：$(p,\,1)$ 经 $T$ 既转又移", r"a point $(p,\,1)$: turned and moved by $T$"), fontsize=10.5)
ax.text(-0.3, -1.05, TT(r"方向：$(v,\,0)$ 经 $T$ 只转不移，$v' = Rv$", r"a direction $(v,\,0)$: only turned, $v' = Rv$"),
        fontsize=10.5, color="#1f77b4")
ax.text(2.6, 2.6, TT("位移后", "after the displacement"), fontsize=9.5, color=C["accent"])
ax.text(0.25, 1.0, TT("位移前", "before"), fontsize=9.5, color=C["muted"])
plane(ax, (-0.45, 3.4), (-1.2, 2.9))
figure(fig, "fig5_2_2")
plt.close(fig)
