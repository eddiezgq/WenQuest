"""4.2 节的示意图。

图 4.2.1：{s} 与转动后的 {b}；R_sb 的三列就是 {b} 的三根轴在 {s} 中的分量。
图 4.2.2：书本实验——同样两个 90° 转动，次序不同，结果不同。
"""
import math

import numpy as np

from _rot import box, frame, axes3d, rot_x, rot_z, rot_y, C
from bookout import figure, style

plt = style()
d = math.radians

# ---------------------------------------------------------------- 图 4.2.1
R = rot_z(d(35)) @ rot_y(d(-25)) @ rot_x(d(20))
fig, ax = axes3d(plt, size=(4.2, 3.8), lim=0.75)
frame(ax, np.eye(3), sub="s", lw=1.2, alpha=0.45, ls="--")
frame(ax, R, sub="b", lw=2.2)
ax.text2D(0.02, 0.02, r"$R_{sb}=\left(\hat x_b\ \ \hat y_b\ \ \hat z_b\right)$，各列为 {b} 的轴在 {s} 中的分量",
          transform=ax.transAxes, fontsize=9.5, color=C["ink"])
ax.text2D(0.02, 0.93, "虚线：{s}　实线：{b}", transform=ax.transAxes, fontsize=9, color=C["muted"])
figure(fig, "fig4_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 4.2.2
steps = {
    "A": [("起始", np.eye(3)), ("先绕 $\\hat x_s$ 转 90°", rot_x(d(90))), ("再绕 $\\hat z_s$ 转 90°", rot_z(d(90)) @ rot_x(d(90)))],
    "B": [("起始", np.eye(3)), ("先绕 $\\hat z_s$ 转 90°", rot_z(d(90))), ("再绕 $\\hat x_s$ 转 90°", rot_x(d(90)) @ rot_z(d(90)))],
}
fig = plt.figure(figsize=(8.4, 5.4))
for row, key in enumerate(("A", "B")):
    for col, (title, Rk) in enumerate(steps[key]):
        ax = fig.add_subplot(2, 3, row * 3 + col + 1, projection="3d")
        ax.set_proj_type("ortho")
        ax.view_init(elev=22, azim=-58)
        for f in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
            f(-0.8, 0.8)
        ax.set_box_aspect((1, 1, 1))
        ax.set_axis_off()
        frame(ax, np.eye(3), length=0.75, sub="s", lw=0.9, alpha=0.5, fs=9)
        box(ax, Rk)
        ax.set_title(f"做法 {key}：{title}", fontsize=9.5, pad=-2)
fig.text(0.5, 0.01, "加粗的金色棱为书脊。做法 A 书脊最后竖直向上，做法 B 书脊最后水平向左", ha="center", fontsize=9.5)
fig.subplots_adjust(wspace=0.02, hspace=0.08, left=0, right=1, top=0.95, bottom=0.05)
figure(fig, "fig4_2_2")
plt.close(fig)
