"""10.7 节的示意图。

图 10.7.1：为什么是 6：(a) 定 A 要 3 个数；(b) A 定后，B 在以 A 为心、半径 |AB| 的球面上，要 2 个数；
           (c) A、B 都定后，C 在绕直线 AB 的圆上，要 1 个数。3 + 2 + 1 = 6。
图 10.7.2：刚体的速度场（俯视，ω 沿 z 轴）：v_B = v_A + ω × r_AB；两点速度在连线方向上的投影相等。
"""
import math

import numpy as np

from _kin import AXIS, C, G_COL, V_COL, arrow, oblique
from bookout import T, figure, style

plt = style()

A = np.array([0.0, 0.0, 0.0])
B = np.array([0.0, 1.0, 0.35])
Cp = np.array([0.0, 0.25, 0.95])
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.9))
titles = [T("(a) 定 A：3 个数", "(a) Fix A: 3 numbers"), T("(b) 再定 B：2 个数", "(b) Then B: 2 numbers"),
          T("(c) 再定 C：1 个数", "(c) Then C: 1 number")]
for k, ax in enumerate(axs):
    ax.set_aspect("equal")
    ax.axis("off")
    O = np.array([-0.9, -0.9, -0.6])
    for i in range(3):
        e = np.zeros(3)
        e[i] = 0.4
        arrow(ax, oblique(O), oblique(O + e), AXIS[i], 0.9)
    pa = oblique(A)
    if k == 0:
        for i in range(3):
            e = np.zeros(3)
            e[i] = A[i] - O[i]
            q0 = O + np.array([A[0] - O[0] if i > 0 else 0, A[1] - O[1] if i > 1 else 0, 0])
        ax.plot(*np.array([oblique(O), oblique([A[0], O[1], O[2]]), oblique([A[0], A[1], O[2]]), oblique(A)]).T, color=G_COL, lw=0.8, ls=":")
        ax.text(*(pa + np.array([0.08, 0.05])), "A", fontsize=12)
        ax.text(-1.2, -1.15, T("A 的坐标 (x, y, z)", "coordinates (x, y, z) of A"), fontsize=9.5)
    if k >= 1:
        rr = np.linalg.norm(B - A)
        ax.add_patch(plt.Circle(pa, rr * 1.0, fill=False, color=C["accent"], lw=1.0, ls="--"))
        u = np.linspace(0, 2 * math.pi, 100)
        eq = np.array([oblique(A + rr * np.array([math.cos(t), math.sin(t), 0])) for t in u])
        ax.plot(eq[:, 0], eq[:, 1], color=C["accent"], lw=0.7, ls=":")
        ax.plot(*np.array([pa, oblique(B)]).T, color=C["ink"], lw=1.2)
        ax.plot(*oblique(B), "o", color=C["ink"], ms=5)
        ax.text(*(oblique(B) + np.array([0.06, 0.03])), "B", fontsize=12)
        ax.text(*(pa + np.array([-0.2, 0.06])), "A", fontsize=12)
        if k == 1:
            ax.text(-1.2, -1.15, T("B 在以 A 为心、半径 |AB| 的球面上", "B lies on the sphere about A of radius |AB|"), fontsize=9.5)
    if k == 2:
        u_ab = (B - A) / np.linalg.norm(B - A)
        foot = A + ((Cp - A) @ u_ab) * u_ab
        rc = np.linalg.norm(Cp - foot)
        e1 = (Cp - foot) / rc
        e2 = np.cross(u_ab, e1)
        circ = np.array([oblique(foot + rc * (math.cos(t) * e1 + math.sin(t) * e2)) for t in np.linspace(0, 2 * math.pi, 120)])
        ax.plot(circ[:, 0], circ[:, 1], color=C["z"], lw=1.2, ls="--")
        ax.plot(*np.array([oblique(A - 0.4 * u_ab), oblique(B + 0.4 * u_ab)]).T, color=G_COL, lw=0.8, ls="-.")
        ax.plot(*np.array([oblique(foot), oblique(Cp)]).T, color=G_COL, lw=0.8)
        tri = np.array([pa, oblique(B), oblique(Cp), pa])
        ax.fill(tri[:, 0], tri[:, 1], color=C["z"], alpha=0.15)
        ax.plot(tri[:, 0], tri[:, 1], color=C["ink"], lw=1.2)
        ax.plot(*oblique(Cp), "o", color=C["ink"], ms=5)
        ax.text(*(oblique(Cp) + np.array([0.06, 0.03])), "C", fontsize=12)
        ax.text(-1.2, -1.15, T("C 在绕直线 AB 的圆上：只剩一个转角", "C lies on a circle about line AB: one angle left"), fontsize=9.5)
    ax.plot(*pa, "o", color=C["ink"], ms=5, zorder=6)
    ax.set_title(titles[k], fontsize=11)
    ax.set_xlim(-1.25, 1.45)
    ax.set_ylim(-1.25, 1.4)
fig.text(0.5, 0.01, T("刚体在空间中的位置由 3 + 2 + 1 = 6 个数确定", "A rigid body in space is fixed by 3 + 2 + 1 = 6 numbers"), ha="center", fontsize=10.5)
fig.tight_layout(rect=(0, 0.05, 1, 1))
figure(fig, "fig10_7_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.7.2
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.set_aspect("equal")
ax.axis("off")
plate = np.array([[-0.3, -0.25], [1.4, -0.25], [1.4, 0.9], [-0.3, 0.9], [-0.3, -0.25]])
ax.fill(plate[:, 0], plate[:, 1], color="#e9edf0")
ax.plot(plate[:, 0], plate[:, 1], color=G_COL, lw=0.8)
Ap, Bp, Cq = np.array([0.0, 0.0]), np.array([1.0, 0.1]), np.array([0.3, 0.7])
w = 0.6
vA = np.array([0.45, 0.25])
vel = lambda P: vA + w * np.array([-(P - Ap)[1], (P - Ap)[0]])
k = 1.0
for P, lab in ((Ap, "A"), (Bp, "B"), (Cq, "C")):
    ax.plot(*P, "o", color=C["ink"], ms=5, zorder=6)
    ax.text(*(P + np.array([-0.1, -0.12])), lab, fontsize=12)
    arrow(ax, P, P + k * vel(P), V_COL, 1.8)
ax.text(*(Ap + k * vA + np.array([0.02, 0.02])), "$v_A$", color=V_COL, fontsize=11)
arrow(ax, Bp, Bp + k * vA, G_COL, 1.0, ls="--")
wr = vel(Bp) - vA
arrow(ax, Bp + k * vA, Bp + k * vel(Bp), C["y"], 1.2, ls="--")
ax.text(*(Bp + k * vA + np.array([0.04, -0.06])), "$v_A$", color=G_COL, fontsize=10)
ax.text(*(Bp + k * (vA + wr / 2) + np.array([0.04, 0.0])), r"$\omega\times r_{AB}$", color=C["y"], fontsize=10)
ax.text(*(Bp + k * vel(Bp) + np.array([0.02, 0.03])), "$v_B$", color=V_COL, fontsize=11)
ax.text(*(Cq + k * vel(Cq) + np.array([-0.12, 0.04])), "$v_C$", color=V_COL, fontsize=11)
ax.plot(*np.array([Ap, Bp]).T, color=C["ink"], lw=0.8, ls=":")
u = (Bp - Ap) / np.linalg.norm(Bp - Ap)
for P in (Ap, Bp):
    pr = (vel(P) @ u) * u
    ax.plot(*np.array([P + k * vel(P), P + k * pr]).T, color=C["x"], lw=0.7, ls=":")
    ax.plot(*np.array([P, P + k * pr]).T, color=C["x"], lw=2.5, alpha=0.6)
ax.text(-0.3, -0.45, T(r"粗红线：$v_A$、$v_B$ 在 AB 方向上的投影，二者相等", r"thick red: projections of $v_A$ and $v_B$ on AB, which are equal"), fontsize=9)
ax.text(-0.3, 1.0, T(r"$\omega$ 垂直纸面向外", r"$\omega$ points out of the page"), fontsize=9)
ax.set_xlim(-0.45, 2.1)
ax.set_ylim(-0.55, 1.65)
figure(fig, "fig10_7_2")
plt.close(fig)
