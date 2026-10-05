"""18.1 节的示意图。

图 18.1.1：工作空间。(a) 2R 串联臂：两个圆的“和”是圆环，深色为 LCI ≥ 0.3 的部分；(b) 平面五杆机器人：两条支链各自的
           工作空间（以两台电机为圆心的两个圆环）的“交”，深色为一种装配模式、一种工作模式下 LCI ≥ 0.3 的部分。两者都画出到达 P0 的姿势。
图 18.1.2：速度（误差）椭圆：两台电机转速组成的单位圆，经 J 映射成末端速度的椭圆；同一组点上 2R 臂（蓝）与五杆（金）对照。
"""
import math

import numpy as np

from _ch18 import ARM2, FIVE, arm2_ik, arm2_J, five_AB, five_fk, five_ik, five_motors
from _fig18 import BLUE2, C, GOLD, PALE, PALEGOLD, draw_arm2, draw_five, ellipse_pts, plane
from bookout import T, figure, style

plt = style()
plt.rcParams["axes.unicode_minus"] = True
L1, L2 = ARM2["L1"], ARM2["L2"]
c, l1, l2 = FIVE["c"], FIVE["l1"], FIVE["l2"]
P0 = np.array([0.0, 0.35])

# ---------------------------------------------------------------- 图 18.1.1
h = 0.004
g = np.arange(-0.68, 0.68 + h / 2, h)
img_s = np.zeros((len(g), len(g)))
img_p = np.zeros((len(g), len(g)))
for i, y in enumerate(g):
    for j, x in enumerate(g):
        P = np.array([x, y])
        r = math.hypot(x, y)
        if L2 - L1 <= r <= L1 + L2:
            img_s[i, j] = 1
            ts = arm2_ik(P, +1)
            s = np.linalg.svd(arm2_J(ts))[1] if ts is not None else (1.0, 0.0)
            if s[1] / s[0] >= 0.3:
                img_s[i, j] = 2
        r1, r2 = math.hypot(x + c, y), math.hypot(x - c, y)
        if l2 - l1 <= r1 <= l1 + l2 and l2 - l1 <= r2 <= l1 + l2:
            img_p[i, j] = 1
            tp = five_ik(P)
            Q = five_fk(tp, +1) if tp is not None else None
            if Q is not None and np.abs(Q - P).max() < 1e-9:
                A, B = five_AB(P, tp)
                s = np.linalg.svd(np.linalg.solve(A, B))[1]
                if s[1] / s[0] >= 0.3:
                    img_p[i, j] = 2
from matplotlib.colors import ListedColormap

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 5.2))
ext = (g[0] - h / 2, g[-1] + h / 2, g[0] - h / 2, g[-1] + h / 2)
for ax, img, cols in ((a1, img_s, ["#ffffff", PALE, BLUE2]), (a2, img_p, ["#ffffff", PALEGOLD, GOLD])):
    plane(ax, (-0.68, 0.68), (-0.62, 0.66))
    ax.imshow(img, origin="lower", extent=ext, cmap=ListedColormap(cols), vmin=0, vmax=2, interpolation="nearest", alpha=0.85)
t = np.linspace(0, 2 * math.pi, 300)
for r in (L2 - L1, L1 + L2):
    a1.plot(r * np.cos(t), r * np.sin(t), color=C["z"], lw=0.9)
draw_arm2(a1, arm2_ik(P0, +1), C["z"], lw=5)
a1.plot(*P0, "o", color=C["x"], ms=6, zorder=9)
a1.text(P0[0] + 0.03, P0[1] + 0.03, r"$P_0$", fontsize=11, color=C["x"])
a1.text(-0.66, 0.6, T("(a) 2R 串联臂：两个圆的“和”", "(a) 2R serial arm: the “sum” of two circles"), fontsize=10)
a1.text(-0.04, -0.13, T("基座", "base"), fontsize=9, color=C["muted"])
for A in five_motors():
    for r in (l2 - l1, l1 + l2):
        a2.plot(A[0] + r * np.cos(t), A[1] + r * np.sin(t), color=C["muted"], lw=0.8, ls="--")
draw_five(a2, five_ik(P0), P0, C["accent"], lw=5)
a2.plot(*P0, "o", color=C["x"], ms=6, zorder=9)
a2.text(P0[0] + 0.03, P0[1] + 0.03, r"$P_0$", fontsize=11, color=C["x"])
a2.text(-0.66, 0.6, T("(b) 五杆：两条支链工作空间的“交”", "(b) five-bar: the “intersection” of the legs' workspaces"), fontsize=10)
A1, A2 = five_motors()
a2.text(A1[0] - 0.05, A1[1] - 0.075, r"$A_1$", fontsize=10)
a2.text(A2[0] + 0.01, A2[1] - 0.075, r"$A_2$", fontsize=10)
for ax, (cl, cd), y0 in ((a1, (PALE, BLUE2), -0.52), (a2, (PALEGOLD, GOLD), -0.52)):
    for col, name, dy in ((cl, T("可达", "reachable"), 0.0), (cd, T("LCI ≥ 0.3", "LCI ≥ 0.3"), -0.07)):
        ax.add_patch(plt.Rectangle((0.3, y0 + dy - 0.02), 0.05, 0.04, facecolor=col, edgecolor=C["muted"], lw=0.5))
        ax.text(0.37, y0 + dy - 0.012, name, fontsize=9)
a2.text(-0.66, -0.6, T("虚线：以电机为圆心、半径 0.1 m 和 0.5 m 的圆", "dashed: circles of radius 0.1 m and 0.5 m about each motor"),
        fontsize=8.5, color=C["muted"])
figure(fig, "fig18_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 18.1.2
fig, ax = plt.subplots(figsize=(7.6, 5.0))
plane(ax, (-0.42, 0.42), (-0.06, 0.56))
pts = [np.array(p) for p in ((0.0, 0.2), (0.0, 0.35), (0.0, 0.46), (-0.22, 0.3), (0.22, 0.3), (-0.1, 0.42), (0.1, 0.42))]
sc = 0.10                    # 1 rad/s 的电机转速画成 0.1 倍长（m/s → 图上长度）
for P in pts:
    Js = arm2_J(arm2_ik(P, +1))
    A, B = five_AB(P, five_ik(P))
    Jp = np.linalg.solve(A, B)
    for J, col in ((Js, C["z"]), (Jp, C["accent"])):
        E = ellipse_pts(J, sc) + P
        ax.fill(E[:, 0], E[:, 1], color=col, alpha=0.12, lw=0)
        ax.plot(E[:, 0], E[:, 1], color=col, lw=1.3)
    ax.plot(*P, "o", color=C["ink"], ms=3)
for A in five_motors():
    ax.plot(*A, "s", color=C["accent"], ms=6)
ax.plot(0, 0, "o", color=C["z"], ms=6)
ax.text(0.015, -0.035, T("2R 的基座", "2R base"), fontsize=9, color=C["z"])
ax.text(-0.24, -0.035, T("五杆的电机", "five-bar motors"), fontsize=9, color=C["accent"])
ax.plot([0.22, 0.3], [0.03, 0.03], color=C["z"], lw=2)
ax.text(0.31, 0.022, T("2R 串联臂", "2R serial arm"), fontsize=9)
ax.plot([0.22, 0.3], [-0.02, -0.02], color=C["accent"], lw=2)
ax.text(0.31, -0.028, T("五杆", "five-bar"), fontsize=9)
ax.text(-0.41, 0.53, T("单位电机转速（1 rad/s）对应的末端速度椭圆", "end-point velocity ellipses for unit motor speed (1 rad/s)"), fontsize=10)
ax.text(-0.41, 0.495, T("图上长度 = 0.1 × 速度（m/s）", "length on the figure = 0.1 × speed (m/s)"), fontsize=8.5, color=C["muted"])
figure(fig, "fig18_1_2")
plt.close(fig)
