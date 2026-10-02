"""10.2 节的示意图。

图 10.2.1：(a) SCARA 涂胶的椭圆轨迹（俯视），t = 0.5 s 时的位置矢量 r、速度 v、加速度 a，及其他时刻的加速度（都指向中心）；
           (b) 速度图：把各时刻的速度矢量平移到同一起点，端点画出的曲线；a 是速度图的切向量。
图 10.2.2：夹爪运动中松开零件，零件沿抛物线落入料箱。
"""
import math

import numpy as np

from _kin import A_COL, C, G_COL, V_COL, arrow
from bookout import T, figure, style

plt = style()
xc, yc, a, b = 0.40, 0.05, 0.12, 0.08
w = 2 * math.pi / 4.0
t1 = 0.5
r = lambda t: np.array([xc + a * math.cos(w * t), yc + b * math.sin(w * t)])
v = lambda t: np.array([-a * w * math.sin(w * t), b * w * math.cos(w * t)])
acc = lambda t: np.array([-a * w * w * math.cos(w * t), -b * w * w * math.sin(w * t)])

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.3), gridspec_kw={"width_ratios": [1.45, 1]})
for ax in (a1, a2):
    ax.set_aspect("equal")
    ax.axis("off")
tt = np.linspace(0, 4, 300)
P = np.array([r(t) for t in tt])
a1.plot(P[:, 0], P[:, 1], color=C["ink"], lw=1.2)
arrow(a1, (0, 0), (0.62, 0), C["x"], 1.1)
arrow(a1, (0, 0), (0, 0.22), C["y"], 1.1)
a1.text(0.625, -0.012, "$x_s$", color=C["x"], fontsize=11)
a1.text(0.006, 0.225, "$y_s$", color=C["y"], fontsize=11)
a1.text(-0.03, -0.025, "$O_s$", fontsize=11)
a1.plot(xc, yc, "+", color=G_COL, ms=8)
a1.plot([xc, xc + 0.01], [yc, yc - 0.083], color=G_COL, lw=0.5, ls=":")
a1.text(xc - 0.02, yc - 0.105, T("椭圆中心 +", "centre +"), fontsize=9, color=G_COL)
k = 0.2                                    # 加速度箭头比例：1 m/s² 画成 0.2 m
for t in np.linspace(0, 4, 9)[:-1]:
    p = r(t)
    arrow(a1, p, p + k * acc(t), A_COL, 0.8, ms=8)
p1 = r(t1)
arrow(a1, (0, 0), p1, C["ink"], 1.3)
a1.text(p1[0] * 0.5 + 0.0, p1[1] * 0.5 + 0.018, "$r$", fontsize=12)
arrow(a1, p1, p1 + 0.6 * v(t1), V_COL, 1.8)
a1.text(*(p1 + 0.6 * v(t1) + np.array([-0.035, 0.008])), "$v$", color=V_COL, fontsize=12)
arrow(a1, p1, p1 + k * acc(t1), A_COL, 1.8)
a1.text(*(p1 + k * acc(t1) + np.array([0.0, -0.03])), "$a$", color=A_COL, fontsize=12)
a1.plot(*p1, "o", color=C["ink"], ms=4, zorder=6)
a1.text(p1[0] + 0.01, p1[1] + 0.012, "$t = 0.5$ s", fontsize=10)
a1.text(0.0, -0.13, T("细红箭头：其他时刻的加速度，都指向椭圆中心", "thin red arrows: accelerations at other times, all towards the centre"),
        fontsize=8.5, color=A_COL)
a1.set_title(T("(a) 工具尖的轨迹（俯视）", "(a) Path of the tool tip (top view)"), fontsize=11)
a1.set_xlim(-0.05, 0.66)
a1.set_ylim(-0.14, 0.24)
# (b) 速度图
V = np.array([v(t) for t in tt])
a2.plot(V[:, 0], V[:, 1], color=V_COL, lw=1.2)
arrow(a2, (-0.24, 0), (0.25, 0), G_COL, 0.9)
arrow(a2, (0, -0.17), (0, 0.18), G_COL, 0.9)
a2.text(0.252, -0.012, "$\\dot x$", fontsize=11, color=G_COL)
a2.text(0.006, 0.182, "$\\dot y$", fontsize=11, color=G_COL)
v1 = v(t1)
arrow(a2, (0, 0), v1, V_COL, 1.8)
a2.text(v1[0] + 0.01, v1[1] + 0.015, "$v(0.5\\,\\mathrm{s})$", color=V_COL, fontsize=11)
arrow(a2, v1, v1 + 0.35 * acc(t1), A_COL, 1.8)
a2.text(*(v1 + 0.35 * acc(t1) + np.array([-0.03, -0.035])), "$a$", color=A_COL, fontsize=12)
a2.text(-0.23, -0.21, T("速度矢量的端点画出的曲线；a 沿它的切线", "the curve traced by the tip of v; a is tangent to it"),
        fontsize=8.5, color=C["ink"])
a2.set_title(T("(b) 速度图（单位 m/s）", "(b) Hodograph (m/s)"), fontsize=11)
a2.set_xlim(-0.25, 0.27)
a2.set_ylim(-0.23, 0.2)
figure(fig, "fig10_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.2.2
g, vx0, h = 9.81, 0.6, 0.25
tl = math.sqrt(2 * h / g)
fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.set_aspect("equal")
ax.axis("off")
t = np.linspace(0, tl, 60)
ax.plot(vx0 * t, h - 0.5 * g * t * t, color=C["accent"], lw=1.4, ls="--")
for tk in np.linspace(0, tl, 5):
    x, z = vx0 * tk, h - 0.5 * g * tk * tk
    ax.add_patch(plt.Rectangle((x - 0.012, z - 0.012), 0.024, 0.024, color=C["accent"], alpha=0.5 + 0.5 * tk / tl))
# 料箱
ax.plot([-0.05, -0.05, 0.25, 0.25], [0.06, -0.012, -0.012, 0.06], color=C["ink"], lw=1.5)
# 夹爪（松开时刻）
ax.plot([-0.03, -0.03], [h + 0.015, h + 0.09], color=G_COL, lw=3)
ax.plot([-0.045, -0.02, -0.02], [h + 0.02, h + 0.02, h - 0.015], color=G_COL, lw=1.6)
ax.plot([0.045, 0.02, 0.02], [h + 0.02, h + 0.02, h - 0.015], color=G_COL, lw=1.6)
ax.plot([-0.045, 0.045], [h + 0.02, h + 0.02], color=G_COL, lw=1.6)
arrow(ax, (0.06, h + 0.05), (0.15, h + 0.05), V_COL, 1.6)
ax.text(0.16, h + 0.042, "$v_0 = 0.6$ m/s", color=V_COL, fontsize=10)
arrow(ax, (vx0 * tl * 0.5 + 0.045, h - 0.5 * g * (tl * 0.5) ** 2), (vx0 * tl * 0.5 + 0.045, h - 0.5 * g * (tl * 0.5) ** 2 - 0.07), C["z"], 1.4)
ax.text(vx0 * tl * 0.5 + 0.06, h - 0.5 * g * (tl * 0.5) ** 2 - 0.06, "$a = (0, 0, -g)$", color=C["z"], fontsize=10)
ax.annotate("", xy=(-0.09, 0.0), xytext=(-0.09, h), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.8))
ax.text(-0.135, h / 2, "$h$", fontsize=11)
ax.annotate("", xy=(vx0 * tl, -0.045), xytext=(0, -0.045), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.8))
ax.text(vx0 * tl / 2 - 0.04, -0.075, T("落点前移 x", "landing shift x"), fontsize=9.5)
ax.text(-0.02, h + 0.11, T("松开", "release"), fontsize=9.5, color=G_COL)
ax.set_xlim(-0.16, 0.36)
ax.set_ylim(-0.09, 0.39)
figure(fig, "fig10_2_2")
plt.close(fig)
