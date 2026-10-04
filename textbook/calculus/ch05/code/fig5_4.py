"""图 5.4.1：介值定理与零点定理，以及条件不满足时的反例；图 5.4.2：两节连杆能伸到的距离与四足机器人的“摆正角”。"""
import math

import numpy as np

from _arm import L1, L2
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
x = np.linspace(0, 4, 400)
f = lambda x: 1 + 0.9 * np.sin(1.4 * x) + 0.35 * x
ax = axs[0]
ax.plot(x, f(x), color=BLUE, lw=2)
C = 1.6
ax.axhline(C, color=RED, lw=1, ls="--")
roots = x[:-1][np.diff(np.sign(f(x) - C)) != 0]
for r in roots:
    ax.plot([r], [C], "o", color=RED, ms=5)
ax.text(4.05, C, "$C$", color=RED, va="center")
ax.set_xticks([0, 4])
ax.set_xticklabels(["$a$", "$b$"])
ax.set_title(T("介值定理：介于 f(a)、f(b) 之间的 C 都能取到", "IVT: every C between f(a) and f(b) is attained"), fontsize=9.5)
clean(ax, zero=False)
ax = axs[1]
xx = np.linspace(0.05, 1, 300)
ax.plot(xx, 1 / xx, color=BLUE, lw=2)
ax.plot([1], [1], "o", color=BLUE, ms=5)
ax.set_ylim(0, 20)
ax.set_title(T("(0, 1] 上的 1/x：无界，没有最大值", "1/x on (0, 1]: unbounded, no maximum"), fontsize=9.5)
clean(ax, zero=False)
ax = axs[2]
xl, xr = np.linspace(-1, 0, 100), np.linspace(0, 1, 100)
ax.plot(xl, -0.5 + 0 * xl, color=BLUE, lw=2)
ax.plot(xr[1:], 0.5 + 0 * xr[1:], color=BLUE, lw=2)
ax.plot([0], [-0.5], "o", color=BLUE, ms=5)
ax.plot([0], [0.5], "o", mfc="white", mec=BLUE, ms=5)
ax.axhline(0, color=RED, lw=1, ls="--")
ax.set_ylim(-1, 1)
ax.set_title(T("有间断：两端异号，却没有零点", "With a jump: signs differ, yet no zero"), fontsize=9.5)
clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig5_4_1")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
t2 = np.linspace(0, math.pi, 400)
r = np.sqrt(L1 ** 2 + L2 ** 2 + 2 * L1 * L2 * np.cos(t2))
a1.plot(np.degrees(t2), r * 1000, color=BLUE, lw=2)
d = 600
t2s = math.degrees(math.acos((0.36 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)))
a1.axhline(d, color=RED, lw=1, ls="--")
a1.plot([t2s], [d], "o", color=RED, ms=6)
a1.set_xlabel(T("肘关节角 θ₂ / (°)", "elbow angle θ₂ / (°)"))
a1.set_ylabel(T("腕心到肩的距离 r / mm", "wrist distance r / mm"))
rmax, rmin = (L1 + L2) * 1000, abs(L1 - L2) * 1000
a1.set_title(T(f"r(θ₂) 连续，从 {rmax:.0f} mm 降到 {rmin:.0f} mm，其间每个距离都能取到", "r(θ₂) is continuous: every distance in between is reached"), fontsize=9.5)
clean(a1, zero=False)
z = lambda x, y: 0.03 * np.sin(2.1 * x + 0.4) * np.cos(1.7 * y) + 0.02 * np.sin(3.3 * x * y + 1.0) + 0.015 * x
rho = 0.35


def D(phi):
    h = [z(rho * np.cos(phi + k * math.pi / 2), rho * np.sin(phi + k * math.pi / 2)) for k in range(4)]
    return h[0] + h[2] - h[1] - h[3]


ph = np.linspace(0, 2 * math.pi, 721)
a2.plot(np.degrees(ph), D(ph) * 1000, color=ACC, lw=2)
a2.axvline(90, color=MUTED, lw=0.8, ls=":")
a2.set_xticks([0, 90, 180, 270, 360])
a2.set_xlabel(T("机身转过的角 φ / (°)", "body rotation φ / (°)"))
a2.set_ylabel(T("第 4 只脚离地高度 D / mm", "gap of leg 4, D / mm"))
a2.set_title(T("D(φ + 90°) = −D(φ)：0° 到 90° 之间必有 D = 0", "D(φ + 90°) = −D(φ): a zero lies in [0°, 90°]"), fontsize=9.5)
clean(a2)
fig.tight_layout()
figure(fig, "fig5_4_2")
