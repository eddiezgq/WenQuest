"""图 1.2.1：差速 AGV 的同一个矩阵——行图（两条直线的交点）、列图（两列的组合）、几何变换（单位正方形变成平行四边形）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

r, b = 0.075, 0.40
A = np.array([[r / 2, r / 2], [-r / b, r / b]])
want = np.array([0.5, 0.5])
sol = np.linalg.solve(A, want)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.0, 4.3))
x = np.linspace(0, 12, 2)
a1.plot(x, (want[0] - A[0, 0] * x) / A[0, 1], color=BLUE, label=T("v = 0.5 m/s", "v = 0.5 m/s"))
a1.plot(x, (want[1] - A[1, 0] * x) / A[1, 1], color=RED, label=T("ω = 0.5 rad/s", "ω = 0.5 rad/s"))
a1.plot(*sol, "o", color=INK)
a1.annotate(T(f"解 ({sol[0]:.2f}, {sol[1]:.0f})", f"solution ({sol[0]:.2f}, {sol[1]:.0f})"), sol, (sol[0] + 0.6, sol[1] - 2.2), fontsize=10)
a1.set_xlim(0, 12)
a1.set_ylim(0, 16)
a1.set_xlabel(r"$\omega_L$ / (rad/s)")
a1.set_ylabel(r"$\omega_R$ / (rad/s)")
a1.legend(frameon=False, loc="upper right")
a1.set_title(T("① 行图：每个方程一条直线", "① Row picture: one line per equation"), fontsize=11)
c1, c2 = A[:, 0] * sol[0], A[:, 1] * sol[1]
arrow(a2, c1, BLUE, T(r"$\omega_L\,\boldsymbol{a}_1$", r"$\omega_L\,\boldsymbol{a}_1$"), (0.02, -0.15))
arrow(a2, c2, GREEN, None, start=c1)
a2.text(c1[0] + c2[0] / 2 + 0.04, c1[1] + c2[1] / 2, r"$\omega_R\,\boldsymbol{a}_2$", color=GREEN, fontsize=12)
arrow(a2, want, RED, None, lw=1.4)
a2.text(0.02, 0.68, T("(v, ω) = (0.5, 0.5)", "(v, ω) = (0.5, 0.5)"), color=RED, fontsize=11)
a2.set_xlim(-0.1, 0.8)
a2.set_ylim(-1.2, 1.2)
a2.axhline(0, color=MUTED, lw=0.6)
a2.axvline(0, color=MUTED, lw=0.6)
a2.set_xlabel("v / (m/s)")
a2.set_ylabel("ω / (rad/s)")
a2.set_title(T("② 列图：两列的线性组合", "② Column picture: a combination of the columns"), fontsize=11)
sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]).T * 4
P = A @ sq
a3.fill(P[0], P[1], color=ACC, alpha=0.3)
a3.plot(P[0], P[1], color=INK)
arrow(a3, A @ [4, 0], BLUE, T("左轮 4 rad/s", "left 4 rad/s"), (0.0, -0.18))
arrow(a3, A @ [0, 4], GREEN, T("右轮 4 rad/s", "right 4 rad/s"), (0.0, 0.08))
a3.set_xlim(-0.1, 0.4)
a3.set_ylim(-1.0, 1.0)
a3.axhline(0, color=MUTED, lw=0.6)
a3.axvline(0, color=MUTED, lw=0.6)
a3.set_xlabel("v / (m/s)")
a3.set_ylabel("ω / (rad/s)")
a3.set_title(T("③ 几何变换：轮速正方形变成平行四边形", "③ A map: the wheel-speed square becomes a parallelogram"), fontsize=11)
for ax in (a1, a2, a3):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_2_1")

# 图 1.2.2：三个矩阵对平面网格的作用——伸缩、旋转、剪切
import math

mats = [(np.array([[2.0, 0.0], [0.0, 0.5]]), T("伸缩 diag(2, 0.5)", "stretch diag(2, 0.5)")),
        (np.array([[math.cos(math.pi / 6), -math.sin(math.pi / 6)], [math.sin(math.pi / 6), math.cos(math.pi / 6)]]), T("旋转 30°", "rotation by 30°")),
        (np.array([[1.0, 1.0], [0.0, 1.0]]), T("剪切 [[1, 1], [0, 1]]", "shear [[1, 1], [0, 1]]"))]
fig, axs = plt.subplots(1, 3, figsize=(11.0, 4.0))
for ax, (M, name) in zip(axs, mats):
    for i in range(-3, 4):
        for P, Q in (([i, -3], [i, 3]), ([-3, i], [3, i])):
            ax.plot([P[0], Q[0]], [P[1], Q[1]], color=MUTED, lw=0.5, alpha=0.35)
            p, q = M @ P, M @ Q
            ax.plot([p[0], q[0]], [p[1], q[1]], color=BLUE, lw=0.9 if i else 1.6, alpha=0.8)
    sq = M @ np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]])
    ax.fill(sq[0], sq[1], color=ACC, alpha=0.45)
    arrow(ax, M @ [1, 0], RED, None)
    arrow(ax, M @ [0, 1], GREEN, None)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(name, fontsize=11)
fig.tight_layout()
figure(fig, "fig1_2_2")
