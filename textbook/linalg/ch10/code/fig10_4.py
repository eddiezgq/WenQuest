"""图 10.4.1：工具中心点（TCP）的定点转动标定（侧视示意）。工具尖端顶住同一个固定点 q，机器人换几个姿态；
每个姿态下法兰位置 p_i 与姿态 R_i 已知，满足 R_i t + p_i = q，t 是尖端在法兰坐标系中的位置。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, ax = plt.subplots(figsize=(6.8, 4.6))
q = np.array([0.0, 0.0])
Lt = 1.8
cols = [BLUE, GREEN, RED, ACC]
for k, ang in enumerate((-35, -12, 12, 35)):
    d = np.array([np.sin(np.radians(ang)), np.cos(np.radians(ang))])
    p = q + Lt * d
    ax.plot(*np.c_[q, p], color=cols[k], lw=3, solid_capstyle="round")
    nrm = np.array([d[1], -d[0]])
    ax.plot(*np.c_[p - 0.35 * nrm, p + 0.35 * nrm], color=cols[k], lw=6, solid_capstyle="butt")
    ax.plot(*p, "o", color=INK, ms=4, zorder=5)
    ax.text(*(p + 0.25 * d + np.array([-0.1, 0.0])), f"p{'₁₂₃₄'[k]}", fontsize=12, color=cols[k], ha="center")
ax.fill([-1.6, 1.6, 1.6, -1.6], [-0.05, -0.05, -0.45, -0.45], color=MUTED, alpha=0.4)
ax.plot(*q, "o", color=INK, ms=7, zorder=6)
ax.text(0.12, -0.35, "q", fontsize=13, color=INK)
ax.annotate("", xy=q + 0.05 * np.array([np.sin(np.radians(12)), np.cos(np.radians(12))]),
            xytext=q + Lt * np.array([np.sin(np.radians(12)), np.cos(np.radians(12))]),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2, mutation_scale=12, linestyle="--"))
ax.text(0.6, 1.0, "R₃ t", fontsize=12, color=INK)
ax.set_aspect("equal"); ax.set_xlim(-1.8, 1.8); ax.set_ylim(-0.6, 2.4); ax.axis("off")
ax.set_title(T("工具尖端顶住固定点 q，换姿态：R_i t + p_i = q", "tool tip held at a fixed point q in several poses: R_i t + p_i = q"), fontsize=11)
figure(fig, "fig10_4_1")
