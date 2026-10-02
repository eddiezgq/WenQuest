"""9.3 节的示意图。

图 9.3.1：算例 9.3.1 的自然频数树：1000 个零件中，有缺陷的 10 个、报警的 9.5 个；无缺陷的 990 个、误报 49.5 个。
图 9.3.2：算例 9.3.2 走廊里的 AGV：先验、每次测量和前进之后的概率分布。
图 9.3.3：算例 9.3.3：里程计的先验、激光雷达测量的似然与后验。
"""
import itertools
import math

import numpy as np

from _prob import gauss_pdf
from bookout import COLORS as C, T, figure, style

plt = style()


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


# ---------------------------------------------------------------- 图 9.3.1 自然频数树
fig, ax = plt.subplots(figsize=(7.6, 3.6))
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)


def node(x, y, text, col, w=2.1):
    ax.add_patch(plt.Rectangle((x - w / 2, y - 0.33), w, 0.66, fc="white", ec=col, lw=1.4))
    ax.text(x, y, text, ha="center", va="center", fontsize=9.5, color=col)


def edge(p, q, text, side=1):
    ax.plot([p[0] + 1.05, q[0] - 1.05], [p[1], q[1]], color=C["muted"], lw=1)
    ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.22 * side, text, ha="center", fontsize=8.5, color=C["muted"])


node(1.2, 2.5, T("1000 个零件", "1000 parts"), C["ink"])
node(4.6, 3.9, T("有缺陷 10 个", "defective: 10"), C["x"])
node(4.6, 1.1, T("无缺陷 990 个", "good: 990"), C["z"])
node(8.6, 4.5, T("报警 9.5 个", "alarm: 9.5"), C["x"])
node(8.6, 3.3, T("漏检 0.5 个", "missed: 0.5"), C["muted"])
node(8.6, 1.7, T("误报 49.5 个", "false alarm: 49.5"), C["z"])
node(8.6, 0.5, T("不报警 940.5 个", "no alarm: 940.5"), C["muted"])
edge((1.2, 2.5), (4.6, 3.9), "1%")
edge((1.2, 2.5), (4.6, 1.1), "99%", -1)
edge((4.6, 3.9), (8.6, 4.5), "95%")
edge((4.6, 3.9), (8.6, 3.3), "5%", -1)
edge((4.6, 1.1), (8.6, 1.7), "5%")
edge((4.6, 1.1), (8.6, 0.5), "95%", -1)
ax.text(5.0, -0.25, T("报警的 59 个零件中，真有缺陷的只有 9.5 个：9.5 / 59 ≈ 16%",
                      "Of the 59 parts that raise an alarm only 9.5 are defective: 9.5 / 59 ≈ 16%"), ha="center", fontsize=10)
ax.set_ylim(-0.5, 5)
figure(fig, "fig9_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.3.2 走廊里的 AGV（与算例 9.3.2 相同的计算）
ncell, tags, hit = 20, {2, 6, 7, 15}, 0.9
move = {0: 0.1, 1: 0.8, 2: 0.1}


def like(z, i):
    p = hit if i in tags else 1 - hit
    return p if z else 1 - p


def predict(b):
    nb = np.zeros(ncell)
    for i in range(ncell):
        for k, pk in move.items():
            nb[min(i + k, ncell - 1)] += pk * b[i]
    return nb


bel = np.full(ncell, 1 / ncell)
rows = [(T("先验：不知道在哪里", "prior: no idea where"), bel.copy(), None)]
labels = [T("测得“有”", "sensed “tag”"), T("测得“有”", "sensed “tag”"), T("测得“无”", "sensed “no tag”")]
true_pos = [6, 7, 8]
for j, z in enumerate((1, 1, 0)):
    bel = np.array([like(z, i) for i in range(ncell)]) * bel
    bel /= bel.sum()
    rows.append((T(f"第 {j + 1} 次测量：", f"measurement {j + 1}: ") + labels[j], bel.copy(), true_pos[j]))
    if j < 2:
        bel = predict(bel)
        rows.append((T("前进一格（有走多、走少的可能）", "move one cell (may over- or undershoot)"), bel.copy(), true_pos[j + 1]))
fig, axs = plt.subplots(len(rows), 1, figsize=(7.8, 7.4), sharex=True)
for ax, (title, b, tp) in zip(axs, rows):
    cols = [C["accent"] if i in tags else "#c9d3d9" for i in range(ncell)]
    ax.bar(range(ncell), b, color=cols, width=0.8)
    ax.set_ylim(0, 0.5)
    ax.set_yticks([0, 0.25, 0.5])
    ax.tick_params(labelsize=8)
    ax.text(-0.6, 0.38, title, fontsize=9)
    if tp is not None:
        ax.annotate("", xy=(tp, b[tp] + 0.02), xytext=(tp, b[tp] + 0.14),
                    arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.2))
    clean(ax)
axs[-1].set_xticks(range(ncell))
axs[-1].set_xlabel(T("格号（金色：有反光标志的格；红箭头：AGV 实际所在的格）", "cell (gold: cells with a reflector; red arrow: where the AGV really is)"), fontsize=9)
fig.text(0.01, 0.5, T("概率", "probability"), rotation=90, va="center", fontsize=10)
fig.tight_layout(rect=(0.02, 0, 1, 1))
figure(fig, "fig9_3_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.3.3 高斯先验 × 高斯似然
mu0, s0, z1, sz = 5.20, 0.10, 5.25, 0.03
K = s0 ** 2 / (s0 ** 2 + sz ** 2)
mu1, s1 = mu0 + K * (z1 - mu0), math.sqrt((1 - K) * s0 ** 2)
x = np.linspace(4.85, 5.55, 600)
fig, ax = plt.subplots(figsize=(7.2, 3.6))
ax.plot(x, gauss_pdf(x, mu0, s0), color=C["muted"], lw=1.8, ls="--")
ax.plot(x, gauss_pdf(x, z1, sz), color=C["accent"], lw=1.8, ls=":")
ax.plot(x, gauss_pdf(x, mu1, s1), color=C["z"], lw=2.2)
ax.text(mu0 - 0.25, 3.6, T(f"先验（里程计）\n$\\mathcal{{N}}$({mu0:.2f}, {s0:.2f}²)", f"prior (odometry)\n$\\mathcal{{N}}$({mu0:.2f}, {s0:.2f}²)"), color=C["muted"], fontsize=9)
ax.text(z1 + 0.06, 12.0, T(f"似然（激光雷达）\n中心 z = {z1:.2f}，σ = {sz:.2f}", f"likelihood (lidar)\ncentred at z = {z1:.2f}, σ = {sz:.2f}"), color=C["accent"], fontsize=9)
ax.text(mu1 + 0.035, 14.2, T(f"后验 $\\mathcal{{N}}$({mu1:.3f}, {s1:.3f}²)", f"posterior $\\mathcal{{N}}$({mu1:.3f}, {s1:.3f}²)"), color=C["z"], fontsize=9)
ax.set_xlim(4.85, 5.55)
ax.set_ylim(0, 15.5)
ax.set_xlabel(T("AGV 沿通道的位置 x / m", "AGV position along the aisle x / m"))
ax.set_ylabel(T("概率密度 / m⁻¹", "density / m⁻¹"))
clean(ax)
figure(fig, "fig9_3_3")
plt.close(fig)
