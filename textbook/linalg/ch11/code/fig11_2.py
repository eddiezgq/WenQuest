"""图 11.2.1：格拉姆–施密特的几何。左：b 减去它在 q₁ 方向上的投影，得到与 q₁ 垂直的 B；右：c 减去它在 q₁、q₂ 张成的平面上的投影，
得到与平面垂直的 C。a = (1, −1, 0)、b = (2, 0, −2)、c = (3, −3, 3)。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow3, figure, plt, view3

a, b, c = np.array([1.0, -1, 0]), np.array([2.0, 0, -2]), np.array([3.0, -3, 3])
q1 = a / np.linalg.norm(a)
pb = (q1 @ b) * q1
B = b - pb
q2 = B / np.linalg.norm(B)
pc = (q1 @ c) * q1 + (q2 @ c) * q2
C = c - pc
P1, _ = view3(45, 35.26)
P2, _ = view3(-20, 15)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8))
for ax, PP in ((ax1, None), (ax2, None)):
    ax.set_aspect("equal"); ax.axis("off")
arrow3(ax1, P1, (0, 0, 0), q1, RED, "q₁", lw=2.6)
arrow3(ax1, P1, (0, 0, 0), b, BLUE, "b", off=(0.15, 0.0))
arrow3(ax1, P1, (0, 0, 0), pb, MUTED, "(q₁·b)q₁ = a", lw=1.4, size=10, off=(-0.3, 0.15))
arrow3(ax1, P1, pb, b, GREEN, "B = b − (q₁·b)q₁", size=11, off=(-1.6, 0.25))
m = 0.25
ax1.plot(*np.c_[P1(pb - m * q1), P1(pb - m * q1 + m * B / np.linalg.norm(B)), P1(pb + m * B / np.linalg.norm(B))], color=INK, lw=1)
ax1.set_title(T("第 2 步：从 b 中减去 q₁ 方向的分量", "step 2: remove from b its component along q₁"), fontsize=11)
corners = [P2(s * q1 + t * q2) for s, t in ((-1.5, -3.0), (5.5, -3.0), (5.5, 1.5), (-1.5, 1.5))]
ax2.add_patch(plt.Polygon(corners, closed=True, fc=ACC, alpha=0.2, ec=ACC))
arrow3(ax2, P2, (0, 0, 0), q1, RED, "q₁", lw=2.6, off=(0.1, -0.3))
arrow3(ax2, P2, (0, 0, 0), q2, GREEN, "q₂", lw=2.6)
arrow3(ax2, P2, (0, 0, 0), c, BLUE, "c", off=(0.15, 0.05))
arrow3(ax2, P2, (0, 0, 0), pc, MUTED, T("c 在平面上的投影", "projection of c"), lw=1.4, size=10, off=(0.05, -0.4))
arrow3(ax2, P2, pc, c, ACC)
u, w = -pc / np.linalg.norm(pc), C / np.linalg.norm(C)
ax2.plot(*np.c_[P2(pc + m * u), P2(pc + m * u + m * w), P2(pc + m * w)], color=INK, lw=1)
ax2.text(*(P2((pc + c) / 2) + np.array([-0.5, 0.15])), "C", color=ACC, fontsize=13)
ax2.set_title(T("第 3 步：从 c 中减去它在 q₁、q₂ 平面上的投影", "step 3: remove from c its projection onto the q₁q₂ plane"), fontsize=11)
for ax, PP, pts in ((ax1, P1, [a, b, pb, np.zeros(3), q1]), (ax2, P2, [c, pc, q1, q2, np.zeros(3)])):
    ax.plot(*PP(np.zeros(3)), "o", color=INK, ms=4)
    pp = np.array([PP(v) for v in pts] + ([*corners] if ax is ax2 else []))
    lo, hi = pp.min(0), pp.max(0)
    ax.set_xlim(lo[0] - 0.8, hi[0] + 1.6); ax.set_ylim(lo[1] - 0.6, hi[1] + 0.6)
figure(fig, "fig11_2_1")
