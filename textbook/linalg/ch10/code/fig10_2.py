"""图 10.2.1：线性代数基本定理的全景图（正交版）。左：ℝⁿ 中行空间与零空间互为正交补，x = x_r + x_n；右：ℝᵐ 中列空间与左零空间互为正交补。
A 把 x_r 送到 Ax，把 x_n 送到 0；b 不在列空间中时，最小二乘把它分解为 p = A x̂（列空间）与 e（左零空间）。"""
import numpy as np
from matplotlib.patches import FancyArrowPatch

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, ax = plt.subplots(figsize=(10.4, 5.0))
ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-3.2, 12.0); ax.set_ylim(-2.6, 4.2)


def frame(O, ang, c1, c2, n1, n2, L=2.9):
    u = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
    v = np.array([-u[1], u[0]])
    ax.plot(*np.c_[O - L * u, O + L * u], color=c1, lw=5, alpha=0.75, solid_capstyle="round")
    ax.plot(*np.c_[O - 2.2 * v, O + 2.2 * v], color=c2, lw=5, alpha=0.75, solid_capstyle="round")
    m = 0.28
    ax.plot(*np.c_[O + m * u, O + m * u + m * v, O + m * v], color=INK, lw=1.2)
    ax.text(*(O + (L + 0.2) * u), n1, color=c1, fontsize=11, ha="left", va="center")
    ax.text(*(O + 2.35 * v), n2, color=c2, fontsize=11, ha="center", va="bottom")
    ax.plot(*O, "o", color=INK, ms=5, zorder=6)
    return u, v


O1, O2 = np.array([0.6, 0.6]), np.array([8.0, 0.6])
u1, v1 = frame(O1, 30, BLUE, GREEN, T("行空间 C(Aᵀ)", "row space C(Aᵀ)"), T("零空间 N(A)", "null space N(A)"))
u2, v2 = frame(O2, 25, RED, ACC, T("列空间 C(A)", "column space C(A)"), T("左零空间 N(Aᵀ)", "left null space N(Aᵀ)"))
ax.text(O1[0] - 2.6, 3.7, T("ℝⁿ：维数 r 与 n − r", "ℝⁿ: dimensions r and n − r"), fontsize=12)
ax.text(O2[0] - 2.4, 3.7, T("ℝᵐ：维数 r 与 m − r", "ℝᵐ: dimensions r and m − r"), fontsize=12)
xr, xn = 2.0 * u1, 1.1 * v1
for a, b, c in ((O1, O1 + xr, BLUE), (O1, O1 + xn, GREEN), (O1, O1 + xr + xn, INK)):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=c, lw=2, mutation_scale=14), zorder=5)
ax.plot(*np.c_[O1 + xr, O1 + xr + xn, O1 + xn], color=MUTED, lw=1, ls="--")
ax.text(*(O1 + xr + xn + np.array([0.08, 0.1])), "x = x_r + x_n", fontsize=11, color=INK)
ax.text(*(O1 + xr + np.array([0.1, -0.35])), "x_r", fontsize=11, color=BLUE)
ax.text(*(O1 + xn + np.array([-0.55, 0.0])), "x_n", fontsize=11, color=GREEN)
Ax = O2 + 1.0 * u2
p = O2 - 2.0 * u2
b = p + 1.2 * v2
ax.annotate("", xy=Ax, xytext=O2, arrowprops=dict(arrowstyle="-|>", color=RED, lw=2, mutation_scale=14), zorder=5)
ax.text(*(Ax + np.array([0.0, -0.45])), "Ax", fontsize=11, color=RED)
ax.annotate("", xy=p, xytext=O2, arrowprops=dict(arrowstyle="-|>", color=RED, lw=2, mutation_scale=14), zorder=5)
ax.annotate("", xy=b, xytext=O2, arrowprops=dict(arrowstyle="-|>", color=INK, lw=2, mutation_scale=14), zorder=5)
ax.plot(*np.c_[p, b], color=ACC, lw=1.8, ls="--")
ax.text(*(p + np.array([-0.2, -0.5])), "p = Ax̂", fontsize=11, color=RED)
ax.text(*(b + np.array([-0.25, 0.12])), "b", fontsize=12, color=INK)
ax.text(*((p + b) / 2 + np.array([-1.25, 0.0])), "e = b − p", fontsize=11, color=ACC)
ax.add_patch(FancyArrowPatch(O1 + xr + np.array([0.25, 0.05]), Ax + np.array([0.0, 0.2]), arrowstyle="-|>", mutation_scale=16,
                             color=BLUE, lw=1.5, connectionstyle="arc3,rad=-0.35"))
ax.text(5.3, 3.15, "A x_r = A x", color=BLUE, fontsize=12, ha="center")
ax.add_patch(FancyArrowPatch(O1 + xn + np.array([0.1, -0.1]), O2 + np.array([-0.1, -0.1]), arrowstyle="-|>", mutation_scale=16,
                             color=GREEN, lw=1.5, connectionstyle="arc3,rad=0.25"))
ax.text(4.3, -1.25, "A x_n = 0", color=GREEN, fontsize=12, ha="center")
ax.text(4.4, -2.45, T("两对子空间各自垂直（直角记号），而且合起来是整个空间", "each pair is perpendicular (right-angle marks) and together they fill the whole space"),
        fontsize=10, color=MUTED, ha="center")
figure(fig, "fig10_2_1")
