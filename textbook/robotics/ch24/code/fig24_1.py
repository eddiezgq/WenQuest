"""24.1 节的示意图。

图 24.1.1：(a) 秋千：广义坐标 φ，绳拉力沿绳、虚位移沿切线；(b) 桁架吊运：小车位置 x、摆角 φ；
          (c) 小车以 0.5 m/s² 加速 t_a 后匀速（吊绳 1 m），吊重的摆角：t_a = T_p/2 与 t_a = T_p；
          (d) 残留摆幅与 t_a/T_p 的关系：曲线为式 (24.1.21)，点为非线性方程 (24.1.19) 的数值解（RK4，1 ms）。
"""
import math

import numpy as np

from _ch24 import G0, rk4_step
from bookout import COLORS as C, T, figure, style

plt = style()


def arrow(ax, p, q, color, lw=1.5, ms=11, z=5, style_="-|>"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle=style_, color=color, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0),
                zorder=z)


lc, acc = 1.0, 0.5
w = math.sqrt(G0 / lc)
Tp = 2 * math.pi / w


def run(ta, Tend=8.0, h=1e-3):
    def f(s):
        a = acc if s[4] < ta else 0.0
        return np.array([s[1], a, s[3], -(a * math.cos(s[2]) + G0 * math.sin(s[2])) / lc, 1.0])
    s = np.zeros(5)
    n = int(round(Tend / h))
    S = np.zeros((n + 1, 5))
    for i in range(n):
        s = rk4_step(f, s, h)
        S[i + 1] = s
    return S


def residual(S, ta, h=1e-3):
    i0 = int(round(ta / h)) + 1
    E = 0.5 * lc ** 2 * S[i0:, 3] ** 2 + G0 * lc * (1 - np.cos(S[i0:, 2]))
    return math.degrees(math.acos(1 - E.max() / (G0 * lc)))


fig = plt.figure(figsize=(12.0, 8.4))
gs = fig.add_gridspec(2, 2, height_ratios=[0.8, 1.0], hspace=0.3, wspace=0.22)
a1, a2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
a3, a4 = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])

# (a) 秋千
a1.set_aspect("equal")
a1.axis("off")
ph = math.radians(35)
O = np.array([0.0, 0.0])
P = 2.5 * np.array([math.sin(ph), -math.cos(ph)])
a1.plot([-0.9, 0.9], [0, 0], color=C["ink"], lw=3)
a1.plot([O[0], P[0]], [O[1], P[1]], color=C["muted"], lw=1.4)
a1.plot([0, 0], [0, -2.7], color=C["muted"], lw=0.8, ls="--")
tt = np.linspace(-math.radians(55), math.radians(55), 100)
a1.plot(2.5 * np.sin(tt), -2.5 * np.cos(tt), color=C["muted"], lw=0.8, ls=":")
a1.add_patch(plt.Rectangle((P[0] - 0.22, P[1] - 0.06), 0.44, 0.12, fc=C["accent"], ec=C["ink"], lw=0.8, zorder=5))
arc = np.linspace(0, ph, 30)
a1.plot(0.8 * np.sin(arc), -0.8 * np.cos(arc), color=C["x"], lw=1.2)
a1.text(0.22, -1.05, r"$\varphi$", fontsize=14, color=C["x"])
u = (O - P) / np.linalg.norm(O - P)
arrow(a1, P, P + 0.9 * u, C["z"], lw=1.8)
a1.text(*(P + 0.95 * u + np.array([0.08, 0.0])), T("绳拉力", "rope tension"), fontsize=10.5, color=C["z"])
tg = np.array([math.cos(ph), math.sin(ph)])
arrow(a1, P, P + 0.75 * tg, C["y"], lw=1.8)
a1.text(*(P + 0.8 * tg + np.array([0.02, -0.1])), r"$\delta r$" + T("（虚位移）", " (virtual displacement)"), fontsize=10.5, color=C["y"])
arrow(a1, P, P + np.array([0, -0.8]), C["ink"], lw=1.4)
a1.text(P[0] + 0.07, P[1] - 0.85, r"$m\mathfrak{g}$", fontsize=12)
a1.set_xlim(-1.2, 2.6)
a1.set_ylim(-3.3, 0.35)
a1.set_title(T("(a) 秋千：一个广义坐标 φ", "(a) a swing: one generalized coordinate φ"), fontsize=11.5, loc="left")

# (b) 桁架吊运
a2.set_aspect("equal")
a2.axis("off")
a2.plot([-0.3, 3.4], [0.0, 0.0], color=C["ink"], lw=3)
xc = 1.2
a2.add_patch(plt.Rectangle((xc - 0.3, -0.18), 0.6, 0.3, fc="#c6dbef", ec=C["z"], lw=1.2, zorder=4))
phc = math.radians(-18)
L = np.array([xc + 1.3 * math.sin(phc), -0.03 - 1.3 * math.cos(phc)])
a2.plot([xc, L[0]], [-0.03, L[1]], color=C["muted"], lw=1.4)
a2.plot([xc, xc], [-0.03, -1.5], color=C["muted"], lw=0.8, ls="--")
a2.add_patch(plt.Rectangle((L[0] - 0.22, L[1] - 0.3), 0.44, 0.3, fc=C["accent"], ec=C["ink"], lw=0.8, zorder=4))
arc = np.linspace(phc, 0, 20)
a2.plot(xc + 0.6 * np.sin(arc), -0.03 - 0.6 * np.cos(arc), color=C["x"], lw=1.2)
a2.text(xc - 0.36, -0.82, r"$\varphi$", fontsize=14, color=C["x"])
arrow(a2, (0.0, 0.32), (xc, 0.32), C["y"], style_="-|>")
a2.text(0.5, 0.42, "x", fontsize=13, color=C["y"], style="italic")
arrow(a2, (xc + 0.3, -0.03), (xc + 1.0, -0.03), C["z"], lw=1.8)
a2.text(xc + 1.05, 0.03, "F", fontsize=13, color=C["z"], style="italic")
arrow(a2, (xc + 1.6, -0.5), (xc + 2.1, -0.5), C["ink"], lw=1.2)
a2.text(xc + 1.55, -0.38, T("加速 a", "accelerating a"), fontsize=10.5)
a2.text(xc - 0.12, -0.1, r"$M_{\mathrm{c}}$", fontsize=11.5, zorder=6)
a2.text(L[0] + 0.28, L[1] - 0.2, "m", fontsize=12, style="italic")
a2.text(xc + 0.5 * (L[0] - xc) - 0.18, -0.03 + 0.5 * (L[1] + 0.03), "l", fontsize=12, style="italic", color=C["muted"])
a2.set_xlim(-0.4, 3.6)
a2.set_ylim(-1.75, 0.65)
a2.set_title(T("(b) 桁架吊运：广义坐标 x、φ", "(b) gantry transfer: generalized coordinates x, φ"), fontsize=11.5, loc="left")

# (c) 摆角随时间
for ta, col, lab in ((round(Tp / 2, 3), C["x"], r"$t_a = T_p/2$"), (round(Tp, 3), C["z"], r"$t_a = T_p$")):
    S = run(ta)
    t = np.arange(len(S)) * 1e-3
    a3.plot(t, np.degrees(S[:, 2]), color=col, lw=1.4, label=lab)
    a3.axvline(ta, color=col, lw=0.8, ls=":")
a3.axhline(-math.degrees(2 * acc / G0), color=C["muted"], lw=0.8, ls="--")
a3.text(2.45, -math.degrees(2 * acc / G0) + 0.25, r"$-2a/\mathfrak{g}$", fontsize=11, color=C["muted"])
a3.set_xlabel(T("时间 t / s", "time t / s"))
a3.set_ylabel(T("吊重摆角 φ / (°)", "swing angle φ / (°)"))
a3.legend(frameon=False, fontsize=10, loc="upper right", ncol=2)
a3.set_ylim(-6.6, 7.6)
a3.set_xlim(0, 8)
a3.set_title(T("(c) 小车以 0.5 m/s² 加速 $t_a$ 后匀速（吊绳 1 m）", "(c) cart accelerates at 0.5 m/s² for $t_a$, then cruises (1 m rope)"),
             fontsize=11.5, loc="left")
for s_ in ("top", "right"):
    a3.spines[s_].set_visible(False)

# (d) 残留摆幅与加速时间
r = np.linspace(0, 2.6, 400)
a4.plot(r, np.degrees(2 * acc / G0 * np.abs(np.sin(math.pi * r))), color=C["ink"], lw=1.3, label=T("式 (24.1.21)", "Eq. (24.1.21)"))
pts = np.arange(0.25, 2.6, 0.25)
res = [residual(run(round(k * Tp, 3)), round(k * Tp, 3)) for k in pts]
a4.plot(pts, res, "o", color=C["x"], ms=5, label=T("非线性方程的数值解", "nonlinear equation (RK4)"))
a4.set_xlabel(T("加速时间 $t_a$ / 摆动周期 $T_p$", "acceleration time $t_a$ / swing period $T_p$"))
a4.set_ylabel(T("残留摆幅 / (°)", "residual swing / (°)"))
a4.legend(frameon=False, fontsize=10, loc="upper right")
a4.set_xlim(0, 2.6)
a4.set_ylim(0, 7.5)
a4.set_title(T("(d) 加速时间取周期的整数倍，不残留摆动", "(d) no residual swing when t_a is a whole number of periods"),
             fontsize=11.5, loc="left")
for s_ in ("top", "right"):
    a4.spines[s_].set_visible(False)
figure(fig, "fig24_1_1")
