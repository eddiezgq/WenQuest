"""21.2 节的示意图。

图 21.2.1：(a) 同一高度上向前加速（算例 21.2.1）：推力 f z_b、重力 m𝔤 与合力 m a 的三角形，倾角 θ；
          (b) 保持高度时倾角、总推力与水平加速度的关系，标出 X2 的全推力极限和 30° 的倾角限制（示意值）。
图 21.2.2：(a) 由推力方向 z_b 和偏航角 ψ 构造姿态（定理 21.2.1，倾角取 30° 只为看清）；
          (b) 协调转弯的后视图（算例 21.2.3）：向左压坡度 18.1°，推力的水平分量提供向心力。
图 21.2.3：加速度在 T_r 内由 0 线性增大到 2 m/s²（T_r = 0.2、0.1、0.05 s）：加速度、俯仰角、俯仰角速度。
"""
import math

import numpy as np

from _fig21 import C, arrow, side_drone
from _uav import EZ, G, attitude, flat, x2
from bookout import T, figure, style

plt = style()
P = x2()
m = P["m"]
W = m * G

# ---------------------------------------------------------------- 图 21.2.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.8), gridspec_kw={"width_ratios": [1.0, 1.15]})
a = 2.0
th = math.atan2(a, G)
f = m * math.hypot(a, G)
a1.set_aspect("equal")
a1.axis("off")
o = np.array([0.0, 0.0])
k = 0.11                                           # 1 N 画成 0.11 个单位
zb = side_drone(a1, o, -th, s=2.2, arms=0.3)        # 机头在右，低头 θ：图中顺时针转
tip = o + k * f * zb
arrow(a1, o, tip, C["blue"], 2.2, 13)
a1.text(tip[0] + 0.05, tip[1], r"$f\,z_b$", color=C["blue"], fontsize=13)
g_tip = o + np.array([0, -k * W])
arrow(a1, o, g_tip, C["dark"], 2.0, 13)
a1.text(g_tip[0] + 0.06, g_tip[1] + 0.1, r"$-m\mathfrak{g}\,\hat z$", color=C["dark"], fontsize=12)
arrow(a1, g_tip, g_tip + (tip - o), C["blue"], 1.0, 9, ls="--")
res = tip + np.array([0, -k * W])
arrow(a1, o, res, C["red"], 2.2, 13)
a1.text(res[0] - 0.05, -0.36, r"$m\,\ddot p$", color=C["red"], fontsize=13)
a1.plot([0, 0], [0, 1.6], color=C["muted"], lw=0.7, ls=":")
t = np.linspace(math.pi / 2 - th, math.pi / 2, 30)
a1.plot(0.95 * np.cos(t), 0.95 * np.sin(t), color=C["accent"], lw=1.2)
a1.text(0.12, 1.0, r"$\theta$", color=C["accent"], fontsize=13)
arrow(a1, (-1.1, -1.2), (-0.7, -1.2), C["x"], 1.3, 9)
arrow(a1, (-1.1, -1.2), (-1.1, -0.8), C["z"], 1.3, 9)
a1.text(-0.68, -1.25, "$x_s$", color=C["x"], fontsize=11)
a1.text(-1.17, -0.74, "$z_s$", color=C["z"], fontsize=11)
a1.text(0.74, -0.2, T("机头", "nose"), fontsize=9.5, color=C["accent"], va="top")
a1.set_xlim(-1.25, 1.35)
a1.set_ylim(-1.55, 1.75)
a1.set_title(T(r"(a) 以 $\ddot p = 2$ m/s² 向前加速，高度不变", r"(a) accelerating forward at 2 m/s², height kept"), fontsize=11)

ah = np.linspace(0, 40, 400)
tilt = np.degrees(np.arctan2(ah, G))
ratio = np.hypot(ah, G) / G
a2.plot(ah, tilt, color=C["blue"], lw=1.8, label=T("倾角 / (°)", "tilt / (°)"))
a2.set_xlabel(T("水平加速度 / (m/s²)", "horizontal acceleration / (m/s²)"))
a2.set_ylabel(T("倾角 / (°)", "tilt / (°)"), color=C["blue"])
a2.set_ylim(0, 90)
a2.set_xlim(0, 40)
b2 = a2.twinx()
b2.plot(ah, ratio, color=C["orange"], lw=1.6, ls="--")
b2.set_ylabel(T(r"总推力 / 重力 $f/(m\mathfrak{g})$", r"collective / weight $f/(m\mathfrak{g})$"), color=C["orange"])
b2.set_ylim(0, 4.5)
a_full = G * math.tan(math.acos(W / (4 * P["fmax"])))
for x, y, txt, dx, dy in ((2.0, math.degrees(th), T("算例 21.2.1", "Example 21.2.1"), 1.2, -6),
                          (G * math.tan(math.radians(30)), 30, T("倾角限制 30°（示意）", "tilt limit 30° (illustrative)"), -5.4, 3),
                          (a_full, math.degrees(math.acos(W / 52)), T("四个旋翼全推力", "all rotors at full thrust"), -12.5, -1.5)):
    a2.plot(x, y, "o", color=C["blue"], ms=6, zorder=5)
    a2.text(x + dx, y + dy, txt, fontsize=9.5)
b2.axhline(4 * P["fmax"] / W, color=C["orange"], lw=0.8, ls=":")
b2.text(1, 4 * P["fmax"] / W + 0.08, T("推重比 4.0", "thrust-to-weight 4.0"), color=C["orange"], fontsize=9)
a2.grid(alpha=0.25)
a2.set_title(T("(b) 保持高度：倾角与总推力随水平加速度增大", "(b) height kept: tilt and thrust grow with acceleration"), fontsize=11)
fig.tight_layout()
figure(fig, "fig21_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.2.2
fig = plt.figure(figsize=(11.8, 5.2))
ax = fig.add_subplot(1, 2, 1, projection="3d")
psi = math.radians(40)
az = psi + math.radians(150)                                                   # 示意：向后上方倾 30°，x_b 在水平面之上，便于看清
zb = np.array([math.sin(math.radians(30)) * math.cos(az), math.sin(math.radians(30)) * math.sin(az), math.cos(math.radians(30))])
R, th_, ph_ = attitude(zb, psi)
yc = np.array([-math.sin(psi), math.cos(psi), 0])
xc = np.array([math.cos(psi), math.sin(psi), 0])


def v3(vv, col, lab, lw=2.0, ls="-", off=(0, 0, 0)):
    ax.quiver(0, 0, 0, *vv, color=col, lw=lw, arrow_length_ratio=0.12, linestyle=ls)
    ax.text(*(1.1 * np.asarray(vv) + np.asarray(off)), lab, color=col, fontsize=12)


rr = np.linspace(-1, 1, 2)
X, Y = np.meshgrid(rr, rr)
ax.plot_surface(X, Y, 0 * X, color=C["light"], alpha=0.25, linewidth=0)
v3(EZ, C["muted"], r"$\hat z$", 1.2, off=(0, 0, 0.02))
v3(zb, C["z"], r"$z_b$")
v3(yc, C["green"], r"$y_c$", 1.2, "--", off=(0, 0.0, 0.1))
v3(xc, C["red"], r"$x_c$", 1.0, ":", off=(0.03, 0, -0.05))
v3(R[:, 0], C["x"], r"$x_b$")
v3(R[:, 1], C["y"], r"$y_b$", off=(0.05, 0.0, -0.2))
t = np.linspace(0, psi, 30)
ax.plot(0.45 * np.cos(t), 0.45 * np.sin(t), 0 * t, color=C["accent"], lw=1.2)
ax.text(0.5 * math.cos(psi / 2), 0.5 * math.sin(psi / 2), 0, r"$\psi$", color=C["accent"], fontsize=12)
ax.plot([1, 0], [0, 0], [0, 0], color=C["muted"], lw=0.6)
xh = R[:, 0].copy()
ax.plot([xh[0], xh[0]], [xh[1], xh[1]], [xh[2], 0], color=C["red"], lw=0.8, ls=":")      # x_b 末端到水平面的垂线
ax.plot([0, xh[0]], [0, xh[1]], [0, 0], color=C["red"], lw=1.4, ls=":")
ax.text(1.05, 0, 0, r"$x_s$", color=C["muted"], fontsize=10)
ax.set_xlim(-0.8, 1.0)
ax.set_ylim(-0.8, 1.0)
ax.set_zlim(0, 1.2)
ax.view_init(elev=20, azim=-75)
ax.set_box_aspect((1.8, 1.8, 1.2))
ax.set_axis_off()
ax.set_title(T(r"(a) $x_b \perp y_c$：$x_b$ 的水平投影沿 $x_c$，偏航角为 ψ", r"(a) $x_b \perp y_c$: $x_b$ projects onto $x_c$, yaw is ψ"),
             fontsize=11)

a2 = fig.add_subplot(1, 2, 2)
a2.set_aspect("equal")
a2.axis("off")
ac = 4.0 ** 2 / 5.0
phi = math.atan2(ac, G)
f3 = m * math.hypot(ac, G)
k = 0.1
zb2 = side_drone(a2, (0, 0), phi, s=2.2, arms=0.3)       # 后视：左侧（圆心一侧）在图的左边，向左压坡度：逆时针转
tip = k * f3 * zb2
arrow(a2, (0, 0), tip, C["blue"], 2.2, 13)
a2.text(tip[0] - 0.42, tip[1] + 0.04, r"$f\,z_b$", color=C["blue"], fontsize=13)
arrow(a2, (0, 0), (0, -k * W), C["dark"], 2.0, 13)
a2.text(0.06, -k * W + 0.1, r"$-m\mathfrak{g}\,\hat z$", color=C["dark"], fontsize=12)
arrow(a2, (0, 0), (-k * m * ac, 0), C["red"], 2.2, 13)
a2.text(-k * m * ac - 0.05, 0.1, r"$m v^2/\rho$", color=C["red"], fontsize=12, ha="center")
a2.plot([0, 0], [0, 1.5], color=C["muted"], lw=0.7, ls=":")
t = np.linspace(math.pi / 2, math.pi / 2 + phi, 30)
a2.plot(1.0 * np.cos(t), 1.0 * np.sin(t), color=C["accent"], lw=1.2)
a2.text(-0.33, 1.07, r"$|\varphi|$", color=C["accent"], fontsize=12)
arrow(a2, (-0.6, -1.15), (-1.6, -1.15), C["muted"], 1.0, 9)
a2.text(-1.1, -1.08, T("转弯中心方向", "towards the turn centre"), fontsize=9.5, color=C["muted"], ha="center")
a2.text(0.6, -1.15, T("从机尾往前看", "seen from behind"), fontsize=9.5, color=C["muted"])
a2.set_xlim(-1.75, 1.35)
a2.set_ylim(-1.45, 1.65)
a2.set_title(T("(b) 协调转弯：v = 4 m/s，ρ = 5 m，向左压坡度 18.1°", "(b) coordinated turn: v = 4 m/s, ρ = 5 m, banked 18.1° left"),
             fontsize=11)
fig.tight_layout()
figure(fig, "fig21_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.2.3
fig, axs = plt.subplots(1, 3, figsize=(12.0, 3.8))
cols = [C["blue"], C["green"], C["orange"]]
for Tr, col in zip((0.2, 0.1, 0.05), cols):
    jj = 2.0 / Tr
    ts = np.linspace(-0.05, 0.3, 701)
    acc, ths, wys = [], [], []
    for tt in ts:
        tc = min(max(tt, 0.0), Tr)
        aa = jj * tc
        j_now = jj if 0 <= tt <= Tr else 0.0
        d = [np.zeros(3), np.zeros(3), np.array([aa, 0, 0]), np.array([j_now, 0, 0]), np.zeros(3)]
        F = flat(d, 0.0, 0.0, 0.0, m)
        acc.append(aa)
        ths.append(math.degrees(F["th"]))
        wys.append(math.degrees(F["w"][1]))
    lab = f"$T_r$ = {Tr:g} s"
    axs[0].plot(ts, acc, color=col, lw=1.6, label=lab)
    axs[1].plot(ts, ths, color=col, lw=1.6)
    axs[2].plot(ts, wys, color=col, lw=1.6)
axs[0].set_ylabel(T("水平加速度 / (m/s²)", "horizontal acceleration / (m/s²)"))
axs[1].set_ylabel(T("俯仰角 θ / (°)", "pitch θ / (°)"))
axs[2].set_ylabel(T(r"俯仰角速度 $\omega_y$ / (°/s)", r"pitch rate $\omega_y$ / (°/s)"))
for a_ in axs:
    a_.set_xlabel(T("时间 / s", "time / s"))
    a_.grid(alpha=0.25)
axs[0].legend(fontsize=9.5, frameon=False, loc="lower right")
axs[0].set_title(T("(a) 加速度线性增大", "(a) acceleration ramped up"), fontsize=10.5)
axs[1].set_title(T("(b) 机身随之低头", "(b) the nose goes down with it"), fontsize=10.5)
axs[2].set_title(T("(c) 角速度与加加速度成正比", "(c) body rate follows the jerk"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig21_2_3")
plt.close(fig)
