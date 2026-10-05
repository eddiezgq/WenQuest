"""图 8.3.1：三连杆平面臂 J θ̇ = v（2 个方程、3 个未知数）的全部解：关节速度空间 ℝ³ 中的一条直线
θ̇ = θ̇ₚ + t n，与过原点的零空间直线（自运动）平行。"""
import math

import numpy as np
import scipy.linalg as sla

from _fig import BLUE, GREEN, INK, RED, T, figure, plt

L = [0.3, 0.3, 0.3]
th = np.radians([30.0, 45.0, -60.0])
c = np.cumsum(th)
J = np.array([[-sum(L[k] * math.sin(c[k]) for k in range(i, 3)) for i in range(3)],
              [sum(L[k] * math.cos(c[k]) for k in range(i, 3)) for i in range(3)]])
qp = np.linalg.lstsq(J, np.array([0.1, 0.0]), rcond=None)[0]
n = sla.null_space(J)[:, 0]
t = np.linspace(-1.0, 1.0, 2)
fig = plt.figure(figsize=(6.2, 5.0))
ax = fig.add_subplot(projection="3d")
ax.plot(*(np.outer(t, n).T), color=GREEN, lw=2.5, label=T("零空间：自运动", "null space: self-motion"))
ax.plot(*((qp + np.outer(t, n)).T), color=BLUE, lw=2.5, label=T("全部解：θ̇ₚ + t n", "all solutions: θ̇ₚ + t n"))
ax.quiver(0, 0, 0, *qp, color=RED, lw=2, arrow_length_ratio=0.1)
ax.text(*(qp * 1.1), "θ̇ₚ", color=RED, fontsize=12)
ax.scatter([0], [0], [0], color=INK, s=20)
ax.set_xlabel("θ̇₁")
ax.set_ylabel("θ̇₂")
ax.set_zlabel("θ̇₃")
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.view_init(elev=18, azim=-50)
fig.tight_layout()
figure(fig, "fig8_3_1")
