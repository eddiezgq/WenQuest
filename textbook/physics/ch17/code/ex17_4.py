"""17.4 节的计算：

算例 17.4.1  竖直上抛：0.50 kg 的球在 t = 0 从地面抛出，t = 2.0 s 时落回地面。比较几条“可能的路径”的作用量
            S = ∫(T − V)dt：一族抛物线 y = A t(2.0 s − t)，以及在真实路径上叠加一个小扰动的路径。哪一条的作用量最小（图 17.4.1）？
算例 17.4.2  用作用量直接求运动：长 1.0 m 的单摆，t = 0 时摆角 0.30 rad，t = 0.80 s 时摆角 −0.20 rad。
            把时间分成 40 段，作用量变成 39 个中间摆角的函数，用计算机求它的极小值；与“打靶法”（解运动方程、调初速度命中终点）
            的结果比较（图 17.4.2）。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 17.4.1
m, Tt = 0.50, 2.0
t = np.linspace(0, Tt, 2001)


def action(y):
    """S = ∫(½mẏ² − mgy)dt，梯形求积；ẏ 用数值微分。"""
    yd = np.gradient(y, t)
    return np.trapezoid(0.5 * m * yd ** 2 - m * g * y, t)


A_true = g / 2
y_true = A_true * t * (Tt - t)
S_true = action(y_true)
S_exact = m * Tt ** 3 / 6 * (A_true ** 2 - g * A_true)           # 抛物线族的作用量可以积出来：S(A) = mT³(A² − gA)/6
assert abs(S_true - S_exact) < 1e-4
As = np.linspace(2.0, 8.0, 61)
S_A = np.array([action(A * t * (Tt - t)) for A in As])
assert As[np.argmin(S_A)] == min(As, key=lambda a: abs(a - A_true))
eps = 0.5
S_pert = action(y_true + eps * np.sin(2 * math.pi * t / Tt))
S_pert2 = action(y_true + eps * np.sin(3 * math.pi * t / Tt))
assert S_pert > S_true and S_pert2 > S_true
out(m=m, Tt=Tt, v0=g * Tt / 2, ymax=A_true * (Tt / 2) ** 2, S_true=S_true, S_A3=action(3.0 * t * (Tt - t)),
    S_A7=action(7.0 * t * (Tt - t)), S_pert=S_pert, S_pert2=S_pert2)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.9))
for A, col, lw in [(3.0, d.MUTED, 1.2), (7.0, d.MUTED, 1.2)]:
    a1.plot(t, A * t * (Tt - t), color=col, lw=lw, ls="--")
a1.plot(t, y_true + eps * np.sin(2 * math.pi * t / Tt), color=d.VB, lw=1.2, ls="-.", label=T("真实路径 + 扰动", "true path + a wiggle"))
a1.plot(t, y_true, color=d.VR, lw=2.2, label=T("真实路径", "true path"))
a1.text(1.0, 7.35, "A = 7", fontsize=8.5, color=d.MUTED, ha="center")
a1.text(1.0, 2.45, "A = 3", fontsize=8.5, color=d.MUTED, ha="center", va="top")
a1.set_xlabel(T("t / s", "t / s")); a1.set_ylabel(T("高度 y / m", "height y / m"))
a1.legend(frameon=False, fontsize=8.5, loc="lower center")
d.spines(a1)
a2.plot(As, S_A, color=d.VA, lw=2)
a2.plot([A_true], [S_true], "o", color=d.VR, ms=6)
a2.annotate(T("真实路径\nA = g/2", "true path\nA = g/2"), (A_true, S_true), xytext=(0, 18), textcoords="offset points", fontsize=8.5, color=d.VR, ha="center")
a2.set_xlabel(T("抛物线的参数 A / (m/s²)", "parabola parameter A / (m/s²)")); a2.set_ylabel(T("作用量 S / (J·s)", "action S / (J·s)"))
d.spines(a2)
fig.tight_layout()
figure(fig, "fig17_4_1")

# ---- 算例 17.4.2：离散的作用量。S ≈ Σ [½ml²((θⱼ₊₁ − θⱼ)/Δt)² − ½(V(θⱼ) + V(θⱼ₊₁))] Δt，V = −mgl cosθ
lp, th0, th1, Tp, N = 1.0, 0.30, -0.20, 0.80, 40
dt = Tp / N
assert Tp < math.pi / math.sqrt(g / lp)                        # 时间短于半个周期，真实路径是作用量的极小值


def S_disc(inner):
    th = np.concatenate([[th0], inner, [th1]])
    kin = 0.5 * lp ** 2 * ((th[1:] - th[:-1]) / dt) ** 2
    pot = -0.5 * g * lp * (np.cos(th[1:]) + np.cos(th[:-1]))
    return np.sum(kin - pot) * dt                                # 取 m = 1 kg，不影响极值的位置


guess = np.linspace(th0, th1, N + 1)[1:-1]                      # 从一条直线（匀速摆过去）出发
res = minimize(S_disc, guess, method="BFGS", options={"gtol": 1e-10})
th_act = np.concatenate([[th0], res.x, [th1]])


def shoot(w0):
    sol = solve_ivp(lambda t_, y: [y[1], -g / lp * math.sin(y[0])], (0, Tp), [th0, w0], rtol=1e-11, atol=1e-12, dense_output=True)
    return sol


w_hit = brentq(lambda w0: shoot(w0).y[0, -1] - th1, -5, 5, xtol=1e-12)
tt = np.linspace(0, Tp, N + 1)
th_shoot = shoot(w_hit).sol(tt)[0]
err = np.max(np.abs(th_act - th_shoot))
assert err < 2e-3
out(lp=lp, th0=th0, th1=th1, Tp=Tp, N=N, w_hit=w_hit, err_mrad=err * 1000, S_line=S_disc(guess), S_min=res.fun)

fig, ax = plt.subplots(figsize=(4.8, 2.9))
tf = np.linspace(0, Tp, 400)
ax.plot(tf, shoot(w_hit).sol(tf)[0], color=d.VR, lw=2, label=T("打靶法（解运动方程）", "shooting (solve the equation of motion)"))
ax.plot(tt, th_act, "o", color=d.VA, ms=3.5, label=T("作用量取极小（40 段）", "minimum of the action (40 steps)"))
ax.plot(tt, np.linspace(th0, th1, N + 1), color=d.MUTED, lw=1, ls="--", label=T("出发时猜的路径", "initial guess"))
ax.set_xlabel(T("t / s", "t / s")); ax.set_ylabel(T("摆角 θ / rad", "angle θ / rad"))
ax.legend(frameon=False, fontsize=8.5, loc="lower left")
d.spines(ax)
figure(fig, "fig17_4_2")
