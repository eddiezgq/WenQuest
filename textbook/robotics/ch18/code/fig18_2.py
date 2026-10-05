"""18.2 节的示意图。

图 18.2.1：平面五杆（肘部朝外）的奇异。(a) 平面上的奇异曲线：逆运动学奇异（某条支链伸直或折叠，以电机为圆心、半径
           0.5 m 和 0.1 m 的圆）与正运动学奇异（两根从动杆共线，det A = 0）；画出 y* 处的机构和两个相切的圆；
           (b) 末端沿 y 轴向下运动、受 20 N 向下力时，电机力矩的最大值（对数坐标），以及另一种装配模式的位置。
图 18.2.2：Delta 的一条支链。(a) 约束力偶 n = t × u 与驱动力（沿杆、过肘点）；(b) 三根主动臂转角相同、平台在中心轴上时，
           det N（约束）、det A（正运动学）与 det B（逆运动学，放大 100 倍）随转角的变化。
图 18.2.3：Stewart 平台。(a) 绕竖直轴转 ψ 时 det A 的变化（三个高度）；(b) 托住 500 N 时最大腿力随 ψ 的变化，
           阴影为腿长超出 0.55～0.85 m 行程的范围。
"""
import math

import numpy as np

from _ch18 import (DELTA, FIVE, ST_LMAX, ST_LMIN, delbow, delta_AB, delta_couples, delta_fk, delta_u, ek, elbow, five_AB,
                   five_elbows, five_fk, five_ik, five_motors, pose, rot, st_ik, st_W, tk)
from _fig18 import (BLUE2, C, GOLD, GREY, PALE, PALEGOLD, arrow3d, axes3d, draw_five, equal3d, joint, label3d, plane,
                    polygon3d)
from bookout import T, figure, style

plt = style()
plt.rcParams["axes.unicode_minus"] = True
c, l1, l2 = FIVE["c"], FIVE["l1"], FIVE["l2"]
y_star = math.sqrt(l1 ** 2 - c ** 2)

# ---------------------------------------------------------------- 图 18.2.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.9), gridspec_kw={"width_ratios": [1.05, 1.0]})
plane(a1, (-0.62, 0.62), (-0.02, 0.62))
h = 0.003
gx = np.arange(-0.6, 0.6 + h / 2, h)
gy = np.arange(-0.03, 0.63 + h / 2, h)
D = np.full((len(gy), len(gx)), np.nan)
for i, y in enumerate(gy):
    for j, x in enumerate(gx):
        th = five_ik(np.array([x, y]))
        if th is None:
            continue
        A, _ = five_AB(np.array([x, y]), th)
        D[i, j] = np.linalg.det(A)
X, Y = np.meshgrid(gx, gy)
a1.contourf(X, Y, np.where(np.isnan(D), np.nan, np.sign(D)), levels=[-2, 0, 2], colors=[PALEGOLD, PALE], alpha=0.8)
a1.contour(X, Y, np.nan_to_num(D, nan=1.0), levels=[0], colors=[C["x"]], linewidths=1.8)
t = np.linspace(0, 2 * math.pi, 300)
for A in five_motors():
    for r in (l2 - l1, l1 + l2):
        a1.plot(A[0] + r * np.cos(t), A[1] + r * np.sin(t), color=C["z"], lw=1.2, ls="--")
Ps = np.array([0.0, y_star])
ths = five_ik(Ps)
draw_five(a1, ths, Ps, C["accent"], lw=4)
for B in five_elbows(ths):
    a1.plot(B[0] + l2 * np.cos(t), B[1] + l2 * np.sin(t), color=C["muted"], lw=0.8, ls=":")
a1.plot(*Ps, "o", color=C["x"], ms=6, zorder=9)
a1.text(0.02, y_star + 0.03, r"$y^* = 0.132$ m", fontsize=9.5, color=C["x"])
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
a1.legend(handles=[Line2D([], [], color=C["x"], lw=1.8, label=T("正运动学奇异（det A = 0）", "direct singularity (det A = 0)")),
                   Line2D([], [], color=C["z"], lw=1.2, ls="--", label=T("逆运动学奇异（det B = 0）", "inverse singularity (det B = 0)")),
                   Patch(facecolor=PALE, edgecolor=C["muted"], lw=0.5, label=T("det A > 0：末端在上方的装配模式", "det A > 0: end point above")),
                   Line2D([], [], color=C["muted"], lw=0.8, ls=":", label=T("以两个肘点为圆心、半径 0.3 m 的圆，在 P 处相切", "circles of 0.3 m about the elbows, touching at P"))],
          loc="upper center", bbox_to_anchor=(0.5, 0.0), frameon=False, fontsize=8.5)
a1.text(-0.6, 0.6, T("(a) 肘部朝外时的奇异曲线", "(a) singular curves, elbows out"), fontsize=10)

ys = np.linspace(0.47, y_star + 0.0015, 400)
tau, other = [], []
for y in ys:
    P = np.array([0, y])
    th = five_ik(P)
    A, B = five_AB(P, th)
    J = np.linalg.solve(A, B)
    tau.append(np.abs(J.T @ np.array([0, -20.0])).max())
    other.append(five_fk(th, -1)[1])
a2.semilogy(ys, tau, color=C["accent"], lw=2)
a2.axvline(y_star, color=C["x"], lw=1.2, ls="--")
a2.text(y_star + 0.006, 120, r"$y^*$", color=C["x"], fontsize=11)
a2.set_xlabel(T("末端的高度 y / m", "height of the end point y / m"))
a2.set_ylabel(T("最大电机力矩 / N·m", "largest motor torque / N·m"), color=C["accent"])
a2.set_xlim(0.1, 0.48)
a2.grid(alpha=0.3)
ax2 = a2.twinx()
ax2.plot(ys, ys, color=C["muted"], lw=1, ls=":")
ax2.plot(ys, other, color=C["z"], lw=1.6)
ax2.set_ylabel(T("末端高度 / m", "end-point height / m"), color=C["z"])
ax2.tick_params(axis="y", colors=C["z"])
ax2.text(0.33, 0.37, T("本装配模式", "this mode"), color=C["muted"], fontsize=9)
ax2.text(0.33, 0.035, T("另一种装配模式", "the other mode"), color=C["z"], fontsize=9)
a2.set_title(T("(b) 沿 y 轴接近正运动学奇异（末端受 20 N 向下的力）", "(b) towards the direct singularity along y (20 N downward)"), fontsize=10, loc="left")
figure(fig, "fig18_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 18.2.2
fig = plt.figure(figsize=(11.0, 5.2))
fig, ax = axes3d(plt, fig=fig, pos=121, elev=14, azim=-68)
from _ch18 import delta_ik
from _fig18 import draw_delta
p1 = np.array([0.05, -0.08, -0.47])
th1 = delta_ik(p1)
k = 0
e, tt = ek(k), tk(k)
H, E = DELTA["Rb"] * e, elbow(k, th1[k])
Pp = p1 + DELTA["Rp"] * e
u = delta_u(p1, th1)[k]
n = np.cross(tt, u)
n /= np.linalg.norm(n)
w = 0.06
# 整台 Delta 画淡一些，支链 1 加粗
draw_delta(ax, th1, p1, color=BLUE2, lw=1.4, rods=GREY)
ax.plot(*np.vstack([H - 0.1 * tt, H + 0.1 * tt]).T, color=C["muted"], lw=1.0, ls="-.")
ax.plot(*np.vstack([H, E]).T, color=C["z"], lw=3.5)
for s_ in (1, -1):
    ax.plot(*np.vstack([E + s_ * w / 2 * tt, Pp + s_ * w / 2 * tt]).T, color=C["ink"], lw=1.6)
ax.plot(*np.vstack([E - w / 2 * tt, E + w / 2 * tt]).T, color=C["z"], lw=2.5)
ax.plot(*np.vstack([Pp - w / 2 * tt, Pp + w / 2 * tt]).T, color=C["accent"], lw=3)
ax.plot(*np.vstack([E - 0.1 * u, Pp + 0.14 * u]).T, color=C["x"], lw=1.0, ls="--")
arrow3d(ax, Pp + 0.02 * u, 0.13 * u, C["x"], lw=2.4)
m0 = E + 0.55 * (Pp - E)
arrow3d(ax, m0, 0.16 * n, GOLD, lw=2.4)
arrow3d(ax, m0 + 0.02 * n, 0.14 * n, GOLD, lw=2.4, ratio=0.25)
label3d(ax, Pp + 0.16 * u + np.array([0.0, 0, -0.02]), T("驱动力：沿杆的方向 $u_1$", "actuation force along $u_1$"), C["x"], fs=10)
label3d(ax, m0 + 0.17 * n + np.array([-0.06, 0, 0.04]), T("约束力偶 $n_1 = t_1 \\times u_1$", "constraint couple $n_1 = t_1 \\times u_1$"), GOLD, fs=10)
label3d(ax, H + np.array([0.0, 0.0, 0.05]), T("铰点 $H_1$", "hinge $H_1$"), C["ink"], fs=10)
label3d(ax, E + np.array([0.03, 0, 0.0]), T("肘点 $E_1$", "elbow $E_1$"), C["ink"], fs=10)
pts = np.array([H, E, Pp, m0 + 0.18 * n, Pp + 0.2 * u, [-0.2, -0.2, 0], [0.25, 0.2, 0.0]])
equal3d(ax, pts, pad=0.0, zoom=1.25)
ax.text2D(0.0, 1.0, T("(a) Delta 支链 1 的约束力偶与驱动力", "(a) constraint couple and actuation force of leg 1"), transform=ax.transAxes, fontsize=10)

a2 = fig.add_subplot(122)
thg = np.radians(np.linspace(-40, 140, 361))
dN, dA, dB = [], [], []
for q in thg:
    th = np.full(3, q)
    p = delta_fk(th)
    A, B = delta_AB(p, th)
    dN.append(np.linalg.det(delta_couples(p, th)))
    dA.append(np.linalg.det(A))
    dB.append(np.linalg.det(B) * 100)
a2.plot(np.degrees(thg), dN, color=GOLD, lw=2, label=T("det N（约束）", "det N (constraint)"))
a2.plot(np.degrees(thg), dA, color=C["x"], lw=2, label=T("det A（正运动学）", "det A (direct)"))
a2.plot(np.degrees(thg), dB, color=C["z"], lw=2, label=T("100 det B（逆运动学）", "100 det B (inverse)"))
a2.axhline(0, color=C["muted"], lw=0.8)
a2.axvspan(90, 140, color=GREY, alpha=0.4, lw=0)
a2.text(93, 0.75, T("超出限位", "beyond the limit"), fontsize=9, color=C["muted"])
a2.axvline(120, color=GOLD, lw=1, ls="--")
a2.text(92, -0.62, T("120°：三根杆\n都竖直", "120°: all rods\nvertical"), fontsize=8.5, color=GOLD)
a2.set_xlabel(T("三根主动臂的转角 θ / °", "angle of the three upper arms θ / °"))
a2.set_xlim(-40, 140)
a2.grid(alpha=0.3)
a2.legend(fontsize=8.5, loc="lower left", frameon=False)
a2.set_title(T("(b) 平台在中心轴上时三个行列式", "(b) the three determinants on the central axis"), fontsize=10, loc="left")
figure(fig, "fig18_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 18.2.3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.2))
ps = np.radians(np.linspace(-180, 180, 721))
for hgt, col in ((0.5, C["y"]), (0.6, C["z"]), (0.7, C["accent"])):
    a1.plot(np.degrees(ps), [np.linalg.det(st_W(pose(rot([0, 0, 1], q), [0, 0, hgt]))) for q in ps], color=col, lw=1.8,
            label=T(f"高度 {hgt} m", f"height {hgt} m"))
a1.axhline(0, color=C["muted"], lw=0.8)
for v in (-90, 90):
    a1.axvline(v, color=C["x"], lw=1, ls="--")
a1.set_xlabel(T("平台绕竖直轴的转角 ψ / °", "platform rotation about the vertical ψ / °"))
a1.set_ylabel("det A")
a1.set_xticks([-180, -90, 0, 90, 180])
a1.grid(alpha=0.3)
a1.legend(fontsize=8.5, frameon=False, loc="upper right")
a1.set_title(T("(a) det A 在 ψ = ±90° 处为零", "(a) det A vanishes at ψ = ±90°"), fontsize=10, loc="left")
ps2 = np.radians(np.linspace(0, 89.5, 400))
fm, bad = [], []
for q in ps2:
    Tq = pose(rot([0, 0, 1], q), [0, 0, 0.6])
    fm.append(np.abs(np.linalg.solve(st_W(Tq), np.r_[0, 0, 0, 0, 0, 500.0])).max())
    L = st_ik(Tq)
    bad.append(L.max() > ST_LMAX or L.min() < ST_LMIN)
bad = np.array(bad)
a2.semilogy(np.degrees(ps2), fm, color=C["z"], lw=2)
if bad.any():
    a2.axvspan(np.degrees(ps2[bad.argmax()]), 90, color=GREY, alpha=0.45, lw=0)
    a2.text(np.degrees(ps2[bad.argmax()]) + 1, 3000, T("腿长超出\n行程", "legs out\nof stroke"), fontsize=9, color=C["muted"])
a2.set_xlabel(T("ψ / °", "ψ / °"))
a2.set_ylabel(T("最大腿力 / N（托住 500 N）", "largest leg force / N (carrying 500 N)"))
a2.set_xlim(0, 90)
a2.grid(alpha=0.3, which="both")
a2.set_title(T("(b) 接近奇异时腿力急剧增大", "(b) leg forces soar near the singularity"), fontsize=10, loc="left")
figure(fig, "fig18_2_3")
plt.close(fig)
