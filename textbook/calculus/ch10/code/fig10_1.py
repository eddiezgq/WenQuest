"""图 10.1.1：左：关节阶跃响应 ζ = 0.6（有超调，单调区间交替）与 ζ = 1（单调上升）；右：腕心距离 r(θ₂) 在 [0°, 180°] 上严格递减，
给定距离 0.6 m 时肘关节角唯一。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import ur5e_links

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
wn = 10.0
t = np.linspace(0, 1.2, 600)
z = 0.6
s = math.sqrt(1 - z * z)
wd = wn * s
q = 1 - np.exp(-z * wn * t) * (np.cos(wd * t) + z / s * np.sin(wd * t))
qc = 1 - np.exp(-wn * t) * (1 + wn * t)
for k in range(4):
    lo, hi = k * math.pi / wd, min((k + 1) * math.pi / wd, 1.2)
    if lo < 1.2:
        a1.axvspan(lo, hi, color=GREEN if k % 2 == 0 else RED, alpha=0.08, lw=0)
a1.plot(t, q, color=BLUE, lw=2, label="ζ = 0.6")
a1.plot(t, qc, color=INK, lw=2, ls="--", label=T("ζ = 1（单调）", "ζ = 1 (monotone)"))
a1.set_xlabel("t / s")
a1.set_ylabel("q(t)")
a1.set_title(T("q′ > 0 的区间递增（绿），q′ < 0 的区间递减（红）", "Increasing where q′ > 0 (green), decreasing where q′ < 0 (red)"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right")
clean(a1, zero=False)
l1, l2 = ur5e_links()
th = np.linspace(0, np.pi, 400)
r = np.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * np.cos(th))
a2.plot(np.degrees(th), r, color=INK, lw=2)
th0 = math.acos((0.36 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2))
a2.axhline(0.6, color=RED, lw=1, ls="--")
a2.plot([math.degrees(th0)], [0.6], "o", color=ACC, ms=7)
a2.set_xlabel(T("肘关节角 θ₂ / (°)", "elbow angle θ₂ / (°)"))
a2.set_ylabel("r / m")
a2.set_title(T("r 严格递减：每个距离只对应一个肘关节角", "r strictly decreasing: one elbow angle per distance"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig10_1_1")
