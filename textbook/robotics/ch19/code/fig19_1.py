"""19.1 节的示意图。

图 19.1.1：四种车轮（俯视）：固定标准轮、可转向标准轮、脚轮、瑞典轮；滚动方向 e、轮轴方向 n、脚轮的偏距 d、瑞典轮的辊子轴线。
图 19.1.2：四种车轮布置的轮轴线与瞬心：差速 AGV、购物车、按阿克曼条件转向的四轮车、两前轮平行转向的四轮车。
"""
import math

import numpy as np

from _fig19 import C, arrow, label, rect, rot, wheel
from _mob import diff_cart
from bookout import T, figure, style

plt = style()
P = diff_cart()

# ---------------------------------------------------------------- 图 19.1.1
fig, axs = plt.subplots(1, 4, figsize=(11.2, 3.4))
O = (0.0, 0.0, 0.0)
for ax in axs:
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-0.16, 0.16)
    ax.set_ylim(-0.15, 0.15)


def frame_small(ax, o=(-0.135, -0.125)):
    arrow(ax, o, (o[0] + 0.05, o[1]), C["x"], 1.0, 8)
    arrow(ax, o, (o[0], o[1] + 0.05), C["y"], 1.0, 8)
    ax.text(o[0] + 0.052, o[1] - 0.006, "$x_b$", color=C["x"], fontsize=9)
    ax.text(o[0] - 0.012, o[1] + 0.054, "$y_b$", color=C["y"], fontsize=9)


def en_arrows(ax, c, beta, slip=True):
    e = np.array([math.cos(beta), math.sin(beta)])
    n = np.array([-math.sin(beta), math.cos(beta)])
    arrow(ax, c, c + 0.095 * e, C["green"], 1.8)
    ax.text(*(c + 0.1 * e + np.array([0.004, -0.004])), "$e$", color=C["green"], fontsize=12)
    if slip:
        ax.plot(*np.array([c - 0.09 * n, c + 0.09 * n]).T, color=C["red"], lw=1.0, ls="--")
        ax.text(*(c + 0.095 * n + np.array([0.004, 0.0])), "$n$", color=C["red"], fontsize=12)
        q = c + 0.06 * n
        ax.plot([q[0] - 0.008, q[0] + 0.008], [q[1] - 0.008, q[1] + 0.008], color=C["red"], lw=1.5)
        ax.plot([q[0] - 0.008, q[0] + 0.008], [q[1] + 0.008, q[1] - 0.008], color=C["red"], lw=1.5)


# (a) 固定标准轮
ax = axs[0]
c = np.array([0.0, 0.0])
wheel(ax, O, 0, 0, 0.0, r=0.05, width=0.026)
en_arrows(ax, c, 0.0)
ax.text(-0.15, 0.13, T("(a) 固定标准轮", "(a) fixed standard wheel"), fontsize=10)
ax.text(-0.02, -0.135, T("β 固定", "β fixed"), fontsize=9, color=C["muted"])
frame_small(ax)
# (b) 可转向标准轮
ax = axs[1]
bt = math.radians(35)
wheel(ax, O, 0, 0, bt, r=0.05, width=0.026)
ax.plot([0, 0.07], [0, 0], color=C["muted"], lw=0.8, ls=":")
t = np.linspace(0, bt, 30)
ax.plot(0.045 * np.cos(t), 0.045 * np.sin(t), color=C["accent"], lw=1.0)
ax.text(0.05, 0.012, "β", color=C["accent"], fontsize=11)
en_arrows(ax, c, bt)
ax.plot([0], [0], "o", color=C["accent"], ms=5, zorder=6)
ax.text(-0.15, 0.13, T("(b) 可转向标准轮", "(b) steerable standard wheel"), fontsize=10)
ax.text(-0.02, -0.135, T("β 由电机控制", "β set by a motor"), fontsize=9, color=C["muted"])
frame_small(ax)
# (c) 脚轮：转向轴 A、偏距 d、接地点 C
ax = axs[2]
bt = math.radians(25)
A = np.array([0.03, 0.02])
e = np.array([math.cos(bt), math.sin(bt)])
Cc = A - 0.06 * e
wheel(ax, O, *Cc, bt, r=0.05, width=0.026)
ax.plot(*np.array([A, Cc]).T, color=C["ink"], lw=2.0, zorder=5)
ax.plot(*A, "o", color=C["accent"], ms=6, zorder=6)
ax.text(A[0] + 0.006, A[1] + 0.01, "A", fontsize=11, color=C["accent"])
ax.text(Cc[0] - 0.028, Cc[1] - 0.03, "C", fontsize=11)
mid = (A + Cc) / 2
ax.text(mid[0] - 0.004, mid[1] - 0.03, "$d$", fontsize=12)
en_arrows(ax, Cc, bt, slip=True)
ax.text(-0.15, 0.13, T("(c) 脚轮", "(c) castor wheel"), fontsize=10)
ax.text(-0.02, -0.135, T("β 自由转动", "β turns freely"), fontsize=9, color=C["muted"])
frame_small(ax)
# (d) 瑞典轮：辊子轴线与轮平面成 γ
ax = axs[3]
g = math.radians(45)
wheel(ax, O, 0, 0, 0.0, r=0.05, width=0.03, rollers=5, gamma=-g)
a = np.array([math.cos(-g), math.sin(-g)])
ax.plot(*np.array([-0.09 * a, 0.09 * a]).T, color=C["purple"], lw=1.0, ls="--")
ax.text(*(0.09 * a + np.array([0.004, -0.012])), T("辊子轴线 $a$", "roller axis $a$"), color=C["purple"], fontsize=9)
s = np.array([-math.sin(-g), math.cos(-g)])
arrow(ax, (0, 0), 0.09 * s, C["blue"], 1.5)
ax.text(*(0.095 * s + np.array([-0.04, 0.008])), T("辊子自由滚动", "free roll of roller"), color=C["blue"], fontsize=9)
arrow(ax, (0, 0), (0.095, 0), C["green"], 1.8)
ax.text(0.098, -0.004, "$e$", color=C["green"], fontsize=12)
t = np.linspace(-g, 0, 30)
ax.plot(0.05 * np.cos(t), 0.05 * np.sin(t), color=C["accent"], lw=1.0)
ax.text(0.052, -0.03, "γ", color=C["accent"], fontsize=11)
ax.text(-0.15, 0.13, T("(d) 瑞典轮（麦克纳姆轮）", "(d) Swedish (mecanum) wheel"), fontsize=10)
ax.text(-0.02, -0.135, T("无侧向约束", "no sideways constraint"), fontsize=9, color=C["muted"])
frame_small(ax)
fig.text(0.13, 0.02, T("绿：滚动方向 e（轮心速度 rθ̇ 沿此方向）；红虚线：轮轴方向 n（标准轮在此方向上不能滑动）",
                       "green: rolling direction e (the hub moves at rθ̇ along it); red dashed: axle direction n (a standard wheel cannot slide along it)"),
         fontsize=9.5, color=C["ink"])
fig.subplots_adjust(wspace=0.05, bottom=0.1)
figure(fig, "fig19_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.1.2
fig, axs = plt.subplots(2, 2, figsize=(10.0, 8.0))
for ax in axs.flat:
    ax.set_aspect("equal")
    ax.axis("off")


def car_body(ax, L, W, x0, color=C["body"]):
    rect(ax, O, x0, 0, 0, L, W, color, C["dark"], 0.8, 1)


def axle(ax, p, beta, lo, hi, color=C["red"]):
    n = np.array([-math.sin(beta), math.cos(beta)])
    q0, q1 = np.asarray(p) + lo * n, np.asarray(p) + hi * n
    ax.plot([q0[0], q1[0]], [q0[1], q1[1]], color=color, lw=0.9, ls="--", zorder=2)


def icr_mark(ax, c, txt=None):
    ax.plot(*c, "o", ms=7, mfc="white", mec=C["accent"], mew=2, zorder=8)
    ax.text(c[0] + 0.03 * (axs[0, 0].get_xlim()[1] if False else 1), c[1] + 0.02, txt or T("瞬心", "ICR"), color=C["accent"], fontsize=11)


# (a) 差速 AGV：两轮共轴，瞬心在这条轴线上任一点
ax = axs[0, 0]
b = P["b"]
car_body(ax, P["length"], P["width"], -0.03)
for y in (b / 2, -b / 2):
    wheel(ax, O, 0, y, 0.0, r=P["r"], width=0.03)
wheel(ax, O, -0.15, 0, 0.0, r=0.025, width=0.018, fc="#8a959b")
axle(ax, (0, 0), 0.0, -0.45, 0.62)
ax.plot([0], [0], "o", color=C["ink"], ms=3)
for yy, tt in ((0.45, T("ω_R < ω_L 时瞬心在右侧", "")), (-0.3, "")):
    pass
icr_mark(ax, (0, 0.5), T("瞬心（v/ω）", "ICR (v/ω)"))
arrow(ax, (0.0, -0.13), (0.16, -0.13), C["green"], 1.4)
arrow(ax, (0.0, 0.13), (0.11, 0.13), C["green"], 1.4)
ax.text(-0.42, -0.42, T("脚轮不施加约束；两轮轴线重合", "the castor adds nothing; both axles on one line"), fontsize=9, color=C["muted"])
ax.set_xlim(-0.45, 0.45)
ax.set_ylim(-0.47, 0.66)
ax.set_title(T("(a) 差速 AGV：rank C = 1，δm = 2", "(a) differential AGV: rank C = 1, δm = 2"), fontsize=10.5)
# (b) 购物车：后轮固定，前轮是脚轮
ax = axs[0, 1]
car_body(ax, 0.8, 0.56, 0.32, "#eef0e6")
for y in (0.25, -0.25):
    wheel(ax, O, 0, y, 0.0, r=0.05, width=0.03)
for y, bt in ((0.25, math.radians(70)), (-0.25, math.radians(40))):
    wheel(ax, O, 0.64, y, bt, r=0.04, width=0.025, fc="#8a959b")
axle(ax, (0, 0), 0.0, -0.4, 0.95)
icr_mark(ax, (0, 0.85))
ax.text(0.45, 0.42, T("前轮：脚轮", "front: castors"), fontsize=9, color=C["muted"])
ax.text(-0.25, -0.48, T("后轮固定：瞬心只能在后轴延长线上", "rear wheels fixed: the ICR must lie on the rear axle line"), fontsize=9, color=C["muted"])
ax.set_xlim(-0.3, 0.9)
ax.set_ylim(-0.52, 1.0)
ax.set_title(T("(b) 购物车：rank C = 1，δm = 2", "(b) shopping cart: rank C = 1, δm = 2"), fontsize=10.5)
# (c) 阿克曼：四条轴线交于一点
L4, w4, di = 1.2, 0.8, math.radians(30)
R = L4 / math.tan(di) + w4 / 2
do = math.atan(L4 / (R + w4 / 2))
for ax, (bl, br), ttl in ((axs[1, 0], (di, do), T("(c) 按阿克曼条件转向：rank C = 2，δm = 1", "(c) Ackermann steering: rank C = 2, δm = 1")),
                          (axs[1, 1], (di, di), T("(d) 两前轮平行转向：rank C = 3，δm = 0", "(d) parallel steering: rank C = 3, δm = 0"))):
    car_body(ax, 1.6, 0.9, 0.6)
    for y in (w4 / 2, -w4 / 2):
        wheel(ax, O, 0, y, 0.0, r=0.16, width=0.09)
    wheel(ax, O, L4, w4 / 2, bl, r=0.16, width=0.09)
    wheel(ax, O, L4, -w4 / 2, br, r=0.16, width=0.09)
    axle(ax, (0, 0), 0.0, -0.6, R + 0.35)
    for p, bt in (((L4, w4 / 2), bl), ((L4, -w4 / 2), br)):
        n = np.array([-math.sin(bt), math.cos(bt)])
        hi = (R + 0.4 - p[1]) / n[1]
        axle(ax, p, bt, -0.25, hi)
    ax.set_xlim(-0.6, 1.8)
    ax.set_ylim(-0.75, R + 0.45)
    ax.set_title(ttl, fontsize=10.5)
icr_mark(axs[1, 0], (0, R))
axs[1, 0].text(-0.55, -0.7, T("内侧轮转得多，外侧轮转得少", "the inner wheel turns more than the outer"), fontsize=9, color=C["muted"])
# (d) 平行转向：两条前轴线与后轴线围成三角形
n1 = np.array([-math.sin(di), math.cos(di)])
p1, p2 = np.array([L4, w4 / 2]), np.array([L4, -w4 / 2])
t1 = (0 - p1[0]) / n1[0]
t2 = (0 - p2[0]) / n1[0]
q1, q2 = p1 + t1 * n1, p2 + t2 * n1
axs[1, 1].fill([q1[0], q2[0], q2[0]], [q1[1], q2[1], q2[1]], color=C["red"], alpha=0.1)
axs[1, 1].plot([q1[0], q2[0]], [q1[1], q2[1]], "o", color=C["red"], ms=4)
axs[1, 1].text(-0.55, -0.7, T("三条轴线不交于一点：至少一个轮子要侧滑", "the axles do not meet: some wheel must slide"), fontsize=9, color=C["red"])
fig.subplots_adjust(wspace=0.08, hspace=0.18)
figure(fig, "fig19_1_2")
plt.close(fig)
