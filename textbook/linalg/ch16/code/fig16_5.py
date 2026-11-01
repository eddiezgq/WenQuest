"""图 16.5.1：反对称矩阵的指数是旋转（程序 16.5.1）。(a) p(t) = e^{[ω]×t}p₀ 绕 ω 画出一个圆锥，长度不变；
(b) 陀螺仪姿态积分 60 s：欧拉法 R(I + [ω]×Δt) 的正交性误差 ‖RᵀR − I‖ 不断增大，指数法 R e^{[ω]×Δt} 始终在舍入误差的量级。"""
import math

import numpy as np
import scipy.linalg as sl

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow3, figure, plt, view3


def hat(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.4), gridspec_kw={"width_ratios": [1, 1.2]})
P, _ = view3(35, 20)
wv = np.array([1.0, 2, 2]) / 3
p0 = np.array([1.0, 0, 0])
for e, lab in zip(np.eye(3), "xyz"):
    arrow3(a1, P, [0, 0, 0], 1.2 * e, MUTED, lab, lw=1)
arrow3(a1, P, [0, 0, 0], 1.4 * wv, ACC, "ω", lw=2.4)
ts = np.linspace(0, 2 * math.pi, 200)
C = np.array([P(sl.expm(hat(wv) * t) @ p0) for t in ts])
a1.plot(C[:, 0], C[:, 1], color=BLUE, lw=1.6)
for t in (0, 1.0, 2.0):
    q = sl.expm(hat(wv) * t) @ p0
    arrow3(a1, P, [0, 0, 0], q, BLUE, f"p({t:g})", lw=1.8, size=10)
cen = (wv @ p0) * wv
a1.plot(*np.array([P(cen), P(p0)]).T, color=MUTED, lw=0.8, ls=":")
a1.set_aspect("equal"); a1.axis("off")
a1.set_title(T("(a) p(t) = exp([ω]×t)p₀ 绕 ω 转动", "(a) p(t) = exp([ω]×t)p₀ turns about ω"), fontsize=11, pad=16)
w = np.array([0.3, -0.5, 1.2]); dt = 0.01
Re, Rx = np.eye(3), np.eye(3)
Ee, Ex = np.eye(3) + hat(w) * dt, sl.expm(hat(w) * dt)
tt, oe, ox = [], [], []
for k in range(1, 6001):
    Re, Rx = Re @ Ee, Rx @ Ex
    if k % 20 == 0:
        tt.append(k * dt); oe.append(np.abs(Re.T @ Re - np.eye(3)).max()); ox.append(np.abs(Rx.T @ Rx - np.eye(3)).max() + 1e-17)
a2.semilogy(tt, oe, color=RED, lw=2, label=T("欧拉法 R(I + [ω]×Δt)", "Euler R(I + [ω]×Δt)"))
a2.semilogy(tt, ox, color=BLUE, lw=2, label=T("指数法 R exp([ω]×Δt)", "exponential R exp([ω]×Δt)"))
a2.set_xlabel(T("t / s", "t / s")); a2.set_ylabel(T("正交性误差 max|RᵀR − I|", "orthogonality error max|RᵀR − I|"))
a2.legend(frameon=False, fontsize=9, loc="center right")
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 姿态积分 60 s，Δt = 0.01 s", "(b) Attitude integration, 60 s, Δt = 0.01 s"), fontsize=11)
fig.tight_layout()
figure(fig, "fig16_5_1")
