"""25.3 节的示意图。

图 25.3.1：书中 UR5e（n = 6）在算例 25.1.1 的姿态下，把各连杆的量排成长矢量后几个矩阵的非零元素分布：
          (a) 𝒲（只有次对角线上的块 [Ad_{T_{i,i−1}}]）；(b) ℒ = (I − 𝒲)⁻¹（块下三角，(i, j) 块是 [Ad_{T_ij}]）；
          (c) ℒ𝒜（6n × n，第 i 个块行是连杆 i 的物体雅可比 J_i）。
"""
import numpy as np

from _ch25 import cell_move, quintic, ur_chain
from bookout import COLORS as C, T, figure, style

plt = style()
ch = ur_chain()
thA, thB, T_move = cell_move()
q, qd, _ = quintic(thA, thB, T_move, 0.40)
A, G, W, L = ch.stacked(q, qd)
LA = L @ A
fig, axs = plt.subplots(1, 3, figsize=(11.2, 4.6), gridspec_kw=dict(width_ratios=[36, 36, 14]))
for ax, Mx, title in ((axs[0], W, T(r"(a) $\mathcal{W}$（36×36）", r"(a) $\mathcal{W}$ (36×36)")), (axs[1], L, r"(b) $\mathcal{L} = (I - \mathcal{W})^{-1}$"),
                      (axs[2], LA, T(r"(c) $\mathcal{L}\mathcal{A}$（36×6）", r"(c) $\mathcal{L}\mathcal{A}$ (36×6)"))):
    nz = np.abs(Mx) > 1e-12
    ax.imshow(np.where(nz, 1.0, 0.0), cmap="Blues", vmin=0, vmax=1.4, interpolation="nearest", aspect="equal")
    r, c = Mx.shape
    for k in range(0, r + 1, 6):
        ax.axhline(k - 0.5, color=C["muted"], lw=0.5)
    for k in range(0, c + 1, 6 if c > 6 else 1):
        ax.axvline(k - 0.5, color=C["muted"], lw=0.5)
    ax.set_xticks([])
    ax.set_yticks([6 * i + 2.5 for i in range(6)])
    ax.set_yticklabels([str(i + 1) for i in range(6)], fontsize=9)
    if c > 6:
        ax.set_xticks([6 * i + 2.5 for i in range(6)])
        ax.set_xticklabels([str(i + 1) for i in range(6)], fontsize=9)
    else:
        ax.set_xticks(range(6))
        ax.set_xticklabels([str(i + 1) for i in range(6)], fontsize=9)
    ax.set_title(title, fontsize=11)
axs[2].set_xlabel(T("关节", "joint"), fontsize=10)
axs[0].set_ylabel(T("连杆（块行）", "link (block row)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig25_3_1")
