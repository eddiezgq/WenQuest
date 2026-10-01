"""4.5 节的示意图。

图 4.5.1：三环万向支架——正常状态与万向节锁（中环转过 90°，外环与内环的转轴重合）。
图 4.5.2：俯仰角接近 90° 时，0.1° 的姿态扰动引起的偏航角跳变（数据与程序 4.5.1 同法计算）。
"""
import math

import numpy as np

from _rot import C, rot_axis, rot_x, rot_y, rot_z
from bookout import figure, style

plt = style()
d = math.radians


def ring(ax, a, b, radius, color, lw=3.0):
    """圆环：在单位矢量 a、b 张成的平面内。"""
    t = np.linspace(0, 2 * math.pi, 160)
    P = radius * (np.outer(a, np.cos(t)) + np.outer(b, np.sin(t)))
    ax.plot(*P, color=color, lw=lw)


def axis_line(ax, v, length, color, label, at=1.08):
    v = np.asarray(v, float)
    ax.plot(*np.array([-length * v, length * v]).T, color=color, lw=1.2, ls="--")
    ax.text(*(v * length * at), label, color=color, fontsize=10)


def gimbal(ax, psi, theta, phi, title):
    """外环绕竖直轴 z 转 ψ；中环装在外环上，绕水平轴 y_o 转 θ；内环装在中环上，绕 x_m 转 φ。
    θ = −90° 时 x_m 竖直，与外环轴重合：万向节锁（外环与中环共面）。"""
    Ro = rot_z(psi)
    x_o, y_o, z = Ro[:, 0], Ro[:, 1], np.array([0, 0, 1.0])
    Rm = Ro @ rot_y(theta)
    x_m, z_m = Rm[:, 0], Rm[:, 2]
    Ri = Rm @ rot_x(phi)
    y_i, z_i = Ri[:, 1], Ri[:, 2]
    ring(ax, y_o, z, 1.0, C["z"], 3.2)          # 外环：在 y_o–z 平面内（含外环轴 z）
    ring(ax, x_m, y_o, 0.8, C["y"], 3.0)        # 中环：在 x_m–y_o 平面内（含中环轴 y_o）
    ring(ax, x_m, z_i, 0.6, C["x"], 3.0)      # 内环：在 x_m–z_i 平面内（含内环轴 x_m）
    axis_line(ax, z, 1.25, C["z"], "外环轴")
    axis_line(ax, y_o, 1.18, C["y"], "中环轴")
    axis_line(ax, x_m, 0.95, C["x"], "内环轴", at=1.2)
    ax.set_title(title, fontsize=10.5)


fig = plt.figure(figsize=(8.4, 4.2))
for k, (mid, title) in enumerate(((d(-30), "正常：三根转轴各不相同"), (d(-90), "万向节锁：内环轴转到与外环轴重合"))):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    ax.set_proj_type("ortho")
    ax.view_init(elev=32, azim=-30)
    for f in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
        f(-1.2, 1.2)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    gimbal(ax, d(25), mid, d(30), title)
fig.subplots_adjust(left=0, right=1, top=0.92, bottom=0.02, wspace=0.0)
figure(fig, "fig4_5_1")
plt.close(fig)


# ---------------------------------------------------------------- 图 4.5.2
def zyx(psi, th, phi):
    return rot_z(psi) @ rot_y(th) @ rot_x(phi)


def yaw_of(R):
    return math.atan2(R[1, 0], R[0, 0])


pitches = np.linspace(80, 89.99, 200)
jumps = [abs(math.degrees(yaw_of(rot_axis([1, 0, 0], d(0.1)) @ zyx(d(10), d(p), d(20))) - yaw_of(zyx(d(10), d(p), d(20)))))
         for p in pitches]
fig, ax = plt.subplots(figsize=(5.2, 3.2))
ax.semilogy(pitches, jumps, color=C["x"], lw=1.6)
ax.axhline(0.1, color=C["muted"], lw=0.8, ls="--")
ax.text(80.2, 0.13, "姿态本身只变了 0.1°", fontsize=9.5, color=C["muted"])
ax.set_xlabel("俯仰角 θ（°）")
ax.set_ylabel("偏航角的跳变（°）")
ax.grid(True, lw=0.3, alpha=0.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig4_5_2")
plt.close(fig)
