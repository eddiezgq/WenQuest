"""10.5 节的示意图。

图 10.5.1：算例 10.5.1。(a) 工具尖在加速结束时的位置，切向单位矢量 e_t、主法线 e_n，切向加速度、法向加速度与总加速度；
           (b) 切向、法向、总加速度随时间的变化：在 t = 0.5 s 处总加速度突变。
图 10.5.2：算例 10.5.2。涂胶椭圆上各点的曲率（颜色），长轴端点与短轴端点的密切圆。
图 10.5.3：算例 10.5.3。同一时刻的速度 v、加速度 a，分别在直角、柱面、球面、自然坐标的局部基上分解。
"""
import math

import numpy as np

from _kin import A_COL, AXIS, C, G_COL, V_COL, arrow, cyl_basis, oblique, sph_basis, to_sph
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 10.5.1
R, at0, vmax = 0.10, 0.5, 0.25
t_acc = vmax / at0
u = 0.5 * at0 * t_acc ** 2 / R
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.2), gridspec_kw={"width_ratios": [1, 1.15]})
a1.set_aspect("equal")
a1.axis("off")
t = np.linspace(0, 2 * math.pi, 200)
a1.plot(R * np.cos(t), R * np.sin(t), color=C["ink"], lw=1.1)
tt = np.linspace(0, u, 40)
a1.plot(R * np.cos(tt), R * np.sin(tt), color=C["accent"], lw=3, alpha=0.6)
a1.text(R * 1.08, 0.012, T("加速段", "speed-up"), fontsize=9, color=C["accent"])
a1.plot(0, 0, "+", color=G_COL, ms=8)
a1.text(0.004, -0.016, T("圆心", "centre"), fontsize=9, color=G_COL)
P = R * np.array([math.cos(u), math.sin(u)])
et = np.array([-math.sin(u), math.cos(u)])
en = -P / R
a1.plot(*P, "o", color=C["ink"], ms=5, zorder=6)
a1.plot(*np.array([P - 0.06 * et, P + 0.12 * et]).T, color=C["x"], lw=0.7, ls=":")
a1.plot(*np.array([P, P + 0.1 * en]).T, color=C["y"], lw=0.7, ls=":")
a1.text(*(P + 0.125 * et + np.array([-0.004, 0.004])), T("$e_t$ 方向", "$e_t$ direction"), color=C["x"], fontsize=10)
a1.text(*(P + 0.1 * en + np.array([-0.006, 0.006])), T("$e_n$ 方向", "$e_n$ direction"), color=C["y"], fontsize=10, ha="right")
k = 0.11
at_v, an_v = at0 * et, vmax ** 2 / R * en
arrow(a1, P, P + k * at_v, A_COL, 1.2, ls="--")
arrow(a1, P, P + k * an_v, A_COL, 1.2, ls="--")
arrow(a1, P, P + k * (at_v + an_v), A_COL, 2.0)
a1.text(*(P + k * at_v + np.array([0.006, -0.008])), "$a_t$", color=A_COL, fontsize=11)
a1.text(*(P + k * an_v + np.array([0.004, -0.004])), "$a_n$", color=A_COL, fontsize=11)
a1.text(*(P + k * (at_v + an_v) + np.array([-0.022, 0.0])), "$a$", color=A_COL, fontsize=12)
a1.set_title(T("(a) 加速结束时（俯视）", "(a) End of the speed-up (top view)"), fontsize=11)
a1.set_xlim(-0.13, 0.17)
a1.set_ylim(-0.12, 0.2)
ts = np.linspace(0, 1.0, 1001)
atv = np.where(ts < t_acc, at0, 0.0)
anv = np.array([(at0 * x if x < t_acc else vmax) ** 2 / R for x in ts])
a2.plot(ts, atv, color=C["z"], lw=1.5, label=T("切向加速度 $a_t$", "tangential $a_t$"))
a2.plot(ts, anv, color=C["y"], lw=1.5, label=T("法向加速度 $a_n$", "normal $a_n$"))
a2.plot(ts, np.hypot(atv, anv), color=A_COL, lw=2.0, label=T("总加速度 |a|", "total |a|"))
a2.axvline(t_acc, color=G_COL, ls=":", lw=0.9)
a2.text(t_acc + 0.02, 0.05, T("加速结束", "speed-up ends"), fontsize=9, color=G_COL)
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("加速度 /(m/s²)", "acceleration /(m/s²)"))
a2.set_ylim(0, 0.9)
a2.grid(alpha=0.3)
a2.legend(fontsize=9, loc="upper right", frameon=False)
a2.set_title(T("(b) 加速度随时间的变化", "(b) Accelerations against time"), fontsize=11)
fig.tight_layout()
figure(fig, "fig10_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.5.2
a, b = 0.12, 0.08
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.set_aspect("equal")
ax.axis("off")
uu = np.linspace(0, 2 * math.pi, 400)
x, y = a * np.cos(uu), b * np.sin(uu)
kap = a * b / (a * a * np.sin(uu) ** 2 + b * b * np.cos(uu) ** 2) ** 1.5
pts = np.array([x, y]).T.reshape(-1, 1, 2)
from matplotlib.collections import LineCollection
segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
lc = LineCollection(segs, cmap="viridis", linewidths=4)
lc.set_array(kap[:-1])
ax.add_collection(lc)
cb = fig.colorbar(lc, ax=ax, fraction=0.04, pad=0.02)
cb.set_label(T("曲率 κ /(1/m)", "curvature κ /(1/m)"), fontsize=9.5)
r1, r2 = b * b / a, a * a / b
ax.plot(a - r1 + r1 * np.cos(uu), r1 * np.sin(uu), color=C["x"], lw=0.9, ls="--")
ua = np.linspace(math.radians(55), math.radians(125), 80)
ax.plot(r2 * np.cos(ua), b - r2 + r2 * np.sin(ua), color=C["z"], lw=0.9, ls="--")
ax.plot([a - r1, a], [0, 0], color=C["x"], lw=0.9)
ax.text(a - r1 / 2 - 0.012, 0.006, r"$1/\kappa_{\max}$", color=C["x"], fontsize=10)
ax.annotate("", xy=(0, b), xytext=(0, -0.1), arrowprops=dict(arrowstyle="-|>", color=C["z"], lw=0.9))
ax.text(-0.075, -0.098, r"$1/\kappa_{\min}$ = 0.18 m" + T("（圆心在下方图外）", " (centre below, off the figure)"), color=C["z"], fontsize=9)
ax.text(-0.17, 0.115, T("长轴端点曲率最大，短轴端点曲率最小；虚线为两处的密切圆",
                        "curvature is largest at the ends of the major axis, smallest at the ends of the minor axis; dashed: osculating circles"),
        fontsize=8.5)
ax.set_xlim(-0.18, 0.18)
ax.set_ylim(-0.12, 0.13)
figure(fig, "fig10_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.5.3
xc, yc, z0 = 0.40, 0.05, 0.10
w, t1 = math.pi / 2, 0.5
P = np.array([xc + a * math.cos(w * t1), yc + b * math.sin(w * t1), z0])
v1 = np.array([-a * w * math.sin(w * t1), b * w * math.cos(w * t1), 0])
a1v = np.array([-a * w * w * math.cos(w * t1), -b * w * w * math.sin(w * t1), 0])
cam = np.array([0.40, 0.05, 0.40])
uu = np.linspace(0, 2 * math.pi, 300)
E = np.array([xc + a * np.cos(uu), yc + b * np.sin(uu), z0 + 0 * uu]).T
phi = math.atan2(P[1], P[0])
er_c, ep_c, ez_c = cyl_basis(phi)
r, th, ph = to_sph(P - cam)
er_s, et_s, ep_s = sph_basis(th, ph)
et_n = v1 / np.linalg.norm(v1)
en_n = a1v - (a1v @ et_n) * et_n
en_n /= np.linalg.norm(en_n)
panels = [
    (T("(a) 直角坐标", "(a) Cartesian"), [(np.array([1.0, 0, 0]), "$e_x$"), (np.array([0, 1.0, 0]), "$e_y$")], None),
    (T("(b) 柱面坐标（轴为 SCARA 关节 1）", "(b) Cylindrical (axis = SCARA joint 1)"), [(er_c, r"$e_\rho$"), (ep_c, r"$e_\varphi$")], "cyl"),
    (T("(c) 球面坐标（原点为相机光心）", "(c) Spherical (origin = camera)"), [(er_s, "$e_r$"), (et_s, r"$e_\theta$"), (ep_s, r"$e_\varphi$")], "sph"),
    (T("(d) 自然坐标", "(d) Natural"), [(et_n, "$e_t$"), (en_n, "$e_n$")], None),
]
fig, axs = plt.subplots(2, 2, figsize=(9.6, 7.6))
for (title, basis, kind), ax in zip(panels, axs.flat):
    ax.set_aspect("equal")
    ax.axis("off")
    if kind == "sph":                       # 俯视略带倾斜：高度 z 画成向上的偏移，看得见相机
        prj = lambda p: np.array([p[0] - 0.25 * (p[2] - z0), p[1] + 0.35 * (p[2] - z0)])
    else:
        prj = lambda p: np.array([p[0], p[1]])
    q = np.array([prj(p) for p in E])
    ax.plot(q[:, 0], q[:, 1], color=C["ink"], lw=1.0)
    Pp = prj(P)
    if kind == "cyl":
        O2 = prj(np.array([0.0, 0.0, z0]))
        ax.plot([O2[0], Pp[0]], [O2[1], Pp[1]], color=G_COL, lw=0.8, ls="--")
        ax.plot(*O2, "o", color=G_COL, ms=4)
        ax.text(O2[0] + 0.006, O2[1] - 0.02, T("关节 1 轴", "joint-1 axis"), fontsize=8.5, color=G_COL)
    if kind == "sph":
        Cp = prj(cam)
        ax.plot([Cp[0], Pp[0]], [Cp[1], Pp[1]], color=G_COL, lw=0.8, ls="--")
        ax.add_patch(plt.Rectangle(Cp - np.array([0.012, 0.007]), 0.024, 0.014, color="#4a5560"))
        ax.text(Cp[0] + 0.015, Cp[1], T("相机", "camera"), fontsize=8.5, color=G_COL)
    kb, kv, ka = 0.05, 0.55, 0.35
    for i, (e, lab) in enumerate(basis):
        tip = prj(P + kb * e)
        arrow(ax, Pp, tip, AXIS[i], 1.0)
        off = (tip - Pp) / (np.linalg.norm(tip - Pp) + 1e-12) * 0.018
        if kind is None and lab == "$e_t$":
            off = np.array([0.012, 0.012])
        ax.text(*(tip + off + np.array([-0.006, -0.006])), lab, color=AXIS[i], fontsize=11)
    arrow(ax, Pp, prj(P + kv * v1), V_COL, 2.0)
    ax.text(*(prj(P + kv * v1) + np.array([-0.02, 0.008])), "$v$", color=V_COL, fontsize=12)
    arrow(ax, Pp, prj(P + ka * a1v), A_COL, 2.0)
    ax.text(*(prj(P + ka * a1v) + np.array([-0.02, -0.02])), "$a$", color=A_COL, fontsize=12)
    ax.plot(*Pp, "o", color=C["ink"], ms=4, zorder=6)
    ax.set_title(title, fontsize=10.5)
    if kind == "sph":
        ax.set_xlim(0.2, 0.6)
        ax.set_ylim(-0.06, 0.2)
    elif kind == "cyl":
        ax.set_xlim(-0.03, 0.6)
        ax.set_ylim(-0.08, 0.24)
    else:
        ax.set_xlim(0.22, 0.6)
        ax.set_ylim(-0.06, 0.2)
fig.text(0.5, 0.02, T("同一支箭头 v、a，在四组局部基上读出四组不同的分量（数值见算例 10.5.3）",
                      "The same arrows v and a give four different sets of components on four local bases (values in Example 10.5.3)"),
         ha="center", fontsize=9.5)
fig.tight_layout(rect=(0, 0.04, 1, 1))
figure(fig, "fig10_5_3")
plt.close(fig)
