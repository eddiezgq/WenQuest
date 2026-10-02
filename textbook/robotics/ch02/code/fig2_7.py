"""2.7 节的示意图。

图 2.7.1：格拉姆-施密特法的三步：① 第一个向量归一化得 e1；② 第二个向量减去它在 e1 上的投影，剩下的部分 w2 垂直于 e1；
         ③ w2 归一化得 e2。
图 2.7.2：三点法示教工件坐标系（示意，示教误差放大画出）：p0 为原点，p1 定 x 方向，p2 定 xy 平面；
         示教出的两个方向不垂直，正交化后得到坐标系 {u}。
"""
import math

import numpy as np

from _la import C, arrow
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 2.7.1
a1 = np.array([2.2, 0.5])
a2 = np.array([1.1, 1.7])
e1 = a1 / np.linalg.norm(a1)
pr = (e1 @ a2) * e1
w2 = a2 - pr
e2 = w2 / np.linalg.norm(w2)
fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.4))
titles = [T("① 归一化第一个向量", "① normalise the first vector"), T("② 减去投影：w₂ = a₂ − (q₁·a₂) q₁", "② w₂ = a₂ − (q₁·a₂) q₁"),
          T("③ 归一化 w₂：q₁ ⟂ q₂，长度都是 1", "③ normalise w₂: q₁ ⟂ q₂")]
for k, ax in enumerate(axs):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-0.4, 2.6)
    ax.set_ylim(-0.6, 2.0)
    t = np.linspace(0, 2 * math.pi, 100)
    ax.plot(np.cos(t), np.sin(t), color="#dde2e6", lw=0.8)
    ax.text(-0.4, -0.55, titles[k].replace("⟂", "⊥"), fontsize=9.5)
    if k == 0:
        arrow(ax, (0, 0), a1, C["muted"], 1.6)
        arrow(ax, (0, 0), a2, C["muted"], 1.6)
        arrow(ax, (0, 0), e1, C["x"], 2.4)
        ax.text(a1[0] - 0.1, a1[1] + 0.1, "$a_1$", fontsize=12, color=C["muted"])
        ax.text(a2[0] + 0.05, a2[1] + 0.02, "$a_2$", fontsize=12, color=C["muted"])
        ax.text(e1[0] - 0.05, e1[1] - 0.25, "$q_1$", fontsize=12, color=C["x"])
    if k == 1:
        ax.plot([-0.2 * e1[0], 2.4 * e1[0]], [-0.2 * e1[1], 2.4 * e1[1]], color="#e4b9b9", lw=0.8)
        arrow(ax, (0, 0), e1, C["x"], 2.4)
        arrow(ax, (0, 0), a2, C["muted"], 1.6)
        arrow(ax, (0, 0), pr, C["accent"], 1.8)
        arrow(ax, pr, a2, C["y"], 2.0)
        arrow(ax, (0, 0), w2, C["y"], 1.0)
        ax.plot([w2[0], a2[0]], [w2[1], a2[1]], color=C["muted"], lw=0.8, ls=":")
        ax.text(a2[0] + 0.05, a2[1] + 0.02, "$a_2$", fontsize=12, color=C["muted"])
        ax.text(pr[0] - 0.05, pr[1] - 0.3, r"$(q_1\!\cdot a_2)\,q_1$", fontsize=11, color=C["accent"])
        ax.text((pr[0] + a2[0]) / 2 + 0.08, (pr[1] + a2[1]) / 2, "$w_2$", fontsize=12, color=C["y"])
        ax.text(e1[0] - 0.1, e1[1] - 0.28, "$q_1$", fontsize=12, color=C["x"])
        u, v = e1, e2
        sq = np.array([pr + 0.12 * u, pr + 0.12 * u + 0.12 * v, pr + 0.12 * v])
        ax.plot(sq[:, 0], sq[:, 1], color=C["ink"], lw=0.8)
    if k == 2:
        arrow(ax, (0, 0), e1, C["x"], 2.4)
        arrow(ax, (0, 0), e2, C["y"], 2.4)
        ax.text(e1[0] + 0.05, e1[1] - 0.15, "$q_1$", fontsize=12, color=C["x"])
        ax.text(e2[0] - 0.3, e2[1] + 0.02, "$q_2$", fontsize=12, color=C["y"])
        sq = np.array([0.15 * e1, 0.15 * e1 + 0.15 * e2, 0.15 * e2])
        ax.plot(sq[:, 0], sq[:, 1], color=C["ink"], lw=0.8)
figure(fig, "fig2_7_1")
plt.close(fig)


# ---------------------------------------------------------------- 图 2.7.2
def P3(v):
    x, y, z = v
    return np.array([x + 0.45 * y, 0.35 * y + z])


fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.set_aspect("equal")
ax.axis("off")
table = np.array([P3(v) for v in ([-0.2, -0.2, 0], [1.6, -0.2, 0], [1.6, 1.4, 0], [-0.2, 1.4, 0], [-0.2, -0.2, 0])])
ax.fill(table[:, 0], table[:, 1], color="#ece4d4")
ax.plot(table[:, 0], table[:, 1], color=C["muted"], lw=0.8)
p0 = np.array([0.0, 0.0, 0.0])
p1 = np.array([1.3, 0.12, 0.0])                 # 误差放大画出
p2 = np.array([0.18, 1.15, 0.0])
for p, lab, off in ((p0, "$p_0$", (-0.18, -0.1)), (p1, "$p_1$", (0.05, -0.12)), (p2, "$p_2$", (-0.2, 0.05))):
    ax.plot(*P3(p), "o", color=C["ink"], ms=5, zorder=6)
    ax.text(*(P3(p) + np.array(off)), lab, fontsize=12)
ax.plot(*np.array([P3(p0), P3(p1)]).T, color=C["muted"], lw=1.0, ls="--")
ax.plot(*np.array([P3(p0), P3(p2)]).T, color=C["muted"], lw=1.0, ls="--")
ax.text(*(P3((p0 + p1) / 2) + np.array([-0.1, -0.15])), "$a_1$", fontsize=11, color=C["muted"])
ax.text(*(P3((p0 + p2) / 2) + np.array([0.12, -0.08])), "$a_2$", fontsize=11, color=C["muted"])
a1, a2 = p1 - p0, p2 - p0
e1 = a1 / np.linalg.norm(a1)
w2 = a2 - (e1 @ a2) * e1
e2 = w2 / np.linalg.norm(w2)
e3 = np.cross(e1, e2)
L = 0.75
for e, col, lab in ((e1, C["x"], "$x_u$"), (e2, C["y"], "$y_u$"), (e3, C["z"], "$z_u$")):
    arrow(ax, P3(p0), P3(L * e), col, 2.2, z=7)
    ax.text(*(P3(1.08 * L * e) + np.array([-0.05, 0.07])), lab, fontsize=12, color=col)
ax.text(-0.35, -0.42, T("虚线：示教出的两个方向（误差放大画出）；彩色：正交化后的工件坐标系 {u}",
                        "dashed: the two taught directions (errors exaggerated); colour: the work frame {u} after orthonormalisation"),
        fontsize=9, color=C["ink"])
ax.set_xlim(-0.4, 2.3)
ax.set_ylim(-0.48, 1.1)
figure(fig, "fig2_7_2")
plt.close(fig)
