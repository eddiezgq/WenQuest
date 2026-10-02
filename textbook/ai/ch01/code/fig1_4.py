"""1.4 节的示意图。

图 1.4.1：三个代表性模型的训练算力（对数坐标），以及从 AlexNet 出发按摩尔定律（两年翻一番）和按每年 4.5 倍增长的两条参考线。
AlexNet 为按逐层乘加数的估算（程序 1.4.1），GPT-3、Llama 3 405B 为论文公布值。
"""
import numpy as np

from _ch1 import ALEXNET, GPT3, LLAMA3, alexnet_layers
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
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
figure(fig, "fig1_4_1")
plt.close(fig)
