"""12.4 节的计算：

算例 12.4.1  用扳手拧螺栓：手离螺栓中心 0.30 m，用 200 N 的力，力与扳手成 90° 与 60° 时的力矩；要求 50 N·m，60° 时手要用多大的力。
算例 12.4.2  机械臂的肩关节：大臂 8.4 kg（质心离肩 0.21 m）、小臂 2.3 kg（质心离肩 0.62 m）、末端负载 5.0 kg（离肩 0.82 m），
            整条臂伸直，与水平方向成 φ 角。重力对肩关节的力矩随 φ 的变化，最大值（图 12.4.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

F, rw = 200.0, 0.30
out(F=F, rw=rw, M90=F * rw, M60=F * rw * math.sin(math.radians(60)), F_need=50 / (rw * math.sin(math.radians(60))), d60=rw * math.sin(math.radians(60)))

parts = [(8.4, 0.21), (2.3, 0.62), (5.0, 0.82)]
G = sum(mm * rr for mm, rr in parts) * g
out(G=G, M_load=5.0 * 0.82 * g, frac_load=5.0 * 0.82 / sum(mm * rr for mm, rr in parts), M45=G * math.cos(math.radians(45)))

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
phi = np.linspace(-90, 90, 361)
ax.plot(phi, G * np.cos(np.radians(phi)), color=d.VR, lw=2, label=T("总的重力矩", "total gravity torque"))
ax.plot(phi, 5.0 * 0.82 * g * np.cos(np.radians(phi)), color=d.VA, lw=1.5, ls="--", label=T("其中负载的贡献", "of which the load"))
ax.set_xlabel(T("臂与水平方向的夹角 φ / (°)", "arm angle above horizontal φ / (°)")); ax.set_ylabel(T("力矩 / (N·m)", "torque / (N·m)"))
ax.set_xlim(-90, 90); ax.set_xticks([-90, -45, 0, 45, 90]); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig12_4_1")
