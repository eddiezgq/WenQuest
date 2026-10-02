"""8.5 节的示意图。

图 8.5.1：UR5e 位置逆解（算例 8.5.1）。左：四种方法的残差 ‖r‖ 随迭代次数的变化；右：从伸直的形态出发，
         高斯-牛顿法与 LM 法每一步的关节 3 转角。
图 8.5.2：LM 步随阻尼系数 μ 的变化（平面 2R 臂，θ = (30°, 30°)）：μ = 0 是高斯-牛顿步，μ → ∞ 时步长趋于零、
         方向趋于负梯度；每个 μ 对应的步是线性化模型在以 ‖Δ‖ 为半径的圆内的最小点（信赖域）。
图 8.5.3：平面 3R 臂的运动学标定（算例 8.5.2）。左：12 个测量形态；右：50 个检验形态的末端误差，标定前后对比。
"""
import math

import numpy as np

from _fig8 import BLUE, C, GREY, ORANGE, PURPLE, arrow, clean, draw_arm, target
from _opt import (L2R, L3R, arm_points, d, gauss_newton, gradient_descent, jac, levenberg_marquardt, newton, tip,
                  ur5e_flange, ur5e_flange_jac)
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 8.5.1
wrist = np.array([d(-90), d(-90), 0.0])
th_true = np.array([d(40), d(-70), d(100)])
pd = ur5e_flange(np.r_[th_true, wrist])
res = lambda x: ur5e_flange(np.r_[x, wrist]) - pd
jr = lambda x: ur5e_flange_jac(np.r_[x, wrist])[:, :3]
F = lambda x: 0.5 * float(res(x) @ res(x))
gF = lambda x: jr(x).T @ res(x)


def hF(x):
    J, r = jr(x), res(x)
    S = np.zeros((3, 3))
    for j in range(3):
        e = np.zeros(3)
        e[j] = 1e-6
        S[:, j] = ((jr(x + e) - jr(x - e)) / 2e-6).T @ r
    return J.T @ J + (S + S.T) / 2


x0 = np.array([0.0, d(-90), d(90)])
runs = [(gradient_descent(F, gF, x0, tol=1e-10, alpha0=8.0)[1], GREY, T("梯度下降（阿米霍）", "gradient descent (Armijo)")),
        (newton(gF, hF, x0, tol=1e-12, f=F, safeguard=True)[1], PURPLE, T("牛顿法", "Newton's method")),
        (gauss_newton(res, jr, x0)[1], BLUE, T("高斯-牛顿法", "Gauss-Newton")),
        (levenberg_marquardt(res, jr, x0)[1], ORANGE, T("LM 法", "Levenberg-Marquardt"))]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 3.9))
for path, col, lab in runs:
    rr = np.array([max(np.linalg.norm(res(p)), 1e-17) for p in path])
    a1.semilogy(np.arange(len(rr)), rr, "-o" if len(rr) < 20 else "-", color=col, ms=3.5, lw=1.4, label=lab)
a1.set_xlim(0, 85)
a1.set_ylim(1e-17, 2)
a1.set_xlabel(T("迭代次数 k", "iteration k"), fontsize=9.5)
a1.set_ylabel(r"$\|r(\theta_k)\|$ / m", fontsize=9.5)
a1.legend(fontsize=8.5, loc="upper right")
a1.grid(alpha=0.3, lw=0.5)
a1.tick_params(labelsize=8)
pg = gauss_newton(res, jr, np.zeros(3))[1]
pl = levenberg_marquardt(res, jr, np.zeros(3))[1]
a2.plot(np.arange(len(pg)), np.degrees(pg[:, 2]), "-o", color=BLUE, ms=4, lw=1.3, label=T("高斯-牛顿法", "Gauss-Newton"))
a2.plot(np.arange(len(pl)), np.degrees(pl[:, 2]), "-o", color=ORANGE, ms=4, lw=1.3, label=T("LM 法", "Levenberg-Marquardt"))
a2.axhline(100, color=C["x"], lw=0.8, ls="--")
a2.text(len(pg) - 1, 180, T("真解 θ₃ = 100°", "true θ₃ = 100°"), fontsize=8.5, color=C["x"], ha="right")
a2.text(len(pg) - 1, np.degrees(pg[-1, 2]) - 170, T("1900° = 100° + 5 × 360°", "1900° = 100° + 5 × 360°"), fontsize=8.5, color=BLUE, ha="right")
a2.set_xlabel(T("迭代次数 k", "iteration k"), fontsize=9.5)
a2.set_ylabel(T("θ₃ / (°)", "θ₃ / (°)"), fontsize=9.5)
a2.legend(fontsize=8.5, loc="center right")
a2.grid(alpha=0.3, lw=0.5)
a2.tick_params(labelsize=8)
a2.set_title(T("从伸直的形态 θ = (0, 0, 0) 出发", "starting from the stretched posture θ = (0, 0, 0)"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig8_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.5.2
L = L2R
pd2 = np.array([0.5, 0.4])
th = np.array([d(30), d(30)])
r0 = tip(th, L) - pd2
J = jac(th, L)
g = J.T @ r0
A = J.T @ J
fig, ax = plt.subplots(figsize=(7.2, 5.4))
dgn = -np.linalg.solve(A, g)
lams = np.geomspace(1e-5, 1e2, 300)
curve = np.array([-np.linalg.solve(A + l * np.eye(2), g) for l in lams])
span = 1.15 * max(abs(dgn).max(), 0.3)
x1 = np.linspace(-span * 0.3, span * 1.1, 300)
x2 = np.linspace(-span * 0.3, span * 1.1, 300)
lo, hi, lo2, hi2 = -0.95, 0.55, -0.3, 1.55
X1, X2 = np.meshgrid(np.linspace(lo, hi, 300), np.linspace(lo2, hi2, 300))
Ft = np.zeros_like(X1)
Fm = np.zeros_like(X1)
for i in range(X1.shape[0]):
    for j in range(X1.shape[1]):
        dlt = np.array([X1[i, j], X2[i, j]])
        rr = tip(th + dlt, L) - pd2
        Ft[i, j] = 0.5 * rr @ rr
        rm = r0 + J @ dlt
        Fm[i, j] = 0.5 * rm @ rm
ax.contour(X1, X2, Ft, levels=np.geomspace(1e-4, 0.15, 9), colors=C["muted"], linewidths=0.7)
ax.contour(X1, X2, Fm, levels=np.geomspace(1e-4, 0.15, 9), colors="#9cc3e4", linewidths=0.7, linestyles="--")
ax.plot(curve[:, 0], curve[:, 1], color=ORANGE, lw=2.0, label=T("LM 步 Δ(μ)，μ 从 0 到 ∞", "LM step Δ(μ), μ from 0 to ∞"))
ax.plot(0, 0, "o", color=C["ink"], ms=5)
ax.text(0.03, 0.04, T("当前点 θ", "current point θ"), fontsize=9)
ax.plot(*dgn, "s", color=BLUE, ms=7, zorder=6)
ax.text(dgn[0] + 0.04, dgn[1] - 0.03, T("μ = 0：高斯-牛顿步", "μ = 0: Gauss-Newton step"), fontsize=9, color=BLUE)
gd = -g / np.linalg.norm(g) * 0.18
arrow(ax, (0, 0), gd, C["x"], 1.6)
ax.text(gd[0] - 0.12, gd[1] - 0.16, T("−∇F：μ → ∞ 时\n的方向", "−∇F: direction\nas μ → ∞"), fontsize=9, color=C["x"])
lk = 0.02
dk = -np.linalg.solve(A + lk * np.eye(2), g)
rad = np.linalg.norm(dk)
tt = np.linspace(0, 2 * math.pi, 200)
ax.plot(rad * np.cos(tt), rad * np.sin(tt), color=PURPLE, lw=1.0, ls=":")
ax.plot(*dk, "o", color=PURPLE, ms=6, zorder=6)
ax.text(dk[0] + 0.02, dk[1] - 0.05, T(f"μ = {lk}：圆内模型的最小点", f"μ = {lk}: model minimum inside the circle"), fontsize=9, color=PURPLE,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.0))
ax.set_aspect("equal")
ax.set_xlim(lo, hi)
ax.set_ylim(lo2, hi2)
ax.set_xlabel(T("Δ₁ / rad", "Δ₁ / rad"), fontsize=9.5)
ax.set_ylabel(T("Δ₂ / rad", "Δ₂ / rad"), fontsize=9.5)
ax.tick_params(labelsize=8)
h1, = ax.plot([], [], color=C["muted"], lw=0.8, label=T("F(θ + Δ) 的等高线", "level curves of F(θ + Δ)"))
h2, = ax.plot([], [], color="#9cc3e4", lw=0.8, ls="--", label=T("线性化模型的等高线", "level curves of the linearised model"))
ax.legend(fontsize=8.5, loc="upper right", framealpha=0.95)
figure(fig, "fig8_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.5.3
rng = np.random.default_rng(8)
Nm = 12
TH = np.radians(rng.uniform([-90, -150, -150], [90, 150, 150], size=(Nm, 3)))
phi_true = np.r_[0.4262, 0.3911, 0.1013, np.radians([0.3, -0.5, 0.8])]
phi_nom = np.r_[L3R, 0.0, 0.0, 0.0]
sig = 5e-5
model = lambda phi, t: tip(t + phi[3:], phi[:3])
meas = np.array([model(phi_true, t) for t in TH]) + sig * rng.standard_normal((Nm, 2))


def rc(phi):
    return np.concatenate([model(phi, t) - m for t, m in zip(TH, meas)])


def jc(phi):
    rows = []
    for t in TH:
        th_ = t + phi[3:]
        a = np.cumsum(th_)
        rows.append(np.hstack([np.array([[math.cos(a[i]), math.sin(a[i])] for i in range(3)]).T, jac(th_, phi[:3])]))
    return np.vstack(rows)


phat = gauss_newton(rc, jc, phi_nom)[0]
THv = np.radians(rng.uniform([-90, -150, -150], [90, 150, 150], size=(50, 3)))
ev_nom = np.array([np.linalg.norm(model(phi_nom, t) - model(phi_true, t)) for t in THv]) * 1000
ev_cal = np.array([np.linalg.norm(model(phat, t) - model(phi_true, t)) for t in THv]) * 1000
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.2), gridspec_kw=dict(width_ratios=[1, 1.2]))
clean(a1)
for t in TH:
    draw_arm(a1, arm_points(t, L3R), BLUE, lw=1.6, alpha=0.45, base=False, joint=False)
    a1.plot(*model(phi_true, t), "o", color=C["x"], ms=3.5, zorder=7)
draw_arm(a1, arm_points(np.zeros(3), L3R)[:1], C["ink"], lw=1, joint=False)
a1.text(-0.9, -0.98, T("12 个测量形态；红点：激光跟踪仪测得的末端", "12 measuring postures; red dots: tips measured by a laser tracker"), fontsize=8.5)
a1.set_xlim(-0.95, 0.95)
a1.set_ylim(-0.92, 0.95)
idx = np.arange(1, 51)
a2.bar(idx - 0.2, ev_nom, width=0.4, color=GREY, label=T("用名义参数", "nominal parameters"))
a2.bar(idx + 0.2, ev_cal, width=0.4, color=C["accent"], label=T("用标定后的参数", "calibrated parameters"))
a2.set_yscale("log")
a2.set_ylim(5e-4, 20)
a2.set_xlabel(T("检验形态编号", "test posture no."), fontsize=9.5)
a2.set_ylabel(T("末端位置误差 / mm", "tip position error / mm"), fontsize=9.5)
a2.legend(fontsize=8.5, loc="upper right", ncol=2)
a2.grid(alpha=0.3, lw=0.5, axis="y")
a2.tick_params(labelsize=8)
figure(fig, "fig8_5_3")
plt.close(fig)
