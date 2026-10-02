"""10.4 节的示意图。

图 10.4.1：球面坐标 (r, θ, φ)（ISO 80000-2：θ 为极角，从 +z 量起；φ 为方位角）与点 P 处的局部基 e_r、e_θ、e_φ。
图 10.4.2：云台相机跟踪 AGV。(a) 几何关系（斜投影）；(b) 不同偏距 d 下水平转动角速度 φ̇ 随时间的变化，虚线为 90°/s 限速。
"""
import math

import numpy as np

from _kin import AXIS, C, G_COL, V_COL, arrow, oblique, sph_basis
from bookout import T, figure, style

plt = style()


def line3(ax, pts, sc=1.0, **kw):
    q = np.array([oblique(p, sc) for p in pts])
    ax.plot(q[:, 0], q[:, 1], **kw)


# ---------------------------------------------------------------- 图 10.4.1
fig, ax = plt.subplots(figsize=(5.8, 4.9))
ax.set_aspect("equal")
ax.axis("off")
for i, (lab, L) in enumerate((("x", 1.5), ("y", 1.6), ("z", 1.55))):
    e = np.zeros(3)
    e[i] = L
    arrow(ax, oblique(np.zeros(3)), oblique(e), AXIS[i], 1.1)
    ax.text(*(oblique(e) + np.array([0.04, -0.05 if i < 2 else 0.02])), f"${lab}$", color=AXIS[i], fontsize=12)
r, th, ph = 1.35, math.radians(50), math.radians(45)
er, et, ep = sph_basis(th, ph)
P = r * er
Pf = np.array([P[0], P[1], 0.0])
line3(ax, [np.zeros(3), P], color=C["ink"], lw=1.2)
line3(ax, [np.zeros(3), Pf], color=G_COL, lw=0.9, ls="--")
line3(ax, [Pf, P], color=G_COL, lw=0.9, ls="--")
ax.text(*(oblique(P * 0.6) + np.array([0.05, -0.08])), "$r$", fontsize=13)
# θ：从 +z 到 OP 的弧
a = np.linspace(0, th, 40)
line3(ax, [0.5 * (math.cos(t) * np.array([0, 0, 1.0]) + math.sin(t) * np.array([math.cos(ph), math.sin(ph), 0])) for t in a],
      color=C["accent"], lw=1.3)
ax.text(*(oblique(0.62 * (math.cos(th / 2) * np.array([0, 0, 1.0]) + math.sin(th / 2) * np.array([math.cos(ph), math.sin(ph), 0]))) + np.array([0.0, 0.02])),
        r"$\theta$", color=C["accent"], fontsize=13)
a = np.linspace(0, ph, 40)
line3(ax, [0.45 * np.array([math.cos(t), math.sin(t), 0]) for t in a], color=C["z"], lw=1.3)
ax.text(*(oblique(0.55 * np.array([math.cos(ph / 2), math.sin(ph / 2), 0])) + np.array([-0.05, -0.12])), r"$\varphi$", color=C["z"], fontsize=13)
ax.plot(*oblique(P), "o", color=C["ink"], ms=5, zorder=6)
ax.text(*(oblique(P) + np.array([-0.2, 0.05])), "P", fontsize=12)
for e, lab, col, off in ((er, r"$e_r$", AXIS[0], (0.03, 0.02)), (et, r"$e_\theta$", AXIS[1], (0.05, 0.02)),
                         (ep, r"$e_\varphi$", AXIS[2], (0.03, 0.02))):
    q = oblique(P + 0.55 * e)
    arrow(ax, oblique(P), q, col, 2.0)
    ax.text(*(q + np.array(off)), lab, color=col, fontsize=13)
ax.text(-1.3, -1.05, T(r"θ：从 +z 轴量起的极角，0 ≤ θ ≤ π；φ：方位角", r"θ: polar angle measured from +z, 0 ≤ θ ≤ π; φ: azimuth"),
        fontsize=9)
ax.text(-1.3, -1.2, T("（ISO 80000-2 的约定；部分数学书把 θ、φ 对调）", "(ISO 80000-2 convention; some mathematics books swap θ and φ)"),
        fontsize=9, color=G_COL)
ax.set_xlim(-1.35, 2.2)
ax.set_ylim(-1.3, 1.85)
figure(fig, "fig10_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.4.2
H, v = 3.0, 1.0
fig = plt.figure(figsize=(10.0, 4.4))
ax = fig.add_axes([0.0, 0.0, 0.45, 1.0])
ax.set_aspect("equal")
ax.axis("off")
s = 0.6                                   # 斜投影缩放
O = np.zeros(3)
for i, (lab, L) in enumerate((("x", 1.4), ("y", 1.3), ("z", 0.7))):
    e = np.zeros(3)
    e[i] = L
    arrow(ax, oblique(O, s), oblique(e, s), AXIS[i], 1.0)
    ax.text(*(oblique(e, s) + (np.array([-0.16, -0.1]) if i == 0 else np.array([0.03, 0.0]))), f"${lab}_g$", color=AXIS[i], fontsize=11)
ax.add_patch(plt.Rectangle(oblique(O, s) - np.array([0.12, 0.05]), 0.24, 0.1, color="#4a5560", zorder=4))
ax.text(*(oblique(O, s) + np.array([-0.85, 0.12])), T("云台相机（离地 H）", "gimbal camera (height H)"), fontsize=9)
# 地面与 AGV 路线
fl = [np.array([-3.0, -1.2, -H]), np.array([3.0, -1.2, -H]), np.array([3.0, 1.6, -H]), np.array([-3.0, 1.6, -H])]
q = np.array([oblique(p, s) for p in fl + [fl[0]]])
ax.fill(q[:, 0], q[:, 1], color="#eef1f3", zorder=0)
d = 0.5
line3(ax, sc=s, pts=[np.array([-3.0, d, -H]) * 1, np.array([3.0, d, -H])], color=V_COL, lw=1.0, ls="--")
line3(ax, sc=s, pts=[np.array([0, 0, -H]), np.array([0, d, -H])], color=C["ink"], lw=0.8)
ax.text(*(oblique([0, d / 2, -H], s) + np.array([-0.05, -0.17])), "$d$", fontsize=11)
line3(ax, sc=s, pts=[O, np.array([0, 0, -H])], color=G_COL, lw=0.8, ls=":")
ax.text(*(oblique([0, 0, -H / 2], s) + np.array([-0.2, 0.0])), "$H$", fontsize=11)
tg = np.array([-1.0, d, -H])
q = np.array([oblique(O, s), oblique(tg, s)])
ax.plot(q[:, 0], q[:, 1], color=C["accent"], lw=1.4)
ax.add_patch(plt.Rectangle(oblique(tg, s) - np.array([0.13, 0.06]), 0.26, 0.12, color="#1f77b4", alpha=0.8, zorder=5))
arrow(ax, oblique(tg, s) + np.array([0.0, 0.1]), oblique(tg + np.array([1.0, 0, 0]), s) + np.array([0.0, 0.1]), V_COL, 1.6)
ax.text(*(oblique(tg + np.array([0.6, 0, 0]), s) + np.array([-0.12, 0.16])), "$v$", color=V_COL, fontsize=12)
ax.text(*(oblique(tg, s) + np.array([0.18, -0.12])), "AGV", fontsize=10, color="#1f77b4")
ax.text(*(oblique(tg * 0.5, s) + np.array([0.1, 0.05])), T("视线 r", "line of sight r"), fontsize=10, color=C["accent"])
ax.text(-1.95, -2.55, T(r"水平转动角 = 方位角 $\varphi$；俯仰角由极角 $\theta$ 决定", r"pan angle = azimuth $\varphi$; tilt follows the polar angle $\theta$"),
        fontsize=9)
ax.set_xlim(-2.0, 2.2)
ax.set_ylim(-2.65, 0.75)
ax.set_title(T("(a) 几何关系", "(a) Geometry"), fontsize=11, y=1.0)
bx = fig.add_axes([0.55, 0.14, 0.42, 0.72])
t = np.linspace(-4, 4, 801)
for dd, col in ((0.25, C["x"]), (0.5, C["accent"]), (1.0, C["z"])):
    bx.plot(t, np.degrees(-v * dd / (v * v * t * t + dd * dd)), color=col, lw=1.5, label=f"$d$ = {dd} m")
bx.axhline(-90, color=C["ink"], ls="--", lw=0.9)
bx.text(1.6, -84, T("限速 −90°/s", "limit −90°/s"), fontsize=9)
bx.set_xlabel(T("时间 t / s（t = 0 时 AGV 离相机最近）", "time t / s (closest to the camera at t = 0)"), fontsize=9.5)
bx.set_ylabel(T(r"水平转动角速度 $\dot\varphi$ /(°/s)", r"pan rate $\dot\varphi$ /(°/s)"), fontsize=9.5)
bx.set_ylim(-240, 10)
bx.legend(fontsize=9, loc="lower right", frameon=False)
bx.grid(alpha=0.3)
bx.set_title(T("(b) 方位角的变化率（v = 1.0 m/s，H = 3.0 m）", "(b) Rate of the azimuth (v = 1.0 m/s, H = 3.0 m)"), fontsize=11)
figure(fig, "fig10_4_2")
plt.close(fig)
