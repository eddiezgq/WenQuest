"""39.1 节的示意图。

图 39.1.1：正确度与精密度（四个靶）。
图 39.1.2：算例 39.1.1 的 10 个读数、平均值、±U 区间与砝码标称值。
"""
import math

import numpy as np

from bookout import COLORS as C, T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 39.1.1
rng = np.random.default_rng(3911)
cases = [(T("正确度高、精密度高", "High trueness, high precision"), (0, 0), 0.25), (T("正确度低、精密度高", "Low trueness, high precision"), (1.3, 0.9), 0.25),
         (T("正确度高、精密度低", "High trueness, low precision"), (0, 0), 0.95), (T("正确度低、精密度低", "Low trueness, low precision"), (1.2, -0.9), 0.95)]
fig, axs = plt.subplots(1, 4, figsize=(10, 2.9))
for ax, (title, c, s) in zip(axs, cases):
    for r, col in ((3, "#eef2f4"), (2, "#dde4e8"), (1, "#c9d3d9")):
        ax.add_patch(plt.Circle((0, 0), r, color=col, zorder=0))
    ax.plot(0, 0, "+", color=C["ink"], ms=12, mew=1.5)
    p = np.array(c) + rng.normal(0, s, (12, 2))
    ax.scatter(p[:, 0], p[:, 1], s=16, color=C["x"], zorder=3)
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)
fig.text(0.5, 0.02, T("靶心 = 真值；弹着点的平均位置偏离靶心 → 系统误差；弹着点的分散 → 随机误差", "Bull's-eye = true value; mean position of the hits off the bull's-eye → systematic error; spread of the hits → random error"), ha="center", fontsize=9)
figure(fig, "fig39_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 39.1.2（数据与算例 39.1.1 相同）
rng = np.random.default_rng(391)
x = np.round(20.0 + 0.12 + rng.normal(0, 0.06, 10), 2)
mean, s = x.mean(), x.std(ddof=1)
uc = math.sqrt((s / math.sqrt(10)) ** 2 + (0.005 / math.sqrt(3)) ** 2 + 0.05 ** 2)
U = 2 * uc
fig, ax = plt.subplots(figsize=(6.2, 3.0))
ax.axhspan(mean - U, mean + U, color=C["z"], alpha=0.12, lw=0)
ax.axhline(mean, color=C["z"], lw=1.5)
ax.axhline(20.0, color=C["ink"], lw=1.2, ls="--")
ax.plot(np.arange(1, 11), x, "o", color=C["x"], ms=6)
ax.text(10.5, mean + 0.003, T(f"平均值 {mean:.3f} N", f"Mean {mean:.3f} N"), va="bottom", fontsize=9, color=C["z"])
ax.text(10.5, 20.0 + 0.003, T("砝码 20 N", "Weight 20 N"), va="bottom", fontsize=9)
ax.text(0.7, mean + U + 0.006, T(f"阴影：平均值 ± U（U = {U:.2f} N，k = 2）", f"Shaded: mean ± U (U = {U:.2f} N, k = 2)"), fontsize=8.5, color=C["z"])
ax.set_xlim(0.5, 12.8)
ax.set_xticks(range(1, 11))
ax.set_xlabel(T("测量序号", "Measurement number"))
ax.set_ylabel(T("读数 / N", "Reading / N"))
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig39_1_2")
plt.close(fig)
