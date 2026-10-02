"""图 18.3.1：奇异值分解给出四个基本子空间的标准正交基；图 18.3.2：检测数据矩阵的奇异值与数值秩。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from matplotlib.patches import FancyArrowPatch, Polygon

fig, ax = plt.subplots(figsize=(10, 5.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.6)
ax.axis("off")


def box(cx, cy, w, h, ang, color, text, sub):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    P = np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]]) @ np.array([[c, s], [-s, c]]) + [cx, cy]
    ax.add_patch(Polygon(P, closed=True, fc=color, ec=INK, alpha=0.18, lw=1.2))
    ax.add_patch(Polygon(P, closed=True, fill=False, ec=INK, lw=1.2))
    ax.text(cx, cy + 0.15, text, ha="center", va="center", fontsize=12, color=INK)
    ax.text(cx, cy - 0.32, sub, ha="center", va="center", fontsize=10.5, color=MUTED)


box(2.0, 3.85, 2.9, 1.9, 0, BLUE, T("行空间 C(Aᵀ)", "row space C(Aᵀ)"), r"$\boldsymbol{v}_1,\dots,\boldsymbol{v}_r$  " + T("（r 维）", "(dim r)"))
box(2.0, 1.45, 2.9, 1.6, 0, GREEN, T("零空间 N(A)", "null space N(A)"), r"$\boldsymbol{v}_{r+1},\dots,\boldsymbol{v}_n$  " + T("（n − r 维）", "(dim n − r)"))
box(8.0, 3.85, 2.9, 1.9, 0, RED, T("列空间 C(A)", "column space C(A)"), r"$\boldsymbol{u}_1,\dots,\boldsymbol{u}_r$  " + T("（r 维）", "(dim r)"))
box(8.0, 1.45, 2.9, 1.6, 0, ACC, T("左零空间 N(Aᵀ)", "left null space N(Aᵀ)"), r"$\boldsymbol{u}_{r+1},\dots,\boldsymbol{u}_m$  " + T("（m − r 维）", "(dim m − r)"))
ax.text(2.0, 5.35, r"$\mathbb{R}^n$", ha="center", fontsize=15)
ax.text(8.0, 5.35, r"$\mathbb{R}^m$", ha="center", fontsize=15)
ax.text(2.0, 2.62, "⊥", ha="center", fontsize=16, color=INK)
ax.text(8.0, 2.62, "⊥", ha="center", fontsize=16, color=INK)
ax.add_patch(FancyArrowPatch((3.55, 3.95), (6.45, 3.95), arrowstyle="-|>", mutation_scale=18, lw=2, color=INK))
ax.text(5.0, 4.2, r"$A\boldsymbol{v}_i=\sigma_i\boldsymbol{u}_i\ (i\leq r)$", ha="center", fontsize=12)
ax.add_patch(FancyArrowPatch((3.55, 1.45), (6.2, 2.75), arrowstyle="-|>", mutation_scale=18, lw=1.6, color=MUTED, ls="--"))
ax.text(5.15, 1.75, r"$A\boldsymbol{v}_i=\boldsymbol{0}\ (i>r)$", ha="center", fontsize=12, color=MUTED)
ax.plot([6.2], [2.75], "o", color=INK)
ax.text(6.3, 2.62, r"$\boldsymbol{0}$", fontsize=12)
figure(fig, "fig18_3_1")

# 图 18.3.2
import ex18_3_data as d  # noqa: E402

fig, ax = plt.subplots(figsize=(6.4, 3.6))
x = np.arange(1, 4)
ax.bar(x - 0.18, d.s_exact, width=0.34, color=BLUE, label=T("无测量误差", "exact data"))
ax.bar(x + 0.18, d.s_meas, width=0.34, color=RED, label=T("含测量误差", "with gauge error"))
ax.axhline(d.tol, color=ACC, lw=1.5, ls="--")
ax.text(1.75, d.tol * 1.6, T("阈值 δ(√m+√n)", "threshold δ(√m+√n)"), color=ACC, ha="center", fontsize=10)
ax.set_yscale("log")
ax.set_xticks(x, [r"$\sigma_1$", r"$\sigma_2$", r"$\sigma_3$"])
ax.set_ylabel(T("奇异值 / mm", "singular value / mm"))
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.02, 0.02))
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig18_3_2")
