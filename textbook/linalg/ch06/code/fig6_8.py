"""图 6.8.1：两连杆臂（UR5e 上臂 0.425 m、前臂 0.392 m）。左：肘关节角 θ₂ = 90°、45°、10°、0° 四个位形，
θ₂ = 0 时手臂伸直；右：雅可比行列式 det J = l₁l₂ sin θ₂ 随 θ₂ 的变化，θ₂ = 0、±180° 时为零（奇异位形）。"""
import math

import numpy as np

from _arm import ur5e_links
from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

l1, l2 = ur5e_links()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.2), gridspec_kw={"width_ratios": [1, 1.2]})
t1 = math.radians(30)
for deg, c in zip((90, 45, 10, 0), (BLUE, GREEN, "#c98f00", RED)):
    t2 = math.radians(deg)
    j = np.array([l1 * math.cos(t1), l1 * math.sin(t1)])
    p = j + l2 * np.array([math.cos(t1 + t2), math.sin(t1 + t2)])
    a1.plot([0, j[0], p[0]], [0, j[1], p[1]], "-o", color=c, lw=3, ms=5, label=f"θ₂ = {deg}°")
a1.plot(0, 0, "s", color=INK, ms=9)
a1.set_aspect("equal")
a1.set_xlim(-0.35, 0.85)
a1.set_ylim(-0.05, 0.75)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.legend(frameon=False, fontsize=9, loc="upper left")
th = np.linspace(-180, 180, 361)
a2.plot(th, l1 * l2 * np.sin(np.radians(th)), color=BLUE, lw=2)
for deg, c in zip((90, 45, 10, 0), (BLUE, GREEN, "#c98f00", RED)):
    a2.plot(deg, l1 * l2 * math.sin(math.radians(deg)), "o", color=c, ms=7)
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xticks([-180, -90, 0, 90, 180])
a2.set_xlabel(T("肘关节角 θ₂ / °", "elbow angle θ₂ / °"))
a2.set_ylabel("det J / m²")
for ax in (a1, a2):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig6_8_1")
