"""13.3 节的示意图。

图 13.3.1：UR5e 厂商 DH 参数与零件库模型尺寸逐项之差，以及每一项单独造成的末端位置偏差（与程序 13.3.1 相同的算法），
          并与“各项全部改变”时一万组随机关节角下的最大偏差、平均偏差比较。
"""
import math

import numpy as np

from _dh import fk_sdh, fk_space, lines_to_sdh, ur_poe, ur_vendor
from _fig13 import C
from bookout import T, figure, style

plt = style()
pi = math.pi
vend = ur_vendor()
tab, S, M = ur_poe()
model, _ = lines_to_sdh([("R", np.asarray(w, float), np.asarray(q, float)) for w, q in tab], M[:3, 3])
rng = np.random.default_rng(12)
for _ in range(10000):
    rng.uniform(-pi, pi, 6)
Q = np.array([rng.uniform(-pi, pi, 6) for _ in range(10000)])
gaps = np.array([np.linalg.norm(fk_sdh(vend, q)[:3, 3] - fk_space(S, M, q)[:3, 3]) for q in Q]) * 1000
items = [("$d_1$", 0, 2), ("$a_2$", 1, 0), ("$a_3$", 2, 0), ("$d_4$", 3, 2), ("$d_5$", 4, 2), ("$d_6$", 5, 2)]
diff = [abs(vend[r][c] - model[r][c]) * 1000 for _, r, c in items]

fig, ax = plt.subplots(figsize=(7.4, 3.6))
y = np.arange(len(items))[::-1] + 3
ax.barh(y, diff, color=C["z"], height=0.6)
for yi, d in zip(y, diff):
    ax.text(d + 0.03, yi, f"{d:.1f}", va="center", fontsize=9.5, color=C["ink"])
ax.barh([1.5], [sum(diff)], color=C["muted"], height=0.6)
ax.text(sum(diff) + 0.03, 1.5, T(f"{sum(diff):.1f}（各项之和：上界）", f"{sum(diff):.1f} (sum: upper bound)"), va="center", fontsize=9.5)
ax.barh([0.5], [gaps.max()], color=C["accent"], height=0.6)
ax.text(gaps.max() + 0.03, 0.5, T(f"{gaps.max():.2f}（一万组关节角中的最大值）", f"{gaps.max():.2f} (largest of 10 000 random poses)"), va="center", fontsize=9.5)
ax.barh([-0.5], [gaps.mean()], color=C["accent"], alpha=0.55, height=0.6)
ax.text(gaps.mean() + 0.03, -0.5, T(f"{gaps.mean():.2f}（平均值）", f"{gaps.mean():.2f} (mean)"), va="center", fontsize=9.5)
ax.set_yticks(list(y) + [1.5, 0.5, -0.5])
ax.set_yticklabels([n for n, _, _ in items] + [T("合计", "total"), T("实际最大", "actual max"), T("实际平均", "actual mean")], fontsize=10)
ax.set_xlabel(T("末端位置偏差 / mm（单独一项时等于该参数之差）", "tool position gap / mm (one item alone: equals that parameter's difference)"), fontsize=9.5)
ax.set_xlim(0, 3.3)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.axhline(2.5, color=C["muted"], lw=0.6, ls=":")
figure(fig, "fig13_3_1")
plt.close(fig)
