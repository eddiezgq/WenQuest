"""7.1 节的示意图。

图 7.1.1：导数是割线斜率的极限：电机转速曲线上，割线随 h 减小而趋于切线。
图 7.1.2：关节电机的阶跃响应：时间常数 τ、63.2%、起点切线。
图 7.1.3：(a) 自由摆动的连杆；(b) 它的相平面：向量场、几条轨线、两个平衡点和分界线。
"""
import math

import numpy as np

from _ode import link_params, motor_first_order
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
box = dict(fc="white", ec="none", pad=1.0, alpha=0.9)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


tau, K = motor_first_order()
w_inf = K * 12.0
w = lambda t: w_inf * (1 - np.exp(-t / tau))
dw = lambda t: w_inf / tau * np.exp(-t / tau)

# ---------------------------------------------------------------- 图 7.1.1
fig, ax = plt.subplots(figsize=(5.6, 3.6))
ts = np.linspace(0, 0.09, 300)
ax.plot(ts * 1e3, w(ts), color=C["ink"], lw=1.6)
t0 = 0.02
ax.plot([t0 * 1e3], [w(t0)], "o", color=C["ink"], ms=4, zorder=5)
for h, col, ls in ((0.05, C["muted"], "--"), (0.025, C["z"], "--"), (0.01, C["y"], "--")):
    s = (w(t0 + h) - w(t0)) / h
    xx = np.array([t0 - 0.012, t0 + h + 0.006])
    ax.plot(xx * 1e3, w(t0) + s * (xx - t0), color=col, lw=1.0, ls=ls)
    ax.plot([(t0 + h) * 1e3], [w(t0 + h)], "o", color=col, ms=3.5)
    ax.text((t0 + h) * 1e3 + 1.5, w(t0 + h) - 16, f"h = {h * 1e3:.0f} ms", color=col, fontsize=9,
            bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.8))
s0 = dw(t0)
xx = np.array([t0 - 0.014, t0 + 0.022])
ax.plot(xx * 1e3, w(t0) + s0 * (xx - t0), color=C["x"], lw=1.6)
ax.text(t0 * 1e3 - 13, w(t0) + s0 * (-0.014) - 8, T("切线", "tangent"), color=C["x"], fontsize=10)
ax.text(t0 * 1e3 + 1.5, w(t0) - 20, r"$(t_0,\ \omega(t_0))$", fontsize=10)
ax.set_xlabel(T("时间 t / ms", "time t / ms"))
ax.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
ax.set_xlim(0, 90)
ax.set_ylim(0, 270)
ax.text(38, 40, T("割线斜率 $[\\omega(t_0+h)-\\omega(t_0)]/h$\n随 $h\\to 0$ 趋于切线斜率 $\\dot\\omega(t_0)$",
                  "slope of the secant $[\\omega(t_0+h)-\\omega(t_0)]/h$\ntends to the tangent slope $\\dot\\omega(t_0)$ as $h\\to 0$"),
        fontsize=10, color=C["ink"], linespacing=1.6)
clean(ax)
figure(fig, "fig7_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.1.2
fig, ax = plt.subplots(figsize=(5.6, 3.5))
ts = np.linspace(0, 0.1, 400)
ax.plot(ts * 1e3, w(ts), color=C["z"], lw=1.8)
ax.axhline(w_inf, color=C["muted"], lw=0.8, ls="--")
ax.text(101, w_inf, r"$\omega_\infty = Ku$", va="center", fontsize=10, color=C["muted"])
ax.plot([0, tau * 1e3], [0, w_inf], color=C["x"], lw=1.1)
ax.annotate(T("起点的切线", "tangent at the start"), xy=(tau * 1e3 * 0.45, w_inf * 0.45), xytext=(30, 95),
            color=C["x"], fontsize=9.5, arrowprops=dict(arrowstyle="-", color=C["x"], lw=0.7))
for n, lab in ((1, "63.2%"), (3, "95.0%")):
    ax.plot([n * tau * 1e3] * 2, [0, w(n * tau)], color=C["accent"], lw=0.9, ls=":")
    ax.plot([0, n * tau * 1e3], [w(n * tau)] * 2, color=C["accent"], lw=0.9, ls=":")
    ax.plot([n * tau * 1e3], [w(n * tau)], "o", color=C["accent"], ms=4)
    ax.text(n * tau * 1e3 + 1.5, w(n * tau) - 16, lab, color=C["accent"], fontsize=10)
ax.set_xticks([0, tau * 1e3, 2 * tau * 1e3, 3 * tau * 1e3, 4 * tau * 1e3, 5 * tau * 1e3])
ax.set_xticklabels(["0", r"$\tau$", r"$2\tau$", r"$3\tau$", r"$4\tau$", r"$5\tau$"])
ax.set_xlabel(T("时间 t", "time t"))
ax.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
ax.set_xlim(0, 100)
ax.set_ylim(0, 265)
clean(ax)
figure(fig, "fig7_1_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.1.3
Jo, lc, wn2 = link_params()
fig = plt.figure(figsize=(9.6, 4.2))
ax = fig.add_axes([0.0, 0.08, 0.27, 0.84])
ax.set_aspect("equal")
ax.axis("off")
th = math.radians(35)
L = 0.5
ax.plot([-0.12, 0.12], [0.0, 0.0], color=C["ink"], lw=2)
for x in np.linspace(-0.11, 0.11, 8):
    ax.plot([x, x - 0.025], [0.0, 0.025], color=C["muted"], lw=0.8)
ax.plot([0, 0], [0, -0.58], color=C["muted"], lw=0.8, ls="--")
tip = np.array([L * math.sin(th), -L * math.cos(th)])
ax.plot([0, tip[0]], [0, tip[1]], color=C["z"], lw=7, solid_capstyle="round", alpha=0.85)
ax.plot([0], [0], "o", color="white", ms=7, mec=C["ink"], zorder=5)
cm = tip / 2
ax.plot([cm[0]], [cm[1]], "o", color=C["ink"], ms=4, zorder=6)
ax.annotate("", xy=(cm[0], cm[1] - 0.17), xytext=cm, arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.4))
ax.text(cm[0] + 0.015, cm[1] - 0.15, r"$m\mathfrak{g}$", color=C["x"], fontsize=12)
tt = np.linspace(0, th, 30)
ax.plot(0.16 * np.sin(tt), -0.16 * np.cos(tt), color=C["accent"], lw=1.0)
ax.text(0.03, -0.24, r"$\theta$", color=C["accent"], fontsize=13)
ax.text(cm[0] / 2 + 0.04, cm[1] / 2 + 0.02, r"$l_c$", fontsize=12)
ax.text(-0.18, -0.70, T("(a) 刹车松开后自由摆动的连杆", "(a) a link swinging freely,\nbrake released"), fontsize=10)
ax.set_xlim(-0.25, 0.42)
ax.set_ylim(-0.75, 0.08)

ax = fig.add_axes([0.36, 0.13, 0.62, 0.8])
th_g = np.linspace(-1.5 * math.pi, 1.5 * math.pi, 25)
om_g = np.linspace(-11, 11, 13)
TH, OM = np.meshgrid(th_g, om_g)
U, V = OM, -wn2 * np.sin(TH)
sx, sy = 3 * math.pi / 24, 22 / 12                       # 每格的宽和高：箭头按格子大小归一，只表示方向
N = np.hypot(U / sx, V / sy) + 1e-9
ax.quiver(TH, OM, 0.42 * sx * U / N, 0.42 * sy * V / N, color=C["muted"], alpha=0.7, angles="xy", scale_units="xy", scale=1,
          width=0.0022, headwidth=4, headlength=4)
thc = np.linspace(-1.5 * math.pi, 1.5 * math.pi, 600)
omc = np.linspace(-12, 12, 600)
THc, OMc = np.meshgrid(thc, omc)
Ec = 0.5 * OMc ** 2 + wn2 * (1 - np.cos(THc))          # 能量 (7.1.13)：轨线就是它的等值线
ax.contour(THc, OMc, Ec, levels=[0.3 * wn2, 1.2 * wn2], colors=[C["z"]], linewidths=1.4)
ax.contour(THc, OMc, Ec, levels=[2 * wn2], colors=[C["x"]], linewidths=1.6)
ax.contour(THc, OMc, Ec, levels=[2.6 * wn2], colors=[C["y"]], linewidths=1.4)
for x0 in (-2 * math.pi, 0, 2 * math.pi):
    if abs(x0) <= 1.5 * math.pi:
        ax.plot([x0], [0], "o", color=C["ink"], ms=5, zorder=5)
for x0 in (-math.pi, math.pi):
    ax.plot([x0], [0], "o", mfc="white", mec=C["ink"], ms=6, zorder=5)
ax.set_xticks([-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi])
ax.set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])
ax.set_xlim(-1.5 * math.pi, 1.5 * math.pi)
ax.set_ylim(-12, 12)
ax.set_xlabel(T("角度 θ / rad", "angle θ / rad"))
ax.set_ylabel(T("角速度 $\\dot\\theta$ / (rad/s)", "angular velocity $\\dot\\theta$ / (rad/s)"))
ax.text(0.12, 0.7, T("稳定平衡点", "stable\nequilibrium"), fontsize=9, color=C["ink"], bbox=box)
ax.text(math.pi + 0.12, 0.7, T("不稳定\n平衡点", "unstable\nequilibrium"), fontsize=9, color=C["ink"], bbox=box)
ax.annotate(T("分界线", "separatrix"), xy=(-0.5 * math.pi, 2 * math.sqrt(wn2) * math.cos(math.pi / 4)), xytext=(-1.45 * math.pi, 3.2),
            color=C["x"], fontsize=9.5, bbox=box, arrowprops=dict(arrowstyle="-", color=C["x"], lw=0.7))
ax.text(1.5 * math.pi - 0.1, 7.4, T("越过顶点、\n一直转下去", "over the top,\nkeeps turning"), color=C["y"], fontsize=9.5, bbox=box, ha="right")
ax.text(-0.75, -3.0, T("来回摆动", "swinging"), color=C["z"], fontsize=9.5, bbox=box)
ax.text(-0.35 * math.pi, -11.4, T("(b) 相平面：箭头表示 $(\\dot\\theta,\\ \\ddot\\theta)$ 的方向", "(b) phase plane: arrows give the direction of $(\\dot\\theta,\\ \\ddot\\theta)$"),
        fontsize=10, bbox=box)
clean(ax)
figure(fig, "fig7_1_3")
plt.close(fig)
