"""图 12.2.1：空间形式的三步（算例 12.2.1，θ = (30°, 45°, −90°)）。
(a) e^[S3]θ3 M：只转关节 3；(b) 再左乘 e^[S2]θ2：绕零位时的 q2 转；(c) 再左乘 e^[S1]θ1：绕原点转。
每一步的转轴（圆点）都还在零位时的位置。
"""
import math

import numpy as np

from _fig12 import C, arc_arrow, arm_points, draw_arm, plane
from bookout import T, figure, style

plt = style()
th = [math.radians(30), math.radians(45), math.radians(-90)]
zero, _ = arm_points([0, 0, 0])
stages = [arm_points([0, 0, th[2]])[0], arm_points([0, th[1], th[2]])[0], arm_points(th)[0]]
prev = [zero, stages[0], stages[1]]
names = [T(r"(a) $e^{[\mathcal{S}_3]\theta_3}M$：绕 $q_3$ 转 −90°", r"(a) $e^{[\mathcal{S}_3]\theta_3}M$: turn −90° about $q_3$"),
         T(r"(b) 左乘 $e^{[\mathcal{S}_2]\theta_2}$：绕 $q_2$ 转 45°", r"(b) premultiply by $e^{[\mathcal{S}_2]\theta_2}$: turn 45° about $q_2$"),
         T(r"(c) 左乘 $e^{[\mathcal{S}_1]\theta_1}$：绕 $q_1$ 转 30°", r"(c) premultiply by $e^{[\mathcal{S}_1]\theta_1}$: turn 30° about $q_1$")]
centers = [zero[2], zero[1], zero[0]]
angles = [th[2], th[1], th[0]]

fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.3))
for k, ax in enumerate(axs):
    plane(ax, (-0.1, 1.0), (-0.25, 0.75))
    draw_arm(ax, zero, C["muted"], lw=3, alpha=0.3, ls="--", joints=False)
    draw_arm(ax, prev[k], C["muted"], lw=4, alpha=0.5)
    draw_arm(ax, stages[k], C["accent"], lw=5)
    c = centers[k]
    ax.plot(*c, "o", color=C["x"], ms=7, zorder=8)
    a0 = math.atan2(*(prev[k][-1] - c)[::-1])
    arc_arrow(ax, c, 0.13, a0, a0 + angles[k], C["x"])
    tip = stages[k][-1]
    ax.plot(*tip, "o", color=C["ink"], ms=4, zorder=9)
    ax.text(tip[0] + 0.03, tip[1] - (0.09 if k == 0 else -0.03), f"({tip[0]:.3f}, {tip[1]:.3f})", fontsize=8.5, color=C["ink"])
    ax.set_title(names[k], fontsize=10)
fig.text(0.5, 0.01, T("红点：这一步转动所绕的点，仍在零位时的位置；灰色：上一步的结果；虚线：零位",
                       "Red dot: the point this step turns about, still where it was in the home configuration;\ngrey: result of the previous step; dashed: home configuration"), ha="center", fontsize=9)
figure(fig, "fig12_2_1")
plt.close(fig)
