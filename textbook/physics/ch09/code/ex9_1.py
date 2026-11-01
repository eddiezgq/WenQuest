"""9.1 节的计算：

算例 9.1.1  工人用拉杆把料车拉上坡道：料车 m = 60 kg，坡道倾角 5°，沿坡道走 s = 8.0 m；拉力 F = 80 N，与坡道成 20° 斜向上；
            滚动阻力系数 C_rr = 0.020。求拉力、重力、支持力、滚动阻力各做多少功，总功多少（图 9.1.1）。
算例 9.1.2  气缸推动活塞：缸径 50 mm，关闭进气阀时缸内气柱长 x0 = 50 mm、绝对压强 0.50 MPa，活塞另一侧为大气（取 0.10 MPa）。
            气体缓慢膨胀、温度不变（pV 不变），活塞走过 s = 100 mm。每 20 mm 测一次推力，用梯形法求功，与精确值比较；
            间隔减半，误差变成多少（图 9.1.2）。
算例 9.1.3  功与路径：AGV（M = 500 kg，C_rr = 0.015）从 A(0, 0) 到 B(8, 6) m，走直线与沿通道（先 x 后 y），滚动阻力各做多少功；
            机械臂把 2.0 kg 的零件从 A(0.60, 0.20) m 移到 B(0.20, 0.70) m（x 水平、z 竖直），走直线与走向上凸起的圆弧，
            重力各做多少功。两种力都按线积分 ∫F·dr 数值计算（图 9.1.3）。
估一估      码垛机器人每小时搬 600 箱，每箱 20 kg，抬高 1.2 m：对箱子做的功与平均功率。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 9.1.1
m, alpha, s, F, phi, Crr = 60.0, math.radians(5.0), 8.0, 80.0, math.radians(20.0), 0.020
W_F = F * s * math.cos(phi)
W_g = -m * g * s * math.sin(alpha)
N = m * g * math.cos(alpha) - F * math.sin(phi)                # 垂直坡道方向平衡（拉力有向上的分量）
W_r = -Crr * N * s
W_tot = W_F + W_g + W_r
out(m=m, alpha_deg=5.0, s=s, F=F, phi_deg=20.0, Crr=Crr, W_F=W_F, W_g=W_g, N=N, W_r=W_r, W_tot=W_tot,
    Fpar=F * math.cos(phi), mg_sin=m * g * math.sin(alpha), nW_g=-W_g, nW_r=-W_r)

# ---- 算例 9.1.2：气缸
D, x0, p0, pa, stroke = 0.050, 0.050, 0.50e6, 0.10e6, 0.100
A = math.pi * D ** 2 / 4


def force(x):
    return (p0 * x0 / (x0 + x) - pa) * A


W_exact = p0 * A * x0 * math.log((x0 + stroke) / x0) - pa * A * stroke


def trap(n):
    xs = np.linspace(0, stroke, n + 1)
    fs = force(xs)
    return float(np.sum((fs[1:] + fs[:-1]) / 2 * np.diff(xs))), xs, fs


W5, xs5, fs5 = trap(5)
W10, _, _ = trap(10)
assert W5 > W_exact and W10 > W_exact                         # 曲线下凸，梯形法偏大
out(D_mm=D * 1000, x0_mm=x0 * 1000, p0=p0 / 1e6, pa=pa / 1e6, stroke_mm=stroke * 1000, A_cm2=A * 1e4,
    F0=force(0.0), F1=force(stroke), W_exact=W_exact, W5=W5, W10=W10, e5=W5 - W_exact, e10=W10 - W_exact,
    ratio=(W5 - W_exact) / (W10 - W_exact), W_gas=p0 * A * x0 * math.log((x0 + stroke) / x0), W_air=pa * A * stroke,
    Favg=W_exact / stroke)


# ---- 算例 9.1.3：线积分 ∫F·dr，把路径分成很多小段求和
def line_integral(Ffun, path, n=4000):
    """path(u), u 从 0 到 1；用每一小段中点的力乘这一小段的位移再求和。"""
    u = np.linspace(0, 1, n + 1)
    r = np.array([path(t) for t in u])
    dr = np.diff(r, axis=0)
    mid = (r[1:] + r[:-1]) / 2
    return float(sum(np.dot(Ffun(p, q), q) for p, q in zip(mid, dr)))


M, Crr2 = 500.0, 0.015
A2, B2 = np.array([0.0, 0.0]), np.array([8.0, 6.0])
roll = lambda p, dr: -Crr2 * M * g * dr / np.linalg.norm(dr)    # 滚动阻力：大小 C_rr Mg，方向与这一小段位移相反
straight = lambda t: A2 + t * (B2 - A2)
aisle = lambda t: np.array([16 * t, 0.0]) if t <= 0.5 else np.array([8.0, 12 * (t - 0.5)])
W_roll_s = line_integral(roll, straight)
W_roll_a = line_integral(roll, aisle)
assert abs(W_roll_s + Crr2 * M * g * 10) < 1e-6 and abs(W_roll_a + Crr2 * M * g * 14) < 1e-6

mp = 2.0
Ap, Bp = np.array([0.60, 0.20]), np.array([0.20, 0.70])
weight = lambda p, dr: np.array([0.0, -mp * g])
line_p = lambda t: Ap + t * (Bp - Ap)
mid_ab, half = (Ap + Bp) / 2, np.linalg.norm(Bp - Ap) / 2
nrm = np.array([-(Bp - Ap)[1], (Bp - Ap)[0]]) / (2 * half)     # 垂直于 AB、指向左上方的单位矢量
if nrm[1] < 0:
    nrm = -nrm
bulge = 0.25                                                   # 圆弧中点离开直线 0.25 m
R = (half ** 2 + bulge ** 2) / (2 * bulge)
C = mid_ab + nrm * (bulge - R)
a0, a1 = math.atan2(*(Ap - C)[::-1]), math.atan2(*(Bp - C)[::-1])
if a1 < a0:
    a1 += 2 * math.pi
if a1 - a0 > math.pi:                                          # 取经过上方凸起的那段短弧
    a0, a1 = a0 + 2 * math.pi, a1
arc = lambda t: C + R * np.array([math.cos(a0 + (a1 - a0) * t), math.sin(a0 + (a1 - a0) * t)])
assert np.allclose(arc(0), Ap) and np.allclose(arc(1), Bp)
W_g_line = line_integral(weight, line_p)
W_g_arc = line_integral(weight, arc)
assert abs(W_g_line - W_g_arc) < 1e-9 and abs(W_g_line + mp * g * 0.5) < 1e-9
top = max(arc(t)[1] for t in np.linspace(0, 1, 401))
out(M=M, Crr2=Crr2, W_roll_s=W_roll_s, W_roll_a=W_roll_a, nRs=-W_roll_s, nRa=-W_roll_a, nGl=-W_g_line, F_roll=Crr2 * M * g, mp=mp, W_g_line=W_g_line, W_g_arc=W_g_arc,
    arc_top=top)

# ---- 估一估：码垛
mb, hb, nb = 20.0, 1.2, 600
Wb = mb * g * hb
out(mb=mb, hb=hb, nb=nb, Wb=Wb, Wh=Wb * nb / 1000, Pavg_pal=Wb * nb / 3600)

plt = style()
# ---- 图 9.1.1：坡道上的料车与各力（示意：坡角画大一些）
fig, ax = plt.subplots(figsize=(5.4, 3.2))
al = math.radians(12)
ca, sa = math.cos(al), math.sin(al)
u_, n_ = np.array([ca, sa]), np.array([-sa, ca])                # 沿坡道、垂直坡道的单位矢量
ax.plot([0, 6.0 * ca], [0, 6.0 * sa], color=d.INK, lw=1.5)
ax.plot([0, 6.0 * ca], [0, 0], color=d.MUTED, lw=0.8)
th = np.linspace(0, al, 20)
ax.plot(0.9 * np.cos(th), 0.9 * np.sin(th), color=d.INK, lw=0.8); ax.text(1.0, 0.05, r"$\alpha$", fontsize=11)
c0 = 2.2 * u_
body = [c0 - 0.55 * u_ + 0.12 * n_, c0 + 0.55 * u_ + 0.12 * n_, c0 + 0.55 * u_ + 0.62 * n_, c0 - 0.55 * u_ + 0.62 * n_]
ax.add_patch(plt.Polygon(body, closed=True, fc="#e8d9a8", ec=d.INK, lw=1.2))
for k in (-0.35, 0.35):
    ax.add_patch(plt.Circle(c0 + k * u_ + 0.06 * n_, 0.06, color=d.INK))
cm = c0 + 0.37 * n_
fdir = math.cos(phi) * u_ + math.sin(phi) * n_
d.arrow(ax, cm, cm + 1.7 * fdir, d.VA, label=T("拉力 F", "pull F"), off=(-0.05, 0.25), fs=10)
d.arrow(ax, cm, cm + 1.7 * math.cos(phi) * u_, d.VA, lw=1.1, label=r"$F\cos\varphi$", off=(0.35, -0.12), fs=10)
tp = np.linspace(al, al + phi, 20)
ax.plot(cm[0] + 0.75 * np.cos(tp), cm[1] + 0.75 * np.sin(tp), color=d.VA, lw=0.8)
ax.text(cm[0] + 0.85, cm[1] + 0.33, r"$\varphi$", fontsize=11, color=d.VA)
d.arrow(ax, cm, cm + np.array([0, -1.25]), d.VR, label=T("重力 mg", "weight mg"), off=(0.6, -0.35), fs=10)
d.arrow(ax, c0 + 0.62 * n_, c0 + 1.5 * n_, d.VB, label=r"$F_\mathrm{N}$", off=(-0.3, 0.0), fs=10)
d.arrow(ax, c0 - 0.55 * u_ + 0.12 * n_, c0 - 1.25 * u_ + 0.12 * n_, d.MUTED, fs=9)
ax.text(*(c0 - 1.6 * u_ + 0.45 * n_), T("滚动阻力", "rolling resistance"), fontsize=9, color=d.MUTED, rotation=12, ha="center")
d.arrow(ax, 4.1 * u_ + 1.25 * n_, 5.9 * u_ + 1.25 * n_, d.INK, lw=1.2)
ax.text(*(5.0 * u_ + 1.5 * n_), T("位移 s", "displacement s"), fontsize=10, rotation=12, ha="center")
ax.set_aspect("equal"); ax.set_xlim(-0.2, 6.0); ax.set_ylim(-0.4, 3.5); d.clean(ax)
figure(fig, "fig9_1_1")

# ---- 图 9.1.2：气缸推力与位移，梯形法
fig, ax = plt.subplots(figsize=(4.8, 3.1))
xx = np.linspace(0, stroke, 300)
ax.fill_between(xx * 1000, force(xx), color=d.FIT, alpha=0.12, lw=0)
for i in range(5):
    ax.fill([xs5[i] * 1000, xs5[i + 1] * 1000, xs5[i + 1] * 1000, xs5[i] * 1000], [0, 0, fs5[i + 1], fs5[i]],
            fc="none", ec=d.DATA, lw=1.0)
ax.plot(xx * 1000, force(xx), color=d.FIT, lw=2, label=T("推力 F(x)", "force F(x)"))
ax.plot(xs5 * 1000, fs5, "o", color=d.DATA, ms=5, label=T("每 20 mm 一次测量", "a reading every 20 mm"))
ax.text(52, 420, T("曲线下的面积\n= 气体推力做的功", "area under the curve\n= work done by the gas"), fontsize=9, color=d.FIT)
ax.set_xlabel(T("活塞位移 x / mm", "piston displacement x / mm")); ax.set_ylabel(T("推力 F / N", "force F / N"))
ax.set_xlim(0, 105); ax.set_ylim(0, 850); ax.legend(frameon=False, fontsize=8.5, loc="upper right"); d.spines(ax)
figure(fig, "fig9_1_2")

# ---- 图 9.1.3：功与路径
fig, (a1_, a2_) = plt.subplots(1, 2, figsize=(6.6, 3.0))
P1 = np.array([straight(t) for t in np.linspace(0, 1, 50)])
P2 = np.array([aisle(t) for t in np.linspace(0, 1, 101)])
a1_.plot(P1[:, 0], P1[:, 1], color=d.VA, lw=2, label=T(f"直线 10 m：−{-W_roll_s:.0f} J", f"straight 10 m: −{-W_roll_s:.0f} J"))
a1_.plot(P2[:, 0], P2[:, 1], color=d.VR, lw=2, label=T(f"沿通道 14 m：−{-W_roll_a:.0f} J", f"along aisles 14 m: −{-W_roll_a:.0f} J"))
for p, n in ((A2, "A"), (B2, "B")):
    a1_.plot(*p, "o", color=d.INK); a1_.text(p[0] - 0.6, p[1] + 0.3, n, fontsize=11)
a1_.set_title(T("(a) 地面上：滚动阻力的功", "(a) floor: work of rolling resistance"), fontsize=10)
a1_.set_xlabel("x / m"); a1_.set_ylabel("y / m"); a1_.set_aspect("equal"); a1_.set_xlim(-1, 10); a1_.set_ylim(-1, 8.5)
a1_.legend(frameon=False, fontsize=8, loc="upper left"); d.spines(a1_)
Q1 = np.array([line_p(t) for t in np.linspace(0, 1, 50)])
Q2 = np.array([arc(t) for t in np.linspace(0, 1, 101)])
a2_.plot(Q1[:, 0], Q1[:, 1], color=d.VA, lw=2, label=T(f"直线：−{-W_g_line:.2f} J", f"straight: −{-W_g_line:.2f} J"))
a2_.plot(Q2[:, 0], Q2[:, 1], color=d.VR, lw=2, label=T(f"圆弧：−{-W_g_arc:.2f} J", f"arc: −{-W_g_arc:.2f} J"))
for p, n in ((Ap, "A"), (Bp, "B")):
    a2_.plot(*p, "o", color=d.INK); a2_.text(p[0] - 0.07, p[1] - 0.03, n, fontsize=11)
for t in (0.2, 0.5, 0.8):
    q = arc(t); d.arrow(a2_, q, q + np.array([0, -0.12]), d.MUTED, lw=1.0, ms=9)
a2_.set_title(T("(b) 竖直面内：重力的功", "(b) vertical plane: work of gravity"), fontsize=10)
a2_.set_xlabel("x / m"); a2_.set_ylabel("z / m"); a2_.set_aspect("equal"); a2_.set_xlim(0, 0.85); a2_.set_ylim(0.0, 0.95)
a2_.legend(frameon=False, fontsize=8, loc="upper right"); d.spines(a2_)
fig.tight_layout()
figure(fig, "fig9_1_3")
