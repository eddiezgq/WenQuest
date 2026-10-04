"""2.6 节的计算：

算例 2.6.1  二维激光雷达给出的是 (距离 r, 方位角 θ)。机器人正前方（x 轴）4.0 m 处有一面与 x 轴垂直的墙，雷达在
            θ = −30°、−20°、…、30° 七个方向上测到墙。求各点的距离，并换算成直角坐标（都应在 x = 4 m 上，图 2.6.2）。
            另有一点在 (2.5 m, 120°)；反过来，点 (−3, −4) m 的极坐标是多少？比较 atan2 与 arctan。
算例 2.6.2  SCARA 机器人末端在柱坐标 (ρ, φ, z) = (0.40 m, 50°, 0.12 m)，换算成直角坐标。
算例 2.6.3  三维激光雷达测到一点：距离 12.0 m，方位角 40°，仰角 8°（雷达手册的写法，从水平面向上量）。换算成球坐标
            （极角从 z 轴量起）和直角坐标。
算例 2.6.4  估一估，再算：北京（39.90°N，116.40°E）到上海（31.23°N，121.47°E）的大圆距离。地球取半径 6371 km 的球，
            两地的位置矢量用球坐标写出，夹角由点积求出。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

rad, deg = math.radians, math.degrees
# ---- 算例 2.6.1
th = np.arange(-30, 31, 10.0)
rr = 4.0 / np.cos(np.radians(th))
xs, ys = rr * np.cos(np.radians(th)), rr * np.sin(np.radians(th))
assert np.allclose(xs, 4.0)
r_list = "、".join(f"{v:.3f}" for v in rr)
P = (2.5 * math.cos(rad(120)), 2.5 * math.sin(rad(120)))
q = (-3.0, -4.0)
rq = math.hypot(*q)
t_atan2 = deg(math.atan2(q[1], q[0]))
t_atan = deg(math.atan(q[1] / q[0]))
out(r_list=r_list, r30=rr[0], y30=ys[0], y30n=-ys[0], Px=P[0], Py=P[1], rq=rq, t_atan2=t_atan2, t_atan2p=t_atan2 + 360, t_atan=t_atan)

# ---- 算例 2.6.2
rho, phi, z = 0.40, 50.0, 0.12
out(cx=rho * math.cos(rad(phi)), cy=rho * math.sin(rad(phi)), cz=z)

# ---- 算例 2.6.3
R3, az, el = 12.0, 40.0, 8.0
pol = 90.0 - el
X3 = R3 * math.sin(rad(pol)) * math.cos(rad(az))
Y3 = R3 * math.sin(rad(pol)) * math.sin(rad(az))
Z3 = R3 * math.cos(rad(pol))
assert abs(math.sqrt(X3 ** 2 + Y3 ** 2 + Z3 ** 2) - R3) < 1e-12
out(pol=pol, X3=X3, Y3=Y3, Z3=Z3)

# ---- 算例 2.6.4：大圆距离
Re = 6371.0


def unit(lat, lon):
    """纬度、经度 → 球心指向该点的单位矢量。球坐标的极角 θ = 90° − 纬度，方位角 φ = 经度。"""
    t, p = rad(90 - lat), rad(lon)
    return np.array([math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t)])


bj, sh = (39.90, 116.40), (31.23, 121.47)
u1, u2 = unit(*bj), unit(*sh)
cosd = float(u1 @ u2)
ang = deg(math.acos(cosd))
dist = Re * math.acos(cosd)
# 估算：把附近一小块地面看成平面，南北 1° 纬度约 111 km，东西 1° 经度约 111 cos(平均纬度) km
dlat, dlon = sh[0] - bj[0], sh[1] - bj[1]
km_deg = 2 * math.pi * Re / 360
flat = math.hypot(dlat * km_deg, dlon * km_deg * math.cos(rad((bj[0] + sh[0]) / 2)))
chord = Re * float(np.linalg.norm(u1 - u2))
out(bj_str=f"{bj[0]:.2f}°N，{bj[1]:.2f}°E", sh_str=f"{sh[0]:.2f}°N，{sh[1]:.2f}°E",
    cosd=cosd, ang=ang, dist=dist, km_deg=km_deg, flat=flat, chord=chord, Re=Re)

plt = style()
# ---- 图 2.6.1：极坐标与随位置转动的单位矢量
fig, ax = plt.subplots(figsize=(4.8, 3.9))
for rg in (1, 2, 3):
    ax.add_patch(plt.Circle((0, 0), rg, fill=False, color="#e3e7e9", lw=0.8))
for a in range(0, 360, 30):
    ax.plot([0, 3.2 * math.cos(rad(a))], [0, 3.2 * math.sin(rad(a))], color="#eef1f2", lw=0.8, zorder=0)
for (r0, t0), nm in (((2.4, 35.0), "P"), ((2.0, 150.0), "Q")):
    p = np.array([r0 * math.cos(rad(t0)), r0 * math.sin(rad(t0))])
    er = np.array([math.cos(rad(t0)), math.sin(rad(t0))]); et = np.array([-math.sin(rad(t0)), math.cos(rad(t0))])
    ax.plot([0, p[0]], [0, p[1]], color=d.MUTED, lw=1, ls="--")
    ax.plot(*p, "o", color=d.INK, ms=4); ax.text(p[0] - 0.25, p[1] - 0.35, nm, fontsize=10)
    d.arrow(ax, p, p + 0.8 * er, d.VR, lw=2); ax.text(*(p + 0.95 * er), r"$\hat{\boldsymbol{e}}_r$", color=d.VR, fontsize=11, ha="center")
    d.arrow(ax, p, p + 0.8 * et, d.VA, lw=2); ax.text(*(p + 1.0 * et), r"$\hat{\boldsymbol{e}}_\theta$", color=d.VA, fontsize=11, ha="center")
from matplotlib.patches import Arc
ax.add_patch(Arc((0, 0), 1.2, 1.2, theta1=0, theta2=35, color=d.INK, lw=1)); ax.text(0.75, 0.2, r"$\theta$", fontsize=11)
ax.text(1.3, 0.95, r"$r$", fontsize=11)
ax.plot([-3.3, 3.3], [0, 0], color=d.INK, lw=0.8); ax.plot([0, 0], [-1.2, 3.3], color=d.INK, lw=0.8)
ax.text(3.25, -0.3, "x"); ax.text(0.1, 3.15, "y")
ax.set_xlim(-3.4, 3.6); ax.set_ylim(-1.2, 3.4); ax.set_aspect("equal"); d.clean(ax)
figure(fig, "fig2_6_1")

# ---- 图 2.6.2：激光雷达扫墙
fig, ax = plt.subplots(figsize=(4.6, 3.4))
ax.plot([4.0, 4.0], [-3, 3], color=d.INK, lw=4, solid_capstyle="butt")
ax.text(4.15, 2.6, T("墙", "wall"), fontsize=9)
for t0, r0, x0, y0 in zip(th, rr, xs, ys):
    ax.plot([0, x0], [0, y0], color=d.VR, lw=0.8, alpha=0.7)
    ax.plot(x0, y0, "o", color=d.VR, ms=4)
ax.text(xs[0] - 0.2, ys[0] - 0.35, f"({rr[0]:.2f} m, −30°)", fontsize=8.5, ha="right", color=d.VR)
ax.add_patch(plt.Rectangle((-0.4, -0.3), 0.8, 0.6, fc="#c8d0d4", ec=d.INK, zorder=4))
ax.plot(-2.5 * 0.5, 2.5 * math.sin(rad(120)), "s", color=d.VA, ms=5)
ax.text(-1.25, 2.4, T("(2.5 m, 120°) 的点", "point at (2.5 m, 120°)"), fontsize=8.5, ha="center", color=d.VA)
ax.set_xlim(-2.6, 5); ax.set_ylim(-3, 3); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig2_6_2")

# ---- 图 2.6.3：柱坐标与球坐标
fig = plt.figure(figsize=(7.6, 3.6))
for k in range(2):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    for v, c, n in ((np.array([1.6, 0, 0]), d.X_, "x"), (np.array([0, 1.6, 0]), d.Y_, "y"), (np.array([0, 0, 1.5]), d.Z_, "z")):
        ax.quiver(0, 0, 0, *v, color=c, lw=1, arrow_length_ratio=0.06); ax.text(*(v * 1.07), n, color=c)
    Pp = np.array([0.9, 0.8, 0.9])
    ax.plot([0, Pp[0]], [0, Pp[1]], [0, 0], color=d.MUTED, lw=1, ls="--")
    ax.plot([Pp[0]] * 2, [Pp[1]] * 2, [0, Pp[2]], color=d.MUTED, lw=1, ls="--")
    ax.plot([Pp[0]], [Pp[1]], [Pp[2]], "o", color=d.INK, ms=4); ax.text(*(Pp + 0.06), "P", fontsize=10)
    ph = np.linspace(0, math.atan2(Pp[1], Pp[0]), 30)
    ax.plot(0.4 * np.cos(ph), 0.4 * np.sin(ph), 0 * ph, color=d.INK, lw=1); ax.text(0.45, 0.12, 0, r"$\varphi$", fontsize=11)
    if k == 0:
        ax.text(Pp[0] * 0.75, Pp[1] * 0.75 + 0.12, 0.02, r"$\rho$", fontsize=12)
        ax.text(Pp[0] + 0.05, Pp[1], Pp[2] / 2, r"$z$", fontsize=12)
        ax.set_title(T("柱坐标 ", "cylindrical ") + r"$(\rho,\ \varphi,\ z)$", fontsize=9)
    else:
        ax.plot([0, Pp[0]], [0, Pp[1]], [0, Pp[2]], color=d.VR, lw=2)
        ax.text(*(Pp / 2 + np.array([-0.1, 0, 0.12])), r"$r$", fontsize=12, color=d.VR)
        rr_ = np.linalg.norm(Pp); tt = np.linspace(0, math.acos(Pp[2] / rr_), 30); pp = math.atan2(Pp[1], Pp[0])
        ax.plot(0.45 * np.sin(tt) * math.cos(pp), 0.45 * np.sin(tt) * math.sin(pp), 0.45 * np.cos(tt), color=d.INK, lw=1)
        ax.text(0.12, 0.12, 0.5, r"$\theta$", fontsize=11)
        ax.set_title(T("球坐标 ", "spherical ") + r"$(r,\ \theta,\ \varphi)$" + T("，θ 从 z 轴量起", ", θ from the z axis"), fontsize=9)
    ax.set_xlim(0, 1.6); ax.set_ylim(0, 1.6); ax.set_zlim(0, 1.5)
    ax.view_init(elev=20, azim=25); ax.set_axis_off(); ax.set_box_aspect((1, 1, 0.95))
figure(fig, "fig2_6_3")
