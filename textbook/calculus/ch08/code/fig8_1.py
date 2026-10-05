"""图 8.1.1：微分与增量——腕心距离 r(θ₂) 在 60° 处：Δr 与 dr（切线的增量）；|Δr − dr| 与 Δθ² 成正比。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import ur5e_links

l1, l2 = ur5e_links()
r = lambda t: np.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * np.cos(t)) * 1000
dr = lambda t: -l1 * l2 * np.sin(t) / np.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * np.cos(t)) * 1000
t0, d = math.radians(60), 0.5
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
t = np.linspace(t0 - 0.3, t0 + 0.7, 300)
a1.plot(np.degrees(t), r(t), color=INK, lw=2, label="$r(\\theta_2)$")
a1.plot(np.degrees(t), r(t0) + dr(t0) * (t - t0), color=BLUE, lw=1.2, ls="--", label=T("切线", "tangent"))
x0, x1 = math.degrees(t0), math.degrees(t0 + d)
a1.plot([x0, x1], [r(t0), r(t0)], color=MUTED, lw=1)
a1.annotate("", xy=(x1, r(t0 + d)), xytext=(x1, r(t0)), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.5))
a1.annotate("", xy=(x1 + 1.2, r(t0) + dr(t0) * d), xytext=(x1 + 1.2, r(t0)), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.5))
a1.text(x1 - 1, (r(t0) + r(t0 + d)) / 2, "$\\Delta r$", color=RED, ha="right")
a1.text(x1 + 2, r(t0) + dr(t0) * d / 2, "$dr$", color=BLUE)
a1.text((x0 + x1) / 2, r(t0) + 4, "$\\Delta\\theta = d\\theta$", ha="center", fontsize=9)
a1.plot([x0], [r(t0)], "o", color=INK, ms=5)
a1.set_xlabel(T("肘关节角 θ₂ / (°)", "elbow angle θ₂ / (°)"))
a1.set_ylabel("r / mm")
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("Δr 是曲线的增量，dr 是切线的增量", "Δr: rise of the curve; dr: rise of the tangent"), fontsize=10)
clean(a1, zero=False)
hs = 10.0 ** np.linspace(-4, -0.5, 40)
gap = np.abs(r(t0 + hs) - r(t0) - dr(t0) * hs)
a2.loglog(hs, gap, "o", color=RED, ms=4, label="$|\\Delta r - dr|$")
a2.loglog(hs, 88.21 * hs ** 2, color=MUTED, lw=1, label="$\\propto(\\Delta\\theta)^2$")
a2.loglog(hs, abs(dr(t0)) * hs, color=BLUE, lw=1, ls="--", label="$|dr|\\propto\\Delta\\theta$")
a2.set_xlabel(T("Δθ / rad", "Δθ / rad"))
a2.set_ylabel("mm")
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("Δr − dr 是比 Δθ 高阶的无穷小", "Δr − dr is of higher order than Δθ"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig8_1_1")
