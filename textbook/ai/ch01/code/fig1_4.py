"""1.4 节的示意图。

图 1.4.1：数据、算法、算力三要素各自提供什么，以及它们共同决定模型能力。
图 1.4.2：三个代表性模型的训练算力（对数坐标），以及从 AlexNet 出发按摩尔定律（两年翻一番）和按每年 4.5 倍增长的两条参考线。
AlexNet 为按逐层乘加数的估算（程序 1.4.1），GPT-3、Llama 3 405B 为论文公布值。
"""
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from _ch1 import ALEXNET, GPT3, LLAMA3, alexnet_layers
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 1.4.1 三要素
fig, ax = plt.subplots(figsize=(8.6, 3.8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.4)
ax.axis("off")
TRIO = [(1.7, "数据", "Data", "提供经验 $E$", "supplies experience $E$", "#eef3f8", C["z"]),
        (5.0, "算法", "Algorithm", "决定怎样学", "decides how to learn", "#f1f6ef", C["y"]),
        (8.3, "算力", "Compute", "决定学多大规模", "decides at what scale", "#fdf3ea", C["accent"])]
for x, zh, en, szh, sen, fc, ec in TRIO:
    ax.add_patch(FancyBboxPatch((x - 1.25, 2.5), 2.5, 1.15, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.5))
    ax.text(x, 3.33, T(zh, en), ha="center", va="center", fontsize=13, color=C["ink"], weight="bold")
    ax.text(x, 2.85, T(szh, sen), ha="center", va="center", fontsize=9.5, color=C["ink"])
    ax.add_patch(FancyArrowPatch((x, 2.44), (5.0 if x == 5.0 else x + (0.95 if x < 5 else -0.95), 1.62),
                                 arrowstyle="-|>", mutation_scale=13, lw=1.4, color=ec,
                                 connectionstyle="arc3,rad=0"))
ax.add_patch(FancyBboxPatch((2.6, 0.85), 4.8, 0.78, boxstyle="round,pad=0.02,rounding_size=0.12",
                            fc="#f7f7f5", ec=C["ink"], lw=1.4))
ax.text(5.0, 1.24, T("模型的能力", "what the model can do"), ha="center", va="center",
        fontsize=12, color=C["ink"], weight="bold")
ax.text(5.0, 0.4, T("三者可以在一定程度上互相替代，但都不可缺；算力是必要条件，不是充分条件",
                    "the three substitute for one another only in part; compute is necessary, not sufficient"),
        ha="center", va="center", fontsize=9.5, color=C["muted"])
figure(fig, "fig1_4_1")

# ---------------------------------------------------------------- 图 1.4.2 训练运算量
macs = sum(m for _, m, _ in alexnet_layers())
C_alex = 3 * 2 * macs * ALEXNET["train_images"] * ALEXNET["epochs"]
pts = [(2012, C_alex, T("AlexNet（估算）", "AlexNet (estimate)")), (GPT3["year"], GPT3["C_paper"], "GPT-3"),
       (LLAMA3["year"], LLAMA3["C_paper"], "Llama 3 405B")]

fig, ax = plt.subplots(figsize=(7.2, 4.2))
yrs = np.linspace(2012, 2026, 100)
ax.semilogy(yrs, C_alex * 2 ** ((yrs - 2012) / 2), color=C["muted"], lw=1.4, ls="--",
            label=T("摩尔定律：两年翻一番（每年 ×1.41）", "Moore's law: doubling every 2 years (×1.41/yr)"))
ax.semilogy(yrs, C_alex * 4.5 ** (yrs - 2012), color=C["accent"], lw=1.6, ls="-",
            label=T("每年 ×4.5（约 5.5 个月翻一番）", "×4.5 per year (doubling ≈ 5.5 months)"))
for yr, c, name in pts:
    ax.semilogy(yr, c, "o", color=C["z"], ms=8, zorder=3)
    ax.text(yr + 0.3, c / 3, name, fontsize=10, color=C["ink"], va="top")
ax.set_xlim(2011, 2026.5)
ax.set_ylim(1e16, 1e28)
ax.set_xlabel(T("年份", "year"))
ax.set_ylabel(T("训练算力 / FLOP", "training compute / FLOP"))
ax.grid(True, which="major", axis="y", color="#e5e5e5", lw=0.8)
ax.legend(fontsize=8.6, frameon=False, loc="upper left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig1_4_2")
plt.close(fig)
