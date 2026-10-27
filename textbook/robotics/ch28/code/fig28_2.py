"""28.2 节的示意图。

图 28.2.1：(a) G1 站立时的脚掌（脚底四个接触小球围成）与双脚支撑多边形（俯视），叉为质心的投影；
          (b) MuJoCo 中 G1 用踝策略前后摆动：接触力的压力中心、按式 (28.2.3) 算出的零力矩点、线性倒立摆的近似 x − z ẍ/𝔤，
              以及质心的 x；虚线为脚尖、脚跟。
图 28.2.2：(a) 线性倒立摆的相平面：横轴为质心相对零力矩点（脚尖）的位置，纵轴为速度；两条斜线 ẋ = ±ω(x − p) 之间的轨线
              越不过支点，被推得太快就越过去；(b) 按零力矩点规划质心（算例 28.2.3）：侧向的零力矩点与质心；
          (c) 俯视：脚印、零力矩点与质心的路线。
"""
import math

import numpy as np
from scipy.spatial import ConvexHull

from _ch28 import G, g1_stand, g1_sway, lip_bounded
from bookout import COLORS as C, T, figure, style

plt = style()
S = g1_stand()
com = S["com"]
r = S["r"]
fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.0), gridspec_kw=dict(width_ratios=[1, 1.6]))
ax = axs[0]
allp = []
for side, col in (("left", C["z"]), ("right", C["x"])):
    P = S["soles"][side][:, :2]
    x0, x1 = P[:, 0].min() - r, P[:, 0].max() + r
    poly = np.array([[x0, P[P[:, 0] < 0, 1].min() - r], [x1, P[P[:, 0] > 0, 1].min() - r], [x1, P[P[:, 0] > 0, 1].max() + r],
                     [x0, P[P[:, 0] < 0, 1].max() + r]])
    ax.fill(poly[:, 1] * 1000, poly[:, 0] * 1000, color=col, alpha=0.25, lw=1.2, ec=col)
    ax.plot(P[:, 1] * 1000, P[:, 0] * 1000, "o", color=col, ms=4)
    allp.append(poly)
allp = np.vstack(allp)
hull = ConvexHull(allp)
hp = allp[np.r_[hull.vertices, hull.vertices[0]]]
ax.plot(hp[:, 1] * 1000, hp[:, 0] * 1000, color=C["ink"], lw=1.2, ls="--", label=T("双脚支撑多边形", "double-support polygon"))
ax.plot([com[1] * 1000], [com[0] * 1000], "x", color=C["ink"], ms=10, mew=2, label=T("质心的投影", "projection of the CoM"))
ax.set_aspect("equal")
ax.invert_xaxis()
ax.set_xlabel(T("y / mm（向左为正）", "y / mm (positive to the left)"))
ax.set_ylabel(T("x / mm（向前）", "x / mm (forward)"))
ax.set_title(T("(a) G1 的脚掌与支撑多边形", "(a) G1's feet and support polygon"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="lower center", ncol=2)
ax.set_ylim(-125, 160)
ax.grid(alpha=0.25)
ax = axs[1]
t, cop, zmp, lip, cx, _ = g1_sway(0.02, -0.02, f=0.5)
sl = t < 6.0
toe = S["soles"]["left"][:, 0].max() + r
heel = S["soles"]["left"][:, 0].min() - r
ax.plot(t[sl], cop[sl] * 1000, color=C["z"], lw=2.6, alpha=0.6, label=T("压力中心（接触力）", "centre of pressure (contact forces)"))
ax.plot(t[sl], zmp[sl] * 1000, color=C["ink"], lw=1.1, ls="--", label=T("零力矩点，式 (28.2.3)", "ZMP, Eq. (28.2.3)"))
ax.plot(t[sl], lip[sl] * 1000, color=C["accent"], lw=1.4, label=T(r"线性倒立摆 $x - z\ddot x/\mathfrak{g}$", r"linear inverted pendulum $x - z\ddot x/\mathfrak{g}$"))
ax.plot(t[sl], cx[sl] * 1000, color=C["y"], lw=1.6, label=T("质心 x", "CoM x"))
for yv, lab in ((toe, T("脚尖", "toe")), (heel, T("脚跟", "heel"))):
    ax.axhline(yv * 1000, color=C["muted"], lw=1, ls=":")
    ax.text(t[sl][0] + 0.02, yv * 1000 + 3, lab, fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("x / mm", "x / mm"))
ax.set_title(T("(b) MuJoCo 中 G1 前后摆动", "(b) G1 swaying back and forth in MuJoCo"), fontsize=11)
ax.legend(fontsize=8, frameon=False, loc="lower right", ncol=2)
ax.set_ylim(-110, 160)
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig28_2_1")

# ---------------------------------------------------------------- 图 28.2.2
z_c = float(com[2])
w = math.sqrt(G / z_c)
fig, axs = plt.subplots(1, 3, figsize=(13.4, 3.9), gridspec_kw=dict(width_ratios=[1, 1.25, 1.25]))
ax = axs[0]
front = toe - com[0]
xs = np.linspace(-0.25, 0.1, 10)
ax.plot(xs * 1000, -w * xs, color=C["muted"], lw=1.2, ls="--")
ax.plot(xs * 1000, w * xs, color=C["muted"], lw=1.2, ls="--")
for v0, col in ((0.3, C["y"]), (w * front, C["accent"]), (0.6, C["x"])):
    x0 = -front
    tt = np.linspace(0, 1.4, 400)
    x = x0 * np.cosh(w * tt) + v0 / w * np.sinh(w * tt)
    v = x0 * w * np.sinh(w * tt) + v0 * np.cosh(w * tt)
    keep = (x < 0.1) & (x > -0.25)
    ax.plot(x[keep] * 1000, v[keep], color=col, lw=1.8, label=T(f"推后 {v0:.2f} m/s", f"pushed to {v0:.2f} m/s"))
ax.axvline(0, color=C["ink"], lw=0.8)
ax.text(3, -0.55, T("零力矩点\n（脚尖）", "ZMP\n(toe)"), fontsize=8.5)
ax.set_xlabel(T("质心相对零力矩点的位置 x − p / mm", "CoM relative to the ZMP, x − p / mm"))
ax.set_ylabel(T("质心速度 / (m/s)", "CoM velocity / (m/s)"))
ax.set_title(T("(a) 相平面：推一下能不能站住", "(a) phase plane: can it stand after a push"), fontsize=11)
ax.legend(fontsize=8, frameon=False, loc="upper left")
ax.set_ylim(-0.7, 0.8)
ax.grid(alpha=0.25)
# 步行
SL, TS, TD, NSTEP = 0.2, 0.6, 0.1, 10
yf = float(S["soles"]["left"][:, 1].mean())
dt = 0.001
t_all = np.arange(0, (NSTEP + 4) * TS, dt)
px, py = np.zeros_like(t_all), np.zeros_like(t_all)
for i, tt in enumerate(t_all):
    k = int(tt // TS) - 1
    tau = tt - (k + 1) * TS
    if k < 0:
        continue
    if k > NSTEP:
        px[i], py[i] = (NSTEP - 1) * SL, 0.0
        continue
    side = 1 if k % 2 == 0 else -1
    x_now, y_now = k * SL, side * yf
    x_prev = (k - 1) * SL if k >= 1 else 0.0
    y_prev = -side * yf if k >= 1 else 0.0
    if k == NSTEP:
        x_now, y_now = (NSTEP - 1) * SL, 0.0
    s = min(tau / TD, 1.0)
    px[i] = x_prev + s * (x_now - x_prev)
    py[i] = y_prev + s * (y_now - y_prev)
xc = lip_bounded(px, dt, w)
yc = lip_bounded(py, dt, w)
ax = axs[1]
ax.plot(t_all, py * 1000, color=C["z"], lw=1.6, label=T("零力矩点 p_y", "ZMP p_y"))
ax.plot(t_all, yc * 1000, color=C["x"], lw=1.8, label=T("质心 y", "CoM y"))
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("y / mm", "y / mm"))
ax.set_title(T("(b) 侧向的零力矩点与质心", "(b) sideways ZMP and CoM"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
ax.grid(alpha=0.25)
ax = axs[2]
for k in range(NSTEP):
    side = 1 if k % 2 == 0 else -1
    ax.add_patch(plt.Rectangle((k * SL - 0.055 + 0.0, side * yf - 0.03), 0.18, 0.06, color=C["z"] if side > 0 else C["x"], alpha=0.22))
ax.add_patch(plt.Rectangle(((NSTEP - 1) * SL - 0.055, yf - 0.03), 0.18, 0.06, color=C["z"], alpha=0.22))   # 最后一步：左脚并到右脚旁
ax.plot(px, py, color=C["ink"], lw=1.0, ls="--", label=T("零力矩点", "ZMP"))
ax.plot(xc, yc, color=C["accent"], lw=1.8, label=T("质心", "CoM"))
ax.set_xlabel(T("x / m", "x / m"))
ax.set_ylabel(T("y / m", "y / m"))
ax.set_title(T("(c) 俯视：脚印与路线", "(c) top view: footprints and paths"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.0))
ax.set_ylim(-0.25, 0.3)
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig28_2_2")
