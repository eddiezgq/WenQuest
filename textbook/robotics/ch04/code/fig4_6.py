"""4.6 节的示意图。

图 4.6.1：转角 θ 从 0 到 4π——旋转矩阵（以 r11 为例，绕 (1,1,1)/√3 转动）以 2π 为周期，四元数实部 q0 = cos(θ/2) 以 4π 为周期。
"""
import math

import numpy as np

from _rot import C, rot_axis
from bookout import figure, style

plt = style()
w = np.ones(3) / math.sqrt(3)
t = np.linspace(0, 4 * math.pi, 400)
r11 = [rot_axis(w, x)[0, 0] for x in t]
q0 = np.cos(t / 2)

fig, ax = plt.subplots(figsize=(6.0, 3.2))
ax.plot(t / math.pi, r11, color=C["z"], lw=1.8, label=r"旋转矩阵元素 $r_{11}$")
ax.plot(t / math.pi, q0, color=C["accent"], lw=1.8, label=r"四元数实部 $q_0=\cos(\theta/2)$")
ax.axhline(0, color=C["muted"], lw=0.6)
for k in (2, 4):
    ax.axvline(k, color=C["muted"], lw=0.6, ls="--")
ax.annotate("转一圈：R 复原，\nq 变为 −q", xy=(2, -1), xytext=(2.25, -0.6), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
ax.annotate("转两圈：q 才复原", xy=(4, 1), xytext=(2.55, 0.72), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
ax.set_xticks([0, 1, 2, 3, 4])
ax.set_xticklabels(["0", "π", "2π", "3π", "4π"])
ax.set_xlabel("转角 θ")
ax.set_ylim(-1.15, 1.25)
ax.legend(loc="lower left", fontsize=9, frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig4_6_1")
plt.close(fig)
