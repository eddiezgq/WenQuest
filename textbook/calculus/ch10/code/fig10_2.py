"""图 10.2.1：左：ζ = 0.6 的阶跃响应，峰值时刻 t_p = π/ω_d 处 q′ = 0、q″ < 0；右：超调量随阻尼比的变化，超调 5% 对应 ζ ≈ 0.69。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
wn, z = 10.0, 0.6
s = math.sqrt(1 - z * z)
wd = wn * s
t = np.linspace(0, 1.2, 600)
q = 1 - np.exp(-z * wn * t) * (np.cos(wd * t) + z / s * np.sin(wd * t))
tp = math.pi / wd
Mp = math.exp(-z * math.pi / s)
a1.plot(t, q, color=BLUE, lw=2)
a1.axhline(1, color=MUTED, lw=0.8)
a1.plot([tp], [1 + Mp], "o", color=ACC, ms=7)
a1.plot([tp - 0.12, tp + 0.12], [1 + Mp, 1 + Mp], color=RED, lw=1.5)
a1.annotate("$t_p = \\pi/\\omega_d$", (tp, 1 + Mp), xytext=(tp + 0.15, 0.88), fontsize=10, arrowprops=dict(arrowstyle="->", color=MUTED))
a1.set_xlabel("t / s")
a1.set_ylabel("q(t)")
a1.set_title(T("峰值处切线水平，曲线向下弯", "At the peak: horizontal tangent, bending down"), fontsize=10)
clean(a1, zero=False)
zz = np.linspace(0.05, 0.99, 300)
a2.plot(zz, 100 * np.exp(-zz * np.pi / np.sqrt(1 - zz ** 2)), color=INK, lw=2)
zr = 0.6901
a2.axhline(5, color=RED, lw=1, ls="--")
a2.plot([zr], [5], "o", color=ACC, ms=7)
a2.set_xlabel(T("阻尼比 ζ", "damping ratio ζ"))
a2.set_ylabel(T("超调量 / %", "overshoot / %"))
a2.set_title(T("超调不超过 5% 要求 ζ ≥ 0.69", "Overshoot ≤ 5% needs ζ ≥ 0.69"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig10_2_1")
