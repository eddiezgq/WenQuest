"""图 5.6.1：一致连续——x² 在离原点越远处能用的 δ 越小；√x 一个 δ 处处可用；肘关节角 θ₂(r) 在伸直位置附近。"""
import math

import numpy as np

from _arm import L1, L2
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, axs = plt.subplots(1, 3, figsize=(13, 3.8))
eps = 0.6
ax = axs[0]
x = np.linspace(0, 3.2, 300)
ax.plot(x, x ** 2, color=INK, lw=2)
for x0, c in ((0.5, BLUE), (1.5, GREEN), (2.8, RED)):
    d = math.sqrt(x0 ** 2 + eps) - x0
    ax.axvspan(x0 - d, x0 + d, color=c, alpha=0.25)
    ax.axhspan(x0 ** 2 - eps, x0 ** 2 + eps, color=c, alpha=0.08)
ax.set_title(T("x²：同一个 ε，x 越大 δ 越小", "x²: same ε, smaller δ for larger x"), fontsize=10)
clean(ax, zero=False)
ax = axs[1]
x = np.linspace(0, 3.2, 300)
ax.plot(x, np.sqrt(x), color=INK, lw=2)
eps = 0.25
for x0, c in ((0.0, BLUE), (1.2, GREEN), (2.6, RED)):
    ax.axvspan(max(0, x0 - eps ** 2), x0 + eps ** 2, color=c, alpha=0.35)
    ax.axhspan(math.sqrt(x0) - eps, math.sqrt(x0) + eps, color=c, alpha=0.08)
ax.set_title(T("√x：δ = ε² 处处可用", "√x: δ = ε² works everywhere"), fontsize=10)
clean(ax, zero=False)
ax = axs[2]
R = L1 + L2
r = np.linspace(0.3, R, 2000)
c = np.clip((r ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2), -1, 1)
ax.plot(r * 1000, np.degrees(np.arccos(c)), color=ACC, lw=2)
ax.set_xlabel(T("腕心到肩的距离 r / mm", "wrist distance r / mm"))
ax.set_ylabel(T("肘关节角 θ₂ / (°)", "elbow angle θ₂ / (°)"))
ax.set_title(T("θ₂(r) 在 r = R 处切线竖直，但仍一致连续", "θ₂(r): vertical tangent at r = R, still uniformly continuous"), fontsize=10)
clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig5_6_1")
