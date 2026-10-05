"""19.4 节的示意图。

图 19.4.1：阿克曼转向的几何：四个车轮的轴线交于后轴延长线上的瞬心；内、外侧前轮的转角 δi、δo，轴距 L、前轮距 w，
           转弯半径 R；自行车模型用前轴中点一个虚拟车轮（转角 δ）代替两个前轮。
图 19.4.2：转向梯形：(a) 结构（梯形臂、横拉杆、底角 λ，臂的延长线）；(b) 外侧轮转角与理想值之差随内侧轮转角的变化。
图 19.4.3：(a) 以最小转弯半径调头时车身扫过的圆环，与差速 AGV 原地转动比较；(b) 侧方停车的三段路径。
"""
import math

import numpy as np

from _fig19 import C, arrow, rect, rot, wheel
from bookout import T, figure, style

plt = style()
O = (0.0, 0.0, 0.0)
L, w = 1.2, 0.8
deg = math.pi / 180


def car(ax, pose, dl, dr, body=True, alpha=1.0, col=None):
    if body:
        rect(ax, pose, L / 2, 0, 0, 1.8, 1.0, col or C["body"], C["dark"], 0.8, 1, alpha)
    for y in (w / 2, -w / 2):
        wheel(ax, pose, 0, y, 0.0, r=0.16, width=0.09)
    wheel(ax, pose, L, w / 2, dl, r=0.16, width=0.09)
    wheel(ax, pose, L, -w / 2, dr, r=0.16, width=0.09)


# ---------------------------------------------------------------- 图 19.4.1
di = 30 * deg
R = L / math.tan(di) + w / 2
do = math.atan(L / (R + w / 2))
db = math.atan(L / R)
fig, ax = plt.subplots(figsize=(7.4, 7.6))
ax.set_aspect("equal")
ax.axis("off")
car(ax, O, di, do)
c = np.array([0, R])
ax.plot([0, 0], [-0.7, R + 0.25], color=C["red"], lw=0.9, ls="--")
for p, bt in (((L, w / 2), di), ((L, -w / 2), do)):
    ax.plot([p[0], c[0]], [p[1], c[1]], color=C["red"], lw=0.9, ls="--")
ax.plot([L, c[0]], [0, c[1]], color=C["purple"], lw=0.9, ls=":")
wheel(ax, O, L, 0, db, r=0.16, width=0.06, fc="#b9a6d6")
ax.plot(*c, "o", ms=8, mfc="white", mec=C["accent"], mew=2, zorder=8)
ax.text(c[0] + 0.07, c[1] + 0.05, T("瞬心", "ICR"), color=C["accent"], fontsize=12)
for p, bt, nm, off in (((L, w / 2), di, r"$\delta_i$", (0.2, 0.12)), ((L, -w / 2), do, r"$\delta_o$", (0.22, -0.2))):
    ax.plot([p[0], p[0] + 0.45], [p[1], p[1]], color=C["muted"], lw=0.7, ls=":")
    t = np.linspace(0, bt, 20)
    ax.plot(p[0] + 0.32 * np.cos(t), p[1] + 0.32 * np.sin(t), color=C["accent"], lw=1.0)
    ax.text(p[0] + off[0] + 0.15, p[1] + off[1] - 0.04, nm, color=C["accent"], fontsize=13)
t = np.linspace(0, db, 20)
ax.text(L + 0.36, 0.02, r"$\delta$", color=C["purple"], fontsize=13)
ax.annotate("", xy=(0, -0.62), xytext=(L, -0.62), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.9))
ax.text(L / 2 - 0.04, -0.75, "$L$", fontsize=13)
ax.annotate("", xy=(L + 0.62, w / 2), xytext=(L + 0.62, -w / 2), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.9))
ax.text(L + 0.68, -0.05, "$w$", fontsize=13)
ax.annotate("", xy=(-0.18, R), xytext=(-0.18, 0), arrowprops=dict(arrowstyle="<->", color=C["accent"], lw=1.0))
ax.text(-0.36, R / 2, "$R$", color=C["accent"], fontsize=13)
ax.plot(0, 0, "o", color=C["ink"], ms=3)
ax.text(0.05, -0.15, T("后轴中点", "rear-axle centre"), fontsize=9)
ax.text(-0.75, -1.0, T("红虚线：四个车轮的轴线，交于一点；紫：自行车模型的虚拟前轮", "red dashed: the four wheel axles, meeting at one point; purple: the bicycle model's virtual front wheel"),
        fontsize=9, color=C["muted"])
ax.set_xlim(-0.8, 2.3)
ax.set_ylim(-1.05, R + 0.35)
figure(fig, "fig19_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.4.2
a_k = 0.15
lam0 = math.atan((w / 2) / L)


def outer_angle(din, lam):
    Kl, Kr = np.array([0.0, w / 2]), np.array([0.0, -w / 2])
    ul = np.array([-math.cos(lam), -math.sin(lam)])
    ur = np.array([-math.cos(lam), math.sin(lam)])
    rod = w - 2 * a_k * math.sin(lam)
    Al = Kl + a_k * rot(din) @ ul
    f = lambda t: np.linalg.norm(Al - (Kr + a_k * rot(t) @ ur)) - rod
    lo, hi = -0.05, din + 0.05
    for _ in range(50):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


ideal = lambda d: math.atan(1 / (1 / math.tan(d) + w / L))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.6), gridspec_kw=dict(width_ratios=[1.1, 1]))
a1.set_aspect("equal")
a1.axis("off")
# 前轴、两主销、梯形臂、横拉杆（零位），以及转向 25° 时的位置（淡色）
for dl, alp in ((0.0, 1.0), (25 * deg, 0.35)):
    dr = outer_angle(dl, lam0) if dl else 0.0
    Kl, Kr = np.array([L, w / 2]), np.array([L, -w / 2])
    Al = Kl + a_k * rot(dl) @ np.array([-math.cos(lam0), -math.sin(lam0)])
    Ar = Kr + a_k * rot(dr) @ np.array([-math.cos(lam0), math.sin(lam0)])
    a1.plot([Kl[0], Kr[0]], [Kl[1], Kr[1]], color=C["dark"], lw=3, alpha=alp)
    a1.plot([Kl[0], Al[0]], [Kl[1], Al[1]], color=C["blue"], lw=3, alpha=alp)
    a1.plot([Kr[0], Ar[0]], [Kr[1], Ar[1]], color=C["blue"], lw=3, alpha=alp)
    a1.plot([Al[0], Ar[0]], [Al[1], Ar[1]], color=C["orange"], lw=2.5, alpha=alp)
    for K, d in ((Kl, dl), (Kr, dr)):
        wheel(a1, O, K[0], K[1] + (0.07 if K[1] > 0 else -0.07), d, r=0.16, width=0.07)
        a1.plot(*K, "o", color=C["ink"], ms=4, alpha=alp)
for y in (w / 2, -w / 2):
    wheel(a1, O, 0, y + (0.07 if y > 0 else -0.07), 0, r=0.16, width=0.07)
a1.plot([0, 0], [-w / 2, w / 2], color=C["dark"], lw=1.5)
for s in (1, -1):
    a1.plot([L, 0], [s * w / 2, 0], color=C["muted"], lw=0.8, ls="--")
a1.plot(0, 0, "o", color=C["accent"], ms=5)
a1.text(-0.2, -0.13, T("后轴中点", "rear-axle centre"), fontsize=9, color=C["accent"])
t = np.linspace(math.pi, math.pi + lam0, 20)
a1.plot(L + 0.35 * np.cos(t), w / 2 + 0.35 * np.sin(t), color=C["accent"], lw=1.0)
a1.plot([L, L - 0.45], [w / 2, w / 2], color=C["muted"], lw=0.6, ls=":")
a1.text(L - 0.56, w / 2 - 0.05, "λ", color=C["accent"], fontsize=12)
a1.text(L - 0.36, 0.0, T("横拉杆", "tie rod"), color=C["orange"], fontsize=9)
a1.text(L - 0.45, w / 2 - 0.2, T("梯形臂", "steering arm"), color=C["blue"], fontsize=9)
a1.text(0.1, -0.68, T("淡色：内侧轮转 25° 时", "faint: inner wheel at 25°"), fontsize=9, color=C["muted"])
a1.set_xlim(-0.3, 1.6)
a1.set_ylim(-0.72, 0.68)
a1.set_title(T("(a) 转向梯形（俯视）", "(a) steering trapezoid (top view)"), fontsize=10.5)
dd = np.linspace(0.5, 40, 60) * deg
lamb = 22.5 * deg
for lam, col, nm in ((lam0, C["blue"], T("λ = 18.4°（延长线交于后轴中点）", "λ = 18.4° (lines meet at rear-axle centre)")),
                     (lamb, C["green"], T("λ = 22.5°（最大误差最小）", "λ = 22.5° (smallest worst error)")),
                     (0.0, C["red"], T("λ = 0（平行转向）", "λ = 0 (parallel steering)"))):
    e = [(outer_angle(d, lam) - ideal(d)) / deg for d in dd]
    a2.plot(dd / deg, e, color=col, lw=1.6, label=nm)
a2.axhline(0, color=C["muted"], lw=0.7)
a2.set_xlabel(T("内侧轮转角 δi / (°)", "inner wheel angle δi / (°)"))
a2.set_ylabel(T("外侧轮转角误差 / (°)", "outer-angle error / (°)"))
a2.set_ylim(-1.5, 12.5)
a2.legend(fontsize=8.5, loc="upper left", frameon=False)
a2.set_title(T("(b) 外侧轮转角减去阿克曼理想值", "(b) outer angle minus the Ackermann ideal"), fontsize=10.5)
fig.subplots_adjust(wspace=0.2)
figure(fig, "fig19_4_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.4.3
R_min = L / math.tan(40 * deg) + w / 2
R_out = math.hypot(R_min + 0.5, L + 0.3)
R_in = R_min - 0.5
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 5.0))
a1.set_aspect("equal")
tt = np.linspace(0, 2 * math.pi, 200)
a1.fill(np.r_[R_out * np.cos(tt), R_in * np.cos(tt[::-1])], np.r_[R_out * np.sin(tt), R_in * np.sin(tt[::-1])],
        color=C["blue"], alpha=0.10)
a1.plot(R_out * np.cos(tt), R_out * np.sin(tt), color=C["blue"], lw=1.0)
a1.plot(R_in * np.cos(tt), R_in * np.sin(tt), color=C["blue"], lw=1.0, ls="--")
pose = (0.0, -R_min, 0.0)
dlm = 40 * deg
car(a1, pose, dlm, math.atan(L / (R_min + w / 2)))
a1.plot(0, 0, "o", ms=6, mfc="white", mec=C["accent"], mew=2)
a1.annotate("", xy=(R_out * math.cos(1.0), R_out * math.sin(1.0)), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=C["blue"]))
a1.text(1.25, 1.75, T("车身外侧前角", "outer front corner") + f"\n{R_out:.2f} m", fontsize=9, color=C["blue"])
a1.annotate("", xy=(R_in * math.cos(2.4), R_in * math.sin(2.4)), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=C["blue"]))
a1.text(-1.6, 0.25, T("车身内侧", "inner side") + f"\n{R_in:.2f} m", fontsize=9, color=C["blue"])
ud = math.hypot(0.32, 0.22) / 2
a1.plot(-2.2 + ud * np.cos(tt), 2.2 + ud * np.sin(tt), color=C["red"], lw=1.2)
a1.text(-2.95, 2.55, T("差速 AGV 原地转", "differential AGV spin"), fontsize=9, color=C["red"])
a1.set_xlim(-3.2, 3.2)
a1.set_ylim(-3.1, 3.2)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("(a) 以最小转弯半径转一圈扫过的圆环", "(a) the ring swept at the minimum turning radius"), fontsize=10.5)
# (b) 侧方停车
a2.set_aspect("equal")
R0 = R_min
alpha = math.acos(1 - 0.6 / (2 * R0))
dmb = math.atan(L / R0)


def drive(q, v, delta, dist, n=300):
    q = np.array(q, float)
    out = [q.copy()]
    k = math.tan(delta) / L
    for _ in range(n):
        ds = v * dist / n
        dphi = k * ds
        if abs(dphi) < 1e-12:
            q[0] += ds * math.cos(q[2]); q[1] += ds * math.sin(q[2])
        else:
            q[0] += (math.sin(q[2] + dphi) - math.sin(q[2])) / k
            q[1] -= (math.cos(q[2] + dphi) - math.cos(q[2])) / k
        q[2] += dphi
        out.append(q.copy())
    return np.array(out)


p1 = drive([0, 0, 0], -1, -dmb, R0 * alpha)
p2 = drive(p1[-1], -1, dmb, R0 * alpha)
p3 = drive(p2[-1], 1, 0.0, 2 * R0 * math.sin(alpha))
for P_, col, nm in ((p1, C["blue"], T("① 倒车，向右打满", "① reverse, full right")), (p2, C["purple"], T("② 倒车，向左打满", "② reverse, full left")),
                    (p3, C["green"], T("③ 前进，回正", "③ forward, straight"))):
    a2.plot(P_[:, 0], P_[:, 1], color=col, lw=1.8, label=nm)
car(a2, (0, 0, 0), 0, 0, alpha=0.35)
car(a2, tuple(p1[-1]), 0, 0, alpha=0.35)
car(a2, tuple(p3[-1]), 0, 0, alpha=0.8, col="#f3e2b3")
a2.plot([-3.5, 3.0], [-1.45, -1.45], color=C["dark"], lw=2)
a2.text(-3.4, -1.75, T("路沿", "kerb"), fontsize=9)
a2.set_xlim(-3.6, 3.2)
a2.set_ylim(-1.9, 1.2)
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.legend(fontsize=8.5, loc="upper right", frameon=False)
a2.set_title(T("(b) 侧方停车：向右平移 0.6 m（后轴中点的路径）", "(b) parallel parking: 0.6 m to the right (rear-axle centre)"), fontsize=10.5)
fig.subplots_adjust(wspace=0.22)
figure(fig, "fig19_4_3")
plt.close(fig)
