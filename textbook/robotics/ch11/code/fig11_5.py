"""11.5 节的示意图。

图 11.5.1：(a) 四杆机构（机架 0.40、曲柄 0.15、连杆 0.35、摇杆 0.30 m），θ1 = 60° 时开式（实线）与交叉式（虚线）两种装配模式；
          (b) 构型空间在 (θ1, θ3) 正方形上的投影：满足格拉斯霍夫条件时是两条分开的闭曲线（两种装配模式），
          机架加长到 0.58 m 后只剩一条闭曲线，两种装配模式在极限位置（黑点）相接。
图 11.5.2：(a) Delta 的支链 1 在它的竖直平面内：肘点在以铰点为圆心、半径 La 的圆上，又在以 P′ 为圆心、半径 Lb 的圆上，
          两圆的两个交点就是逆运动学的两组解；(b) Stewart 平台 6-UPS 平移并绕 x 轴转 10° 时的六条腿长（数据同程序 11.5.1）。
图 11.5.3：(a) 车轮不侧滑：车体中心的速度只能沿车头方向；(b) 两种轮速过程，两轮最终转角相同，车停的位置不同。
"""
import math

import numpy as np

from _ch11 import DELTA, FB, FB_NG, agv_programs, fourbar
from _fig11 import C, bar, clean3d, ground, pin, plane
from bookout import T, figure, style

plt = style()


def e(t):
    return np.array([math.cos(t), math.sin(t)])


def arc(ax, c, r, a0, a1, color, lw=1.2):
    t = np.linspace(a0, a1, 40)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw)


# ---------------------------------------------------------------- 图 11.5.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.6), gridspec_kw=dict(width_ratios=[1.05, 1]))
l0, l1, l2, l3 = FB
t1 = math.radians(60)
A, D = np.array([0.0, 0.0]), np.array([l0, 0.0])
B = A + l1 * e(t1)
t3o, t3x = fourbar(*FB, t1, -1), fourbar(*FB, t1, 1)
Co, Cx = D + l3 * e(t3o), D + l3 * e(t3x)
plane(a1, (-0.12, 0.56), (-0.3, 0.42))
a1.plot([A[0], D[0]], [A[1], D[1]], color=C["muted"], lw=1.2, ls="--", zorder=1)
bar(a1, B, Cx, C["accent"], lw=3, alpha=0.35)
bar(a1, D, Cx, C["z"], lw=3, alpha=0.35)
bar(a1, A, B, C["z"], lw=5)
bar(a1, B, Co, C["accent"], lw=5)
bar(a1, D, Co, C["z"], lw=5)
for P in (A, D):
    ground(a1, P, w=0.06)
for P in (A, B, Co, D):
    pin(a1, P, r=0.011)
pin(a1, Cx, r=0.011, color=C["muted"])
# 角度：都从 x 轴量起，逆时针为正
arc(a1, A, 0.05, 0, t1, C["x"])
a1.text(0.055, 0.025, "$\\theta_1$", color=C["x"], fontsize=11)
a1.plot([B[0], B[0] + 0.09], [B[1], B[1]], color=C["muted"], lw=0.8)
t2o = math.atan2(*(Co - B)[::-1])
arc(a1, B, 0.06, 0, t2o, C["x"])
a1.text(B[0] + 0.065, B[1] + 0.012, "$\\theta_2$", color=C["x"], fontsize=11)
a1.plot([D[0], D[0] + 0.09], [0, 0], color=C["muted"], lw=0.8)
arc(a1, D, 0.05, 0, t3o, C["x"])
a1.text(D[0] + 0.045, 0.045, "$\\theta_3$", color=C["x"], fontsize=11)
a1.text(0.2, -0.035, "$l_0$", ha="center", fontsize=11)
a1.text(*(A + B) / 2 + np.array([-0.045, 0.0]), "$l_1$", fontsize=11, color=C["z"])
a1.text(*(B + Co) / 2 + np.array([-0.01, 0.025]), "$l_2$", fontsize=11, color=C["accent"])
a1.text(*(D + Co) / 2 + np.array([0.015, 0.0]), "$l_3$", fontsize=11, color=C["z"])
for P, s, d in ((A, "A", (-0.035, 0.012)), (B, "B", (-0.035, 0.01)), (Co, "C", (0.012, 0.012)), (D, "D", (-0.045, 0.015))):
    a1.text(P[0] + d[0], P[1] + d[1], s, fontsize=10, weight="bold")
a1.text(Cx[0] + 0.022, Cx[1] - 0.012, "C′", fontsize=10, color=C["muted"], weight="bold")
a1.text(-0.11, -0.25, T("实线：开式（C 在上）\n淡色：交叉式（C′，连杆与机架交叉）",
                        "solid: open mode (C above)\nfaint: crossed mode (C′, coupler crosses the frame)"), fontsize=8.5, color=C["dark"])
a1.set_title(T("(a) 四杆机构，θ₁ = 60° 时的两种装配模式", "(a) Four-bar: two assembly modes at θ₁ = 60°"), fontsize=10)


def branch(L, mode, n=3601):
    th = np.linspace(-math.pi, math.pi, n)
    out = [(t, fourbar(*L, t, mode)) for t in th]
    return np.array([(np.degrees(a), np.degrees(b)) if b is not None else (np.nan, np.nan) for a, b in out])


def plot_wrapped(ax, xy, **kw):
    x, y = xy[:, 0], np.mod(xy[:, 1], 360)              # θ3 画在 [0°, 360°) 内，曲线不被边界切断
    br = np.where(np.abs(np.diff(y)) > 180)[0] + 1
    first = True
    for xs, ys in zip(np.split(x, br), np.split(y, br)):
        ax.plot(xs, ys, **(kw if first else {k: v for k, v in kw.items() if k != "label"}))
        first = False


plot_wrapped(a2, branch(FB, -1), color=C["z"], lw=2.2, label=T("开式（机架 0.40 m）", "open (frame 0.40 m)"))
plot_wrapped(a2, branch(FB, 1), color=C["accent"], lw=2.2, label=T("交叉式（机架 0.40 m）", "crossed (frame 0.40 m)"))
ng_up, ng_dn = branch(FB_NG, -1), branch(FB_NG, 1)
ok = ~np.isnan(ng_up[:, 0])
loop = np.vstack([ng_up[ok], ng_dn[ok][::-1], ng_up[ok][:1]])
plot_wrapped(a2, loop, color=C["dark"], lw=1.6, ls="--", label=T("机架 0.58 m：一条闭曲线", "frame 0.58 m: a single loop"))
for k in (0, -1):
    P = ng_up[ok][k]
    a2.plot(P[0], P[1] % 360, "o", color=C["ink"], ms=5, zorder=6)
    a2.text(P[0] + (12 if k == 0 else -12), P[1] % 360 - 4, T("极限位置", "limit position"), fontsize=8.5,
            ha="left" if k == 0 else "right", va="top", color=C["ink"], bbox=dict(facecolor="white", edgecolor="none", pad=1))
for t3, col in ((t3o, C["z"]), (t3x, C["accent"])):
    a2.plot(60, math.degrees(t3) % 360, "o", color=col, mec="white", ms=7, zorder=7)
a2.add_patch(plt.Rectangle((-180, 0), 360, 360, facecolor=C["fill"], edgecolor=C["muted"], lw=0.8, zorder=0))
a2.set_xlim(-180, 180)
a2.set_ylim(0, 360)
a2.set_xticks([-180, -90, 0, 90, 180])
a2.set_yticks([0, 90, 180, 270, 360])
a2.set_xlabel(T("曲柄角 θ₁ / (°)", "crank angle θ₁ / (°)"))
a2.set_ylabel(T("摇杆角 θ₃ / (°)", "rocker angle θ₃ / (°)"))
a2.legend(loc="lower center", fontsize=8, framealpha=0.95)
a2.set_title(T("(b) 构型空间：环面上的闭曲线（左右、上下边粘合）", "(b) C-space: closed curves on the torus (edges glued)"), fontsize=10)
fig.subplots_adjust(wspace=0.12, left=0.02, right=0.98, top=0.92, bottom=0.11)
figure(fig, "fig11_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 11.5.2
fig = plt.figure(figsize=(10.6, 4.8))
a1 = fig.add_subplot(1, 2, 1)
Rb, Rp, La, Lb = DELTA["Rb"], DELTA["Rp"], DELTA["La"], DELTA["Lb"]
p1 = np.array([0.1, -0.45])                        # 动平台中心 (x, z)，在支链 1 的竖直平面 y = 0 内
Pp = p1 + np.array([Rp, 0])                         # 球关节中心 P′ = p + Rp e1
O = np.array([Rb, 0.0])                             # 主动臂铰点


def cint(c0, r0, c1, r1):
    d = np.linalg.norm(c1 - c0)
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = math.sqrt(max(r0 * r0 - a * a, 0))
    u = (c1 - c0) / d
    m = c0 + a * u
    return [m + s * h * np.array([-u[1], u[0]]) for s in (1, -1)]


E1, E2 = cint(O, La, Pp, Lb)
Eo, Ei = (E1, E2) if E1[0] > E2[0] else (E2, E1)   # 朝外、朝内两个肘点
plane(a1, (-0.22, 0.62), (-0.62, 0.2))
a1.plot([-0.2, 0.25], [0, 0], color=C["dark"], lw=6, solid_capstyle="butt")
a1.text(-0.2, 0.035, T("静平台（基座）", "base"), fontsize=9, color=C["dark"])
a1.plot([0, 0], [0.12, -0.6], color=C["muted"], lw=0.8, ls=(0, (6, 3)))
a1.text(0.005, 0.13, "z", fontsize=10, color=C["muted"])
tt = np.linspace(0, 2 * math.pi, 200)
a1.plot(O[0] + La * np.cos(tt), O[1] + La * np.sin(tt), color=C["z"], lw=0.9, ls=":")
a1.plot(Pp[0] + Lb * np.cos(tt), Pp[1] + Lb * np.sin(tt), color=C["accent"], lw=0.9, ls=":")
bar(a1, O, Eo, C["z"], lw=5)
bar(a1, Eo, Pp, C["muted"], lw=2.5)
bar(a1, O, Ei, C["z"], lw=2.5, alpha=0.35)
bar(a1, Ei, Pp, C["muted"], lw=1.5, alpha=0.35)
bar(a1, p1 - np.array([Rp, 0]), Pp, C["accent"], lw=6)
pin(a1, O, r=0.012)
for P in (Eo, Pp):
    a1.plot(*P, "o", color=C["x"], ms=6, zorder=7)
a1.plot(*Ei, "o", color=C["x"], ms=5, alpha=0.4, zorder=7)
a1.plot(*p1, "+", color=C["ink"], ms=9, mew=1.5, zorder=8)
a1.plot([O[0], O[0] + 0.12], [0, 0], color=C["muted"], lw=0.8)
thE = math.atan2(-(Eo - O)[1], (Eo - O)[0])
arc(a1, O, 0.08, -thE - 0.0, 0.0, C["x"])
a1.text(O[0] + 0.09, -0.035, "$\\theta_1$", color=C["x"], fontsize=11)
a1.text(*(O + Eo) / 2 + np.array([0.0, 0.025]), "$L_a$", color=C["z"], fontsize=11)
a1.text(*(Eo + Pp) / 2 + np.array([0.02, 0.0]), "$L_b$", color=C["dark"], fontsize=11)
a1.text(Eo[0] + 0.02, Eo[1] + 0.02, T("肘点 E₁", "elbow E₁"), fontsize=9, color=C["x"])
a1.text(Ei[0] - 0.01, Ei[1] - 0.06, T("另一组解的肘点", "elbow of the\nother solution"), fontsize=8.5, color=C["muted"], ha="center", va="top")
a1.text(Pp[0] + 0.02, Pp[1] - 0.045, "P′", fontsize=10, color=C["x"])
a1.text(p1[0] - 0.09, p1[1] - 0.06, T("动平台中心 p", "platform centre p"), fontsize=9, color=C["accent"])
a1.text(-0.21, -0.6, T("点线：半径 La、Lb 的两个圆；交点即肘点", "dotted: circles of radii La and Lb; they meet at the elbow"),
        fontsize=8.5, color=C["dark"])
a1.set_title(T("(a) Delta 支链 1 所在的竖直平面（p 在此平面内）", "(a) The vertical plane of Delta leg 1 (p lies in it)"), fontsize=10)

ax = fig.add_subplot(1, 2, 2, projection="3d")
clean3d(ax, 0.5, elev=22, azim=-62, zoom=1.3)
ra, rb = 0.5, 0.3
aa = [ra * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-10, 10, 110, 130, 230, 250])]
bb = [rb * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-50, 50, 70, 170, 190, 290])]
ang = math.radians(10)
Rx = np.array([[1, 0, 0], [0, math.cos(ang), -math.sin(ang)], [0, math.sin(ang), math.cos(ang)]])
ps = np.array([0, 0, 0.6])
z0 = np.array([0, 0, -0.3])
A6 = np.array(aa) + z0
B6 = np.array([ps + Rx @ b for b in bb]) + z0
ax.plot(*np.vstack([A6, A6[:1]]).T, color=C["dark"], lw=2)
ax.plot(*np.vstack([B6, B6[:1]]).T, color=C["accent"], lw=2.5)
legs = np.linalg.norm(B6 - A6, axis=1)
for i in range(6):
    ax.plot(*np.array([A6[i], B6[i]]).T, color=C["z"], lw=2.5)
    ax.scatter(*A6[i], color=C["y"], s=14)
    ax.scatter(*B6[i], color=C["x"], s=14)
    m = A6[i] + 0.55 * (B6[i] - A6[i])
    off = 0.06 * np.array([math.cos(math.radians([-10, 10, 110, 130, 230, 250][i])), math.sin(math.radians([-10, 10, 110, 130, 230, 250][i])), 0])
    ax.text(*(m + off), f"{legs[i]:.3f}", fontsize=8, color=C["z"])
ax.quiver(*(ps + z0), 0.25, 0, 0, color=C["x"], lw=1.4, arrow_length_ratio=0.2)
ax.text(*(ps + z0 + np.array([0.27, 0, 0.0])), "x", color=C["x"], fontsize=9)
ax.text2D(0.02, 0.02, T("动平台中心升到 0.6 m 并绕 x 轴转 10°；数字为腿长 / m",
                        "platform centre at 0.6 m, turned 10° about x; numbers are leg lengths / m"), transform=ax.transAxes, fontsize=8.5)
ax.set_title(T("(b) Stewart 平台：位姿给定，腿长直接算出", "(b) Stewart platform: given the pose, leg lengths follow"), fontsize=10, pad=-4)
fig.subplots_adjust(wspace=0.02, left=0.02, right=0.98, top=0.92, bottom=0.03)
figure(fig, "fig11_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 11.5.3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.6), gridspec_kw=dict(width_ratios=[0.9, 1.1]))
plane(a1, (-0.3, 1.05), (-0.25, 0.95))
ph = math.radians(30)
c = np.array([0.4, 0.3])
u, n = e(ph), e(ph + math.pi / 2)
body = np.array([c + 0.16 * u + 0.11 * n, c - 0.16 * u + 0.11 * n, c - 0.16 * u - 0.11 * n, c + 0.16 * u - 0.11 * n, c + 0.16 * u + 0.11 * n])
a1.fill(*body.T, facecolor=C["fill"], edgecolor=C["dark"], lw=1.4)
for s in (1, -1):
    w0 = c + s * 0.13 * n
    a1.plot(*np.array([w0 - 0.05 * u, w0 + 0.05 * u]).T, color=C["ink"], lw=6, solid_capstyle="butt")
a1.annotate("", xy=c + 0.42 * u, xytext=c, arrowprops=dict(arrowstyle="-|>", color=C["y"], lw=2.2))
a1.text(*(c + 0.44 * u + np.array([0.0, 0.02])), T("允许：沿车头方向", "allowed: along the heading"), fontsize=9, color=C["y"])
a1.annotate("", xy=c + 0.3 * n, xytext=c, arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=2.0, ls="--"))
q = c + 0.2 * n
a1.plot([q[0] - 0.035, q[0] + 0.035], [q[1] - 0.035, q[1] + 0.035], color=C["x"], lw=2)
a1.plot([q[0] - 0.035, q[0] + 0.035], [q[1] + 0.035, q[1] - 0.035], color=C["x"], lw=2)
a1.text(*(c + 0.33 * n + np.array([-0.2, 0.02])), T("禁止：侧滑", "forbidden: side slip"), fontsize=9, color=C["x"])
a1.annotate("", xy=(0.95, 0), xytext=(-0.25, 0), arrowprops=dict(arrowstyle="-|>", color=C["muted"], lw=1))
a1.annotate("", xy=(-0.2, 0.9), xytext=(-0.2, -0.2), arrowprops=dict(arrowstyle="-|>", color=C["muted"], lw=1))
a1.text(0.96, -0.04, "x", fontsize=10, color=C["muted"])
a1.text(-0.18, 0.9, "y", fontsize=10, color=C["muted"])
a1.plot([c[0], c[0] + 0.3], [c[1], c[1]], color=C["muted"], lw=0.8, ls="--")
arc(a1, c, 0.22, 0, ph, C["z"])
a1.text(c[0] + 0.235, c[1] + 0.035, "φ", fontsize=11, color=C["z"])
a1.plot(*c, "o", color=C["ink"], ms=4)
a1.text(c[0] - 0.15, c[1] - 0.035, "(x, y)", fontsize=9.5)
a1.text(-0.28, -0.22, "$\\dot x\\,\\sin\\varphi - \\dot y\\,\\cos\\varphi = 0$", fontsize=12)
a1.set_title(T("(a) 车轮不侧滑：速度只能沿车头方向", "(a) No side slip: velocity along the heading only"), fontsize=10)

qa, qb = agv_programs()
for q, col, name in ((qa, C["z"], T("过程 A：两轮同时变速转动", "programme A: both wheels, varying speeds")),
                     (qb, C["accent"], T("过程 B：先只转右轮，再只转左轮", "programme B: right wheel only, then left only"))):
    a2.plot(q[:, 0], q[:, 1], color=col, lw=2, label=name)
    x, y, f = q[-1, :3]
    a2.annotate("", xy=(x + 0.12 * math.cos(f), y + 0.12 * math.sin(f)), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
    a2.plot(x, y, "o", color=col, ms=6)
a2.plot(0, 0, "s", color=C["ink"], ms=7)
a2.annotate("", xy=(0.14, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=2))
a2.text(0.03, -0.1, T("起点", "start"), fontsize=9)
a2.set_aspect("equal")
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.grid(color=C["light"], lw=0.6)
a2.legend(loc="upper right", fontsize=8, framealpha=0.95)
a2.text(0.02, 0.02, T("终点两轮转角相同、车头方向相同，位置相差 {:.2f} m".format(np.linalg.norm(qa[-1, :2] - qb[-1, :2])),
                      "same final wheel angles and heading; positions {:.2f} m apart".format(np.linalg.norm(qa[-1, :2] - qb[-1, :2]))),
        transform=a2.transAxes, fontsize=8.5, bbox=dict(facecolor="white", edgecolor="none", pad=1))
a2.set_xlim(-1.2, 1.3)
a2.set_ylim(-0.45, 1.95)
a2.set_title(T("(b) 两轮转角相同，位置不同（数据同程序 11.5.1）", "(b) Same wheel angles, different positions (Program 11.5.1)"), fontsize=10)
fig.subplots_adjust(wspace=0.12, left=0.02, right=0.98, top=0.92, bottom=0.11)
figure(fig, "fig11_5_3")
plt.close(fig)
