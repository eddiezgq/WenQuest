"""4.7 节的示意图。

图 4.7.1：算例 4.7.1 中，末端 z 轴指向在单位球面上的轨迹：欧拉角插值与测地线（Slerp）。
图 4.7.2：三种插值的角速度（以平均角速度为 1）。
"""
import math

import numpy as np

from _rot import C, axes3d, rot_x, rot_y, rot_z
from bookout import figure, style

plt = style()
d = math.radians


def zyx(psi, th, phi):
    return rot_z(psi) @ rot_y(th) @ rot_x(phi)


def q_from_R(R):
    q0 = 0.5 * math.sqrt(max(0.0, 1 + np.trace(R)))
    return np.concatenate([[q0], np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (4 * q0)])


def R_from_q(q):
    q0, q1, q2, q3 = q / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (q2 * q2 + q3 * q3), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q3 + q0 * q2)],
        [2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1 * q1 + q3 * q3), 2 * (q2 * q3 - q0 * q1)],
        [2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1 * q1 + q2 * q2)]])


def slerp(qa, qb, t):
    om = math.acos(min(1.0, float(qa @ qb)))
    return (math.sin((1 - t) * om) * qa + math.sin(t * om) * qb) / math.sin(om)


def angle_between(Ra, Rb):
    return math.acos(max(-1.0, min(1.0, (np.trace(Ra.T @ Rb) - 1) / 2)))


E1 = np.array([d(90), d(45), d(90)])
q0, q1 = q_from_R(np.eye(3)), q_from_R(zyx(*E1))
N = 400
ts = np.linspace(0, 1, N + 1)
paths = {"欧拉角插值": [zyx(*(t * E1)) for t in ts],
         "归一化线性插值": [R_from_q((1 - t) * q0 + t * q1) for t in ts],
         "球面线性插值（Slerp）": [R_from_q(slerp(q0, q1, t)) for t in ts]}
colors = {"欧拉角插值": C["x"], "归一化线性插值": C["z"], "球面线性插值（Slerp）": C["accent"]}

# ---------------------------------------------------------------- 图 4.7.1
fig, ax = axes3d(plt, size=(5.0, 4.4), elev=24, azim=-40, lim=0.85, zoom=1.15, center=(0.2, 0.2, 0.3))
u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]
ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="#c9d1d6", lw=0.3)
for name in ("欧拉角插值", "球面线性插值（Slerp）"):
    tip = np.array([R[:, 2] for R in paths[name]])
    ax.plot(*tip.T, color=colors[name], lw=2.4, label=name)
    ticks = tip[::40]
    ax.scatter(*ticks.T, color=colors[name], s=10)
a, b = paths["欧拉角插值"][0][:, 2], paths["欧拉角插值"][-1][:, 2]
ax.scatter(*a, color=C["ink"], s=30)
ax.scatter(*b, color=C["ink"], s=30)
ax.text(*(a * 1.12), "起点", fontsize=10)
ax.text(*(b * 1.12), "终点", fontsize=10)
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.text2D(0.02, 0.02, "圆点为等时间间隔的位置", transform=ax.transAxes, fontsize=9, color=C["muted"])
figure(fig, "fig4_7_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 4.7.2
theta = angle_between(np.eye(3), zyx(*E1))
fig, ax = plt.subplots(figsize=(5.6, 3.2))
for name, Rs in paths.items():
    sp = [angle_between(Rs[i], Rs[i + 1]) * N / theta for i in range(N)]
    ax.plot(ts[:-1] + 0.5 / N, sp, color=colors[name], lw=1.8, label=name)
ax.set_xlabel("进程 t")
ax.set_ylabel("角速度（以最短转法为 1）")
ax.set_ylim(0.7, 1.45)
ax.legend(fontsize=9, frameon=False, loc="upper right")
ax.grid(True, lw=0.3, alpha=0.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig4_7_2")
plt.close(fig)
