"""23.3 节的示意图。

图 23.3.1：算例 23.3.1：UR5e 零位（俯视，{s} 的 x–y 平面），关节 1 以 θ̇₁ = 1.2 rad/s、θ̈₁ = 6 rad/s² 转动；
          法兰上的夹爪与毛坯（沿工具方向 y_b = −y_s），负载质心的切向、法向加速度与法兰对负载的水平力。
图 23.3.2：(a) 算例 23.3.2：手腕以 Ω 扳动电主轴，陀螺力矩 M = Ω × L 垂直于两根轴；
          (b) 算例 23.3.3：陀螺仪的轴水平，重力矩使它绕竖直线进动。
"""
import math

import numpy as np

from _ch23 import G0, GRIP_C, GRIP_M, UR_M, sh301_blank, ur_points
from bookout import COLORS as C, T, figure, style

plt = style()


def arrow(ax, p, q, color, lw=1.6, ms=11, z=5, style_="-|>"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle=style_, color=color, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0), zorder=z)


m_b, r_b, L_b = sh301_blank()
m_p = GRIP_M + m_b
c_p = (GRIP_M * GRIP_C + m_b * (0.15 - 0.04 + L_b / 2)) / m_p
dth, ddth = 1.2, 6.0

# ---------------------------------------------------------------- 图 23.3.1
fig, ax = plt.subplots(figsize=(8.6, 6.4))
ax.set_aspect("equal")
ax.axis("off")
P = ur_points(np.zeros(6))
ax.plot(P[:, 0], P[:, 1], color=C["muted"], lw=5, solid_capstyle="round", alpha=0.55, zorder=2)
ax.plot(P[1:-1, 0], P[1:-1, 1], "o", color="white", mec=C["muted"], ms=6, zorder=3)
fl = UR_M[:3, 3]
yb = UR_M[:3, 1]                                                     # 工具方向 y_b = −y_s
g0, g1 = fl + 0.0 * yb, fl + 0.10 * yb
ax.plot([g0[0], g1[0]], [g0[1], g1[1]], color="#5d6b73", lw=12, solid_capstyle="butt", zorder=3)
b0, b1 = fl + 0.11 * yb, fl + (0.11 + L_b) * yb
ax.plot([b0[0], b1[0]], [b0[1], b1[1]], color="#8c6d1f", lw=9, solid_capstyle="butt", zorder=3)
c = fl + c_p * yb
ax.plot(*c[:2], "o", color=C["x"], ms=7, zorder=6)
ax.text(c[0] + 0.03, c[1] - 0.005, T("负载质心", "payload CoM"), fontsize=10.5, color=C["x"], va="center")
ax.plot(0, 0, "o", color=C["ink"], ms=6, zorder=6)
ax.text(0.03, -0.05, T("关节 1 轴（竖直）", "joint 1 axis (vertical)"), fontsize=10.5)
th = np.linspace(math.radians(150), math.radians(250), 60)
ax.plot(0.16 * np.cos(th), 0.16 * np.sin(th), color=C["z"], lw=1.5)
arrow(ax, (0.16 * math.cos(th[-2]), 0.16 * math.sin(th[-2])), (0.16 * math.cos(th[-1]), 0.16 * math.sin(th[-1])), C["z"], lw=1.5)
ax.text(-0.2, 0.11, r"$\dot\theta_1,\ \ddot\theta_1$", fontsize=13, color=C["z"])
# 负载质心的加速度（{s} 的水平面）
rv = c[:2]
r = float(np.linalg.norm(rv))
u_n = -rv / r                                                        # 指向转轴
u_t = np.array([-rv[1], rv[0]]) / r                                  # 逆时针切向
ft, fn = m_p * ddth * r, m_p * dth ** 2 * r
sc = 0.012                                                           # 1 N 画成 0.012 m
arrow(ax, c[:2], c[:2] + sc * ft * u_t, C["y"], lw=2.2)
ax.text(*(c[:2] + sc * ft * u_t + [-0.02, -0.04]), T(f"切向 $m\\ddot\\theta_1 r$ = {ft:.1f} N", f"tangential $m\\ddot\\theta_1 r$ = {ft:.1f} N"), fontsize=10.5, color=C["y"], ha="right")
arrow(ax, c[:2], c[:2] + sc * fn * u_n, C["z"], lw=2.2)
ax.text(*(c[:2] + sc * fn * u_n + [0.03, 0.035]), T(f"法向 $m\\dot\\theta_1^2 r$ = {fn:.2f} N", f"normal $m\\dot\\theta_1^2 r$ = {fn:.2f} N"), fontsize=10.5, color=C["z"])
F = ft * u_t + fn * u_n
arrow(ax, c[:2], c[:2] + sc * F, C["accent"], lw=1.6)
ax.text(*(c[:2] + sc * F + [0.02, -0.035]), T(f"合力 {np.linalg.norm(F):.1f} N", f"resultant {np.linalg.norm(F):.1f} N"), fontsize=10.5, color=C["accent"])
ax.plot([0, c[0]], [0, c[1]], color=C["muted"], lw=0.8, ls=":")
ax.text(c[0] / 2 + 0.03, c[1] / 2 - 0.045, f"r = {r:.4f} m", fontsize=10.5, color=C["muted"])
# 法兰坐标系 {b}
for k, col, nm in ((0, C["x"], r"$x_b$"), (1, C["y"], r"$y_b$")):
    e = UR_M[:3, k]
    arrow(ax, fl[:2], fl[:2] + 0.09 * e[:2], col, lw=1.3, ms=9)
    ax.text(*(fl[:2] + 0.11 * e[:2] + ([0.0, 0.01] if k == 0 else [-0.07, 0.02])), nm, fontsize=12, color=col)
ax.text(fl[0] - 0.03, fl[1] + 0.03, "{b}", fontsize=11, color=C["ink"], ha="right")
ax.text(-1.05, 0.21, T("俯视；手臂沿 −x 伸直；重力竖直向下（垂直纸面）", "top view; arm along −x; gravity into the page"), fontsize=10.5)
for k, col, nm in ((0, C["x"], r"$x_s$"), (1, C["y"], r"$y_s$")):
    e = np.eye(3)[k]
    arrow(ax, (0.12, 0.08), (0.12, 0.08) + 0.08 * e[:2], col, lw=1.2, ms=8)
    ax.text(*((0.12, 0.08) + 0.1 * e[:2] + [0.005, 0.005]), nm, fontsize=11, color=col)
ax.set_xlim(-1.1, 0.35)
ax.set_ylim(-0.62, 0.26)
figure(fig, "fig23_3_1")

# ---------------------------------------------------------------- 图 23.3.2
fig = plt.figure(figsize=(12.0, 5.2))


def disk(ax, c, n, r, color, alpha=0.45):
    n = np.asarray(n, float) / np.linalg.norm(n)
    e1 = np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    u = np.linspace(0, 2 * math.pi, 40)
    rr = np.linspace(0, r, 2)
    U, R = np.meshgrid(u, rr)
    X = c[0] + R * (np.cos(U) * e1[0] + np.sin(U) * e2[0])
    Y = c[1] + R * (np.cos(U) * e1[1] + np.sin(U) * e2[1])
    Z = c[2] + R * (np.cos(U) * e1[2] + np.sin(U) * e2[2])
    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, linewidth=0, shade=False)
    ax.plot(c[0] + r * (np.cos(u) * e1[0] + np.sin(u) * e2[0]), c[1] + r * (np.cos(u) * e1[1] + np.sin(u) * e2[1]),
            c[2] + r * (np.cos(u) * e1[2] + np.sin(u) * e2[2]), color=C["ink"], lw=0.8)


def q3(ax, p, d, color, lw=2.0, ratio=0.15):
    ax.quiver(*p, *d, color=color, lw=lw, arrow_length_ratio=ratio)


def setup(ax, lim):
    ax.set_axis_off()
    ax.view_init(elev=22, azim=-58)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim * 0.75, lim * 0.75)
    ax.set_box_aspect((1, 1, 0.75), zoom=1.2)


# (a) 电主轴：转轴沿 y，手腕绕竖直的 z 轴以 Ω 扳动它
a1 = fig.add_axes([0.0, 0.05, 0.5, 0.92], projection="3d")
setup(a1, 1.0)
a1.plot([0, 0], [-0.9, 0.9], [0, 0], color=C["muted"], lw=1.0, ls="-.")
disk(a1, (0, 0.25, 0), (0, 1, 0), 0.45, "#c6dbef")
a1.plot([0, 0], [-0.5, 0.25], [0, 0], color=C["ink"], lw=4)                      # 主轴
q3(a1, (0, 0.25, 0), (0, 0.75, 0), C["x"])
a1.text(0, 1.05, 0.05, r"$\boldsymbol{L} = I_3\omega\,\hat s$", fontsize=13, color=C["x"])
q3(a1, (0, 0, 0), (0, 0, 0.85), C["z"])
a1.text(0.04, 0, 0.9, r"$\boldsymbol{\Omega}$" + T("（手腕扳动）", " (wrist turns)"), fontsize=12, color=C["z"])
tt = np.linspace(0.3, 2.0 * math.pi - 0.6, 50)
a1.plot(0.22 * np.cos(tt), 0.22 * np.sin(tt), 0.62 + 0 * tt, color=C["z"], lw=1.2)
q3(a1, (0, 0, 0), (-0.8, 0, 0), C["accent"])
a1.text(-0.95, -0.05, -0.2, r"$\boldsymbol{M} = \boldsymbol{\Omega}\times\boldsymbol{L}$", fontsize=13, color=C["accent"])
a1.text2D(0.05, 0.06, T("(a) 扳动高速旋转的电主轴：M 垂直于 Ω 和 L", "(a) turning a fast spindle: M is normal to both Ω and L"),
          transform=a1.transAxes, fontsize=11)

# (b) 陀螺仪：支点在原点，轴沿 x 水平，盘心在 x = l
a2 = fig.add_axes([0.5, 0.05, 0.5, 0.92], projection="3d")
setup(a2, 1.0)
a2.plot([0, 0], [0, 0], [-0.8, 0], color="#5d6b73", lw=5)                          # 支架
a2.scatter([0], [0], [0], s=30, color=C["ink"], depthshade=False)
lx = 0.6
a2.plot([0, lx + 0.12], [0, 0], [0, 0], color=C["ink"], lw=3)
disk(a2, (lx, 0, 0), (1, 0, 0), 0.32, "#c6dbef")
q3(a2, (lx, 0, 0), (0.45, 0, 0), C["x"])
a2.text(lx + 0.5, 0, 0.08, r"$\boldsymbol{L}$", fontsize=13, color=C["x"])
q3(a2, (lx, 0, 0), (0, 0, -0.55), C["muted"])
a2.text(lx + 0.04, 0, -0.62, r"$m\mathfrak{g}$", fontsize=13, color=C["muted"])
q3(a2, (0, 0, 0), (0, 0.75, 0), C["accent"])
a2.text(-0.05, 0.8, 0.05, r"$\boldsymbol{M} = m\mathfrak{g}l$" + T("（水平）", " (horizontal)"), fontsize=12, color=C["accent"])
tt = np.linspace(-0.3, 1.9, 60)
a2.plot(lx * np.cos(tt), lx * np.sin(tt), 0 * tt, color=C["z"], lw=1.2, ls="--")
q3(a2, (0, 0, 0.0), (0, 0, 0.7), C["z"])
a2.text(0.03, 0, 0.75, r"$\boldsymbol{\Omega} = \dfrac{m\mathfrak{g}l}{I_3\omega}$", fontsize=12, color=C["z"])
a2.text(lx * 0.5, -0.1, -0.12, "l", fontsize=12, style="italic")
a2.text2D(0.05, 0.06, T("(b) 陀螺仪：重力矩使轴在水平面内进动", "(b) a gyroscope: the gravity moment makes the axle precess"),
          transform=a2.transAxes, fontsize=11)
figure(fig, "fig23_3_2")
