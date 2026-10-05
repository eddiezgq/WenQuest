"""21.3 节的示意图。

图 21.3.1：(a) 差速 AGV：某一位姿下允许的速度只在车头方向的一条直线上（一阶约束，第 19 章）；
          (b) X2：某一姿态下可以产生的加速度只在一条线段上：从 −𝔤ẑ 出发、沿 z_b、长 4f_max/m（二阶约束）。侧视 x–z 平面。
图 21.3.2：横移 2 m（算例 21.3.2）：倾角、侧向加速度、侧向速度、位移随时间的变化；X2 与假想的全驱动飞行器比较。
图 21.3.3：倾斜旋翼的六旋翼（算例 21.3.3）：(a) 俯视，推力方向交替向两侧倾斜 α；(b) 机身水平时的最大侧向加速度与悬停推力的增加。
"""
import math

import numpy as np

from _fig21 import C, arrow, side_drone
from _uav import G, x2
from bookout import T, figure, style
import ex21_3 as E

plt = style()
P = x2()
m, fmax = P["m"], P["fmax"]

# ---------------------------------------------------------------- 图 21.3.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.8, 5.2))
a1.set_aspect("equal")
a1.axis("off")
# 俯视 AGV（简图）：车体矩形、车头方向、允许速度的直线
L, Wd = 0.6, 0.4
for k, (x0, y0, hd) in enumerate(((0.0, 0.0, 0.0), (1.4, 0.9, math.radians(35)))):
    Rm = np.array([[math.cos(hd), -math.sin(hd)], [math.sin(hd), math.cos(hd)]])
    box = np.array([[-L / 2, -Wd / 2], [L / 2, -Wd / 2], [L / 2, Wd / 2], [-L / 2, Wd / 2], [-L / 2, -Wd / 2]]) @ Rm.T + [x0, y0]
    a1.fill(box[:, 0], box[:, 1], color=C["body"], ec=C["dark"], lw=1.0, zorder=2)
    for sy in (-1, 1):
        wpts = np.array([[-0.12, sy * Wd / 2 - 0.03], [0.12, sy * Wd / 2 - 0.03], [0.12, sy * Wd / 2 + 0.03], [-0.12, sy * Wd / 2 + 0.03]]) @ Rm.T + [x0, y0]
        a1.fill(wpts[:, 0], wpts[:, 1], color=C["dark"], zorder=3)
    u = Rm @ np.array([1.0, 0.0])
    a1.plot([x0 - 1.0 * u[0], x0 + 1.0 * u[0]], [y0 - 1.0 * u[1], y0 + 1.0 * u[1]], color=C["blue"], lw=2.4, alpha=0.8, zorder=1)
    arrow(a1, (x0, y0), (x0 + 0.75 * u[0], y0 + 0.75 * u[1]), C["blue"], 2.0, 12, z=4)
a1.text(-0.95, -0.42, T("允许的速度：沿车头方向的一条直线", "allowed velocities: a line along the heading"), color=C["blue"], fontsize=10)
a1.text(-0.95, 1.55, T("位姿不同，直线的方向不同；\n但任何位姿都能到达（第 19 章）", "the line turns with the pose,\nyet every pose is reachable (Chapter 19)"),
        fontsize=9.5, color=C["muted"])
a1.set_xlim(-1.05, 2.6)
a1.set_ylim(-0.6, 2.05)
a1.set_title(T("(a) 差速 AGV：约束在速度上（一阶）", "(a) differential AGV: a constraint on velocity (first order)"), fontsize=11)

a2.set_aspect("equal")
a2.axis("off")
k = 0.06                                                  # 1 m/s² 画成 0.06 个单位
g0 = np.array([0.0, -k * G])
amax = 4 * fmax / m
for deg, col in ((0, C["dark"]), (25, C["blue"]), (-40, C["green"])):
    th = math.radians(deg)
    zb = np.array([math.sin(th), math.cos(th)])
    end = g0 + k * amax * zb
    a2.plot([g0[0], end[0]], [g0[1], end[1]], color=col, lw=3.0, alpha=0.75, solid_capstyle="round")
    side_drone(a2, end + 0.18 * zb, -th, s=0.9, color=col, arms=0.28)
    a2.text(end[0] + (0.12 if deg >= 0 else -0.62), end[1] - (0.05 if deg >= 0 else 0.3),
            T(f"倾角 {abs(deg)}°", f"tilt {abs(deg)}°") if deg else T("水平", "level"), color=col, fontsize=10)
a2.plot(*g0, "o", ms=8, color=C["red"], zorder=6)
a2.text(g0[0] + 0.1, g0[1] - 0.1, T(r"$-\mathfrak{g}\hat z$（推力为零）", r"$-\mathfrak{g}\hat z$ (zero thrust)"), color=C["red"], fontsize=11)
a2.plot(0, 0, "+", ms=12, color=C["ink"], mew=1.5)
a2.text(0.08, 0.05, T("加速度为零（悬停）", "zero acceleration (hover)"), fontsize=9.5)
arrow(a2, (-1.85, -1.0), (-1.45, -1.0), C["x"], 1.2, 9)
arrow(a2, (-1.85, -1.0), (-1.85, -0.6), C["z"], 1.2, 9)
a2.text(-1.42, -1.05, r"$\ddot p_x$", color=C["x"], fontsize=11)
a2.text(-1.95, -0.52, r"$\ddot p_z$", color=C["z"], fontsize=11)
a2.text(-1.9, 2.55, T("每个姿态下：只能沿 $z_b$ 的一条线段加速，\n线段从 $-\\mathfrak{g}\\hat z$ 出发，长 $4f_{\\max}/m$",
                      "at each attitude: acceleration only on a segment along $z_b$,\nstarting at $-\\mathfrak{g}\\hat z$, of length $4f_{\\max}/m$"), fontsize=9.5, color=C["muted"])
a2.set_xlim(-2.0, 2.3)
a2.set_ylim(-1.2, 3.0)
a2.set_title(T("(b) X2：约束在加速度上（二阶）", "(b) X2: a constraint on acceleration (second order)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig21_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.3.2
t, ph, a, v, y = E.profile(E.h_star)
Ti = E.T_ideal
ti = np.linspace(0, Ti, 800)
ai = np.where(ti < Ti / 2, E.a_cap, -E.a_cap)
vi = np.where(ti < Ti / 2, E.a_cap * ti, E.a_cap * (Ti - ti))
yi = np.where(ti < Ti / 2, 0.5 * E.a_cap * ti ** 2, E.d - 0.5 * E.a_cap * (Ti - ti) ** 2)
fig, axs = plt.subplots(1, 4, figsize=(13.0, 3.6))
axs[0].plot(t, np.degrees(ph), color=C["blue"], lw=1.8, label="X2")
axs[0].plot(ti, 0 * ti, color=C["orange"], lw=1.5, ls="--", label=T("全驱动（不倾斜）", "fully actuated (no tilt)"))
axs[1].plot(t, a, color=C["blue"], lw=1.8)
axs[1].plot(ti, ai, color=C["orange"], lw=1.5, ls="--")
axs[2].plot(t, v, color=C["blue"], lw=1.8)
axs[2].plot(ti, vi, color=C["orange"], lw=1.5, ls="--")
axs[3].plot(t, y, color=C["blue"], lw=1.8)
axs[3].plot(ti, yi, color=C["orange"], lw=1.5, ls="--")
for ax_, yl, tt in zip(axs, (T("横滚角 φ / (°)", "roll φ / (°)"), T("侧向加速度 / (m/s²)", "lateral acceleration / (m/s²)"),
                             T("侧向速度 / (m/s)", "lateral speed / (m/s)"), T("侧向位移 / m", "lateral displacement / m")),
                       (T("(a) 倾角", "(a) tilt"), T("(b) 加速度", "(b) acceleration"), T("(c) 速度", "(c) speed"), T("(d) 位移", "(d) displacement"))):
    ax_.set_xlabel(T("时间 / s", "time / s"))
    ax_.set_ylabel(yl)
    ax_.grid(alpha=0.25)
    ax_.set_title(tt, fontsize=10.5)
axs[0].legend(fontsize=9, frameon=False, loc="lower left")
axs[3].axhline(E.d, color=C["muted"], lw=0.6, ls=":")
fig.tight_layout()
figure(fig, "fig21_3_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.3.3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.8), gridspec_kw={"width_ratios": [1.0, 1.15]})
a1.set_aspect("equal")
a1.axis("off")
for i in range(6):
    az = math.radians(60 * i)
    r = 0.25 * np.array([math.cos(az), math.sin(az)])
    a1.plot([0, r[0]], [0, r[1]], color=C["dark"], lw=3)
    a1.add_patch(__import__("matplotlib").patches.Circle(tuple(r), 0.09, fc=C["rotor"], ec=C["dark"], alpha=0.6))
    e_t = np.array([-math.sin(az), math.cos(az)])
    s = 1 if i % 2 == 0 else -1
    arrow(a1, r, r + s * 0.12 * e_t, C["blue"], 2.0, 11)
a1.add_patch(__import__("matplotlib").patches.Circle((0, 0), 0.06, fc=C["body"], ec=C["dark"]))
a1.text(0, -0.43, T("蓝色箭头：推力的水平分量（交替向两侧）", "blue: horizontal part of each thrust (alternating sides)"), ha="center",
        fontsize=9.5, color=C["blue"])
a1.set_xlim(-0.45, 0.45)
a1.set_ylim(-0.47, 0.4)
a1.set_title(T("(a) 推力方向绕机臂交替倾斜 ±α（俯视）", "(a) thrusts tilted ±α about the arms, alternately (top view)"), fontsize=11)
al = np.linspace(0.5, 35, 70)
acc, eff = [], []
for dd in al:
    A6 = E.hexa(math.radians(dd))
    from scipy.optimize import linprog
    res = linprog(c=-A6[3], A_eq=A6[[0, 1, 2, 4, 5]], b_eq=[0, 0, 0, 0, m * G], bounds=[(0, fmax)] * 6, method="highs")
    acc.append(-res.fun / m)
    eff.append((1 / math.cos(math.radians(dd)) - 1) * 100)
a2.plot(al, acc, color=C["blue"], lw=1.8)
a2.set_xlabel(T("倾斜角 α / (°)", "tilt angle α / (°)"))
a2.set_ylabel(T("机身水平时的最大侧向加速度 / (m/s²)", "max lateral acceleration, body level / (m/s²)"), color=C["blue"])
b2 = a2.twinx()
b2.plot(al, eff, color=C["orange"], lw=1.6, ls="--")
b2.set_ylabel(T("悬停推力增加 / %", "extra hover thrust / %"), color=C["orange"])
a2.axhline(E.a_cap, color=C["muted"], lw=0.7, ls=":")
a2.text(1, E.a_cap - 0.3, T("X2 倾斜 25° 时的侧向加速度", "X2's lateral acceleration at 25° tilt"), fontsize=9, color=C["muted"])
a2.grid(alpha=0.25)
a2.set_xlim(0, 35)
a2.set_title(T("(b) 侧推能力与悬停代价（示意值）", "(b) side force and hover cost (illustrative)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig21_3_3")
plt.close(fig)
