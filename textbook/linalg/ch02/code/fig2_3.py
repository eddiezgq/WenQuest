"""图 2.3.1：点积的几何意义——u·v = ‖u‖‖v‖cos θ；夹角为锐角、直角、钝角时点积为正、零、负。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt
from matplotlib.patches import Arc

fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.8))
u = np.array([2.2, 0.0])
cases = [(math.radians(40), T("锐角：u·v > 0", "acute: u·v > 0")), (math.radians(90), T("直角：u·v = 0", "right: u·v = 0")),
         (math.radians(135), T("钝角：u·v < 0", "obtuse: u·v < 0"))]
for ax, (th, name) in zip(axs, cases):
    v = 1.8 * np.array([math.cos(th), math.sin(th)])
    arrow(ax, u, BLUE, None, lw=2.4)
    arrow(ax, v, GREEN, None, lw=2.4)
    proj = (u @ v) / (u @ u) * u
    ax.plot([v[0], proj[0]], [v[1], proj[1]], color=MUTED, ls="--", lw=0.9)
    if abs(proj[0]) > 1e-9:
        ax.plot([0, proj[0]], [-0.12, -0.12], color=RED, lw=3.5, solid_capstyle="butt")
        ax.text(proj[0] / 2, -0.42, r"$\Vert\boldsymbol{v}\Vert\cos\theta$", color=RED, ha="center", fontsize=11)
    ax.add_patch(Arc((0, 0), 0.8, 0.8, theta1=0, theta2=math.degrees(th), color=INK, lw=1))
    ax.text(0.5 * math.cos(th / 2), 0.5 * math.sin(th / 2), r"$\theta$", fontsize=12)
    ax.text(u[0] + 0.05, 0.1, r"$\boldsymbol{u}$", color=BLUE, fontsize=13)
    ax.text(v[0] + (0.08 if v[0] >= 0 else -0.3), v[1] + 0.05, r"$\boldsymbol{v}$", color=GREEN, fontsize=13)
    ax.set_xlim(-1.6, 2.7)
    ax.set_ylim(-0.7, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(name, fontsize=11)
fig.tight_layout()
figure(fig, "fig2_3_1")
