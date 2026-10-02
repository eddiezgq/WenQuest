"""1.4 节的示意图。

图 1.4.1：机器人的七个组成部分及其间的信息流与能量流（以 UR5e 为例）。
图 1.4.2：自由度的计数：(a) 平面刚体，两点四个坐标减一个距离约束；(b) 固定基座上的平面两连杆；(c) 空间中的自由刚体需要六个数。
"""
import math

import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
INFO, POWER = "#1f77b4", "#d9822b"


def box(ax, x, y, title, sub, fc, w=2.5, h=1.0):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc,
                                ec=C["ink"], lw=0.9))
    ax.text(x, y + 0.2, title, ha="center", va="center", fontsize=11.5, weight="bold", color=C["ink"])
    ax.text(x, y - 0.17, sub, ha="center", va="center", fontsize=8, color=C["ink"], linespacing=1.25)


def arr(ax, p, q, color, lw=1.4, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, lw=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}", zorder=2))


# ---------------------------------------------------------------- 图 1.4.1
fig, ax = plt.subplots(figsize=(9.6, 5.6))
ax.set_xlim(0, 9.6)
ax.set_ylim(0, 5.6)
ax.axis("off")
box(ax, 1.6, 4.6, T("智能", "Intelligence"), T("识别工件、规划动作、\n从数据中学习", "recognise parts, plan,\nlearn from data"), "#f3e2b3")
box(ax, 4.8, 4.6, T("软件", "Software"), T("作业程序、操作系统、\n通信与仿真", "task program, OS,\ncommunication, simulation"), "#f3e2b3")
box(ax, 8.0, 4.6, T("控制", "Control"), T("轨迹插补、关节伺服，\n每 2 ms 一个周期", "interpolation, joint servo,\none cycle every 2 ms"), "#f3e2b3")
box(ax, 8.0, 2.75, T("电气", "Electrics"), T("电源、伺服驱动器、\n线缆、急停回路", "power supply, servo drives,\ncables, emergency stop"), "#fbe3cf")
box(ax, 8.0, 0.9, T("驱动", "Actuation"), T("电机 + 减速器 + 制动器\n（6 套）", "motor + reducer + brake\n(6 sets)"), "#fbe3cf")
box(ax, 4.8, 0.9, T("机构", "Mechanism"), T("基座、6 根连杆、\n6 个转动关节、法兰", "base, 6 links,\n6 revolute joints, flange"), "#dcefdc")
box(ax, 1.6, 0.9, T("作业对象与环境", "Task and environment"), T("工件、机床、人、障碍物", "parts, machines,\npeople, obstacles"), "#eceff1")
box(ax, 1.6, 2.75, T("传感", "Sensing"), T("关节编码器、电流、\n力/力矩、相机", "joint encoders, currents,\nforce/torque, camera"), "#dbe9f6")
arr(ax, (2.87, 4.6), (3.53, 4.6), INFO)
arr(ax, (6.07, 4.6), (6.73, 4.6), INFO)
arr(ax, (8.0, 4.08), (8.0, 3.27), INFO)
arr(ax, (8.0, 2.23), (8.0, 1.42), POWER, 2.6)
arr(ax, (6.73, 0.9), (6.07, 0.9), POWER, 2.6)
arr(ax, (3.53, 0.9), (2.87, 0.9), POWER, 2.6)
arr(ax, (1.6, 1.42), (1.6, 2.23), INFO)
arr(ax, (1.6, 3.27), (1.6, 4.08), INFO)
arr(ax, (2.87, 2.95), (6.8, 4.15), INFO, rad=-0.12)
arr(ax, (4.8, 1.42), (2.6, 2.3), INFO, rad=0.15)
ax.plot([0.3, 0.8], [5.42, 5.42], color=INFO, lw=1.4)
ax.text(0.9, 5.42, T("信息（测量值、指令）", "information (measurements, commands)"), va="center", fontsize=9)
ax.plot([4.6, 5.1], [5.42, 5.42], color=POWER, lw=2.6)
ax.text(5.2, 5.42, T("能量与运动", "energy and motion"), va="center", fontsize=9)
ax.text(4.8, 2.75, T("以 UR5e 为例", "UR5e as the example"), ha="center", fontsize=10, color=C["muted"])
figure(fig, "fig1_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.4.2
fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.7))
for a in axs:
    a.set_aspect("equal")
    a.axis("off")
# (a) 平面刚体：两点 A、B
a = axs[0]
A, B = np.array([0.6, 0.6]), np.array([2.0, 1.4])
th = math.atan2(B[1] - A[1], B[0] - A[0])
d = np.array([-math.sin(th), math.cos(th)]) * 0.35
body = np.array([A - d - 0.25 * (B - A), B - d + 0.25 * (B - A), B + d + 0.25 * (B - A), A + d - 0.25 * (B - A)])
a.add_patch(Polygon(body, closed=True, fc="#f3e2b3", ec=C["ink"], lw=0.9, alpha=0.8))
a.annotate("", xy=(2.75, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["x"]))
a.annotate("", xy=(0, 2.2), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["y"]))
a.text(2.78, -0.05, "x", color=C["x"])
a.text(0.05, 2.2, "y", color=C["y"])
for P, n in ((A, "A"), (B, "B")):
    a.plot(*P, "o", color=C["ink"], ms=5)
    a.text(P[0] + 0.06, P[1] - 0.22, n, fontsize=11)
a.plot([A[0], B[0]], [A[1], B[1]], "--", color=C["ink"], lw=0.9)
a.text(1.0, 1.45, "|AB| = L", fontsize=10, color=C["accent"])
a.text(0.0, -0.55, T("4 个坐标 − 1 个约束 = 3", "4 coordinates − 1 constraint = 3"), fontsize=9.5)
a.text(0.0, -0.85, T("(x, y, φ)", "(x, y, φ)"), fontsize=9.5, color=C["muted"])
a.set_title("(a)", fontsize=10, loc="left")
a.set_xlim(-0.1, 3.0)
a.set_ylim(-1.0, 2.4)
# (b) 平面两连杆
a = axs[1]
base = np.array([0.4, 0.2])
t1, t2 = math.radians(50), math.radians(-70)
P1 = base + 1.2 * np.array([math.cos(t1), math.sin(t1)])
P2 = P1 + 1.0 * np.array([math.cos(t1 + t2), math.sin(t1 + t2)])
a.add_patch(Polygon([base + [-0.35, -0.2], base + [0.35, -0.2], base + [0.15, 0], base + [-0.15, 0]], fc="#c9d2db",
                    ec=C["ink"], lw=0.8))
a.plot([base[0], P1[0], P2[0]], [base[1], P1[1], P2[1]], "-", color=C["z"], lw=5, solid_capstyle="round")
for P in (base, P1):
    a.plot(*P, "o", color="white", mec=C["ink"], ms=8)
a.plot(*P2, "o", color=C["ink"], ms=4)
a.text(base[0] + 0.25, base[1] + 0.15, "θ₁", fontsize=11, color=C["accent"])
a.text(P1[0] + 0.12, P1[1] - 0.05, "θ₂", fontsize=11, color=C["accent"])
a.text(0.0, -0.55, T("固定基座 + 2 个转动关节 = 2", "fixed base + 2 revolute joints = 2"), fontsize=9.5)
a.text(0.0, -0.85, T("开链：自由度 = 各关节自由度之和", "open chain: DOF = sum of joint DOF"), fontsize=9.5, color=C["muted"])
a.set_title("(b)", fontsize=10, loc="left")
a.set_xlim(-0.1, 3.0)
a.set_ylim(-1.0, 2.4)
# (c) 空间自由刚体
a = axs[2]
o = np.array([1.2, 0.9])


def pr(p):
    x, y, z = p
    return o + np.array([y - 0.5 * x, z - 0.3 * x])


cube = [np.array(v) * 0.6 for v in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]]
for i, j in [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]:
    p, q = pr(cube[i]), pr(cube[j])
    a.plot([p[0], q[0]], [p[1], q[1]], color=C["ink"], lw=0.9)
for v, col, n in (((1.3, 0, 0), C["x"], "x"), ((0, 1.3, 0), C["y"], "y"), ((0, 0, 1.3), C["z"], "z")):
    p = pr(v)
    a.annotate("", xy=p, xytext=o, arrowprops=dict(arrowstyle="-|>", color=col))
    a.text(p[0] + 0.03, p[1] + 0.03, n, color=col)
a.text(0.0, -0.55, T("位置 3 个 + 姿态 3 个 = 6", "3 for position + 3 for orientation = 6"), fontsize=9.5)
a.text(0.0, -0.85, T("(x, y, z, 横滚, 俯仰, 偏航)", "(x, y, z, roll, pitch, yaw)"), fontsize=9.5, color=C["muted"])
a.set_title("(c)", fontsize=10, loc="left")
a.set_xlim(-0.1, 3.0)
a.set_ylim(-1.0, 2.4)
fig.tight_layout()
figure(fig, "fig1_4_2")
plt.close(fig)
