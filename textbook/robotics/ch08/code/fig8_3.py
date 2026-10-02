"""8.3 节的示意图。

图 8.3.1：算例 8.3.1 的二次规划：目标函数的等高线（椭圆）、可行域（正方形 |Δ_i| ≤ 0.1 rad）、无约束的解、
         截断解、等比例缩小的解和二次规划的解；在最优点，−∇q 沿起作用约束的外法向（μ ≥ 0），有效集法的迭代路径。
图 8.3.2：加了关节限位的扭簧手臂（算例 8.3.2）：无限位的解（关节 3 超限）与有限位的解（关节 3 靠在挡块上）。
图 8.3.3：单关节最小能量轨迹（算例 8.3.3）：速度曲线（无限速：三次多项式；限速 1.2 rad/s）、加速度曲线、乘子 μ_k。
"""
import math

import numpy as np
from scipy.optimize import linprog

from _fig8 import BLUE, C, GREY, ORANGE, PURPLE, arrow, clean, draw_arm, target
from _opt import L2R, L3R, arm_points, d, jac, qp_active_set, tip, tip_hessians
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 8.3.1
th = np.array([0.0, d(90)])
pd = np.array([0.5, 0.4])
J = jac(th, L2R)
e = pd - tip(th, L2R)
Q, c = J.T @ J, -J.T @ e
A = np.vstack([np.eye(2), -np.eye(2)])
b = 0.1 * np.ones(4)
r = qp_active_set(Q, c, A, b, x0=np.zeros(2))
dq = r["x"]
dfree = np.linalg.solve(J, e)
dclip = np.clip(dfree, -0.1, 0.1)
dscale = dfree * 0.1 / np.abs(dfree).max()
fig, ax = plt.subplots(figsize=(7.4, 5.4))
x1 = np.linspace(-0.2, 0.2, 400)
x2 = np.linspace(-0.32, 0.12, 400)
X1, X2 = np.meshgrid(x1, x2)
qv = 0.5 * (Q[0, 0] * X1 ** 2 + 2 * Q[0, 1] * X1 * X2 + Q[1, 1] * X2 ** 2) + c[0] * X1 + c[1] * X2
q0 = 0.5 * dfree @ Q @ dfree + c @ dfree
qopt = 0.5 * dq @ Q @ dq + c @ dq
ax.contour(X1, X2, qv - q0, levels=[1e-5, 1e-4, 3e-4, qopt - q0, 1e-3, 2e-3], colors=[C["muted"]] * 3 + [BLUE] + [C["muted"]] * 2,
           linewidths=[0.7, 0.7, 0.7, 1.3, 0.7, 0.7])
ax.fill([-0.1, 0.1, 0.1, -0.1], [-0.1, -0.1, 0.1, 0.1], color="#e3eef7", zorder=0)
ax.plot([-0.1, 0.1, 0.1, -0.1, -0.1], [-0.1, -0.1, 0.1, 0.1, -0.1], color=BLUE, lw=1.2)
ax.text(-0.095, 0.088, T("可行域\n|Δᵢ| ≤ 0.1 rad", "feasible set\n|Δᵢ| ≤ 0.1 rad"), fontsize=9, color=BLUE, va="top")
ax.plot(*dfree, "o", color=C["ink"], ms=6, zorder=6)
ax.text(dfree[0] + 0.008, dfree[1] - 0.005, T("无约束的解\n（末端一步到位）", "unconstrained\n(tip reached at once)"), fontsize=8.5)
ax.plot(*dclip, "s", color=ORANGE, ms=6, zorder=6)
ax.plot([dclip[0], 0.05], [dclip[1], -0.125], color=ORANGE, lw=0.6)
ax.text(0.052, -0.13, T("截断", "clipped"), fontsize=9, color=ORANGE)
ax.plot(*dscale, "D", color=PURPLE, ms=5, zorder=6)
ax.plot([dscale[0], 0.045], [dscale[1], -0.065], color=PURPLE, lw=0.6)
ax.text(0.047, -0.065, T("按比例缩小", "scaled down"), fontsize=9, color=PURPLE)
hist = np.array([h[0] for h in r["history"]])
ax.plot(hist[:, 0], hist[:, 1], "--", color=C["accent"], lw=1.0, zorder=5)
ax.plot(hist[:, 0], hist[:, 1], ".", color=C["accent"], ms=7, zorder=5)
ax.plot(*dq, "*", color=C["x"], ms=13, zorder=7)
ax.text(dq[0] - 0.012, dq[1] - 0.03, T("二次规划的解 Δ*", "QP solution Δ*"), fontsize=9.5, color=C["x"], ha="right")
g = Q @ dq + c
gn = -g / np.linalg.norm(g) * 0.06
arrow(ax, dq, dq + gn, C["x"], 1.6)
ax.text(dq[0] + gn[0] + 0.005, dq[1] + gn[1] - 0.012, r"$-\nabla q(\Delta^*) = \mu_4\,a_4$", fontsize=10, color=C["x"])
ax.text(-0.19, -0.3, T("虚线：有效集法的迭代（从 Δ = 0 出发）", "dashed: active-set iterates (from Δ = 0)"), fontsize=8.5, color=C["accent"])
ax.set_xlim(-0.2, 0.2)
ax.set_ylim(-0.32, 0.12)
ax.set_aspect("equal")
ax.set_xlabel(T("Δ₁ / rad", "Δ₁ / rad"), fontsize=10)
ax.set_ylabel(T("Δ₂ / rad", "Δ₂ / rad"), fontsize=10)
ax.tick_params(labelsize=8)
figure(fig, "fig8_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.3.2
L = L3R
thc = np.array([d(30), d(60), d(-60)])
Kw = np.diag([20.0, 10.0, 5.0])
pd3 = np.array([0.55, 0.45])
lo = np.array([d(-90), d(0), d(-80)])
hi = np.array([d(90), d(150), d(80)])
A3 = np.vstack([np.eye(3), -np.eye(3)])


def lagrange_newton(x, lam, k=20):
    for _ in range(k):
        Jx, H2 = jac(x, L), tip_hessians(x, L)
        HL = Kw + lam[0] * H2[0] + lam[1] * H2[1]
        st = np.linalg.solve(np.block([[HL, Jx.T], [Jx, np.zeros((2, 2))]]), -np.r_[Kw @ (x - thc) + Jx.T @ lam, tip(x, L) - pd3])
        x, lam = x + st[:3], lam + st[3:]
    return x, lam


xf, _ = lagrange_newton(thc.copy(), np.zeros(2))
x, lam = thc.copy(), np.zeros(2)
for _ in range(10):
    Jx, H2 = jac(x, L), tip_hessians(x, L)
    HL = Kw + lam[0] * H2[0] + lam[1] * H2[1]
    b3 = np.r_[hi - x, x - lo]
    beq = tip(x, L) - pd3
    lp = linprog(np.zeros(3), A_ub=A3, b_ub=0.95 * b3, A_eq=Jx, b_eq=-beq, bounds=[(None, None)] * 3)
    rr = qp_active_set(HL, Kw @ (x - thc), A3, b3, Jx, -beq, x0=lp.x)
    x, lam, mu = x + rr["x"], rr["lam"], rr["mu"]
fig, (ax, az) = plt.subplots(1, 2, figsize=(10.2, 4.6), gridspec_kw=dict(width_ratios=[1, 1]))
clean(ax)
clean(az)
arrow(ax, (-0.08, 0), (0.78, 0), C["x"], 1.0)
arrow(ax, (0, -0.08), (0, 0.72), C["y"], 1.0)
ax.text(0.785, -0.02, "$x$", color=C["x"], fontsize=12)
ax.text(0.015, 0.71, "$y$", color=C["y"], fontsize=12)
pf = arm_points(xf, L)
ps = arm_points(x, L)
for a_, lw_ in ((ax, 1.0), (az, 2.2)):
    draw_arm(a_, arm_points(thc, L), GREY, lw=2.5 * lw_, alpha=0.6, ls=(0, (4, 2)))
    draw_arm(a_, pf, ORANGE, lw=3.0 * lw_, ls=(0, (2, 1.5)))
    draw_arm(a_, ps, BLUE, lw=3.5 * lw_)
    target(a_, pd3)
ax.plot([0.38, 0.38, 0.6, 0.6, 0.38], [0.38, 0.51, 0.51, 0.38, 0.38], color=C["ink"], lw=0.6)
ax.text(0.38, 0.53, T("右图放大", "enlarged on the right"), fontsize=8.5)
ax.text(-0.08, -0.14, T(r"灰色虚线：自然形态 $\theta_c$；橙色虚线：不加限位的解；蓝色：加限位的解", r"grey dashed: natural posture $\theta_c$; orange dashed: without limits; blue: with limits"),
        fontsize=8.5, color=C["ink"])
ax.set_xlim(-0.12, 0.85)
ax.set_ylim(-0.18, 0.75)
j3 = ps[2]
a_link2 = math.atan2(ps[2][1] - ps[1][1], ps[2][0] - ps[1][0])
a_stop = a_link2 + lo[2]                                   # 挡块的方向：连杆 2 的延长线转过 −80°
az.plot([j3[0], j3[0] + 0.045 * math.cos(a_link2)], [j3[1], j3[1] + 0.045 * math.sin(a_link2)], color=C["muted"], lw=0.8, ls="--")
wedge = np.array([j3 + 0.016 * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(a_stop - 0.03, a_stop - 0.6, 12)])
az.fill(np.r_[j3[0], wedge[:, 0]], np.r_[j3[1], wedge[:, 1]], color=C["x"], alpha=0.85, zorder=9)
az.text(j3[0] + 0.006, 0.426, T("挡块：θ₃ 不能小于 −80°", "stop: θ₃ cannot go below −80°"), fontsize=9, color=C["x"])
pfz = pf[3]
az.text(0.505, 0.493, T(f"橙色（无限位）：θ₃ = {math.degrees(xf[2]):.1f}°，超限", f"orange (no limits): θ₃ = {math.degrees(xf[2]):.1f}°, beyond the limit")
        .replace("-", "−"), fontsize=9, color=ORANGE, ha="center")
az.text(0.456, 0.392, T(f"蓝色（加限位）：θ₃ = −80°，\n挡块的力矩 μ = {mu[5]:.3f} N·m", f"blue (with limits): θ₃ = −80°,\nstop torque μ = {mu[5]:.3f} N·m"),
        fontsize=9, color=BLUE, ha="left")
az.set_xlim(0.38, 0.6)
az.set_ylim(0.38, 0.51)
figure(fig, "fig8_3_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.3.3
Tt, thf, vmax, N = 2.0, 2.0, 1.2, 100
hh = Tt / N
Om = np.vstack([np.tril(np.ones((N, N)), -1) * hh, hh * np.ones(N)])
thN = np.array([hh * hh * (N - j - 1) + hh * hh / 2 for j in range(N)])
E = np.vstack([thN, hh * np.ones(N)])
ee = np.array([thf, 0.0])
Qt = hh * np.eye(N)
At, bt = Om[1:N], vmax * np.ones(N - 1)
lp = linprog(np.zeros(N), A_ub=At, b_ub=0.9 * bt, A_eq=E, b_eq=ee, bounds=[(None, None)] * N)
rt = qp_active_set(Qt, np.zeros(N), At, bt, E, ee, x0=lp.x)
r0 = qp_active_set(Qt, np.zeros(N), None, None, E, ee, x0=lp.x)
tk = np.arange(N + 1) * hh
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(11.0, 3.4))
a1.plot(tk, Om @ r0["x"], color=GREY, lw=1.6, label=T("不限速（三次多项式）", "no limit (cubic)"))
a1.plot(tk, Om @ rt["x"], color=BLUE, lw=1.8, label=T("限速 1.2 rad/s", "limit 1.2 rad/s"))
a1.axhline(vmax, color=C["x"], lw=0.8, ls="--")
a1.text(0.05, vmax + 0.04, r"$v_{\max}$", fontsize=10, color=C["x"])
a1.set_ylabel(r"$\omega$ / (rad/s)", fontsize=9.5)
a1.set_ylim(0, 1.75)
a1.legend(fontsize=8, loc="lower center")
tm = (np.arange(N) + 0.5) * hh
a2.step(tm, r0["x"], where="mid", color=GREY, lw=1.4)
a2.step(tm, rt["x"], where="mid", color=BLUE, lw=1.6)
a2.axhline(0, color=C["muted"], lw=0.5)
a2.set_ylabel(r"$a$ / (rad/s²)", fontsize=9.5)
a3.bar(tk[1:N], rt["mu"], width=hh * 0.8, color=C["accent"])
a3.set_ylabel(T(r"乘子 $\mu_k$", r"multiplier $\mu_k$"), fontsize=9.5)
a3.text(0.05, rt["mu"].max() * 0.93, r"$\Sigma\mu_k = %.2f$" % rt["mu"].sum(), fontsize=9.5)
for a in (a1, a2, a3):
    a.set_xlabel(r"$t$ / s", fontsize=9.5)
    a.set_xlim(0, 2)
    a.tick_params(labelsize=8)
    a.grid(alpha=0.3, lw=0.5)
fig.tight_layout()
figure(fig, "fig8_3_3")
plt.close(fig)
