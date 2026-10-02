"""8.1 节的示意图。

图 8.1.1：左：平面 2R 臂、目标点 p_d 与两组逆解；右：f(θ) = ½‖p(θ) − p_d‖² 在 (θ1, θ2) 平面上的等高线，
         标出两个极小点、鞍点、极大点和几处的负梯度方向。
图 8.1.2：梯度与等高线垂直；方向导数 D_u f = ∇f · u；最速下降方向 −∇f。
图 8.1.3：左：同一起点出发，梯度下降（α = 1、3）与牛顿法在等高线上的迭代路径；右：误差随迭代次数的变化（对数坐标）。
图 8.1.4：左：一元函数的牛顿步——用抛物线代替函数，跳到抛物线的最低点；右：牛顿法从 (0, 0.3) 出发收敛到鞍点，
         加保护的牛顿法收敛到极小点。
"""
import math

import numpy as np

from _fig8 import BLUE, C, GREY, ORANGE, PURPLE, arrow, clean, draw_arm, target
from _opt import L2R, arm_points, d, gradient_descent, ik_closed_2r, jac, newton, tip, tip_hessians
from bookout import T, figure, style

plt = style()
L = L2R
pd = np.array([0.5, 0.4])


def f(th):
    r = tip(th, L) - pd
    return 0.5 * float(r @ r)


def grad(th):
    return jac(th, L).T @ (tip(th, L) - pd)


def hess(th):
    J, r, H2 = jac(th, L), tip(th, L) - pd, tip_hessians(th, L)
    return J.T @ J + r[0] * H2[0] + r[1] * H2[1]


def fgrid(t1, t2):
    T1, T2 = np.meshgrid(t1, t2)
    x = L[0] * np.cos(T1) + L[1] * np.cos(T1 + T2) - pd[0]
    y = L[0] * np.sin(T1) + L[1] * np.sin(T1 + T2) - pd[1]
    return T1, T2, 0.5 * (x * x + y * y)


ta = ik_closed_2r(pd, L, +1)
tb = ik_closed_2r(pd, L, -1)
phi = math.atan2(pd[1], pd[0])
stat = {"min": [ta, tb], "saddle": [np.array([phi, 0.0]), np.array([phi, math.pi]), np.array([phi - math.pi, math.pi])],
        "max": [np.array([phi - math.pi, 0.0])]}
# 核对驻点的类型（黑塞矩阵的特征值）
kinds = {}
for k, pts in stat.items():
    for p in pts:
        lam = np.linalg.eigvalsh(hess(p))
        assert np.linalg.norm(grad(p)) < 1e-12
        kinds.setdefault(k, []).append(lam)
assert all(l.min() > 0 for l in kinds["min"])
assert all(l.min() < 0 < l.max() for l in kinds["saddle"])          # 三个鞍点：伸直指向目标、折叠指向或背向目标
assert all(l.max() < 0 for l in kinds["max"])                        # 一个极大点：伸直背向目标


def wrapd(a):
    return (math.degrees(a) + 180) % 360 - 180


# ---------------------------------------------------------------- 图 8.1.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.6), gridspec_kw=dict(width_ratios=[1, 1.25]))
clean(a1)
arrow(a1, (-0.08, 0), (0.86, 0), C["x"], 1.0)
arrow(a1, (0, -0.08), (0, 0.78), C["y"], 1.0)
a1.text(0.865, -0.02, "$x$", color=C["x"], fontsize=12)
a1.text(0.015, 0.77, "$y$", color=C["y"], fontsize=12)
th0 = np.array([0.0, d(90)])
draw_arm(a1, arm_points(th0, L), GREY, lw=3.5, alpha=0.9)
draw_arm(a1, arm_points(ta, L), BLUE, lw=3.5)
draw_arm(a1, arm_points(tb, L), ORANGE, lw=3.5, ls=(0, (4, 2)))
target(a1, pd, "$p_d$", dx=0.02, dy=-0.005, fs=12)
p0 = tip(th0, L)
a1.text(0.12, 0.2, T("起始形态\nθ₀ = (0°, 90°)", "start\nθ₀ = (0°, 90°)"), fontsize=9, color=C["muted"])
pa = arm_points(ta, L)[1]
a1.text(pa[0] - 0.02, pa[1] - 0.07, T("解 A（肘部在下）", "solution A (elbow down)"), fontsize=9, color=BLUE)
pb = arm_points(tb, L)[1]
a1.text(pb[0] - 0.1, pb[1] + 0.05, T("解 B（肘部在上）", "solution B (elbow up)"), fontsize=9, color=ORANGE)
a1.text(-0.06, -0.15, T("L₁ = 0.425 m，L₂ = 0.392 m", "L₁ = 0.425 m, L₂ = 0.392 m"), fontsize=9, color=C["ink"])
a1.set_xlim(-0.12, 0.92)
a1.set_ylim(-0.2, 0.82)

t = np.linspace(-math.pi, math.pi, 361)
T1, T2, Fz = fgrid(t, t)
levels = [0.002, 0.01, 0.03, 0.06, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.05]
cs = a2.contour(np.degrees(T1), np.degrees(T2), Fz, levels=levels, colors=C["muted"], linewidths=0.7)
a2.clabel(cs, levels=[0.01, 0.1, 0.35, 0.7], fmt=lambda v: f"{v:g}", fontsize=7)
a2.set_aspect("equal")
a2.set_xlim(-180, 180)
a2.set_ylim(-180, 180)
a2.set_xticks(range(-180, 181, 90))
a2.set_yticks(range(-180, 181, 90))
a2.set_xlabel(T("θ₁ / (°)", "θ₁ / (°)"), fontsize=10)
a2.set_ylabel(T("θ₂ / (°)", "θ₂ / (°)"), fontsize=10)
a2.tick_params(labelsize=8)
mk = {"min": ("o", BLUE), "saddle": ("s", PURPLE), "max": ("^", C["x"])}
for k, pts in stat.items():
    for p in pts:
        for dx in (0, 360, -360):
            x, y = wrapd(p[0]) + dx, math.degrees(p[1])
            for yy in ({y} | ({-180.0} if abs(y - 180) < 1e-9 else set())):
                if -181 <= x <= 181:
                    a2.plot(x, yy, mk[k][0], color=mk[k][1], ms=7, zorder=6, clip_on=False)
a2.text(wrapd(ta[0]) + 8, math.degrees(ta[1]) - 14, "A", color=BLUE, fontsize=11, fontweight="bold")
a2.text(wrapd(tb[0]) + 8, math.degrees(tb[1]) - 22, "B", color=ORANGE, fontsize=11, fontweight="bold")
for th in [np.array([d(-100), d(60)]), np.array([d(120), d(-30)]), np.array([d(-60), d(-120)]), np.array([d(150), d(110)]),
           np.array([d(0), d(90)]), np.array([d(90), d(10)])]:
    g = grad(th)
    u = -g / np.linalg.norm(g) * 32
    x, y = math.degrees(th[0]), math.degrees(th[1])
    arrow(a2, (x, y), (x + u[0], y + u[1]), C["accent"], 1.3, z=7, ms=9)
a2.plot(0, 90, "o", ms=5, color=C["ink"], zorder=8)
a2.text(4, 96, "θ₀", fontsize=10)
h1, = a2.plot([], [], "o", color=BLUE, ms=6, label=T("极小点", "minimum"))
h2, = a2.plot([], [], "s", color=PURPLE, ms=6, label=T("鞍点", "saddle"))
h3, = a2.plot([], [], "^", color=C["x"], ms=6, label=T("极大点", "maximum"))
h4, = a2.plot([], [], color=C["accent"], lw=1.5, label=T("负梯度方向 −∇f", "negative gradient −∇f"))
a2.legend(handles=[h1, h2, h3, h4], loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8.5, frameon=False)
figure(fig, "fig8_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.1.2
fig, ax = plt.subplots(figsize=(6.6, 4.4))
clean(ax)
Qm = np.array([[3.0, 1.0], [1.0, 1.5]])
xs = np.linspace(-2.2, 2.2, 300)
X, Y = np.meshgrid(xs, xs)
Z = 0.5 * (Qm[0, 0] * X * X + 2 * Qm[0, 1] * X * Y + Qm[1, 1] * Y * Y)
ax.contour(X, Y, Z, levels=[0.25, 0.75, 1.5, 2.5, 3.7], colors=C["muted"], linewidths=0.8)
x0 = np.array([0.9, 0.55])
g = Qm @ x0
gn = g / np.linalg.norm(g)
tang = np.array([-gn[1], gn[0]])
ax.plot([x0[0] - 0.9 * tang[0], x0[0] + 0.9 * tang[0]], [x0[1] - 0.9 * tang[1], x0[1] + 0.9 * tang[1]], color=C["ink"], lw=0.8, ls="--")
arrow(ax, x0, x0 + 0.85 * gn, C["x"], 2.0)
arrow(ax, x0, x0 - 0.85 * gn, C["accent"], 2.0)
ang = math.radians(35)
u = np.array([gn[0] * math.cos(ang) - gn[1] * math.sin(ang), gn[0] * math.sin(ang) + gn[1] * math.cos(ang)])
arrow(ax, x0, x0 + 0.75 * u, BLUE, 1.8)
proj = x0 + 0.75 * math.cos(ang) * gn
ax.plot([x0[0] + 0.75 * u[0], proj[0]], [x0[1] + 0.75 * u[1], proj[1]], color=BLUE, lw=0.8, ls=":")
a = np.linspace(math.atan2(gn[1], gn[0]), math.atan2(u[1], u[0]), 30)
ax.plot(x0[0] + 0.32 * np.cos(a), x0[1] + 0.32 * np.sin(a), color=BLUE, lw=0.8)
ax.text(x0[0] + 0.42 * math.cos(a[15]), x0[1] + 0.42 * math.sin(a[15]) - 0.05, r"$\varphi$", color=BLUE, fontsize=12)
ax.plot(*x0, "o", color=C["ink"], ms=4, zorder=6)
ax.text(x0[0] - 0.04, x0[1] - 0.3, "$x$", fontsize=12)
e = x0 + 0.85 * gn
ax.text(e[0] + 0.04, e[1] + 0.02, r"$\nabla f(x)$", color=C["x"], fontsize=12)
e = x0 - 0.85 * gn
ax.text(e[0] - 0.55, e[1] - 0.22, T(r"$-\nabla f$：下降最快", r"$-\nabla f$: steepest descent"), color=C["accent"], fontsize=10)
e = x0 + 0.75 * u
ax.text(e[0] - 0.2, e[1] + 0.08, "$u$", color=BLUE, fontsize=12)
ax.text(-2.2, -1.95, T(r"虚线：等高线在 $x$ 处的切线，与 $\nabla f$ 垂直", r"dashed: tangent of the level curve at $x$, perpendicular to $\nabla f$"), fontsize=9.5)
ax.text(-2.2, -2.25, T(r"沿 $u$ 的变化率 $D_u f = \nabla f\cdot u = \|\nabla f\|\cos\varphi$",
                       r"rate of change along $u$: $D_u f = \nabla f\cdot u = \|\nabla f\|\cos\varphi$"), fontsize=9.5)
ax.set_xlim(-2.25, 2.4)
ax.set_ylim(-2.3, 2.1)
figure(fig, "fig8_1_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.1.3
paths = {}
for a in (1.0, 3.0):
    paths[a] = gradient_descent(f, grad, th0, alpha=a, tol=1e-8)[1]
p4 = gradient_descent(f, grad, th0, alpha=4.0, tol=1e-8, kmax=300)[1]
pn = newton(grad, hess, th0, tol=1e-12)[1]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.4), gridspec_kw=dict(width_ratios=[1.05, 1]))
lo1, hi1, lo2, hi2 = -12, 12, 66, 94
t1 = np.radians(np.linspace(lo1, hi1, 300))
t2 = np.radians(np.linspace(lo2, hi2, 300))
T1, T2, Fz = fgrid(t1, t2)
a1.contour(np.degrees(T1), np.degrees(T2), Fz, levels=np.geomspace(2e-5, 3e-3, 9), colors=C["muted"], linewidths=0.7)
for pth, col, lab, mkr in ((paths[1.0], GREY, T("梯度下降 α = 1", "gradient descent α = 1"), "."),
                           (paths[3.0], C["accent"], T("梯度下降 α = 3", "gradient descent α = 3"), "."),
                           (pn, BLUE, T("牛顿法", "Newton's method"), "o")):
    P = np.degrees(pth)
    a1.plot(P[:, 0], P[:, 1], "-", marker=mkr, color=col, lw=1.2, ms=4 if mkr == "o" else 3, label=lab, zorder=5)
a1.plot(math.degrees(ta[0]), math.degrees(ta[1]), "*", color=C["x"], ms=11, zorder=7)
a1.text(math.degrees(ta[0]) + 0.6, math.degrees(ta[1]) - 1.6, T("解 A", "solution A"), color=C["x"], fontsize=9)
a1.text(0.6, 90.3, "θ₀", fontsize=10)
a1.set_xlim(lo1, hi1)
a1.set_ylim(lo2, hi2)
a1.set_aspect("equal")
a1.set_xlabel(T("θ₁ / (°)", "θ₁ / (°)"), fontsize=10)
a1.set_ylabel(T("θ₂ / (°)", "θ₂ / (°)"), fontsize=10)
a1.tick_params(labelsize=8)
a1.legend(fontsize=8.5, loc="lower left", frameon=True, framealpha=0.9)
for pth, col, lab in ((paths[1.0], GREY, "α = 1"), (paths[3.0], C["accent"], "α = 3"), (p4, PURPLE, "α = 4"), (pn, BLUE, T("牛顿法", "Newton"))):
    err = np.linalg.norm(pth - ta, axis=1)
    err = np.maximum(err, 1e-16)
    a2.semilogy(np.arange(len(err)), err, "-", marker="o" if col == BLUE else None, ms=4, color=col, lw=1.4, label=lab)
a2.set_xlim(0, 300)
a2.set_ylim(1e-15, 3)
a2.set_xlabel(T("迭代次数 k", "iteration k"), fontsize=10)
a2.set_ylabel(r"$\|\theta_k - \theta^*\|$ / rad", fontsize=10)
a2.tick_params(labelsize=8)
a2.grid(alpha=0.3, lw=0.5)
a2.legend(fontsize=8.5, loc="lower right")
a2.text(95, 0.6, T(r"$\alpha = 4$ 超过上限 $2/\lambda_{\max}$，不收敛", r"$\alpha = 4$ exceeds $2/\lambda_{\max}$: no convergence"), fontsize=8.5, color=PURPLE)
figure(fig, "fig8_1_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.1.4
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.2))
g1 = lambda x: 0.25 * x ** 4 - x ** 2 * 0.4 + 0.3 * x + 1.0
d1 = lambda x: x ** 3 - 0.8 * x + 0.3
dd1 = lambda x: 3 * x ** 2 - 0.8
x = np.linspace(-1.6, 1.7, 300)
a1.plot(x, g1(x), color=C["ink"], lw=1.6, label="$f(x)$")
xk = 1.2
q = g1(xk) + d1(xk) * (x - xk) + 0.5 * dd1(xk) * (x - xk) ** 2
a1.plot(x, q, color=BLUE, lw=1.2, ls="--", label=T(r"二次模型 $m_k(x)$", r"quadratic model $m_k(x)$"))
xn1 = xk - d1(xk) / dd1(xk)
a1.plot([xk], [g1(xk)], "o", color=C["ink"], ms=5)
a1.plot([xn1], [g1(xk) + d1(xk) * (xn1 - xk) + 0.5 * dd1(xk) * (xn1 - xk) ** 2], "o", color=BLUE, ms=5)
a1.plot([xn1, xn1], [0.55, g1(xn1)], color=BLUE, lw=0.8, ls=":")
a1.plot([xn1], [g1(xn1)], "o", color=C["accent"], ms=5)
a1.annotate("", xy=(xn1, 0.6), xytext=(xk, 0.6), arrowprops=dict(arrowstyle="-|>", color=C["accent"], lw=1.4))
a1.text((xk + xn1) / 2 - 0.25, 0.63, T("牛顿步", "Newton step"), color=C["accent"], fontsize=9.5)
a1.text(xk + 0.03, g1(xk) + 0.05, "$x_k$", fontsize=11)
a1.text(xn1 - 0.1, 0.48, "$x_{k+1}$", fontsize=11, color=BLUE)
a1.set_ylim(0.4, 1.9)
a1.set_xlim(-1.6, 1.7)
a1.set_yticks([])
a1.set_xticks([])
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.legend(fontsize=9, loc="upper center")
lo1, hi1, lo2, hi2 = -25, 75, -40, 100
t1 = np.radians(np.linspace(lo1, hi1, 300))
t2 = np.radians(np.linspace(lo2, hi2, 300))
T1, T2, Fz = fgrid(t1, t2)
a2.contour(np.degrees(T1), np.degrees(T2), Fz, levels=[0.002, 0.008, 0.016, 0.025, 0.04, 0.06, 0.09, 0.13], colors=C["muted"], linewidths=0.7)
thb = np.array([0.0, 0.3])
ps = newton(grad, hess, thb, tol=1e-12)[1]
pg = newton(grad, hess, thb, tol=1e-12, f=f, safeguard=True)[1]
P = np.degrees(ps)
a2.plot(P[:, 0], P[:, 1], "-o", color=PURPLE, ms=4, lw=1.3, label=T("牛顿法：收敛到鞍点", "Newton: converges to the saddle"))
P = np.degrees(pg)
a2.plot(P[:, 0], P[:, 1], "-o", color=BLUE, ms=4, lw=1.3, label=T("加保护的牛顿法：到极小点", "safeguarded Newton: to the minimum"))
a2.plot(math.degrees(phi), 0, "s", color=PURPLE, ms=8, zorder=6)
a2.plot(math.degrees(ta[0]), math.degrees(ta[1]), "*", color=C["x"], ms=11, zorder=6)
a2.text(math.degrees(thb[0]) - 9, math.degrees(thb[1]) - 9, T("起点", "start"), fontsize=9)
a2.set_xlim(lo1, hi1)
a2.set_ylim(lo2, hi2)
a2.set_aspect("equal")
a2.set_xlabel(T("θ₁ / (°)", "θ₁ / (°)"), fontsize=10)
a2.set_ylabel(T("θ₂ / (°)", "θ₂ / (°)"), fontsize=10)
a2.tick_params(labelsize=8)
a2.legend(fontsize=8.5, loc="lower left", framealpha=0.9)
figure(fig, "fig8_1_4")
plt.close(fig)
