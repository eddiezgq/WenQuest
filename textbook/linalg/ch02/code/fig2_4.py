"""图 2.4.1：向一条直线投影——AGV 测得的位置向通道中心线投影，误差垂直于中心线；斜面输送带上重力的分解。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.4))
A, a, Q = np.array([2.0, 1.0]), np.array([4.0, 3.0]), np.array([5.0, 4.1])
b = Q - A
p = (a @ b) / (a @ a) * a
s = np.linspace(-0.3, 1.6, 2)
a1.fill_between([0, 10], [0, 0], [0, 0], color="white")
L = np.array([A + t * a for t in (-0.35, 1.5)])
off = 0.7 * np.array([-0.6, 0.8])
a1.fill([L[0, 0] + off[0], L[1, 0] + off[0], L[1, 0] - off[0], L[0, 0] - off[0]], [L[0, 1] + off[1], L[1, 1] + off[1], L[1, 1] - off[1], L[0, 1] - off[1]], color="#e9eef3", zorder=0)
a1.plot(L[:, 0], L[:, 1], color=MUTED, ls="-.", lw=1)
arrow(a1, a / 2.5, INK, None, start=A, lw=2.2)
arrow(a1, b, GREEN, None, start=A, lw=2.2)
arrow(a1, p, BLUE, None, start=A, lw=2.6)
arrow(a1, b - p, RED, None, start=A + p, lw=2.2)
a1.plot([A[0] + p[0] - 0.18 * 0.8, A[0] + p[0] - 0.18 * 0.8 - 0.18 * 0.6, A[0] + p[0] - 0.18 * 0.6], [A[1] + p[1] - 0.18 * 0.6, A[1] + p[1] - 0.18 * 0.6 + 0.18 * 0.8, A[1] + p[1] + 0.18 * 0.8], color=INK, lw=0.8)
a1.plot(*A, "o", color=INK, ms=5)
a1.plot(*Q, "o", color=GREEN, ms=6)
a1.text(A[0] + 0.1, A[1] - 0.45, "A", fontsize=11)
a1.text(Q[0] - 3.4, Q[1] + 0.3, T("AGV 实测位置 Q", "measured AGV position Q"), color=GREEN, fontsize=10)
a1.text(A[0] + 0.4, A[1] + 0.75, r"$\boldsymbol{a}$", fontsize=13)
a1.text(A[0] + 1.2, A[1] + 1.75, r"$\boldsymbol{b}$", color=GREEN, fontsize=13)
a1.text(A[0] + p[0] - 0.4, A[1] + p[1] - 0.75, r"$\boldsymbol{p}=\hat{x}\boldsymbol{a}$", color=BLUE, fontsize=13)
a1.text(A[0] + p[0] + 0.25, A[1] + p[1] + 0.25, r"$\boldsymbol{e}=\boldsymbol{b}-\boldsymbol{p}$", color=RED, fontsize=12)
a1.text(7.3, 6.6, T("通道中心线", "aisle centre line"), color=MUTED, fontsize=10)
a1.set_xlim(0.5, 9)
a1.set_ylim(0, 7.2)
a1.set_aspect("equal")
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("向通道中心线投影：e 垂直于 a", "Projection onto the aisle line: e ⟂ a"), fontsize=11)
th = math.radians(20)
t = np.array([math.cos(th), math.sin(th)])
n = np.array([-math.sin(th), math.cos(th)])
a2.plot([-0.2 * t[0] * 10, 1.6 * t[0] * 10 / 2.0], [-0.2 * t[1] * 10, 1.6 * t[1] * 10 / 2.0], color=INK, lw=2)
c = 4.0 * t + 0.35 * n
sq = np.array([c + 0.35 * (x * t + y * n) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))])
a2.fill(sq[:, 0], sq[:, 1], color="#f2d7a6", ec=INK, lw=1)
G = np.array([0, -2.6])
Gt = (G @ t) * t
Gn = G - Gt
arrow(a2, G, INK, None, start=c, lw=2.4)
arrow(a2, Gt, BLUE, None, start=c, lw=2.2)
arrow(a2, Gn, RED, None, start=c, lw=2.2)
a2.plot([c[0] + Gt[0], c[0] + G[0], c[0] + Gn[0]], [c[1] + Gt[1], c[1] + G[1], c[1] + Gn[1]], color=MUTED, ls=":", lw=0.9)
a2.text(c[0] + G[0] + 0.1, c[1] + G[1], r"$m\boldsymbol{g}$", fontsize=13)
a2.text(c[0] + Gt[0] - 1.4, c[1] + Gt[1] - 0.1, T("沿带面分量", "along the belt"), color=BLUE, fontsize=10)
a2.text(c[0] + Gn[0] + 0.15, c[1] + Gn[1] + 0.25, T("压向带面分量", "into the belt"), color=RED, fontsize=10)
a2.text(1.0, 0.1, "20°", fontsize=10)
a2.plot([-1, 8], [0, 0], color=MUTED, lw=0.6)
a2.set_xlim(-0.5, 8)
a2.set_ylim(-1.6, 3.6)
a2.set_aspect("equal")
a2.axis("off")
a2.set_title(T("斜面输送带：重力向带面方向投影", "Inclined belt: projecting gravity onto the belt direction"), fontsize=11)
for s_ in ("top", "right"):
    a1.spines[s_].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_4_1")
