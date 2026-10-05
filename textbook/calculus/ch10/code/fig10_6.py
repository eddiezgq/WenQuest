"""图 10.6.1：左：|r′(θ₂)| 随肘关节角的变化，最大值 l₂ 在 cos θ₂ = −l₂/l₁ 处；右：障碍物到五次多项式换道路径的最近点，
连线与路径垂直。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _path import lane
from _traj import ur5e_links

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
l1, l2 = ur5e_links()
th = np.linspace(0, np.pi, 600)
r = np.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * np.cos(th))
a1.plot(np.degrees(th), l1 * l2 * np.sin(th) / r * 1000, color=INK, lw=2)
ts = math.acos(-l2 / l1)
a1.plot([math.degrees(ts)], [l2 * 1000], "o", color=ACC, ms=7)
a1.axhline(l2 * 1000, color=RED, lw=0.8, ls="--")
a1.set_xlabel(T("肘关节角 θ₂ / (°)", "elbow angle θ₂ / (°)"))
a1.set_ylabel("|r′| / (mm/rad)")
a1.set_title(T("最大值恰为 l₂，在接近折叠处取得", "Maximum equals l₂, near the folded pose"), fontsize=10)
clean(a1, zero=False)
y, yp, ypp = lane("quintic", 1.0, 4.0)
x = np.linspace(0, 4, 400)
a2.plot(x, [y(v) for v in x], color=INK, lw=2)
ax_, by_ = 2.2, 0.75
xm = 2.2589062
a2.plot([ax_], [by_], "s", color=RED, ms=7)
a2.plot([xm], [y(xm)], "o", color=ACC, ms=6)
a2.plot([ax_, xm], [by_, y(xm)], color=RED, lw=1.2)
a2.set_aspect("equal")
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.set_title(T("障碍物到路径的最近点：连线垂直于路径", "Closest point: the segment is normal to the path"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig10_6_1")
