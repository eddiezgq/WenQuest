"""图 21.7.1：(a) 三连杆平面机械臂：腕部几乎折回的位形 q₀（灰）沿可操作度的梯度在零空间里运动 400 步（每步 0.5°）后的位形（红），
末端不动；(b) 运动过程中的可操作度 w 与最小奇异值 σ₂；(c) 测距传感器标定的梯度下降（最优固定步长）：
原始读数 κ(AᵀA) ≈ 1.6×10⁷，几乎不动；读数除以标准差后 κ 约几十；再去均值，κ = 1，一步收敛。"""
import math

import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

L = np.array([0.40, 0.35, 0.25])


def joints(q):
    c = np.cumsum(q)
    return np.vstack([[0, 0], np.cumsum(np.column_stack([L * np.cos(c), L * np.sin(c)]), axis=0)])


def jac(q):
    c = np.cumsum(q)
    return np.array([[-np.sum(L[j:] * np.sin(c[j:])) for j in range(3)], [np.sum(L[j:] * np.cos(c[j:])) for j in range(3)]])


def manip(q):
    J = jac(q)
    return math.sqrt(np.linalg.det(J @ J.T))


def grad(q, h=1e-6):
    return np.array([(manip(q + h * e) - manip(q - h * e)) / (2 * h) for e in np.eye(3)])


q = np.radians([45.0, 5.0, 170.0])
p0 = joints(q)[-1]
traj, ws, s2 = [q.copy()], [manip(q)], [np.linalg.svd(jac(q), compute_uv=False)[1]]
for _ in range(400):
    J = jac(q)
    Jp = np.linalg.pinv(J)
    g = (np.eye(3) - Jp @ J) @ grad(q)
    dq = g / max(1e-12, np.linalg.norm(g)) * math.radians(0.5)
    dq += Jp @ (p0 - joints(q + dq)[-1] + J @ dq)
    q = q + dq
    traj.append(q.copy()); ws.append(manip(q)); s2.append(np.linalg.svd(jac(q), compute_uv=False)[1])
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.5, 4.3), gridspec_kw={"width_ratios": [1, 1, 1]})
for k in range(0, 401, 50):
    P = joints(traj[k])
    a1.plot(P[:, 0], P[:, 1], "-", color=MUTED, lw=0.7, alpha=0.6)
for k, col, lw in ((0, INK, 2.2), (400, RED, 2.6)):
    P = joints(traj[k])
    a1.plot(P[:, 0], P[:, 1], "o-", color=col, lw=lw, ms=5)
a1.plot(*p0, "*", color=BLUE, ms=14)
a1.set_aspect("equal")
a1.set_xlim(-0.3, 0.75)
a1.set_ylim(-0.25, 0.75)
a1.set_title(T("(a) 零空间运动：末端（★）不动", "(a) Null-space motion: the tip (★) stays put"), fontsize=10)
a1.text(-0.28, 0.62, T("黑：初始（接近奇异）\n红：400 步后", "black: start (near-singular)\nred: after 400 steps"), fontsize=8.5)
st = np.arange(401)
a2.plot(st, ws, color=RED, lw=1.8, label=T("可操作度 w = √det(JJᵀ)", "manipulability w = √det(JJᵀ)"))
a2.plot(st, s2, color=BLUE, lw=1.4, label=T("最小奇异值 σ₂(J)", "smallest singular value σ₂(J)"))
a2.set_xlabel(T("步数（每步 0.5°）", "steps (0.5° each)"))
a2.legend(frameon=False, fontsize=8.5)
a2.set_title(T("(b) 沿 ∇w 的零空间运动远离奇异位形", "(b) Following ∇w in the null space"), fontsize=10)
d = np.linspace(0.3, 3.0, 12)
r = (d - 0.031) / 0.00098 + np.random.default_rng(7).normal(0, 4.0, d.size)
cases = ((T("原始读数 r", "raw readings r"), r, RED), (T("r / 标准差", "r / std"), r / r.std(), GREEN),
         (T("(r − 均值) / 标准差", "(r − mean) / std"), (r - r.mean()) / r.std(), BLUE))
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def kfmt(k):
    if k < 1000:
        return f"{k:.3g}"
    e = int(math.floor(math.log10(k)))
    return f"{k / 10 ** e:.1f}×10" + str(e).translate(SUP)


for name, x, col in cases:
    D = np.column_stack([x, np.ones_like(x)])
    lam = np.linalg.eigvalsh(D.T @ D)
    eta = 1 / (lam[0] + lam[-1])
    th = np.zeros(2)
    fs = np.linalg.lstsq(D, d, rcond=None)[1][0]
    gap = []
    for k in range(60):
        gap.append(max(np.sum((D @ th - d) ** 2) - fs, 1e-16))
        th = th - eta * 2 * D.T @ (D @ th - d)
    a3.semilogy(range(60), gap, color=col, lw=1.8, label=name + T("：", ": ") + "κ = " + kfmt(lam[-1] / lam[0]))
a3.set_xlabel(T("迭代次数", "iterations"))
a3.set_ylabel("f(θ) − f*")
a3.set_ylim(1e-16, 1e2)
a3.legend(frameon=False, fontsize=8.5, loc="center right")
a3.set_title(T("(c) 标定的梯度下降：条件数决定快慢", "(c) Gradient descent for calibration: κ sets the pace"), fontsize=10)
for a in (a2, a3):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig21_7_1")
