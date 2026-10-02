"""图 12.4.1：指数积的读法（算例 12.2.1 的关节角）。
(a) 从里往外：关节 1 转过 30° 后，关节 2、3 的轴（红点）跟着移动，q2 → q2′；
(b) 写反次序：先绕零位的 q1、q2、q3 依次转，末端落到工作空间（虚线圆）以外。
"""
import math

import numpy as np

from _fig12 import C, L, arc_arrow, arm_points, draw_arm, plane
from bookout import T, figure, style

plt = style()
th = [math.radians(30), math.radians(45), math.radians(-90)]
zero, _ = arm_points([0, 0, 0])
reach = sum(L)

fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.0))
# (a)
ax = axs[0]
plane(ax, (-0.2, 1.05), (-0.25, 0.75))
after1, _ = arm_points([th[0], 0, 0])
final, _ = arm_points(th)
draw_arm(ax, zero, C["muted"], lw=3, alpha=0.35, ls="--", joints=False)
draw_arm(ax, after1, C["muted"], lw=4, alpha=0.6)
draw_arm(ax, final, C["accent"], lw=5)
for k in (1, 2):
    ax.plot(*zero[k], "o", color=C["muted"], ms=6, zorder=8)
    ax.plot(*after1[k], "o", color=C["x"], ms=7, zorder=8)
    ax.annotate("", xy=after1[k], xytext=zero[k], arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.0, ls=":",
                                                                   connectionstyle="arc3,rad=0.25", mutation_scale=9))
ax.text(zero[1][0] - 0.03, zero[1][1] - 0.08, "$q_2$", fontsize=11)
ax.text(after1[1][0] - 0.1, after1[1][1] + 0.03, "$q_2'$", fontsize=11, color=C["x"])
ax.text(after1[2][0] - 0.02, after1[2][1] + 0.05, "$q_3'$", fontsize=11, color=C["x"])
arc_arrow(ax, (0, 0), 0.14, 0, th[0], C["x"])
ax.set_title(T("(a) 从里往外：关节 1 转过 30°，外侧各轴跟着移动",
               "(a) Inside out: joint 1 turns 30°; outer axes follow"), fontsize=10)

# (b)
ax = axs[1]
plane(ax, (-0.25, 1.6), (-0.6, 0.85))
t = np.linspace(0, 2 * math.pi, 200)
ax.plot(reach * np.cos(t), reach * np.sin(t), color=C["muted"], lw=1, ls="--")
ax.text(-0.2, -0.55, T(f"工作空间边界：半径 {reach:.3f} m", f"workspace boundary: radius {reach:.3f} m"), fontsize=9, color=C["muted"])
draw_arm(ax, final, C["accent"], lw=4)


def exp_about(c, a, p):
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return c + R @ (p - c)


# 写反：e^{S3θ3} e^{S2θ2} e^{S1θ1} M，从右往左作用在末端上
p = zero[-1].copy()
trace = [p.copy()]
for c, a in ((zero[0], th[0]), (zero[1], th[1]), (zero[2], th[2])):
    p = exp_about(c, a, p)
    trace.append(p.copy())
trace = np.array(trace)
ax.plot(trace[:, 0], trace[:, 1], color=C["x"], lw=1.2, ls=":", marker="o", ms=4)
ax.plot(*trace[-1], "X", color=C["x"], ms=10)
ax.text(trace[-1][0] - 0.3, trace[-1][1] + 0.07, T("写反次序得到的“末端”", "“end-effector” from the\nreversed order"), fontsize=9.5, color=C["x"])
ax.text(final[-1][0] - 0.38, final[-1][1] + 0.06, T("正确的末端", "correct end-effector"), fontsize=9.5, color=C["accent"])
for k in range(3):
    ax.plot(*zero[k], "o", color=C["muted"], ms=5)
ax.set_title(T("(b) 写反次序：绕已经不在那里的轴转动", "(b) Reversed order: turning about axes no longer there"), fontsize=10)
figure(fig, "fig12_4_1")
plt.close(fig)
