"""图 9.3.1：柯西中值定理——左：两个关节同时运动时关节空间里的路径 (θ₁(t), θ₂(t))，弦与 ξ 处的切线平行；
右：速度之比 θ₂′/θ₁′ 随时间的变化，与增量之比 Δθ₂/Δθ₁ = 1/2 相交于 ξ。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

Tt, D1, D2 = 2.0, 90.0, 45.0
t = np.linspace(0.001, Tt - 0.001, 500)
s = t / Tt
th1 = D1 * (10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5)
th2 = D2 * (3 * s ** 2 - 2 * s ** 3)
w1 = D1 / Tt * 30 * s ** 2 * (1 - s) ** 2
w2 = D2 / Tt * 6 * s * (1 - s)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
a1.plot(th1, th2, color=INK, lw=2, label=T("路径", "path"))
a1.plot([0, D1], [0, D2], color=RED, lw=1.5, label=T("弦：Δθ₂/Δθ₁ = 1/2", "chord: Δθ₂/Δθ₁ = 1/2"))
for xi in (Tt * (1 - math.sqrt(0.2)) / 2, Tt * (1 + math.sqrt(0.2)) / 2):
    si = xi / Tt
    p1 = D1 * (10 * si ** 3 - 15 * si ** 4 + 6 * si ** 5)
    p2 = D2 * (3 * si ** 2 - 2 * si ** 3)
    xx = np.array([p1 - 18, p1 + 18])
    a1.plot(xx, p2 + 0.5 * (xx - p1), color=BLUE, lw=1.2, ls="--")
    a1.plot([p1], [p2], "o", color=ACC, ms=6)
a1.set_xlabel("θ₁ / (°)")
a1.set_ylabel("θ₂ / (°)")
a1.set_aspect("equal")
a1.set_title(T("关节空间里的路径：切线与弦平行", "Path in joint space: tangent parallel to chord"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="upper left")
clean(a1, zero=False)
a2.plot(t, w2 / w1, color=INK, lw=2, label="θ₂′/θ₁′")
a2.axhline(0.5, color=RED, lw=1.3, label="Δθ₂/Δθ₁")
a2.set_ylim(0, 2.5)
a2.set_xlabel("t / s")
a2.set_title(T("速度之比在 ξ 处等于增量之比", "Velocity ratio equals increment ratio at ξ"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig9_3_1")
