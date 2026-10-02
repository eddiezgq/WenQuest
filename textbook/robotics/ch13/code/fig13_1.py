"""13.1 节的示意图。

图 13.1.1：三根关节轴、两条公垂线与四个参数。(a) 标准 DH：{i−1} 在轴 i 上、{i} 在轴 i+1 上；(b) 改进 DH（Craig）：
          {i−1} 在轴 i−1 上、{i} 在轴 i 上。两幅图的几何完全相同，只是坐标系放的位置不同。
图 13.1.2：平面 3R 臂（θ = 30°, 45°, −90°）的两种连杆坐标系。
"""
import math

import numpy as np

from _dh import Rx, Rz, Tx, Tz, fk_mdh, fk_sdh
from _fig13 import C, L3R, arc3d, arm_points, axes3d, draw_arm, equal3d, frame2d, frame3d, line3d, plane
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 几何：轴 i 为 z 轴；轴 i−1 在 x = −A0 处；轴 i+1 由 θ、d、a、α 给出
A0, AL0 = 0.7, math.radians(35)
TH, D, A, AL = math.radians(55), 0.5, 0.75, math.radians(45)
u_prev = (Rx(-AL0)[:3, :3] @ [0, 0, 1.0])            # 轴 i−1 的方向
p_prev = np.array([-A0, 0, 0])
x_i = np.array([math.cos(TH), math.sin(TH), 0])
o_i = A * x_i + np.array([0, 0, D])
Fi = Rz(TH) @ Tz(D) @ Tx(A) @ Rx(AL)                  # 标准 DH 的 {i}
z_i = Fi[:3, 2]
assert np.allclose(Fi[:3, 3], o_i)

GREY, NORM = "#5b6670", C["accent"]


def scene(ax, mdh_frames: bool):
    line3d(ax, p_prev, u_prev, -0.45, 0.75, GREY, lw=2.2)
    line3d(ax, (0, 0, 0), (0, 0, 1), -0.3, 1.0, GREY, lw=2.2)
    line3d(ax, o_i, z_i, -0.5, 0.6, GREY, lw=2.2)
    ax.text(*(p_prev + 0.8 * u_prev), T("轴 $i-1$", "axis $i-1$"), fontsize=10, color=GREY)
    ax.text(0.03, 0.0, 1.03, T("轴 $i$", "axis $i$"), fontsize=10, color=GREY)
    ax.text(*(o_i + 0.66 * z_i), T("轴 $i+1$", "axis $i+1$"), fontsize=10, color=GREY)
    # 两条公垂线
    ax.plot(*np.array([p_prev, [0, 0, 0]]).T, color=NORM, lw=1.6, ls="--")
    ax.plot(*np.array([[0, 0, D], o_i]).T, color=NORM, lw=1.6, ls="--")
    ax.text(-A0 / 2 - 0.12, -0.02, -0.14, "$N_{i-1}$", fontsize=10, color=NORM)
    ax.text(*(np.array([0, 0, D]) + 0.8 * A * x_i + np.array([0.0, 0.0, 0.06])), "$N_i$", fontsize=10, color=NORM)
    # d_i：沿轴 i，从 N_{i−1} 到 N_i
    ax.plot([-0.1, -0.1], [0.0, 0.0], [0, D], color=C["z"], lw=2.6, solid_capstyle="butt")
    ax.plot([-0.13, -0.07], [0, 0], [0, 0], color=C["z"], lw=1.2)
    ax.plot([-0.13, -0.07], [0, 0], [D, D], color=C["z"], lw=1.2)
    ax.text(-0.3, 0.0, D / 2, "$d_i$", fontsize=12, color=C["z"])
    # θ_i：在 N_i 的高度上，从 x 方向（与 N_{i−1} 平行）转到 N_i
    ax.plot(*np.array([[0, 0, D], [0.55, 0, D]]).T, color=C["muted"], lw=0.9, ls=":")
    arc3d(ax, (0, 0, D), (1, 0, 0), (0, 1, 0), 0.45, 0.0, TH, C["x"])
    ax.text(0.56 * math.cos(TH / 2), 0.56 * math.sin(TH / 2), D - 0.1, r"$\theta_i$", fontsize=12, color=C["x"])
    # a_i 写在 N_i 旁
    ax.text(*(np.array([0, 0, D]) + 0.5 * A * x_i + np.array([0.0, 0.0, 0.05])), "$a_i$", fontsize=12, color=NORM)
    # α_i：在 o_i 处，绕 x_i，从“轴 i 的方向”转到“轴 i+1 的方向”
    ax.plot(*np.array([o_i, o_i + [0, 0, 0.42]]).T, color=C["muted"], lw=0.9, ls=":")
    e2 = np.cross(x_i, [0, 0, 1.0])
    arc3d(ax, o_i, (0, 0, 1), e2, 0.32, 0.0, AL, C["z"])
    ax.text(*(o_i + 0.42 * (math.cos(AL / 2) * np.array([0, 0, 1]) + math.sin(AL / 2) * e2)),
            r"$\alpha_i$", fontsize=12, color=C["z"])
    # a_{i−1}、α_{i−1}（只在改进 DH 中出现在这一行）
    if mdh_frames:
        ax.text(-0.17, -0.02, -0.13, "$a_{i-1}$", fontsize=11, color=NORM)
        ax.plot(*np.array([[0, 0, 0], 0.4 * u_prev]).T, color=C["muted"], lw=0.9, ls=":")
        arc3d(ax, (0, 0, 0), u_prev, np.cross([1.0, 0, 0], u_prev), 0.3, 0.0, AL0, NORM)
        ax.text(0.02, 0.1, 0.36, r"$\alpha_{i-1}$", fontsize=11, color=NORM)
    if not mdh_frames:
        F0 = np.eye(4)
        frame3d(ax, F0, 0.25, "{i−1}".replace("−", "-"), names=("x_{i-1}", None, "z_{i-1}"), off=(0.05, -0.08, -0.12))
        frame3d(ax, Fi, 0.25, "{i}", names=("x_i", None, "z_i"), off=(0.05, 0.05, -0.12))
    else:
        Fm_prev = np.eye(4)
        Fm_prev[:3, 0], Fm_prev[:3, 2] = [1, 0, 0], u_prev
        Fm_prev[:3, 1] = np.cross(u_prev, [1, 0, 0])
        Fm_prev[:3, 3] = p_prev
        frame3d(ax, Fm_prev, 0.25, "{i-1}", names=("x_{i-1}", None, "z_{i-1}"), off=(-0.05, -0.1, -0.13))
        Fm = Rz(TH) @ Tz(D)
        frame3d(ax, Fm, 0.25, "{i}", names=("x_i", None, "z_i"), off=(-0.12, 0.02, 0.02))
    equal3d(ax, [p_prev + 0.75 * u_prev, [0, 0, 1.0], o_i + 0.6 * z_i, o_i - 0.5 * z_i, [0, 0, -0.3], [0.6, 0.6, 0]], pad=0.0, zoom=1.25)


fig = plt.figure(figsize=(10.4, 4.6))
ax = fig.add_subplot(121, projection="3d")
ax.view_init(elev=18, azim=-62)
ax.set_axis_off()
scene(ax, False)
ax.set_title(T("(a) 标准 DH：{i} 固定在轴 $i+1$ 上", "(a) Standard DH: {i} sits on axis $i+1$"), fontsize=10, y=0.98)
ax = fig.add_subplot(122, projection="3d")
ax.view_init(elev=18, azim=-62)
ax.set_axis_off()
scene(ax, True)
ax.set_title(T("(b) 改进 DH（Craig）：{i} 固定在轴 $i$ 上", "(b) Modified DH (Craig): {i} sits on axis $i$"), fontsize=10, y=0.98)
fig.text(0.5, 0.06, T("同一组几何量：公垂线 $N_i$ 的长度 $a_i$、轴 $i$ 到轴 $i+1$ 的扭角 $\\alpha_i$；沿轴 $i$ 的距离 $d_i$ 和转角 $\\theta_i$",
                      "Same geometry: length $a_i$ of the common normal $N_i$, twist $\\alpha_i$ from axis $i$ to $i+1$; offset $d_i$ and angle $\\theta_i$ along axis $i$"),
         ha="center", fontsize=9.5, color=C["ink"])
figure(fig, "fig13_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 13.1.2 平面 3R 的两种坐标系
th = [math.radians(30), math.radians(45), math.radians(-90)]
pts, _ = arm_points(th)
sdh3 = [(L3R[0], 0, 0, 0), (L3R[1], 0, 0, 0), (L3R[2], 0, 0, 0)]
mdh3 = [(0, 0, 0, 0), (L3R[0], 0, 0, 0), (L3R[1], 0, 0, 0)]
Fs = fk_sdh(sdh3, th, frames=True)
Fm = fk_mdh(mdh3, th, frames=True)
fig, axs = plt.subplots(1, 2, figsize=(10.0, 3.9))
for ax, Fr, title in ((axs[0], Fs, T("(a) 标准 DH：{i} 在连杆 i 的末端（轴 i+1 上）", "(a) Standard DH: {i} at the far end of link i (on axis i+1)")),
                      (axs[1], Fm, T("(b) 改进 DH：{i} 在连杆 i 的始端（轴 i 上）", "(b) Modified DH: {i} at the near end of link i (on axis i)"))):
    plane(ax, (-0.22, 0.9), (-0.1, 0.75))
    draw_arm(ax, pts, C["muted"], lw=7, alpha=0.45)
    for i, F in enumerate(Fr):
        ang = math.atan2(F[1, 0], F[0, 0])
        dx, dy = ((-0.12, -0.05) if i == 0 else (0.02, -0.07))
        if Fr is Fm and i == 1:
            dx, dy = (0.04, -0.06)
        frame2d(ax, F[:2, 3], ang, 0.11, "{%d}" % i, fs=11, dx=dx, dy=dy)
    if Fr is Fm:
        ax.annotate(T("末端还差 $X_3$：沿 $x_3$ 平移 $L_3$", "tool still needs $X_3$: shift $L_3$ along $x_3$"), xy=pts[-1], xytext=(0.48, 0.05),
                    fontsize=9, color=C["ink"], arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
    ax.set_title(title, fontsize=10)
fig.text(0.5, 0.02, T("θ = (30°, 45°, −90°)；两种约定算出的末端位姿相同（算例 13.1.2）", "θ = (30°, 45°, −90°); both conventions give the same tool pose (Example 13.1.2)"),
         ha="center", fontsize=9.5, color=C["ink"])
figure(fig, "fig13_1_2")
plt.close(fig)
