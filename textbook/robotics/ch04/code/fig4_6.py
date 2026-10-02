"""4.6 节的示意图。

图 4.6.1：转角 θ 从 0 到 4π——旋转矩阵（以 r11 为例，绕 (1,1,1)/√3 转动）以 2π 为周期，四元数实部 q0 = cos(θ/2) 以 4π 为周期。
"""
import math

import numpy as np

from _rot import C, rot_axis
from bookout import T, figure, style

plt = style()
w = np.ones(3) / math.sqrt(3)
t = np.linspace(0, 4 * math.pi, 400)
r11 = [rot_axis(w, x)[0, 0] for x in t]
q0 = np.cos(t / 2)

fig, ax = plt.subplots(figsize=(6.0, 3.2))
ax.plot(t / math.pi, r11, color=C["z"], lw=1.8, label=T(r"旋转矩阵元素 $r_{11}$", r"Rotation matrix entry $r_{11}$"))
ax.plot(t / math.pi, q0, color=C["accent"], lw=1.8, label=T(r"四元数实部 $q_0=\cos(\theta/2)$", r"Real part of the quaternion $q_0=\cos(\theta/2)$"))
ax.axhline(0, color=C["muted"], lw=0.6)
for k in (2, 4):
    ax.axvline(k, color=C["muted"], lw=0.6, ls="--")
ax.annotate(T("转一圈：R 复原，\nq 变为 −q", "One turn: R is restored,\nq becomes −q"), xy=(2, -1), xytext=(0.3, -0.9), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
ax.annotate(T("转两圈：q 才复原", "After two turns q is restored"), xy=(4, 1), xytext=(2.3, 1.13), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
ax.set_xticks([0, 1, 2, 3, 4])
ax.set_xticklabels(["0", "π", "2π", "3π", "4π"])
ax.set_xlabel(T("转角 θ", "Angle of rotation θ"))
ax.set_ylim(-1.15, 1.35)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=9, frameon=False)   # 图例放在图外下方，不挡注释箭头
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig4_6_1")
plt.close(fig)
